"""已提供的编排：主实验比较正则化，选做比较特征组，最后单独测试。"""
import argparse
import copy
import json
from pathlib import Path
import platform
import pandas as pd
import torch
import support
import checkpoints


def fit_candidate(implementation, train, val, kind, strength):
    """固定训练设置，保存验证数据损失最低的一轮。

    Args:
        implementation (module): student 或 reference 模块。
        train (tuple): 训练集 (X, y) 张量对。
        val (tuple): 验证集 (X, y) 张量对。
        kind (str): 正则化类型，取 "none"、"l1" 或 "l2"。
        strength (float): 正则化系数，例如 0.01。

    Returns:
        tuple: (row, model, history, probabilities)。row 为候选设置与验证指标（dict），
            model 为最佳轮的模型，history 为每轮损失（list of dict），
            probabilities 为形状 (N_val, 1) 的验证概率。
    """
    torch.manual_seed(42)
    model = implementation.LogisticRegression(train[0].shape[1])
    loader = implementation.make_loader(implementation.UniversityDataset(*train), 64, True)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.05)
    history = []
    best_loss = float("inf")
    for epoch in range(1, 61):
        implementation.train_epoch(model, loader, optimizer, kind, strength)
        train_metrics, _ = support.evaluate(implementation, model, train)
        val_metrics, _ = support.evaluate(implementation, model, val)
        history.append({"epoch": epoch, "train_loss": train_metrics["loss"], "val_loss": val_metrics["loss"]})
        if val_metrics["loss"] < best_loss:
            best_loss = val_metrics["loss"]
            snapshot = copy.deepcopy(model.state_dict())
            best_epoch = epoch
    model.load_state_dict(snapshot)
    metrics, probabilities = support.evaluate(implementation, model, val)
    row = {"kind": kind, "strength": strength, "lr": 0.05, "epoch": best_epoch,
           "max_epochs": 60, "batch_size": 64, "seed": 42,
           "val_loss": metrics["loss"], "val_accuracy": metrics["accuracy"],
           "val_precision": metrics["precision"], "val_recall": metrics["recall"], "val_f1": metrics["f1"]}
    return row, model, history, probabilities


def train_candidates(implementation, data_dir, output):
    """比较三个正则化方案，冻结主实验模型、预处理和0.5阈值。

    Args:
        implementation (module): student 或 reference 模块。
        data_dir (str or pathlib.Path): 课堂数据目录。
        output (pathlib.Path): 主实验结果目录，例如 outputs-qs/。
    """
    output.mkdir(parents=True, exist_ok=True)
    train, val, state = support.prepare_train_val(implementation, data_dir)
    candidates = []
    best_loss = float("inf")
    for kind, strength in [("none", 0.0), ("l2", 0.01), ("l1", 0.01)]:
        row, model, history, probabilities = fit_candidate(implementation, train, val, kind, strength)
        candidates.append(row)
        pd.DataFrame(history).to_csv(output / (kind + "_history.csv"), index=False)
        support.plot_history(history, output / (kind + "_loss.png"))
        print(row)
        if row["val_loss"] < best_loss:
            best_loss = row["val_loss"]
            selected = dict(row)
            selected_model = model
            selected_probabilities = probabilities
    torch.save(selected_model.state_dict(), output / "selected.pt")
    selected.update({"threshold": 0.5, "feature_set": "full", "input_dim": train[0].shape[1],
                     "train_n": len(train[1]), "val_n": len(val[1]),
                     "train_positive_fraction": train[1].mean().item(),
                     "majority_class": int(train[1].mean().item() > 0.5),
                     "python": platform.python_version(), "torch": torch.__version__, "pandas": pd.__version__})
    saved = {"means": state["means"].to_dict(), "scales": state["scales"].to_dict(),
             "categories": state["categories"], "numeric": support.NUMERIC, "feature_set": "full"}
    (output / "preprocessing.json").write_text(json.dumps(saved, indent=2))
    (output / "selection.json").write_text(json.dumps(selected, indent=2))
    pd.DataFrame(candidates).to_csv(output / "candidates.csv", index=False)
    thresholds = []
    for threshold in [0.3, 0.5, 0.7]:
        metrics = implementation.binary_metrics(val[1], selected_probabilities, threshold)
        thresholds.append({"threshold": threshold, **metrics})
    pd.DataFrame(thresholds).to_csv(output / "validation_thresholds.csv", index=False)
    names = ["intercept"] + support.NUMERIC
    for column, levels in state["categories"].items():
        names.extend([column + "=" + level for level in levels])
    pd.DataFrame({"feature": names, "weight": selected_model.theta.detach().reshape(-1).tolist()}).to_csv(output / "weights.csv", index=False)
    print("主实验模型、特征和阈值已冻结；未读取测试集。")


