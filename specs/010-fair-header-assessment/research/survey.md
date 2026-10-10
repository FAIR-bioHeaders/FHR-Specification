# Research: survey of headers in real public download files

**Feature**: 010-fair-header-assessment | **Phase**: 0 (research) | **Fetched**: 2026-10-10 (UTC)

**Method**: every file was streamed over HTTPS and decompression stopped as soon as the header ended
(`curl -sL URL | gzip -dc | head | awk ...`). No file was downloaded whole. Only header lines
were kept. For FASTA that is any lines before the first `>` plus the first `>` defline. For GFF3,
`#`-lines before the first feature. For GAF, `!` lines. For VCF, `##` lines and `#CHROM`.
The evidence is in `research/headers/<provider>_<type>_<file>.txt`. Each evidence file starts with
`# SOURCE-URL` and `# FETCHED` lines added by the survey; they are not part of the original file.
Long runs of `##sequence-region` lines (FlyBase has 1,870) were shortened to five, and an
`[ELIDED ...]` note gives the count. The capture helper is `/tmp/fhrreview/scripts/hdr.sh`.

**Scope**: 34 files, 9 provider groups, all 4 types.

| Provider | FASTA genome | FASTA transcript | FASTA protein | GFF3 | GAF | VCF | Total |
|---|---|---|---|---|---|---|---|
| Alliance of Genome Resources | 2 | | | 3 | 1 | 1 | 7 |
| WormBase (WS298) | 1 | 1 | 1 | 1 | | 1 | 5 |
| FlyBase (FB2026_03, r6.69) | 1 | 1 | 1 | 1 | | | 4 |
| Ensembl (release 116) | 1 | 1 | 1 | 1 | | 1 | 5 |
| Ensembl Plants (release 63) | | | | 1 | | | 1 |
| NCBI RefSeq assembly | 1 | 1 | 1 | 2 | | | 5 |
| NCBI GenBank assembly | 1 | | | 1 | | | 2 |
| NCBI ClinVar / dbSNP | | | | | | 2 | 2 |
| GO Consortium (current) | | | | | 3 | | 3 |
| **Total** | 7 | 4 | 4 | 10 | 4 | 5 | **34** |

Release notes taken while fetching:
- Ensembl `current` was release 116 and Ensembl Plants `current` was release 63.
- WormBase `downloads.wormbase.org` returned a Cloudflare challenge (HTTP 403) to non-browser
  clients. The EBI mirror `ftp.ebi.ac.uk/pub/databases/wormbase/releases/WS298/` was used instead.
  WS298 was the newest release on the mirror.
- FlyBase `current` was FB2026_03 / r6.69. The same files are under the versioned path
  `https://s3ftp.flybase.org/genomes/dmel/dmel_r6.69_FB2026_03/` (HTTP 200).
- The Alliance FMS API (`https://fms.alliancegenome.org/api/datafile/by/<TYPE>?latest=true`)
  reported current release 9.1.0 (2026-09-02). Release 9.2.0 (2026-10-14) was already listed for
  some files. The Alliance's own FASTA and VCF files are old (3.1.1/2020 for WB FASTA, 3.2.0/2020
  for VCF).
- GO `current` reported release-date 2026-08-05. Its GAFs say `!date-generated: 2026-05-21`.
- ClinVar `fileDate=2026-10-04`. dbSNP `latest_release` is build 157, `fileDate=20241205`.

## 1. Per-file catalogue

The table abbreviates URLs to the path after the host. Full URLs are in each evidence file and in
section 5.

