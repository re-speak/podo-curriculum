# English curriculum review and proofreading workflow

This workflow separates three kinds of review that answer different questions:

1. **Catalog review:** are the curriculum's outcomes, model lines, frames and topics worth teaching?
2. **Lesson proofreading:** does an authored deck teach its approved outcome naturally and correctly?
3. **Rendered QA:** does the actual interaction work on both screens at lesson width?

Passing one never substitutes for the others. The active 303-item catalog is a curriculum review;
it does not approve a future deck, prove a CEFR band or validate mobile layout.

---

## Native catalog review — the active stage

The generated `catalog.html` is the review gateway; each generated page under `catalog/` is a
track-specific review surface. Reviewers may flag an item, leave an item
comment, add general comments and use **Copy review**. The copied text includes a stable id, title
and first-line snapshot so feedback can be checked against the current TOCs.

Save pasted feedback as plain text and validate it:

```sh
python3 tools/authoring/en/parse_catalog_review.py review.txt --output review.json
```

The parser rejects unknown ids, duplicate entries and stale titles/model lines. It never edits a
TOC. If it reports a stale snapshot, regenerate and republish the catalog, then ask the reviewer to
confirm their comment against that current item rather than guessing how an old comment maps.

### Triage every reviewed item

For each structured item, record one decision before editing:

| Decision | Meaning | Source action |
| --- | --- | --- |
| **keep** | Natural and strong enough as a production target | no TOC change |
| **rewrite** | Communicative move survives; wording/frame changes | edit model + frame together |
| **demote** | Useful language, but not a retrievable primary pattern | move to Expressions/Grammar |
| **remove** | Neither a production target nor useful support | delete and repair sequence references |
| **needs evidence** | Reviewer concern is plausible but disputed | corpus/source check before decision |

Flagging is not automatically rejection, and a positive comment is not a formal approval. General
comments become a separate cross-cutting work list; do not duplicate them onto every item.

### Apply an accepted review round

1. Preserve the original copied text and parsed JSON as review evidence.
2. Resolve conflicting suggestions and mark decisions.
3. Edit only authoritative TOCs and reference standards—not catalog HTML or generated briefs.
4. Re-run strict parser tests.
5. Regenerate briefs, grammar map and catalog.
6. Check every changed Core reference in Contextual/Freetalking remains in range and semantically
   points to the pattern owner.
7. Re-run the catalog and generated-artifact tests.
8. Publish a fresh catalog only after the round is internally consistent.

---

## Corpus and source validation

Native judgment answers “would someone say this?” It does not establish level, frequency or
transfer. Items marked **needs evidence**, all disputed Part 2 frames and every row-level CEFR claim
receive a separate pass under `reference/curriculum-source-hierarchy.md`:

- attested substitutions and collocations;
- Core Inventory communicative scope;
- English Grammar Profile form-and-meaning use;
- conservative productive band when sources disagree;
- Japanese-L1 risk treated as a hypothesis until learner evidence exists.

Record paraphrased findings and citations in the authoritative reference layer. Do not paste
copyrighted corpus passages into the curriculum.

---

## Complete lesson proofreading

An unqualified request to proofread a lesson means a complete review, not spelling alone. Read the
workflow, track blueprint, generated brief and canonical deck, then inspect every page in order.

**Proofreading immediately follows generation in the same batch workflow.** Generated HTML is
provisional until the complete review below, the static checker, exact-generation tests and
rendered QA all pass. Do not publish owner-review links, call a batch finished or begin the next
batch before that pass. Any defect is fixed in the highest owning source or generator, the affected
decks are regenerated, and the complete review is repeated on the new bytes.

1. **Outcome:** the page arc earns the TOC can-do and both primary patterns.
2. **Language:** English is natural for the scene and level; Japanese preserves agent, tense,
   object, register and emotional force.
3. **Teaching:** meaning/use precedes formation; rules draw only honest branches; future forms stay
   out of learner production unless explicitly chunked.
4. **Activities:** one activity per page, four closed questions, consistent meaningful reorder
   chunks, one prompt per answer box and believable distractors. Name the new decision each row
   requires; four repetitions of one answer or an option that can never be right do not count as
   four useful questions. Verify the operation from both roles: what the learner says or chooses,
   what the tutor reads or types, and what happens before the page advances.
5. **Application:** Core merges both patterns; Contextual replays the opening scene and proves
   standalone transfer in a second situation; Core/Contextual Free Talk is a reciprocal live
   exchange; Freetalking maintains one question plus the correction loop.
6. **Scaffolding:** every non-target word is supported; hint chips are vocabulary only; no katakana
   reading or `yomi.js` appears.
7. **Scripts:** each line is the shortest natural, conversational wording that preserves the
   learner's next action or the page's meaning; it does not narrate visible setup, inventory later
   activities or repeat framing such as “today” / “by the end of the lesson.” English and Japanese
   match in meaning, sentence count and tone, and tutor notes do not expose answers. Learner reading
   is the default; tutor reading appears only on an explicit listening/comprehension task. Teaching
   copy explains the idea, while the tutor note states the operation.
