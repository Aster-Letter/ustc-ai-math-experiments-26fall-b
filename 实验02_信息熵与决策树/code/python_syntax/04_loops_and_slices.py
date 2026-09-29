"""04 操作列表：循环、切片、复制和元组（教材第 4 章）。

主讲：钟志诚；整理：曾有成。
单位：中国科学技术大学 人工智能与数据科学学院。
配套讲稿：../../Python语法带练.md。
在本目录运行：python 04_loops_and_slices.py
本文件可独立运行，只依赖 Python 标准库。
"""

print("\n04 操作列表")
labels = [1, 1, 0, 0]  # 对应教材原编号 1、2、9、11 的标签。
total = 0
for item in labels:
    total += item
    print("本次标签：", item, "；累计好瓜数：", total)
print("循环结束，好瓜数：", total)
print("range(4)：", list(range(4)))
print("前两项：", labels[:2], "；从第 3 项开始：", labels[2:])

features = [0, 1, 2, 3, 4, 5]
alias = features
copied = features.copy()
copied.remove(3)
print("原候选列：", features, "；副本：", copied)
print("alias 与 features 是同一个对象：", alias is features)
shape = (4, 6)
print("元组保存形状：", shape)
# 修改练习：将上面的 total += item 临时移到循环外，预测输出再运行。
# 提醒：copy() 在此复制一维列表；嵌套列表的内层对象仍会共享。
