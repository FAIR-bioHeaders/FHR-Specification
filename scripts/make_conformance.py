"""Write the FHR FASTA/GFA conformance vectors and their manifest (stdlib only).

Every vector is built from a small metadata template. Expected checksums are
computed here with ``hashlib.sha512_256`` and base64 over the bytes the
docs/FORMAT.md rules cover, never by the FHR File Converter. Output is
deterministic: compressed vectors use stored deflate blocks, mtime 0 and no file
name, so rerunning the script reproduces identical bytes.
"""

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "conformance"
MANIFEST_VERSION = 1

# Stable, non-normative labels for the docs/FORMAT.md rules.
RULES = {
    "R1": "Checksum rule 1: hash the exact file bytes without normalization; "
          "for gzip/BGZF input, the decompressed bytes.",
    "R2": "Checksum rule 2: exactly one root-level checksum line with an unquoted "
          "key; spaces only to match root indentation and before the colon; nested "
          "checksum properties stay covered.",
    "R3": "Checksum rule 3: exclude that entire line and its terminator; hash every "
          "other byte, so changing covered bytes invalidates the checksum.",
    "R4": "Checksum rule 4: SHA-512/256 digest in standard padded base64, no prefix.",
    "R5": "Header parsing: the checksum value is a single-line YAML scalar on the "
          "checksum line; block scalars and continuation lines are invalid.",
    "R6": "Header parsing: FHR header lines are UTF-8 without U+0085, U+2028 or "
          "U+2029; bytes outside header lines are not decoded.",
    "R7": "Header parsing: a FASTA/GFA file must not begin with a UTF-8 byte "
          "order mark.",
    "R8": "Header parsing: no duplicate mapping keys, YAML anchors, aliases or "
          "merge keys.",
    "R9": "Header parsing: microdata repeated attributes and token lists "
          "(not applicable to FASTA/GFA vectors).",
    "R10": "Header parsing: FHR lines form the leading header block; a later "
           "FHR line, including one from a concatenated file, is invalid.",
}
NOT_APPLICABLE = {"R9": "Microdata (HTML) rule; these vectors are FASTA and GFA only."}

PREFIX = {"fasta": b";~", "gfa": b"#~"}
COMMENT = {"fasta": b";", "gfa": b"#"}
SUFFIX = {"fasta": ".fhr.fasta", "gfa": ".fhr.gfa"}
MARK = b"@CHECKSUM@"
GENOME = "Synthetic FHR conformance genome"
VERSION = "1.0.0"
MASKING = "not-masked"

# Root-level YAML metadata; ``None`` marks the checksum line.
METADATA = [
    "schema: https://raw.githubusercontent.com/FAIR-bioHeaders/FHR-Specification/main/fhr.json",
    "schemaVersion: 1.0",
    f"genome: {GENOME}",
    "taxon:",
    "  name: Homo sapiens",
    "  uri: https://identifiers.org/taxonomy:9606",
    f"version: {VERSION}",
    "metadataAuthor:",
    "- name: Synthetic metadata author (placeholder)",
    "assemblyAuthor:",
    "- name: Synthetic assembly author (placeholder)",
    "dateCreated: '2026-10-08'",
    f"masking: {MASKING}",
    "documentation: Synthetic FHR conformance vector; not a real assembly.",
    None,
]
BODY = {
    "fasta": [b">Contig1 synthetic sequence", b"ACGTACGTAC", b"GGTTAACCAT"],
    "gfa": [b"H\tVN:Z:1.0", b"S\tContig1\tACGTACGTACGGTTAACCAT"],
}
EXPECTED_METADATA = {"genome": GENOME, "version": VERSION, "masking": MASKING}


def digest(data):
    return base64.b64encode(hashlib.new("sha512_256", data).digest()).decode("ascii")


class Line:
    """One line without its terminator; ``excluded`` lines are not hashed."""

    def __init__(self, text, excluded=False):
        self.text = text
        self.excluded = excluded


def header(kind, metadata=METADATA, indent="", key="checksum: "):
    """FHR lines for ``metadata``, with the checksum line written as ``key``."""
    prefix = PREFIX[kind]
    lines = []
    for item in metadata:
        if item is None:
            text = prefix + indent.encode() + key.encode() + MARK
            lines.append(Line(text, excluded=True))
        else:
            lines.append(Line(prefix + indent.encode() + item.encode("utf-8")))
    return lines


