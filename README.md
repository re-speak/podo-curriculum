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
| `state/*.lock.yaml` | slug → DB row id + room key. **Written by CI, never by hand.** |
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

## Slugs are identity

`GT_CLASS_COURSE.ID` is a DB-side autoincrement and also the S3 prefix
(`lemonboard-html/{ID}/`), so YAML cannot know it. `state/<env>.lock.yaml` binds
the two — exactly the job a Terraform state file does.

The consequence: **a directory slug is permanent.** Rename one and the live course
is orphaned; the next apply creates a duplicate instead of updating it.
`validate.py` refuses a rename that has no matching state move. Retire a course by
setting `enabled: false`, never by deleting it — learners mid-course hold
`pl_user_lesson_progress.lesson_id` pointing at those rows.

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
contract — [`shared/interaction-protocol.md`](shared/interaction-protocol.md).
Getting it wrong fails silently: the activity works on your screen and never
reaches the other person. Copy from
[`shared/reference-lesson.html`](shared/reference-lesson.html) rather than
inventing markup.

Both slots are mandatory. A lesson with only a 수업용 deck leaves
`PRESTUDY_LEMONBOARD_KEY` empty, and class creation then fails at
`/rooms/null/duplicate` — so `validate.py` blocks the merge rather than letting
the failure surface in production.

## How a change reaches a learner

1. PR → `validate.yml` runs schema, structure, packaging and the contract check, and comments the plan.
2. Merge to `main` → `deploy-stage.yml` applies to stage and commits `state/stage.lock.yaml` back.
3. Tag `prod-*` → `deploy-prod.yml` applies to prod, gated on the `prod` environment.

Content updates are an S3 overwrite at the same key; the lemonboard room is
created once and survives them. That is what makes a re-deploy safe.

## What is deliberately not here

- **The PDF pipeline.** Page images, `podo-pdf-tool`, `BOOK_FILE_ID`, audio via `TB_COM_FILE`. Grape still owns all of it for legacy courses. This repo is HTML 교재 only.
- **Textbook scans.** ~1GB of licensed PDFs and page images stay in `beginner-curriculum`. Only derived markdown moved.
- **The Japanese curriculum.** The layout is language-neutral (`courses/<lang>/`), so it can move in later; nothing here assumes Korean.
