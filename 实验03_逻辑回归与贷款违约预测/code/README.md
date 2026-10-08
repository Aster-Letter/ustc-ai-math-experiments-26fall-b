> **历史参考材料，不作为实际实验课内容。** 本贷款版本仅用于方案对照与自主阅读，不计入课程实验任务，也不要求提交本版本报告。正式第三次实验请使用 [QS 大学排名分类](https://github.com/Aster-Letter/ustc-ai-math-experiments-26fall-b/tree/main/实验03_逻辑回归与大学排名分类)。下文保留旧方案的课时、任务与报告格式，仅供参考。

# 实验 03 代码

主要编辑 `student.py`，不要为每个 checkpoint 复制整套工程。所有函数使用简洁签名和 Google 风格文档字符串。

## 阶段与函数

| 阶段 | 补全位置 | 检查命令 |
| --- | --- | --- |
| C0 | 无，先运行 | `python checkpoints.py C0` |
| C1 | `filter_labels`、`encode_employment` | `python checkpoints.py C1` |
| C2 | `fit_statistics`、`apply_statistics`、`to_tensors` | `python checkpoints.py C2` |
| C3 | `LoanDataset.__len__`、`__getitem__`、`make_loader` | `python checkpoints.py C3` |
| C4 | `sigmoid`、模型 `__init__` 与 `forward` | `python checkpoints.py C4` |
| C5 | `data_loss`、模型 `penalty` | `python checkpoints.py C5` |
| C6 | `train_epoch` | `python checkpoints.py C6` |
| C7 | `binary_metrics` | `python checkpoints.py C7` |

C5 依赖 C4；C6 依赖 C3–C5。C7 指标小测试可独立执行；完整实验需要全部完成。初始 `None` 只是占位，不会悄悄替学生返回正确答案。每个 TODO 旁的 Hint 提供语法与小样例。

## 运行完整实验

```bash
python checkpoints.py all
python run_lab.py
python run_lab.py --final-test
```

第一条检查小样例；第二条只用训练/验证选择模型；第三条恢复已经冻结的模型、预处理和阈值，读取测试集。先查看第二步结果，再执行第三步；测试后不要反复调参。

`support.py` 提供固定日期编码、列选择、预处理编排与绘图；`workflow.py` 提供三个候选方案、模型快照与文件输出，不属于初学者补全范围。训练循环使用 SGD（Stochastic Gradient Descent，随机梯度下降），其更新规则在前置讲义推导。损失使用 BCE（Binary Cross-Entropy，二元交叉熵）。

图中的 Train 和 Validation 表示每轮结束时，用同一组参数计算的无正则数据损失。`train_epoch` 的批次累计记录是另一个量，不直接用作图中 Train 曲线。

## Notebook 入口

从 `code/` 打开 `logic.ipynb`，按顺序执行。修改 `student.py` 后重启内核并重新执行至当前阶段。C7 训练单元只用训练/验证；最后测试单元默认 `RUN_FINAL_TEST = False`，记录冻结方案后改为 `True` 并执行一次。

## 数据目录与自备划分

```bash
python run_lab.py --data-dir ../course-data --output outputs-course
python run_lab.py --data-dir ../course-data --output outputs-course --final-test
```

默认读取 `data/classroom/` 的真实贷款子集，结果保存到 `outputs-tianchi-balanced/`；Notebook 保存到 `outputs-tianchi-balanced-notebook/`。原始 `data/train.csv` 不直接参与训练。数据约定见 [data/README.md](data/README.md)。两个命令必须使用同一数据目录与输出目录。新的数据或不同预处理必须用新的输出目录，不能复用之前的权重。

## 环境

Python 3.11；在课程环境中缺哪个库再安装。`requirements.txt` 为本机验证过的核心库版本，Notebook 另外使用现有 Jupyter 内核；本包不依赖 scikit-learn。本实验使用 CPU（Central Processing Unit，中央处理器），在普通电脑上完成。
