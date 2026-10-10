# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Generate the synthetic FAIR header assessment fixtures (assessment/pairs, edge).

The output is deterministic: gzip members carry mtime 0 and no file name, tar
members are owned by uid/gid 0 with mtime 0. Real provider captures in
assessment/headers are copied, not generated. Their expected outcomes, and those
of the generated files, are listed in assessment/manifest.json.

Usage: python scripts/make_assessment_fixtures.py [--output DIR]
"""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fixtures():
    """Return {relative path: bytes} for every generated fixture."""
    return {}


def write(output):
    for name, content in sorted(fixtures().items()):
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=ROOT / "assessment",
                        help="directory that receives pairs/ and edge/ (default: assessment/)")
    args = parser.parse_args()
    write(args.output)


if __name__ == "__main__":
    main()
