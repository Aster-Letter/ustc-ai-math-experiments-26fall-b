* [ ] 

# 实验06：小型语言模型实现与中文古诗生成

主讲：钟志诚；整理：曾有成、冯筱璐；单位：中国科学技术大学 人工智能与数据科学学院。

用 PyTorch 实现 Tiny GPT（Generative Pre-trained Transformer，生成式预训练 Transformer），从随机参数训练中文古诗模型，再输入“春”等开头，让它逐字续写。 正式训练、生成和测试统一在中科大107算力平台通过 Slurm 提交。课堂3学时、135分钟，完整训练与报告课后完成；建议接在第8次理论课 Transformer 之后，日期与截止时间另行通知。

## 材料入口

| 材料                                                                | 用途                                                   |
| ------------------------------------------------------------------- | ------------------------------------------------------ |
| [课堂课件](slides/实验06_TinyGPT五言诗生成.pptx)                     | 自回归任务、公式与代码对应、实测结果                   |
| [实验讲义](实验06_实验讲义.pdf) / [可编辑源文件](实验06_实验讲义.tex) | 原理、135分钟流程、任务与评分                          |
| [学生材料包](../downloads/lab06-tiny-gpt-26fall-B.zip)               | 课件、讲义、代码、古诗数据、报告模板，不含完整教师实现 |
| [学生代码](code/student.py)                                          | 唯一必改代码文件，T1–T6及 Hint                        |
| [热身](code/warmup.py) / [自检](code/checks.py)                       | 可运行小例子与分阶段检查                               |
| [Slurm入口](code/scripts/submit.sh)                                  | smoke、train、sample、evaluate四类作业                 |
| [数据说明](code/data/README.md)                                      | 筛选、整首去重、划分、未知字符与来源                   |
| [报告模板](report-template.md)                                       | 推导、自检、训练、生成与结果分析                       |

语料采用THU-CCPC（THU Chinese Classical Poetry Corpus，清华中国古典诗歌语料库）的五言子集：训练19,537首、验证3,935首、测试4,911首，保留官方划分。数据仅供学术使用，具体说明见 `code/data/SOURCE-TERMS.txt`。

## 最终能看到什么

输入一个开头，如“春”“山”“夜”，模型根据学到的字符概率逐字续写。语料统一为五言四句作品，保留来源字形（扩充子集以简体为主）。生成器逐字采样得到完整文本，句长、标点与诗句内容都来自模型输出，生成后保留原文。展示时保留原始输出，分别分析五字句与分行、局部搭配、全诗连贯性，以及重复和训练诗句复现。格式、语义与原创性需要分别评价。

比较同一权重、同一开头、同一种子下的温度0.8、1.0、1.2和贪心生成。另用 `inspect_poems.py` 检查第一段的句长及与训练诗句的完全重合；该脚本负责统计，四份生成原文均保留用于对照。预跑设置与结果见实验讲义第7.4节。

## 六个任务与135分钟流程

| 时间         | 任务              | 学生活动与可观察产出                         |
| ------------ | ----------------- | -------------------------------------------- |
| 0–10分钟    | 演示与复习        | 运行热身，解释下一字符预测                   |
| 10–30分钟   | T1 数据与目标     | 补全错位标签；说明按整首划分的必要性         |
| 30–50分钟   | T2 多头拆分与合并 | 写出 [B,T,d] ↔ [B,H,T,k]，核对通道顺序      |
| 50–75分钟   | T3 因果注意力     | 手算一行权重；实现缩放、掩码、归一化、加权和 |
| 75–95分钟   | T4 解码器块       | 连接前置层归一化与两条残差                   |
| 95–115分钟  | T5 模型与训练     | 连接嵌入、位置、块、输出与损失，提交短作业   |
| 115–135分钟 | T6 生成与评价     | 补全生成循环，制定正式训练与古诗展示计划     |
| 合计         | 135分钟           | 环境和数据课前准备；完整训练课后完成         |

