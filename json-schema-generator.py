"""Generate a validation-equivalent FHR schema from its LinkML model."""

import argparse
import json
from pathlib import Path

from linkml.generators.jsonschemagen import JsonSchemaGenerator
from linkml_runtime import SchemaView

ROOT = Path(__file__).resolve().parent


def generate():
    view = SchemaView(str(ROOT / "fhr_linkml.yml"))
    generated = json.loads(
        JsonSchemaGenerator(
            view.schema,
            include_null=False,
            not_closed=False,
        ).serialize()
    )
    # Legacy FHR nested objects are open; provenance software objects are closed.
    for name in ("Taxon", "Author", "AccessionID", "VitalStats"):
        generated["$defs"][name].pop("additionalProperties", None)
    # LinkML emits a scalar type beside a heterogeneous union. Retain the union.
    for node in (generated, generated["$defs"]["FHR"]):
        node["properties"]["assemblySoftware"].pop("type", None)
        node["properties"]["checksum"].update(minLength=44, maxLength=44)
        node["properties"]["seqcol_id"].update(minLength=32, maxLength=32)
    generated["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    return generated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "fhr_linkml.json")
    args = parser.parse_args()
    args.output.write_text(json.dumps(generate(), indent=2) + "\n", encoding="utf-8")
    print(f"Generated {args.output}")


if __name__ == "__main__":
    main()
