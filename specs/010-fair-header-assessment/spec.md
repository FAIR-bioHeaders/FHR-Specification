# Feature Specification: FAIR header assessment for specified and unspecified file types

**Feature Branch**: `010-fair-header-assessment`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: "Annotation files should say which sequence file they
relate to. Is it possible to make something that checks whether a header is FAIR, or
at least guidelines for file types we have not specified yet? For example the
Alliance could put their download files through it to find out whether their headers
are FAIR."

## Clarifications

### Session 2026-10-10

- Q: Should the assessment contact external services? → A: Offline by default; an explicit opt-in may check that identifiers and URLs resolve (FR-011).
- Q: What should the criteria be based on? → A: The RDA FAIR Data Maturity Model indicators, with file-header interpretations (FR-012).

## Context

FAIR-bioHeaders specifies headers for particular file types (FHR for genomes, with
FHT, FHP and FHGFF3 drafted). Most biological data files in circulation use no FAIR
header at all, or use their own header conventions (GFF3 `##` directives and `#!`
metadata lines, GAF `!` lines, VCF `##` lines). Existing FAIR assessment services
evaluate datasets through landing pages and persistent identifiers; none assesses
the metadata carried inside a file. Derived files (annotations, proteomes,
transcriptomes) in particular rarely state, in a checkable way, which exact sequence
file they belong to.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Assess the header of any data file (Priority: P1)

A data provider (for example the Alliance of Genome Resources) runs the assessment
on one of its download files, of any common type, and receives a report that says,
for each FAIR principle, what the header already provides, what is missing, and a
concrete suggestion to fix each gap.

**Why this priority**: It works on files as they are today, without anyone adopting
a new header first, so it is the cheapest route to adoption.

**Independent Test**: Run the assessment on real download files from five providers
(Alliance, WormBase, FlyBase, Ensembl, NCBI) covering FASTA, GFF3, GAF and VCF; each
report lists evidence per principle that a reviewer can confirm by reading the file.

**Acceptance Scenarios**:

1. **Given** a GFF3 file whose header names an assembly by accession, **When** it is
   assessed, **Then** the report credits the qualified reference to related data and
   cites the header line used as evidence.
2. **Given** a FASTA file with no header, **When** it is assessed, **Then** every
   principle is reported as not evidenced, with a suggestion for each, and the report
   is not an error.
3. **Given** a file carrying a valid FHR header, **When** it is assessed, **Then** the
   report reflects the FHR fields, and conformance to the FHR schema is reported
   separately from the FAIR assessment.

---

### User Story 2 - Check that an annotation matches its sequence file (Priority: P1)

A provider assesses an annotation file together with the genome it is meant to
annotate and learns whether they really belong together.

**Why this priority**: This is the core FAIR-bioHeaders promise for derived files:
an annotation can be tied to the exact assembly it describes.

**Independent Test**: Pairs of correct, mismatched (different assembly version) and
partially matching files produce the expected verdicts.

**Acceptance Scenarios**:

1. **Given** an annotation that records a genome identity (checksum, SeqCol digest or
   accession) and the genome file, **When** both are assessed together, **Then** the
   report states whether the recorded identity matches the genome.
2. **Given** an annotation with no recorded genome identity, **When** it is assessed
   with a genome, **Then** the report states whether sequence names and lengths are
   consistent, labelled as circumstantial evidence rather than a recorded link.
3. **Given** an annotation whose sequence names are absent from the genome, **When**
   assessed together, **Then** the report lists the missing names.

---

### User Story 3 - Guidelines for file types not yet specified (Priority: P2)

A producer of a file type FAIR-bioHeaders has not specified (for example a variant
call file or a gene-expression matrix) reads one short guideline that says what a
FAIR header should contain, independent of file type, with examples.

**Why this priority**: The guideline is what the assessment checks against, and it
lets communities improve headers before a dedicated specification exists.

**Independent Test**: For each guideline item there is an example header line in at
least two file types and a corresponding assessment check.

**Acceptance Scenarios**:

1. **Given** the guideline, **When** a reader maps it to the FAIR principles, **Then**
   every item cites the principle it serves and every principle relevant to files is
   covered or explicitly marked out of scope.
