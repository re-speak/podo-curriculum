# Contextual English — the page arc of one practical lesson

**This is a map, not a table of contents or a markup source.** It fixes the order and job of the
pages in one lesson. Take situation facts from the TOC and generated brief; take component markup and
tutor voice from the canonical deck after the track pilot is approved.

- **Superseded prototype — historical reference only:**
  [`courses/arriving-and-getting-settled/lessons/01-the-room-is-fine-but/lesson.html`](courses/arriving-and-getting-settled/lessons/01-the-room-is-fine-but/lesson.html).
  It implements the retired four-area curriculum and is not an approval candidate. Do not copy it,
  review it as current content, or use it to seed a batch.
- **Next pilot:** choose one revised low-intermediate Travel or Business lesson only after its TOC
  row passes review. No current Contextual deck is canonical.
- **Structural precedent only:**
  [`../../../korean/tracks/3-contextual-korean/sample-lesson.html`](../../../korean/tracks/3-contextual-korean/sample-lesson.html).
- **Lesson facts:** [`table-of-contents.md`](./table-of-contents.md) and the generated
  [`toc/`](./toc/) brief with the same `CTX-N` id.
- **Shared page contract:** [`../../../ux-philosophy.md`](../../../ux-philosophy.md) plus
  [`../../AGENTS.md`](../../AGENTS.md).

Read this map, then the complete canonical English deck once one exists. This track sells useful
English for a recognisable situation, not a grammar sequence. Believable reactions, pressure, and
tutor voice cannot be recovered from a page table.

---

## What makes this a situational lesson

The learner takes the active role. Every learner line is `私`; the tutor reads the other person.

- **Scene before objective.** The learner hears the situation and exchange before being told what
  it teaches. Without the scene, these are Core drills wearing travel or workplace nouns.
- **The reply is part of the line.** The TOC's partner reaction is never optional decoration. It is
  the consequence that makes the learner's line an action inside a situation.
- **Core owns grammar.** A lesson retrieves a known form or teaches a marked future form as a
  bounded chunk. It never opens a second grammar syllabus.
- **Reception has a real lane.** `Understand` items are what staff, signs and other characters say
  back. They are heard and recognised, never turned into learner production targets.
- **The lesson stands alone.** It assumes no cast, plot, callback, or earlier lesson. Course order
  reflects language load and useful grouping only.
- **The last page proves transfer.** It changes at least two scene variables while keeping the same
  communicative job; nothing follows it.
- **No katakana readings.** The target is English; this track never loads `yomi.js` at any level.

---

## The skeleton

One lesson is normally **29 pages**: five scene-setting pages, two pattern ladders, a return to the
scene, one adjacent native choice and one transfer scene. Omit an untaught or dishonest choice/rule page
rather than padding to reach a fixed count.

| # | `data-page-id` | Job |
| ---: | --- | --- |
| 1 | `situation-card` | Practical area · course · situation. Establish the learner's immediate job |
| 2 | `scene` | The TOC exchange, complete: learner lines and partner reactions |
| 3 | `lesson-goal` | Connect the scene to the one observable can-do |
| 4 | `expressions` | One or two production-ready chunks already doing work in the scene |
| 5 | `understand` | Receptive-only lines from the TOC; recognise, never produce |
| 6–14 | `part1-*` | Pattern A, beginning with its line from `scene` |
| 15–23 | `part2-*` | Pattern B, beginning with its line from `scene` |
| 24–27 | `part3-*` | Replay the same scene, then vary it with the learner's facts |
| 28 | `native-tip` | One new adjacent choice: register, softening, stress, contraction or collocation |
| 29 | `transfer-scene` | A second 5–7-turn situation using both patterns with changed facts |

The first page carries the lesson's short `data-act`. Track lessons contain no sales cover.

### The five opening pages

`situation-card` names the practical area, course, place, partner role, and immediate need. Include
only facts required to understand this lesson; an avatar never replaces the printed short speaker
name.

`scene` stages the two learner lines and both partner reactions exactly as a small conversational
exchange. It may add the minimum connective turns needed for a coherent scene, but it may not
replace the reviewed target lines. If it must split for height, split on a conversational beat and reuse
the identical boundary in `p3-model-*`.

Use **5–9 purposeful turns** for the complete opening scene and preserve the same turns, order and
beat boundary in `p3-model` and `p3-complete`. Five is the minimum needed for an opening, a useful
reaction or follow-up and a resolved ending; eight or nine is appropriate when the real task has a
short setup before the two target lines. Do not call a shortened excerpt a replay. If the complete
scene must be split for height, give both halves explicit scene page IDs and replay both halves later.

