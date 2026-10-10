# FAIR header assessment: headers/alliance\_vcf\_VCF-GZ\_WBcel235\_38.vcf (vcf, none)

- Input: assessed; format from content; header lines read: 35; records sampled: 0
- Header SHA-256: 6860ffeee8e3ffdbc3fc9f2336651380d2c674911353990cdd24f250d3075483
- Online checks: not requested
- Rubric 1.1.0, synonyms 1.0.0, formats 2026-10-10, id-schemes identifiers.org-2026-10-10, spdx-licenses 3.29.0; bioheaders assess 0.4.0

## Findable

| Indicator | Status | Evidence | Suggestion |
|---|---|---|---|
| RDA-F1-01M Metadata is identified by a persistent identifier | not applicable (embedded-metadata) |  |  |
| RDA-F1-01D Data is identified by a persistent identifier | not evidenced |  | State a persistent identifier of this file's own data, in a registered scheme (see guideline G1).<br>##identifier=&lt;persistent identifier of this file, e.g. doi:10.5281/zenodo.6762549&gt; |
| RDA-F1-02M Metadata is identified by a globally unique identifier | not applicable (embedded-metadata) |  |  |
| RDA-F1-02D Data is identified by a globally unique identifier | not evidenced |  | State a persistent identifier of this file's own data, in a registered scheme (see guideline G1).<br>##identifier=&lt;persistent identifier of this file, e.g. doi:10.5281/zenodo.6762549&gt; |
| RDA-F2-01M Rich metadata is provided to allow discovery | partially evidenced | line 2: ##fileDate=20201017<br>line 28: ##source=AGR VCF File generator<br>line 29: ##contig=&lt;ID=IV,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 30: ##contig=&lt;ID=II,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 31: ##contig=&lt;ID=III,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 32: ##contig=&lt;ID=I,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 33: ##contig=&lt;ID=V,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 34: ##contig=&lt;ID=X,assembly=WBcel235,species="Caenorhabditis elegans"&gt; | State the version or release of this file's data (see guideline G2).<br>##version=&lt;version or release of this file's data, e.g. WS298&gt; |
| RDA-F3-01M Metadata includes the identifier for the data | not evidenced |  | State a persistent identifier of this file's own data, in a registered scheme (see guideline G1).<br>##identifier=&lt;persistent identifier of this file, e.g. doi:10.5281/zenodo.6762549&gt; |
| RDA-F4-01M Metadata is offered in such a way that it can be harvested and indexed | not applicable (repository-level) |  |  |

## Accessible

