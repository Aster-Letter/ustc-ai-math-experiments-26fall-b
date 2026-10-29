"""查看 Parquet 结构；可均匀抽取小参考谱库用于入门实验。"""

import argparse
import json
from pathlib import Path
import pyarrow.parquet as pq
from algorithms.baseline.preprocess import sample_reference


def main():
    """检查元数据；指定 sample-out 时才保存训练样本。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True)
    parser.add_argument("--sample-out")
    parser.add_argument("--sample-rows", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    reader = pq.ParquetFile(args.file)
    print("rows:", reader.metadata.num_rows)
    print("columns:", reader.schema_arrow.names)
    if args.sample_out:
        frame = sample_reference(args.file, args.sample_rows, args.seed)
        out = Path(args.sample_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(out, index=False)
        record = dict(source=str(Path(args.file)), source_bytes=Path(args.file).stat().st_size,
                      seed=args.seed, method="uniform row sample across full file",
                      requested=args.sample_rows, rows=len(frame), structures=frame.inchikey14.nunique())
        out.with_suffix(".sampling.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        print("saved:", out, "structures:", frame.inchikey14.nunique())


if __name__ == "__main__":
    main()
