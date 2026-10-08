# Tasks: Shared LinkML core for FAIR-bioHeaders

**Input**: [spec.md](spec.md), [plan.md](plan.md)

- [x] T001 [US1] `schemas/core.yaml`: core slots (FR-001) with FHR's names and
      constraints, plus `Taxon`, `Author`, `AccessionID`, `sha2` and `seqcol_id`.
- [x] T002 [US1] `fhr_linkml.yml` imports the core and adds the FHR-only slots
      and classes (FR-002).
- [x] T003 [US2] Core `DerivedFrom` class, `derivedFrom` slot and the
      `HeaderType` and provisional `DerivationRelationship` enums (FR-003).
      Not added to FHR.
- [x] T004 `json-schema-generator.py`: `generate_from()` for core-importing
      schemas.
- [x] T005 [US1] `tests/test_core_schema.py` with the `tests/fixtures/fhp_stub.yaml`
      toy FHP: core slots and `derivedFrom` are generated, the core constraints
      equal `fhr.json`, and `derivedFrom` instances are checked (valid and invalid).
- [x] T006 Docs: README "Schema files", AGENTS repository map, CHANGELOG.
- [x] T007 Verify: all gates pass, `fhr.json` and the schema baseline are unchanged (SC-001).
- [ ] T008 Maintainers decide the relationship vocabulary and PROV-O/RO mapping (#54).
- [ ] T009 Maintainers decide the persistent schema URL (FR-004), then set the core `id`.
- [ ] T010 FHT, FHP and FHGFF3 modules import the core (SC-002; specs 005–007).
- [ ] T011 FHR adopts `derivedFrom` in a later schema version, with baseline review.
