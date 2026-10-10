# Contract: JSON-LD in the toolkit (`.jsonld` input and output)

**Feature**: 011-jsonld-mapping | **Repository**: FAIR-bioHeaders-Tools (package `fair-bioheaders`, import and command `bioheaders`) | Research: R-04, R-07, R-09, R-11, R-12, R-13

JSON-LD becomes one more metadata format beside `json`, `yaml`, `fasta`, `gfa` and `microdata`.
- No new subcommand.
- No new `fhr-*` entry point.
- The existing command behaviour does not change (toolkit constitution V).
- The writer and the canonical reader add **no runtime dependency**. Only the general reader
  needs the optional extra `fair-bioheaders[jsonld]`.

## Format dispatch

| Change in `bioheaders/cli.py` | Value |
|---|---|
| `FORMATS` | Add `".jsonld": "jsonld"` |
| `FORMAT_NAMES` (the choices for `--from`, `--to` and the other format options) | Add `"jsonld": "jsonld"` |

- The format is taken from the extension before `.gz`/`.bgz`, as for every other format, so
  `x.jsonld.gz` is BGZF-compressed JSON-LD.
- Stdin and stdout need `--from jsonld` or `--to jsonld`.
- Every command that reads or writes a metadata file accepts JSON-LD through the existing
  `read_metadata`/`write_metadata` dispatch:
  - `bioheaders convert` and `fhr-convert`;
  - `bioheaders validate` and `fhr-validate`;
  - the metadata argument of `combine` and `fhr-*-combine`.

```text
bioheaders convert examples/example.fhr.json /tmp/example.fhr.jsonld
bioheaders convert /tmp/example.fhr.jsonld /tmp/example.fhr.yaml
bioheaders validate /tmp/example.fhr.jsonld
bioheaders convert --from jsonld --to json - - < page-record.jsonld
bioheaders combine /tmp/example.fhr.jsonld genome.fa -o genome.fhr.fa   # metadata format from the extension
```

New option, on `convert` and `validate` only:

| Option | Default | Meaning |
|---|---|---|
| `--ignore-unknown-terms` | off | General-path JSON-LD input only (rule J4). Terms that do not map to an FHR field are reported on stderr as warnings, and conversion continues. Without the option they are an error. It has no effect on other formats or on canonical JSON-LD |

## Writing (rule J7): byte layout

`output_jsonld()` returns exactly:

```python
json.dumps(document, ensure_ascii=False, indent=2) + "\n"
```

`document` is built as follows. Dicts keep insertion order.

1. `"@context"`: the value of the `"@context"` key of the bundled `bioheaders/fhr.context.jsonld`,
   embedded, not as a URL (research R-09).
2. `"@type": "Dataset"`.
3. Every record key, in record order, with its value unchanged except that nested objects gain a
   first key `"@type"`:
   - `taxon`: `"Taxon"`;
   - each item of `metadataAuthor` and `assemblyAuthor`: `"Person"` if the item has the key
     `uri`, else `"Agent"`;
   - `accessionID`: `"PropertyValue"`;
   - each **object** item of the `assemblySoftware` array: `"SoftwareApplication"` (a legacy
     string is unchanged);
   - `vitalStats`: `"VitalStats"`.
4. Nothing else is added. Absent optional fields stay absent, and no `null` and no empty node is
   emitted (spec edge case).

**Warnings.** For each key inside `taxon`, an author item, `accessionID` or `vitalStats` that the
context does not define, `convert` prints one line to stderr and still writes the output:

```text
FHR: JSON-LD: taxon.checksum has no JSON-LD term; linked-data consumers will ignore it
```

The path uses `[i]` for array items, for example `assemblyAuthor[0].affiliation`.

`examples/example.fhr.jsonld` and `examples/minimal.fhr.jsonld` in FHR-Specification are this
output for the two JSON examples. The toolkit's output must be byte-identical (rule J7).

## Reading

`input_jsonld(stream)` decodes UTF-8, ignoring a BOM as `input_json` does, and parses JSON with
duplicate-key rejection (J2). It then chooses a path.

### Canonical path (J1): no dependency, works on Python 3.9

The document takes this path when all of these hold:
- the root is an object with `"@context"`;
- its value is either
  - an object equal, as parsed JSON, to the `"@context"` value of a **bundled released
    context**; or
  - a string in `KNOWN_CONTEXT_URLS`:
    - `https://raw.githubusercontent.com/FAIR-bioHeaders/FHR-Specification/main/jsonld/fhr.context.jsonld`;
    - `https://raw.githubusercontent.com/FAIR-bioHeaders/FHR-Specification/vX.Y.Z/jsonld/fhr.context.jsonld`;
    - `https://w3id.org/fair-bioheaders/fhr/vX.Y.Z/jsonld/fhr.context.jsonld`.

    These are recognised for each bundled release `vX.Y.Z`. The raw-main URL means the newest
    bundled context, and nothing is fetched;
- the only keys starting with `@` anywhere are the root `@context` and `@type` on objects;
- every `@type` value is a string or an array of strings.

