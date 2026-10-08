"""Check the FHR conformance vectors against their manifest.

Without options this needs only the Python standard library: it regenerates the
vectors in a temporary directory and compares bytes, and recomputes each valid
vector's SHA-512/256 checksum with its own reading of docs/FORMAT.md.
``--schema`` also validates valid vectors' metadata against fhr.json (needs
PyYAML and jsonschema). ``--converter`` runs fhr-fasta-validate/fhr-gfa-validate
on every vector: valid vectors must exit 0 and invalid vectors nonzero.
"""

import argparse
import base64
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "make_conformance.py"
PREFIXES = {"fasta": b";~", "gfa": b"#~"}
PLACEHOLDER_CHECKSUMS = {"A" * 43 + "="}
COMMANDS = {"fasta": "fhr-fasta-validate", "gfa": "fhr-gfa-validate"}


def generated_files(directory):
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob("*"))
        if path.is_file() and (path.name == "manifest.json" or path.parent.name in {"valid", "invalid"})
    }


def check_up_to_date(conformance):
    """Regenerate the vectors and report files whose bytes differ."""
    with tempfile.TemporaryDirectory() as temporary:
        result = subprocess.run(
            [sys.executable, str(GENERATOR), "--output", temporary],
            capture_output=True, text=True,
        )
        if result.returncode:
            return [f"generator failed: {result.stderr.strip()}"]
        expected = generated_files(Path(temporary))
    actual = generated_files(conformance)
    problems = [f"{name}: missing" for name in sorted(expected.keys() - actual.keys())]
    problems += [f"{name}: not produced by the generator" for name in sorted(actual.keys() - expected.keys())]
    problems += [
        f"{name}: differs from the generator output"
        for name in sorted(expected.keys() & actual.keys()) if expected[name] != actual[name]
    ]
    return problems


def split_lines(data):
    """Yield (start, end) offsets of lines ending in LF, CRLF, CR or end of data."""
    start, size = 0, len(data)
    while start < size:
        end = start
        while end < size and data[end] not in (10, 13):
            end += 1
        if end < size:
            end += 2 if data[end] == 13 and data[end + 1:end + 2] == b"\n" else 1
        yield start, end
        start = end


def fhr_checksum(data, kind):
    """Return (value on the checksum line, computed checksum) for decompressed bytes."""
    prefix = PREFIXES[kind]
    fhr_lines = []
    block = True
    for start, end in split_lines(data):
        line = data[start:end]
        if block and (line[:1] == b">" if kind == "fasta" else line[:1] != b"#" and line.strip()):
            block = False
        if line.startswith(prefix):
            if not block:
                raise ValueError("FHR line after the leading header block")
            fhr_lines.append((start, end, line[len(prefix):].rstrip(b"\r\n")))
    content = [text for _, _, text in fhr_lines if text.strip() and text.lstrip()[:1] != b"#"]
    if not content:
        raise ValueError("no FHR metadata")
    root = min(len(text) - len(text.lstrip(b" \t")) for text in content)
    candidates = []
    for start, end, text in fhr_lines:
        found = re.fullmatch(rb"([ \t]*)checksum[ \t]*:(.*)", text, re.S)
        if found and len(found.group(1)) == root:
            candidates.append((start, end, found.group(2)))
    if len(candidates) != 1:
        raise ValueError(f"{len(candidates)} root-level checksum lines")
    start, end, value = candidates[0]
    value = value.strip().decode("utf-8")
    if len(value) > 1 and value[0] == value[-1] and value[0] in "'\"":
        value = value[1:-1]
    sha = hashlib.new("sha512_256")
    sha.update(data[:start])
    sha.update(data[end:])
    return value, base64.b64encode(sha.digest()).decode("ascii")


def read_vector(conformance, vector):
    data = (conformance / vector["file"]).read_bytes()
    if vector["compressed"]:
        if not data.startswith(b"\x1f\x8b"):
            raise ValueError("compressed vector lacks the gzip magic bytes")
        data = gzip.decompress(data)  # Reads every gzip/BGZF member.
    return data


def check_checksums(conformance, manifest):
    problems = []
    for vector in manifest["vectors"]:
        name = vector["id"]
        try:
            data = read_vector(conformance, vector)
        except (OSError, ValueError, EOFError) as error:
            problems.append(f"{name}: {error}")
            continue
        try:
            stated, computed = fhr_checksum(data, vector["format"])
        except (ValueError, UnicodeDecodeError) as error:
            if vector["expected"] == "valid":
                problems.append(f"{name}: {error}")
            continue
        if vector["expected"] == "valid":
            if vector["checksum"] in PLACEHOLDER_CHECKSUMS:
                problems.append(f"{name}: placeholder checksum")
            if not stated == computed == vector["checksum"]:
                problems.append(
                    f"{name}: manifest {vector['checksum']}, line {stated}, computed {computed}"
                )
        elif vector["rule"] in {"R1", "R3", "R4"} and stated == computed:
            problems.append(f"{name}: expected a checksum mismatch")
    return problems


