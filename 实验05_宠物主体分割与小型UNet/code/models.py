"""已提供：编解码器连接、可运行演示模型与模型选择入口。"""
from torch import nn
from student_encoder import PetEncoder, ImprovedEncoder
from student_decoder import PetDecoder


class BasicSegmenter(nn.Module):
    """把学生编码器与学生解码器连接起来。"""

    def __init__(self, encoder):
        """保存两个可训练的子模块。

        Args:
            encoder (nn.Module): 返回三种尺度特征的编码器。
        """
        super().__init__()
        self.encoder = encoder
        self.decoder = PetDecoder()

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
