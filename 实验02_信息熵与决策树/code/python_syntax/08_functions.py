"""08 函数与导入（教材第 8 章）。

主讲：钟志诚；整理：曾有成。
单位：中国科学技术大学 人工智能与数据科学学院。
配套讲稿：../../Python语法带练.md。
在本目录运行：python 08_functions.py
本文件可独立运行，只依赖 Python 标准库。
"""

print("\n08 函数与导入")


def label_name(label, good_name="好瓜"):
    """将二分类标签转换为便于阅读的名称。

    Args:
        label (int): 类别标签，约定为 0 或 1。
        good_name (str): 标签为 1 时使用的名称，默认为“好瓜”。

    Returns:
        str: 类别名称。
    """
    if label == 1:
        return good_name
    return "坏瓜"


def count_good(labels):
    """练习：计算好瓜的数量，留给学生补全。

    Args:
        labels (list): 由整数 0 和 1 组成的标签列表。

    Returns:
        int: 标签为 1 的样本数；空列表返回 0。
    """
    # TODO S1：用显式循环统计标签 1 的个数，替换 return None。
    # Hint：计数器从 0 开始；for 遍历；if 判断；满足条件时加 1。
    # 手算：[1, 1, 0, 0] 返回 2，[] 返回 0。
    return None


name = label_name(1)
print("位置实参：", name)
print("关键字实参：", label_name(label=1, good_name="合格瓜"))
result = count_good([1, 1, 0, 0])
if result is None:
    print("[待完成 S1] 请补全 count_good；预期结果为 2。")
else:
    print("S1 返回值：", result, "；预期：2")

from math import log2

print("导入标准库函数：log2(2) =", log2(2))
# 导入放在这里是为了配合讲解顺序；正式整理脚本时通常放在文件开头。
