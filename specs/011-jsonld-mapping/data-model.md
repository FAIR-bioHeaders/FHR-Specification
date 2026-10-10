# Data model: JSON-LD mapping

**Feature**: 011-jsonld-mapping | **Date**: 2026-10-10 | **Plan**: [plan.md](plan.md)

This model covers the spec's three key entities (Context, Vocabulary term, Mapping entry) and the
entities the toolkit needs to write and read JSON-LD. The field names are those of the contracts:

- [fhr.context.jsonld](contracts/fhr.context.jsonld);
- [vocabulary.md](contracts/vocabulary.md);
- [mapping-table.schema.json](contracts/mapping-table.schema.json);
- [cli.md](contracts/cli.md).

```text
LinkML model (schemas/core.yaml + fhr_linkml.yml)        ← single source of term IRIs (R-08)
   │  slot_uri / class_uri / default_prefix fhr / annotations
   ▼
scripts/make_jsonld.py ──► Context (jsonld/fhr.context.jsonld) 1──* Scope 1──* TermDefinition
                     ├──► Vocabulary (jsonld/terms.ttl, docs/TERMS.md) 1──* VocabularyTerm
                     └──◄ MappingTable (mappings/fhr-jsonld-dcmi.yml) 1──45 MappingEntry  (curated; checked against LinkML)

FHR record ──writer (TypingRule)──► JSON-LD document ──reader──► FHR record
                                           │ canonical path (J1) / general path (J3–J6, ReverseMap)
                                           └──► ReadReport (UnknownTerm*)
```

---

## 1. Context

This is a spec key entity: the published JSON-LD context document.

| Field | Type | Rules |
|---|---|---|
| `@version` | `1.1` | Required. Property-scoped contexts and `@protected` need 1.1 |
| `@protected` | `true` | Top-level terms cannot be redefined by a later context |
| prefixes | `sdo`, `fhr`, `xsd`, `dct` | `sdo` = `http://schema.org/`, `fhr` = `https://w3id.org/fair-bioheaders/terms#`, `dct` = `http://purl.org/dc/terms/` (root only, for `conformsTo`). **No `schema` prefix**, because `schema` is an FHR key (R-05). **No `@vocab`** |
| type terms | `Dataset`, `Taxon`, `Person`, `Organization`, `Agent`, `PropertyValue`, `SoftwareApplication`, `VitalStats` | `Dataset` is declared at the root. The others are declared in the scope where they are used |
| term definitions | one per FHR key, in `fhr.json` property order | See TermDefinition (§2) |
| output-only terms (root, after the FHR keys) | `subjectOf` (`sdo:subjectOf`, `@id`), `keywords` (`sdo:keywords`, `@set`), `url` (`sdo:url`, `@id`), `conformsTo` (`dct:conformsTo`, `@id`) | Not FHR keys. `subjectOf` carries a `documentation` URL (maintainer decision 3; LinkML annotation `jsonld_slot_uri_if_url`); the others come only from an export context (maintainer decision 2; a constant in `make_jsonld.py`) |

**Identity and version**:
- The file is `jsonld/fhr.context.jsonld`, at the canonical URL raw-main.
- Released copies are addressed as `https://w3id.org/fair-bioheaders/fhr/vX.Y.Z/jsonld/fhr.context.jsonld`.
- The toolkit bundles every released version.
- Within one FHR schemaVersion the context changes only additively (R-09).

**Validation**:
1. It is generated, so `make_jsonld.py --check` reports no drift.
2. It is injective per scope (§2 rule 4).
3. Every key of `fhr.json`, at every depth, is a term in the right scope (FR-001).
4. Every `fhr:` IRI it uses is defined in the vocabulary.

## 2. Scope and TermDefinition

A scope is the active context for one kind of node. There are six scopes:

