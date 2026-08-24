# English pilot feedback and release checklist

This is the durable retrospective from the approved English pilots. Use it after the track
blueprint and canonical deck, before asking for review or multiplying a lesson into a batch.
It records failures that can look plausible in static HTML while changing the intended learning
experience.

## Decision order

1. The English TOC and generated brief own the title, outcome, level, and content.
2. The English track blueprint owns the learning arc and page job.
3. The matching approved English canonical deck owns voice, interaction rhythm, and learner load.
4. A whole Korean lesson may be used to check component behavior and visual parity, but isolated
   screenshots are not a curriculum specification and Korean tutor copy is never copied into an
   English course.
5. Fix the highest source that is wrong, regenerate what it owns, and then audit the rendered deck.

## Every English lesson

- Keep learner-facing English natural enough to say outside a lesson; do not preserve translated
  phrasing merely because it is grammatical.
- Tutor-only operating copy is English, short, positive, and action-oriented. Do not narrate visible
  setup or add defensive prohibitions such as “do not model” when the positive action already makes
  the operation clear.
- Tutor notes do not add coaching unless the activity would otherwise be ambiguous or unsafe. Keep
  teaching content in the teaching component and put the activity procedure in the tutor note.
- Learner reading is the default. The tutor reads target language only when the page is explicitly
  a listening/comprehension activity, and that page names who speaks and what the learner does.
- Preserve English/Japanese meaning, sentence count, target highlighting, and the learner's next
  action as a pair.
- Use the exact TOC/brief title. A convenient short label is not a new title.
- Validate both 480 px and 360 px, with 480 px as the classroom release viewport. English strings
  are longer: inputs must wrap or grow vertically, labels must remain readable, and nothing may
  clip or escape its card. Measure every inline input component (`slot-input` and `phrase-input`),
  including fields on consecutive wrapped rows; checking only one visually similar class is not a
  batch-level spacing audit.
- Interactive controls exist in source HTML. JavaScript binds behavior; it does not manufacture the
  input, textarea, choice, or build zone that static Lemonboard validation expects.

### The approved operating language

- **Goal:** one can-do, then “Please read the title aloud.” The learner reads the title once; no
  example boxes, target exchange or three-outcome preview lives on the goal page.
- **Choose:** choose the answer, then read the complete sentence aloud. The tutor does not move on
  after a silent tap.
- **Reorder:** “Put the words in order, then say the whole sentence out loud.”
- **Fill:** “Say each whole sentence aloud, including the missing words.” The tutor types only the
  missing words exactly as spoken.
- **Translate:** “Read the Japanese, then say it in English.” The tutor types the complete English
  sentence exactly as spoken.
- **Open production:** name the pattern or communicative job in the blue script; let the learner
  answer aloud before capture and correction. The response component contains no second task
  instruction and labels the captured line **Student's sentence**.
- The same operation uses the same trusted script in Core and Contextual. A noun may change when it
  improves naturalness (“sentence” / “request”), but the learner action may not.

### Page usefulness

- A dark transition page is a short bilingual spoken bridge, not a Japanese-only explanation and
  not a grammar lesson.
- A vocabulary/expression page stays only if it removes a real obstacle. A short list of words
  already transparent from Japanese or taught on the next page does no instructional work.
- Use concrete communicative language: “what you need help with,” “what you want,” “the words at
  the end.” Avoid abstract labels such as “thing,” “request frame,” “softener” and “availability”
  when ordinary language explains the same idea.
- Read-aloud directions stay plain unless a concrete, teachable delivery feature matters. Do not
  add vague coaching such as “keep the seat clear,” “make the ending soft,” or “sound calm.”
- Roleplays assign the two visible roles in one or two short sentences and begin. Do not narrate
  bubble colours, layout or reading order.
- Check target fidelity before variety: the exact `pN-read` target must be the `pN-fill` blank.
  Never move the blank onto vocabulary to manufacture four different answers. On translation,
  record `supported` or `checkpoint`; supported rows carry lexical hints, while articles,
  auxiliaries and inflections never become hints.

## Core Patterns

- Mirror the taught English target and its exact Japanese meaning with `.ending` in the model.
  Highlight the Japanese segment that reconstructs the missing English with `.target` in
  completion activities.
- Make the learner choose the smallest honest contrast. If only `went/go` and `had/have` are being
  tested, keep the sentence fixed and make those words the choices.
- Every row must add a real decision. Do not repeat one identical blank/answer down the page, and
  do not offer a binary contrast such as `do / am` when the same option is obviously correct every
  time. Include contexts where both alternatives can genuinely be correct, add a useful negative
  contrast, or choose a different activity.
- `Make it yours` prints the exact target frame and a concrete question or situation. Do not make
  the learner infer the required pattern from an earlier page, and do not say “the same question”
  unless that question is visible on the current page.
- A controlled inline phrase input contains only an exact target already established on the
  corresponding fill page. Keep scene facts and slot vocabulary visibly printed around it. Use a
  whole-sentence field only on translation or open production, where whole-sentence recall is the
  actual learner job.
