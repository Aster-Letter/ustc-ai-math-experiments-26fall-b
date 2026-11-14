"""T1：只查看训练数据，不打开测试集。"""
import argparse
from data import PetDataset, read_manifest
from visuals import save_examples

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--output", default="outputs/data_preview.png")
    args = parser.parse_args()
    splits, fingerprint = read_manifest(args.data_dir)
    dataset = PetDataset(args.data_dir, splits["train"])
    save_examples(None, dataset, "cpu", args.output)
    print("Saved", args.output, "split fingerprint:", fingerprint)
