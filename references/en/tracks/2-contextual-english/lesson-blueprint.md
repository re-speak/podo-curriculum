# Contextual English — the page arc of one episode

**This is a map, not a table of contents or a markup source.** It fixes the order and job of the
pages in one episode. Take story facts from the TOC and generated brief; take component markup and
tutor voice from the canonical deck after the track pilot is approved.

- **Canonical English deck:** not yet authored. This track has its own pilot gate; do not treat the
  Core pilot or a Korean deck as an approved English Contextual template.
- **Structural precedent only:**
  [`../../../korean/tracks/3-contextual-korean/sample-lesson.html`](../../../korean/tracks/3-contextual-korean/sample-lesson.html).
- **Episode facts:** [`table-of-contents.md`](./table-of-contents.md) and the generated
  [`toc/`](./toc/) brief with the same `CTX-N` id.
- **Shared page contract:** [`../../../ux-philosophy.md`](../../../ux-philosophy.md) plus
  [`../../AGENTS.md`](../../AGENTS.md).

Read this map, then the complete canonical English deck once one exists. This track sells a scene,
not a grammar sequence; the dramatic timing, believable reactions and tutor voice cannot be
recovered from a page table.

---

## What makes this an episode

The learner is a cast member. Every learner line is `私`; the tutor reads every other named role.

- **Scene before objective.** The learner hears the situation and exchange before being told what
  it teaches. Without the scene, these are Core drills wearing travel or workplace nouns.
- **The reply is part of the line.** The TOC's partner reaction is never optional decoration. It is
  the consequence that makes the learner's line an action inside a story.
- **Core owns grammar.** An episode retrieves a known form or teaches a marked future form as a
  bounded chunk. It never opens a second grammar syllabus.
- **Reception has a real lane.** `Understand` items are what staff, signs and other characters say
  back. They are heard and recognised, never turned into learner production targets.
- **The last page sells the next episode.** Nothing follows the teaser—not a recap, tip or score.
- **No katakana readings.** The target is English; this track never loads `yomi.js` at any level.

---

## The skeleton

One episode is normally **29 pages**: five scene-setting pages, two pattern ladders, a return to the
scene, one adjacent native choice and one teaser. Omit an untaught or dishonest choice/rule page
rather than padding to reach a fixed count.

| # | `data-page-id` | Job |
| ---: | --- | --- |
| 1 | `episode-card` | Show · season · episode · cast. Establish who the learner is playing |
| 2 | `scene` | The TOC exchange, complete: learner lines and partner reactions |
| 3 | `lesson-goal` | Connect the scene to the one observable can-do |
| 4 | `expressions` | One or two production-ready chunks already doing work in the scene |
| 5 | `understand` | Receptive-only lines from the TOC; recognise, never produce |
| 6–14 | `part1-*` | Pattern A, beginning with its line from `scene` |
| 15–23 | `part2-*` | Pattern B, beginning with its line from `scene` |
| 24–27 | `part3-*` | Replay the same scene, then vary it with the learner's facts |
| 28 | `native-tip` | One new adjacent choice: register, softening, stress, contraction or collocation |
| 29 | `next-episode` | A 5–7-turn teaser ending on an unresolved dramatic beat |

The first page carries the episode's short `data-act`. Track lessons contain no sales cover.

### The five opening pages

`episode-card` uses the show and season bible already written in the TOC. Name only characters who
appear in this episode; an avatar never replaces the printed short speaker name.

`scene` stages the two learner lines and both partner reactions exactly as a small dramatic
exchange. It may add the minimum connective turns needed for a coherent scene, but it may not
replace the reviewed target lines. If it must split for height, split on a dramatic beat and reuse
the identical boundary in `p3-model-*`.

`lesson-goal` says: *that scene you just heard is what you will be able to handle.* Its success
condition is the TOC can-do, not a grammar label and not “learn two patterns.”

`expressions` holds fixed chunks the learner may produce. They support the exchange but are not a
third or fourth primary pattern. `understand` is the inverse: partner/staff language the learner
must recover but is not asked to say. A listen-and-pick or meaning match is appropriate; fill,
translate and free-write are not.

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
| `pN-write` | `.answer-box tall` | One open line that belongs in this episode's situation | no |

### Marked chunks do not receive a hidden grammar lesson

The generated brief names the season's productive Core floor and each pattern's Core owner. A TOC
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
- Every closed read/choose/reorder/fill/translate activity has **four questions**.
- Reorder uses four meaningful chunks as ceiling and default; three is allowed only when the
  sentence genuinely has three. One page uses one chunking criterion throughout.
- One answer box answers one question. A second prompt may only narrow the first.
- Blank only the target frame. Hint chips contain `JP:EN` vocabulary, never articles, auxiliaries
  or inflections.
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
recognising the exchange that was initially opaque.

`p3-freetalk` must be reciprocal. The tutor's final answer is typed live into the neutral partner
bubble; it is not a canned model and it does not expose a hidden answer to the learner.

---

## Native choice and next-episode teaser

`native-tip` adds exactly one usable choice adjacent to today's lines. If it repeats Expressions,
the meaning box or the rule, replace it. When both options are valid, present equal-weight situation
labels; never use a correction arrow to rank two contextual choices.

`next-episode` is the last page and a complete **5–7-turn mini-scene**:

- it uses both reviewed patterns through 2–3 learner completions;
- it advances the show's relationship, problem or decision;
- it takes its premise from the next TOC episode without teaching that episode's new grammar;
- it ends on an unresolved question, discovery, condition or reaction;
- no page follows it.

The first and final episode of a season need deliberate variants. A season opener may establish a
new cast relationship; a finale's teaser points to the next season or closes the work honestly
rather than pretending another episode exists.

---

## Continuity ownership

The orchestrator, not an individual deck writer, owns the show bible. Integrate drafts in episode
order and check:

- canonical names, roles and speaker labels;
- what each character knows at this point;
- relationship state and unresolved conflict;
- the TOC's `継続` fact;
- callbacks already spent and promises not yet paid off;
- teaser → next episode continuity.

A writer may report a conflict but may not repair another episode or rewrite the TOC from inside a
lesson assignment.

---

## This track does not

- start from a grammar label or replace the scene with disconnected example sentences;
- ask the learner to produce `Understand` or partner-reaction language;
- unpack a marked chunk into untaught grammar;
- invent a third target pattern because a scene contains another useful phrase;
- put two activities on one page;
- add katakana readings or load `yomi.js`;
- append anything after the next-episode teaser;
- create episode batches before this track's own pilot is explicitly approved.
