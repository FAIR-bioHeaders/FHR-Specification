# Implementation Plan: Conformance test vectors for header parsing and checksum coverage

**Branch**: `001-checksum-conformance-vectors` (work branch `feat/conformance-vectors`) | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

## Summary

Generate byte-exact FASTA/GFA vectors and a JSON manifest from small templates,
with checksums computed independently of the converter. A second script checks
that the vectors are current, recomputes the checksums with its own reading of
the rules, and can run any converter CLI over the vectors. CI runs these checks
with the released converter.

## Technical Context

- **Language**: Python 3.13 (the repository's CI version). The generator and the
  stdlib checks use only `hashlib`, `base64`, `gzip`/`zlib`, `json` and `struct`.
- **Optional dependencies**: PyYAML and jsonschema (`--schema`), already in
  `requirements-validation.txt`. The converter checks need `fhr` (PyPI 0.3.3) or a
  checkout.
- **Testing**: unittest in `tests/test_conformance.py`, matching existing tests.
- **Determinism**: gzip/BGZF vectors use stored deflate blocks, mtime 0 and no
  file name, so output never depends on the zlib build.

## Constitution Check

- I (schema is the contract): valid vectors' metadata is validated against
  `fhr.json`. The schema and schemaVersion are unchanged.
- II (compatibility): additive only. Rule ids in docs/FORMAT.md are labels and
  change no rule's meaning.
- III (identity bytes): this feature gives every parsing rule a conformance
  example. `.gitattributes` keeps the vectors byte-exact.
- IV (no invented metadata): authors are labelled placeholders, there is no
  SeqCol value, and every checksum is real (FR-006).
- V (minimal): no new runtime dependencies. JSON manifest.

## Design

- Rule ids: R1–R4 are the numbered checksum rules, R5–R9 the header parsing
  bullets, and R10 the leading header block rule. R9 (microdata) has no
  FASTA/GFA vectors and is marked `notApplicable`.
- Layout: `conformance/{valid,invalid}/<id>.fhr.{fasta,gfa}[.gz]` plus
  `manifest.json`, with field definitions in `conformance/README.md`.
- An invalid vector breaks one rule and otherwise carries a correct checksum.
  R1/R3/R4 vectors carry a deliberately wrong or stale checksum.
- Two independent readings of the checksum rule:
  - The generator marks the lines it excludes as it builds each file, and also
    self-checks with a line-splitting reader.
  - The checker has its own offset-based reader.

## Verification gates

```bash
python -m unittest discover -s tests -v
python scripts/validate_examples.py
python scripts/check_linkml.py
python scripts/check_schema_drift.py
python scripts/check_release.py --converter ../FHR-File-Converter
python scripts/check_conformance.py --schema --converter ../FHR-File-Converter
```
