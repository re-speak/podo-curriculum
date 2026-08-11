# Shipping the Korean curriculum

This is the path from the Korean authoring tree to a bookable PODO course. It reflects the
runtime contracts in `podo-app`, `podo-backend`, and `grape` as of 2026-08-11.

Three repositories are involved:

| Repository | Role |
|---|---|
| `beginner-curriculum/korean` | Authoring: plans, lesson decks, shared runtime source |
| `podo-curriculum` (here) | Deployment: manifests, packaging, grape sync |
| `grape` | Admin and sync endpoint; owns persisted course identity |

All planned track courses remain `enabled: false`, so changing their manifests does not make
them learner-visible by itself.

## Course identity: use `BASIC`

Every regular Korean course uses:

```yaml
spec:
  curriculumType: BASIC
```

`curriculumType` is a product category, not a curriculum-edition number. `podo-app`,
`podo-backend`, and `grape` already recognize `BASIC`; none supports a version-suffixed type. The
value also forms the tutor-assignment key `PODO_{LANG}_{TYPE}`, so Korean BASIC tutors use
`PODO_KR_BASIC`.

Do not create a new curriculum type for a later content generation. A future English BASIC
generation should remain `(LANG_TYPE=EN, CURRICULUM_TYPE=BASIC)` and receive unused
`CLASS_LEVEL` values. If two generations must coexist at the exact same level, define an
explicit version-selection design first; `VER_YEAR` / `VER_NUM` currently label rows but are
not part of grape's natural key or the app's selection routing.

Grape matches a course using:

```text
CLASS_TYPE + LANG_TYPE + CURRICULUM_TYPE + LESSON_TIME + CLASS_LEVEL + CLASS_WEEK
```

For cover rows, `CLASS_WEEK` is `0`. This means a new course under `BASIC` is safe when its
language, lesson time, or level is distinct. It also means changing a level after a row has
already synced creates a new identity rather than updating the old row; retire the old row
deliberately during migration.

## Korean level bands

The five tracks use low-numbered, non-overlapping ranges:

| Range | Track | Current slots |
|---|---|---|
| `100.000–199.999` | Hangul reading | `100.010` |
| `200.000–299.999` | Core grammar patterns | `200.010–200.120` |
| `300.000–399.999` | Korean in context | `300.010–300.140` |
| `400.000–499.999` | Free talking | `400.010–400.100` |
| `500.000–599.999` | Pronunciation repair | `500.010` |

Primary course positions advance by `0.010` across the entire section. For example, Core
continues `200.980`, `200.990`, `201.000`, `201.010`, rather than stopping at `200.999`.
That provides 9,999 primary positions and leaves nine thousandth-level insertion positions
between neighbours (`200.011–200.019` between `200.010` and `200.020`).

Reasons for these bands:

- `LANG_TYPE=KR` already namespaces them from English and Japanese levels.
- `1–99` stays available for a future simple graded ladder.
- Values below `1000` stay in the backend's regular BASIC range. Existing hard-coded ranges
  at `1000–1999` and `3000–3999` mean Breaking News and free-talking content.
- `999` is already associated with test content and is not a production namespace.
- The backend handles `CLASS_LEVEL` as a Java `Float`; starting at `10000` makes three-decimal
  course slots needlessly close to the type's precision limit.

The numeric bands are stable routing data, not automatic UI sections. To show five named
sections, add explicit range-to-section behavior in `podo-backend` and presentation support
in `podo-app`. Until that feature exists, these levels remain regular BASIC courses rather
than acquiring incorrect legacy section labels.

## Applying the same rule to a future English generation

Keep `LANG_TYPE=EN` and `CURRICULUM_TYPE=BASIC`. First inventory the active EN/BASIC levels
in the target environment, then allocate unused values below `1000`. Because language is
part of course identity, English may reuse `100.xxx`, `200.xxx`, and so on if those ranges
are free for English; the Korean rows do not collide with them.

If an older English generation must remain enabled, a distinct unused level range avoids
grape's duplicate-course check but does **not**
solve version selection: today's regular BASIC query returns every enabled level below
`1000`. Add explicit generation routing in backend/app before enabling both, or retire the
old generation when the new one launches. Do not encode the generation in curriculum type.

## What remains before launch

1. **Tutor eligibility:** create or assign appropriate `PODO_KR_BASIC` tutor rows, and fill
   `tutorGroups` in the enabled course manifests. Empty groups cannot random-match a tutor.
2. **Learner language support:** the student-facing app/schema currently recognizes EN/JP
   paths, not a complete KR curriculum flow. Add and verify the KR selection and labels.
3. **Named track sections:** if the product requires five visible sections, implement the
   range mapping described above in backend and app code.
4. **Runtime publishing:** sync and publish the shared runtime before repointing decks to its
   immutable CDN tag.
5. **Lesson completeness:** enable a course only when every planned lesson has valid lecture
   and prestudy decks and consecutive weeks.

Recommended deployment sequence:

```text
python3 tools/sync-from-authoring.py
python3 tools/import-track-lessons.py <track>
python3 tools/repoint-shared.py
python3 tools/validate.py --contract --env stage
```

`import-track-lessons.py` intentionally keeps an existing `course.yaml`, because `enabled`,
`classLevel`, and `tutorGroups` are reviewed deployment decisions. When an authoring identity
change is intentional—as in this migration to `BASIC`—update both copies and review
the manifest diff explicitly.

## Existing hand-authored Hangul course

`courses/kr/test-hangul-lv1` is an older `BASIC`, level `1` course. The new Hangul track starts at
`100.010`, so grape considers them distinct and can store both. They overlap in learning
purpose, however; decide which course is offered to learners before enabling either one.

## Verification checklist

- Every planned Korean track manifest has `curriculumType: BASIC`.
- Planned levels occupy only `100.xxx` through `500.xxx` and are unique within KR/BASIC/25m.
- Tutor assignments resolve through `PODO_KR_BASIC`.
- No subscription/code-table/admin work exists solely to support a made-up version type.
- `python3 tools/validate.py --contract --env stage` passes before enabling a course.
- If a previously synced level is replaced, its old grape rows are explicitly retired.
