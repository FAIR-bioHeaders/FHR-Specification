# FHR Specification Constitution

> **Status: draft.** Proposed for Spec Kit planning gates. It restates existing
> AGENTS.md, CONTRIBUTING.md, and docs/FORMAT.md practice and adds no authority.
> David and Adam must approve it before it is treated as ratified; it does not adopt
> the GOVERNANCE.md successor proposal.

## Core Principles

### I. The published JSON schema is the contract

`fhr.json` is authoritative. `fhr_linkml.yml`, generated output, both converter
schema copies, examples, docs, and `Diagram.svg` must agree with it. LinkML
generation must stay validation-equivalent (`scripts/check_linkml.py`).

### II. Compatibility before tightening

Metadata valid under the current schemaVersion stays valid unless a change is an
explicit, reviewed compatibility break. Prefer additive optional fields. Required
fields, types, patterns, unknown-property policy, and URI/date formats change only
with a stated use case, a concrete schema diff, a migration note, and a changelog
entry. Never refresh `.github/schema-baseline.json` merely to hide drift.
Package version, release version, and schemaVersion are distinct.

### III. Preserve user data and identity bytes

FHR checksums are SHA-512/256 over exact FASTA/GFA bytes except the single
root-level checksum line (docs/FORMAT.md). Specifications must leave no ambiguity
about which bytes are hashed or which lines are metadata; every parsing rule needs
a conformance example. SeqCol is a supplied identifier, never an FHR checksum.

### IV. No invented metadata

Do not invent authorship, accessions, software provenance, statistics, contacts,
DOIs, or ontology mappings. Mappings use authoritative pinned terms and state
partial or lossy projections explicitly. Placeholders are labelled as placeholders.

### V. Minimal and interoperable

Keep required metadata and runtime dependencies small. Favour incremental,
interoperable changes over speculative frameworks, guided by FAIR and TRUST as
interpreted in the 2024 FHR paper.

## Verification gates

Every plan names the checks it must pass from the repository root:

```bash
python -m unittest discover -s tests -v
python scripts/validate_examples.py
python scripts/check_linkml.py
python scripts/check_schema_drift.py
python scripts/check_release.py --converter ../FHR-File-Converter
```

Schema or format changes also update the converter schema copies, shared
fixtures, and docs in coordinated, cross-linked PRs.

## Decision boundaries

David and Adam hold schema authority until a governance model is explicitly
adopted. Publishing releases, archiving DOIs, adopting governance, and confirming
reporting contacts are separate maintainer actions; a spec, plan, or task list
never authorizes them. Security-relevant findings follow SECURITY.md before any
public issue or PR.

## Governance

This constitution guides Spec Kit specify/plan/tasks gates. Amendments follow the
normal review process with a changelog note. On conflict, the published schema,
docs/FORMAT.md, and maintainer decisions win.

**Version**: 0.1.0 (draft) | **Ratified**: pending maintainer approval | **Last Amended**: 2026-10-08
