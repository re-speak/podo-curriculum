# Curriculum and lesson creation workflow

This is the operating procedure for requests such as **create a curriculum**, **create a course**,
**create lessons**, **generate the remaining lessons**, or **write lessons from the TOC**. It
applies to the three production-facing English tracks; pronunciation remains planning-only. Read [`AGENTS.md`](./AGENTS.md) and
[`../ux-philosophy.md`](../ux-philosophy.md) first; this document defines the
production sequence and ownership boundaries.

Before review or batch generation, also apply
[`reference/pilot-feedback-release-checklist.md`](./reference/pilot-feedback-release-checklist.md).
It is the regression checklist distilled from pilot feedback across all three tracks; the track
blueprints remain authoritative for page-by-page construction.

**Read [`BUILD-PLAN.md`](./BUILD-PLAN.md) before proposing any batch.** Native catalog review is
complete, but representative-lesson and product gates still control what may scale. Do not treat
the presence of parsers, briefs or a skeleton generator as permission to cross those gates.

The workflow is course-aware. A lesson is identified by:

```text
track + course code + lesson number
```

**Never identify a lesson by number alone.** Use the stable TOC/review id (`CORE-31`, `CTX-32`,
`FT-107`) in briefs and feedback, and the deck slug inside a course. All current TOCs happen to use
global numbers, but deployable course boundaries are still undecided and must not be inferred from
those numbers.

## Source hierarchy

When sources disagree, fix the higher source and regenerate the lower one:

1. `tracks/<track>/table-of-contents.md` — curriculum facts, course order, lesson outcomes, content
2. `tracks/<track>/lesson-blueprint.md` — the page arc and track-specific pedagogy
3. the track's canonical deck — voice, component composition, interaction rhythm
4. `tracks/<track>/toc/<REVIEW-ID>.md` — generated writing packet
5. `courses/<course-code>/course.yaml` — generated deploy plan **[not built]**
6. `courses/<course-code>/lessons/<slug>/lesson.html` — the authored lesson

The `reference/` folder sits above all of this for questions of *scope and level*:
`curriculum-source-hierarchy.md` decides what is authoritative when sources disagree about whether
an item belongs at a level, and `teaching-philosophy.md` decides whether a candidate frame is
allowed to be a pattern at all. Neither is negotiable from inside a lesson assignment.

## 1. Plan or change a curriculum

Write the curriculum in `table-of-contents.md` before writing decks. Every course needs a stable
course code, level band, title, outcome and ordered lessons. Every lesson needs a title, one
observable can-do and the content that earns it.

**Every pattern must pass the level-sensitive test** in `reference/teaching-philosophy.md` §4:
stable purpose, retrievable fixed language, clear boundaries, four natural completions, transfer,
appropriate load, readiness. A frame that is mostly slots (`My ___ was ___ yesterday.`) is a
grammar formula, not a pattern, and the philosophy rejects it by name.

For a **contextual course**, state the practical area, learner need, level band, entry floor, and
coverage boundary. Each lesson states a self-contained who/where/what scene, learner lines, partner
reactions, and patterns. Course order may raise language load, but no lesson may require a cast,
plot event, or relationship state from another lesson. *A list of grammar slots is not a practical
course plan; a list of situations with no coverage logic is not one either.*

Then generate and validate the course plan:

```sh
# [not built] — BUILD-PLAN.md → T4.4
python3 english/tools/plan_courses.py english/tracks/<track>
```

Until it exists, a "course" is whatever the TOC says it is, and no deploy plan is produced.

## 2. Generate textual lesson briefs

```sh
python3 english/tools/build_lesson_briefs.py <track-name>
# or regenerate all four tracks
python3 english/tools/build_lesson_briefs.py --all
```

The brief repeats the exact source content, adjacent lessons and sequence guardrails. Core gets
explicit **already learned** and **not yet** ranges; Contextual gets its productive floor, pattern
ownership and chunk treatment; Freetalking gets its retrieval-only constraint. The negative half
is load-bearing: it stops a writer quietly teaching future grammar inside an earlier deck.

Briefs are generated text: **never hand-edit one.** If a brief is weak or wrong, improve the TOC or
the parser and regenerate.

## 3. Prove one lesson before multiplying it

