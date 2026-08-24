# Deck conventions — read before writing any lesson

The track TOCs fix the **grammar**: what a lesson teaches, what the learner already has, what a
later lesson owns and must not be borrowed. That part is (or will be) airtight.

This file fixes everything the TOCs do not: **who appears, what things are called, which scenes
are spent, and what art exists.** Lessons get written in parallel, and without a shared answer to
those, ten lessons independently set their bonus scene in a café and introduce ten different words
for the same object. That reads as ten samples, not one course.

**Append to this file when you spend something.** Using a scene, a name, or a payoff word marks it
used. This is the one file a lesson-writer is expected to edit — **unless you are one of a parallel
batch**, in which case report it and let the orchestrator write it. Ten writers editing one file is
how the file gets lost.

> **Status: the course-batch gate is open.** Core 20 and replacement CTX-1 are the canonical
> shells for their tracks. The old CTX-1 deck is a superseded four-area prototype and must not be
> approved or copied. Both language-load versions of FT-1 are their respective canonical shells.
> Core 32/45/82 and the FT-7/9/49 pairs are approved golden examples for structural variation. The
> owner approved the complete set on 2026-08-19. Pronunciation remains planning-only.

---

## The inline mark vocabulary in English

**`.ending` means "the taught frame words" — the fixed language the learner has to retrieve.**
It is the only inline accent an English deck uses, and it has exactly one meaning.

This is a decision, not an inheritance. Korean's two accents are grammatical categories —
`.topic` violet = 조사, `.ending` orange = 어미 — and English has neither. Rather than pick a
second category arbitrarily, English spends one accent on one idea and leaves violet unused.

Consequences a writer has to honour:

- A rule diagram about the taught frame takes **`class="batchim ending-rule"`**, not bare
  `.batchim`. Bare `.batchim` renders violet, which in this repo means 조사 — a category English
  does not have and must not borrow. The pilot shipped violet first and it was wrong.
- **`.topic` is unspent.** Do not reach for it as a spare slot. If a lesson genuinely teaches two
  distinct pieces, report it — a second accent needs one human decision about what it *means*,
  the same way Korean's third-accent gap does.

---

## Roles

**Decided:** Contextual English is built as **standalone practical situations**, grouped into five
Travel and five Business courses. Both begin at low-intermediate and progress to B2–C1-bridge
tasks. Everyday or social language belongs here only when it completes a travel or workplace job.
It does not inherit Korean Contextual's continuing drama architecture. Course order communicates
coverage and language load, not plot chronology.

**Core Patterns** — practice dialogues use `Tutor` and `Me` with icon avatars.

**Contextual English** — every lesson gives `私` one immediate practical job and gives the tutor the
other role: colleague, staff member, customer, traveller, stranger, or decision-maker. A local name may
make one scene natural, but no name, relationship, or fact may be required by another lesson.

**The learner is a role, not a spectator.** The speaker of every learner line is `私`. The tutor
reads the other role, and the final transfer scene changes at least two meaningful variables.

**Named third parties in example sentences:** *(none yet)*

---

## Scenes already spent

Do not set a new bonus or transfer scene in one already used. The point of a transfer scene is that
the learner meets today's pattern somewhere they have not been yet.

| Scene | Where | Track |
| --- | --- | --- |
| Airport check-in counter, too much luggage | Core 20 `in-the-wild` | core |
| New office, moving boxes in | Core 20 `p3-model` (main dialogue, **not** available as a transfer scene) | core |
| Friday work schedule through dinner | Core 12 `in-the-wild` | core |
| Comparing home-cooking habits | Core 13 `in-the-wild` | core |
| A breakfast alternative | Core 14 `in-the-wild` | core |
| Asking about a brother who lives nearby | Core 15 `in-the-wild` | core |
| Comparing a coworker's workday | Core 16 `in-the-wild` | core |
| Comparing how often two friends cook | Core 17 `in-the-wild` | core |
| Comparing swimming and walking ability | Core 18 `in-the-wild` | core |
| Confirming a bag price | Core 19 `in-the-wild` | core |
| Two friends choosing seats together | Core 21 `in-the-wild` | core |
| Ordering soup and water | Core 22 `in-the-wild` | core |
| Planning drinks and supplies for a trip | Core 23 `in-the-wild` | core |
| Confirming a person's name | Core 24 `in-the-wild` | core |
| **60 contextual main scenes** — every lesson's `場面:` line | `2-contextual-english` CTX-1–60 | contextual |
| Student flat, meeting Sam and checking the front-door code | superseded CTX-1 prototype; unavailable | contextual |
| Hotel reception after immigration | CTX-2 `transfer-scene` | contextual |
| Train station number confirmation | CTX-3 `transfer-scene` | contextual |
| Airport rail ticket desk | CTX-4 `transfer-scene` | contextual |
| City-center route confirmation | CTX-5 `transfer-scene` | contextual |
| Hotel front desk after arranging a taxi | CTX-6 `transfer-scene` | contextual |

**The contextual track assigns its main scenes in the TOC**, one per lesson. Do not replace one
inside a deck assignment—take the `場面:` line from the brief. The writer proposes a distinct final
transfer scene, and the orchestrator checks it against this ledger and neighbouring lessons.

