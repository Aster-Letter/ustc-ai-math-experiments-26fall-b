#import "../foundation/context.typ": active-theme

#let callout(body, kind: "note", title: none) = context {
  let theme = active-theme.get()
  assert(theme != none, message: "callout must be used inside a personal-typst-kit profile")
  let variants = (
    note: (label: [说明], color: theme.colors.accent, fill: theme.colors.accent-soft),
    tip: (label: [提示], color: theme.colors.success, fill: theme.colors.success-soft),
    warning: (label: [注意], color: theme.colors.warning, fill: theme.colors.warning-soft),
    danger: (label: [危险], color: theme.colors.danger, fill: theme.colors.danger-soft),
  )
  assert(variants.keys().contains(kind), message: "callout kind must be note, tip, warning, or danger")
  let variant = variants.at(kind)
  block(
    width: 100%,
    inset: (left: 1em, right: 1em, top: 0.75em, bottom: 0.75em),
    fill: variant.fill,
    stroke: (left: 3pt + variant.color),
    radius: theme.spacing.radius,
  )[
    #set par(first-line-indent: 0em, justify: false)
    #set text(size: 10pt)
    #text(font: theme.fonts.heading, weight: "bold", fill: variant.color)[
      #if title == none { variant.label } else { title }
    ]
    #v(0.35em)
    #body
  ]
}

#let source-quote(body, source: none) = context {
  let theme = active-theme.get()
  assert(theme != none, message: "source-quote must be used inside a personal-typst-kit profile")
  block(
    width: 100%,
    inset: (left: 1.1em, right: 1.1em, top: 0.8em, bottom: 0.8em),
    stroke: (left: 3pt + theme.colors.accent),
    fill: theme.colors.surface,
    radius: theme.spacing.radius,
  )[
    #set par(first-line-indent: 0em)
    #set text(size: 10pt)
    #body
    #if source != none [
      #v(0.4em)
      #align(right)[#text(fill: theme.colors.muted, size: theme.type-scale.small)[- #source]]
    ]
  ]
}
