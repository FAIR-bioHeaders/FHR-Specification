# Contract: `bioheaders assess` command

**Feature**: 010-fair-header-assessment | **Repository**: FAIR-bioHeaders-Tools (package `fair-bioheaders`, command `bioheaders`) | Research: R-01, R-07, R-10, R-12, R-14, R-16

`assess` is a new subcommand of the existing `bioheaders` command, added to `SUBCOMMANDS` in
`bioheaders/cli.py`. No new `fhr-*` entry point is added, and the existing commands do not
change (toolkit constitution V).

## Synopsis

```text
bioheaders assess [options] PATH [PATH ...]
bioheaders assess [options] --type FORMAT -          # one file from stdin
```

`PATH` is a file or, with `--recursive`, a directory. When several files are given, or a
directory, the command runs in **batch mode** (US4).

## Options

| Option | Default | Meaning |
|---|---|---|
| `--type {auto,fasta,gff3,gaf,vcf,gfa}` | `auto` | Format of the input. `auto` sniffs the content first, then the extension (`.gz`/`.bgz` are ignored). Required for `-` |
| `--related FILE` | none | The related file (usually the genome FASTA) for **every** derived input. Verifies the recorded links (FR-006) and runs the circumstantial check (FR-005) |
| `--pairs TSV` | none | The derived → related mapping for batch mode ([data-files.md §5](data-files.md)). Cannot be combined with `--related` |
| `--format {text,markdown,json}` | `text` | The format written to stdout in single-file mode |
| `--output DIR` | none | Writes `<rel>.assessment.json` and `<rel>.assessment.md` per file, plus `summary.json`, `summary.md` and `summary.tsv`. Required in batch mode. The directory is created if missing. Existing report files are replaced atomically (temporary file, then `os.replace`) |
| `--recursive` | off | Descend into the directories given as `PATH` |
| `--include GLOB` / `--exclude GLOB` | all / none | Repeatable. Matched against paths relative to the root. Hidden files and directories are skipped unless included explicitly |
| `--record-limit N` | `1000` | The maximum number of data records sampled after the header (research R-14). `0` reads the header only |
| `--jobs N` | `min(CPU count, 8)` | Number of files assessed in parallel. The output order does not depend on `N` |
| `--online` | off | Opt in to resolving header identifiers and URLs (FR-011, research R-10). File contents are never sent |
| `--online-timeout SECONDS` | `10` | Per-request timeout (only with `--online`) |
| `--hash-inputs` | off | Adds the full-file SHA-256 (`input.file_sha256`). This costs a full read |
| `--fail-on-mismatch` | off | Exit 3 if any recorded link verdict is `mismatch` |
| `--version`, `-h/--help` | | As for the other subcommands. The help epilogue carries the RDA attribution (research R-19) |

## Outputs

| Mode | stdout | Files |
|---|---|---|
| Single file, no `--output` | The report in `--format` | none |
| Single file, `--output DIR` | A one-line status per file | `DIR/<name>.assessment.json`, `DIR/<name>.assessment.md` |
| Batch (`--output` required) | A progress line per file, then the `summary.md` table | Per-file reports mirroring the input tree, plus `summary.json`, `summary.md` and `summary.tsv` |

- The JSON validates against [assessment-report.schema.json](assessment-report.schema.json). It
  is written with sorted keys, UTF-8, LF line endings and a trailing newline.
- The text and Markdown forms render the same report, with these sections:
  1. the input;
  2. the online-checks line ("Online checks: not requested" or "ran");
  3. the FAIR-bioHeaders conformance result, when a FAIR-bioHeaders header is present (FR-008);
  4. the **checklist**: one row per indicator, grouped F/A/I/R, giving the status, the evidence
     lines (`line N: raw text`) and the suggestion;
  5. the recorded links and their verdicts;
  6. "Circumstantial evidence (not a recorded link)", when a related file was given;
  7. the findings;
  8. the attribution.

  The words "score", "FAIR score", "is FAIR" and "certified" never appear (FR-004). A test checks
  this.
- `summary.tsv` has the columns `path`, `format`, `scope`, `pair_classification`, then one column
  per indicator in rubric order. The cell values are `E` (evidenced), `P` (partially evidenced),
  `N` (not evidenced), `NA` (not applicable) and `NAS` (not assessed). It has no total column.
- Diagnostics go to stderr, prefixed `FHR: ` like the other subcommands.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Every input was assessed or reported as out of scope. Statuses of any kind, including all `not_evidenced`, are not failures (US1 scenario 2) |
| `1` | At least one input could not be read: a missing path, permission denied, corrupt gzip, or an unreadable `--related` file. Reports for the other inputs are still written. This code also covers an output write failure |
| `2` | Usage error (argparse): an unknown option, `--related` together with `--pairs`, a duplicate derived path in `--pairs`, `-` without `--type`, batch mode without `--output`, `--online-timeout` without `--online`, a directory without `--recursive`, `--pairs` without exactly one directory `PATH`, or two inputs with the same report path |
| `3` | Only with `--fail-on-mismatch`: at least one recorded link verdict is `mismatch`. This takes precedence over 0, but not over 1 |

