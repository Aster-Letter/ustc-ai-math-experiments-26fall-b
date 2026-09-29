# 实验 01 代码与练习

两个微项目各自保存在独立目录，项目说明、代码、验证程序与所需数据放在一起。

| 目录或文件 | 用途 | 需要修改的内容 |
| --- | --- | --- |
| [bookstore/](bookstore/README.md) | 微型书店数据管理与统计 | `book_tasks.py` 中的 B1–B6，B2 包含两个小方法 |
| [iris/](iris/README.md) | 鸢尾花数据观察与分类 | `iris_classification.py` 中的 I1–I3 |
| [practice.ipynb](practice.ipynb) | Python 基础练习，不要求提交 | 按 `PRACTICE` 提示修改和运行 |
| [books.txt](books.txt) | 讲义第 5 章的文本读取示例数据 | 用于理解路径、文本拆分和类型转换 |

## 运行基础练习

在本目录中激活课程环境后执行 `python -m jupyterlab`，打开 `practice.ipynb`，从准备单元开始运行。修改函数或类后先重跑定义，再运行调用。它不替代两个项目的作业文件。

## 运行项目与验证

以下命令均从本目录 `code` 执行：

```bash
python bookstore/check_book_tasks.py
python iris/check_iris.py
python bookstore/book_tasks.py
python iris/iris_classification.py
```

也可以先进入对应项目目录，再按该目录的 README 运行。例如进入 `bookstore` 后，运行 `python check_book_tasks.py --stage B3` 可单独验证销售记录解析。

书店验证使用内置固定样例，不读取或修改你的 CSV；各阶段可独立检查。书店首次运行需要先完成 B1，之后可通过菜单尝试功能；选择保存时才写入项目内的 `books_updated.csv`。

鸢尾花 I1 选择两个不同的特征列，I2/I3 补全训练与预测调用。验证应通过 3/3 组检查，再运行程序查看图和评价结果；绘图使用两个特征，模型使用四个特征。

TODO 中的 `raise NotImplementedError(...)` 是待实现提示，应由实际代码替换。菜单、验证程序与提供的辅助模块无需改写。

## 提交

保留 `bookstore` 和 `iris` 两个子目录，提交已完成的学生脚本、书店辅助模块与两份 CSV，以及 `report.pdf`。基础练习、文本示例数据和验证程序无需提交。完整结构见[实验手册](../实验01_实验手册.md#提交成果)。
