# English Freetalking — the page arc of one session

**This is a map, not a question bank or markup source.** It fixes the shape of one 25-minute
session and the standards for writing its questions. Topic facts come from the TOC and generated
brief. Component markup and tutor voice come from the matching approved canonical English deck.

- **Approved canonical decks (2026-08-18):** [`courses/talk-between-two-countries-full/lessons/01-this-surprised-me/lesson.html`](./courses/talk-between-two-countries-full/lessons/01-this-surprised-me/lesson.html)
  and [`courses/talk-between-two-countries-accessible/lessons/01-this-surprised-me/lesson.html`](./courses/talk-between-two-countries-accessible/lessons/01-this-surprised-me/lesson.html).
  Use the full shell for full lessons and the accessible shell for accessible lessons. Preserve
  their semantic pairing while lowering language load only in the accessible version.
- **Live runtime state:** shared runtime `v1.12.1` is published and live. It localizes generated
  teaching-mode labels from `<meta name="podo:target-language" content="en">`, so the approved
  English behavior has no outstanding publish or repoint dependency. Future runtime changes still
  require a coordinated publish and repoint; do not hide runtime gaps with deck-local overrides.
- **Structural counterpart:**
  [`../../../korean/tracks/4-freetalking/sample-lesson.html`](../../../korean/tracks/4-freetalking/sample-lesson.html).
  Its 10–15-sentence pre-study article, correction contract and question-page rhythm are the
  cross-language baseline. **This blueprint and the approved English decks remain authoritative**
  for English tutor voice, language load and glossary judgment.
- **Topic-specific question counterparts:**
  [`../../../korean/tracks/4-freetalking/courses/talk-between-two-countries-intermediate/lessons/01-what-surprised-me/lesson.html`](../../../korean/tracks/4-freetalking/courses/talk-between-two-countries-intermediate/lessons/01-what-surprised-me/lesson.html)
  and
  [`../../../korean/tracks/4-freetalking/courses/talk-between-two-countries-advanced/lessons/01-what-surprised-me/lesson.html`](../../../korean/tracks/4-freetalking/courses/talk-between-two-countries-advanced/lessons/01-what-surprised-me/lesson.html).
  Use these for the topic ladder, not as authority for replacing the article with a tutor story.
- **Topic facts and format:** [`table-of-contents.md`](./table-of-contents.md) and the generated
  [`toc/`](./toc/) brief with the same `FT-N` id.
- **Shared contract:** [`../../../ux-philosophy.md`](../../../ux-philosophy.md) plus
  [`../../AGENTS.md`](../../AGENTS.md).

This track has no pattern ladder and no answer key. Its instructional unit is the learner's own
sentence becoming more natural, precise or intelligible without stopping the conversation.

> **The blueprint, both approved canonical decks and `english/tools/check_deck.py` are one spec in
> four forms.** When a countable rule changes, update all four in the same change. A prose-only rule
> is too easy for a generated course to miss, while a checker-only rule leaves writers copying a
> stale canonical deck.

> **What the learner said → the tutor's revision → the visible difference → say it again.**

No katakana reading appears anywhere. English is the target language, and installing katakana
rhythm would work directly against the course.

---

## The skeleton

One session is **13 pages**: one outcome, one pre-study article, one correction contract, eight
questions and one closing feedback page.

| # | `data-page-id` | Job |
| ---: | --- | --- |
| 1 | `lesson-goal` | One observable speaking outcome; carries the short `data-act` |
| 2 | `article` | 10–15 sentence rows, read only before class; open in class only to answer a learner question |
| 3 | `lesson-style` | Learner chooses discussion-first or correction-first |
| 4 | `talk-intro` | Make clear the ladder is a pool, not a checklist |
| 5–6 | `warm-1` · `warm-2` | Immediate experience and one concrete detail |
| 7–12 | `q1`–`q6` | The TOC ladder, easy → spicy → flipped close |
| 13 | `feedback` | One strength and one next focus, then re-say one useful correction |

