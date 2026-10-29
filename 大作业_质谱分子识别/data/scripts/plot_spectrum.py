"""绘制小文件中指定行的质谱，使用前请先生成抽样文件。"""

import argparse
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    """输出适合放入报告的静态谱图。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True)
    parser.add_argument("--row", type=int, default=0)
    parser.add_argument("--out", default="outputs/data_review/spectrum.png")
    args = parser.parse_args()
    row = pd.read_parquet(args.file).iloc[args.row]
    figure, ax = plt.subplots(figsize=(8, 3.4))
    ax.vlines(row.ms2_mzs, 0, row.ms2_normalized_intensities, color="#2878B5", linewidth=1)
    ax.set(xlabel="Mass-to-charge ratio (m/z)", ylabel="Relative intensity",
           title=f"Spectrum row {args.row}; precursor m/z = {row.precursor_mz:.4f}")
    ax.spines[["top", "right"]].set_visible(False)
    figure.tight_layout()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.out, dpi=180)
    plt.close(figure)
    print("saved:", args.out)


if __name__ == "__main__":
    main()
