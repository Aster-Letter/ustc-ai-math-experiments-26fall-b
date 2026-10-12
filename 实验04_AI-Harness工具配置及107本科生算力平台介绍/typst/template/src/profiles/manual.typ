#import "../themes/themes.typ": themes
#import "../foundation/numbering.typ": numbering-presets
#import "../foundation/config.typ": normalize-meta, normalize-options
#import "../foundation/base.typ": base-style, render-outline, page-header, page-footer, draft-background, render-bibliography
#import "common.typ": manual-title

#let manual(meta: (:), theme: themes.blue, options: (:), body) = context {
  let meta = normalize-meta(meta)
  let opts = normalize-options("manual", (
    revision-history: none,
    header: true,
  ), options)
  assert(type(opts.header) == bool, message: "manual options.header must be bool")
  let heading-numbering = if opts.numbering == none { numbering-presets.decimal } else { opts.numbering }
  set document(title: meta.title)
  base-style(
    theme: theme,
    numbering: heading-numbering,
    draft-mode: opts.draft-mode,
    heading-mode: "manual",
  )[
    #if target() == "html" [
      #manual-title(meta, theme)
      #if opts.revision-history != none [#opts.revision-history]
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
      #if opts.cover [#manual-title(meta, theme)#pagebreak()]
      #counter(page).update(1)
      #set page(
        header: if opts.header { page-header(theme, left: meta.title, right: meta.version) } else { none },
        footer: page-footer(theme),
      )
      #if opts.revision-history != none [#opts.revision-history#pagebreak()]
      #if opts.toc [#render-outline(theme, depth: opts.toc-depth)#pagebreak()]
      #body
      #render-bibliography(opts.bibliography)
    ]
  ]
}
