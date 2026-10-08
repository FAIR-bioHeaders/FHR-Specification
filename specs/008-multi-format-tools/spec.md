# Feature Specification: Multi-format tools and generated libraries

**Feature Branch**: `008-multi-format-tools`

**Created**: 2026-10-08

**Status**: Draft

**Input**: Grant Aim 2 (A.2.2–A.2.5): extend the FHR tools to all header types,
generate libraries in R, Java, JavaScript, Python and Julia from LinkML, support
community profiles, and contribute header handling upstream.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One CLI for all headers (Priority: P1)

`fhr` (or a renamed package) validates, converts, combines, strips and checksums
FHR, FHT, FHP and FHGFF3 with the same streaming, gzip/BGZF and pipe support.

**Independent Test**: The conformance vectors of every type pass through the CLI.

### User Story 2 - Verify provenance links (Priority: P1)

`verify-links child.gff3 --parent genome.fa` checks the recorded parent checksum.

### User Story 3 - Community profile validation (Priority: P2)

`validate --profile agbiodata` applies extra LinkML constraints.

### User Story 4 - Libraries in other languages (Priority: P3)

Generated R/JS/Java/Julia libraries read headers and pass the vectors.

## Requirements *(mandatory)*

- **FR-001**: The converter's streaming core is generalised by container
  (FASTA `;~`, GFA/GFF3 `#~`) and schema type; existing `fhr-*` commands keep
  working unchanged [NEEDS CLARIFICATION: one package with a type registry and
  new entry points (`fht-*`, `fhp-*`, `fhgff3-*` or a single `bioheader` command),
  or separate packages sharing a core library? Recommendation: one package].
- **FR-002**: Type detection from the `schema` URL; explicit `--type` override.
- **FR-003**: `verify-links` checks `derivedFrom` checksums against supplied files.
- **FR-004**: Profiles: LinkML profile schemas layered on a type; `--profile`.
- **FR-005**: JSON-LD serialisation alongside JSON, YAML and microdata.
- **FR-006**: Library generation from LinkML for R, JavaScript, Java and Julia,
  each tested against the conformance vectors in CI.
- **FR-007**: FHR-Nextflow modules generalised to all types.
- **FR-008**: Upstream support: htslib/samtools comment handling (spec#40),
  JBrowse header display (Web Component), GFF3 tool fixes.

## Success Criteria *(mandatory)*

- **SC-001**: All vectors for all types pass in the Python CLI and at least one
  generated library.
- **SC-002**: PyPI/Bioconda releases include all header types.

## Assumptions

- Builds on converter 0.3.3 (streaming, gzip/BGZF, pipes) and the conformance
  vector tooling (spec#34).
