"""已提供的读取、固定编码和绘图，不属于学生补全内容。"""
from pathlib import Path
import pandas as pd
import torch

DATA_DIR = Path(__file__).resolve().parent / "data" / "classroom"
FEATURES = ["loanAmnt", "interestRate", "annualIncome", "dti", "grade",
            "employmentLength", "issueDate", "earliesCreditLine"]


def load_split(data_dir, name):
    """读取预先划分的数据。

    Args:
        data_dir (str or Path): 三份数据所在目录。
        name (str): train、val 或 test。
    Returns:
        pd.DataFrame: 原始表格。
    """
    return pd.read_csv(Path(data_dir) / (name + ".csv"))


def date_origin(train):
    """仅从已过滤标签的训练表拟合日期原点。

    Args:
        train (pd.DataFrame): 训练数据。
    Returns:
        dict: 最早发放日期和最早信用月份序号。
    """
    issue = pd.to_datetime(train["issueDate"], format="%Y-%m-%d")
    credit = pd.to_datetime(train["earliesCreditLine"], format="%b-%Y")
    return {"issue": issue.min(), "credit": (credit.dt.year * 12 + credit.dt.month).min()}


def encode_features(frame, origin, employment_function):
    """选取八个教学特征，并进行固定字段编码。

    Args:
        frame (pd.DataFrame): 原始数据。
        origin (dict): 训练集日期原点。
        employment_function (function): 学生就业年限转换函数。
    Returns:
        pd.DataFrame: 尚未填充或标准化的八列数值特征。
    """
    result = frame[FEATURES].copy()
    result["grade"] = result["grade"].map({"A": 1, "B": 2, "C": 3, "D": 4,
                                           "E": 5, "F": 6, "G": 7})
    result["employmentLength"] = result["employmentLength"].apply(employment_function)
    issue = pd.to_datetime(result["issueDate"], format="%Y-%m-%d")
    credit = pd.to_datetime(result["earliesCreditLine"], format="%b-%Y")
    result["issueDate"] = (issue - origin["issue"]).dt.days
    result["earliesCreditLine"] = credit.dt.year * 12 + credit.dt.month - origin["credit"]
    return result.astype(float)


def prepare_train_val(implementation, data_dir):
    """拟合训练预处理并转换验证集，此时不读取测试文件。

    Args:
        implementation (module): student 或 reference 模块。
        data_dir (str or Path): 数据目录。
    Returns:
        tuple: 训练张量对、验证张量对和预处理状态。
    """
    train = implementation.filter_labels(load_split(data_dir, "train"))
    val = implementation.filter_labels(load_split(data_dir, "val"))
    origin = date_origin(train)
    train_features = encode_features(train, origin, implementation.encode_employment)
    val_features = encode_features(val, origin, implementation.encode_employment)
    means, scales = implementation.fit_statistics(train_features)
    train_values = implementation.apply_statistics(train_features, means, scales)
    val_values = implementation.apply_statistics(val_features, means, scales)
    state = {"origin": origin, "means": means, "scales": scales}
    return (implementation.to_tensors(train_values, train["isDefault"]),
            implementation.to_tensors(val_values, val["isDefault"]), state)


def prepare_test(implementation, data_dir, state):
    """最终方案冻结后才读取测试集。

    Args:
        implementation (module): student 或 reference 模块。
        data_dir (str or Path): 数据目录。
        state (dict): 训练预处理状态。
    Returns:
        tuple: 测试张量 (X,y)。
    """
    test = implementation.filter_labels(load_split(data_dir, "test"))
    features = encode_features(test, state["origin"], implementation.encode_employment)
    values = implementation.apply_statistics(features, state["means"], state["scales"])
    return implementation.to_tensors(values, test["isDefault"])


def evaluate(implementation, model, tensors, threshold=0.5):
    """关闭梯度后计算数据损失和指标。

    Args:
        implementation (module): 实现模块。
        model (torch.nn.Module): 模型。
        tensors (tuple): (X,y) 张量对。
        threshold (float): 分类阈值。
    Returns:
        tuple: (含 loss 的指标字典, 概率张量)。
    """
    model.eval()
    X, y = tensors
    with torch.no_grad():
        logits = model(X)
        probabilities = implementation.sigmoid(logits)
        metrics = implementation.binary_metrics(y, probabilities, threshold)
        metrics["loss"] = float(implementation.data_loss(logits, y))
    return metrics, probabilities


def plot_history(history, output_path):
    """绘制每轮结束时的训练/验证数据损失。

    Args:
        history (list): 每轮的指标字典列表。
        output_path (str or Path): 图片保存路径。
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    frame = pd.DataFrame(history)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(frame.epoch, frame.train_loss, label="Train", color="#2878B5")
    ax.plot(frame.epoch, frame.val_loss, label="Validation", color="#2A9D8F")
    ax.set(xlabel="Epoch", ylabel="Mean binary cross-entropy")
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