`lesson-goal` says: *that scene you just heard is what you will be able to handle.* Its success
condition is the TOC can-do, not a grammar label and not “learn two patterns.”

`expressions` holds fixed chunks the learner may produce. They support the exchange but are not a
third or fourth primary pattern. `understand` is the inverse: partner/staff language the learner
must recover but is not asked to say. A listen-and-pick or meaning match is appropriate; fill,
translate and free-write are not.

Each `understand` row tests the **meaning or practical intent of the complete staff line**. Write
both options as short, natural English paraphrases of the same semantic type. For a staff question,
both choices describe what the staff member is asking about; they are not two possible traveler
answers. For a statement, both choices describe the statement. The distractor should represent one
plausible local confusion, not an unrelated noun swap, an unnatural category label or a fragment.
The correct option must add evidence of comprehension rather than merely repeat the source line.

The English-speaking tutor must be able to run both pages without reading Japanese. Give
`expressions` an explicit spoken action such as reading the phrases together, not a passive
description of why they are useful. On `understand`, the tutor reads the English staff line; every
tappable meaning option exposes a concise English sense label alongside the learner's Japanese
support. Never present Japanese-only alternatives and expect the tutor to infer the answer.

---

## Pattern A and Pattern B

The ladder is Core's receive → recognise → produce arc, but the hero sentence is the line already
heard in `scene`.

| `data-page-id` | Component | Job | Model visible |
| --- | --- | --- | :---: |
| `partN-intro` | `.transition-page` | Pattern plus one Japanese bridge back to the scene. No grammar | — |
| `pN-teach` | `.pattern-meaning` + `.sent-hero` | Meaning/use, then the exact scene line | yes |
| `pN-read` | `.model-line` ×4 | Read the frame with scene-adjacent substitutions | yes |
| `pN-rule` (conditional) | existing rule component | One honest formation branch or distinction | — |
| `pN-choose` (conditional) | `.choose-row` ×4 | Only when two taught alternatives genuinely compete | yes |
| `pN-reorder` | `.task-block` ×4 | Rebuild four sentences from meaningful chunks | no |
| `pN-fill` | `.task-block` ×4 | Fill only the pattern slot | no |
| `pN-translate` | `.task-block` ×4 | Japanese scene cue → English | no |
| `pN-write` | `.answer-box tall` | One open line that belongs in this lesson's situation | no |

Each `pN-teach` meaning/use box contains **one short conversational English sentence** combining
what the frame does with when a speaker reaches for it, followed by a direct one-sentence Japanese
counterpart. Do not put an activity instruction, Japanese wording or a lesson-number reference in
the tutor's English line. Formation belongs on `pN-rule`; its spoken line adds only what the visible
diagram cannot show instead of reciting the diagram's branches and examples.

### Marked chunks do not receive a hidden grammar lesson

The generated brief names the course's productive Core floor and each pattern's Core owner. A TOC
line marked `chunk` is deliberately too far ahead to derive here.

For a chunk:

- teach the whole fixed anchor and its scene purpose;
- keep substitutions narrow and semantically obvious;
- omit a rule page that would unpack the later Core grammar;
- never test free recombination of the internal form;
- allow reorder/fill only when they retrieve the intact chunk rather than manufacture its rule.

The tutor may speak natural English beyond the floor. The restriction binds learner production,
not the tutor's voice or the partner's receptive line.

### Counting rules mirrored from the workflow

- Every ordinary blue script box has the same number of English and Japanese sentences.
  `.pattern-meaning` owns its own pairing and remains short.
- Tutor scripts use the shortest natural, conversational line that preserves the learner's next
  action or the page's meaning. They do not narrate visible setup, preview later activities, or
  repeat `Today we'll...` / `By the end of the lesson...` framing. Japanese matches the shorter
  English line's meaning, sentence count and tone.
- Tutor-only notes are English and appear only when the tutor must catch or do something the page
  cannot make obvious. Put them on the production page where that action happens, not on a teaching
  page that produces nothing yet; never repeat an answer already revealed by teaching mode.
- Mirror the taught target on every `pN-teach` and `pN-read` model: wrap each English target word or
  phrase in `.ending` and wrap its exact Japanese meaning in `.ending` too. If the English frame has
  two independently meaningful pieces, such as `We'd like` and `if possible`, both languages show
  two corresponding highlights.
- On `pN-fill`, put `.target.ending` around exactly the Japanese word or phrase represented by the
  blank. Use one Japanese cue per blank. Reorder and translate prompts remain neutral because the
  learner produces the whole sentence there.
