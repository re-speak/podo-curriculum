# English Curriculum — Current Build Plan

**Status:** native catalog and all thirteen active representative pilots approved · first Core,
Contextual and paired Freetalking course batches authored on `stage` and awaiting owner spot check

**Current as of:** 2026-08-19

This is an operational plan, not a diary. It states what exists now, what remains, and what
unblocks what. Git history preserves the implementation chronology; completed work is summarized
here only when it changes the starting point for future work.

---

## Current snapshot

| Area | Current state |
| --- | --- |
| Audience | Japanese speakers learning English; learner support is Japanese and tutor-only operating copy is English |
| Curriculum | 4 tracks · 315 planned items |
| Production-facing catalog | 303 items: 122 Core · 60 Contextual · 121 Freetalking |
| Planning-only catalog | 12 pronunciation lessons; no pronunciation decks authorized |
| Authored lessons | 43 HTML files: 42 active decks (16 Core · 6 Contextual · 20 Freetalking decks covering 10 paired topics) plus one superseded old CTX-1 prototype. Against the 424-deck production target, 382 decks remain. |
| Blueprints | Core, Contextual and Freetalking complete |
| Generated author packets | 315 item briefs plus 4 indexes |
| Review surface | current generated 303-item production catalog owner-approved on 2026-08-18 with no requested row dispositions |
| Core evidence | 122-row generated triage ledger complete; five priority rows resolved against current first-party sources; Core 76/105 productive bands remain provisional |
| Core audit | final progression pass plus a 52-row corpus-informed naturalness audit for Core 71–122; no audit-led TOC changes are pending |
| Automated quality | 87 regression tests; all 43 English HTML files pass with 0 errors and 0 warnings; all render without horizontal overflow at 480px and 360px |
| Deployment | 43 disabled `course.yaml` plans exist, but no English `promotion.yaml` or `courses/en/` output exists; prestudy and learner-visible promotion remain open |

The curriculum is no longer waiting for basic architecture, tooling, native catalog approval or
course identity. Its immediate content risk is whether the approved shells remain natural and
pedagogically sound when repeated across complete courses. Its main product risk is the deferred
prestudy contract, which blocks promotion even while authoring continues.

---

## Decisions already fixed

These are constraints, not open tasks.

- **Learner:** Japanese L1.
- **Support language:** Japanese throughout; English is the target language.
- **Pronunciation readings:** no katakana over English, no `.yomi`, and no `yomi.js` at any level.
- **Core reach:** Pre-A1 through working C1, currently 122 lessons.
- **Contextual identity:** scene-first, standalone practical lessons grouped into five Travel and
  five Business courses; both start at low-intermediate and rise to B2–C1-bridge tasks; no
  continuing fictional plot.
- **Freetalking identity:** 121 shared topics, each designed for accessible and full versions.
- **Pronunciation:** a 12-lesson plan exists, but decks are deferred until Core is substantially
  further along.
- **Decoding:** no separate alphabet/decoding track; the learner already reads Latin script.
- **Product family:** remain `curriculumType: BASIC`; do not invent a version-suffixed family.
- **Audience separation:** required `spec.countryCode` persists as
  `GT_CLASS_COURSE.COUNTRY_CODE`; it belongs there, not in a new level-number scheme.

### Open or deferred gates

| Decision | Why it is open | What it blocks |
| --- | --- | --- |
| CEFR → product ladder mapping | Owner deferred trial/report mapping on 2026-08-13 | recommendation logic, trial report |
| Prestudy contract | Owner deferred prestudy on 2026-08-13 | deployable lesson manifests and shipping |
| Pronunciation notation | No model-line scaffold has been approved | only future pronunciation/scaffold work; not current Core authoring |

Do not invent answers to the product decisions inside a generator. Prepare evidence and options;
the owner/product system supplies the final values.

---

## What is already done

### 1. Curriculum architecture

- **Core:** 122 ordered two-pattern lessons in 22 units, Pre-A1 through working C1. All lessons
  have can-dos, two patterns, expressions, learner-facing grammar support and Japanese-L1 risk
  notes.
- **Contextual:** 2 practical areas, 10 courses and 60 standalone lessons. Every lesson has a
  can-do, who/where/what scene, two learner lines and two partner reactions. Seven lessons carry an
  optional receptive-only `Understand` target. Every lesson also has its required expression field.
  Stable CTX ids and reviewed pattern language survived the architectural replacement.
