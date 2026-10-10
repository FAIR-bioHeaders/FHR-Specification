# FAIR header assessment fixtures

These files are the shared fixtures of feature 010
([specs/010-fair-header-assessment](../specs/010-fair-header-assessment/)). They are
used to check any implementation of the FAIR header assessment, such as
`bioheaders assess` in FAIR-bioHeaders-Tools, against implementation-neutral
expected outcomes. They follow the pattern of [`conformance/`](../conformance/).

## Layout

- `headers/`: real header lines captured from public provider download files during
  the Phase 0 survey (research/survey.md §R3). Each file holds only the original
  header lines; the survey's provenance comment lines were removed and the source
  URL and fetch time moved to `manifest.json`. Long runs of `##sequence-region`
  lines that the survey shortened are not reconstructed.
- `pairs/`: small synthetic annotation and genome pairs for User Story 2, made by
  `scripts/make_assessment_fixtures.py`. Sequence names and lengths are
  scaled-down WBcel235 style; the sequences are synthetic.
- `edge/`: synthetic edge cases (no header, compression, archives, binary stubs,
  mixed conventions, malformed and conflicting values), made by the same script.
- `review/`: reviewer agreement tables for SC-001 (`sc001-<date>.tsv`).
- `manifest.json`: one entry per fixture with its provenance and the expected
  outcomes the fixture exercises. Its format is `manifest.schema.json`.
- `pairs.tsv`: derived → related pairs for batch runs.

Every file is byte-exact: `.gitattributes` turns off line-ending conversion here.
Regenerate the synthetic files with `python scripts/make_assessment_fixtures.py`
instead of editing them.

## Running

```bash
python scripts/check_assessment.py --tool ../FHR-File-Converter
```

`--tool` takes a toolkit checkout, a virtual environment or bin directory, or
`PATH`.

## Licence

New files here are licensed MPL-2.0 (see [LICENSE](../LICENSE) and CONTRIBUTING.md).
The captured provider header lines are short factual metadata from public download
files, used as test fixtures with their source URLs recorded in the manifest.
