#!/usr/bin/env bash
set -euo pipefail
lab05_profile=${1:-}
case "$lab05_profile" in
    smoke|basic|improved|evaluate) ;;
    *) echo 'Usage: bash scripts/submit.sh smoke|basic|improved|evaluate [sbatch options]' >&2; exit 2 ;;
esac
shift
lab05_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd -- "$lab05_root"
mkdir -p logs outputs
sbatch --export=ALL --chdir="$lab05_root" "$@" scripts/job.sbatch "$lab05_profile"
