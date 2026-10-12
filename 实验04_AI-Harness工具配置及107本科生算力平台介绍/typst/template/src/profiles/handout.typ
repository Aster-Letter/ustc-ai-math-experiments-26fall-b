#import "../themes/themes.typ": themes
#import "../foundation/numbering.typ": numbering-presets
#import "../foundation/config.typ": normalize-meta, normalize-options, validate-choice
#import "../foundation/base.typ": base-style, render-outline, page-header, page-footer, draft-background, render-bibliography
#import "common.typ": handout-title

#let handout(meta: (:), theme: themes.warm, options: (:), body) = context {
  let meta = normalize-meta(meta)
  let opts = normalize-options("handout", (
    toc: false,
    header: true,
    title-style: "panel",
  ), options)
  assert(type(opts.header) == bool, message: "handout options.header must be bool")
  validate-choice("handout options.title-style", opts.title-style, ("panel", "compact"))
  let heading-numbering = if opts.numbering == none { numbering-presets.decimal } else { opts.numbering }
  set document(title: meta.title)
  base-style(
    theme: theme,
    numbering: heading-numbering,
    draft-mode: opts.draft-mode,
    heading-mode: "handout",
  )[
    #if target() == "html" [
      #handout-title(meta, theme, style: opts.title-style)
      #if opts.toc [#render-outline(theme, depth: opts.toc-depth)]
      #body
      #render-bibliography(opts.bibliography)
    ] else [
      #set page(
        paper: opts.paper,
        margin: opts.margin,
        header: if opts.header { page-header(theme, left: meta.course, right: meta.title) } else { none },
        footer: page-footer(theme),
        background: draft-background(theme, opts.draft-mode),
      )
      #handout-title(meta, theme, style: opts.title-style)
      #if opts.toc [#pagebreak()#render-outline(theme, depth: opts.toc-depth)#pagebreak()]
      #body
      #render-bibliography(opts.bibliography)
    ]
  ]
}
