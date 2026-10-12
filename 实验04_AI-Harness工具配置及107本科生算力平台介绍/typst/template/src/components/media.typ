#import "../foundation/context.typ": active-theme

#let render-image-source(source, width: 100%, alt: none) = {
  if type(source) == content {
    source
  } else if type(source) == path or type(source) == bytes {
    image(source, width: width, alt: alt)
  } else {
    assert(false, message: "image source must be path(...), bytes, or content; bare strings are not package-safe")
  }
}

#let figure-image(source, caption: none, alt: none, width: 72%) = {
  figure(
    render-image-source(source, width: width, alt: alt),
    caption: caption,
  )
}

#let figure-grid(items, caption: none, columns: 2, gap: 1em) = context {
  let theme = active-theme.get()
  assert(theme != none, message: "figure-grid must be used inside a personal-typst-kit profile")
  assert(type(items) == array and items.len() > 0, message: "figure-grid items must be a non-empty array")
  assert(type(columns) == int and columns > 0, message: "figure-grid columns must be a positive integer")
  let cells = ()
  for item in items {
    let normalized = if type(item) == dictionary { item } else { (source: item,) }
    assert(normalized.keys().contains("source"), message: "each figure-grid item requires source")
    let item-caption = normalized.at("caption", default: none)
    let item-alt = normalized.at("alt", default: none)
    let item-width = normalized.at("width", default: 100%)
    cells.push([
      #set par(first-line-indent: 0em)
      #align(center)[#render-image-source(normalized.source, width: item-width, alt: item-alt)]
      #if item-caption != none [
        #v(0.3em)
        #align(center)[#text(size: theme.type-scale.small, fill: theme.colors.muted)[#item-caption]]
      ]
    ])
  }
  if target() == "html" {
    figure(
      cells.join([#v(0.6em)]),
      caption: caption,
    )
  } else {
    figure(
      grid(columns: columns, gutter: gap, ..cells),
      caption: caption,
    )
  }
}