**Assign scenes up front for a parallel batch, one per lesson**, and let the assignment travel in
each writer's packet. Korean assigned 과 11–45 in advance precisely so parallel writers could not
collide, and still produced one duplicate — because two scenes were compared *by name* rather than
by situation (`waiting for a late friend` twice, under two different venue names).
**Compare situations, not labels.**

**A venue used for a main dialogue is not available as that lesson's transfer scene either.** A
learner who meets the same room twice in one lesson reads it as a mistake.

---

## Words

**A payoff word is spent once within a track.** The word or phrase a lesson lands on should not be
another lesson's payoff in the same track. Where the TOC assigns a word to a lesson, the TOC wins
over this list.

| Track | Spent | By |
| --- | --- | --- |
| 1-core-patterns | `I can carry the small one.` — the line the transfer scene lands on | Core 20 |
| 2-contextual-english | `Got it. No worries. Thank you!` — retired with the superseded prototype | old CTX-1 |
| 3-freetalking | `What ordinary part of life in Japan might surprise me?` — the flipped close shared by both language loads | FT-1 |

### Vocabulary in circulation

[`../reference/running-lexicon.md`](../reference/running-lexicon.md) is the generated working copy.
Lesson HTML owns the four-way editorial declaration: **new**, **recycled** (with its earlier stable
id), **assumed-known**, and **receptive-only**. `build_running_lexicon.py` projects those declarations;
never hand-edit the generated ledger or maintain a second word list here.

Accessible and full Freetalking decks with the same `FT-N` are two language-load renderings of one
curricular topic, so the generated ledger permits them to share new-word ownership. Different
`FT-N` topics still cannot both declare the same word new.

For Core and Contextual, `shared/lesson-template.md`'s normal ceiling of eight new content words is
enforced by `check_deck.py`. A genuine exception needs a written `podo:vocabulary-waiver`, which is
surfaced as a warning rather than silently accepted. Every `JP:EN` hint-chip word must appear in
exactly one declaration category. Reuse what is already in circulation rather than inventing
synonyms.

Supporting expressions heard but never asked for in a learner slot:
`What do you need?` (Core 20) · `Anything else?` (Core 9) · `Do you need help?` (receptive)

### Receptive-only

Words and forms that appear in partner lines but are never asked for in a learner-produced slot go
in the deck's `podo:vocabulary:receptive` declaration. Korean's example is a counter that no lesson
owns yet, kept receptive until the TOC assigns it. Keep that restraint rather than quietly
promoting a word to productive.

---

## Art

**Everything referenced must already exist.** A deck that names a file nobody drew fails packaging,
and the packager only bundles paths written in the markup — so an invented filename 404s on the
board while looking fine locally.

Korean's assets live under `korean/trial/assets/`. **Whether English may reference one is decided
per asset, in the table below** — the test is whether the art carries anything Korean in it, not
whether it happens to sit in the Korean folder. Check the file before adding a row; do not assume.

| Asset | Covers | Path | Shared? |
| --- | --- | --- | --- |
| Well-done stamp | the `stamp.js` mark | `en/trial/assets/good-job.svg` | **no** — English has its own. Korean's `well-done.svg` reads 참!잘했어요, outlined into paths; "pure paths" was never the test, since outlined lettering is still lettering. The English twin is the same ring, character and stars with a `Good Job!` arc |
| Mascot | brand pages | `korean/trial/assets/podo-character{,-point}.png` | untested — no English deck uses a brand page yet |
| Mouth shapes | six Korean vowels | `korean/trial/assets/mouth/…` | **no** — hangul-specific. If an English pronunciation track ever needs mouth art it needs its own, drawn for English contrasts |

Note the path: `trial/assets/` stayed inside `korean/` when the runtime was hoisted to the repo
root, so from a lesson deck the assets are **one `../` shorter** than the runtime.

---

## Touching the runtime is an orchestrator decision

"No inline CSS or JS" means the deck ships none of its own. It does **not** mean the shared runtime
is yours to change.

Korean learned this the expensive way: two lesson-writers in one batch each made a *correct* fix to
a shared stylesheet, and the correctness was the problem — a shared-file change made by one of ten
parallel writers lands with no review, no coordination, and no way for a reader to tell it apart
from the file's existing uncommitted work. Worse, it does not reach a learner: decks load a pinned
CDN tag, not the working folder, so a deck depending on a local runtime change renders right for
its author and **unstyled in class**.

So: if a lesson needs something the runtime cannot do, the lesson writer **stops and reports it**.
The orchestrator decides whether to change the one shared runtime, verifies both language paths,
and tracks publication/repointing. The writer never adds a deck-local override.

### The type scale came down — for both languages, with no English branch

This was queued here as *"the type scale is calibrated for CJK density · affects every English
deck"*, and it is now written, so it has left the queue. **There is no English-only class.** The
first attempt added one; it was thrown away, because the sizes turned out to be too large in
Korean too — a Korean goal line was never near wrapping at 22px, it was simply a sentence set at
`.section-title` size. Fixing the shared value fixed both languages and removed a concept.

