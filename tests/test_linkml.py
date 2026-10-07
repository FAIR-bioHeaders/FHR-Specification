import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_linkml import constraints
from project_mixs import project

spec = importlib.util.spec_from_file_location(
    "generator", ROOT / "json-schema-generator.py"
)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class LinkMLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published = json.loads((ROOT / "fhr.json").read_text())
        cls.generated = generator.generate()
        cls.example = json.loads((ROOT / "examples/example.fhr.json").read_text())

    def test_all_validation_constraints_match(self):
        self.assertEqual(
            constraints(self.published, self.published),
            constraints(self.generated, self.generated),
        )

    def test_generated_schema_accepts_minimal_rich_and_legacy_software(self):
        validator = Draft202012Validator(self.generated, format_checker=FormatChecker())
        validator.check_schema(self.generated)
        validator.validate(self.example)
        validator.validate(
            {key: self.example[key] for key in self.published["required"]}
        )
        legacy = copy.deepcopy(self.example)
        legacy["assemblySoftware"] = "hifiasm"
        validator.validate(legacy)

    def test_invalid_cases_fail_both_schemas(self):
        for key, value in [
            ("seqcol_id", "wrong"),
            ("vitalStats", {"gcContent": -1}),
            ("metadataAuthor", [{"name": "test", "uri": 7}]),
            ("assemblySoftware", [{"version": "1"}]),
            ("checksum", "A" * 43 + "\n"),
        ]:
            with self.subTest(key=key):
                instance = copy.deepcopy(self.example)
                instance[key] = value
                for schema in (self.published, self.generated):
                    self.assertFalse(
                        Draft202012Validator(
                            schema, format_checker=FormatChecker()
                        ).is_valid(instance)
                    )

    def test_projection_and_omissions(self):
        projection = project(self.example)
        self.assertEqual(projection["target_version"], "v7.0.1")
        self.assertEqual(
            projection["metadata"],
            {
                "number_contig": 1,
                "sop": "https://example.org/assembly-protocol",
                "assembly_software": "hifiasm;0.19.8;-t 2",
            },
        )
        self.assertEqual(projection["unmapped"], {})
        self.assertNotIn("assembly_accession", projection["metadata"])
        for software in (
            "legacy",
            [{"name": "tool"}],
            self.example["assemblySoftware"] * 2,
        ):
            instance = copy.deepcopy(self.example)
            instance["assemblySoftware"] = software
            self.assertIn("assembly_software", project(instance)["unmapped"])

    def test_unmapped_source_fields_are_not_invented(self):
        minimal = {key: self.example[key] for key in self.published["required"]}
        projection = project(minimal)
        self.assertEqual(projection["metadata"], {})
        self.assertEqual(
            set(projection["unmapped"]), {"assembly_software", "sop", "number_contig"}
        )


if __name__ == "__main__":
    unittest.main()
