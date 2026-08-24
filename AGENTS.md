# Working in podo-curriculum

This repo deploys. A merge to `main` changes what a learner sees in a live class,
so the bar is closer to `podo-database-schema` than to a docs repo.

## The branch is the release boundary

Every change ships through the same four steps. There is no other path — the two
merges *are* the two deploys. Four environments, two branches: `stage` fills the
three non-production ones in one build, `main` is prod.

```sh
# 1. branch off stage, PR into stage
git fetch origin && git switch -c feat/my-lesson origin/stage
python3 tools/validate.py --env stage
git push -u origin feat/my-lesson && gh pr create --base stage

# 2. merge → podo-curriculum-deploy-stage applies to stage, qa, dev — automatically
# 3. gh pr create --base main --head stage        ← the release PR
# 4. merge → podo-curriculum-deploy-prod applies to prod, automatically
```

- **Work branches off `origin/stage`, and the PR's base is `stage`.** Merging to
  `stage` deploys to stage, qa and dev, automatically — there is no button.
- **Stop before the release PR and look.** Step 2 covers the only environments
  where a mistake is cheap; don't open the release PR until you have verified in one.
- **Verify in qa or dev, not stage, when it has to survive the night.** stage is a
  prod clone that is overwritten from prod every morning, which resets
  `CLASS_LEMONBOARD_KEY` to prod's room ids. qa and dev keep their own data.
- **There is no qa or dev lemonboard.** All three non-production environments share
  the stage one (`getPodoEnv() != "prod"`), so their rooms sit side by side under
  identical names. What separates their content is the `-{env}` prefix in `contentUrl`.
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
python3 tools/make-promotion.py <course-draft-dir> --force     # refresh promotion.yaml
python3 tools/promote.py --check                               # see what would ship
python3 tools/promote.py                                       # write courses/
python3 tools/repoint-shared.py && python3 tools/validate.py    # pin + gate
```

- **`tools/authoring/`** holds the checks that are true of both curricula —
  `check_deck.py`, `check_quotes.py`, `vocabulary.py`, `page_review.py`. Run them
  against either corpus; `--all` walks the whole repo. **`tools/authoring/{kr,en}/`**
  holds what is genuinely language-specific, plus the lesson scaffolder
  (`new_lesson.py`), course planning and the brief/catalog builders. Run all of them
  against the drafts, not `courses/`. **A new check goes in the shared directory
  unless it cannot be written for the other language** — filing a general check under
  one language is how the last round of duplicated rules started.
- **Promotion is named in a manifest**, `promotion.yaml`, sitting beside the
  drafts. Adding a lesson to a course means adding a row there — that row is the
  reviewable part. `tools/make-promotion.py` derives the whole file from the decks
  that exist: the week is a deck's position in the list and the three titles come
  from its own `<meta name="podo:title-*">`, so nothing in the manifest is typed
  twice. It refuses to overwrite an existing one without `--force`, and refuses to
  guess a title a deck does not declare.
- **Promotion copies; the draft stays put.** `promote.py` only ever reads
  `sandbox/`. The one directory it clears is `courses/<lang>/<slug>/lessons/`, its
  own output — so the draft survives promotion, remains the thing you edit, and
  re-promoting after a fix is the whole update path.
- **A new course needs its `courses/` target to exist first.** `promote.py` refuses
  a target with no `course.yaml`, which is what keeps a course's identity and its
  `enabled` flag a human act rather than a side effect. `make-promotion.py
  --scaffold-target` copies the draft's `course.yaml` into place, and will not do it
  for a draft that is already `enabled: true`.
- **Never edit `courses/` by hand.** `promote.py` owns every `lessons/` directory
  it writes and clears it on each run, so a hand edit is lost on the next
  promotion without anything reporting it.

## Before touching a deck

**Read [`shared/ux-philosophy.md`](shared/ux-philosophy.md) plus the delta file for
the language you are working in — every time, including small edits.**

- [`shared/ux-philosophy.md`](shared/ux-philosophy.md) — the language-neutral
  contract for every lesson page: one activity per page, instant clarity, minimal
  everything, target-language-first titles, one blue tutor-script box, one boxed
  component that *fills* the page, receptive → productive.
- [`shared/deltas-kr.md`](shared/deltas-kr.md) — Korean for Japanese speakers.
- [`shared/deltas-en.md`](shared/deltas-en.md) — English for Japanese speakers.

A delta is a consequence of the target language changing, never a matter of taste.
**A rule that would be just as true of the other language belongs in
`ux-philosophy.md`.** That split is the whole point of the three files: the contract
was a Korean document with an English appendix until 2026-08-22, so an English
learning had nowhere to flow back to, and both curricula spent a week re-deriving
each other's rules a day apart and disagreeing on the details.

If a change you are about to make conflicts with any of the three, say so and ask —
don't quietly deviate.

## Also true here

- **Shared design system:** `shared/css/lesson-card.css`. The palette lives in `:root` — **use the tokens, never the hex.** Reuse the existing component vocabulary before inventing one.
- **Every colour means one thing.** `green-500`/`green-100` = state. `blue-100` = the tutor's spoken script. `lime` = brand chrome only, never state. `gray-200` = ordinary outlines. Dashed grey = "write here".
- **Two curricula, one audience.** Japanese speakers learning **Korean** (`courses/kr`,
  `sandbox/drafts/kr`) and Japanese speakers learning **English** (`courses/en`,
  `sandbox/drafts/en`). Support text is Japanese in both; the target language is whichever
  the deck teaches. Kana sound anchors are a Korean-only device — kana over English installs
  the error instead of scaffolding it, so English decks carry none at any level.
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
python3 tools/validate.py --env stage          # deployability
python3 tools/authoring/check_deck.py sandbox/drafts   # content, both languages
```

