"""课堂本地指标；可选结构规范化，均不冒充官方评分实现。"""

import argparse
import hashlib
from functools import lru_cache
import json
from pathlib import Path
import pandas as pd


@lru_cache(maxsize=100000)
def match_key(smiles, mode="string"):
    """把结构字符串转换为本次评价所用的匹配键。

    Args:
        smiles (str): 单个结构的 SMILES。
        mode (str): string 原文相等；tautomer 使用本机 RDKit 的互变异构体规范化。

    Returns:
        str or None: 匹配键；无法解析的结构返回 None。
    """
    if mode == "string":
        return smiles.strip() or None
    from rdkit import Chem
    from rdkit.Chem.MolStandardize import rdMolStandardize
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        return None
    molecule = rdMolStandardize.TautomerEnumerator().Canonicalize(molecule)
    return Chem.MolToInchiKey(molecule).split("-")[0]


def evaluate(predictions, labels, mode="string"):
    """按分子计算首个正确候选的倒数排名。

    Args:
        predictions (pandas.DataFrame): molecule_id 与分号分隔的 smiles。
        labels (pandas.DataFrame): 每分子的单个正确 smiles。
        mode (str): 匹配方式。

    Returns:
        pandas.DataFrame: 每个分子的倒数排名、命中与排名。
    """
    assert predictions.molecule_id.is_unique and labels.molecule_id.is_unique
    assert set(predictions.molecule_id) == set(labels.molecule_id), "预测编号与标签集合不一致。"
    values = predictions.set_index("molecule_id").smiles
    rows = []
    for row in labels.itertuples():
        truth = match_key(row.smiles, mode)
        assert truth is not None, "标签无法解析。"
        rank = 0
        for position, candidate in enumerate(str(values[row.molecule_id]).split(";")[:25], 1):
            if match_key(candidate, mode) == truth:
                rank = position
                break
        rows.append(dict(molecule_id=row.molecule_id, rank=rank,
                         reciprocal_rank=1/rank if rank else 0.0,
                         top1=int(rank == 1), top5=int(0 < rank <= 5), top25=int(rank > 0)))
    return pd.DataFrame(rows)


def main():
    """保存每分子结果和带评价口径的汇总。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--labels", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--match", choices=["string", "tautomer"], default="string")
    parser.add_argument("--reference", help="可选：估算整个参考库的结构覆盖上限，不是质量窗召回率")
    args = parser.parse_args()
    pred = pd.read_csv(args.predictions, dtype=str, keep_default_na=False)
    labels = pd.read_csv(args.labels, dtype=str, keep_default_na=False)
    rows = evaluate(pred, labels, args.match)
    summary = dict(molecules=len(rows), mrr25=float(rows.reciprocal_rank.mean()),
                   top1=float(rows.top1.mean()), top5=float(rows.top5.mean()), top25=float(rows.top25.mean()),
                   matching=args.match, metric_scope="classroom approximation, not official Kaggle scoring",
                   labels_file=str(Path(args.labels).resolve()),
                   labels_sha256=hashlib.sha256(Path(args.labels).read_bytes()).hexdigest())
    if args.reference:
        reference = pd.read_parquet(args.reference, columns=["normalized_smiles"])
        keys = {match_key(s, args.match) for s in reference.normalized_smiles.dropna().unique()}
        summary["reference_structure_coverage"] = sum(match_key(s, args.match) in keys for s in labels.smiles) / len(labels)
    if args.match == "tautomer":
        from rdkit import rdBase
        summary["rdkit_version"] = rdBase.rdkitVersion
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows.to_csv(out / "per_molecule.csv", index=False)
    (out / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
