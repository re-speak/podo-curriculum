# Curriculum and lesson creation workflow

This is the operating procedure for requests such as **create a curriculum**, **create a
course**, **create lessons**, **generate the remaining lessons**, or **write lessons from the
TOC**. It applies to all five Korean tracks. Read `AGENTS.md` and `ux-philosophy.md` first;
this document defines the production sequence and ownership boundaries.

The workflow is intentionally course-aware. A lesson is identified by:

```text
track + course code + lesson number
```

Never identify a lesson by number alone. Contextual Korean and free talking restart at 1 in
every course, so `3-contextual-korean / 1` names fourteen different episodes.

## Source hierarchy

When sources disagree, fix the higher source and regenerate the lower one:

1. `table-of-contents.md` — curriculum facts, course order, lesson outcomes and content
2. `lesson-blueprint.md` — the page arc and track-specific pedagogy
3. `trial/lessons/trial-N-*.html` — canonical voice, component composition and interaction rhythm
4. `toc/<course-code>/lesson-NNN.md` — generated, course-scoped writing packet
5. `courses/<course-code>/course.yaml` — generated deploy plan
6. `courses/<course-code>/lessons/<lesson-slug>/lesson.html` — authored lesson

Core patterns is the one legacy exception: its lesson numbers are globally unique and its
richer generated briefs remain at `toc/lesson-NNN.md`. The common brief command handles that
exception automatically.

## 1. Plan or change a curriculum

Write the curriculum in `table-of-contents.md` before writing decks. Every course needs a
stable romanized course code, level, three-language title, outcome and ordered lessons. Every
lesson needs a title, one observable outcome and the content that earns that outcome. A track
parser in `tools/track_parsers.py` must represent those fields without guessing.

For a narrative course, also write a small season bible in the TOC: work title, cast,
relationship state, setting and course-level dramatic movement. Each episode must state its
scene, learner lines, partner reactions, patterns and any continuity-changing note. A list of
grammar slots is not a narrative course plan.

Then generate and validate the course plan:

```sh
python3 korean/tools/plan_courses.py korean/tracks/<track>
python3 korean/tools/plan_courses.py --all --dry-run
```

`course.yaml` is generated. Do not hand-edit its course code, class level or planned lesson
comments; change the TOC/parser and rerun.

## 2. Generate textual lesson briefs

```sh
python3 korean/tools/build_lesson_briefs.py korean/tracks/<track>
# or, after a cross-curriculum change
python3 korean/tools/build_lesson_briefs.py --all
```

For course-numbered tracks this writes:

```text
tracks/<track>/toc/<course-code>/lesson-NNN.md
```

The brief repeats the course code, course context, exact lesson content and adjacent lessons.
Contextual briefs also carry the work, cast, learner line, partner reaction, nuance and story
continuity. Briefs are generated text: never hand-edit one. If a brief is weak or wrong, improve
the TOC or parser and regenerate it.

## 3. Prove one lesson before multiplying it

Choose a representative lesson and scaffold it with the exact course code:

```sh
python3 korean/tools/new_lesson.py \
  --track <track> \
  --course <course-code> \
  --lesson <number> \
  --id <NN-english-slug> \
  --title-ko "..." --title-ja "..." --title-en "..."
```

Before writing pages, read these in full and in order:

1. `ux-philosophy.md`
2. this workflow
3. the track blueprint
4. the generated brief for that exact course and lesson
5. the canonical trial deck named by the blueprint
6. `AUTHORING.md`

The trial deck is not optional and the sample deck is not its replacement. The blueprint gives
structure; the canonical trial carries the tutor's voice, believable distractors and activity
rhythm.

Validate this pilot at 480px before assigning a batch. If the curriculum introduces a new page
type or interaction, validate that shared design once in the pilot rather than letting multiple
lesson writers invent variants.

## 4. Run lesson production as an orchestrated writer workflow

For a batch, one orchestrator owns the shared truth and lesson writers own disjoint deck files.
This is the default workflow when sub-agents are available; it is also the ownership model when
humans split the work.