Twenty-five minutes is the stop time, not a requirement to consume eight questions. A long,
productive answer is success. The tutor moves to `feedback` with 2–3 minutes left even when several
question pages remain.

### `lesson-goal`

Use the transition page for one useful orientation only. The blue script introduces the topic and
asks the learner to read the title aloud once; the tutor note says to move on after that. Do not add
three outcome rows, sample answers, a question preview or a page schedule. The visible English
title and document title preserve the exact title from the lesson's generated `FT-N` brief. Only
the short pager `data-act` may summarize it. If the title needs improvement, change the TOC and
regenerate the brief rather than inventing a separate deck title.

---

## The pre-study article on page 2

Page 2 is an article the learner reads **only during pre-study**. It is not an in-class reading,
silent-reading or catch-up activity. The tutor does not read it aloud, ask the learner to skim it,
or present it as their own experience. In class the page has one job: ask whether the learner has
questions about the article. Answer those questions and move on; if there are none, skip the page.
If the learner did not complete the pre-study, skip the article rather than using class time to
read it.

- Use **10–15 sentence rows**, not a four- or five-line mini-story. The article must be long enough
  to anchor the full question ladder, while each row still carries one readable claim. Keep the
  full article on one page so a learner can tap the exact sentence that caused trouble.
- Each row opens its Japanese translation and, only when needed, an in-context vocabulary gloss.
  One row stays open at a time.
- The blue script asks only whether the learner has questions about the article. It does not tell
  them to tap, read, skim or otherwise operate the page. The tutor may open the relevant sentence
  while answering a question. A short private note records the skip rule; it is not spoken.
- Full and accessible versions keep the same claims in the same order. Accessible lowers rare
  vocabulary and clause load; it does not merely shorten the full version while preserving its
  hardest words, and it does not remove the article's reasoning.

| Format | What the article contributes | It must not become |
| --- | --- | --- |
| `story` | A neutral observation that gives the learner somewhere to begin | a personal story the tutor pretends is theirs |
| `opinion` | One tension or piece of context that leaves room for disagreement | the correct position or a lecture |
| `choose` | A balanced setup that makes both sides defensible | eight repeated A/B votes |
| `両国` | A bounded observation about expectations and difference | a national stereotype or claim about the tutor's country |

### What earns a highlighted gloss

Highlighting is a comprehension aid, not a quota and not a list of topic vocabulary.

- Highlight an item only when it is plausibly difficult enough at that version's entry level to
  block the sentence. Use this editorial test: **if the learner knew the rest of the sentence,
  would not knowing this item prevent them from recovering its main claim?** If no, do not gloss
  it. A line may have **zero, one or two** glosses; three needs a real reason. There is no minimum
  per row or per article, so a readable article may legitimately have only a few word-bank items.
- Default to one word. Highlight a multiword span only when it is a genuine lexical unit—an idiom,
  phrasal verb or fixed expression whose meaning cannot be recovered reliably word by word. Use the
  shortest span that carries that meaning.
- Do not highlight proper names, familiar topic nouns, transparent phrases or ordinary words merely
  because they are important to the topic. `barbecue restaurant`, `be the same` and `table`, for
  example, do not earn glosses for a B1 article.
- Vocabulary metadata does not create a gloss quota. `new`, `assumed` and `receptive` describe
  curriculum ownership and load; the word bank is a separate, sentence-level comprehension
  decision. Conversely, do not withhold a gloss merely because a word was declared elsewhere if
  its less familiar sense is what carries the sentence's claim here.
- Every `.s-key` has exactly one matching `.s-w`, and vice versa. The highlighted text uses the
  surface form in the sentence; the gloss names the word or expression and gives its meaning in
  that sentence, not a broad dictionary inventory.

For `choose`, page 2 establishes that both sides are defensible. After `q1` the session changes
verbs: use, lose, pay, tolerate, switch—not “which do you choose?” seven more times.

---

## Two language-load versions, one intellectual session

