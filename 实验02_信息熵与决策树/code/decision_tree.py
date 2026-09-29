"""实验 02：基于信息增益的离散决策树课堂骨架。

主讲：钟志诚；整理：曾有成。
单位：中国科学技术大学 人工智能与数据科学学院。

只使用 Python 标准库。按 T1 → T7 补全，替换对应的 return None。
Args 是 Google 风格文档字符串的参数字段（即 params），Returns 是返回值字段。
TODO 表示待完成任务，Hint 给出提示。None 是占位符，不是合法预测类别。
未补全时演示会输出 None；补全后直接观察信息增益、树结构和预测结果。
运行：python decision_tree.py
原理、公式推导和手算见上一级目录的《实验02_从二叉树到决策树》讲义。
"""

from math import log2
from pprint import pprint


def load_watermelon():
    """读取内置的西瓜数据集 2.0，无需联网或额外文件。

    数据来源：《机器学习》（周志华）第 4 章表 4.1，第 76 页。
    原始 17 行、6 个离散属性全部保留；是/否编码为 1/0。
    编号仅用于追溯教材，绝不能加入 X 作为特征。

    Returns:
        tuple: (X, y, feature_names, original_ids)。X 为 17×6 的字符串
        二维列表；y 为长度 17 的整数列表；feature_names 为长度 6 的
        属性名称列表；original_ids 为长度 17 的教材原编号列表。
    """
    feature_names = ["色泽", "根蒂", "敲声", "纹理", "脐部", "触感"]
    # 每行：教材原编号、六个属性、标签。保持教材顺序。
    rows = [
        [1, "青绿", "蜷缩", "浊响", "清晰", "凹陷", "硬滑", 1],
        [2, "乌黑", "蜷缩", "沉闷", "清晰", "凹陷", "硬滑", 1],
        [3, "乌黑", "蜷缩", "浊响", "清晰", "凹陷", "硬滑", 1],
        [4, "青绿", "蜷缩", "沉闷", "清晰", "凹陷", "硬滑", 1],
        [5, "浅白", "蜷缩", "浊响", "清晰", "凹陷", "硬滑", 1],
        [6, "青绿", "稍蜷", "浊响", "清晰", "稍凹", "软粘", 1],
        [7, "乌黑", "稍蜷", "浊响", "稍糊", "稍凹", "软粘", 1],
        [8, "乌黑", "稍蜷", "浊响", "清晰", "稍凹", "硬滑", 1],
        [9, "乌黑", "稍蜷", "沉闷", "稍糊", "稍凹", "硬滑", 0],
        [10, "青绿", "硬挺", "清脆", "清晰", "平坦", "软粘", 0],
        [11, "浅白", "硬挺", "清脆", "模糊", "平坦", "硬滑", 0],
        [12, "浅白", "蜷缩", "浊响", "模糊", "平坦", "软粘", 0],
        [13, "青绿", "稍蜷", "浊响", "稍糊", "凹陷", "硬滑", 0],
        [14, "浅白", "稍蜷", "沉闷", "稍糊", "凹陷", "硬滑", 0],
        [15, "乌黑", "稍蜷", "浊响", "清晰", "稍凹", "软粘", 0],
        [16, "浅白", "蜷缩", "浊响", "模糊", "平坦", "硬滑", 0],
        [17, "青绿", "蜷缩", "沉闷", "稍糊", "稍凹", "硬滑", 0],
    ]
    X, y, original_ids = [], [], []
    for row in rows:
        original_ids.append(row[0])
        X.append(row[1:7])
        y.append(row[7])
    return X, y, feature_names, original_ids