def body(kind):
    return [Line(text) for text in BODY[kind]]


def assemble(lines, endings=b"\n", final_newline=True, hash_data=None):
    """Join ``lines`` and fill the checksum marker.

    ``endings`` is one terminator or a list cycled over the lines. The checksum
    is computed over the bytes of every line not marked excluded, unless
    ``hash_data`` maps those bytes to the bytes that should be hashed instead.
    """
    if isinstance(endings, bytes):
        endings = [endings]
    pieces = []
    for index, line in enumerate(lines):
        last = index == len(lines) - 1
        ending = b"" if last and not final_newline else endings[index % len(endings)]
        pieces.append((line, line.text + ending))
    covered = b"".join(data for line, data in pieces if not line.excluded)
    value = digest(hash_data(covered) if hash_data else covered).encode("ascii")
    return b"".join(data.replace(MARK, value) for _, data in pieces), value.decode()


def standard(kind, **options):
    return assemble(header(kind) + body(kind), **options)


# Compression: stored deflate blocks keep the bytes independent of zlib builds.

def _stored_deflate(data):
    if not data:
        return b"\x01\x00\x00\xff\xff"
    out = b""
    for start in range(0, len(data), 0xFFFF):
        chunk = data[start:start + 0xFFFF]
        final = start + 0xFFFF >= len(data)
        out += bytes([final]) + struct.pack("<HH", len(chunk), len(chunk) ^ 0xFFFF) + chunk
    return out


def _trailer(data):
    return struct.pack("<II", zlib.crc32(data), len(data) & 0xFFFFFFFF)


def gzip_member(data):
    # ID1 ID2 CM=deflate FLG=0 MTIME=0 XFL=0 OS=unknown: no name, fixed time.
    return b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\xff" + _stored_deflate(data) + _trailer(data)


BGZF_EOF = bytes.fromhex("1f8b08040000000000ff0600424302001b0003000000000000000000")


def bgzf(data, block_size=96):
    """BGZF: gzip members carrying a BC extra field, then the standard EOF block."""
    out = b""
    for start in range(0, len(data), block_size):
        chunk = data[start:start + block_size]
        deflated = _stored_deflate(chunk)
        block_size_minus_one = 18 + len(deflated) + 8 - 1
        out += (
            b"\x1f\x8b\x08\x04\x00\x00\x00\x00\x00\xff"
            + struct.pack("<H", 6) + b"BC" + struct.pack("<HH", 2, block_size_minus_one)
            + deflated + _trailer(chunk)
        )
    return out + BGZF_EOF


def multimember_gzip(data, split):
    return gzip_member(data[:split]) + gzip_member(data[split:])


def decompress(data):
    """Decompress concatenated gzip members (for self-checks)."""
    out = b""
    while data:
        engine = zlib.decompressobj(31)
        out += engine.decompress(data) + engine.flush()
        data = engine.unused_data
    return out


# Reference reading of the rules, used to self-check valid vectors.

def reference_checksum(data, kind):
    """Return (stated value, computed value) or raise ValueError."""
    prefix = PREFIX[kind]
    lines = data.splitlines(keepends=True)
    header_lines, in_block = [], True
    for line in lines:
        if in_block:
            if kind == "fasta" and line.startswith(b">"):
                in_block = False
            elif kind == "gfa" and not line.startswith(b"#") and line.strip():
                in_block = False
        if line.startswith(prefix):
            if not in_block:
                raise ValueError("FHR line after the header block")
            header_lines.append(line)
    contents = [line[len(prefix):].rstrip(b"\r\n") for line in header_lines]
    indents = [
        len(text) - len(text.lstrip(b" \t")) for text in contents
        if text.strip() and not text.lstrip().startswith(b"#")
    ]
    pattern = re.compile(rb"^" + re.escape(prefix) + rb"([ \t]*)checksum[ \t]*:(.*)$", re.S)
    matches = [
        line for line in header_lines
        if (found := pattern.match(line.rstrip(b"\r\n"))) and len(found.group(1)) == min(indents)
    ]
    if len(matches) != 1:
        raise ValueError("expected exactly one root checksum line")
    excluded = matches[0]
    position = data.index(excluded) if lines.count(excluded) == 1 else None
    if position is None:
        raise ValueError("ambiguous checksum line")
    value = pattern.match(excluded.rstrip(b"\r\n")).group(2).strip().strip(b"'\"").decode()
    return value, digest(data[:position] + data[position + len(excluded):])


