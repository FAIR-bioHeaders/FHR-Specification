#!/usr/bin/env python3
"""Fingerprint tool outputs so header and control runs can be compared.

fp.py fasta FILE   -> name<TAB>length<TAB>md5(upper sequence) per record
fp.py sam FILE     -> @SQ name/length + read/ref/pos/cigar per mapped read
fp.py text FILE    -> md5 of FILE with FHR header lines (;~ / #~) removed
fp.py gfa FILE     -> sorted S/L/P lines (segment names as given)

FHR header lines (';~', '#~') before the first record are not data; inside a
FASTA record they are counted as sequence. The number found in
the output is reported on the first line as 'fhr-header-lines-in-output: N' so
"header passed through" is visible separately from "data changed".
"""
import gzip
import hashlib
import sys


def lines(path):
    with open(path, "rb") as f:
        op = gzip.open if f.read(2) == b"\x1f\x8b" else open
    with op(path, "rb") as f:
        for raw in f:
            yield raw.decode("utf-8", "replace").rstrip("\r\n")


def is_hdr(line):
    return line.startswith((";~", "#~"))


def main():
    mode, path = sys.argv[1], sys.argv[2]
    try:
        ls = list(lines(path))
    except FileNotFoundError:
        print("missing-output")
        return
    nh = sum(1 for x in ls if is_hdr(x))
    # FASTA keeps every line so that ';' text inside a record is visible.
    body = ls if mode == "fasta" else [x for x in ls if not is_hdr(x)]
    print(f"fhr-header-lines-in-output: {nh}")
    if mode == "fasta":
        name, seq = None, []
        def emit():
            if name is not None:
                s = "".join(seq).upper()
                print(f"{name}\t{len(s)}\t{hashlib.md5(s.encode()).hexdigest()}")
        for x in body:
            if x.startswith(">"):
                emit(); name, seq = x[1:].split()[0] if x[1:].split() else "", []
            elif name is None and x.startswith(";"):
                continue  # leading comment block: not data
            else:
                # Inside a record every line counts, as it would for a naive
                # reader, so absorbed header text shows up as a change.
                if name is None:
                    name = "<before-first-record>"
                seq.append(x.strip())
        emit()
    elif mode == "sam":
        for x in body:
            f = x.split("\t")
            if x.startswith("@SQ"):
                print("\t".join(t for t in f if t[:3] in ("SN:", "LN:", "M5:")))
            elif not x.startswith("@") and len(f) > 5 and f[2] != "*":
                print(f[0], f[2], f[3], f[5])
    elif mode == "gfa":
        print("\n".join(sorted(x for x in body if x[:1] in ("S", "L", "P"))))
    elif mode == "text":
        print(hashlib.md5("\n".join(body).encode()).hexdigest())
    else:
        sys.exit("unknown mode")


if __name__ == "__main__":
    main()
