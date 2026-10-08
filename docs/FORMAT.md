# FHR v0.3 format and compatibility

FHR release v0.3 and the converter 0.3.x packages retain numeric schemaVersion 1.
The header parsing rules below are implemented from converter 0.3.1.
The assembly's own version string is independent. No required fields were added.
Top-level metadata is closed; optional fields may be omitted, not replaced by null.

## New optional fields

| Field | Value | Meaning |
| --- | --- | --- |
| `assemblySoftware` | Legacy string or array of objects | Assembly software name; objects require `name`, with optional `uri`, `version`, and `commandLineOption` (array of argument strings). |
| `assemblyProtocol` | URI string | External assembly protocol/workflow documentation. |
| `vitalStats.N90` | Nonnegative integer | Contig length in base pairs at the 90% cumulative assembly-length threshold. |
| `vitalStats.gcContent` | Number from 0 to 100 | Percentage of G/C bases; contributors must document how ambiguous bases were handled. |
| `seqcol_id` | 32 base64url characters | Unprefixed level-zero GA4GH refget sequence collection digest. |

SeqCol uses [sha512t24u](https://ga4gh.github.io/refget/seqcols/): SHA-512 truncated
to 24 bytes and URL-safe base64. Its default collection identity incorporates
names, lengths, and sequence digests; it is not simply a hash of concatenated
sequence letters. FHR stores a user-supplied digest and does not compute it,
resolve it, or verify it against a local genome. Different attribute profiles can
produce different digests; record that context in external documentation.

## Checksum decision for v0.3

The [FHR paper](https://doi.org/10.1093/bib/bbae122) describes identity covering
metadata and sequence data together. The published schema specifies SHA-512/256
in a 44-character base64 representation; older README examples and converter
helpers used MD5 and described different coverage. v0.3 explicitly adopts:

1. Read the FASTA/GFA as bytes; do not normalize line endings, encoding, comments,
   sequence wrapping, ordering, or whitespace.
2. Require exactly one root-level header line matching `;~checksum:` (FASTA) or
   `#~checksum:` (GFA), with an unquoted key. Spaces or tabs may appear before
   the key only to match the root indentation of the other header lines, and
   before the colon.
   Nested properties named checksum remain covered.
3. Exclude that entire line and its line terminator. Hash every other byte,
   including all other metadata and ordinary comments.
4. Apply SHA-512/256 (the SHA-512/256 algorithm, not SHA-512 truncated manually).
   Encode its 32-byte digest using standard padded base64, with no `md5:` prefix.

Header lines are identified on the same byte lines that are hashed, so every
reader must agree on what the checksum line contains:

- The checksum value must appear on the checksum line itself as a single-line
  YAML scalar; block scalars and continuation lines are invalid.
- FHR header lines must be UTF-8 and must not contain U+0085, U+2028, or U+2029,
  which YAML treats as line breaks. Bytes outside header lines are not decoded.
- A FASTA/GFA file must not begin with a UTF-8 byte order mark. JSON, YAML, and
  HTML metadata may begin with one; it is ignored.
- FHR metadata must not contain duplicate mapping keys, YAML anchors, aliases,
  or merge keys.
- In microdata, the first of repeated attributes applies, and `itemtype` and
  `itemprop` are space-separated token lists.

- FHR lines must form the leading header block: every `;~`/`#~` line must come
  before the first FASTA `>` line, or the first GFA line that is neither a `#`
  comment nor blank. Ordinary comments and blank lines may be mixed in. A
  `;~`/`#~` line after that point, including one from a concatenated file, makes
  the file invalid; it is neither ignored nor merged.

Changing any covered metadata or data bytes invalidates the checksum. The
checksum does not authenticate an author or protect against malicious rewriting.
A supplied SeqCol digest identifies a collection through a separate algorithm.

The combine helpers regenerate a canonical YAML header, strip existing FHR lines
from the supplied payload, preserve every other payload byte, and compute the new
checksum. Strip removes complete FHR lines and leaves ordinary comments intact.
A bare metadata file's checksum is only a value; metadata validation does not
establish correspondence with a genome file.

## Migration

Recombine metadata with the original FASTA/GFA to recalculate old MD5 or
payload-only checksums. Do not relabel an MD5 digest as SHA-512/256. The synthetic
checksum and SeqCol placeholders in standalone examples are for structure only.

Legacy software strings remain accepted. New objects have a closed set of
properties and require a name. ORCID values now explicitly require strings;
previously the pattern-only definition could inadvertently accept nonstrings.
The checksum pattern also requires all 44 characters to be base64 characters,
closing a trailing-newline regex loophole. These corrections reject malformed
metadata rather than changing valid ORCID/checksum representations.
No implied license rename is introduced: `reuseConditions` remains the field.

Review a concrete schema/baseline diff for intentional changes, synchronize the
bundled converter schema, and run LinkML equivalence and example validation.
