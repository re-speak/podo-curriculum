# Korean deltas from `ux-philosophy.md`

Korean for Japanese speakers. **Everything in [`ux-philosophy.md`](./ux-philosophy.md) holds
except what is written here**, and each entry below is a consequence of the target language
being Korean — not a matter of taste, and not a place to record that the two curricula happen
to differ. If a rule here would be just as true of English, it belongs in the shared file.

The English counterpart is [`deltas-en.md`](./deltas-en.md). Keep the two symmetric: when one
gains a section, ask whether the other needs the answering one.

## Level bands

`<meta name="podo:level">` carries one of six values, low to high:

| Band | | Reading scaffold | Notes |
|---|---|---|---|
| `왕초급` | absolute beginner | yes | **Exempt from the teaching-set variation rule** — a rehearsed repertoire is the intended experience here, the same reason English exempts Pre-A1 |
| `초급` | beginner | yes | |
| `초중급` | upper beginner | yes | last band that carries a reading |
| `중급` | intermediate | no | |
| `중고급` | upper intermediate | no | |
| `고급` | advanced | no | |

## Scripts

- Natural, simple, **spoken** Korean — `해 주세요` / `볼까요`, not textbook phrasing. No grammar
  jargon in the learner's hearing (avoid `조사`).
- First person is `제가` / `私が`, never `선생님이` / `先生が`.
- Audio-only, in Korean terms: no `제 입 모양을 보고`, no `口の形をまねして`. Model a sound by saying
  it — `제가 먼저 읽을게요. 잘 듣고 따라 읽어 보세요.` Describing the learner's *own* mouth is fine and
  matters more here: `입술을 동그랗게`.

### Register, in Korean

The shared rules under *The tutor's register* take these forms:

| Shared rule | In Korean |
|---|---|
| Frame the activity in the arc | `오늘은` · `먼저` · `이번엔` · `지금까지` |
| Invite rather than command | `읽어 보세요` → `한 번 읽어 볼까요?` |
| Name the subject | `막히면` → `학생이 막히면`; `읽고` → `학생이 읽고 나면` |
| Reassure on covered ground | `이미 알고 있는 글자죠?` · `이렇게만 기억해 주시면 돼요` |
| Tutor demonstration, when genuinely needed | `제가 먼저 읽을게요` — only for a new sound or a role the tutor holds. Plain, not `읽어 볼게요`: the tutor is demonstrating, not attempting |
| Learner instruction ending | The activity decides, not taste — silent screen actions take `눌러 보세요`, anything said aloud takes `읽어 볼까요?`, and the Japanese moves with it (`てください` / `てみましょうか`) |

The Hangul track additionally has a set of **settled repeated phrases** agreed with a native
proofreader — the exact strings for pages that recur across decks. They live in
`sandbox/drafts/kr/AUTHORING.md` § 「한글 트랙에서 합의한 반복 문구」 and are enforced by
`tools/authoring/kr/check_teaching.py` rule 7.

### Tutor notes are written in Korean

The tutor reads Korean; a beginner learner cannot, so the language itself is a second lock on
the answers. This is a real delta: English has no such lock and relies on the badge and the
switch instead.

## Citation marks

The shared quoting convention takes Korean marks: an expression the deck teaches, pulled into a
sentence as-is, is wrapped `‘ ’` inside `.ko` and `「 」` inside `.ja`. Straight quotes are never
used. Particles stay outside the quote (`‘어때?’만`), both sides quote in the same places, and a
full-sentence citation puts the period outside the closing quote. The full rule is in
`sandbox/drafts/kr/AUTHORING.md` § 「인용한 표현」.

## Readings — the `.yomi` scaffold

This is the largest delta, and it has no English counterpart at all.

- **A reading is a decoding crutch, so it stops at `초중급`.** `왕초급` · `초급` · `초중급` decks carry
  one; `중급` and above do not, because reading hangul is by then a skill the learner has and a
  deck that keeps doing it for them takes the practice away. The level is the whole test — check
  `<meta name="podo:level">` before adding a reading to anything.
- **Below that line the deck assumes the learner cannot read hangul, so every Korean they are
  asked to say carries a kana reading** (`.yomi`) — model lines, pattern cards, dialogue, the
  chips they arrange, the hint chips. Not the page title (its Japanese gloss already says what
  the page is), not the blue script box (the tutor reads that), not an answer key.
- **A reading does not go inside a two-way choice.** The pills in a 고르기 row only ever hold the
  pattern the page has just taught, so by the time the learner is choosing between them the kana
  is not help — it is a second line of type inside a two-em target, and four rows of it turn a
  glance into a paragraph. The *word* beside the pills keeps its reading; the thing being chosen
  doesn't get one. Wide chips (문장 만들기) have room for both and keep theirs.
- **The switch is named, on the page, and shared.** It rides the right end of the page's own
  title line, labelled 「よみがな」 in the learner's own language — an icon in the pager was read as
  deck machinery and the learner never guessed it was theirs to touch. It sits *in* the title row
  rather than floating over the corner, so a long title wraps in front of it instead of sliding
  underneath. One `body` class drives every copy, so one tap clears the deck. Unlike teaching
  mode this state *is* pushed to the other screen: turning the readings off is a move in the
  lesson (`이제 가나 없이 읽어 볼까요?`), not a private reveal, and the sentence doesn't work if only
  one person's page changes.

## Romanize the parts

Latin letters are phonetic labels, not English (English *mnemonics* like "ㅗ as in go" are the
thing to avoid). They do what kana cannot: ナ doesn't come apart, n ＋ a does — so they make a
syllable's composition visible. Silent ㅇ is written as `–`.

This rule is about the hangul track, where decoding is the skill being built. It is deliberately
overridden by the reading scaffold above in trial and beginner decks, where a learner in their
first hour needs the crutch and the point is to get them speaking.

Hints that disambiguate, in Korean terms: letters that collapse to the same katakana
(어/오 → オ, 우/으 → ウ) get one side-by-side page; letters with no confusable twin get nothing —
이＝イ needs no instruction, and 「そのまま」 is a label that says *ignore me*.

## Decoding arc

Korean has an alphabet track; English has none, so this whole arc is a delta.

- **Decoding arc (letters, syllables): Listen and pick → Read aloud → Build from the parts.**
  Hearing which one it was asks less than saying it, and saying it asks less than assembling it
  from a keypad. Listening leads even though reading looks more elementary — and it is the only
  rung that checks whether a sound the learner cannot yet distinguish (어/오) actually landed.
- **A decoding drill matches the block it drills** rather than the sentence-activity default of
  four: three new letters, three items.

## Reorder chunking

Korean is agglutinative, so a short beginner sentence can honestly hold two meaning units beside
a four-unit sentence on the same page. Mixed chip counts on one page are therefore a **review
candidate rather than proof of a defect**, and `tools/authoring/check_deck.py` reports them as a
warning for Korean where English treats them as an error. Counts above four still fail in both.

The consistency rule still binds: what is being judged is whether the *cutting criterion* is the
same down the page, and a mixed count is only the symptom that makes it visible. `한 국 사람이에요?`
on the same page as `학생` + `이에요?` is not a shorter sentence, it is the same grammar chunked
two different ways.

> **Open:** whether Korean keeps the softer verdict once the content checkers become required PR
> checks is not yet decided. See the note in `sandbox/drafts/kr/AGENTS.md`.

## Pedagogy colours

Korean adds one pair to the shared colour table, and it means nothing outside the hangul track:

| Colour | Means | Never |
|---|---|---|
| cream / pink seats | consonant / vowel | anything else, anywhere |
