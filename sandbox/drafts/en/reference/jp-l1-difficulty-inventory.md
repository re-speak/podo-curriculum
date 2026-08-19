# What is hard about English for a Japanese speaker

**Status:** evidence base for the TOC audit and the spine rewrite.
**Written:** 2026-08-13, after D1 fixed the learner as a Japanese speaker.

## Why this document exists

`proposed-authoritative-build-method.md` opens with **Step 1 · Define the learner and endpoint**,
and notes that interpreting "B1" as one universal course without that context is a mistake. That
step was never done: the 72-lesson spine and its grammar map were written **before** the learner
was defined, so every difficulty judgment in them is L1-neutral. This file supplies the missing
input.

## What this is, and what it is not

This is **contrastive analysis** — a comparison of the two systems that predicts where a Japanese
speaker will struggle. It is a *hypothesis generator*, and it must be labelled as one:

- **Contrastive analysis over-predicts.** Not every structural difference produces an error, and
  some of the most persistent learner errors are not predicted by any contrast at all. A predicted
  difficulty is a candidate for teaching time, not proof of one.
- **It says nothing about level.** Where an item belongs in the sequence is decided by the sources
  in [`curriculum-source-hierarchy.md`](./curriculum-source-hierarchy.md) — Core Inventory band
  first, English Grammar Profile form-and-meaning second. This file says *how much attention* an
  item deserves for this learner, not *when* it is teachable.
- **It must be checked against performance.** The validation steps in
  [`curriculum-rationale.md`](./curriculum-rationale.md) apply unchanged: recorded learner
  performance, delayed retrieval, transfer.

Used correctly, this file answers one question the CEFR and the Core Inventory cannot, because both
are language-of-origin-neutral: **given finite lesson slots, which of them does *this* learner need
most?**

---

## The ranking principle

An item earns teaching weight by three things multiplied together:

1. **Frequency** — how often it is unavoidable in ordinary speech.
2. **L1 gap** — how much scaffolding Japanese provides. None is worst; a partial-but-misleading
   mapping is often worse than none.
3. **Persistence** — whether it resolves through exposure or fossilises without instruction.

Articles score maximum on all three. Comparatives score low on the second, because Japanese `より`
maps cleanly, which is why they do not need many slots however frequent they are.

---

## Tier 1 · Japanese has no equivalent system

The learner has nothing to transfer. These are invisible to them — not hard-but-noticeable,
**unnoticeable**, which is what makes them fossilise.

### 1. Articles — `a` / `an` / `the` / zero

**The single highest-value item in the entire curriculum for this learner**, and the current spine
does not teach it.

Japanese has no article system. Definiteness is carried by context, word order and particles such
as `は`/`が`, none of which surfaces as a word. So the learner is not choosing the wrong article —
they have no slot in which the choice occurs.

- Predicted: `I bought book.` · `I went to the Tokyo.` · `She is teacher.` · `Could you pass salt?`
- Frequency: articles are among the most frequent words in English; nearly every noun phrase forces
  a decision.
- Persistence: notoriously the last thing to stabilise, and it does not resolve through exposure
  alone.

**Teaching consequence:** this cannot be one lesson. It is a thread — introduced as a bounded
lexical habit (`I'm **a** designer`, `**the** station`) very early, then revisited as first-mention
vs later-mention, then as generic reference. Treating it as a single grammar row is what produced
the current gap.

### 2. Number marking on nouns

Japanese does not obligatorily mark plural. `本` is one book or several.

- Predicted: `I have two brother.` · `a lot of thing` · plural agreement failures downstream
  (`These box is heavy`).
- Interacts with articles: `a book` / `books` / `the books` is one decision space, not two.

### 3. Count vs non-count

A lexical property Japanese does not encode. Cannot be derived from meaning — `advice`, `furniture`
and `information` are non-count in English for no reason the learner can predict.

