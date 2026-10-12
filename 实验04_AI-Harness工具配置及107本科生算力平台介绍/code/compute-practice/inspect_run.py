"""Inspect one run and its saved checkpoint; this does not grade a student."""

import argparse
import csv
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args()
    result = json.loads((args.run_dir / "run.json").read_text(encoding="utf-8"))
    if result["status"] != "complete" or not result.get("parameter_changed"):
        raise ValueError("Run did not complete with a changed parameter probe")
    if args.require_cuda and result["device"] != "cuda":
        raise ValueError("This is not a CUDA training run")
    import torch
    checkpoint = torch.load(args.run_dir / "model.pt", map_location="cpu", weights_only=True)
    if checkpoint["state_dict"]["fc.weight"].shape[0] != 10 or len(checkpoint["classes"]) != 10:
        raise ValueError("Checkpoint does not describe the expected ten-class model")
    with (args.run_dir / "metrics.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or int(rows[-1]["steps"]) != result["completed_steps"]:
        raise ValueError("Metrics and metadata disagree about completed steps")
    if not (args.run_dir / "loss.png").is_file():
        raise ValueError("Loss figure is missing")
    print(json.dumps({key: result[key] for key in
                      ("status", "device", "gpu", "completed_steps", "parameter_changed",
                       "train_seconds", "train_images_per_second")}, indent=2))
    print("checkpoint readable; metrics agree; loss.png exists")


if __name__ == "__main__":
    main()
