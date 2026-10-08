# Changelog

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