The toolkit then removes the root `@context` and every `@type` (FR-009). The remaining object is
loaded exactly as `input_json` would load it. `fhr_validate()` (and so `convert` and `validate`)
validates it against the bundled `fhr_schema.json`, following the toolkit's schema-version
policy.

### General path (J3 to J6): needs `fair-bioheaders[jsonld]` and Python 3.10 or later

Every other JSON object document takes this path. Input that is not an object or an array is
invalid.

1. If PyLD is not installed, the read fails:

   ```text
   FHR: reading this JSON-LD form needs the jsonld extra: pip install "fair-bioheaders[jsonld]"
   ```
2. **Expand** (JSON-LD 1.1) with a document loader that serves only the bundled contexts, under
   `KNOWN_CONTEXT_URLS`. Any other URL gives:

   ```text
   FHR: JSON-LD context is not available offline: <url>
   ```

   There is no network access in any case (FR-005).
3. Collect the terms that expansion drops, through `on_property_dropped`.
4. There must be exactly one top-level node object, directly or as the only item of `@graph`.
   Otherwise:

   ```text
   FHR: JSON-LD must describe exactly one FHR record (found N nodes)
   ```
5. **Map** the expanded node back to FHR keys, scope by scope, using the reverse of the bundled
   context (data-model §4):
   - Values: `{"@value": v}` becomes `v`.
   - IRI-valued fields accept `{"@id": iri}` or `{"@value": iri}`.
   - `dateCreated` accepts `@type` `xsd:date` or no type. Any other datatype is an error.
   - The `@id` of a taxon or author node becomes `uri`.
   - `@list` becomes an array.
   - A schema array field becomes a list in document order.
   - A single-valued field with more than one value is an error:

     ```text
     FHR: JSON-LD gives 2 values for single-valued field genome
     ```
   - `assemblySoftware` with a single string value becomes that string (the legacy form).
   - A nested node given only as `{"@id": ...}`, without properties (flattened form), is an
     error.
   - Every `@type` is set aside.
6. **Unknown terms.** Dropped terms (step 3), and expanded IRIs that map to no FHR field in their
   scope (including a root `@id`), are listed:

   ```text
   FHR: JSON-LD term not in the FHR mapping: http://schema.org/keywords (at the record)
   ```

   Without `--ignore-unknown-terms`, any such term makes the read fail with exit 1. With it, each
   is printed with the prefix `FHR: warning:`, and reading continues.
7. The resulting record goes through the same validation as JSON (J6).

The general reader emits keys in `fhr.json` property order, and nested keys in their class
property order. Equality with the original record is order-insensitive for keys (research R-12).

## Errors and exit codes

There are no new exit codes:
- `0` on success;
- `1` on any error above, any schema validation failure or any I/O error, through the existing
  `run()`;
- argparse errors exit `2`.

Messages use the existing `FHR: ` prefix, and existing messages are unchanged.

## Python API (provisional, documented in the README)

```python
from bioheaders import fhr
from bioheaders import jsonld          # new module

record = fhr()
record.input_json(open("examples/example.fhr.json", "rb"))
text = record.output_jsonld()          # str, the byte layout above
record.input_jsonld(open("x.jsonld", "rb"))           # canonical or general path
record.input_jsonld(stream, ignore_unknown_terms=True)

jsonld.CONTEXT                          # dict: the bundled context document
jsonld.KNOWN_CONTEXT_URLS               # tuple of str
jsonld.to_jsonld(data: dict) -> dict    # writer, steps 1 to 4
jsonld.from_jsonld(doc, *, ignore_unknown_terms=False, warn=print_to_stderr) -> dict
jsonld.unmapped_keys(data: dict) -> list[str]   # paths for the writer warnings
```

`from_jsonld` raises `ValueError` with the messages above. It never performs I/O except calling
`warn`.

## Packaging

| File | Change |
|---|---|
| `bioheaders/fhr.context.jsonld` | New. Byte-identical to FHR-Specification `jsonld/fhr.context.jsonld` |
| `pyproject.toml` | `include` gains `bioheaders/fhr.context.jsonld`. A new extra: `[tool.poetry.extras] jsonld = ["pyld"]`, with `pyld = {version = "^3.3", optional = true, python = ">=3.10"}`. The dev group gains `pyld` with the same marker. Runtime `dependencies` are unchanged |
| `fhr/` and root compatibility copies | None. The context is not a schema copy and is not needed by the checkout-only `fhr/` scripts |
| `compat/fhr` | No change. The `fhr` distribution requires `fair-bioheaders` without extras |

## Guarantees (tested)

1. **Offline.** Every JSON-LD operation works with sockets disabled. The general path's loader
   raises for every URL that is not bundled.
2. **Round trip** (FR-004, SC-001). `from_jsonld(to_jsonld(r)) == r` for every valid record,
   compared by JSON value and type (research R-12), through the canonical path. Through the
   general path it holds for records without nested keys that lack a term.
3. **Deterministic.** The output bytes depend only on the record and the bundled context.
4. **Schema unchanged** (FR-009). `fhr_schema.json` and its two copies are untouched. JSON-LD
   keywords never reach the validator.
