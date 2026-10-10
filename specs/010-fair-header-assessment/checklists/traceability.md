# Traceability: spec ↔ plan ↔ tasks

**Feature**: 010-fair-header-assessment | **Created**: 2026-10-10 | **Inputs**: [spec.md](../spec.md), [plan.md](../plan.md), [research.md](../research.md), [data-model.md](../data-model.md), [contracts/](../contracts/), [tasks.md](../tasks.md)

This is the result of an analyze-style consistency pass. Every functional requirement, success
criterion, acceptance scenario and edge case is traced to the design decisions and to the tasks
that implement (I) or test (T) it.

## Functional requirements

| Req | Summary | Design | Tasks (T = test, I = implement) |
|---|---|---|---|
| FR-001 | Any text format. Recognise FAIR-bioHeaders, FASTA, GFF3, GAF and VCF headers | R-02, R-15; data-model §1–2 | T: T006, T019, T020. I: T009, T013, T016, T026, T027 |
| FR-002 | Five statuses with reasons; cite the evidence lines | R-04, R-05; data-model §5; report schema `result` | T: T004, T021, T023. I: T010, T012, T030 |
| FR-003 | A concrete suggestion for every gap, in the file's convention or as a FAIR-bioHeaders field | R-11; data-model §7; rubric `suggestions` | T: T021, T024. I: T010, T031, T046 |
| FR-004 | A checklist with evidence; no score, no "is FAIR" | R-04, R-16; report schema `additionalProperties: false` | T: T023, T048. I: T014, T032, T050 |
| FR-005 | Recorded link reported separately from circumstantial consistency | R-06, R-08; data-model §8–10 | T: T037, T036. I: T028, T040, T041 |
| FR-006 | Check a recorded identity against the related file: match, mismatch or unverifiable | R-07; data-model §8 | T: T036, T037. I: T038, T039, T042 |
| FR-007 | Guideline maps items to principles, gives ≥ 2 file types, uses core field names | R-17; data-model §13 | T: T043. I: T044, T045, T046 |
| FR-008 | FAIR-bioHeaders schema conformance reported separately | R-09; data-model §11 | T: T019 (FHR and FHT fixtures), T022. I: T029 |
| FR-009 | Human-readable and machine-readable reports; reproducible | R-12; contracts/cli.md guarantee 2 | T: T023, T048, T049. I: T014, T032, T050 |
| FR-010 | File contents never sent anywhere | R-10; cli.md guarantee 1 | T: T002 (sockets blocked), T023, T053. I: T054 |
| FR-011 | Offline by default; online opt-in; the report says whether online checks ran | R-10; data-model §12 | T: T023, T053. I: T054 |
| FR-012 | Based on the RDA indicators, with file-header interpretations; N/A with reasons | R-03, R-19; rubric (41 entries) | T: T004, T021. I: T010, T044 |

## Success criteria

| SC | Summary | Design | Tasks |
|---|---|---|---|
| SC-001 | ≥ 5 providers and 4 types; ≥ 90% reviewer agreement | R-18, R-21 | T016, T018, T035 (corpus); T061 (independent review) |
| SC-002 | Suggestions can be applied without other documentation | R-11 | T024 (automated proxy); T061 (reviewer column `note`) |
| SC-003 | Correct, mismatched and partial pairs classified correctly | R-07, R-08; data-model §10 | T036, T037, T042 |
| SC-004 | 200 files in under 10 minutes on a laptop | R-14 | T050, T052, T060 |
| SC-005 | A provider runs it and reports it useful | R-21 | T056 (trial guide). The outreach itself is a maintainer action and not a task |

## Acceptance scenarios and edge cases

| Item | Tasks |
|---|---|
| US1-1: GFF3 with an assembly accession gets credit, citing the line | T018, T021 |
| US1-2: FASTA with no header gives all not evidenced, with suggestions, not an error | T019, T021, T025 |
| US1-3: FHR header reflected in the checklist; conformance separate | T019, T022, T029 |
| US2-1: Recorded identity matches or does not match the genome | T036, T037, T039 |
| US2-2: No recorded identity gives a circumstantial name and length check, labelled as such | T036, T040 |
| US2-3: Missing names are listed | T036, T037, T040 |
| US3-1: Every item cites its principle; every relevant principle covered or out of scope | T043, T044 |
| US3-2: Items expressed in the existing convention | T044, T031 |
| US4: 200 files give a summary and per-file reports; identical re-runs | T048, T049, T050, T052 |
| Edge: gzip, BGZF, too large to read whole | T006, T013, T020 (header-truncated), T052 |
| Edge: several conventions in one file | T019 (FHR plus `##`), T026 |
| Edge: unknown convention reported as unrecognised lines | T019, T020 |
| Edge: identifier-like free text | T019, T021, T027 |
| Edge: recorded genome identity present but malformed | T019, T036, T028, T039 |
| Edge: binary formats out of scope | T006, T013, T019, T025 |

## Consistency findings

The pass found these points. Each one is resolved in the artefacts as noted.

1. **Status vocabulary.** `research/rda-indicators.md` (appendix B) still describes four statuses,
   with `online-check-not-run` and `deferred-data-body` as not-applicable reasons. That is
   superseded by the spec clarification (FR-002) and research R-03/R-04. Those two cases are now
   `not_assessed`. research.md states that it takes precedence over the appendices.
2. **FASTA with no header versus US1-2.** Appendix B made an undeclared FASTA "partial" on the
   format indicators, which would contradict "every principle is reported as not evidenced".
   Research R-05 resolves this: a format recognised only by sniffing is not header evidence.
   T019 and T021 test it.
3. **"Per principle" versus "per indicator".** US1 and SC-001 speak of principles. FR-012 and the
   design report per RDA indicator, grouped by principle (F/A/I/R) in the human-readable form.
   Agreement per indicator is a stricter test than agreement per principle, so SC-001 is still
   met if per-indicator agreement reaches ≥ 90%.
4. **"Criterion" entity.** The spec's Key Entity "Criterion" is the RDA *Indicator* in the
   rubric (data-model §4).
5. **Fixture location.** Putting the fixtures under `conformance/` would break
   `check_conformance.py` (a nested `manifest.json`). They go in a top-level `assessment/`
   (plan, Structure Decision).
6. **The DerivedFrom shape.** `schemas/core.yaml` requires `headerType` and `relationship`, and
   `checksum` is optional. The suggestions therefore always state a relationship, and they use a
   placeholder checksum or accession (T010, T031). The relationship vocabulary is provisional
   (#54, open question 5).
7. **Coverage.** Every FR and SC maps to at least one implementing task and one testing or
   validating task. No task lacks a requirement or plan source. The polish tasks T055–T059 and
   T062 support the constitution gates and the quickstart.

No CRITICAL or HIGH issues remain. The open maintainer questions (plan.md) have stated defaults,
so none of them blocks the MVP.