The orchestrator alone may change:

- TOCs, parsers, blueprints and generated briefs
- `runtime/`, `AUTHORING.md`, `ux-philosophy.md` and this workflow
- course plans, catalogs and shared `_conventions.md`
- the season bible and cross-lesson continuity ledger

Each writer receives one explicit assignment packet:

```text
track
course code
lesson number and output path
track blueprint
course-scoped textual brief
complete canonical trial deck
relevant shared conventions
```

Each writer edits only its assigned `lesson.html`. It must not alter runtime, the TOC,
blueprint, brief, course plan or another lesson. If shared infrastructure is missing, the writer
reports the need to the orchestrator instead of solving it locally.

Start with three structurally different lessons, review them, then expand the batch. For a
narrative course, review and integrate in episode order even if writers draft in parallel. The
orchestrator checks names, chronology, relationship state, callbacks and the teaser chain. Do
not fan out all episodes until the season bible and pilot have held up under review.

## 5. Authoring rules every writer checks

**A rule added here only reaches the writers who were told to read this file.** In practice a lesson
writer works from its track blueprint and the canonical trial deck, so a rule that exists only in this
document or in `ux-philosophy.md` will be followed by whichever track was being written when it was
added and silently missed by every other one. When you add or change a rule with a number in it,
mirror it into each track's `lesson-blueprint.md` — and check the canonical trial deck actually obeys
it, because that deck is what writers copy. Core Patterns spent 348 reorder sentences at three chips
for exactly this reason: the four-chunk rule was written during the Contextual batch, and Core's
blueprint and trial deck both said nothing about a count.

- One activity per page; Korean-first title; one blue tutor-script box.
- Keep the Contextual shell canonical instead of copying an older deck variant: open with
  `episode-card` → `scene` → `lesson-goal` → `expressions`; put the two exact target
  lines in `.known.lines > .known-row`; name the two open production pages `p1-write` and
  `p2-write`. The opening scene must already contain both target lines, and each `pN-teach`
  repeats its target verbatim in `.sent-hero` before adding examples in `.sent-more`.
  Before handing off, read the rendered episode card itself: its course label, episode number,
  title and cast must belong to the assigned course, not to the deck that supplied the markup.
- Keep `partN-intro` as a pacing and story bridge: pattern name plus one short Japanese line that
  moves from the scene into the next beat. Do not teach grammar on the dark transition page.
- Open `pN-teach` with one compact `.section-subtitle.pattern-meaning` box. Give the short meaning
  and communicative use in Korean, followed by its exact Japanese counterpart; the Korean tutor
  reads the Korean and can point the learner to the Japanese. Keep formation for the later rule page.
- Every closed sentence activity keeps four questions from read through translate; difficulty must
  not taper by silently dropping questions. Free-writing remains one open prompt.
- Reorder activities use four meaningful phrase chunks per sentence, with four as the ceiling and the
  working default. Three is fine when the sentence honestly holds three units; do not pad a sentence
  to reach four, and never reach four by splitting a compound noun, a particle off its noun or an
  ending off its stem. Do not stop short either — if a fourth unit is already in the sentence, give it
  its own chip rather than gluing it to a neighbour, and chunk every sentence on a page the same way.
  Present those chips in a genuinely scrambled source order; a row that already reads as its answer
  does no retrieval work even when its chunk count is correct.
- A spoken prompt that feeds one answer box asks one question. Two only when the second narrows the
  first (either/or, or a yes/no setting up the real question); never three, and never two unrelated
  questions joined with 그리고. Three answers wanted means three turns, not one crowded box.
- A visual rule page has one block per real formation branch, not one block per example. Keep one
  block for an invariant rule; compare two or three blocks only when the learner must distinguish
  those forms.
