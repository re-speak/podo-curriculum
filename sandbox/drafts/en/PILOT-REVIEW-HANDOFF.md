# English pilot review handoff

Status snapshot: 2026-08-20

This document preserves the context behind the three English reference lessons and provides a
starting point for owner feedback. The immediate goal is to review these lessons as real learner
experiences. The larger goal is to turn the right feedback into explicit rules, source changes,
and checks that improve the rest of the English curriculum without blindly copying a local fix.

For the existing standards distilled from earlier reviews, also read
[`reference/pilot-feedback-release-checklist.md`](reference/pilot-feedback-release-checklist.md).

## Short version

Three canonical lessons were selected to represent the three active English curriculum types:

| Type | Reference lesson | Why this lesson |
| --- | --- | --- |
| Core Patterns | Core 20 — `Could you help me with this?` | Original approved Core pilot and canonical two-pattern lesson shell |
| Contextual English | CTX-1 — `Check in and request a seat` | Approved replacement Contextual pilot and canonical practical-scene shell |
| Freetalking | FT-1 Full — `Something that surprised you about another culture` | Approved Full Freetalking pilot and canonical article-to-discussion shell |

The request began as a three-lesson pilot promotion. It was changed to publish each pilot in its
complete course so no lesson had to be temporarily renamed or reordered. Core 20 therefore remains
week 9 in its natural 13-lesson course; CTX-1 and FT-1 remain week 1 in theirs.

The result is live in production. This is not a mockup-only review: feedback can be grounded in the
same deployed HTML a learner and tutor receive.

## What shipped

The three complete Japan-market English courses were released as `BASIC`, 25-minute courses with
`enabled: true`:

| Course | Production cover row | Lessons | Decks |
| --- | ---: | ---: | ---: |
| `core-first-exchanges-2` | 12693 | Core 12–24: 13 | 26 |
| `ctx-travel-arrivals-transport` | 12707 | CTX 1–6: 6 | 12 |
| `talk-between-two-countries-full` | 12714 | FT 1–8 Full: 8 | 16 |

That is 27 lesson rows and 54 uploaded deck slots. Every lesson has both `lecture` and `prestudy`,
which is required for class creation. For these promoted pilots, both slots come from the same
canonical draft `lesson.html`; the lesson itself still decides what belongs in pre-study and what
the tutor should skip during class.

Release trail:

