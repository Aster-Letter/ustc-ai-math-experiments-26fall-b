"""模型确定后运行；使用训练输出中的 source/evaluate.py 复现该模型。"""
import argparse
import csv
import json
from pathlib import Path
import torch
from torch.utils.data import DataLoader, Subset
from data import PetDataset, SyntheticPets, read_manifest
from models import build_model
from train import evaluate_loader
from visuals import save_examples


def evaluate(args):
    """在指定划分上计算逐图指标并保存可视化。

    Args:
        args (Namespace): 模型路径、数据位置、设备、划分和输出位置。
    """
    torch.set_num_threads(2)
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=True)
    config = checkpoint["config"]
    model = build_model(config["model"])
    model.load_state_dict(checkpoint["model_state"])
    model.to(args.device)
    if config["synthetic"]:
        dataset = SyntheticPets(args.split, config["size"])
    else:
        splits, fingerprint = read_manifest(args.data_dir)
        assert fingerprint == checkpoint["split_fingerprint"], "Split differs from training. Use the original splits.json."
        dataset = PetDataset(args.data_dir, splits[args.split], config["size"])
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False)
    scores, rows = evaluate_loader(model, loader, args.device)
    scores.update({"split": args.split, "checkpoint": args.checkpoint,
                   "model": config["model"], "selected_epoch": checkpoint["epoch"],
                   "size": config["size"], "threshold": 0.5,
                   "data_kind": "synthetic_smoke_only" if config["synthetic"] else "Oxford-IIIT Pet",
                   "partial_training": checkpoint["partial_run"],
                   "aggregation": "mean of per-image foreground scores; ignore trimap=3; empty=1"})
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    (output / "metrics.json").write_text(json.dumps(scores, indent=2), encoding="utf-8")
    with (output / "per_image.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["image", "iou", "dice"])
        writer.writeheader()
        writer.writerows(rows)
    save_examples(model, dataset, args.device, output / "examples.png")
    order = sorted(range(len(rows)), key=lambda index: rows[index]["iou"])
    selected = order[:3] + order[-3:]
    save_examples(model, Subset(dataset, selected), args.device,
                  output / "best_worst_examples.png")
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--device", choices=["cpu", "cuda", "mps"], default="cuda")
    parser.add_argument("--split", choices=["val", "test"], default="test")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--output", required=True)
    evaluate(parser.parse_args())
