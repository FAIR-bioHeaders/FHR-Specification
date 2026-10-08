# Feature Specification: Protein FASTA header (FHP)

**Feature Branch**: `006-protein-header`

**Created**: 2026-10-08

**Status**: Draft

**Input**: Umbrella spec 003. Proteome FASTA files (predicted or curated) have the
same provenance gap as genomes; they are usually derived from a specific genome
and annotation, which is lost when files are copied.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ship a predicted proteome traceable to its annotation (Priority: P1)

An annotation pipeline emits `proteins.fa` whose header names the genome and
GFF3 it was translated from, the genetic code and isoform policy.

**Independent Test**: With the GFF3 and genome present, `verify-links` confirms
the chain; changing the GFF3 breaks it.

### User Story 2 - Curated protein set (Priority: P2)

A resource publishes a curated protein set (e.g. a UniProt reference proteome
subset) with source database release and accession.

## Requirements *(mandatory)*

- **FR-001**: FHP imports the core; subject slot `proteome` (FHP is the working name; it may still be revisited (decided in #54)).
- **FR-002**: Required beyond core: `sourceType` (predicted | curated | mixed).
- **FR-003**: Optional: `derivedFrom` (genome and annotation checksums),
  `geneticCode` (NCBI translation table ID), `isoformPolicy` (all | longest |
  canonical), `predictionSoftware` (structured), `sourceDatabase` (name, release,
  e.g. UniProt release and proteome ID `UP...`), `vitalStats` (protein count),
  `completeness` (BUSCO).
- **FR-004**: Header parsing and checksum identical to FHR (`;~` prefix, R1–R10).
- **FR-005**: Examples and conformance vectors with amino-acid sequences
  (including `*` stop symbols) prove alphabet independence.

## Success Criteria *(mandatory)*

- **SC-001**: FHP v0.1 released with examples, vectors and DOI.
- **SC-002**: A genome → GFF3 → protein chain verifies end to end on public data.
