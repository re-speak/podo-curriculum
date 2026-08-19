# Lesson UX Philosophy

The guiding principles behind every page of the Korean curriculum.

## North star
- **One activity type per page.** Never combine two kinds of task on one screen.
- **Instant clarity.** A learner should know what to do in ~2 seconds, before reading carefully.
- **Minimal everything.** Fewest words, fewest elements; no decoration that doesn't help the task.
- **Receptive → productive.** Every pattern moves from recognizing it to producing it.

## Page anatomy
- **Korean-first title**, with a light, thin Japanese gloss in parentheses.
- **The title is a label, not speech** — a noun phrase, never a question or a full sentence. If there's a question to ask, it belongs in the script box.
- **One blue script box** per page — the exact line the tutor reads aloud (see *Scripts*). Blue means exactly one thing in this system: the tutor is saying it out loud. Nothing else may take that fill.
- **One boxed component** holds the activity (max two levels of nesting); it fills the page.

## Scripts & language
- The script box is the tutor's **word-for-word spoken script** — natural, simple, *spoken* Korean (해 주세요 / 볼까요), not textbook phrasing, no grammar jargon (e.g. avoid 조사).
- **Conversational brevity is part of accuracy.** Use the shortest line a person would naturally
  say without losing the learner's next action or the lesson's meaning. A goal names the
  conversation; it does not inventory every later prompt, tell the learner to speak at length, or
  repeat framing the page already supplies (`오늘은`, `수업이 끝나면`). When Korean gets shorter,
  rewrite the Japanese to match its meaning and conversational tone in the same change.
