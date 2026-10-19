"""T4：完成三次上采样、卷积特征融合与单通道输出头。"""
from torch import nn
from torch.nn import functional as F


class PetDecoder(nn.Module):
    """把[B,64,16,16]特征恢复为[B,1,128,128]原始得分。"""

    def __init__(self):
        """注册三个卷积块和一个输出头。"""
        super().__init__()
        # TODO T4.1: 补全三个保持空间尺寸的卷积块。
        # Hint: 每块使用 nn.Sequential(卷积, ReLU)，卷积为3×3、padding=1。
        # block2: 64 -> 32；block1: 32 -> 16；block0: 16 -> 16。
        self.block2 = nn.Identity()
        self.block1 = nn.Identity()
        self.block0 = nn.Identity()
        # TODO T4.2: 用1×1卷积把16通道映射为1通道。
        # Hint: 输出是原始得分，损失函数内部处理sigmoid。
        self.output = nn.Identity()

    def forward(self, features, output_size):
        """依次恢复空间尺寸并生成原始得分。

        Args:
            features (Tensor): [B,64,16,16]最深层特征。
            output_size (tuple): 最终图片的高、宽，本实验为(128,128)。

        Returns:
            Tensor: [B,1,128,128]原始得分。
        """
        # TODO T4.3: 将三处占位上采样改为F.interpolate。
        # Hint: 前两次用scale_factor=2，最后一次用size=output_size；
        # mode="bilinear", align_corners=False。上采样保持通道数。
        up2 = features                 # 目标：[B,64,32,32]
        # TODO T4.4: 依次调用block2、block1、block0和output。
        # Hint: d2 = self.block2(up2)；后续卷积块接上一次上采样结果。
        d2 = up2                       # 目标：[B,32,32,32]
        up1 = d2                       # 目标：[B,32,64,64]
        d1 = up1                       # 目标：[B,16,64,64]
        up0 = d1                       # 目标：[B,16,128,128]
        d0 = up0                       # 目标：[B,16,128,128]
        logits = d0                    # 目标：[B,1,128,128]
        return logits
