"""检查解压后的宠物数据集；使用CPU，无需下载数据。"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image


SPLIT_FINGERPRINT = "37cee4018bbc0efe2e7652fdab3d5e0cecab3a4e62bb015eaea61530d4fa3770"


def check_pair(image_path, mask_path):
    """检查一张图片及其原始三值掩码。

    Args:
        image_path (Path): 图片路径。
        mask_path (Path): 掩码路径。

    Returns:
        str or None: 文件、尺寸或标注问题；符合要求时返回None。
    """
    for path in [image_path, mask_path]:
        if not path.is_file():
            return f"缺少文件：{path}"
    try:
        with Image.open(image_path) as image:
            image.load()
            image_size = image.size
        with Image.open(mask_path) as mask:
            mask.load()
            if image_size != mask.size:
                return f"图片与掩码尺寸不同：{image_path.name}"
            colors = mask.getcolors(maxcolors=256)
            if colors is None or not {value for count, value in colors} <= {1, 2, 3}:
                return f"掩码像素值应属于1、2、3：{mask_path.name}"
    except OSError as error:
        return f"文件无法读取：{image_path.name}；{error}"
    return None


def check_data(root):
    """检查数据目录、课程固定划分与全部图片掩码对。

    Args:
        root (str): 包含splits.json与oxford-iiit-pet的目录。

    Returns:
        bool: 全部检查通过时为True。
    """
    root = Path(root)
    folder = root / "oxford-iiit-pet"
    required = [root / "splits.json",
                folder / "annotations/trainval.txt",
                folder / "annotations/test.txt"]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        print("缺少文件：\n" + "\n".join(missing))
        print("--data-dir 指向包含 splits.json 的目录。")
        return False

    splits = json.loads((root / "splits.json").read_text(encoding="utf-8"))
    fingerprint = hashlib.sha256(json.dumps(splits, sort_keys=True).encode()).hexdigest()
    if fingerprint != SPLIT_FINGERPRINT:
        print("splits.json 与课程固定划分不同。")
        return False

    print("固定划分：", {key: len(splits[key]) for key in ["train", "val", "test"]})
    errors = []
    checked = 0
    for split in ["train", "val", "test"]:
        for name in splits[split]:
            error = check_pair(folder / "images" / (name + ".jpg"),
                               folder / "annotations/trimaps" / (name + ".png"))
            if error is not None:
                errors.append(error)
            checked += 1
        print(f"已检查 {split}：{len(splits[split])} 对")

    if errors:
        print(f"检测发现 {len(errors)} 对图片或掩码存在问题，前10项：")
        print("\n".join(errors[:10]))
        return False
    print(f"数据集检测通过：{checked} 对图片与掩码，尺寸一致，标注值属于1、2、3。")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data")
    args = parser.parse_args()
    success = check_data(args.data_dir)
    raise SystemExit(0 if success else 1)
