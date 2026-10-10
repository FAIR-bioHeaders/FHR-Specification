# Contract: the FAIR-bioHeaders vocabulary (`terms#`)

**Feature**: 011-jsonld-mapping | **Repository**: FHR-Specification | Research: R-05, R-08, R-10, R-17

The vocabulary defines every FHR-specific term that the JSON-LD context uses (FR-002, FR-008).
It is **generated** by `scripts/make_jsonld.py` from the LinkML model, and it is committed.
Nobody edits it by hand; `make_jsonld.py --check` fails on drift.

## Namespace

- `https://w3id.org/fair-bioheaders/terms#`. It is unversioned: a term IRI never changes and is
  never reused with another meaning.
- The local name is exactly the LinkML slot or class name, which is the FHR key. Examples:
  `seqcol_id`, `commandLineOption`, `VitalStats`.
- The vocabulary is family-wide. Terms that later header types share (FHT, FHP, FHGFF3) reuse
  the same IRI. A new term is added only when a header type needs it, with a changelog entry.
- **Deprecation.** A term is never deleted. It gains `owl:deprecated true` and a
  `dcterms:isReplacedBy` if a replacement exists.

## Files

| File | Purpose | Media type served |
|---|---|---|
| `jsonld/terms.ttl` | RDF vocabulary (Turtle) | `text/turtle` requested. Raw GitHub actually serves `text/plain` (known limitation, research R-09) |
| `docs/TERMS.md` | Human documentation page and the default redirect target | HTML (GitHub-rendered) |

## `jsonld/terms.ttl` layout

The prefixes are fixed, the term blocks are sorted (classes first, then properties, each
alphabetically by local name), and the file ends with a trailing newline. Every term carries:

| Predicate | Required | Source |
|---|---|---|
| `a rdf:Property` or `a rdfs:Class` | yes | LinkML slot or class |
| `rdfs:label` (`@en`) | yes | The FHR key itself, for example `"seqcol_id"@en` |
| `rdfs:comment` (`@en`) | yes | The LinkML description (equal in meaning to the `fhr.json` description) |
| `rdfs:isDefinedBy <https://w3id.org/fair-bioheaders/terms>` | yes | constant |
| `sdo:domainIncludes` | properties | The `class_uri` of every class that uses the slot (FHR → `sdo:Dataset`) |
| `sdo:rangeIncludes` | properties | `sdo:Text`, `sdo:Number`, `sdo:Integer` or `sdo:URL`, or the type IRIs the writer emits for the range class (for authors `sdo:Person`, `sdo:Organization` and `fhr:Agent`) |
| `rdfs:subPropertyOf` | when stated | From a LinkML `broad_mappings` entry that points at an `sdo:` property. In release 1 that is `fhr:accessionID rdfs:subPropertyOf sdo:identifier`. The mapping table must agree (test) |
| `rdfs:subClassOf` | classes | `sdo:Thing` for `fhr:Agent`; `sdo:StructuredValue` for `fhr:VitalStats`. LinkML source: the class annotation `vocabulary_subclass_of` (and `vocabulary_comment` for the `fhr:Agent` comment, since the `Author` class description describes authors) |
| `skos:closeMatch` | when stated | From LinkML `close_mappings`. In release 1 that is `fhr:Agent skos:closeMatch dcterms:Agent` |
| `owl:deprecated`, `dcterms:isReplacedBy` | when deprecated | |

The ontology header node:

```turtle
@prefix fhr:     <https://w3id.org/fair-bioheaders/terms#> .
@prefix sdo:     <http://schema.org/> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:     <http://www.w3.org/2002/07/owl#> .
@prefix skos:    <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<https://w3id.org/fair-bioheaders/terms> a owl:Ontology ;
    rdfs:label "FAIR-bioHeaders vocabulary"@en ;
    rdfs:comment "Terms for FAIR-bioHeaders metadata that have no schema.org equivalent. Generated from the FHR-Specification LinkML model; do not edit."@en ;
    dcterms:license <https://www.mozilla.org/en-US/MPL/2.0/> ;
    rdfs:seeAlso <https://github.com/FAIR-bioHeaders/FHR-Specification/blob/main/docs/TERMS.md> .
```

Example term blocks (illustrative; the generated file is authoritative):

