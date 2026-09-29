# 实验 01：Python 环境与基础入门

人工智能数学原理与算法 B，2026 年秋季。

主讲：钟志诚。整理：曾有成、史睿铭、胡泷。单位：中国科学技术大学 人工智能与数据科学学院。

本次实验通过两个微项目学习 Python。书店项目练习组织数据、使用对象与继承、更新库存与售价，以及计算销售额和毛利；鸢尾花项目练习辨认数据与调用关系，补全训练和预测，并验证结果。

你在 C 语言中学过的条件、循环和函数仍然适用。可以结合讲义中的对照示例，关注 Python 在具体写法和数据处理方式上的区别。

## 课前准备

**建议课前完成环境安装和首次运行，尤其是参加线下实验课的同学。** 集中下载可能遇到网络缓慢或中断，请在网络较好的时候按照[实验手册第 2–4 节](实验01_实验手册.md)完成准备：

1. 下载并完整解压[学生材料包](../downloads/lab01-python-basics-26fall-B.zip)。
2. 安装或检查 conda，创建课程环境并安装依赖。
3. 试运行简单脚本和 `practice.ipynb`，修改一处并确认输出变化。

只下载 Miniforge 安装包还不够，创建环境和安装库也需要联网。已有可用 conda 的同学无需重复安装。遇到问题时保留执行命令和完整报错，便于排查。

## 两个主任务

| 项目与说明 | 需要完成的功能 | 学生代码 |
| --- | --- | --- |
| [bookstore：微型书店数据管理与统计](code/bookstore/README.md) | 图书对象、补货与改价、预算查询、销售记录解析、销售额与毛利统计 | [book_tasks.py](code/bookstore/book_tasks.py) |
| [iris：鸢尾花数据观察与分类](code/iris/README.md) | 选择绘图特征、补全训练与预测调用、观察评价结果 | [iris_classification.py](code/iris/iris_classification.py) |

每个项目的说明、代码、验证程序和所需数据均在自己的目录中。先读 README，再搜索 `LAB01_TODO`，按阶段完成并检查。

## 基础练习与阅读材料

| 材料 | 用途 |
| --- | --- |
| [practice.ipynb](code/practice.ipynb) | Python 基础教学配套练习，不要求提交 |
| [代码目录说明](code/README.md) | 文件布局、运行与验证入口 |
| [实验手册](实验01_实验手册.md) · [PDF](实验01_实验手册.pdf) | 环境配置、运行步骤、任务与提交说明 |
| [实验讲义](实验01_实验讲义.md) · [PDF](实验01_实验讲义.pdf) | 概念解释、C / Python 对照与示例 |

讲义中的选读内容标有 `*`。`code/books.txt` 仅用于第 5 章的文本读取示例；书店项目使用自己目录中的 `books.csv` 和 `sales.csv`。

## 已装好环境：开始练习

进入实验目录下的 `code` 文件夹，激活环境并启动 JupyterLab：

```bash
conda activate ustc-ai-experiments-26fall-B
python -m jupyterlab
```

打开 `practice.ipynb`，从上往下运行。它用于练习单个 Python 操作，两个微项目再把这些操作组合成完整功能。

## 运行项目

下面的命令均在 `code` 目录执行：

```bash
python bookstore/check_book_tasks.py
python iris/check_iris.py
python bookstore/book_tasks.py
python iris/iris_classification.py
```

初始框架会提示尚未完成的位置；按项目说明补全后再检查。书店首次进入菜单需要完成 B1。绘图程序可能等待关闭图窗后继续。

## 提交作业

提交 `学号_姓名_lab01.zip`，保留 `code/bookstore` 和 `code/iris` 的目录区分，包含两个学生脚本、书店辅助模块、两份 CSV 和 `report.pdf`。报告展示完成情况、一张训练集散点图、准确率、混淆矩阵及简短分析。完整目录和自查步骤见[手册第 7 节](实验01_实验手册.md#提交成果)。
