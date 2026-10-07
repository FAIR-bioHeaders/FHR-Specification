"""Check schema copies and example identity across local companion checkouts."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--converter", type=Path, required=True)
    args = parser.parse_args()
    schema = json.loads((ROOT / "fhr.json").read_text())
    for relative in ("fhr_schema.json", "fhr/fhr_schema.json"):
        path = args.converter / relative
        if json.loads(path.read_text()) != schema:
            print(f"Schema copy differs: {path}", file=sys.stderr)
            return 1
    for example in (ROOT / "examples").iterdir():
        if (
            example.is_file()
            and example.read_bytes()
            != (args.converter / "examples" / example.name).read_bytes()
        ):
            print(f"Companion example differs: {example.name}", file=sys.stderr)
            return 1
    print("Both converter schema copies and all example files match the specification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
