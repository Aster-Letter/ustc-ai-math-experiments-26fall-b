# 实验 02 · Python 语法带练：从第一行代码到读取西瓜数据

主讲：钟志诚。整理：曾有成。

单位：中国科学技术大学 人工智能与数据科学学院。

这份材料供教师打开 Markdown 对照讲解，配套 [分章脚本](code/python_syntax/README.md) 现场运行和修改。章节顺序参照《Python 编程：从入门到实践（第 3 版）》第 1–9 章，最后停在 **10.1“读取文件”**。选讲本次实验需要的语法，不逐小节复述教材；示例围绕西瓜记录重新编写。

学习目标：能读懂列表和字典中的数据；能用条件与循环筛选记录；能区分参数、返回值、实例和方法；能把文本文件读成决策树需要的特征行与标签。第 9 章选讲类的基础，不展开继承；不安排 10.2 之后的文件写入、异常处理、数据存储和测试框架。

## 讲课前的准备

1. 将本实验文件夹完整保留，尤其是 `code/python_syntax/data/watermelon_samples.txt`。只用 Python 标准库。
2. 打开 `code/python_syntax/`，按文件名前的 01–10 顺序讲解。每章是独立的普通脚本，例如运行 `python 01_getting_started.py`；也可在编辑器中打开对应文件后直接运行或打断点。
3. 按“先猜结果 → 教师手敲 → 运行观察 → 学生改一个值 → 口头检查”推进。每个初始脚本都能单独运行，仅 S1、S2 留作学生练习；显示“待完成 S1”是正常现象，不代表函数已经实现。
4. 第 7 节默认模拟输入，避免运行时停住。讲 `input()` 时再把 `ENABLE_INPUT` 改为 `True`，按提示输入整数。第 10 节使用 `__file__`，请运行保存好的 `.py` 文件；直接粘贴到交互控制台时通常没有这个变量。

这些脚本用于课堂逐章演示，顶层示例会立即执行。每个文件都包含本章需要的变量和定义，不依赖其他文件先运行；S1、S2 也可以分别练习。

**数据约定：** 配套文本选取西瓜书表 4.1 原编号 **1、2、9、11**，保留全部六个属性，好瓜“是/否”编码为 1/0。四条子集只用来练语法，不是训练／测试划分。人工价格 `3.5`、临时修改的列表和简化节点结构都只是语法示例。原编号不作为模型特征。

## 建议课堂安排

下表是独立的 **135 分钟语法带练路线**，包含学生修改与反馈。它可作为决策树实现前的准备课，不与原决策树路线的 135 分钟直接叠加。若两者必须在同一次课完成，可只选第 4、6、8、9、10 节的检查点做 30–40 分钟复习，再相应减少决策树现场补全的任务量。

| 时间 | 教材对应 | 教师活动 | 学生当场产出 |
|---|---|---|---|
| 0–5（5 分钟） | 第 1 章 起步 | 运行脚本、保存后重跑 | 打印自己的消息 |
| 5–15（10 分钟） | 第 2 章 变量和简单的数据类型 | 字符串与数值对比 | 解释 `"1"` 与 `1` |
| 15–25（10 分钟） | 第 3 章 列表简介 | 取值、修改、排序 | 找到最后一个索引 |
| 25–40（15 分钟） | 第 4 章 操作列表 | 逐轮跟踪循环与复制 | 算出好瓜数，保留原候选列表 |
| 40–50（10 分钟） | 第 5 章 if 语句 | 比较、成员判断与 None | 正确区分列 0 和叶节点 |
| 50–65（15 分钟） | 第 6 章 字典 | 字典、嵌套与配对 | 沿两层键找到标签 |
| 65–75（10 分钟） | 第 7 章 用户输入和 while 循环 | 输入转换、循环停止 | 指出退出条件与更新语句 |
| 75–95（20 分钟） | 第 8 章 函数 | 参数、return、导入 | 补全 S1 并检查两种输入 |
| 95–110（15 分钟） | 第 9 章 类 | 创建两个实例、修改属性 | 解释 self，区分两对象状态 |
| 110–130（20 分钟） | 10.1 读取文件 | 定位文件、拆行、转类型 | 得到 4×6 特征和 4 个标签 |
| 130–135（5 分钟） | 综合回顾 | 退出卡与答疑 | 口述文本到数据的处理过程 |

