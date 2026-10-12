#import "../themes/themes.typ": themes
#import "../foundation/numbering.typ": numbering-presets
#import "../foundation/config.typ": ensure-dictionary, merge-known, normalize-meta, reject-unknown, require-key, validate-choice
#import "../foundation/base.typ": base-style, draft-background, page-footer, page-header, render-bibliography, render-keywords, render-outline

#let author-defaults = (
  name: none,
  affiliation: none,
  email: none,
  corresponding: false,
  note: none,
)

#let normalize-author(entry, index) = {
  ensure-dictionary("working-paper meta.authors.at(" + str(index) + ")", entry)
  let name = "working-paper meta.authors.at(" + str(index) + ")"
  let result = merge-known(name, author-defaults, entry)
  require-key(name, result, "name")
  assert(type(result.corresponding) == bool, message: name + ".corresponding must be bool")
  assert(result.email == none or type(result.email) == str, message: name + ".email must be a string")
  result
}

#let normalize-authors(meta) = {
  assert(not (meta.author != none and meta.authors != none), message: "working-paper meta.author and meta.authors cannot both be provided")
  let values = if meta.authors != none {
    assert(type(meta.authors) == array, message: "working-paper meta.authors must be an array")
    meta.authors
  } else if meta.author != none {
    ((name: meta.author),)
  } else {
    ()
  }
  values.enumerate().map(pair => normalize-author(pair.at(1), pair.at(0)))
}

#let normalize-english(value) = {
  if value == none {
    none
  } else {
    ensure-dictionary("working-paper meta.english", value)
    let result = merge-known("working-paper meta.english", (
      title: none,
      abstract: none,
      keywords: none,
    ), value)
    require-key("working-paper meta.english", result, "title")
    require-key("working-paper meta.english", result, "abstract")
    result
  }
}

#let option-defaults = (
  paper: "a4",
  margin: 2.54cm,
  front-matter: "cover-toc",
  front-matter-density: "normal",
  toc-depth: 3,
  numbering: none,
  page-numbering-start: "body",
  header: false,
  draft-mode: "hide",
  bibliography: none,
)

#let normalize-working-options(options) = {
  let result = merge-known("working-paper options", option-defaults, options)
  validate-choice("working-paper options.front-matter", result.front-matter, ("cover-toc", "title-page", "inline"))
  validate-choice("working-paper options.front-matter-density", result.front-matter-density, ("compact", "normal", "relaxed"))
  validate-choice("working-paper options.page-numbering-start", result.page-numbering-start, ("document", "body"))
  validate-choice("working-paper options.draft-mode", result.draft-mode, ("show", "hide", "error"))
  assert(type(result.toc-depth) == int and result.toc-depth >= 1, message: "working-paper options.toc-depth must be a positive integer")
  assert(type(result.header) == bool, message: "working-paper options.header must be bool")
  result
}

#let spacing-value(theme, key, fallback, factor: 1) = theme.spacing.at(key, default: fallback) * factor

#let front-density-factor(value) = if value == "compact" {
  0.74
} else if value == "relaxed" {
  1.16
} else {
  1
}

#let metadata-string(value) = if type(value) == str {
  value
} else {
  let rendered = repr(value)
  if rendered.starts-with("[") and rendered.ends-with("]") {
    rendered.slice(1, rendered.len() - 1)
  } else {
    rendered
  }
}

#let render-author(author, theme, factor) = align(center)[
  #set par(first-line-indent: 0em)
  #text(font: theme.fonts.heading, weight: "semibold")[
    #author.name#if author.corresponding [#super[\*]]
  ]
  #if author.affiliation != none [
    #v(0.4em * factor)
    #text(size: theme.type-scale.small, fill: theme.colors.muted)[#author.affiliation]
  ]
]

