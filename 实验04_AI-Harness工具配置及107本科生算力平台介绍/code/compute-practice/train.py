"""One CIFAR-10/ResNet-18 entry point for CPU checks and explicit CUDA training."""

import argparse
import csv
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import random
import socket
import sys
import time


def read_config(path, overrides):
    config = json.loads(path.read_text(encoding="utf-8"))
    integer_keys = ("seed", "train_samples", "eval_samples", "batch_size", "epochs",
                    "max_steps", "num_workers", "cpu_threads", "log_every")
    allowed = set(integer_keys) | {"learning_rate"}
    if set(config) != allowed:
        raise ValueError(f"Config needs exactly these fields: {sorted(allowed)}")
    for key, value in overrides.items():
        if value is not None:
            config[key] = value
    for key in integer_keys:
        minimum = 0 if key in ("seed", "max_steps", "num_workers") else 1
        if type(config[key]) is not int or config[key] < minimum:
            raise ValueError(f"Invalid {key}: expected an integer >= {minimum}")
    if config["train_samples"] > 45000 or config["eval_samples"] > 5000:
        raise ValueError("Use at most 45000 training and 5000 validation samples.")
    if config["batch_size"] < 2 or config["train_samples"] < 2:
        raise ValueError("Training batch size and sample count must be >= 2.")
    rate = config["learning_rate"]
    if isinstance(rate, bool) or not isinstance(rate, (int, float)) or not math.isfinite(rate) or rate <= 0:
        raise ValueError("learning_rate must be finite and positive")
    return config


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def sync(torch, device):
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def run(args):
    overrides = {key: getattr(args, key) for key in
                 ("train_samples", "eval_samples", "max_steps", "epochs", "num_workers", "cpu_threads")}
    config = read_config(args.config, overrides)
    data_dir = args.data_dir.resolve()
    if not (data_dir / "cifar-10-batches-py").is_dir():
        raise FileNotFoundError(
            f"CIFAR-10 directory not found: {data_dir / 'cifar-10-batches-py'}. "
            "Run prepare_data.py, then check --data-dir and the job working directory."
        )
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {output}; use a new run directory.")

    import torch
    import torchvision
    from torch import nn
    from torch.utils.data import DataLoader, Subset
    from torchvision import datasets, transforms
    from torchvision.models import resnet18

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable. Check GPU allocation and the installed wheel; no CPU fallback.")
    device = torch.device(args.device)
    torch.set_num_threads(config["cpu_threads"])
    random.seed(config["seed"])
    torch.manual_seed(config["seed"])
    if device.type == "cuda":
        torch.cuda.manual_seed_all(config["seed"])
        torch.cuda.reset_peak_memory_stats(device)
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
    ])
    dataset = datasets.CIFAR10(str(data_dir), train=True, transform=transform, download=False)
    # The official test set is left untouched. A fixed holdout comes from the training set.
    indices = torch.randperm(len(dataset), generator=torch.Generator().manual_seed(config["seed"])).tolist()
    eval_indices = indices[:5000][:config["eval_samples"]]
    train_indices = indices[5000:][:config["train_samples"]]
    train_loader = DataLoader(Subset(dataset, train_indices), batch_size=config["batch_size"],
                              shuffle=True, num_workers=config["num_workers"],
                              generator=torch.Generator().manual_seed(config["seed"]),
                              pin_memory=device.type == "cuda")
    eval_loader = DataLoader(Subset(dataset, eval_indices), batch_size=config["batch_size"],
                             shuffle=False, num_workers=config["num_workers"],
                             pin_memory=device.type == "cuda")
    model = resnet18(weights=None, num_classes=10)
    # CIFAR-10 uses 32x32 images; retain spatial detail instead of the ImageNet stem.
    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model.maxpool = nn.Identity()
    model.to(device)
    initial_probe = model.conv1.weight.detach().cpu().clone()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=config["learning_rate"], momentum=0.9)
    output.mkdir(parents=True, exist_ok=True)
    metadata = {
        "status": "running", "started_utc": datetime.now(timezone.utc).isoformat(),
        "config": config, "device": str(device), "python": sys.version.split()[0],
        "torch": str(torch.__version__), "torchvision": str(torchvision.__version__),
        "cuda_build": torch.version.cuda, "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "node": socket.gethostname(), "job_id": os.environ.get("SLURM_JOB_ID"),
        "cwd": str(Path.cwd()), "data_dir": str(data_dir),
        "model": "resnet18-cifar10-stem", "weights": "random initialization",
        "split": "fixed 45000/5000 train/validation from official training set; official test untouched",
    }
    write_json(output / "run.json", metadata)
    print(f"device={device}; gpu={metadata['gpu']}; output={output}", flush=True)
    rows, steps, train_seconds, eval_seconds, seen = [], 0, 0.0, 0.0, 0
    try:
        with (output / "metrics.csv").open("w", newline="", encoding="utf-8") as stream:
            fields = ["epoch", "steps", "train_loss", "train_accuracy", "validation_loss",
                      "validation_accuracy", "train_seconds", "validation_seconds"]
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for epoch in range(1, config["epochs"] + 1):
                model.train()
                total_loss, correct, count = 0.0, 0, 0
                sync(torch, device)
                started = time.perf_counter()
                for images, labels in train_loader:
                    images, labels = images.to(device), labels.to(device)
                    optimizer.zero_grad(set_to_none=True)
                    logits = model(images)
                    loss = criterion(logits, labels)
                    if not torch.isfinite(loss):
                        raise RuntimeError("Non-finite training loss")
                    loss.backward()
                    optimizer.step()
                    batch = labels.size(0)
                    total_loss += loss.item() * batch
                    correct += (logits.argmax(1) == labels).sum().item()
                    count += batch
                    steps += 1
                    if steps == 1 or steps % config["log_every"] == 0:
                        print(f"train epoch={epoch} step={steps} loss={loss.item():.6f}", flush=True)
                    if config["max_steps"] and steps >= config["max_steps"]:
                        break
                sync(torch, device)
                elapsed_train = time.perf_counter() - started
                model.eval()
                val_loss, val_correct, val_count = 0.0, 0, 0
                started = time.perf_counter()
                with torch.inference_mode():
                    for images, labels in eval_loader:
                        images, labels = images.to(device), labels.to(device)
                        logits = model(images)
                        batch = labels.size(0)
                        val_loss += criterion(logits, labels).item() * batch
                        val_correct += (logits.argmax(1) == labels).sum().item()
                        val_count += batch
                sync(torch, device)
                elapsed_eval = time.perf_counter() - started
                row = {"epoch": epoch, "steps": steps, "train_loss": total_loss / count,
                       "train_accuracy": correct / count, "validation_loss": val_loss / val_count,
                       "validation_accuracy": val_correct / val_count,
                       "train_seconds": elapsed_train, "validation_seconds": elapsed_eval}
                writer.writerow(row)
                stream.flush()
                rows.append(row)
                train_seconds += elapsed_train
                eval_seconds += elapsed_eval
                seen += count
                print(f"epoch={epoch} train_loss={row['train_loss']:.6f} validation_loss={row['validation_loss']:.6f}", flush=True)
                if config["max_steps"] and steps >= config["max_steps"]:
                    break
        changed = not torch.equal(initial_probe, model.conv1.weight.detach().cpu())
        if not changed:
            raise RuntimeError("The conv1.weight probe did not change after training")
        torch.save({"state_dict": {key: value.detach().cpu() for key, value in model.state_dict().items()},
                    "classes": dataset.classes, "model": metadata["model"], "config": config}, output / "model.pt")
        import matplotlib
        matplotlib.use("Agg")
        from matplotlib import pyplot as plt
        figure, axis = plt.subplots(figsize=(6, 3.5))
        axis.plot([row["steps"] for row in rows], [row["train_loss"] for row in rows], "o-", label="training batches")
        axis.plot([row["steps"] for row in rows], [row["validation_loss"] for row in rows], "o-", label="validation")
        axis.set(xlabel="completed optimizer steps", ylabel="cross entropy", title="CIFAR-10 / ResNet-18")
        axis.legend()
        figure.tight_layout()
        figure.savefig(output / "loss.png", dpi=160)
        plt.close(figure)
        metadata.update(status="complete", completed_steps=steps, parameter_probe="conv1.weight",
                        parameter_changed=changed, train_images_seen=seen,
                        train_seconds=train_seconds, validation_seconds=eval_seconds,
                        train_images_per_second=seen / train_seconds,
                        peak_cuda_allocated_mb=torch.cuda.max_memory_allocated(device) / 1024**2 if device.type == "cuda" else None)
        write_json(output / "run.json", metadata)
        print(f"complete: steps={steps}; parameter_changed={changed}; saved run.json, metrics.csv, model.pt, loss.png", flush=True)
    except Exception as error:
        metadata.update(status="failed", error=f"{type(error).__name__}: {error}", completed_steps=steps)
        write_json(output / "run.json", metadata)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/smoke.json"))
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, required=True, help="New or empty run directory")
    parser.add_argument("--device", choices=("cpu", "cuda"), required=True)
    for key in ("train_samples", "eval_samples", "max_steps", "epochs", "num_workers", "cpu_threads"):
        parser.add_argument("--" + key.replace("_", "-"), type=int)
    args = parser.parse_args()
    try:
        run(args)
    except Exception as error:
        print(f"ERROR {type(error).__name__}: {error}", file=sys.stderr, flush=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
