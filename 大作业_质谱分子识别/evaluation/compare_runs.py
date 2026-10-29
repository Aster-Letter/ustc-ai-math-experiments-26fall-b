"""对相同分子和相同评价口径计算两次实验的配对差值。"""

import argparse
import json
from pathlib import Path
import pandas as pd


def main():
    """读取 evaluate.py 产物，比较 B 减 A 的指标变化。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a", required=True)
    parser.add_argument("--b", required=True)
    args = parser.parse_args()
    a, b = Path(args.a), Path(args.b)
    ma, mb = [json.loads((p / "metrics.json").read_text()) for p in [a, b]]
    assert ma["matching"] == mb["matching"], "匹配方式不同，不能直接比较。"
    assert ma["labels_sha256"] == mb["labels_sha256"], "标签文件不同，先核对验证对象与答案。"
    assert ma.get("rdkit_version") == mb.get("rdkit_version"), "结构工具版本不同。"
    x, y = [pd.read_csv(p / "per_molecule.csv", dtype={"molecule_id": str}).set_index("molecule_id") for p in [a, b]]
    assert x.index.is_unique and y.index.is_unique and set(x.index) == set(y.index)
    difference = y.reindex(x.index).reciprocal_rank - x.reciprocal_rank
    print(json.dumps(dict(molecules=len(x), mrr25_b_minus_a=float(difference.mean()),
                          improved=int((difference > 0).sum()), worsened=int((difference < 0).sum()),
                          unchanged=int((difference == 0).sum())), indent=2))


if __name__ == "__main__":
    main()
