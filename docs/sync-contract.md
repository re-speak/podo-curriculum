# The sync endpoint

What grape exposes for this repo, and why it behaves the way it does. **It is
live** — `tools/apply.py` calls it on every deploy, against both stage and prod.

## Why grape and not CI

Grape already owns every write this repo needs:

| Step | Where it lives today |
|---|---|
| zip → GCS, flattened to `lemonboard-html/{교재ID}/` | `uploadLessonHtmlZip()` |
| lemonboard HTML room create + monitor member | `ensureLessonHtmlLemonboardRoom()` |
| contract validation before save | `validateLessonHtmlZipContract()` |
| `GT_CLASS_COURSE` COVER + MAIN rows | `CREATE_COURSE` / `UPDATE_COURSE` |
| `le_tutor_curriculum` mapping | same, `PODO_{LANG}_{TYPE}` |

all in `admin/system/class_course/process/class_course_ps.php`.

CI could do it directly — GCS credentials, the lemonboard API and a Cloud SQL Auth
Proxy are all things `podo-database-schema` already wires up. But then the rules
about what a valid course is would live in two languages and drift, with
production in between. So the endpoint is a second entry point into the same
functions, not a second implementation.

## Shape

```
POST {grapeSyncApi}
Authorization: Bearer <Google OIDC ID token>
Content-Type: multipart/form-data
```

| Part | Contents |
|---|---|
| `manifest` | JSON — the full desired state of **one** course |
| `zip[{lessonSlug}][{lecture\|prestudy}]` | the packaged deck. Every slot, every time — see `unchanged` below |

One course per request. Courses are independent, and a partial failure should
cost one course rather than the whole curriculum.

### manifest

```json
{
  "apiVersion": "podo.curriculum/v1",
  "classType": "PODO",
  "bookFormat": "HTML",
  "langType": "KR",
  "course": {
    "slug": "hangul-lv1",
    "key": "kr/hangul-lv1",
    "curriculumType": "BASIC",
    "curriculumTypeKey": "PODO_KR_BASIC",
    "classLevel": "1",
    "lessonTime": 25,
    "useYn": "N",
    "difficulty": "BEGINNER",
    "title":       { "ko": "한글 떼기", "en": "Hangul Basics", "ja": "ハングル入門" },
    "description": { "ko": "…", "ja": "…" },
    "tutorGroups": { "allowRandom": [], "assignedOnly": [] }
  },
  "lessons": [
    {
      "slug": "01-block-and-first-sounds",
      "week": 1,
      "title": { "ko": "블록과 첫 소리", "en": "…", "ja": "…" },
      "decks": {
        "lecture":  { "digest": "sha256:…", "unchanged": false },
        "prestudy": { "digest": "sha256:…", "unchanged": false }
      }
    }
  ]
}
```

**No row ids are sent.** grape finds the row by its natural key
`(CLASS_TYPE, LANG_TYPE, CURRICULUM_TYPE, LESSON_TIME, CLASS_LEVEL, CLASS_WEEK)`
— which is what makes the endpoint an upsert without either side remembering
anything between runs. There is no state lock; see the README.

`unchanged` is always `false` today and every zip is attached. The field is kept
because the skip is grape's to make if it ever wants it: deciding it on this side
would mean remembering last run's digests, and that memory *is* the lock file the
repo deliberately removed. A whole course is a few tens of MB, and re-uploading
to the same key leaves the room untouched, so the skip buys little.

### response

```json
{
  "ok": true,
  "course": {
    "slug": "hangul-lv1",
    "coverId": 1043,
    "lessons": {
      "01-block-and-first-sounds": {
        "courseRowId": 1044,
        "lemonboard": { "lecture": "rm_a1b2c3", "prestudy": "rm_d4e5f6" }
      }
    }
  },
  "warnings": ["…"]
}
```

