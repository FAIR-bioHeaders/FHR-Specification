# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The shared FAIR header assessment fixtures and their manifest (feature 010)."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ASSESSMENT = ROOT / "assessment"
GENERATOR = ROOT / "scripts" / "make_assessment_fixtures.py"
FIXTURE_DIRECTORIES = ("headers", "pairs", "edge")
GENERATED_DIRECTORIES = ("pairs", "edge")


def tree(directory, subdirectories):
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for name in subdirectories
        for path in sorted((directory / name).rglob("*"))
        if path.is_file() and path.name != ".gitkeep"
    }


class AssessmentFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ASSESSMENT / "manifest.json").read_text(encoding="utf-8"))
        cls.schema = json.loads((ASSESSMENT / "manifest.schema.json").read_text(encoding="utf-8"))

    def test_manifest_validates_against_its_schema(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:  # pragma: no cover - requirements-validation.txt has it
            self.skipTest("jsonschema is not installed")
        Draft202012Validator.check_schema(self.schema)
        errors = sorted(Draft202012Validator(self.schema).iter_errors(self.manifest), key=str)
        self.assertEqual([], [f"{list(e.absolute_path)}: {e.message}" for e in errors])

    def test_every_fixture_file_is_listed_once(self):
        listed = [entry["file"] for entry in self.manifest["fixtures"]]
        self.assertEqual(len(listed), len(set(listed)), "a file is listed twice")
        on_disk = set(tree(ASSESSMENT, FIXTURE_DIRECTORIES))
        related = {entry["related"] for entry in self.manifest["fixtures"] if "related" in entry}
        self.assertEqual(sorted(on_disk - set(listed) - related), [], "files not in the manifest")
        self.assertEqual(sorted(set(listed) - on_disk), [], "manifest entries without a file")
        self.assertEqual(sorted(related - on_disk), [], "related files that do not exist")

    def test_ids_are_unique(self):
        ids = [entry["id"] for entry in self.manifest["fixtures"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_provenance(self):
        for entry in self.manifest["fixtures"]:
            with self.subTest(entry["id"]):
                if entry["file"].startswith("headers/"):
                    self.assertTrue(entry["source_url"].startswith("https://"))
                    self.assertRegex(entry["fetched"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z$")
                    self.assertNotIn("generator", entry)
                else:
                    self.assertEqual(entry["generator"], "scripts/make_assessment_fixtures.py")
                    self.assertNotIn("source_url", entry)

    def test_real_captures_keep_no_survey_annotations(self):
        for path in sorted((ASSESSMENT / "headers").iterdir()):
            if path.suffix == ".gz" or path.name == ".gitkeep":
                continue
            with self.subTest(path.name):
                text = path.read_bytes().decode("utf-8")
                for marker in ("# SOURCE-URL", "# FETCHED", "----- captured header lines", "[ELIDED"):
                    self.assertNotIn(marker, text)

    def test_generator_is_deterministic_and_matches_the_committed_files(self):
        outputs = []
        for _ in range(2):
            directory = tempfile.TemporaryDirectory()
            self.addCleanup(directory.cleanup)
            result = subprocess.run(
                [sys.executable, str(GENERATOR), "--output", directory.name],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            outputs.append(tree(Path(directory.name), GENERATED_DIRECTORIES))
        self.assertEqual(outputs[0], outputs[1])
        committed = tree(ASSESSMENT, GENERATED_DIRECTORIES)
        self.assertEqual(sorted(outputs[0]), sorted(committed))
        for name, content in outputs[0].items():
            self.assertEqual(content, committed[name], f"{name} differs from the generator output")


if __name__ == "__main__":
    unittest.main()
