"""从小参考谱库构建已知结构检索验证，或结构不重叠验证。"""

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd


def spectrum_signature(row):
    """用当前基线读取的原始谱字段识别完全重复项。

    Args:
        row (pandas.Series): 一行谱数据。

    Returns:
        str: 排序后的峰数组及前体信息摘要，不使用结构标签。
    """
    peaks = sorted(zip(row.ms2_mzs, row.ms2_normalized_intensities))
    text = json.dumps([peaks, float(row.precursor_mz), str(row.adduct), str(row.ionization_mode)])
    return hashlib.sha256(text.encode()).hexdigest()


def build_validation(frame, out, mode="known", molecules=200, seed=0):
    """按结构分开选参数组和最后检查组，移除参考库里的查询谱。

    Args:
        frame (pandas.DataFrame): 含标签的小参考谱库。
        out (str or Path): 保存划分的目录。
        mode (str): known 保留同结构其他谱；structure 移除查询结构全部谱。
        molecules (int): 最多选取的查询结构数。
        seed (int): 抽样种子。

    Returns:
        dict: 划分规模和方式，原始行号保存在查询与参考表中。
    """
    frame = frame.dropna(subset=["inchikey14", "normalized_smiles"]).copy()
    frame["signature"] = frame.apply(spectrum_signature, axis=1)
    unique_counts = frame.groupby("inchikey14").signature.nunique()
    eligible = sorted(unique_counts[unique_counts >= (2 if mode == "known" else 1)].index)
    rng = np.random.default_rng(seed)
    chosen = rng.permutation(eligible)[:molecules]
    assert len(chosen) >= 2, "可用结构不足；扩大训练样本，至少需要两个查询结构。"
    query_rows = []
    for key in chosen:
        group = frame[frame.inchikey14 == key].drop_duplicates("signature")
        query_rows.append(group.iloc[int(rng.integers(len(group)))])
    query = pd.DataFrame(query_rows).reset_index(drop=True)
    reference = frame[~frame.signature.isin(query.signature)].copy()
    if mode == "structure":
        reference = reference[~reference.inchikey14.isin(chosen)]
    else:
        query = query[query.inchikey14.isin(reference.inchikey14)].reset_index(drop=True)
    assert len(query) >= 2 and len(reference) > 0, "划分后样本不足，请扩大抽样规模。"
    query["molecule_id"] = [f"validation_{i:05d}" for i in range(len(query))]
    query["spectrum_id"] = query.molecule_id + "_s0"
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    reference.drop(columns="signature").to_parquet(out / "reference.parquet", index=False)
    boundary = max(1, len(query) // 2)
    for name, part in [("tune", query.iloc[:boundary]), ("holdout", query.iloc[boundary:])]:
        labels = part[["molecule_id", "normalized_smiles", "inchikey14"]].rename(columns={"normalized_smiles": "smiles"})
        labels.to_csv(out / f"labels_{name}.csv", index=False)
        part.drop(columns=["signature", "normalized_smiles", "inchikey14"]).to_parquet(out / f"queries_{name}.parquet", index=False)
    record = dict(mode=mode, seed=seed, input_spectra=len(frame), reference_spectra=len(reference),
                  query_structures=len(query), tune_structures=boundary,
                  holdout_structures=len(query)-boundary, duplicate_policy="exact input fields; sorted peaks",
                  note="Raw inchikey14 split; tautomer-equivalent groups require additional audit.")
    (out / "split.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(record))
    return record


def main():
    """读取命令行指定的样本与划分设置。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--mode", choices=["known", "structure"], default="known")
    parser.add_argument("--molecules", type=int, default=200)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    build_validation(pd.read_parquet(args.reference), args.out, args.mode, args.molecules, args.seed)


if __name__ == "__main__":
    main()
