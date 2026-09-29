"""03 列表简介（教材第 3 章）。

主讲：钟志诚；整理：曾有成。
单位：中国科学技术大学 人工智能与数据科学学院。
配套讲稿：../../Python语法带练.md。
在本目录运行：python 03_lists.py
本文件可独立运行，只依赖 Python 标准库。
"""

print("\n03 列表简介")
colors = ["青绿", "乌黑", "浅白"]
print("首项：", colors[0], "；末项：", colors[-1], "；长度：", len(colors))
colors.append("青绿")
removed = colors.pop()
print("弹出的元素：", removed, "；剩余：", colors)
colors[0] = "浅白"  # 只修改语法示例，不修改配套数据文件。
print("修改后的首项：", colors[0])
ids = [9, 1, 11, 2]
print("sorted 的返回值：", sorted(ids), "；原列表：", ids)
ids.sort()
print("sort 修改原列表：", ids)
# 观察练习：为什么最后一个有效索引是 len(colors)-1？