Write the **C1 full version first** as the best version of the conversation: the most natural,
interesting and immediately answerable questions the topic can support. A question that is already
plain and easy to answer does not become better because it sounds more advanced. Then derive the
**B1 accessible version** from that deck. Until product level codes are decided, these are
curriculum labels only; do not invent `classLevel` values.

Both versions retain:

- the same `FT-N`, topic, format and page ids;
- the same opening intent and easy → spicy ladder;
- the same adult interest and correction workflow;
- the same point where a `深く` topic becomes appropriate.

The accessible version lowers rare vocabulary, sentence length, nested clauses, stacked
hypotheticals and unnecessary abstraction. It does **not** remove the difficult idea, replace
later questions with small talk or force a rewrite of every line.

| Full question | Accessible decision |
| --- | --- |
| `What have you bought that was really worth the money?` | Keep it. Natural, interesting and easy to answer at B1. |
| `What kind of purchase most often becomes a regret?` | Rewrite: `Is there anything you regret buying? Why?` |
| `What can make a useful item stop feeling worth it?` | Replace at both levels. The task is hard even in the learner's first language. |

**Identical is not the defect; unnecessary adaptation is.** A pair should differ only when the
Full line contains a real B1 barrier. Tiny synonym swaps (`genuinely`, `especially`, `revive`) are
not level adaptation, and making C1 abstract or clever is never a level strategy.

The track's working entry floor is Core 53. Freetalking retrieves Core language; it never quietly
introduces a new grammar sequence.

---

## `lesson-style` — the correction contract

The learner chooses one of two modes, shared to the tutor view:

- Spoken script: **Please choose your preferred discussion style.**
- Japanese support: **希望する会話の進め方を選んでください。**

- **Discussion first:** do not interrupt; extend with questions; collect only high-value corrections.
- **Correction first:** capture important or repeated errors; correct at a natural pause; give the
  learner time to say the revision again.

The selected mode changes tutor behaviour, not the questions or difficulty. It is not persisted as
a permanent learner setting. Use the existing fluency/accuracy imagery rather than inventing a
third visual language. Keep the two labels **Discussion first** and **Correction first** in that
order. Do not paraphrase the spoken script as a vague question about how the tutor should “support
your English”; the learner's action is simply to choose a discussion style.

---

## Writing the eight prompts

The TOC `Opens:` line becomes the first spoken prompt. Its `Ladder:` supplies the semantic climb;
the deck author turns that compact arrow chain into eight single-prompt pages.

| Page | Job |
| --- | --- |
| `warm-1` | **Put one concrete thing on the table.** A recent fact, a yes/no setup or a named pick, answerable in about three seconds |
| `warm-2` | One visible detail **of that same thing** |
| `q1` | The topic's central story, choice or position — now that the referent exists |
| `q2`–`q3` | Stay on that referent: when, who with, what changed, what it replaced |
| `q4`–`q5` | Widen — compare it, price it, put it in the other country, change a condition |
| `q6` | **Flip it.** `Now the opposite — …` Close the topic; do not open a new subject |

### The eight prompts are one thread, not eight survey items

`warm-1` names something — a dish, a show, a purchase, a person — and the next six prompts talk
about *that*. `it`, `that dish`, `them` are correct here and are what makes a follow-up possible.

This is the difference between a session and a questionnaire, and it is the second defect the
content-lead review found: eight independent prompts, each asking the learner to search their whole
life afresh, produce a topic where the tutor has nothing to dig into. Korean's decks have always
threaded one referent (`그걸 언제 제일 자주 써요?` — *when do you use **it** most?*) and close with
`그럼 반대로…`; English decks now do the same.

A prompt with no person (`you`, `I`, `we`) **and** no referent (`that`, `it`, `them`) is dead on
arrival — there is nothing in it to retrieve. `What can make a useful item stop feeling worth it?`
is the shape to recognise; `When do you use it most?` is the same page done right.

### The one-hearing, three-second test

The TOC uses the three-second test to admit a topic through its opening. Authored decks apply a
stricter version to **every printed prompt and every tutor follow-up**. The learner hears the tutor;
they do not get to study the sentence as an essay question.