| Indicator | Status | Evidence | Suggestion |
|---|---|---|---|
| RDA-A1-01M Metadata contains information to enable the user to get access to the data | not evidenced |  | Say where this file can be obtained, as a URL (see guideline G8).<br>##relatedLink=&lt;URL where this file can be downloaded, e.g. https://ftp.ensembl.org/pub/release-116/&gt; |
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
| RDA-I1-01M Metadata uses knowledge representation expressed in standardised format | evidenced | line 1: ##fileformat=VCFv4.3 |  |
| RDA-I1-01D Data uses knowledge representation expressed in standardised format | evidenced | line 1: ##fileformat=VCFv4.3 |  |
| RDA-I1-02M Metadata uses machine-understandable knowledge representation | not evidenced |  | Map the header keys to IRIs with a JSON-LD context, so that the metadata is machine-understandable (see guideline G3).<br>##'@context'=&lt;URL of a JSON-LD context for the header keys, e.g. https://example.org/context.jsonld&gt; |
| RDA-I1-02D Data uses machine-understandable knowledge representation | evidenced | line 1: ##fileformat=VCFv4.3<br>line 13: ##INFO=&lt;ID=hgvs\_nomenclature,Number=1,Type=String,Description="the HGVS name of the allele"&gt;<br>line 14: ##INFO=&lt;ID=geneLevelConsequence,Number=.,Type=String,Description="VEP consequence of the variant on the Gene"&gt;<br>line 15: ##INFO=&lt;ID=transcriptLevelConsequence,Number=.,Type=String,Description="VEP consequence of the variant on the Transcript"&gt;<br>line 16: ##INFO=&lt;ID=geneImpact,Number=.,Type=String,Description="Variant impact scale for Gene"&gt;<br>line 17: ##INFO=&lt;ID=transcriptImpact,Number=.,Type=String,Description="Variant impact scale for Transcript"&gt;<br>line 18: ##INFO=&lt;ID=allele\_ids,Number=.,Type=String,Description="The ID of the Allele"&gt;<br>line 19: ##INFO=&lt;ID=allele\_symbols,Number=.,Type=String,Description="The human readable name of the Allele"&gt;<br>line 20: ##INFO=&lt;ID=allele\_symbols\_text,Number=.,Type=String,Description="Another human readable representation of the allele"&gt;<br>line 21: ##INFO=&lt;ID=soTerm,Number=1,Type=String,Description="The Sequence Ontology term for the variant"&gt;<br>line 22: ##INFO=&lt;ID=allele\_of\_gene\_ids,Number=.,Type=String,Description="The gene ids that the Allele is located on"&gt;<br>line 23: ##INFO=&lt;ID=allele\_of\_gene\_symbols,Number=.,Type=String,Description="The gene names that the Allele is located on"&gt;<br>line 24: ##INFO=&lt;ID=allele\_of\_transcript\_ids,Number=.,Type=String,Description="The gene ids that the Allele is located on"&gt;<br>line 25: ##INFO=&lt;ID=allele\_of\_transcript\_gff3\_ids,Number=.,Type=String,Description="The transcript gff3ID that the Allele is located on"&gt;<br>line 26: ##INFO=&lt;ID=allele\_of\_transcript\_gff3\_names,Number=.,Type=String,Description="The transcript gff3 Names that the Allele is located on"&gt; |  |
| RDA-I2-01M Metadata uses FAIR-compliant vocabularies | partially evidenced | line 29: ##contig=&lt;ID=IV,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 30: ##contig=&lt;ID=II,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 31: ##contig=&lt;ID=III,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 32: ##contig=&lt;ID=I,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 33: ##contig=&lt;ID=V,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 34: ##contig=&lt;ID=X,assembly=WBcel235,species="Caenorhabditis elegans"&gt; | Give the taxon as a persistent identifiers.org IRI (see guideline G4).<br>##taxon=https://identifiers.org/taxonomy:&lt;NCBI taxon id, e.g. 6239&gt; |
| RDA-I2-01D Data uses FAIR-compliant vocabularies | not evidenced |  | Point to documentation that defines the fields and vocabularies of the records (see guideline G4).<br>##documentation=&lt;URL of the documentation of the record fields, e.g. https://example.org/fields.html&gt; |
| RDA-I3-01M Metadata includes references to other metadata | not evidenced |  | Give the taxon as a persistent identifiers.org IRI (see guideline G4).<br>##taxon=https://identifiers.org/taxonomy:&lt;NCBI taxon id, e.g. 6239&gt; |
| RDA-I3-01D Data includes references to other data | not assessed (deferred-data-body) |  |  |
| RDA-I3-02M Metadata includes references to other data | partially evidenced | line 29: ##contig=&lt;ID=IV,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 30: ##contig=&lt;ID=II,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 31: ##contig=&lt;ID=III,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 32: ##contig=&lt;ID=I,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 33: ##contig=&lt;ID=V,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 34: ##contig=&lt;ID=X,assembly=WBcel235,species="Caenorhabditis elegans"&gt; | Give each contig the MD5 of its reference sequence, one line per contig, so that the genome can be checked exactly (see guideline G5).<br>##contig=&lt;ID=&lt;sequence name, e.g. I&gt;,length=&lt;sequence length, e.g. 15072434&gt;,md5=&lt;MD5 of the sequence, e.g. 6aef897c3d6ff0c78aff06ac189178dd&gt;&gt; |
| RDA-I3-02D Data includes qualified references to other data | not assessed (deferred-data-body) |  |  |
| RDA-I3-03M Metadata includes qualified references to other metadata | not evidenced |  | Name the author of the header with an ORCID iD, which states the role and links to a record about the person (see guideline G4).<br>##metadataAuthor=\[{name: &lt;author name, e.g. Josiah Carberry&gt;, uri: https://orcid.org/&lt;ORCID iD, e.g. 0000-0002-1825-0097&gt;}\] |
| RDA-I3-04M Metadata include qualified references to other data | partially evidenced | line 29: ##contig=&lt;ID=IV,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 30: ##contig=&lt;ID=II,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 31: ##contig=&lt;ID=III,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 32: ##contig=&lt;ID=I,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 33: ##contig=&lt;ID=V,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 34: ##contig=&lt;ID=X,assembly=WBcel235,species="Caenorhabditis elegans"&gt; | Give each contig the MD5 of its reference sequence, one line per contig, so that the genome can be checked exactly (see guideline G5).<br>##contig=&lt;ID=&lt;sequence name, e.g. I&gt;,length=&lt;sequence length, e.g. 15072434&gt;,md5=&lt;MD5 of the sequence, e.g. 6aef897c3d6ff0c78aff06ac189178dd&gt;&gt; |

