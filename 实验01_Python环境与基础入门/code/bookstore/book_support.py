"""教师提供的 CSV、菜单、保存与显示工具，无需补全。"""

import argparse
import csv
import math
from pathlib import Path

import numpy as np


def check_money(value):
    if not math.isfinite(value) or value < 0:
        raise ValueError("金额应为有限的非负数")
    return value


class CSVReader:
    """公共流程：读取一行后，调用当前子类的 parse_row 解释数据。"""

    fields = ()

    def read(self, path):
        records = []
        with Path(path).open(encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames or []
            if len(headers) != len(self.fields) or set(headers) != set(self.fields):
                raise ValueError(f"{path}：表头应为 {','.join(self.fields)}")
            for row in reader:
                try:
                    if None in row or any(row[name] is None or not row[name].strip() for name in self.fields):
                        raise ValueError("字段缺失、空白或列数不匹配")
                    record = self.parse_row(row)
                    self.validate_record(record)
                    records.append(record)
                except (ValueError, TypeError, KeyError) as error:
                    raise ValueError(f"{path} 第 {reader.line_num} 行：{error}") from error
        return records

    def parse_row(self, row):
        raise NotImplementedError("请由子类实现 parse_row")

    def validate_record(self, record):
        """子类按各自数据规则检查记录；公共流程不重复。"""


def load_catalog(path, reader):
    catalog = {}
    for book in reader.read(path):
        if book.title in catalog:
            raise ValueError(f"{path}：书名重复：{book.title}")
        catalog[book.title] = book
    return catalog


def save_catalog(catalog, path):
    """保存当前对象属性；调用方负责确认覆盖。"""
    with Path(path).open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "cost", "price", "stock"])
        writer.writeheader()
        for book in catalog.values():
            writer.writerow({"title": book.title, "cost": book.cost,
                             "price": book.price, "stock": book.stock})


def show_catalog(catalog, output=print):
    output("书名 | 成本 | 售价 | 库存")
    for book in catalog.values():
        output(f"{book.title} | {book.cost:.2f} | {book.price:.2f} | {book.stock}")
    quantity = sum(book.stock for book in catalog.values())
    cost = sum(book.cost * book.stock for book in catalog.values())
    value = sum(book.price * book.stock for book in catalog.values())
    output(f"库存 {quantity} 册；库存成本 {cost:.2f} 元；按当前售价计 {value:.2f} 元")


def show_sales(data, result, output=print):
    """按书名展示已有逐条计算结果；分组显示代码已提供。"""
    titles = np.asarray(data["titles"])
    output("书名 | 销量 | 销售额 | 毛利")
    for title in dict.fromkeys(data["titles"]):
        selected = titles == title
        quantity = int(np.sum(data["quantities"][selected]))
        revenue = float(np.sum(result["line_revenue"][selected]))
        profit = float(np.sum(result["line_profit"][selected]))
        output(f"{title} | {quantity} | {revenue:.2f} | {profit:.2f}")
    quantity = int(np.sum(data["quantities"]))
    output(f"合计 {quantity} 册；销售额 {result['total_revenue']:.2f} 元；毛利 {result['total_profit']:.2f} 元")


def run_menu(api, argv=None, input_fn=input, output=print):
    """提供交互入口；业务实现通过 api 调用学生文件中的类和函数。"""
    directory = Path(api.__file__).resolve().parent
    parser = argparse.ArgumentParser(description="模拟的微型书店数据管理与统计程序")
    parser.add_argument("--books", type=Path, default=directory / "books.csv")
    parser.add_argument("--sales", type=Path, default=directory / "sales.csv")
    parser.add_argument("--output", type=Path, default=directory / "books_updated.csv")
    args = parser.parse_args(argv)
    # 初始导入失败直接抛错，不能用默认数据替换学生实际文件。
    catalog = load_catalog(args.books, api.BookReader())
    dirty = False
    output(f"已读取 {len(catalog)} 种图书：{args.books}")

    def save():
        if args.output.exists():
            answer = input_fn(f"{args.output} 已存在，覆盖？[y/N] ").strip().lower()
            if answer != "y":
                output("取消保存。")
                return False
        save_catalog(catalog, args.output)
        output(f"已保存：{args.output}")
        return True

    while True:
        try:
            output("\n1 书库与库存统计  2 按书名查询  3 预算内有货图书")
            output("4 补充库存  5 修改售价  6 保存书库  7 销售统计  0 退出")
            choice = input_fn("选择：").strip()
            if choice == "0":
                if dirty:
                    answer = input_fn("有未保存修改：s 保存并退出 / d 放弃并退出 / 其他键继续：").strip().lower()
                    if answer == "s":
                        if not save():
                            continue
                    elif answer != "d":
                        continue
                return 0
            if choice == "1":
                show_catalog(catalog, output)
            elif choice in ("2", "4", "5"):
                title = input_fn("书名：").strip()
                if title not in catalog:
                    output("未找到这本书。")
                    continue
                book = catalog[title]
                if choice == "2":
                    show_catalog({title: book}, output)
                elif choice == "4":
                    quantity = int(input_fn("补货册数（正整数）："))
                    if quantity <= 0:
                        raise ValueError("补货册数应为正整数")
                    book.restock(quantity)
                    dirty = True
                    output(f"当前库存：{book.stock}；修改尚未保存。")
                else:
                    price = check_money(float(input_fn("新售价：")))
                    book.set_price(price)
                    dirty = True
                    output(f"当前售价：{book.price:.2f}；修改尚未保存。")
            elif choice == "3":
                budget = check_money(float(input_fn("单本预算上限：")))
                titles = api.affordable_books(catalog, budget)
                output("、".join(titles) if titles else "没有符合条件的图书。")
            elif choice == "6":
                if save():
                    dirty = False
            elif choice == "7":
                records = api.SalesReader().read(args.sales)
                for record in records:
                    if record["title"] not in catalog:
                        raise ValueError(f"销售记录中的书名不在书库中：{record['title']}")
                data = api.prepare_sales(catalog, records)
                result = api.calculate_sales(data["quantities"], data["unit_prices"], data["costs"])
                show_sales(data, result, output)
            else:
                output("请输入菜单中的编号。")
        except NotImplementedError as error:
            output(f"[待完成] {error}。可先退出，再运行独立验证程序。")
        except (ValueError, OSError) as error:
            output(f"[输入或文件问题] {error}")
        except (EOFError, KeyboardInterrupt):
            output("\n退出；本次修改未保存。" if dirty else "\n退出。")
            return 1 if dirty else 0
