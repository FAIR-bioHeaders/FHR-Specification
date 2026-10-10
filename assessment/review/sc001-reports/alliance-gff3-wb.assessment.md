# FAIR header assessment: headers/alliance\_gff3\_GFF\_WB\_4.gff (gff3, none)

- Input: assessed; format from content; header lines read: 12; records sampled: 0
- Header SHA-256: 5908a1ad6e1753bb694273b5be0b55e675574442416b37560f008a376fc3f68f
- Online checks: not requested
- Rubric 1.1.0, synonyms 1.0.0, formats 2026-10-10, id-schemes identifiers.org-2026-10-10, spdx-licenses 3.29.0; bioheaders assess 0.4.0

## Findable

| Indicator | Status | Evidence | Suggestion |
|---|---|---|---|
| RDA-F1-01M Metadata is identified by a persistent identifier | not applicable (embedded-metadata) |  |  |
| RDA-F1-01D Data is identified by a persistent identifier | not evidenced |  | State a persistent identifier of this file's own data, in a registered scheme (see guideline G1).<br>#!identifier &lt;persistent identifier of this file, e.g. doi:10.5281/zenodo.6762549&gt; |
| RDA-F1-02M Metadata is identified by a globally unique identifier | not applicable (embedded-metadata) |  |  |
| RDA-F1-02D Data is identified by a globally unique identifier | not evidenced |  | State a persistent identifier of this file's own data, in a registered scheme (see guideline G1).<br>#!identifier &lt;persistent identifier of this file, e.g. doi:10.5281/zenodo.6762549&gt; |
| RDA-F2-01M Rich metadata is provided to allow discovery | not evidenced |  | Give the taxon as a persistent identifiers.org IRI (see guideline G4).<br>##species https://identifiers.org/taxonomy:&lt;NCBI taxon id, e.g. 6239&gt; |
| RDA-F3-01M Metadata includes the identifier for the data | not evidenced |  | State a persistent identifier of this file's own data, in a registered scheme (see guideline G1).<br>#!identifier &lt;persistent identifier of this file, e.g. doi:10.5281/zenodo.6762549&gt; |
| RDA-F4-01M Metadata is offered in such a way that it can be harvested and indexed | not applicable (repository-level) |  |  |

## Accessible

| Indicator | Status | Evidence | Suggestion |
|---|---|---|---|
| RDA-A1-01M Metadata contains information to enable the user to get access to the data | not evidenced |  | Say where this file can be obtained, as a URL (see guideline G8).<br>#!relatedLink &lt;URL where this file can be downloaded, e.g. https://ftp.ensembl.org/pub/release-116/&gt; |
| RDA-A1-02M Metadata can be accessed manually | not applicable (embedded-metadata) |  |  |
| RDA-A1-02D Data can be accessed manually | not applicable (object-in-hand) |  |  |
| RDA-A1-03M Metadata identifier resolves to a metadata record | not applicable (embedded-metadata) |  |  |
| RDA-A1-03D Data identifier resolves to a digital object | not assessed (online-check-not-requested) |  |  |
| RDA-A1-04M Metadata is accessed through standardised protocol | not applicable (embedded-metadata) |  |  |
| RDA-A1-04D Data is accessible through standardised protocol | not assessed (online-check-not-requested) |  |  |
| RDA-A1-05D Data can be accessed automatically | not assessed (online-check-not-requested) |  |  |
| RDA-A1.1-01M Metadata is accessible through a free access protocol | not applicable (embedded-metadata) |  |  |
| RDA-A1.1-01D Data is accessible through a free access protocol | not assessed (online-check-not-requested) |  |  |
| RDA-A1.2-01D Data is accessible through an access protocol that supports authentication and authorisation | not applicable (repository-level) |  |  |
| RDA-A2-01M Metadata is guaranteed to remain available after data is no longer available | not applicable (repository-level) |  |  |

## Interoperable

