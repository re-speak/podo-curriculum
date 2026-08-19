# Core English Patterns — the page arc of one lesson

**This document is not a table of contents; it is a map.** It records which pages come in what
order and what each page is for. Do not copy markup or tone from here — take those from the
canonical deck.

- **Canonical deck (source of truth):**
  [`courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html`](./courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html)
  — the approved Core 20 pilot. The course directory remains provisional until product course
  planning lands; the deck's component composition and tutor voice are canonical now.
- **What goes in this lesson:** the generated stable-id brief in [`toc/`](./toc/). It carries the
  authoritative TOC entry, adjacent lessons and already-learned/not-yet guardrails. Fix the TOC or
  parser and regenerate; never hand-edit the brief.
- **Component markup:** [`../../../korean/AUTHORING.md`](../../../korean/AUTHORING.md) §2–§3.
- **What may be a pattern at all:** [`../../reference/teaching-philosophy.md`](../../reference/teaching-philosophy.md) §4.

Read this map, then read the canonical deck **in full**. Do not skip it — the page structure
transfers through this document, but the tutor's voice, the instinct for which wrong answer is
worth offering, and the rhythm of the example sentences do not. Those decide the lesson's quality.

---

## The skeleton

One lesson = **2 opening pages + 2 pattern parts + 1 merge part + 2 closing pages.** About 26–28
pages.

| # | `data-page-id` | What it is for |
| ---: | --- | --- |
| 1 | `lesson-goal` | Show, whole, the conversation the learner will be able to have by the end |
| 2 | `words-you-know` | Start from what they already have — see the note below, it is different here |
| 3–11 | `part1-*` | Pattern A — the ladder below |
| 12–20 | `part2-*` | Pattern B — the same ladder |
| 21–24 | `part3-*` | The two patterns meet in one scene |
| 25 | `in-the-wild` | The same patterns dropped into a place the lesson has not been |
| 26 | `native-tip` | One thing a fluent speaker actually does — not new grammar |

The first surviving page (`lesson-goal`) carries `data-act` directly. There is no `cover` page on a
track lesson; sales pages belong to trial decks only.

### `words-you-know` is doing a second job in English

For a Korean deck this page is pure motivation: *look how much you already have.* For a Japanese
speaker learning English it is also the first honest look at **katakana loanwords** — `コーヒー`,
`チケット`, `レストラン`. The learner genuinely knows the meanings, which is the motivation half,
and that is worth using.

Handle it carefully:

- The page's job is still **recognition and motivation**, not correction. Show the English words and
  let the learner notice they already know them.
- It is fine — and useful — for the tutor's spoken line to say the English aloud and invite the
  learner to hear the difference. It is **not** fine to turn the page into a pronunciation drill, or
  to print katakana next to the English as if it were a reading. See `AGENTS.md`: kana over English
  installs the error rather than scaffolding the word.
- Keep it to three or four rows. Korean measured six and the last one fell under the pager while the
  tutor's line still promised it.
- **Six full-width glyphs per source word is the ceiling.** The bridge sets both columns at 26px in
  a 155px column, which carries six — `スーツケース` fits, `コンピューター` and `スマートフォン`
  (seven) wrap and make that row taller than its neighbours. A loanword bridge almost always has a
  shorter candidate, so prefer one; but if the seven-glyph word is the *right* example, take the
  wrap rather than losing it. This is a content constraint, not a runtime branch — both languages
  share one type scale and there is no English-only class to reach for.

---

## The pattern ladder — `part1` and `part2` use the same one

**Receive → recognize → produce.** This order *is* the teaching design of this track. You may drop a
rung, but **never reorder or skip forward** — each page assumes the one before it is already in the
learner's mouth, and the later pages take the model sentence off the screen.

