# Lesson UX Philosophy

The guiding principles behind every page of every curriculum in this repository.

**This file is language-neutral, and that is load-bearing.** It used to say "the Korean
curriculum", with English carried as an appendix inside `sandbox/drafts/en/AGENTS.md`. The
effect was structural rather than editorial: a Korean learning became shared simply by being
written down here, while an English learning could only ever be a delta, with nowhere to flow
back to. Both sides then re-derived the same rules from their own review rounds, a day apart,
and disagreed on the details. Anything true of both languages belongs in this file. Anything
true of one belongs in its delta file, and the delta files are symmetric:

- [`deltas-kr.md`](./deltas-kr.md) — Korean for Japanese speakers
- [`deltas-en.md`](./deltas-en.md) — English for Japanese speakers

A delta is a consequence of the target language changing, not a matter of taste. If you are
about to write one because the two sides merely happen to differ, you are looking at drift —
fix it here instead.

Throughout, **target language** means the language being taught (Korean or English) and
**support language** means Japanese, which is the learner's own language in both curricula.

## North star
- **One activity type per page.** Never combine two kinds of task on one screen.
- **Instant clarity.** A learner should know what to do in ~2 seconds, before reading carefully.
- **Minimal everything.** Fewest words, fewest elements; no decoration that doesn't help the task.
- **Receptive → productive.** Every pattern moves from recognizing it to producing it.

## Page anatomy
- **Target-language-first title**, with a light, thin Japanese gloss in parentheses.
- **The title is a label, not speech** — a noun phrase, never a question or a full sentence. If there's a question to ask, it belongs in the script box.
- **One blue script box** per page — the exact line the tutor reads aloud (see *Scripts*). Blue means exactly one thing in this system: the tutor is saying it out loud. Nothing else may take that fill.
- **One boxed component** holds the activity (max two levels of nesting); it fills the page.
- **Every page uses the full screen width; colour distinguishes chapter pages.**
  Colour-led pages — the lime brand pages and the dark part dividers — carry a kicker, a title
  and at most the script box. They hold no activity, so they need no card to hold it, and the
  colour reaching every edge *is* the signal that the chapter turned. They run full-bleed: no
  margin, no radius, no shadow.

  Teaching pages use the same outer width and horizontal content gutter. Their white surface
  stays visually quiet while the title, tutor script and activity component carry the page's
  hierarchy. There is only one lesson page on screen at a time, so an outer white margin does
  not communicate a page boundary; it only makes the usable content area narrower.

  A report or 안내 page whose content is itself a bordered card also keeps the outer surface
  frameless, because adding a page frame would make three levels of nesting out of the two
  allowed above.

## Scripts & language
- The script box is the tutor's **word-for-word spoken script** — natural, simple, *spoken* language, not textbook phrasing, and no grammar jargon.
- **Conversational brevity is part of accuracy.** Use the shortest line a person would naturally
  say without losing the learner's next action or the lesson's meaning. A goal names the
  conversation; it does not inventory every later prompt, tell the learner to speak at length, or
  repeat framing the page already supplies. When the target-language line gets shorter,
  rewrite the Japanese to match its meaning and conversational tone in the same change.
