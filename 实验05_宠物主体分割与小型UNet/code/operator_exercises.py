"""T2：观察一个可运行例子，再补全三个小函数。"""
import torch
from torch.nn import functional as F


def correlate2d(image, kernel):
    """计算无填充、步长为1的单通道互相关（深度学习中的卷积）。

    Args:
        image (Tensor): 二维输入矩阵。
        kernel (Tensor): 二维卷积核，不翻转。

    Returns:
        Tensor: 高和宽分别为 H-KH+1、W-KW+1 的输出。
    """
    height, width = image.shape
    kh, kw = kernel.shape
    result = torch.zeros(height-kh+1, width-kw+1)
    # TODO T2.1: 用两层循环遍历输出位置，截取窗口，逐元素乘并求和。
    # Hint: window = image[row:row+kh, col:col+kw]。
    # 讲义例子左上角的结果为 -4。
    return result


def relu(values):
    """将负数变为0，非负数保持不变。

    Args:
        values (Tensor): 任意形状的数值。

    Returns:
        Tensor: 与输入形状相同的激活值。
    """
    # TODO T2.2: 返回逐元素 max(0, x)。
    # Hint: 可以使用 torch.clamp；不要修改原输入。
    return values


def max_pool2d(image):
    """做2×2、步长2的最大池化；边缘不足一个窗口时舍去。

    Args:
        image (Tensor): 二维矩阵。

    Returns:
        Tensor: 高和宽各减半并向下取整的二维矩阵。
    """
    height, width = image.shape
    result = torch.zeros(height//2, width//2)
    # TODO T2.3: 遍历2×2窗口，把窗口最大值填入输出。
    # Hint: 第(row,col)个窗口从输入的(2*row,2*col)开始。
    return result


if __name__ == "__main__":
    # 先运行这个完整例子，观察结果，再修改一个输入值。
    image = torch.arange(1, 10, dtype=torch.float32).reshape(1, 1, 3, 3)
    kernel = torch.tensor([[[[1., 0.], [0., -1.]]]])
    print("input:", image[0, 0])
    print("PyTorch convolution:", F.conv2d(image, kernel)[0, 0])
    print("Your convolution:", correlate2d(image[0, 0], kernel[0, 0]))