| Indicator | Status | Evidence | Suggestion |
|---|---|---|---|
| RDA-I1-01M Metadata uses knowledge representation expressed in standardised format | evidenced | line 2: ##gff-version 3 |  |
| RDA-I1-01D Data uses knowledge representation expressed in standardised format | evidenced | line 2: ##gff-version 3 |  |
| RDA-I1-02M Metadata uses machine-understandable knowledge representation | not evidenced |  | Map the header keys to IRIs with a JSON-LD context, so that the metadata is machine-understandable (see guideline G3).<br>#~'@context': &lt;URL of a JSON-LD context for the header keys, e.g. https://example.org/context.jsonld&gt; |
| RDA-I1-02D Data uses machine-understandable knowledge representation | partially evidenced | line 2: ##gff-version 3 | Name the Sequence Ontology release used for feature types (see guideline G4).<br>##feature-ontology &lt;URL of the Sequence Ontology release used, e.g. http://purl.obolibrary.org/obo/so/2024-11-18/so.owl&gt; |
| RDA-I2-01M Metadata uses FAIR-compliant vocabularies | not evidenced |  | Give the taxon as a persistent identifiers.org IRI (see guideline G4).<br>##species https://identifiers.org/taxonomy:&lt;NCBI taxon id, e.g. 6239&gt; |
| RDA-I2-01D Data uses FAIR-compliant vocabularies | partially evidenced | line 2: ##gff-version 3 | Name the Sequence Ontology release used for feature types (see guideline G4).<br>##feature-ontology &lt;URL of the Sequence Ontology release used, e.g. http://purl.obolibrary.org/obo/so/2024-11-18/so.owl&gt; |
| RDA-I3-01M Metadata includes references to other metadata | not evidenced |  | Give the taxon as a persistent identifiers.org IRI (see guideline G4).<br>##species https://identifiers.org/taxonomy:&lt;NCBI taxon id, e.g. 6239&gt; |
| RDA-I3-01D Data includes references to other data | not assessed (deferred-data-body) |  |  |
| RDA-I3-02M Metadata includes references to other data | partially evidenced | line 5: #!assembly WBcel235 | Record the accession of the assembly this annotation describes, so that the genome can be identified exactly (see guideline G5).<br>#!genome-build-accession NCBI\_Assembly:&lt;versioned assembly accession, e.g. GCF\_000002985.6&gt; |
| RDA-I3-02D Data includes qualified references to other data | not assessed (deferred-data-body) |  |  |
| RDA-I3-03M Metadata includes qualified references to other metadata | not evidenced |  | Name the author of the header with an ORCID iD, which states the role and links to a record about the person (see guideline G4).<br>#~metadataAuthor: \[{name: &lt;author name, e.g. Josiah Carberry&gt;, uri: https://orcid.org/&lt;ORCID iD, e.g. 0000-0002-1825-0097&gt;}\] |
| RDA-I3-04M Metadata include qualified references to other data | partially evidenced | line 5: #!assembly WBcel235 | Record the accession of the assembly this annotation describes, so that the genome can be identified exactly (see guideline G5).<br>#!genome-build-accession NCBI\_Assembly:&lt;versioned assembly accession, e.g. GCF\_000002985.6&gt; |

## Reusable

| Indicator | Status | Evidence | Suggestion |
|---|---|---|---|
| RDA-R1-01M Plurality of accurate and relevant attributes are provided to allow reuse | not evidenced |  | State the version or release of this file's data (see guideline G2).<br>#!version &lt;version or release of this file's data, e.g. WS298&gt; |
| RDA-R1.1-01M Metadata includes information about the licence under which the data can be reused | not evidenced |  | State the licence of this file as an SPDX identifier (see guideline G7).<br>#!reuseConditions &lt;SPDX licence id, e.g. CC-BY-4.0&gt; |
| RDA-R1.1-02M Metadata refers to a standard reuse licence | not evidenced |  | State the licence of this file as an SPDX identifier (see guideline G7).<br>#!reuseConditions &lt;SPDX licence id, e.g. CC-BY-4.0&gt; |
| RDA-R1.1-03M Metadata refers to a machine-understandable reuse licence | not evidenced |  | State the licence of this file as an SPDX identifier (see guideline G7).<br>#!reuseConditions &lt;SPDX licence id, e.g. CC-BY-4.0&gt; |
| RDA-R1.2-01M Metadata includes provenance information according to community-specific standards | partially evidenced | line 3: #!date-produced 2025-11-13T16:37:34+00:00<br>line 4: #!data-source WormBase | Record the accession of the assembly this annotation describes, so that the genome can be identified exactly (see guideline G5).<br>#!genome-build-accession NCBI\_Assembly:&lt;versioned assembly accession, e.g. GCF\_000002985.6&gt; |
| RDA-R1.2-02M Metadata includes provenance information according to a cross-community language | not evidenced |  | Record the parent file with a derivedFrom entry and its relationship; the relationship vocabulary is still provisional (FHR-Specification#54) (see guideline G5).<br>#~derivedFrom: \[{headerType: &lt;header type of the parent file, e.g. FHR&gt;, relationship: &lt;relationship to the parent, e.g. annotates&gt;, checksum: &lt;FHR checksum of the parent file, e.g. 3an6Cqo2eomqlt75XIpyWXDtls3GhA8EOpjK97S+ykc=&gt;}\] |
| RDA-R1.3-01M Metadata complies with a community standard | partially evidenced | line 2: ##gff-version 3 | Declare the format and its version on the first line (see guideline G3).<br>##gff-version &lt;GFF version, e.g. 3&gt; |
| RDA-R1.3-01D Data complies with a community standard | partially evidenced | line 2: ##gff-version 3 | Declare the format and its version on the first line (see guideline G3).<br>##gff-version &lt;GFF version, e.g. 3&gt; |
| RDA-R1.3-02M Metadata is expressed in compliance with a machine-understandable community standard | partially evidenced | line 2: ##gff-version 3 | Add a FAIR-bioHeaders header that names its machine-readable schema; for a genome, create it with bioheaders combine so that it validates (see guideline G3).<br>#~schema: &lt;schema URL of the FAIR-bioHeaders header type, e.g. https://raw.githubusercontent.com/FAIR-bioHeaders/FHR-Specification/main/fhr.json&gt; |
| RDA-R1.3-02D Data is expressed in compliance with a machine-understandable community standard | evidenced | line 2: ##gff-version 3 |  |

## Recorded links

- name  WBcel235  (line 5, annotates)  not verified: no related file given

## Findings

- format-irregularity: line 1 comes before the format declaration on line 2, which the format specification requires first
- unrecognised-comment: line 1: a comment line in no recognised header convention

Indicator identifiers and titles from: FAIR Data Maturity Model Working Group (2020). FAIR Data Maturity Model. Specification and Guidelines. Research Data Alliance. doi:10.15497/rda00050. Licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). File-header interpretations are adaptations by FAIR-bioHeaders and are not endorsed by the RDA.
