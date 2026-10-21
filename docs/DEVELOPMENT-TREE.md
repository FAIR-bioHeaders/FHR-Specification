# The FHR development tree

This repository, `FAIR-bioHeaders/FHR-Specification`, is the **development home
for the FHR (FAIR Header Reference genome) header**. The released specification
for every FAIR-bioHeaders type, including FHR, is published from
`FAIR-bioHeaders/FAIR-bioHeaders-Specification` (called `FHR-Specification` until
2026-10-14). This tree still contains a copy of the whole family publication tree
because that is how the repository was renamed and split; this document records
what belongs here, what must stay byte-identical to the shared publication tree,
and what is inherited material that the checks still depend on.

Family migration tracker: [FAIR-bioHeaders-Specification#107](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/issues/107).
This work: [FHR-Specification#5](https://github.com/FAIR-bioHeaders/FHR-Specification/issues/5).

The classification is enforced by `scripts/check_development_tree.py` and
checked in CI (`.github/workflows/validate-specification.yml`).

## Development branches versus released `main`

- **Develop on branches.** FHR-specific model, documentation, example and check
  changes start here and are reviewed in a branch/PR.
- **Reviewed schema changes publish in FAIR-bioHeaders-Specification first.**
  Finished work goes there by pull request; only then is this repository's
  `main` synchronized.
- **`main` keeps the published files unchanged.** Existing FHR files cite
  `https://raw.githubusercontent.com/FAIR-bioHeaders/FHR-Specification/main/fhr.json`,
  so `main`'s `fhr.json`, `fhp.json`, `fhgff3.json` and `jsonld/` always equal
  FAIR-bioHeaders-Specification `main`'s copies. The `published-files` workflow
  enforces that live; `scripts/check_development_tree.py` enforces it locally
  against recorded digests.
- **Never rewrite history, tags or released bytes.** The release tags
  (`v0.3.0`, `v0.3.1`, `v0.4.0`) and their files stay. Deleting a file from a
  development branch does not touch a tag; it only stops serving that path on
  `main`, which is why a published path may not be deleted.

## Classification

### 1. FHR development artifacts that belong here

These are the FHR development surface. They are owned here and coordinated into
shared publication by pull request:

- the FHR model and mappings: `fhr_linkml.yml`, `fhr_mappings.yml`,
  `json-schema-generator.py`, `mappings/fhr-jsonld-dcmi.yml`,
  `mappings/fhr-schemaorg-export.yml`;
- the shared core that FHR imports: `schemas/core.yaml`,
  `schemas/versions.json`;
- FHR docs: `docs/FORMAT.md`, `docs/MICRODATA.md`, `docs/JSONLD.md`,
  `docs/SCHEMA-VERSIONS.md`, `docs/TERMS.md`, `docs/SCHEMAORG-EXPORT.md`,
  `docs/MAPPINGS.md`, `docs/FAIR_HEADER_GUIDELINE.md`,
  `docs/TOOL_COMPATIBILITY.md`, `docs/SCHEMA-CHANGES-v0.4.md`,
  `docs/proposals/`;
- FHR examples and vectors: `examples/*.fhr.*`, the `fhr` `conformance/`
  vectors and `conformance/manifest.json`, the `assessment/` fixtures;
- checks: `scripts/*.py`, `tests/*.py`, `.github/workflows/`, the schema
  baselines in `.github/`;
- repository metadata: `README.md`, `AGENTS.md`, `CONTRIBUTING.md`,
  `CHANGELOG.md`, `CITATION.cff`, `GOVERNANCE.md`, `LICENSE`,
  `CODE_OF_CONDUCT.md`, `SECURITY.md`, `Diagram.svg`, `requirements-*.txt`.

### 2. Shared-publication artifacts that must stay byte-identical

These files serve established `raw.githubusercontent.com`/tag/Pages URLs, or
are published companion copies. They may not be edited here except by
synchronizing the shared `main`, and they may not be deleted:
`scripts/check_development_tree.py` fails if any is missing or differs from its
recorded shared-copy digest.

| Path | Why it must stay |
| --- | --- |
| `fhr.json` | `$id` and cited raw-main URL `.../FHR-Specification/main/fhr.json`; used by FHR-Nextflow, gff3-validator, the website and the toolkit |
| `fhp.json` | published FHP contract; old-name raw-main URL used by the toolkit, FAIR-bioHeaders-Specification and FHP-Specification tests |
| `fhgff3.json` | published FHGFF3 contract; same old-name raw-main URL usage |
| `jsonld/fhr.context.jsonld`, `jsonld/terms.jsonld`, `jsonld/terms.ttl` | served on GitHub Pages as `terms/` and `fhr/{main,vX.Y.Z}/jsonld/`; `https://w3id.org/fair-bioheaders/terms` and `.../fhr/vX.Y.Z/jsonld/...` redirect there |
| `examples/**` | published examples; `scripts/check_release.py` requires them byte-identical to the toolkit copies |
| `assessment/manifest.schema.json` | `$id` raw-main URL `.../FHR-Specification/main/assessment/manifest.schema.json` |
| `mappings/mapping-table.schema.json` | `$id` raw-main URL `.../FHR-Specification/main/mappings/mapping-table.schema.json` |
| `specs/013-schemaorg-export/contracts/export-table.schema.json` | `$id` raw-main URL `.../FHR-Specification/main/specs/013-schemaorg-export/contracts/export-table.schema.json` |

The `published-files` workflow additionally compares `fhr.json`, `fhp.json`,
`fhgff3.json` and `jsonld/*` against shared `main` over the network. That live
check and this digest check are complementary: the workflow catches shared
`main` moving, and this check catches a local edit or deletion.

### 3. Inherited FHP/FHGFF3/shared fixtures and machinery

The repository still carries the family tree that was copied when it was the
shared repository. These files are *not* FHR development surface, but most are
**actual dependencies of the checks**, so they are retained.

#### 3a. Actual dependencies of the checks (retained)

Removing any of these breaks `scripts/check_conformance.py`,
`scripts/check_linkml.py`, `scripts/check_schema_drift.py`,
`scripts/check_release.py`, a workflow, or the unittest suite:

- `fhp_linkml.yml`, `fhgff3_linkml.yml`, `schemas/shared.yaml` — read by
  `check_linkml.py` and `json-schema-generator.py` to regenerate `fhp.json` and
  `fhgff3.json`; `check-schema-drift.yml` reads `.github/schema-baseline-fhp.json`
  and `.github/schema-baseline-fhgff3.json`;
- `examples/fhp/**`, `examples/fhgff3/**` — compared with the toolkit by
  `check_release.py` and validated by `validate-specification.yml`;
- the `fhp-fasta` and `fhgff3` `conformance/` vectors and `docs/FHP.md`,
  `docs/FHGFF3.md` — read by `check_conformance.py` (rule labels, schema
  selection and checksums);
- `tests/test_fhp_schema.py`, `tests/test_fhgff3_schema.py`,
  `tests/fixtures/fhp_stub.yaml` — the unittest suite.

Evidence: `grep -rln 'fhp.json\|fhgff3.json\|fhp_linkml\|fhgff3_linkml\|examples/fhp\|examples/fhgff3\|shared.yaml\|FHP.md\|FHGFF3.md' scripts tests .github`
returns `check_conformance.py`, `check_linkml.py`, `check_release.py`,
`make_conformance.py`, `test_conformance.py`, `test_fhp_schema.py`,
`test_fhgff3_schema.py` and the three workflows. These files cannot be removed
without scoping the family checks, which is a separate change.

#### 3b. Removal candidates retained for now

- `scripts/tool_survey/**` — the completed tool survey that produced
  `docs/TOOL_COMPATIBILITY.md`. No script, test or workflow reads it, but the
  published doc and `CHANGELOG.md` link to `results/`, `make_inputs.py`,
  `run_survey.py`, `results.tsv`, `environment*.yml` and `package.json`.
  Retained: it is the provenance for a published FHR document. A future change
  could move the machinery to the shared repository and repoint the links.
- `specs/005-rna-transcriptome-header/`, `specs/006-protein-header/`,
  `specs/007-gff3-header/`, `specs/009-gff3-validator/` — per-type specs for
  other repositories, but cited by established URLs (FHT#5, FHP#1, FHGFF3#2 and
  `gff3-validator/pyproject.toml` link the `FHR-Specification` raw/blob paths).
  Retained: deleting them would break those links.
- `specs/001`, `specs/002`, `specs/003`, `specs/004`, `specs/010`, `specs/011`,
  `specs/012`, `specs/013` — FHR and shared design history (checksum vectors,
  v0.4 tightening, family, shared core, assessment, JSON-LD, versioning,
  schema.org export). `schemas/core.yaml` and `fhp.json`/`fhgff3.json` cite
  `specs/004-shared-core-schema`, and `docs/SCHEMA-CHANGES-v0.4.md` cites
  `specs/002`. Retained as provenance.
- `assessment/review/sc001-reports/**` and
  `specs/010-fair-header-assessment/research/headers/**` — review packet and
  survey evidence. The latter is read by
  `tests/test_assessment_guideline.py`. Retained as provenance and test input.
- `docs/proposals/htslib-fasta-comments.md` — linked from
  `docs/TOOL_COMPATIBILITY.md` and `CHANGELOG.md`. Retained.

### 4. Inherited shared machinery assessed and retained

No files were removed by this change. Every candidate was checked against the
published-URL rule and against references from scripts, tests, workflows and
other family repositories; each is retained for a concrete reason.

| Candidate | Why it stays |
| --- | --- |
| `.claude/skills/speckit-*/SKILL.md` | Active agent tooling, not inherited FHP/FHGFF3 material. Removing it would change contributors' workflow and is outside this issue. |
| `.specify/**` | The same Spec Kit project configuration; `constitution.md` is referenced by historical plans and tasks. |
| `specs/008-multi-format-tools/spec.md` | Historical design record for the family toolkit. It is not served by a URL, but `specs/**` is the project's design history and the issue asks to preserve history. |
| `specs/005`, `006`, `007`, `009` | Per-type specs cited by established raw/blob URLs in FHT#5, FHP#1, FHGFF3#2 and `gff3-validator/pyproject.toml`. |
| `scripts/tool_survey/**` | Provenance for the published `docs/TOOL_COMPATIBILITY.md`; the doc and CHANGELOG link its files. |

A later, separately reviewed change may remove a candidate after rechecking the
URL inventory and the cross-repository references. `scripts/check_development_tree.py`
keeps an empty removal list so such a change can add entries and have the check
enforce that they stay gone.

## What the check does

`scripts/check_development_tree.py`:

1. fails if any file in section 2 is missing or its bytes differ from the
   recorded shared-copy SHA-256;
2. lists any files classified as removable (section 4; currently none),
   reporting whether each is still present; `--strict` fails if a
   classified-removable file is still present;
3. with `--shared PATH`, compares section 2 byte-for-byte against a local
   `FAIR-bioHeaders-Specification` checkout; with `--remote`, against its raw
   `main` over the network.

Run it from the repository root:

```bash
python scripts/check_development_tree.py
python scripts/check_development_tree.py --shared ../FAIR-bioHeaders-Specification
```

## Keeping this document current

When a file moves between sections, update both this document and the
classification constants in `scripts/check_development_tree.py`, and recompute
the digests of any newly published file. Adding a new published path without a
digest makes the check fail, which is intentional.
