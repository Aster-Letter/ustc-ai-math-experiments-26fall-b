#import "../foundation/context.typ": active-draft-mode, active-theme

#let draft-note(body, title: [草稿说明]) = context {
  let mode = active-draft-mode.get()
  if mode == "error" {
    assert(false, message: "draft content remains: " + str(title))
  } else if mode == "hide" {
    []
  } else {
    let theme = active-theme.get()
    assert(theme != none, message: "draft-note must be used inside a personal-typst-kit profile")
    block(
      width: 100%,
      inset: 0.8em,
      fill: theme.colors.warning-soft,
      stroke: (left: 3pt + theme.colors.warning),
      radius: theme.spacing.radius,
    )[
      #set par(first-line-indent: 0em, justify: false)
      #text(font: theme.fonts.heading, weight: "bold", fill: theme.colors.warning)[#title]
      #v(0.3em)
      #body
    ]
  }
}

#let todo(body) = context {
  let mode = active-draft-mode.get()
  if mode == "error" {
    assert(false, message: "TODO remains: " + str(body))
  } else if mode == "hide" {
    []
  } else {
    let theme = active-theme.get()
    box(
      inset: (x: 0.35em, y: 0.12em),
      fill: theme.colors.warning-soft,
      stroke: theme.spacing.line-width + theme.colors.warning,
      radius: theme.spacing.radius,
    )[#text(size: theme.type-scale.small, fill: theme.colors.warning, weight: "bold")[TODO: #body]]
  }
}
