"""已提供的实验编排：验证集选模型，单独命令做最终测试。"""
import argparse
import copy
import json
from pathlib import Path
import platform
import pandas as pd
import torch
import support
import checkpoints


def train_candidates(implementation, data_dir, output):
    """比较三个预先指定的方案，保存验证数据损失最小的参数。

    Args:
        implementation (module): student 或 reference 模块。
        data_dir (str or Path): 数据目录。
        output (Path): 结果目录。
    """
    train, val, state = support.prepare_train_val(implementation, data_dir)
    configs = [("none", 0.0), ("l2", 0.01), ("l1", 0.01)]
    candidates = []
    selected = None
    best_loss = float("inf")
    for kind, strength in configs:
        torch.manual_seed(42)
        model = implementation.LogisticRegression(train[0].shape[1])
        loader = implementation.make_loader(implementation.LoanDataset(*train), 64, True)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.05)
        history = []
        local_best = float("inf")
        for epoch in range(1, 61):
            implementation.train_epoch(model, loader, optimizer, kind, strength)
            train_metrics, _ = support.evaluate(implementation, model, train)
            val_metrics, _ = support.evaluate(implementation, model, val)
            history.append({"epoch": epoch, "train_loss": train_metrics["loss"], "val_loss": val_metrics["loss"]})
            if val_metrics["loss"] < local_best:
                local_best = val_metrics["loss"]
                snapshot = copy.deepcopy(model.state_dict())
                best_epoch = epoch
        model.load_state_dict(snapshot)
        metrics, probabilities = support.evaluate(implementation, model, val)
        candidate = {"kind": kind, "strength": strength, "lr": 0.05,
                     "epoch": best_epoch, "max_epochs": 60, "batch_size": 64,
                     "seed": 42, "val_loss": metrics["loss"], "val_accuracy": metrics["accuracy"]}
        candidates.append(candidate)
        pd.DataFrame(history).to_csv(output / (kind + "_history.csv"), index=False)
        support.plot_history(history, output / (kind + "_loss.png"))
        print(candidate)
        if metrics["loss"] < best_loss:
            best_loss = metrics["loss"]
            selected = dict(candidate)
            selected_state = snapshot
            selected_probabilities = probabilities
    torch.save(selected_state, output / "selected.pt")
    threshold_rows = []
    for threshold in [0.3, 0.5, 0.7]:
        metrics = implementation.binary_metrics(val[1], selected_probabilities, threshold)
        threshold_rows.append({"threshold": threshold, **metrics,
                               "example_cost": 2 * metrics["fn"] + metrics["fp"]})
    pd.DataFrame(threshold_rows).to_csv(output / "validation_thresholds.csv", index=False)
    # 主实验阈值预先固定为 0.5；其他阈值只作验证集上的代价讨论。
    selected.update({"threshold": 0.5, "input_dim": train[0].shape[1],
                     "train_n": len(train[1]), "val_n": len(val[1]),
                     "train_positive_fraction": train[1].mean().item(),
                     "val_positive_fraction": val[1].mean().item(),
                     # 训练集两类相同时，预先约定基线总预测 0（未违约）。
                     "majority_class": int(train[1].mean().item() > .5),
                     "python": platform.python_version(), "torch": torch.__version__,
                     "pandas": pd.__version__})
    preprocessing = {"issue": str(state["origin"]["issue"]), "credit": float(state["origin"]["credit"]),
                     "means": state["means"].to_dict(), "scales": state["scales"].to_dict(),
                     "features": support.FEATURES}
    (output / "preprocessing.json").write_text(json.dumps(preprocessing, indent=2), encoding="utf-8")
    (output / "selection.json").write_text(json.dumps(selected, indent=2), encoding="utf-8")
    pd.DataFrame(candidates).to_csv(output / "candidates.csv", index=False)
    print("已冻结模型与阈值。尚未读取 test.csv；最终测试使用 --final-test。")


def final_test(implementation, data_dir, output):
    """恢复已冻结的模型和预处理状态，报告一次最终测试。

    Args:
        implementation (module): student 或 reference 模块。
        data_dir (str or Path): 原实验数据目录。
        output (Path): 包含已选模型的结果目录。
    """
    selected = json.loads((output / "selection.json").read_text())
    saved = json.loads((output / "preprocessing.json").read_text())
    state = {"origin": {"issue": pd.Timestamp(saved["issue"]), "credit": saved["credit"]},
             "means": pd.Series(saved["means"]), "scales": pd.Series(saved["scales"])}
    test = support.prepare_test(implementation, data_dir, state)
    model = implementation.LogisticRegression(selected["input_dim"])
    model.load_state_dict(torch.load(output / "selected.pt", map_location="cpu", weights_only=True))
    metrics, probabilities = support.evaluate(implementation, model, test, selected["threshold"])
    baseline = torch.full_like(test[1], float(selected["majority_class"]))
    metrics["majority_baseline_accuracy"] = implementation.binary_metrics(test[1], baseline)["accuracy"]
    metrics["test_n"] = len(test[1])
    metrics["threshold"] = selected["threshold"]
    (output / "test_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    pd.DataFrame({"label": test[1].reshape(-1).tolist(), "probability": probabilities.reshape(-1).tolist()}).to_csv(output / "test_predictions.csv", index=False)
    print(json.dumps(metrics, indent=2))
    print("测试完成；不要根据此结果重新选择参数或阈值。")


def main(implementation):
    """读取运行参数并调度已完成的学生实现。

    Args:
        implementation (module): student 或 reference 模块。
    """
    parser = argparse.ArgumentParser(description="实验03：逻辑回归")
    parser.add_argument("--data-dir", type=Path, default=support.DATA_DIR)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs-tianchi-balanced")
    parser.add_argument("--final-test", action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(1)
    checkpoints.check_all(implementation)
    args.output.mkdir(parents=True, exist_ok=True)
    if args.final_test:
        final_test(implementation, args.data_dir, args.output)
    else:
        train_candidates(implementation, args.data_dir, args.output)
