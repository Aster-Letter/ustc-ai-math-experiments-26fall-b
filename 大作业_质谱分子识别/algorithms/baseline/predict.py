"""本地与 Kaggle 共用的预测入口；命令示例见项目根目录 README。"""

import argparse
import json
import time
from pathlib import Path
import pandas as pd
from algorithms.baseline.retrieval import predict


def run_prediction(reference_path, query_path, out_dir, bin_width=1.0,
                   power=0.5, ppm=20.0, merge="max"):
    """读入已准备的参考库，生成预测并记录参数、规模和耗时。

    Args:
        reference_path (str or Path): 参考谱库 Parquet。
        query_path (str or Path): 查询谱 Parquet。
        out_dir (str or Path): 本次实验输出目录。
        bin_width (float): 分箱宽度。
        power (float): 强度变换指数。
        ppm (float): 前体质量筛选阈值。
        merge (str): 多谱合并方式 max 或 mean。

    Returns:
        pandas.DataFrame: 每分子一行的预测。
    """
    start = time.monotonic()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    reference = pd.read_parquet(reference_path)
    queries = pd.read_parquet(query_path)
    predictions, stats = predict(reference, queries, bin_width, power, ppm, merge)
    assert not predictions.empty and predictions.smiles.str.len().min() > 0
    predictions.to_csv(out / "predictions.csv", index=False)
    config = dict(reference=str(reference_path), queries=str(query_path), bin_width=bin_width,
                  power=power, ppm=ppm, merge=merge, max_mz=1500.0)
    (out / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    stats["elapsed_seconds"] = round(time.monotonic() - start, 3)
    (out / "run_summary.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False))
    return predictions


def main():
    """解析终端参数并运行预测。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--queries", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--bin-width", type=float, default=1.0)
    parser.add_argument("--power", type=float, default=0.5)
    parser.add_argument("--ppm", type=float, default=20.0)
    parser.add_argument("--merge", choices=["max", "mean"], default="max")
    args = parser.parse_args()
    assert args.bin_width > 0 and args.power > 0 and args.ppm >= 0
    run_prediction(args.reference, args.queries, args.out, args.bin_width, args.power, args.ppm, args.merge)


if __name__ == "__main__":
    main()
