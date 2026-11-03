"""已提供：训练、固定窗口评估、二元计数基线和结果保存。"""
import argparse
import csv
import json
import math
import os
from pathlib import Path
import platform
import shutil
import time

import torch
from torch.nn import functional as F

from data import load_data, get_batch


@torch.no_grad()
def evaluate(model, ids, device):
    """逐块遍历整段文本；每个目标字符恰计一次，块间重置上下文。

    Args:
        model (Module): 待评估模型。
        ids (Tensor): 一维编号，首字符只作上下文。
        device (str): 运行设备。

    Returns:
        dict: 每字符平均交叉熵、困惑度、计分字符数。
    """
    model.eval()
    total_loss, count = 0.0, 0
    for start in range(0, len(ids) - 1, model.block_size):
        end = min(start + model.block_size, len(ids) - 1)
        x = ids[start:end].unsqueeze(0).to(device)
        y = ids[start + 1:end + 1].to(device)
        logits = model(x)[0]
        total_loss += F.cross_entropy(logits, y, reduction="sum").item()
        count += len(y)
    mean = total_loss / count
    return {"loss": mean, "perplexity": math.exp(mean), "tokens": count}


def bigram_scores(train_ids, eval_ids, vocab_size):
    """仅在训练集数相邻字符对，使用加一平滑。

    Args:
        train_ids (Tensor): 训练编号。
        eval_ids (Tensor): 验证或测试编号。
        vocab_size (int): 含未知字符的词表大小。

    Returns:
        dict: 二元字符模型的平均交叉熵、困惑度和计分字符数。
    """
    counts = torch.ones(vocab_size, vocab_size, dtype=torch.float64)
    pair_ids = train_ids[:-1] * vocab_size + train_ids[1:]
    counts += torch.bincount(pair_ids, minlength=vocab_size ** 2).reshape(vocab_size, vocab_size)
    probabilities = counts / counts.sum(dim=1, keepdim=True)
    mean = -probabilities[eval_ids[:-1], eval_ids[1:]].log().mean().item()
    return {"loss": mean, "perplexity": math.exp(mean), "tokens": len(eval_ids) - 1}


def train(api, args):
    """运行一次训练，按验证交叉熵选择权重；训练过程不评价测试集。

    Args:
        api (module): 学生模块或教师参考模块。
        args (Namespace): 命令行设置。
    """
    torch.set_num_threads(args.threads)
    torch.manual_seed(args.seed)
    splits, vocab, data_info = load_data(args.data)
    config = dict(vocab_size=len(vocab), block_size=args.block_size, width=args.width,
                  n_head=args.heads, n_layer=args.layers, dropout=args.dropout)
    model = api.TinyGPT(**config).to(args.device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.0)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    source = output / "source"
    source.mkdir()
    for path in Path(__file__).parent.glob("*.py"):
        shutil.copy2(path, source / path.name)
    scripts = Path(__file__).parent / "scripts"
    if scripts.exists():
        shutil.copytree(scripts, source / "scripts")
    # 教师运行时保存实际参考实现；学生运行时此处就是学生自己的 student.py。
    shutil.copy2(api.__file__, source / "student.py")
    settings = {
        "arguments": vars(args), "model": config, "data": data_info, "vocab": vocab,
        "python": platform.python_version(), "torch": str(torch.__version__),
        "platform": platform.platform(), "device": str(args.device),
        "parameters": sum(p.numel() for p in model.parameters()),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "evaluation": "all targets once, non-overlapping blocks, context reset per block",
        "optimizer": "AdamW, weight_decay=0, fixed learning rate",
    }
    (output / "run.json").write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
    baseline = bigram_scores(splits["train"], splits["val"], len(vocab))
    (output / "bigram_validation.json").write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    # 与训练抽样独立的固定训练窗口，便于观察训练/验证差距。
    monitor = splits["train"][:min(8193, len(splits["train"]))]
    best = float("inf")
    started = time.perf_counter()
    with (output / "history.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["step", "train_loss", "val_loss", "val_perplexity", "seconds"])
        writer.writeheader()
        for step in range(args.steps + 1):
            if step % args.eval_every == 0 or step == args.steps:
                train_metrics = evaluate(model, monitor, args.device)
                val_metrics = evaluate(model, splits["val"], args.device)
                row = dict(step=step, train_loss=train_metrics["loss"], val_loss=val_metrics["loss"],
                           val_perplexity=val_metrics["perplexity"], seconds=time.perf_counter() - started)
                writer.writerow(row)
                stream.flush()
                print(f"step={step:4d} train={row['train_loss']:.4f} val={row['val_loss']:.4f} "
                      f"ppl={row['val_perplexity']:.2f}", flush=True)
                if val_metrics["loss"] < best:
                    best = val_metrics["loss"]
                    torch.save({"model": model.state_dict(), "config": config, "vocab": vocab,
                                "step": step, "val_loss": best, "data": data_info}, output / "best.pt")
            if step == args.steps:
                break
            model.train()
            x, y = get_batch(splits["train"], args.batch_size, args.block_size, api.make_xy, args.device)
            optimizer.zero_grad()
            loss = api.language_loss(model(x), y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
    print("保存到", output, "；在验证集选好方案后再运行 evaluate.py。")


def parser():
    """建立课程所需的少量运行参数。

    Returns:
        ArgumentParser: 共用参数解析器。
    """
    result = argparse.ArgumentParser()
    result.add_argument("--data", default="data")
    result.add_argument("--output", default="outputs/run-01")
    result.add_argument("--device", choices=["cpu", "cuda", "mps"], default="cpu")
    result.add_argument("--steps", type=int, default=3000)
    result.add_argument("--eval-every", type=int, default=300)
    result.add_argument("--batch-size", type=int, default=64)
    result.add_argument("--block-size", type=int, default=32)
    result.add_argument("--width", type=int, default=128)
    result.add_argument("--heads", type=int, default=4)
    result.add_argument("--layers", type=int, default=2)
    result.add_argument("--dropout", type=float, default=0.1)
    result.add_argument("--lr", type=float, default=0.0003)
    result.add_argument("--seed", type=int, default=2026)
    result.add_argument("--threads", type=int, default=2)
    return result
