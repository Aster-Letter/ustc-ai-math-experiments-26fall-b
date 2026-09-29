"""09 类：实例、属性和方法（教材第 9 章，选讲 9.1–9.2）。

主讲：钟志诚；整理：曾有成。
单位：中国科学技术大学 人工智能与数据科学学院。
配套讲稿：../../Python语法带练.md。
在本目录运行：python 09_classes.py
本文件可独立运行，只依赖 Python 标准库。
"""

print("\n09 类")


class TreeNode:
    """用最少的属性演示一个节点对象，不负责学习或训练。

    Attributes:
        label (int): 节点保存的类别 0 或 1。
        feature (int or None): 属性列编号；None 表示叶节点。
    """

    def __init__(self, label, feature=None):
        """初始化当前节点的类别和属性列。

        Args:
            label (int): 需要保存的类别。
            feature (int or None): 属性列编号；默认 None 表示叶节点。
        """
        self.label = label
        self.feature = feature

    def is_leaf(self):
        """判断当前节点是否是叶节点。

        Returns:
            bool: feature 为 None 时返回 True，否则返回 False。
        """
        return self.feature is None


first = TreeNode(label=0)
second = TreeNode(label=1, feature=3)
print("第一个节点：", first.label, first.is_leaf())
print("第二个节点：", second.label, second.is_leaf())
second.feature = None
print("修改第二个节点后：", second.is_leaf(), "；第一个节点类别：", first.label)
# 修改练习：令 second.feature = 0，is_leaf() 应为 False。
