# English Product Decision Packet

**Prepared:** 2026-08-13
**Scope:** Japanese-market learners studying English
**Decision status:** owner decisions recorded 2026-08-13; no product rows or identifiers reserved

> **Contextual direction approved 2026-08-13:** five standalone Travel English courses and five
> standalone Business English courses, both beginning at low-intermediate and rising to B2–C1
> bridge work. The earlier show/season and interim four-area identifiers are retired.

> Prefer the low-cognitive-load interactive version:
> [`../product-decisions.html`](../product-decisions.html)

## Approved decision record

The owner selected:

1. **Natural learning arcs** for course packaging.
2. **Separate accessible and full Freetalking courses.**
3. **Defer trial mapping.** No trial starting points or report bands are approved yet.
4. **Defer prestudy.** Lecture prototypes may be authored after their other gates clear, but no
   English lesson is deployable until a prestudy contract is approved and both slots exist.

Fixed product facts remain `LANG_TYPE=EN`, `COUNTRY_CODE=JP`, `CURRICULUM_TYPE=BASIC`, and
`LESSON_TIME=25`.

The natural-arc decision approves Core unit boundaries and Contextual's ten practical course
boundaries. Contextual courses organize visible use cases and language load; they do not create
plot prerequisites between lessons.

## Resulting product shape

Adopt the following product shape:

- subject language: **`LANG_TYPE=EN`**;
- audience scope: **`COUNTRY_CODE=JP`**;
- regular product line: **`CURRICULUM_TYPE=BASIC`**;
- lesson length: **25 minutes only** for the first release;
- Core and Contextual courses in unused, regular-course bands below 1000;
- Freetalking in the existing 3000–3999 Freetalking section;
- all new courses created disabled until both lesson slots and stage validation pass.

This supports Core, Contextual, and Freetalking planning once their editorial gates clear.
Trial/report work is deferred. Prestudy is also deferred, so lecture-only work remains prototype
work and must not create deployable lesson manifests.

## 1. What the product already decides for us

| Field | Decision | Reason |
| --- | --- | --- |
| `classType` | `PODO` | The curriculum deployment contract supports this class type. |
| `LANG_TYPE` | `EN` | This is the language being learned. `JP` means Japanese as the subject, not Japanese support text. |
| `COUNTRY_CODE` | `JP` | Audience belongs in the country scope. It prevents this curriculum mixing with English for the Korean market. |
| `CURRICULUM_TYPE` | `BASIC` | This is an entitlement and tutor-matching product line, not a content version. Do not invent `BASIC_V2` or a similar value. |
| `LESSON_TIME` | `25` | All three blueprints describe 25-minute sessions. A 15-minute edition would be a separate product and should be designed later. |
| enabled state | `false` initially | A natural-key identity becomes learner-visible when enabled. Incomplete or unreviewed courses stay disabled. |

The database natural key is:

```text
(CLASS_TYPE, LANG_TYPE, CURRICULUM_TYPE, LESSON_TIME,
 CLASS_LEVEL, CLASS_WEEK, COUNTRY_CODE)
```

Changing `classLevel`, `lessonTime`, or `countryCode` creates a different course identity; it is
not an in-place rename. Slugs are the permanent human/git identity and must never be reused.

## 2. Recommended regular-course allocation

The numbers below are deliberately unique across the currently observed English market rows, even
though country is now part of the formal natural key. This is defensive: some existing backend
progression helpers still query by language, product, time and level without country. Unique bands
prevent those older paths from selecting an English-for-Korean-market row by accident.

### Core · 11 courses · `100.xxx`

Units stay intact and each course is approximately 10–13 lessons.

| `classLevel` | Permanent slug | Core span | Working band |
| --- | --- | ---: | --- |
| `100.010` | `core-first-exchanges-1` | 1–11 · Units 1–2 | Pre-A1 → A1 |
| `100.020` | `core-first-exchanges-2` | 12–24 · Units 3–4 | A1 |
| `100.030` | `core-daily-life-and-past` | 25–36 · Units 5–6 | A1 → A2 |
| `100.040` | `core-plans-and-comparison` | 37–47 · Units 7–8 | A2 |
| `100.050` | `core-experience-and-ideas` | 48–59 · Units 9–10 | A2 → B1 |
| `100.060` | `core-careful-interaction` | 60–70 · Units 11–12 | B1 |
| `100.070` | `core-work-and-arrangements` | 71–80 · Units 13–14 | B1+ |
| `100.080` | `core-nuance-at-work` | 81–91 · Units 15–16 | B1+ → B2 |
| `100.090` | `core-diplomacy-and-reasoning` | 92–102 · Units 17–18 | B2 |
| `100.100` | `core-emphasis-and-tone` | 103–112 · Units 19–20 | B2 → C1 bridge |
| `100.110` | `core-advanced-stance` | 113–122 · Units 21–22 | C1-associated language |

