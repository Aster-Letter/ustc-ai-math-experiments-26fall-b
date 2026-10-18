"""已提供：保存样例与训练曲线，无需桌面窗口。"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch


def save_examples(model, dataset, device, path, count=6):
    """展示原图、真实掩码、预测掩码；忽略区域以灰色标出。

    Args:
        model (nn.Module or None): 网络；None表示只查看数据。
        dataset (Dataset): 不带随机增强的数据集。
        device (str): 计算设备。
        path (str or Path): 输出图片路径。
        count (int): 展示固定顺序中的前几张。
    """
    count = min(count, len(dataset))
    fig, axes = plt.subplots(count, 3, figsize=(9, 3*count), squeeze=False)
    if model is not None:
        model.eval()
    with torch.no_grad():
        for row in range(count):
            image, target, valid, name = dataset[row]
            truth = target[0].numpy().copy()
            truth[valid[0].numpy() == 0] = 0.5
            prediction = np.full_like(truth, 0.5)
            if model is not None:
                logits = model(image.unsqueeze(0).to(device))[0, 0].cpu()
                prediction = (logits >= 0).float().numpy()
                prediction[valid[0].numpy() == 0] = 0.5
            axes[row, 0].imshow(image.permute(1, 2, 0))
            axes[row, 1].imshow(truth, vmin=0, vmax=1, cmap="gray")
            axes[row, 2].imshow(prediction, vmin=0, vmax=1, cmap="gray")
            axes[row, 0].set_title(name, fontsize=8)
            axes[row, 1].set_title("Target (gray = ignored)")
            axes[row, 2].set_title("Prediction" if model is not None else "Not predicted")
            for axis in axes[row]:
                axis.axis("off")
    fig.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=130)
    plt.close(fig)


def save_curves(history, path):
    """保存损失曲线和验证指标。

    Args:
        history (list): 每轮指标字典。
        path (str or Path): 输出图片路径。
    """
    epochs = [row["epoch"] for row in history]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for key in ["train_loss", "val_loss"]:
        axes[0].plot(epochs, [row[key] for row in history], label=key)
    for key in ["val_iou", "val_dice"]:
        axes[1].plot(epochs, [row[key] for row in history], label=key)
    for axis in axes:
        axis.set_xlabel("Epoch")
        axis.legend()
        axis.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