- `p3-model` and `p3-complete` are the same conversation: same turn count, order, partner lines,
  and closing. Completion removes learner language; it does not rewrite or shorten the scene.
- Model, completion, and `Out in the world` are roleplays and use profile images for every turn.
  Live tutor/learner Free Talk uses generic Tutor/Me icons because those people are actually in the
  class.
- Free Talk is a real reciprocal exchange: the learner uses the actual target scaffold, asks the
  tutor a concrete matching question, and receives the tutor's real answer when that exchange is
  natural. After required controlled production, an interesting relevant question may take
  priority over forcing the exact frame. Labels such as “Use both patterns” or “Ask the tutor” are
  not usable speaking support.
- The final transfer must complete the practical job, not stop immediately after the first target
  sentence.

## Contextual English

- Build one self-contained practical scene with a believable partner reaction and a complete job.
- Open with one goal page, then start the roleplay. Do not repeat the same roles and can-do in a
  separate situation overview.
- An English-speaking tutor must be able to run every activity without understanding Japanese.
  Receptive meaning choices show a concise English sense label alongside Japanese learner support;
  Japanese-only answer options are not teachable operating copy.
- `Expressions` is optional. Keep it only when the items remove a real obstacle, and give the tutor
  and learner a clear action. Do not use a passive page description where the script should say
  what to read or do.
- Mirror English/Japanese target highlights through teaching, reading, fill, model, and replay just
  as in Core. Every controlled blank has one exact Japanese `.target`; reorder and full translation
  prompts remain neutral.
- Scene, model, replay, and transfer are roleplays with profile images on every turn. Only the live
  reciprocal Tutor/Me page uses generic icons.
- On `Understand`, the tutor reads each staff line and the learner chooses its meaning. Say that
  explicitly; do not tell the learner to read the staff line while also telling the tutor to read it.
- Keep the production ladder intact: notice, constrained choice, model, replay, reciprocal use,
  then transfer.
- Reorder by semantic chunks. Three is the default working minimum, but two is correct when the
  sentence genuinely contains only two meaningful units; do not split an article from its noun or
  tear apart a fixed request frame to satisfy a count.
- The transfer scene must let the learner resolve the situation, not merely produce one line.
- Late replay and transfer phrases use wrapping, auto-growing fields. Do not force long English
  production into a clipped single-line control, and do not blank an untaught closing line.
- The live discussion page follows the most interesting relevant answer. Invite today's pattern
  only if it fits naturally; controlled practice and roleplay own mandatory pattern retrieval.
- The live discussion remains reciprocal even when exact pattern reuse is optional: tutor asks,
  learner answers and asks back, tutor answers truthfully. A single feedback box is reflection, not
  Free Talk.

## Freetalking

- The goal page introduces the topic and asks the learner to read the title once. It has no three
  outcome rows.
- Page 2 is a 10-to-15-row pre-study article. Class time begins with one direct question about
  learner questions; if there are none, move on. Do not read, skim, or catch up on the article in
  class.
- Gloss only a word likely to block comprehension at that version's level. Default to one word;
  use multiple words only for a true lexical unit such as `confirmation bias`. Familiar topic
  nouns, transparent phrases, and ordinary level-appropriate words do not earn highlights.
- Use the exact style script `Please choose your preferred discussion style.` and put
  `Discussion first` before `Correction first`.
- Each discussion page has one printed talking job and two or three follow-ups only. Every
  follow-up must depend on a plausible answer, add distinct depth or breadth, avoid repeating the
  prompt, and remain usable when the learner says “no,” “neither,” or has no matching experience.
- Do not assume the tutor's nationality, travel history, personality, or personal circumstances.
- Interesting questions outrank strict topical repetition. A useful tangent is allowed when it
  remains connected to the learner's answer and opens a better conversation.
- Full and Accessible versions preserve the same topic progression and claim sequence; simplify
  language and support, not the intellectual job.

## Release gate

1. Compare the whole lesson with the matching canonical lesson, not one page in isolation.
2. Read every prompt, follow-up, answer, hint, and tutor-only note aloud for naturalness and purpose.
3. Run `python3 tools/authoring/check_deck.py sandbox/drafts/en/tracks` and the English tool test suite.
4. Render every new or changed lesson at 480 px and 360 px. Inspect every page manually, including
   long inputs, Core
   model/replay/transfer, Freetalking article/style/questions, and the final page—not only the
   opening screen. Run `tools/authoring/en/audit_rendered_decks.py` through an Orca browser tab for
   a whole batch so hidden pages are activated and measured too, but do not treat its overflow and
   spacing measurements as a human visual or pedagogical approval.
5. Audit the entire generated batch before release. A clean pilot does not prove its siblings kept
   the same standards.
6. Complete and pass a hash-bound `page_review.py` ledger for the final lesson bytes. If the lesson
   is regenerated after review, its old ledger is invalid even when the page count is unchanged.
   Do not collapse generated, mechanically validated, human-audited and owner-approved into one
   `complete` label.