```sh
python3 english/tools/new_lesson.py --track <track> --review-id <CORE-N|CTX-N|FT-N> \
  --course <course-code> --lesson <n> --id <NN-slug> --title <title> --level <level>
```

The tool lifts the shell from an approved English canonical deck, removes its pages and identity
comments, retargets metadata and shared paths, checks references, and refuses to overwrite. Core
defaults to its approved pilot. Contextual and Freetalking deliberately require `--from-deck`
until their own pilots are explicitly approved. **Never use a Korean deck** — its script list loads
`yomi.js`, which English must not.

Before writing pages, read these in full and in order:

1. `../ux-philosophy.md`
2. `AGENTS.md`, including the *English deltas* table
3. this workflow
4. the track blueprint
5. the brief (or the TOC entry, per step 2)
6. the canonical deck named by the blueprint
7. `tracks/_conventions.md`
8. `reference/running-lexicon.md`

**The canonical deck is not optional.** The blueprint gives structure; the deck carries the tutor's
voice, believable distractors and activity rhythm. A lesson written from the blueprint alone comes
out correctly shaped and lifeless.

Validate the pilot at **480px and 360px** before assigning a batch. If the lesson introduces a new
page type or interaction, validate that shared design once in the pilot rather than letting
multiple writers invent variants.

### The gate

**The first English deck in any track is a pilot and stops for explicit user approval.** Structural
checks never approve a pilot. If it is rejected, rewrite and re-review; do not use a rejected pilot
as a template. After approval, write **three structurally different lessons**, review those, and
only then expand.

## 4. Run lesson production as an orchestrated writer workflow

For a batch, one orchestrator owns the shared truth and lesson writers own disjoint deck files.

The **orchestrator alone** may change:

- TOCs, parsers, blueprints and generated briefs
- the runtime, `AGENTS.md`, `ux-philosophy.md` and this workflow
- course plans, catalogs and `tracks/_conventions.md`
- practical course coverage, scene allocation, and the cross-lesson duplication ledger

Each **writer** receives one explicit assignment packet:

```text
track · course code · lesson number and output path
required read path: ../ux-philosophy.md · AGENTS.md · LESSON-CREATION-WORKFLOW.md
track blueprint
the brief (or TOC entry + constructed "not yet" list)
the complete canonical deck
relevant shared conventions, including the assigned scene
```

Each writer edits only its assigned `lesson.html`. It must not alter the runtime, the TOC, the
blueprint, the brief, the course plan or another lesson. **If shared infrastructure is missing, the
writer reports the need to the orchestrator instead of solving it locally.**

For a contextual course, review and integrate **in course order** even if writers draft in
parallel. The orchestrator checks coverage, difficulty, duplicated situations, clear local roles,
and final-transfer collisions. Do not fan out a course until its practical boundary and pilot have
held up under review.

## 5. Authoring rules every writer checks

**A rule added here only reaches the writers who were told to read this file.** In practice a
writer works from its blueprint and the canonical deck, so a rule that exists only in this document
will be followed by whichever track was being written when it was added and silently missed by
every other one. When you add or change a rule with a number in it, **mirror it into each track's
`lesson-blueprint.md`** — and check the canonical deck actually obeys it, because that deck is what
writers copy. Korean spent 348 reorder sentences at the wrong chip count for exactly this reason.

- **No katakana over English. Ever. `yomi.js` is not loaded.** See `AGENTS.md`. This is the rule
  most likely to be broken by an agent that read the Korean instructions first.
- Every English shell carries `<meta name="podo:target-language" content="en">`. Shared runtime
  controls use it to choose English tutor-facing copy while Korean decks safely keep the default.
- Classify vocabulary in the four `podo:vocabulary:*` metadata fields before changing
  `podo:vocabulary-status` from `todo` to `reviewed`. New shells deliberately inherit no word list.
  Every `JP:EN` hint chip belongs to exactly one category. Core and Contextual normally introduce
  at most eight content words; a genuine exception needs a written `podo:vocabulary-waiver`.
- One activity per page; English-first title with a Japanese gloss; one blue tutor-script box.
- Preserve the authoritative TOC/generated-brief title in the document title and visible opening
  title. A short `data-act` may summarize the activity, but it must not replace or rewrite the
  curriculum title. If the title itself needs improving, edit the TOC and regenerate the brief and
  catalogs first; do not improvise a different title inside one deck.
