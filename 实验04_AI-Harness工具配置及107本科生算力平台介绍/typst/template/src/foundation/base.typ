#import "context.typ": activate-context, special-heading-supplement
#import "config.typ": normalize-bibliography

#let color-token(theme, key, fallback) = theme.colors.at(key, default: fallback)
#let spacing-token(theme, key, fallback) = theme.spacing.at(key, default: fallback)
#let style-token(theme, key, fallback) = theme.at("styles", default: (:)).at(key, default: fallback)

#let render-heading(it, theme, mode: "paper", chapter-label: none) = {
  let special = it.supplement == special-heading-supplement
  if special {
    block(above: 1.05em, below: 0.7em, sticky: true)[
      #set par(first-line-indent: 0em)
      #set text(font: theme.fonts.heading, fill: color-token(theme, "heading", theme.colors.accent))
      #text(size: theme.type-scale.h2, weight: "semibold")[#it.body]
      #v(0.28em)
      #line(length: 3.2em, stroke: theme.spacing.line-width + theme.colors.accent)
    ]
  } else if mode == "book" and it.level == 1 {
    if target() == "paged" { pagebreak(weak: true) }
    block(above: 0em, below: 1.2em, sticky: true)[
      #set par(first-line-indent: 0em)
      #set text(font: theme.fonts.heading, fill: color-token(theme, "heading", theme.colors.accent))
      #if chapter-label != none and it.numbering != none [
        #text(size: theme.type-scale.small, fill: theme.colors.muted)[#chapter-label]
        #v(0.4em)
      ]
      #text(size: 19pt, weight: "bold")[#it]
      #v(0.55em)
      #line(length: 100%, stroke: theme.spacing.line-width + theme.colors.line)
    ]
  } else {
    let size = if it.level == 1 {
      theme.type-scale.h1
    } else if it.level == 2 {
      theme.type-scale.h2
    } else {
      theme.type-scale.h3
    }
    let above = if it.level == 1 {
      spacing-token(theme, "heading-1-above", 1.5em)
    } else if it.level == 2 {
      spacing-token(theme, "heading-2-above", 1em)
    } else {
      spacing-token(theme, "heading-3-above", 1em)
    }
    let below = if it.level == 1 {
      spacing-token(theme, "heading-1-below", 0.9em)
    } else if it.level == 2 {
      spacing-token(theme, "heading-2-below", 0.5em)
    } else {
      spacing-token(theme, "heading-3-below", 0.5em)
    }
    block(above: above, below: below, sticky: true)[
      #set par(first-line-indent: 0em)
      #set text(font: theme.fonts.heading, fill: color-token(theme, "heading", theme.colors.accent))
      #text(size: size, weight: if it.level == 1 { "bold" } else { "semibold" })[#it]
    ]
  }
}