| `data-page-id` | Component | What it does | Model on screen |
| --- | --- | --- | :---: |
| `partN-intro` | `.transition-page` | Pattern name + one Japanese line bridging from the scene. **No grammar here** | — |
| `pN-teach` | `.section-subtitle.pattern-meaning` + `.sent-hero` + `.sent-more` | **Meaning and use first**, then the sentence whole. The tutor reads it | yes |
| `pN-read` | `.model-line` ×4 | The learner reads alone. Model still on screen | yes |
| `pN-rule` | `.batchim` / `.bt-*` diagram | **One** form rule. This is the only grammar-explanation page in the part | — |
| `pN-choose` | `.choose-row` + `.opt` | Two-way choice — the last rung of recognizing | yes |
| `pN-reorder` | `.task-block` ×4 + `.answer-box small` | Chips into order. **Four meaning chunks per sentence** | no |
| `pN-fill` | `.task-block` + `.answer-box` | Blank — only the pattern slot is empty | no |
| `pN-translate` | `.task-block` + `.answer-box` | Japanese prompt → English. Hints are vocabulary only | no |
| `pN-write` | `.task-block` + `.answer-box tall` | Their own sentence. The first page with no right answer | no |

If a part carries a second form (a question form, a negative), insert another `teach` + `read` pair
at that point — `pN-question-teach` / `pN-question-read`. The ladder itself does not change.

### `pN-teach` opens with meaning and use, never with formation

Put a `.pattern-meaning` box at the top of the blue script area with a
`意味・使い方` kicker. Its English tutor line is **one short conversational sentence** combining
what the frame does with when a speaker reaches for it; the Japanese line is its direct one-sentence
counterpart. Do not add “Listen,” “Repeat,” or another activity direction here—the model directly
below already makes the next action visible. Never put Japanese or a lesson number in the English
line, and never refer to another lesson number in learner- or tutor-facing copy.

Formation does not go here — that is `pN-rule`'s job. Korean learned this the expensive way: without
this box, "when do I use it" has nowhere to live, drifts into the rule page, and the rule page can
only draw a form. The learner ends up with a diagram they cannot act on.

### `pN-rule` — one block per real branch, and English will hit the three-branch wall

A rule page draws **one block per genuine formation branch**, not one block per example. One block
for an invariant rule; two or three only when the learner must actually distinguish them.

If the content is a small set of lexical mappings such as `buy → bought`, it is not a branch
diagram at all. Show every pair at equal weight in an `.irregular-pair-grid`; do not promote the
first pairs into a large outcome band and leave the others looking like secondary examples.

The spoken line does not recite the branches or examples already visible in the diagram. Point to
the diagram and add only the one thing it cannot show. If the diagram already makes the action
obvious, keep the script to the natural prompt that gets the learner using it.

English has plenty of honest two-branch rules that fit the existing `.batchim` component:
`do / does`, `is / are`, `a / an`, `some / any`, `much / many`.

**It also has three-branch rules the component cannot draw** — `do / does / did`, `a / an / the`,
`-s / -es / -ies`. Korean hit exactly this wall four times independently and documented it: `.batchim`
is single-column and three boxes overflow the page. Every Korean deck that met it shipped an honest
two-box split and kept the third case out of learner-produced language.

**Do the same, and report it.** Do not compress three cases into two boxes with a misleading tile —
a wrong branch teaches a wrong structure, which is worse than no diagram. Record the gap in
[`../_conventions.md`](../_conventions.md) § runtime queue. This is a component limit that will
generate a different missing piece in every lesson that meets it, and the fix is one human decision
about the runtime, not something a lesson writer works around.

### The counting rules

These are not style preferences; each one was paid for on the Korean side — and the first two
below were paid for again by this track's own pilot, because they were not written here yet.

- **The tutor script box has the same number of sentences on both sides.** `script-lines.js`
  rebuilds the blue box as one sentence per line, each with its own translation underneath, but
  **only when the counts match**; when they differ it deliberately does nothing rather than pair
  the wrong translation to the wrong line. So a mismatch does not error — it just renders as a
  block of bunched prose. Write the English, then write exactly that many Japanese sentences.
  `.pattern-meaning` is exempt (it owns its own pairing), so keep *its* text short instead.
- **Conversational brevity is part of correctness.** Say only the learner's next action or the
  meaning the page must supply. Do not narrate visible setup, preview later activities, or pad a
  goal with `Today we'll...` / `By the end of the lesson...`. Rewrite the Japanese to preserve the
  shorter English line's meaning, sentence count and tone.