合计：5+10+10+15+10+15+10+20+15+20+5=135 分钟。每个模块都保留预测输出、修改和检查的时间。

## 对照讲解

以下代码与配套脚本逐章对应，每节标题下都有同编号文件的链接。

## 01 起步：打印一条消息（教材第 1 章）

对应脚本：[01_getting_started.py](code/python_syntax/01_getting_started.py)

**教师先讲：** 程序按顺序执行。`print(...)` 把括号里的内容显示到控制台；字符串要用成对引号。`#` 后面是注释，不参与执行。先确认“保存文件”和“运行文件”是两步。

```python
print("01 起步")
print("开始整理西瓜记录")
# 修改练习：把消息改成自己的名字，再保存、重新运行。
```

**预期观察：** 输出 `01 起步` 和 `开始整理西瓜记录`。

**现场检查：** 改成自己的名字并重跑。如果输出没变，先检查是否保存、运行的是不是当前文件。此阶段只排查运行流程，不重新安装整套环境。

## 02 变量和简单的数据类型（教材第 2 章）

对应脚本：[02_variables.py](code/python_syntax/02_variables.py)

**教师先讲：** 变量名是指向值的名字，`=` 是赋值。`str` 表示字符串、`int` 表示整数、`float` 表示浮点数。`type()` 用来观察类型；`f"...{变量}..."` 把变量放进字符串。`strip()` 返回去掉两端空白的新字符串，原字符串不会被原地修改；`repr()` 让引号和空白更容易看清。

```python
print("\n02 变量和简单的数据类型")
color = "青绿"
sample_id = 1
price = 3.5  # 人工设置的价格，仅用于演示浮点数，不是教材特征。
label = 1
print(type(color), type(sample_id), type(price))
print(f"编号 {sample_id} 的西瓜，色泽为{color}")
print("每只价格：", price, "；两只价格：", price * 2)
raw_color = "  青绿  "
print("原文本：", repr(raw_color), "；清理后：", raw_color.strip())
print("除法：", 5 / 2, "整除：", 5 // 2, "余数：", 5 % 2)
print("字符串拼接：", "1" + "1", "；数值相加：", int("1") + 1)
# 修改练习：把 label 改为 0；观察赋值会改变哪个变量。
```

**预期观察：** 两只价格为 `7.0`；`5 / 2` 为 `2.5`，`5 // 2` 为 `2`，`5 % 2` 为 `1`；`"1" + "1"` 为字符串 `"11"`，`int("1") + 1` 为整数 `2`。浮点数不保证所有十进制小数都能精确表示，本次先观察类型与运算。

**现场检查：** `raw_color.strip()` 之后再打印 `raw_color`，两端空格还在吗？参考：还在；若要保留清理结果，需要赋值。

**衔接决策树：** 特征值可能是中文字符串，标签需要整数；读文件后必须主动转换标签。

## 03 列表简介（教材第 3 章）

对应脚本：[03_lists.py](code/python_syntax/03_lists.py)

**教师先讲：** 方括号创建列表，逗号分隔元素。索引从 0 开始，负索引 `-1` 表示最后一项；`len()` 返回元素数量。`append()` 加到末尾，`pop()` 删除并返回末项。`sorted()` 返回新列表，`sort()` 修改原列表。

```python
print("\n03 列表简介")
colors = ["青绿", "乌黑", "浅白"]
print("首项：", colors[0], "；末项：", colors[-1], "；长度：", len(colors))
colors.append("青绿")
removed = colors.pop()
print("弹出的元素：", removed, "；剩余：", colors)
colors[0] = "浅白"  # 只修改语法示例，不修改配套数据文件。
print("修改后的首项：", colors[0])
ids = [9, 1, 11, 2]
print("sorted 的返回值：", sorted(ids), "；原列表：", ids)
ids.sort()
print("sort 修改原列表：", ids)
# 观察练习：为什么最后一个有效索引是 len(colors)-1？
```

**预期观察：** 最初的首项是青绿、末项是浅白，长度为 3。添加再弹出后回到三项。`sorted(ids)` 得到 `[1, 2, 9, 11]`，但原 `ids` 仍为 `[9, 1, 11, 2]`；调用 `ids.sort()` 后原列表才改变。