- `643f7060` — promoted the three complete courses in canonical order.
- `5b06e289` — added the missing English deployment mapping after the first stage apply exposed it.
- [PR #59](https://github.com/re-speak/podo-curriculum/pull/59) — `stage` to `main` release.
- `20fb3824` — production merge commit.
- Cloud Build `9423e114-2867-4653-993b-2014b9d8c9e1` — successful production deployment.

The Core and Contextual pilots also retain the approved Korean-style correction/diff treatment for
their open own-sentence activities. That component is part of the review target: it should be
judged as a teaching interaction, not merely as a visual restyle.

## The three review targets

### 1. Core Patterns — Core 20

`Could you help me with this?` / `I can help with ...`

- Canonical source:
  [`tracks/1-core-patterns/courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html`](tracks/1-core-patterns/courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html)
- Production:
  [lecture](https://storage.googleapis.com/podo-assets/lemonboard-html/12702/lecture.html) ·
  [prestudy](https://storage.googleapis.com/podo-assets/lemonboard-html/12702/prestudy.html)
- Natural position: week 9 of 13.
- Page IDs: `lesson-goal`, `words-you-know`, `part1-intro`, `p1-teach`, `p1-read`,
  `p1-rule`, `p1-choose`, `p1-reorder`, `p1-fill`, `p1-translate`, `p1-write`,
  `part2-intro`, `p2-teach`, `p2-read`, `p2-rule`, `p2-reorder`, `p2-fill`,
  `p2-translate`, `p2-write`, `part3-intro`, `p3-model`, `p3-complete`,
  `p3-freetalk`, `in-the-wild`, `native-tip`.

What this pilot is meant to prove:

- Two useful patterns can be taught and practiced without becoming two disconnected mini-lessons.
- The learner moves from recognition and controlled construction into a reciprocal request-and-help
  exchange.
- Japanese support helps without becoming katakana pronunciation or doing the English task for the
  learner.
- The final pages transfer the patterns into a plausible real-world interaction.
- The correction/diff box makes open production more useful without making the activity feel heavy.

Questions worth answering:

- Would a real person naturally say the model lines in the stated situations?
- Is the distinction between asking for help and offering help clear enough to remember and use?
- Does each practice page add a meaningful step, or does any part feel repetitive?
- At `p1-write` and `p2-write`, does correction help the learner understand what changed?
- Does `p3-freetalk` create a genuine exchange with the tutor rather than a disguised drill?
- Does `in-the-wild` finish a practical job, or stop too soon after producing the target line?

### 2. Contextual English — CTX-1

`Check in and request a seat`

- Canonical source:
  [`tracks/2-contextual-english/courses/ctx-travel-arrivals-transport/lessons/01-check-in-and-request-a-seat/lesson.html`](tracks/2-contextual-english/courses/ctx-travel-arrivals-transport/lessons/01-check-in-and-request-a-seat/lesson.html)
- Production:
  [lecture](https://storage.googleapis.com/podo-assets/lemonboard-html/12708/lecture.html) ·
  [prestudy](https://storage.googleapis.com/podo-assets/lemonboard-html/12708/prestudy.html)
- Natural position: week 1 of 6.
- Page IDs: `situation-card`, `scene`, `lesson-goal`, `expressions`, `understand`,
  `part1-intro`, `p1-teach`, `p1-read`, `p1-rule`, `p1-reorder`, `p1-fill`,
  `p1-translate`, `p1-write`, `part2-intro`, `p2-teach`, `p2-read`, `p2-rule`,
  `p2-reorder`, `p2-fill`, `p2-translate`, `p2-write`, `part3-intro`, `p3-model`,
  `p3-complete`, `p3-freetalk`, `native-tip`, `transfer-scene`.

What this pilot is meant to prove:

- A lesson can complete one believable travel task instead of collecting loosely related phrases.
- The opening scene gives the patterns a reason to exist before they are analyzed.
- An English-speaking tutor can run the lesson without needing to interpret Japanese.
- The production ladder returns to the original scene, lets the learner replay it, and then transfers
  the language to a related situation.
- The correction/diff box works for a learner's real preference, not only a fixed correct answer.

Questions worth answering:

- Does the airline-desk conversation sound like an interaction that could actually happen?
- Are `We'd like ..., if possible` and `Could we have ...?` distinct and useful enough to teach
  together?
- Does the learner understand why each expression is polite, without an unnecessary grammar lecture?
- Can the tutor infer every activity's action and answer path from the English operating copy?
- Does the replay require productive recall, or can the learner coast on what is still visible?
- Does the train-counter transfer preserve the skill while genuinely changing the situation?

### 3. Freetalking — FT-1 Full

`Something that surprised you about another culture`

- Canonical source:
  [`tracks/3-freetalking/courses/talk-between-two-countries-full/lessons/01-this-surprised-me/lesson.html`](tracks/3-freetalking/courses/talk-between-two-countries-full/lessons/01-this-surprised-me/lesson.html)
- Production:
  [lecture](https://storage.googleapis.com/podo-assets/lemonboard-html/12715/lecture.html) ·
  [prestudy](https://storage.googleapis.com/podo-assets/lemonboard-html/12715/prestudy.html)
- Natural position: week 1 of 8.
- Page IDs: `lesson-goal`, `article`, `lesson-style`, `talk-intro`, `warm-1`, `warm-2`,
  `q1`, `q2`, `q3`, `q4`, `q5`, `q6`, `feedback`.

What this pilot is meant to prove:

- The pre-study article supplies ideas and language without consuming class time.
- The learner can choose discussion-first or correction-first without changing the lesson's topic.
- One visible talking job per page creates a coherent conversation rather than an interview script.
- Follow-ups deepen a plausible answer without assuming nationality, travel history, or a particular
  life experience.
- The conversation moves from a concrete event toward reflection without becoming abstract too soon.

Questions worth answering:

- Is the article genuinely useful preparation, or is any part longer or harder than its payoff?
- Can a learner with no travel experience still answer naturally?
- Do the questions form one developing conversation, or do they feel like separate prompts?
- Does any question invite stereotyping or treating one person's experience as a national truth?
- Are the private follow-ups useful to a tutor, concise, and non-repetitive?
- Does the final feedback page make the conversation feel complete?
- Which language or support would need simplifying in the matched Accessible version while preserving
  the same intellectual job?

## How to record feedback

Plain-language reactions are welcome; the reviewer does not need to propose implementation. When
possible, anchor a comment with the lesson and page ID:

```text
[Core 20 / p1-write]
Observation: The correction result is visually clear, but I lose the original sentence too quickly.
Learner impact: I cannot compare what I said with the corrected version.
Desired outcome: Keep the comparison visible long enough to understand the change.
```

For each observation, the implementation pass should record:

| Field | Meaning |
| --- | --- |
| Observation | What felt wrong, confusing, unnatural, slow, or especially effective |
| Evidence | Exact page, line, interaction, screenshot, or learner/tutor reaction |
| Learner impact | Why it matters in the live lesson |
| Classification | Local content, track shell, shared component, generator/checker, or product decision |
| Candidate rule | The narrowest reusable rule that would prevent the same problem elsewhere |
| Intended scope | This lesson, this track, all English, or shared English/Korean runtime |
| Exceptions | Cases where applying the rule mechanically would make another lesson worse |
| Owner decision | Keep, revise pilot first, propagate, investigate, or reject |

Useful shorthand:

- `LOCAL` — this sentence, fact, distractor, example, or scene only.
- `TRACK` — a Core, Contextual, or Freetalking blueprint/shell rule.
- `EN-ALL` — applies to every English deck.
- `SHARED` — component/runtime behavior that may also affect Korean decks.
- `PRODUCT` — changes the TOC, level, course identity, or what the course promises.

## From one comment to a curriculum-wide change

Do not treat similarity as permission to run a global replacement. Use this sequence:

1. Reproduce the observation in the production pilot and identify the exact page/component.
2. Decide whether the cause is content, the track blueprint, generator data/template, shared runtime,
   or a product decision.
3. Write the candidate rule in plain language and name its intended scope and exceptions.
4. Search the complete English draft corpus for the same defect class.
5. Change the highest authoritative source that is wrong. Do not hand-edit generated siblings or
   `courses/en/`.
6. Regenerate the affected lessons and inspect representative diffs before accepting the batch.
7. Re-review the changed pilot first. A rule that does not improve its source example is not ready
   to propagate.
8. Run static checks and render every affected lesson at 480 px and 360 px. Inspect the actual pages,
   interactions, wrapping, and final transfer—not only counts or HTML structure.
9. Promote from `sandbox/drafts/en/` only after owner approval. Stop at stage for visual and class
   verification before a production release.

Examples of correct classification:

- “This one airline line sounds unnatural” is probably `LOCAL` until the same construction is found
  elsewhere.
- “The blue box keeps narrating what is already visible” is likely `EN-ALL` tutor-copy guidance and
  may require a corpus audit.
- “The correction view hides the comparison too quickly” is likely `SHARED`; changing it may affect
  Core, Contextual, and Korean lessons using the same feedback component.
- “Every Freetalking article is too demanding for class preparation” is `TRACK` or `PRODUCT`, not a
  one-page copy edit.
- “This topic is not valuable enough to spend a lesson on” is a TOC/product decision. A template fix
  cannot solve it.

## What these pilots do not prove

- A good canonical shell does not prove every generated sentence, distractor, scene, or question is
  natural and valuable.
- Core 20 does not represent every later Core level or grammar dependency.
- CTX-1 does not prove all travel and business situations are realistic or sufficiently distinct.
- FT-1 Full does not replace review of its matched Accessible version; Freetalking changes must keep
  the pair aligned in topic and intellectual work.
- These three lessons do not cover Pronunciation, which remains planning-only.
- Passing structural checks does not prove teachability, cognitive load, conversation quality, or
  narrow-screen usability.

The desired output of this review is therefore not “approve three files.” It is a set of concrete,
scoped decisions: what is already good and must be preserved, what should change only here, and what
should become a rule enforced across a track or the whole English curriculum.

## 2026-08-21 — target fidelity and support retrospective

### Feedback accepted

- A controlled fill page should blank the exact pattern highlighted on the corresponding read page.
  Vocabulary must not become the blank merely to create four different answers.
- A later Japanese-to-English production page may ask for the whole sentence, but its support level
  must be explicit. A `supported` page gives every row the lexical hints needed to retrieve the
  sentence; a `checkpoint` intentionally gives none.
- Hint chips teach lexical content only. Articles, auxiliaries, inflections and other grammatical
  decisions stay in the sentence task rather than being supplied as hints.
- Page usefulness is judged by the learner decision it creates. Repeating an obvious answer, or
  offering alternatives that can never plausibly be correct, is not practice merely because the
  control is interactive.

### What changed in the sample lessons

- Core 13 now blanks `Do you` on every Part 1 controlled fill row and leaves the action and habit
  detail visible. Its supported whole-sentence production rows hint only `coffee`, `cook`, `work`
  and `exercise`.
- CTX 2 now blanks `I'm here for` and `I'm staying at` on the controlled fill pages. Destinations,
  purposes and their articles remain visible. Its supported production rows hint only lexical
  items such as `holiday`, `conference`, `Central Hotel` and `airport hotel`.
- Later replay and transfer blanks are generated from the same canonical targets instead of a
  separate vocabulary-blank override.

### Why generation and proofreading both missed it

The generator had a lesson-specific `fill_rows` escape hatch that could replace canonical pattern
rows with vocabulary blanks. The prose standards said to preserve target fidelity, but the checker
did not compare the exact highlighted target on `pN-read` with every `data-answer` on `pN-fill`.
A regression test then reinforced the defect by requiring four distinct fill answers. Finally, the
old review ledger recorded conclusions in prose without storing the actual targets, blank answers
or hint chips extracted from the reviewed HTML. A reviewer could therefore approve the intended
activity instead of proving what the page actually contained.

### Prevention now implemented

- Generation validates that each controlled pattern has four rows and an explicit target marker;
  canonical fill pages no longer accept the lesson-specific vocabulary override.
- `check_deck.py` compares each read-page target with every fill-page answer, including its Japanese
  target cue. A mismatch is a blocking error.
- Whole-sentence production opts into `data-scaffolding-contract="target-v2"` and declares either
  `data-support-stage="supported"` or `"checkpoint"`. Supported rows require hints; checkpoint
  rows reject them; function-word hints are rejected in either case.
- Regression tests assert exact target answers and allowed hint ownership. They no longer reward
  answer variety when it conflicts with the learning target.
- Page-review ledgers are hash-bound and now store exact extracted target highlights, blank answers,
  hint chips and support stage per page. A changed lesson or changed evidence invalidates the pass.
  The reviewer must separately state the learning target, likely failure, non-target support and
  article treatment before `humanPageAudit` can pass.
- The release gate still requires manual review at 360px and 480px. Automated rendering checks
  overflow and spacing, but cannot mark the human page audit complete.

### Corpus consequence

The first full scan found 448 target/support-contract violations in the existing 295-lesson English
draft corpus. That number is an audit backlog, not permission for a blind replacement. Revise in
bounded batches, regenerate from the owning source, complete page ledgers against the final bytes,
and return each batch for owner review before promotion.
