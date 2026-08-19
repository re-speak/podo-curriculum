# Working in `korean/`

**Read [`ux-philosophy.md`](../ux-philosophy.md) before touching anything in this folder — every
time, including small edits.** It is the contract for every lesson page: one activity per page,
instant clarity, minimal everything, Korean-first titles, one blue tutor-script box, one boxed
component that *fills* the page, receptive → productive.

Do not design a page, add a component, or write copy here until you have read it. If a change
you are about to make conflicts with it, say so and ask — don't quietly deviate.

## Also true of this folder

- **Shared design system:** `runtime/css/lesson-card.css`. White cards on a 1px grey outline; the
  palette lives in `:root` there — **use the tokens, never the hex**. Per-track additions go in
  that track's own stylesheet, loaded after it (e.g. `runtime/css/trial.css`). Reuse the existing
  component vocabulary before inventing a new one — consistency over novelty.
- **Every colour means one thing.** `green-500`/`green-100` = state (chosen, correct, active).
  `blue-100` = the tutor's spoken script. `lime` = brand chrome only, never state.
  `gray-200` = ordinary outlines. Dashed grey = "write here". The cream/pink seat colours are
  pedagogy and outrank everything. Adding a second meaning to any of these is the single
  easiest way to make a page unreadable — see the table in `ux-philosophy.md`.
- **Audience is Japanese speakers learning Korean.** All support text is Japanese; no English.
  Sound anchors are kana, not English words.
- **Pronunciation stops at 초중급. This is a level rule, not a per-deck taste.**
  A kana reading (`.yomi`) under the Korean is a decoding crutch, so it belongs only where the
  learner may not yet decode hangul — **왕초급 · 초급 · 초중급 and no further**. From 중급 up,
  reading hangul is a skill the learner already has and the deck must not do it for them.
  Every deck declares its own level in `<meta name="podo:level">`; check it before adding a
  reading to anything.

  | Trial deck | Level | Readings |
  |---|---|---|
  | `trial-1-hangul` | 왕초급 | yes |
  | `trial-2-patterns` | 초급 | yes — the reference implementation |
  | `trial-3-contextual` | 중급 | **no** |
  | `trial-4-freetalking` | 고급 | **no** |

  Where readings do apply, `runtime/js/yomi.js` puts a named **よみがな** switch on the title
  line of every page that has them; it hides them deck-wide and the state is shared with the
  other screen. See `AUTHORING.md` § 발음 표기 for where a reading goes and where it must not
  (never inside a two-way `.opt` pill).
- **The blue `.section-subtitle` box is the tutor's spoken script** (`.ko` = the line read
  aloud, `.ja` = its Japanese translation). Natural spoken Korean, no grammar jargon.
- **Nothing in `.ko` that a Korean tutor cannot say.** No kana, no kanji, no lesson numbers —
  a tutor can no more resolve 「90과」 on sight than a learner can. Japanese that genuinely
  helps goes in `.tutor-note` with its Hangul reading in parentheses. In 2-core-patterns the
  form's Japanese equivalent lives in the `.anchor` slot, whose reading comes from
  `tools/ja_to_hangul.py` — never typed by hand. `tools/check_teaching.py` enforces all of it;
  see `AUTHORING.md` § 가르치는 면에 걸리는 다섯 가지.
- **Lessons are audio-only.** The learner hears the tutor but never sees them, so no
  instruction may depend on watching the tutor (口の形をまねして, gestures, "look at me").
  Model sounds by saying them. Do not reach for 제가 읽을게요. 잘 듣고 따라 읽어 보세요. as the
  house phrase — it was identical on 246 of 255 teach boxes and is now a `check_teaching.py`
  finding; say the thing this page actually needs instead.
- **Max two levels of boxes:** the page card plus ONE boxed component inside it. Never wrap
  bordered components in another bordered card.
- Every lesson page needs `<meta name="google" content="notranslate">` or Chrome auto-translate
  mangles the mixed ja/ko content.
- **Verify visually.** These are visual documents; render them in a browser at 480px width and
  look at the screenshots before claiming a change works.

## Writing a new lesson

