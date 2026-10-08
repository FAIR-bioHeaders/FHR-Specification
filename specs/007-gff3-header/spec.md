# Feature Specification: GFF3 annotation header (FHGFF3)

**Feature Branch**: `007-gff3-header`

**Created**: 2026-10-08

**Status**: Draft

**Input**: Umbrella spec 003. The FHGFF3 repository is a fork of the LinkML GFF3
data model (biodatamodels/gff-schema) with a 2024 validator prototype and web app.
Annotations are the files most often separated from the exact assembly they
describe.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Annotation bound to its assembly (Priority: P1)

A GFF3 file records the FHR checksum and SeqCol ID of the genome it annotates,
the pipeline and evidence used, and the Sequence Ontology release.

**Independent Test**: Combine a header onto a GFF3; validate; run `verify-links`
against the genome; checksum verifies; stripping restores the original bytes.

### User Story 2 - Existing GFF3 tools still work (Priority: P1)

AGAT, gffread, GenomeTools and JBrowse load an FHGFF3 file (headers are `#`
comments), or the strip command restores a plain file.

## Requirements *(mandatory)*

- **FR-001**: Placement: the first line stays `##gff-version 3` (required by the
  GFF3 spec); `#~` header lines follow it and form the leading header block,
  which ends at the first feature line, `##FASTA` or other non-comment directive
  [NEEDS CLARIFICATION: may `##sequence-region` and other `##` directives appear
  before or among `#~` lines?].
- **FR-002**: Checksum: R1–R4 over the whole file including any `##FASTA` section;
  `#~` is the prefix, as for GFA. Note `###` (forward-reference resolution) is
  unaffected.
- **FR-003**: FHGFF3 imports the core; subject slot `annotation`. Required beyond
  core: `derivedFrom` with relationship `annotates` (genome checksum; SeqCol ID
  recommended) [NEEDS CLARIFICATION: require the genome link, or allow annotation
  of unpublished assemblies with accession only?].
- **FR-004**: Optional: `annotationSoftware` (structured), `evidence` (RNA-seq
  runs, protein sets, by accession or FHR-family checksum), `soVersion`
  (Sequence Ontology release), `annotationAuthority`, `vitalStats` (gene,
  transcript, CDS counts), `completeness` (BUSCO).
- **FR-005**: Relationship to the LinkML GFF3 data model: the header schema is
  separate from the feature data model; the existing validator prototype is
  evaluated for reuse in feature validation [NEEDS CLARIFICATION: in scope now?].
- **FR-006**: Survey GFF3 tools for handling of `#~` lines and `##gff-version`
  ordering (see also spec#40 for FASTA tools).

## Success Criteria *(mandatory)*

- **SC-001**: FHGFF3 v0.1 released with examples, vectors and DOI.
- **SC-002**: Five common GFF3 tools documented as compatible or needing strip.
