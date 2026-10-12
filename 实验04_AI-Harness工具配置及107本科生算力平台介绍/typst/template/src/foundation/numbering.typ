// Native Typst numbering presets. No hand-maintained upper bound.

#let cjk-paper-numbering(..numbers) = {
  let values = numbers.pos()
  let value = values.last()
  if values.len() == 1 {
    [#numbering("一", value)、]
  } else if values.len() == 2 {
    [（#numbering("一", value)）]
  } else {
    [#numbering("1", value).]
  }
}

#let chapter-numbering(..numbers) = {
  let values = numbers.pos()
  if values.len() == 1 {
    [第#numbering("一", values.first())章]
  } else {
    numbering("1.1", ..values)
  }
}

#let decimal-numbering(..numbers) = numbering("1.1", ..numbers.pos())
#let roman-outline-numbering(..numbers) = numbering("I.i.1", ..numbers.pos())

#let numbering-presets = (
  cjk-paper: cjk-paper-numbering,
  chapter: chapter-numbering,
  decimal: decimal-numbering,
  roman-outline: roman-outline-numbering,
)
