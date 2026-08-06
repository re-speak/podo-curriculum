# Working in podo-curriculum

This repo deploys. A merge to `main` changes what a learner sees in a live class,
so the bar is closer to `podo-database-schema` than to a docs repo.

## Before touching a deck

**Read [`shared/ux-philosophy.md`](shared/ux-philosophy.md) — every time, including
small edits.** It is the contract for every lesson page: one activity per page,
instant clarity, minimal everything, Korean-first titles, one blue tutor-script
box, one boxed component that *fills* the page, receptive → productive.

If a change you are about to make conflicts with it, say so and ask — don't
quietly deviate.

## Also true here

- **Shared design system:** `shared/css/lesson-card.css`. The palette lives in `:root` — **use the tokens, never the hex.** Reuse the existing component vocabulary before inventing one.
- **Every colour means one thing.** `green-500`/`green-100` = state. `blue-100` = the tutor's spoken script. `lime` = brand chrome only, never state. `gray-200` = ordinary outlines. Dashed grey = "write here".
- **Audience is Japanese speakers learning Korean.** All support text is Japanese; no English. Sound anchors are kana.
- **Lessons are audio-only.** The learner hears the tutor but never sees them, so no instruction may depend on watching (口の形をまねして, gestures, "look at me").
- **Max two levels of boxes:** the page card plus ONE boxed component inside it.
- Every page needs `<meta name="google" content="notranslate">` or Chrome mangles the mixed ja/ko content.
- **Verify visually.** These are visual documents — render at 480px and look at the screenshots before claiming a change works.

## Interactions

Anything the learner taps, types or drags goes through lemonboard's `data-sync`
contract — [`shared/interaction-protocol.md`](shared/interaction-protocol.md).
Getting it wrong fails silently: it works on your screen and never reaches the
other person. Copy from `shared/reference-lesson.html` rather than inventing markup.

Two rules catch most mistakes: an element is shared **only** if it has a
`data-sync-id` (no id = private), and verdicts are never shared — send the choice
and let each side derive `correct`/`wrong` locally.

## Things that will bite you

- **`classLevel` / `lessonTime` are identity.** grape matches a row by
  `(CLASS_TYPE, LANG_TYPE, CURRICULUM_TYPE, LESSON_TIME, CLASS_LEVEL, CLASS_WEEK)`.
  Change either and you get a *different* course — the old rows stay. That is intended;
  a 15-minute Level 3 and a 25-minute Level 3 are different products. Retire with `enabled: false`.
- **There is no state lock.** Identity lives in the DB's natural key, so nothing is written back to git.
- **Both deck slots are mandatory.** A lesson with only 수업용 fails class creation at `/rooms/null/duplicate`.
- **`sandbox/` cannot deploy** — `tools/model.py` only walks `courses/`. Put speculative work there; promoting it is the move into `courses/`.
- **Run `python3 tools/validate.py` before pushing.** It catches the things that otherwise 404 from S3 while the build prints success.

## Not in scope

The PDF pipeline (page images, `podo-pdf-tool`, `BOOK_FILE_ID`, audio via
`TB_COM_FILE`). Grape still owns it for legacy courses. This repo is HTML 교재 only.
