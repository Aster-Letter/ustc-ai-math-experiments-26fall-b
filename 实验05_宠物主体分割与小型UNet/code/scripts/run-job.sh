#!/usr/bin/env bash
set -euo pipefail
lab05_profile=$1
lab05_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd -- "$lab05_root"
# 显式指定环境解释器，避免批处理误用登录节点的系统Python。
lab05_python=${LAB05_PYTHON:-"${COMPUTE_ENV_PREFIX:-$HOME/.conda/envs/compute-resnet}/bin/python"}
lab05_data=${LAB05_DATA_DIR:-data}
lab05_run_id=${SLURM_JOB_ID:-"manual-$(date +%Y%m%d-%H%M%S)"}
lab05_output="outputs/$lab05_profile-$lab05_run_id"
printf 'project=%s\npython=%s\ndata=%s\noutput=%s\n' "$lab05_root" "$lab05_python" "$lab05_data" "$lab05_output"
hostname
nvidia-smi
case "$lab05_profile" in
    smoke)
        "$lab05_python" -u train.py --model demo --synthetic --device cuda \
            --epochs 1 --limit-train 16 --limit-val 8 --output "$lab05_output"
        ;;
    basic|improved)
        "$lab05_python" -u checks.py "$lab05_profile"
        "$lab05_python" -u train.py --model "$lab05_profile" --device cuda \
            --data-dir "$lab05_data" --output "$lab05_output" \
            --epochs "${LAB05_EPOCHS:-20}" --batch-size "${LAB05_BATCH_SIZE:-16}" \
            --lr "${LAB05_LR:-0.001}" --seed "${LAB05_SEED:-42}"
        ;;
    evaluate)
        : "${LAB05_CHECKPOINT:?Set LAB05_CHECKPOINT to the selected run/best.pt}"
        lab05_snapshot=$(dirname -- "$LAB05_CHECKPOINT")/source/evaluate.py
        "$lab05_python" -u "$lab05_snapshot" --checkpoint "$LAB05_CHECKPOINT" \
            --data-dir "$lab05_data" --device cuda --split test --output "$lab05_output"
        ;;
    *) echo "Unknown profile: $lab05_profile" >&2; exit 2 ;;
esac