## Reusable

| Indicator | Status | Evidence | Suggestion |
|---|---|---|---|
| RDA-R1-01M Plurality of accurate and relevant attributes are provided to allow reuse | partially evidenced | line 2: ##fileDate=20201017<br>line 28: ##source=AGR VCF File generator<br>line 29: ##contig=&lt;ID=IV,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 30: ##contig=&lt;ID=II,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 31: ##contig=&lt;ID=III,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 32: ##contig=&lt;ID=I,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 33: ##contig=&lt;ID=V,assembly=WBcel235,species="Caenorhabditis elegans"&gt;<br>line 34: ##contig=&lt;ID=X,assembly=WBcel235,species="Caenorhabditis elegans"&gt; | State the version or release of this file's data (see guideline G2).<br>##version=&lt;version or release of this file's data, e.g. WS298&gt; |
| RDA-R1.1-01M Metadata includes information about the licence under which the data can be reused | not evidenced |  | State the licence of this file as an SPDX identifier (see guideline G7).<br>##reuseConditions=&lt;SPDX licence id, e.g. CC-BY-4.0&gt; |
| RDA-R1.1-02M Metadata refers to a standard reuse licence | not evidenced |  | State the licence of this file as an SPDX identifier (see guideline G7).<br>##reuseConditions=&lt;SPDX licence id, e.g. CC-BY-4.0&gt; |
| RDA-R1.1-03M Metadata refers to a machine-understandable reuse licence | not evidenced |  | State the licence of this file as an SPDX identifier (see guideline G7).<br>##reuseConditions=&lt;SPDX licence id, e.g. CC-BY-4.0&gt; |
| RDA-R1.2-01M Metadata includes provenance information according to community-specific standards | partially evidenced | line 2: ##fileDate=20201017<br>line 28: ##source=AGR VCF File generator | Give each contig the MD5 of its reference sequence, one line per contig, so that the genome can be checked exactly (see guideline G5).<br>##contig=&lt;ID=&lt;sequence name, e.g. I&gt;,length=&lt;sequence length, e.g. 15072434&gt;,md5=&lt;MD5 of the sequence, e.g. 6aef897c3d6ff0c78aff06ac189178dd&gt;&gt; |
| RDA-R1.2-02M Metadata includes provenance information according to a cross-community language | not evidenced |  | Record the parent file with a derivedFrom entry and its relationship; the relationship vocabulary is still provisional (FHR-Specification#54) (see guideline G5).<br>##derivedFrom=\[{headerType: &lt;header type of the parent file, e.g. FHR&gt;, relationship: &lt;relationship to the parent, e.g. annotates&gt;, checksum: &lt;FHR checksum of the parent file, e.g. 3an6Cqo2eomqlt75XIpyWXDtls3GhA8EOpjK97S+ykc=&gt;}\] |
| RDA-R1.3-01M Metadata complies with a community standard | evidenced | line 1: ##fileformat=VCFv4.3 |  |
| RDA-R1.3-01D Data complies with a community standard | partially evidenced | line 1: ##fileformat=VCFv4.3 | Declare the format and its version on the first line (see guideline G3).<br>##fileformat=VCFv&lt;VCF version, e.g. 4.3&gt; |
| RDA-R1.3-02M Metadata is expressed in compliance with a machine-understandable community standard | partially evidenced | line 1: ##fileformat=VCFv4.3 | Add a FAIR-bioHeaders header that names its machine-readable schema; for a genome, create it with bioheaders combine so that it validates (see guideline G3).<br>##schema=&lt;schema URL of the FAIR-bioHeaders header type, e.g. https://raw.githubusercontent.com/FAIR-bioHeaders/FHR-Specification/main/fhr.json&gt; |
| RDA-R1.3-02D Data is expressed in compliance with a machine-understandable community standard | evidenced | line 1: ##fileformat=VCFv4.3 |  |

## Recorded links

- name  WBcel235  (line 29, 30, 31, 32, 33, 34, annotates)  not verified: no related file given

## Findings

- none

Indicator identifiers and titles from: FAIR Data Maturity Model Working Group (2020). FAIR Data Maturity Model. Specification and Guidelines. Research Data Alliance. doi:10.15497/rda00050. Licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). File-header interpretations are adaptations by FAIR-bioHeaders and are not endorsed by the RDA.
