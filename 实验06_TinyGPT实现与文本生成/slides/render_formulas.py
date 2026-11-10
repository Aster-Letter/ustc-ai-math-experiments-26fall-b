"""用 Tectonic 和 Poppler 渲染整份课件的 LaTeX 公式。"""

import json
import hashlib
from pathlib import Path
import re
import subprocess
import tempfile

from PIL import Image


SLIDES = Path(__file__).resolve().parent
ASSETS = SLIDES / "assets" / "formulas"
DPI = 384
TEMPLATE = r"""\documentclass[border=3pt]{standalone}
\usepackage{fontspec,xeCJK,amsmath,xcolor,unicode-math}
\setmathfont{STIX Two Math}
\setCJKmainfont{Noto Sans CJK SC}
\definecolor{CourseBlue}{HTML}{216C9C}
\begin{document}
\color{CourseBlue}\fontsize{20}{25}\selectfont
\(\displaystyle FORMULA\)
\end{document}
"""


def main():
    """把每条公式渲染为透明 PNG，并保存供课件构建读取的尺寸。"""
    formulas = []
    for source_path in sorted((SLIDES / "latex").glob("*-formulas.tex")):
        source = source_path.read_text()
        for name, formula in re.findall(r"% formula: (\w+)\n([^\n]+)", source):
            formulas.append((name, formula, source_path.name))
    ASSETS.mkdir(parents=True, exist_ok=True)
    scratch = SLIDES.parent / "tmp"
    scratch.mkdir(exist_ok=True)
    previous = json.loads((ASSETS / "manifest.json").read_text()) if (ASSETS / "manifest.json").exists() else {}
    manifest = {}
    with tempfile.TemporaryDirectory(prefix="latex-course-", dir=scratch) as work:
        work = Path(work)
        for name, formula, source_name in formulas:
            document = TEMPLATE.replace("FORMULA", formula)
            digest = hashlib.sha256((document + str(DPI)).encode()).hexdigest()
            if previous.get(name, {}).get("sha256") == digest and (ASSETS / (name + ".png")).exists():
                manifest[name] = previous[name]
                continue
            tex = work / (name + ".tex")
            tex.write_text(document)
            result = subprocess.run(["tectonic", "--keep-logs", str(tex)], capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(name + "\n" + result.stdout + result.stderr)
            log = tex.with_suffix(".log").read_text()
            if any(issue in log for issue in ["Missing character", "Overfull", "! LaTeX Error"]):
                raise RuntimeError("请检查公式编译日志：" + str(tex.with_suffix(".log")))
            target = ASSETS / name
            subprocess.run([
                "pdftocairo", "-png", "-singlefile", "-transp", "-r", str(DPI),
                str(tex.with_suffix(".pdf")), str(target),
            ], check=True)
            with Image.open(target.with_suffix(".png")) as img:
                width, height = img.size
            manifest[name] = {"width": width * 96 / DPI, "height": height * 96 / DPI,
                              "latex": formula, "source": source_name, "sha256": digest,
                              "fontPx": 20 * 96 / 72.27, "dpi": DPI}
            print("LaTeX:", name, flush=True)
    (ASSETS / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print("已渲染", len(manifest), "条 LaTeX 公式。")


if __name__ == "__main__":
    main()