- Tutor scripts use the shortest natural, conversational line that preserves the learner's next
  action or the page's meaning. Do not narrate visible setup, inventory later activities, or pad a
  goal with `Today we'll...` / `By the end of the lesson...`. A sentence whose whole content is a
  count of what is already on screen (`There are four.`) narrates visible setup too — but a count
  folded into the instruction (`Read the four sentences.`) *is* that page's instruction and stays,
  and a find-all activity keeps its count because there the number says when to stop hunting.
  Rewrite the Japanese in the same change so meaning, sentence count and conversational tone still
  match.
- Core and Contextual `pattern-meaning` boxes use **one short English sentence** combining meaning
  and communicative use, with one direct Japanese counterpart. Do not put an activity direction,
  Japanese wording or a lesson-number reference in the English line. A rule-page script adds only
  what its visible diagram cannot show instead of reciting the diagram.
- Core and Contextual teaching/read models mirror every taught target with `.ending` in English and
  on its exact Japanese meaning. Controlled fills use one Japanese `.target.ending` per blank;
  word-level choice uses one Japanese highlight per independent decision. Reorder and whole-sentence
  translation prompts stay neutral. Highlight presence somewhere on a page is not enough—check each
  row and each decision.
- Every Contextual interaction must be runnable by an English-speaking tutor who does not read
  Japanese. `Understand` meaning options expose a concise English sense label alongside Japanese
  support, and the English tutor note states the read order when it is not visible. Never use
  Japanese-only alternatives as the tutor's answer key.
- Tutor-only notes are English in every track. Add one only when the tutor must catch or do
  something the page cannot make obvious, and place it on the production page where that action
  happens—not on a teaching page that produces nothing yet. Do not repeat a revealed answer.
- In Freetalking, default to **no coaching in the spoken script**: use the conversation question or
  a natural transition alone. Add a procedural direction only when the learner cannot infer the
  essential interaction without it. Page 2 is read only in pre-study; the class script may ask for
  questions about the article but must never tell the learner to read or skim it during class.
- Freetalking page 2 uses **10–15 sentence rows**. Full and accessible keep the same claims in the
  same order; accessible lowers rare vocabulary and clause load rather than merely shortening the
  full wording while retaining its hardest words.
- Freetalking question-page tutor notes contain only 2–3 concise follow-up questions. Do not add a
  coaching preamble about answer shape, pacing, correction strategy or the lesson author's intent.
  Give every prompt a distinct job: concretize, cause, perspective, consequence or hindsight. Do
  not restate the printed question, pre-empt a later ladder question, spend two slots on the same
  yes/no branch, or assume an in-person scene or another speaker. Two strong prompts beat a filler
  third. The accessible version simplifies their language without replacing open depth with generic
  yes/no prompts. Reserve a short operational note for a non-question page whose essential behavior
  is otherwise invisible, such as the article's pre-study-only skip rule.
- A Freetalking question page prints one **talking prompt**. An imperative is valid; reject two
  independent conversational jobs on one page rather than mechanically requiring a question mark.
- Keep the pattern-intro page as a pacing bridge: pattern name plus one short Japanese line moving
  from the scene into the next beat. Do not teach grammar on the dark transition page.
- Open the first teaching page of each pattern with one compact meaning-and-use box: what this
  frame means, and **when a speaker reaches for it**. Keep formation for the later rule page. A
  rule page can only draw a form; put use there and the learner gets a diagram they cannot act on.
- Every closed sentence activity keeps **four questions** from read through translate; difficulty
  must not taper by silently dropping questions. Free-writing stays one open prompt.
- Reorder activities use **four meaningful phrase chunks** per sentence — four is the ceiling and
  the working default. Three is fine when the sentence honestly holds three units; do not pad to
  reach four, and never reach four by splitting a compound noun, an article off its noun, an
  auxiliary off its verb, or an inflection off its stem. Do not stop short either: if a fourth unit
  is already in the sentence, give it its own chip. Chunk every sentence on a page the same way.
  The checker flags an English three-chip page for explicit review so this default cannot silently
  become a three-chip habit.
- Core `p3-model` and `p3-complete` use the same **5–7-turn** exchange. The count is a guardrail,
  not permission to pad: the dialogue still needs an opening, an answer-dependent follow-up and a
  resolved ending, and every added turn must change or complete the interaction.