The titles deliberately stop short of claiming that finishing a course certifies the CEFR band.
The evidence audit supports a progression and a C1 bridge, not a proficiency award.
The second slug preserves the approved Core 20 pilot's existing authoring path; moving that deck
for a more decorative name would create migration work without product value.

### Contextual · 10 courses · `200.xxx`

Each six-lesson course exposes one practical learner need. The lessons are standalone; the course
boundary represents coherent coverage and a shared Core floor, not a season or story arc.

| `classLevel` | Permanent slug | Lessons | Practical area |
| --- | --- | ---: | --- |
| `200.010` | `ctx-travel-arrivals-transport` | CTX 1–6 | Travel English |
| `200.020` | `ctx-travel-hotels-food` | CTX 7–12 | Travel English |
| `200.030` | `ctx-travel-disruptions-urgent-problems` | CTX 13–18 | Travel English |
| `200.040` | `ctx-travel-independent-social` | CTX 19–24 | Travel English |
| `200.050` | `ctx-travel-complex-decisions` | CTX 25–30 | Travel English |
| `200.060` | `ctx-business-workplace-essentials` | CTX 31–36 | Business English |
| `200.070` | `ctx-business-projects-deadlines` | CTX 37–42 | Business English |
| `200.080` | `ctx-business-meetings-decisions` | CTX 43–48 | Business English |
| `200.090` | `ctx-business-negotiation-diplomacy` | CTX 49–54 | Business English |
| `200.100` | `ctx-business-leadership-high-stakes` | CTX 55–60 | Business English |

The previous fictional-work slugs and the interim four-area slugs (`ctx-arriving-*`,
`ctx-routines-*`, `ctx-important-*`, `ctx-international-*`, `ctx-projects-*`, `ctx-decisions-*`,
`ctx-travel-essentials`, `ctx-travel-problems-*`, `ctx-meeting-*`, and `ctx-opinions-*`) are
retired. Do not reuse them for the two-area curriculum.

### Freetalking · 22 courses · `3100.xxx`

Each of the 11 themes becomes two adjacent courses because the B1 accessible and B2–C1 full
versions are separate authored decks, not a runtime toggle. Use this allocation rule:

| Version | Theme 1 | Theme 2 | … | Theme 11 |
| --- | ---: | ---: | ---: | ---: |
| B1 accessible | `3100.009` | `3100.019` | … | `3100.109` |
| B2–C1 full | `3100.010` | `3100.020` | … | `3100.110` |

Slug shape:

```text
talk-<theme>-accessible
talk-<theme>-full
```

This keeps each pair adjacent and places it in the existing 3000–3999 Freetalking section. The
accessible version changes language load only; it must retain the same adult topic and reasoning.

## 3. Deferred trial and report mapping

**Owner decision:** defer this work. The table below is retained only as the rejected-for-now
proposal that informed the decision; it is not an approved mapping and must not enter code,
manifests or learner-facing reports.

Keep the existing external band codes (`B`, `C1`, `C2`, `D`) for API compatibility, but give them
clear learner-facing labels and map them to exact Core entry points.

| Existing code | Report label | Curriculum interpretation | Recommended regular start |
| --- | --- | --- | --- |
| `B` | Foundation · 基礎 | Pre-A1–A1 | Core 1 · `100.010`, week 1 |
| `C1` | Developing · 初中級 | A2 | Core 30 · `100.030`, week 6 |
| `C2` | Independent · 中級 | B1/B1+ | Core 54 · `100.050`, week 7 |
| `D` | Advanced · 中上級以上 | B2 and C1 bridge | Core 87 · `100.080`, week 7 |

The report should say “recommended starting point,” not “your CEFR level.” A short trial cannot
certify a CEFR level, and Core's final units contain C1-associated language without proving full C1
performance.

