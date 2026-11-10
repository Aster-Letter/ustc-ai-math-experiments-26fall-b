#!/usr/bin/env bash
set -euo pipefail
lab06_profile=${1:-}
case "$lab06_profile" in
    smoke|train|sample|evaluate) ;;
    *) echo 'Usage: bash scripts/submit.sh smoke|train|sample|evaluate [sbatch options]' >&2; exit 2 ;;
esac
shift
if [[ -n "${SLURM_JOB_ID:-}" ]]; then
    echo "Already inside a Slurm job. In the web job command, use: bash scripts/run-job.sh $lab06_profile" >&2
    exit 2
fi
export LAB06_PYTHON="/home/scc/pb24081512/anaconda3/envs/ustc-ai-experiments-26fall-B/bin/python"
: "${LAB06_PYTHON:?Set LAB06_PYTHON to the environment path from conda env list plus /bin/python}"
lab06_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd -- "$lab06_root"
mkdir -p logs outputs
sbatch --export=ALL --chdir="$lab06_root" "$@" scripts/job.sbatch "$lab06_profile"
