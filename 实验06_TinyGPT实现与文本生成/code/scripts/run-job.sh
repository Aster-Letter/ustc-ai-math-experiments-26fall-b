#!/usr/bin/env bash
set -euo pipefail
: "${SLURM_JOB_ID:?Run this script inside a 107 Slurm job, submitted through the web form or submit.sh}"
lab06_profile=$1
lab06_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd -- "$lab06_root"
LAB06_PYTHON=${LAB06_PYTHON:-"/home/scc/pb24081512/anaconda3/envs/ustc-ai-experiments-26fall-B"}
if [[ ! -x "$LAB06_PYTHON" ]]; then
    echo "Python interpreter is not executable: $LAB06_PYTHON" >&2
    exit 2
fi
lab06_python=$LAB06_PYTHON
lab06_data=${LAB06_DATA_DIR:-"$lab06_root/data"}
lab06_output="$lab06_root/outputs/$lab06_profile-$SLURM_JOB_ID"
printf 'job=%s\npython=%s\ndata=%s\noutput=%s\n' "$SLURM_JOB_ID" "$lab06_python" "$lab06_data" "$lab06_output"
hostname
nvidia-smi
"$lab06_python" -c 'import torch; print(torch.__version__); assert torch.cuda.is_available(), "CUDA unavailable"; print(torch.cuda.get_device_name(0))'
case "$lab06_profile" in
    smoke|train)
        lab06_steps=${LAB06_STEPS:-3000}
        lab06_eval_every=300
        if [[ "$lab06_profile" == smoke ]]; then
            lab06_steps=20
            lab06_eval_every=20
        fi
        "$lab06_python" -u train.py --device cuda --data "$lab06_data" --output "$lab06_output" \
            --steps "$lab06_steps" --eval-every "$lab06_eval_every" --threads "${SLURM_CPUS_PER_TASK:-4}" \
            --batch-size "${LAB06_BATCH_SIZE:-64}" --width "${LAB06_WIDTH:-128}" \
            --layers "${LAB06_LAYERS:-2}" --block-size "${LAB06_BLOCK_SIZE:-32}" \
            --lr "${LAB06_LR:-0.0003}" --seed "${LAB06_SEED:-2026}"
        ;;
    sample|evaluate)
        lab06_checkpoint="$LAB06_RUN/best.pt"
        mkdir -p "$lab06_output"
        if [[ "$lab06_profile" == sample ]]; then
            for lab06_temp in 0.8 1.0 1.2; do
                "$lab06_python" -u "$LAB06_RUN/source/sample.py" --device cuda \
                    --checkpoint "$lab06_checkpoint" --prompt "${LAB06_PROMPT:-春}" \
                    --seed "${LAB06_SEED:-2026}" --temperature "$lab06_temp" \
                    --output "$lab06_output/temperature-$lab06_temp.txt"
            done
            "$lab06_python" -u "$LAB06_RUN/source/sample.py" --device cuda \
                --checkpoint "$lab06_checkpoint" --prompt "${LAB06_PROMPT:-春}" --greedy \
                --seed "${LAB06_SEED:-2026}" --output "$lab06_output/greedy.txt"
        else
            "$lab06_python" -u "$LAB06_RUN/source/evaluate.py" --device cuda \
                --checkpoint "$lab06_checkpoint" --data "$lab06_data" --output "$lab06_output/test_metrics.json"
        fi
        ;;
esac
