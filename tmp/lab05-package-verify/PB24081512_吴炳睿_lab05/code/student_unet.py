"""进阶选做：复用基础编码器，在两个尺度上拼接跳跃特征。"""
import torch
from torch import nn
from torch.nn import functional as F
from student_encoder import PetEncoder


class SmallUNet(nn.Module):
    """两条跳跃连接的小型 U-Net，返回单通道原始得分。"""

    def __init__(self):
        super().__init__()
        self.encoder = PetEncoder()
        self.block2 = nn.Sequential(nn.Conv2d(64 + 32, 32, 3, padding=1), nn.ReLU())
        self.block1 = nn.Sequential(nn.Conv2d(32 + 16, 16, 3, padding=1), nn.ReLU())
        self.block0 = nn.Sequential(nn.Conv2d(16, 16, 3, padding=1), nn.ReLU())
        self.output = nn.Conv2d(16, 1, 1)

    def forward(self, images):
        e1, e2, z = self.encoder(images)
        up2 = F.interpolate(z, size=e2.shape[-2:], mode="bilinear", align_corners=False)
        d2 = self.block2(torch.cat([up2, e2], dim=1))
        up1 = F.interpolate(d2, size=e1.shape[-2:], mode="bilinear", align_corners=False)
        d1 = self.block1(torch.cat([up1, e1], dim=1))
        up0 = F.interpolate(d1, size=images.shape[-2:], mode="bilinear", align_corners=False)
        return self.output(self.block0(up0))