- **Freetalking:** 11 themes and 121 topics with four explicit formats (`story`, `opinion`,
  `choose`, `両国`), a learner-facing English title, an immediate opening and a question ladder.
  Titles name a personal experience, concrete angle or natural choice rather than using translated
  category labels. The blueprint defines accessible and full language loads, correction loops and
  format-specific model pages.
- **Pronunciation:** 12 Japanese-L1 contrastive lessons are planned and parsed, but remain
  planning-only.
- Cross-track Core references were re-derived against the 122-lesson spine and mechanically
  range-checked. Generated briefs carry positive prerequisites and explicit “not yet” boundaries.

### 2. Authoring contract and pilot

- `AGENTS.md`, `LESSON-CREATION-WORKFLOW.md`, `PROOFREADING-WORKFLOW.md` and
  `tracks/_conventions.md` define the English-specific production and review rules.
- Core, Contextual and Freetalking each have a production blueprint.
- Core 20 is an approved, visually reviewed 25-page canonical deck. Core 12–24 now forms the first
  complete approved-shell Core batch on `stage`.
- The old authored CTX-1 deck under `arriving-and-getting-settled` belongs to the retired four-area
  curriculum and remains a superseded prototype, not a canonical source. Replacement Travel CTX
  1–6 now forms the first Contextual batch on `stage`.
- FT-1 is authored as separate 13-page full and accessible decks, visually reviewed at 480px and
  360px, and owner-approved on 2026-08-18 as the matching canonical shells for their language loads.
  Topics 1–8 now form the first paired Freetalking batch on `stage`.
- `new_lesson.py` copies only an approved English shell, retargets stable identity and paths,
  clears inherited vocabulary, refuses overwrite and keeps non-Core tracks behind their pilot gate.
- The running lexicon classifies new, recycled, assumed-known and receptive-only vocabulary.
  Core 20 currently owns two new content words. Deck validation enforces declarations, hint-chip
  coverage and the normal eight-word Core/Contextual ceiling.

### 3. Generated infrastructure

- One strict parser covers all four TOCs and rejects discontinuous or malformed source structure.
- Core's parser also validates 20 stable Japanese-L1 spiral targets: reviews cannot precede their
  introduction, exceed two per lesson, use unknown modes, remain shallow, or omit delayed return.
- `build_lesson_briefs.py` generates all 315 briefs and four indexes.
- Core briefs carry the whole-model production gate, any explicit bounded survival chunk, and the
  lesson's planned spiral-review targets and modes.
- `build_grammar_map.py` generates the 122-row Core sequence/coverage map, a review-spiral health
  table, and an explicit grammar-support completeness check.
- `build_catalog.py` generates the 303-item native-review catalog; the catalog holds no curriculum
  facts of its own.
- `parse_catalog_review.py` validates copied feedback against stable ids, titles and first-line
  snapshots, then emits structured JSON without editing a TOC.
- `build_running_lexicon.py` generates the authored vocabulary ledger from lesson metadata.
- `check_deck.py` checks identity, references, duplicate ids, inline code, no-yomi, tutor-script
  parity, reorder chunking, reorder answer solvability and vocabulary ownership/load.
- Eighty-seven regression tests prove parser contracts, shell retargeting, generated
  brief/map/ledger/catalog/lexicon freshness and review-intake failure cases.

### 4. Shared foundation

- The language-neutral runtime, UX philosophy and viewer were moved to the repository root and all
  in-repository references were repaired.
- English uses the shared runtime without forking it. Korean trial art remains under `korean/` and
  is not implicitly reusable.
- This repository is now the authoring source. There is no external authoring-sync step: reviewed
  drafts are named in `promotion.yaml` and promoted directly into `courses/en/` with
  `tools/promote.py` when the prestudy contract permits it.

---

## Native catalog approval

The owner passed the current production-facing native catalog on 2026-08-18 with no requested row
dispositions. That approval covers the 303 Core, Contextual and Freetalking rows generated from the
current authoritative TOCs; Pronunciation remains planning-only and was not promoted by this pass.
The exact approved snapshot is recorded in
[`reference/native-catalog-approval.md`](./reference/native-catalog-approval.md).

The catalog hold on additional Core and Freetalking authoring is therefore lifted. Generated files
remain generated—change authoritative TOCs and rebuild them—and product ids and Pronunciation remain
behind their separate gates.

