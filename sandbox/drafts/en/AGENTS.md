# Working in `english/`

**Read [`../../../shared/ux-philosophy.md`](../../../shared/ux-philosophy.md) and
[`../../../shared/deltas-en.md`](../../../shared/deltas-en.md) before touching anything in this
folder — every time, including small edits.** The first is the language-neutral contract for
every lesson page in this repo: one activity per page, instant clarity, minimal everything, one
blue tutor-script box, one boxed component that *fills* the page, receptive → productive. The
second is the complete list of places where English differs, and it is the only place those
differences are recorded — this file no longer carries a copy.

Do not design a page, add a component, or write copy here until you have read both. If a change
you are about to make conflicts with either, say so and ask — don't quietly deviate.

**Where a new rule goes.** If it would be just as true of Korean, it belongs in
`ux-philosophy.md`, not here and not in `deltas-en.md`. The two curricula spent most of 2026-08
re-deriving each other's rules a day apart because English had no way to write a shared rule
down; putting a general rule in a delta file is how that starts again.

**This folder is pre-production, not empty.** It has four TOCs (315 planned items), approved Core
and Freetalking canonical decks, three production blueprints, strict parsers, generated briefs and
grammar map, a deck checker and an owner-approved native-review catalog.
[`BUILD-PLAN.md`](./BUILD-PLAN.md) is the reconciled list of what remains and who unblocks whom.
The catalog hold was lifted on 2026-08-18. On 2026-08-19 the owner approved the complete
representative set: Core 20/32/45/82, replacement Contextual CTX-1, and the FT-1/7/9/49
accessible/full pairs. Core, Contextual and Freetalking may now proceed in course-sized batches;
Pronunciation remains planning-only.

---

## Audience

**Japanese speakers learning English.** Same learner as the Korean curriculum, different target
language. The language rules that follow from that — support text is Japanese, tutor notes are
English and carry no language lock, no Korean in a learner-facing deck — are in
[`../../../shared/deltas-en.md`](../../../shared/deltas-en.md). What stays here is what is true
of *this folder* rather than of the language.

- **Every English deck declares `<meta name="podo:target-language" content="en">`.** The shared
  runtime uses that explicit signal for generated tutor controls. `<html lang="ja">` correctly
  describes the learner-support language and must not be repurposed as the teaching-language flag.
- **Freetalking question-page notes are follow-ups, not coaching.** Put only 2–3 concise follow-up
  questions in the private band. Each one must make a different conversational move—for example,
  concretize, explain a cause, add another perspective, explore a consequence or invite hindsight.
  Do not repeat the printed question or a later ladder question, split one idea across multiple
  yes/no prompts, or assume the story happened in person or involved another speaker. **Two strong
  follow-ups are better than a filler third.** Do not precede them with advice about how to shape
  the answer, extend the story, preserve a frame, correct the learner, or interpret the topic. A
  non-question page may carry one short operational note only when the tutor cannot infer an
  essential contract from the page—for example, skipping the pre-study article rather than reading
  it in class.

### No katakana readings. Ever. At any level.

The full rule and the reasoning behind it are in
[`../../../shared/deltas-en.md`](../../../shared/deltas-en.md) § *No katakana readings*. It is
kept there, once, because it is the one rule that **inverts** rather than copies its Korean
counterpart, and an agent that has just read `deltas-kr.md` will otherwise reach for `.yomi` out
of habit. Two copies of an inverted rule is how one of them ends up stale.

Short form: English decks do not load `yomi.js` and carry no `.yomi`, at any level. Kana is fine
wherever it is *not* pronouncing English — a Japanese gloss, a `JP:EN` hint chip, a tutor note, a
title's parenthetical.

---

## Also true of this folder

