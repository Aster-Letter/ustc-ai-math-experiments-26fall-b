#import "../components/callouts.typ": callout
#import "../foundation/context.typ": active-theme

#let learning-objectives(..items) = {
  let values = items.pos()
  assert(values.len() > 0, message: "learning-objectives requires at least one item")
  callout(kind: "tip", title: [学习目标])[
    #list(..values)
  ]
}

#let definition-box(term, body) = callout(kind: "note", title: [定义：#term])[#body]

#let worked-example(body, title: [例题]) = callout(kind: "tip", title: title)[#body]

#let exercise(body, title: [练习], points: none) = callout(kind: "warning", title: [
  #title#if points != none [（#points 分）]
])[#body]

#let lesson-summary(..items) = {
  let values = items.pos()
  assert(values.len() > 0, message: "lesson-summary requires at least one item")
  callout(kind: "note", title: [本节小结])[
    #list(..values)
  ]
}

#let response-area(
  rows: 5,
  label: [作答区],
  ruled: false,
) = context {
  let theme = active-theme.get()
  assert(theme != none, message: "response-area must be used inside a personal-typst-kit profile")
  assert(type(rows) == int and rows >= 1, message: "response-area rows must be a positive integer")
  assert(type(ruled) == bool, message: "response-area ruled must be bool")

  block(
    width: 100%,
    inset: (x: 0.8em, y: 0.55em),
    stroke: theme.spacing.line-width + theme.colors.line,
    radius: theme.spacing.radius,
  )[
    #set par(first-line-indent: 0em)
    #if label != none [
      #text(size: theme.type-scale.small, fill: theme.colors.muted)[#label]
      #v(0.55em)
    ]
    #if ruled [
      #for _ in range(rows) [
        #line(length: 100%, stroke: 0.5pt + theme.colors.line)
        #v(1.15em)
      ]
    ] else [
      #v(rows * 1.35em)
    ]
  ]
}
