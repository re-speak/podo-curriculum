# Shipping the Korean curriculum

What still has to happen before a Japanese-speaking learner can take a Korean lesson, and in
what order. Written 2026-08-10, after wiring the authoring tree to this repo.

Three repos are involved:

| Repo | Role |
|---|---|
| `beginner-curriculum/korean` | authoring — TOCs, decks, the shared runtime source |
| `re-speak/podo-curriculum` (here) | deployment — courses, packaging, sync to grape |
| `grape` | the admin and the sync endpoint; owns what a course *is* |

**Nothing below is blocking today.** All 38 Korean courses are `enabled: false`, so they can
sit in `main` indefinitely without reaching a learner. The order matters only once you want
one live.

---

## Where things stand

Done:

- 5 tracks cut into **38 courses / 375 planned lessons**, each `course.yaml` validating
  against `schemas/`
- `classLevel` section bands — `1000` hangul · `2000` core · `3000` contextual ·
  `4000` freetalking · `5000` pronunciation
- `curriculumType: BASIC_V2` on all of them
- `import-track-lessons.py` copies the plan; `repoint-shared.py` pins the CDN runtime
- **2 decks actually written** (`core-beginner-1` 과 7 and 과 8), verified at 480px

Not done: everything below.

---

## 1 · Register `BASIC_V2` in the code table

**Why:** `TB_SYS_CODE_DETAIL` drives the curriculum-type dropdown on subscription products
(`inc/db_class.php:25` → `select_code_list($db, 'PODO_CURRICULUM_TYPE')`). Without a row here
you cannot sell or attach a subscription to the new curriculum.

**Not** needed for the course sync itself — `api/curriculum/sync.php` writes
`CURRICULUM_TYPE` straight through with no allowlist, so courses land fine without this.

Current contents (stage). `BUSINESS` is the precedent: types are retired by flag, not deleted.

| VALUE | NAME | ORDER | USE_YN |
|---|---|---|---|
| TRIAL | 체험레슨 | 1 | Y |
| BASIC | 스탠다드 | 2 | Y |
| BUSINESS | 비즈니스 | 3 | **N** |
| SMART_TALK | 스마트토크 | 4 | Y |

```sql
-- grape/sql/podo_curriculum_type_basic_v2.sql
-- CODE_ID is the existing PODO_CURRICULUM_TYPE parent; confirm it per environment:
--   SELECT CODE_ID FROM TB_SYS_CODE WHERE CODE_VALUE = 'PODO_CURRICULUM_TYPE';
-- (stage: c86a644d312c35a56dc513c27e427b83)
INSERT INTO TB_SYS_CODE_DETAIL
  (CODE_DETAIL_ID, CODE_ID, CODE_DETAIL_VALUE, CODE_DETAIL_NAME, ORDER_LEVEL, USE_YN)
SELECT REPLACE(UUID(), '-', ''), TSC.CODE_ID, 'BASIC_V2', 'BASIC v2', 5, 'Y'
FROM TB_SYS_CODE TSC
WHERE TSC.CODE_VALUE = 'PODO_CURRICULUM_TYPE'
  AND NOT EXISTS (
      SELECT 1 FROM TB_SYS_CODE_DETAIL D
      WHERE D.CODE_ID = TSC.CODE_ID AND D.CODE_DETAIL_VALUE = 'BASIC_V2');
```

Re-runnable, and it looks the parent up rather than hard-coding an id that differs per
environment. Run dev → stage → prod.

> **`CODE_DETAIL_VALUE` is case-sensitive** — the column is `utf8mb3_bin`. `BASIC_v2` would
> be a second, tutor-less curriculum with no error anywhere. Copy the string, don't retype it.

**Verify:** the type appears in the dropdown at
`admin/subscribe/subscribe_origin_manage_create.php`.

---

## 2 · Un-hardcode the three-value lists in grape

**Why:** the code table above does *not* feed the course admin. Six places enumerate
`BASIC / TRIAL / SMART_TALK` literally, so a `BASIC_V2` course syncs correctly and is then
invisible in the UI. This is the "hardcode creep" — each was written when three types were
all there were.

