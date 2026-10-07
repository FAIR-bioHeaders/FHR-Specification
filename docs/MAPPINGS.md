# MIxS/MIGS mappings

The crosswalk is pinned to [MIxS v7.0.1](https://github.com/GenomicsStandardsConsortium/mixs/blob/v7.0.1/src/mixs/schema/mixs.yaml).
MIGS is a family of MIxS checklists. These mappings project overlapping sequencing
terms; they do not create a complete MIGS record or establish checklist compliance.

| FHR source | Target | Relationship | Handling and loss |
| --- | --- | --- | --- |
| `vitalStats.numberContigs` | `number_contig` (`MIXS:0000060`) | Exact | Copy the submitted assembly contig count. |
| `assemblyProtocol` | `sop` (`MIXS:0000090`) | Narrow | Copy the assembly protocol URI; FHR does not describe annotation procedures. |
| `assemblySoftware` | `assembly_software` (`MIXS:0000058`) | Lossy | One structured tool becomes `name;version;parameters`; URI is omitted. |

The LinkML model records term mappings on the corresponding slots. The reviewed
crosswalk in `fhr_mappings.yml` is executed by the small FHR-specific projection
script below; it is not a claim that an arbitrary LinkML transformation engine
can execute its expression extensions.

```bash
python scripts/project_mixs.py examples/example.fhr.json
```

The output includes `metadata`, `unmapped` reasons, and `target_version`. Missing
software versions/options are never invented. Legacy software-name strings,
multiple tools, or embedded semicolon/newline delimiters require manual projection.
An explicitly empty option list renders as `none`; argument lists use shell quoting.
No commands are executed. Missing source fields are reported as omissions.

`genome` names an organism/reference, while MIxS `assembly_name` identifies a
submitter's named/versioned assembly: there is no unconditional equivalence.
`dateCreated` is not a sample collection date. `accessionID.name` can name a
repository and must not be treated as an INSDC accession. Taxonomy and accession
crosswalks need additional source context. The earlier speculative NCBI/RefSeq/JGI
mappings have been removed rather than emitting misleading accession values.

Check the target checklist's required fields, controlled vocabularies, and resource
submission rules before using the projection in a submission. Updating MIxS versions
requires reviewing term definitions and running the mapping fixtures again.
