# 实验03代码：大学排名分类

主要编辑 `student.py`，所有17处TODO都带Hint，函数使用Google风格文档字符串，不要求类型标注或复杂封装。完整教学顺序见上一级实验手册。

| 阶段 | 函数 | 主要输入 → 输出 | 命令 |
| --- | --- | --- | --- |
| C0 | 已提供小例子 | `X`(2×2)、`w`(2×1) 张量 → `X @ w`(2×1) | `python checkpoints.py C0` |
| C1 | `filter_labels`, `clean_numeric` | `pd.DataFrame` → 删去缺失标签行的表；`pd.Series` 文本 → 数值列（无效值为 NaN） | `python checkpoints.py C1` |
| C2 | `fit_statistics`, `apply_statistics`, `fit_categories`, `encode_categories`, `to_tensors` | 训练/验证表 → 均值与尺度、类别表（`dict`）、0/1 独热表 → `X`(N×(d+1))、`y`(N×1) 的 float32 张量 | `python checkpoints.py C2` |
| C3 | `UniversityDataset.__len__`, `__getitem__`, `make_loader` | `X`、`y` 张量 → 样本数、`(X[i], y[i])`、按批迭代的 `DataLoader` | `python checkpoints.py C3` |
| C4 | `sigmoid`, `LogisticRegression.__init__`, `forward` | 得分张量 → 同形状概率；`input_dim`(int) → 参数 `theta`(input_dim×1)；`X`(B×(d+1)) → 得分(B×1) | `python checkpoints.py C4` |
| C5 | `data_loss`, `penalty` | 得分与标签(B×1) → 平均 BCE 标量；`kind`(str) → 惩罚标量 | `python checkpoints.py C5` |
| C6 | `train_epoch` | 模型、`DataLoader`、优化器、`kind`、`strength` → 本轮平均数据损失(float) | `python checkpoints.py C6` |
| C7 | `binary_metrics` | 标签与概率(N×1)、阈值(float) → 四种计数与四项指标(`dict`) | `python checkpoints.py C7` |

各函数参数的具体类型、形状与返回值写在 `student.py` 的文档字符串中，实验手册各检查点的“输入、输出与提示”框与之一致。

C5依赖C4，C6依赖C3–C5；C7小测试独立于训练，但完整运行需要全部完成。保留末批，标签和特征始终成对。普通SGD（Stochastic Gradient Descent，随机梯度下降）不保证L1生成精确零权重。

## 完整运行

```bash
python checkpoints.py all
python run_lab.py
# 选做，须在看测试结果前讨论；不覆盖主实验模型
python run_lab.py --feature-study
# 记录冻结方案后再执行
python run_lab.py --final-test
```

默认保存 `outputs-qs/`，选做在其 `feature_study/`。训练比较无正则、L2=0.01、L1=0.01；每组60轮，按验证数据损失选择，不按测试准确率选择。训练与验证曲线均为每轮结束、同一参数下的平均二元交叉熵，不含正则惩罚。测试恢复冻结的模型与预处理。

`support.py`负责拼接：三个标准化数值列在前，五组0/1独热列在后，再由学生函数在最前加常数1。类别顺序从训练集确定，Unknown始终预留；独热列不标准化。`workflow.py`是提供的编排，不是额外补全任务。

Notebook从 `code/` 打开；修改student后重启内核，从头执行。选做开关 `RUN_FEATURE_STUDY=False`，最终测试开关 `RUN_FINAL_TEST=False`，记录方案后再设True。Notebook默认写入 `outputs-qs-notebook/`，独立于脚本输出。

## 自备数据

```bash
python run_lab.py --data-dir ../course-data --output outputs-course
python run_lab.py --data-dir ../course-data --output outputs-course --final-test
```

保持相同课堂列定义。新数据或不同预处理使用新目录；不要把其他来源的原始文件混入QS流程。环境为Python3.11；核心库见requirements，不依赖scikit-learn，Notebook使用现有Jupyter内核。
