"""读取一小份参考谱库，并把变长质谱变成定长向量。"""

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

COLUMNS = ["ms2_mzs", "ms2_normalized_intensities", "precursor_mz",
           "adduct", "ionization_mode", "normalized_smiles", "inchikey14"]


def sample_reference(path, max_rows=5000, seed=0):
    """在整个文件的行号中均匀抽样，分批读取，保存原始行号。

    Args:
        path (str or Path): 官方训练 Parquet 文件。
        max_rows (int): 最多保留的谱数；不是文件开头的行数。
        seed (int): 随机种子。

    Returns:
        pandas.DataFrame: 带 source_row 原始行号的参考谱。
    """
    reader = pq.ParquetFile(path)
    count = reader.metadata.num_rows
    rng = np.random.default_rng(seed)
    selected = np.sort(rng.choice(count, min(max_rows, count), replace=False))
    parts = []
    offset = 0
    for batch in reader.iter_batches(batch_size=4096, columns=COLUMNS):
        rows = selected[(selected >= offset) & (selected < offset + len(batch))]
        if len(rows):
            part = batch.take(rows - offset).to_pandas()
            part["source_row"] = rows
            parts.append(part)
        offset += len(batch)
    return pd.concat(parts, ignore_index=True)


def spectrum_vector(mzs, intensities, bin_width=1.0, max_mz=1500.0, power=0.5):
    """合并同一质荷比区间的峰，再归一化为单位长度。

    Args:
        mzs (array): 峰的质荷比。
        intensities (array): 与峰位置一一对应的非负强度。
        bin_width (float): 每个区间的宽度。
        max_mz (float): 保留 [0, max_mz) 内的峰。
        power (float): 强度变换指数；0.5 为平方根，1 为不变。

    Returns:
        numpy.ndarray: 定长向量；没有有效峰时为零向量。
    """
    vector = np.zeros(int(np.ceil(max_mz / bin_width)), dtype=np.float32)
    for mz, intensity in zip(mzs, intensities):
        if np.isfinite(mz) and np.isfinite(intensity) and 0 <= mz < max_mz and intensity > 0:
            vector[int(mz / bin_width)] += intensity ** power
    length = np.linalg.norm(vector)
    if length > 0:
        vector /= length
    return vector


def reference_matrix(reference, bin_width=1.0, power=0.5):
    """逐谱构建按行排列的参考矩阵。

    Args:
        reference (pandas.DataFrame): 参考谱表。
        bin_width (float): 分箱宽度。
        power (float): 强度变换指数。

    Returns:
        numpy.ndarray: 行为谱、列为分箱的矩阵。
    """
    vectors = []
    for row in reference.itertuples():
        vectors.append(spectrum_vector(row.ms2_mzs, row.ms2_normalized_intensities,
                                       bin_width=bin_width, power=power))
    return np.stack(vectors)