| File:line | What it does | Effect if unfixed |
|---|---|---|
| `admin/popup/search_course_list.php:39` | `$allowedCurriculumTypes = array('BASIC','TRIAL','SMART_TALK')` | course not selectable anywhere that popup is used |
| `admin/popup/search_course_list.php:104` | `AND c.CURRICULUM_TYPE IN (…)` | filtered out of the result set |
| `admin/popup/search_course_list.php:107` | `FIELD(c.CURRICULUM_TYPE, …)` sort | sorts to an arbitrary position |
| `admin/popup/search_course_list.php:190` | `<option>` filter | cannot narrow to it |
| `admin/system/class_course/class_course_create.php:109` | `<option>` | cannot hand-create one |
| `admin/system/class_course/class_course_update.php:134–136` | `<option>` | **a BASIC_V2 course cannot be edited without changing its type** |
| `admin/system/class_course/class_course_list.php:125` | `<option>` search filter | cannot list them |
| `admin/podo_teachers_v1.php:576` | `foreach (['TRIAL','BASIC','SMART_TALK'])` | cannot assign a tutor — blocks §3 |

`class_course_update.php` is the one to fix first. Its `<select>` offers only an empty
`선택해주세요`, `BASIC` and `SMART_TALK`, and carries `required`. Opening a `BASIC_V2` course
therefore lands on the empty option and the form refuses to save until someone picks `BASIC`
or `SMART_TALK` — so any edit made through that screen converts the course. It is at least
loud rather than silent, but it is a one-way door for anyone who does not know why.

That screen already omits `TRIAL`, which is a fair sign it is not the route used for
non-`BASIC` courses today — worth confirming how those are maintained before assuming the
same path has to work for `BASIC_V2`.

**Preferred fix:** replace the literals with `select_code_list($db, 'PODO_CURRICULUM_TYPE')`,
which several other screens already use — then §1 is the only place a future type is added.
The minimal fix is adding `'BASIC_V2'` to each list, which just moves the creep forward.

**Verify:** create a class through the admin against a `BASIC_V2` course, and re-save an
existing one and confirm `CURRICULUM_TYPE` is unchanged.

---

## 3 · Assign tutors to `PODO_KR_BASIC_V2`

**Why:** `le_tutor_curriculum` keys on `PODO_{LANG}_{TYPE}`. **There are currently zero
`PODO_KR_*` rows of any type on stage** — so no tutor can be matched to *any* Korean course,
new type or old. This is independent of everything else here and is the hardest blocker.

Forking the namespace is deliberate: driving an interactive board is a different skill from
reading a PDF, and a Korean-for-Japanese tutor needs Japanese. But it means the assignment
has to be made explicitly, and §2's `podo_teachers_v1.php` fix has to land first for the
admin route to exist.

Also fill in `tutorGroups` in each `course.yaml` — all 38 currently have
`allowRandom: []` / `assignedOnly: []`, which is honest but means nobody is matched.

**Verify:**
`SELECT COUNT(*) FROM le_tutor_curriculum WHERE curriculum_type = 'PODO_KR_BASIC_V2';`

---

## 4 · Settle the entitlement question — **unresolved**

`GT_CLASS_TICKET.CURRICULUM_TYPE` and `GT_SUBSCRIBE.CURRICULUM_TYPE` both exist. I did not
find the code path that decides whether a `BASIC` ticket may book a `BASIC_V2` class, so
**it is unknown whether existing subscribers can take these lessons or need a new product.**

This is the item with commercial consequence and it should be answered by whoever owns
billing, not inferred from the schema. Two outcomes:

- ticket type must match course type → `BASIC_V2` needs its own subscription products, and
  every existing learner needs a migration path
- booking ignores it → nothing to do

Everything else in this document is mechanical. This one is a product decision.

---

## 5 · Publish the shared runtime (`v1.2.0`)

`korean/tools/check_runtime_drift.py` currently reports four files ahead of the published
tag:

```
css/trial.css              +9,804 bytes vs v1.1.0
js/freetalk-activities.js  +1,711
js/highlight.js            +1,533
js/spotlight.js            +1,165
```

Decks render locally against the working tree and in production against the pinned tag, so
until this is published, **a lesson verified at 480px is not the page a learner gets** — and
nothing errors; components just lose their styles.

Blocked on `korean/runtime/css/trial.css` having uncommitted work in the authoring tree.
When it is finished:

```
python3 tools/sync-from-authoring.py --runtime-only
python3 tools/publish-shared.py v1.2.0      # immutable tag; cannot be moved later
python3 tools/repoint-shared.py
python3 tools/validate.py --contract --env stage
```