- **Shared design system:** `../../../shared/css/lesson-card.css`. White cards on a 1px grey
  outline; the palette lives in `:root` there — **use the tokens, never the hex**. Reuse the
  existing component vocabulary before inventing a new one — consistency over novelty.

  **The runtime lives at the repo root and is shared with the Korean curriculum.** There is exactly
  one copy; do not fork it, and lesson writers do not change it from inside their assignments. If
  an English deck needs something the runtime cannot do, the writer reports the gap to the
  orchestrator. The orchestrator may make one coordinated shared-runtime change, test both English
  and Korean behavior, record any publish dependency in `tracks/_conventions.md`, and keep it
  separate from concurrent writer edits. A local fix still does not reach a learner until the
  pinned CDN runtime is republished and the deployed decks are repointed.

  Two path facts that will bite a hand-edited deck:

  | Target | Where | From a lesson deck |
  | --- | --- | --- |
  | the runtime | repo root, shared | seven `../` |
  | `trial/assets/` | still inside `../kr/` — **did not move** | six `../` |
- **Every colour means one thing.** `green-500`/`green-100` = state (chosen, correct, active).
  `blue-100` = the tutor's spoken script. `blue-200` = the tutor-only band fused under it.
  `lime` = brand chrome only, never state. `gray-200` = ordinary outlines. Dashed grey = "write
  here". Adding a second meaning to any of these is the single easiest way to make a page
  unreadable — see the table in `ux-philosophy.md`.
- **The blue `.section-subtitle` box is the tutor's spoken script.** Use the shortest natural,
  conversational English that preserves the learner's next action or the page's meaning. Do not
  inventory later activities, narrate what the page already shows, or add framing such as
  `Today we'll...` and `By the end of the lesson...`. Use no grammar jargon and write in the first
  person (`I'll read it first` — never `the teacher will`). Its Japanese line is a direct
  translation with the same conversational tone, not extra teaching content.
- **Freetalking scripts are conversation, not coaching.** The blue box should normally contain
  only the question or natural transition the tutor actually says. Do not script directions for
  how to answer, where to tap, how long to speak, or how to move through the page unless the
  interaction would otherwise be impossible to understand. In particular, the Freetalking article
  is completed only during pre-study: its in-class script asks whether the learner has questions
  and never tells them to read, skim, or catch up during class.
- **Lessons are audio-only.** The learner hears the tutor but never sees them, so no instruction
  may depend on watching the tutor — no "watch my mouth", no gestures, no "look at me". Model a
  sound by *saying* it. Describing the learner's **own** mouth is fine and matters more here than
  it does in Korean, because several of the target contrasts are articulatory
  (`Put your tongue between your teeth` for /θ/).
- **Max two levels of boxes:** the page card plus ONE boxed component inside it. Never wrap
  bordered components in another bordered card.
- Every lesson page needs `<meta name="google" content="notranslate">` or Chrome auto-translate
  mangles the mixed ja/en content. **This matters more for English than it did for Korean** —
  Chrome is far likelier to offer to translate a page that is half English.
- **Verify visually.** These are visual documents; render them in a browser at 480px width and
  look at the screenshots before claiming a change works.

---

## Writing a new lesson

**If the request says create/generate a curriculum, course, lesson, or batch of lessons, read
[`LESSON-CREATION-WORKFLOW.md`](./LESSON-CREATION-WORKFLOW.md) before planning or delegating.**

### Mandatory pilot gate

Core 20, replacement Contextual CTX-1, and both Freetalking FT-1 variants are approved canonical
decks. The owner passed the current 303-item native-review catalog on 2026-08-18 and explicitly
approved the remaining representative decks on 2026-08-19. The course-batch gate is therefore open
for all three production tracks. Freetalking must still be authored as matched accessible/full
pairs. Structural checks validate a batch; they never substitute for owner approval of a new
canonical shell.

### The inputs, in order

1. **A deck skeleton.** `tools/authoring/en/new_lesson.py` lifts metadata, shared paths and the
   load-order-bearing scripts from an approved English canonical deck, removes its pages, checks
   references and refuses overwrite. Core and Contextual default to their approved pilots.
   Freetalking writers pass the matching approved accessible or full FT-1 deck with `--from-deck`.
   Never use a Korean deck, whose shell loads `yomi.js`.