```turtle
fhr:Agent a rdfs:Class ;
    rdfs:label "Agent"@en ;
    rdfs:comment "A person or organization that the FHR record does not classify; FHR records the kind of agent only through an ORCID or ROR identifier."@en ;
    rdfs:subClassOf sdo:Thing ;
    skos:closeMatch dcterms:Agent ;
    rdfs:isDefinedBy <https://w3id.org/fair-bioheaders/terms> .

fhr:seqcol_id a rdf:Property ;
    rdfs:label "seqcol_id"@en ;
    rdfs:comment "Unprefixed GA4GH refget sequence collection top-level digest (sha512t24u); supplied by the user, not calculated by FHR."@en ;
    sdo:domainIncludes sdo:Dataset ;
    sdo:rangeIncludes sdo:Text ;
    rdfs:isDefinedBy <https://w3id.org/fair-bioheaders/terms> .
```

### Terms in release 1

These are derived from research R-03.

- **Classes (2)**: `Agent` and `VitalStats`.
- **Properties (22)**:
  - top-level: `schemaVersion`, `metadataAuthor`, `voucherSpecimen`, `accessionID`,
    `instrument`, `relatedLink`, `masking`, `vitalStats`, `checksum`, `assemblySoftware`,
    `assemblyProtocol` and `seqcol_id`;
  - in `vitalStats`: `L50`, `N50`, `L90`, `N90`, `totalBasePairs`, `numberContigs`,
    `numberScaffolds`, `readTechnology` and `gcContent`;
  - in `assemblySoftware`: `commandLineOption`.

The core slots that FHR schemaVersion 1 does not use (`derivedFrom`, `headerType`,
`relationship`) get **no** term until a header type uses them and #54 decides their vocabulary.

## `docs/TERMS.md` layout

The page is generated. It has a short introduction (namespace, licence, how to cite, link to
`docs/JSONLD.md` and the mapping table), then one section per term, sorted like the Turtle file:

```markdown
### seqcol_id

`https://w3id.org/fair-bioheaders/terms#seqcol_id`. Property.

Unprefixed GA4GH refget sequence collection top-level digest (sha512t24u); supplied by the user, not calculated by FHR.

- Used on: Dataset (the FHR record)
- Value: Text
- DCMI: none (see the [mapping table](../mappings/fhr-jsonld-dcmi.yml))
```

The heading text is exactly the local name, so GitHub's anchor is `#seqcol_id`. A test asserts
that every term has exactly one heading.

## w3id registration (maintainer action; prepared, not submitted)

The rules below go into `ids/fair-bioheaders/.htaccess` in perma-id/w3id.org, before the
existing `fhr/` rules. The header comment gains the bullet shown. A PR may be opened only by Adam
Wright or David Molik, the administrators of `/fair-bioheaders/`.

```apache
# - https://w3id.org/fair-bioheaders/terms is the namespace of FAIR-bioHeaders
#   vocabulary terms (https://w3id.org/fair-bioheaders/terms#checksum etc.).
#   RDF clients asking for Turtle get the vocabulary file; everyone else gets
#   its documentation page, where each term has an anchor.
RewriteCond %{HTTP_ACCEPT} text/turtle
RewriteRule ^terms/?$ https://raw.githubusercontent.com/FAIR-bioHeaders/FHR-Specification/main/jsonld/terms.ttl [R=302,L]
RewriteRule ^terms/?$ https://github.com/FAIR-bioHeaders/FHR-Specification/blob/main/docs/TERMS.md [R=302,L]
```

Checks before submitting:
1. Run `node tools/check/bin/w3id-check.js` in a clone. There must be no error, and no
   `htaccess/no-406-fallback`, `htaccess/github-raw-target` (`/blob/` is for documentation only)
   or `htaccess/avoid-permanent-redirect` warning.
2. Run a local Apache from `tools/server` and request the namespace twice:
   - `curl -sI -H 'Accept: text/turtle' http://localhost/fair-bioheaders/terms` → 302 to `terms.ttl`;
   - `curl -sI http://localhost/fair-bioheaders/terms` → 302 to `TERMS.md`.
3. Confirm that the targets exist on `main`: `jsonld/terms.ttl` and `docs/TERMS.md` are merged.
4. Confirm that the existing rules still behave as before (`fhr/vX.Y.Z`, `gff3-validator`).

## Verification (FHR-Specification)

- `python scripts/make_jsonld.py --check`: the context, `terms.ttl` and `TERMS.md` are up to date.
- `tests/test_jsonld_vocabulary.py`:
  - `terms.ttl` parses with rdflib, which `requirements-linkml.txt` already installs as a
    LinkML dependency;
  - every `fhr:` IRI in the context and the mapping table is defined, with a label and a
    comment;
  - no term is defined twice;
  - every term has a heading in `TERMS.md`.
