"""05 if 语句（教材第 5 章）。

主讲：钟志诚；整理：曾有成。
单位：中国科学技术大学 人工智能与数据科学学院。
配套讲稿：../../Python语法带练.md。
在本目录运行：python 05_conditions.py
本文件可独立运行，只依赖 Python 标准库。
"""

print("\n05 if 语句")
label = 0
if label == 1:
    print("好瓜")
elif label == 0:
    print("坏瓜")
else:
    print("标签应为 0 或 1")

texture = "清晰"
print("相等判断：", texture == "清晰")
print("是否在取值列表中：", texture in ["清晰", "稍糊", "模糊"])
print("两个条件都成立：", label == 0 and texture == "清晰")
print("至少一个条件成立：", label == 1 or texture == "清晰")
feature = 0
print("列编号 0 是 None 吗：", feature is None)
remaining = []
if not remaining:
    print("没有剩余候选属性")
# 修改练习：把 feature 改为 None，重新运行最后两条判断。
