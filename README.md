# FHR Specification

[![Specification checks](https://github.com/FAIR-bioHeaders/FHR-Specification/actions/workflows/validate-specification.yml/badge.svg?branch=main)](https://github.com/FAIR-bioHeaders/FHR-Specification/actions/workflows/validate-specification.yml)
[![Schema drift checks](https://github.com/FAIR-bioHeaders/FHR-Specification/actions/workflows/check-schema-drift.yml/badge.svg?branch=main)](https://github.com/FAIR-bioHeaders/FHR-Specification/actions/workflows/check-schema-drift.yml)
[![Specification DOI](https://img.shields.io/badge/Specification_DOI-10.5281%2Fzenodo.6762549-blue)](https://doi.org/10.5281/zenodo.6762549)
[![File Converter DOI](https://img.shields.io/badge/File_Converter_DOI-10.5281%2Fzenodo.6762547-blue)](https://doi.org/10.5281/zenodo.6762547)

FHR (FAIR Header Reference genome) keeps machine-readable and human-readable
provenance with reference genome data. This repository defines the JSON Schema,
LinkML model, examples, and partial MIxS/MIGS mappings. The
[FHR File Converter](https://github.com/FAIR-bioHeaders/FHR-File-Converter)
provides conversion, validation, and FASTA/GFA header tools.

## v0.3 metadata

The v0.3 release adds optional fields and fixes examples; the required metadata
set and numeric `schemaVersion: 1` remain unchanged. Package/release version,
schema version, and assembly `version` are distinct.

Required fields: `schema`, `schemaVersion`, `genome`, `taxon`, `version`,
`metadataAuthor`, `assemblyAuthor`, `dateCreated`, `masking`, and `checksum`.
See [the minimal instance](examples/minimal.fhr.json) and
[the annotated field reference](docs/FORMAT.md). Top-level unknown fields are
rejected by the schema. Many nested objects remain open for existing metadata;
software provenance objects have an explicit field set.

The [rich YAML example](examples/example.fhr.yaml) shows optional
`assemblySoftware`, `assemblyProtocol`, `vitalStats.N90`, `vitalStats.gcContent`,
and `seqcol_id`. A legacy software name string remains valid. GC content uses a
percentage from 0 to 100; N90 uses base pairs. SeqCol digests are supplied by users
and have a different identity/algorithm from the FHR file checksum.

Checksum helpers require SHA-512/256 support in the Python build. Some Apple
system Python builds omit it; use an OpenSSL-enabled Python distribution.
Metadata conversion and validation do not require that hash implementation.

## Serialization and checksums

YAML is embedded in FASTA comments with `;~` and GFA comments with `#~`; the prefix
is removed to recover YAML. JSON/YAML and HTML microdata can store the same
metadata separately. See [the HTML example](examples/example.microdata.fhr.html)
and [microdata guidance](docs/MICRODATA.md).

The v0.3 checksum policy is base64 SHA-512/256 over the exact file bytes except
the scalar FHR checksum line (including that line's newline). Metadata, ordinary
comments, and sequence bytes all contribute. [Checksum and migration details](docs/FORMAT.md)
explain the change from the old MD5/payload-only documentation.

[Conformance vectors](conformance/README.md) give valid and invalid FASTA/GFA
files, with expected checksums, for the header parsing and checksum rules. Use
them to test other FHR implementations.

JSON/YAML/HTML examples contain synthetic checksum and SeqCol placeholders.
The FASTA/GFA examples have verified FHR file checksums but retain a synthetic
SeqCol placeholder; it must not be used as the sequence collection's identity.

## Validation and LinkML

Use Python 3.13 or later for repository checks. The cross-repo `check_release.py`
command requires a companion FHR-File-Converter checkout at the supplied path:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-linkml.txt
python -m unittest discover -s tests -v
python scripts/validate_examples.py
python scripts/check_linkml.py
python scripts/check_schema_drift.py
python scripts/check_release.py --converter ../FHR-File-Converter
python scripts/check_conformance.py --converter ../FHR-File-Converter
python json-schema-generator.py --output /tmp/fhr_linkml.json
python scripts/project_mixs.py examples/example.fhr.json
```

CI checks JSON/YAML examples, the explicit schema review baseline, and LinkML
validation equivalence. Generation uses pinned LinkML 1.11.1 and preserves
legacy open nested objects and checksum length constraints. Equivalence checking
resolves local references and compares validation keywords, ignoring descriptive
annotations and ordering of required fields. Generated output does not overwrite
the published `fhr.json`. [MIxS/MIGS mapping limits](docs/MAPPINGS.md) include
partial/lossy terms and omissions; the output is not a complete MIGS submission.

For intentional schema edits, explain compatibility and update the review baseline:

```bash
python scripts/check_schema_drift.py --update
```

Commit the baseline with the schema/model changes, synchronize both converter
schema copies, and run every check. Require `schema-drift` and `validate` checks in
branch protection to block failing merges. Whitespace/key order do not count as
drift; other JSON changes require an explicit update and maintainer review.

## Project guidance

See [CONTRIBUTING](CONTRIBUTING.md), [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md),
[SECURITY](SECURITY.md), and [AGENTS](AGENTS.md). David and Adam retain schema
authority; [GOVERNANCE](GOVERNANCE.md) describes the current two-maintainer model and a future steering-group option that is not active.
The [schema diagram](Diagram.svg) is generated with
`python scripts/render_diagram.py` and summarizes required and optional fields.
[Release notes](CHANGELOG.md) document compatibility and deferred work.

## Citing FHR

Chicago bibliography entries are used below. Cite the published paper for a
general description of FHR; cite the specification or converter when using that
resource directly. The software and specification links are concept DOIs; for a
specific release, use the corresponding version DOI from Zenodo. Authors and
years follow the v0.3 records resolved by the concept DOIs, and can change as later records are published.

### Published paper

Wright, Adam, Mark D. Wilkinson, Christopher Mungall, Scott Cain, Stephen Richards, Paul Sternberg, Ellen Provin, Jonathan L. Jacobs, Scott Geib, Daniela Raciti, Karen Yook, Lincoln Stein, and David C. Molik. “FAIR Header Reference Genome: A TRUSTworthy Standard.” *Briefings in Bioinformatics* 25, no. 3 (2024): bbae122. https://doi.org/10.1093/bib/bbae122.

### Specification

Molik, David, and Adam Wright. *FHR Specification*. Data set. 2026. https://doi.org/10.5281/zenodo.6762549.

### Converter

Molik, David, and Adam Wright. *FHR File Converter*. Computer software. 2026. https://doi.org/10.5281/zenodo.6762547.

Machine-readable entries are maintained in
[FHR-Citation](https://github.com/FAIR-bioHeaders/FHR-Citation/blob/main/citation.bib).