#let base-style(
  body,
  theme: none,
  numbering: none,
  draft-mode: "show",
  heading-mode: "paper",
  chapter-label: none,
  heading-hook: none,
) = {
  assert(theme != none, message: "base-style requires theme")
  assert(numbering != none, message: "base-style requires numbering")
  activate-context(theme, draft-mode: draft-mode)
  set text(
    font: theme.fonts.body,
    size: theme.type-scale.body,
    fill: theme.colors.text,
    lang: "zh",
    region: "CN",
  )
  set par(
    first-line-indent: 2em,
    leading: theme.spacing.leading,
    spacing: theme.spacing.paragraph-gap,
    justify: true,
  )
  set heading(numbering: numbering)
  set quote(block: true)
  show link: set text(fill: color-token(theme, "link", theme.colors.accent))
  if style-token(theme, "link-underline", true) { show link: underline }
  show raw: set text(font: theme.fonts.mono, size: theme.type-scale.code)
  set figure(gap: spacing-token(theme, "caption-gap", 0.65em))
  set list(spacing: spacing-token(theme, "list-gap", 0.35em))
  set enum(spacing: spacing-token(theme, "list-gap", 0.35em))
  set terms(spacing: spacing-token(theme, "list-gap", 0.35em))
  set footnote.entry(clearance: spacing-token(theme, "footnote-clearance", 1em))
  show list: set block(
    above: spacing-token(theme, "list-block-gap", theme.spacing.paragraph-gap),
    below: spacing-token(theme, "list-block-gap", theme.spacing.paragraph-gap),
  )
  show enum: set block(
    above: spacing-token(theme, "list-block-gap", theme.spacing.paragraph-gap),
    below: spacing-token(theme, "list-block-gap", theme.spacing.paragraph-gap),
  )
  show terms: set block(
    above: spacing-token(theme, "list-block-gap", theme.spacing.paragraph-gap),
    below: spacing-token(theme, "list-block-gap", theme.spacing.paragraph-gap),
  )
  show footnote.entry: set par(
    first-line-indent: 0em,
    leading: spacing-token(theme, "footnote-leading", 0.62em),
  )
  show footnote.entry: set block(
    above: spacing-token(theme, "footnote-entry-gap", 0.3em),
  )
  show math.equation: set block(
    above: spacing-token(theme, "display-math-gap", 0.65em),
    below: spacing-token(theme, "display-math-gap", 0.65em),
  )
  show figure: set block(
    above: spacing-token(theme, "figure-gap", theme.spacing.block-gap),
    below: spacing-token(theme, "figure-gap", theme.spacing.block-gap),
  )
  show bibliography: it => {
    set par(
      first-line-indent: 0em,
      leading: spacing-token(theme, "bibliography-leading", theme.spacing.leading),
      spacing: spacing-token(theme, "bibliography-gap", theme.spacing.paragraph-gap),
      justify: style-token(theme, "bibliography-justify", false),
    )
    show link: set text(fill: color-token(theme, "bibliography-link", theme.colors.muted))
    if not style-token(theme, "bibliography-link-underline", false) {
      show underline: item => item.body
    }
    it
  }
  show heading: it => {
    if heading-hook != none { heading-hook(it) }
    render-heading(it, theme, mode: heading-mode, chapter-label: chapter-label)
  }
  body
}

#let render-keywords(values, separator: [、]) = {
  if type(values) == array { values.join(separator) } else { values }
}

#let render-outline(theme, title: [目录], depth: 3) = {
  block(
    above: spacing-token(theme, "outline-title-above", 1em),
    below: spacing-token(theme, "outline-title-below", 0.75em),
  )[
    #set par(first-line-indent: 0em)
    #set text(font: theme.fonts.heading, fill: color-token(theme, "heading", theme.colors.accent))
    #text(size: 18pt, weight: "bold")[#title]
  ]
  show outline.entry: set block(above: spacing-token(theme, "outline-entry-gap", 0.18em))
  outline(title: none, depth: depth)
}

#let page-footer(theme, numbering-style: "1") = context [
  #set text(size: theme.type-scale.small, fill: theme.colors.muted)
  #h(1fr)
  #counter(page).display(numbering-style)
  #h(1fr)
]

#let page-header(theme, left: none, right: none) = context [
  #set text(size: theme.type-scale.small, fill: theme.colors.muted)
  #if left != none [#left]
  #h(1fr)
  #if right != none [#right]
]

#let draft-background(theme, mode) = if mode == "show" {
  context {
    place(
      center + horizon,
      rotate(-24deg, text(size: 48pt, weight: "bold", fill: theme.colors.line)[DRAFT]),
    )
  }
} else {
  none
}

#let render-bibliography(config) = {
  let normalized = normalize-bibliography(config)
  if normalized != none {
    if normalized.pagebreak and target() == "paged" { pagebreak(weak: false) }
    let sources = if type(normalized.sources) == array {
      normalized.sources
    } else {
      (normalized.sources,)
    }
    bibliography(
      ..sources,
      title: normalized.title,
      style: normalized.style,
      full: normalized.full,
    )
  }
}