Failure is `4xx` with `{"ok": false, "errors": [...]}`. The caller writes the
response for logging, so **every row grape created or confirmed should appear
there, even on partial success** — an id that grape allocated but did not report
becomes an orphan course nobody can reach or update.

## Behaviour it has to get right

- **Upsert on the natural key, and treat a change to it as a different course.** Matching on `(CLASS_TYPE, LANG_TYPE, CURRICULUM_TYPE, LESSON_TIME, CLASS_LEVEL, CLASS_WEEK)` means editing `classLevel` or `lessonTime` in YAML does not rename the live course — it addresses a different one, and the old rows stay behind untouched. That is intended (a 15-minute Level 3 and a 25-minute Level 3 are different products), but it is the one edit that silently leaves an orphan, so it belongs in review.
- **Rooms are created once.** `ensureLessonHtmlLemonboardRoom()` already returns early when the key is set. Content updates are a GCS overwrite; the room key must survive them.
- **Contract validation stays a hard gate.** Same call, same fail-open on 5xx, same block on `severity: error`.
- **Both slots or neither.** Reject a lesson whose `prestudy` key would end up empty — class creation duplicates `/rooms/null/` and fails downstream.
- **Removing a lesson deactivates, never deletes.** A learner mid-course holds `pl_user_lesson_progress.lesson_id` pointing at that row. Set `USE_YN='N'`; leave the row.
- **OIDC, not an admin session and not a shared secret.** Cloud Build mints an ID token
  for its own service account off the metadata server and grape verifies the Google
  signature. Nothing is stored, nothing needs rotating, and a leaked token dies in an hour.
  Verify all four: signature, `iss`, `aud` (the called URL — stops a token minted for
  another service being replayed here), and `email` against an allowlist. Signature alone
  is authentication, not authorisation — anyone with a Google account can mint a token.

## Still open: `LANG_TYPE = 'KR'` outside this endpoint

The column is a plain varchar, so **the sync endpoint writes `KR` rows fine** —
stage carries `kr/taiken-trial` as `GT_CLASS_COURSE` 8142–8148, created by an
apply. What is still missing is everywhere *else* in the product that enumerates
languages:

- `grape/admin/system/class_course/class_course_create.php:96` — the dropdown lists only `EN` and `JP`, so a Korean course cannot be created or edited by hand
- `podo-backend` `LangType` — `enum { EN, JP }`

Until both carry `KR`, a Korean course exists in the table but is not a
first-class product. Confirm the `podo-backend` side before flipping any Korean
course to `enabled: true`.

## Secrets

`PODO_CURRICULUM_SYNC_TOKEN` is no longer a stored secret — the deploy build fills that
env var with a freshly minted OIDC token. grape decides who may call via
`CONF_CURRICULUM_SYNC_CALLERS` (comma-separated service-account emails).

Everything else lives in Secret Manager and is read by the build service account
(`cloud-build@podospeaking`), not stored on the GitHub side:

| Secret Manager name | Used by | What it is |
|---|---|---|
| `curriculum-lemonboard-key-stage` | `podo-curriculum-validate`, `podo-curriculum-deploy` (`_DEPLOY_ENV=stage`) | lemonboard API bearer key — the same `$conf_dev_lemonboard_key` grape uses |
| `curriculum-lemonboard-key-prod` | `podo-curriculum-deploy` (`_DEPLOY_ENV=prod`) | `$conf_prod_lemonboard_key` |
| `cloud-build` (`GITHUB_PAT`) | `podo-curriculum-validate` | fine-grained PAT for the plan comment. Needs **Pull requests: Read and write** — Issues alone gets a 403 on PR comments |
| `podo-common` (`PODO_NOTIFICATOR_SLACK_TOKEN`) | `podo-curriculum-validate` | posts contract violations to Slack |

`/api/v1/lesson-html/validate` is authenticated; without a key it answers
`400 INVALID_AUTHENTICATION`. `validate.py` refuses `--contract` when the key is
missing rather than letting an auth rejection read as a clean pass.
