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

## Interactions — the `data-sync` contract

**The implementation in lemonboard is the SSOT.** Not this file, not what a nearby
deck happens to do. When they disagree, lemonboard wins:

- `apps/web/src/views/meet/lib/html-sync/protocol.ts` — the attributes
- `apps/web/src/views/meet/lib/html-sync/kinds.ts` — the built-in kinds and the inference
- `apps/api/src/modules/lesson-html/handlers/v1/validate-lesson-html.ts` — the validator CI calls

Getting it wrong **fails silently**. The activity works on your screen, the other
person never sees it, and nothing errors. That is the whole reason the contract
check is a merge gate rather than advice.

### The four attributes

| Attribute | Meaning |
|---|---|
| `data-sync-id` | Marks the element as shared **and** is the sync key. No id = private, never shared. |
| `data-sync-kind` | Names the kind explicitly. Omit only if the inference below is unambiguous. |
| `data-sync-option` | Marks a descendant as a choice for `selection`. **The attribute's value is the option id.** |
| `data-sync-state` | Space-separated classes that count as "active" (e.g. `"right wrong"`). Defaults to `selected`. |

### The three built-in kinds

- **`value`** — a form control's value. `INPUT` / `TEXTAREA` / `SELECT` only.
  Applying dispatches `input` and `change` so the page's own grading listener runs.
- **`toggle`** — whether the element itself carries an active class. Applied by clicking it.
- **`selection`** — the set of active `[data-sync-option]` descendants. Covers single and
  multi select; single select is just a set with capacity one, enforced by the page's own
  click handler. Applied by clicking only the options that differ.

Anything these cannot express, the deck brings itself via
`window.lessonSync.register('<kind>', { read, apply })`.

### How kind is resolved

```
data-sync-kind present            → use it
element is INPUT/TEXTAREA/SELECT  → value
has a [data-sync-option] descendant → selection
has a data-sync-state attribute   → toggle
otherwise                          → NOT SYNCED (this is the failure)
```

That last line is the one that bites. An element with `data-sync-id` and nothing
else is dropped from the sync set — no warning, no error, just two screens that
quietly disagree.

### Write the real control into the HTML — never promote a shell at runtime

**A synced element must already be what it claims to be when the file is parsed.** Do not
write a `<span>` placeholder and swap it for an `<input>` on load, even if you carry the
`data-sync-id` across.

The validator parses statically — `parseHTML(html)` via linkedom, no scripts run
(`apps/api/src/modules/lesson-html/handlers/v1/validate-lesson-html.ts`). The binder does
the opposite: it re-scans the live DOM on every publish (`html-sync/binder.ts`,
`collectTargets`). So a promoted shell *works in class* and *fails the gate* — the deck
looks broken to CI while behaving fine, and you cannot tell that apart from a deck that is
genuinely broken. Keep the two views identical and the question never comes up.

If the learner types, ship an `<input>` or `<textarea>`. If they pick, ship the options with
`data-sync-option`. If neither can express it, `register()` a kind and name it with
`data-sync-kind` in the markup so the validator sees a name it can resolve.

- **Count your ids against your kinds.** Every `data-sync-id` must land on one of the four
  resolution rules above. An id that resolves to nothing is silently private.
- **Share the choice, never the verdict.** Send which option is selected and let each side
  derive `correct`/`wrong` locally. State is shared as a snapshot, not as events, so a late
  joiner or a refresh converges from one message.

### Before you push

```sh
python3 tools/validate.py --contract --env stage
```

`--contract` runs the deck through lemonboard's own validator — the same call CI makes.
It fail-opens on network trouble and 5xx (a lemonboard outage must not block a PR) but
blocks on any `severity: error`. Without `PODO_LEMONBOARD_API_KEY` it refuses to run rather
than letting an auth rejection read as a clean pass.

Copy from a deck that passes the gate rather than inventing markup —
[`courses/kr/taiken-trial/lessons/06-taiken-self-intro`](courses/kr/taiken-trial/lessons/06-taiken-self-intro)
carries all four shapes (typed blank, write-in area, tap-one-of-two, order-the-chips) with
the controls written straight into the HTML.

## Things that will bite you

- **`classLevel` / `lessonTime` are identity.** grape matches a row by
  `(CLASS_TYPE, LANG_TYPE, CURRICULUM_TYPE, LESSON_TIME, CLASS_LEVEL, CLASS_WEEK)`.
  Change either and you get a *different* course — the old rows stay. That is intended;
  a 15-minute Level 3 and a 25-minute Level 3 are different products. Retire with `enabled: false`.
- **There is no state lock.** Identity lives in the DB's natural key, so nothing is written back to git.
- **Both deck slots are mandatory.** A lesson with only 수업용 fails class creation at `/rooms/null/duplicate`.
- **`sandbox/` cannot deploy** — `tools/model.py` only walks `courses/`. Put speculative work there; promoting it is the move into `courses/`.
- **Run `python3 tools/validate.py` before pushing.** It catches the things that otherwise 404 from GCS while the build prints success.

## Not in scope

The PDF pipeline (page images, `podo-pdf-tool`, `BOOK_FILE_ID`, audio via
`TB_COM_FILE`). Grape still owns it for legacy courses. This repo is HTML 교재 only.