- Every closed read/choose/reorder/fill/translate activity has **four questions**.
- Reorder uses four meaningful chunks as ceiling and default; three is allowed only when the
  sentence genuinely has three. One page uses one chunking criterion throughout.
- One answer box answers one question. A second prompt may only narrow the first.
- Blank only the target frame. Hint chips contain `JP:EN` vocabulary, never articles, auxiliaries
  or inflections.
- This boundary still applies on `p3-complete` and `transfer-scene`: the editable
  `phrase-input` contains only words from a frame already established on `pN-fill`. Keep names,
  objects, quantities, times, places and other scene facts visibly printed around it. When a frame
  is discontinuous (`We'd like ___, if possible`), use two wrapping phrase inputs and leave the
  lexical slot between them visible. Whole-sentence recall belongs in a full-width translate or
  open-production field, not an inline pattern blank.
- Fixed English printed around an inline blank is part of the same sentence and must render with
  the same font family, size and weight as the editable target. Do not use typography to make
  untargeted support language look less important.
- Declare each content word as new, recycled, assumed-known or receptive-only in deck metadata.
  Contextual normally adds no more than eight; every hint-chip English value must be declared.
- Omit `pN-rule` or `pN-choose` when the pattern has no honest formation branch or binary choice.

---

## Returning to the scene

| `data-page-id` | Job |
| --- | --- |
| `part3-intro` | Shift the learner from practice back into their role |
| `p3-model` | Replay the opening scene with meaning and ownership now established |
| `p3-complete` | Same turns and beat boundaries; only `私` lines are incomplete |
| `p3-freetalk` | Tutor asks → learner answers → learner asks back → tutor gives a real answer |

`p3-model` is a return, not a bonus scene. Replacing it with a new situation removes the payoff of
recognising the exchange that was initially opaque. It is also not a shortened highlight reel:
preserve the opening scene's turn count, order and connective lines exactly.

`scene`, `p3-model`, `p3-complete`, and `transfer-scene` are roleplays. Use profile images for every
turn and keep the short character names stable; the cast on `situation-card` uses the same images.
Only `p3-freetalk` represents the actual people in class, so only that page uses generic
`Tutor`/`Me` icons.

Mirror target highlights in `p3-model`. In `p3-complete`, each missing learner phrase has one exact
Japanese `.target` cue and one wrapping, auto-growing `textarea.free-input.phrase-input`. Do not
put a long late-production sentence in a single-line field.

`p3-freetalk` must be reciprocal. The tutor's final answer is typed live into the neutral partner
bubble; it is not a canned model and it does not expose a hidden answer to the learner.

---

## Native choice and final transfer

`native-tip` adds exactly one usable choice adjacent to today's lines. If it repeats Expressions,
the meaning box or the rule, replace it. When both options are valid, present equal-weight situation
labels; never use a correction arrow to rank two contextual choices.

`transfer-scene` is the last page and a complete **5–7-turn mini-scene**:

- it uses both reviewed patterns through 2–3 learner completions;
- it changes at least two meaningful variables: partner, place, object, reason, urgency, or outcome;
- it preserves today's communicative job without copying the opening dialogue;
- it ends with the practical outcome resolved or clearly handed off;
- no page follows it.

Its 2–3 learner completions use the same frame-only wrapping phrase fields and exact Japanese
`.target` cues as `p3-complete`; each answer must exactly reuse a controlled `pN-fill` frame. A
connective or closing line that is not one of today's targets stays visible;
do not turn it into an extra unscaffolded production test merely to add another blank.

The transfer scene is not a preview of another lesson and never introduces its grammar. Its job is
to show that the learner can carry today's frames into a second plausible encounter.

---

## Standalone ownership

The orchestrator owns coverage across the practical course. Integrate drafts in course order and
check:

- course titles still describe the jobs the lessons actually cover;
- adjacent lessons do not duplicate the same outcome or situation;
- partner roles and speaker labels are clear inside each lesson;
- no lesson requires a character, fact, or event from another lesson;
- final transfer scenes do not steal a neighbouring lesson's target.

A writer may report a coverage conflict but may not repair another lesson or rewrite the TOC from inside a
lesson assignment.

---

## This track does not

- start from a grammar label or replace the scene with disconnected example sentences;
- ask the learner to produce `Understand` or partner-reaction language;
- unpack a marked chunk into untaught grammar;
- invent a third target pattern because a scene contains another useful phrase;
- put two activities on one page;
- add katakana readings or load `yomi.js`;
- add a continuing plot, callback, unresolved teaser, or required cast history;
- append anything after the final transfer scene;
- create lesson batches before this track's own pilot is explicitly approved.
