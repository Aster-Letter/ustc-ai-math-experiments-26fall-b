"""任务二：鸢尾花数据观察与分类。

搜索 LAB01_TODO，完成特征选择、训练调用和预测调用。
项目说明见 本目录的 README.md；数据、绘图和评价已提供。
"""

import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix


def select_feature_columns():
    """选择散点图的横纵轴；返回部分已提供。

    列 0–3 分别是花萼长、花萼宽、花瓣长、花瓣宽，单位为 cm。
    """
    # LAB01_TODO I1：把两个 None 改为 0–3 中不同的列编号。
    x_column = None
    y_column = None

    # 下方检查和返回已提供，无需修改。
    if x_column is None or y_column is None:
        raise NotImplementedError("I1：请选择横纵轴的特征列")
    if (type(x_column) is not int or type(y_column) is not int
            or x_column not in range(4) or y_column not in range(4) or x_column == y_column):
        raise ValueError("I1：请选择 0–3 中两个不同的整数列编号")
    return x_column, y_column


def run_classification(X_train, y_train, X_test):
    """在同一流程中训练并预测；模型创建和最终返回已提供。

    X_train：训练花的四项测量值；y_train：对应的真实品种编号。
    X_test：待预测花的四项测量值。真实测试标签不传入本函数。
    """
    model = DecisionTreeClassifier(max_depth=3, random_state=42)

    # LAB01_TODO I2：让 model 从训练特征及对应的真实类别中学习。
    # 接口提示：模型对象.fit(特征, 标签)。结合上方参数说明选择输入。
    raise NotImplementedError("I2：请补全训练调用")

    # LAB01_TODO I3：使用同一个 model 预测测试特征，结果保存为 predictions。
    # 接口提示：模型对象.predict(特征)，返回每个样本的预测类别。
    raise NotImplementedError("I3：请补全预测调用")

    return model, predictions


def draw_scatter(features, labels, x_column, y_column, feature_names, class_names):
    """绘制训练数据，返回 Figure；此函数已提供，无需补全。

    features 每行是一朵花、四列为原始测量值；labels 为对应的类别编号。
    x_column、y_column 是横纵轴列编号，范围 0–3。
    feature_names 与 class_names 用于坐标和图例。
    """
    figure, axes = plt.subplots(figsize=(6, 4))
    for class_id, (color, marker) in enumerate(
        zip(["#2878B5", "#C77C25", "#2A9D8F"], ["o", "s", "^"])
    ):
        selected = labels == class_id
        axes.scatter(
            features[selected, x_column], features[selected, y_column],
            color=color, marker=marker, label=class_names[class_id], alpha=0.75,
        )
    axes.set_xlabel(feature_names[x_column])
    axes.set_ylabel(feature_names[y_column])
    axes.set_title(f"Iris training set ({len(labels)} samples)")
    axes.legend()
    axes.grid(alpha=0.2)
    figure.tight_layout()
    return figure


def main():
    """提供固定数据和结果显示，串起三段学生实现。"""
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42, stratify=iris.target,
    )
    print("训练集：", X_train.shape, "测试集：", X_test.shape)
    print("特征名称：", iris.feature_names)
    print("类别顺序：", iris.target_names)

    # 每补完一段便可运行：已经生成的图仍会显示，下一段会提示待完成。
    try:
        x_column, y_column = select_feature_columns()
        draw_scatter(X_train, y_train, x_column, y_column, iris.feature_names, iris.target_names)
        model, predictions = run_classification(X_train, y_train, X_test)
    except NotImplementedError as error:
        print(f"[待完成] {error}")
        plt.show()
        return 1

    # 评价已提供：将预测结果与真实品种对照，不再训练模型。
    accuracy = accuracy_score(y_test, predictions)
    matrix = confusion_matrix(y_test, predictions, labels=[0, 1, 2])
    print("已训练模型的特征数：", model.n_features_in_)
    print("预测数量：", len(predictions))
    print("前 5 个测试样本（真实品种 -> 预测品种）：")
    for actual, predicted in zip(y_test[:5], predictions[:5]):
        print(iris.target_names[actual], "->", iris.target_names[predicted])
    print("测试准确率：", accuracy)
    print("混淆矩阵（行：真实类别；列：预测类别）：")
    print(matrix)
    # 结果用于观察与分析，不设置测试准确率达标线。
    # 可用图窗的保存按钮保留散点图；默认不写入或覆盖文件。
    plt.show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
