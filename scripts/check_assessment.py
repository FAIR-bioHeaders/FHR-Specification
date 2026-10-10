# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Check a FAIR header assessment tool against the shared fixtures.

Runs ``bioheaders assess --format json [--type T] [--related R] FILE`` for every
entry of assessment/manifest.json, validates each report against the tool's own
bundled report schema (needs jsonschema), and compares only the fields listed
under ``expected``. Prints ``ok: <id>`` or the differences, and exits 1 if any
fixture differs. Modelled on check_conformance.py.
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ASSESSMENT = ROOT / "assessment"
REPORT_SCHEMA = "bioheaders/assess/data/assessment-report.schema.json"
SCHEMA_CODE = ("from importlib.resources import files; import sys; "
               "sys.stdout.write(files('bioheaders.assess').joinpath('data')"
               ".joinpath('assessment-report.schema.json').read_text(encoding='utf-8'))")


class Tool:
    """How to run ``bioheaders`` and where its report schema is."""

    def __init__(self, location):
        if location == "PATH":
            found = shutil.which("bioheaders")
            if not found:
                raise ValueError("bioheaders is not on PATH")
            self.command = [found]
            self.python = shutil.which("python", path=str(Path(found).parent))
            self.checkout = None
            return
        path = Path(location)
        if (path / "bioheaders" / "cli.py").is_file():  # A toolkit checkout.
            code = (f"import sys; sys.path.insert(0, {str(path.resolve())!r}); "
                    "sys.argv[0] = 'bioheaders'; from bioheaders.cli import main; sys.exit(main())")
            self.command = [sys.executable, "-c", code]
            self.python = None
            self.checkout = path
            return
        for directory in (path, path / "bin", path / "Scripts"):
            found = shutil.which("bioheaders", path=str(directory))
            if found:
                self.command = [found]
                self.python = shutil.which("python", path=str(directory))
                self.checkout = None
                return
        raise ValueError(f"{location}: no toolkit checkout, environment or bin directory")

    def schema(self):
        if self.checkout is not None:
            return json.loads((self.checkout / REPORT_SCHEMA).read_text(encoding="utf-8"))
        if self.python is None:
            raise ValueError("cannot find the Python of the tool to read its report schema")
        result = subprocess.run([self.python, "-c", SCHEMA_CODE], capture_output=True, text=True)
        if result.returncode:
            raise ValueError(f"cannot read the tool's report schema: {result.stderr.strip()}")
        return json.loads(result.stdout)

    def assess(self, entry, assessment):
        arguments = ["assess", "--format", "json"]
        if "type" in entry:
            arguments += ["--type", entry["type"]]
        if "related" in entry:
            arguments += ["--related", str(assessment / entry["related"])]
        arguments.append(str(assessment / entry["file"]))
        return subprocess.run(self.command + arguments, capture_output=True, text=True,
                              timeout=300, env={**os.environ, "PYTHONSAFEPATH": "1"})


def _status(result):
    if result["status"] in ("not_applicable", "not_assessed"):
        return f"{result['status']}/{result['reason']}"
    return result["status"]


def _matches(expected, actual):
    """True if ``expected`` (a status or status/reason) describes ``actual``."""
    return actual == expected or ("/" not in expected and actual.split("/")[0] == expected)