| Scope | Entered through | Type term(s) | Keys |
|---|---|---|---|
| `record` | the document root | `Dataset` | the 24 top-level FHR keys |
| `taxon` | `taxon` | `Taxon` | `name`, `uri` |
| `author` | `metadataAuthor`, `assemblyAuthor` | `Person`, `Organization`, `Agent` | `name`, `uri` |
| `accession` | `accessionID` | `PropertyValue` | `name`, `url` |
| `vitalStats` | `vitalStats` | `VitalStats` | the 9 statistics |
| `software` | `assemblySoftware` | `SoftwareApplication` | `name`, `uri`, `version`, `commandLineOption` |

`author` is shared by the two author lists, which have identical definitions.

Each nested scope is a **property-scoped context that starts with `null`**: it inherits nothing
from `record` (R-06).

| TermDefinition field | Values | Derived from (LinkML) |
|---|---|---|
| key | the FHR key | slot or attribute name |
| `@id` | a full IRI via `sdo:` or `fhr:`, or the keyword `@id` | `slot_uri`, else `default_prefix` (`fhr`) + name. The keyword `@id` comes from the annotation `jsonld_node_id: true` |
| `@type` | `@id` or `xsd:date`, or absent | range `uri`, or the annotation `jsonld_iri: true` (on `schema`, which `fhr.json` types as a plain string), gives `@id`; range `date` gives `xsd:date` |
| `@container` | `@set`, `@list`, or absent | `multivalued` gives `@set`. `multivalued` plus `list_elements_ordered` gives `@list`. `assemblySoftware` (any_of string or a multivalued class) gives `@set` |
| `@context` | the nested scope | a class range (inlined) |

**Rules**:
1. A field that may be free text or an identifier is never IRI-coerced (R-06 rule 4).
2. The type terms of a scope are exactly those the TypingRule (§5) can emit there.
3. Numbers are never coerced.
4. **Injectivity.** In each scope the map from key to `@id` is one-to-one. The keyword `@id` may
   appear once per scope.

## 3. VocabularyTerm

This is a spec key entity: an FHR-specific property or class.

| Field | Type | Rules |
|---|---|---|
| `iri` | IRI in `https://w3id.org/fair-bioheaders/terms#` | Local name = LinkML name. Unversioned and never reused (FR-008) |
| `kind` | `property` or `class` | |
| `label` | string | The FHR key or class name |
| `description` | string, non-empty | The LinkML description. FR-002 requires one for every term |
| `domainIncludes` | list of class IRIs | The `class_uri` of every class that uses the slot |
| `rangeIncludes` | list of IRIs | `sdo:Text`, `sdo:Number`, `sdo:Integer`, `sdo:URL` or the range class IRI |
| `subPropertyOf`, `subClassOf`, `closeMatch` | optional IRIs | Only as listed in [vocabulary.md](contracts/vocabulary.md) |
| `deprecated` | boolean | Default false. A deprecated term is kept |

Release 1 has 2 classes and 22 properties (research R-03; listed in vocabulary.md).

## 4. MappingEntry

This is a spec key entity: one row of `mappings/fhr-jsonld-dcmi.yml`, one per FHR property path.

| Field | Type | Rules |
|---|---|---|
| `path` | string, for example `assemblySoftware[].commandLineOption[]` | The set of paths equals the set of property paths in `fhr.json` (45 in schemaVersion 1). Unique |
| `jsonld.term` | IRI or `@id` | Equals the IRI derived from LinkML for that path. Never `none` (FR-001) |
| `jsonld.status` | `core`, `pending`, `fhr` or `keyword` | `core`/`pending` must match the pinned schema.org subset |
| `jsonld.kind` | a kind (R-02) | `exact` for every `fhr:` term |
| `jsonld.coercion` | `literal`, `iri`, `node-id`, `xsd:date`, `node`, `set`, `list`, `set-of-iri` or `set-of-nodes` | Agrees with the context |
| `jsonld.type` | list of type IRIs | For node-valued paths: the TypingRule outputs |
| `schemaorg_gap` | string | Required for `fhr:` terms: the closest candidate and why it was rejected |
| `dcmi[]` | list of mappings, at least 1 | `{term: none, kind: unsupported, reason}`, or DCMI term IRIs (`http://purl.org/dc/terms/…`) that are in the pinned term list |
| `*.condition` | string | Required when `kind` = `conditional` |
| `*.loss` | string | Required when `kind` = `lossy` |
| `*.subject` | `assembly`, `record` or `nested` | `record` for `schema` and `metadataAuthor` (and their nested paths) |
| `*.rdf_loss` | string | For example "order of @set items" on the author lists and `identifier` |
| `notes`, `sources` | string, list of URLs | `sources` cites #56, MAPPINGS.md and the vocabulary pages |