# The vectors.

VALID = []
INVALID = []


def valid(name, kind, data, value, rules, description, compression=None):
    VALID.append(dict(name=name, kind=kind, data=data, checksum=value, rules=rules,
                      description=description, compression=compression))


def invalid(name, kind, data, rule, reason, compression=None):
    INVALID.append(dict(name=name, kind=kind, data=data, rule=rule, reason=reason,
                        compression=compression))


def comments_and_blanks(kind):
    comment = COMMENT[kind]
    lines = header(kind)
    lines.insert(0, Line(comment + b" ordinary comment before the FHR lines"))
    lines.insert(1, Line(b""))
    lines.insert(5, Line(comment + b" ordinary comment between FHR lines"))
    lines.insert(6, Line(b""))
    lines.insert(9, Line(PREFIX[kind] + b"# a YAML comment inside the FHR header"))
    lines.insert(len(lines) - 1, Line(comment))
    extra = [Line(b";  legacy FASTA comment after a record")] if kind == "fasta" else []
    return lines + [Line(b"")] + body(kind) + extra


def with_metadata(kind, replacements=(), insert=(), **options):
    metadata = list(METADATA)
    for old, new in replacements:
        metadata[metadata.index(old)] = new
    for anchor, items in insert:
        position = metadata.index(anchor) + 1
        metadata[position:position] = items
    return header(kind, metadata, **options)


