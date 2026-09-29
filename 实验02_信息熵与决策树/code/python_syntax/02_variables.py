"""02 变量和简单的数据类型（教材第 2 章）。

主讲：钟志诚；整理：曾有成。
单位：中国科学技术大学 人工智能与数据科学学院。
配套讲稿：../../Python语法带练.md。
在本目录运行：python 02_variables.py
本文件可独立运行，只依赖 Python 标准库。
"""

print("\n02 变量和简单的数据类型")
color = "青绿"
sample_id = 1
price = 3.5  # 人工设置的价格，仅用于演示浮点数，不是教材特征。
label = 1
print(type(color), type(sample_id), type(price))
print(f"编号 {sample_id} 的西瓜，色泽为{color}")
print("每只价格：", price, "；两只价格：", price * 2)
raw_color = "  青绿  "
print("原文本：", repr(raw_color), "；清理后：", raw_color.strip())
print("除法：", 5 / 2, "整除：", 5 // 2, "余数：", 5 % 2)
print("字符串拼接：", "1" + "1", "；数值相加：", int("1") + 1)
# 修改练习：把 label 改为 0；观察赋值会改变哪个变量。
