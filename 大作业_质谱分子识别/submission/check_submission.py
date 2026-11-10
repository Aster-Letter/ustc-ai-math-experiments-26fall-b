"""核对预测格式和当前测试编号；结构解析为可选检查。"""

import argparse
import pandas as pd


def check_submission(predictions, queries, parse_smiles=False):
    """检查每个当前测试分子恰好对应一行、1 到 25 个非空候选。

    Args:
        predictions (pandas.DataFrame): 两列 molecule_id、smiles。
        queries (pandas.DataFrame): 当前测试输入，含 molecule_id。
        parse_smiles (bool): 是否用本机 RDKit 检查结构语法。

    Returns:
        dict: 通过检查的行数和检查范围；不代表获得了评分。
    """
    assert list(predictions.columns) == ["molecule_id", "smiles"], "列名或列顺序错误。"
    ids = predictions.molecule_id.astype(str)
    assert predictions.molecule_id.notna().all() and ids.str.strip().ne("").all()
    assert ids.is_unique, "一个分子出现多行。"
    assert set(ids) == set(queries.molecule_id.astype(str)), "必须覆盖当前测试编号，不能硬编码400行。"
    assert predictions.smiles.notna().all(), "预测中有空值。"
    for value in predictions.smiles:
        candidates = str(value).split(";")
        assert 1 <= len(candidates) <= 25 and all(s.strip() for s in candidates), "候选为空或数量不符。"
        if parse_smiles:
            from rdkit import Chem
            assert all(Chem.MolFromSmiles(s) is not None for s in candidates), "存在无法解析的SMILES。"
    return dict(rows=len(predictions), format_ok=True, smiles_parsed=parse_smiles,
                note="Does not verify model completion, candidate correctness, or Kaggle score.")


def main():
    """对指定预测文件执行检查，不上传文件。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--test", required=True)
    parser.add_argument("--parse-smiles", action="store_true")
    args = parser.parse_args()
    predictions = pd.read_csv(args.predictions, dtype=str, keep_default_na=False)
    print(check_submission(predictions, pd.read_parquet(args.test, columns=["molecule_id"]), args.parse_smiles))


if __name__ == "__main__":
    main()
