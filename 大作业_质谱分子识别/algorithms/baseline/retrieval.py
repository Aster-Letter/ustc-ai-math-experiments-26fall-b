"""用余弦相似度排序参考结构；不从头生成新分子。"""

import numpy as np
import pandas as pd
from algorithms.baseline.preprocess import spectrum_vector, reference_matrix


def predict(reference, queries, bin_width=1.0, power=0.5, ppm=20.0, merge="max"):
    """逐谱检索、按结构去重，再为每个分子合并排名。

    Args:
        reference (pandas.DataFrame): 含结构标签的参考谱。
        queries (pandas.DataFrame): 含 molecule_id 的查询谱；不读取其标签。
        bin_width (float): 分箱宽度。
        power (float): 强度变换指数。
        ppm (float): 相同加合物、离子模式下的前体相对误差阈值。
        merge (str): max 取多谱证据最大值；mean 对全部查询谱取平均。

    Returns:
        tuple: 预测表和运行统计；零候选时放宽检索条件并记录次数。
    """
    reference = reference.dropna(subset=["normalized_smiles", "inchikey14"]).reset_index(drop=True)
    matrix = reference_matrix(reference, bin_width, power)
    masses = reference.precursor_mz.to_numpy(dtype=float)
    keys = reference.inchikey14.astype(str).to_numpy()
    smiles = reference.normalized_smiles.astype(str).to_numpy()
    output = []
    relaxed = 0
    zero_queries = 0
    for molecule_id, group in queries.groupby("molecule_id", sort=False):
        evidence = {}
        structures = {}
        for row in group.itertuples():
            vector = spectrum_vector(row.ms2_mzs, row.ms2_normalized_intensities,
                                     bin_width=bin_width, power=power)
            zero_queries += int(np.linalg.norm(vector) == 0)
            compatible = ((reference.adduct == row.adduct) &
                          (reference.ionization_mode == row.ionization_mode)).to_numpy()
            error = np.abs(masses - row.precursor_mz) / max(abs(row.precursor_mz), 1e-12) * 1e6
            chosen = np.flatnonzero(compatible & (error <= ppm))
            if len(chosen) == 0:
                relaxed += 1
                chosen = np.flatnonzero(compatible)
                if len(chosen) == 0:
                    chosen = np.arange(len(reference))
            scores = matrix[chosen] @ vector
            per_structure = {}
            for index, score in zip(chosen, scores):
                key = keys[index]
                structures[key] = smiles[index]
                per_structure[key] = max(per_structure.get(key, -1.0), float(score))
            for key, score in per_structure.items():
                evidence.setdefault(key, []).append(score)
        merged = {}
        for key, values in evidence.items():
            merged[key] = max(values) if merge == "max" else sum(values) / len(group)
        ranking = sorted(merged, key=lambda key: (-merged[key], key))[:25]
        output.append({"molecule_id": str(molecule_id),
                       "smiles": ";".join(structures[key] for key in ranking)})
    return pd.DataFrame(output), {"query_spectra": len(queries), "molecules": len(output),
                                  "reference_spectra": len(reference),
                                  "relaxed_spectra": relaxed, "zero_query_spectra": zero_queries}
