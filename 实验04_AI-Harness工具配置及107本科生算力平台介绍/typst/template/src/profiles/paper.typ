#import "../themes/themes.typ": themes
#import "../foundation/numbering.typ": numbering-presets
#import "../foundation/config.typ": normalize-meta, normalize-options, validate-choice
#import "../foundation/base.typ": base-style, render-outline, page-header, page-footer, draft-background, render-bibliography
#import "common.typ": paper-title, abstract-block

#let paper(meta: (:), theme: themes.teal, options: (:), body) = context {
  let meta = normalize-meta(meta)
  let opts = normalize-options("paper", (
    page-numbering-start: "body",
    header: true,
  ), options)
  validate-choice("paper options.page-numbering-start", opts.page-numbering-start, ("document", "toc", "body"))
  assert(type(opts.header) == bool, message: "paper options.header must be bool")
  let heading-numbering = if opts.numbering == none { numbering-presets.cjk-paper } else { opts.numbering }

  set document(title: meta.title)
  base-style(
    theme: theme,
    numbering: heading-numbering,
    draft-mode: opts.draft-mode,
    heading-mode: "paper",
  )[
    #if target() == "html" [
      #paper-title(meta, theme)
      #if meta.abstract != none [#v(1em)#abstract-block(meta, theme)]
      #if opts.toc [#render-outline(theme, depth: opts.toc-depth)]
      #body
      #render-bibliography(opts.bibliography)
    ] else [
      #let main-header = if opts.header { page-header(theme, left: meta.title, right: meta.course) } else { none }
      #let numbered-from-cover = opts.page-numbering-start == "document"
      #set page(
        paper: opts.paper,
        margin: opts.margin,
        header: none,
        footer: if numbered-from-cover { page-footer(theme) } else { none },
        background: draft-background(theme, opts.draft-mode),
      )
      #if opts.cover [
        #paper-title(meta, theme)
        #if meta.abstract != none [#v(1.25em)#abstract-block(meta, theme)]
        #pagebreak()
      ]
      #set page(header: main-header)
      #if opts.toc [
        #if opts.page-numbering-start == "toc" [
          #counter(page).update(1)
        ]
        #set page(footer: if opts.page-numbering-start == "body" { none } else { page-footer(theme) })
        #render-outline(theme, depth: opts.toc-depth)
        #pagebreak()
      ]
      #if opts.page-numbering-start == "body" or (opts.page-numbering-start == "toc" and not opts.toc) [
        #counter(page).update(1)
      ]
      #set page(footer: page-footer(theme))
      #body
      #render-bibliography(opts.bibliography)
    ]
  ]
}