- **Tutor-only notes are English and appear only when the tutor must catch or do something the
  page cannot make obvious.** Put them on the production page where that action happens, not on a
  teaching page that produces nothing yet. Do not repeat an answer already revealed by teaching
  mode.
- **Mirror target highlights in every teaching and read model.** In `.sent-hero`, `.sent-more`, and
  `.model-line`, wrap each English target word or phrase in `.ending` and wrap its exact Japanese
  meaning in `.ending` too. The two languages must identify the same learning target; never leave
  only the support-language cue highlighted or highlight an entire sentence around a smaller target.
- **Use highlights according to the learner's job.** On `pN-fill`, wrap only the Japanese segment
  represented by the English blank in `class="target ending"`. On `pN-reorder` and
  `pN-translate`, leave the Japanese prompt neutral because the learner is producing the whole
  sentence rather than retrieving one marked form. On `p3-complete`, `.target` marks exactly the
  missing learner segment. Do not apply highlights decoratively or to every occurrence of a pattern.

- **Four questions in every closed activity** — read, choose, reorder, fill, translate. Difficulty
  must not taper by silently dropping questions. Free-writing stays one open prompt.
- **Four meaning chunks per reorder sentence**, ceiling and working default. Three is fine when the
  sentence honestly holds three. Never reach four by splitting a compound noun, an article off its
  noun, an auxiliary off its verb, or an inflection off its stem — and never stop at three when a
  fourth unit is already in the sentence and got glued to a neighbour. Chunk every sentence on a
  page the same way.
- **One blank answers one question.** Two prompts only when the second narrows the first. Three is
  never allowed, and neither is joining two unrelated questions with "and". If the scene wants three
  answers, give it three turns. Turns are cheap; working memory at A1 is not.
- **A question the page asks must be answered by the model.** A learner stalls in front of a
  question that has no landing place.
- **Blank only the pattern.** Every other word the learner needs is given. Hint chips are
  `JP:EN` vocabulary only — never articles, auxiliaries or inflections.
- Declare each content word as new, recycled, assumed-known or receptive-only in deck metadata.
  Core normally adds no more than eight; every hint-chip English value must be declared.
- **Omit `pN-choose` when there is no honest binary.** Do not manufacture a wrong form for an
  invariant pattern, and do not offer two grammatical options whose difference needs a nuance
  lecture the lesson has not given.
- **Put the choice at the smallest meaningful unit.** When only one or two target words differ,
  show the sentence once and put an independent two-way `.word-choice` group at each target. Do
  not repeat two full-sentence pills and make the learner reread identical surrounding language.
  Full-sentence options are for alternatives whose meaning or structure genuinely differs across
  the whole sentence. Several word groups still form one choose activity, not several activities.
- **Mark the Japanese cue for every word-level choice.** In a `.word-choice-card`, wrap the exact
  Japanese word or short phrase corresponding to each English choice group in `.ending`. Two
  English choice groups require two Japanese cues. Keep both English options neutral until the
  learner chooses; the support-language highlight locates the decision without revealing it.

---

## The merge — `part3`

Where the two patterns **call for each other** in one scene. Pattern B must be needed *because*
Pattern A was used — question and answer, request and response, problem and repair.

| `data-page-id` | Component | What it does |
| --- | --- | --- |
| `part3-intro` | `.transition-page` | Opens the scene |
| `p3-model` | `.dialogue` | The finished exchange. Tutor takes one role, learner the other |
| `p3-complete` | `.dialogue` + `.answer-box` | Same exchange, the learner's lines empty |
| `p3-freetalk` | `.dialogue` + `.answer-box small` | The same scene with their own facts |

`p3-model` is a real exchange, not two target lines joined by a generic reaction. It needs an
opening, an answer-dependent follow-up and a resolved ending. In `p3-complete`, preserve the exact
same turn sequence—including the opening question and closing reaction—and replace only the
learner's lines with answer fields. If the completion starts with a learner blank but the model
starts with the partner, the activity is incomplete.

Use **5–7 turns** as the working range for `p3-model` and its exact `p3-complete` replay. Five is
enough only when the exchange still has an opening, an answer-dependent follow-up and a resolved
ending. Do not pad a complete four-turn exchange with empty reactions just to reach the range;
rewrite it into a real exchange whose turns create a reason for the learner's next line.

