"""创建或核对本地附件摘要；不会登录 Kaggle 或读取远端文件。"""

import argparse
import hashlib
import json
from pathlib import Path


def file_digest(path):
    """分块计算一个文件的内容摘要。

    Args:
        path (str or Path): 待检查文件。

    Returns:
        str: SHA-256 十六进制摘要。
    """
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def create_manifest(folder, source="local course assets"):
    """记录附件中推理文件的大小与摘要，排除会被编辑的发布元数据。

    Args:
        folder (str or Path): 仅放待检查附件的目录。
        source (str): 来源链接或版本说明。

    Returns:
        dict: 来源和相对路径对应的文件摘要。
    """
    folder = Path(folder)
    files = {}
    for path in sorted(folder.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path.name not in ["assets_manifest.json", "dataset-metadata.json", "README.md"]:
            files[path.relative_to(folder).as_posix()] = dict(bytes=path.stat().st_size, sha256=file_digest(path))
    return dict(source=source, files=files)


def main():
    """默认核对已有清单；--create 才创建新清单。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", required=True)
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--source", default="record the source and version here")
    args = parser.parse_args()
    folder = Path(args.folder)
    path = folder / "assets_manifest.json"
    if args.create:
        assert not path.exists(), "已有清单；核对差异后再明确另存或替换，避免覆盖原证据。"
        path.write_text(json.dumps(create_manifest(folder, args.source), indent=2), encoding="utf-8")
        print("manifest created:", path)
    else:
        saved = json.loads(path.read_text(encoding="utf-8"))
        actual = create_manifest(folder, saved["source"])
        assert saved["files"] == actual["files"], "文件内容或列表有变化。"
        print("assets verified:", len(actual["files"]), "files; remote version not checked")


if __name__ == "__main__":
    main()
