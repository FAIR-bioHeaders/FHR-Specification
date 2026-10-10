# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Check a FAIR header assessment tool against the shared fixtures.

Runs ``bioheaders assess --format json [--type T] [--related R] FILE`` for every
entry of assessment/manifest.json, validates each report against the tool's own
bundled report schema (needs jsonschema), and compares only the fields listed
under ``expected``. Prints ``ok: <id>`` or the differences, and exits 1 if any
fixture differs. Modelled on check_conformance.py.

``--guideline`` also compares the tool's bundled rubric.json with the item table
of docs/FAIR_HEADER_GUIDELINE.md, in both directions.
"""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ASSESSMENT = ROOT / "assessment"
GUIDELINE = ROOT / "docs" / "FAIR_HEADER_GUIDELINE.md"
DATA = "bioheaders/assess/data/"
REPORT_SCHEMA = "assessment-report.schema.json"
DATA_CODE = ("from importlib.resources import files; import sys; "
             "sys.stdout.write(files('bioheaders.assess').joinpath('data')"
             ".joinpath(sys.argv[1]).read_text(encoding='utf-8'))")


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

    def data(self, name):
        """A JSON data file bundled with the tool (bioheaders/assess/data/NAME)."""
        if self.checkout is not None:
            return json.loads((self.checkout / DATA / name).read_text(encoding="utf-8"))
        if self.python is None:
            raise ValueError(f"cannot find the Python of the tool to read its {name}")
        result = subprocess.run([self.python, "-c", DATA_CODE, name], capture_output=True, text=True)
        if result.returncode:
            raise ValueError(f"cannot read the tool's {name}: {result.stderr.strip()}")
        return json.loads(result.stdout)

    def schema(self):
        return self.data(REPORT_SCHEMA)

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


def guideline_tables(text):
    """The summary rows {item: row} and out-of-scope rows {indicator: row} of the guideline."""
    summary, out_of_scope = {}, {}
    lines = text.splitlines()
    for index, line in enumerate(lines[:-1]):
        if not (line.startswith("|") and re.match(r"^\|[-| :]+\|$", lines[index + 1])):
            continue
        header = [cell.strip() for cell in line.strip().strip("|").split("|")]
        target = {"Item": summary, "Indicator": out_of_scope}.get(header[0])
        if target is None:
            continue
        for row_line in lines[index + 2:]:
            if not row_line.startswith("|"):
                break
            row = dict(zip(header, (c.strip() for c in row_line.strip().strip("|").split("|"))))
            target[row[header[0]]] = row
    return summary, out_of_scope


def _ids(cell):
    return {part.strip() for part in cell.split(",") if part.strip()}


def check_guideline(rubric, text):
    """Differences between the rubric and the guideline item table, in both directions."""
    problems = []
    summary, out_of_scope = guideline_tables(text)
    if not summary:
        return ["guideline: no item table (columns Item | Title | ...)"]
    indicators = {indicator["id"]: indicator for indicator in rubric["indicators"]}
    by_item = {}
    for identifier, indicator in indicators.items():
        by_item.setdefault(indicator["guideline_item"], set()).add(identifier)
    for item in sorted(set(summary) | {i for i in by_item if i != "out-of-scope"}):
        row = summary.get(item)
        rubric_ids = by_item.get(item, set())
        if row is None:
            problems.append(f"{item}: in the rubric ({', '.join(sorted(rubric_ids))}) but not in the guideline")
            continue
        listed = _ids(row["Indicators"])
        checks = _ids(row["Checks"])
        for missing in sorted(rubric_ids - listed):
            problems.append(f"{item}: rubric indicator {missing} is not listed under the item")
        for extra in sorted(listed - rubric_ids):
            where = indicators[extra]["guideline_item"] if extra in indicators else "not in the rubric"
            problems.append(f"{item}: guideline lists {extra}, rubric says {where}")
        assessed = {i for i in rubric_ids if indicators[i]["assessability"] != "deferred"}
        for missing in sorted(assessed - checks):
            problems.append(f"{item}: rubric check {missing} is not among the item's checks")
        for extra in sorted(checks - assessed):
            problems.append(f"{item}: guideline check {extra} is not an assessed rubric indicator of {item}")
    rubric_out = by_item.get("out-of-scope", set())
    for missing in sorted(rubric_out - set(out_of_scope)):
        problems.append(f"out of scope: rubric indicator {missing} is not in the guideline's table")
    for extra in sorted(set(out_of_scope) - rubric_out):
        problems.append(f"out of scope: guideline lists {extra}, rubric does not mark it out of scope")
    for identifier in sorted(rubric_out & set(out_of_scope)):
        if out_of_scope[identifier]["Reason"].strip("`") != indicators[identifier]["reason"]:
            problems.append(f"out of scope: {identifier} reason differs from the rubric")
    for identifier, indicator in sorted(indicators.items()):
        for convention, template in sorted((indicator.get("suggestions") or {}).items()):
            if f"see guideline {indicator['guideline_item']}" not in template["text"]:
                problems.append(f"{identifier}: the {convention} suggestion text does not name "
                                f"guideline {indicator['guideline_item']}")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tool", default="PATH", metavar="LOCATION",
                        help="a toolkit checkout, a virtual environment or bin directory, "
                             "or PATH (the default)")
    parser.add_argument("--assessment", type=Path, default=ASSESSMENT,
                        help="fixture directory (default: assessment/)")
    parser.add_argument("--guideline", action="store_true",
                        help="also compare the tool's rubric.json with docs/FAIR_HEADER_GUIDELINE.md")
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
    if args.guideline:
        rubric = tool.data("rubric.json")
        if rubric["rubric_version"] != manifest["rubric_version"]:
            print(f"note: the tool's rubric is {rubric['rubric_version']}, "
                  f"the manifest was written for {manifest['rubric_version']}")
        problems = check_guideline(rubric, GUIDELINE.read_text(encoding="utf-8"))
        for problem in problems:
            print(f"FAIL guideline: {problem}")
        if not problems:
            print(f"ok: guideline items agree with rubric {rubric['rubric_version']}")
        failures += bool(problems)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
