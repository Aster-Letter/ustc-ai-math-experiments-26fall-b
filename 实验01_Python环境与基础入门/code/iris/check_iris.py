"""鸢尾花公开自查：python check_iris.py。无需修改或提交此文件。

核对训练/预测调用、输入对应与结果一致性，不设置准确率达标线。
检查不打开图窗；散点图仍需运行项目程序查看。
"""

import os

os.environ["MPLBACKEND"] = "Agg"

import numpy as np
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils.validation import check_is_fitted
from unittest.mock import patch


def check_pipeline(tasks, X_train, y_train, X_test, y_test):
    """临时观察真实模型的调用，仍使用真实决策树训练和预测。"""
    events, created = [], []
    originals = [value.copy() for value in (X_train, y_train, X_test)]

    class ObservedTree(DecisionTreeClassifier):
        def fit(self, X, y, **kwargs):
            events.append(("fit", self, np.array(X, copy=True), np.array(y, copy=True)))
            return super().fit(X, y, **kwargs)

        def predict(self, X, **kwargs):
            result = super().predict(X, **kwargs)
            events.append(("predict", self, np.array(X, copy=True), result.copy()))
            return result

    def create_model(*args, **kwargs):
        model = ObservedTree(*args, **kwargs)
        created.append(model)
        return model

    with patch.object(tasks, "DecisionTreeClassifier", create_model):
        model, predictions = tasks.run_classification(X_train, y_train, X_test)

    assert len(created) == 1 and model is created[0], "应返回本流程创建并使用的同一个模型"
    assert model.max_depth == 3 and model.random_state == 42, "请保留给定的模型参数"
    assert [event[0] for event in events] == ["fit", "predict"], "应先训练一次，再预测一次"
    assert all(event[1] is model for event in events), "训练与预测应使用同一个模型对象"
    np.testing.assert_array_equal(events[0][2], originals[0], err_msg="fit 应接收训练特征")
    np.testing.assert_array_equal(events[0][3], originals[1], err_msg="fit 应接收对应训练标签")
    np.testing.assert_array_equal(events[1][2], originals[2], err_msg="predict 应接收测试特征")
    for actual, before in zip((X_train, y_train, X_test), originals):
        np.testing.assert_array_equal(actual, before, err_msg="不要修改传入的数据")
    check_is_fitted(model)
    assert model.n_features_in_ == 4, "模型应使用原始四列特征"
    predictions = np.asarray(predictions)
    assert predictions.shape == (len(X_test),), "每个测试样本应对应一个预测类别"
    assert np.isin(predictions, [0, 1, 2]).all(), "预测类别应为 0、1、2"
    np.testing.assert_array_equal(predictions, events[1][3], err_msg="返回结果应来自 predict 调用")
    matrix = confusion_matrix(y_test, predictions, labels=[0, 1, 2])
    accuracy = accuracy_score(y_test, predictions)
    assert matrix.shape == (3, 3) and matrix.sum() == len(X_test)
    assert np.isclose(np.trace(matrix) / len(X_test), accuracy), "矩阵与准确率应一致"


def run_checks(tasks):
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42, stratify=iris.target,
    )

    def check_columns():
        x, y = tasks.select_feature_columns()
        assert type(x) is int and type(y) is int and 0 <= x < 4 and 0 <= y < 4 and x != y

    indices = [8, 2, 25, 0, 17, 4, 13]

    def varied_inputs():
        # 同时覆盖短于和长于默认测试集的输入，避免固定长度的处理。
        for selection in (indices, indices + list(range(len(X_test)))):
            check_pipeline(tasks, X_train.copy(), y_train.copy(), X_test[selection], y_test[selection])

    cases = [
        ("I1：两个不同的有效特征列", check_columns),
        ("I2/I3：训练与预测调用、30 个测试样本和评价一致性",
         lambda: check_pipeline(tasks, X_train.copy(), y_train.copy(), X_test.copy(), y_test)),
        ("I2/I3：改变测试样本数量与顺序后仍正确连接",
         varied_inputs),
    ]
    passed = 0
    for name, check in cases:
        try:
            check()
        except NotImplementedError as error:
            print(f"[待完成] {name}：{error}")
        except Exception as error:
            print(f"[未通过] {name}：{type(error).__name__}: {error}")
        else:
            passed += 1
            print(f"[通过] {name}")
    print(f"\n通过 {passed}/{len(cases)} 项。接着运行项目程序，查看图与真实/预测类别对照。")
    return 0 if passed == len(cases) else 1


def main():
    try:
        import iris_classification
    except Exception as error:
        print(f"[无法加载] {type(error).__name__}: {error}")
        return 1
    return run_checks(iris_classification)


if __name__ == "__main__":
    raise SystemExit(main())
