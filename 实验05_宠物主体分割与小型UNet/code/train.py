"""完整训练入口：只使用训练与验证集，不读取测试图片。"""
import argparse
import csv
import json
import os
import platform
import random
import shutil
import time
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader, Subset
from data import PetDataset, SyntheticPets, read_manifest
from metrics import masked_loss, foreground_scores
from models import build_model
from visuals import save_curves, save_examples


def evaluate_loader(model, loader, device):
    """按图片数加权汇总指标，不对大小不同的批次直接平均。

    Args:
        model (nn.Module): 分割网络。
        loader (DataLoader): 验证或测试数据。
        device (str): 计算设备。

    Returns:
        tuple: 平均指标字典，以及每张图片的指标记录。
    """
    model.eval()
    total_loss, count = 0., 0
    rows = []
    with torch.no_grad():
        for images, targets, valid, names in loader:
            images, targets, valid = images.to(device), targets.to(device), valid.to(device)
            logits = model(images)
            total_loss += masked_loss(logits, targets, valid).item()*len(images)
            ious, dices = foreground_scores(logits, targets, valid)
            for name, iou, dice in zip(names, ious.cpu().tolist(), dices.cpu().tolist()):
                rows.append({"image": name, "iou": iou, "dice": dice})
            count += len(images)
    metrics = {"loss": total_loss/count,
               "iou": sum(row["iou"] for row in rows)/count,
               "dice": sum(row["dice"] for row in rows)/count, "count": count}
    return metrics, rows


def make_parser():
    """创建训练命令行选项。

    Returns:
        ArgumentParser: 学生与教师入口共用的参数解析器。
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["demo", "basic", "improved"], default="basic")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--output", default="outputs/basic-01")
    parser.add_argument("--device", choices=["cpu", "cuda", "mps"], default="cuda")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--size", type=int, default=128)
    parser.add_argument("--augment", action="store_true")
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--limit-train", type=int, default=0)
    parser.add_argument("--limit-val", type=int, default=0)
    return parser


def run_training(args, model=None):
    """完成训练、验证选择与保存；可由教师传入参考模型。

    Args:
        args (Namespace): 命令行参数。
        model (nn.Module or None): None时构建学生模型。

    Returns:
        dict: 运行元数据和最佳验证分数。
    """
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(2)
    if args.device == "cuda":
        assert torch.cuda.is_available(), "No CUDA device: submit a GPU job and check the PyTorch environment."
        torch.cuda.manual_seed_all(args.seed)
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True
    output = Path(args.output)
    # 不覆盖上一次对比实验。换 --output 即可开始新实验。
    output.mkdir(parents=True, exist_ok=False)
    source = output / "source"
    source.mkdir()
    for path in Path(__file__).parent.glob("*.py"):
        shutil.copy2(path, source / path.name)
    if args.synthetic:
        train = SyntheticPets("train", args.size)
        val = SyntheticPets("val", args.size)
        fingerprint = "synthetic-v1"
    else:
        splits, fingerprint = read_manifest(args.data_dir)
        train = PetDataset(args.data_dir, splits["train"], args.size, args.augment)
        val = PetDataset(args.data_dir, splits["val"], args.size)
        shutil.copy2(Path(args.data_dir) / "splits.json", output / "splits.json")
    if args.limit_train:
        train = Subset(train, range(min(args.limit_train, len(train))))
    if args.limit_val:
        val = Subset(val, range(min(args.limit_val, len(val))))
    generator = torch.Generator().manual_seed(args.seed)
    train_loader = DataLoader(train, batch_size=args.batch_size, shuffle=True,
                              generator=generator, num_workers=args.workers)
    val_loader = DataLoader(val, batch_size=args.batch_size, num_workers=args.workers)
    if model is None:
        model = build_model(args.model)
    model = model.to(args.device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    metadata = {"config": vars(args), "data_kind": "synthetic_smoke_only" if args.synthetic else "Oxford-IIIT Pet",
                "split_fingerprint": fingerprint, "train_n": len(train), "val_n": len(val),
                "parameters": sum(p.numel() for p in model.parameters()),
                "torch": str(torch.__version__), "python": platform.python_version(),
                "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
                "device": args.device, "gpu": torch.cuda.get_device_name() if args.device == "cuda" else None,
                "partial_run": bool(args.synthetic or args.limit_train or args.limit_val),
                "metric_protocol": "128-default; per-image foreground; ignore trimap=3; probability>=0.5; empty=1"}
    (output / "run.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2), flush=True)
    history, best_iou = [], -1.
    start = time.perf_counter()
    for epoch in range(1, args.epochs+1):
        model.train()  # BN 在此使用当前批次统计量。
        total_loss, count = 0., 0
        for images, targets, valid, names in train_loader:
            images, targets, valid = images.to(args.device), targets.to(args.device), valid.to(args.device)
            optimizer.zero_grad()
            logits = model(images)
            loss = masked_loss(logits, targets, valid)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()*len(images)
            count += len(images)
        scores, rows = evaluate_loader(model, val_loader, args.device)
        record = {"epoch": epoch, "train_loss": total_loss/count,
                  "val_loss": scores["loss"], "val_iou": scores["iou"], "val_dice": scores["dice"]}
        history.append(record)
        print(record, flush=True)
        with (output / "history.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(record))
            writer.writeheader()
            writer.writerows(history)
        if scores["iou"] > best_iou:
            best_iou = scores["iou"]
            checkpoint = {"model_state": model.state_dict(), "config": vars(args),
                          "epoch": epoch, "val_iou": best_iou,
                          "split_fingerprint": fingerprint, "partial_run": metadata["partial_run"]}
            torch.save(checkpoint, output / "best.pt")
    checkpoint = torch.load(output / "best.pt", map_location=args.device, weights_only=True)
    model.load_state_dict(checkpoint["model_state"])
    save_examples(model, val, args.device, output / "validation_examples.png")
    save_curves(history, output / "curves.png")
    metadata.update({"best_epoch": checkpoint["epoch"], "best_val_iou": best_iou,
                     "elapsed_seconds": time.perf_counter()-start})
    if args.device == "cuda":
        metadata["peak_tensor_memory_mib"] = torch.cuda.max_memory_allocated()/1024**2
    (output / "run.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("Saved best validation checkpoint. Test images were not evaluated.", flush=True)
    return metadata


if __name__ == "__main__":
    run_training(make_parser().parse_args())