Both local gates are mandatory, and both now run as a required PR check —
`validate.py` covers deployability (schema, packaging, the `data-sync` contract,
CDN pins, retirement) and the `authoring-gate` step covers content: the shared
deck checks, English corpus integrity, and the Korean checkers that make an
assertion rather than surface a candidate.

**The content gate is new as of 2026-08-22, and its absence is why rules stopped
at whichever language their author was working in.** A check that does not block
a merge reaches exactly as far as somebody remembered to run it. `check_quotes.py`
is deliberately still advisory — the citation convention was only just extended to
English and predates most of both corpora, so gating it today would block every PR.

This local gate is mandatory. The authenticated contract gate is authoritative in the PR:
`podo-curriculum-validate` runs lemonboard's own validator automatically for every PR into
`stage` or `main`, using its repository-managed secret, and blocks the merge on any
`severity: error`.

If your current shell already has `PODO_LEMONBOARD_API_KEY`, you may run the same check
early with `python3 tools/validate.py --contract --env stage`. Do not stop, ask the user to
paste a key, or search secret files merely because that optional local credential is absent.
Open the PR and let its required check own the authenticated verdict.

Copy from a deck that passes the gate rather than inventing markup —
[`courses/kr/trial-lv2-patterns/lessons/01-trial-patterns`](courses/kr/trial-lv2-patterns/lessons/01-trial-patterns)
carries all four shapes (typed blank, write-in area, tap-one-of-two, order-the-chips) with
the controls written straight into the HTML.

## Things that will bite you

- **`classLevel` / `lessonTime` / `countryCode` are identity.** grape matches a row by
  `(CLASS_TYPE, LANG_TYPE, CURRICULUM_TYPE, LESSON_TIME, CLASS_LEVEL, CLASS_WEEK, COUNTRY_CODE)`.
  Change any of them and you get a *different* course — the old rows stay. That is intended;
  a 15-minute Level 3 and a 25-minute Level 3 are different products. Moving a live course
  takes two deploys: first retire the old identity with `enabled: false`, then change the
  identity and re-enable it.
- **A course is named three times, and the learner reads only one of them.**
  `GT_CLASS_COURSE` keeps `BOOK_NAME` (ko), `EN_BOOK_NAME` and `JP_BOOK_NAME`, and the app
  picks by the learner's locale — so for a `countryCode: JP` course, `spec.title.ja` is the
  string on screen and `ko` is grape's admin label. `spec.description` is the same shape and
  is learner-facing prose, not a note to yourself: it becomes the course's tagline under the
  title. Fill all three languages of both. `tools/apply.py` sends whatever is there, including
  nothing.
- **`difficulty` is a five-value enum that nothing validates.** `BEGINNER`,
  `UPPER_BEGINNER`, `INTERMEDIATE`, `UPPER_INTERMEDIATE`, `ADVANCED` — but
  `schemas/course.schema.json` types it as a bare string, so `Upper beginner` passes
  validation, deploys, and reaches grape as a band the app does not know. The two middle
  values carry more of the live catalogue than the other three combined; do not collapse them
  into their neighbours. The full convention, and how each track maps onto it, is in
  `sandbox/drafts/kr/AGENTS.md` and `sandbox/drafts/en/AGENTS.md`.
- **Lesson rows ship a title but no description.** Every course in the live catalogue gives
  each lesson a one-line can-do; ours send `slug`, `week`, `title` and `decks` only. Live rows
  also carry an `"N. "` prefix matching `CLASS_WEEK`, which nothing here adds. Both are open
  work, written up under *What still has no path to a learner* in `sandbox/drafts/kr/AGENTS.md`.
- **There is no state lock.** Identity lives in the DB's natural key, so nothing is written back to git.
- **Both deck slots are mandatory.** A lesson with only 수업용 fails class creation at `/rooms/null/duplicate`.
- **`sandbox/` cannot deploy** — `tools/model.py` only walks `courses/`. Put speculative work there; promoting it is the move into `courses/`.
- **Deleting a course does not retire it.** `apply.py` is a pure upsert with no
  delete path — it never reads back from grape and never removes a row. A course
  deleted from `courses/` keeps `USE_YN='Y'`, keeps pointing at content nobody
  updates, and the learner keeps seeing it while the deploy goes green. Set
  `enabled: false`, let that deploy, *then* delete the directory. `promote.py`
  stops and offers to write the flag for you; `validate.py` layer 6 fails the PR
  if you go around it. When the rows cannot be deleted at all — class history
  hangs off them — clean up the rows and GCS objects by hand and declare it with a
  `Retired-course: courses/<code>/<slug>` trailer on a commit in the PR.
- **Run `python3 tools/validate.py` before pushing.** It catches the things that otherwise 404 from GCS while the build prints success.

## Not in scope

The PDF pipeline (page images, `podo-pdf-tool`, `BOOK_FILE_ID`, audio via
`TB_COM_FILE`). Grape still owns it for legacy courses. This repo is HTML 교재 only.