**If the request says create/generate a curriculum, course, lesson, or batch of lessons, read
[`LESSON-CREATION-WORKFLOW.md`](./LESSON-CREATION-WORKFLOW.md) before planning or delegating.**
It defines the course-aware brief pipeline, pilot gate, sub-agent ownership boundaries,
continuity review and integrated QA for every track.

### Mandatory pilot gate

Treat the workflow's pilot sequence as a stop gate, not advice. For a new curriculum or course,
author **one representative lesson by hand**, verify its complete narrative, pedagogy, component
markup, and every page at 480px, then stop for explicit user approval. Do not use a generic content
generator, assign a lesson batch, or present additional decks as finished before that approval.
Structural checks alone never approve a pilot. If the pilot is rejected, rewrite and re-review it;
do not use it as a template. After approval, draft three structurally different lessons, review
those, and only then expand the remaining batch as described in the workflow.

## Reviewing many existing lessons

For a curriculum-wide proofreading, consistency check or other judgment-heavy audit, read
[`PROOFREADING-WORKFLOW.md`](./PROOFREADING-WORKFLOW.md), especially **Token-efficient projected
audits**. Do not give whole lesson HTML files to parallel reviewers when the question concerns a
small semantic field. Project only the relevant `{source, pageId, field, current, context}` records,
have reviewers return exact-match proposals without editing decks, and validate centrally before
applying anything.

Four inputs, in this order. Read them all — the budget saved by the first two is there to be
spent on the last one.

1. **`tools/new_lesson.py`** stamps the deck skeleton. The meta block, the stylesheet links and
   the sixteen script tags whose load order is load-bearing are not yours to retype — the script
   lifts them off the track's canonical deck so they cannot drift.
   `python3 korean/tools/new_lesson.py --track 3-contextual-korean --course ctx-drama-crush-intermediate --lesson 1 --id 01-first-meeting --title-ko "첫 만남" --title-ja "初対面" --title-en "First meeting"`
2. **`tracks/<track>/toc/<course-code>/lesson-NNN.md`** — the course-scoped textual brief:
   what this lesson teaches, its course context and the lessons on either side. Core patterns,
   whose numbers never restart, keeps its richer legacy path `toc/lesson-NNN.md`. Both are
   generated from `table-of-contents.md` by `tools/build_lesson_briefs.py`; **never hand-edit a
   brief**, edit the TOC/parser and re-run. Read the brief, not the full TOC.
3. **`tracks/<track>/lesson-blueprint.md`** — which pages, in what order, doing what. Plan the
   arc from here.
4. **The trial deck the blueprint names** (`trial/lessons/trial-N-*.html`), in full. This is the
   expensive read and it is the one worth paying for: the blueprint carries structure, but the
   tutor's spoken voice, the way a wrong answer is made wrong for a reason, and the rhythm of
   the example sentences live only in the deck itself. A lesson written from the blueprint alone
   comes out correctly shaped and lifeless.

Regenerate the briefs after any TOC change:
`python3 korean/tools/build_lesson_briefs.py korean/tracks/<track>`

**Before trusting a local render, check the runtime you rendered against.**
`python3 korean/tools/check_runtime_drift.py` compares `runtime/` with the CDN tag
production actually serves. Deployed decks load that tag, not this folder — so when
the two differ, the page you approved at 480px is not the page the learner gets, and
nothing errors to tell you. A component that only exists locally just renders unstyled.

### Checking a deck you just wrote

Eight `check_*` scripts verify the things a reader cannot see. Run them on the decks you
touched before committing; several also take no arguments and sweep the whole repo.

