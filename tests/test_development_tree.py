# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The FHR development tree classification (docs/DEVELOPMENT-TREE.md)."""

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_development_tree as tree  # noqa: E402


class DevelopmentTreeTests(unittest.TestCase):
    def test_published_files_match_their_recorded_shared_digests(self):
        self.assertEqual(tree.check_published(ROOT), [])

    def test_classified_removable_files_are_gone(self):
        self.assertEqual(tree.removable_present(ROOT), [])

    def test_development_tree_document_exists(self):
        text = (ROOT / "docs" / "DEVELOPMENT-TREE.md").read_text(encoding="utf-8")
        self.assertIn("FAIR-bioHeaders-Specification", text)
        self.assertIn("issues/107", text)
        self.assertIn("must stay byte-identical", text)
        self.assertIn("removable", text.lower())

    def test_missing_published_file_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            problems = tree.check_published(root, {"fhr.json": "0" * 64})
            self.assertEqual(len(problems), 1)
            self.assertIn("missing published file: fhr.json", problems[0])

    def test_changed_published_file_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "fhr.json").write_text("{}\n")
            problems = tree.check_published(root, {"fhr.json": "0" * 64})
            self.assertEqual(len(problems), 1)
            self.assertIn("changed published file: fhr.json", problems[0])

    def test_shared_comparison_detects_a_difference(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            local, shared = base / "local", base / "shared"
            for name in tree.PUBLISHED:
                (local / name).parent.mkdir(parents=True, exist_ok=True)
                (local / name).write_text("local\n")
                (shared / name).parent.mkdir(parents=True, exist_ok=True)
                (shared / name).write_text("shared\n")
            self.assertTrue(tree.check_shared(local, shared))
            (shared / "fhr.json").write_text("local\n")
            self.assertFalse(
                [p for p in tree.check_shared(local, shared) if p.endswith(": fhr.json")])


if __name__ == "__main__":
    unittest.main()
