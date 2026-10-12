# 实验04：决策树代码协作

本练习用实验02的决策树初始代码，观察 Agent 怎样读取项目、修改指定方法、运行检查，再根据结果继续修正。重点是学会组织任务和判断实际执行结果。本目录保留未完成的 T1–T7，内置西瓜数据；复制一份练习副本即可保留自己原来的实验02代码。

本练习供自学，不要求提交或评分。完整提示与操作见实验04讲义1.3章；需要复习 Python 时，可先看实验02的语法带练。

## 练习内容

| 阶段 | 交给 Agent 的任务 | 完成后自己查看 |
| --- | --- | --- |
| 先读项目 | 阅读 README、AGENTS.md 和程序，解释 T1–T7 的依赖关系 | 工具记录是否读到文件，解释是否与代码一致 |
| A：小范围修改 | 只实现 T1 `_entropy`，保持其余 TODO 不变 | T1 的代码差异、手算小例子和 `5/5 passed` |
| B：继续推进 | 基于当前 T1，分阶段完成 T2–T7 | 完整自查 `16/16 passed`，实际运行的树与预测结果 |

## 从这里开始

**准备副本与环境**

1. 先按实验04讲义配置可用的 Codex/API 连接，再把本目录完整复制到自己的练习位置。
2. 用桌面应用打开这份副本，新建会话；在课程终端进入同一个目录。
3. 沿用实验01/02的 `ustc-ai-experiments-26fall-B`（Python 3.11）。本程序和自查工具只使用标准库，无需新增依赖。在副本根目录运行：

```powershell
conda activate ustc-ai-experiments-26fall-B
python --version
python -c "import sys; print(sys.executable)"
python decision_tree.py
```

在 Miniforge Prompt 或已初始化 conda 的终端执行。将打印出的完整 Python 路径告诉 Agent，后续使用同一解释器；新开的 Agent 命令进程可能没有继承终端环境。初始程序输出 `None` 是待补方法的占位结果。

**先读取，再做 A→B**

先要求 Agent 阅读项目并解释数据与函数调用，暂不修改。随后按讲义 A 阶段的提示只完成 T1，自己打开代码差异并运行：

```powershell
python checks.py --stage a
```

T1 完成后再按 B 阶段的提示扩展到 T2–T7，运行：

```powershell
python checks.py --stage b
python decision_tree.py
```

初始骨架的自查会失败；A/B 完成后的预期分别为 `5/5 passed` 和 `16/16 passed`。遇到失败，把具体项目、报错和当前改动交给 Agent 继续修正。保留检查脚本和内置数据不变；看实际运行输出，也结合小例子理解实现。训练集上的回代预测用于检查程序，不代表独立测试集上的泛化表现。

## 配套文件与补充用法

- `decision_tree.py`：实验02初始骨架，T1–T7 保持未完成。
- `checks.py`：只用标准库的分阶段自查工具，失败输出指出项目、预期值或异常。
- `AGENTS.md`：练习范围、解释器、实现规则与自查方式的项目约定。

检查其他位置的实现时，可用 `--target`，例如：

```powershell
python checks.py --stage a --target "C:\Users\your-name\Documents\agent-lab2\decision_tree.py"
```

检查样例覆盖部分重要行为，不能证明所有输入上都正确。平台 GPU 项目使用另设环境，按平台项目说明准备。

来源：[课程实验02初始材料](https://github.com/Aster-Letter/ustc-ai-math-experiments-26fall-b/tree/main/实验02_信息熵与决策树)，复制日期 2026-10-02。T1–T7 保持未补全。原始文件中的上级讲义路径属于实验02原有布局；实验04操作从本说明开始，练习副本不改变原课程任务。

返回[实验04讲义](../../实验04_实验讲义.md#sec-06)。
