"""Exercise the conformance vectors, their generator and their checker."""

import gzip
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONFORMANCE = ROOT / "conformance"


def run(*arguments):
    return subprocess.run([sys.executable, *map(str, arguments)], capture_output=True, text=True)


class ConformanceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.manifest = json.loads((CONFORMANCE / "manifest.json").read_text())

    def check(self, *extra, conformance=CONFORMANCE):
        return run(ROOT / "scripts/check_conformance.py", "--conformance", conformance, *extra)

    def copy_vectors(self):
        copy = self.root / "conformance"
        shutil.copytree(CONFORMANCE, copy)
        return copy

    def test_committed_vectors_pass_stdlib_and_schema_checks(self):
        result = self.check("--schema")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ok: vectors match the generator", result.stdout)
        self.assertIn("ok: valid metadata matches fhr.json", result.stdout)

    def test_generator_is_deterministic(self):
        outputs = [self.root / "first", self.root / "second"]
        for output in outputs:
            result = run(ROOT / "scripts/make_conformance.py", "--output", output)
            self.assertEqual(result.returncode, 0, result.stderr)
        first, second = ({path.relative_to(output): path.read_bytes()
                          for path in output.rglob("*") if path.is_file()} for output in outputs)
        self.assertEqual(first, second)

    def test_modified_vector_is_reported(self):
        copy = self.copy_vectors()
        vector = copy / "valid/fasta-lf.fhr.fasta"
        vector.write_bytes(vector.read_bytes().replace(b"ACGT", b"ACGA", 1))
        result = self.check(conformance=copy)
        self.assertEqual(result.returncode, 1)
        self.assertIn("valid/fasta-lf.fhr.fasta: differs from the generator output", result.stderr)
        self.assertIn("fasta-lf: manifest", result.stderr)

    def test_line_ending_normalization_is_reported(self):
        copy = self.copy_vectors()
        vector = copy / "valid/gfa-crlf.fhr.gfa"
        vector.write_bytes(vector.read_bytes().replace(b"\r\n", b"\n"))
        result = self.check("--skip-regeneration", conformance=copy)
        self.assertEqual(result.returncode, 1)
        self.assertIn("gfa-crlf: manifest", result.stderr)

    def test_extra_file_is_reported(self):
        copy = self.copy_vectors()
        (copy / "invalid/stray.fhr.fasta").write_bytes(b">x\nA\n")
        result = self.check(conformance=copy)
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid/stray.fhr.fasta: not produced by the generator", result.stderr)

    def test_every_rule_is_labelled_and_covered(self):
        labels = [label for document in ("docs/FORMAT.md", "docs/MICRODATA.md")
                  for label in re.findall(r"\[([RM]\d+)\]", (ROOT / document).read_text())]
        self.assertEqual(labels, list(self.manifest["rules"]))
        for rule, details in self.manifest["rules"].items():
            outcomes = {
                vector["expected"] for vector in self.manifest["vectors"]
                if rule in vector.get("rules", [vector.get("rule")])
            }
            expected = set() if "notApplicable" in details else {"valid", "invalid"}
            self.assertEqual(outcomes, expected, rule)

    def test_manifest_fields(self):
        required = json.loads((ROOT / "fhr.json").read_text())["required"]
        for vector in self.manifest["vectors"]:
            self.assertIn(vector["format"], {"fasta", "gfa", "microdata"})
            self.assertTrue((CONFORMANCE / vector["file"]).is_file(), vector["file"])
            self.assertEqual(vector["file"].split("/")[0], vector["expected"])
            if vector["format"] == "microdata":
                self.assertTrue(vector["file"].endswith(".html"), vector["file"])
                self.assertNotIn("checksum", vector)
                if vector["expected"] == "valid":
                    self.assertTrue(set(required) <= vector["metadata"].keys(), vector["id"])
                else:
                    self.assertTrue(vector["reason"])
                continue
            if vector["expected"] == "valid":
                self.assertRegex(vector["checksum"], r"^[A-Za-z0-9+/]{43}=$")
                self.assertTrue({"genome", "version"} <= vector["metadata"].keys())
            else:
                self.assertIn(vector["rule"], self.manifest["rules"])
                self.assertTrue(vector["reason"])

    def test_compressed_vectors_share_the_plain_checksum(self):
        vectors = {vector["id"]: vector for vector in self.manifest["vectors"]}
        compressed = [vector for vector in vectors.values()
                      if vector["compressed"] and vector["expected"] == "valid"]
        self.assertGreaterEqual(len(compressed), 4)
        for vector in compressed:
            kind = vector["format"]
            plain = vectors[f"{kind}-lf"]
            data = (CONFORMANCE / vector["file"]).read_bytes()
            self.assertEqual(data[3] & 0x08, 0, "no stored file name")
            self.assertEqual(data[4:8], b"\0\0\0\0", "mtime 0")
            self.assertEqual(gzip.decompress(data), (CONFORMANCE / plain["file"]).read_bytes())
            self.assertEqual(vector["checksum"], plain["checksum"])

    def test_converter_that_accepts_everything_fails(self):
        bin_directory = self.root / "bin"
        bin_directory.mkdir()
        for name in ("fhr-fasta-validate", "fhr-gfa-validate"):
            script = bin_directory / name
            script.write_text(f"#!{sys.executable}\nraise SystemExit(0)\n")
            script.chmod(0o755)
        # A converter that extracts only the genome from every HTML file.
        script = bin_directory / "fhr-convert"
        script.write_text(f"#!{sys.executable}\nimport sys\n"
                          "open(sys.argv[2], 'w').write('{\"genome\": \"Synthetic FHR "
                          "conformance genome\"}')\n")
        script.chmod(0o755)
        result = self.check("--skip-regeneration", "--converter", bin_directory)
        self.assertEqual(result.returncode, 1)
        self.assertIn("fasta-u2028-in-header: converter accepted; expected invalid, R6",
                      result.stderr)
        self.assertIn("microdata-type-mismatch: converter accepted; expected invalid, M3",
                      result.stderr)
        self.assertIn("microdata-canonical: converter extracted different metadata for "
                      "assemblyAuthor,", result.stderr)
        self.assertNotIn("fasta-lf:", result.stderr)

    @unittest.skipUnless(os.environ.get("FHR_CONVERTER"), "set FHR_CONVERTER to test a converter")
    def test_converter_agrees_with_manifest(self):
        result = self.check("--skip-regeneration", "--converter", os.environ["FHR_CONVERTER"])
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
