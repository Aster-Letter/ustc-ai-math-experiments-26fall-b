"""无需补全即可运行：观察编码、输入标签对齐与下三角可见矩阵。"""
import torch

text = "hello"
chars = sorted(set(text))
stoi = {char: index for index, char in enumerate(chars)}
ids = torch.tensor([stoi[char] for char in text])
print("词表:", stoi)
print("原文:", text, "编号:", ids.tolist())
print("输入:", text[:-1], "标签:", text[1:])
print("允许读取的位置（1=可见，行=查询，列=键）:")
print(torch.tril(torch.ones(4, 4, dtype=torch.int64)))
print("试一试：把 hello 改成 banana，再运行并解释第2行。")
