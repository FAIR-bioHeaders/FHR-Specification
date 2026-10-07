"""Emit a documented partial MIxS/MIGS projection with explicit omissions."""

import argparse
import json
from pathlib import Path
import shlex
import sys

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError
import yaml

ROOT = Path(__file__).resolve().parents[1]


def project(metadata):
    mapping = yaml.safe_load((ROOT / "fhr_mappings.yml").read_text())
    schema = json.loads((ROOT / "fhr.json").read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(metadata)
    result = {}
    omissions = {}
    for target, rule in mapping["class_derivations"]["MIGSProjection"][
        "slot_derivations"
    ].items():
        expr = rule["expr"]
        if expr.startswith("{") and expr.endswith("}"):
            value = metadata
            try:
                for key in expr[1:-1].split("."):
                    value = value[key]
                result[target] = value
            except KeyError:
                omissions[target] = "Source field absent"
        elif expr == "assembly_software(assemblySoftware)":
            software = metadata.get("assemblySoftware")
            if not isinstance(software, list) or len(software) != 1:
                omissions[target] = (
                    "Requires one structured software object; legacy names and multiple tools need manual projection"
                )
                continue
            item = software[0]
            if "version" not in item or "commandLineOption" not in item:
                omissions[target] = (
                    "Version and command options must be explicitly supplied"
                )
                continue
            values = [
                item["name"],
                item["version"],
                shlex.join(item["commandLineOption"]) or "none",
            ]
            if any(";" in value or "\n" in value or not value for value in values):
                omissions[target] = (
                    "Empty values or delimiter characters require manual projection"
                )
                continue
            result[target] = ";".join(values)
        else:
            raise ValueError(f"Unsupported mapping expression: {expr}")
    return {
        "target_version": mapping["target_version"],
        "metadata": result,
        "unmapped": omissions,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        stream = args.input.read_text()
        metadata = (
            json.loads(stream)
            if args.input.suffix == ".json"
            else yaml.safe_load(stream)
        )
        print(json.dumps(project(metadata), indent=2))
    except (OSError, ValueError, yaml.YAMLError, ValidationError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
