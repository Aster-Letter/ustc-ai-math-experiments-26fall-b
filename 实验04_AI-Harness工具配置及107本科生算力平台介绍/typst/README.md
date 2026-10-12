# 讲义排版源与模板

Typst 是一种文档排版语言，用 `.typ` 纯文本文件编写正文、数学公式和样式，再编译为 PDF，适合讲义、报告和论文。它支持简洁的标记语法，也能用函数统一排版；例如 `= 标题` 表示标题，`*加粗*` 表示强调，`$a^2 + b^2 = c^2$` 写公式，`#set text(size: 11pt)` 设置字号。可以从 [Typst 官方入门教程](https://typst.app/docs/tutorial/)开始了解。

这里附上本轮实际使用的排版源。模板来源为 [personal-typst-kit 仓库](https://github.com/Aster-Letter/personal-typst-kit)，包内保留本轮采用的 0.2.3 源码和许可证，放在 template/；无需安装本地 Typst 包或另行下载模板。

- [main.typ](main.typ)：本轮从 Markdown 导出的完整讲义排版源。
- [course.typ](course.typ)：本实验的字体、字号、间距及主题配置。
- [template/lib.typ](template/lib.typ)：模板入口；版本信息见 [typst.toml](template/typst.toml)，许可见 [LICENSE](template/LICENSE)。

## 在 VS Code 中阅读与预览

推荐使用 **[Tinymist Typst](https://marketplace.visualstudio.com/items?itemName=myriad-dreamin.tinymist)** 扩展，扩展 ID 为 `myriad-dreamin.tinymist`。它提供 Typst 语法支持和实时排版预览。

1. 完整解压材料包，用 VS Code 打开包含 assets/、code/、typst/ 的实验根目录，再在扩展面板搜索并安装 Tinymist Typst。
2. 在当前工作区设置中搜索 **Tinymist Root Path**，填入这个实验根目录的绝对路径，即 assets/ 所在的目录；设置后重载窗口。本讲义的图片路径从这个根目录解析。
3. 打开 `typst/main.typ`，按 `Ctrl+Shift+P` 打开命令面板，执行 **Typst Pin Main** 固定主文件，再搜索 **Typst Preview** 打开预览；也可使用快捷键 `Ctrl+K V`。
4. 编辑正文或 course.typ 时，观察主讲义预览和错误提示。需要导出时执行 **Typst Export PDF**，或使用下方命令指定输出文件。

预览的是 main.typ 排出的讲义，Markdown 阅读仍使用 VS Code 的 Markdown 预览。主文件固定状态在重开编辑器后可能需要重新设置；更多操作见 [Tinymist 官方使用说明](https://github.com/Myriad-Dreamin/tinymist/blob/main/editors/vscode/README.md)。

## 编译 PDF

安装 Typst 0.15 或更新版本。完整解压材料包，进入含 README.md、讲义和 assets/ 的实验根目录，执行：

```powershell
typst compile --root . typst/main.typ 实验04_实验讲义.pdf
```

从整个实验根目录编译，保留 assets/；单独移动 main.typ 会缺少模板和配图。阅读 PDF、运行决策树或平台项目都不需要安装 Typst。

## 调整字体与正文

编辑 course.typ 中的 course-fonts、course-type-scale、course-prose-tracking，以及主题 spacing 中的 leading / paragraph-gap。当前正文用 Noto Serif SC，标题用 Noto Sans SC，代码用 DejaVu Sans Mono；中文字体带宋体/微软雅黑回退。用 typst fonts 查看可用家族，换机器后字体差异可能影响分页；图中文字来自 PNG，不随正文字体修改。

讲义 Markdown 保存正文，main.typ 是对应的排版导出源。维护正文时优先改 Markdown；直接改 main.typ 可以编译 PDF，但不会回写 Markdown。生成更新稿时应重新导出 main.typ，避免两份正文分叉。
