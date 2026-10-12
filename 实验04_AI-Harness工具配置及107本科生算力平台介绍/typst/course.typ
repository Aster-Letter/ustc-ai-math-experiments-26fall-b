// Course-specific composition; the kit remains an unmodified external dependency.
#import "template/lib.typ": manual, handout, themes, densities, theme-with, code-block, callout

// Keep the kit's font families; adjust typography independently of its theme.
#let course-fonts = (
  body: ("Noto Serif SC", "SimSun"),
  heading: ("Noto Sans SC", "Microsoft YaHei"),
  mono: ("DejaVu Sans Mono", "Noto Sans SC"),
)
#let course-type-scale = (body: 11.5pt, code: 9.2pt, h1: 17pt, h2: 14pt)
#let course-prose-tracking = 0.02em

#let course-code(value, language: "text") = {
  let label = if language == "bash" { [Bash · 平台终端] }
    else if language == "powershell" { [PowerShell · Windows] }
    else if language == "text" { [示例文本] }
    else { language }
  code-block(language: label, breakable: value.split("\n").len() > 16)[
    #set par(leading: 0.68em, spacing: 0em)
    #raw(value, block: true, lang: language)
  ]
}

#let course-body(body) = {
  // The unified Markdown carries section and appendix numbers for both formats.
  set heading(numbering: none)
  set par(first-line-indent: 0em)
  set text(tracking: course-prose-tracking)
  // An explicit size keeps shell commands readable and within the text column.
  show raw: set text(size: course-type-scale.code, tracking: 0pt)
  // Pandoc emits explicit header cells; keep the table structure.
  set table(inset: (x: 0.7em, y: 0.75em), stroke: themes.teal.spacing.line-width + themes.teal.colors.line)
  show table.cell.where(y: 0): set text(weight: "semibold")
  show table: set text(size: 10pt)
  body
}

#let course-document(body, front: [], title: "", variant: "handout", main: true) = {
  // Fit the combined long title without leaving its final character on a new line.
  show text.where(size: 19pt): set text(size: 17.5pt)
  let palette = if variant == "manual" { themes.blue } else { themes.teal }
  let theme = theme-with(
    palette,
    fonts: course-fonts,
    type-scale: course-type-scale,
    spacing: densities.normal + (
      leading: 0.78em,
      paragraph-gap: 1.1em,
      heading-1-above: 1.6em,
      heading-1-below: 0.7em,
      heading-2-above: 1.1em,
      heading-2-below: 0.55em,
      list-gap: 0.4em,
    ),
  )
  let meta = (
    title: title,
    subtitle: if main { [Windows 本地协作 · 107平台 CPU/GPU 实践] }
      else { [CIFAR-10 + ResNet-18 · 本地短测到平台单卡训练] },
    course: [AI1001B.03 · 实验 04],
    status: [自学试用版],
    version: [2026-10-12],
  )
  let options = (
    draft-mode: "hide",
    margin: (top: 2.4cm, bottom: 2.3cm, left: 2.2cm, right: 2.2cm),
    toc-depth: 2,
  )
  if variant == "manual" {
    manual(meta: meta, theme: theme, options: options + (toc: main,))[
      #course-body([#front#body])
    ]
  } else {
    handout(meta: meta, theme: theme, options: options + (toc: false, title-style: "compact"))[
      #if main [
        #course-body(front)
        #block(above: 0.9em, below: 1em)[
          #set text(size: 10pt)
          #set par(first-line-indent: 0em, leading: 0.65em)
          #outline(title: [阅读导航], depth: 2)
        ]
        #pagebreak()
      ]
      #course-body(if main { body } else { [#front#body] })
    ]
  }
}

