"""已提供：检查生成原文的句长与训练文本重合；不修正或补齐生成诗句。"""
import argparse
import json
from pathlib import Path
import re


def inspect(text, training):
    """检查第一段生成文本，并与训练诗句逐句比较。

    Args:
        text (str): 采样文件原文，包含提示词。
        training (list): 训练诗的来源记录。

    Returns:
        dict: 原文、形状及逐句重合统计；不评价意境、平仄或押韵。
    """
    first = text.strip().split("\n\n")[0]
    clauses = [part.strip() for part in re.split("[，。！？\n]+", first) if part.strip()]
    known = set()
    for poem in training:
        for clause in re.split("[，。！？\n]+", poem["text"]):
            if clause.strip():
                known.add(clause.strip())
    matches = [clause for clause in clauses if clause in known]
    normalized = "".join(clauses)
    exact = any(normalized == re.sub("[，。！？\n]+", "", poem["text"]) for poem in training)
    return {"first_stanza_raw": first, "clause_lengths": [len(c) for c in clauses],
            "four_five_character_clauses": len(clauses) == 4 and all(len(c) == 5 for c in clauses),
            "training_line_matches": matches, "whole_training_poem_match": exact,
            "note": "包含提示词；只检出完全一致的句或整首，不能排除近似记忆"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sample")
    parser.add_argument("--data", default="data")
    args = parser.parse_args()
    training = json.loads((Path(args.data) / "train_poems.json").read_text(encoding="utf-8"))
    result = inspect(Path(args.sample).read_text(encoding="utf-8"), training)
    print(json.dumps(result, ensure_ascii=False, indent=2))