def build():
    VALID.clear()
    INVALID.clear()
    plain = {}
    for kind in ("fasta", "gfa"):
        k = kind
        data, value = standard(k)
        plain[k] = (data, value)
        valid(f"{k}-lf", k, data, value, ["R1", "R2", "R3", "R4", "R7", "R10"],
              "LF line endings; the checksum line is the last FHR line.")
        data, value = standard(k, endings=b"\r\n")
        valid(f"{k}-crlf", k, data, value, ["R1", "R3"], "CRLF line endings; CR bytes are hashed.")
        crlf = data
        data, value = standard(k, endings=b"\r")
        valid(f"{k}-cr", k, data, value, ["R1", "R3"], "Lone CR line endings.")
        data, value = standard(k, endings=[b"\n", b"\r\n", b"\r"])
        valid(f"{k}-mixed-endings", k, data, value, ["R1", "R3"],
              "LF, CRLF and CR line endings mixed in one file.")
        data, value = standard(k, final_newline=False)
        valid(f"{k}-no-final-newline", k, data, value, ["R1", "R3"],
              "The last sequence line has no terminator.")
        data, value = assemble(comments_and_blanks(k))
        valid(f"{k}-comments-and-blank-lines", k, data, value, ["R3", "R10"],
              "Ordinary comments, blank lines and a YAML comment before and between "
              "FHR lines; all of them are hashed.")
        data, value = assemble(header(k, indent=" ") + body(k))
        valid(f"{k}-root-indented", k, data, value, ["R2"],
              "Every FHR line, including the checksum line, has root indentation 1.")
        data, value = assemble(header(k, key="checksum  : ") + body(k))
        valid(f"{k}-space-before-colon", k, data, value, ["R2"], "Spaces before the colon.")
        lines = with_metadata(k, insert=[(
            "  uri: https://identifiers.org/taxonomy:9606",
            ["  checksum: nested property, hashed like other metadata"],
        )])
        data, value = assemble(lines + body(k))
        valid(f"{k}-nested-checksum", k, data, value, ["R2", "R3"],
              "A nested taxon.checksum property is ordinary covered metadata.")
        quote = "'" if k == "fasta" else '"'
        lines = header(k)
        lines[-1].text = lines[-1].text.replace(MARK, quote.encode() + MARK + quote.encode())
        data, value = assemble(lines + body(k))
        valid(f"{k}-quoted-value", k, data, value, ["R2", "R5"],
              "The checksum value is a quoted single-line scalar; the key is unquoted.")
        lines = header(k)
        lines[-1].text += b"   "
        data, value = assemble(lines + body(k))
        valid(f"{k}-checksum-trailing-spaces", k, data, value, ["R3", "R5"],
              "Trailing spaces on the checksum line are excluded with it.")
        lines = header(k)
        lines.insert(0, lines.pop())
        data, value = assemble(lines + body(k))
        valid(f"{k}-checksum-first", k, data, value, ["R2", "R3"],
              "The checksum line is the first line of the file.")
        comment = COMMENT[k]
        lines = header(k)
        lines.insert(3, Line(comment + b" ordinary comment, Latin-1 bytes: caf\xe9 \xff\xfe"))
        tail = [Line(b">Contig1 description in Latin-1: caf\xe9 na\xefve"), Line(BODY[k][1]), Line(BODY[k][2])] \
            if k == "fasta" else [Line(BODY[k][0]), Line(BODY[k][1] + b"\tDS:Z:caf\xe9")]
        data, value = assemble(lines + tail)
        valid(f"{k}-non-utf8-outside-header", k, data, value, ["R1", "R6"],
              "Non-UTF-8 bytes in an ordinary comment and a sequence line are hashed, "
              "not decoded.")
        lines = with_metadata(k, replacements=[(
            "documentation: Synthetic FHR conformance vector; not a real assembly.",
            "documentation: 'Synthetic vector, UTF-8 text: café µm — 測試'",
        )])
        data, value = assemble(lines + body(k))
        valid(f"{k}-utf8-metadata", k, data, value, ["R6"],
              "Non-ASCII UTF-8 text in a header value.")
        lines = with_metadata(k, replacements=[(
            "documentation: Synthetic FHR conformance vector; not a real assembly.",
            "documentation: 'Quoted YAML indicators are text: &anchor *alias <<: merge'",
        )])
        data, value = assemble(lines + body(k))
        valid(f"{k}-yaml-indicators-in-strings", k, data, value, ["R8"],
              "Anchor, alias and merge-key characters inside a quoted string are text.")

        # Invalid vectors with otherwise correct checksums unless stated.
        data, _ = standard(k, endings=b"\r\n", hash_data=lambda b: b.replace(b"\r\n", b"\n"))
        assert data != crlf
        invalid(f"{k}-crlf-normalized-checksum", k, data, "R1",
                "CRLF file whose checksum was computed after converting line endings to LF.")
        lines = header(k)[:-1]
        data, _ = assemble(lines + body(k))
        invalid(f"{k}-missing-checksum", k, data, "R2", "No checksum line.")
        lines = header(k)
        lines.insert(2, Line(lines[-1].text, excluded=True))
        data, _ = assemble(lines + body(k))
        invalid(f"{k}-two-checksum-lines", k, data, "R2",
                "Two root-level checksum lines with the same value.")
        quote = "'" if k == "fasta" else '"'
        data, _ = assemble(header(k, key=f"{quote}checksum{quote}: ") + body(k))
        invalid(f"{k}-quoted-key", k, data, "R2", "The checksum key is quoted.")
        lines = with_metadata(k, insert=[("  uri: https://identifiers.org/taxonomy:9606", [None])])
        lines[6].text = lines[6].text.replace(b"checksum: ", b"  checksum: ")
        lines.pop()
        data, _ = assemble(lines + body(k))
        invalid(f"{k}-only-nested-checksum", k, data, "R2",
                "Only a nested taxon.checksum holds the digest; there is no root checksum line.")
        data, value = standard(k)
        data = data.replace(GENOME.encode(), b"Tampered genome name")
        invalid(f"{k}-metadata-tampered", k, data, "R3",
                "Metadata changed after the checksum was computed (checksum mismatch).")
        data, _ = standard(k)
        data = data.replace(b"GGTTAACC", b"GGTTAACG")
        invalid(f"{k}-sequence-tampered", k, data, "R3",
                "Sequence changed after the checksum was computed (checksum mismatch).")
        lines = header(k)
        lines[-1].excluded = False
        data, _ = assemble(lines + body(k), hash_data=lambda b, k=k: b.replace(
            PREFIX[k] + b"checksum: " + MARK + b"\n", b"\n"))
        invalid(f"{k}-checksum-terminator-hashed", k, data, "R3",
                "Checksum computed with the checksum line's terminator still included.")
        data, _ = assemble(comments_and_blanks(k))
        data = data.replace(b"ordinary comment between", b"ordinary comment edited between")
        invalid(f"{k}-comment-tampered", k, data, "R3",
                "An ordinary comment changed after the checksum was computed; comments are covered.")
        data, _ = assemble(header(k) + body(k))
        covered = data.replace(re.search(rb"[;#]~checksum: \S+\n", data).group(), b"")
        wrong = base64.b64encode(hashlib.sha512(covered).digest()[:32])
        data = re.sub(rb"(~checksum: )\S+", lambda m: m.group(1) + wrong, data)
        invalid(f"{k}-truncated-sha512", k, data, "R4",
                "SHA-512 truncated to 32 bytes instead of SHA-512/256.")
        wrong = base64.b64encode(hashlib.sha256(covered).digest())
        data = re.sub(rb"(~checksum: )\S+", lambda m: m.group(1) + wrong, data)
        invalid(f"{k}-sha256", k, data, "R4", "SHA-256 instead of SHA-512/256.")
        lines = header(k, key="checksum: |")
        lines[-1].text = lines[-1].text.replace(MARK, b"")
        lines.append(Line(PREFIX[k] + b"  " + MARK, excluded=True))
        data, _ = assemble(lines + body(k))
        invalid(f"{k}-block-literal-checksum", k, data, "R5",
                "The checksum value is a literal block scalar on the next line.")
        lines = header(k, key="checksum: >-")
        lines[-1].text = lines[-1].text.replace(MARK, b"")
        lines.append(Line(PREFIX[k] + b"  " + MARK, excluded=True))
        data, _ = assemble(lines + body(k))
        invalid(f"{k}-folded-checksum", k, data, "R5",
                "The checksum value is a folded block scalar on the next line.")
        data, value = standard(k)
        head, rest = value[:22], value[22:]
        data = data.replace(value.encode(), f"{head}\n".encode() + PREFIX[k] + f"  {rest}".encode())
        invalid(f"{k}-continued-checksum", k, data, "R5",
                "The plain checksum value continues on a second FHR line.")
        data, value = standard(k)
        data = data.replace(value.encode(), f'"{head}\n'.encode() + PREFIX[k] + f'  {rest}"'.encode())
        invalid(f"{k}-quoted-continued-checksum", k, data, "R5",
                "A double-quoted checksum value continues on a second FHR line.")
        for code, label in (("\u0085", "u0085"), (" ", "u2028"), (" ", "u2029")):
            lines = with_metadata(k, replacements=[(
                "documentation: Synthetic FHR conformance vector; not a real assembly.",
                f"documentation: Synthetic{code}  vector text",
            )])
            data, _ = assemble(lines + body(k))
            invalid(f"{k}-{label}-in-header", k, data, "R6",
                    f"An FHR header line contains U+{label[1:].upper()}, a YAML line break.")
        lines = header(k)
        lines[13].text = lines[13].text.replace(b"Synthetic", b"Synth\xe9tic")
        data, _ = assemble(lines + body(k))
        invalid(f"{k}-non-utf8-header", k, data, "R6", "An FHR header line is not valid UTF-8.")
        data, _ = assemble([Line(b"\xef\xbb\xbf" + line.text, line.excluded) if i == 0 else line
                            for i, line in enumerate(header(k) + body(k))])
        invalid(f"{k}-utf8-bom", k, data, "R7", "The file begins with a UTF-8 byte order mark.")
        lines = with_metadata(k, insert=[(f"genome: {GENOME}", ["genome: Second genome value"])])
        data, _ = assemble(lines + body(k))
        invalid(f"{k}-duplicate-key", k, data, "R8", "The root key genome appears twice.")
        lines = with_metadata(k, replacements=[(f"genome: {GENOME}", f"genome: &name {GENOME}")])
        data, _ = assemble(lines + body(k))
        invalid(f"{k}-yaml-anchor", k, data, "R8", "A YAML anchor on the genome value.")
        lines = with_metadata(k, replacements=[(f"genome: {GENOME}", f"genome: &name {GENOME}")],
                              insert=[(f"genome: &name {GENOME}", ["genomeSynonym:", "- *name"])])
        data, _ = assemble(lines + body(k))
        invalid(f"{k}-yaml-alias", k, data, "R8", "A YAML alias repeats the anchored genome value.")
        lines = with_metadata(k, replacements=[("  name: Homo sapiens", "  <<: {name: Homo sapiens}")])
        data, _ = assemble(lines + body(k))
        invalid(f"{k}-yaml-merge-key", k, data, "R8", "taxon uses a YAML merge key.")
        late = [Line(PREFIX[k] + b"funding: added after the sequence data")]
        data, _ = assemble(header(k) + body(k) + late)
        invalid(f"{k}-fhr-line-after-sequence", k, data, "R10",
                "An FHR line follows the first record; it is hashed, not ignored or merged.")
        second_metadata = [item.replace(GENOME, "Second concatenated genome") if item else item
                           for item in METADATA]
        second, _ = assemble(header(k, second_metadata) + body(k))
        data = plain[k][0] + second
        invalid(f"{k}-concatenated", k, data, "R10",
                "Two complete FHR files concatenated; each part has a correct checksum.")

    for k in ("fasta", "gfa"):
        data, value = plain[k]
        valid(f"{k}-gzip", k, gzip_member(data), value, ["R1"],
              f"{k}-lf compressed as one gzip member; same checksum.", "gzip")
        valid(f"{k}-bgzf", k, bgzf(data), value, ["R1"],
              f"{k}-lf compressed as multi-block BGZF; same checksum.", "bgzf")
        split = data.index(b"checksum: ") + 20
        valid(f"{k}-gzip-multimember", k, multimember_gzip(data, split), value, ["R1"],
              f"{k}-lf as two gzip members split inside the checksum line; same checksum.",
              "gzip")
    data, _ = plain["fasta"]
    invalid("fasta-gzip-sequence-tampered", "fasta",
            gzip_member(data.replace(b"GGTTAACC", b"GGTTAACG")), "R3",
            "Compressed copy of a sequence-tampered file (checksum mismatch).", "gzip")


