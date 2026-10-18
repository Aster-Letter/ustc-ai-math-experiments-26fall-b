"""联网机器上运行一次；平台训练期间不下载数据。"""
import argparse
import json
from pathlib import Path
from torchvision.datasets import OxfordIIITPet
from data import make_splits


def prepare(root, download):
    """准备官方数据并写出固定划分。

    Args:
        root (str): 数据目录。
        download (bool): 是否允许首次联网下载。
    """
    OxfordIIITPet(root, split="trainval", target_types="segmentation", download=download)
    splits = make_splits(root)
    groups = [set(splits[key]) for key in ["train", "val", "test"]]
    assert not (groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2])
    folder = Path(root) / "oxford-iiit-pet"
    for names in groups:
        for name in names:
            assert (folder / "images" / (name + ".jpg")).is_file(), name
            assert (folder / "annotations" / "trimaps" / (name + ".png")).is_file(), name
    (Path(root) / "splits.json").write_text(json.dumps(splits, indent=2), encoding="utf-8")
    print({key: len(splits[key]) for key in ["train", "val", "test"]})
    print("Saved fixed split: seed=2026; test is the official test list.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    prepare(args.data_dir, args.download)
