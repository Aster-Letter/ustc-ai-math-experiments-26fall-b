"""模拟的微型书店数据管理与统计程序。

阅读 本目录的 README.md，搜索 LAB01_TODO 完成 B1–B6（B2 分为两个小方法）。
运行本文件打开菜单；check_book_tasks.py 使用独立数据分阶段检查。
"""

import sys

import numpy as np

from book_support import CSVReader, check_money, run_menu


class Book:
    """一本书的当前信息；同名书的进货成本在本项目中保持不变。"""

    def __init__(self, title, cost, price, stock):
        """接收书名、进货单价、当前售价和库存册数，数值已转换好。"""
        # LAB01_TODO B1：把四个参数保存为同名的对象属性。
        raise NotImplementedError("B1：请补全 Book.__init__")

    def restock(self, quantity):
        """将当前库存增加 quantity 册；入口保证 quantity 为正整数。"""
        # LAB01_TODO B2a：更新当前对象的库存，不修改其他属性。
        raise NotImplementedError("B2a：请补全 Book.restock")

    def set_price(self, price):
        """修改当前售价；入口已检查 price 为非负有限数。"""
        # LAB01_TODO B2b：修改售价，进货成本保持不变。
        raise NotImplementedError("B2b：请补全 Book.set_price")


class BookReader(CSVReader):
    """书库读取示例已完成；父类负责打开文件和遍历各行。"""

    fields = ("title", "cost", "price", "stock")

    def parse_row(self, row):
        title = row["title"].strip()
        cost = check_money(float(row["cost"]))
        price = check_money(float(row["price"]))
        stock = int(row["stock"])
        if stock < 0:
            raise ValueError("库存不能为负数")
        return Book(title, cost, price, stock)


class SalesReader(CSVReader):
    """销售记录读取器，继承同一 read 流程，只重写一行的转换方式。"""

    fields = ("title", "quantity", "unit_price")

    def parse_row(self, row):
        """row 的值均为字符串；返回含以下三项的字典。

        title：去除两端空白的书名；quantity：整数销量；unit_price：浮点成交单价。
        可参照 BookReader 的转换写法，无需再打开文件或写一遍读取循环。
        """
        # LAB01_TODO B3：把一行文本字段转换成上述销售记录。
        raise NotImplementedError("B3：请补全 SalesReader.parse_row")

    def validate_record(self, record):
        """数据检查已提供，无需修改。"""
        if type(record["quantity"]) is not int or record["quantity"] <= 0:
            raise ValueError("销售数量应为正整数")
        check_money(record["unit_price"])


def affordable_books(catalog, budget):
    """返回有库存、且当前售价不超过 budget 的书名列表，保持书库顺序。

    catalog 是“书名 -> Book 对象”的字典；无符合项时返回空列表。
    不修改书库或图书对象。
    """
    # LAB01_TODO B4：遍历书库，按库存和当前售价筛选。
    raise NotImplementedError("B4：请补全 affordable_books")


def prepare_sales(catalog, records):
    """关联书库成本，将销售记录整理为一一对应的四列。

    返回字典：titles 为书名列表；quantities 为整数 NumPy 数组；
    unit_prices、costs 为浮点 NumPy 数组。每条销售记录对应一个位置。
    成交价来自销售记录，成本来自 catalog[书名].cost，均不使用当前售价。
    同名记录不合并、不遗漏；空记录返回四个空的列表/一维数组。
    """
    # LAB01_TODO B5：逐条按书名查找成本，再整理列表和一维数组。
    # 输入保证书名在书库中；不要在这里扣库存或修改销售记录。
    raise NotImplementedError("B5：请补全 prepare_sales")


def calculate_sales(quantities, unit_prices, costs):
    """完成逐条计算和总体汇总，返回结构已提供。

    三个输入都是长度相同的一维 NumPy 数组。
    line_revenue 为逐条销售额，line_profit 为逐条毛利；
    total_revenue、total_profit 为各自总和。空输入的总和为 0。
    """
    # LAB01_TODO B6：计算上述四个变量。
    # NumPy 数组可以逐元素相乘；毛利使用成交价与进货成本的差。
    raise NotImplementedError("B6：请补全 calculate_sales")

    return {
        "line_revenue": line_revenue,
        "line_profit": line_profit,
        "total_revenue": float(total_revenue),
        "total_profit": float(total_profit),
    }


if __name__ == "__main__":
    try:
        raise SystemExit(run_menu(sys.modules[__name__]))
    except NotImplementedError as error:
        print(f"[待完成] {error}。可先运行 check_book_tasks.py 独立检查其他阶段。")
        raise SystemExit(1)
