"""Require explicit baseline updates for changes to the published FHR schema."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"invalid JSON constant: {value}")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=unique_object, parse_constant=reject_constant)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def differences(before, after, pointer=""):
    """Report changed JSON pointers without discarding any schema keywords."""
    if canonical(before) == canonical(after):
        return
    if isinstance(before, dict) and isinstance(after, dict):
        for key in sorted(before.keys() | after.keys()):
            child = pointer + "/" + key.replace("~", "~0").replace("/", "~1")
            if key not in before:
                yield f"{child}: added {canonical(after[key])}"
            elif key not in after:
                yield f"{child}: removed {canonical(before[key])}"
            else:
                yield from differences(before[key], after[key], child)
    else:
        yield f"{pointer or '/'}: {canonical(before)} -> {canonical(after)}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "fhr.json")
    parser.add_argument("--baseline", type=Path, default=ROOT / ".github/schema-baseline.json")
    parser.add_argument("--update", action="store_true",
                        help="Explicitly accept the schema as the new review baseline")
    args = parser.parse_args()
    try:
        schema = load(args.schema)
        if not isinstance(schema, dict):
            raise ValueError(f"{args.schema}: schema must be a JSON object")
        if args.update:
            args.baseline.write_text(json.dumps(schema, indent=2, sort_keys=True,
                                                ensure_ascii=False, allow_nan=False) + "\n",
                                     encoding="utf-8")
            print(f"Updated {args.baseline}; review and commit it with the schema change.")
            return 0
        baseline = load(args.baseline)
    except (OSError, ValueError) as error:
        print(f"Schema drift check failed: {error}", file=sys.stderr)
        return 1

    changes = list(differences(baseline, schema))
    if changes:
        print(f"{args.schema}: differs from {args.baseline}", file=sys.stderr)
        for change in changes:
            print(change, file=sys.stderr)
        print("For an intentional change, review compatibility and update the baseline "
              "with python scripts/check_schema_drift.py --update. "
              "Commit both files and explain the change in the PR.", file=sys.stderr)
        return 1
    print(f"{args.schema}: matches the schema baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main())
