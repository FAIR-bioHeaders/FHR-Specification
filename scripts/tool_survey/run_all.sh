#!/usr/bin/env bash
# Regenerate inputs and rerun the FHR tool-compatibility survey.
#
#   scripts/tool_survey/run_all.sh WORKDIR
#
# Expects on PATH: the survey and survey-graph environment bin directories
# (environment.yml, environment-graph.yml) and the fhr-* converter CLIs
# (FHR-File-Converter 0.3.3). Set SURVEY_NODE_DIR to a directory where
# `npm install` was run with package.json from this directory to include the
# JBrowse tests; otherwise they are reported as n/a or c.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
work=${1:?usage: run_all.sh WORKDIR}
mkdir -p "$work"
python3 "$here/make_inputs.py" "$work/inputs" --fhr-bin "$(dirname "$(command -v fhr-fasta-combine)")"
python3 "$here/run_survey.py" "$work/inputs" "$work/results" --node-dir "${SURVEY_NODE_DIR:-}"
echo "results: $work/results/results.tsv"
