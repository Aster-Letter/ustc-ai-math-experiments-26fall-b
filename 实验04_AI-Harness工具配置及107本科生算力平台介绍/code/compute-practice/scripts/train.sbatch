#!/usr/bin/env bash
# Candidate single-GPU settings; duration and resource use have not been measured on the platform.
#SBATCH --job-name=compute-train
#SBATCH --partition=Students
#SBATCH --qos=qos_stu_default
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
set -euo pipefail
bash scripts/run-job.sh train
