"""整理明确指定的算法文件与小参考库，生成本地上传材料；不执行上传。"""

import argparse
import json
from pathlib import Path
import shutil
from submission.check_assets import create_manifest


def main():
    """每个实验使用新目录，避免旧文件混入上传材料。"""
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--reference")
    source.add_argument("--full-training", action="store_true",
                        help="B2：直接读取Kaggle官方全量训练集，仅打包独立运行代码")
    parser.add_argument("--out", required=True)
    parser.add_argument("--username", default="YOUR_USERNAME")
    parser.add_argument("--config", help="predict.py 记录的 config.json；只读取算法参数")
    parser.add_argument("--license", default="REVIEW_LICENSE_BEFORE_UPLOAD", help="核对来源条款后填写Kaggle接受的许可证标识")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = Path(args.out)
    assert not out.exists(), "请选择新的构建目录，避免覆盖旧版本。"
    if args.full_training:
        notebook = out / "notebook"
        notebook.mkdir(parents=True)
        shutil.copy2(root / "submission/kaggle/full_library.py", notebook / "main.py")
        kernel = json.loads((root / "submission/kaggle/kernel-metadata.example.json").read_text())
        kernel.update(id=args.username + "/casmi-b2-full-library", title="CASMI B2 Full Library",
                      dataset_sources=[])
        (notebook / "kernel-metadata.json").write_text(json.dumps(kernel, indent=2), encoding="utf-8")
        print("Prepared B2:", notebook, "(uses official train.parquet; no dataset upload)")
        return
    assets = out / "assets"
    notebook = out / "notebook"
    assets.mkdir(parents=True)
    notebook.mkdir()
    for folder in ["algorithms", "submission"]:
        selected = list((root / folder).glob("*.py")) if folder == "algorithms" else [root / folder / "__init__.py", root / folder / "check_submission.py", root / folder / "check_environment.py"]
        if folder == "algorithms":
            selected += list((root / "algorithms/baseline").glob("*.py"))
        for path in selected:
            target = assets / path.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    shutil.copy2(args.reference, assets / "reference.parquet")
    parameters = dict(bin_width=1.0, power=0.5, ppm=20.0, merge="max")
    if args.config:
        recorded = json.loads(Path(args.config).read_text(encoding="utf-8"))
        parameters = {key: recorded[key] for key in parameters}
    config = dict(course_assets_version=1, reference="reference.parquet", parameters=parameters)
    (assets / "course_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (assets / "README.md").write_text("# Course retrieval baseline\n\nReference spectra sampled from official competition training data.\nRecord sampling, source terms, team contributors and modifications before uploading.\n", encoding="utf-8")
    metadata = dict(title="CASMI Course Assets", id=args.username + "/casmi-course-assets", licenses=[dict(name=args.license)])
    (assets / "dataset-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    manifest = create_manifest(assets, "course code and user-selected reference; complete source records before upload")
    (assets / "assets_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    shutil.copy2(root / "submission/kaggle/main.py", notebook / "main.py")
    kernel = json.loads((root / "submission/kaggle/kernel-metadata.example.json").read_text())
    kernel["id"] = args.username + "/casmi-course-submit"
    kernel["dataset_sources"] = [args.username + "/casmi-course-assets"]
    (notebook / "kernel-metadata.json").write_text(json.dumps(kernel, indent=2), encoding="utf-8")
    print("Prepared:", out)
    print("Before upload: review username, licenses, source records, parameters, and team access.")


if __name__ == "__main__":
    main()