A prompt passes only when a proofreader can hear or read it once and immediately say a plausible
first answer. Allow about three seconds to begin the answer. The answer can be short; the question
should make extending it easy. If the proofreader first has to paraphrase the question, choose an
interpretation, recover a hidden situation or decide what an abstract noun refers to, rewrite it.

This is a processing-load test, not a vocabulary blacklist. Common words can still form a slow
question:

- `What risk creates the boundary?` is grammatical but abstract. Use `Why wouldn't you trust AI
  with that?`.
- `Which works best when explaining a custom: a reason, a comparison, or an example?` asks the
  learner to evaluate overlapping communication strategies. Use a concrete choice such as `Which
  is easier to explain: bowing or taking off your shoes?`.

Prefer direct verbs, named people or things, and one visible situation. Reject:

- nominalized or metaphorical packaging (`the boundary`, `the factor`, `the conclusion`) when a
  direct `why`, `what happened` or `what would you do` asks the real question;
- `it`, `that`, `this situation` or `the difference` when the referent is not unmistakable in
  speech;
- meta-questions about how to explain, classify, judge or frame an answer unless that action is the
  topic itself;
- unrestricted requests to retrieve a personal memory, fact or example with no concrete foothold;
  when recall is optional, put two or three familiar choices in the prompt or the no-answer route;
- choices that mix or overlap categories, such as `words, a picture, or an example`;
- a Full rewrite that deepens the vocabulary or sentence structure instead of the answer.

For every prompt, the proofreader records the pass mentally by saying a plausible opening answer
aloud. For every follow-up set, test two paths: one after a substantive answer and one after `I
don't know`, `none` or `never`. At least one follow-up must give the second path a concrete new
foothold. A slightly tangential rescue is better than repeating the question the learner could not
answer.

### One printed prompt

Each page prints exactly one talking prompt. A direct imperative such as “Tell me about the first
time you noticed it” is valid; the rule is one conversational job, not one question mark. If the
line contains two questions or joins two independent requests with “and,” rewrite it. Put **2–3
follow-up questions and nothing else** in the English tutor note, never on the learner screen.
Follow-ups rescue a short answer; they are not a second visible assignment. Do not add a coaching
preamble about how to shape the answer, extend the story, preserve a correction frame or interpret
the topic. If a rule applies across lessons, it belongs in this blueprint rather than being
repeated in every private band.

The English question and Japanese support line are direct equivalents. When one changes, change
the other. Tutor notes are English and private. A non-question page may carry one short operational
note only when an essential behavior is otherwise invisible; the pre-study article skip rule and
the final correction re-say are examples. Do not provide a model opinion for the learner to copy.

### Follow-ups must earn their slot

Read the printed question and its follow-ups as one real conversation, then name the job of each
follow-up. Useful jobs include **concretize**, **cause**, **another perspective**, **consequence**,
**contrast** and **hindsight**. If two prompts have the same job, or a prompt has no job beyond
making the list reach three, rewrite it or remove it. **Two strong prompts are better than a filler
third.**

Every set must pass all eight checks:

1. **Answer-dependent.** It responds naturally to a plausible answer to the printed question.
2. **Distinct.** No two follow-ups ask for the same information through different wording.
3. **Non-repeating.** It does not restate the printed question or consume a later main question in
   the TOC ladder. Generic sequence prompts such as “What happened first?” add nothing when the
   printed question already asks for the sequence.
4. **Scenario-safe.** The set still works if the experience happened through a film, online, in a
   shop or through another person's story. Do not silently require travel, a location, or another
   speaker; make a genuinely useful conditional prompt explicit when needed.
5. **Conversation-opening.** A yes/no rescue may be useful, but do not spend two slots dividing one
   dimension into yes/no branches. Ask for the reason, difference, effect or example that can carry
   the conversation forward.
6. **Intellectually paired.** Full and accessible prompts perform the same semantic jobs. The
   accessible version lowers language load; it does not replace a reason or perspective with “Did
   you like it?” or another generic reaction check.
