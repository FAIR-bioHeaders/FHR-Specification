# Implementation Plan: Shared LinkML core for FAIR-bioHeaders

**Branch**: `004-shared-core-schema` (work branch `feat/shared-core`) | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md) | **Issue**: #43

## Summary

Move the slots and classes every header type shares into a LinkML core module
and make `fhr_linkml.yml` import it. Add a provisional `DerivedFrom` class and
`derivedFrom` slot to the core, but leave them off the FHR class. The published
`fhr.json` does not change.

## Technical Context

- **Language**: LinkML 1.11.1 (pinned), Python 3.13, jsonschema.
- **Layout**: `schemas/core.yaml` holds the core. Other header-type modules can
  go in `schemas/` later. LinkML resolves imports relative to the importing file
  and appends `.yaml`, so the core needs that extension. `fhr_linkml.yml` stays
  at the root as the FHR module and entry point, so scripts, CI and links keep
  working.
- **Generation**: `json-schema-generator.py` gains `generate_from(path)` for any
  schema that imports the core. It keeps the legacy core objects open and pins
  exact lengths for `checksum` and `seqcol_id` wherever they appear. `generate()`
  adds the FHR-only post-processing.

## Constitution Check

- I (schema is the contract): `fhr.json` stays byte-identical, and
  `check_linkml.py` still passes. The only differences in the generated schema
  are descriptions and new `$defs`.
- II (compatibility): FHR validity is unchanged, and `derivedFrom` is not added to
  FHR. Adding it later needs its own schema change and baseline review.
- IV (no invented metadata): the relationship vocabulary is marked provisional
  until #54 is decided. The core `id` is provisional until FR-004 is decided.
- V (minimal): no new dependencies.

## Design decisions

- Core slots are top-level LinkML `slots`. Header classes list them, and FHR uses
  `slot_usage` to keep its genome-specific descriptions.
- The `seqcol_id` definition is in the core because `DerivedFrom` reuses it. FHR
  opts in by listing it, and other types need not.
- `Author` keeps its class name (Person/ORCID) for continuity with existing
  generated `$defs`.
- `DerivedFrom` requires `headerType`, `checksum` and `relationship`. It is closed
  (`additionalProperties: false`), like other new objects.

## Verification gates

```bash
python -m unittest discover -s tests -v
python scripts/validate_examples.py
python scripts/check_linkml.py
python scripts/check_schema_drift.py
python scripts/check_conformance.py --schema
python scripts/check_release.py --converter ../FHR-File-Converter
```