- **Written in first person.** The tutor is the one speaking, never "the teacher".
- **Lessons are audio-only — the learner never sees the tutor.** Nothing may depend on watching them: no "copy my mouth", no gestures, no "look at me". Model a sound by *saying* it. (Pointing at the lesson page is fine — the learner has it. Describing the learner's *own* mouth is fine and matters more here.)
- **Both lines say the same sentence.** In the script box the Japanese is a direct translation of the target language, not extra teaching content. When they drift apart, expand the target-language line up to the Japanese — don't trim the Japanese down. `script-lines.js` rebuilds the box as one sentence per line with its own translation underneath, and it silently gives up when the two sides have different sentence counts, so this is a functional requirement and not only an editorial one.
- **Say the learner's next action, not how the page was prepared.** If cards or chunks are visibly out of order, keep the shuffle rationale in an authoring comment and tell the learner only what to do. Do not make the tutor narrate obvious setup such as "I shuffled these". A real contrast or decision the learner must notice still belongs in the script.
- **Japanese is always secondary support** — title parentheses, a header label above an answer area, or small gloss text — never competing with the target language.
- Translations sit **as a header box on top** of the answer/content, consistently.
- **The header band means translation, and anything else in it is labelled.** Three pages in, a learner reads that band as the Japanese of the target-language line below it — so when a write-in activity has nothing to translate yet and the band carries *what to do* instead, it takes a `やること` badge and drops a type weight. Marked, never recoloured: the band's fill already means whose turn it is. A pair of parentheses is not a marker — a translation and an instruction in one run of text reads as one sentence.

### A cited expression is quoted

When an expression the deck **teaches** is pulled into a sentence as-is — in a rule line, a
tutor note, a meaning box — it gets wrapped. Unquoted, it dissolves into the surrounding prose:
in a Japanese sentence a bare run of Korean or English reads as part of the sentence rather than
as the thing being named, and the learner cannot see where the expression starts and stops.

The rule is the same in both curricula; only the marks differ, and each delta file names its
own. In every case: the support-language side uses `「 」`, straight quotes are never used,
particles and articles stay *outside* the quote, both language halves quote in the same places,
and a full-sentence citation puts the sentence-ending punctuation outside the closing quote.

`tools/authoring/check_quotes.py` checks both corpora. It over-selects deliberately — deciding
what counts as a taught expression is a judgement — so treat a hit as a question, not a verdict.

### The tutor's register
A tutor script is a real teacher leading a lesson, not a list of correct task instructions.
Where the meaning is the same, prefer the register below to the short administrative command.
These rules came out of a Korean native-speaker proofreading round and an English pilot review
that reached the same conclusions independently; the wording examples for each language are in
its delta file.

- **Frame the activity in the arc of the lesson** — "today", "first", "this time", "so far" —
  so the learner knows where they are rather than only what to do next.
- **Invite rather than command.** The imperative is not wrong, but a whole deck of it reads as a
  worksheet. Reach for the invitational form as the default and keep the bare imperative for
  where it earns emphasis.
- **Name the subject when it could be ambiguous.** "If they get stuck" beats "if stuck": a tutor
  reading aloud should never have to work out who is meant to do the thing.
- **Reassure on ground already covered**, without asserting the learner knows something they
  have not met yet.
- **Do not narrate the visible state of the screen.** Say why the activity exists and what
  happens next.
- **A slightly longer sentence a tutor would really say beats a shorter one they would not.**
  This does not license padding: never expand into explanation the screen already carries.
- **Fix the support language in the same change.** When the target-language line moves to this
  register, the Japanese moves with it — same subject, same strength of invitation, same
  reassurance.
- **Never claim the activity is the real one.** "This time it's a real question", "now for the
  real thing" — the frame is doing nothing except telling the learner that everything up to here
  was pretend. Say whose turn it is and what they produce. This was the single most repeated
  comment across two Korean proofreading rounds, on four courses, in four separate weeks.
- **An instruction says what to do, not how it should feel.** Cut the atmospheric rider and keep
  the task: "read the four sentences" is the instruction; "without rushing the ending, letting it
  linger" is direction for a performance the page never asked for. Mood belongs in the scene the
  learner reads and in the tutor note, not in the imperative.
- **Prefer the ordinary word to the pretty one.** A support line's job is to be understood at
  speed by someone reading in their second language. Where a literary synonym and an everyday
  word mean the same thing, the everyday word wins — and where the deck has already taught the
  everyday word elsewhere, using its synonym here costs the learner the connection.
- **Name the thing the learner is looking at.** An instruction that calls the on-screen chips
  something other than what they visibly are ("place the four chunks in order") makes the learner
  hunt for an object that is not on the page.

### An activity title is a verb phrase
A title names what the learner will do, with enough context that it is unambiguous on its own —
"ask for a table at a restaurant", not "getting a table"; "report a problem with the room", not
"room problems". A bare noun label reads as a chapter heading, and the learner arrives at the page
still not knowing what is being asked of them. Fourteen titles were rewritten this way in a single
proofreading round, which is what turned it from a preference into a rule.

Titles are also the one place an inline gloss does *not* go: a title is two or three words, and a
parenthetical inside one attaches itself to the last word only.

### Slang is glossed where the learner first meets it
A curriculum that teaches fandom or internet language has to teach it, not just use it. The gloss
goes on the first learner-facing line that uses the short form — the scene, the goal, the question
— as `줄임말(원말)` or by writing the full form. A gloss in the vocabulary strip on a later page
does not count: that is exactly the deck state a reviewer was reading when they wrote "what is
생카? I don't know either." The short form is welcome in the dialogue the lesson is teaching, once
the learner has been told what it is.

### The learner reads the model; the tutor does not read it first
On a page whose models are already printed on screen, the learner reads them. Do **not** build
it as two rounds — tutor reads all four, learner repeats. The model is visible, the learner can
decode it, and the second round spends class time on something the page already did.

Two exceptions, and only two: an activity whose whole point is a **sound the learner cannot yet
produce or distinguish** (pronunciation and alphabet work), and a **dialogue where the tutor
and learner hold different roles** and the exchange requires both voices. Both are cases where
the tutor's voice carries information the page cannot.

This rule is enforced for both languages by `tools/authoring/check_deck.py`; it exists because
the two curricula independently arrived at three different answers for the same page type
within one day of each other, and a spoken-script rule that lives only in prose does not survive
the next generator.

## Input
- **Every activity is answered by tapping or typing — there is no whiteboard and no pen.** Anything that asks the learner to circle, trace, or write by hand has to be re-shaped, not just re-worded: circling becomes tapping tiles, tracing and dictation become assembling the answer from an on-screen keypad holding *only the parts already taught*.
- **Answering gives immediate, quiet feedback** — right takes a green tint, a green outline and a solid ✓ badge; wrong takes a plain grey fill, a ✕ and a faded glyph; a second tap undoes it. The two differ by *having colour or not*, never by being lighter or darker shades of the same thing — a beginner has to read it in about a second. The tutor still leads; the page just stops the learner guessing silently.
- **Reuse one interaction across the deck.** A learner should meet two or three input patterns in a lesson, not a new one per page.
- **Several questions must look like several questions.** Six tiles in one grid read as a single six-way choice; the same six as three numbered rows read as three easy pairs. Group them visually — the activity is otherwise harder than it was designed to be, and the learner blames themselves rather than the layout.

## Teaching mode
- **Two script channels in one card.** A page has a single instruction block: the `blue-100` band is what the tutor *says* to the learner, and a `blue-200` band fused to its underside is what only the tutor sees — read order, pacing, answers. Same family so they read as one card, one shade apart so they are never confused. Never mix the two.
- **The private band is labelled, not just coloured.** It carries a badge, set from CSS so every note gets it without markup. That badge is what lets the band stay soft: an ink-black footer said "not for the learner" by brute contrast, but against `blue-100` it was an ~86-point lightness slam that tore the card in half. Say it in words and the fill only has to be a step.
- **A tutor note sits directly under the script it belongs to** — that is where the tutor looks after reading the line aloud, and being fused to it means there is no gap to cross. Placement costs the learner nothing: the note is `display:none` for them, and the script box takes its own radius and bottom margin back, so nothing hints that anything was removed. A note that follows something *other* than a script box keeps its standalone chip shape.
- **A note is one short instruction, and never repeats an answer the page already shows.** Teaching mode marks correct tiles and ghosts answers into blanks, so the note points at them rather than restating them. If the marks alone make the action obvious, the page needs no note at all. Do not write "for teachers" into the note text — the badge already says whose it is.
- **Everything tutor-only lives behind the 티칭 모드 switch on the cover, and the switch is off by default.** Student view is what the page loads as, and nothing is persisted — reload returns to it. Answers reveal in the same barely-there way as `.slot-input`: a ghost of the answer inside the blank, never a loud key.

## The shared pointer
- **The lesson is spoken over two screens, so the tutor needs a finger.** Tapping a block rings it in red on *both* screens, and exactly one thing is ever lit. It is symmetric — the learner points too. Red is the pointer's alone: a colour that also means something else stops meaning "here". What travels between the screens is *which block is lit*, never the click — see [`interaction-protocol.md`](./interaction-protocol.md).
- **Anything worth saying out loud has to be pointable, and coverage is the whole feature.** A gap in it raises no error — the block simply doesn't light, and a tutor who meets that twice stops trusting the pointer and goes back to describing positions out loud. The pointable vocabulary is a class list in `shared/js/spotlight.js`; **a new component isn't finished until its name is in that list.** The sales and report pages count as much as the teaching ones — they're where the tutor talks longest.
- **Point at content; never take a click a control already owns.** Pills, chips, buttons and text boxes keep their own taps. But the *container* of an activity is not a control: tapping the card around the pills does nothing to the activity, so it stays the tutor's surface for "this question". Excluding whole activity cards merely because they carry the sync id removed the one gesture that names which question is being worked on.
- **Block first, part second.** The first tap rings the whole block; tapping again inside narrows to the part under the finger; a third puts the finger down. Both levels stay reachable through one gesture, so registering a finer part never costs you the block it sits in.
- **A text box is entered, not pointed at — so entering one rings the block around it.** The tutor's cursor doesn't exist on the learner's screen, and without this the learner cannot see which blank is being filled. Ringing the box itself fails twice over: every field clears its own outline on `:focus`, so the ring came off on the writer's screen — the one screen they're looking at — and a ring squeezed onto a 60px slot only points at the slot, where ringing the block says *which question is being answered*. Steady, never pulsing: this one sits under the writer's eyes for as long as the typing lasts, and a throb reads as an alarm.
- **Clicking anywhere else puts the finger down.** Having to hunt down the lit block to switch it off is not how pointing works.
- **The ring is drawn outside the block, in space the block does not own.** Two consequences these decks keep producing: a later sibling with an opaque fill paints over it — so the lit block is lifted while it is lit — and a block sitting flush inside a card that clips its overflow gets the ring sliced down to one stray line, so it is drawn inward instead. Both are *measured* at run time rather than kept as a list of special-case classes, because that list would go stale the next time someone adds a component.

## Scaffolding rules
- **Every slot in a repeated row is filled, or it isn't a slot.** If a column is only sometimes relevant, it doesn't belong in the row — the ragged holes read as broken. Give the column something true for every item, and move the sometimes-relevant thing to its own page.
- **A hint earns its place only by disambiguating**, and a contrast is taught by comparison, not by a footnote on each item. Forms that collapse together in the support language get one side-by-side page; forms with no confusable twin get nothing, and a label that says *ignore me* is worse than silence.
- **Hint chips list vocabulary only** (Japanese:target) — never particles, articles, auxiliaries or inflections.
- **A chip earns its place by being needed for *that* blank's answer, and nothing else earns it.** Not a word already printed in the line, not a word the tutor just said, not a word that would be nice to know. Hinting a word that is already on screen spends the learner's attention on the one thing they can see; worse is hinting the scene noun and leaving out the verb the blank actually needs. On a free-writing box there is no one answer, so the chips are the menu — list what can be chosen from.
- **Blanks target only the pattern** being practiced. A blank that swallows the whole sentence is not a blank, it is a dictation.
- **Scaffold every non-target word** so the learner produces only the new piece.
- **Answer keys are present but barely visible** (for review); hideable for production.
- **Write-the-whole-thing inputs are tinted** as a "fill here" cue; short blanks reuse one dashed-pill style, sized to the answer.
- **A scaffold that can be switched off must leave nothing behind when it is.** Anything that hands space to an optional thing is conditional on that thing being shown; with the switch off, the page must be pixel-identical to the design before the scaffold existed. (`:has()` and `+` keep matching an element that is `display:none`, which is how hiding one silently took a card's floor with it.)
- **A persistent control takes no meaning-bearing colour.** Green would say *correct* and lime would say *brand* on every page at once, and a colour that appears everywhere stops saying anything. A switch shape already carries on and off.

### What a proofread claim means

A deck that declares `podo:proofread-status="complete"` is claiming a human read
it page by page. That claim has to be backed by a review ledger that passes its
own checker — hash-bound to the deck's exact bytes, with the machine-extracted
evidence agreeing and the visual checks at both phone widths marked `pass`.
Otherwise the field says only that something wrote the word.

Today it mostly says only that. Every English generator calls
`set_proofread_status(head, "complete")` unconditionally, and
`page_review.py audit-claims` puts a number on the gap: **395 of 421 English
decks claim a proofreading no ledger can show** — 236 because the visual audit at
360px and 480px was never performed, 156 because the deck was regenerated after
its review and the hash no longer matches, 3 because no ledger exists.

Two rules follow, and the second is the one that keeps being broken:

- **The claim is earned, not written.** A generator may not assert it.
- **Regenerating a deck invalidates its review.** The ledger is bound to bytes on
  purpose, so that a content fix cannot quietly inherit the approval of the deck
  it replaced. When a generator changes, the review is *repeated* on the new
  bytes — not refreshed. `refresh` exists for the narrow case where the evidence
  moved and the judgement did not, and reaching for it after a content change is
  how a stale approval survives.

Korean has the opposite half of this: `build_proofreading_packets.py` runs a real
native-speaker round with a rigorous issue protocol, and records nothing in the
deck at all. The two halves are one mechanism.

## Difficulty arc & cadence
- **Drill each block before teaching the next.** A teaching page is followed by its own drills, never by another teaching page. The learner should never be carrying more than three or four untested items at once. Batching the drills at the end of an act is what makes a lesson *feel* too fast even when nothing in it was too hard — the problem is rarely the difficulty of a page, it's how much went untested before practice arrived.
- **A group is drilled alone before it meets another.** Two groups share an activity only after each has been drilled by itself, and after the page that names what they have in common. Mix them earlier and the learner is tested on two things at once with no way to tell which one they got wrong.
- **Sentence arc (patterns): Read → Choose the right one → Reorder the words → Fill the blank → Translate → Write from scratch.**
- **Four items in every closed sentence activity.** Read, choose, reorder, fill and translate do not taper as the learner moves toward production; scrolling is preferable to quietly reducing practice. Review may intentionally use fewer, and free-writing stays one open prompt.
- **Each activity in a lesson half draws its own sentence set.** Read, reorder, fill and translate are four rungs of a ladder, not one sentence set in four costumes. Running all four over the same four sentences turns a half-lesson into one activity repeated, and the learner stops reading by the third page. Repetition across *forms* is the point; repetition of the *same items* is not. (Measured house norm: 266 of 389 hand-authored lesson-halves already draw four distinct sets; the 122 that did not were almost entirely one generator's output.)
- **Reorder four meaningful chunks, not four arbitrary fragments.** Four is the ceiling and the working default. **Three is allowed when the sentence honestly holds only three meaning units** — and padding it with a time or a place the lesson does not need buys a chip at the cost of a natural sentence. What is never allowed is reaching four by breaking something that is one unit: a compound noun, a particle off its noun, an article off its noun, or an ending off its stem. Nor is stopping at two or three when the sentence already carries a fourth unit that got glued to its neighbour. Decide the boundaries from the sentence, then keep them consistent down the page. **Chunk boundaries are an authoring decision and may never be computed from word count** — arithmetic does not know which words are one idea.
- **A reorder row must actually be scrambled, and not scrambled the same way twice.** The chips are presented out of order so that putting them back is the work. A fixed permutation applied down the page — "the last chip always goes first" — is not a scramble: the learner learns the permutation instead of the sentence, and one generator shipped exactly that to 360 of 360 rows before anyone noticed, because every row was individually solvable and nothing compared them.
- **One blank answers one question.** A spoken prompt that feeds a single answer box asks for one piece of information. Two are allowed only when the second *narrows* the first — an either/or, or a yes/no that sets up the real question. Three is never allowed, and neither is joining two unrelated questions with "and": the learner then has to hold the prompts, compose two or three sentences, and lose track of which one the box is waiting for. If the scene really wants three answers, give it three turns — a short question, a box, the next question. Turns are cheap; working memory at beginner level is not.
- **A choice needs two teachable branches.** Use a two-way choice when the lesson has two forms the learner must genuinely distinguish. Do not manufacture a wrong option for an invariant pattern, and do not use two grammatical sentences whose difference requires an unintroduced nuance lecture. When there is no honest binary decision, omit the choose page — deleting the weaker activity is always available and is usually right.
- **Both branches must be correct somewhere on the page.** Four rows whose correct answer is the same option are visually interactive and pedagogically inert: after the first row the learner taps without reading. This is an objective failure, separate from the human question of whether a distractor is *plausible*.
- **The correct option may not sit in the same place every time, and may not simply alternate.** A learner who can answer by position has stopped reading, and left-right-left-right is that same defect one step later. Vary where the answer sits, irregularly.
- **A teaching set varies in more than one aligned word.** Four exemplars that differ in exactly one token are a substitution drill, not a pattern: the learner swaps a noun into a frame that never changes shape and stores the whole thing as one phrase. Usage-based work on construction learning is explicit that this is worse than merely unhelpful — high token frequency with *low* type frequency inhibits generalisation, because the exemplars form a tight cluster and get stored as one phrase instead of a slot (Bybee 1995; Suttle and Goldberg 2011). Vary the form the pattern actually alternates, not just the noun. The lowest band of each curriculum is exempt, because a rehearsed repertoire is the intended experience there — each delta file names its own exempt level. Above that band a page may still declare `data-exemplar-review="frame-fixed"`, and the case it exists for is narrow: a first-course lesson whose only available subject is the first person, where varying the frame would spend grammar a later lesson owns and the noun swap really is the lesson. The marker is the author saying so on the record, not a way to make the check quiet — a page that *could* vary its frame must. When a whole pattern can only ever produce noun swaps, the pattern is too narrow and the fix is at curriculum level, not on the page.
- **Target fidelity outranks row variety, and only on the blank.** The rule above is about the *teaching set*. On a fill page the blank must be the exact unit the read page highlighted, on every row — even when that makes all four answers identical. Do not manufacture variety by blanking a different word each row; that trades the lesson's target for the appearance of range. If four target-only rows genuinely add no retrieval, the page should be redesigned or omitted, not varied.
- **Show the operation, not a clipped answer.** When an invariant rule removes part of a dictionary form and attaches one ending, the visual starts with the complete dictionary form. Keep that source grouped as one word; a lone stem hides the operation, while separate syllable or letter tiles falsely suggest alternatives. Stem-only tiles remain useful when the final stem sound itself determines a real branch.
- **Meaning comes before mechanics, but not on the transition.** The dark pattern intro is a pacing
  and story bridge. The first teaching page opens with one compact bilingual meaning/use box:
  the target language for the tutor to read, Japanese for the learner to follow. The visual rule that follows
  shows how to build the form, not what the form is for.
- **A native tip must add something.** It contributes one immediately usable adjacent choice — such
  as register, softening, contraction, prosody, collocation or intensity — and never repeats the
  intro, expression page or rule. If both choices are grammatical, present them at equal visual
  weight with situation labels; a correction arrow falsely turns a contextual decision into a
  right/wrong rule.
- **End by playing the next beat.** A contextual teaser is a complete 5–7-turn mini-scene with 2–3
  learner completions using both patterns, and its final turn leaves an unresolved story hook.
- **3-part lesson shape:** Teach → Practice → Converse / Roleplay.

## Dialogue & characters
- **Chat layout:** partner on the left, the learner on the right (green-tinted bubble), one corner sharpened. The learner's bubble takes the tint but *not* the green outline — a speaker is not a choice.
- **Story characters use photo avatars; tutor/student practice uses a neutral default-icon avatar.**
- **Show a short speaker name beside every avatar.** An avatar supports recognition; it does not
  replace an explicit identity. Use the same canonical name throughout the scene and do not add
  titles or descriptions to individual turns.
- **Two names in one scene are two faces, and one name keeps one face across a course.** A
  reviewer reported this four times in one round — "지민, 선배 and 형 have the same face", "the
  friend and 소희 look identical", "지훈 is a woman" — and every instance had the same cause: the
  shared runtime ships two portraits, so every partner in every scene pointed at the same one.
  Assign faces per course, not per deck: a 직원 who is one person in lesson 4 and someone else in
  lesson 7 is worse than the collision it was meant to fix. Where the cast outgrows the portraits
  that exist, that is an asset request, not something to paper over by reusing a face.

## Visual system
- **White cards on a 1px grey outline.** Weight is carried by type and by fills, not by
  outlines — a page of eight ink-outlined rows reads as eight boxes before it reads as eight
  choices, and the learner blames themselves for the difficulty.
- **Every colour carries exactly one meaning**, and this is the rule that keeps a page
  scannable. Breaking it is the fastest way to make the deck unreadable:

  | Colour | Means | Never |
  |---|---|---|
  | `green-500` + `green-100` | state — chosen, correct, active | decoration |
  | `blue-100` | the tutor is saying this aloud | any other box |
  | `blue-200` | fused under it: the same instruction, tutor's eyes only | free-floating anywhere else |
  | `lime` | brand chrome — brand pages, kickers, the pager | state (one lime row out of seven reads as the screen flashing) |
  | `gray-200` | every ordinary outline | emphasis |

  Each delta file may add a pedagogy colour of its own; none may reassign one above.

- **Dashed grey means "write here"** (`.slot-input`, `.build-slot`) and nothing else.
  A wrong answer is not an empty field, so it is never dashed.
- **Dark pages need no separate system.** The components on a transition page were never
  dark — they are light cards on a dark ground, and the outline lives on the card, not on
  the page. Do not invert anything for them.
- **Mobile-first** — a phone-width column everywhere.
- **Consistency over novelty** — one component vocabulary reused on every page.
- Tokens live in `:root` in `shared/css/lesson-card.css`. Use the existing semantic
  variables instead of repeating their literal values in deck or track CSS. Do not create
  deck-local variables or a one-use custom property merely to hide a literal. Add a root
  token only when it represents a recurring design-system role, then migrate every consumer
  of that role together.
