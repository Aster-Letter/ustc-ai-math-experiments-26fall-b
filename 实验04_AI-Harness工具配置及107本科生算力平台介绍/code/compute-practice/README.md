# 实验04：107平台 CPU/GPU 实践

本项目帮助你认识远程计算任务怎样运行：先用一个 CPU 小程序走通上传、提交、日志与结果下载，再用 CIFAR-10 + ResNet-18 运行一次短 GPU 训练。CIFAR-10 包含十类小图像，ResNet-18 是这里使用的图像分类网络；程序已提供，先关注环境、数据、提交脚本和运行结果。

本地电脑保存代码并供 Agent 协助修改；你通过平台网页和终端上传、配置环境、提交任务，再下载日志与结果。较重的训练在平台分配的计算节点执行。完整步骤见实验04讲义第二部分，平台实践采用图文，不另补视频；本项目供自学，不要求提交或评分。

## 实践内容与阅读顺序

| 阶段 | 你会操作什么 | 会看到什么 |
| --- | --- | --- |
| CPU 入门 | 上传项目，用网页提交 `hello.py` | 任务 ID、日志和 `outputs/hello/result.json` |
| GPU 短训练 | 创建环境、准备图像数据、读配置并提交任务 | 训练日志、模型文件、指标表和损失图 |
| 结果管理 | 下载同次任务的结果，读取模型和指标，结束临时应用 | 本地可查看的产物和已结束的任务 |
| 选做 | 带回路径错误日志，请本地 Agent 改脚本；或扩大训练规模 | 修改后的脚本及重跑结果 |

主线使用少样本、少步数配置，先把流程跑通；完整规模训练在讲义附录A中。训练准确率不作为这次入门的完成门槛。

## 开始：先提交一个 CPU 小任务

1. 在 Windows 浏览器打开107平台，通过统一身份认证登录。按讲义2.1章找到文件管理、任务提交和日志入口。
2. 把本目录完整上传为平台上的 `compute-practice/` 项目，保留目录结构。首次 CPU 任务只使用标准库，可先完成这一步。
3. 在网页提交任务时，将工作目录设为项目根目录，申请 CPU 任务、GPU 数设为0，运行 `python hello.py`；平台默认命令若为 `python3`，按实际解释器调整。
4. 查看任务状态和日志，再下载 `outputs/hello/result.json`，打开确认本次结果。任务提交不等于执行完成。

CPU 小任务跑通后，再按讲义2.2章在平台终端创建独立 GPU 项目环境、准备 CIFAR-10 数据和提交短训练。环境安装在登录节点完成，训练通过资源申请运行在计算节点。它与实验01/02的课程基础环境分别管理。

下面是项目文件和常用命令，具体终端位置、资源字段和数据下载步骤以讲义为准。从本项目根目录执行命令。

## 文件与配置

- `hello.py`：标准库 CPU 入门，保存 `outputs/hello/result.json`。
- `prepare_data.py`：原始包校验和安全解包，训练前单独完成。
- `train.py`：CIFAR-10 + ResNet-18，随机初始化，32×32 小图像 stem。
- `inspect_run.py`：读取运行结果和 checkpoint，自学检查，不评分。
- `configs/smoke.json`：256 训练/128 验证样本，batch 32，最多 8 次更新。
- `configs/train.json`：45000 训练/5000 验证样本，batch 128，10 epoch；平台负载和时长待实测。
- `scripts/setup-env.sh`：新建 Linux 项目环境，接受 cpu/cu126/cu128 构建。
- `scripts/submit.sh`：从项目根目录提交，预先创建日志目录；另有正常和路径错误演示脚本。
- [数据来源](data-sources.md)：包、校验值和数据划分。
- [AGENTS.md](AGENTS.md)：供本地 agent 阅读的项目约定。

脚本内 `Students`、`qos_stu_default`、GPU 及资源字段是候选配置，按自己的平台权限调整。项目参考 Python 3.11、torch 2.7.1、torchvision 0.22.1；安装时按实际 CPU/GPU 和驱动选择构建。

## 准备数据

先从原始来源下载 `cifar-10-python.tar.gz`，再执行：

```bash
python prepare_data.py --archive cifar-10-python.tar.gz --data-dir data
python prepare_data.py --data-dir data --check-only
```

完整数据必须位于 `data/cifar-10-batches-py/`。该程序不在线下载，不覆盖已有数据目录；已有目录校验失败时先保留并检查，使用新的完整副本恢复。

## 本地 CPU 短检查

在兼容项目环境中：

```bash
python train.py --config configs/smoke.json --device cpu --output outputs/local-check --max-steps 2
python inspect_run.py outputs/local-check
```

结果目录非空时程序拒绝覆盖，再次运行换一个目录。CPU 检查不证明 GPU 或平台流程已通过。

## 平台 CUDA 任务

以下在已核验资源配置的平台提交终端执行，环境位置按实际设置：

```bash
export COMPUTE_ENV_PREFIX="$HOME/.conda/envs/compute-resnet"
bash scripts/submit.sh smoke
```

输出位于 `outputs/smoke-任务ID/`，日志位于 `logs/compute-smoke-任务ID.out/.err`。任务完成后把实际 ID 填入检查命令：

```bash
"$COMPUTE_ENV_PREFIX/bin/python" inspect_run.py \
  outputs/smoke-12345 --require-cuda
```

`--device cuda` 明确要求 CUDA；不可用时失败，不自动回退 CPU。任务用环境前缀里的 `bin/python`，无需依赖提交终端激活状态。`submit.sh` 可追加经过核验的 sbatch 参数，例如分区、QOS 或 GPU 类型。

## 参数与输出含义

`train.py --help` 列出入口。可以在命令行覆盖样本数、步数、epoch、workers 和 CPU 线程，实际生效配置保存在 `run.json`。`max_steps=0` 不额外限制更新步数；其他值是整个任务的上限，不会每轮重置。

使用官方训练集的固定训练/验证划分，不使用官方测试集调参。训练池和验证池不相交；配置控制从两池各取多少样本。

每次成功运行保存 `run.json`、`metrics.csv`、`model.pt` 和 `loss.png`。运行元数据记录种子、配置、数据划分、实际设备、版本、计算耗时和参数变化情况。训练损失是更新过程中批次的平均值，验证在每轮训练结束后执行。

短训练核对计算流程，不设置准确率门槛。吞吐包含数据加载与更新，GPU 计时做同步；峰值只统计 PyTorch 分配的 CUDA 内存，不能直接视作整机资源用量。

## 明确标注的路径错误演示

`bash scripts/submit.sh path-error` 使用 `data-does-not-exist`。取回实际日志及目录信息，交给本地 agent，只修正 `scripts/run-job.sh` 的该分支数据路径，上传后重跑。新的任务 ID 对应新的输出目录。

这只是排错示例，不要求跟练者主动运行错误任务，也无需提交记录。

返回[实验04讲义](../../实验04_实验讲义.md#platform)。
