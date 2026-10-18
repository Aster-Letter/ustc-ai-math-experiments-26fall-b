"""已提供：边界忽略、逐图损失以及前景重合指标。"""
import torch
from torch.nn import functional as F


def masked_loss(logits, targets, valid):
    """先在每张图的有效像素上平均，再对批量取平均。

    Args:
        logits (Tensor): [B,1,H,W] 的原始得分。
        targets (Tensor): 同形状，宠物1、背景0。
        valid (Tensor): 同形状，有效像素1、不确定边界0。

    Returns:
        Tensor: 标量损失，可用于 backward；全忽略图的贡献为0。
    """
    pixel_loss = F.binary_cross_entropy_with_logits(logits, targets, reduction="none")
    count = valid.sum(dim=(1, 2, 3)).clamp_min(1)
    per_image = (pixel_loss * valid).sum(dim=(1, 2, 3)) / count
    return per_image.mean()


def foreground_scores(logits, targets, valid):
    """逐图计算前景 IoU 和 Dice，预测阈值固定为0.5。

    Args:
        logits (Tensor): [B,1,H,W] 的原始得分。
        targets (Tensor): 同形状，二元标签。
        valid (Tensor): 同形状，有效像素掩码。

    Returns:
        tuple: 长度均为B的 IoU、Dice 张量；双方前景都空时取1。
    """
    predicted = (logits >= 0) & valid.bool()
    truth = targets.bool() & valid.bool()
    dims = (1, 2, 3)
    intersection = (predicted & truth).sum(dims).float()
    union = (predicted | truth).sum(dims).float()
    total = predicted.sum(dims).float() + truth.sum(dims).float()
    iou = torch.where(union > 0, intersection / union.clamp_min(1), 1.)
    dice = torch.where(total > 0, 2*intersection / total.clamp_min(1), 1.)
    return iou, dice
