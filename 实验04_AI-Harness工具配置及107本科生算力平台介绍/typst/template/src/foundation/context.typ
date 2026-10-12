// Context installed by document profiles and consumed by semantic components.

#let active-theme = state("personal-typst-kit-active-theme", none)
#let active-draft-mode = state("personal-typst-kit-draft-mode", "show")

#let activate-context(theme, draft-mode: "show") = {
  active-theme.update(theme)
  active-draft-mode.update(draft-mode)
}

#let special-heading-supplement = [personal-typst-kit-special-section]