**现场检查：** 三项列表能否读取 `colors[3]`？参考：不能，有效索引为 0、1、2。可以口述或现场看一次报错的最后一行，不安排异常处理代码。

**易错提醒：** 不要写 `ids = ids.sort()`；`sort()` 的返回值是 `None`。

## 04 操作列表：循环、切片、复制和元组（教材第 4 章）

对应脚本：[04_loops_and_slices.py](code/python_syntax/04_loops_and_slices.py)

**教师先讲：** `for item in labels:` 每次取一个元素；冒号后的缩进块重复执行。计数器放在循环前，每轮更新，最后在循环外总结。`range(4)` 生成 0、1、2、3。切片不包含右端位置。元组用圆括号表达，其元素位置不能重新赋值。

```python
print("\n04 操作列表")
labels = [1, 1, 0, 0]  # 对应教材原编号 1、2、9、11 的标签。
total = 0
for item in labels:
    total += item
    print("本次标签：", item, "；累计好瓜数：", total)
print("循环结束，好瓜数：", total)
print("range(4)：", list(range(4)))
print("前两项：", labels[:2], "；从第 3 项开始：", labels[2:])

features = [0, 1, 2, 3, 4, 5]
alias = features
copied = features.copy()
copied.remove(3)
print("原候选列：", features, "；副本：", copied)
print("alias 与 features 是同一个对象：", alias is features)
shape = (4, 6)
print("元组保存形状：", shape)
# 修改练习：将上面的 total += item 临时移到循环外，预测输出再运行。
# 提醒：copy() 在此复制一维列表；嵌套列表的内层对象仍会共享。
```

**预期观察：** 累计好瓜数依次为 1、2、2、2；前两项为 `[1, 1]`。复制后的候选列没有 3，原候选列仍有 3。

**现场检查：** 若将 `total += item` 移到循环外会怎样？参考：只对最后一次留下的 `item=0` 累加，最终为 0，而不是 2。若 `alias.remove(3)` 又会怎样？参考：`alias` 和 `features` 指向同一列表，原列表也会变化。

**易错提醒：** 这里的 `is` 检查是否同一个对象；比较两个列表的内容是否相等用 `==`。浅复制只复制最外层，不能据此认为嵌套列表也全部独立。

**衔接决策树：** 给不同子树准备候选属性时创建新列表；不要让一个分支修改另一个分支的候选列表。

## 05 if 语句（教材第 5 章）

对应脚本：[05_conditions.py](code/python_syntax/05_conditions.py)

**教师先讲：** `==` 比较值，结果为布尔值 `True` 或 `False`；`if/elif/else` 只进入第一个成立的分支。`and` 要求两个条件都成立，`or` 要求至少一个成立。`in` 检查成员，`not` 取反。`None` 表示这里没有属性编号。

```python
print("\n05 if 语句")
label = 0
if label == 1:
    print("好瓜")
elif label == 0:
    print("坏瓜")
else:
    print("标签应为 0 或 1")

texture = "清晰"
print("相等判断：", texture == "清晰")
print("是否在取值列表中：", texture in ["清晰", "稍糊", "模糊"])
print("两个条件都成立：", label == 0 and texture == "清晰")
print("至少一个条件成立：", label == 1 or texture == "清晰")
feature = 0
print("列编号 0 是 None 吗：", feature is None)
remaining = []
if not remaining:
    print("没有剩余候选属性")
# 修改练习：把 feature 改为 None，重新运行最后两条判断。
```

**预期观察：** `label=0` 输出坏瓜；`texture` 在候选取值中；`feature=0` 时 `feature is None` 为 `False`；空候选列表进入 `if not remaining`。

**现场检查：** 为什么不能用 `if not feature` 判断叶节点？参考：整数 0 在条件判断中也被视为假，而第 0 列是合法特征。必须使用 `feature is None`。

**边界说明：** 本段只是把现有标签翻译成文字，不是在用一条手写规则训练分类器。

## 06 字典与嵌套（教材第 6 章；附决策树所需的小工具）

对应脚本：[06_dictionaries.py](code/python_syntax/06_dictionaries.py)

