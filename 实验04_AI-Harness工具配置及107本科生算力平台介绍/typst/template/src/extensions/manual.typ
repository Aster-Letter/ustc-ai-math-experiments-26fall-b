#import "../foundation/context.typ": active-theme
#import "../components/callouts.typ": callout

#let prerequisites(..items) = {
  let values = items.pos()
  assert(values.len() > 0, message: "prerequisites requires at least one item")
  callout(kind: "note", title: [前置条件])[
    #list(..values)
  ]
}

#let revision-history(entries, title: [修订记录]) = context {
  let theme = active-theme.get()
  assert(theme != none, message: "revision-history must be used inside a personal-typst-kit profile")
  assert(type(entries) == array and entries.len() > 0, message: "revision-history entries must be a non-empty array")
  let rows = (
    table.header([*版本*], [*日期*], [*变更摘要*]),
  )
  for entry in entries {
    assert(type(entry) == dictionary, message: "each revision-history entry must be a dictionary")
    for key in ("version", "date", "summary") {
      assert(entry.keys().contains(key), message: "revision-history entry requires " + key)
    }
    rows.push(entry.version)
    rows.push(entry.date)
    rows.push(entry.summary)
  }
  block(above: 0.8em, below: 0.8em)[
    #set par(first-line-indent: 0em)
    #text(
      font: theme.fonts.heading,
      size: theme.type-scale.h2,
      weight: "bold",
      fill: theme.colors.accent,
    )[#title]
    #v(0.55em)
    #table(
      columns: (auto, auto, 1fr),
      inset: 0.55em,
      stroke: theme.spacing.line-width + theme.colors.line,
      fill: (x, y) => if y == 0 { theme.colors.accent-soft } else { none },
      ..rows,
    )
  ]
}
