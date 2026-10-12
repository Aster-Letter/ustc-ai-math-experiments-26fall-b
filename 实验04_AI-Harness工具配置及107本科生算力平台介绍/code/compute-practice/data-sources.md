# CIFAR-10 数据来源与校验

- 原始项目：[CIFAR-10 / CIFAR-100](https://cave.cs.toronto.edu/kriz/cifar.html)。引用 Alex Krizhevsky, *Learning Multiple Layers of Features from Tiny Images*, 2009。
- Python 原始包：[cifar-10-python.tar.gz](https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz)，170498071 字节，原始 MD5 为 `c58f30108f718f92721af3b95e74349a`。
- 包内文件校验值参照 [TorchVision v0.22.1 CIFAR10 实现](https://github.com/pytorch/vision/blob/v0.22.1/torchvision/datasets/cifar.py)。
- `prepare_data.py` 仅校验和解包已经下载的原始包；MD5 用于对照和排查传输损坏，下载来源仍应核对。
- 训练脚本不在线下载数据或预训练权重，代码包不包含数据、环境与训练模型。
- 使用官方训练集的固定 45000/5000 划分，smoke 与 train 取同一划分的不同规模；官方测试集不参与训练或选模。

首次需要完整原始包，少样本配置只减少训练样本数，不减少原始下载量。当前机器能够获取原始包，不代表所有学生网络都能达到相同速度；可在本地下载后通过平台文件管理上传。