- Contextual opening scenes use **5–9 purposeful turns** and replay the same turn sequence in
  `p3-model` and `p3-complete`; a short excerpt is not a replay. Receptive meaning choices paraphrase
  the complete staff line, and both options answer the same comprehension question. A staff
  question is never matched to two possible learner answers or two bare topic labels.
- A spoken prompt feeding one answer box asks **one question**. Two only when the second narrows
  the first (either/or, or a yes/no setting up the real question); never three, and never two
  unrelated questions joined with "and". Three answers wanted means three turns, not one crowded
  box. Turns are cheap; working memory at A1 is not.
- **A question the page asks must be answered by the model.** Korean shipped a lesson that asked
  「지금은 괜찮아요?」 and never picked it up; the learner stalls in front of a question with no
  landing place.
- A visual rule page has **one block per real formation branch**, not one block per example. One
  block for an invariant rule; two or three only when the learner must distinguish those forms.
- Include a choose page only for an **honest, taught distinction**. Omit it when one option is a
  manufactured wrong form, or when both answers are grammatical and choosing needs an unintroduced
  nuance.
- A native tip adds one **adjacent** choice not already taught — register, softening, contraction,
  prosody, collocation, intensity. It is not a recap or a delayed explanation. When both options are
  valid, show them at equal visual weight with situation labels; a correction arrow falsely turns a
  contextual decision into a right/wrong rule. **Contractions and ordinary spoken forms are taught
  alongside full forms**, not months later as "native speed" (`lesson-template.md`).
- A form can be grammatical and still be the wrong production target. If contemporary speakers
  rarely choose it beside a common alternative, demote it to receptive recognition or remove it;
  do not drill it merely to complete a paradigm. Re-check the TOC and brief rather than hiding the
  decision inside one deck.
- Contextual free-talk is a **reciprocal exchange**, not a single student prompt: the tutor asks,
  the student answers, the student asks a related question, and the tutor gives a real personal
  answer in the editable field. Do not end the page after the student's answer.
- The final Contextual transfer is a complete **5–7-turn mini-scene** with 2–3 learner completions,
  uses both of today's patterns, changes at least two meaningful scene variables, and resolves the
  same practical job without introducing another lesson's target.
- Contextual scene/model/replay/transfer turns use profile images for their roleplay characters and
  stable English speaker names; only the live Tutor/Me exchange uses generic icons. Late replay and
  transfer blanks use wrapping `phrase-input` textareas with exact Japanese `.target` cues.
- Use existing components and `data-sync` contracts. An element is shared **only** if it has a
  `data-sync-id`; verdicts are never shared — send the choice and let each side derive
  correct/wrong locally.
- Keep the receptive → productive arc from the blueprint.
- Show a short, consistent speaker name beside every avatar.
- **No inline CSS or JavaScript**, and do not change the shared runtime from a lesson assignment.
- Unique `data-page-id` per page; unique `data-sync-id` per shared control.
- Preserve enough bottom clearance that the fixed pager never makes content unreachable.

Scrolling is allowed. Split a long page only when its size creates another problem: the pager hides
an unfinished task, the learner cannot tell the activity's scope, or one page asks them to retain
too many turns at once. Split dialogue at a meaningful conversational beat, never at an arbitrary height.

For contextual lessons, the native tip comes **before** the final transfer scene. Nothing follows
the transfer; it is the last image the learner leaves with.

## 6. Verify each deck and the integrated course

Static checks:

- required `podo:*` and `notranslate` metadata
- lesson id equals its directory name
- all relative CSS/JS/image refs resolve
- unique page and sync ids
- **no `.yomi`, no katakana over English, `yomi.js` not loaded**
- no inline CSS/JS, no accidental shared-runtime changes
- **every tutor script box has the same number of sentences on both sides**
- **every tutor-only block is English**
- Core/Contextual meaning/use boxes contain one concise English sentence and one Japanese sentence
- **every reorder page uses one chunking criterion down the page**
- **every reorder chip set can reconstruct its own `data-a` answer under the runtime's comparison**
- reviewed four-way vocabulary ownership; every hint chip declared; Core/Contextual new-word cap
- Freetalking page inventory/order, 10–15-row article contract and paired full/accessible row parity

