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
| `shared/` | `lesson-card.css`, the four interaction add-ons, the design and sync contracts |
| `schemas/` | JSON Schema for the three document kinds |
| `tools/` | build · validate · plan · apply |
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
```

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

1. **PR → `podo-curriculum-validate`** runs schema, structure, packaging and the contract check, and comments the plan. Fires on any PR targeting `main`.
2. **Merge to `main` → `podo-curriculum-deploy` applies to stage, automatically.** The trigger listens on push to `main` with `_DEPLOY_ENV=stage`. Merging *is* the stage deploy; there is no separate button, because a deploy someone has to remember to press eventually goes unpressed and then `main` and the learner disagree.
3. **Prod is the same trigger, run by hand**, with the env chosen at run time:

```sh
gcloud builds triggers run podo-curriculum-deploy --region=asia-northeast3 \
  --branch=main --substitutions=_DEPLOY_ENV=prod
```

`prod` refuses any commit that is not an ancestor of `main`. That is the same
protection the old `prod-*` tag gave — the point was that only reviewed content
ships, not the tag itself.

Content updates are a GCS overwrite at the same key; the lemonboard room is
created once and survives them. That is what makes a re-deploy safe.

## What is deliberately not here

- **The PDF pipeline.** Page images, `podo-pdf-tool`, `BOOK_FILE_ID`, audio via `TB_COM_FILE`. Grape still owns all of it for legacy courses. This repo is HTML 교재 only.
- **Textbook scans.** ~1GB of licensed PDFs and page images stay in `beginner-curriculum`. Only derived markdown moved.
- **The Japanese curriculum.** The layout is language-neutral (`courses/<lang>/`), so it can move in later; nothing here assumes Korean.
