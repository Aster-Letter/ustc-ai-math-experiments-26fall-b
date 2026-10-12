#import "../foundation/context.typ": active-theme

#let align-content = align

#let statement-kind = "personal-typst-kit-working-paper-statement"
#let statement-counter = counter(figure.where(kind: statement-kind))
#let statement-state = state("personal-typst-kit-working-paper-statement-state", (
  section: none,
  local: 0,
  labels: (:),
))

#let statement-numbering(..numbers) = context {
  let values = numbers.pos()
  let global = values.last()
  statement-state.get().labels.at(str(global), default: numbering("1", global))
}

#let statement(body, label, title: none) = figure(
  kind: statement-kind,
  supplement: label,
  numbering: statement-numbering,
  context {
    let theme = active-theme.get()
    assert(theme != none, message: "working-paper statements must be used inside a personal-typst-kit profile")
    let heading-color = theme.colors.at("heading", default: theme.colors.accent)
    let global = statement-counter.get().first()
    let section-values = counter(heading).get()
    let section = if section-values.len() > 0 { section-values.first() } else { 0 }
    let snapshot = statement-state.get()
    let local = if snapshot.section == section { snapshot.local + 1 } else { 1 }
    let rendered-number = if section > 0 { str(section) + "." + str(local) } else { str(local) }
    let labels = snapshot.labels
    labels.insert(str(global), rendered-number)
    statement-state.update((section: section, local: local, labels: labels))
    align(left)[
      #block(
        width: 100%,
        inset: (left: 0.8em),
        stroke: (left: theme.spacing.line-width + theme.colors.line),
      )[
        #set par(first-line-indent: 0em)
        #text(font: theme.fonts.heading, weight: "semibold", fill: heading-color)[
          #label #rendered-number
          #if title != none [（#title）]
        ]
        #h(0.65em)
        #body
      ]
    ]
  },
)

#let theorem(body, title: none) = statement(body, [定理], title: title)
#let lemma(body, title: none) = statement(body, [引理], title: title)
#let proposition(body, title: none) = statement(body, [命题], title: title)
#let definition(body, title: none) = statement(body, [定义], title: title)

#let proof(body, title: [证明]) = context {
  let theme = active-theme.get()
  assert(theme != none, message: "proof must be used inside a personal-typst-kit profile")
  block(width: 100%, above: theme.spacing.block-gap, below: theme.spacing.block-gap)[
    #set par(first-line-indent: 0em)
    #text(font: theme.fonts.heading, weight: "semibold")[#title：]
    #body
    #align(right)[□]
  ]
}

#let remark(body, title: [注]) = context {
  let theme = active-theme.get()
  assert(theme != none, message: "remark must be used inside a personal-typst-kit profile")
  block(
    width: 100%,
    above: theme.spacing.block-gap,
    below: theme.spacing.block-gap,
    inset: (left: 0.8em),
    stroke: (left: theme.spacing.line-width + theme.colors.line),
  )[
    #set par(first-line-indent: 0em)
    #text(font: theme.fonts.heading, weight: "semibold")[#title：]
    #body
  ]
}

#let acknowledgements(body, title: [致谢], outlined: true) = {
  assert(type(outlined) == bool, message: "acknowledgements outlined must be bool")
  heading(numbering: none, outlined: outlined)[#title]
  body
}

#let paper-table(
  body,
  caption: none,
  note: none,
  align: auto,
  inset: none,
  header-fill: true,
  outlined: true,
) = context {
  let theme = active-theme.get()
  assert(theme != none, message: "paper-table must be used inside a personal-typst-kit profile")
  assert(type(header-fill) == bool, message: "paper-table header-fill must be bool")
  assert(type(outlined) == bool, message: "paper-table outlined must be bool")
  let cell-inset = if inset == none {
    (
      x: theme.spacing.at("paper-table-inset-x", default: 0.7em),
      y: theme.spacing.at("paper-table-inset-y", default: 0.55em),
    )
  } else {
    inset
  }
  figure(
    block(width: 100%)[
      #set par(first-line-indent: 0em)
      #set table(
        align: align,
        inset: cell-inset,
        stroke: theme.spacing.line-width + theme.colors.line,
      )
      #show table.cell.where(y: 0): set text(font: theme.fonts.heading, weight: "semibold")
      #if header-fill {
        show table.cell.where(y: 0): set table.cell(fill: theme.colors.surface)
      }
      #body
      #if note != none [
        #block(
          width: 100%,
          above: theme.spacing.at("paper-table-note-gap", default: 0.55em),
        )[
          #set par(first-line-indent: 0em, justify: false)
          #align-content(left)[#text(size: theme.type-scale.small, fill: theme.colors.muted)[#note]]
        ]
      ]
    ],
    kind: table,
    caption: caption,
    outlined: outlined,
  )
}

#let appendix-numbering(..numbers) = {
  let values = numbers.pos()
  if values.len() == 1 {
    [附录 #numbering("A", values.first())]
  } else {
    [#numbering("A", values.first()).#numbering("1.1", ..values.slice(1))]
  }
}

#let force-pagebreak = pagebreak

#let appendices(
  body,
  pagebreak: true,
  numbering: appendix-numbering,
  outlined: true,
) = context {
  assert(type(pagebreak) == bool, message: "appendices pagebreak must be bool")
  assert(type(outlined) == bool, message: "appendices outlined must be bool")
  if pagebreak and target() == "paged" { force-pagebreak(weak: false) }
  counter(heading).update(0)
  set heading(numbering: numbering, outlined: outlined)
  body
}