7. **No-answer route.** After `I don't know`, `none` or `never`, at least one follow-up supplies a
   concrete foothold instead of asking for another detail from the missing answer.
8. **Immediate in speech.** Each line independently passes the one-hearing, three-second test. A
   rescue that needs interpretation is not a rescue.

Topic relevance is a boundary, not a cage. A slightly tangential question is better than a dull
restatement when it opens a natural, adult conversation. Follow the most interesting detail in the
learner's answer; do not force every listed question or a preselected language pattern into the
exchange.

### Six checks for a prompt

1. **One hearing, then an answer.** Say one plausible first answer aloud within about three seconds;
   if you must paraphrase the prompt first, rewrite it.
2. **One hypothetical layer.** Do not stack another “if” on a topic already built on a condition.
3. **A visible object.** The learner should not first have to decide what “change” or “improve” is
   supposed to act on.
4. **Anchored vocabulary.** At least one important noun or verb comes from the opening/model/topic.
5. **Not finished by yes/no or A/B.** Except for the deliberate warm-up/setup, ask for the scene,
   reason, threshold or consequence.
6. **No assumed life.** “Your work or studies” remains answerable by workers, students, retirees and
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
- Label the captured line **Student's sentence**. Do not repeat a Japanese task instruction inside
  the response component; the blue script already tells the learner what to do.

The question page needs no choices, explanation card, model answer or grammar tip. Adding any of
those creates a second activity and turns conversation into a worksheet.

`feedback` is course-level reflection, not another correction list: **one strength, one next focus**.
Two lines are enough. Select one useful correction from the session and have the learner re-say it
before closing.

---

## Counting and language rules mirrored from the workflow

- One blue script box per page; English and Japanese carry the same sentence count.
- Tutor scripts are the conversation itself, not a layer of coaching around it. Use the question or
  natural transition alone. Add an instruction only when the learner cannot infer an essential
  interaction without it; never tell them how long to speak, how to structure an answer, where to
  tap, or how to advance through an obvious page. They do not narrate visible setup, preview later
  activities, or repeat `Today we'll...` / `By the end of the lesson...` framing. Japanese matches
  the shorter English line's meaning, sentence count and tone.
- One printed talking prompt per question page, plus 2–3 private follow-ups with no coaching preamble.
  Each follow-up earns a distinct conversational job; two strong prompts beat a filler third, and
  the accessible version preserves the full version's semantic work.
- All learner-facing support is Japanese; English is the target language.
- No `.yomi`, no katakana pronunciation scaffold and no `yomi.js`.
- Vocabulary support is `JP:EN` only. Never put articles, auxiliaries or inflections in hint chips.
- Declare each supported content word as new, recycled, assumed-known or receptive-only in deck
  metadata, and make every hint-chip English value belong to exactly one category. Freetalking's
  load is recorded but is not governed by the Core/Contextual eight-word ceiling.
- Every `data-page-id`, feedback id and sync id is unique.
- Load the same activity sequence as the Korean canonical deck: `activities.js`, `feedback.js`,
  `freetalk-activities.js`, `pager.js`, `script-lines.js`, `spotlight.js`, `tutor-notes.js`,
  `highlight.js`, then `stamp.js`. `feedback.js` is what creates the correction rows.
- Scrolling is allowed; split only when the activity's scope or pager access becomes unclear.

---

## This track does not

- teach a pattern, explain grammar, run a drill or show an answer key;
- read or skim the pre-study article during class, whether aloud or silently;
- put answer coaching or page-operation directions into the spoken script unless essential;
- put answer-shaping, pacing or correction coaching before private follow-up questions;
- replace the Korean sample article with a tutor-authored story or blank dialogue;
- highlight easy words or whole phrases merely to fill a glossary quota;
- expose follow-up questions outside tutor notes;
- cut a productive answer short to reach `q6`;
- make the accessible version intellectually smaller;
- assume the tutor's country, accent or culture;
- use politics or breaking news as reusable topics;
- add katakana readings;
- mix the full and accessible canonical shells or let the accessible version lose semantic depth.