**教师先讲：** 字典用“键 → 值”查找信息，方括号中放键而非列表位置。`get(键, 默认值)` 可在键不存在时得到指定值，`items()` 同时给出键与值。值还可以是字典，从而表示一个节点的各个分支。

**语法补充：** 为后面的决策树补充 `set`、`enumerate` 和 `zip`：分别用于去重、同时得到行索引和元素、把等长特征与标签按位置配对。这是本实验的补充，不将三者另称为教材章节。集合不依赖显示顺序，不能用下标索引。

```python
print("\n06 字典与嵌套")
record = {"original_id": 1, "color": "青绿", "label": 1}
print("查标签：", record["label"])
print("不存在的备注：", record.get("note", "暂无备注"))
record["note"] = "课堂观察"
for key, value in record.items():
    print(key, "->", value)

leaf = {"feature": None, "label": 0, "children": {}}
node = {"feature": 3, "label": 0, "children": {"模糊": leaf}}
print("模糊分支的类别：", node["children"]["模糊"]["label"])
# 上面的单分支字典仅演示嵌套结构，不是一棵训练完成的决策树。

textures = ["清晰", "清晰", "稍糊", "模糊"]
labels = [1, 1, 0, 0]
print("不同纹理：", sorted(set(textures)))
for index, value in enumerate(textures):
    print("行索引：", index, "；纹理：", value)
for value, label in zip(textures, labels):
    print("对应的一对：", value, label)
# set 去重且无索引顺序保证；sorted 只是让显示顺序固定。
# zip 按位置配对，并在最短输入耗尽时停止；样本和标签长度应一致。
```

**预期观察：** 第一次读取备注得到“暂无备注”，随后添加备注；沿 `node["children"]["模糊"]["label"]` 得到 0；四个纹理去重后只剩三种。

**现场检查：** 如果 `zip` 的两边分别有 4 项和 3 项，会产生几对？参考：3 对，默认不会因为长度不同而报错。所以特征行与标签要保持一一对应。

**衔接决策树：** `set` 对应不同属性值；`zip` 防止手工分别遍历时错配标签；嵌套字典对应当前决策树骨架中的节点。

## 07 用户输入和 while 循环（教材第 7 章）

对应脚本：[07_input_and_while.py](code/python_syntax/07_input_and_while.py)

**教师先讲：** `input()` 返回字符串，输入看起来像数字也一样；计算之前要用 `int()` 转换。`while` 每次先判断条件，再执行循环体；循环体必须推动状态变化。`break` 结束整个循环。

**演示方式：** 先保留 `ENABLE_INPUT=False` 看固定结果，再改成 `True` 输入 `3`。本节先约定输入整数文本，让学生认识转换；不增加异常捕获和反复重输的框架。

```python
print("\n07 用户输入和 while 循环")
ENABLE_INPUT = False  # 现场演示 input 时改为 True；默认本文件直接跑完。
if ENABLE_INPUT:
    text = input("请输入好瓜的数量（整数，例如 2）：")
else:
    text = "2"  # 模拟键盘输入，类型仍然是 str。
count = int(text)
print("输入文本：", repr(text), "；加 1 后：", count + 1)

index = 0
labels = [1, 1, 0, 0]
while index < len(labels):
    print("while 访问：", index, labels[index])
    index += 1

index = 0
while index < len(labels):
    if labels[index] == 0:
        print("找到第一个坏瓜，行索引：", index)
        break
    index += 1
# 讨论：删除第一段循环的 index += 1 会怎样？只口述，不运行无限循环。
```

**预期观察：** 默认文本为 `'2'`，加 1 后为 3；第一段循环访问索引 0、1、2、3；第二段在索引 2 找到第一个坏瓜并停止。

**现场检查：** 第一段循环的条件、更新、退出分别是什么？参考：`index < len(labels)`、`index += 1`、`index` 达到 4 时退出。删除更新会导致无限循环，只分析原因，不现场运行这个错误。

**衔接决策树：** 遍历已知样本适合 `for`；从当前节点不断前进到叶节点适合 `while`。

## 08 函数与导入（教材第 8 章）

对应脚本：[08_functions.py](code/python_syntax/08_functions.py)

