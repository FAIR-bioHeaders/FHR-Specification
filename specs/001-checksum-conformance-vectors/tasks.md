# Tasks: Conformance test vectors for header parsing and checksum coverage

**Input**: [spec.md](spec.md), [plan.md](plan.md)

- [x] T001 Label the docs/FORMAT.md rules R1–R10 (non-normative annotation).
- [x] T002 [US1] `scripts/make_conformance.py`: templates, stdlib checksums,
      deterministic gzip/BGZF, manifest, coverage self-check (FR-001–FR-003, FR-006).
- [x] T003 [US1] Generate `conformance/` covering every spec edge case for FASTA and GFA.
- [x] T004 [US1] `.gitattributes`: `-text` for `conformance/**`, binary for `*.gz` (FR-004).
- [x] T005 [US2] `scripts/check_conformance.py`: up-to-date check, independent
      checksums, rule coverage, `--schema`, `--converter` (SC-003).
- [x] T006 [US2] `tests/test_conformance.py`: determinism, tamper/normalization
      detection, coverage, compressed copies, fake permissive converter.
- [x] T007 [US2] CI: a conformance job runs the stdlib checks and converter 0.3.3 from PyPI (FR-005).
- [x] T008 Docs: `conformance/README.md`, README, docs/FORMAT.md, CHANGELOG.
- [x] T009 Verify: all repository gates; converter 0.3.3 (PyPI) and main pass (SC-002).
      Converter 0.3.0 was run for comparison only (not in CI).