### Trial blockers to fix before shipping a trial

1. `LevelUtils` currently hard-codes `EN` trial codes to the Korean-market ladder (`3`, `4`,
   `5/week 10`, `7`) and has no country input. Add a country-aware mapping while preserving the
   existing KR behavior.
2. Several next-course and cover helpers still query by `LANG_TYPE + CURRICULUM_TYPE +
   LESSON_TIME + CLASS_LEVEL` without `COUNTRY_CODE`. Make all progression paths country-scoped.
3. The curriculum `lesson.yaml` schema has no trial-band/`BOOK_TYPE` field, while the Grape sync
   writes regular lessons as `MAIN`. Decide how a deployable trial declares the four diagnostic
   bands before generating English trial manifests.

These are trial/product-path blockers, not blockers for disabled regular pilot courses.

## 4. Deferred prestudy

Production requires both `lecture` and `prestudy` deck slots. The English authoring tree currently
defines only the live 25-minute lesson, so the representative pilot would not yet be deployable.

**Owner decision:** defer prestudy. The candidate below remains design evidence, not an approved
blueprint:

- Core/Contextual: 5–7 pages—outcome, hear/read the two targets, meaning check, one retrieval task,
  and a close. It previews; it does not duplicate the full lesson.
- Freetalking: topic preview, optional vocabulary, and two private think prompts. It must not script
  the learner's opinion.
- Use the same interaction and metadata contracts as the lecture deck.
- Do not point both product slots at the same full lesson merely to satisfy schema validation.

## 5. Repository work permitted by these decisions

### Authoring repository

1. Maintain `english/tools/plan_courses.py` for approved Core, Contextual, and Freetalking inputs.
2. Keep every generated `course.yaml` disabled and set its required market identity to
   `countryCode: JP`.
3. Do not generate deployable `lesson.yaml` while prestudy is deferred; both approved deck slots
   remain mandatory.
4. Validate stable slugs, continuous weeks, unique levels and TOC coverage.

### Consuming `podo-curriculum` repository

1. Add language declaration `en: { langType: EN, audience: ja, displayName: 영어 }`.
2. Use an explicit English course importer. The existing authoring sync intentionally mirrors
   references and runtime only; it does not copy `course.yaml` or make decks deployable. The
   importer must preserve `countryCode` verbatim while the destination directory supplies
   `LANG_TYPE=EN`.
3. Promote only complete courses into `courses/en/`; both deck slots are mandatory.
4. Validate and plan from a branch based on `origin/stage`, deploy to stage/qa/dev, inspect, then
   release through `stage → main`.

Grape's current main branch accepts and persists `countryCode` in the curriculum natural key. No
new Grape feature is required for regular course sync, but every environment must have the
`GT_CLASS_COURSE.COUNTRY_CODE` column before a JP-scoped apply.

## 6. Collision check

Read-only stage inspection on 2026-08-13 found:

- 22 English BASIC 15-minute covers, all `COUNTRY_CODE=KR`;
- 58 English BASIC 25-minute covers, all `COUNTRY_CODE=KR`;
- 4 English TRIAL 25-minute covers, all `COUNTRY_CODE=KR`;
- **zero existing `LANG_TYPE=EN`, `COUNTRY_CODE=JP` BASIC or TRIAL covers**.

The proposed `100.xxx`, `200.xxx`, and `3100.xxx` values did not collide with the observed English
rows. Stage is refreshed from production but is not a permanent reservation system; run the same
check again immediately before the first apply.

## 7. Remaining owner gates

- Complete native catalog dispositions before further Core production.
- Review the regenerated practical Contextual catalog, then approve one representative pilot
  before any Contextual batch authoring.
- Reopen trial mapping only when trial/report work becomes a priority.
- Reopen prestudy before any English lesson is represented as deployable.

## Evidence inspected

- English authoritative TOCs, blueprints and [`BUILD-PLAN.md`](../BUILD-PLAN.md).
- `podo-curriculum` schemas, model, deploy workflow and current course manifests.
- Grape's current country-scoped curriculum sync and natural-key implementation.
- Podo backend course discovery, country filtering, progression and trial-level mappings.
- Podo app lesson/course surfaces and the existing server-title display contract.
- Read-only `GT_CLASS_COURSE` stage snapshot on 2026-08-13.
