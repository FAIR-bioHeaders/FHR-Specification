# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Check the FHR development tree classification (docs/DEVELOPMENT-TREE.md).

This repository develops the FHR header; the released specification publishes
from FAIR-bioHeaders-Specification. The tree still carries a copy of the family
publication tree, so this check encodes which files may be edited here and which
are compatibility copies that must stay byte-identical to the shared repository.

Only the standard library is used. By default the check is offline: it compares
each published file against the recorded SHA-256 of its shared copy and lists
the files classified as removable. ``--shared PATH`` compares against a local
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

# Section 2 of docs/DEVELOPMENT-TREE.md: files that serve established raw-main,
# tag or Pages URLs, or are published companion copies. Each value is the
# SHA-256 of the file in FAIR-bioHeaders-Specification main. A file that is
# missing here, or whose bytes differ, fails the check.
PUBLISHED = {
    "fhr.json": "168a60467e3651dfdfe9855747f38257d5889bfcce6ec8661d9a378762a362dd",
    "fhp.json": "e3f8f45260b833f931644e87ff7530cb9b4151e67094023dd96edde9a1d90366",
    "fhgff3.json": "f89635f252f6e204944de99e6c40bad1b0c9b37af5108fce05ee63f6dfd40bbd",
    "jsonld/fhr.context.jsonld": "5e19e1a36797f2457316a28f89b1aeac39e23a5796696027346c591fc1565f51",
    "jsonld/terms.jsonld": "072f509abcbcc7fa3a1572249ac770eb939b3b776521c9836c8cb37496f49c36",
    "jsonld/terms.ttl": "0c641879818a1ce02ed10348b344cb11c37fd86c8a120a9f9bfe8e618d32042c",
    "assessment/manifest.schema.json": "a5b5f2cfca0ff3ec40fd577e992754157e25827d8d3c24c507dcf65eb77492e2",
    "mappings/mapping-table.schema.json": "33f51dcf776bbce216035b7fe50956d4b2a3ee1c54280ecc3e3818f3d7a54eb9",
    "specs/013-schemaorg-export/contracts/export-table.schema.json": "d43d699a0c60d19ca3da596764101ad7f9299a309c70430a6244d66ec61ea911",
    "examples/example.fhr.export.jsonld": "6263db9b7dadd3084e60658ab9d24376f30b9562ae8748c300eba8b7a4a9a6ce",
    "examples/example.fhr.fasta": "ad8fc67864daf0ad592eb6a4013ba681a8b75e304db6ef1c461f47810e60adda",
    "examples/example.fhr.gfa": "7f94a22c2381553f17a628408359479949ac78c07afa3553678b9ff86072a470",
    "examples/example.fhr.json": "78f75c880d69be4797509457b658068eb8cb46ab817986d8e2f442b96f07f0d6",
    "examples/example.fhr.jsonld": "1e9fdc468d139a113e28c1f83d371cf93cd1de103231c593608090ef6a9916ec",
    "examples/example.fhr.yaml": "0c243642cd5b3cb0c152f25b4d0b9b11c1d38ca01dea58c25c638de2bcc8d110",
    "examples/example.microdata.fhr.html": "6b98a46985ba48c7d5283ba29af0eecd93464a3d436a08f8073b92177d7bbc6a",
    "examples/fhgff3/annotation.fhgff3.gff3": "e8dab46b7d94b0f04408a2fcec776ba690a69ac79c19113f6d7e37aa058affd8",
    "examples/fhgff3/annotation.fhgff3.yaml": "751eeb18585fc7a64f84ad6f959266207e11cac2e50c48a2c52071374db11428",
    "examples/fhgff3/embedded-fasta.fhgff3.gff3": "99d3357b48fffc256d5424b357f7cd4503a9eaf14cd436328d3fdc143a476341",
    "examples/fhgff3/genome.fhr.fasta": "860070c7113b86146657241af3992a8a155052dd7f4d41833aca642afdcd41f6",
    "examples/fhgff3/header-invalid.fhgff3.gff3": "e9d1792cd78d4b4a69339d9a73587ef4c4d6b68a3221fe27d2c84591f707cf42",
    "examples/fhgff3/minimal-reference.fhgff3.json": "3805652b537ac72acce017e5d12f91754627590883331031f133e91d74c9ec43",
    "examples/fhgff3/no-header.gff3": "d2f0e995edd2e9cb48f02661b8253e198c56c79de185feeb8482d19e469d36d6",
    "examples/fhgff3/rich.fhgff3.yaml": "43115e7aded6c49610f98e0862264f9589f4308cb8750ead540ef1a6ec3fc0ae",
    "examples/fhgff3/stale-parent.fhgff3.gff3": "a2f394a5a9ddfbe1f773ef58894e4ad1d53a3e8013ac3d099448fa043dafe94e",
    "examples/fhp/example.fhp.fasta": "a7219a5b07666e18317745331f1e4efecc95294252f507a55c3c8be00323653a",
    "examples/fhp/minimal-database.fhp.json": "61d7eed5ed688e348371353260b87e52b32bb2ad07cd85c57b530871c045725c",
    "examples/fhp/minimal-mixed.fhp.json": "3bb6b1d5594b4ad5d24636e0f97c28bb9d49b2a40f77b101e1365f302d868902",
    "examples/fhp/minimal-predicted.fhp.json": "afa97ce4040902ec4451f6a2848ed009d499fba4313f76542094d0f064041cd1",
    "examples/fhp/rich-database.fhp.json": "d9018ca0ddc48efbe04bd2f0159da7d6ee575e59a08e4448d04809921dd66d5b",
    "examples/fhp/rich-mixed.fhp.yaml": "d4ce68fe1bd17ac274093b3026a979d337cfa1c11f7c537a080105d60991a65a",
    "examples/fhp/rich-predicted.fhp.yaml": "4903379b382910b941f40304b92a46074cdd7211bb7afcaad4eb33b265135597",
    "examples/minimal.fhr.json": "691bba1ef46fa18bbac1bd1d99255c8d7d67249b4bd442e4470ec645a2369550",
    "examples/minimal.fhr.jsonld": "7dc0daf3c8deb21c8247eb8af23024c570e53f4ddc45d42cf233aba6f618178f",
}

# Section 4 of docs/DEVELOPMENT-TREE.md: candidates assessed for removal. This
# change removes none of them: each is either agent tooling, historical design
# provenance, or URL-served. The tuple stays so a later, separately reviewed
# change can classify a file and have the check enforce its removal.
REMOVABLE = ()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_published(root, published=PUBLISHED):
    """Problems with the published set: missing files or changed bytes."""
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
                        help="also fail when a classified-removable file is present")
    parser.add_argument("--list", action="store_true",
                        help="only list the classification and exit")
    args = parser.parse_args(argv)

    present = removable_present(ROOT)
    if args.list:
        print(f"{len(PUBLISHED)} published/URL-served files; "
              f"{len(REMOVABLE)} classified removable")
        for name in REMOVABLE:
            state = "present" if name in present else "removed"
            print(f"  removable ({state}): {name}")
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
    print(f"ok: {len(PUBLISHED)} published files match their shared copy; "
          f"{len(REMOVABLE) - len(present)} of {len(REMOVABLE)} classified-removable "
          f"file(s) removed ({len(present)} still present)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