| script | catches |
| --- | --- |
| `check_structure.py <deck…>` | unbalanced tags, duplicate `data-page-id`, missing sync ids |
| `check_reorder.py [deck…]` | **a word-tile that is not in its own answer.** Replays `activities.js`'s own comparison and asks whether some permutation of the tiles reconstructs the answer exactly. Silent breakage otherwise — the page looks fine and can never be solved |
| `check_syllabus.py [track]` | a deck using grammar a later 과 owns. Strips the tutor's spoken script first, since that may run ahead of the syllabus. Reports set phrases too (`반갑습니다`), so read hits before acting |
| `check_distractors.py <deck…>` | a wrong option that is real Korean somewhere else. Surfaces candidates only — whether it is *also correct in this slot* is a human call |
| `check_quotes.py [deck…]` | a cited expression not wrapped per `AUTHORING.md` § 인용한 표현 |
| `check_chips.py [track…]` | word-tile counts per sentence against the four-chunk rule |
| `check_freetalk.py [--warnings]` | **4-freetalking pedagogy** — page inventory, page-2 length, one prompt per page, follow-up counts, vocab/highlight parity, and a soft check on 중급 decks that never simplified their 고급 sibling. The other checks verify markup; this one verifies the lesson. Blocking rules exit non-zero; `--warnings` shows the judgment calls |
| `check_teaching.py [deck…]` | **the five teaching-surface rules** — the `.anchor` slot, Japanese in a spoken line, lesson numbers anywhere, the boilerplate close, and length. Runs the whole repo with no arguments; `--rule ref` narrows to one |
| `check_render.sh <deck…>` | tallest page, stray `.yomi`, and horizontal overflow at 480px. Needs the Orca browser with a tab already open |

`check_teaching.py` and `check_reorder.py` are the two to run every time. The first is the
gate on everything the tutor says; the second has caught twelve sentences in this track whose
tiles could not build their own answer — a class of bug no other check sees.

## Getting a lesson to production

This folder is the authoring tree; `re-speak/podo-curriculum` is what deploys. **Keep
writing relative `../../runtime/…` refs** — that is the input format the production
tools expect. `sync-from-authoring.py` rewrites them to `shared/`, and
`repoint-shared.py` then pins them to the CDN tag declared in one place
(`curriculum.yaml` → `spec.sharedRuntime`). Writing a CDN URL here by hand would
hand-pin a version in every file and break local verification.

**These courses are `curriculumType: BASIC`.** Curriculum type is a supported product line,
not a content-version label: `podo-app`, `podo-backend`, and `grape` all recognize `BASIC`
and do not recognize version-suffixed variants. Tutor assignment consequently uses the existing
`PODO_KR_BASIC` key. A later English curriculum generation should also stay `BASIC` and use
unused `classLevel` values; do not create `BASIC_V3`.

**Each track gets a `classLevel` band, with a decimal slot per course.** Existing backend
queries already give special meaning to levels at and above `1000` (Breaking News and free
talking), so Korean stays below that boundary and inside the regular BASIC range. The band
is a stable routing convention; it does not create a visible app section until the backend
and app add a label/filter for that range. Ours:

| Band | Track | Courses |
|---|---|---|
| `100` | `1-hangul` | 1 |
| `200` | `2-core-patterns` | 12 |
| `300` | `3-contextual-korean` | 14 |
| `400` | `4-freetalking` | 10 |
| `500` | `5-pronunciation` | 1 |

Primary course positions advance by `0.010`: for example, Core starts at `200.010`,
`200.020`, and continues across the full `200 ≤ classLevel < 300` range. This leaves
`200.011` through `200.019` available for later insertion between the first two courses and
provides 9,999 primary positions in one section. Free talking uses reserved thousandth slots
deliberately for level pairs while preserving its existing Advanced natural keys: Intermediate
is `400.009`, `400.019`, ... and its Advanced sibling remains `400.010`, `400.020`, ....

`1–99` stays free in case Korean ever gets a graded ladder the way EN and JP have. **Never
use `999.x`** — that is where throwaway rows live (`html test (john)`), which is why the
trial decks sit there and nothing else should.

`LANG_TYPE` (KR) separates these from the English and Japanese curricula, so the numbers
cannot collide across languages even where they coincide. Avoid very large bands such as
`10000`: `CLASS_LEVEL` is handled as a Java `Float`, making three-decimal slots needlessly
fragile at that magnitude. **Audience is
`GT_CLASS_COURSE.COUNTRY_CODE`**, not the level. `spec.countryCode` is required by the downstream
course schema and is part of grape's natural key. This Japanese-market authoring tree always emits
`countryCode: JP`. Changing it on an already-deployed course addresses a different identity; first
deploy the old identity with `enabled: false`, then change `countryCode` and deploy the new identity.

