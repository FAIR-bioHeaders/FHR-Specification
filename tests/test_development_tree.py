# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The FHR development tree classification (docs/DEVELOPMENT-TREE.md)."""

import json
import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_development_tree as tree  # noqa: E402


class DevelopmentTreeTests(unittest.TestCase):
    def test_external_agreement_cannot_bypass_frozen_bytes_or_classification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "fhr.json").write_bytes(b"edited\n")
            (root / "examples").mkdir()
            (root / "examples/unclassified.json").write_bytes(b"{}\n")
            pins = {"fhr.json": tree.digest(b"frozen\n")}
            for args in (["--shared", str(root)], ["--remote", "--ref", "main"]):
                stderr = io.StringIO()
                with self.subTest(args=args), mock.patch.object(tree, "ROOT", root), \
                        mock.patch.object(tree, "PUBLISHED", pins), \
                        mock.patch.object(tree, "check_remote", return_value=[]), \
                        contextlib.redirect_stderr(stderr):
                    self.assertEqual(tree.main(args), 1)
                self.assertIn("changed published file: fhr.json", stderr.getvalue())
                self.assertIn("unexpected published file", stderr.getvalue())

    def test_external_comparison_accepts_locally_pinned_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "fhr.json").write_bytes(b"frozen\n")
            with mock.patch.object(tree, "ROOT", root), \
                    mock.patch.object(tree, "PUBLISHED", {"fhr.json": tree.digest(b"frozen\n")}), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(tree.main(["--shared", str(root)]), 0)

    def test_external_modes_are_mutually_exclusive(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            tree.main(["--shared", ".", "--remote"])
        self.assertEqual(error.exception.code, 2)

    def test_hidden_root_json_is_not_a_published_schema(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".editor.json").write_bytes(b"{}\n")
            self.assertEqual(tree.unexpected_published(root, {}), [])

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

    def test_no_unexpected_published_files(self):
        self.assertEqual(tree.unexpected_published(ROOT), [])

    def test_extra_file_in_strict_directory_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "jsonld").mkdir()
            (root / "jsonld" / "fhr.context.jsonld").write_text("{}\n")
            (root / "jsonld" / "new-vocabulary.jsonld").write_text("{}\n")
            (root / "examples" / "fhp").mkdir(parents=True)
            (root / "examples" / "fhp" / "unclassified.fhp.yaml").write_text("{}\n")
            digest = tree.digest(b"{}\n")
            problems = tree.check_published(
                root, {"jsonld/fhr.context.jsonld": digest})
            self.assertTrue(any(
                p.startswith("unexpected published file: "
                             "jsonld/new-vocabulary.jsonld")
                for p in problems))
            self.assertTrue(any(
                p.startswith("unexpected published file: "
                             "examples/fhp/unclassified.fhp.yaml")
                for p in problems))
            self.assertEqual(len(problems), 2)

    def test_extra_root_schema_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "fhr.json").write_text("{}\n")
            (root / "fht.json").write_text("{}\n")
            problems = tree.check_published(
                root, {"fhr.json": tree.digest(b"{}\n")})
            self.assertEqual(
                problems,
                ["unexpected published file: fht.json (not in the published "
                 "set; classify it with its shared-copy digest or move it out "
                 "of the published location)"])

    def test_hidden_files_in_strict_directories_are_ignored(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "jsonld").mkdir()
            (root / "jsonld" / ".DS_Store").write_bytes(b"local\n")
            self.assertEqual(tree.unexpected_published(root, {}), [])

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


    def test_pin_is_the_current_release(self):
        # The published copies follow the released shared contract, so the pin
        # is the release that schemas/versions.json names as current.
        versions = json.loads((ROOT / "schemas" / "versions.json").read_text(encoding="utf-8"))
        self.assertEqual(tree.SHARED_TAG, versions["current"])
        self.assertRegex(tree.SHARED_COMMIT, r"^[0-9a-f]{40}$")

    def test_remote_comparison_reads_the_pinned_tag(self):
        requested = []

        class Response:
            def __init__(self, url):
                requested.append(url)
                self.url = url

            def __enter__(self):
                return self

            def __exit__(self, *arguments):
                return False

            def read(self):
                return b"same\n"

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in tree.PUBLISHED:
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_bytes(b"same\n")
            with mock.patch.object(tree.urllib.request, "urlopen",
                                   lambda request, timeout: Response(request.full_url)):
                self.assertEqual(tree.check_remote(root), [])
                self.assertEqual(len(requested), len(tree.PUBLISHED))
                self.assertTrue(all(
                    url.startswith(f"{tree.RAW_BASE}/{tree.SHARED_TAG}/") for url in requested))
                requested.clear()
                self.assertEqual(tree.check_remote(root, "main"), [])
                self.assertTrue(all(url.startswith(f"{tree.RAW_BASE}/main/") for url in requested))

if __name__ == "__main__":
    unittest.main()
