#!/usr/bin/env bash
# Submit from a known project root; the log directory must exist before Slurm opens it.
set -euo pipefail
compute_profile=${1:-}
case "$compute_profile" in
    smoke|train|path-error) ;;
    *) echo 'Usage: bash scripts/submit.sh smoke|train|path-error [sbatch options]' >&2; exit 2 ;;
esac
shift
compute_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd -- "$compute_root"
mkdir -p logs outputs
if ! command -v sbatch >/dev/null 2>&1; then
    echo 'sbatch not found. Run this in the platform submission terminal.' >&2
    exit 1
fi
sbatch --chdir="$compute_root" "$@" "scripts/$compute_profile.sbatch"
