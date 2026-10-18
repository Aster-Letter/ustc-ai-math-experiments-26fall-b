#!/usr/bin/env bash
# 沿用实验04的候选设置；以107平台当前账号权限为准，尚未实测时长。
#SBATCH --job-name=lab05-pets
#SBATCH --partition=Students
#SBATCH --qos=qos_stu_default
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
set -euo pipefail
bash scripts/run-job.sh "$1"
