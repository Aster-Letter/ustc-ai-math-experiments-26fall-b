"""已提供的数据编排；数值填补与类别编码只在训练集拟合。"""
from pathlib import Path
import pandas as pd
import torch

DATA_DIR = Path(__file__).resolve().parent / "data" / "classroom"
NUMERIC = ["faculty_student_score", "international_faculty_score", "international_student_score"]
CATEGORICAL = ["region", "status", "size", "focus", "research"]


def load_split(data_dir, name):
    """读取一份课堂数据。

    Args:
        data_dir (str or Path): 数据目录。
        name (str): train、val 或 test。
    Returns:
        pd.DataFrame: 原始课堂表。
    """
    return pd.read_csv(Path(data_dir) / (name + ".csv"))


def feature_columns(feature_set):
    """返回事先约定的类别字段组，数值字段固定。

    Args:
        feature_set (str): full 或 reduced。
    Returns:
        list: 按固定顺序排列的类别字段名。
    """
    if feature_set == "reduced":
        return ["region", "status", "size"]
    return CATEGORICAL


def transform(implementation, frame, state):
    """应用训练状态，拼接标准化数值列与未经标准化的独热列。

    Args:
        implementation (module): student 或 reference。
        frame (pd.DataFrame): 标签已过滤的数据表。
        state (dict): 训练均值、尺度、类别表和特征方案。
    Returns:
        tuple: 增广特征和标签张量。
    """
    numeric = frame[NUMERIC].apply(implementation.clean_numeric)
    numeric = implementation.apply_statistics(numeric, state["means"], state["scales"])
    category = implementation.encode_categories(frame, state["categories"])
    features = pd.concat([numeric, category], axis=1)
    return implementation.to_tensors(features, frame["top500"])


def prepare_train_val(implementation, data_dir, feature_set="full"):
    """只读取训练和验证表，拟合后保持列顺序一致。

    Args:
        implementation (module): student 或 reference。
        data_dir (str or Path): 课堂目录。
        feature_set (str): full 为主实验，reduced 为选做对照。
    Returns:
        tuple: (train, val, state)，前两项为张量对。
    """
    train = implementation.filter_labels(load_split(data_dir, "train"))
    val = implementation.filter_labels(load_split(data_dir, "val"))
    numeric = train[NUMERIC].apply(implementation.clean_numeric)
    means, scales = implementation.fit_statistics(numeric)
    categories = implementation.fit_categories(train[feature_columns(feature_set)])
    state = {"means": means, "scales": scales, "categories": categories, "feature_set": feature_set}
    return transform(implementation, train, state), transform(implementation, val, state), state


def prepare_test(implementation, data_dir, state):
    """模型冻结后，读取测试表并应用已保存的训练状态。

    Args:
        implementation (module): student 或 reference。
        data_dir (str or Path): 课堂目录。
        state (dict): 训练预处理状态。
    Returns:
        tuple: 测试增广特征和标签张量。
    """
    test = implementation.filter_labels(load_split(data_dir, "test"))
    return transform(implementation, test, state)


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
