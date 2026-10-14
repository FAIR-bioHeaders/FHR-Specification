"""Render a compact, portable SVG field overview from the published schema."""

from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render(schema):
    required = schema["required"]
    optional = [key for key in schema["properties"] if key not in required]
    height = 170 + max(len(required), len(optional)) * 38 + 240
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}">',
        "<title>FHR metadata field overview</title>",
        "<desc>Required and optional fields in the FHR v0.3 schema. See fhr.json for full validation constraints.</desc>",
        '<rect width="1200" height="100%" fill="#f8fafc"/>',
        '<g font-family="sans-serif" fill="#0f172a">',
        '<text x="40" y="50" font-size="28">FHR v0.3 metadata — schemaVersion 1</text>',
        '<text x="40" y="85" font-size="17">JSON/YAML · FASTA ;~ · GFA #~ · HTML microdata</text>',
    ]
    for x, heading, keys in [(40, "Required", required), (620, "Optional", optional)]:
        parts.append(
            f'<text x="{x}" y="130" font-size="22" font-weight="bold">{heading}</text>'
        )
        for i, key in enumerate(keys):
            node = schema["properties"][key]
            kind = node.get(
                "type",
                (
                    schema["definitions"][node["$ref"].split("/")[-1]]["type"]
                    if "$ref" in node
                    else "string or object array"
                ),
            )
            parts.append(
                f'<text x="{x}" y="{170+i*38}" font-size="18">{escape(key)}: {escape(kind)}</text>'
            )
    y = height - 185
    for i, line in enumerate(
        [
            "assemblySoftware objects: name (required), uri, version, commandLineOption[]",
            "vitalStats: contig N50, L50, N90, L90; scaffoldN50, scaffoldL50, scaffoldN90, scaffoldL90; totalBasePairs,",
            "numberContigs, numberScaffolds, gcContent, readTechnology · nested objects reject unknown keys",
            "N50/N90: base pairs · gcContent: 0–100 percent · seqcol_id: supplied 32-character base64url digest",
            "checksum: exact-byte SHA-512/256 including metadata and sequence, except its checksum line",
            "This overview is generated from fhr.json; the JSON Schema defines the full contract.",
        ]
    ):
        parts.append(f'<text x="40" y="{y+i*30}" font-size="15">{escape(line)}</text>')
    return "\n".join(parts + ["</g>", "</svg>"]) + "\n"


if __name__ == "__main__":
    (ROOT / "Diagram.svg").write_text(
        render(json.loads((ROOT / "fhr.json").read_text())), encoding="utf-8"
    )
