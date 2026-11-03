# 实验六课件

`实验06_TinyGPT五言诗生成.pptx`：35页，30页课堂主线与5页附录。135分钟与讲义一致，完整训练和报告可课后完成。主讲钟志诚，整理曾有成、冯筱璐。

- 第2页用一页对照CNN、BERT、GPT、GAN与扩散模型。整份课件的公式、数学形状标注和手算表达统一由LaTeX渲染，42条源表达式在课件中使用44次。公式以高分辨率透明图像嵌入，修改时编辑对应LaTeX源后重建。
- 正文、代码、图示框线与连接线保留原生对象；11页使用原生表格，3页使用原生图表，并包含图表数据工作簿。主要标题约32pt，正文与代码约18—25pt，核心公式约25.5pt；英文全称、页码及图下注释按辅助信息处理。
- 公式编号按讲义主题小节组织，拆开的等式在课件内重新编号；推导细节参见讲义相应小节。矩阵与标量的样式在PowerPoint中保留。
- 教学示意均为本课绘制；实测曲线取自原始记录，未平滑，图表数值为兼容电子表格保留6位小数，完整精度见随附CSV。
- 当前主数据：THU-CCPC五言子集。旧小语料长训练和散文清洗作为补充对照，页内注明设置与来源。预跑设备为pro5k；学生在107平台通过Slurm完成实验。
- 第19—21页在提交作业前说明1节点、1任务、1张GPU、每任务4个CPU、8G主内存、1小时时限；演示通过107的Web终端运行 `pwd` 与 `conda env list`，整串替换 `your` 占位路径，再检查解释器与PyTorch。
- 第35页及各结果页备注列出来源。完整实验记录位于上级 `teacher/` 中，不随学生材料包分发。

## 内容安排

1—3：任务对比、目标与真实输出；4—7：自回归、嵌入、掩码与解码器；8—10：数据、配置、任务地图；11—18：T1—T6公式与代码练习；19—22：107资源配置、Web终端查路径、网页提交与复现；23—27：评估、真实结果与记忆；28—30：学生对照、自检与提交；31—35：参数、梯度、命令、散文对照及来源。

## 维护

直接编辑PPTX即可。`build.mjs` 为构建源，使用OpenAI Artifact Tool生成课件，需配置以下环境变量后运行 `node build.mjs`：

- `RUNTIME_NODE_MODULES`：包含 `@oai/artifact-tool` 的依赖目录。
- `PRESENTATION_SKILL_DIR`：包含 `container_tools/artifact_tool_utils.mjs` 和验证脚本的 presentations 技能目录。
- `PRESENTATION_PYTHON`：带验证依赖的Python解释器绝对路径。

每次构建在实验目录的 `tmp/slides-build-时间戳/` 保存图像与验证记录，成功后更新本目录PPTX。发布前逐页检查，并同步更新学生材料包。

第2页公式源保存在 `latex/task-formulas.tex`，其余数学表达保存在 `latex/course-formulas.tex`。在实验目录执行 `python slides/render_formulas.py`，再构建课件。公式渲染需要Tectonic、Poppler的 `pdftocairo`、Python的Pillow、Noto Sans CJK SC字体和STIX Two Math数学字体；使用384dpi透明图像，图像和尺寸清单保存在 `assets/formulas/`。脚本按源内容缓存，未修改公式时可直接使用随源文件保留的图像构建。
