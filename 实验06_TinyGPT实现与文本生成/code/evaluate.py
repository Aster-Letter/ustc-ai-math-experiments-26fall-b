"""最终测试入口：选好模型后，在其保存的 source/ 中运行。"""
import argparse
import json
from pathlib import Path

import torch
import student
from data import load_data
from engine import evaluate, bigram_scores


def main():
    """报告测试交叉熵及困惑度，并核对数据与训练时一致。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="../best.pt")
    parser.add_argument("--data", default="../../../data")
    parser.add_argument("--device", choices=["cpu", "cuda", "mps"], default="cpu")
    parser.add_argument("--output", default="../test_metrics.json")
    args = parser.parse_args()
    torch.set_num_threads(2)
    splits, vocab, info = load_data(args.data)
    saved = torch.load(args.checkpoint, map_location=args.device, weights_only=True)
    assert info == saved["data"] and vocab == saved["vocab"], "数据与训练记录不同，请检查文件"
    model = student.TinyGPT(**saved["config"]).to(args.device)
    model.load_state_dict(saved["model"])
    result = {
        "gpt": evaluate(model, splits["test"], args.device),
        "bigram": bigram_scores(splits["train"], splits["test"], len(vocab)),
        "selected_step": saved["step"], "validation_loss": saved["val_loss"],
        "data_sha256": info["sha256"], "unknown_test_characters": info["unknown_counts"]["test"],
    }
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
