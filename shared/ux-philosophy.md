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
- **Written in first person.** The tutor is the one speaking: 제가 / 私が, never 선생님이 / 先生が.
- **Lessons are audio-only — the learner never sees the tutor.** Nothing may depend on watching them: no 제 입 모양을 보고 / 口の形をまねして, no gestures, no "look at me". Model a sound by *saying* it: 제가 먼저 읽을게요. 잘 듣고 따라 읽어 보세요. (Pointing at the lesson page is fine — the learner has it. Describing the learner's *own* mouth is fine and matters more here: 입술을 동그랗게.)
- **Both lines say the same sentence.** In the script box the Japanese is a direct translation of the Korean, not extra teaching content. When they drift apart, expand the Korean up to the Japanese — don't trim the Japanese down.
- **Japanese is always secondary support** — title parentheses, a header label above an answer area, or small gloss text — never competing with the Korean.
- Translations sit **as a header box on top** of the answer/content, consistently.

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
- **Everything tutor-only lives behind the 티칭 모드 switch on the cover, and the switch is off by default.** Student view is what the page loads as, and nothing is persisted — reload returns to it. Answers reveal in the same barely-there way as `.slot`: a ghost of the answer inside the blank, never a loud key.

## Scaffolding rules
- **Every slot in a repeated row is filled, or it isn't a slot.** If a column is only sometimes relevant, it doesn't belong in the row — the ragged holes read as broken. Give the column something true for every item, and move the sometimes-relevant thing to its own page.
- **A hint earns its place only by disambiguating**, and a contrast is taught by comparison, not by a footnote on each item. Letters that collapse to the same katakana (어/오 → オ, 우/으 → ウ) get one side-by-side page; letters with no confusable twin get nothing — 이＝イ needs no instruction, and 「そのまま」 is a label that says *ignore me*.
- **Romanize the parts.** Latin letters are phonetic labels, not English (English *mnemonics* like "ㅗ as in go" are the thing to avoid). They do what kana cannot: ナ doesn't come apart, n ＋ a does — so they make a syllable's composition visible. Silent ㅇ is written as –.
- **Hint chips list vocabulary only** (JP:KO) — never particles or verb endings.
- **Blanks target only the pattern** being practiced (the particle, the ending).
- **Scaffold every non-target word** so the learner produces only the new piece.
- **Answer keys are present but barely visible** (for review); hideable for production.
- **Write-the-whole-thing inputs are tinted** as a "fill here" cue; short blanks reuse one dashed-pill style, sized to the answer.

## Difficulty arc & cadence
- **Drill each block before teaching the next.** A teaching page is followed by its own drills, never by another teaching page. The learner should never be carrying more than three or four untested items at once. Batching the drills at the end of an act is what makes a lesson *feel* too fast even when nothing in it was too hard — the problem is rarely the difficulty of a page, it's how much went untested before practice arrived.
- **A group is drilled alone before it meets another.** 모음 ① is taught and drilled to completion before 모음 ② begins; the two share an activity only after each has been drilled by itself, and after the page that names what they have in common. Mix them earlier and the learner is tested on two things at once with no way to tell which one they got wrong.
- **Decoding arc (letters, syllables): Listen and pick → Read aloud → Build from the parts.** Hearing which one it was asks less than saying it, and saying it asks less than assembling it from a keypad. Listening leads even though reading looks more elementary — and it is the only rung that checks whether a sound the learner cannot yet distinguish (어/오) actually landed.
- **Sentence arc (patterns): Read → Choose the right one → Reorder the words → Fill the blank → Translate → Write from scratch.**
- **Default 4 items** per activity (fewer for review, one for free-writing). A decoding drill instead matches the block it drills — three new letters, three items.
- **3-part lesson shape:** Teach → Practice → Converse / Roleplay.

## Dialogue & characters
- **Chat layout:** partner on the left, the learner on the right (green-tinted bubble), one corner sharpened. The learner's bubble takes the tint but *not* the green outline — a speaker is not a choice.
- **Story characters use photo avatars; tutor/student practice uses a neutral default-icon avatar.**
- **No names cluttering turns** — avatars carry identity.

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

- **Dashed grey means "write here"** (`.slot`, `.slot-input`, `.build-slot`) and nothing else.
  A wrong answer is not an empty field, so it is never dashed.
- **Dark pages need no separate system.** The components on a transition page were never
  dark — they are light cards on a dark ground, and the outline lives on the card, not on
  the page. Do not invert anything for them.
- **Mobile-first** — a phone-width column everywhere.
- **Consistency over novelty** — one component vocabulary reused on every page.
- Tokens live in `:root` in `shared/lesson-card.css`. Use the variables, not the hex.
