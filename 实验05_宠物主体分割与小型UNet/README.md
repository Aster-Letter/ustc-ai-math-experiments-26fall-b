# 实验05：宠物主体分割

使用 PyTorch，在107平台训练与评估。基础任务手搭卷积编码器并接入提供的解码器，完成基础版与改进版的对照。学生包提供编码器–解码器框架；小型 U-Net 为独立选做，由学生自行实现。

先读[实验讲义](实验05_实验讲义.pdf)，再进入 `code/` 操作。完整材料可从[学生包](../downloads/lab05-pet-segmentation-26fall-B.zip)下载。

| 材料 | 用途 |
| --- | --- |
| `code/` | 运算练习、编码器骨架、已提供的解码器、训练评估与107脚本 |
| `实验05_实验讲义.pdf` | 实验说明、理论、步骤、评分与进阶要求 |
| `slides/实验05_课堂讲解.pptx` | 33页课堂PPT，含实验结果与训练曲线 |
| `slides/实验05_课堂讲解.pdf` | 课堂PPT的便携阅读版 |
| `report-template.md` | 可编辑报告模板，填写后导出 `report.pdf` |
| `提交与打包说明.md` | 提交目录、实验记录与打包命令 |
| 讲义 `.tex` 与 `assets/` | 讲义可编辑源文件及其配套图片 |

## 学生修改范围

- `code/operator_exercises.py`：T2，卷积、激活、池化。
- `code/student_encoder.py`：T3基础编码器，T5改进编码器。
- `report-template.md`：过程、结果和分析。

其余代码完整提供，按讲义阅读数据处理、解码器、训练与评估的关键步骤。

## 快速开始

在解压后的 `code/` 目录运行。使用实验04已核对的PyTorch环境；安装说明与平台操作见讲义。

先运行基础运算示例，再补全两个学生文件，并查看各阶段的尺寸与更新结果：

```bash
python operator_exercises.py
python checks.py operators
python checks.py encoder
python checks.py basic
python checks.py improved
```

检查输出与手算结果、网络尺寸表一起记入报告。

## 数据准备

联网机器运行一次，约755MB图片与19MB标注压缩包，解压需额外磁盘空间：

```bash
python prepare_data.py --data-dir data --download
python preview_data.py --data-dir data
```

数据源为 [Oxford-IIIT Pet 官方页面](https://www.robots.ox.ac.uk/~vgg/data/pets/)，通过Torchvision下载。数据放在 `data/oxford-iiit-pet/`，划分写入 `data/splits.json`。将整个 `data/` 上传到107平台，训练作业直接读取该目录中的数据。也可从官网手动下载两个归档，分别解压到 `data/oxford-iiit-pet/`，再去掉 `--download` 运行准备程序。

标注1=宠物、2=背景、3=不确定；目标转换为1/0，3在损失与指标中忽略。固定划分使用官方trainval和test名单；仅在trainval内按品种用种子2026划分80%训练、20%验证。指标在统一缩放后的128×128网格上计算；每张图先计算前景指标，再对全部图片取平均。

## 107平台

在平台登录/提交终端进入 `code/`。`LAB05_PYTHON` 填实验04已核对的环境解释器绝对路径：

```bash
export LAB05_PYTHON="$HOME/.conda/envs/compute-resnet/bin/python"
export LAB05_DATA_DIR="$PWD/data"
bash scripts/submit.sh basic
bash scripts/submit.sh improved
```

脚本默认请求单张图形处理器GPU（Graphics Processing Unit）、4个CPU（Central Processing Unit，中央处理器）核心、8GB主内存、1小时。脚本的默认分区为Students，服务质量QOS（Quality of Service）为qos_stu_default，资源配置按账号可用参数设置。可在命令末追加sbatch资源选项，1小时为默认作业时限。可用 `LAB05_EPOCHS`、`LAB05_BATCH_SIZE`、`LAB05_LR`、`LAB05_SEED` 设置实验预算，比较模型时保持一致。

在验证集上选定模型后，填写对应路径并提交测试任务：

```bash
export LAB05_CHECKPOINT="$PWD/outputs/basic-实际作业号/best.pt"
bash scripts/submit.sh evaluate
```

程序使用该次训练的 `source/evaluate.py` 与相应权重恢复模型。每次输出目录带独立作业编号。

## 进阶选做

讲义与PPT保留小型 U-Net 的结构和维度提示。选做时另建模型文件，自行扩展模型选择、训练选项、自检与平台提交分支；沿用同一数据划分、损失、指标和评估流程。记录各融合阶段的形状与参数量，完成同一预算下的训练和对照分析。进阶最多加20分，总分封顶100分。与ResNet（Residual Network，残差网络）的比较采用理论分析。

## 输出与提交

训练输出包括 `best.pt`、`run.json`、`history.csv`、`curves.png`、`validation_examples.png` 和 `source/`。评估输出包括 `metrics.json`、`per_image.csv`、`examples.png`及`best_worst_examples.png`（前三行是IoU最低样例，后三行是最高样例）。白色=宠物，黑色=背景，灰色=忽略区域。

提交 `学号_姓名_lab05.zip`，包含代码、`report.pdf`、选定模型、两组训练记录、一次最终测试记录和平台日志。按[提交与打包说明](提交与打包说明.md)整理本人代码、报告和实验记录。数据来源与环境配置写入复现说明。主指标为逐图前景交并比IoU（Intersection over Union）的平均值，辅助指标为Dice；概率阈值固定0.5。评分比例20/30/20/20/10，进阶最多加20分且总分封顶100，详见讲义。
