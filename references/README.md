# Declared-reference advisory audit

This consumer implements its part of
[shared issue #241](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/issues/241).
The adapter reads this repository's **current owning declarations** on every run;
it does not score the central inventory's older snapshot or change any pin.

`checker.json` pins the accepted shared checker by source commit and SHA-256.
The runner verifies the checkout HEAD and script bytes before execution. The
engine is not copied here. Schema, model, suite, carrier and historical copy
pins remain unchanged. A checker-code refresh is a separate reviewed change.

## Scope

The 35 published files come from the literal `PUBLISHED`, `SHARED_TAG` and
`SHARED_COMMIT` declarations in `scripts/check_development_tree.py`. The two
complete published directories, `examples/` and `jsonld/`, get source/local set
comparison; the remaining released schemas/contracts resolve at their named tag.
Existing development-tree classification remains required for root/owned paths.
Inherited same-repository fixtures and package/action/tool-code dependencies do
not become new cross-repository contract pins.

Every main push triggers this repository's existing JSON-LD Pages workflow.
Merging this concrete tooling PR therefore retains a separate publication gate.

## Local commands and evidence

```sh
python3 -m unittest discover -s tests -p test_reference_audit.py -v
python3 scripts/reference_audit.py --inventory-only
python3 scripts/reference_audit.py --checker-root /path/to/pinned/shared --checkout FAIR-bioHeaders/FAIR-bioHeaders-Specification=/path/to/pinned/shared --strict
python3 scripts/check_reference_audit_controls.py --checker-root /path/to/pinned/shared
```

The shared checkout must be at the exact checker commit and have all referenced
release tags/history available. Offline controls compare actual authority/local
bytes, then require a digest computed from deliberately different bytes to report
DRIFT and an unmapped query to report QUERY_FAILED. No fixture, pin or source file
is rewritten by these controls. PR checks run adapter/refusal tests and these
actual offline comparisons; they do not gate on live network state.

The scheduled/manual job checks authoritative tag/commit bytes over the GitHub
API with read-only permissions and retains the generated inventory and JSON
report. Its normal exit is advisory: inspect every FRESH/DRIFT/ABSENT/QUERY_FAILED
result and the explicit local/source-set coverage. An unusable declaration or
unverified checker refuses execution with exit 2. Failed queries are not missing
artifacts, and an unperformed comparison is not a pass. No auto-repin runs.

The checks establish fidelity to the declared revision, not adoption, latest-main
currency, biological validity or a new contract release. Other consumers still
need their own actual rollout before the federation-wide issue can close.
