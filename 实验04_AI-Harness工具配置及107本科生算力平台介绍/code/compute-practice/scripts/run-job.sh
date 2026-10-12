#!/usr/bin/env bash
set -euo pipefail
compute_profile=${1:-}
case "$compute_profile" in
    smoke|train|path-error) ;;
    *) echo 'Expected smoke, train or path-error' >&2; exit 2 ;;
esac
compute_project=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
compute_env_prefix=${COMPUTE_ENV_PREFIX:-"$HOME/.conda/envs/compute-resnet"}
compute_python="$compute_env_prefix/bin/python"
if [[ ! -x "$compute_python" ]]; then
    echo "Project Python not found: $compute_python" >&2
    echo 'Set COMPUTE_ENV_PREFIX to the verified environment prefix.' >&2
    exit 1
fi
cd -- "$compute_project"
compute_config=configs/smoke.json
[[ "$compute_profile" == train ]] && compute_config=configs/train.json
compute_data=data
if [[ "$compute_profile" == path-error ]]; then
    # Deliberately incorrect path, only for the explicitly labelled troubleshooting demo.
    compute_data=data-does-not-exist
    echo 'DEMONSTRATION: this job intentionally uses a missing data directory.'
fi
compute_run_id=${SLURM_JOB_ID:-"manual-$(date +%Y%m%d-%H%M%S)"}
printf 'project=%s\npython=%s\nconfig=%s\ndata=%s\n' "$compute_project" "$compute_python" "$compute_config" "$compute_data"
hostname
nvidia-smi
"$compute_python" -u train.py --config "$compute_config" --device cuda \
    --data-dir "$compute_data" --output "outputs/$compute_profile-$compute_run_id"