2. **The generated lesson brief.** Run `tools/authoring/en/build_lesson_briefs.py`; read the stable-id brief in
   `tracks/<track>/toc/`. It carries the exact TOC facts, adjacent context and negative sequence
   guardrails. Never hand-edit it.
3. **`tracks/<track>/lesson-blueprint.md`** — which pages, in what order, doing what. Plan the arc
   from here. *(Written per track as each track's pilot lands.)*
4. **The canonical deck the blueprint names**, in full. This is the expensive read and it is the
   one worth paying for: the blueprint carries structure, but the tutor's voice, the way a wrong
   answer is made wrong for a reason, and the rhythm of the example sentences live only in the
   deck itself. A lesson written from the blueprint alone comes out correctly shaped and lifeless.
5. **The generated running lexicon.** Read `reference/running-lexicon.md`, classify every content
   word as new, recycled, assumed-known or receptive-only in the deck metadata, then set
   `podo:vocabulary-status` from `todo` to `reviewed`. The shell deliberately clears the pilot's
   vocabulary so copied words cannot acquire false provenance.

### Two constraints that are easy to lose

- **The "not yet" constraint binds the learner's whole produced sentence, not only its blank.** At
  Pre-A1/A1, every fixed word in learner production must come from earlier Core or from the two
  patterns explicitly taught here. At most one TOC-labelled bounded survival chunk may run ahead;
  keep it whole and never transform or assess its internal grammar. The tutor's spoken
  `.section-subtitle` and partner turns may run ahead only as supported receptive English. Forcing
  the syllabus into tutor speech makes it stilted, but silently turning that speech into a learner
  target breaks the sequence.
- **Implement the TOC's spiral review metadata.** A `Spiral review:` target is retrieval inside the
  current can-do, not a third pattern or a second explanation. Match its declared mode
  (`recognition`, `controlled`, `contrast`, `transfer`, or `checkpoint`) and carry no more than two
  targets in one ordinary lesson.
- **Scaffold every non-target word.** Blanks target only the pattern being practiced. Hint chips
  list vocabulary only (`JP:EN`) — never articles, auxiliaries or inflections, which are the
  English analogue of the particles-and-endings rule in `ux-philosophy.md`. Every hint-chip English
  value must appear in exactly one vocabulary metadata category; Core and Contextual normally add
  no more than eight new content words.
- **Target fidelity outranks row variety.** The exact frame highlighted on `pN-read` is the exact
  answer removed on `pN-fill`. Never move a blank onto vocabulary to make four answers different;
  redesign or omit a weak page instead. Whole-sentence production declares `supported` with lexical
  hints on every row or `checkpoint` with none. Neither stage hints articles, auxiliaries or
  inflections.

---

## English deltas from `ux-philosophy.md`

They now live in **[`../../../shared/deltas-en.md`](../../../shared/deltas-en.md)**, beside the
contract they qualify and beside their Korean mirror
[`deltas-kr.md`](../../../shared/deltas-kr.md). Keeping the table here made an English rule
structurally unable to become a shared one: there was no file it could move *to*.

Read that file. In short, and not a substitute for reading it: English-first titles, tutor notes
in English with no language lock on the answers, **no katakana readings at any level**, no
decoding track, `.ending` as the only inline accent, mixed reorder chip counts as a hard error,
and `Pre-A1` as the band exempt from the teaching-set variation rule.

---

## Layout

- **`tracks/`** — the learner-facing curriculum: `1-core-patterns` · `2-contextual-english` ·
  `3-freetalking`, plus planning-only `4-pronunciation`. The three production-facing tracks now
  have a blueprint and an approved canonical deck (two matching shells for Freetalking's two
  language-load variants).
- **`reference/`** — the author-only source trail: teaching philosophy and the pattern standard,
  the source hierarchy and provenance policy, the proposed evidence-first build method, the
  grammar coverage map, the rationale, and the transformation map from the linked Podolingo doc.
  **This is the strongest part of the English folder** and it is more rigorous than anything on the
  Korean side; it should eventually be back-ported rather than diluted.
- **`shared/`** — `lesson-template.md`, the two-pattern lesson spec. Core and Contextual translate
  that hierarchy into page arcs; Freetalking deliberately uses a correction loop instead.
- **`BUILD-PLAN.md`** — the ordered gap list and its decisions. Read it before proposing work.
- **Archive — deliberately not here.** Retired drafts live in `sandbox/archive/` at the *repo*
  root. They are **not part of the read path**: never cite one as precedent, never copy markup
  out of one. If a grep turns up a `sandbox/archive/` hit, the live answer is elsewhere.

## Getting a lesson to production

**English is live.** As of 2026-08-21 there are 47 enabled courses under `courses/en/` carrying
425 promoted lessons, and a merge to `main` changes what an English learner sees in class. This
paragraph used to say deployment was not yet possible and that the generator must not create
`lesson.yaml`; both were true when written and neither is true now. Treat an English change with
the same care as a Korean one.

Two constraints are already fixed and worth knowing before anyone designs around them, both from
`../kr/AGENTS.md`:

- **Stay `curriculumType: BASIC`.** It is a supported product line recognized by `podo-app`,
  `podo-backend` and `grape`. Do not create a version-suffixed variant.
- **Audience is `spec.countryCode`, not the level.** It is required downstream, persists as
  `GT_CLASS_COURSE.COUNTRY_CODE`, and is part of the natural key. This Japanese-market curriculum
  emits `countryCode: JP`. Changing it on an already-deployed course creates a different identity:
  first deploy the old identity with `enabled: false`, then change `countryCode` and deploy the new
  identity.

`LANG_TYPE` separates English from the Korean and Japanese curricula, so band numbers cannot
collide across languages even where they coincide. Do not add it to `course.yaml`: the consuming
repository derives `EN` from the destination directory. This tree is the source — there is no sync
step any more. A verified course reaches learners by being named in `promotion.yaml` and
promoted into `courses/en/` with `tools/promote.py`.

### Catalogue names: three languages, always

`GT_CLASS_COURSE` names a course and a lesson in three columns — `BOOK_NAME` (ko),
`EN_BOOK_NAME`, `JP_BOOK_NAME` — and `DESCRIPTION` is an i18n JSON object rather than prose.
**The app picks a column by the learner's locale.** This track teaches English to Japanese
speakers, so `ja` is the string on screen, `en` is the course's own language, and `ko` is
grape's admin label. All three are required; a deck or course with only English in all three
slots reaches the catalogue effectively unnamed.

- **Course title and description** come from `tools/authoring/en/course-copy.json`, keyed by slug, never
  from the TOC. Generating them produced English in all three slots and shipped build notation
  (`Core 25–36 · A1 → A2`, `13 topics · Full version`) as the learner-facing description.
  `plan_courses.py` reports any missing language and `test_plan_courses.py` fails on it.
- **The CEFR band is the last segment of every course title** and ships deliberately: English
  learners in Japan read CEFR, and for free talking it is the only thing separating an
  accessible course from its full sibling. It does not belong inside the description.
- **Title length** is held at 40 characters for `en` and 30 for `ko`/`ja`. Live cover rows
  average 13 characters in ko and 22 in en, so shorter is the house style; the titles this
  replaced ran to 72.
- **Lesson titles live in the deck.** `podo:title-{ko,en,ja}` is written by `new_lesson.py`
  and required by `check_deck.py`, which also holds `podo:title-en` equal to the generated
  brief heading. They are load-bearing and must not be removed.

`DIFFICULTY` maps from the CEFR band, highest first, across all five values a course can take:
`C1 → ADVANCED`, `B2 / B1+ → UPPER_INTERMEDIATE`, `B1 → INTERMEDIATE`, `A2 → UPPER_BEGINNER`,
`A1 → BEGINNER`. A course is entered at its ceiling, because difficulty describes what it takes
to finish rather than to start.
