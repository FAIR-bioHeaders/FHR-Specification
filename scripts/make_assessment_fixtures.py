# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Generate the synthetic FAIR header assessment fixtures (assessment/pairs, edge).

The output is deterministic: gzip members carry mtime 0 and no file name, tar
members are owned by uid/gid 0 with mtime 0. Real provider captures in
assessment/headers are copied, not generated. Their expected outcomes, and those
of the generated files, are listed in assessment/manifest.json.

Usage: python scripts/make_assessment_fixtures.py [--output DIR]
"""

import argparse
import gzip
import io
from pathlib import Path
import tarfile

from make_conformance import bgzf

ROOT = Path(__file__).resolve().parents[1]
HEADERS = ROOT / "assessment" / "headers"
FHR_URL = "https://raw.githubusercontent.com/FAIR-bioHeaders/FHR-Specification/main/fhr.json"
FHT_URL = "https://raw.githubusercontent.com/FAIR-bioHeaders/FHT-Specification/main/fht.json"
REFSEQ_GFF3 = "ncbi-refseq_gff3_GCF_000002985.6_WBcel235_genomic.gff"
FEATURE = b"ctg1\tsynthetic\tgene\t1\t20\t.\t+\t.\tID=gene1\n"
# Synthetic FHR metadata, the same as conformance/valid/fasta-lf.fhr.fasta.
FHR_METADATA = [
    f"schema: {FHR_URL}",
    "schemaVersion: 1.0",
    "genome: Synthetic FHR conformance genome",
    "taxon:",
    "  name: Homo sapiens",
    "  uri: https://identifiers.org/taxonomy:9606",
    "version: 1.0.0",
    "metadataAuthor:",
    "- name: Synthetic metadata author (placeholder)",
    "assemblyAuthor:",
    "- name: Synthetic assembly author (placeholder)",
    "dateCreated: '2026-10-08'",
    "masking: not-masked",
    "documentation: Synthetic FHR conformance vector; not a real assembly.",
    "checksum: 3an6Cqo2eomqlt75XIpyWXDtls3GhA8EOpjK97S+ykc=",
]


def gzip_bytes(data):
    return gzip.compress(data, mtime=0)


def tar_gz(name, data):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        info = tarfile.TarInfo(name)
        info.size, info.mtime, info.mode = len(data), 0, 0o644
        info.uname = info.gname = ""
        tar.addfile(info, io.BytesIO(data))
    return gzip_bytes(buffer.getvalue())


def lines(*items):
    return b"".join((item if isinstance(item, bytes) else item.encode("utf-8")) + b"\n"
                    for item in items)


def edge():
    """The edge cases of research R-15/R-18 (tasks.md T019)."""
    refseq = (HEADERS / REFSEQ_GFF3).read_bytes() + b"NC_003279.8\tRefSeq\tregion\t1\t15072434\t.\t+\t.\tID=NC_003279.8:1..15072434\n"
    gff3 = lines("##gff-version 3", "##sequence-region ctg1 1 20") + FEATURE
    return {
        "edge/no-header.fa": lines(">seq1", "ACGTACGTAC", "GGTTAACCAT"),
        "edge/gzip-refseq.gff.gz": gzip_bytes(refseq),
        "edge/bgzf-refseq.gff.gz": bgzf(refseq),
        "edge/gff3-in-tar.gff.gz": tar_gz("annotation.gff3", gff3),
        "edge/stub.bam": bgzf(b"BAM\x01" + bytes(60)),
        "edge/fhr-and-directives.gff3": lines("##gff-version 3", *("#~" + item for item in FHR_METADATA),
                                              "##sequence-region ctg1 1 20") + FEATURE,
        "edge/unknown-convention.txt": lines("% produced by a synthetic tool", "% columns: x y", "1 2", "3 4"),
        "edge/accession-in-comment.gff3": lines("##gff-version 3", "# built on GCF_000002985.6 (synthetic)",
                                                "##sequence-region ctg1 1 20") + FEATURE,
        "edge/malformed-checksum.gff3": lines(
            "##gff-version 3",
            "#~derivedFrom: [{headerType: FHR, relationship: annotates, checksum: "
            + "A" * 42 + "=}]",
            "##sequence-region ctg1 1 20") + FEATURE,
        "edge/conflicting-accessions.gff3": lines(
            "##gff-version 3", "#!genome-build-accession NCBI_Assembly:GCF_000002985.6",
            "#!genome-build-accession NCBI_Assembly:GCA_000002985.3", "##sequence-region ctg1 1 20") + FEATURE,
        "edge/non-utf8.gff3": lines("##gff-version 3") + b"#!data-source Synth\xe9tique\n" + FEATURE,
        "edge/fhr-valid.fhr.fasta": (ROOT / "conformance" / "valid" / "fasta-lf.fhr.fasta").read_bytes(),
        "edge/fht-stub.fa": lines(f";~schema: {FHT_URL}", ";~schemaVersion: 1.0",
                                  ";~transcriptome: Synthetic transcriptome stub (no published FHT schema)",
                                  ";~reuseConditions: CC0-1.0", ">tx1", "ACGUACGUAC"),
    }


def fixtures():
    """Return {relative path: bytes} for every generated fixture."""
    return {**edge()}


def write(output):
    for name, content in sorted(fixtures().items()):
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=ROOT / "assessment",
                        help="directory that receives pairs/ and edge/ (default: assessment/)")
    args = parser.parse_args()
    write(args.output)


if __name__ == "__main__":
    main()
