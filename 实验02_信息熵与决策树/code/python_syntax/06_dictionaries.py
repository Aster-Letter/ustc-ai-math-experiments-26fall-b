"""06 字典与嵌套（教材第 6 章；附决策树所需的小工具）。

主讲：钟志诚；整理：曾有成。
单位：中国科学技术大学 人工智能与数据科学学院。
配套讲稿：../../Python语法带练.md。
在本目录运行：python 06_dictionaries.py
本文件可独立运行，只依赖 Python 标准库。
"""

print("\n06 字典与嵌套")
record = {"original_id": 1, "color": "青绿", "label": 1}
print("查标签：", record["label"])
print("不存在的备注：", record.get("note", "暂无备注"))
record["note"] = "课堂观察"
for key, value in record.items():
    print(key, "->", value)

leaf = {"feature": None, "label": 0, "children": {}}
node = {"feature": 3, "label": 0, "children": {"模糊": leaf}}
print("模糊分支的类别：", node["children"]["模糊"]["label"])
# 上面的单分支字典仅演示嵌套结构，不是一棵训练完成的决策树。

textures = ["清晰", "清晰", "稍糊", "模糊"]
labels = [1, 1, 0, 0]
print("不同纹理：", sorted(set(textures)))
for index, value in enumerate(textures):
    print("行索引：", index, "；纹理：", value)
for value, label in zip(textures, labels):
    print("对应的一对：", value, label)
# set 去重且无索引顺序保证；sorted 只是让显示顺序固定。
# zip 按位置配对，并在最短输入耗尽时停止；样本和标签长度应一致。
