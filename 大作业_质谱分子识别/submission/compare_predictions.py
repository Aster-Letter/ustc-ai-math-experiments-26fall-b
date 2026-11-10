"""比较相同输入在本地与提交程序产生的原始候选和顺序。"""

import argparse
import json
import pandas as pd


def main():
    """按分子编号对齐，而非按文件行号比较。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", required=True)
    parser.add_argument("--deployed", required=True)
    args = parser.parse_args()
    a, b = [pd.read_csv(path, dtype=str, keep_default_na=False).set_index("molecule_id") for path in [args.local, args.deployed]]
    assert a.index.is_unique and b.index.is_unique and set(a.index) == set(b.index), "输入分子编号不同。"
    b = b.reindex(a.index)
    ordered = a.smiles.eq(b.smiles)
    same_set = [set(x.split(";")) == set(y.split(";")) for x, y in zip(a.smiles, b.smiles)]
    top1 = a.smiles.str.split(";").str[0].eq(b.smiles.str.split(";").str[0])
    print(json.dumps(dict(molecules=len(a), identical_order=int(ordered.sum()),
                          identical_candidate_set=sum(same_set), identical_top1=int(top1.sum()),
                          note="Raw SMILES text comparison; not chemical equivalence."), indent=2))
    assert ordered.all(), "存在差异，请检查参数、附件版本、预处理和随机性。"


if __name__ == "__main__":
    main()
