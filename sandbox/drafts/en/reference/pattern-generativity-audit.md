# Core and Contextual pattern-generativity audit

**Audit date:** 2026-08-21
**Scope:** 119 active Core lessons and 60 active Contextual English lessons
**Sources of truth:** the two track tables of contents, their generated briefs, and the active lesson decks

## Question

This audit is narrower than a naturalness or grammar audit. It asks whether each of the two primary
targets is a reusable speaking scaffold, or merely an expression with a decorative lexical slot.
It also asks whether the pair completes one communicative job. Activity design is checked
separately: a strong frame can still have a mechanical exercise, and a varied exercise cannot make
a weak frame worth teaching.

## Standard and dispositions

Every row was tested against `teaching-philosophy.md` section 4: purpose, retrievability,
boundaries, at least four useful completions, transfer, load, readiness, contemporary use, and pair
cooperation. The recorded disposition is one of **Keep**, **Broaden**, **Reframe**, **Merge**, or
**Cut/replace**.

A narrow complement type is not automatically a failure. `Could I have ___?` remains useful across
many real requests. Conversely, four interchangeable nouns do not prove generativity when the
learner never has to vary meaning, form, or communicative consequence.

## Corpus-level activity evidence

`check_deck.py` was run across both complete track trees after the Pre-A1 repair.

- Active lessons reviewed: **179**.
- Repeated two-branch choice pages with the same correct branch throughout: **0**.
- A1+ teaching sets whose exemplars differ by one aligned word only: **0**.
- One old Contextual prototype produced 28 unrelated operating-contract errors; it is explicitly
  superseded and is not part of the 60-lesson Contextual inventory.

These are automated activity results, not substitutes for the curriculum dispositions below.

## Core dispositions

### Broaden — completed

| IDs | Decision | Result |
| --- | --- | --- |
| CORE-1–3 | Six formulaic Pre-A1 rows over-segmented names, jobs, origin, introductions, possession, and identity questions. | Replaced by three broader lessons: `I'm ___` / `My ___ is ___`; origin and residence across people; `Is this ___?` / `Are you ___?`. CORE-4–6 retired. |

### Keep

| IDs | Why the frames remain generative |
| --- | --- |
| CORE-7–11 | Existence, weather, counted requests, first/shared reference, and location questions accept several complement types or require a real form decision. They are bounded because A1 load should be bounded, not because they are memorised scripts. |
| CORE-12–18 | Routine time, yes/no questions, negatives and alternatives, third-person agreement, wh-questions, frequency, and ability all accept productive action phrases; subject, agreement, time, and polarity vary across the sets. |
| CORE-19–24 | Price checks, help, permission, ordering, countability, and repair are high-reach conversational anchors. Their noun or phrase slots transfer across service encounters and the paired response completes the same exchange. |
| CORE-25–29 | Current activity, routine-versus-now, preferences, invitations, and arrangements require action, time, person, or polarity choices rather than one-category noun replacement. |
| CORE-30–36 | Past state and setting, activities, event sequences, questions, negatives, countability, sequencing, and background interruption vary event structure and serve coherent recounting jobs. |
| CORE-37–47 | Plans, offers, possibility, advice, obligation, factual answers to negative questions, description, degree, comparison, superlatives, preferences, and experiencer/stimulus adjectives remain reusable beyond their model scenes. |
| CORE-48–59 | Experience, finished time, duration, ongoing cause, progress, reasons, relative identification, concession, conditions, time clauses, and purpose all take phrase or clause content while preserving a retrievable conversational anchor. |
| CORE-60–70 | Requests, permission, embedded questions, preference, troubleshooting, theft reports, hypotheticals, wishes, deduction, and reported requests transfer across people and situations; the pairs form request/response, problem/repair, or evidence/inference exchanges. |
| CORE-71–86 | Regret, past inference, sequencing, unrealised plans, former habits, services, unmet expectations, future estimates, role description, status/risk, clarification, negotiation, disagreement, and follow-up use proposition-sized slots appropriate to B1+. |
| CORE-87–102 | Degree, near-zero quantity, reframing, sufficiency, evidence conditions, concession, suggestions, objection, repair, refusal, cause, inference, result, dependency, and fallback are discourse operations rather than lexical substitution frames. |
| CORE-103–122 | Focus, linked change, topic management, register, impact/intent, qualification, counterargument, reversal, summary, withholding, softened direction, boundaries, and framing all retain a short spoken anchor while accepting a developed proposition, which is the intended B2–C1 progression. |