核心任务由学生用基础张量运算、Linear、Embedding、LayerNorm、GELU（Gaussian Error Linear Unit，高斯误差线性单元）、Dropout、自动求导和优化器完成。现成 Transformer、TransformerDecoder、MultiheadAttention、scaled_dot_product_attention 及预训练模型不在核心任务可用接口范围内。参数注册和训练框架已提供，自动求导直接使用PyTorch。

## 先在本地完成代码自检

使用课程 PyTorch 环境；缺少依赖时在自己的环境中安装 `requirements.txt`。命令从 `code/` 执行：

```bash
python warmup.py
# 依次补全 student.py，再检查相应阶段
python checks.py data
python checks.py heads
python checks.py attention
python checks.py block
python checks.py model
python checks.py generate
python checks.py all
```

本地CPU（Central Processing Unit，中央处理器）用于热身与自检。学生骨架中的零值占位代码会在对应检查中报错，补全任务后再运行自检。自检会核对注意力数值、改变未来输入后前缀输出不变、参数获得梯度、权重更新和生成长度。

## 107平台：先准备文件与环境

先按实验01和平台[环境配置文档](https://107.ustc.edu.cn/docs/basics/environments/)安装Conda并准备含PyTorch的环境。通过“文件管理”上传学生材料包的ZIP文件并解压，进入解压后的 `lab06-tiny-gpt/code/`。直接上传文件夹若只得到空目录，改用上传ZIP再解压。在107网页的Web终端中检查文件，并查询平台上的目录与环境：

```bash
pwd
ls student.py train.py sample.py evaluate.py
ls data/train.txt data/val.txt data/test.txt
ls scripts/submit.sh scripts/run-job.sh
conda env list
```

`pwd` 输出当前目录的绝对路径；确认末尾为 `code`，将它填入网页的“工作目录”。若终端不在该目录，先用 `cd` 进入文件管理中显示的 `code/` 绝对路径。`conda env list` 列出环境名与路径，从中选择已安装PyTorch的课程环境，把完整环境路径末尾加 `/bin/python`，填写为 `LAB06_PYTHON`。

`your` 表示占位内容。将 `/your/env/bin/python` 整串替换为刚在107平台查到的解释器路径，再在同一Web终端检查：

```bash
export LAB06_PYTHON="/your/env/bin/python"
"$LAB06_PYTHON" -c "import sys; print(sys.executable)"
"$LAB06_PYTHON" -c "import torch; print(torch.__version__)"
```

两条检查分别输出实际解释器路径与PyTorch版本。GPU（Graphics Processing Unit，图形处理器）与CUDA（Compute Unified Device Architecture，统一计算设备架构）可用性在计算作业内检查。每个新建网页作业单独填写真实路径和 `export` 设置。终端显示混乱时可用 `clear` 清屏。

### 提交前的Slurm资源配置

| 资源           | 本实验设置 | Slurm参数                     |
| -------------- | ---------- | ----------------------------- |
| 节点、任务进程 | 各1个      | `--nodes=1`、`--ntasks=1` |
| 每节点GPU      | 1张        | `--gres=gpu:1`              |
| 每任务CPU      | 4个        | `--cpus-per-task=4`         |
| 每节点主内存   | 8G         | `--mem=8G`                  |
| 最长运行时间   | 1小时      | `--time=01:00:00`           |

4个CPU供同一个训练任务使用，按平台配置计为核或逻辑线程；8G表示主内存，GPU显存由所分配的卡决定。1小时是申请上限，实际耗时以作业日志为准。

## 107平台：网页提交作业

进入“作业 → 提交作业”，集群选本科生算力平台，工作目录选上述 `code/` 的绝对路径。表单中选择本人可用账户、`Students`分区和QOS（Quality of Service，服务质量），节点数1、单节点加速卡卡数1、最长运行时间1小时；标准输出、错误输出分别填 `job.%j.out`、`job.%j.err`，保存在工作目录中。QOS从本人账号的可用项中选择；平台补充资料中的 `default` 与 `qos_stu_default` 是两个不同名称。

在“命令”框填以下内容，把解释器示例路径换成上一步查到的值。任务数、CPU与主内存若无网页表单字段，用命令开头的3行 `#SBATCH` 指令补充1个任务、每任务4个CPU与8G主内存；若已在表单设置，则删除对应行。每项资源在表单或命令中设置一次。

```bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
set -euo pipefail
export LAB06_PYTHON="/your/env/bin/python"
export LAB06_DATA_DIR="$PWD/data"
bash scripts/run-job.sh smoke
```

网页已通过Slurm分配资源，命令直接调用 `run-job.sh` 执行当前阶段。普通终端的 `submit.sh` 负责调用一次 `sbatch`；两种入口分别使用各自的脚本，作业状态才能对应当前训练过程。短作业完成20次更新，检查路径、设备、训练和保存；成功后新建相同配置的网页作业，将末行 `smoke` 改为 `train`。各阶段依次提交，排队期间查看已有作业的状态。

## 107平台：也可从终端提交

若使用“文件管理”打开的普通终端，在 `code/` 中设置解释器和数据路径后，由 `submit.sh` 调用一次 `sbatch`。网页入口与此入口二选一。

```bash
export LAB06_PYTHON="/your/env/bin/python"
export LAB06_DATA_DIR="$PWD/data"
bash scripts/submit.sh smoke
```

查看作业状态与 `logs/lab06-poetry-作业号.out/.err`。短作业完成20次更新，用于核对路径、设备、训练和保存；生成质量在正式训练后评价。通过后提交正式训练：

```bash
bash scripts/submit.sh train
squeue -u "$USER"
# 作业结束后，将12345换成自己的作业号
sacct -j 12345 --format=JobID,State,Elapsed,MaxRSS
```

终端脚本默认请求1个节点、1个任务、1张GPU、每任务4个CPU、8G主内存、1小时；`Students`分区和`qos_stu_default`服务质量是沿用实验04/05的候选设置，须符合本人账号实际权限，可在提交命令后追加已核验的 `sbatch` 参数，例如用 `--qos=本人获准的值` 覆盖。正式训练在获配GPU的计算节点运行，脚本要求CUDA可用。`submit.sh` 检测到已在Slurm作业内会停止并提示使用 `run-job.sh`。

默认模型2层、4头、宽128、上下文32，词表5,409项，共1,785,600参数；批量64、3000次更新、学习率0.0003、Dropout概率0.1、种子2026，每300步验证一次。优化器为AdamW（Adam with decoupled Weight Decay），本实验设置权重衰减为0，采用固定学习率。`LAB06_STEPS`、`LAB06_BATCH_SIZE`、`LAB06_WIDTH`、`LAB06_LAYERS`、`LAB06_BLOCK_SIZE`、`LAB06_LR`、`LAB06_SEED`可配置；做对照时一次只改一个因素。

每个训练作业输出独立目录 `outputs/train-作业号/`，含 `best.pt`、`history.csv`、`run.json`、`bigram_validation.json`、`source/`。训练监测损失来自训练集前8193个字符；验证遍历完整验证文本，保存最低验证交叉熵的权重。测试指标在模型选定后单独计算。设备差异可能影响数值和采样结果；107平台的训练耗时记录在作业日志中。

## 107平台：提交古诗生成与最终测试

训练完成后指定选定运行目录的绝对路径。下面是普通终端提交命令：

```bash
export LAB06_RUN="$PWD/outputs/train-实际作业号"
export LAB06_PROMPT="春"
bash scripts/submit.sh sample
# 用验证集确定模型方案后，只进行一次最终测试
bash scripts/submit.sh evaluate
```

使用网页提交时，保留网页作业中的资源指令、解释器和数据路径，在“命令”框中同样填写 `LAB06_RUN` 与 `LAB06_PROMPT`；生成作业最后一行改为 `bash scripts/run-job.sh sample`。选定方案后另建测试作业，最后一行改为 `bash scripts/run-job.sh evaluate`。每个新网页作业都填写所需的 `export` 行。

采样作业使用该次训练保存的代码与权重，一次生成四份对照文本及参数记录，放入 `outputs/sample-作业号/`。默认添加诗歌边界的两个换行，随后以提示词开头继续生成80字符；保留完整原始输出。测试作业将结果存入 `outputs/evaluate-作业号/test_metrics.json`。排队期间查看已提交作业的状态。

下载生成文本后，本地可检查句长与训练集重合：

```bash
python inspect_poems.py outputs/sample-实际作业号/temperature-0.8.txt
```

二元字符计数基线只在训练集拟合，使用加一平滑。最终比较同一测试目标上的交叉熵与困惑度，并结合原始生成文本分析。困惑度只在相同数据、词表、上下文和计分规则下可比；温度改变采样分布，不改变固定权重的原始交叉熵。训练集之外的字符统一映射到未知词元，必须报告未知字符比例。

## 评分与提交

目标与维度15分；T1–T4实现35分；T5–T6实现与自检25分；训练与生成对照15分；复现与分析10分。选做只改变层数、上下文或位置编码之一，在验证集分析效果及代价。评分依据实现、实验过程和结果分析；诗歌文学性用于讨论。模型调试使用验证集，测试集留到方案选定后评价。

提交 `学号_姓名_lab06.zip`：本人代码（含脚本）、`report.pdf`、选定训练目录（含权重与代码快照）、四份生成文本与参数记录、一次最终测试结果、Slurm日志和作业状态。去掉环境、缓存、重复的数据副本；保留数据来源与指纹。报告内容按模板填写。

参考项目与“官方”含

- [Isaac Pérez的项目介绍](https://isaacperez.github.io/posts/TinyGPT/)直接链接到[isaacperez/tinygpt](https://github.com/isaacperez/tinygpt)：这是该作者项目的原始仓库，主旨是纯Python、零外部依赖地实现张量、自动求导与训练框架，适合作为课后扩展阅读。项目由Isaac Pérez发布。
- [OthersideAI/tinyGPT](https://github.com/OthersideAI/tinyGPT)是minGPT的分叉，代码保留Karpathy版权。课程模型与采样代码从其版本 `e8564668c00b65af1bb7afac3f4c9d15e725c29f`改编，保留[许可](THIRD_PARTY_LICENSES.txt)，按仓库作者标注来源。
- [Karpathy/minGPT](https://github.com/karpathy/minGPT)与[nanoGPT](https://github.com/karpathy/nanoGPT)是其作者维护的教学/训练参考；本实验使用PyTorch实现便于在107的GPU运行。
- [GoClaw导学](https://goclawai.cn/llm/start/)与[从零训练TinyGPT](https://goclawai.cn/llm/tiny-gpt/)用于组织“短流程验证—正式训练—重载生成—对照分析”。其中的微调、服务与框架开发可作课后扩展。

本课保留可学习位置、前置归一化、GELU、无偏置词表头；简化优化调度、移除参考采样函数遇空格停止的逻辑，加入整首诗划分、因果性检查、基线和Slurm入口。输入与输出嵌入各自使用独立权重。旧版 `26fall-B/labs/06_mlp_backward`为历史编号，保留原样。

平台操作参考2026-10-27提供的《坑 of 本科生算力平台.docx》，包括ZIP上传、环境路径查询与网页字段。清屏命令和作业提交方式按下列文档核对。命令含义参见[Slurm sbatch文档](https://slurm.schedmd.com/sbatch.html)、[Conda环境列表](https://docs.conda.io/projects/conda/en/stable/commands/env/list.html)与[clear手册](https://invisible-island.net/ncurses/man/clear.1.html)。账户、分区与QOS按平台显示的可用项填写。
