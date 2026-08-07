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

**Nothing deploys yet.** Validation, packaging and planning work today; `apply`
needs a sync endpoint in grape that does not exist, and Korean needs `LANG_TYPE='KR'`
which the admin does not offer. Both are specified in
[`docs/sync-contract.md`](docs/sync-contract.md).

Until then this repo is the source of truth for authoring, and decks are uploaded
by hand through 교재 등록/수정 → **html로 생성하기**.

## Layout

| Path | What it is |
|---|---|
| `curriculum.yaml` | languages, environments, repo-wide constants |
| `courses/<lang>/<course>/` | **deployable.** `course.yaml` + `lessons/<NN-slug>/` |
| `shared/` | the deck runtime — `lesson-card.css` + `trial.css`, thirteen activity/chrome scripts, and the design contract |
| `schemas/` | JSON Schema for the three document kinds |
| `tools/` | build · validate · plan · apply, plus the two sync tools below |
| `sandbox/` | experiments. Committed, reviewable, and structurally undeployable |
| `references/` | table-of-contents plans, textbook pattern maps, research |
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
  lessonTime: 25                 # 15 | 25
  enabled: false                 # USE_YN
  title: { ko: 한글 떼기, en: Hangul Basics, ja: ハングル入門 }
  tutorGroups: { allowRandom: [], assignedOnly: [] }
```

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
(CLASS_TYPE, LANG_TYPE, CURRICULUM_TYPE, LESSON_TIME, CLASS_LEVEL, CLASS_WEEK)
```

Verified unique across 3,514 prod rows (SMART_TALK excluded — it has 18 duplicate
groups of its own, unrelated to this repo). A COVER row is simply `CLASS_WEEK=0`.

So nothing here has to remember what the last apply created. There is no lock
file and no write-back step — which is what used to turn a failed apply into a
duplicate course on the next run.

The consequence: **changing `classLevel` or `lessonTime` makes a different
course**, because it is one. The old rows stay; retire them with
`enabled: false`. A directory slug is still permanent by convention — it is what
a human uses to find the course — but it is no longer what the DB matches on.

## Working locally

```sh
pip install -r tools/requirements.txt

python3 tools/validate.py                      # schema + structure + packaging
python3 tools/validate.py --contract           # …plus lemonboard's data-sync validator
python3 tools/plan.py --env stage              # what apply would do
python3 tools/build.py courses/kr/hangul-lv1/lessons/01-block-and-first-sounds/lecture/index.html \
        --out /tmp/deck                        # one deck, to inspect the zip

python3 tools/sync-from-authoring.py           # refresh shared/, sandbox/, references/
python3 tools/import-trial-decks.py            # …then rebuild the trial course
python3 tools/import-report-deck.py            # promote the sandbox report deck
```

The two sync tools find the authoring tree next door; pass `--upstream PATH` or
set `$PODO_AUTHORING_ROOT` if yours sits somewhere else. Run them in that order —
the second reads the runtime the first mirrored. Neither is called by CI.

`import-report-deck.py` reads no authoring tree — its source is this repo's own
`sandbox/`, which `tools/model.py` refuses to walk. Re-run it after editing
`sandbox/trial/reports/trial-1-report.html`; it rewrites `courses/kr/report-test/lessons/`
from scratch and re-audits every `data-sync-id` on the way through.

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

## How a change reaches a learner

CI/CD is Cloud Build, not GitHub Actions. Triggers live in
`podo-infra/gcp/global/cloudbuild`; the build files are in `.cloudbuild/`.

**The environment is the branch.** `stage` is where work lands; `main` is what the
learner sees.

1. **PR → `podo-curriculum-validate`** runs schema, structure, packaging and the contract check, and comments the plan. Fires on any PR targeting `stage` or `main`, and labels the plan with the env that merging it would deploy to.
2. **Merge to `stage` → `podo-curriculum-deploy-stage` applies to stage, automatically.**
3. **Merge `stage` → `main` → `podo-curriculum-deploy-prod` applies to prod, automatically.** That PR *is* the release: its diff is the release note and its review is the gate.

Neither step has a button someone has to remember to press, because a deploy like
that eventually goes unpressed and then the branch and the learner disagree.

A rollback or a one-off re-deploy still goes through `podo-curriculum-deploy`, the
manual trigger, which takes any branch × any env:

```sh
gcloud builds triggers run podo-curriculum-deploy --region=asia-northeast3 \
  --branch=<branch> --substitutions=_DEPLOY_ENV=<stage|prod>
```

That path is why `prod` still refuses any commit that is not an ancestor of `main`.
On the push trigger the check is trivially true; on the manual one it is the same
protection the old `prod-*` tag gave — the point was that only reviewed content
ships, not the tag itself.

Content updates are a GCS overwrite at the same key; the lemonboard room is
created once and survives them. That is what makes a re-deploy safe.

## Where the content comes from

`beginner-curriculum/korean` is the authoring tree and the upstream for
`shared/`, `sandbox/` and `references/`. It shares one `runtime/` across every
deck; this repo needs each deck self-contained, because grape flattens the
uploaded zip into a single GCS prefix. So a sync is not a copy:

| upstream | here | what changes |
|---|---|---|
| `runtime/{css,js}` | `shared/{css,js}` | nothing — straight mirror |
| `trial/lessons/*.html` | `courses/kr/hangul-trial-test/` | refs flattened to basenames, runtime bundled per deck, **input controls written into the markup** instead of built at load |
| `trial/*`, `tracks/*/sample-lesson.html`, `interactive/` | `sandbox/` | `runtime/` refs repointed at `shared/` |
| `tracks/*/table-of-contents.md`, `references/` | `references/` | licensed scans dropped (see below) |

The control rewrite is the one that matters. lemonboard's validator parses
statically, so a `<span>` that only becomes an `<input>` when the page loads has
no resolvable `data-sync-kind` — the element is dropped from the sync set with no
warning, and the deck works in class while failing the merge gate. See
[`CLAUDE.md`](CLAUDE.md).

That is also why `shared/js/activities.js` is *not* what the trial decks ship.
Upstream's version builds those controls at load;
[`tools/deck-runtime/activities.js`](tools/deck-runtime/activities.js) binds them
instead, and is the one file here that has to be ported by hand when upstream
changes an activity.

Re-syncing replaces those directories wholesale, so **edit them upstream**, not
here. `courses/`, `tools/`, `schemas/`, `docs/`, `shared/assets/` and
`sandbox/archive/` are this repo's own.

## What is deliberately not here

- **The PDF pipeline.** Page images, `podo-pdf-tool`, `BOOK_FILE_ID`, audio via `TB_COM_FILE`. Grape still owns all of it for legacy courses. This repo is HTML 교재 only.
- **Textbook scans.** 41 licensed PDFs and `dekiru-kankokugo/page-images/` — 726MB of the 1.0GB in `korean/references/curricula` — stay in `beginner-curriculum`. Only derived markdown and the wireframe PNGs moved.
- **The Japanese curriculum.** The layout is language-neutral (`courses/<lang>/`), so it can move in later; nothing here assumes Korean.
