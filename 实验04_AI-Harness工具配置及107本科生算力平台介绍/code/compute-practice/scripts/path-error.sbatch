#!/usr/bin/env bash
# Explicitly labelled error demonstration; do not use this for a normal first run.
#SBATCH --job-name=compute-path-error
#SBATCH --partition=Students
#SBATCH --qos=qos_stu_default
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:05:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
set -euo pipefail
bash scripts/run-job.sh path-error