| # | Provider | Type | URL (abbrev.) | Convention(s) | Metadata keys present (normalised) |
|---|---|---|---|---|---|
| 1 | Alliance | GFF3 | download.alliancegenome.org/9.2.0/GFF/HUMAN/GFF_HUMAN_0.gff.gz | `##` + `#!` | gff-version=3; annotationSource=`ENSEMBL 111.38 (GRCh38.p14)` and `RefSeq RS_2023_10 (GRCh38.p14)`; `assembly:`=GRCh38 (with colon); data-source=`RAT GENOME DATABASE (https://rgd.mcw.edu/)`; date-produced=2026-09-26T20:54:41+00:00; primary-contact=email; species=`Human`; tool=`AGR GFF3 extractor v 2025-01-28`; 25 sequence-region |
| 2 | Alliance | GFF3 | …/9.1.0/GFF/MGI/GFF_MGI_1.gff.gz | `##` + `#!` | gff-version; data-source=MGI; date-produced=`Mon Sep 21 09:32:10 2026` (free text); assembly=GRCm39 (no colon); annotationSource=`RefSeq GCF_000001635.27-RS_2024_02` and `ENSEMBL 114`; no sequence-region |
| 3 | Alliance | GFF3 | …/8.3.0/GFF/WB/GFF_WB_4.gff.gz | plain `#` **before** `##gff-version`, then `#!` | `# WormBase release WS298` (line 1, so `##gff-version` is not the first line, which breaks GFF3); date-produced (ISO); data-source=WormBase; assembly=WBcel235; 7 sequence-region |
| 4 | Alliance | FASTA genome | …/9.1.0/FASTA/GRCz12tu/FASTA_GRCz12tu_0.fa.gz | defline only | `>NC_133176.1 Danio rerio strain Tuebingen ... chromosome 1, GRCz12tu, whole genome shotgun sequence` (RefSeq seq accession, assembly name in free text) |
| 5 | Alliance | FASTA genome | …/3.1.1/FASTA/WB/FASTA_WB_0.fa | defline only | `>I` (nothing else) |
| 6 | Alliance | GAF | …/9.1.0/GAF/WB/GAF_WB_1.gaf.gz | `!key: value` | gaf-version=2.2; generated-by=UniProt; date-generated=`2026-08-04 15:14`; go-version=PURL of go-plus 2026-08-02 |
| 7 | Alliance | VCF | …/3.2.0/VCF-GZ/WBcel235/VCF-GZ_WBcel235_38.vcf.gz | VCF `##` | fileformat=VCFv4.3; fileDate=20201017; source=`AGR VCF File generator`; phasing; `##contig=<ID=..,assembly=WBcel235,species="Caenorhabditis elegans">` (**no length, no md5**); 14 INFO, 10 ALT |
| 8 | WormBase | GFF3 | ftp.ebi.ac.uk/…/WS298/…/c_elegans.PRJNA13758.WS298.annotations.gff3.gz | `##` only | gff-version; 7 sequence-region. **Nothing else**: release, assembly and species appear only in the file name |
| 9 | WormBase | FASTA genome | …WS298.genomic.fa.gz | defline only | `>I` |
| 10 | WormBase | FASTA transcript | …WS298.mRNA_transcripts.fa.gz | defline `key=value` | `>2L52.1a.1 gene=WBGene00007063` |
| 11 | WormBase | FASTA protein | …WS298.protein.fa.gz | defline `key=value` | wormpep=, gene=, status=, uniprot=, insdc=, product= (record-level only) |
| 12 | WormBase | VCF | …WS298.variations.vcf.gz | VCF `##` | fileformat=VCFv4.3; `##contig=<ID,length,species>` (**no assembly, no md5**); INFO/ALT. **No fileDate, source or reference** |
| 13 | FlyBase | GFF3 | s3ftp.flybase.org/genomes/Drosophila_melanogaster/current/gff/dmel-all-r6.69.gff.gz | `##` | gff-version; species=NCBI Taxonomy URL (taxid 7227); feature-ontology=URL of so.obo in FB2026_03; `##genome-build FlyBase r6.69` (name, no accession); 1,870 sequence-region. **The file is a gzipped tar archive, not a gzipped GFF.** |
| 14 | FlyBase | FASTA genome | …/fasta/dmel-all-chromosome-r6.69.fasta.gz | defline `key=value;` | type, loc, ID, dbxref=`GB:AE014134,REFSEQ:NT_033779`, **MD5=** (of this sequence), length, release=r6.69, species=Dmel |
| 15 | FlyBase | FASTA transcript | …/dmel-all-transcript-r6.69.fasta.gz | defline `key=value;` | type, loc, ID, name, dbxref, MD5=, length, parent, release=r6.69, species=Dmel |
| 16 | FlyBase | FASTA protein | …/dmel-all-translation-r6.69.fasta.gz | defline `key=value;` | as above, plus parent=gene and transcript |
| 17 | Ensembl | GFF3 | ftp.ensembl.org/pub/current_gff3/homo_sapiens/Homo_sapiens.GRCh38.116.chr.gff3.gz | `##` + `#!` | gff-version; sequence-region; `#!genome-build Genome Reference Consortium GRCh38.p14`; genome-version=GRCh38; genome-date=2013-12; **genome-build-accession=GCA_000001405.29** (bare); genebuild-last-updated=2025-11 |
| 18 | Ensembl Plants | GFF3 | ftp.ensemblgenomes.ebi.ac.uk/pub/plants/current/gff3/arabidopsis_thaliana/Arabidopsis_thaliana.TAIR10.63.chromosome.1.gff3.gz | `##` + `#!` | same keys as #17: genome-build=`The Arabidopsis Information Resource TAIR10`, genome-build-accession=GCA_000001735.1 |
| 19 | Ensembl | FASTA genome | …/current_fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.chromosome.MT.fa.gz | defline | `>MT dna:chromosome chromosome:GRCh38:MT:1:16569:1 REF` (assembly **name** in each record) |
| 20 | Ensembl | FASTA transcript | …/cdna/Homo_sapiens.GRCh38.cdna.all.fa.gz | defline | `cdna scaffold:GRCh38:HG2290_PATCH:...` plus gene:, gene_biotype, transcript_biotype, gene_symbol, description (record-level assembly name) |
| 21 | Ensembl | FASTA protein | …/pep/Homo_sapiens.GRCh38.pep.all.fa.gz | defline | `pep scaffold:GRCh38:...` plus gene:, transcript:, ... |
| 22 | Ensembl | VCF | …/current_variation/vcf/homo_sapiens/homo_sapiens-chrMT.vcf.gz | VCF `##` | fileformat=VCFv4.1; fileDate=20260404; `source=ensembl;version=116;url=https://e116.ensembl.org/homo_sapiens`; **`reference=https://ftp.ensembl.org/pub/release-116/fasta/homo_sapiens/dna/`** (a directory URL, not a file); INFO lines name source versions (ClinVar_202509, dbSNP_156, COSMIC_102); **no ##contig** |
| 23 | NCBI RefSeq | GFF3 | ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/002/985/GCF_000002985.6_WBcel235/…_genomic.gff.gz | `##` + `#!` | gff-version; gff-spec-version=1.21; processor=`NCBI annotwriter`; genome-build=WBcel235; **genome-build-accession=`NCBI_Assembly:GCF_000002985.6`**; annotation-source=`WormBase WS298`; sequence-region; species=NCBI Taxonomy URL |
| 24 | NCBI RefSeq | GFF3 | …/GCF_000001405.40_GRCh38.p14/…_genomic.gff.gz | `##` + `#!` | as #23, plus annotation-date=`08/01/2025` (US format); annotation-source=`NCBI RefSeq GCF_000001405.40-RS_2025_08` |
| 25 | NCBI RefSeq | FASTA genome | …GCF_000002985.6_WBcel235_genomic.fna.gz | defline | `>NC_003279.8 Caenorhabditis elegans chromosome I` |
| 26 | NCBI RefSeq | FASTA transcript | …_rna.fna.gz | defline | `>NM_001025786.5 Caenorhabditis elegans ALG-1 (ain-2), mRNA` |
| 27 | NCBI RefSeq | FASTA protein | …_protein.faa.gz | defline | `>NP_001020957.2 ALG-1 [Caenorhabditis elegans]` |
| 28 | NCBI GenBank | GFF3 | …/GCA_000002985.3_WBcel235/…_genomic.gff.gz | `##` + `#!` | as #23 with `NCBI_Assembly:GCA_000002985.3`; no annotation-source |
| 29 | NCBI GenBank | FASTA genome | …GCA_000002985.3_WBcel235_genomic.fna.gz | defline | `>BX284601.5 Caenorhabditis elegans chromosome I` |
| 30 | NCBI ClinVar | VCF | ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz | VCF `##` | fileformat=VCFv4.1; fileDate=2026-10-04 (non-standard form; VCF says YYYYMMDD); source=ClinVar; **reference=GRCh38** (name only); `##ID=<Description=...>`; no contig |
| 31 | NCBI dbSNP | VCF | ftp.ncbi.nlm.nih.gov/snp/latest_release/VCF/GCF_000001405.40.gz | VCF `##` | fileformat=VCFv4.2; fileDate=20241205; source=dbSNP; dbSNP_BUILD_ID=157; **reference=GRCh38.p14** (name; the accession appears only in the file name); phasing; no contig |
| 32 | GO | GAF | current.geneontology.org/annotations/goa_human.gaf.gz | `!key: value`, nested | gaf-version=2.2; generated-by (GOC, UniProt, PANTHER); date-generated (three formats); go-version=PURL; `PANTHER version: v.19.0.`; `GO version: 2025-10-05.`; `Created on Mon Jan 5 ...`; documentation URL |
| 33 | GO | GAF | …/fb.gaf.gz | as #32 | as #32 |
| 34 | GO | GAF | …/wb.gaf.gz | as #32 | as #32 |

