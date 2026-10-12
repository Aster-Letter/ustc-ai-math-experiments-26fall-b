#import "../foundation/base.typ": render-keywords

#let inline-meta(meta, fields, separator: 1.4em) = {
  let values = ()
  for field in fields {
    let value = meta.at(field)
    if value != none { values.push(value) }
  }
  for (index, value) in values.enumerate() {
    if index > 0 { h(separator) }
    value
  }
}

#let paper-title(meta, theme) = align(center)[
  #v(1.7em)
  #text(font: theme.fonts.heading, size: theme.type-scale.title, weight: "bold")[#meta.title]
  #if meta.subtitle != none [
    #v(0.7em)
    #text(size: theme.type-scale.subtitle, fill: theme.colors.muted)[#meta.subtitle]
  ]
  #v(1.4em)
  #set text(size: 10.5pt)
  #inline-meta(meta, ("author", "organization", "course", "date"))
]

#let book-title(meta, theme) = align(center)[
  #v(5.5em)
  #block(width: 72%)[
    #set par(first-line-indent: 0em)
    #align(left)[
      #text(font: theme.fonts.heading, size: theme.type-scale.small, fill: theme.colors.muted)[BOOK]
      #v(0.7em)
      #line(length: 5em, stroke: 1.15pt + theme.colors.accent)
      #v(1.2em)
      #text(font: theme.fonts.heading, size: 25pt, weight: "bold")[#meta.title]
      #if meta.subtitle != none [
        #v(0.75em)
        #text(size: theme.type-scale.subtitle, fill: theme.colors.muted)[#meta.subtitle]
      ]
      #v(2.5em)
      #if meta.author != none [#text(size: 12pt)[#meta.author]]
      #if meta.organization != none [#v(0.45em)#text(fill: theme.colors.muted)[#meta.organization]]
      #if meta.date != none [#v(0.45em)#text(fill: theme.colors.muted)[#meta.date]]
    ]
  ]
]

#let manual-title(meta, theme) = align(center)[
  #v(4em)
  #block(width: 78%)[
    #set par(first-line-indent: 0em)
    #text(font: theme.fonts.heading, size: theme.type-scale.small, fill: theme.colors.accent, weight: "bold")[TECHNICAL GUIDE]
    #v(0.7em)
    #text(font: theme.fonts.heading, size: 24pt, weight: "bold")[#meta.title]
    #if meta.subtitle != none [#v(0.65em)#text(size: theme.type-scale.subtitle, fill: theme.colors.muted)[#meta.subtitle]]
    #v(1.3em)
    #line(length: 100%, stroke: theme.spacing.line-width + theme.colors.line)
    #v(0.8em)
    #set text(size: 10pt)
    #inline-meta(meta, ("version", "status", "organization", "author", "date"))
  ]
]

#let handout-panel-title(meta, theme) = block(
  width: 100%,
  inset: (left: 1.1em, right: 1.1em, top: 1.1em, bottom: 1em),
  fill: theme.colors.accent-soft,
  stroke: (left: 4pt + theme.colors.accent),
  radius: theme.spacing.radius,
)[
  #set par(first-line-indent: 0em)
  #text(font: theme.fonts.heading, size: 9pt, fill: theme.colors.accent, weight: "bold")[LEARNING HANDOUT]
  #v(0.35em)
  #text(font: theme.fonts.heading, size: 20pt, weight: "bold")[#meta.title]
  #if meta.subtitle != none [#v(0.45em)#text(fill: theme.colors.muted)[#meta.subtitle]]
  #v(0.65em)
  #set text(size: 9.5pt)
  #inline-meta(meta, ("course", "audience", "author", "date"))
]

#let handout-compact-title(meta, theme) = block(
  above: 0.4em,
  below: 0.9em,
)[
  #set par(first-line-indent: 0em)
  #text(
    font: theme.fonts.heading,
    size: 19pt,
    weight: "bold",
    fill: theme.colors.accent,
  )[#meta.title]
  #if meta.subtitle != none [
    #v(0.35em)
    #text(size: 10pt, fill: theme.colors.muted)[#meta.subtitle]
  ]
  #v(0.65em)
  #line(length: 100%, stroke: theme.spacing.line-width + theme.colors.line)
]

#let handout-title(meta, theme, style: "panel") = {
  if style == "compact" {
    handout-compact-title(meta, theme)
  } else {
    handout-panel-title(meta, theme)
  }
}

#let abstract-block(meta, theme) = if meta.abstract != none {
  block(
    inset: 0.85em,
    stroke: 0.45pt + theme.colors.line,
    radius: calc.min(theme.spacing.radius, 2pt),
  )[
    #set par(first-line-indent: 0em)
    #strong[摘要] \
    #meta.abstract
    #if meta.keywords != none [
      #v(0.75em)
      #strong[关键词：]#render-keywords(meta.keywords)
    ]
  ]
}
