"""独立验证：python check_book_tasks.py [--stage B3]。

内置测试数据，不读取或修改学生的 books.csv、sales.csv。
不同阶段独立运行；无需修改或提交本文件。
"""

import argparse
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import numpy as np


def fixture():
    # 固定对象样例：绕开尚未实现的 Book.__init__，供其他阶段独立检查。
    return {
        "星空旅行": SimpleNamespace(title="星空旅行", cost=20.0, price=32.0, stock=5),
        "山间日记": SimpleNamespace(title="山间日记", cost=15.0, price=25.0, stock=0),
        "海边故事": SimpleNamespace(title="海边故事", cost=10.0, price=18.0, stock=3),
    }


def sales_fixture():
    return [
        {"title": "星空旅行", "quantity": 2, "unit_price": 30.0},
        {"title": "海边故事", "quantity": 3, "unit_price": 18.0},
        {"title": "星空旅行", "quantity": 1, "unit_price": 32.0},
        {"title": "山间日记", "quantity": 2, "unit_price": 25.0},
    ]


def equal(actual, expected):
    assert actual == expected, f"预期 {expected!r}；实际 {actual!r}"


def array_equal(actual, expected):
    assert isinstance(actual, np.ndarray) and actual.ndim == 1, "应返回一维 NumPy 数组"
    np.testing.assert_allclose(actual, expected, rtol=1e-9, atol=1e-9)


def build_cases(tasks):
    cases = []

    def case(stage, name):
        def register(function):
            cases.append((stage, name, function))
            return function
        return register

    @case("B1", "属性初始化与对象独立")
    def constructor():
        a, b = tasks.Book("甲", 6.5, 10.0, 2), tasks.Book("乙", 3.0, 5.0, 0)
        equal((a.title, a.cost, a.price, a.stock), ("甲", 6.5, 10.0, 2))
        a.stock += 1
        equal((b.title, b.cost, b.price, b.stock), ("乙", 3.0, 5.0, 0))

    @case("B2", "补货累加且不改其他属性")
    def restock():
        book = fixture()["星空旅行"]
        tasks.Book.restock(book, 2)
        tasks.Book.restock(book, 1)
        equal(vars(book), {"title": "星空旅行", "cost": 20.0, "price": 32.0, "stock": 8})

    @case("B2", "改价不改成本与库存")
    def repricing():
        book = fixture()["星空旅行"]
        tasks.Book.set_price(book, 17.5)
        equal(vars(book), {"title": "星空旅行", "cost": 20.0, "price": 17.5, "stock": 5})
        tasks.Book.set_price(book, 0.0)
        equal(book.price, 0.0)

    @case("B3", "字符串字段转换且保留输入")
    def parse_row():
        row = {"title": " 星空旅行 ", "quantity": "2", "unit_price": "29.5"}
        before = row.copy()
        record = tasks.SalesReader().parse_row(row)
        equal(record, {"title": "星空旅行", "quantity": 2, "unit_price": 29.5})
        assert type(record["quantity"]) is int and type(record["unit_price"]) is float
        equal(row, before)

    @case("B3", "继承 read 处理多行和带逗号书名")
    def read_rows():
        with TemporaryDirectory() as directory:
            path = Path(directory) / "fixed-sales.csv"
            path.write_text('title,quantity,unit_price\n"科学,入门",2,12.5\n海边故事,1,18\n', encoding="utf-8-sig")
            equal(tasks.SalesReader().read(path), [
                {"title": "科学,入门", "quantity": 2, "unit_price": 12.5},
                {"title": "海边故事", "quantity": 1, "unit_price": 18.0},
            ])

    for budget, expected in [(30, ["海边故事"]), (18, ["海边故事"]),
                             (40, ["星空旅行", "海边故事"]), (10, [])]:
        @case("B4", f"预算 {budget}、库存与原顺序")
        def query(budget=budget, expected=expected):
            catalog = fixture()
            before = deepcopy(catalog)
            equal(tasks.affordable_books(catalog, budget), expected)
            equal(catalog, before)

    @case("B4", "空书库")
    def empty_catalog():
        equal(tasks.affordable_books({}, 100), [])

    @case("B5", "关联成本、重复记录与历史成交价")
    def prepare():
        catalog, records = fixture(), sales_fixture()
        catalog["星空旅行"].price = 99.0
        before = deepcopy((catalog, records))
        data = tasks.prepare_sales(catalog, records)
        equal(data["titles"], [r["title"] for r in records])
        array_equal(data["quantities"], [2, 3, 1, 2])
        assert np.issubdtype(data["quantities"].dtype, np.integer), "销量数组应为整数类型"
        array_equal(data["unit_prices"], [30, 18, 32, 25])
        array_equal(data["costs"], [20, 10, 20, 15])
        equal((catalog, records), before)

    @case("B5", "新书目，不能固定写入默认成本")
    def different_catalog():
        catalog = {"新书": SimpleNamespace(title="新书", cost=7.25, price=12.0, stock=0)}
        data = tasks.prepare_sales(catalog, [{"title": "新书", "quantity": 4, "unit_price": 10.5}])
        equal(data["titles"], ["新书"])
        array_equal(data["quantities"], [4])
        array_equal(data["unit_prices"], [10.5])
        array_equal(data["costs"], [7.25])

    @case("B5", "空销售记录")
    def empty_sales():
        data = tasks.prepare_sales(fixture(), [])
        equal(data["titles"], [])
        for key in ("quantities", "unit_prices", "costs"):
            array_equal(data[key], [])

    for quantities, prices, costs, revenue, profit in [
        ([2, 3, 1, 2], [30, 18, 32, 25], [20, 10, 20, 15], [60, 54, 32, 50], [20, 24, 12, 20]),
        ([3], [5.5], [7], [16.5], [-4.5]),
        ([], [], [], [], []),
    ]:
        @case("B6", f"数组计算与汇总：{len(quantities)} 条记录")
        def calculate(q=quantities, p=prices, c=costs, r=revenue, g=profit):
            inputs = (np.array(q, dtype=int), np.array(p, dtype=float), np.array(c, dtype=float))
            before = [a.copy() for a in inputs]
            result = tasks.calculate_sales(*inputs)
            array_equal(result["line_revenue"], r)
            array_equal(result["line_profit"], g)
            np.testing.assert_allclose(result["total_revenue"], sum(r), atol=1e-9)
            np.testing.assert_allclose(result["total_profit"], sum(g), atol=1e-9)
            for actual, original in zip(inputs, before):
                np.testing.assert_array_equal(actual, original)
    return cases


def run_checks(tasks, stage=None):
    cases = [case for case in build_cases(tasks) if stage is None or case[0] == stage]
    passed = 0
    for stage_name, name, function in cases:
        try:
            function()
        except NotImplementedError as error:
            print(f"[待完成] {stage_name} {name}：{error}")
        except Exception as error:
            print(f"[未通过] {stage_name} {name}：{type(error).__name__}: {error}")
        else:
            passed += 1
            print(f"[通过] {stage_name} {name}")
    print(f"\n通过 {passed}/{len(cases)} 项。公开自查不等同于全部评分规则。")
    return 0 if passed == len(cases) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=[f"B{i}" for i in range(1, 7)])
    args = parser.parse_args()
    try:
        import book_tasks
    except Exception as error:
        print(f"[无法加载] {type(error).__name__}: {error}")
        return 1
    return run_checks(book_tasks, args.stage)


if __name__ == "__main__":
    raise SystemExit(main())
