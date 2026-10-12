// Stable public facade. Internal src/ paths are not public API.

#import "src/profiles/paper.typ" as paper-module
#import "src/profiles/working-paper.typ" as working-paper-module
#import "src/profiles/book.typ" as book-module
#import "src/profiles/manual.typ" as manual-module
#import "src/profiles/handout.typ" as handout-module
#import "src/themes/themes.typ" as theme-module
#import "src/foundation/numbering.typ" as numbering-module
#import "src/components/callouts.typ" as callout-module
#import "src/components/media.typ" as media-module
#import "src/components/structure.typ" as structure-module
#import "src/extensions/manual.typ" as manual-extension
#import "src/extensions/handout.typ" as handout-extension
#import "src/extensions/draft.typ" as draft-extension
#import "src/extensions/working-paper.typ" as working-paper-extension

#let paper = paper-module.paper
#let working-paper = working-paper-module.working-paper
#let book = book-module.book
#let manual = manual-module.manual
#let handout = handout-module.handout

#let themes = theme-module.themes
#let densities = theme-module.densities
#let theme-with = theme-module.theme-with
#let numbering-presets = numbering-module.numbering-presets

#let callout = callout-module.callout
#let source-quote = callout-module.source-quote
#let figure-image = media-module.figure-image
#let figure-grid = media-module.figure-grid
#let code-block = structure-module.code-block
#let steps = structure-module.steps
#let cn-footnote = structure-module.cn-footnote
#let source-note = structure-module.source-note
#let special-section = structure-module.special-section

#let prerequisites = manual-extension.prerequisites
#let revision-history = manual-extension.revision-history
#let learning-objectives = handout-extension.learning-objectives
#let definition-box = handout-extension.definition-box
#let worked-example = handout-extension.worked-example
#let exercise = handout-extension.exercise
#let lesson-summary = handout-extension.lesson-summary
#let response-area = handout-extension.response-area
#let draft-note = draft-extension.draft-note
#let todo = draft-extension.todo

#let theorem = working-paper-extension.theorem
#let lemma = working-paper-extension.lemma
#let proposition = working-paper-extension.proposition
#let definition = working-paper-extension.definition
#let proof = working-paper-extension.proof
#let remark = working-paper-extension.remark
#let acknowledgements = working-paper-extension.acknowledgements
#let paper-table = working-paper-extension.paper-table
#let appendices = working-paper-extension.appendices
