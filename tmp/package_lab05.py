"""按课程提交说明复制白名单文件，创建ZIP并逐字节校验解压副本。"""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / '实验05_宠物主体分割与小型UNet'
NAME = 'PB24081512_吴炳睿_lab05'
DEST = ROOT / NAME
ZIP = ROOT / (NAME + '.zip')
VERIFY = ROOT / 'tmp' / 'lab05-package-verify'
for path in (DEST, ZIP, VERIFY):
    if path.exists():
        raise FileExistsError(f'Refusing to overwrite: {path}')

def copy(source, relative):
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

def copy_python(source, relative):
    for path in sorted(source.glob('*.py')):
        copy(path, Path(relative) / path.name)

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

runs = {'basic': 'basic-local-01', 'improved': 'improved-local-02', 'unet': 'unet-local-01'}
fingerprints = set()
for label, folder in runs.items():
    src = LAB / 'code/outputs' / folder
    metadata = read(src / 'run.json')
    assert metadata['train_n'] == 2941 and metadata['val_n'] == 739
    assert metadata['partial_run'] is False
    assert metadata['config']['model'] == label
    assert metadata['config']['epochs'] == 20
    assert metadata['config']['batch_size'] == 16
    assert metadata['config']['lr'] == 0.001
    assert metadata['config']['seed'] == 42
    fingerprints.add(metadata['split_fingerprint'])
    with (src / 'history.csv').open() as handle:
        history = list(csv.DictReader(handle))
    assert len(history) == 20
    best = max(history, key=lambda row: float(row['val_iou']))
    assert int(best['epoch']) == metadata['best_epoch']
    assert float(best['val_iou']) == metadata['best_val_iou']
    for filename in ('run.json', 'history.csv', 'curves.png', 'validation_examples.png', 'splits.json'):
        copy(src / filename, Path('runs') / label / filename)
    copy_python(src / 'source', Path('runs') / label / 'source')
assert len(fingerprints) == 1

copy(LAB / 'report.pdf', 'report.pdf')
copy_python(LAB / 'code', 'code')
copy(LAB / 'code/requirements.txt', 'code/requirements.txt')
for path in sorted((LAB / 'code/scripts').iterdir()):
    if path.is_file() and path.suffix in ('.sh', '.sbatch'):
        copy(path, Path('code/scripts') / path.name)

selected = LAB / 'code/outputs/improved-local-02'
for filename in ('best.pt', 'run.json', 'splits.json'):
    copy(selected / filename, Path('selected') / filename)
copy_python(selected / 'source', 'selected/source')

evaluation = LAB / 'code/outputs/final-test-01'
metrics = read(evaluation / 'metrics.json')
assert metrics['split'] == 'test' and metrics['count'] == 3669
assert metrics['partial_training'] is False and metrics['model'] == 'improved'
assert metrics['selected_epoch'] == 16 and metrics['data_kind'] == 'Oxford-IIIT Pet'
with (evaluation / 'per_image.csv').open() as handle:
    assert len(list(csv.DictReader(handle))) == 3669
for filename in ('metrics.json', 'per_image.csv', 'examples.png', 'best_worst_examples.png'):
    copy(evaluation / filename, Path('evaluation') / filename)

for prefix in ('basic-local-01-', 'improved-local-02-', 'unet-local-01-', 'final-test-01-'):
    paths = list((LAB / 'code/logs').glob(prefix + '*.log'))
    assert len(paths) == 1
    copy(paths[0], Path('logs') / paths[0].name)
copy(LAB / 'report-assets/checks.log', 'logs/report-checks.log')

# 报告中引用的插图、案例清单和验证逐图记录，作为补充证据保留。
for path in sorted((LAB / 'report-assets').iterdir()):
    if path.is_file() and path.suffix in ('.png', '.json', '.log'):
        copy(path, Path('report-assets') / path.name)
for label, folder in {'basic': 'basic-val-01', 'improved': 'improved-val-report-01', 'unet': 'unet-val-01'}.items():
    for filename in ('metrics.json', 'per_image.csv'):
        copy(LAB / 'code/outputs' / folder / filename, Path('runs') / label / 'validation' / filename)
copy(LAB / 'code/outputs/unet-comparison/summary.csv', 'runs/comparison-summary.csv')

readme = '''# 实验05提交与复现说明

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
'''
(DEST / 'README.md').write_text(readme, encoding='utf-8')

assert len(list(DEST.rglob('*.pt'))) == 1
assert len(list(DEST.rglob('*.pdf'))) == 1
files = sorted(p for p in DEST.rglob('*') if p.is_file())
for path in files:
    assert not set(path.relative_to(DEST).parts) & {'__pycache__', '.git', 'data'}
    assert path.suffix != '.pyc'
with zipfile.ZipFile(ZIP, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for path in files:
        archive.write(path, Path(NAME) / path.relative_to(DEST))
with zipfile.ZipFile(ZIP) as archive:
    assert archive.testzip() is None
    assert {Path(name).parts[0] for name in archive.namelist()} == {NAME}
    for name in archive.namelist():
        assert '..' not in Path(name).parts and not Path(name).is_absolute()
    archive.extractall(VERIFY)
for path in files:
    restored = VERIFY / NAME / path.relative_to(DEST)
    assert hashlib.sha256(path.read_bytes()).digest() == hashlib.sha256(restored.read_bytes()).digest()
print(json.dumps({'directory': str(DEST), 'zip': str(ZIP), 'files': len(files),
                  'zip_bytes': ZIP.stat().st_size,
                  'sha256': hashlib.sha256(ZIP.read_bytes()).hexdigest(),
                  'verified_extract': str(VERIFY / NAME)}, ensure_ascii=False, indent=2))
