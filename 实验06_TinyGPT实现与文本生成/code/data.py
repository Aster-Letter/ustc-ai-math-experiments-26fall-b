"""已提供：先划分原文，再建训练词表，最后在各段内部取窗口。"""
import hashlib
import json
from pathlib import Path

import torch


def load_data(path):
    """读取已按整首诗划分的三个文件；仅训练集建立字符词表。

    Args:
        path (str or Path): 含 train.txt、val.txt、test.txt 的数据目录。

    Returns:
        tuple: 三段整数张量、词表列表、用于复现的数据说明。
    """
    parts = {}
    fingerprint = hashlib.sha256()
    for name in ["train", "val", "test"]:
        raw = (Path(path) / (name + ".txt")).read_bytes()
        fingerprint.update(name.encode("utf-8") + b"\0" + raw)
        parts[name] = raw.decode("utf-8")
    manifest = json.loads((Path(path) / "manifest.json").read_text(encoding="utf-8"))
    vocab = ["<unk>"] + sorted(set(parts["train"]))
    stoi = {char: index for index, char in enumerate(vocab)}
    splits = {}
    unknown = {}
    for name, part in parts.items():
        splits[name] = torch.tensor([stoi.get(char, 0) for char in part], dtype=torch.long)
        unknown[name] = int((splits[name] == 0).sum())
    info = {
        "sha256": fingerprint.hexdigest(),
        "characters": sum(len(part) for part in parts.values()),
        "poems": {name: item["poems"] for name, item in manifest["splits"].items()},
        "lengths": {name: len(part) for name, part in parts.items()},
        "unknown_counts": unknown, "vocab_size": len(vocab),
        "split_rule": manifest["split_rule"],
    }
    return splits, vocab, info


def get_batch(ids, batch_size, block_size, make_xy, device):
    """从同一个划分中抽取连续窗口。

    Args:
        ids (Tensor): 一维整数序列。
        batch_size (int): 每批样本数。
        block_size (int): 输入长度。
        make_xy (function): 学生完成的错位标签函数。
        device (str): cpu、cuda 或 mps。

    Returns:
        tuple: 输入、标签，均为 [B,T]。
    """
    starts = torch.randint(len(ids) - block_size, (batch_size,))
    inputs, targets = [], []
    for start in starts:
        x, y = make_xy(ids[start:start + block_size + 1])
        inputs.append(x)
        targets.append(y)
    return torch.stack(inputs).to(device), torch.stack(targets).to(device)


def decode(ids, vocab):
    """把编号序列还原为可读文本。

    Args:
        ids (list): 整数编号列表。
        vocab (list): 编号到字符的列表；0为未知字符。

    Returns:
        str: 解码文本，未知字符显示为替换符。
    """
    return "".join(vocab[index] if index else "�" for index in ids)
