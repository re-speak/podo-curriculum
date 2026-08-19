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
- Tutor-only operating copy is English, short, and action-oriented. Do not narrate visible setup.
- Tutor notes do not add coaching unless the activity would otherwise be ambiguous or unsafe.
- Preserve English/Japanese meaning, sentence count, target highlighting, and the learner's next
  action as a pair.
- Use the exact TOC/brief title. A convenient short label is not a new title.
- Validate both 480 px and 360 px, with 480 px as the classroom release viewport. English strings
  are longer: inputs must wrap or grow vertically, labels must remain readable, and nothing may
  clip or escape its card.
- Interactive controls exist in source HTML. JavaScript binds behavior; it does not manufacture the
  input, textarea, choice, or build zone that static Lemonboard validation expects.

## Core Patterns

- Mirror the taught English target and its exact Japanese meaning with `.ending` in the model.
  Highlight the Japanese segment that reconstructs the missing English with `.target` in
  completion activities.
- Make the learner choose the smallest honest contrast. If only `went/go` and `had/have` are being
  tested, keep the sentence fixed and make those words the choices.
- A phrase input includes the pattern and the meaningful content the learner must actually produce.
  Do not shrink late production to the frame alone, and do not make the whole sentence editable
  when unrelated framing is already supplied.
- `p3-model` and `p3-complete` are the same conversation: same turn count, order, partner lines,
  and closing. Completion removes learner language; it does not rewrite or shorten the scene.
- Model, completion, and `Out in the world` are roleplays and use profile images for every turn.
  Live tutor/learner Free Talk uses generic Tutor/Me icons because those people are actually in the
  class.
- Free Talk is a real reciprocal exchange: the learner uses the actual target scaffold, asks the
  tutor a concrete matching question, and receives the tutor's real answer. Labels such as “Use
  both patterns” or “Ask the tutor” are not usable speaking support.
- The final transfer must complete the practical job, not stop immediately after the first target
  sentence.

## Contextual English

- Build one self-contained practical scene with a believable partner reaction and a complete job.
- An English-speaking tutor must be able to run every activity without understanding Japanese.
  Receptive meaning choices show a concise English sense label alongside Japanese learner support;
  Japanese-only answer options are not teachable operating copy.
- `Expressions` gives the tutor and learner a clear action. Do not use a passive page description
  where the script should say what to read or do.
- Mirror English/Japanese target highlights through teaching, reading, fill, model, and replay just
  as in Core. Every controlled blank has one exact Japanese `.target`; reorder and full translation
  prompts remain neutral.
- Scene, model, replay, and transfer are roleplays with profile images on every turn. Only the live
  reciprocal Tutor/Me page uses generic icons.
- Keep the production ladder intact: notice, constrained choice, model, replay, reciprocal use,
  then transfer.
- Reorder by semantic chunks. Three is the default working minimum, but two is correct when the
  sentence genuinely contains only two meaningful units; do not split an article from its noun or
  tear apart a fixed request frame to satisfy a count.
- The transfer scene must let the learner resolve the situation, not merely produce one line.
- Late replay and transfer phrases use wrapping, auto-growing fields. Do not force long English
  production into a clipped single-line control, and do not blank an untaught closing line.

## Freetalking

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
- Full and Accessible versions preserve the same topic progression and claim sequence; simplify
  language and support, not the intellectual job.

## Release gate

1. Compare the whole lesson with the matching canonical lesson, not one page in isolation.
2. Read every prompt, follow-up, answer, hint, and tutor-only note aloud for naturalness and purpose.
3. Run `python3 english/tools/check_deck.py english/tracks` and the English tool test suite.
4. Render every new or changed lesson at 480 px. Inspect long inputs, Core model/replay/transfer,
   Freetalking article/style/questions, and the final page—not only the opening screen.
5. Audit the entire generated batch before release. A clean pilot does not prove its siblings kept
   the same standards.