class DecisionTree:
    """以信息增益选择属性的多叉分类树，只接受非空的离散属性数据。

    X 始终按样本行排列；切子集时保留原来的列顺序。
    y 的元素为 0 或 1；训练数据没有缺失值。先 fit，再 predict。
    属性增益相差不超过 1e-12 时保留候选列表中靠前的属性。
    不剪枝；零增益的非常量属性仍可继续划分。

    Attributes:
        root (dict or None): 根节点；未训练或 T5 未完成时为 None。
            节点统一有 feature、label、children 三个键。
            feature 为原始列编号，叶节点为 None；label 为当前节点多数类；
            children 为“属性值 → 子节点”的字典，叶节点为空字典。
    """

    def __init__(self):
        """初始化尚未训练的树；本方法已提供，无需补全。"""
        self.root = None

    def _entropy(self, y):
        """计算一组标签的信息熵，对应 T1。

        Args:
            y (list): 当前节点的标签，元素为 0 或 1。

        Returns:
            float: Ent(D)，单位为 bit；纯节点为 0.0。
            空列表约定返回 0.0，仅为便于计算，并非空集的概率分布。
        """
        # TODO T1：统计每类数量，再累加 -p_k * log2(p_k)。
        # 公式：p_k = count(k) / len(y); Ent(D) = -sum_k p_k log2(p_k)。
        # Hint：先处理空列表；用 y.count(k) 统计；p_k=0 时跳过该项。
        # 手算检查：[0, 1] → 1.0；[1, 1] → 0.0。
        return None

    def _majority_label(self, y):
        """选出当前节点的多数类，对应 T2。

        Args:
            y (list): 非空标签列表，元素为 0 或 1。

        Returns:
            int: 数量最多的标签；两类数量相等时固定返回 0。
        """
        # TODO T2：比较 0 和 1 的数量，返回多数类。
        # 公式：c* = argmax_{k in {0,1}} count(k)，平票选 0。
        # Hint：y.count(1) > y.count(0) 时返回 1，否则返回 0。
        return None

    def _information_gain(self, X, y, feature):
        """计算按一个离散属性分组后的信息增益，对应 T3。

        Args:
            X (list): 当前节点 N×d 的特征二维列表，N>0。
            y (list): 长度 N 的标签列表，与 X 逐行对应。
            feature (int): 待评估属性的原始列编号，范围 0 到 d-1。

        Returns:
            float: 父节点熵减去各子节点的加权熵，单位为 bit。
        """
        # TODO T3：枚举第 feature 列的不同取值，取出各分支标签。
        # 公式：Gain(D,j) = Ent(D) - sum_v |D_{j=v}|/|D| * Ent(D_{j=v})。
        # Hint：先用循环和 set 收集取值；再用 zip(X, y) 同步遍历。
        # 用 len(child_y)/len(y) 加权，调用 self._entropy(child_y)。
        # 注意：不能直接平均子节点熵；恒定属性的增益为 0。
        return None

    def _best_feature(self, X, y, features):
        """在当前仍可用且非常量的属性中选择最大信息增益，对应 T4。

        Args:
            X (list): 当前节点 N×d 的完整特征行，N>0。
            y (list): 长度 N 的标签列表。
            features (list): 仍可用的原始列编号，按固定顺序排列。

        Returns:
            int or None: 最优属性的原始列编号；无可划分属性时返回 None。
        """
        # TODO T4：只比较 features 中至少有两种取值的属性。
        # 公式：j* = argmax_{j in A, |values_j|>1} Gain(D,j)。
        # Hint：best_feature=None, best_gain=-float("inf")；用循环搜索。
        # 当 gain > best_gain + 1e-12 时更新；并列保留先遇到的属性。
        # 不因 gain==0 停止：零增益也可能是后续有效划分的入口。
        # 整张教材数据的答案应为列 3（纹理），而非返回“纹理”字符串。
        return None

    def _build_tree(self, X, y, features):
        """在当前非空样本子集上递归建树，对应 T5。

        Args:
            X (list): 当前节点 N×d 的特征行，N>0；不删除属性列。
            y (list): 当前节点的 N 个标签，与 X 一一对应。
            features (list): 当前路径尚未使用的原始列编号列表。

        Returns:
            dict: 包含 feature、label、children 的节点字典。
                叶节点示例：{"feature": None, "label": 0, "children": {}}。
        """
        # TODO T5：先建立默认叶节点，label 使用 self._majority_label(y)。
        # 停止条件：标签全相同；features 为空；或无非常量的候选属性。
        # Hint：len(set(y)) == 1 判断纯节点；用 _best_feature 选 j*。
        # 若继续划分，将节点 feature 设为 j*，按该列实际出现的值分组。
        # 递归关系：child_v = Build(D_{j*=v}, A 去掉 j*)。
        # Hint：每个分支用循环构造 child_X、child_y 和新的 remaining。
        # 只从 features 去掉 j*，不要删 X 的列，不要原地修改 features。
        # 将递归结果存入 node["children"][value]，最后返回 node。
        # 这里只创建非空分支；预测遇到不存在的分支由 T6 回退到多数类。
        return None

    def fit(self, X, y):
        """训练并保存根节点；本方法已提供，无需补全。

        Args:
            X (list): 非空训练集 N×d 的离散特征列表，d>0。
            y (list): 长度 N 的标签，元素为 0 或 1。

        Returns:
            DecisionTree: 返回自身，便于继续预测；需先补全 T5 才能得到训练树。
        """
        features = list(range(len(X[0])))
        self.root = self._build_tree(X, y, features)
        return self

    def _predict_one(self, x):
        """从根到叶遍历，为一个样本预测类别，对应 T6。

        Args:
            x (list): 长度 d 的特征行，列顺序与训练时一致。
                调用前需完成 fit；允许出现训练时该节点未见的属性值。

        Returns:
            int: 预测类别 0 或 1；未知分支返回当前节点的多数类。
        """
        # TODO T6：从 self.root 开始，用 while 循环沿分支走到叶节点。
        # 规则：若存在 child[x[j]] 则进入子节点；否则返回当前 label。
        # Hint：node["feature"] is None 表示叶节点，应返回 node["label"]。
        # 列编号 0 是合法属性，不能写 if not node["feature"] 来判断叶节点。
        # 不要用真实标签选路；不要修改树；不要把未知值擅自送进首个分支。
        return None

    def predict(self, X):
        """逐样本预测，保持输入行顺序，对应 T7。

        Args:
            X (list): M×d 的待预测特征列表；允许空列表。
                调用前需完成 fit，列顺序与训练时一致。

        Returns:
            list: 长度 M 的预测标签列表；输入为空时返回 []。
        """
        # TODO T7：遍历每一行，调用 self._predict_one(x)，追加到结果列表。
        # Hint：先写 predictions=[]，再用 for 和 append，最后返回列表。
        return None


def run_demo():
    """演示数据、信息增益、训练和预测；补全方法后观察各步输出。"""
    X, y, names, original_ids = load_watermelon()
    print("数据形状：", len(X), "行 ×", len(names), "列")
    print("好瓜：", y.count(1), "坏瓜：", y.count(0))
    model = DecisionTree()

    # 先计算根节点熵和各属性的信息增益，和讲义中的手算结果对照。
    print("根节点信息熵：", model._entropy(y))
    for feature, name in enumerate(names):
        print(name, "信息增益：", model._information_gain(X, y, feature))

    # 训练：由 fit 调用递归建树方法；feature 始终是原始列编号。
    model.fit(X, y)
    print("属性列顺序：", names)
    print("训练得到的树：")
    pprint(model.root, sort_dicts=False)

    # 推理：第 15 条记录对应下标 14，可对照讲义沿分支走到叶节点。
    print("教材编号", original_ids[14], "的特征：", X[14])
    print("预测类别：", model._predict_one(X[14]), "真实类别：", y[14])
    print("全部真实标签：", y)
    print("全部预测标签：", model.predict(X))
    print("本演示在同一批 17 条数据上训练和回代，不是测试集泛化表现。")


if __name__ == "__main__":
    run_demo()
