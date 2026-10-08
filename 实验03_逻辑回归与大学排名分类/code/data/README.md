# QS 2026 数据来源、字段与课堂划分

QS（Quacquarelli Symonds）大学排名，访问与固定下载日期2026-10-08。本实验的实际下载源是第三方公开镜像，不是从QS官网逐校采集，也未逐校核验真实性；官方资料用于核对字段定义与榜单方法。

- [实际CSV镜像](https://raw.githubusercontent.com/Olcmyk/university-rankings-tracker/main/2026_QS_World%20University_Rankings.csv)
- [镜像仓库](https://github.com/Olcmyk/university-rankings-tracker)
- [QS官方学校分类](https://support.qs.com/hc/en-gb/articles/360021876820-QS-Institution-Classifications)
- [QS官方排名方法](https://www.qs.com/insights/world-university-rankings-methodology)

完整原文件 `qs2026_raw.csv` 1504行30列，SHA-256（Secure Hash Algorithm 256-bit）摘要 `3e6266bb55c5636ae1c09bba32e7afb39bc20b6d5def73197de2f0f2e547e300`。源表来自第三方整理；不额外宣称公共领域或另授许可。学生包只包含课堂划分和出处，原表在本地材料目录保留用于重建。

## 标签与划分

目标 `top500`：源Rank小于或等于500为1，榜单其余学校为0。不是按前500行切分；源表并列名次使正类共502所。源Rank有如701-710的区间，还有低排名段的区间起点数值；它们都在500之外，不影响本标签。跨越500的区间应视为标签不明，不能猜测，本固定文件没有此情况。不能用这些下界值训练“精确名次回归”。

学校名无重复。每类用NumPy种子20261008打乱，按round(60%×类样本数)、round(20%×类样本数)、剩余样本分配，再打乱每份内部顺序。三份学校互斥；不做重采样，不人工挖空，保持自然类别比例。源表行号从1开始保留为row_id，它与原排名排序相关，严禁作输入。

| 划分 | 样本数 | 正类数 | 实际特征缺失 |
| --- | ---: | ---: | --- |
| train | 902 | 301 | status 31；国际教师分数49；国际学生分数18 |
| val | 300 | 100 | status 13；国际教师分数20；国际学生分数12 |
| test | 302 | 101 | status 4；size 1；research 1；国际教师分数18；国际学生分数7 |

标签均有效。缺失标签处理只通过C1小例子练习。缺失是该镜像的真实空值，不声称其机制是完全随机。测试统计仅由教师构建时记录，学生训练/选模程序不读取测试表。

## 原始列到课堂字段

| 原始列 | 课堂列 | 模型处理 |
| --- | --- | --- |
| Faculty Student Ratio SCORE | faculty_student_score | 数值分数，训练均值填补并标准化 |
| International Faculty  SCORE | international_faculty_score | 原名Faculty后为两个空格；分数，不是人数或百分比 |
| International Student SCORE | international_student_score | 数值分数，非原始比例 |
| Region | region | 独热编码 |
| Status | status | Public、Private not for Profit、Private for Profit等，独热编码 |
| Size | size | S/M/L/XL，统一独热编码，不假设等距 |
| Focus | focus | SP/FO/CO/FC，学科覆盖类型，独热编码 |
| Research | research | LO/MD/HI/VH，研究活跃程度，独热编码 |
| Name | name | 保留追溯，不输入 |
| 原文件行号 | row_id | 新增追溯列，不能输入 |
| Rank派生 | top500 | 二分类标签，不能作为特征 |

三个数值列分别用训练非缺失均值填补，填补后计算总体标准差ddof=0；常数列尺度1，全空训练列均值0。每个类别字段取训练非缺失类别排序，再附Unknown；缺失和未见值映射Unknown。完整独热组包含所有类别，独热列不标准化。列顺序由训练状态固定。

完整组3个数值+25个独热=28维，增广后29维。精简组删除focus和research，共18维、增广后19维。名称、行号、排名、所有单项排名、总分、上年排名及完整评分向量不输入；只使用上述白名单。

## 可用时点与边界

本实验用部分同年已公布指标识别同年排名区间，不能称为预测未来排名。所选分数仍参与或关联排名构造，这是教学分类任务的局限。没有上榜不等于负类，源表之外的学校不在评价范围内。跨年任务要另建时点一致的输入/标签和时间划分。

教师在实验目录运行 `python teacher/prepare_classroom_data.py` 可重建。学生无需重建或另下载。完整摘要、版本、映射和划分在 `classroom/split_manifest.json`。原始资料的缺失和分段名次应如实保留，不为追求指标修改。