### Reframe, merge, cut/replace

No remaining Core row earned one of these dispositions. Several adjacent rows share grammar, but
they do different communicative work or form an intentional progression—for example CORE-49 versus
CORE-50 (present relevance versus finished past time), and CORE-81 versus Contextual CTX-31 (Core
inventory followed by applied retrieval). Merging those would remove a useful contrast rather than
eliminate a decorative slot.

## Contextual English dispositions

### Keep

| IDs | Why the frames transfer beyond one script |
| --- | --- |
| CTX-1–6 | Seat requests, immigration answers, number repair, ticket comparison, directions, and transport arrangements preserve stable service moves while destination, quantity, option, route, and request content change. |
| CTX-7–12 | Reservation identification, temporary arrangements, hotel remedies, dietary checks, order correction, exchanges, and booking changes transfer across hotels, restaurants, shops, dates, people, and objects. |
| CTX-13–18 | Rebooking, baggage description, route recovery, lost property, charge disputes, and medical triage are high-consequence tasks with multiple event, object, time, description, and remedy completions. |
| CTX-19–24 | Priority-based recommendations, joining activities, invitations, compromise, cultural repair, and proportionate complaint use clause-level choices and produce different outcomes when the slot changes. |
| CTX-25–30 | Escalation, insurance evidence, accessibility requirements, conflicting records, safety judgment, and post-trip advice are optional higher-level tasks whose proposition slots transfer across consequential cases. |
| CTX-31–36 | Role descriptions, call repair, time-zone scheduling, file requests, progress updates, and technical blockers deliberately retrieve Core anchors with workplace-specific vocabulary and one transparent expansion. |
| CTX-37–42 | Priority negotiation, ownership, risk, deadlines, bad news, and action summaries vary owners, deliverables, constraints, dates, and consequences; changing a slot changes the project outcome. |
| CTX-43–48 | Interruption, decision summaries, recommendations, uncertainty, upward disagreement, and decision framing are meeting moves with proposition or action slots, not memorised meeting sentences. |
| CTX-49–54 | Reframing, conditional proposals, commitment boundaries, trade-offs, concession, and deadlock repair transfer across negotiation subjects and explicitly require contrasting propositions. |
| CTX-55–60 | Performance conversations, actionable feedback, uncertainty, stakeholder persuasion, crisis updates, and qualified recommendations use developed evidence/action slots appropriate to the B2–C1 bridge. |

### Broaden, reframe, merge, cut/replace

No Contextual row currently earns one of these dispositions. Contextual lessons are allowed to be
domain-bounded; the test is whether the frame survives changed facts inside that domain. Each of
the 60 rows does. Their continued approval depends on the Core ownership floor remaining honest:
when a repaired Core frame changes, the affected Contextual row must be rechecked rather than
grandfathered by ID.

## Release consequence

The curriculum-level defect was concentrated in the original six-row Pre-A1 runway and is repaired
in the authoring source. The broader active Core and Contextual inventories pass the stricter
generativity test; rewriting them merely to make slots visually wider would increase load without
adding communicative range.

The separate activity gate remains mandatory on every regeneration. A future deck fails even when
its TOC row is kept if all correct branches are identical or its A1+ exemplars collapse to one-word
substitution. The automated checks make those regressions blocking rather than relying on this
dated audit document.
