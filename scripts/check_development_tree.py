# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Check the FHR development tree classification (docs/DEVELOPMENT-TREE.md).

This repository develops the FHR header; the released specification publishes
from FAIR-bioHeaders-Specification. The tree still carries a copy of the family
publication tree, so this check encodes which files may be edited here and which
are compatibility copies that must stay byte-identical to the shared repository.

Only the standard library is used. By default the check is offline: it compares
each published file against the recorded SHA-256 of its shared copy, rejects
unclassified files in a strict published location, and lists the files
classified as removable. ``--shared PATH`` compares against a local
FAIR-bioHeaders-Specification checkout instead, and ``--remote`` against its
raw ``main`` over the network (as .github/workflows/published-files.yml does).

The published set and the digests mirror FAIR-bioHeaders-Specification main; the
``published-files`` workflow checks the same files live. Keep this file and
docs/DEVELOPMENT-TREE.md in sync when a file changes section.
"""

import argparse
import hashlib
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SHARED_REPOSITORY = "FAIR-bioHeaders-Specification"
RAW_MAIN = ("https://raw.githubusercontent.com/FAIR-bioHeaders/"
            + SHARED_REPOSITORY + "/main")

# Section 2 of docs/DEVELOPMENT-TREE.md: directories whose entire contents are
# published. Every file below one of these does not have to be listed in
# PUBLISHED explicitly to be checked, but an unlisted file is an unexpected
# published path: either classify it (with its digest) or move it elsewhere.
STRICT_DIRECTORIES = ("examples", "jsonld")

# The only root-level JSON schemas that serve published URLs. The root holds
# other file types, but a fourth root-level ``*.json`` schema is an unexpected
# published path until it is classified here and in PUBLISHED.
ROOT_SCHEMAS = ("fhr.json", "fhp.json", "fhgff3.json")

# Section 2 of docs/DEVELOPMENT-TREE.md: files that serve established raw-main,
# tag or Pages URLs, or are published companion copies. Each value is the
# SHA-256 of the file in FAIR-bioHeaders-Specification main. A file that is
# missing here, or whose bytes differ, fails the check.
PUBLISHED = {
    "fhr.json": "694ab5afaf8c3743eacf9e2aacb5551f7cbe37073b6f4afc3ae4a65b47f9d4df",
    "fhp.json": "2409739d4a223164ca368f93afa78c8f1e3809fb04ec46cc9a793cc5aaaba427",
    "fhgff3.json": "20ce320f5d706f11ed21cdece4dfb56e3568b50be126e25b4016f46f2e8e416c",
    "jsonld/fhr.context.jsonld": "5e19e1a36797f2457316a28f89b1aeac39e23a5796696027346c591fc1565f51",
    "jsonld/terms.jsonld": "37457fe381ad473916213be850ba21c335a79b28dae0899bcd0d2cdb1473fd0f",
    "jsonld/terms.ttl": "e85c9867e640809b8c0de366255c1db2beaf1d90b9313e22e8e95ede21a0bbeb",
    "assessment/manifest.schema.json": "a5b5f2cfca0ff3ec40fd577e992754157e25827d8d3c24c507dcf65eb77492e2",
    "mappings/mapping-table.schema.json": "33f51dcf776bbce216035b7fe50956d4b2a3ee1c54280ecc3e3818f3d7a54eb9",
    "specs/013-schemaorg-export/contracts/export-table.schema.json": "d43d699a0c60d19ca3da596764101ad7f9299a309c70430a6244d66ec61ea911",
    "examples/example.fhr.export.jsonld": "43665f3293945813290138b7e4dbac6ed6a7ba4a33605b0be26d01e36ff4a920",
    "examples/example.fhr.fasta": "2a948f5062ed9a618d7850e5e8d4e75bc5ca5abed5f9e5e6b77cf9f1778616ab",
    "examples/example.fhr.gfa": "0d0c42d9c9a7f83472697622c83f17afe878a7f4bf05ed4eb7a01080064c8c16",
    "examples/example.fhr.json": "bd26248f11a96128f0ae7cb68fdeea3b942f9bb1f833e08b0c9fbe20dab3dd89",
    "examples/example.fhr.jsonld": "2727130320249e3acda1920323d9d772b942981de5b36ca5a13bbc54bcffd4af",
    "examples/example.fhr.yaml": "b91b570124a01dc73f04780d4b1d5d1c23404d9af810b7525f49e50db67f7735",
    "examples/extension-fields.fhr.yaml": "c10ee133d2d0997fc0e2b0cf1755a93674adbb0dbee01a399925530fbf6ef66e",
    "examples/example.microdata.fhr.html": "2ec01c66861bc4728981e882c63ee7a95106c508bc957419f60135e8b994ff36",
    "examples/fhgff3/annotation.fhgff3.gff3": "04b8daf3d53b313f9c192821ae9108716962538b04cb1484cbf624c954c6174c",
    "examples/fhgff3/annotation.fhgff3.yaml": "9b3482bef7f60a421152bd5d2de3e0185c8437de6e14ac8fac0497b7bede32bf",
    "examples/fhgff3/embedded-fasta.fhgff3.gff3": "a11c3dc1b98f2e04d7442091ef68d59424327d19dee392d86c475cab842b0f32",
    "examples/fhgff3/genome.fhr.fasta": "4eb16531a3c0c87a2a06fe84c3739bd9563bd77e18951c8233610b6a89984d19",
    "examples/fhgff3/header-invalid.fhgff3.gff3": "d73a3466a03217e17579ba86fb145cc2a3466fd8ac136c34a219adf3d75b0708",
    "examples/fhgff3/minimal-reference.fhgff3.json": "ba128038f5545de509a5096e2dff4edeacad797fb919e96d70409287665f6d2a",
    "examples/fhgff3/no-header.gff3": "d2f0e995edd2e9cb48f02661b8253e198c56c79de185feeb8482d19e469d36d6",
    "examples/fhgff3/rich.fhgff3.yaml": "fc8310e0565a533a1e6107d91bb81e6e9368d78547d383e5de00cccffd2c171f",
    "examples/fhgff3/stale-parent.fhgff3.gff3": "c1003eff5842ad49018d4583f04323abf1e64f21e12ff887e212c9f8d6254761",
    "examples/fhp/example.fhp.fasta": "baceab7d1dfbb99f7cdcfe85492314486a0af9e301de572f7d67d0c7eb4426a2",
    "examples/fhp/minimal-database.fhp.json": "fdc6eb7ef7e81d95dc4bc29bf051bd5523129fc0f8599ee04862289e23d9da8b",
    "examples/fhp/minimal-mixed.fhp.json": "5594c9605864f89edccfab1e19b6fff9d24976ec0f17ce1405ad3b5ee3791864",
    "examples/fhp/minimal-predicted.fhp.json": "dfec7c7055195b80c84e71c1d9ca322fb4b55545f7da7e57390183037ad18acd",
    "examples/fhp/rich-database.fhp.json": "cef3cb277ea1385c8c5c16da9f185ac19cca025e54778646c75c09794005f9aa",
    "examples/fhp/rich-mixed.fhp.yaml": "a9d0a4ff3f552aaf64c0c15c858f192d838d645ae2b10b60a827bc8a053e8ee2",
    "examples/fhp/rich-predicted.fhp.yaml": "b7efdbc301288986612d961f27cfbbcf709c600d7f45dc0d4e82f1ea6d8ab2e9",
    "examples/minimal.fhr.json": "9926b7ffd6698b664a196b5087e81d413c270bef21a6b85f3b302e4274490379",
    "examples/minimal.fhr.jsonld": "9dc801f79341fe1ea820a4a8d5d2eca64034c6c24de5b68f9c68fc8479cfbc0f",
}

# Section 4 of docs/DEVELOPMENT-TREE.md: candidates assessed for removal. This
# change classifies and defers removals and deletes nothing: every candidate is
# either agent tooling, historical design provenance, or URL-served. The tuple
# stays so a later, separately reviewed change can add a path and have the check
# enforce that it stays gone (with --strict failing while it is present).
REMOVABLE = ()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def unexpected_published(root, published=PUBLISHED):
    """Published-location files that ``published`` does not classify.

    The whole of each strict directory is published, so a new file there must
    get a digest instead of silently escaping the check. Root-level ``*.json``
    schemas are held to the same rule. Hidden files are ignored (they are local
    editor/OS droppings, not part of the published tree).
    """
    unexpected = set()
    for directory in STRICT_DIRECTORIES:
        base = root / directory
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            if any(part.startswith(".") for part in relative.parts):
                continue
            name = relative.as_posix()
            if name not in published:
                unexpected.add(name)
    for path in root.glob("*.json"):
        if path.is_file() and path.name not in ROOT_SCHEMAS:
            unexpected.add(path.name)
    return sorted(unexpected)


def check_published(root, published=PUBLISHED):
    """Problems with the published set: missing, changed or unclassified files."""
    problems = []
    for name, expected in sorted(published.items()):
        path = root / name
        if not path.is_file():
            problems.append(f"missing published file: {name}")
            continue
        actual = digest(path.read_bytes())
        if actual != expected:
            problems.append(
                f"changed published file: {name} (expected {expected[:12]}…, "
                f"got {actual[:12]}…); synchronize the shared main copy")
    for name in unexpected_published(root, published):
        problems.append(
            f"unexpected published file: {name} (not in the published set; "
            "classify it with its shared-copy digest or move it out of the "
            "published location)")
    return problems


def check_shared(root, shared):
    """Problems comparing the published set with a local shared checkout."""
    problems = []
    for name in sorted(PUBLISHED):
        local, remote = root / name, shared / name
        if not local.is_file():
            problems.append(f"missing published file: {name}")
        elif not remote.is_file():
            problems.append(f"shared copy missing (cannot compare): {name}")
        elif local.read_bytes() != remote.read_bytes():
            problems.append(f"published file differs from the shared copy: {name}")
    return problems


def check_remote(root, base=RAW_MAIN):
    """Problems comparing the published set with raw shared main over the network."""
    problems = []
    for name in sorted(PUBLISHED):
        local = root / name
        if not local.is_file():
            problems.append(f"missing published file: {name}")
            continue
        request = urllib.request.Request(
            f"{base}/{name}", headers={"User-Agent": "fhr-development-tree-check"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                remote = response.read()
        except (urllib.error.URLError, OSError) as error:
            problems.append(f"cannot fetch the shared copy of {name}: {error}")
            continue
        if local.read_bytes() != remote:
            problems.append(f"published file differs from shared main: {name}")
    return problems


def removable_present(root, removable=REMOVABLE):
    """The classified-removable files that are still in the tree."""
    return [name for name in removable if (root / name).exists()]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--shared", type=Path,
                        help="compare the published set with a local "
                             f"{SHARED_REPOSITORY} checkout")
    parser.add_argument("--remote", action="store_true",
                        help="compare the published set with raw shared main over "
                             "the network")
    parser.add_argument("--strict", action="store_true",
                        help="also fail when a classified-removable file is "
                             "present (no additional effect while REMOVABLE is "
                             "empty)")
    parser.add_argument("--list", action="store_true",
                        help="only list the classification and exit")
    args = parser.parse_args(argv)

    present = removable_present(ROOT)
    if args.list:
        print(f"{len(PUBLISHED)} published/URL-served files; "
              f"strict directories: {', '.join(STRICT_DIRECTORIES)}; "
              f"{len(REMOVABLE)} classified removable")
        for name in REMOVABLE:
            state = "present" if name in present else "removed"
            print(f"  removable ({state}): {name}")
        if not REMOVABLE:
            print("  none classified; removals are deferred to a later change")
        return 0

    if args.shared:
        problems = check_shared(ROOT, args.shared)
    elif args.remote:
        problems = check_remote(ROOT)
    else:
        problems = check_published(ROOT)
    if args.strict and present:
        problems += [f"classified-removable file is still present: {name}"
                     for name in present]

    for problem in problems:
        print(f"development-tree check: {problem}", file=sys.stderr)
    for name in present:
        print(f"present: removable candidate {name}")
    if problems:
        print(f"{len(problems)} problem(s); see docs/DEVELOPMENT-TREE.md", file=sys.stderr)
        return 1
    if REMOVABLE:
        removals = (f"{len(REMOVABLE) - len(present)} of {len(REMOVABLE)} "
                    f"classified-removable file(s) removed ({len(present)} still "
                    "present)")
    else:
        removals = "no files classified removable yet (removals deferred)"
    print(f"ok: {len(PUBLISHED)} published files match their shared copy; "
          f"{removals}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