No FASTA file from any provider has a file-level header: there are no `;` or `#` lines before the
first `>`. All FASTA metadata is per record, in the defline.

## 2. Per-concept analysis

| Concept | Files that carry it, and how | Notes |
|---|---|---|
| **Identifier of the data itself** | None in-file. The nearest thing is the file name (`GCF_000002985.6_WBcel235_*`, `*.WS298.*`). dbSNP's file name is an assembly accession. | No file states its own persistent identifier or DOI. |
| **Version / release** | GFF3: Alliance WB (`# WormBase release WS298`, free comment), FlyBase `##genome-build FlyBase r6.69` (genome release), NCBI `#!annotation-source NCBI RefSeq …-RS_2025_08` / `WormBase WS298`, Ensembl `#!genebuild-last-updated`, Alliance `#!annotationSource ENSEMBL 114`. VCF: Ensembl `##source=ensembl;version=116`, dbSNP `##dbSNP_BUILD_ID=157`. FASTA: FlyBase `release=r6.69` per record. GAF: none for the data (only ontology version). | Release mostly appears in path or file name (Ensembl, WormBase, Alliance). |
| **Date** | GFF3: Alliance `#!date-produced` (ISO in two files, ctime-style free text in MGI), NCBI `#!annotation-date 08/01/2025`, Ensembl `#!genome-date 2013-12` (date of the assembly, not the file). VCF: `##fileDate` (ClinVar `2026-10-04`, others `YYYYMMDD`; missing in WormBase). GAF: `!date-generated` (formats `2026-05-21T07:43`, `2026-04-30 09:24`, `2026-01-05`) and `!Created on Mon Jan 5 19:04:15 2026.` | Date formats vary even within one GAF, so the parser must accept several. |
| **Creator / provider** | GFF3: Alliance `#!data-source`, `#!primary-contact`; NCBI `#!processor`. VCF: `##source=`. GAF: `!generated-by:`. FASTA: none. | Alliance HUMAN GFF says `data-source RAT GENOME DATABASE`: this records who generated the file, not where the data came from. |
| **Source URL / landing page** | Ensembl VCF `##source=…;url=https://e116.ensembl.org/homo_sapiens`, Alliance HUMAN `#!data-source … (https://rgd.mcw.edu/)`, GAF documentation URL. | Rare. |
| **Licence** | **None of the 34 files.** | This is a universal gap (R1.1). |
| **Taxon** | GFF3: `##species` with an NCBI Taxonomy URL (NCBI, FlyBase); `#!species Human` (Alliance, free text). VCF: `species="…"` inside `##contig` (WormBase, Alliance). FASTA: free text in the defline (NCBI `[Caenorhabditis elegans]`, FlyBase `species=Dmel`). GAF: none in the header (taxon is only in column 13). Ensembl: none in-file (only the file name). | Only `##species <taxonomy URL>` is machine-actionable. |
| **Assembly / genome identity** | See the next table. | |
| **Checksum** | FlyBase deflines `MD5=` per sequence (genome, transcript and protein). **No file records a checksum of another file, and no VCF `##contig` carries `md5=`.** | |
| **Software / provenance** | NCBI `#!processor NCBI annotwriter`; Alliance `#!tool AGR GFF3 extractor v 2025-01-28`; Alliance `##source=AGR VCF File generator`; Ensembl VCF INFO IDs naming input versions (`dbSNP_156`, `ClinVar_202509`); GAF nested "Header from source association file" blocks (GOC, UniProt, PANTHER v.19.0); WormBase VCF CSQ `from EnsEMBL VEP`. | GAF provenance is the richest, but it is unstructured nesting. |
| **Format version** | `##gff-version 3` (all GFF3), `#!gff-spec-version 1.21` (NCBI), `##fileformat=VCFv4.x` (all VCF), `!gaf-version: 2.2` (all GAF). FASTA: none. | Present everywhere the format defines it. |
| **Ontology versions** | GAF `!go-version: <PURL of dated go-plus>` and `!GO version: 2025-10-05.`; FlyBase `##feature-ontology <URL to so.obo of FB2026_03>`. GFF3 from other providers: SO version not stated. | |
| **Links to related files** | Ensembl VCF `##reference=<URL of FASTA directory>`; FlyBase `##feature-ontology` URL. Otherwise none. Protein and transcript FASTA never name their GFF or genome file. | |

