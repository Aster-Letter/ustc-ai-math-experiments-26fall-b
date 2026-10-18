"""已提供：官方划分、成对空间变换与小型合成数据。"""
import hashlib
import json
import random
from pathlib import Path
import numpy as np
import torch
from PIL import Image, ImageOps
from torch.utils.data import Dataset


def make_splits(root):
    """从官方名单生成固定的、按品种分层的训练和验证划分。

    Args:
        root (str): 包含 oxford-iiit-pet 的数据目录。

    Returns:
        dict: train、val、test 图片名称列表及划分种子。
    """
    folder = Path(root) / "oxford-iiit-pet" / "annotations"
    groups = {}
    for line in (folder / "trainval.txt").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        name, category, *rest = line.split()
        groups.setdefault(int(category), []).append(name)
    rng = random.Random(2026)
    splits = {"train": [], "val": [], "test": [], "split_seed": 2026}
    for category in sorted(groups):
        names = sorted(groups[category])
        rng.shuffle(names)
        cut = int(0.8 * len(names))
        splits["train"].extend(names[:cut])
        splits["val"].extend(names[cut:])
    for line in (folder / "test.txt").read_text().splitlines():
        if line and not line.startswith("#"):
            splits["test"].append(line.split()[0])
    for key in ["train", "val", "test"]:
        splits[key].sort()
    return splits


def read_manifest(root):
    """读取准备数据时生成的固定名单。

    Args:
        root (str): 数据目录。

    Returns:
        tuple: 划分字典、该字典的 SHA-256 指纹字符串。
    """
    splits = json.loads((Path(root) / "splits.json").read_text())
    canonical = json.dumps(splits, sort_keys=True).encode()
    return splits, hashlib.sha256(canonical).hexdigest()


def convert_trimap(mask):
    """把官方三值标注转为目标和有效区域。

    Args:
        mask (PIL.Image): 原始标注，1=宠物、2=背景、3=不确定边界。

    Returns:
        tuple: [1,H,W] 的浮点目标和有效区域掩码。
    """
    values = torch.from_numpy(np.array(mask, dtype=np.int64))
    target = (values == 1).float().unsqueeze(0)
    valid = (values != 3).float().unsqueeze(0)
    return target, valid


class PetDataset(Dataset):
    """按固定名单读取图片和标注，训练时可同步水平翻转。"""

    def __init__(self, root, names, size=128, augment=False):
        """保存数据位置和变换选项。

        Args:
            root (str): 数据目录。
            names (list): 无扩展名的图片名称。
            size (int): 统一的正方形边长。
            augment (bool): 是否对训练样本同步随机水平翻转。
        """
        self.folder = Path(root) / "oxford-iiit-pet"
        self.names = names
        self.size = size
        self.augment = augment

    def __len__(self):
        """返回图片数量。"""
        return len(self.names)

    def __getitem__(self, index):
        """读取一对图片和掩码；变换不会把边界类别插值成其他类别。

        Args:
            index (int): 当前数据集中的位置。

        Returns:
            tuple: image、target、valid、name。
        """
        name = self.names[index]
        with Image.open(self.folder / "images" / (name + ".jpg")) as source:
            image = source.convert("RGB")
        with Image.open(self.folder / "annotations" / "trimaps" / (name + ".png")) as source:
            mask = source.copy()
        image = image.resize((self.size, self.size), Image.Resampling.BILINEAR)
        mask = mask.resize((self.size, self.size), Image.Resampling.NEAREST)
        if self.augment and torch.rand(()) < 0.5:
            image, mask = ImageOps.mirror(image), ImageOps.mirror(mask)
        image = torch.from_numpy(np.array(image)).permute(2, 0, 1).float() / 255
        target, valid = convert_trimap(mask)
        return image, target, valid, name


class SyntheticPets(Dataset):
    """彩色圆形合成数据，仅验证流程，不能代表宠物分割效果。"""

    def __init__(self, split, size=128):
        """给不同划分分配不同随机种子。

        Args:
            split (str): train、val 或 test。
            size (int): 图片边长。
        """
        self.size = size
        self.split = split
        self.offset = {"train": 1000, "val": 2000, "test": 3000}[split]

    def __len__(self):
        """返回32张合成图片。"""
        return 32

    def __getitem__(self, index):
        """返回可重复生成的图片与圆形前景。

        Args:
            index (int): 样本位置。

        Returns:
            tuple: 与 PetDataset 相同格式的数据。
        """
        generator = torch.Generator().manual_seed(self.offset + index)
        yy, xx = torch.meshgrid(torch.arange(self.size), torch.arange(self.size), indexing="ij")
        center = torch.randint(self.size//3, 2*self.size//3, (2,), generator=generator)
        radius = self.size//4
        distance = ((xx-center[0])**2 + (yy-center[1])**2).float().sqrt()
        target = (distance < radius).float().unsqueeze(0)
        valid = ((distance-radius).abs() > 2).float().unsqueeze(0)
        image = torch.rand(3, self.size, self.size, generator=generator)*0.2
        image[0] += 0.7*target[0]
        return image, target, valid, f"synthetic_{self.split}_{index}"
