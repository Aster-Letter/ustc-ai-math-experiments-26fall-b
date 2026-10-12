#import "../themes/themes.typ": themes
#import "../foundation/numbering.typ": numbering-presets
#import "../foundation/config.typ": normalize-meta, normalize-options
#import "../foundation/base.typ": base-style, render-outline, page-header, page-footer, draft-background, render-bibliography
#import "common.typ": book-title

#let book(meta: (:), theme: themes.teal, options: (:), body) = context {
  let meta = normalize-meta(meta)
  let opts = normalize-options("book", (
    preface: none,
    chapter-label: [Chapter],
    front-numbering: "i",
    body-numbering: "1",
    header: true,
  ), options)
  assert(type(opts.header) == bool, message: "book options.header must be bool")
  let heading-numbering = if opts.numbering == none { numbering-presets.chapter } else { opts.numbering }
  set document(title: meta.title)
  base-style(
    theme: theme,
    numbering: heading-numbering,
    draft-mode: opts.draft-mode,
    heading-mode: "book",
    chapter-label: opts.chapter-label,
  )[
    #if target() == "html" [
      #book-title(meta, theme)
      #if opts.preface != none [#heading(numbering: none)[前言]#opts.preface]
      #if opts.toc [#render-outline(theme, depth: opts.toc-depth)]
      #body
      #render-bibliography(opts.bibliography)
    ] else [
      #set page(
        paper: opts.paper,
        margin: opts.margin,
        header: none,
        footer: none,
        background: draft-background(theme, opts.draft-mode),
      )
      #if opts.cover [#book-title(meta, theme)#pagebreak()]
      #counter(page).update(1)
      #set page(
        header: if opts.header { page-header(theme, left: meta.title, right: meta.subtitle) } else { none },
        footer: page-footer(theme, numbering-style: opts.front-numbering),
      )
      #if opts.preface != none [
        #heading(numbering: none)[前言]
        #opts.preface
        #pagebreak()
      ]
      #if opts.toc [#render-outline(theme, depth: opts.toc-depth)#pagebreak()]
      #counter(page).update(1)
      #set page(footer: page-footer(theme, numbering-style: opts.body-numbering))
      #body
      #render-bibliography(opts.bibliography)
    ]
  ]
}
