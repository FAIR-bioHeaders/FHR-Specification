# Feature Specification: RNA and transcriptome FASTA header (FHT)

**Feature Branch**: `005-rna-transcriptome-header`

**Created**: 2026-10-08

**Status**: Draft

**Input**: Grant Aim 1 names reference transcriptomes as the next header; the
FHT-Specification and FHT-File-Converter forks (2024, WIP) started this, but
`fht.json` currently fails to parse (JSON syntax error near line 202) and the
example carries genome-only fields such as `masking`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publish a de novo transcriptome with provenance (Priority: P1)

A lab assembles a transcriptome (e.g. Trinity) and embeds who built it, from which
samples, with which tools, and its completeness.

**Independent Test**: Combine an FHT header onto a small transcript FASTA;
validate, strip, round-trip all serialisations; checksum verifies.

### User Story 2 - Genome-guided transcript set linked to its genome (Priority: P1)

A transcript FASTA derived from an annotated genome records the genome and
annotation it came from (`derivedFrom`, 004).

## Requirements *(mandatory)*

- **FR-001**: FHT imports the core; subject slot `transcriptome`.
- **FR-002**: Required beyond core: `assemblyType` (de novo | genome-guided |
  annotation-derived) and `moleculeType` (mRNA | total RNA | cDNA | ncRNA)
  [NEEDS CLARIFICATION: which are required vs optional after curator consultation].
- **FR-003**: Optional: `assemblySoftware` (structured, as FHR v0.3), `sample`
  (tissue/UBERON, developmental stage, condition, strain), `libraryStrategy`,
  `strandedness`, `sequencingRuns` (accessions, e.g. SRA), `vitalStats`
  (transcript count, N50, mean length), `completeness` (e.g. BUSCO lineage,
  version and scores), `derivedFrom`.
- **FR-004**: Drop genome-only fields (`masking`) from FHT; keep the FHT example
  schema-valid with a real checksum.
- **FR-005**: Fix the existing `fht.json` syntax error and migrate it to LinkML;
  supersede the WIP fork contents with a released schema.
- **FR-006**: RNA FASTA may use U for uracil; header parsing and checksums are
  alphabet-independent.

## Success Criteria *(mandatory)*

- **SC-001**: FHT v0.1 released with examples, conformance vectors and DOI.
- **SC-002**: At least one real public transcriptome carries an FHT header.

## Assumptions

- The forked FHT-File-Converter is retired in favour of the multi-format toolkit (008).
