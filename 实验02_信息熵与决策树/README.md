# 实验 02：从二叉树到决策树

主讲：钟志诚。整理：曾有成。

单位：中国科学技术大学 人工智能与数据科学学院。

本次实验从二叉树和二叉搜索树出发，学习决策树的预测过程，用信息熵和信息增益选择划分属性，并补全一个 Python 决策树程序。

## 材料入口

- [实验讲义（PDF）](实验02_从二叉树到决策树.pdf) · [LaTeX 源文件](实验02_从二叉树到决策树.tex)：概念、例题、练习与参考解答。
- [决策树代码](code/decision_tree.py)：内置西瓜数据，需按 T1–T7 补全。
- [Python 语法带练](Python语法带练.md) · [分章脚本](code/python_syntax/README.md)：复习列表、字典、函数、类和文件读取。

需要复习基础语法时，可先运行分章脚本；已有基础的同学可直接阅读讲义并开始决策树练习。

## 实验准备

本次实验只使用 Python 标准库，沿用实验 01 的 `ustc-ai-experiments-26fall-B` 环境即可，无需另外安装库。每次新开终端后，先激活环境：

```bash
conda activate ustc-ai-experiments-26fall-B
python -c "import sys; print(sys.executable)"
```

第二条命令显示当前 Python 的位置，可用来确认环境是否选对。使用 VS Code 或 Jupyter 时，也要选择该环境对应的解释器或内核；切换代码目录不会自动切换 Python 环境。

后续实验可以按下面的方式管理环境：

- **基础实验继续沿用。** 使用 NumPy、Matplotlib、scikit-learn 等已有库时，无需每次重建环境；需要新库时，先激活环境，再按实验说明用 `python -m pip` 安装。
- **特殊依赖单独配置。** 后续若使用 PyTorch、图神经网络扩展库，或要求不同的 Python／库版本，建议为该实验新建环境，保留当前可用的课程环境。具体版本和 CPU／GPU 安装方式以届时的实验说明为准，不必现在提前安装。
- **保留安装记录。** 记下环境名称和额外安装的库；若实验提供 `requirements.txt` 或 `environment.yml`，优先按配套说明配置，避免为了运行新实验而反复升级、降级旧环境中的库。

忘记已有环境名称时，可运行 `conda env list` 查看。更多操作见 [Conda 环境管理文档](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html)。

## 运行方法

在本实验 `code/` 目录运行：

```bash
python decision_tree.py
```

初始代码中的待补方法返回 `None`，因此首次运行会看到部分输出为 `None`。补全后，程序将输出各属性的信息增益、训练得到的树和预测标签。

语法脚本可以单独运行，例如：

```bash
python python_syntax/01_getting_started.py
python python_syntax/10_read_files.py
```

## 实验练习

先结合讲义完成手算与路径分析，再按顺序补全代码中的 `TODO`。`__init__`、`fit`、数据和演示函数已提供。

| 任务 | 方法 | 需要实现的功能 |
|------|------|----------------|
| T1 | `_entropy` | 计算标签的信息熵 |
| T2 | `_majority_label` | 返回多数类，平票选 0 |
| T3 | `_information_gain` | 按属性分组，计算信息增益 |
| T4 | `_best_feature` | 选择信息增益最大的可划分属性 |
| T5 | `_build_tree` | 判断终止条件，递归建立子树 |
| T6 | `_predict_one` | 沿树的分支预测一个样本 |
| T7 | `predict` | 按输入顺序返回所有样本的预测结果 |

每完成一个方法，用小样例检查结果，再对照讲义中的西瓜数据运行。完整数据应选择纹理作为根节点，其信息增益约为 `0.380592`。本次不另行要求提交报告。

## 数据与实现约定

西瓜数据来自周志华《机器学习》第 4 章表 4.1，共 17 条记录、6 个离散属性；好瓜与坏瓜分别编码为 1 和 0，教材编号不参与划分。语法练习中的[文本样例](code/python_syntax/data/watermelon_samples.txt)只含其中 4 条记录，用于练习文件读取。

离散属性、多叉划分、不剪枝；节点保存原始列编号，只从候选列表移除已用属性，不删特征列。多数类平票选 0，增益相差不超过 `1e-12` 时按候选顺序处理并列。零增益的非常量属性仍可继续划分。未知分支返回当前节点的多数类。

程序使用同一批 17 条记录训练并回代预测，结果用于核对实现，不能代替独立测试集上的评估。
