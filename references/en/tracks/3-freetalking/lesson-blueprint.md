# English Freetalking — the page arc of one session

**This is a map, not a question bank or markup source.** It fixes the shape of one 25-minute
session and the standards for writing its questions. Topic facts come from the TOC and generated
brief. Component markup and tutor voice come from the canonical English deck after the track pilot
is approved.

- **Canonical English deck:** not yet authored. Freetalking has its own pilot gate.
- **Structural precedent only:**
  [`../../../korean/tracks/4-freetalking/sample-lesson.html`](../../../korean/tracks/4-freetalking/sample-lesson.html).
- **Topic facts and format:** [`table-of-contents.md`](./table-of-contents.md) and the generated
  [`toc/`](./toc/) brief with the same `FT-N` id.
- **Shared contract:** [`../../../ux-philosophy.md`](../../../ux-philosophy.md) plus
  [`../../AGENTS.md`](../../AGENTS.md).

This track has no pattern ladder and no answer key. Its instructional unit is the learner's own
sentence becoming more natural, precise or intelligible without stopping the conversation.

> **What the learner said → the tutor's revision → the visible difference → say it again.**

No katakana reading appears anywhere. English is the target language, and installing katakana
rhythm would work directly against the course.

---

## The skeleton

One session is **13 pages**: one outcome, one format-specific model, one correction contract, eight
questions and one closing feedback page.

| # | `data-page-id` | Job |
| ---: | --- | --- |
| 1 | `lesson-goal` | One observable speaking outcome; carries the short `data-act` |
| 2 | `model-story` / `model-position` / `model-choice` / `two-sides` | Format-specific tutor contribution |
| 3 | `lesson-style` | Learner chooses fluency-first or correction-first |
| 4 | `talk-intro` | Make clear the ladder is a pool, not a checklist |
| 5–6 | `warm-1` · `warm-2` | Immediate experience and one concrete detail |
| 7–12 | `q1`–`q6` | The TOC ladder, easy → spicy → flipped close |
| 13 | `feedback` | One strength and one next focus, then re-say one useful correction |

Twenty-five minutes is the stop time, not a requirement to consume eight questions. A long,
productive answer is success. The tutor moves to `feedback` with 2–3 minutes left even when several
question pages remain.

### `lesson-goal`

Use the existing transition page and three quiet outcome rows. The rows are three dimensions of
one conversation—experience, reason, change or consequence—not a list of questions and not a page
schedule. The goal never says “answer eight questions.”

---

## The four formats choose page 2

Do not force every topic through an article. The TOC's format tag determines what the tutor brings
before the learner starts.

| Format | `data-page-id` | Tutor contribution | It must not become |
| --- | --- | --- | --- |
| `story` | `model-story` | One concrete experience, ~5 sentences / under 30 seconds | an opinion the learner copies |
| `opinion` | `model-position` | A short, explicitly partial position with one reason | the correct answer or a lecture |
| `choose` | `model-choice` | Tutor's pick plus one line explaining the real tradeoff | eight repeated A/B votes |
| `両国` | `two-sides` | Tutor's side of the same country-neutral question | an assumption that every tutor is American/British |

Every model uses existing sentence-list/dialogue components. Do not add a new interaction merely
to give each format a novel visual treatment.

### Format-specific rules

For `story`, specificity is the model: one event, one place, one small consequence. Do not widen to
a moral or general claim. The learner needs permission to tell a small story, not content to echo.

For `opinion`, label the position as one possible answer. Give enough structure to borrow, but the
question ladder must require the learner's evidence and may let the tutor test the opposite side.

For `choose`, page 2 establishes that both sides are defensible. After `q1` the session changes
verbs: use, lose, pay, tolerate, switch—not “which do you choose?” seven more times.

For `両国`, the learner teaches Japan and the tutor teaches where they are from. The wording remains
country-neutral because an English tutor may be from anywhere. Both sides answer the same prompt;
neither becomes the default culture against which the other is measured.

---

## Two language-load versions, one intellectual session

Write the **B2–C1 full version first**, then derive the **B1 accessible version**. Until product
level codes are decided, these are curriculum labels only; do not invent `classLevel` values.

Both versions retain:

- the same `FT-N`, topic, format and page ids;
- the same opening intent and easy → spicy ladder;
- the same adult interest and correction workflow;
- the same point where a `深く` topic becomes appropriate.

The accessible version lowers rare vocabulary, sentence length, nested clauses, stacked
hypotheticals and unnecessary abstraction. It does **not** remove the difficult idea or replace
later questions with small talk. A short natural question may remain identical in both versions.

The track's working entry floor is Core 53. Freetalking retrieves Core language; it never quietly
introduces a new grammar sequence.

---