Order is load-bearing — publish before repoint, or `main` briefly holds decks pointing at a
tag nobody pushed, which 404s in class on the learner's screen only.

---

## 6 · Write the lessons

**2 of 375 written.** This is the bulk of the remaining work and the only part that cannot
be automated.

Per lesson, following `korean/CLAUDE.md` § Writing a new lesson:

```
python3 korean/tools/new_lesson.py --track <t> --lesson <n> --id NN-english-words \
    --title-ko … --title-ja … --title-en …
# then: read toc/lesson-NNN.md → lesson-blueprint.md → the trial deck in full
python3 korean/tools/plan_courses.py korean/tracks/<t>   # regenerates lesson.yaml
```

Suggested order — finish one course end to end rather than sampling across tracks, so
something becomes deployable early:

1. `core-beginner-1` (과 1–10, 8 remaining) — 과 7 and 8 exist; completing it gives the first
   fully deployable course and exercises the whole pipeline once
2. `hangul-reading` (14) — the entry product, and the track most learners meet first
3. `kpop-talk` (10) — the contextual track's own front door (lowest grammar floor, 과 42)

Two things to watch, both learned the hard way:

- **`5-pronunciation`'s blueprint is marked provisional** — it was derived from the TOC, not
  from a working deck, because that track has no sample. The first deck there should be
  treated as design work, and the blueprint rewritten from it afterwards.
- **`hangul-lv1` (hand-authored, 11 lessons, `classLevel: "1"`, `BASIC`) overlaps
  `hangul-reading` (14 lessons, `1000.001`, `BASIC_V2`).** They are two versions of the same
  curriculum. Decide which wins before either goes live.

---

## 7 · Optional: carry `verYear` / `verNum` through the sync

`GT_CLASS_COURSE.VER_YEAR` / `VER_NUM` are how PODO already labels generations — EN and JP
BASIC each carry `2024/2`, `2024/3`, `2025/3` alongside a null legacy set. The sync never
sends them, so our rows land null.

Not required: `VER_*` is not part of the natural key, so it changes nothing about identity —
`BASIC_V2` is already doing that job. Worth adding only when you want generations legible
*inside* `BASIC_V2` later. Needs `course.yaml` → `course.schema.json` → manifest →
`api/curriculum/sync.php`.

---

## Reference — what identifies a course

From `admin/system/class_course/process/class_course_ps.php:656`, confirmed in code rather
than inferred:

```sql
WHERE CLASS_TYPE='PODO' AND BOOK_TYPE='COVER' AND CLASS_WEEK=0
  AND LANG_TYPE=… AND CURRICULUM_TYPE=… AND LESSON_TIME=… AND CLASS_LEVEL=…
→ "동일한 조건(언어/커리큘럼/수업시간/레벨)의 코스가 이미 존재합니다."
```

Consequences worth remembering:

- **`COUNTRY_CODE` is not in it.** "English for Japanese speakers" cannot coexist with
  "English for Korean speakers" at the same level today — grape rejects the second outright.
  Whenever English gains a second audience, that lookup, the manifest, and the learner→course
  query all have to learn about `COUNTRY_CODE`. `GT_USER.LANGUAGE_CODE`
  (`system|ko|en|ja`) already exists on the learner side and should be a default and sort,
  never an enrolment filter.
- **`VER_*` is not in it** either — which is why §7 is optional and a new type was the right
  answer to the overlap problem.
- **There is no unique index on `GT_CLASS_COURSE`** — only `PRIMARY KEY (ID)`. The natural key
  is enforced entirely in PHP, so anything writing outside `class_course_ps.php` or
  `api/curriculum/sync.php` can create duplicates the app will then pick between arbitrarily.

## Reference — the `classLevel` section convention

The integer part is the section; the decimal is the course. Undocumented anywhere else; this
is what the live rows do.

```
1–2          the graded ladder (level 1, level 2)      EN / JP
1000         Breaking News, 15 courses                 EN / JP
1001, 1002   single topic courses
2001–2006    the Business series
3500         가벼운 프리토킹, 12 courses
999          throwaway rows — 'html test (john)'
```

Korean uses `1000`/`2000`/`3000`/`4000`/`5000`, one band per track, inside `BASIC_V2` where
they cannot collide with the English or Japanese curricula at all. `1–99` is left free in
case Korean ever gets a graded ladder.
