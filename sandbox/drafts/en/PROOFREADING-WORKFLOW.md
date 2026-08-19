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
python3 english/tools/parse_catalog_review.py review.txt --output review.json
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

1. **Outcome:** the page arc earns the TOC can-do and both primary patterns.
2. **Language:** English is natural for the scene and level; Japanese preserves agent, tense,
   object, register and emotional force.
3. **Teaching:** meaning/use precedes formation; rules draw only honest branches; future forms stay
   out of learner production unless explicitly chunked.
4. **Activities:** one activity per page, four closed questions, consistent meaningful reorder
   chunks, one prompt per answer box and believable distractors.
5. **Application:** Core merges both patterns; Contextual replays the opening scene and proves
   standalone transfer in a second situation; Freetalking maintains one question plus the correction loop.
6. **Scaffolding:** every non-target word is supported; hint chips are vocabulary only; no katakana
   reading or `yomi.js` appears.
7. **Scripts:** each line is the shortest natural, conversational wording that preserves the
   learner's next action or the page's meaning; it does not narrate visible setup, inventory later
   activities or repeat framing such as “today” / “by the end of the lesson.” English and Japanese
   match in meaning, sentence count and tone, and tutor notes do not expose answers.
8. **Rendered behaviour:** every page works at 480px and 360px, including interaction, sync,
   teaching mode, scrolling, pager clearance and console state.

Record exact stable id, `data-page-id`, current text and proposed replacement. Separate confirmed
errors from editorial alternatives requiring an owner decision.

### Authored-deck packets

English does not yet need a bulk deck packet builder: only one approved deck exists and further
production is on hold. When the three-lesson Core gate lands, build the one-way HTML projection
before parallel proofreading, following Korean's guarded model:

- HTML remains authoritative;
- packets carry source hashes and exact field locators;
- issue validation refuses stale hashes/current text;
- applying suggestions is explicit, never an automatic merge;
- regenerated packets must prove current after fixes.

Building that projection before there is a representative three-deck set would encode the pilot's
single structure as universal—the exact mistake the three-lesson gate exists to prevent.
