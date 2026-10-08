# Changelog

## Unreleased

- Add a tool-compatibility survey for FHR-headed FASTA, GFA and GFF3 files
  (#40, #49) in `docs/TOOL_COMPATIBILITY.md`, with scripts in
  `scripts/tool_survey/`. htslib faidx and most FASTA indexers reject the
  leading `;~` block; kseq-based tools ignore it; all GFA and GFF3 tools tested
  accept `#~` lines. Concatenated FHR files (invalid under R10) are silently
  misread as sequence by many tools. Also adds a draft, unfiled htslib proposal
  in `docs/proposals/htslib-fasta-comments.md`.
- Split the LinkML model into a shared FAIR-bioHeaders core
  (`schemas/core.yaml`) and the FHR module (`fhr_linkml.yml`), which imports it
  (#43, spec 004). The core holds the slots every header type shares, with
  FHR's current names and constraints. It also adds a provisional `DerivedFrom`
  class and `derivedFrom` slot (`headerType`, `checksum`, optional `seqcol_id`
  and `accessionID`, `relationship`). The relationship values await a decision
  on a PROV-O/RO mapping (#54). FHR does not include `derivedFrom`. `fhr.json`
  is unchanged and the generated schema is still validation-equivalent.
  `json-schema-generator.py` gains `generate_from()` for any schema that
  imports the core. A test generates a toy FHP stub from the core.
- Add FASTA/GFA conformance vectors for header parsing and checksum coverage
  (#34). `conformance/manifest.json` lists the expected outcome for each vector.
  `scripts/make_conformance.py` generates the vectors and computes their
  checksums with the standard library only. `scripts/check_conformance.py`
  checks that the vectors are current, recomputes the checksums, and optionally
  runs the converter over the vectors. CI runs these checks with converter 0.3.3
  from PyPI.
- Label the docs/FORMAT.md checksum and header parsing rules R1 to R10. The labels
  are non-normative and the rule text is unchanged.
- Mark the conformance files `-text` in `.gitattributes` so git never converts
  their line endings.

## v0.3.1 — 2026-10-08 (documentation patch)

- docs/FORMAT.md specifies how FHR header lines are parsed: a single-line checksum
  value on an unquoted root-level key, permitted header characters, byte order
  mark handling, no duplicate keys or YAML anchors/aliases, microdata attribute
  rules, and FHR lines forming the leading header block (FASTA and GFA). These
  match converter 0.3.1 (GHSA-pvq5-772j-fq72).
- Archive the private reporting and conflict/appeal contacts added after the
  v0.3.0 tag, and correct stale release, citation and policy wording.
- Add Spec Kit scaffolding with a draft constitution and draft feature specs.

The schema, examples and schemaVersion 1 are unchanged from v0.3.0.

## v0.3 — 2026-10-07 (from v0.2)

- Add optional structured assembly software, assembly protocol URI, N90, GC-content
  percentage, and supplied refget sequence collection ID. Preserve legacy software names.
- Retain required fields and schemaVersion 1; make ORCID's string type explicit.
- Align LinkML generation with the published contract and add equivalence checks.
- Replace speculative resource mappings with verified partial MIxS/MIGS projections.
- Correct JSON/YAML, FASTA/GFA, and escaped/typed microdata examples.
- Adopt exact-byte SHA-512/256 coverage of metadata and sequence, except the checksum
  line; old MD5/payload-only examples must be regenerated, not relabeled.
- Add CI, explicit schema drift protection, a generated diagram, project guidance,
  and a successor governance proposal. Private conduct/security reporting contacts
  and conflict/appeal routing are documented in CODE_OF_CONDUCT and SECURITY.
- Use verified Chicago bibliography citations with concept DOI links.

Published 2026-10-07 as v0.3.0 (version DOI
[10.5281/zenodo.23224136](https://doi.org/10.5281/zenodo.23224136)). Reusable
Nextflow modules are developed in the separate FHR-Nextflow repository (0.1.0-dev,
not yet released). The governance plan remains a proposal. Reporting-contact
updates on main after the tag are not included in the v0.3.0 archive.
