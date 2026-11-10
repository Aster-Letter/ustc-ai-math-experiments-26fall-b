"""只检查本机解释器与依赖，不安装包、不登录平台。"""

import argparse
import importlib
import json
import platform
import sys
from importlib.metadata import version


def check_environment(require_rdkit=False):
    """导入基线必需依赖，显示可追溯的版本。

    Args:
        require_rdkit (bool): 高级方法或结构检查是否需要 RDKit。

    Returns:
        dict: Python、系统、架构与依赖版本。
    """
    result = dict(python=platform.python_version(), executable=sys.executable,
                  system=platform.system(), machine=platform.machine(), packages={})
    packages = ["numpy", "pandas", "pyarrow"] + (["rdkit"] if require_rdkit else [])
    for package in packages:
        importlib.import_module(package)
        result["packages"][package] = version(package)
    return result


def main():
    """打印环境检查结果。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-rdkit", action="store_true")
    args = parser.parse_args()
    print(json.dumps(check_environment(args.require_rdkit), indent=2))


if __name__ == "__main__":
    main()
