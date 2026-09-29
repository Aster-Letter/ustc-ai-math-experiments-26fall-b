"""10 读取文件：文本 → 行 → 字段 → 特征和标签（教材 10.1）。

主讲：钟志诚；整理：曾有成。
单位：中国科学技术大学 人工智能与数据科学学院。
配套讲稿：../../Python语法带练.md。
在本目录运行：python 10_read_files.py
本文件可独立运行，只依赖 Python 标准库。
"""

print("\n10 读取文件")
from pathlib import Path

# __file__ 是当前 .py 文件的位置；parent 是它所在的目录。
# Path 对象之间的 / 表示拼接路径，不是数值除法。
script_dir = Path(__file__).resolve().parent
path = script_dir / "data" / "watermelon_samples.txt"
print("当前工作目录：", Path.cwd())
print("本次读取：", path)
contents = path.read_text(encoding="utf-8")
print("文件全部内容：")
print(contents.rstrip())

lines = contents.splitlines()
print("表头：", lines[0])
X, y, original_ids = [], [], []
for line in lines[1:]:
    parts = line.split()  # 本文件以空白分隔，字段本身不含空格。
    original_ids.append(int(parts[0]))
    X.append(parts[1:7])
    y.append(int(parts[7]))
print("教材原编号：", original_ids)
print("X 的形状：", len(X), "行 ×", len(X[0]), "列")
print("第一行特征：", X[0])
print("标签 y：", y)
print("读入的第一条标签类型：", type(y[0]))

# TODO S2：统计 y 中的好瓜数并打印。
# Hint：用 for 和 if 逐个检查标签，为 1 时累加；这 4 行应得到 2。
# 这里保留空位，不修改文件内容。

# 本课到读取文件为止。四条子集只练语法，不计算测试准确率。
