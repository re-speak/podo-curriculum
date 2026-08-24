# English deltas from `ux-philosophy.md`

English for Japanese speakers. **Everything in [`ux-philosophy.md`](./ux-philosophy.md) holds
except what is written here**, and each entry below is a consequence of the target language
being English — not a matter of taste, and not a place to record that the two curricula happen
to differ. If a rule here would be just as true of Korean, it belongs in the shared file.

The Korean counterpart is [`deltas-kr.md`](./deltas-kr.md). Keep the two symmetric: when one
gains a section, ask whether the other needs the answering one.

## Level bands

`<meta name="podo:level">` carries a CEFR band. `Pre-A1` is **exempt from the teaching-set
variation rule** — the CEFR Companion Volume defines that band as one where the learner "has not
yet acquired generative capacity, but relies upon a repertoire of words and formulaic
expressions", so a rehearsed set is the intended experience there. From A1 — "the lowest level
of generative language use … rather than relying purely on a very finite rehearsed, lexically
organised repertoire of situation-specific phrases" — it is a defect. Korean exempts `왕초급` for
the same reason.

Every English deck also declares `<meta name="podo:target-language" content="en">`. The shared
runtime uses that explicit signal for generated tutor controls; `<html lang="ja">` correctly
describes the learner-support language and must not be repurposed as the teaching-language flag.

## Scripts

- **Tutor notes and tutor-only controls are in English.** They are operating instructions for an
  English-speaking tutor, not learner support. Korean gets a second lock on its answers for free —
  a beginner cannot read the tutor's Korean — and English does not: an English learner can read
  the note. So rely on the tutor-only badge and the teaching-mode switch, and **never restate an
  answer the page already reveals.**
- **An English-speaking tutor never has to interpret Japanese to run an activity.** Japanese
  remains the learner's support language, but a receptive meaning choice also exposes a short
  English sense label, and any non-obvious read order is stated in an English tutor-only note.
  Japanese-only alternatives may support the learner; they may not become the tutor's hidden
  answer key.
- **No Korean anywhere in a learner-facing English deck.**

### Register, in English

The shared rules under *The tutor's register* take these forms. English arrived at several of
these independently during the pilot review — "learner reading is the default", "name who
speaks", "do not narrate visible setup" — a day before Korean generalised the same conclusions
from a native-proofreading round. They are one standard now.

| Shared rule | In English |
|---|---|
| Frame the activity in the arc | "Today…" · "First…" · "This time…" · "So far…" |
| Invite rather than command | "Read it aloud." → "Shall we read it once together?" / "Let's read it once." |
| Name the subject | "If stuck…" → "If the learner gets stuck…" |
| Reassure on covered ground | "You already know this one." |
| Tutor demonstration, when genuinely needed | "I'll read it first." — only for a sound being modelled or a role the tutor holds |

The approved shared activity scripts are byte-exact constants in
`tools/authoring/check_deck.py` and in the batch generators. Changing one is a change to every
deck that uses it: as of this writing the top three run 358, 348 and 264 times. Treat the wording
as a curriculum decision, not a copy edit, and change constant, generators, blueprints and
checker together.

## Citation marks

The shared quoting convention takes English marks: an expression the deck teaches, pulled into a
sentence as-is, is wrapped `“ ”` inside the English line and `「 」` inside `.ja`. Straight quotes
are never used. This convention is new to English — it came across from Korean's
§ 「인용한 표현」 — so expect existing decks to predate it. `tools/authoring/check_quotes.py`
covers both languages.

## No katakana readings. Ever. At any level.

This is the one rule that *inverts* rather than copies its Korean counterpart, and it is the
easiest mistake for an agent that has just read `deltas-kr.md` to make.

Korean decks put a kana `.yomi` under the hangul through 초중급 because hangul is an unfamiliar
script and a beginner genuinely cannot decode it. **English has no such problem** — a Japanese
learner reads the Latin alphabet on day one, so the crutch scaffolds nothing.

Worse, it would actively teach the error. Writing `マクドナルド` over *McDonald's* does not support
the word; it installs mora-timed katakana English, which is the single most damaging Japanese-L1
pronunciation habit in the language and the thing a speaking course exists to undo. This is the
same reasoning that makes `1-hangul` carry no `.yomi` at all — printing the answer over the thing
being learned cancels the learning — except that here it applies to **every English deck at every
level**, not to one track.

So:

- English decks **do not load `yomi.js`** and carry no `.yomi`.
- `<meta name="podo:level">` still declares the deck's level for other purposes; it does not gate
  a reading, because there is no reading to gate.
- Kana is fine wherever it is *not* pronouncing English: a Japanese gloss, a hint chip
  (`JP:EN` vocabulary), a tutor note, a page title's parenthetical.
- If a model line ever genuinely needs a pronunciation scaffold, it must be IPA or a
  stress/rhythm mark, and it needs its own decision first (`BUILD-PLAN.md` → D3b). Do not reach
  for kana.

## Romanize the parts — not applicable

The target language *is* Latin letters, so there is nothing to romanize. If a page needs to show
a sound apart from its spelling, that is IPA and it needs a decision first.

## Decoding arc — none yet

No decoding track exists (`BUILD-PLAN.md` → D6/T5.4). The sentence arc in the shared file is the
only one in use, and it is the spine of every English lesson.

## Reorder chunking

Mixed chip counts on one page are a **hard error** in English, where Korean treats them as a
warning — Korean's agglutination makes a genuinely two-unit sentence possible beside a four-unit
one, and English's does not. Three chips per sentence require an explicit
`data-chunk-review="meaningful"` marker. Meaningful prepositions may stand alone when placing
that preposition is the learning operation; articles and auxiliaries may not.

## The inline mark vocabulary

**`.ending` means "the taught frame words" — the fixed language the learner has to retrieve.**
It is the only inline accent an English deck uses, and it has exactly one meaning.

This is a decision, not an inheritance. Korean's two accents are grammatical categories —
`.topic` violet = 조사, `.ending` orange = 어미 — and English has neither. Rather than pick a
second category arbitrarily, English spends one accent on one idea and leaves violet unused.

- A rule diagram about the taught frame takes **`class="batchim ending-rule"`**, not bare
  `.batchim`. Bare `.batchim` renders violet, which in this repo means 조사 — a category English
  does not have and must not borrow. The pilot shipped violet first and it was wrong.
- **`.topic` is unspent.** Do not reach for it as a spare slot. If a lesson genuinely teaches two
  distinct pieces, report it — a second accent needs one human decision about what it *means*,
  the same way Korean's third-accent gap does.

## Pedagogy colours

English adds none, and inherits one exclusion: the cream / pink consonant-vowel seats are
hangul-specific. Those tokens are unused in English decks; **do not repurpose them** for
something else.

## Vocabulary ownership

English decks declare a four-way vocabulary contract in metadata — `new`, `recycled`, `assumed`,
`receptive` — with every recycled entry naming the earlier lesson that introduced it, validated
for reachability across the whole corpus by `tools/authoring/en/corpus_integrity.py`. Korean has
no equivalent ledger; its nearest relative is `check_syllabus.py`, which does the grammar half by
hand for one track. This is currently a delta because only one side built it, which is exactly
the kind of entry that should stop being a delta — it is not a consequence of the target
language, and it belongs in the shared file the day Korean grows one.