- Predicted: `informations`, `an advice`, `many furnitures`.
- Teaching consequence: this is **vocabulary**, not grammar. It belongs in how words are introduced
  and stored, not in one lesson about `much`/`many`.

### 4. The obligatory subject

Japanese drops subjects freely when recoverable. English requires one, including dummy subjects
that mean nothing.

- Predicted: `Is very hot today.` · `Yesterday went to Osaka.` · `Was fun.`
- The dummy `it` and existential `there` are pure grammar with no semantic hook, so they need
  explicit treatment rather than incidental exposure.

### 5. Do-support

No equivalent operation exists in Japanese. Questions and negatives are made with sentence-final
morphology, so inserting a meaningless auxiliary and stripping tense off the main verb is a
genuinely alien operation.

- Predicted: `You like coffee?` · `He no like it.` · `Did you went?` (tense marked twice) ·
  `What you did yesterday?`
- The current spine touches `do`/`does`/`did` across three rows but never as *the operation*.

---

## Tier 2 · The system exists but maps differently

Something transfers, which makes these deceptive: the learner is confident and wrong.

### 6. Constituent order — SOV → SVO

Japanese is verb-final and relatively free before the verb, because particles carry the roles.
English fixes order and uses position *as* the role marker.

- Predicted: object/adverb misplacement, and it compounds precisely where the learner is already
  loaded — questions, embedded clauses, relative clauses.
- **The current spine has one row touching word order, at lesson 57.** This is a day-one difficulty
  appearing two-thirds of the way through.

### 7. Relative clause position

Japanese pre-modifies: the modifying clause comes *before* the noun. English post-modifies.

- Predicted: `I bought yesterday the book.` · omission of the relative pronoun where required.
- The *concept* is native (連体修飾), so this is cheaper to teach than it looks — the flip is the
  whole lesson, not the idea.

### 8. Prepositions

Japanese particles look like a mapping and are not. `に` alone covers English `to`, `at`, `in`, `on`
and more depending on the verb; English prepositions are governed by the verb and by lexical
convention.

- Predicted: `I arrived to the station.` · `discuss about it` · `on next week`.
- Teaching consequence: like count/non-count, this is **lexical**. Prepositions should be learned
  attached to their verbs and nouns as chunks, which is exactly what the two-pattern architecture
  is good at — and an argument for the architecture, not against it.

### 9. Progressive vs perfect — the `~ている` problem

Japanese `~ている` covers both an action in progress *and* a resulting state. English splits that
across the progressive and the perfect.

- Predicted: `I am knowing him for five years.` · `I have been to Osaka last year.` ·
  stative verbs put into the progressive (`I am wanting`).
- **This is a genuine Tier-2 difficulty and the spine's heavy investment here is defensible.** What
  is missing is the *reason*: no row says the difficulty is `~ている` splitting in two, so a lesson
  writer cannot target the actual confusion.

### 10. Modal + bare verb

Japanese modality is sentence-final and inflecting. English modals sit before the verb and take no
agreement, and the verb after them takes none either.

- Predicted: `He can plays tennis.` · `She must to go.` · `I will can do it.`

### 11. `-ed` / `-ing` adjectives

Japanese i-adjectives do not distinguish experiencer from stimulus this way.

- Predicted: `I am boring.` — high embarrassment cost, which makes it memorable and worth one
  focused slot. The spine has this at L42, correctly.

---

## Tier 3 · Pragmatics — where the learner is fluent and still misread

### 12. Politeness is not grammatical in English

This is the most under-appreciated item on the list. A Japanese speaker arrives with a **highly
developed** politeness system that is *grammatically encoded* — keigo inflects the verb. English
encodes politeness lexically and syntactically instead: modal choice, indirectness, hedging,
question form.

The learner therefore looks for a politeness inflection, does not find one, and produces English
that is grammatically perfect and socially blunt — `Give me the report.` — while believing they
have been neutral.

