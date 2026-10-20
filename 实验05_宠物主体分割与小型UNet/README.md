# 实验05：宠物主体分割

使用 PyTorch，可在本地NVIDIA GPU（Graphics Processing Unit，图形处理器）或107平台训练与评估。基础任务手搭卷积编码器和解码器，完成基础版与改进版的对照。学生包提供编码器–解码器框架；小型 U-Net 为独立选做，由学生自行实现。

先读[实验讲义](实验05_实验讲义.pdf)，再进入 `code/` 操作。完整材料可从[学生包](https://raw.githubusercontent.com/Aster-Letter/ustc-ai-math-experiments-26fall-b/main/downloads/lab05-pet-segmentation-26fall-B.zip)下载。

| 材料 | 用途 |
| --- | --- |
| `code/` | 运算练习、编解码器骨架、本地入口与107脚本 |
| `实验05_实验讲义.pdf` | 实验说明、理论、步骤、评分与进阶要求 |
| `slides/实验05_课堂讲解.pptx` | 33页课堂PPT，含实验结果与训练曲线 |
| `slides/实验05_课堂讲解.pdf` | 课堂PPT的便携阅读版 |
| `report-template.md` | 可编辑报告模板，填写后导出 `report.pdf` |
| `提交与打包说明.md` | 提交目录、实验记录与打包命令 |
| 讲义 `.tex` 与 `assets/` | 讲义可编辑源文件及其配套图片 |

## 学生修改范围

- `code/operator_exercises.py`：T2，卷积、激活、池化。
- `code/student_encoder.py`：T3基础编码器，T5改进编码器。
- `code/student_decoder.py`：T4，三个卷积块、上采样与单通道输出头。
- `report-template.md`：过程、结果和分析。

基础代码修改集中在上述三个Python文件；`student_encoder.py` 中的 `PetEncoder` 为基线，`ImprovedEncoder` 为改进版本。其余代码已提供，`models.py` 自动连接学生编码器和解码器。

## 快速开始

在本地PyTorch环境中进入解压后的 `code/` 目录。基础运算与网络检查使用CPU（Central Processing Unit，中央处理器）；安装说明与平台操作见讲义。

先运行基础运算示例，再补全三个学生文件，并查看各阶段的尺寸与更新结果：

```bash
python operator_exercises.py
python checks.py operators
python checks.py encoder
python checks.py decoder
python checks.py basic
python checks.py improved
```

`checks.py` 默认使用CPU，网络检查使用程序生成的两个128×128输入张量。检查输出与手算结果、网络尺寸表一起记入报告。

## 数据准备

从课程提供的科大网盘下载 `lab05-pet-data.zip`。数据包已包含图片、三值掩码与本实验固定划分。

**Windows：**右键单击压缩包，选择“全部解压”，将解压得到的 `data` 文件夹放入学生包的 `code/` 中。最终划分文件的路径为 `code/data/splits.json`。

**Linux、macOS或107平台：**将压缩包放入 `code/`，在该目录执行：

```bash
unzip lab05-pet-data.zip
```

解压完成后，各系统均在 `code/` 目录运行：

```bash
python check_data.py --data-dir data
python preview_data.py --data-dir data
```

压缩包最外层是 `data/`，解压后目录如下：

```text
code/
  data/
    splits.json
    oxford-iiit-pet/
      images/
      annotations/
        trainval.txt
        test.txt
        trimaps/
  outputs/
    data_preview.png
```

`check_data.py` 使用CPU，检测目录与固定划分、全部7349对图片和掩码的存在性与可读性、图像尺寸是否对应、掩码像素值是否属于1/2/3。正常结束时显示“数据集检测通过”；发现问题时列出对应文件并返回非零退出码。固定划分为训练2941张、验证739张、测试3669张，已保存在 `data/splits.json`。`preview_data.py` 生成 `outputs/data_preview.png`。

训练读取解压后的数据，压缩包可另存。将完整 `code/` 及其中的 `data/` 上传到107平台；也可在平台 `code/` 中解压同一数据包。若数据放在共享目录，`LAB05_DATA_DIR` 指向包含 `splits.json` 的那一级目录。

标注1=宠物、2=背景、3=不确定；目标转换为1/0，3在损失与指标中忽略。固定划分使用官方trainval和test名单；仅在trainval内按品种用种子2026划分80%训练、20%验证。指标在统一缩放后的128×128网格上计算；每张图先计算前景指标，再对全部图片取平均。

## 选择训练路径

两种方式共用代码、固定划分、默认训练预算和评分标准。本地CPU可完成基础运算、编解码器尺寸和梯度检查。

| 当前条件 | 后续操作 |
| --- | --- |
| 本地有NVIDIA GPU，且PyTorch可调用CUDA（Compute Unified Device Architecture，统一计算设备架构） | 按讲义第8.1节，本地训练和评估 |
| 本地没有NVIDIA GPU或当前环境不使用CUDA | 完成本地CPU检查后，转到讲义第8.2节使用107平台Slurm |

### 方案A：本地NVIDIA GPU（讲义8.1）

CUDA版依赖的安装见 [PyTorch官方历史版本说明](https://pytorch.org/get-started/previous-versions/)，课程参考版本为PyTorch 2.7.1、Torchvision 0.22.1。在当前环境确认CUDA可用：

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

输出 `True` 后，在 `code/` 运行以下命令。Windows和Linux命令相同：

```bash
python run_local.py basic --output outputs/basic-local-01
python run_local.py improved --output outputs/improved-local-01
```

本地入口先在CPU上检查编码器、解码器及完整模型，再调用 `train.py --device cuda` 训练。默认20轮、批量16、学习率0.001、种子42，可用 `--epochs`、`--batch-size`、`--lr`、`--seed` 设置；对照组保持一致。每次实验使用新的输出目录；省略 `--output` 时自动按时间命名。终端输出同时保存在 `logs/*.log`，包含命令、检查结果和训练记录。

根据验证集选择模型后评估，下面假定选定改进版：

```bash
python run_local.py evaluate --checkpoint outputs/improved-local-01/best.pt
```

评估自动调用该模型的 `source/evaluate.py`。保存本地日志与训练、评估结果。`run.json` 中的 `slurm_job_id` 在本地运行时为空。

### 方案B：107平台Slurm（讲义8.2）


在平台登录/提交终端进入 `code/`。`LAB05_PYTHON` 填平台环境解释器的绝对路径，以下为实验04的路径示例：

```bash
export LAB05_PYTHON="$HOME/.conda/envs/compute-resnet/bin/python"
export LAB05_DATA_DIR="$PWD/data"
bash scripts/submit.sh basic
bash scripts/submit.sh improved
```

基础版与改进版作业先在CPU上运行对应的编解码器和完整模型检查，再由脚本以 `--device cuda` 启动GPU训练；最终评估也使用GPU。本地与平台使用同一份模型代码，检查输出和训练记录写入Slurm的 `.out` 日志。

脚本默认请求1张GPU、4个CPU核心、8GB主内存、1小时。默认分区为Students，服务质量QOS（Quality of Service）为qos_stu_default，资源配置按账号可用参数设置。可在命令末追加sbatch资源选项，1小时为默认作业时限。可用 `LAB05_EPOCHS`、`LAB05_BATCH_SIZE`、`LAB05_LR`、`LAB05_SEED` 设置实验预算，比较模型时保持一致。

在验证集上选定模型后，填写对应路径并提交测试任务：

```bash
export LAB05_CHECKPOINT="$PWD/outputs/basic-实际作业号/best.pt"
bash scripts/submit.sh evaluate
```

程序使用该次训练的 `source/evaluate.py` 与相应权重恢复模型。每次输出目录带独立作业编号。

## 进阶选做

讲义与PPT保留小型 U-Net 的结构和维度提示。选做时另建模型文件，自行扩展模型选择、训练选项、自检与所选运行入口；沿用同一数据划分、损失、指标和评估流程。记录各融合阶段的形状与参数量，完成同一预算下的训练和对照分析。进阶最多加20分，总分封顶100分。与ResNet（Residual Network，残差网络）的比较采用理论分析。

## 输出与提交

训练输出包括 `best.pt`、`run.json`、`history.csv`、`curves.png`、`validation_examples.png` 和 `source/`。评估输出包括 `metrics.json`、`per_image.csv`、`examples.png`及`best_worst_examples.png`（前三行是IoU最低样例，后三行是最高样例）。白色=宠物，黑色=背景，灰色=忽略区域。

提交 `学号_姓名_lab05.zip`，包含代码、`report.pdf`、选定模型、两组训练记录、一次最终测试记录和运行日志。按[提交与打包说明](提交与打包说明.md)整理本人代码、报告和实验记录。数据来源与环境配置写入复现说明。主指标为逐图前景交并比IoU（Intersection over Union）的平均值，辅助指标为Dice；概率阈值固定0.5。评分比例20/30/20/20/10，进阶最多加20分且总分封顶100，详见讲义。
