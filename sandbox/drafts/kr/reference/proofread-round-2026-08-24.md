# Korean proofreading round — 2026-08-24

**Source:** PR #116, *교정 반영: 96건 (54개 파일)* — 96 applied edits and 82 reviewer comments
dated 2026-08-19 … 2026-08-24.
**Applied in:** PR #121, merged to `stage` 2026-08-24.
**Open decisions:** [`../proofread-decisions.html`](../proofread-decisions.html) — open it in a
browser, decide, and use *Copy for Claude*.

This file exists because the last two rounds proved that a correction without its reason does not
survive. `이번엔 진짜` was softened once in PR #89, was still standing in 88 places afterwards, and
came back in PR #116 on four separate courses across four separate days. What generalised is now
enforced by `tools/authoring/copy_standard.py` and the tables it reads; what could not be settled
by editing words is written down here, so the next person to open one of these decks finds the
question instead of rediscovering it.

## What was settled, and where it now lives

Every rule below is data in `tools/authoring/kr/copy-standard.json`, quotes the reviewer in its
`why`, and blocks a merge through the authoring gate. Read that file, not this list, for the
current wording — this is only the round's ledger.

| Rule | Decision | Reach |
| --- | --- | --- |
| `authenticity-framing` | An instruction never claims the activity is 진짜 | 87 places, 73 decks |
| `own-experience` | 내 이야기로 바꾸기 → 내 경험을 말하기 | 478 places, 60 decks |
| `chunk-word` | 덩어리 → 낱말 in a reorder instruction | 322 |
| `restore-metaphor` | 복원 → 만들기; nothing was destroyed | 93 |
| `slang-gloss` | A fandom abbreviation is glossed where the learner first meets it | 37 |
| `reason-word` | 까닭 → 이유 | 11 |
| `compare-word` | 견주다 → 비교하다 | 9 |
| `mood-rider` | An instruction says what to do, not how it should feel | 9 |
| `argument-framing` | An activity is not framed as an argument | 2 |

Ten further comments named a replacement outright and were applied as one-off corrections, not
rules: 66과 `겪어 본 일`, 53과 and 60과 sentence rewrites, `규정집 → 규정`,
`드느냐 마느냐 → 드느냐 들지 않느냐`, `못 보냈어 → 안 보냈어`, `친한 사람에게 → 다른 사람에게`,
`반찬을 밀어 주다가`, the gift scene's `버릇 → 습관`, `말끝을 흐려 → 완곡하게`.

Three structural defects the reviewer reported as “페이지가 깨졌어요” were unstyled markup —
`vocab-grid`, `tip-compare` and `task-list` had no rule in `shared/css` or `shared/js`. All three
are now canonical `model-list` / `model-line` / `task-block`. The sweep that found the second and
third of them compares every class the decks use against every rule the runtime ships; re-run it
before assuming a page renders.

## What the round could not answer

Twenty comments need a decision that editing words cannot make. They are in the console with the
deck rendered as the learner sees it, the reviewer's words, and a proposed answer.

**Artwork — 4 comments, 1 decision.** `shared/` ships two portraits, so every partner in every
scene drew from the same two. Assigning them per course fixed most collisions and left five
characters without a face: 형, 상대, 다른 친구, 택시 기사, 승객. Three are men. New portraits mean
a `sharedRuntime` version bump and a repoint of every deck.

**Course design — 6 comments, 4 decisions.** 지민 proposes banmal then speaks 존댓말
(02-choosing-address-terms); two speech levels sit in one bubble with no addressee
(08-mixed-hierarchy); 효도 “이 과의 내용도 없어도 될 것 같아요” (10-filial-devotion); and
“단원 2-2 와 유사함” against 01-first-meeting, a reference nobody has resolved yet.

**Scene logic — 5 comments, 4 decisions.** An answer that does not answer its question
(04-hearsay); a softening lesson whose model line is blunt (05-gentle-disagreement); a teaser
describing a different scene (06-suggestions-and-commands); and an awkward moment reported but
never played (09-semi-formal-speech).

**Native ear — 5 comments, 5 decisions.** Lines the reviewer said are not how people speak, with
no replacement offered: three in 10-filial-devotion, plus `계산은 정말 네가 하는 거야?`
(07-one-favor) and `우리 앞으로도 오래 볼 사이일까?` (09-just-between-us).

**Decide 효도 first.** If 10-filial-devotion is retired, three of the native-ear decisions vanish
with it.

## What the rules deliberately cannot reach

- **Reorder chips and their `data-a` answer keys.** A gloss inside a chip changes the answer, so a
  deck that uses a term only as drag-and-drop material — 07-real-life-vs-fandom does, for 스밍 and
  덕메 — is left to human judgment.
- **Titles.** Two or three words long; a parenthetical inside one reads as belonging to the last
  word only. The gloss goes in the first sentence of prose instead.
- **Generators.** `copy_standard.py --sources` reports a violation in the scripts that write decks
  but never rewrites one, because a string in a generator can also be a comment explaining why the
  rule exists.
