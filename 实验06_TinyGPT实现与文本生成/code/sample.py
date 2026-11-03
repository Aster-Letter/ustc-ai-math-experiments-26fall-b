"""用保存的源代码与权重采样：在运行目录的 source/ 内执行本文件。"""
import argparse
import json
from pathlib import Path

import torch
import student
from data import decode


def main():
    """从命令行读取提示词和温度，保存包含提示词的生成文本。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="../best.pt")
    parser.add_argument("--prompt", default="春")
    parser.add_argument("--steps", type=int, default=80)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--greedy", action="store_true")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--device", choices=["cpu", "cuda", "mps"], default="cpu")
    parser.add_argument("--output", default="../sample.txt")
    args = parser.parse_args()
    torch.set_num_threads(2)
    torch.manual_seed(args.seed)
    saved = torch.load(args.checkpoint, map_location=args.device, weights_only=True)
    model = student.TinyGPT(**saved["config"]).to(args.device)
    model.load_state_dict(saved["model"])
    vocab = saved["vocab"]
    stoi = {char: index for index, char in enumerate(vocab)}
    # 两个换行与训练数据的诗歌边界一致，不人为限制句长、选字或韵律。
    ids = torch.tensor([[stoi.get(char, 0) for char in "\n\n" + args.prompt]], device=args.device)
    result = student.generate(model, ids, args.steps, args.temperature, args.greedy)
    text = decode(result[0].tolist(), vocab)
    Path(args.output).write_text(text, encoding="utf-8")
    Path(args.output + ".json").write_text(json.dumps(vars(args), indent=2), encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