- When that one rule removes dictionary-form `다`, show the complete source form and its result
  (`듣다 → 듣기 싫어`), not an unexplained clipped stem (`듣 → 듣기 싫어`). Use a stem-only tile
  only when the stem's final sound is what determines a real formation branch. Group the dictionary
  form as one `.bt-word`; separate syllable tiles are visual evidence for sound-based branches.
- Build rule diagrams with the shared `.batchim` / `.bt-*` component and no lesson-specific widths.
  The rule card must align with the tutor-script column at both a 480px lesson column and a 360px
  narrow column; multiword results may wrap only at an authored space, never between Korean syllables.
- Include a choose page only for an honest, taught distinction. Omit it when one option is merely a
  fake ending or when both answers are grammatical and choosing requires an unintroduced nuance.
  When it exists, use the current `.choose-list > .choose-row.sentence` contract with two `.opt`
  elements, one `data-correct`, and row-level sync metadata; do not revive the old
  `.choice-rows` / `.choice-row` widget, which the shared activity runtime does not wire.
- A native tip adds one adjacent choice not already taught: register, softening, contraction,
  prosody, collocation or a useful difference in intensity. It is not a recap or a delayed core
  explanation. When both expressions are valid, show them with `.nuance-compare`: equal visual
  weight, a Korean/Japanese situation label on each, and `상황에 따라 / 場面で選ぶ` between them.
  Do not draw a correction arrow or frame the lesson expression as universally better.
- Contextual `p3-freetalk` is a reciprocal exchange, not a single student prompt: the tutor asks,
  the student answers, the student asks a related question, and the tutor gives a real personal
  answer in the gray editable `先生の答え` field. Do not end the page after the student's answer.
- The final teaser is a complete 5–7-turn mini-scene with 2–3 learner completions, uses both of
  today's patterns, advances the relationship or conflict, and ends on an unresolved hook. A
  receptive lesson may ask the learner to reconstruct the other speaker's lines.
- Use existing components and `data-sync` contracts from `AUTHORING.md`.
- Keep the required receptive → productive arc from the track blueprint.
- Show a short, consistent speaker name beside every avatar.
- Respect the deck's `podo:level`: `.yomi` only through 초중급.
- Use no inline CSS or JavaScript and do not change shared runtime from a lesson assignment.
- Give every page a unique `data-page-id` and every shared control a unique `data-sync-id`.
- Preserve enough bottom clearance that the fixed pager never makes content unreachable.

Scrolling is allowed. Split a long page only when its size creates another problem: the fixed
pager hides an unfinished task, the learner cannot tell the activity's scope, or one page asks
them to retain too many turns at once. Split dialogue at a meaningful dramatic beat, never at an
arbitrary height. Opening scene and replay must use the same beat boundaries.

For Contextual Korean specifically, the native tip comes before the final next-episode teaser.
Nothing follows the teaser; it is the last image the learner leaves with.

## 6. Verify each deck and the integrated course

Static checks:

- required `podo:*` and `notranslate` metadata
- lesson id equals its directory name
- all relative CSS/JS/image refs resolve
- unique page and sync ids
- no forbidden yomi, inline CSS/JS or accidental shared-runtime changes

Interactive checks at both a 480px lesson column and a 360px narrow column:

- every page is reachable and readable, including after scrolling
- choose/reorder/fill/write controls complete and reset correctly
- learner and tutor views stay in sync where required
- tutor notes and answer visibility are correct for each role
- no console errors and no pager overlap that makes content unreachable
- no page, dialogue turn or generated `.slot-input` widens its container; long answer fields wrap
  onto their own line inside the answer box

Use representative screenshots across the course, plus every new or unusually dense page. A
pass means more than “it scrolls”: the learner must understand what to do before the activity
disappears below the fold.

Finally regenerate plans and catalog after decks or TOCs change:

```sh
python3 korean/tools/plan_courses.py korean/tracks/<track>
python3 korean/tools/build_catalog.py
python3 korean/tools/check_runtime_drift.py
```

Only after the integrated course passes should it move through the production sync and
validation sequence documented in `AGENTS.md`.