def check_manifest(manifest):
    problems = []
    format_rules = set(re.findall(r"\[(R\d+)\]", (ROOT / "docs/FORMAT.md").read_text()))
    if format_rules != set(manifest["rules"]):
        problems.append(f"docs/FORMAT.md rule ids {sorted(format_rules)} differ from the manifest")
    coverage = {rule: set() for rule in manifest["rules"]}
    for vector in manifest["vectors"]:
        rules = vector["rules"] if vector["expected"] == "valid" else [vector["rule"]]
        for rule in rules:
            if rule not in coverage:
                problems.append(f"{vector['id']}: unknown rule {rule}")
                continue
            coverage[rule].add(vector["expected"])
    for rule, outcomes in coverage.items():
        if "notApplicable" not in manifest["rules"][rule] and outcomes != {"valid", "invalid"}:
            problems.append(f"{rule}: needs at least one valid and one invalid vector")
    return problems


def check_schema(conformance, manifest):
    """Validate the metadata of valid vectors against fhr.json."""
    from jsonschema import Draft202012Validator, FormatChecker
    import yaml

    validator = Draft202012Validator(
        json.loads((ROOT / "fhr.json").read_text()), format_checker=FormatChecker()
    )
    problems = []
    for vector in manifest["vectors"]:
        if vector["expected"] != "valid":
            continue
        prefix = PREFIXES[vector["format"]]
        data = read_vector(conformance, vector)
        text = "\n".join(
            line[len(prefix):].rstrip(b"\r\n").decode("utf-8")
            for line in data.splitlines(keepends=True) if line.startswith(prefix)
        )
        metadata = yaml.safe_load(text)
        for error in validator.iter_errors(metadata):
            problems.append(f"{vector['id']}: {error.json_path}: {error.message}")
        for key, value in vector["metadata"].items():
            if metadata.get(key) != value:
                problems.append(f"{vector['id']}: {key} is {metadata.get(key)!r}, expected {value!r}")
        if metadata.get("checksum") != vector["checksum"]:
            problems.append(f"{vector['id']}: parsed checksum differs from the manifest")
        if "seqcol_id" in metadata:
            problems.append(f"{vector['id']}: valid vectors must not carry a SeqCol placeholder")
    return problems


def converter_commands(location):
    """Return a function mapping a format to the command list that validates it."""
    if location == "PATH":
        found = {kind: shutil.which(name) for kind, name in COMMANDS.items()}
        if not all(found.values()):
            raise ValueError("fhr-fasta-validate/fhr-gfa-validate are not on PATH")
        return lambda kind: [found[kind]]
    path = Path(location)
    if (path / "fhr" / "cli.py").is_file():  # A converter source checkout.
        def from_checkout(kind):
            code = (f"import sys; sys.path.insert(0, {str(path.resolve())!r}); "
                    f"sys.argv[0] = {COMMANDS[kind]!r}; "
                    f"from fhr.cli import {kind}_validate_main as main; sys.exit(main())")
            return [sys.executable, "-c", code]
        return from_checkout
    for directory in (path, path / "bin", path / "Scripts"):
        found = {kind: shutil.which(name, path=str(directory)) for kind, name in COMMANDS.items()}
        if all(found.values()):
            return lambda kind: [found[kind]]
    raise ValueError(f"{location}: no converter checkout, environment or bin directory")


def check_converter(conformance, manifest, location):
    command = converter_commands(location)
    problems = []
    for vector in manifest["vectors"]:
        result = subprocess.run(
            command(vector["format"]) + [str(conformance / vector["file"])],
            capture_output=True, text=True, timeout=120, cwd=tempfile.gettempdir(),
            env={**os.environ, "PYTHONSAFEPATH": "1"},
        )
        accepted = result.returncode == 0
        if accepted != (vector["expected"] == "valid"):
            detail = (result.stderr or result.stdout).strip().splitlines()
            detail = detail[-1] if detail else f"exit {result.returncode}"
            outcome = "accepted" if accepted else f"rejected ({detail})"
            expected = vector["expected"] + (f", {vector['rule']}" if "rule" in vector else "")
            problems.append(f"{vector['id']}: converter {outcome}; expected {expected}")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--conformance", type=Path, default=ROOT / "conformance",
                        help="vector directory (default: conformance/)")
    parser.add_argument("--schema", action="store_true",
                        help="validate valid vectors' metadata against fhr.json (needs PyYAML, jsonschema)")
    parser.add_argument("--converter", nargs="?", const="PATH", metavar="LOCATION",
                        help="run the converter CLI: a converter checkout, a virtual environment "
                             "or bin directory, or PATH (the default when no value is given)")
    parser.add_argument("--skip-regeneration", action="store_true",
                        help="do not compare the vectors with freshly generated ones")
    args = parser.parse_args()
    conformance = args.conformance.resolve()
    manifest = json.loads((conformance / "manifest.json").read_text())

    steps = []
    if not args.skip_regeneration:
        steps.append(("vectors match the generator", lambda: check_up_to_date(conformance)))
    steps.append(("manifest covers the docs/FORMAT.md rules", lambda: check_manifest(manifest)))
    steps.append(("checksums recomputed independently", lambda: check_checksums(conformance, manifest)))
    if args.schema:
        steps.append(("valid metadata matches fhr.json", lambda: check_schema(conformance, manifest)))
    if args.converter:
        steps.append((f"converter ({args.converter}) agrees with the manifest",
                      lambda: check_converter(conformance, manifest, args.converter)))

    failed = False
    for label, step in steps:
        try:
            problems = step()
        except ValueError as error:
            problems = [str(error)]
        for problem in problems:
            print(f"{label}: {problem}", file=sys.stderr)
        failed |= bool(problems)
        print(f"{'FAIL' if problems else 'ok'}: {label}", flush=True)
    count = len(manifest["vectors"])
    print(f"{count} vectors {'failed' if failed else 'passed'}")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
