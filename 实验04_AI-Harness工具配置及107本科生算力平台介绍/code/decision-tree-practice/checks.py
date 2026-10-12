"""Public self-check examples for the Lab 2 agent tutorial; no grading or submission."""

import argparse
import copy
import importlib.util
import math
from pathlib import Path


def same(actual, expected):
    if actual != expected:
        raise AssertionError(f"expected {expected!r}, got {actual!r}")


def close(actual, expected):
    if not isinstance(actual, (int, float)) or not math.isfinite(actual):
        raise AssertionError(f"expected finite number near {expected}, got {actual!r}")
    if not math.isclose(actual, expected, abs_tol=1e-9, rel_tol=1e-9):
        raise AssertionError(f"expected {expected:.9f}, got {actual!r}")


def load_target(path):
    spec = importlib.util.spec_from_file_location("tutorial_target", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cases(module, stage):
    tree = module.DecisionTree
    result = []

    def add(name, function):
        result.append((name, function))

    add("A1 empty entropy", lambda: close(tree()._entropy([]), 0.0))
    add("A2 pure zero", lambda: close(tree()._entropy([0, 0]), 0.0))
    add("A3 pure one", lambda: close(tree()._entropy([1, 1]), 0.0))
    add("A4 balanced entropy", lambda: close(tree()._entropy([0, 1]), 1.0))
    add("A5 unbalanced entropy", lambda: close(tree()._entropy([0, 0, 0, 1]), 0.8112781244591328))
    if stage == "a":
        return result

    def majority():
        model = tree()
        same(model._majority_label([0, 1]), 0)
        same(model._majority_label([1, 0, 1]), 1)
        same(model._majority_label([0]), 0)

    def gains():
        model = tree()
        close(model._information_gain([["a"], ["b"]], [0, 1], 0), 1.0)
        close(model._information_gain([["a"], ["a"]], [0, 1], 0), 0.0)
        # Branch sizes 2 and 1 distinguish weighting from a plain mean.
        close(model._information_gain([["a"], ["a"], ["b"]], [0, 1, 1], 0), 0.2516291673878229)

    def feature_tie():
        model = tree()
        X = [["a", "a"], ["a", "a"], ["b", "b"]]
        same(model._best_feature(X, [0, 0, 1], [1, 0]), 1)
        same(model._best_feature(X, [0, 0, 1], []), None)

    def leaves():
        model = tree()
        model.fit([["a"], ["b"]], [1, 1])
        same(model.root, {"feature": None, "label": 1, "children": {}})
        model.fit([["a"], ["a"]], [0, 1])
        same(model.root, {"feature": None, "label": 0, "children": {}})
        same(model._build_tree([["a"], ["b"]], [0, 1], []),
             {"feature": None, "label": 0, "children": {}})

    def zero_gain():
        X = [[0, 0], [0, 1], [1, 0], [1, 1]]
        y = [0, 1, 1, 0]
        model = tree()
        close(model._information_gain(X, y, 0), 0.0)
        same(model._best_feature(X, y, [0, 1]), 0)
        model.fit(X, y)
        same(model.predict(X), y)

    def original_columns():
        X = [["constant", "a"], ["constant", "b"], ["constant", "b"]]
        model = tree()
        model.fit(X, [0, 1, 1])
        same(model.root["feature"], 1)
        same(model.predict([["constant", "b"], ["constant", "a"]]), [1, 0])

    def unknown_branch():
        model = tree()
        model.fit([["a"], ["b"], ["b"]], [0, 1, 1])
        same(model._predict_one(["never-seen"]), 1)
        # Index zero is a feature, not a leaf sentinel.
        same(model._predict_one(["a"]), 0)

    def batch_order():
        model = tree()
        model.fit([["a"], ["b"]], [0, 1])
        same(model.predict([]), [])
        same(model.predict([["b"], ["a"], ["a"]]), [1, 0, 0])

    def unchanged_inputs():
        X = [[0, 0], [0, 1], [1, 0], [1, 1]]
        y, features = [0, 1, 1, 0], [0, 1]
        before = copy.deepcopy((X, y, features))
        tree()._build_tree(X, y, features)
        same((X, y, features), before)

    def watermelon_root():
        X, y, names, ids = module.load_watermelon()
        same((len(X), len(y), len(names), len(ids)), (17, 17, 6, 17))
        model = tree()
        same(model._best_feature(X, y, list(range(6))), 3)
        close(model._information_gain(X, y, 3), 0.3805918973682686)
        model.fit(X, y)
        same(model.root["feature"], 3)

    def watermelon_predictions():
        X, y, _, _ = module.load_watermelon()
        model = tree()
        model.fit(X, y)
        same(model.predict(X), y)

    for name, check in [
        ("B1 majority and tie", majority),
        ("B2 weighted information gain", gains),
        ("B3 candidate order", feature_tie),
        ("B4 termination conditions", leaves),
        ("B5 zero-gain XOR", zero_gain),
        ("B6 original column index", original_columns),
        ("B7 unknown branch and index zero", unknown_branch),
        ("B8 empty batch and input order", batch_order),
        ("B9 preserve caller inputs", unchanged_inputs),
        ("B10 watermelon root", watermelon_root),
        ("B11 watermelon training predictions", watermelon_predictions),
    ]:
        add(name, check)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("a", "b"), required=True)
    parser.add_argument("--target", type=Path, default=Path(__file__).with_name("decision_tree.py"))
    args = parser.parse_args()
    try:
        module = load_target(args.target.resolve(strict=True))
        checks = cases(module, args.stage)
    except Exception as error:
        print(f"Cannot load target: {type(error).__name__}: {error}")
        return 2
    passed = 0
    for name, check in checks:
        try:
            check()
        except Exception as error:
            print(f"FAIL {name}: {type(error).__name__}: {error}")
        else:
            passed += 1
            print(f"PASS {name}")
    print(f"Stage {args.stage.upper()}: {passed}/{len(checks)} passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
