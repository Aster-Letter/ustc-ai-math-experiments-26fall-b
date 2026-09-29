"""07 用户输入和 while 循环（教材第 7 章）。

主讲：钟志诚；整理：曾有成。
单位：中国科学技术大学 人工智能与数据科学学院。
配套讲稿：../../Python语法带练.md。
在本目录运行：python 07_input_and_while.py
本文件可独立运行，只依赖 Python 标准库。
"""

print("\n07 用户输入和 while 循环")
ENABLE_INPUT = False  # 现场演示 input 时改为 True；默认本文件直接跑完。
if ENABLE_INPUT:
    text = input("请输入好瓜的数量（整数，例如 2）：")
else:
    text = "2"  # 模拟键盘输入，类型仍然是 str。
count = int(text)
print("输入文本：", repr(text), "；加 1 后：", count + 1)

index = 0
labels = [1, 1, 0, 0]
while index < len(labels):
    print("while 访问：", index, labels[index])
    index += 1

index = 0
while index < len(labels):
    if labels[index] == 0:
        print("找到第一个坏瓜，行索引：", index)
        break
    index += 1
# 讨论：删除第一段循环的 index += 1 会怎样？只口述，不运行无限循环。
