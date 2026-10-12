#import "../foundation/context.typ": active-theme, special-heading-supplement

#let code-block(body, title: none, language: none, breakable: auto) = context {
  let theme = active-theme.get()
  assert(theme != none, message: "code-block must be used inside a personal-typst-kit profile")
  assert(breakable == auto or type(breakable) == bool, message: "code-block breakable must be auto or bool")
  let can-break = if breakable == auto { true } else { breakable }
  block(
    width: 100%,
    breakable: can-break,
    above: theme.spacing.at("code-block-gap", default: theme.spacing.block-gap),
    below: theme.spacing.at("code-block-gap", default: theme.spacing.block-gap),
    inset: theme.spacing.at("code-block-inset", default: 0.9em),
    fill: theme.colors.surface,
    stroke: theme.spacing.line-width + theme.colors.line,
    radius: theme.spacing.radius,
  )[
    #set par(first-line-indent: 0em, justify: false)
    #if title != none or language != none [
      #text(font: theme.fonts.heading, size: theme.type-scale.small, fill: theme.colors.muted, weight: "semibold")[
        #if title != none { title }
        #if title != none and language != none { [ · ] }
        #if language != none { language }
      ]
      #v(theme.spacing.at("code-block-header-gap", default: 0.35em))
    ]
    #body
  ]
}

#let steps(..items) = context {
  let theme = active-theme.get()
  assert(theme != none, message: "steps must be used inside a personal-typst-kit profile")
  enum(
    numbering: "1.",
    indent: 1.4em,
    body-indent: 0.6em,
    spacing: 0.55em,
    ..items.pos(),
  )
}

#let cn-footnote(body) = footnote[#text(size: 9pt)[#body]]

#let source-note(body, label: [资料说明]) = cn-footnote[
  #strong[#label：]#body
]

#let special-section(
  title,
  label: "EX",
  level: 2,
  numbered: true,
  counter-style: "A",
  outlined: true,
) = {
  assert(type(label) == str, message: "special-section label must be a string")
  assert(type(level) == int and level >= 1, message: "special-section level must be a positive integer")
  let named-counter = counter("personal-typst-kit-special-" + label)
  if numbered { named-counter.step() }
  context {
    let marker = if numbered {
      [ #numbering(counter-style, named-counter.get().first())]
    } else {
      []
    }
    heading(
      level: level,
      numbering: none,
      outlined: outlined,
      supplement: special-heading-supplement,
    )[#label#marker：#title]
  }
}
