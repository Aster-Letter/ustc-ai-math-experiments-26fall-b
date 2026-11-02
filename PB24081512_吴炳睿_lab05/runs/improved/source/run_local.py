"""已提供：本地NVIDIA GPU训练与评估入口，同时保存终端日志。"""
import argparse
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys


def run_commands(commands, log_path):
    """依次运行命令，把输出同时显示在终端并保存到日志。

    Args:
        commands (list): 由解释器、脚本路径和参数组成的命令列表。
        log_path (Path): 日志文件路径。

    Returns:
        int: 成功时为0，否则返回相应命令的退出码。
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, PYTHONIOENCODING="utf-8")
    with log_path.open("w", encoding="utf-8") as log:
        for command in commands:
            line = "Command: " + subprocess.list2cmdline(command) + "\n"
            print(line, end="", flush=True)
            log.write(line)
            log.flush()
            with subprocess.Popen(command, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True,
                                  encoding="utf-8", env=environment) as process:
                for line in process.stdout:
                    print(line, end="", flush=True)
                    log.write(line)
                    log.flush()
                return_code = process.wait()
            if return_code != 0:
                return return_code
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["basic", "improved", "evaluate"])
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--output")
    parser.add_argument("--checkpoint")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.stage == "evaluate" and args.checkpoint is None:
        parser.error("evaluate requires --checkpoint")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    output = args.output or f"outputs/{args.stage}-local-{stamp}"
    if args.stage == "evaluate":
        source = Path(args.checkpoint).parent / "source/evaluate.py"
        commands = [[sys.executable, "-u", str(source),
                     "--checkpoint", args.checkpoint, "--data-dir", args.data_dir,
                     "--device", "cuda", "--split", "test", "--output", output]]
    else:
        commands = [[sys.executable, "-u", "checks.py", args.stage],
                    [sys.executable, "-u", "train.py", "--model", args.stage,
                     "--data-dir", args.data_dir, "--device", "cuda", "--output", output,
                     "--epochs", str(args.epochs), "--batch-size", str(args.batch_size),
                     "--lr", str(args.lr), "--seed", str(args.seed)]]
    log_path = Path("logs") / f"{Path(output).name}-{stamp}.log"
    print("Log:", log_path, flush=True)
    raise SystemExit(run_commands(commands, log_path))