### Run the checker

```sh
python3 english/tools/check_deck.py english/tracks      # a tree
python3 english/tools/check_deck.py path/to/lesson.html # one deck
python3 english/tools/check_deck.py --all               # every deck in the repo
python3 english/tools/build_running_lexicon.py           # regenerate the author ledger
```

It enforces the machine-verifiable static checks above and exits non-zero on any error, so it can
gate a batch. Naturalness, honest meaning-unit boundaries and whether a distractor is believable
remain human review decisions. The checker exists because several silent failures look plausible
in markup and a checklist item only reaches the writers who were told to read it.

### Checks that fail silently

These produce a page that is *valid markup and wrong on screen*, with nothing in the console.

**1 · Tutor script sentence parity.** `runtime/js/script-lines.js` rebuilds the blue box as one
sentence per line, English above its own Japanese — but only when the two sides have **equal
sentence counts**. When they differ it deliberately does nothing, because mis-pairing would print
"this Japanese is the translation of this English" as a lie. The failure mode is a wall of bunched
text that looks merely ugly rather than broken. `AUTHORING.md` §2 has always said the two must be
the same sentences; this is what enforces it.

`.pattern-meaning` is exempt — it owns its own pairing and is skipped on purpose. Keep its text
short instead; nothing will split it for you.

```js
// paste into the rendered deck
[...document.querySelectorAll(".section-subtitle")].filter(b=>!b.classList.contains("pattern-meaning"))
  .map(b=>{const ko=b.querySelector(":scope > .ko"),ja=b.querySelector(":scope > .ja");if(!ko||!ja)return null;
    const c=(t,e)=>[...t].filter(x=>e.includes(x)).length||1;
    const k=c(ko.textContent,".!?"),j=c(ja.textContent,"。！？");
    return k===j?null:`${b.closest("[data-page-id]").dataset.pageId} EN=${k} JA=${j}`;}).filter(Boolean)
```

**2 · Reorder chunking consistency.** Four chunks is the ceiling and the working default; three is
allowed only when the sentence honestly holds three. The trap is not the count — it is **mixing
criteria on one page**. The pilot shipped 3/4/3/4 because `please` had been tacked onto two rows,
which is padding two sentences rather than analysing four the same way.

Write the page's criterion into an HTML comment above it, then check every row against that one
sentence. If a row needs a different criterion to reach its count, the count is wrong.

```js
[...document.querySelectorAll("[data-page-id]")].filter(p=>/reorder/.test(p.dataset.pageId))
  .map(p=>({page:p.dataset.pageId,counts:[...p.querySelectorAll(".task-block")].map(b=>b.querySelectorAll(".choice").length)}))
```

**3 · Reorder solvability.** A page can have the right number of chips and still be impossible if
one word is missing or a chip belongs to another answer. `check_deck.py` mirrors
`activities.js`'s normalization and verifies that some ordering of each task block's chips exactly
reconstructs its own `data-a`. This is a hard error, not an editorial warning.

Interactive checks at both **480px and 360px**:

- every page reachable and readable, including after scrolling
- choose/reorder/fill/write controls complete and reset correctly
- learner and tutor views stay in sync where required
- tutor notes and answer visibility correct for each role
- no console errors, no pager overlap making content unreachable
- no page, dialogue turn or generated input widens its container

Use representative screenshots across the course, plus every new or unusually dense page. A pass
means more than "it scrolls": the learner must understand what to do before the activity disappears
below the fold.

## 7. Then regenerate the derived files

```sh
# [not built] — gated on D4/D5
python3 english/tools/plan_courses.py english/tracks/<track>

# built — regenerate review material after accepted TOC changes
python3 english/tools/build_lesson_briefs.py --all
python3 english/tools/build_grammar_map.py
python3 english/tools/build_catalog.py

# shared-runtime drift checker currently lives on the Korean side
python3 korean/tools/check_runtime_drift.py
```

**`check_runtime_drift.py` matters before you trust any local render.** Deployed decks load a
pinned CDN tag, not the working folder — so when the two differ, the page approved at 480px is not
the page the learner gets, and nothing errors to tell you. A component that exists only locally
just renders unstyled.

Only after the integrated course passes should it move toward production sync — which for English
does not exist yet (`BUILD-PLAN.md` → Phase 7).
