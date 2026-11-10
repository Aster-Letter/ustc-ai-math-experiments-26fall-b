"""课程提交入口：加载小组附件，读取当前官方测试输入，调用共享预测函数。"""

import argparse
import json
from pathlib import Path
import sys

COMPETITION = "enveda-CASMI26-molecule-id-mass-spectra"


def main():
    """支持本地演练；异常直接停止，不生成备用答案。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", help="本地演练的附件目录；Kaggle自动定位")
    parser.add_argument("--test", help="本地演练的同一批测试谱；Kaggle使用官方挂载")
    parser.add_argument("--out", default="/kaggle/working")
    args = parser.parse_args()
    if args.assets:
        assets = Path(args.assets)
    else:
        configs = list(Path("/kaggle/input").rglob("course_config.json"))
        assert len(configs) == 1, "应只挂载一份本课程方法附件。"
        assets = configs[0].parent
    if args.test:
        test = Path(args.test)
    else:
        choices = [Path("/kaggle/input") / COMPETITION / "test.parquet",
                   Path("/kaggle/input/competitions") / COMPETITION / "test.parquet"]
        matches = [p for p in choices if p.is_file()]
        assert len(matches) == 1, "核对官方竞赛输入的挂载路径，不要用私人测试副本代替。"
        test = matches[0]
    sys.path.insert(0, str(assets.resolve()))
    from algorithms.baseline.predict import run_prediction
    from submission.check_submission import check_submission
    from submission.check_environment import check_environment
    import pandas as pd
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "submission.csv").exists(), "已有提交文件，请选择新的演练输出目录。"
    environment = check_environment()
    (out / "environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
    config = json.loads((assets / "course_config.json").read_text())
    print("INPUT:", test, "ASSETS:", assets, "PARAMETERS:", config["parameters"], flush=True)
    predictions = run_prediction(assets / config["reference"], test, out, **config["parameters"])
    print(check_submission(predictions, pd.read_parquet(test, columns=["molecule_id"])))
    predictions.to_csv(out / "submission.csv", index=False)
    print("SUBMISSION_WRITTEN rows=", len(predictions), flush=True)


if __name__ == "__main__":
    main()
