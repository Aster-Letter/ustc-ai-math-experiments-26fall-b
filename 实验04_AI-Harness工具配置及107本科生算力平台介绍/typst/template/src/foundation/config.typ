// Validation helpers used by all public constructors.

#let ensure-dictionary(name, value) = {
  assert(type(value) == dictionary, message: name + " must be a dictionary")
  none
}

#let reject-unknown(name, value, allowed) = {
  ensure-dictionary(name, value)
  for key in value.keys() {
    assert(allowed.contains(key), message: name + " contains unknown key: " + key)
  }
  none
}

#let merge-known(name, defaults, value) = {
  reject-unknown(name, value, defaults.keys())
  defaults + value
}

#let require-key(name, value, key) = {
  assert(value.keys().contains(key), message: name + "." + key + " is required")
  assert(value.at(key) != none, message: name + "." + key + " must not be none")
  none
}

#let validate-choice(name, value, choices) = {
  assert(choices.contains(value), message: name + " must be one of: " + choices.join(", "))
  none
}

#let meta-defaults = (
  title: none,
  subtitle: none,
  author: none,
  authors: none,
  date: none,
  organization: none,
  version: none,
  status: none,
  abstract: none,
  keywords: none,
  course: none,
  extra-lines: none,
  audience: none,
  short-title: none,
  english: none,
)

#let normalize-meta(meta) = {
  let result = merge-known("meta", meta-defaults, meta)
  require-key("meta", result, "title")
  result
}

#let common-option-defaults = (
  paper: "a4",
  margin: (top: 2.35cm, bottom: 2.25cm, left: 2.55cm, right: 2.55cm),
  toc: true,
  toc-depth: 3,
  numbering: none,
  draft-mode: "show",
  bibliography: none,
  cover: true,
)

#let normalize-options(name, defaults, options) = {
  let result = merge-known(name + " options", common-option-defaults + defaults, options)
  assert(type(result.toc) == bool, message: name + " options.toc must be bool")
  assert(type(result.toc-depth) == int and result.toc-depth >= 1, message: name + " options.toc-depth must be a positive integer")
  assert(type(result.cover) == bool, message: name + " options.cover must be bool")
  validate-choice(name + " options.draft-mode", result.draft-mode, ("show", "hide", "error"))
  result
}

#let normalize-bibliography(config) = {
  if config == none {
    none
  } else {
    let defaults = (
      sources: none,
      title: [参考文献],
      style: "gb-7714-2015-numeric",
      full: false,
      pagebreak: true,
    )
    let result = merge-known("bibliography", defaults, config)
    require-key("bibliography", result, "sources")
    assert(type(result.full) == bool, message: "bibliography.full must be bool")
    assert(type(result.pagebreak) == bool, message: "bibliography.pagebreak must be bool")
    result
  }
}