**Derived ReverseMap.** The toolkit derives this from the bundled context, not from the YAML,
so that the toolkit does not need the table. For each scope it maps an IRI to
`(FHR key, coercion, child scope)`. The general reader uses it (§7).

## 5. TypingRule (writer, FR-006)

| Node | Condition | `@type` |
|---|---|---|
| record | always | `Dataset` |
| `taxon` | always | `Taxon` |
| author item | `uri` is an ORCID iD (the `fhr.json` pattern) | `Person` |
| author item | `uri` is a ROR ID | `Organization` |
| author item | no `uri`, or any other `uri` | `Agent` |
| `accessionID` | always | `PropertyValue` |
| `assemblySoftware` item | the item is an object | `SoftwareApplication` |
| `vitalStats` | always | `VitalStats` |

`@type` is the first key of the node, after `@context` at the root. LinkML source:
- `class_uri` of each class;
- `jsonld_type_if_orcid: sdo:Person` and `jsonld_type_if_ror: sdo:Organization` on `Author`,
  whose `class_uri` is `fhr:Agent` (maintainer decision 4).

A `documentation` value that is an absolute URL is written under `subjectOf` (maintainer
decision 3). With an export context, the record node also gets `@id`, `keywords`, `url` and,
only when the Bioschemas Dataset 1.0-RELEASE minimum properties are all present, `conformsTo`
(contracts/cli.md "Writing" step 5).

## 6. JSON-LD document

| Form | Definition | Read by |
|---|---|---|
| **Canonical** | The writer output (cli.md "Writing"). Generally: an FHR record plus a root `@context` (an embedded bundled context, or a known URL), plus `@type` on any objects and an optional root `@id`, and no other keyword. A root `subjectOf` is read as `documentation`; the export terms are set aside with a warning | The canonical path (J1). No dependency |
| **General** | Any other JSON-LD 1.1 tree with exactly one top-level node (directly or in a single-item `@graph`): expanded form, compaction against another context, keys reordered | The general path (J3–J6). Needs the `jsonld` extra |
| **Unsupported** | Flattened (nested nodes by reference), several top-level nodes, non-bundled or remote contexts, a JSON value that is not an object or an array | Error |

**State transitions** (reader):

```text
bytes ─decode/parse (J2)─► JSON value
  ├─ canonical? ─yes─► set aside @context/@type ─► FHR dict ─► schema validation (J6) ─► record | error
  └─ no ─► extra installed? ─no─► error "needs the jsonld extra"
             └─ yes ─► expand with the bundled-only loader (J3) ─► one node? (J4) ─► ReverseMap mapping (J5)
                        ─► unknown terms? ─► error | warnings (--ignore-unknown-terms) ─► schema validation (J6)
```

## 7. ReadReport and UnknownTerm

| Field | Type | Rules |
|---|---|---|
| `unknown[]` | list of `{term, scope, reason}` | `reason` is `dropped` (no IRI during expansion), `unmapped` (an IRI with no FHR field in this scope) or `root-id` (a root `@id`) |
| `warnings[]` | list of strings | The writer's unmapped-key warnings (R-07), or the unknown terms when they are ignored |

On reading, a non-empty `unknown` is an error unless `ignore_unknown_terms`. It is never
silently dropped (spec edge case).

## 8. Round-trip equality (FR-004)

`equal(a, b)`:
- objects: the same key sets and equal values, ignoring key order;
- arrays: equal in order;
- scalars: `a == b` and `type(a) is type(b)`, so `int` is not `float` and `bool` is not `int`.

SC-001 tests use this through the canonical path for every example and conformance metadata
record (research R-12).
