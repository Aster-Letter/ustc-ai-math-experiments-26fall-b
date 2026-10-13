# CIFAR-10 数据来源与准备

- 原始项目：[CIFAR-10 / CIFAR-100](https://cave.cs.toronto.edu/kriz/cifar.html)。引用 Alex Krizhevsky, *Learning Multiple Layers of Features from Tiny Images*, 2009。
- Python 原始包：[cifar-10-python.tar.gz](https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz)，约 163 MiB。
- `prepare_data.py` 自动检查并解包已下载的数据，无需手动对比校验值。文件清单依据 [TorchVision v0.22.1 CIFAR10 实现](https://github.com/pytorch/vision/blob/v0.22.1/torchvision/datasets/cifar.py)。
- 训练脚本不在线下载数据或预训练权重，代码包不包含数据、环境与训练模型。
- 使用官方训练集的固定 45000/5000 划分，smoke 与 train 取同一划分的不同规模；官方测试集不参与训练或选模。

首次需要完整原始包，少样本配置只减少训练样本数，不减少原始下载量。当前机器能够获取原始包，不代表所有学生网络都能达到相同速度；可在本地下载后通过平台文件管理上传。