**A track is not a course.** 2-core-patterns is 116 lessons; a deployable course is one
`classLevel` with weeks 1..N and no gaps. `tools/plan_courses.py` cuts the track against
its TOC into ~12-lesson courses on unit boundaries, and writes `course.yaml` /
`lesson.yaml` that already validate against podo-curriculum's `schemas/` — so the sync is
a copy, not a translation. Decks live at
`tracks/<track>/courses/<course>/lessons/<slug>/lesson.html`.

Lesson slugs are `NN-english-words` (`07-daily-routine`) because the schema demands it, and
the deck's `podo:lesson-id` must equal its directory name. `lesson.yaml` is written only for
lessons that have a deck; the rest of the plan lives as comments in `course.yaml`.

`sync-from-authoring.py` copies the complete track tree — TOCs, briefs, blueprints, manifests and
ordinary lessons — into `sandbox/authoring/kr/`. Nothing there deploys. Review that mirror first,
then run the explicit promotion path for the Korean course so it moves into `courses/kr/` without
translating `countryCode`, followed by `repoint-shared.py` → `validate.py`. `podo:lesson-id` and
`podo:title-{ko,en,ja}` are load-bearing — `new_lesson.py` writes them and they must not be removed.

**Never edit `shared/` or `sandbox/authoring/` in podo-curriculum.** Both are sync destinations
and get replaced wholesale; a fix made there disappears on the next sync with no error.
Fix it here instead.

### What the catalogue shows, and where each string comes from

`GT_CLASS_COURSE` holds one row per course *and* per lesson, and it names both in three
columns — `BOOK_NAME` (ko), `EN_BOOK_NAME`, `JP_BOOK_NAME` — plus a `DESCRIPTION` that is an
i18n JSON object, not prose. **The app picks a column by the learner's locale, so for this
Japanese-market tree `ja` is the string on screen and `ko` is grape's admin label.** Writing
only Korean well means writing well in the one language the learner never reads.

| What a learner sees | Row | Source here |
|---|---|---|
| course title | `BOOK_TYPE=COVER`, `CLASS_WEEK=0` | `course.yaml` → `spec.title.{ko,en,ja}`, composed by `plan_courses.py` |
| course tagline | same row's `DESCRIPTION` | `tools/course-copy.json` — `ko` may fall back to the TOC's 끝내면 할 수 있는 것 line |
| lesson title | `BOOK_TYPE=MAIN`, `CLASS_WEEK=N` | the deck's `podo:title-{ko,en,ja}`, read into `lesson.yaml` |
| lesson can-do | same row's `DESCRIPTION` | **not exported yet** — see below |

`DIFFICULTY` is five bands wide and the live catalogue leans hardest on the two it is easiest
to drop: `UPPER_BEGINNER` and `UPPER_INTERMEDIATE` together carry more deployed lessons than
`BEGINNER`, `INTERMEDIATE` and `ADVANCED` combined. `초중급` and `중고급` map to them and must
not be collapsed into their neighbours. `DIFFICULTY` is not part of the natural key, so this
stays a cheap update — but only while a course is still `enabled: false`.

**Three things this tree cannot finish on its own.** All need `re-speak/podo-curriculum`,
whose `schemas/` reject unknown fields, so none of them may be guessed at from here:

1. **A `COVER` row per course.** `course.yaml` carries a course title and description but
   states no `BOOK_TYPE`. If the exporter writes only `MAIN` rows, the course title never
   reaches a screen no matter how well it is written. Verify before treating this as done.
2. **A lesson-level `DESCRIPTION`.** Every live `MAIN` row has one; ours have none.
   `lesson.yaml` already carries `teaches.canDo`, which is the right sentence in Korean — the
   missing pieces are a schema field to put it in and its `ja`/`en` siblings for 494 lessons.
3. **The `"N. "` title prefix.** Live rows store it, in all three languages, matching
   `CLASS_WEEK`; 100% of BEGINNER and ADVANCED rows carry it. Prepend it **at export from
   `CLASS_WEEK`**, not in the deck — a course re-cut would otherwise rot every baked number by
   hand. Topic-pick courses (Smart Talk, role-play) are never numbered, so the rule is
   per-course, not global.