Model and completion dialogues use profile images for both scene characters, matching Korean Core.
Reserve generic person icons for live `Tutor` / `Me` free-talk where the actual participants are the
people in class. Keep the speaker names short and identical across model and completion.

The input type follows the **learning job**, not the visual length of the answer. The Korean Core
ladder has three distinct levels, and English follows the same progression:

- In early controlled practice (`pN-fill`), keep all non-target English visible and use a
  single-line `.slot-input` for the target word or short target chunk.
- In late controlled production (`p3-complete` and `in-the-wild`), the missing segment normally
  includes both the target pattern and the content that slots into it: for example,
  `went to a restaurant`, not only `went`, and not automatically the entire sentence. Keep the
  surrounding conversational setup visible. Use one wrapping, auto-growing
  `textarea.free-input.phrase-input` for each meaningful production phrase; it may contain a whole
  utterance only when that utterance is itself the smallest honest production unit.
- Use the full-width open `.answer-space` + `.free-input` for genuinely open or whole-utterance work:
  `pN-translate`, free production, and an ask-back line taught as one complete question.

Do not shrink a late production blank to grammar atoms merely to make the field fit, and do not
make the learner recreate unrelated fixed language merely because one expected answer exists. The
phrase field is designed to reach the card edge, wrap internally, and grow vertically.

Mirror target highlighting across languages. In `p3-model`, each highlighted English target has a
matching `.ending` around its direct Japanese meaning. In `p3-complete`, put `.target` around the
specific Japanese word or phrase the learner is retrieving; do not highlight the whole translation
when only one or two forms carry the learning target.

`p3-freetalk` follows the Korean Core handoff from controlled practice to real information. It must
include: a real-fact tutor question, a usable target-language sentence scaffold with a Japanese
`.task`, a compact set of relevant hint chips, an ask-back line, and a field for the tutor's real
answer. If an answer-dependent follow-up is needed to make it a conversation, give the tutor one
short operational note to ask about a detail the learner actually mentioned. Never substitute a
generic label such as “Use both patterns” for the scaffold the learner needs to speak.

`in-the-wild` puts the same patterns in a **different** place to check transfer — the scene assigned
to this lesson in [`../_conventions.md`](../_conventions.md), never one you pick yourself and never
a room already used in this lesson's own dialogue. It is a roleplay between scene characters, so
use profile images for both roles just as in `p3-model` and `p3-complete`. Generic `Tutor` / `Me`
icons remain exclusive to live `p3-freetalk`.

`native-tip` is **one** adjacent thing a fluent speaker does: a contraction, a softener, a stress
shift, a collocation. Not new grammar, not a recap. Teach contractions here and alongside full forms
throughout — not months later as "native speed." When both options are genuinely valid, show them at
equal weight with situation labels; a correction arrow would turn a contextual choice into a
right/wrong rule.

---

## Two things that read wrong in a brief

**The "not yet" constraint binds the learner, not the tutor.** The tutor's spoken
`.section-subtitle` is natural English and may contain forms this lesson has not taught. Pushing the
syllabus into tutor speech makes the English stilted, and that is worse. The constraint applies to
what the learner is asked to *produce*.

**A rule diagram is not only for sound-based rules.** When a choice is decided by something other
than form — `some` vs `any` is decided by the sentence being a question or a negative, not by the
following word — drop the letter tile and the arrow and keep the outcome boxes alone. Forcing a
letter tile onto a non-phonological rule sends the learner hunting for a sound rule that isn't there.

---

## What this track does not do

- **It does not teach a grammar name first.** The learner borrows a whole sentence from a scene and
  changes the slot. One `pN-rule` page is the entire form explanation, and even that is an
  *understanding* target, not a speaking one.
- **It does not use language it has not taught in learner-produced English.**
- **It does not leave the model sentence up past `reorder`.** From that rung down it comes off the
  screen.
- **It does not put two activities on one page.** One page, one activity.
- **It carries no katakana over English and does not load `yomi.js`.** See `AGENTS.md`.
