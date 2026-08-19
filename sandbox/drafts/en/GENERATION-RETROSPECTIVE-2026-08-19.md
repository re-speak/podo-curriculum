# English generation quality retrospective — 2026-08-19

## What failed

The first generated Core batch was structurally repeatable but pedagogically incomplete. Several
pages repeated models without creating a learning decision, reorder activities exposed punctuation
or weak chunking, some repeated inputs visually collapsed together, teaching pages did not use the
canonical main-pattern and example components, choices sometimes repeated whole sentences instead
of isolating the decision, and a generic vocabulary list occupied the native-tip slot.

## Why it failed

1. **Two production paths existed.** CORE-12 eventually received a canonical hand-authored page
   sequence; CORE-13–24 still used a generic fallback. The fallback rendered the same shell but did
   not own the same pedagogy.
2. **The generator data stopped at language examples.** It stored model rows, prose rules and two
   extra expressions, but not the semantic decisions needed for meaning/use, smallest-unit choices,
   formation diagrams or adjacent native use. The template filled those gaps with generic content.
3. **Tests answered the wrong question.** Exact-generation tests proved that checked-in HTML
   matched generator output. They could reproduce a bad template perfectly. Early static checks
   validated counts, markup and interaction solvability but not the canonical Core page contract.
4. **“Proofread” had no enforceable evidence boundary.** Generation, checker repair and owner links
   were treated as separable steps. A structurally clean deck could be shown before page-by-page
   semantic and rendered review had finished.
5. **Repairs followed symptoms.** A reported page triggered a local rule, but the same defect class
   was not immediately searched across every generator-owned deck. The first choice repair repeated
   whole sentences even though the written standard already required the smallest meaningful unit;
   the component choice itself was not being checked.

## Controls added

- All generated Core lessons now use one canonical production arc. There is no generic pedagogical
  fallback.
- Generator data explicitly owns both meaning/use statements, both four-row smallest-unit choice
  sets, both visual rule specifications and one real native-use comparison per lesson.
- `podo:proofread-status=complete` is emitted only for the canonical path.
- The checker requires canonical teaching blocks, visual rules, a final native-tip component,
  smallest-unit choice markup, honest and solvable reorder chunks, canonical editable-field
  structure, and repeated-row spacing.
- A smallest-unit regression rejects sentence-ending punctuation or more than three lexical words
  inside a compact word-choice option. Human proofreading still judges whether the surviving unit
  is the right pedagogical contrast.
- Generation and proofreading are one uninterrupted step. Owner-review links come only after
  semantic review, exact-generation tests, static checks and 360px/480px rendered QA on the same
  bytes.
- The generated-corpus test enumerates all 29 generator-owned decks across Core, Contextual and
  Freetalking and requires zero checker errors and zero warnings.

## Audit performed

- 12 generated Core decks were regenerated from explicit canonical specifications.
- 5 generated Contextual decks were refreshed to the newer canonical teaching components already
  present in their generator.
- 12 generated paired Freetalking decks were verified byte-for-byte against their generator.
- All 43 current English decks, including the 29 generator-owned decks and approved/manual peers,
  passed the static checker and were rendered page by page at 360px and 480px with no overflow,
  collapsed repeated-input spacing or pager-clearance failures.

The remaining non-algorithmic risk is the quality of the pedagogical judgment itself: whether a
contrast is worth teaching, a distractor is believable, a dialogue is natural, or a tip is useful.
That remains a human page-by-page proofreading responsibility and cannot be inferred from valid
HTML or a passing generator test.
