"""把本人输入的 Kaggle API 令牌保存到用户目录；不连接网络。"""

from getpass import getpass
from pathlib import Path
import os


def main():
    """在终端隐藏输入令牌，保存前确认是否替换已有令牌文件。"""
    token_file = Path.home() / ".kaggle" / "access_token"
    if token_file.exists():
        answer = input("已有 access_token，是否覆盖？输入 yes 确认：")
        if answer.strip().lower() != "yes":
            print("已保留原文件。")
            return

    token = getpass("粘贴本人 Kaggle API Token（输入不显示），然后回车：").strip()
    if not token:
        print("未输入令牌，没有修改文件。")
        return

    token_file.parent.mkdir(parents=True, exist_ok=True)
    # 新文件创建时即限制权限，已有文件写入前也收紧权限。
    descriptor = os.open(token_file, os.O_WRONLY | os.O_CREAT, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        if os.name != "nt":
            os.fchmod(stream.fileno(), 0o600)
        stream.truncate(0)
        stream.write(token + "\n")

    print("已保存到：", token_file)
    print("尚未连接 Kaggle，请继续运行指南中的只读检查。")


if __name__ == "__main__":
    main()