The grammar-support pass is complete, and the earlier CTX-54/CTX-58 gap report was stale: both
lessons already had expressions in the authoritative TOC. Neither fact pre-approves a catalog row;
grammar and expression support must move with any row later rewritten or demoted. The hold prevents
avoidable deck-production rework. It does not block read-only evidence gathering, decision
preparation, tooling that holds no curriculum facts, or documentation repair.

The owner approved the broader naturalness and transfer revision on 2026-08-14. The final deep pass
then removed remaining prerequisite leaks, overloaded pairs, weak slots and written-register
defaults while preserving every stable ID. It also raised the two advanced Business course floors
to Core 86 and Core 101 and made future-Core use mechanically require a bounded-chunk label. The
English title pass replaced all 121 Freetalking title snapshots while preserving their IDs. The
generated catalog was rebuilt after these revisions. Do not
submit a copied review form made from a pre-2026-08-14 catalog; open the current catalog and carry
forward only feedback whose row snapshot is unchanged. Pronunciation planning was also corrected,
but it remains outside the production-facing review catalog.

---

## Remaining work, in execution order

### A. Work that can proceed during native review

#### A1. Maintain the Core evidence ledger

The generated [`reference/core-evidence-ledger.md`](./reference/core-evidence-ledger.md) connects
all 122 lessons to a Core Inventory category or explicit gap and to the nearest CEFR Companion
Volume scale. It deliberately distinguishes broad function support from exact exponent or level
evidence. The current English Grammar Profile app and first-party Cambridge usage sources resolved
the five priority rows: Core 77 has a direct EGP B1/B2 progression; Core 79 and 84 have exact B1
use evidence; Core 76 and 105 have direct natural-form attestation but no exact EGP productive-band
result. Their B1+/B2 placements therefore remain working curriculum bands.

The former blanket task to replace all 122 rows with individual EGP results is no longer a gate.
Many Core rows are interactional or lexical rather than a discrete EGP grammar claim, and the EGP
is a profile rather than a prescribed teaching sequence. Add granular evidence when a native
disposition or band decision depends on it; do not manufacture a one-to-one match for every row.
Keep the ledger generated and compact, and keep corpus naturalness and learner performance in their
own artifacts.

The ledger records:

- the relevant Core Inventory item or equivalent source;
- EGP form-and-meaning evidence where applicable;
- a CEFR descriptor or an explicit “no direct descriptor” result;
- the current working band and an evidence status.

Do not convert a missing citation into invented confidence. The owner-approved audit corrections
are already reflected in the live TOC; any further evidence-led rewrite waits for native review.
Until representative lessons and learner evidence resolve the two open productive placements,
B1+–C1 remains a working organization rather than a validated CEFR claim.

#### A2. Maintain the corpus/naturalness audit

[`reference/core-corpus-naturalness-audit.md`](./reference/core-corpus-naturalness-audit.md) now
records construction queries, first-party corpus-informed evidence, pair-load judgments and
verdicts for all 52 Core 71–122 rows without changing the live TOC. All 104 primary model lines
pass; eleven rows carry bounded author watches for morphology, register, regionality or pragmatic
delivery. Re-run an exact row when native feedback changes its snapshot; do not repeat the whole
audit for unchanged rows or turn supporting-expression watches into third production objectives.

#### A3. Prepare the product-decision packet

The [`reference/product-decision-packet.md`](./reference/product-decision-packet.md) now records a
collision-checked recommendation for:

- CEFR-to-trial/report bands;
- English `classLevel` allocation;
- confirmed `LANG_TYPE` behavior;
- course-code conventions and course boundaries;
- the required `countryCode: JP` authoring and downstream import contract.

The owner fixed `LANG_TYPE=EN`, `COUNTRY_CODE=JP`, `BASIC`, 25-minute lessons, natural Core arcs and
separate accessible/full Freetalking courses on 2026-08-13. Trial mapping and prestudy were deferred.
The owner approved the replacement Contextual direction on 2026-08-13: practical, standalone
courses rather than shows. The packet now records the corresponding ten natural course cuts. It
does not reserve identifiers or modify product data. No lesson is deployable while prestudy is
deferred.

### B. Native catalog review — complete

