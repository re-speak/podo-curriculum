# podo-curriculum

The curriculum, as code. What is on `main` is what is live — merge a lesson and it
deploys itself, the way `podo-database-schema` does for the DB schema.

```
courses/kr/hangul-lv1/lessons/01-block-and-first-sounds/lecture/index.html
        │  │          │                                 └── 수업용 deck  → CLASS_LEMONBOARD_KEY
        │  │          └── one lesson = one GT_CLASS_COURSE MAIN row (CLASS_WEEK=1)
        │  └── one course = a COVER row + its MAIN rows
        └── the directory name IS LANG_TYPE
```

## Current status

**All four environments deploy from this repo, and the curriculum is written in
it.** Merging to `stage` applies to stage, qa and dev; merging `stage → main`
applies to prod. Neither has a button — see
[How a change reaches a learner](#how-a-change-reaches-a-learner). The grape sync
endpoint the whole thing rests on is specified in
[`docs/sync-contract.md`](docs/sync-contract.md).

Authoring moved here on 2026-08-19. `podo-curriculum-public` was the upstream for
`shared/`, the drafts and the references; it is now a frozen archive that exists
only to hold the licensed textbook scans, which are too large and too private to
live in a public repository. Nothing syncs from it, and the tool that used to has
been deleted rather than deprecated — see
[Writing a lesson](#writing-a-lesson).

## Layout

| Path | What it is |
|---|---|
| `curriculum.yaml` | languages, environments, repo-wide constants |
| `courses/<lang>/<course>/` | **deployable.** `course.yaml` + `lessons/<NN-slug>/` |
| `shared/` | the deck runtime — `lesson-card.css` + `trial.css`, thirteen activity/chrome scripts, and the design contract. **The source, and served to decks from a CDN rather than copied into them** |
| `schemas/` | JSON Schema for the three document kinds |
| `tools/` | build · validate · plan · apply, the shared-runtime pair (`publish-shared` · `repoint-shared`), and the promotion pair (`make-promotion` · `promote`) |
| `tools/authoring/{kr,en}/` | the authoring toolchain — deck checkers, lesson scaffolding, course planning, brief and catalog builders |
| `sandbox/drafts/` | **where lessons are written.** The complete curriculum under authoring, committed, reviewable, and structurally undeployable |
| `sandbox/archive/` | experiments and retired material |
| `references/` | durable source material: textbook pattern maps and research |
| `docs/` | the sync contract |

### `sandbox/` is not a convention

`tools/model.py` discovers courses by walking `courses/` and nothing else. There
is no flag or env var that widens it, so an experiment cannot reach production by
being renamed, symlinked or copied into the wrong place. Put anything speculative
there and it stays reviewable in git without ever being a deploy candidate.

Move it into `courses/` when it is real. That move is the promotion.

## The three documents

```yaml
# curriculum.yaml — one per repo
spec:
  languages: { kr: { langType: KR, audience: ja } }
  environments: { stage: {…}, prod: {…} }
```

```yaml
# courses/kr/hangul-lv1/course.yaml — the COVER row
metadata: { slug: hangul-lv1 }
spec:
  curriculumType: BASIC          # BASIC | SMART_TALK | TRIAL
  classLevel: "1"                # quoted — 1.10 must not become 1.1
  lessonTime: 25                 # 15 | 25 | 55 (55 = 체험/TRIAL)
  enabled: false                 # USE_YN
  title: { ko: 한글 떼기, en: Hangul Basics, ja: ハングル入門 }
  thumbnail: assets/cover.png    # optional — BOOK_THUMBNAIL, see below
  tutorGroups: { allowRandom: [], assignedOnly: [] }
```

`thumbnail` is the one field whose absence is not a statement. Name a
course-relative PNG or JPEG and it ships with the decks: grape uploads it and
writes the URL to `BOOK_THUMBNAIL` on the COVER row, overwriting whatever was
there. Leave the key out and the column is **not touched** — covers are also
uploaded by hand in grape admin, and a course that says nothing about its cover
must not delete one. Removing a cover is therefore an admin action, not a commit.

```yaml
# …/lessons/01-block-and-first-sounds/lesson.yaml — one MAIN row
metadata: { slug: 01-block-and-first-sounds }
spec:
  week: 1                        # CLASS_WEEK, contiguous from 1
  title: { ko: 블록과 첫 소리, … }
  decks:
    lecture:  { entry: lecture/index.html }
    prestudy: { entry: prestudy/index.html }
  teaches: {…}                   # repo-only. Never reaches the DB.
```

Everything under `teaches` / `outcome` / `prerequisites` exists so a curriculum
change reads as a diff a content person can review, instead of as a blob of HTML.

## What identifies a course

grape resolves a row by its **natural key**:

```
(CLASS_TYPE, LANG_TYPE, CURRICULUM_TYPE, LESSON_TIME, CLASS_LEVEL, CLASS_WEEK, COUNTRY_CODE)
```

Verified unique across 3,514 prod rows (SMART_TALK excluded — it has 18 duplicate
groups of its own, unrelated to this repo). A COVER row is simply `CLASS_WEEK=0`.

So nothing here has to remember what the last apply created. There is no lock
file and no write-back step — which is what used to turn a failed apply into a
duplicate course on the next run.

The consequence: **changing `classLevel`, `lessonTime`, or `countryCode` makes a different
course**, because it is one. The old rows stay; retire them with
`enabled: false`. A directory slug is still permanent by convention — it is what
a human uses to find the course — but it is no longer what the DB matches on.
Moving a live course therefore takes two deploys: disable the old identity first,
then change the identity and re-enable it.

## Working locally

```sh
pip install -r tools/requirements.txt

python3 tools/validate.py                      # schema + structure + packaging
python3 tools/validate.py --contract           # …plus lemonboard's data-sync validator
python3 tools/plan.py --env stage              # what apply would do
python3 tools/build.py courses/kr/hangul-lv1/lessons/01-block-and-first-sounds/lecture/index.html \
        --out /tmp/deck                        # one deck, to inspect the zip

python3 tools/build-catalog.py                 # the public catalog → site/
python3 -m http.server -d site 8000            # …look at it

python3 tools/make-promotion.py --lang en      # derive promotion.yaml from the decks
python3 tools/promote.py --check               # what promotion would change
python3 tools/promote.py                       # promote every reviewed draft

python3 tools/authoring/kr/check_structure.py  # the Korean deck checkers
python3 tools/authoring/en/check_deck.py --all # …and the English one
```

Promotion reads `sandbox/drafts/`, which `tools/model.py` refuses to walk, and
writes `courses/`. It is never called by CI — putting a lesson in front of a
learner is a decision someone makes, and the diff it produces is how that
decision gets reviewed.

Decks are visual documents. Render them in a browser at 480px and look before
claiming a change works.

## Authoring a lesson

Read [`shared/ux-philosophy.md`](shared/ux-philosophy.md) first — every time,
including small edits. It is the contract for every page: one activity per page,
Korean-first titles, one blue tutor-script box, one boxed component that fills the
page, receptive → productive.

Anything the learner taps, types or drags goes through lemonboard's `data-sync`
contract. The implementation in lemonboard is the SSOT; the working summary lives
in [`CLAUDE.md`](CLAUDE.md). Getting it wrong fails silently: the activity works on
your screen and never reaches the other person. Copy from a deck that passes the
gate — [`06-taiken-self-intro`](courses/kr/taiken-trial/lessons/06-taiken-self-intro)
— rather than inventing markup.

Both slots are mandatory. A lesson with only a 수업용 deck leaves
`PRESTUDY_LEMONBOARD_KEY` empty, and class creation then fails at
`/rooms/null/duplicate` — so `validate.py` blocks the merge rather than letting
the failure surface in production.

## The shared runtime

`shared/{css,js}` is the runtime, and this repository is where it is edited. Decks
reference an immutable tag on the public mirror
[`re-speak/podo-curriculum-shared`](https://github.com/re-speak/podo-curriculum-shared),
declared once in `curriculum.yaml` under `spec.sharedRuntime`. One version for the
whole repo; `validate.py` fails any deck that disagrees.

That cuts ~93k duplicated lines out of `courses/` and lets a learner's browser cache
one copy of `trial.css` across a whole course instead of re-fetching it per lesson.

### Changing it

```sh
vim shared/js/activities.js
vim curriculum.yaml                      # bump spec.sharedRuntime.version
python3 tools/publish-shared.py          # cut the tag, push it, verify it serves
python3 tools/repoint-shared.py          # stamp every deck with the new version
python3 tools/validate.py --env stage
```

**Publishing is a step you run, not something CI does on merge — deliberately.**
A merge-triggered publisher would invert the order and leave a window where `main`
holds decks naming a tag nobody pushed yet: a 404 for every activity, mid-class,
visible only to the learner. Publishing first is free, because an unreferenced tag
harms nobody. It also means no stored cross-repo token, which keeps the "nothing is
stored, nothing needs rotating" property the sync contract already relies on.

`publish-shared.py` refuses to move an existing tag. If `shared/` changed, the
version has to change — a deck already pinned to that tag would otherwise change
underneath a live class.

`validate.py` layer 5 catches the two silent failures: a pin whose tag was never
published (404), and a `shared/` that moved on without the tag being re-cut (byte
mismatch). Like the contract check it fail-opens on 5xx and network trouble.

A course may stay on its own bundled runtime — it simply has no URL on that host
and is not checked. `taiken-trial` is on that path deliberately.

## How a change reaches a learner

CI/CD is Cloud Build, not GitHub Actions. Triggers live in
`podo-infra/gcp/global/cloudbuild`; the build files are in `.cloudbuild/`.

**The branch is the release boundary, not the environment.** There are four
environments and two branches: `stage` fills the three non-production ones
(`stage`, `qa`, `dev`) in one build; `main` is what the learner sees.

A branch per environment would turn the merges *between* those branches into a
second release procedure, and from then on someone has to keep track of which
environment is looking at what. One branch feeding all three keeps them identical
by construction.

### The four steps

```sh
# 1. branch off stage — never off main
git fetch origin && git switch -c feat/my-lesson origin/stage
python3 tools/validate.py --contract --env stage    # what CI is about to run
git push -u origin feat/my-lesson
gh pr create --base stage                           # ← base is stage

# 2. merge it → podo-curriculum-deploy-stage applies to stage, qa and dev, automatically
# 3. open the release PR
gh pr create --base main --head stage
# 4. merge it → podo-curriculum-deploy-prod applies to prod, automatically
```

What each step actually runs:

1. **PR into `stage` → `podo-curriculum-validate`** runs schema, structure, packaging and the contract check, and comments the plan. Fires on any PR targeting `stage` or `main`, and labels the plan with the env that merging it would deploy to.
2. **Merge to `stage` → `podo-curriculum-deploy-stage` applies to `stage`, then `qa`, then `dev`, automatically.** One build, three applies, in that order; a failure stops the run where it happened rather than half-filling the rest. Verify before going on — these are the only environments where a mistake is cheap.
3. **PR `stage → main`.** That PR *is* the release: its diff is the release note and its review is the gate. Review it as a deploy approval, because that is what it is.
4. **Merge it → `podo-curriculum-deploy-prod` applies to prod, automatically** — a learner in a live class sees the change immediately.

Two things differ between the three non-production environments and are worth
knowing before you verify in one of them:

- **Only stage is a prod clone, and it is overwritten from prod every morning.** That wipes `CLASS_LEMONBOARD_KEY` back to prod's room ids, so stage rooms end up pointing at prod's GCS objects until the next apply that re-creates them. `qa` and `dev` carry their own data and don't have this problem — prefer them for anything you need to still be true tomorrow.
- **All three share one lemonboard.** There is no qa or dev lemonboard; `getPodoEnv() != "prod"` sends every non-production grape to the stage one. So the three environments' rooms live side by side under identical names, and what keeps their content apart is the `-{env}` prefix in `contentUrl`, nothing else.

Steps 2 and 4 have no button someone has to remember to press, because a deploy
like that eventually goes unpressed and then the branch and the learner disagree.

**Don't branch off `main`.** It lags `stage` by whatever is merged but not yet
released, so you would be writing against content the next release replaces — and
a PR straight into `main` skips the one environment where a mistake is cheap.

A rollback or a one-off re-deploy still goes through `podo-curriculum-deploy`, the
manual trigger, which takes any branch × any env:

```sh
gcloud builds triggers run podo-curriculum-deploy --region=asia-northeast3 \
  --branch=<branch> --substitutions=_DEPLOY_ENV=<dev|qa|stage|prod>
```

`_DEPLOY_ENV` also takes a comma-separated list (`stage,qa,dev`) — that is exactly
what the `stage` push trigger passes. A `prod` anywhere in the list still has to
pass the "is an ancestor of `main`" check; a list is not a way around the gate.

That path is why `prod` still refuses any commit that is not an ancestor of `main`.
On the push trigger the check is trivially true; on the manual one it is the same
protection the old `prod-*` tag gave — the point was that only reviewed content
ships, not the tag itself.

Content updates are a GCS overwrite at the same key; the lemonboard room is
created once and survives them. That is what makes a re-deploy safe.

## The public catalog

[**re-speak.github.io/podo-curriculum**](https://re-speak.github.io/podo-curriculum) is
the same content with a front door: every live course, every lesson in it, and every
deck opened exactly as the room opens it. It exists so somebody who wants to know what
we teach — inside the company or outside it — does not have to clone a repo or book a
class to find out.

```sh
pip install -r tools/requirements.txt          # pyyaml is the only thing the builder needs
python3 tools/build-catalog.py                 # → site/
python3 -m http.server -d site 8000            # → http://localhost:8000
```

Serve it rather than opening `site/index.html` — over `file://` Chrome gives every
file its own opaque origin, and the viewer's iframe is blocked. The catalog pages
look fine either way, so the failure reads as "the deck viewer is broken".

**The decks need the network to render.** They pin the shared runtime to a jsDelivr
tag and the pages pull Pretendard from the same CDN, so offline you get a working
catalog with unstyled decks inside it. That is the pin doing its job, not a break.

- **The design is shared with the authoring catalog.** `tools/authoring/{kr,en}/`
  build a catalog of everything being written; this builds one of what deploys. They
  use the same chrome so the two read as one product — `tools/catalog/site.css`,
  `gateway.html` and `course.html` are the deployed side of that pair, and a change to
  either should usually be made to both.
- **The two are filled from different data.** The authoring catalog is built from
  `tracks/*/table-of-contents.md` and describes the whole curriculum under authoring
  (5 tracks, 494 lessons); this one holds what deploys, so its templates are filled from
  `model.discover()`, with one structural difference: a *track* there is a *course* here,
  and a course has no units — `solo` collapses the unit shell so the lesson list starts
  where the unit list would have.
- **`enabled: true` is the switch.** The flag already means "a learner can reach this"
  (→ `USE_YN`), so the catalog reuses it rather than adding a second one: a course that
  is not live is not advertised, and turning a course on turns its page on with it. The
  999.x test courses stay off the site for the same reason they stay out of the app.
- **Built from `main`, and only from `main`.** It is the last step of
  `podo-curriculum-deploy` and runs only when that build deployed prod, so the page and
  the class never disagree. Merging to `stage` publishes nothing.
- **It is a Cloud Build step, not a GitHub Action.** This org's Actions are tied to the
  self-hosted `day1-runner-respeak`, which does not pick up this repository's jobs, and
  `ubuntu-latest` is rejected by the IP allow list at checkout — the same reason
  validate and deploy moved to Cloud Build. The step pushes the built site to a
  `gh-pages` branch and Pages serves that branch, so nothing here needs a runner.
  **Pages must be pointed at `gh-pages` once, by hand.**
- **It cannot fail a deploy.** The step is `allowFailure: true`: a broken site build must
  not turn a release red when no learner is affected. A failure leaves the last good
  site up.
- **Decks are copied, never rewritten.** A deck is `index.html` + `deck.css` + its own
  images, all relative, with the shared runtime on the CDN — so copying the directory is
  the whole port, and the viewer frames it in an iframe. What a visitor sees is the file
  the room loads, byte for byte.
- **It cannot break a class.** `build-catalog.py` reads the repo through
  `tools/model.py` and writes only to `--out`; nothing in the deploy path imports it.
  A failed catalog build leaves the last good site up and the 교재 untouched.
- **`catalog.json`** ships beside the pages for anything that wants the index as data.

The generated site is gitignored. There is no committed copy to fall out of date —
the only way to change what the page says is to change `courses/`.

## Writing a lesson

Lessons are written **here**, under `sandbox/drafts/<code>/`, and promoted into
`courses/` when they are ready. There is no upstream repository any more:
`podo-curriculum-public` was the authoring repo until 2026-08-19 and is now a
frozen archive holding only the licensed textbook scans.

```
sandbox/drafts/kr/tracks/…/lessons/<NN-slug>/lesson.html   ← write here
        │
        │   tools/authoring/kr/check_*.py                  ← check it
        │   sandbox/drafts/kr/trial/promotion.yaml         ← name it
        ▼
courses/kr/<course>/lessons/<NN-slug>/{lecture,prestudy}/  ← promote.py writes this
```

| directory | what it is |
|---|---|
| `sandbox/drafts/<code>/tracks/` | the curriculum under authoring — 480 Korean lessons, 14 English |
| `sandbox/drafts/kr/trial/` | trial decks and their assets |
| `sandbox/drafts/<code>/reference/` | what the toolchain generates: grammar maps, lexicons, ledgers |
| `tools/authoring/<code>/` | the checkers, scaffolders and builders for that language |
| `references/kr/` | durable source material — textbook pattern maps, research |

`<code>` is the subject taught (`kr`, `en`), matching `courses/<code>/`. The
country is the market and lives in `course.yaml`.

**Why drafts and courses are separate trees.** `tools/model.py` discovers courses
by walking `courses/` and nothing else, so a half-written lesson cannot reach a
learner by being renamed or copied into the wrong place. Promotion is the moment
that changes, and it is a diff someone reviews.

**Why promotion is a transform and not a move.** grape flattens each deck into one
GCS prefix, so a promoted deck cannot keep `../../shared/js/x.js` — `promote.py`
flattens the refs, bundles every sheet, script and image beside the deck, and
audits every `data-sync-id` against lemonboard's own kind resolution on the way
through. See [`tools/promote.py`](tools/promote.py).

**Input controls are static in the authoring HTML.** lemonboard's validator parses
without running scripts, so the real `<input>`, `<textarea>` and `.build-zone`
elements have to be in the file on disk; `activities.js` only binds behaviour to
them. Drafting, review, promotion and CDN publication all preserve that markup —
a control that only exists after JavaScript runs is invisible to the validator and
desyncs silently in class.

**Retiring content.** `apply.py` is a pure upsert with no delete path, so removing
a course from `courses/` does not retire it — the rows stay live in grape pointing
at content nobody updates. Set `enabled: false`, let that deploy, and only then
delete the directory. Both `promote.py` and `validate.py` layer 6 enforce this.

## What is deliberately not here

- **The PDF pipeline.** Page images, `podo-pdf-tool`, `BOOK_FILE_ID`, audio via `TB_COM_FILE`. Grape still owns all of it for legacy courses. This repo is HTML 교재 only.
- **Textbook scans.** 41 licensed PDFs and `dekiru-kankokugo/page-images/` — 726MB, one file of them past GitHub's 100MB ceiling — stay in the archived `podo-curriculum-public`. Nothing in the build reads them; only derived markdown and the wireframe PNGs came across. That archive is the one reason the old repository still exists.
- **Deployable English courses.** The English tree is authored under `sandbox/drafts/en/`, but nothing ships from it yet. Promotion will put verified courses in `courses/en/` with `countryCode: JP` — the code is the subject taught, the country is the market.