## Interactive lessons

Anything the learner taps, types, or drags — and anything that has to stay in step with the
tutor's screen — goes through lemonboard's `data-sync` contract.

**Reuse an existing activity and the contract comes with it** — copy the markup from
[`AUTHORING.md`](./AUTHORING.md) or from a live deck in `trial/lessons/`, `data-sync`
attributes and all, and there is nothing further to read. This is the normal case, and it is
why building a lesson out of the existing component vocabulary is cheaper *and* safer than
inventing markup.

**Read [`interaction-protocol.md`](./interaction-protocol.md) only when
you are inventing a new interaction type** — a new `data-sync-kind`, a new way of sharing state,
anything not already in the vocabulary. Getting it wrong there fails silently: the activity
works on your screen and never reaches the other person. Packaging a deck into an uploadable
zip is not this repo's job — `podo-curriculum` does it in `tools/build.py`.

Two rules that catch most mistakes: an element is shared **only** if it has a `data-sync-id`
(no id = private), and verdicts are never shared — send the choice and let each side derive
`correct`/`wrong` locally. Note that this does *not* hide the answer key: both people load the
same document, so anything in the markup is already on the learner's screen.

## Layout

- **`tracks/`** — the learner-facing curriculum, in learning order: `1-hangul` · `2-core-patterns` ·
  `3-contextual-korean` · `4-freetalking` (pronunciation joins as `5-pronunciation` once it has content).
  Each track holds `table-of-contents.md`, the generated `toc/` briefs, `lesson-blueprint.md`,
  and its lesson HTML. Nothing else — retired drafts live outside this folder, see **Archive**.

  **The trial deck is the source of truth, not the sample.** `trial/lessons/trial-N-*.html` is
  the deck that gets maintained; each track's `sample-lesson.html` is that deck **with the sales
  pages cut** — cover, greeting, trial-intro, todays-result and closing come off, everything
  pedagogical stays. So the samples are full paged decks, not scrolling documents: same
  skeleton, same stylesheets, same scripts, and the shared art still comes from
  `../../trial/assets/`. When a trial lesson changes, re-cut its sample rather than editing both
  by hand — and when the two disagree, **the trial deck wins.** The first surviving page needs
  its own `data-act`; the act name used to come from the cover's `.brand-title`.
- **`trial/`** — sales trial material, not a learning track. `full-trials/` holds the four complete
  decks (`trial-1..4`), `lessons/` holds the standalone lesson decks cut from them
  (`trial-1-hangul-short.html`, `trial-2-patterns-short.html`, `trial-3-contextual-short.html`),
  and `reports/` holds the trial report deck. Plus shared `assets/` (art, mouth, characters).

  **A deck is markup plus shared scripts — no per-deck CSS or JS.** Load them in this
  order: `activities` → `pager` → `script-lines` → `spotlight` → `tutor-notes`
  → `highlight` → `stamp`. The order is load-bearing (see the comments at each tag).
  A hangul deck adds `hangul-activities`, a freetalk deck adds `freetalk-activities`,
  both directly after `activities`. A deck ships **no inline script and no inline CSS**
  of its own — if you are writing either, the thing you need probably belongs in a
  shared module or in `trial.css`.

  **The report's recommendation is a spec, not a guess.** How the trial report gets to
  「N개월 · 이 코스들」 — the lesson counts it draws on, the level ladder, the duration
  formula and its **5-month floor** (a sales policy, not a calculation), and how level ×
  goal × reason pick the courses — lives in [`trial/plan-logic.md`](./trial/plan-logic.md).
  The code for all of it is `runtime/js/report.js`; when the two disagree, the doc wins.
  Read it before touching any number in that file.

  **Read [`AUTHORING.md`](./AUTHORING.md) before building a new deck.** It is
  the component vocabulary — page types, every activity's markup, the colour and spacing
  tokens, and the file skeleton. Reach for an existing component before inventing one.