#let author-notes(authors, theme, factor) = {
  let rows = ()
  let corresponding = authors.filter(author => author.corresponding)
  if corresponding.len() > 0 {
    let contacts = corresponding.map(author => if author.email == none {
      author.name
    } else {
      [#author.name（#link("mailto:" + author.email)[#author.email]）]
    })
    rows.push([\* 通讯作者：#contacts.join([；])])
  }
  for author in authors {
    if author.email != none and not author.corresponding {
      rows.push([#author.name：#link("mailto:" + author.email)[#author.email]])
    }
    if author.note != none { rows.push([#author.name：#author.note]) }
  }
  if rows.len() > 0 {
    v(spacing-value(theme, "front-author-notes-gap", 1.05em, factor: factor))
    block(width: 88%)[
      #set par(first-line-indent: 0em, spacing: 0.42em)
      #set text(size: theme.type-scale.small, fill: theme.colors.muted)
      #rows.join(linebreak())
    ]
  }
}

#let front-details(meta, theme, factor) = {
  let rows = ()
  if meta.course != none { rows.push([#strong[课程：]#meta.course]) }
  if meta.extra-lines != none {
    assert(type(meta.extra-lines) == array, message: "working-paper meta.extra-lines must be an array")
    for line in meta.extra-lines {
      assert(type(line) == content or type(line) == str, message: "working-paper meta.extra-lines entries must be content or strings")
    }
    rows += meta.extra-lines
  }
  if rows.len() > 0 {
    v(spacing-value(theme, "front-details-gap", 0.8em, factor: factor))
    block(width: 88%)[
      #set par(first-line-indent: 0em, spacing: 0.35em * factor)
      #set text(size: 9.5pt, fill: theme.colors.muted)
      #rows.join(linebreak())
    ]
  }
}

#let abstract-section(title, abstract, keywords, theme, english: false, above: 2em, factor: 1) = {
  if abstract != none {
    block(width: 100%, above: above * factor, below: 0.85em * factor)[
      #set par(first-line-indent: 0em)
      #align(center)[
        #text(font: theme.fonts.heading, size: 10.5pt, weight: "semibold")[#title]
      ]
      #v(spacing-value(theme, "front-abstract-title-gap", 1em, factor: factor))
      #set text(size: 9.5pt, lang: if english { "en" } else { "zh" })
      #abstract
      #if keywords != none [
        #block(width: 100%, above: spacing-value(theme, "front-keywords-gap", 0.9em, factor: factor))[
          #strong[#if english { [Keywords: ] } else { [关键词：] }]#render-keywords(keywords, separator: if english { [, ] } else { [、] })
        ]
      ]
    ]
  }
}

#let working-title(meta, authors, english, theme, density: "normal") = {
  let factor = front-density-factor(density)
  align(center)[
  #v(spacing-value(theme, "front-top", 2.65em, factor: factor))
  #block(width: 92%)[
    #set par(first-line-indent: 0em)
    #text(font: theme.fonts.heading, size: theme.type-scale.title, weight: "bold", fill: theme.colors.at("heading", default: theme.colors.accent))[#meta.title]
    #if meta.subtitle != none [
      #v(spacing-value(theme, "front-subtitle-gap", 0.85em, factor: factor))
      #text(size: theme.type-scale.subtitle, fill: theme.colors.muted)[#meta.subtitle]
    ]
    #if authors.len() > 0 [
      #let author-columns = if authors.len() == 4 { 2 } else { calc.min(3, authors.len()) }
      #v(spacing-value(theme, "front-authors-gap", 2em, factor: factor))
      #grid(
        columns: author-columns,
        column-gutter: 1.2em,
        row-gutter: spacing-value(theme, "front-author-row-gap", 1.35em, factor: factor),
        ..authors.map(author => render-author(author, theme, factor)),
      )
      #author-notes(authors, theme, factor)
    ]
    #if meta.organization != none [
      #v(spacing-value(theme, "front-organization-gap", 1.05em, factor: factor))
      #text(size: 10pt, fill: theme.colors.accent)[#meta.organization]
    ]
    #front-details(meta, theme, factor)
    #if meta.version != none [
      #v(spacing-value(theme, "front-version-gap", 0.9em, factor: factor))
      #text(size: 9.5pt)[版本：#meta.version]
    ]
    #if meta.date != none [
      #v(spacing-value(theme, "front-date-gap", 0.7em, factor: factor))
      #text(size: 9.5pt)[日期：#meta.date]
    ]
  ]
  #align(left)[
    #abstract-section(
      [摘 要], meta.abstract, meta.keywords, theme,
      above: theme.spacing.at("front-abstract-gap", default: 2em),
      factor: factor,
    )
    #if english != none [
      #block(width: 100%, above: spacing-value(theme, "front-english-title-gap", 1.25em, factor: factor))[
        #align(center)[
          #text(font: theme.fonts.heading, size: theme.type-scale.subtitle, weight: "semibold", fill: theme.colors.at("heading", default: theme.colors.accent))[#english.title]
        ]
      ]
      #abstract-section(
        [Abstract], english.abstract, english.keywords, theme,
        english: true,
        above: theme.spacing.at("front-english-abstract-gap", default: 1.15em),
        factor: factor,
      )
    ]
  ]
  ]
}

#let working-paper(meta: (:), theme: themes.academic, options: (:), body) = context {
  let meta = normalize-meta(meta)
  let authors = normalize-authors(meta)
  let english = normalize-english(meta.english)
  let opts = normalize-working-options(options)
  let heading-numbering = if opts.numbering == none { numbering-presets.decimal } else { opts.numbering }
  let inline = opts.front-matter == "inline"
  let initial-footer = opts.page-numbering-start == "document" or inline
  let running-title = if meta.short-title == none { meta.title } else { meta.short-title }
  let document-authors = authors.map(author => metadata-string(author.name))
  let document-keywords = if meta.keywords == none {
    ()
  } else if type(meta.keywords) == array {
    meta.keywords.map(metadata-string)
  } else {
    (metadata-string(meta.keywords),)
  }

  set document(
    title: meta.title,
    author: document-authors,
    description: meta.abstract,
    keywords: document-keywords,
  )
  base-style(
    theme: theme,
    numbering: heading-numbering,
    draft-mode: opts.draft-mode,
    heading-mode: "paper",
  )[
    #if target() == "html" [
      #working-title(meta, authors, english, theme, density: opts.front-matter-density)
      #if opts.front-matter == "cover-toc" [#render-outline(theme, depth: opts.toc-depth)]
      #body
      #render-bibliography(opts.bibliography)
    ] else [
      #set page(
        paper: opts.paper,
        margin: opts.margin,
        header: if inline and opts.header { page-header(theme, left: running-title) } else { none },
        footer: if initial-footer { page-footer(theme) } else { none },
        background: draft-background(theme, opts.draft-mode),
      )
      #working-title(meta, authors, english, theme, density: opts.front-matter-density)
      #if opts.front-matter != "inline" [#pagebreak()]
      #if opts.front-matter == "cover-toc" [
        #render-outline(theme, depth: opts.toc-depth)
        #pagebreak()
      ]
      #if inline [
        #body
        #render-bibliography(opts.bibliography)
      ] else [
        #if opts.page-numbering-start == "body" [#counter(page).update(1)]
        #set page(
          header: if opts.header { page-header(theme, left: running-title) } else { none },
          footer: page-footer(theme),
        )
        #body
        #render-bibliography(opts.bibliography)
      ]
    ]
  ]
}