- **The concept transfers completely; only the mechanics are new.** That makes this *cheaper* to
  teach than the spine's 8 rows imply, but it must be taught **explicitly and early**, not as a
  B1 refinement. A learner who is polite in Japanese and blunt in English pays a social cost from
  their first conversation.
- The pilot lesson (Core 22) landed on exactly this with `could` vs `can`, and it was the right
  instinct.

### 13. Answering negative questions

Japanese agrees with the *proposition*; English agrees with the *fact*.

> `Don't you like it?` — Japanese logic answers `Yes` to mean *"correct, I don't"*.

Low frequency, but each occurrence is an outright miscommunication rather than an accent. Cheap to
teach, worth one explicit treatment.

### 14. Backchannelling

Japanese conversation expects frequent あいづち. Transferred into English at Japanese frequency it
reads as interrupting or as impatience.

Belongs in Freetalking as a conversation-management note, not in Core.

---

## Tier 4 · Phonology

Out of scope for Core, and the contents are already knowable — a closed, predictable list, exactly
as `korean/tracks/5-pronunciation` is for the mirror-image learner. Gated on **D6**.

/r/–/l/ · /f/–/h/ · /v/–/b/ · /θ/–/s/ · /z/–/dz/ · **vowel epenthesis** (the katakana-English habit
— the highest-cost item) · consonant clusters · **mora-timing vs stress-timing** · /æ/–/ʌ/–/ɑ/ ·
sentence stress and reduction.

Note the ordering differs from the segmental list most courses teach: epenthesis and rhythm damage
intelligibility far more than /r/–/l/ does.

---

## What the current spine gets wrong

Measured across all 72 rows of [`grammar-coverage-map.md`](./grammar-coverage-map.md):

| Item | L1 gap | Rows in spine | First taught |
| --- | --- | ---: | --- |
| **Articles** | **none — no system** | **1** (incidental, in "I'm a designer") | L3 |
| **Noun number** | **none** | **1** (incidental) | L14 |
| **Prepositions** | misleading partial map | **1** (incidental) | L6 |
| **Basic word order** | **reversed** | **1** | **L57** |
| Obligatory subject | none | 1 (just "subject pronoun I") | L1 |
| Do-support | none | 3 (never as the operation) | L3 |
| Count / non-count | none | 2 | L14 |
| Relative clause position | reversed | 2 | L53 |
| Progressive vs perfect | conflated by ている | 11 | L12 |
| Politeness mechanics | concept transfers | 8 | L20 |

**The pattern is not that the heavy areas are wrong.** Aspect genuinely is hard, and politeness
genuinely matters. The pattern is that **weighting was set without a learner**: the areas where
Japanese supplies *zero* scaffolding get one incidental mention each, while areas where Japanese
supplies a concept to transfer get eight and eleven rows.

A second finding sits underneath it. The map records **forms**, not **difficulties**. Row 22 lists
"modal `could`; `can` response; object pronoun; request sequence" and does not mention the one thing
the lesson actually had to teach — that `help me` takes `with` before a thing and nothing before an
action, a split 「手伝う」 hides. That was found by *writing the lesson*, not by reading the map.
Every row is likely to have such an item, and none of them are recorded.

---

## What this implies for the rewrite

1. **Articles become a thread, not a row.** Introduced as bounded chunks in the first unit, revisited
   at first-vs-later mention, then at generic reference. Nothing else on this list has that shape.
2. **Word order moves to the front.** It is the day-one difficulty and it currently sits at L57.
3. **Number, count/non-count and prepositions move into how vocabulary is introduced** — carried on
   the noun and the verb from first contact, not deferred to a quantity lesson.
4. **Politeness moves earlier and gets shorter.** The concept transfers; the learner needs the
   mechanics before their first real conversation, not at B1.
5. **The aspect block keeps its weight but gains its reason** — every row states the ている split it
   is resolving, so a lesson writer can target the confusion instead of the form.
6. **Every row gains an L1-difficulty field.** Currently the map answers "what form is here"; it must
   also answer "what will this learner get wrong, and why."
