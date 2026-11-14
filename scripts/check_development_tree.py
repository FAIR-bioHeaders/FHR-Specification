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
    "fhp.json": "92a0b3cbcfe69939ebfaac69f0c5958ce426c005873efe8d3e3eb0fc0dab6de5",
    "fhgff3.json": "1942be4cefc8b3a2537942c2252b45fbcef87a5532486e4fd0f5d4c540e0fbf9",
    "jsonld/fhr.context.jsonld": "5e19e1a36797f2457316a28f89b1aeac39e23a5796696027346c591fc1565f51",
    "jsonld/terms.jsonld": "37457fe381ad473916213be850ba21c335a79b28dae0899bcd0d2cdb1473fd0f",
    "jsonld/terms.ttl": "e85c9867e640809b8c0de366255c1db2beaf1d90b9313e22e8e95ede21a0bbeb",
    "assessment/manifest.schema.json": "a5b5f2cfca0ff3ec40fd577e992754157e25827d8d3c24c507dcf65eb77492e2",
    "mappings/mapping-table.schema.json": "33f51dcf776bbce216035b7fe50956d4b2a3ee1c54280ecc3e3818f3d7a54eb9",
    "specs/013-schemaorg-export/contracts/export-table.schema.json": "d43d699a0c60d19ca3da596764101ad7f9299a309c70430a6244d66ec61ea911",
    "examples/example.fhr.export.jsonld": "908dd1007b9d6d56291dd4251df9ee863b288e1eacdf1207f3694fa45a87db71",
    "examples/example.fhr.fasta": "8f45dd786a623071921d278c2392dd4e28638774498f9b8ac356086c3cb34496",
    "examples/example.fhr.gfa": "1f382b5fa87a68f4409c7dc10be258e231b119a81922906e6723e941a46688a0",
    "examples/example.fhr.json": "fbbba44a15e12cbb1371beebefc666bb6fb58f4977799d4a2e11af2784a8e6e9",
    "examples/example.fhr.jsonld": "cafc34dd3710bc8622d21f87f90a102ce1691a683471abddcea92550dca26087",
    "examples/example.fhr.yaml": "dab7fca71f16df0ac9048463b2b19447f58b2524dbaada38c62e918dfece5470",
    "examples/extension-fields.fhr.yaml": "6df15a7b7b66c264ccacf96c8088935904e4e40c97aaa5ebff643ed21345b6f6",
    "examples/example.microdata.fhr.html": "15025b6c752e8bfc565656371eb0ee7cad60169f47291aa4c5f0a52458c24107",
    "examples/fhgff3/annotation.fhgff3.gff3": "7754357bd2280306b45cdbc804850fc59a52e79487483f2f9e2e7f0dda9fb437",
    "examples/fhgff3/annotation.fhgff3.yaml": "417fd8b9f831b05041bfa1d3d216ea9199697212195c0990873ab6e6884b20d7",
    "examples/fhgff3/embedded-fasta.fhgff3.gff3": "3bacaa2e918e7fd428abb7ba10d31fe86849ebdcf5e86422b4bbc0facb953988",
    "examples/fhgff3/genome.fhr.fasta": "baebcb6a0c9af0b31d8bfe8ac9964864cd7a9bb7341edb922a2b32d14d1b7763",
    "examples/fhgff3/header-invalid.fhgff3.gff3": "940fadf04c49e2e31d44b55c2a06a2845186bcdc4fbf619fef133df21a2f68fe",
    "examples/fhgff3/minimal-reference.fhgff3.json": "01fc3332c3dd070062c36a82d0498fea6dd1ae1283e8e90403086eaf19c7aa9d",
    "examples/fhgff3/no-header.gff3": "d2f0e995edd2e9cb48f02661b8253e198c56c79de185feeb8482d19e469d36d6",
    "examples/fhgff3/rich.fhgff3.yaml": "f25682136de1485e1f12f22010612647dcf47681b018cf5347ea9f52ef7a90bf",
    "examples/fhgff3/stale-parent.fhgff3.gff3": "810d99d62f232c1aad41b5e9d6a474d813343a8903b1f3757da267a2ee925971",
    "examples/fhp/example.fhp.fasta": "151621730e4236012af051206fe451597f56ae2aeb08c97a329e1bbed69059bf",
    "examples/fhp/minimal-database.fhp.json": "2d85b84fb5ab14f60f4e520bef7f37ab380be2169f525c39d0bc7061f9add4a7",
    "examples/fhp/minimal-mixed.fhp.json": "7a92350f908802c4686840e7061299397bc05e5e0c7e0e94494bc9cf5c3bcf59",
    "examples/fhp/minimal-predicted.fhp.json": "87b95f044d0a2a0664c0ace06308e08c0a0738fc889f34263660cff744dbdcfe",
    "examples/fhp/rich-database.fhp.json": "71e4d798bf4ffd45519b4a56a86181b161eae95d73a9d6a9ce1e2d6ae943d3d8",
    "examples/fhp/rich-mixed.fhp.yaml": "cefe56807eb25d7c41101d5d3f9f67c847a3ab8ffdd623e8202ea6f74ee19b31",
    "examples/fhp/rich-predicted.fhp.yaml": "2e4034c739cecd4880db05ad7a7ee066c91b32044c30dcc2ae90ffd1de75f3b5",
    "examples/minimal.fhr.json": "97c875c01be3439d54a4323add9bc07e067064c547ec782e22941892f9ba96ea",
    "examples/minimal.fhr.jsonld": "185eb8139052f5200fec9274456fee60687816450590bf7f60aa96f08f592408",
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