## `lesson-style` — the correction contract

The learner chooses one of two modes, shared to the tutor view:

- **Fluency first:** do not interrupt; extend with questions; collect only high-value corrections.
- **Correction first:** capture important or repeated errors; correct at a natural pause; give the
  learner time to say the revision again.

The selected mode changes tutor behaviour, not the questions or difficulty. It is not persisted as
a permanent learner setting. Use the existing fluency/accuracy imagery rather than inventing a
third visual language.

---

## Writing the eight questions

The TOC `Opens:` line becomes the first spoken prompt. Its `Ladder:` supplies the semantic climb;
the deck author turns that compact arrow chain into eight single-question pages.

| Page | Job |
| --- | --- |
| `warm-1` | An answer available in about three seconds: recent fact, yes/no setup or concrete pick |
| `warm-2` | One visible detail from the learner's actual experience |
| `q1` | The topic's central story, choice or position |
| `q2`–`q3` | Expand toward people, work, money, time or a contrasting experience |
| `q4`–`q5` | The most demanding reasoning or changed condition |
| `q6` | Flip the topic and close it; do not open a new subject |

### One printed question

Each page prints exactly one question. If the sentence contains two question marks or joins two
requests with “and,” rewrite it. Put **2–3 follow-ups** in the Japanese tutor note, never on the
learner screen. Follow-ups rescue a short answer; they are not a second visible assignment.

The English question and Japanese support line are direct equivalents. When one changes, change
the other. Tutor notes are Japanese and private; they may include pacing or follow-up options but
must not provide a model opinion for the learner to copy.

### Five checks for a question

1. **One hypothetical layer.** Do not stack another “if” on a topic already built on a condition.
2. **A visible object.** The learner should not first have to decide what “change” or “improve” is
   supposed to act on.
3. **Anchored vocabulary.** At least one important noun or verb comes from the opening/model/topic.
4. **Not finished by yes/no or A/B.** Except for the deliberate warm-up/setup, ask for the scene,
   reason, threshold or consequence.
5. **No assumed life.** “Your work or studies” remains answerable by workers, students, retirees and
   caregivers; “your current job” does not.

At topic level, the TOC's three tests still apply: the opening answer arrives within three seconds,
three successive “whys” remain interesting, and the tutor has a real answer too.

### `choose` ladder

After the immediate pick:

1. name a recent real scene;
2. show how the chosen side would be used;
3. recall when the opposite side mattered;
4. change one condition—amount, duration, person or responsibility;
5. state the exact threshold where the choice flips.

If one option is morally correct, the topic is not a balance game.

### `深く`

`深く` means delayed until rapport exists, not removed and not announced to the learner as
“sensitive content.” The tutor may skip it without explanation. The course planner must not place a
`深く` topic in the opening run of a learner–tutor relationship.

---

## Correction blocks are the activity

Every question page has the same generated correction area (`.fb`) and existing add controls.
Do not hand-write correction rows in HTML; the shared activity script creates them.

- Capture the learner's sentence as heard.
- Edit only the corrected copy so additions/removals remain visible.
- Ask the learner to say the useful corrected sentence again.
- Put pronunciation, register or a future focus in a note row, not in the sentence correction.

The question page needs no choices, explanation card, model answer or grammar tip. Adding any of
those creates a second activity and turns conversation into a worksheet.

`feedback` is course-level reflection, not another correction list: **one strength, one next focus**.
Two lines are enough. Select one useful correction from the session and have the learner re-say it
before closing.

---

## Counting and language rules mirrored from the workflow

- One blue script box per page; English and Japanese carry the same sentence count.
- One printed question per question page, plus 2–3 private follow-ups.
- All learner-facing support is Japanese; English is the target language.
- No `.yomi`, no katakana pronunciation scaffold and no `yomi.js`.
- Vocabulary support is `JP:EN` only. Never put articles, auxiliaries or inflections in hint chips.
- Declare each supported content word as new, recycled, assumed-known or receptive-only in deck
  metadata, and make every hint-chip English value belong to exactly one category. Freetalking's
  load is recorded but is not governed by the Core/Contextual eight-word ceiling.
- Every `data-page-id`, feedback id and sync id is unique.
- Scrolling is allowed; split only when the activity's scope or pager access becomes unclear.

---

## This track does not

- teach a pattern, explain grammar, run a drill or show an answer key;
- give a `story` learner a model opinion to repeat;
- make an article the default model for every format;
- expose follow-up questions outside tutor notes;
- cut a productive answer short to reach `q6`;
- make the accessible version intellectually smaller;
- assume the tutor's country, accent or culture;
- use politics or breaking news as reusable topics;
- add katakana readings;
- create decks before this track's pilot is explicitly approved.
