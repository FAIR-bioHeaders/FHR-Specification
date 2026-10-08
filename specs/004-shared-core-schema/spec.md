# Feature Specification: Shared LinkML core for FAIR-bioHeaders

**Feature Branch**: `004-shared-core-schema`

**Created**: 2026-10-08

**Status**: Draft

**Input**: Umbrella spec 003, FR-001. Grant A.2.1: store schemas in LinkML and
generate JSON Schema; organise schemas to coordinate between file formats.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Define a new header type by importing the core (Priority: P1)

A schema author creates FHP by importing the core and adding protein-specific
slots, without copying provenance fields.

**Independent Test**: FHR re-expressed as core + FHR slots generates a JSON Schema
validation-equivalent to today's `fhr.json` (`scripts/check_linkml.py` passes;
`check_schema_drift.py` shows no semantic change).

### User Story 2 - Link derived files to parents (Priority: P1)

A GFF3 header records the genome it annotates by checksum and SeqCol ID.

## Requirements *(mandatory)*

- **FR-001**: Core slots shared by every type: `schema`, `schemaVersion`,
  `taxon`, `version`, `metadataAuthor`, `dateCreated`, `checksum` (required);
  `identifier`, `accessionID`, `scholarlyArticle`, `documentation`,
  `relatedLink`, `funding`, `reuseConditions`, `voucherSpecimen` (optional).
- **FR-002**: Each type keeps its subject slot (`genome`, `transcriptome`,
  `proteome`, `annotation`) and its own required slots; core slots keep FHR's
  current names, types and constraints.
- **FR-003**: A `derivedFrom` list of objects: `headerType` (FHR|FHT|FHP|FHGFF3),
  `checksum` (FHR-family checksum), `seqcol_id` (optional), `accessionID`
  (optional), `relationship` (e.g. `annotates`, `transcribedFrom`,
  `translatedFrom`, `filteredFrom`) [NEEDS CLARIFICATION: controlled vocabulary,
  or map relationships to PROV-O / RO terms?].
- **FR-004**: Type discrimination: each instance's `schema` URL identifies the type
  and version; schemas are published at versioned, persistent URLs
  [NEEDS CLARIFICATION: w3id.org/fair-bioheaders/... or GitHub release URLs].
- **FR-005**: FHR's existing JSON Schema MUST stay the published contract until
  the generated one is proven validation-equivalent; no FHR instance changes
  validity.
- **FR-006**: Ontology-backed slots (taxon, tissue, assay) use pinned ontology
  versions and record the term IRI, not only a label.

## Success Criteria *(mandatory)*

- **SC-001**: FHR expressed via the core passes all current spec checks and the
  conformance vectors unchanged.
- **SC-002**: FHT, FHP and FHGFF3 schemas import the core with no duplicated slots.

## Assumptions

- LinkML (already used for `fhr_linkml.yml`) is the source of truth; generated
  artefacts are committed and drift-checked as today.