### Genome link in derived files (the key question)

| File | States its genome? | How | Machine-checkable? |
|---|---|---|---|
| NCBI RefSeq / GenBank GFF3 (#23, #24, #28) | Yes | `#!genome-build-accession NCBI_Assembly:GCF_…` (versioned accession, with prefix) plus `#!genome-build <name>`; seqids are versioned sequence accessions (NC_…/BX…) | **Yes, accession** (resolvable). It matches the paired FASTA's directory name. |
| Ensembl / Ensembl Plants GFF3 (#17, #18) | Yes | `#!genome-build-accession GCA_…` (bare, **GenBank** accession, while seqids use Ensembl names `1`, `MT`) plus `#!genome-build`, `#!genome-version` | Accession yes. It does not identify which Ensembl FASTA flavour (toplevel / primary_assembly / chr, sm/rm), and the names differ from the GCA sequence names. |
| FlyBase GFF3 (#13) | Partly | `##genome-build FlyBase r6.69` (name and release, no accession) | Name only, matched against `release=r6.69` in the FASTA deflines. |
| Alliance GFF3 (#1–#3) | Partly | `#!assembly GRCm39` / `#!assembly: GRCh38` / `#!assembly WBcel235` (name, inconsistent syntax); annotationSource sometimes has a RefSeq accession (`GCF_000001635.27-RS_2024_02`) | Name only; HUMAN says `GRCh38` but not the patch, while annotationSource says p14. |
| WormBase GFF3 (#8) | **No** | Only `##sequence-region` | Circumstantial only (names and lengths). |
| All protein and transcript FASTA (#10, #11, #15, #16, #20, #21, #26, #27) | No file-level link | Ensembl puts the assembly **name** per record (`scaffold:GRCh38:…`); FlyBase `release=r6.69` per record; NCBI and WormBase nothing (only the directory or file name) | No recorded file-level link anywhere. |
| GAF (#6, #32–#34) | No | GAF links to gene or protein IDs, not to a genome. Only ontology version is recorded. | N/A for genome; the relevant link would be to the gene set or proteome release. |
| VCF (#7, #12, #22, #30, #31) | Varies | Alliance `##contig=<…,assembly=WBcel235>`; Ensembl `##reference=<URL>`; ClinVar `##reference=GRCh38`; dbSNP `##reference=GRCh38.p14`; WormBase `##contig` with length but no assembly | No `##contig md5=` and no accession in any VCF. The Ensembl URL is the strongest link, but it points to a directory. |

## 3. Gaps and patterns

1. **There is no file-level header in FASTA from any provider.** Metadata, when present, is per record in deflines, using conventions specific to each provider: Ensembl `type coord_system:assembly:seq:start:end:strand`, FlyBase `key=value;`, WormBase `key=value`, NCBI free text with `[organism]`. The assessment must read the **first defline** as weak evidence, and report it separately from a file header.
2. **Genome identity is recorded in only two GFF3 dialects**, by accession: NCBI (`NCBI_Assembly:` prefix, RefSeq or GenBank) and Ensembl (bare GCA). Everyone else gives a name (FlyBase, Alliance) or nothing (WormBase). **No derived file anywhere records a checksum or digest of its genome.** In practice, FR-006 "recorded identity" will almost always mean "accession or name". Matching a name or accession to a FASTA file requires the FASTA to state its own identity, and in today's files it never does, except through file or directory names. The assessment should report this as "recorded but unverifiable offline" rather than "match".
3. **The same concept has many spellings**: `#!genome-build`, `##genome-build` (FlyBase uses `##`), `#!assembly`, `#!assembly:`; `#!annotation-source` and `#!annotationSource`; `#!date-produced`, `#!annotation-date`, `##fileDate`, `!date-generated`. Key matching should ignore case, `-`/`_`/camelCase differences and a trailing `:`.
4. **Licence is absent from all 34 files.** Persistent identifiers of the file itself are also absent. Providers do have these at the landing-page level, so the suggestions should point there.
5. **Taxon** is machine-actionable only in `##species <NCBI Taxonomy URL>` (NCBI, FlyBase). Elsewhere it is free text, or only in the file name.
6. **GAF headers are nested.** GO pipelines copy upstream headers into later files, so one file can contain several `!generated-by` and `!date-generated` lines. The assessment must use the **first** block (before the first `!Header from …`/`!====` separator) as the file's own metadata, and treat the rest as provenance.
7. **Format irregularities to tolerate rather than crash on**:
   - FlyBase `.gff.gz` is a tar.gz.
   - Alliance WB GFF3 has a comment before `##gff-version`.
   - dbSNP VCF has no `.vcf` extension.
   - ClinVar `fileDate` uses a hyphenated date.
   - GAF dates come in three formats.
   - Ensembl `##reference` is a directory URL.
   - Alliance `#!assembly:` has a stray colon.
   - Very long `##sequence-region` runs: FlyBase has 1,870 lines, so header reading must not be capped at a small line count.
8. **VCF `##contig` is the natural place for a recorded genome link** (`assembly=`, `md5=`, `length=`), but no surveyed VCF uses `md5=`. Only Alliance uses `assembly=`, and only WormBase uses `length=`. The assessment can derive circumstantial evidence (names and lengths) from `##contig` and GFF3 `##sequence-region` in the same way.

## 4. Conventions the first release must recognise

| Convention | Lines | Keys observed (normalise) |
|---|---|---|
| GFF3 directives | `##key value` | `gff-version`, `sequence-region`, `species`, `genome-build`, `feature-ontology` (spec also defines `attribute-ontology`, `source-ontology`) |
| GFF3 `#!` metadata (NCBI/Ensembl/Alliance) | `#!key[:] value` | `genome-build`, `genome-build-accession`, `genome-version`, `genome-date`, `genebuild-last-updated`, `gff-spec-version`, `processor`, `annotation-source`/`annotationSource`, `annotation-date`, `assembly`, `data-source`, `date-produced`, `primary-contact`, `species`, `tool` |
| Plain `#` comments before features | `# text` | free text (e.g. `# WormBase release WS298`) → recognised as an unrecognised comment, but scanned for release-like tokens |
| GAF | `!key: value`, nested blocks | `gaf-version`, `generated-by`, `date-generated`, `go-version`, `GO version`, `PANTHER version`, `Created on`, separators `!====`, `!Header from …` |
| VCF meta-information | `##key=value`, `##KEY=<k=v,…>` | `fileformat`, `fileDate`, `source` (may contain `;k=v`), `reference`, `contig` (`ID`, `length`, `assembly`, `md5`, `species`, `URL`), `phasing`, `dbSNP_BUILD_ID`, `INFO`/`FORMAT`/`FILTER`/`ALT`/`ID` (structural, not FAIR metadata) |
| FASTA defline | `>id rest` | Ensembl coord-system triple `(chromosome|scaffold):<assembly>:…`; `key=value;` (FlyBase: `MD5`, `release`, `species`, `dbxref`); `key=value` (WormBase); `[Organism]` (NCBI protein) |
| FAIR-bioHeaders (FHR/FHT/FHP/FHGFF3) | as specified | not observed in any surveyed file; must still be recognised (FR-001) |

## 5. Spec Kit research entries

### R1. Header conventions recognised in the first release

**Decision**: Recognise these six conventions:
1. The FAIR-bioHeaders headers.
2. GFF3 `##` directives.
3. GFF3 `#!` metadata lines, accepting both `key value` and `key: value`.
4. GAF `!key: value` lines, using only the first block as the file's own metadata.
5. VCF `##key=value` and `##KEY=<…>`, with `##contig` sub-fields parsed.
6. The first FASTA defline, parsed for Ensembl coordinate-system strings and `key=value[;]` pairs. This is reported as record-level, weaker evidence.

Keys are mapped to concepts through a synonym table, with case, `-`/`_`/camelCase differences and a trailing `:` normalised. The table starts with the keys in section 4. Any other comment line in the header region is listed as "unrecognised", not dropped.

**Rationale**: These conventions cover every metadata line seen in 34 real files from 9 provider groups. The variations in spelling (`genome-build` with `##` or `#!`, `annotationSource` or `annotation-source`, `assembly:`) are real and common, and a strict parser would miss the Alliance's own headers. FASTA has no file-level header anywhere, so ignoring deflines would report every FASTA as empty, even when FlyBase records MD5 and release.

**Alternatives considered**:
- Parse only the FAIR-bioHeaders headers. Rejected: no surveyed file uses them.
- Use a strict, spec-only GFF3/VCF parser. Rejected: it would reject or misread FlyBase `##genome-build`, the Alliance pre-header comment and ClinVar's date.
- Treat the GAF header as one flat key list. Rejected: nested upstream headers would produce conflicting dates and creators.

### R2. Detecting a recorded genome link in each type

**Decision**: Treat these as **recorded links**, in order of strength. Within each strength, the type-specific source is given.

1. **Checksum or digest**:
   - FHR/FAIR-bioHeaders checksum or SeqCol digest fields.
   - VCF `##contig=<…,md5=…>`. If present on every contig, this is a per-sequence digest set.
   - FASTA defline `MD5=` (FlyBase). This is per-sequence, self-describing, and allows SeqCol-style comparison.
2. **Accession**:
   - GFF3 `#!genome-build-accession`, with an optional `NCBI_Assembly:` prefix and a `GC[AF]_\d{9}\.\d+` pattern.
   - An accession inside `#!annotation-source`/`annotationSource`.
   - VCF `##reference=` or `##contig assembly=` when the value matches an assembly-accession pattern.
3. **URL**: VCF `##reference=<URL>`. Report whether it names a file or a directory.
4. **Name only**:
   - GFF3 `#!genome-build`, `##genome-build`, `#!genome-version`, `#!assembly`.
   - VCF `##reference=GRCh38`, `##contig assembly=`.
   - Ensembl FASTA defline coord-system assembly field.
   - FlyBase `release=`.

   Report these as "named, not identified" (partially evidenced).

GAF gets "not applicable: genome". It is checked instead for a gene-set or ontology version.

Everything else is **circumstantial**, and FR-005 requires it to be reported separately:
- GFF3 `##sequence-region` names and lengths;
- VCF `##contig ID/length`;
- feature seqids.

These are compared against the genome's names and lengths when a genome is supplied.

When an accession or name is recorded but the genome file does not state its own identity, the verdict is **unverifiable** and not match. That is the case for every surveyed FASTA, apart from file or directory names.

**Rationale**:
- Only NCBI and Ensembl GFF3 record an accession.
- FlyBase and Alliance record names, and WormBase records nothing.
- No VCF or derived FASTA records a digest of its genome.

The ordering separates the identifiers that can be checked from the names that only claim a genome, and it matches FR-005 and FR-006.

**Alternatives considered**:
- Accept any assembly-like string as a link. Rejected: it would credit `GRCh38` the same as `NCBI_Assembly:GCF_000001405.40`, while the actual GRCh38 sequences differ between patch levels and naming schemes.
- Infer the genome from the file name or directory (e.g. `GCF_000002985.6_WBcel235_*`). Rejected for "recorded" status because it is not in the header, but kept as a suggestion source.
- Require a checksum. Rejected: zero surveyed derived files would pass.

### R3. Representative test files for SC-001

**Decision**: Use this set as the SC-001 corpus. It has 15 files from 5 required providers plus GO, NCBI ClinVar and dbSNP, and covers all 4 types. The headers captured in `research/headers/` serve as fixtures, so tests do not need the network. Use versioned URLs where they exist, so that results stay reproducible.

| Provider | Type | URL |
|---|---|---|
| Alliance | GFF3 | https://download.alliancegenome.org/9.1.0/GFF/MGI/GFF_MGI_1.gff.gz |
| Alliance | GFF3 | https://download.alliancegenome.org/8.3.0/GFF/WB/GFF_WB_4.gff.gz |
| Alliance | GAF | https://download.alliancegenome.org/9.1.0/GAF/WB/GAF_WB_1.gaf.gz |
| Alliance | VCF | https://download.alliancegenome.org/3.2.0/VCF-GZ/WBcel235/VCF-GZ_WBcel235_38.vcf.gz |
| Alliance | FASTA genome | https://download.alliancegenome.org/9.1.0/FASTA/GRCz12tu/FASTA_GRCz12tu_0.fa.gz |
| WormBase | GFF3 | https://ftp.ebi.ac.uk/pub/databases/wormbase/releases/WS298/species/c_elegans/PRJNA13758/c_elegans.PRJNA13758.WS298.annotations.gff3.gz |
| WormBase | FASTA protein | https://ftp.ebi.ac.uk/pub/databases/wormbase/releases/WS298/species/c_elegans/PRJNA13758/c_elegans.PRJNA13758.WS298.protein.fa.gz |
| WormBase | VCF | https://ftp.ebi.ac.uk/pub/databases/wormbase/releases/WS298/species/c_elegans/PRJNA13758/c_elegans.PRJNA13758.WS298.variations.vcf.gz |
| FlyBase | GFF3 (tar.gz) | https://s3ftp.flybase.org/genomes/dmel/dmel_r6.69_FB2026_03/gff/dmel-all-r6.69.gff.gz |
| FlyBase | FASTA transcript | https://s3ftp.flybase.org/genomes/Drosophila_melanogaster/current/fasta/dmel-all-transcript-r6.69.fasta.gz (versioned twin under `dmel_r6.69_FB2026_03/fasta/`) |
| Ensembl | GFF3 | https://ftp.ensembl.org/pub/release-116/gff3/homo_sapiens/Homo_sapiens.GRCh38.116.chr.gff3.gz |
| Ensembl | FASTA protein | https://ftp.ensembl.org/pub/release-116/fasta/homo_sapiens/pep/Homo_sapiens.GRCh38.pep.all.fa.gz |
| Ensembl | VCF | https://ftp.ensembl.org/pub/release-116/variation/vcf/homo_sapiens/homo_sapiens-chrMT.vcf.gz |
| NCBI RefSeq | GFF3 | https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/002/985/GCF_000002985.6_WBcel235/GCF_000002985.6_WBcel235_genomic.gff.gz |
| NCBI RefSeq | FASTA genome | https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/002/985/GCF_000002985.6_WBcel235/GCF_000002985.6_WBcel235_genomic.fna.gz |
| GO | GAF | https://current.geneontology.org/annotations/wb.gaf.gz (pin to a dated release under `release.geneontology.org/<date>/annotations/` for reproducibility) |
| NCBI ClinVar | VCF | https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz (weekly-changing; use the captured fixture) |

For the User Story 2 pairing tests:
- **correct pair**: the NCBI RefSeq WBcel235 GFF3 with its genomic.fna. The accession is recorded, and the names `NC_003279.8` match.
- **circumstantial-only pair**: the WormBase WS298 GFF3 with the WS298 genomic.fa. There is no recorded link, and `##sequence-region` names and lengths are compared with the `>I` and other sequences.
- **name mismatch pair**: the NCBI GenBank GCA GFF3 (`BX284601.5`) with the RefSeq genomic.fna (`NC_003279.8`). It has the same assembly but different sequence names.

**Rationale**: The set covers the five providers SC-001 names and all four types. It also covers every header pattern found:
- accession links (NCBI, Ensembl);
- name-only links (FlyBase, Alliance);
- no link (WormBase);
- nested GAF;
- VCF `##contig assembly=` (Alliance), `##reference` as a URL (Ensembl) and as a name (ClinVar);
- a header-less FASTA;
- defline metadata;
- the format irregularities from section 3.

**Alternatives considered**:
- Synthetic fixtures only. Rejected: they would not show the spelling variation that real files have.
- Fetching whole real files in CI. Rejected: the files are large (multi-GB GFF3 and dbSNP), and the network is not reproducible. The captured header excerpts plus a few small truncated bodies are enough.
- Human-only files. Rejected: they would miss the variation in model-organism database (MOD) conventions, which is the Alliance use case.