No item-specific changes were requested. The current TOC snapshots and regenerated catalog are the
approved authoring baseline. Later revisions reopen review only for changed rows; they do not erase
the approval of unchanged stable-id snapshots.

### C. Prove representative lessons before scaling

1. **Complete:** authored three structurally different Core candidates: Core 32 narrative, Core 45
   comparison, and Core 82 B1+ workplace nuance.
2. **Complete:** reviewed them together for pedagogy, naturalness, vocabulary load, static
   correctness and rendered behavior at 480px and 360px.
3. **Complete:** repaired repeated failures in the shared workflow, retrospective checklist and
   deck checker rather than leaving lesson-local exceptions.
4. **Complete 2026-08-19:** owner approved the three Core representatives and opened the wider
   Core course-batch gate.
5. **Complete 2026-08-19:** owner approved replacement low-intermediate Travel CTX-1 as the
   canonical Contextual shell. It demonstrates the task-first opening and standalone transfer; do
   not reuse the superseded CTX-1 deck as a canonical source.
6. **Complete:** FT-1 accessible and full were explicitly approved on 2026-08-18 and are canonical
   for their respective language loads. FT-7, FT-9 and FT-49 now provide three additional audited
   full/accessible pairs; the owner approved the full representative set on 2026-08-19 and opened
   the wider paired-topic batch gate.
7. Only after the representative set exists, build the one-way authored-HTML proofreading packet
   projection. One Core pilot is not enough evidence for a universal packet schema.

### D. Create product structure

Within the approved curriculum scope:

1. Maintain the 43 approved course cuts generated by `plan_courses.py`: 11 Core, 10 Contextual and
   22 paired Freetalking courses.
2. Keep the generated, schema-valid `course.yaml` plans disabled with required
   `countryCode: JP`. Do not generate deployable lesson manifests while prestudy is deferred;
   never maintain a second curriculum copy inside the generator.
3. Preserve the approved course codes and `classLevel` mapping. The destination supplies
   `LANG_TYPE=EN`; do not add it to `course.yaml`.
4. Do not build trial materials while trial mapping remains deferred.
5. After prestudy is approved, add reviewable `promotion.yaml` manifests beside the drafts and use
   `tools/promote.py` to produce `courses/en/`; never edit the promoted lesson directories by hand.
6. Prove promotion, shared-reference repointing, contract validation and the stage catalogue before
   opening any `stage` → `main` release PR.

### E. Scale and validate

1. Author by approved course batches, with writers owning disjoint lesson files and an orchestrator
   owning TOCs, generated artifacts, coverage boundaries and shared conventions.
2. Run static checks, exact-generation tests, proofreading and rendered QA for every batch.
3. Maintain the running lexicon and audit Contextual scenes and outcomes for duplication in course order.
4. Conduct learner pilots: two lessons per level, recorded task performance, delayed retrieval at
   one week and a transfer task.
5. Revisit pronunciation notation and deck production only after the remaining Core band evidence, representative
   lessons and the owner gate justify it.

---

## Immediate next action

The first approved-shell course batches are on `stage`: Core 12–24, Contextual Travel 1–6, and the
paired accessible/full Freetalking course 1–8. Their generators, generated-source equality tests,
full-corpus static checks and rendered checks form one review unit. The immediate action is an owner
spot check across all three tracks and both Freetalking loads.

If that review passes, the next review unit is **39 new decks**: Core 1–11, Contextual Travel 7–12,
and paired Freetalking 10–20 (FT-9 already exists). Author them from explicit, reviewable
course-specific content data while reusing the approved shell-building machinery. The three first-
batch generators are deliberately narrow; do not turn their hard-coded content into an implicit
universal generator. Run exact-generation tests, the full checker, the running-lexicon rebuild and
rendered QA, then stop for owner review again. Do not treat catalog or deck approval as learner-pilot
evidence.

---

## Definition of production readiness

English is ready for scaled production only when all of the following are true:

- the approved native catalog snapshot is current, with any later changed rows re-reviewed;
- the Core evidence/corpus audits have no untriaged high-risk rows;
- grammar and expression support remains complete and aligned on the accepted spine;
- the representative Core lessons, replacement Contextual pilot and paired Freetalking examples
  remain the explicit approved golden set;
- course and product identity decisions are fixed and manifests validate;
- the in-repository promotion path passes end to end.

It is ready to ship only after batch QA, trial/report material and learner-pilot evidence are also
complete.