2. **Given** a file type with an existing header convention, **When** the guideline is
   applied, **Then** it shows how to express each item in that convention rather than
   requiring a new header format.

---

### User Story 4 - Assess many files at once (Priority: P3)

A provider assesses a whole release (hundreds of files) and receives a summary
across files plus per-file reports, suitable for tracking improvement between
releases.

**Independent Test**: A directory of 200 files produces a summary table and per-file
reports; re-running on an unchanged release gives identical results.

### Edge Cases

- Compressed files (gzip, BGZF) and files too large to read whole.
- Files whose header uses several conventions at once (FHR lines plus `##` directives).
- Headers in a convention the assessment does not know (reported as unrecognised
  comment lines, not ignored silently).
- Values that look like identifiers but are free text.
- A recorded genome identity that is present but malformed.
- Binary formats (BAM, CRAM, BigWig): out of scope for the first release and reported
  as such.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The assessment MUST accept files in any text format and recognise at
  least the FAIR-bioHeaders header and the native header conventions of FASTA, GFF3,
  GAF and VCF.
- **FR-002**: For each assessed principle the report MUST state one of: evidenced,
  partially evidenced, not evidenced, or not applicable, and cite the header lines used
  as evidence.
- **FR-003**: Every gap MUST come with a concrete suggestion, expressed in the file's
  own convention where one exists and as a FAIR-bioHeaders field otherwise.
- **FR-004**: The report MUST present results as a checklist with evidence. It MUST NOT
  present a single certification score or state that a file "is FAIR".
- **FR-005**: The assessment MUST distinguish a recorded link to related data
  (checksum, SeqCol digest, accession) from circumstantial consistency (matching
  sequence names and lengths), and report each separately.
- **FR-006**: Given a derived file and the related file, the assessment MUST check a
  recorded identity against the related file and report match, mismatch or unverifiable.
- **FR-007**: The guideline MUST map each header item to the FAIR principle(s) it
  serves, give examples in at least two file types, and reuse the FAIR-bioHeaders shared
  core field names.
- **FR-008**: Conformance to a FAIR-bioHeaders schema, where a file claims one, MUST be
  reported separately from the FAIR assessment.
- **FR-009**: Reports MUST be available in a human-readable form and a machine-readable
  form, and results for unchanged inputs MUST be reproducible.
- **FR-010**: The assessment MUST run without sending file contents anywhere.
- **FR-011**: By default the assessment MUST work fully offline and judge only what
  the file states. An explicit opt-in MAY additionally check that identifiers and URLs
  resolve; the report MUST say whether online checks ran, and file contents MUST never
  be sent anywhere.
- **FR-012**: The assessment criteria MUST be based on the RDA FAIR Data Maturity Model
  indicators, each with a documented file-header interpretation; indicators that cannot
  apply to a file header are listed as not applicable with a reason.

### Key Entities

- **Header evidence**: a metadata statement found in a file (key, value, line, convention).
- **Criterion**: a FAIR principle-derived check with its rationale and suggestion text.
- **Assessment result**: per criterion, a status, the evidence and a suggestion.
- **Related-file link**: a recorded identity (checksum, SeqCol, accession) from one file
  to another, with its verification outcome.
- **Guideline item**: what a header should contain, the principles it serves, and
  examples per file type.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Real download files from at least five providers and four file types are
  assessed, and an independent reviewer agrees with at least 90% of the reported
  per-principle statuses.
- **SC-002**: For every reported gap, the suggestion can be applied by the provider
  without consulting other documentation.
- **SC-003**: Correct, mismatched and partially matching annotation-genome pairs are
  classified correctly in all test cases.
- **SC-004**: A release of 200 files is assessed in under 10 minutes on a laptop.
- **SC-005**: At least one data provider (for example the Alliance) runs the assessment
  on its own files and reports the results useful.

## Assumptions

- The first release covers text formats; binary formats are reported as out of scope.
- Providers run the assessment themselves; no hosted service is required.
- The FAIR-bioHeaders shared core (spec 004) and `derivedFrom` links are the reference
  for field names and related-file links.
- A survey of real provider download files (planning, research phase) grounds the
  recognised conventions and the guideline examples.
- Maintainer decisions on schema authority (spec#44, website#15) apply to any FHR
  conformance reporting.