Measured at 480px, Korean decks against Core 20:

| | was | now | Why |
| --- | --- | --- | --- |
| `.known.lines .k` | 22px | **18px** | Exactly `.section-title`'s size, so a stack of these read as a page of headlines instead of the exchange being promised. The row is 342px wide inside: a Korean line needs 208px of it and an English one needed all 342, so English *also* wrapped and the goal page grew 501px → 674px. 18px is a legibility choice that happens to fit English at 320px |
| `.br-cn` / `.br-ko` | 33px | **26px** | Each side of the row gets 155px, and Pretendard sets full-width glyphs at .923em. 33px fits the 2–4 kanji a Korean deck puts here and nothing longer — a 6-glyph katakana loanword broke `スーツケース` mid-word and rendered its row 37px taller than its neighbours |

Columns stay `1fr · 26px · 1fr`. Asymmetric columns would buy a larger size for katakana, but only
by making a Korean row visibly lopsided, and the equal split is what makes the arrow read as an
equals sign.

**26px carries six full-width glyphs. That is the working ceiling for this component**, so a
seven-glyph loanword (`コンピューター`, `スマートフォン`) wraps and its row grows. Prefer
`スーツケース` when the choice is free; a loanword bridge almost always has a shorter candidate.
It is not worth losing the right example over — take the wrap and note it.

### Runtime state and remaining English gaps

| Needed | State | Why |
| --- | --- | --- |
| Shared English runtime | **live at `curriculum.yaml` → `spec.sharedRuntime.version`** | The immutable version declared there is the only current version claim; do not copy a tag into this document |
| Language-aware tutor-only labels | **part of the pinned shared runtime** | English decks declare `podo:target-language=en`. The runtime emits `Spoken sentence`, `Correction`, `Note`, `Delete`, `Tutor only`, `Message to the learner`, and `Well done stamp` for them while keeping Korean as the default |
| A three-branch rule diagram | not written | inherited from Korean and **worse here**: `do/does/did`, `a/an/the` and `-s/-es/-ies` are all three-case, and `.batchim` is single-column. Core 20 dodged it (its rule is an honest two-brancher). The next lesson that does not, ships two boxes and reports it |
| `.ko` / `.korean` class names | naming only, not a defect | they mean "the line the tutor reads" and "the target-language span". English decks reuse them as-is, because renaming is a runtime change touching 316 Korean decks. Worth knowing before someone reads an English deck and thinks it is mislabelled |
| A second inline accent for English | not written | see the mark-vocabulary section above. Not needed yet |

**Expect this table to fill up fast.** The Korean runtime was designed against Korean pedagogy, and
several of its components encode assumptions that do not hold for English — the `.batchim` rule
diagram is built around a phonological branch on the preceding syllable, and English's equivalent
branches (voicing on `-ed`, `-s` allomorphy, article choice) do not have that shape. Record what
does not fit rather than bending a component into a wrong teaching.

---

## Before you call a lesson done

0. **`python3 tools/authoring/check_deck.py <your deck>` — run this first.** It mechanises items
   1, 3, 4 and 5 below and exits non-zero on any error. It does not replace looking at the page.
1. Every `href`/`src` resolves — run the deck's own relative paths, do not eyeball them.
2. Nothing the lesson has not taught appears in learner-produced English.
3. **No `.yomi`, no katakana over any English word, and `yomi.js` is not loaded.** See
   `../AGENTS.md` — this is the rule most likely to be broken by an agent that read the Korean
   instructions first.
4. **Tutor script sentence parity** — same sentence count on both sides of every `.section-subtitle`
   (`.pattern-meaning` exempt). Mismatched counts make `script-lines.js` give up silently and the
   box renders as bunched text. Script in `../LESSON-CREATION-WORKFLOW.md` §6.
5. **Reorder chunking** — one criterion per page, written into a comment above it, and every row
   checked against that one sentence. Mixed criteria are the defect; the count is only the symptom.
6. Render at 480px and look at it. These are visual documents; a page that reads fine as markup can
   be unusable as a page. Both of the checks above were added *because the pilot passed every other
   check and still shipped them* — markup review does not catch either.
7. **Check every page for a tail hidden under the pager.** Korean documented three separate wrong
   ways to measure this, each of which passed on all 59 decks while the defect was live. Read
   `../../korean/tracks/_conventions.md` § "Before you call a lesson done" item 4 and use its probe
   — measure the page's own height with the viewport prop removed, against the smallest screen this
   has to work on, not against your monitor.
8. Append whatever you spent — scene, payoff word, new vocabulary — to this file.

---

## Runtime publish — current source of truth

The immutable tag declared in the repository-root `curriculum.yaml` at
`spec.sharedRuntime.version` is the current published version. It includes the shared pattern
components and language-aware English tutor-only labels described above. Do not copy the tag into
this file or add deck-local workarounds for shared behavior.

Decks continue to load an immutable pinned runtime. Any future shared-runtime change remains an
orchestrator decision: publish the new tag, repoint the intended decks, and verify both language
paths before the decks ship.