def compare(expected, report):
    """Return a list of differences between ``expected`` and ``report``."""
    problems = []
    results = {result["indicator"]: result for result in report["results"]}
    lines = {item["id"]: item["line"] for item in report["evidence"]}
    if "scope" in expected:
        scope, _, reason = expected["scope"].partition("/")
        if report["input"]["scope"] != scope:
            problems.append(f"scope: expected {scope}, got {report['input']['scope']}")
        if reason:
            wrong = sorted(i for i, r in results.items()
                           if r["status"] != "not_applicable" and _status(r) != f"not_assessed/{reason}")
            if wrong:
                problems.append(f"scope: indicators without not_assessed/{reason}: {', '.join(wrong)}")
    for indicator, status in sorted(expected.get("statuses", {}).items()):
        actual = _status(results[indicator]) if indicator in results else "missing"
        if not _matches(status, actual):
            problems.append(f"{indicator}: expected {status}, got {actual}")
    for indicator, wanted in sorted(expected.get("evidence_lines", {}).items()):
        cited = {lines[e] for e in results.get(indicator, {}).get("evidence", [])}
        if not set(wanted) <= cited:
            problems.append(f"{indicator}: expected evidence lines {wanted}, got {sorted(cited)}")
    if "links" in expected:
        links = report.get("links", [])
        if len(links) != len(expected["links"]):
            problems.append(f"links: expected {len(expected['links'])}, got "
                            + json.dumps([[l["kind"], l["value"]] for l in links]))
        else:
            for index, (want, link) in enumerate(zip(expected["links"], links)):
                verification = link.get("verification") or {}
                got = {"kind": link["kind"], "value": link["value"], "well_formed": link["well_formed"],
                       "verdict": verification.get("verdict"), "reason": verification.get("reason")}
                for key, value in want.items():
                    if got[key] != value:
                        problems.append(f"links[{index}].{key}: expected {json.dumps(value)}, "
                                        f"got {json.dumps(got[key])}")
    if "findings" in expected:
        found = [(f["kind"], {lines[e] for e in f["evidence"]}) for f in report["findings"]]
        found += [(f["kind"], {lines[e] for e in f["evidence"]})
                  for result in report["results"] for f in result["findings"]]
        for want in expected["findings"]:
            if not any(kind == want["kind"] and ("line" not in want or want["line"] in cited)
                       for kind, cited in found):
                where = f" at line {want['line']}" if "line" in want else ""
                problems.append(f"findings: no {want['kind']}{where}")
    if "conformance" in expected:
        want, got = expected["conformance"], report.get("conformance")
        if want is None or got is None:
            if want != got:
                problems.append(f"conformance: expected {json.dumps(want)}, got {json.dumps(got)}")
        else:
            for key, value in want.items():
                if got.get(key) != value:
                    problems.append(f"conformance.{key}: expected {json.dumps(value)}, "
                                    f"got {json.dumps(got.get(key))}")
    if "circumstantial" in expected:
        got = report.get("circumstantial") or {}
        for key, value in expected["circumstantial"].items():
            if got.get(key) != value:
                problems.append(f"circumstantial.{key}: expected {json.dumps(value)}, "
                                f"got {json.dumps(got.get(key))}")
    if "pair_classification" in expected and report.get("pair_classification") != expected["pair_classification"]:
        problems.append(f"pair_classification: expected {expected['pair_classification']}, "
                        f"got {report.get('pair_classification')}")
    return problems


def check(tool, manifest, assessment, validator):
    failures = 0
    for entry in manifest["fixtures"]:
        result = tool.assess(entry, assessment)
        try:
            report = json.loads(result.stdout)
        except ValueError:
            detail = (result.stderr or result.stdout).strip().splitlines()
            print(f"FAIL {entry['id']}: no JSON report (exit {result.returncode}"
                  f"{': ' + detail[-1] if detail else ''})")
            failures += 1
            continue
        problems = [f"report does not conform at {error.json_path}: {error.message}"
                    for error in validator.iter_errors(report)][:5]
        problems += compare(entry["expected"], report)
        if problems:
            failures += 1
            print(f"FAIL {entry['id']}:")
            for problem in problems:
                print(f"  {problem}")
        else:
            print(f"ok: {entry['id']}")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tool", default="PATH", metavar="LOCATION",
                        help="a toolkit checkout, a virtual environment or bin directory, "
                             "or PATH (the default)")
    parser.add_argument("--assessment", type=Path, default=ASSESSMENT,
                        help="fixture directory (default: assessment/)")
    args = parser.parse_args()
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        parser.error("check_assessment.py needs jsonschema (requirements-validation.txt)")
    try:
        tool = Tool(args.tool)
        validator = Draft202012Validator(tool.schema(), format_checker=FormatChecker())
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    manifest = json.loads((args.assessment / "manifest.json").read_text(encoding="utf-8"))
    failures = check(tool, manifest, args.assessment, validator)
    total = len(manifest["fixtures"])
    print(f"{total - failures} of {total} fixtures match")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