def feature_study(implementation, data_dir, output):
    """仅在验证集上比较完整/精简特征，固定L2系数，不改主实验选择。

    Args:
        implementation (module): student 或 reference 模块。
        data_dir (str or pathlib.Path): 课堂数据目录。
        output (pathlib.Path): 主实验目录，选做记录保存在其 feature_study 子目录。
    """
    folder = output / "feature_study"
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    for feature_set in ["full", "reduced"]:
        train, val, state = support.prepare_train_val(implementation, data_dir, feature_set)
        row, model, history, probabilities = fit_candidate(implementation, train, val, "l2", 0.01)
        row.update({"feature_set": feature_set, "feature_dim": train[0].shape[1] - 1})
        rows.append(row)
        pd.DataFrame(history).to_csv(folder / (feature_set + "_history.csv"), index=False)
        print(row)
    pd.DataFrame(rows).to_csv(folder / "comparison.csv", index=False)
    print("特征对照仅作验证集分析，不读取测试集，不覆盖主实验冻结模型。")


def final_test(implementation, data_dir, output):
    """恢复已冻结模型与训练预处理状态，报告一次测试结果。

    Args:
        implementation (module): student 或 reference 模块。
        data_dir (str or pathlib.Path): 与训练时相同的课堂数据目录。
        output (pathlib.Path): 保存 selection.json、preprocessing.json 与 selected.pt 的目录。
    """
    selected = json.loads((output / "selection.json").read_text())
    saved = json.loads((output / "preprocessing.json").read_text())
    state = {"means": pd.Series(saved["means"]), "scales": pd.Series(saved["scales"]),
             "categories": saved["categories"], "feature_set": saved["feature_set"]}
    test = support.prepare_test(implementation, data_dir, state)
    model = implementation.LogisticRegression(selected["input_dim"])
    model.load_state_dict(torch.load(output / "selected.pt", map_location="cpu", weights_only=True))
    metrics, probabilities = support.evaluate(implementation, model, test, selected["threshold"])
    baseline = torch.full_like(test[1], float(selected["majority_class"]))
    metrics["majority_baseline_accuracy"] = implementation.binary_metrics(test[1], baseline)["accuracy"]
    metrics.update({"test_n": len(test[1]), "threshold": selected["threshold"]})
    (output / "test_metrics.json").write_text(json.dumps(metrics, indent=2))
    frame = support.load_split(data_dir, "test")
    frame = implementation.filter_labels(frame)
    pd.DataFrame({"row_id": frame.row_id, "label": test[1].reshape(-1).tolist(),
                  "probability": probabilities.reshape(-1).tolist()}).to_csv(output / "test_predictions.csv", index=False)
    print(json.dumps(metrics, indent=2))
    print("测试完成，不根据此结果重选参数、特征或阈值。")


def main(implementation):
    """调度主实验、选做特征对照或最终测试。

    Args:
        implementation (module): student 或 reference 模块。
    """
    parser = argparse.ArgumentParser(description="实验03：逻辑回归与大学排名分类")
    parser.add_argument("--data-dir", type=Path, default=support.DATA_DIR)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs-qs")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--feature-study", action="store_true")
    mode.add_argument("--final-test", action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(1)
    checkpoints.check_all(implementation)
    if args.feature_study:
        feature_study(implementation, args.data_dir, args.output)
    elif args.final_test:
        final_test(implementation, args.data_dir, args.output)
    else:
        train_candidates(implementation, args.data_dir, args.output)
