#!/usr/bin/env bash
# 沿用实验04/05的候选资源；按107平台当前账号权限调整。
#SBATCH -A stu
#SBATCH --job-name=lab06-poetry
#SBATCH --partition=Students
#SBATCH --qos=qos_stu_default
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
set -euo pipefail
bash scripts/run-job.sh "$1"
