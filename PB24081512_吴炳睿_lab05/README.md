# 实验05提交与复现说明

- 姓名：吴炳睿
- 学号：PB24081512
- 课程：人工智能数学原理与算法 B
- 运行方式：本地 NVIDIA GPU；未使用107平台，无Slurm作业编号。
- 环境：Python 3.11.17、PyTorch 2.7.1+cu128、NVIDIA GeForce RTX 5080。
- 依赖约束：见 `code/requirements.txt`，CUDA版PyTorch需与运行设备驱动兼容。
- 基础训练日期：2026-10-20；BN改进、U-Net及最终测试日期：2026-11-02。

## 1. 最终模型与实验结论

三组均使用20轮、batch=16、lr=0.001、seed=42、128×128输入，不开启增强。

| 模型 | 参数量 | 最佳轮次 | 验证IoU | 对应Dice |
| --- | ---: | ---: | ---: | ---: |
| 基础版 | 49,009 | 20 | 0.684446 | 0.797661 |
| 首阶段BN改进版 | 49,041 | 16 | 0.722655 | 0.825147 |
| 小型U-Net | 60,529 | 18 | 0.677494 | 0.790934 |

依据验证集选择BN改进版第16轮，最终权重为 `selected/best.pt`。完整3669张测试图的平均前景IoU为0.731225、Dice为0.829054。阈值0.5，忽略trimap=3，逐图计算再平均。U-Net未超过基础版，报告如实分析，不根据测试集再次选择模型。

## 2. 数据与路径

数据来源为课程提供的 `lab05-pet-data.zip`（Oxford-IIIT Pet），通过课程科大网盘获取。提交包不包含原始图片和掩码。复现者将数据包解压到提交目录根部，形成：

```text
data/
  splits.json
  oxford-iiit-pet/
    images/
    annotations/
```

如需从本包恢复划分文件，可将 `selected/splits.json` 复制到数据目录，但必须使用同一版本的图片与掩码。固定划分：训练2941张、验证739张、测试3669张；划分种子2026，训练种子42。

划分指纹：`37cee4018bbc0efe2e7652fdab3d5e0cecab3a4e62bb015eaea61530d4fa3770`。

原工作目录为 `D:/User/Bingrui_Wu/projects/ustc-ai-math-experiments-26fall-b/实验05_宠物主体分割与小型UNet/code/`，原解释器为 `D:/SoftWare/MiniConda/envs/ustcaib/python.exe`。包内元数据和原始日志保留历史路径；新机器按以下映射解释：

| 原工作目录中的路径 | 提交包路径 |
| --- | --- |
| outputs/basic-local-01/ | runs/basic/ |
| outputs/improved-local-02/ | runs/improved/（训练记录）；selected/（最终权重与快照） |
| outputs/unet-local-01/ | runs/unet/ |
| outputs/final-test-01/ | evaluation/ |
| outputs/basic-val-01/ | runs/basic/validation/ |
| outputs/improved-val-report-01/ | runs/improved/validation/ |
| outputs/unet-val-01/ | runs/unet/validation/ |
| outputs/unet-comparison/summary.csv | runs/comparison-summary.csv |

报告中以 `code/outputs/` 开头的路径是原实验目录中的证据位置，应按上表查找。报告图像已嵌入PDF；额外插图与案例清单放在report-assets/。包内仅有一份最终报告和一份模型权重，不包含历史权重、原始数据、课程讲义、PPT或环境目录。

## 3. 复核最终模型

在已配置CUDA版PyTorch的环境中，从提交目录根部运行：

```bash
python selected/source/evaluate.py --checkpoint selected/best.pt --data-dir data --device cuda --split test --output verify-test-01
```

`verify-test-01` 必须是尚不存在的新目录。评估使用最终模型的原始代码快照，并检查划分指纹。应得到3669张测试样例及与evaluation/metrics.json一致的指标；更换软硬件可能产生微小数值差异。仅验证代码时可使用CPU自检，完整训练建议使用GPU。

## 4. 重新训练

从提交目录根部进入code/，数据仍位于提交目录根部data/，因此显式传入 `--data-dir ../data`。以下命令为新输出目录，不会覆盖包中的runs/或selected/：

```bash
cd code
python check_data.py --data-dir ../data
python checks.py operators
python checks.py core
python checks.py basic
python checks.py improved
python checks.py unet
python run_local.py basic --data-dir ../data --output outputs/basic-reproduce --epochs 20 --batch-size 16 --lr 0.001 --seed 42
python run_local.py improved --data-dir ../data --output outputs/improved-reproduce --epochs 20 --batch-size 16 --lr 0.001 --seed 42
python run_local.py unet --data-dir ../data --output outputs/unet-reproduce --epochs 20 --batch-size 16 --lr 0.001 --seed 42
```

原实验命令及实际解释器保存在logs/中。本次选用本地运行入口；scripts/保留课程原有Slurm脚本，其中未扩展unet选项。

## 5. 代码与协作说明

- operator_exercises.py：卷积、ReLU和最大池化练习。
- student_encoder.py、student_decoder.py：基础编码器与解码器；改进版在首阶段加入BatchNorm2d(16)。
- student_unet.py：独立SmallUNet，两条跳跃连接，融合输入为96和48通道。
- models.py、train.py、run_local.py：注册unet并接入本地训练流程。
- checks.py：核对各融合尺寸、拼接内容、两分支梯度及一次参数更新。

参考课程实验05讲义、README、报告模板及提交说明。使用Codex解释任务、补全BN改进和U-Net、接入检查与训练、执行实验、整理报告及打包；基础运算和基础编解码器此前已填写。使用PyTorch训练与评估、Matplotlib绘图、ReportLab生成报告。所有指标来自真实本地实验，详细限制与案例分析见report.pdf。
