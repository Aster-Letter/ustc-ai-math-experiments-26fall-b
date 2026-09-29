# Python 语法带练：分章脚本

每个文件都可独立运行。按 01–10 的顺序讲解，也可以直接打开某一章运行和调试。

配套讲稿：[Python语法带练.md](../../Python语法带练.md)。

| 文件 | 内容 |
|---|---|
| [01_getting_started.py](01_getting_started.py) | 起步：打印一条消息（教材第 1 章） |
| [02_variables.py](02_variables.py) | 变量和简单的数据类型（教材第 2 章） |
| [03_lists.py](03_lists.py) | 列表简介（教材第 3 章） |
| [04_loops_and_slices.py](04_loops_and_slices.py) | 操作列表：循环、切片、复制和元组（教材第 4 章） |
| [05_conditions.py](05_conditions.py) | if 语句（教材第 5 章） |
| [06_dictionaries.py](06_dictionaries.py) | 字典与嵌套（教材第 6 章；附决策树所需的小工具） |
| [07_input_and_while.py](07_input_and_while.py) | 用户输入和 while 循环（教材第 7 章） |
| [08_functions.py](08_functions.py) | 函数与导入（教材第 8 章） |
| [09_classes.py](09_classes.py) | 类：实例、属性和方法（教材第 9 章，选讲 9.1–9.2） |
| [10_read_files.py](10_read_files.py) | 读取文件：文本 → 行 → 字段 → 特征和标签（教材 10.1） |

在本目录运行，例如：

```bash
python 01_getting_started.py
python 08_functions.py
python 10_read_files.py
```

- 只依赖 Python 标准库。第 7 章默认模拟输入；现场演示时将 `ENABLE_INPUT` 改为 `True`。
- 第 8 章保留 S1 函数练习，第 10 章保留 S2 计数练习；两者可以分别完成。
- 第 10 章自动定位本目录的 [西瓜文本数据](data/watermelon_samples.txt)，从其他工作目录启动也可正常读取。数据保留教材原编号 1、2、9、11，只用于语法练习。
