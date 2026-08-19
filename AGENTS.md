# Working in podo-curriculum

This repo deploys. A merge to `main` changes what a learner sees in a live class,
so the bar is closer to `podo-database-schema` than to a docs repo.

## The branch is the environment

Every change ships through the same four steps. There is no other path — the two
merges *are* the two deploys.

```sh
# 1. branch off stage, PR into stage
git fetch origin && git switch -c feat/my-lesson origin/stage
python3 tools/validate.py --contract --env stage
git push -u origin feat/my-lesson && gh pr create --base stage

# 2. merge → podo-curriculum-deploy-stage applies to stage, automatically
# 3. gh pr create --base main --head stage        ← the release PR
# 4. merge → podo-curriculum-deploy-prod applies to prod, automatically
```

- **Work branches off `origin/stage`, and the PR's base is `stage`.** Merging to
  `stage` deploys to stage, automatically — there is no button.
- **Stop at stage and look.** Step 2 is the only environment where a mistake is
  cheap; don't open the release PR until stage is verified.
- **`main` is prod.** The `stage → main` PR is the release; merging it changes what a
  learner in a live class sees, immediately. Review that PR as a deploy approval,
  because that is what it is.
- **Don't branch off `main`, and never PR straight into it.** It lags `stage` by
  whatever has been merged but not yet released, so you would be writing against
  content the next release replaces — and you would skip stage entirely.

## Where lessons are written

Lessons are written **in this repository**, under `sandbox/drafts/<code>/`, and
promoted into `courses/` when they are ready. `podo-curriculum-public` was the
authoring repo until 2026-08-19; it is now a frozen archive holding only the
licensed textbook scans, and nothing syncs from it.

```sh
vim sandbox/drafts/kr/tracks/…/lessons/<NN-slug>/lesson.html   # write
python3 tools/authoring/kr/check_structure.py                  # check
python3 tools/promote.py --check                               # see what would ship
python3 tools/promote.py                                       # write courses/
python3 tools/repoint-shared.py && python3 tools/validate.py    # pin + gate
```

- **`tools/authoring/{kr,en}/`** holds the checkers, the lesson scaffolder
  (`new_lesson.py`), course planning and the brief/catalog builders. Run them
  against the drafts, not `courses/`.
- **Promotion is named in a manifest**, `promotion.yaml`, sitting beside the
  drafts. Adding a lesson to a course means adding a row there — that row is the
  reviewable part.
- **Never edit `courses/` by hand.** `promote.py` owns every `lessons/` directory
  it writes and clears it on each run, so a hand edit is lost on the next
  promotion without anything reporting it.

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

## The shared runtime is on a CDN, pinned by tag

Decks no longer carry their own copy of `shared/{css,js}`. They point at an
immutable tag on a public mirror, declared once in `curriculum.yaml`:

```yaml
spec:
  sharedRuntime:
    baseUrl: https://cdn.jsdelivr.net/gh/re-speak/podo-curriculum-shared
    repo: re-speak/podo-curriculum-shared
    version: v1.0.0
    join: "@"
```

**Publish before you repoint, and repoint before you PR.** The order is the whole
design — a tag has to be live before a deck naming it ships:

```sh
# only when you have touched shared/
vim curriculum.yaml                      # bump spec.sharedRuntime.version
python3 tools/publish-shared.py          # cut + push the tag, verify it serves
python3 tools/repoint-shared.py          # stamp every deck with the new version
python3 tools/validate.py --env stage    # layer 5 proves the pins are live
```

Do it the other way round and `main` briefly holds decks pointing at a tag nobody
pushed. That is a 404 for every activity, in class, on the learner's screen only.

- **Tags are immutable.** `publish-shared.py` refuses to move one. If `shared/`
  changed, bump the version — never re-cut the same tag, because a deck already
  pinned to it would change underneath a live class.
- **Append-only still holds.** Old decks stay on old tags and are unaffected by
  anything you add. That is what makes a version bump safe rather than a migration.
- **Never pin a branch.** `@main` is re-checked every 12 hours and edges disagree
  during the window — some learners get the new file, some the old, same lesson.
  Only a tag is cached as immutable.
- **A deck may opt out.** One that still bundles its own runtime has no URL on this
  host and is simply not checked. `taiken-trial` is on that path deliberately.

`validate.py` layer 5 blocks two silent failures: a pin whose tag was never
published (404), and a `shared/` that moved on without the tag being re-cut (byte
mismatch). It fail-opens on 5xx and network trouble, like the contract check.

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

- **`classLevel` / `lessonTime` / `countryCode` are identity.** grape matches a row by
  `(CLASS_TYPE, LANG_TYPE, CURRICULUM_TYPE, LESSON_TIME, CLASS_LEVEL, CLASS_WEEK, COUNTRY_CODE)`.
  Change any of them and you get a *different* course — the old rows stay. That is intended;
  a 15-minute Level 3 and a 25-minute Level 3 are different products. Moving a live course
  takes two deploys: first retire the old identity with `enabled: false`, then change the
  identity and re-enable it.
- **There is no state lock.** Identity lives in the DB's natural key, so nothing is written back to git.
- **Both deck slots are mandatory.** A lesson with only 수업용 fails class creation at `/rooms/null/duplicate`.
- **`sandbox/` cannot deploy** — `tools/model.py` only walks `courses/`. Put speculative work there; promoting it is the move into `courses/`.
- **Deleting a course does not retire it.** `apply.py` is a pure upsert with no
  delete path — it never reads back from grape and never removes a row. A course
  deleted from `courses/` keeps `USE_YN='Y'`, keeps pointing at content nobody
  updates, and the learner keeps seeing it while the deploy goes green. Set
  `enabled: false`, let that deploy, *then* delete the directory. `promote.py`
  stops and offers to write the flag for you; `validate.py` layer 6 fails the PR
  if you go around it.
- **Run `python3 tools/validate.py` before pushing.** It catches the things that otherwise 404 from GCS while the build prints success.

## Not in scope

The PDF pipeline (page images, `podo-pdf-tool`, `BOOK_FILE_ID`, audio via
`TB_COM_FILE`). Grape still owns it for legacy courses. This repo is HTML 교재 only.
