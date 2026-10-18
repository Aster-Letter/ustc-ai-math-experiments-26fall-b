"""已提供：基础解码器、可运行演示模型与模型选择入口。"""
from torch import nn
from torch.nn import functional as F
from student_encoder import PetEncoder, ImprovedEncoder


class ProvidedDecoder(nn.Module):
    """将16×16的64通道特征恢复为128×128的单通道得分。"""

    def __init__(self):
        """注册三个上采样后的卷积及输出层。"""
        super().__init__()
        self.block2 = nn.Sequential(nn.Conv2d(64, 32, 3, padding=1), nn.ReLU())
        self.block1 = nn.Sequential(nn.Conv2d(32, 16, 3, padding=1), nn.ReLU())
        self.block0 = nn.Sequential(nn.Conv2d(16, 16, 3, padding=1), nn.ReLU())
        self.output = nn.Conv2d(16, 1, 1)

    def forward(self, features, output_size):
        """上采样只恢复尺寸，卷积负责学习如何组合特征。

        Args:
            features (Tensor): [B,64,16,16] 的最深层特征。
            output_size (tuple): 最终图片的高与宽。

        Returns:
            Tensor: [B,1,H,W] 的原始得分。
        """
        x = F.interpolate(features, scale_factor=2, mode="bilinear", align_corners=False)
        x = self.block2(x)
        x = F.interpolate(x, scale_factor=2, mode="bilinear", align_corners=False)
        x = self.block1(x)
        x = F.interpolate(x, size=output_size, mode="bilinear", align_corners=False)
        return self.output(self.block0(x))


class BasicSegmenter(nn.Module):
    """把学生编码器与统一解码器连接起来。"""

    def __init__(self, encoder):
        """保存两个可训练的子模块。

        Args:
            encoder (nn.Module): 返回三种尺度特征的编码器。
        """
        super().__init__()
        self.encoder = encoder
        self.decoder = ProvidedDecoder()

    def forward(self, images):
        """基础版只把最深层特征传给解码器。

        Args:
            images (Tensor): [B,3,H,W]。

        Returns:
            Tensor: [B,1,H,W]，不执行 sigmoid。
        """
        e1, e2, z = self.encoder(images)
        return self.decoder(z, images.shape[-2:])


def build_model(name):
    """按命令行选择模型。

    Args:
        name (str): demo、basic 或 improved。

    Returns:
        nn.Module: 指定模型；demo 仅用于验证训练流程，不作为T3答案。
    """
    if name == "demo":
        return nn.Sequential(nn.Conv2d(3, 8, 3, padding=1), nn.ReLU(),
                             nn.Conv2d(8, 1, 1))
    encoders = {"basic": PetEncoder, "improved": ImprovedEncoder}
    return BasicSegmenter(encoders[name]())
