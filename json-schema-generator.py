"""Generate a validation-equivalent FHR schema from its LinkML model."""

import argparse
import json
from pathlib import Path

from linkml.generators.jsonschemagen import JsonSchemaGenerator
from linkml_runtime import SchemaView

ROOT = Path(__file__).resolve().parent
# Core string slots whose exact length LinkML cannot express.
EXACT_LENGTHS = {"checksum": 44, "seqcol_id": 32}


def generate_from(schema_path):
    """Generate JSON Schema for any LinkML schema that imports schemas/core.yaml."""
    view = SchemaView(str(schema_path))
    generated = json.loads(
        JsonSchemaGenerator(
            view.schema,
            include_null=False,
            not_closed=False,
        ).serialize()
    )
    # All nested objects are closed (v0.4). The published contract writes the
    # schemaVersion restriction as an enum so later versions can be listed.
    for node in (generated, *generated["$defs"].values()):
        version = node.get("properties", {}).get("schemaVersion", {})
        if "const" in version:
            version["enum"] = [version.pop("const")]
    # A trailing newline satisfies "$" in Python regexes; pin the exact length.
    for node in (generated, *generated["$defs"].values()):
        for name, length in EXACT_LENGTHS.items():
            if name in node.get("properties", {}):
                node["properties"][name].update(minLength=length, maxLength=length)
    generated["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    return generated


def generate():
    generated = generate_from(ROOT / "fhr_linkml.yml")
    # LinkML emits a scalar type beside a heterogeneous union. Retain the union.
    for node in (generated, generated["$defs"]["FHR"]):
        node["properties"]["assemblySoftware"].pop("type", None)
    return generated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "fhr_linkml.json")
    args = parser.parse_args()
    args.output.write_text(json.dumps(generate(), indent=2) + "\n", encoding="utf-8")
    print(f"Generated {args.output}")


if __name__ == "__main__":
    main()
