# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The FAIR header guideline, docs/FAIR_HEADER_GUIDELINE.md (feature 010, US3).

Parses the guideline's summary table, its per-item example tables and its
"Out of scope for headers" table, and checks them against the 41 RDA FAIR Data
Maturity Model indicators (embedded below, so this test does not need the
toolkit), against schemas/core.yaml and fhr.json, and against the survey
evidence files in specs/010-fair-header-assessment/research/headers/.
"""

import json
from pathlib import Path
import re
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
GUIDELINE = ROOT / "docs" / "FAIR_HEADER_GUIDELINE.md"
SURVEY = ROOT / "specs" / "010-fair-header-assessment" / "research" / "headers"

# research.md R-03 / research/rda-indicators.md §2: how each indicator is assessed.
OFFLINE = (
    "RDA-F1-01D RDA-F1-02D RDA-F2-01M RDA-F3-01M RDA-A1-01M RDA-I1-01M RDA-I1-01D "
    "RDA-I1-02M RDA-I1-02D RDA-I2-01M RDA-I2-01D RDA-I3-01M RDA-I3-02M RDA-I3-03M "
    "RDA-I3-04M RDA-R1-01M RDA-R1.1-01M RDA-R1.1-02M RDA-R1.1-03M RDA-R1.2-01M "
    "RDA-R1.2-02M RDA-R1.3-01M RDA-R1.3-01D RDA-R1.3-02M RDA-R1.3-02D"
).split()
ONLINE = "RDA-A1-03D RDA-A1-04D RDA-A1-05D RDA-A1.1-01D".split()
DEFERRED = "RDA-I3-01D RDA-I3-02D".split()
NOT_APPLICABLE = (
    "RDA-F1-01M RDA-F1-02M RDA-F4-01M RDA-A1-02M RDA-A1-02D RDA-A1-03M RDA-A1-04M "
    "RDA-A1.1-01M RDA-A1.2-01D RDA-A2-01M"
).split()
NOT_APPLICABLE_REASONS = {"embedded-metadata", "repository-level", "object-in-hand"}
ITEMS = [f"G{n}" for n in range(1, 9)]
CONVENTIONS = {"FAIR-bioHeaders", "GFF3 ##", "GFF3 #!", "VCF ##", "GAF !"}
FILE_TYPES = {"FASTA", "GFA", "GFF3", "VCF", "GAF"}
KINDS = {"surveyed", "illustrative"}
KEYS = {"native", "core"}
ATTRIBUTION = (
    "Indicator identifiers and titles from: FAIR Data Maturity Model Working Group "
    "(2020). FAIR Data Maturity Model. Specification and Guidelines. Research Data "
    "Alliance. doi:10.15497/rda00050. Licensed CC BY 4.0 "
    "(https://creativecommons.org/licenses/by/4.0/). File-header interpretations are "
    "adaptations by FAIR-bioHeaders and are not endorsed by the RDA."
)


def principle(indicator):
    """RDA-R1.3-01M -> R1.3."""
    return indicator.split("-")[1]


def cells(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def tables(text):
    """Yield (heading, rows) for every Markdown table, rows as dicts."""
    heading, lines = None, text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
        if line.startswith("|") and index + 1 < len(lines) and re.match(r"^\|[-| :]+\|$", lines[index + 1]):
            header = cells(line)
            rows = []
            index += 2
            while index < len(lines) and lines[index].startswith("|"):
                rows.append(dict(zip(header, cells(lines[index]))))
                index += 1
            yield heading, header, rows
            continue
        index += 1


def code_spans(cell):
    return re.findall(r"`([^`]+)`", cell)


def id_list(cell):
    return [part.strip() for part in cell.split(",") if part.strip()]


def example_key(convention, line):
    """The key of a native example line, or None."""
    patterns = {
        "GFF3 #!": r"^#!([A-Za-z][\w.-]*)",
        "GFF3 ##": r"^##([A-Za-z][\w.-]*)",
        "VCF ##": r"^##([A-Za-z][\w.-]*)=",
        "GAF !": r"^!([A-Za-z][\w .-]*?):",
        "FAIR-bioHeaders": r"^[;#]~'?([A-Za-z@][\w-]*)'?:",
    }
    found = re.match(patterns[convention], line)
    return found.group(1) if found else None


class GuidelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = GUIDELINE.read_text(encoding="utf-8")
        cls.summary, cls.examples, cls.out_of_scope = None, {}, None
        for heading, header, rows in tables(cls.text):
            if header[:2] == ["Item", "Title"]:
                cls.summary = {row["Item"]: row for row in rows}
            elif header[:2] == ["File type", "Convention"]:
                match = re.match(r"^(G[1-8])\b", heading or "")
                if match:
                    cls.examples.setdefault(match.group(1), []).extend(rows)
            elif header[:2] == ["Indicator", "Reason"]:
                cls.out_of_scope = {row["Indicator"]: row for row in rows}
        core = yaml.safe_load((ROOT / "schemas" / "core.yaml").read_text(encoding="utf-8"))
        cls.core_slots = set(core["slots"])
        cls.fhr_properties = set(json.loads((ROOT / "fhr.json").read_text(encoding="utf-8"))["properties"])

    def test_tables_are_present(self):
        self.assertIsNotNone(self.summary, "no summary table with columns Item | Title | ...")
        self.assertIsNotNone(self.out_of_scope, "no out-of-scope table with columns Indicator | Reason | ...")

    def test_exactly_the_eight_items(self):
        self.assertEqual(list(self.summary), ITEMS)
        self.assertEqual(sorted(self.examples), ITEMS, "every item needs an example table")
        for item in ITEMS:
            self.assertRegex(self.text, rf"(?m)^## {item}\. \S", f"no section heading for {item}")

    def test_the_embedded_indicator_list_is_complete(self):
        everything = OFFLINE + ONLINE + DEFERRED + NOT_APPLICABLE
        self.assertEqual(len(everything), 41)
        self.assertEqual(len(set(everything)), 41)

    def test_every_assessed_indicator_appears_in_exactly_one_item(self):
        listed = [i for row in self.summary.values() for i in id_list(row["Indicators"])]
        duplicates = sorted({i for i in listed if listed.count(i) > 1})
        self.assertEqual(duplicates, [], "indicators listed under more than one item")
        self.assertEqual(sorted(listed), sorted(OFFLINE + ONLINE + DEFERRED))

    def test_checks_are_the_assessed_indicators_of_the_item(self):
        for item, row in self.summary.items():
            with self.subTest(item):
                checks = id_list(row["Checks"])
                self.assertTrue(checks, "an item needs at least one check")
                self.assertEqual(len(checks), len(set(checks)))
                expected = [i for i in id_list(row["Indicators"]) if i not in DEFERRED]
                self.assertEqual(sorted(checks), sorted(expected))

    def test_principles_are_those_of_the_indicators(self):
        for item, row in self.summary.items():
            with self.subTest(item):
                principles = id_list(row["Principles"])
                self.assertTrue(principles)
                self.assertEqual(
                    sorted(principles), sorted({principle(i) for i in id_list(row["Indicators"])})
                )

    def test_not_applicable_indicators_are_out_of_scope_with_an_action(self):
        self.assertEqual(sorted(self.out_of_scope), sorted(NOT_APPLICABLE))
        for indicator, row in self.out_of_scope.items():
            with self.subTest(indicator):
                self.assertIn(row["Reason"].strip("`"), NOT_APPLICABLE_REASONS)
                self.assertGreater(len(row["Repository-level action"]), 20)
        self.assertRegex(self.text, r"(?m)^## Out of scope for headers$")

    def test_core_fields_exist(self):
        for item, row in self.summary.items():
            with self.subTest(item):
                fields = code_spans(row["Core fields"])
                self.assertTrue(fields, "an item needs at least one core field")
                for name in fields:
                    if name.startswith("FHR:"):
                        self.assertIn(name[4:].split(".")[0], self.fhr_properties, name)
                    else:
                        self.assertIn(name.split(".")[0], self.core_slots, name)

    def test_examples_cover_two_conventions_and_two_file_types(self):
        for item in ITEMS:
            rows = self.examples[item]
            with self.subTest(item):
                for row in rows:
                    self.assertIn(row["Convention"], CONVENTIONS, row)
                    self.assertIn(row["File type"], FILE_TYPES, row)
                    self.assertIn(row["Kind"], KINDS, row)
                    self.assertIn(row["Key"], KEYS, row)
                    self.assertEqual(len(code_spans(row["Example"])), 1, row)
                self.assertGreaterEqual(len({row["Convention"] for row in rows}), 2)
                self.assertGreaterEqual(len({row["File type"] for row in rows}), 2)

    def test_surveyed_examples_cite_a_survey_file_that_contains_them(self):
        for item in ITEMS:
            for row in self.examples[item]:
                line = code_spans(row["Example"])[0]
                source = row["Source"].strip("`")
                with self.subTest(item=item, line=line):
                    if row["Kind"] == "illustrative":
                        self.assertEqual(source, "illustrative")
                        continue
                    evidence = SURVEY / f"{source}.txt"
                    self.assertTrue(evidence.is_file(), f"no survey file {source}")
                    lines = evidence.read_text(encoding="utf-8").splitlines()
                    self.assertIn(line, lines, f"{source} has no line {line!r}")

    def test_core_keys_are_core_field_names(self):
        """A core field name is used as a native key only where the format has none."""
        for item in ITEMS:
            for row in self.examples[item]:
                line = code_spans(row["Example"])[0]
                with self.subTest(item=item, line=line):
                    key = example_key(row["Convention"], line)
                    self.assertIsNotNone(key, f"cannot read the key of {line!r}")
                    if row["Key"] == "core":
                        self.assertNotEqual(row["Convention"], "FAIR-bioHeaders")
                        self.assertEqual(row["Kind"], "illustrative")
                        self.assertIn(key, self.core_slots)
                    if row["Convention"] == "FAIR-bioHeaders":
                        self.assertIn(key, self.core_slots | self.fhr_properties | {"@context"})

    def test_illustrative_values_are_placeholders_not_invented(self):
        """Illustrative lines with a free value use a labelled <placeholder>."""
        for item in ITEMS:
            for row in self.examples[item]:
                line = code_spans(row["Example"])[0]
                if row["Kind"] != "illustrative":
                    continue
                with self.subTest(item=item, line=line):
                    self.assertRegex(line, r"<[^<>]*\s[^<>]*>", "use a labelled <placeholder>")

    def test_status_and_attribution(self):
        head = "\n".join(self.text.splitlines()[:15])
        self.assertRegex(head, r"(?i)\*\*Status\*\*: guidance")
        self.assertIn("changes no schema", head)
        flat = " ".join(self.text.split())
        self.assertIn(ATTRIBUTION, flat)
        self.assertIn("MPL-2.0", flat)


if __name__ == "__main__":
    unittest.main()