## Behavioural guarantees

1. **No network** unless `--online` is given (FR-010, FR-011). The tests run with sockets
   disabled.
2. **Reproducible**: with the same input bytes, options, tool version and data-file versions, the
   JSON and Markdown reports are byte-identical, apart from the `online` section (FR-009, US4).
3. **Never modifies inputs**, and never writes beside them unless `--output` points there.
4. **One reading of FAIR-bioHeaders lines**: the FHR header is read with the same functions as
   `bioheaders validate` and `verify` (toolkit constitution II).
5. **Bounded memory**: at most 16 MiB of header per file and 1 MiB per line. A related file is
   streamed, keeping only its name, length and digest table (toolkit constitution III).

## Examples

```bash
# One file, terminal report
bioheaders assess GCF_000002985.6_WBcel235_genomic.gff.gz

# Machine-readable report
bioheaders assess --format json c_elegans.PRJNA13758.WS298.annotations.gff3.gz > ws298.json

# Annotation against its genome (US2)
bioheaders assess --related c_elegans.PRJNA13758.WS298.genomic.fa.gz \
    c_elegans.PRJNA13758.WS298.annotations.gff3.gz

# A whole release (US4), with pairs, in CI that must fail on a mismatched link
bioheaders assess --recursive --pairs pairs.tsv --output reports/9.1.0 \
    --fail-on-mismatch release-9.1.0/

# From a pipe
curl -sL https://example.org/file.vcf.gz | bioheaders assess --type vcf -
```

## Python API (secondary, for the 009 validator and notebooks)

```python
from bioheaders.assess import assess_file, assess_release
report: dict = assess_file(path, related=None, online=False, record_limit=1000)
summary: dict = assess_release(paths, output_dir, pairs=None, jobs=None, online=False)
```

Both return plain dicts that conform to the JSON Schemas. The API is new and versioned with the
package. It is documented as provisional until 1.0 of the report format is confirmed by provider
feedback (SC-005).

## Implementation notes (toolkit, 2026-10-10)

Decisions taken while implementing batch mode and the online checks (tasks T048-T054). They
refine this contract; none changes an option, an output file or an exit code above.

- **Paths in batch reports.** Per-file reports in batch mode give `input.path` and
  `verification.related_path` relative to the directory (or the file name, for a file given
  as `PATH`), so reports do not depend on where the release is stored. `summary.json` `root`
  is the directory as given, or null for several `PATH`s.
- **`summary.json`** has the ReleaseSummary fields of data-model §14 plus `attribution` and
  `online_checks`, like a report. Keys are sorted; there is no per-file total.
- **Output inside the input tree.** The `--output` directory is never walked, so a re-run
  into a directory inside the release gives the same result.
- **Pairs.** `--pairs` needs exactly one directory `PATH`; its paths are relative to it. A
  related file is scanned once per run and its scan is handed to the worker processes.
- **`--online` in batch mode** assesses the files in one process (related-file scans stay
  parallel), so that requests are made one at a time and de-duplicated across the run.
- **Online requests.** Only the HTTP and HTTPS handlers of `urllib` are installed: proxies
  from the environment, cookies, credentials, FTP, `file:` and `data:` URLs are not used. A
  URL with credentials, spaces or control characters, or a scheme other than http(s), is
  `refused` without a request. Every address a host resolves to must be public; the
  connection is made to the vetted address. GET with `Range: bytes=0-0` follows only when
  HEAD returns an HTTP error (status 400 or more). Redirects keep the method and headers and
  are re-checked; a sixth redirect gives `unavailable`.
- **Online outcomes.** 2xx is `resolved`; 404 and 410 are `not_found`; other HTTP errors,
  timeouts and network errors are `unavailable`. An access indicator is `evidenced` if one of
  its header values resolved, `not_evidenced` if the header has no value for it or every
  value was `not_found`, and otherwise `not_assessed` (`online-check-unavailable`), which
  also covers `refused` and values that are not a DOI, CURIE or URL. RDA-F1-01D, RDA-I2-01M
  and RDA-R1.1-03M get a note per checked value and keep their offline status.
- **Values resolved.** Header values of the concepts `data-identifier`, `access-url`,
  `taxon`, `creator` and `licence`, from file-level header lines only. The FAIR-bioHeaders
  `schema` value is never requested, even if it also appears under another key.