**教师先讲：** `def` 定义一个可重复使用的步骤，定义不会立即执行函数体，调用时才执行。定义中的 `label` 是形参，调用传入的 `1` 是实参；`good_name` 有默认值。`return` 将结果交给调用者并结束本次调用，`print` 只负责显示，不代替返回值。

三引号内是文档字符串。按 Google 风格用 `Args:` 说明参数（即 params），用 `Returns:` 说明返回值。`None` 在 S1 中是未完成占位值；完成后应返回整数。

`from math import log2` 表示从标准库模块中导入指定函数。模块导入用于复用已有功能，不需要额外安装这里的 `math`。

```python
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
```

**预期观察：** 两次名称分别为“好瓜”“合格瓜”；S1 默认打印待完成提示；`log2(2)` 为 `1.0`。这里只认识导入与调用，信息熵公式在《从二叉树到决策树》讲义中再解释。

**学生任务 S1：** 用显式循环补全 `count_good`，检查 `[1,1,0,0] → 2`、`[0,0] → 0`、`[] → 0`。先让学生写，再看文末教师答案。

**现场检查：** 若函数只打印计数而没有 `return`，`result` 是什么？参考：`None`。将 `return` 错放在循环内，会过早结束。

## 09 类：实例、属性和方法（教材第 9 章，选讲 9.1–9.2）

对应脚本：[09_classes.py](code/python_syntax/09_classes.py)

**教师先讲：** 类描述一类对象共同有哪些数据和操作；实例是按类创建的具体对象。`TreeNode(...)` 创建实例并执行 `__init__` 初始化；`self` 表示当前实例。`self.label` 是该实例的属性，`is_leaf()` 是实例的方法。

调用 `first.is_leaf()` 时，Python 自动把 `first` 作为 `self` 传入，调用者不用再手工传一次。`__init__` 只初始化实例，不写 `return self`。

```python
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
```

**预期观察：** 第一个节点输出 `0 True`，第二个输出 `1 False`；把第二个的 `feature` 改为 `None` 后，它也成为叶节点，但第一个实例的类别仍为 0。

**现场检查：** 把 `second.feature` 改为 0，`second.is_leaf()` 应为 `False`。说明 `feature=0` 与 `feature=None` 不同。

**衔接决策树：** `TreeNode` 只用于认识类，不需要把原骨架改成节点类；原 `DecisionTree` 类仍用 `self.root` 保存嵌套字典。递归建树留在《从二叉树到决策树》讲义的专门环节讲解。

## 10 读取文件：文本 → 行 → 字段 → 特征和标签（教材 10.1）

对应脚本：[10_read_files.py](code/python_syntax/10_read_files.py)

**教师先讲：** 教材第 3 版使用 `pathlib.Path` 读文件。`Path` 对象描述位置，`read_text()` 返回字符串，`splitlines()` 返回各行组成的列表，`split()` 再把一行按空白拆成字段。读取不会自动把数字文本转成整数。

**路径必须说清：** 裸相对路径 `Path("data/watermelon_samples.txt")` 从当前工作目录出发，不会自动从脚本目录出发。示例先用 `Path(__file__).resolve().parent` 找到脚本目录，再拼接 `data` 和文件名，因而可以从其他目录启动脚本。`Path.cwd()` 显示当前工作目录，`parent` 是父目录，`resolve()` 在这里取得规范化绝对路径；这些是已提供的路径准备代码，不要求学生先背会。

`encoding="utf-8"` 指明按 UTF-8（Unicode Transformation Format, 8-bit）编码读取中文文本。路径拼接中的 `/` 是 Path 的操作，和数字的除法含义不同。`rstrip()` 只用于显示时去掉结尾空白；它返回新字符串，不更改文件。