def path_for(entry):
    suffix = SUFFIX[entry["kind"]] + (".gz" if entry["compression"] else "")
    status = "valid" if "checksum" in entry else "invalid"
    return f"{status}/{entry['name']}{suffix}"


def self_check():
    names = set()
    for entry in VALID + INVALID:
        assert entry["name"] not in names, entry["name"]
        names.add(entry["name"])
    for entry in VALID:
        data = decompress(entry["data"]) if entry["compression"] else entry["data"]
        stated, computed = reference_checksum(data, entry["kind"])
        assert stated == computed == entry["checksum"], entry["name"]
    for entry in INVALID:
        data = decompress(entry["data"]) if entry["compression"] else entry["data"]
        try:
            stated, computed = reference_checksum(data, entry["kind"])
        except (ValueError, UnicodeDecodeError):
            continue
        if entry["rule"] in {"R1", "R3", "R4"}:
            assert stated != computed, entry["name"]


def manifest():
    covered = {}
    vectors = []
    for entry in VALID + INVALID:
        item = {
            "id": entry["name"],
            "file": path_for(entry),
            "format": entry["kind"],
            "compressed": bool(entry["compression"]),
        }
        if entry["compression"]:
            item["compression"] = entry["compression"]
        if "checksum" in entry:
            item.update(expected="valid", rules=entry["rules"], description=entry["description"],
                        checksum=entry["checksum"], metadata=EXPECTED_METADATA)
            for rule in entry["rules"]:
                covered.setdefault(rule, set()).add("valid")
        else:
            item.update(expected="invalid", rule=entry["rule"], reason=entry["reason"])
            covered.setdefault(entry["rule"], set()).add("invalid")
        vectors.append(item)
    for rule in RULES:
        if rule not in NOT_APPLICABLE:
            assert covered.get(rule) == {"valid", "invalid"}, rule
    return {
        "manifestVersion": MANIFEST_VERSION,
        "specification": "docs/FORMAT.md",
        "checksumDefinition": "base64(SHA-512/256) over the (decompressed) file bytes except the "
                    "root-level checksum line and its terminator",
        "rules": {
            rule: {"summary": text, **({"notApplicable": NOT_APPLICABLE[rule]}
                                       if rule in NOT_APPLICABLE else {})}
            for rule, text in RULES.items()
        },
        "vectors": vectors,
    }


def write(output):
    build()
    self_check()
    for status in ("valid", "invalid"):
        directory = output / status
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True)
    for entry in VALID + INVALID:
        (output / path_for(entry)).write_bytes(entry["data"])
    text = json.dumps(manifest(), indent=2, ensure_ascii=True) + "\n"
    (output / "manifest.json").write_bytes(text.encode("ascii"))
    return len(VALID), len(INVALID)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="directory to write (default: conformance/)")
    args = parser.parse_args()
    if "sha512_256" not in hashlib.algorithms_available:
        print("SHA-512/256 is unavailable in this Python build", file=sys.stderr)
        return 1
    valid_count, invalid_count = write(args.output)
    print(f"Wrote {valid_count} valid and {invalid_count} invalid vectors to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
