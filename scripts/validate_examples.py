"""Validate the published schema and its JSON/YAML examples."""

import argparse
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
import yaml

ROOT = Path(__file__).resolve().parents[1]
DIALECT = "https://json-schema.org/draft/2020-12/schema"


def load_document(path):
    with path.open(encoding="utf-8") as stream:
        if path.suffix == ".json":
            return json.load(stream)
        return yaml.safe_load(stream)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "fhr.json")
    parser.add_argument("--examples", type=Path, default=ROOT / "examples")
    args = parser.parse_args()

    try:
        schema = load_document(args.schema)
        if not isinstance(schema, dict) or schema.get("$schema") != DIALECT:
            raise ValueError(f"expected $schema: {DIALECT}")
        Draft202012Validator.check_schema(schema)
    except (OSError, ValueError, yaml.YAMLError, SchemaError) as error:
        print(f"{args.schema}: invalid schema: {error}", file=sys.stderr)
        return 1

    examples = sorted(
        path for path in args.examples.glob("*")
        if path.is_file() and path.suffix in {".json", ".yaml", ".yml"}
    )
    if not examples:
        print(f"{args.examples}: no JSON/YAML examples found", file=sys.stderr)
        return 1

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    failed = False
    for path in examples:
        try:
            instance = load_document(path)
        except (OSError, ValueError, yaml.YAMLError) as error:
            print(f"{path}: parse error: {error}", file=sys.stderr)
            failed = True
            continue
        errors = sorted(validator.iter_errors(instance), key=lambda error: error.json_path)
        for error in errors:
            print(f"{path}: {error.json_path}: {error.message}", file=sys.stderr)
        if errors:
            failed = True
        else:
            print(f"{path}: valid")

    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