- **`../runtime/`** — **at the repo root, not in this folder.** Everything a deck loads at run
  time: `css/` (the design system plus each track's sheet) and `js/` (the shared modules). It sits
  above both language folders because Korean and English decks load the same runtime, and it is
  the publish set — mirrored to a public repo and served from a CDN — so nothing private may live
  in it. See [`../runtime/README.md`](../runtime/README.md).

  **`trial/assets/` did not move** and is still inside `korean/`, so a deck's `../` count differs
  by one between the two. A lesson deck reaches the runtime with seven `../` and the assets with
  six; `new_lesson.py` handles the difference, but a hand-edited path will not.
- **`interaction-protocol.md`** — the `data-sync` contract. Documentation only; the code
  decks load lives in `runtime/`. Packaging a deck for upload is not done here at all —
  `podo-curriculum` owns it (`tools/build.py`), because the zip is a deploy artefact and
  building one by hand is how a stale deck reaches a classroom.
- **`tools/`** — authoring scripts. `build_lesson_briefs.py` (all TOCs → course-aware textual
  briefs; delegates Core to its richer `shard_toc.py`), `new_lesson.py` (deck skeleton) and
  `build_catalog.py` (five TOCs → `catalog.html`). All three derive their
  output from files that already exist, so none holds a second copy of anything.
  The `check_*` scripts verify a written deck — see 「Checking a deck you just wrote」 above.
  They only read, take deck paths as arguments, and find the repo from their own location,
  so they run from anywhere.
- **`references/`** — source textbook scans (internal reference only).
- **Archive — deliberately not here.** Retired drafts, design variations and capture files live in
  `_archive/` at the *repo* root, under their original paths. They are kept for history and are
  **not part of the read path**: never cite one as precedent, never copy markup out of one, and
  don't search them when looking for how something is done. If a grep turns up an `_archive/`
  hit, the live answer is elsewhere in `korean/`.
- `index.html` here is this curriculum's navigation. **`viewer.html` and `ux-philosophy.md` are at
  the repo root now**, shared with English — the viewer rejects any `?doc=` containing `..`, so its
  links from here read `../viewer.html?doc=korean/<path>`. `AGENTS.md` stays in this folder as the
  canonical Korean instructions, and `CLAUDE.md` imports it for Claude Code.
- **`catalog.html` + `catalog/` are generated — never hand-edit them.** `catalog.html` is the
  gateway (hero, five track cards, 완성된 레슨 덱, level ladder); `catalog/<track>.html` is that
  track's full contents — every 과, what it teaches, and the pattern marked inside its own example
  sentence. All six pages are built from the five `table-of-contents.md` files by
  `tools/build_catalog.py`, out of `tools/gateway_template.html` and `tools/track_template.html`.
  They hold no facts of their own, so a wrong number there is a wrong number in a TOC. Re-run
  `python3 korean/tools/build_catalog.py` after any TOC change, alongside
  `build_lesson_briefs.py`.

  **Written decks link straight out of the catalog, and the disk decides which ones.** The build
  walks `tracks/<track>/courses/*/lessons/*/lesson.html` and counts a 과 as written only if its
  deck has at least one page (`data-act`) — `new_lesson.py` leaves page-less skeletons behind, and
  without that test dozens of empty 과 would advertise themselves as finished. Which 과 a deck
  belongs to comes from the `✓ <슬러그><제목>` line in its `course.yaml` (트랙 3·4 restart lesson
  numbers per course, so the slug's number cannot say it); if that line is stale the build prints
  `! 목차에서 못 찾은 덱` and the fix is to re-run `plan_courses.py`. Written 과 get a **덱 열기**
  link on their row and a chip in the gateway's 완성된 레슨 덱 band — both `target="_blank"`, so
  opening a deck never costs you the catalog.

  **The colour rules are the point, not decoration.** Each track owns one accent, validated as a
  categorical palette (`dataviz` skill's `validate_palette.js`), and that accent appears only in
  the top three levels of the hierarchy — track title, band heading, unit chip. Below that
  everything is ink and hairlines, because the one saturated thing inside an open 과 has to be
  the peach `mark` on the taught pattern (`--pat-mark`/`--pat-ink`, lifted from the decks'
  `--ending-*`). Paint the fourth level too and that mark stops reading.
