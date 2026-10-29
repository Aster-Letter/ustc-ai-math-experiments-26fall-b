# 质谱分子识别课程大作业

《人工智能数学原理与算法 B》· 2026 年秋季

第一次接触质谱？先读 [赛题与数据入门](赛题与数据入门.md)，再按本文开始实验。

## 做什么

参加 [Enveda CASMI 2026](https://www.kaggle.com/competitions/enveda-CASMI26-molecule-id-mass-spectra)，根据质谱识别小分子结构。可以把质谱理解为分子的“碎片线索”：峰的位置和强度帮助我们寻找原来的分子。

输入是一个分子的一张或多张质谱；输出是按可能性排序的候选结构，最多 25 个。结构用 SMILES 字符串表示，例如乙醇是 `CCO`。每个分子提交一行，候选用分号分隔；正确答案排得越靠前，得分越高。

项目已提供“谱分箱 → 余弦相似度检索 → 合并候选”的基线。重点是跑通流程、设计改动并解释结果，不要求化学背景或大型深度模型。

## 怎样组队和完成作业

**三人一组，每组最终汇报共 5 分钟。** 三人分别注册 Kaggle 账号，在竞赛页报名并接受规则，由一人在 Team 页面发起邀请或合并，另外两人接受，组成同一支队伍。Kaggle 是运行代码、提交预测并查看成绩的平台。

每组完成以下工作：

1. 跑通基线，完成至少 **两项有明确目的的改动**，保留至少 **三组可比较实验**。可从分箱宽度、强度变换、参考库规模入手。
2. 在 Kaggle 完成至少 **一次成功评分的正式提交**，保存版本、分数和截图。
3. 提交一份小组材料，汇报方法、对比结果、失败分析和三位成员的贡献。允许参考公开代码和使用 AI，说明来源及自己的工作。

## 什么时候交

| 事项 | 北京时间 |
| --- | --- |
| 课程材料截止 | **待公布** |
| 小组汇报 | **待公布**，每组 5 分钟 |
| Kaggle 报名及组队截止 | 2026 年 12 月 8 日 07:59 |
| Kaggle 最终提交截止 | 2026 年 12 月 15 日 07:59 |

竞赛日期见[官方日程](https://www.kaggle.com/competitions/enveda-CASMI26-molecule-id-mass-spectra/overview)，如有调整以官方为准。

## 交什么、交到哪里

**Kaggle：** 提交运行代码生成 `submission.csv` 的 Notebook 版本，等待评分完成。具体操作见下方“提交到 Kaggle”。

**课程：** 每组提交 `组号_队伍名_final_project.zip`，**提交渠道待公布**。材料包括：

- 代码、依赖和复现步骤，以及使用的额外模型或数据的获取方式。
- 小组报告（建议 4–6 页）：成员姓名、学号、Kaggle 用户名与队伍链接，方法、三组实验对比、结果分析、成员贡献及代码和 AI 使用说明。
- 汇报幻灯片（建议 5–6 页，附可编辑文件）、实验记录、选定版本的 `submission.csv`，以及提交版本、状态、分数、时间和运行日志。

原始数据、环境和账号凭据无需打包。实验记录用一张表即可：**版本｜改动｜数据与参数｜指标｜耗时｜结论｜负责人**。

## 开始实验

下载[课程数据](https://pan.ustc.edu.cn/share/index/5a8f5ad972224a97b401?p=1)（密码 **C8F3**），将 `train.parquet`、`test.parquet`、`sample_submission.csv` 放到 `data/raw/`。从项目根目录打开终端，按下面步骤运行。先用小谱库完成本地实验，再按第三步用 B2 全量谱库完成正式提交。

<details>
<summary><strong>第一步：配置环境，跑通本地基线</strong></summary>

使用实验课已有的 conda，新建环境；已有同名环境时直接激活。

```text
conda create -n casmi-course --override-channels -c conda-forge python=3.11 pip
conda activate casmi-course
python -m pip install -r tools/environments/baseline.txt
python -m submission.check_environment
```

下面四条命令依次完成抽样、划分、预测和评分。`python -m` 表示运行项目里的指定 Python 模块；`--` 开头的是参数，后面跟文件路径或数值。

**① 抽取小样本。** 从训练文件中随机抽取 5000 张谱，保存到 `reference_sample.parquet`，供后续实验使用。`--seed 0` 固定随机种子，方便重复得到相同的抽样结果。

```text
python -m data.scripts.inspect_data --file data/raw/train.parquet --sample-out data/processed/reference_sample.parquet --sample-rows 5000 --seed 0
```

**② 划分验证数据。** 从小样本中选取最多 200 个符合条件的分子，生成参考谱库、待预测的查询谱和正确答案，保存到 `data/processed/validation/`。`--mode known` 保留同一分子的其他谱用于检索，移除查询谱及其重复项；查询分为选参数用的 `tune` 和最终验证用的 `holdout`。

```text
python -m evaluation.build_validation --reference data/processed/reference_sample.parquet --out data/processed/validation --mode known --molecules 200 --seed 0
```

**③ 运行基线预测。** 用 `--reference` 指定的参考谱库，为 `--queries` 中每个分子检索候选结构，预测结果和运行参数保存到 `outputs/B0/`。`B0` 是这次基线实验的编号。

```text
python -m algorithms.baseline.predict --reference data/processed/validation/reference.parquet --queries data/processed/validation/queries_tune.parquet --out outputs/B0
```

**④ 给预测评分。** 将 `--predictions` 中的预测与 `--labels` 中的正确答案比较，计算 MRR 和命中率，保存到 `outputs/B0/metrics.json`；`--reference` 还用于统计参考库覆盖了多少正确结构。

```text
python -m evaluation.evaluate --predictions outputs/B0/predictions.csv --labels data/processed/validation/labels_tune.csv --reference data/processed/validation/reference.parquet --out outputs/B0
```

结果在 `outputs/B0/`：`predictions.csv` 是预测，`config.json` 是参数，`metrics.json` 是指标，`run_summary.json` 含耗时。MRR@25 是正确候选排名倒数的平均值，例如排第 2 得 0.5，未命中得 0；越高越好。本地默认按字符串匹配，是课堂近似指标，官方按结构评分。

这里验证的是“参考库已有该结构的其他谱，能否找回来”。`tune` 用于选参数，固定方案后将上述预测和评分命令中的 `tune` 换成 `holdout`，输出换到新目录做最终验证。可见 `test.parquet` 用于检查运行流程。若提示可用结构不足，增大抽样量。

</details>

<details>
<summary><strong>第二步：改进方法并比较结果</strong></summary>

复用同一验证划分。下面两项改动可以作为起点，也可以自行设计：

```text
python -m algorithms.baseline.predict --reference data/processed/validation/reference.parquet --queries data/processed/validation/queries_tune.parquet --out outputs/A1 --power 1
python -m algorithms.baseline.predict --reference data/processed/validation/reference.parquet --queries data/processed/validation/queries_tune.parquet --out outputs/A2 --bin-width 0.5
```

`A1` 取消强度平方根变换，`A2` 将分箱宽度从 1 改成 0.5。将第一步评分命令中的两处 `B0` 分别换成 `A1`、`A2`，给两组结果评分，再比较：

```text
python -m evaluation.compare_runs --a outputs/B0 --b outputs/A1
python -m evaluation.compare_runs --a outputs/B0 --b outputs/A2
```

记录改动的理由和实际结果，没有提升的尝试也值得分析。更换参考库规模、候选筛选或学习排序都可以继续探索。纯谱库检索只能返回参考库中已有的结构。

代码位置：`data/scripts/` 读取与画谱图，`algorithms/baseline/` 表示与检索，`evaluation/` 划分与评分，`submission/` 打包与提交。各脚本加 `--help` 查看参数。

</details>

<details>
<summary><strong>第三步：使用 B2 全量谱库提交到 Kaggle</strong></summary>

B0 用 5000 张谱练习流程，B2 将参考库扩大为全部训练谱。B2 保持分箱宽度 1、强度平方根变换、20 ppm 筛选和最高分合并，分批读取数据。全量参考库始终保留，程序只对符合当前查询筛选条件的谱计算相似度。

**1. 准备 B2 代码。** 在安装了课程依赖的环境中执行，将 `YOUR_USERNAME` 换成自己的用户名。每个构建目录只生成一次。

```text
python -m submission.prepare_assets --full-training --out submission/build/B2 --username YOUR_USERNAME
```

生成 `submission/build/B2/notebook/`，其中 `main.py` 是独立运行程序。它直接使用官方竞赛输入中的 `train.parquet` 和 `test.parquet`，无需上传谱库或更新 B0 的 Dataset。

**2. 登录、上传并等待运行。** 首次使用 Kaggle 命令行时，在课程 Python 环境中安装并登录：

```text
python -m pip install -r tools/environments/cli.txt
kaggle auth login
```

按提示完成浏览器授权。然后上传 B2：

```text
kaggle kernels push -p .\submission\build\B2\notebook
kaggle kernels status YOUR_USERNAME/casmi-b2-full-library
```

命令中的 `YOUR_USERNAME` 换成自己的 Kaggle 用户名。上传成功后终端会给出程序链接；后续查询以这个链接中的实际名称为准。

日志先显示检查全部参考谱，再显示 `Scanned ...` 扫描进度。运行完成后，打开个人 Code 中的 **CASMI B2 Full Library**，在 Output 中确认 `submission.csv`；`run_summary.json` 的 `reference_spectra` 应为完整训练文件中有结构标签的谱数（当前数据为 2,539,608）。

**3. 网页提交评分。** 在竞赛 Submissions 页面点击 **Submit Prediction**，选择 **CASMI B2 Full Library**、成功运行的版本和 `submission.csv`，备注写 `B2 full library`。等待公开分数出现。

`B2` 是实验名称；Kaggle 的 `Version 1/2/...` 是这份代码的保存次数，提交时选择页面实际显示的成功版本。

如需在本地试跑，使用新的输出目录：

```text
python submission/build/B2/notebook/main.py --train data/raw/train.parquet --test data/raw/test.parquet --out outputs/B2_deployed
```

这个命令检查公开测试数据上的运行流程。全量训练库包含原本用于本地验证的谱，比较验证成绩时，应先从库中移除验证查询及其重复项。

</details>

<details>
<summary><strong>可选：上传自己准备的谱库（以 B0 为例）</strong></summary>

以下以 `B0` 为例；选用其他实验时替换对应目录。`YOUR_USERNAME` 换成负责提交成员的 Kaggle 用户名。

**1. 打包并在本地运行提交入口。** 在 `casmi-course` 环境执行：

```text
python -m submission.prepare_assets --reference data/processed/reference_sample.parquet --config outputs/B0/config.json --out submission/build/B0 --username YOUR_USERNAME
python submission/build/B0/notebook/main.py --assets submission/build/B0/assets --test data/raw/test.parquet --out outputs/B0_deployed
```

成功后得到 `outputs/B0_deployed/submission.csv`。上传包位于 `submission/build/B0/`，包括 `assets/`（参考谱库、算法和参数）与 `notebook/`（运行入口）。在 `assets/README.md` 补充数据来源和小组改动，在 `assets/dataset-metadata.json` 将许可证占位符换成符合数据使用条款的 Kaggle 许可证标识。

**2. 配置 Kaggle 命令行并上传。** 首次使用时执行：

```text
conda create -n kaggle-cli --override-channels -c conda-forge python=3.11 pip
conda activate kaggle-cli
python -m pip install -r tools/environments/cli.txt
kaggle auth login
kaggle datasets create -p .\submission\build\B0\assets --dir-mode zip
kaggle datasets status YOUR_USERNAME/casmi-course-assets
```

按提示在浏览器登录；无法使用浏览器授权时，在 [API 设置](https://www.kaggle.com/settings/api) 生成令牌，运行 `python tools/kaggle/configure_token.py` 输入。数据集就绪后推送代码：

```text
kaggle kernels push -p submission/build/B0/notebook
kaggle kernels status YOUR_USERNAME/casmi-course-submit
```

**3. 等待运行完成，提交该版本。** 在 Kaggle 的个人 Code 页面打开 `casmi-course-submit`，确认输出含 `submission.csv`，记下版本号。下例的 `3` 换成实际版本：

```text
kaggle competitions submit enveda-CASMI26-molecule-id-mass-spectra -k YOUR_USERNAME/casmi-course-submit -v 3 -f submission.csv -m "B0"
kaggle competitions submissions enveda-CASMI26-molecule-id-mass-spectra
```

看到成功评分后保存分数、版本和截图。由一位成员统一提交；返回超时先查看提交记录。后续改进使用新的构建目录，并以 `kaggle datasets version -p .\submission\build\A1\assets --dir-mode zip -m "A1"` 更新已有附件，再推送和提交新代码版本。

正式评分会替换为隐藏测试数据并重新运行代码；保留入口中的官方数据读取逻辑和断网设置。外部资源遵守[竞赛规则](https://www.kaggle.com/competitions/enveda-CASMI26-molecule-id-mass-spectra/rules)，其中 [NIST 质谱及其训练模型禁用](https://www.kaggle.com/competitions/enveda-CASMI26-molecule-id-mass-spectra/discussion/744470)。命令参考 [Kaggle 官方说明](https://github.com/Kaggle/kaggle-cli/blob/main/docs/competitions.md)。

</details>