- **Written in first person.** The tutor is the one speaking: 제가 / 私が, never 선생님이 / 先生が.
- **Lessons are audio-only — the learner never sees the tutor.** Nothing may depend on watching them: no 제 입 모양을 보고 / 口の形をまねして, no gestures, no "look at me". Model a sound by *saying* it: 제가 먼저 읽을게요. 잘 듣고 따라 읽어 보세요. (Pointing at the lesson page is fine — the learner has it. Describing the learner's *own* mouth is fine and matters more here: 입술을 동그랗게.)
- **Both lines say the same sentence.** In the script box the Japanese is a direct translation of the Korean, not extra teaching content. When they drift apart, expand the Korean up to the Japanese — don't trim the Japanese down.
- **Say the learner's next action, not how the page was prepared.** If cards or chunks are visibly out of order, keep the shuffle rationale in an authoring comment and tell the learner only what to do (`한 블록씩 읽어 보세요`). Do not make the tutor narrate obvious setup such as `순서를 섞었어요`. A real contrast or decision the learner must notice still belongs in the script.
- **Japanese is always secondary support** — title parentheses, a header label above an answer area, or small gloss text — never competing with the Korean.
- Translations sit **as a header box on top** of the answer/content, consistently.
- **The header band means translation, and anything else in it is labelled.** Three pages in, a learner reads that band as the Japanese of the Korean below it — so when a write-in activity has nothing to translate yet and the band carries *what to do* instead, it takes a `やること` badge and drops a type weight. Marked, never recoloured: the band's fill already means whose turn it is. A pair of parentheses is not a marker — 「何が好きですか？（先生にも聞いてみよう）」 is a translation and an instruction in one run of text, and it reads as one sentence.

## Input
- **Every activity is answered by tapping or typing — there is no whiteboard and no pen.** Anything that asks the learner to circle, trace, or write by hand has to be re-shaped, not just re-worded: circling becomes tapping tiles, tracing and dictation become assembling the character from an on-screen keypad holding *only the parts already taught*.
- **Answering gives immediate, quiet feedback** — right takes a green tint, a green outline and a solid ✓ badge; wrong takes a plain grey fill, a ✕ and a faded glyph; a second tap undoes it. The two differ by *having colour or not*, never by being lighter or darker shades of the same thing — a learner ten minutes into the alphabet has to read it in about a second. The tutor still leads; the page just stops the learner guessing silently.
- **Reuse one interaction across the deck.** A learner should meet two or three input patterns in a lesson, not a new one per page.
- **Several questions must look like several questions.** Six tiles in one grid read as a single six-way choice; the same six as three numbered rows read as three easy pairs. Group them visually — the activity is otherwise harder than it was designed to be, and the learner blames themselves rather than the layout.

## Teaching mode
- **Two script channels in one card.** A page has a single instruction block: the `blue-100` band is what the tutor *says* to the learner, and a `blue-200` band fused to its underside is what only the tutor sees — read order, pacing, answers. Same family so they read as one card, one shade apart so they are never confused. Never mix the two.
- **The private band is labelled, not just coloured.** It carries a `튜터만` badge, set from CSS so every note gets it without markup. That badge is what lets the band stay soft: an ink-black footer said "not for the learner" by brute contrast, but against `blue-100` it was an ~86-point lightness slam that tore the card in half. Say it in words and the fill only has to be a step.
- **Tutor notes are written in Korean.** The tutor reads Korean; a beginner learner cannot, so the language itself is a second lock on the answers.
- **A tutor note sits directly under the script it belongs to** — that is where the tutor looks after reading the line aloud, and being fused to it means there is no gap to cross. Placement costs the learner nothing: the note is `display:none` for them, and the script box takes its own radius and bottom margin back, so nothing hints that anything was removed. A note that follows something *other* than a script box keeps its standalone chip shape.
- **A note is one short instruction, and never repeats an answer the page already shows.** Teaching mode marks correct tiles and ghosts answers into blanks, so the note points at them (표시된 쪽을 하나씩 읽어 주세요) rather than restating them. If the marks alone make the action obvious, the page needs no note at all. Do not write "for teachers" into the note text — the `튜터만` badge already says whose it is.
- **Everything tutor-only lives behind the 티칭 모드 switch on the cover, and the switch is off by default.** Student view is what the page loads as, and nothing is persisted — reload returns to it. Answers reveal in the same barely-there way as `.slot-input`: a ghost of the answer inside the blank, never a loud key.

## The shared pointer
- **The lesson is spoken over two screens, so the tutor needs a finger.** Tapping a block rings it in red on *both* screens, and exactly one thing is ever lit. It is symmetric — the learner points too. Red is the pointer's alone: a colour that also means something else stops meaning "here". What travels between the screens is *which block is lit*, never the click — see [`interaction-protocol.md`](./interaction-protocol.md).
- **Anything worth saying out loud has to be pointable, and coverage is the whole feature.** A gap in it raises no error — the block simply doesn't light, and a tutor who meets that twice stops trusting the pointer and goes back to describing positions out loud. The pointable vocabulary is a class list in `runtime/js/spotlight.js`; **a new component isn't finished until its name is in that list.** The sales and report pages count as much as the teaching ones — they're where the tutor talks longest.
- **Point at content; never take a click a control already owns.** Pills, chips, buttons and text boxes keep their own taps. But the *container* of an activity is not a control: tapping the card around the pills does nothing to the activity, so it stays the tutor's surface for 「이 문제요」. Excluding whole activity cards merely because they carry the sync id removed the one gesture that names which question is being worked on.
- **Block first, part second.** The first tap rings the whole block; tapping again inside narrows to the part under the finger; a third puts the finger down. Both levels stay reachable through one gesture, so registering a finer part never costs you the block it sits in.
- **A text box is entered, not pointed at — so entering one rings the block around it.** The tutor's cursor doesn't exist on the learner's screen, and without this the learner cannot see which blank is being filled. Ringing the box itself fails twice over: every field clears its own outline on `:focus`, so the ring came off on the writer's screen — the one screen they're looking at — and a ring squeezed onto a 60px slot only points at the slot, where ringing the block says *which question is being answered*. Steady, never pulsing: this one sits under the writer's eyes for as long as the typing lasts, and a throb reads as an alarm.
- **Clicking anywhere else puts the finger down.** Having to hunt down the lit block to switch it off is not how pointing works.
- **The ring is drawn outside the block, in space the block does not own.** Two consequences these decks keep producing: a later sibling with an opaque fill paints over it — so the lit block is lifted while it is lit — and a block sitting flush inside a card that clips its overflow gets the ring sliced down to one stray line, so it is drawn inward instead. Both are *measured* at run time rather than kept as a list of special-case classes, because that list would go stale the next time someone adds a component.

## Scaffolding rules
- **Every slot in a repeated row is filled, or it isn't a slot.** If a column is only sometimes relevant, it doesn't belong in the row — the ragged holes read as broken. Give the column something true for every item, and move the sometimes-relevant thing to its own page.
- **A hint earns its place only by disambiguating**, and a contrast is taught by comparison, not by a footnote on each item. Letters that collapse to the same katakana (어/오 → オ, 우/으 → ウ) get one side-by-side page; letters with no confusable twin get nothing — 이＝イ needs no instruction, and 「そのまま」 is a label that says *ignore me*.
- **Romanize the parts.** Latin letters are phonetic labels, not English (English *mnemonics* like "ㅗ as in go" are the thing to avoid). They do what kana cannot: ナ doesn't come apart, n ＋ a does — so they make a syllable's composition visible. Silent ㅇ is written as –.
- **A reading is a decoding crutch, so it stops at 초중급.** 왕초급 · 초급 · 초중급 decks carry one; 중급 and above do not, because reading hangul is by then a skill the learner has and a deck that keeps doing it for them takes the practice away. The level is the whole test — check `<meta name="podo:level">` before adding a reading to anything, and see the table in `AGENTS.md`.
- **Below that line the deck assumes the learner cannot read hangul, so every Korean they are asked to say carries a kana reading** (`.yomi`) — model lines, pattern cards, dialogue, the chips they arrange, the hint chips. Not the page title (its Japanese gloss already says what the page is), not the blue script box (the tutor reads that), not an answer key. This is the one place the deck deliberately overrides *romanize the parts*: that rule is about the hangul track, where decoding is the skill being built and a reading line would do the learner's work for them. A trial is often somebody's first hour of Korean and its job is to get them speaking, so the crutch is the point — and the **よみがな** switch takes it away the moment it stops being.
- **A reading does not go inside a two-way choice.** The pills in a 고르기 row only ever hold the pattern the page has just taught, so by the time the learner is choosing between them the kana is not help — it is a second line of type inside a two-em target, and four rows of it turn a glance into a paragraph. The *word* beside the pills keeps its reading; the thing being chosen doesn't get one. Wide chips (문장 만들기) have room for both and keep theirs.
- **The switch is named, on the page, and shared.** It rides the right end of the page's own title line, labelled 「よみがな」 in the learner's own language — an icon in the pager was read as deck machinery and the learner never guessed it was theirs to touch. It sits *in* the title row rather than floating over the corner, so a long title wraps in front of it instead of sliding underneath. One `body` class drives every copy, so one tap clears the deck. Unlike teaching mode this state *is* pushed to the other screen: turning the readings off is a move in the lesson ("이제 가나 없이 읽어 볼까요?"), not a private reveal, and the sentence doesn't work if only one person's page changes.
- **A scaffold that can be switched off must leave nothing behind when it is.** A reading takes over the bottom padding of the card it sits in — and `:has()` and `+` keep matching an element that is `display:none`, so hiding one silently took the card's floor with it. Anything that hands space to an optional thing is conditional on that thing being shown; with the switch off, the page must be pixel-identical to the design before readings existed.
- **A persistent control takes no meaning-bearing colour.** The switch's track is ink. Green would say *correct* and lime would say *brand* on all twenty-five pages at once, and a colour that appears everywhere stops saying anything. A switch shape already carries on and off.
- **Hint chips list vocabulary only** (JP:KO) — never particles or verb endings.
- **A chip earns its place by being needed for *that* blank's answer, and nothing else earns it.** Not a word already printed in the line, not a word the tutor just said, not a word that would be nice to know. `네! 일본에 ▁?` hinting 日本:일본 spends the learner's attention on the one word already on screen; worse, `지난주 그 카페에서 ▁.` hinted カフェ and left out 보다, which is the only word the blank actually needs. On a free-writing box there is no one answer, so the chips are the menu — list what can be chosen from.
- **Blanks target only the pattern** being practiced (the particle, the ending).
- **Scaffold every non-target word** so the learner produces only the new piece.
- **Answer keys are present but barely visible** (for review); hideable for production.
- **Write-the-whole-thing inputs are tinted** as a "fill here" cue; short blanks reuse one dashed-pill style, sized to the answer.

## Difficulty arc & cadence
- **Drill each block before teaching the next.** A teaching page is followed by its own drills, never by another teaching page. The learner should never be carrying more than three or four untested items at once. Batching the drills at the end of an act is what makes a lesson *feel* too fast even when nothing in it was too hard — the problem is rarely the difficulty of a page, it's how much went untested before practice arrived.
- **A group is drilled alone before it meets another.** 모음 ① is taught and drilled to completion before 모음 ② begins; the two share an activity only after each has been drilled by itself, and after the page that names what they have in common. Mix them earlier and the learner is tested on two things at once with no way to tell which one they got wrong.
- **Decoding arc (letters, syllables): Listen and pick → Read aloud → Build from the parts.** Hearing which one it was asks less than saying it, and saying it asks less than assembling it from a keypad. Listening leads even though reading looks more elementary — and it is the only rung that checks whether a sound the learner cannot yet distinguish (어/오) actually landed.
- **Sentence arc (patterns): Read → Choose the right one → Reorder the words → Fill the blank → Translate → Write from scratch.**
- **Four items in every closed sentence activity.** Read, choose, reorder, fill and translate do not taper as the learner moves toward production; scrolling is preferable to quietly reducing practice. Review may intentionally use fewer, and free-writing stays one open prompt. A decoding drill instead matches the block it drills — three new letters, three items.
- **One blank answers one question.** A spoken prompt that feeds a single answer box asks for one piece of information. Two are allowed only when the second *narrows* the first — an either/or (`추워요? 더워요?`), or a yes/no that sets up the real question. Three is never allowed, and neither is joining two unrelated questions with 그리고: the learner then has to hold the prompts, compose two or three sentences, and lose track of which one the box is waiting for. If the scene really wants three answers, give it three turns — a short question, a box, the next question. Turns are cheap; working memory at 초급 is not.
- **Reorder four meaningful chunks, not four arbitrary fragments.** Four is the ceiling and the working default. **Three is allowed when the sentence honestly holds only three meaning units** — 저는 · 학생 · 이에요 is three, and padding it with a time or a place the lesson does not need buys a chip at the cost of a natural sentence. What is never allowed is reaching four by breaking something that is one unit: a compound noun (`일본 사람`), a particle off its noun, or an ending off its stem. Nor is stopping at two or three when the sentence already carries a fourth unit that got glued to its neighbour — `한국 사람이에요?` on the same page as `학생` + `이에요?` is not a shorter sentence, it is the same grammar chunked two different ways. Decide the boundaries from the sentence, then keep them consistent down the page.
- **A choice needs two teachable branches.** Use a two-way choice when the lesson has two forms the learner must genuinely distinguish (such as 받침/받침 없음 or 명사+만/동사+기만). Do not manufacture a wrong syllable for an invariant pattern, and do not use two grammatical sentences whose difference requires an unintroduced nuance lecture. When there is no honest binary decision, omit the choose page.
- **Show the operation, not a clipped answer.** When an invariant rule removes dictionary-form `다` and attaches one ending, the visual starts with the complete dictionary form (`듣다 → 듣기 싫어`). Keep that source grouped as one word; a lone stem such as `듣` hides the operation, while separate syllable tiles falsely suggest alternatives. Stem-only tiles remain useful when the final stem sound itself determines a real branch.
- **Meaning comes before mechanics, but not on the transition.** The dark pattern intro is a pacing
  and story bridge. The first teaching page opens with one compact bilingual meaning/use box:
  Korean for the tutor to read, Japanese for the learner to follow. The visual rule that follows
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
  replace an explicit identity. Use the same canonical name throughout the scene (`소희`, `나`,
  `선생님`) and do not add titles or descriptions to individual turns.

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
  | cream / pink seats | consonant / vowel — pedagogy | anything else, anywhere |

- **Dashed grey means "write here"** (`.slot-input`, `.build-slot`) and nothing else.
  A wrong answer is not an empty field, so it is never dashed.
- **Dark pages need no separate system.** The components on a transition page were never
  dark — they are light cards on a dark ground, and the outline lives on the card, not on
  the page. Do not invert anything for them.
- **Mobile-first** — a phone-width column everywhere.
- **Consistency over novelty** — one component vocabulary reused on every page.
- Tokens live in `:root` in `runtime/css/lesson-card.css`. Use the existing semantic
  variables instead of repeating their literal values in deck or track CSS. Do not create
  deck-local variables or a one-use custom property merely to hide a literal. Add a root
  token only when it represents a recurring design-system role, then migrate every consumer
  of that role together.
