# FHR-Specification
FHR (<u>Fair</u> <u>H</u>eader <u>R</u>eference genome): a simple FAIR enough metadata structure for reference genomes that you can TRUST
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6762549.svg)](https://doi.org/10.5281/zenodo.6762549)

Part of what FHR sets off to do is make sure that we can map back to Schema.org as much as possible, this will be useful for microdata and rdfa conversions for users that want to embed data into genome webpages. We also want to be able to split out the header if we have to, we can make the coding easy on ourselves if we throw yaml into the header itself. or something that is a regex away from yaml. I think it's important that the header has a secondary character after the comment delineator to indicate that this is part of the header, otherwise a simple mistake in a regex for the header could easily grab regular comments in the fasta file. I also think that the secondary header delineating character should be on the keyboard, and not a yaml special character, this leaves the tilde as the best option. I could imagine it would look something like this:

_NOTE_: This is the FFRGS Specification Repo, if you would like to convert between data serialization, or validate your ffrgs instance, see [FHR-File-Converter](https://github.com/FAIR-bioHeaders/FHR-File-Converter)

```
;~schema: https://raw.githubusercontent.com/FAIR-bioHeaders/FHR-Specification/main/fhr.json
;~schemaVersion: 1
;~genome: Example species
;~genomeSynonym: eg. species
;~taxon:
;~  name: Example species
;~  uri: https://identifiers.org/taxonomy:0000
;~version: 0.0.1
;~metadataAuthor:
;~  name: Adam Wright
;~  uri: https://orcid.org/0000-0002-5719-4024
;~assembler:
;~  name: David Molik
;~  uri: https://orcid.org/0000-0003-3192-6538
;~dateCreated: '2022-03-21'
;~accessionID:
;~  name: VoucheringDatbase
;~  url: https://example.org/awesome_species/project-1024
;~instrument:
;~- Amazing Sequencer IIe
;~- Neato Sequencer
;~voucherSpecimen: Located in Freezer 33, Drawer 137
;~scholarlyArticle: https://doi.org/10.1371/journal.pntd.0008755
;~documentation: 'Built assembly from... '
;~identifier:
;~- eg:1024512256128643216842
;~relatedLink:
;~- https://example.org/example-species/our_genome
;~funding: 'some'
;~reuseConditions: 'public domain'
;~masking: semi-masked
;~checksum: md5:7582b26fcb0a9775b87c38f836e97c42
>Contig 1
AAAATCGATCGGCATA
.
.
.
``` 
 
## Metadata Draft v0.2 (fasta yaml header with easy microdata conversions)
FFRGS utilizes schema.org as much as possible for later integration

---
Specialised instances of Schema.org (we want as few of these as possible):
 
- `schemaVersion` (String) - Version of FFRGS (Currently always "1.0")
- `genome` (String) - ( Schema.org name )
- `version` (String) - ( Schema.org version ) Version of the Genome
- `license` (String) - ( Schema.org license ) License used (url or name of common license) 
- `funding` (String) - ( Schema.org funding ) Name of Grant used in the creation of the genome
 
These will always be remaps of properties, so:

``` 
Genome: <name>
```

---
Instances of Schema.org entities, where we just want a name and url because we’re not storing that data here: 
 
- `author` - ( Schema.org author ) (URL and String)
- `assembler` - creator of the genome ( Schema.org Person or Organisation ) (URL and String)
- `location` (URL) (Schema.org place)  (URL and String)
- `assemblySoftware` (Schema.org SoftwareApplication) (URL and String) [Optional]
- `voucherSpecimen` (String) - ( Schema.org Thing ) (URL and String)

These will be names, and urls:

``` 
author: 
 name: Name
 url: https://link 
```

---
Direct use of Schema.org entities:
 
- `dateCreated` (DataTime) (Schema.org dateCreated) (date)
- `instrument` (Schema.org instrument) (URL or String) [Optional]
- `scholarlyArticle` (Schema.org ScholarlyArticle) (URL) [Optional]
- `documentation` (Schema.org documentation) (URL or String) [Optional]
- `identifier` (Schema.org identifier ) (String) [Optional]
- `relatedLink` (Schema.org relatedLink) (URL) [Optional]

``` 
These are all direct use:
 
- `dateCreated`: <date>
```

Another benefit of having this easy conversion is that we can submit the spec to say bioschema without much work after publishing. 

## Citing FHR
Information on Citations of FHR


### Citing the Validation Tool
cite the validation tool when directly interacting with the tool or library
The APA citation for the [FHR validation/converter software](https://github.com/FAIR-bioHeaders/FHR-File-Converter) is:

```
Molik, D., & Wright, A. FHR File Converster [Computer software]. https://github.com/FAIR-bioHeaders/FHR-File-Converter
```

Or in bibtex:
```bibtex
% Citation For FHR Validation/Converter Software
@software{FHR_File_Converter,
    author = {Molik, David and Wright, Adam},
    year = {2023},
    license = {PDDL-1.0},
    title = {{FHR File Converster}},
    url = {https://github.com/FAIR-bioHeaders/FHR-File-Converter},
    doi = {10.5281/zenodo.6762547}
}
```
### Citing the Specification
cite the specification when directly interacting with the specification (pull requests, comments on schema)
The APA citation for the [FHR specification](https://github.com/FAIR-bioHeaders/FHR-Specification) is:

```
Molik, D., & Wright, A.  FHR Specification [Data set]. https://github.com/FAIR-bioHeaders/FHR-Specification
```

Or in bibtex:
```bibtex
% Citation For FHR Specification
@misc{FHR_Specification,
    author = {Molik, David and Wright, Adam},
    year = {2023},
    title = {{FHR Specification}},
    url = {https://github.com/FAIR-bioHeaders/FHR-Specification},
    doi = {10.5281/zenodo.6762549}
}
```
### Citing the Preprint
**(best option)** cite the preprint talking about the effort, or want a broad citation of FHR
The APA citation for the [FHR preprint](https://www.biorxiv.org/content/10.1101/2023.11.29.569306v1) is:

```
Wright, A., Wilkinson, M. D., Mungall, C., Cain, S., Richards, S., Sternberg, P., ... & Molik, D. C. (2023). Data Resources and Analyses Fair Header Reference genome: A Trustworthy standard. bioRxiv, 2023-11.
```

Or in bibtex:
```bibtex
% Citation For FHR Pre-print
@article {Wright2023,
	author = {Adam Wright and Mark D Wilkinson and Chris Mungall and Scott Cain and Stephen Richards and Paul Sternberg and Ellen Provin and Jonathan L Jacobs and Scott Geib and Daniela Raciti and Karen Yook and Lincoln Stein and David C Molik},
	title = {DATA RESOURCES AND ANALYSES FAIR Header Reference genome: A TRUSTworthy standard},
	elocation-id = {2023.11.29.569306},
	year = {2023},
	doi = {10.1101/2023.11.29.569306},
	publisher = {Cold Spring Harbor Laboratory},
	abstract = {The lack of interoperable data standards among reference genome data-sharing platforms inhibits cross-platform analysis while increasing the risk of data provenance loss. Here, we describe the FAIR-bioHeaders Reference genome (FHR), a metadata standard guided by the principles of Findability, Accessibility, Interoperability, and Reuse (FAIR) in addition to the principles of Transparency, Responsibility, User focus, Sustainability, and Technology (TRUST). The objective of FHR is to provide an extensive set of data serialisation methods and minimum data field requirements while still maintaining extensibility, flexibility, and expressivity in an increasingly decentralised genomic data ecosystem. The effort needed to implement FHR is low; FHR{\textquoteright}s design philosophy ensures easy implementation while retaining the benefits gained from recording both machine and human-readable provenance.Competing Interest StatementThe authors have declared no competing interest.},
	URL = {https://www.biorxiv.org/content/early/2023/12/01/2023.11.29.569306},
	eprint = {https://www.biorxiv.org/content/early/2023/12/01/2023.11.29.569306.full.pdf},
	journal = {bioRxiv}
}
```