8. **Pilot regressions:** the goal has no preview rows; choose ends in a full-sentence read; reorder,
   fill and translate use the approved shared scripts; open-response blocks have no duplicate task
   text and use `Student's sentence`; roleplays assign roles directly; vague coaching and defensive
   prohibitions are removed; optional vocabulary pages earn their place.
9. **Rendered behaviour:** every page works at 480px and 360px, including interaction, sync,
   teaching mode, scrolling, pager clearance and console state. The automated render audit measures
   overflow and spacing; it does not inspect pedagogy or component consistency. A human still opens
   every page and compares repeated activity types with the approved reference design.

Record exact stable id, `data-page-id`, current text and proposed replacement. Separate confirmed
errors from editorial alternatives requiring an owner decision.

### Generated-batch gate

The representative Core, Contextual and paired Freetalking families are approved, so proofreading
now runs per generated course batch. HTML remains authoritative. Review the complete generated
batch page by page, record issues by stable review id and `data-page-id`, repair the generator or
content data, and regenerate. A spot-check link is an approval surface only after this gate passes;
it is not a substitute for the gate.

Mechanical checks must reject punctuation-only or bound-word reorder chips, unstyled repeated-row
containers, editable phrase fields outside the canonical answer component, impossible answers,
mixed chunk criteria and unmarked full-sentence choices where `.word-choice` was required. Human
proofreading still owns whether every surviving chip is a useful meaning unit, whether a reviewed
whole-sentence choice genuinely differs across the whole sentence, whether a rule teaches the
visible pattern, and whether the activity earns its place. It also owns whether a Free Talk question
is interesting enough to sustain conversation: topical relevance matters, but exact pattern reuse
is optional after the lesson's controlled production and roleplay have already established it.

### Page-by-page tutor-operability pass

For every page, answer these before approving it:

1. What exact sentence does the tutor say aloud?
2. What does the learner do next—read, listen, choose, arrange, speak, or answer?
3. If text is entered, who speaks and who types, and is that division explicit?
4. Does the tutor note add an operation the visible page cannot supply, or merely restate it?
5. If this is a roleplay, are both roles named in ordinary language before it begins?
6. If this is open production, does the visible script print both the exact target frame and the
   concrete question or situation the learner should answer?
7. If this is Free Talk, is there a reciprocal Tutor/Me exchange in which the learner can ask back
   and receive a real answer? Would the topic still be worth discussing without forcing today's
   frame? If not, rewrite the question rather than adding more coaching.
8. What exact language is taught on the preceding model page, and is that exact language—rather
   than vocabulary—the controlled blank here? If failure would diagnose an unrelated word gap,
   redesign the page before considering row variety.
9. What new decision or retrieval does this page add? If every row has the same obvious answer, or
   one option can never be correct, remove or redesign the activity without moving the blank away
   from the taught target.
10. On whole-sentence production, is the page explicitly `supported` or a `checkpoint`? For
   `supported`, does every row supply the lexical help it needs while leaving articles, auxiliaries
   and inflections unhindered?
11. Does this page use the same approved component as other pages with the same teaching job, rather
   than a visually weaker fallback with similar text?

For every generated Core deck, proofreading also records one answer to each of these questions
before `podo:proofread-status=complete`: What new decision does each page ask the learner to make?
What stable sentence stays printed around each choice? What operation does the rule diagram make
visible? What register, softening, contraction, prosody, collocation or intensity distinction does
the native tip add? “It matches the generator,” “it has four rows,” and “the checker passes” are not
answers. A batch with one unanswered page remains incomplete and produces no owner-review links.

The answers are not an informal promise. Create a hash-bound ledger for each reviewed lesson:

```sh
python3 tools/authoring/en/page_review.py init path/to/lesson.html \
  --output sandbox/drafts/en/page-reviews/REVIEW-ID.page-review.json
# Complete every generated page entry only after inspecting that page at 360px and 480px.
python3 tools/authoring/en/page_review.py check path/to/lesson.html \
  sandbox/drafts/en/page-reviews/REVIEW-ID.page-review.json
python3 tools/authoring/en/page_review.py render \
  sandbox/drafts/en/page-reviews/REVIEW-ID.page-review.json \
  --output sandbox/drafts/en/page-reviews/REVIEW-ID.page-review.md
```

The checker requires the exact lesson SHA-256, exact `data-page-id` order, machine-extracted target
highlights, blank answers, hint chips and support stage, plus a completed answer for learner action,
tutor action, visible target/prompt, learning target, failure diagnosis, non-target support, article
treatment, pedagogical value, choice quality, component consistency, both visual widths and verdict.
The extracted evidence must match the lesson; prose cannot override it. Any regenerated byte makes
the ledger stale. Keep the four states separate in the ledger: **generated**, **mechanically validated**,
**human page-audited**, and **owner-approved**. The first three may pass while owner approval stays
pending; only `check --require-owner` may support an owner-approved claim.
