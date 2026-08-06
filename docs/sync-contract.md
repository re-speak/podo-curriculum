# The sync endpoint

What this repo needs grape to expose. **It does not exist yet** — until it does,
everything here validates and plans but cannot apply.

## Why grape and not CI

Grape already owns every write this repo needs:

| Step | Where it lives today |
|---|---|
| zip → S3, flattened to `lemonboard-html/{교재ID}/` | `uploadLessonHtmlZip()` |
| lemonboard HTML room create + monitor member | `ensureLessonHtmlLemonboardRoom()` |
| contract validation before save | `validateLessonHtmlZipContract()` |
| `GT_CLASS_COURSE` COVER + MAIN rows | `CREATE_COURSE` / `UPDATE_COURSE` |
| `le_tutor_curriculum` mapping | same, `PODO_{LANG}_{TYPE}` |

all in `admin/system/class_course/process/class_course_ps.php`.

CI could do it directly — S3 credentials, the lemonboard API and a Cloud SQL Auth
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
| `zip[{lessonSlug}][{lecture\|prestudy}]` | the packaged deck, only for slots whose digest changed |

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
    "coverId": 1043,
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
      "courseRowId": 1044,
      "decks": {
        "lecture":  { "digest": "sha256:…", "unchanged": false, "roomKey": "rm_a1b2c3" },
        "prestudy": { "digest": "sha256:…", "unchanged": true,  "roomKey": "rm_d4e5f6" }
      }
    }
  ]
}
```

`coverId` / `courseRowId` / `roomKey` are `null` on first apply and echo the state
lock afterwards. **They are what makes the endpoint an upsert rather than an
insert** — given an id, update that row; given `null`, create and return the new one.

`unchanged: true` means the packaged bytes match what was uploaded last time, and
no zip part is attached. Skip the S3 write. Do not touch the room.

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

- **Upsert on id, never on shape.** Matching by `(LANG_TYPE, CLASS_LEVEL, CURRICULUM_TYPE, CLASS_WEEK)` looks equivalent and is not: the repo is allowed to change any of those, and a match-on-shape upsert silently creates a duplicate the moment one moves.
- **Rooms are created once.** `ensureLessonHtmlLemonboardRoom()` already returns early when the key is set. Content updates are an S3 overwrite; the room key must survive them.
- **Contract validation stays a hard gate.** Same call, same fail-open on 5xx, same block on `severity: error`.
- **Both slots or neither.** Reject a lesson whose `prestudy` key would end up empty — class creation duplicates `/rooms/null/` and fails downstream.
- **Removing a lesson deactivates, never deletes.** A learner mid-course holds `pl_user_lesson_progress.lesson_id` pointing at that row. Set `USE_YN='N'`; leave the row.
- **OIDC, not an admin session and not a shared secret.** Cloud Build mints an ID token
  for its own service account off the metadata server and grape verifies the Google
  signature. Nothing is stored, nothing needs rotating, and a leaked token dies in an hour.
  Verify all four: signature, `iss`, `aud` (the called URL — stops a token minted for
  another service being replayed here), and `email` against an allowlist. Signature alone
  is authentication, not authorisation — anyone with a Google account can mint a token.

## Prerequisite: `LANG_TYPE = 'KR'`

The column is a plain varchar and `Language.KOREAN` already carries `"KR"`, but
nothing in the product offers it yet:

- `grape/admin/system/class_course/class_course_create.php:96` — the dropdown lists only `EN` and `JP`
- `podo-backend` `LangType` — `enum { EN, JP }`

Both need `KR` before a Korean course can exist, whether it is created through
this repo or by hand in the admin.

## Secrets

`PODO_CURRICULUM_SYNC_TOKEN` is no longer a stored secret — the deploy build fills that
env var with a freshly minted OIDC token. grape decides who may call via
`CONF_CURRICULUM_SYNC_CALLERS` (comma-separated service-account emails).

| Secret | Used by | What it is |
|---|---|---|
| `PODO_LEMONBOARD_API_KEY_STAGE` | `validate`, `deploy-stage` | lemonboard API bearer key — the same `$conf_dev_lemonboard_key` grape uses |
| `PODO_LEMONBOARD_API_KEY_PROD` | `deploy-prod` | `$conf_prod_lemonboard_key` |

`/api/v1/lesson-html/validate` is authenticated; without a key it answers
`400 INVALID_AUTHENTICATION`. `validate.py` refuses `--contract` when the key is
missing rather than letting an auth rejection read as a clean pass.
