#import "../foundation/config.typ": ensure-dictionary, reject-unknown

#let font-defaults = (
  body: (
    "Noto Serif SC",
  ),
  heading: (
    "Noto Sans SC",
  ),
  mono: (
    "DejaVu Sans Mono",
  ),
)

#let type-scale-defaults = (
  body: 11pt,
  small: 9pt,
  code: 9pt,
  title: 22pt,
  subtitle: 13pt,
  h1: 17pt,
  h2: 14pt,
  h3: 12pt,
)

#let spacing-defaults = (
  leading: 0.72em,
  paragraph-gap: 0.55em,
  block-gap: 0.8em,
  heading-1-above: 1.5em,
  heading-1-below: 0.9em,
  heading-2-above: 1em,
  heading-2-below: 0.5em,
  heading-3-above: 1em,
  heading-3-below: 0.5em,
  display-math-gap: 0.65em,
  figure-gap: 0.8em,
  caption-gap: 0.65em,
  bibliography-leading: 0.72em,
  bibliography-gap: 0.55em,
  list-gap: 0.35em,
  list-block-gap: 0.55em,
  footnote-leading: 0.62em,
  footnote-clearance: 1em,
  footnote-entry-gap: 0.3em,
  outline-title-above: 1em,
  outline-title-below: 0.75em,
  outline-entry-gap: 0.18em,
  front-top: 2.65em,
  front-subtitle-gap: 0.85em,
  front-authors-gap: 2em,
  front-author-row-gap: 1.35em,
  front-author-notes-gap: 1.05em,
  front-organization-gap: 1.05em,
  front-details-gap: 0.8em,
  front-version-gap: 0.9em,
  front-date-gap: 0.7em,
  front-abstract-gap: 2em,
  front-abstract-title-gap: 1em,
  front-keywords-gap: 0.9em,
  front-english-title-gap: 1.25em,
  front-english-abstract-gap: 1.15em,
  code-block-gap: 0.9em,
  code-block-inset: 0.9em,
  code-block-header-gap: 0.35em,
  paper-table-inset-x: 0.7em,
  paper-table-inset-y: 0.55em,
  paper-table-note-gap: 0.55em,
  radius: 3pt,
  line-width: 0.7pt,
)

#let densities = (
  compact: (
    leading: 0.62em,
    paragraph-gap: 0.38em,
    block-gap: 0.75em,
    heading-1-above: 1.55em,
    heading-1-below: 0.8em,
    heading-2-above: 1.05em,
    heading-2-below: 0.55em,
    heading-3-above: 0.9em,
    heading-3-below: 0.45em,
    display-math-gap: 0.65em,
    figure-gap: 0.9em,
    caption-gap: 0.6em,
    bibliography-leading: 0.64em,
    bibliography-gap: 0.35em,
    list-gap: 0.32em,
    list-block-gap: 0.4em,
    outline-entry-gap: 0.24em,
  ),
  normal: (
    leading: 0.72em,
    paragraph-gap: 0.62em,
    block-gap: 0.9em,
    heading-1-above: 1.8em,
    heading-1-below: 0.95em,
    heading-2-above: 1.25em,
    heading-2-below: 0.65em,
    heading-3-above: 1.05em,
    heading-3-below: 0.55em,
    display-math-gap: 0.8em,
    figure-gap: 1.1em,
    caption-gap: 0.7em,
    bibliography-leading: 0.7em,
    bibliography-gap: 0.5em,
    list-gap: 0.4em,
    list-block-gap: 0.5em,
    outline-entry-gap: 0.36em,
  ),
  relaxed: (
    leading: 0.82em,
    paragraph-gap: 0.82em,
    block-gap: 1.1em,
    heading-1-above: 2.2em,
    heading-1-below: 1.15em,
    heading-2-above: 1.55em,
    heading-2-below: 0.8em,
    heading-3-above: 1.25em,
    heading-3-below: 0.65em,
    display-math-gap: 0.95em,
    figure-gap: 1.4em,
    caption-gap: 0.8em,
    bibliography-leading: 0.78em,
    bibliography-gap: 0.65em,
    list-gap: 0.48em,
    list-block-gap: 0.65em,
    outline-entry-gap: 0.48em,
  ),
)

#let style-defaults = (
  link-underline: true,
  bibliography-justify: false,
  bibliography-link-underline: false,
)

#let semantic-colors = (
  text: rgb("#20242b"),
  muted: rgb("#667085"),
  line: rgb("#d0d5dd"),
  surface: rgb("#f6f7f9"),
  success: rgb("#2f855a"),
  success-soft: rgb("#edf8f1"),
  warning: rgb("#b7791f"),
  warning-soft: rgb("#fff8e8"),
  danger: rgb("#c2413c"),
  danger-soft: rgb("#fff1f0"),
)

#let make-theme(name, accent, accent-soft) = (
  name: name,
  colors: semantic-colors + (
    accent: accent,
    accent-soft: accent-soft,
    heading: accent,
    link: accent,
    bibliography-link: accent,
  ),
  fonts: font-defaults,
  type-scale: type-scale-defaults,
  spacing: spacing-defaults,
  styles: style-defaults,
)

#let themes = (
  teal: make-theme("teal", rgb("#307e86"), rgb("#edf7f7")),
  ink: make-theme("ink", rgb("#3f4858"), rgb("#f0f2f5")),
  warm: make-theme("warm", rgb("#a56532"), rgb("#fcf3e9")),
  blue: make-theme("blue", rgb("#2f6fa8"), rgb("#edf4fb")),
  academic: make-theme("academic", rgb("#7a1f2b"), rgb("#f8f3f4")) + (
    colors: semantic-colors + (
      accent: rgb("#7a1f2b"),
      accent-soft: rgb("#f8f3f4"),
      heading: rgb("#171717"),
      link: rgb("#7a1f2b"),
      bibliography-link: rgb("#5f4a4f"),
    ),
    fonts: (
      body: ("Noto Serif SC",),
      heading: ("Noto Serif SC",),
      mono: ("DejaVu Sans Mono",),
    ),
    type-scale: type-scale-defaults + (
      body: 11pt,
      title: 20pt,
      subtitle: 12pt,
      h1: 15pt,
      h2: 13pt,
      h3: 12pt,
    ),
    spacing: spacing-defaults + densities.relaxed + (
      footnote-leading: 0.7em,
      footnote-clearance: 1.2em,
      footnote-entry-gap: 0.42em,
      radius: 1.5pt,
      line-width: 0.55pt,
    ),
  ),
)

#let theme-with(
  base,
  colors: (:),
  fonts: (:),
  type-scale: (:),
  spacing: (:),
  styles: (:),
) = {
  ensure-dictionary("theme", base)
  reject-unknown("theme colors", colors, base.colors.keys())
  reject-unknown("theme fonts", fonts, base.fonts.keys())
  reject-unknown("theme type-scale", type-scale, base.type-scale.keys())
  reject-unknown("theme spacing", spacing, base.spacing.keys())
  let base-styles = base.at("styles", default: style-defaults)
  reject-unknown("theme styles", styles, base-styles.keys())
  base + (
    colors: base.colors + colors,
    fonts: base.fonts + fonts,
    type-scale: base.type-scale + type-scale,
    spacing: base.spacing + spacing,
    styles: base-styles + styles,
  )
}
