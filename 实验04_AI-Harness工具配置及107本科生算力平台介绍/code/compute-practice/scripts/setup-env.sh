#!/usr/bin/env bash
# Run on the platform after conda is available. Does not edit global source settings.
set -euo pipefail
compute_variant=${1:-}
compute_env_prefix=${2:-"$HOME/.conda/envs/compute-resnet"}
case "$compute_variant" in
    cpu|cu126|cu128) ;;
    *) echo 'Usage: bash scripts/setup-env.sh cpu|cu126|cu128 [new-environment-prefix]' >&2; exit 2 ;;
esac
compute_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
if ! command -v conda >/dev/null 2>&1; then
    echo 'conda not found. Complete the environment-manager step first.' >&2
    exit 1
fi
if [[ -e "$compute_env_prefix" ]]; then
    echo "Environment path already exists: $compute_env_prefix" >&2
    echo 'Reuse the verified environment, or choose a different new prefix.' >&2
    exit 1
fi
conda create --prefix "$compute_env_prefix" --override-channels \
    -c https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge python=3.11 pip -y
compute_python="$compute_env_prefix/bin/python"
"$compute_python" -m pip install torch==2.7.1 torchvision==0.22.1 \
    --index-url "https://download.pytorch.org/whl/$compute_variant"
"$compute_python" -m pip install -r "$compute_root/requirements.txt" \
    --index-url https://mirrors.ustc.edu.cn/pypi/web/simple
"$compute_python" -c 'import sys,torch,torchvision; print(sys.executable); print(torch.__version__,torchvision.__version__,torch.version.cuda)'
echo "Created: $compute_env_prefix"
echo 'This checks imports. GPU execution still needs a GPU allocation and a real training run.'
