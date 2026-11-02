"""T3/T5：只用 PyTorch 基础层搭建编码器；每个 TODO 都有 Hint。"""
from torch import nn


class PetEncoder(nn.Module):
    """将图片编码为三种尺度的特征，供基础解码器使用并观察中间层尺寸。"""

    def __init__(self):
        """注册三个阶段；先完成基线，再做改进实验。"""
        super().__init__()
        # TODO T3.1: 3 -> 16 通道，128 -> 64 像素。
        # Hint: nn.Sequential 中依次放 Conv2d、ReLU、MaxPool2d。
        # 3×3 卷积使用 padding=1 保持尺寸；2×2 池化、stride=2 缩小一半。
        self.stage1 = nn.Sequential(nn.Conv2d(3, 16, kernel_size = 3, stride = 1, padding = 1), nn.ReLU(), nn.MaxPool2d(kernel_size = 2, stride = 2),)
        # TODO T3.2: 16 -> 32 通道，64 -> 32 像素。
        # Hint: 上一层 out_channels 必须等于这一层 in_channels。
        self.stage2 = nn.Sequential(nn.Conv2d(16, 32, kernel_size = 3, stride = 1, padding = 1), nn.ReLU(), nn.MaxPool2d(kernel_size = 2, stride = 2), )
        # TODO T3.3: 32 -> 64 通道，32 -> 16 像素。
        # Hint: 不要 Flatten，解码器还需要空间位置。
        self.stage3 = nn.Sequential(nn.Conv2d(32, 64, kernel_size = 3, stride = 1, padding = 1), nn.ReLU(), nn.MaxPool2d(kernel_size = 2, stride = 2), )

    def forward(self, images):
        """依次计算三个阶段。

        Args:
            images (Tensor): [B, 3, 128, 128]，像素范围为 0 到 1。

        Returns:
            tuple: e1、e2、z，形状分别为 [B,16,64,64]、
                [B,32,32,32]、[B,64,16,16]。
        """
        # TODO T3.4: 把下面的占位赋值改为依次调用三个阶段。
        # Hint: 第一个调用形如 self.stage1(images)；后一个接前一个的输出。
        e1 = self.stage1(images)
        e2 = self.stage2(e1)
        z = self.stage3(e2)
        return e1, e2, z


class ImprovedEncoder(PetEncoder):
    """T5：保留基线代码，在这里记录一个可解释的结构改动。"""

    def __init__(self):
        """继承基线后，替换需要改动的阶段。"""
        super().__init__()
        # T5.1: 仅在第一阶段的卷积与 ReLU 之间加入 BN。
        # BN 对 16 个输出通道分别归一化，不改变三个阶段的输出尺寸。
        # 对照训练使用相同的数据划分、训练轮数和种子。
        self.stage1 = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