```python
print("\n10 读取文件")
from pathlib import Path

# __file__ 是当前 .py 文件的位置；parent 是它所在的目录。
# Path 对象之间的 / 表示拼接路径，不是数值除法。
script_dir = Path(__file__).resolve().parent
path = script_dir / "data" / "watermelon_samples.txt"
print("当前工作目录：", Path.cwd())
print("本次读取：", path)
contents = path.read_text(encoding="utf-8")
print("文件全部内容：")
print(contents.rstrip())

lines = contents.splitlines()
print("表头：", lines[0])
X, y, original_ids = [], [], []
for line in lines[1:]:
    parts = line.split()  # 本文件以空白分隔，字段本身不含空格。
    original_ids.append(int(parts[0]))
    X.append(parts[1:7])
    y.append(int(parts[7]))
print("教材原编号：", original_ids)
print("X 的形状：", len(X), "行 ×", len(X[0]), "列")
print("第一行特征：", X[0])
print("标签 y：", y)
print("读入的第一条标签类型：", type(y[0]))

# TODO S2：统计 y 中的好瓜数并打印。
# Hint：用 for 和 if 逐个检查标签，为 1 时累加；这 4 行应得到 2。
# 这里保留空位，不修改文件内容。

# 本课到读取文件为止。四条子集只练语法，不计算测试准确率。
```

**预期观察：** 表头之外有 4 条记录，教材原编号为 `[1, 2, 9, 11]`；`X` 为 4 行 6 列，`y` 为 `[1, 1, 0, 0]`，标签元素类型为 `int`。索引 `parts[1:7]` 取第 1–6 列属性，`parts[7]` 是标签，`parts[0]` 的原编号单独保存。

**学生任务 S2：** 用循环与条件判断统计读入的好瓜数，打印结果，预期为 2。本文件不依赖第 8 章的函数。

**现场检查：** 为什么不直接让 `y.append(parts[7])`？参考：那样保存的是 `'1'`、`'0'` 字符串，与整数 1、0 的比较不同；需要 `int()`。

**边界说明：** 本文件字段本身没有空格，因此能直接用 `split()`。这里只读一个很小的文本文件；`read_text()` 先把全部内容放进内存，之后遍历 `splitlines()` 并不等于从磁盘逐行流式读取。

## 退出卡：用五个问题结束

1. `=`、`==`、`is None` 各做什么？参考：赋值、值比较、检查是否为 None。
2. `print` 和 `return` 的区别？参考：向屏幕显示、把结果交给调用者。
3. `features.copy()` 在本实验解决什么问题？参考：让分支拥有独立的候选编号列表。
4. `self` 指什么？参考：当前实例，可以让不同树保存不同状态。
5. 文件如何变成决策树输入？参考：路径 → 文本 → 行 → 字段 → 六列字符串特征与整数标签；原编号另存。

进入决策树讲义和配套脚本后，`X` 每行是一条记录，`y` 保存相应标签；先在当前节点计数，再分组，最后递归。在这份语法带练里先确保数据表示和循环能读懂，不提前要求学生完成信息增益或训练算法。

## 教师参考：S1 与 S2

建议学生先完成后再展开；配套脚本仍保留空位。

<details>
<summary>S1：显式计数循环</summary>

替换 `count_good` 方法体中的占位 `return None`，保留原文档字符串：

```python
count = 0
for label in labels:
    if label == 1:
        count += 1
return count
```

以上是函数体片段，需要整体缩进到函数内部。空列表使循环执行零次，仍返回初值 0；因此不需要额外的空列表分支。

</details>

<details>
<summary>S2：统计文件读入的标签</summary>

```python
good_count = 0
for label in y:
    if label == 1:
        good_count += 1
print("文件中的好瓜数：", good_count)
```

预期为 2。注意判断整数 `1`，而不是字符串 `"1"`；读取时已用 `int()` 转换标签。

</details>

## 实际参考资料

- `source/pdf/Python编程：从入门到实践（第3版）.pdf`：目录第 1–10 章（文件页序 4–12），用于安排顺序与选讲范围；10.1.1–10.1.4（文件页序 285–290），用于核对 `Path`、`read_text()`、路径、`splitlines()` 与文本转数值的讲解。此处“文件页序”指阅读器从 1 开始数的 PDF 页面，不是印刷页码。本文是针对西瓜实验重新组织的讲解稿，不是教材摘录。
- `source/pdf/机器学习周志华.pdf`：第 4 章表 4.1，第 76 页；本实验已核验的完整数据见 [decision_tree.py](code/decision_tree.py)，本次据此取原编号 1、2、9、11 作为读文件样例。
- [本实验决策树说明](README.md)：对齐原有列表、字典、类及 `fit`／`predict` 的使用方式。
