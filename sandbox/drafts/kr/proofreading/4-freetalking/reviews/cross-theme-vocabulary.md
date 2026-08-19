# Cross-theme model scaffold integrity audit

Audit date: 2026-08-11

Scope: all 182 current Free Talking lesson decks. This was a read-only audit of lesson HTML; no lesson was edited.

## Initial audit result (pre-repair)

The model/article scaffold is structurally complete, but it is not editorially clean yet.

- 182 decks checked: 168 five-line `model-story` decks and 14 seven-line `article` decks.
- 938 source lines checked: 840 model-story lines and 98 article lines.
- 1,880 `s-key` highlights and 1,880 paired Korean/Japanese vocabulary entries checked.
- 91 Advanced/Intermediate lesson pairs checked.
- Structural parity passed: every source line has Japanese text, every line has the same number of highlights and vocabulary entries, every story has five lines, every article has seven lines, and all sibling pairs use the same source kind, line count, and `data-sync-option` sequence.
- High-confidence residuals: **76 exact line/entry locations across 40 decks**, comprising 51 reversed vocabulary-order lines and 25 fragment/meaning mismatches. The 51 reversals mis-pair both entries on their line, so the two defect classes affect 127 highlight-to-gloss mappings in total.
- Uncertain/editorial-call cases: 6 entries, listed separately below.

## Method

1. Parsed every `lesson.html` below `korean/tracks/4-freetalking/courses/` and selected the `model-story` or `article` source page.
2. Counted source lines, `s-key` spans, `.s-w` entries, Korean vocabulary heads, Japanese glosses, Japanese source sentences, sync IDs/options, and Advanced/Intermediate siblings.
3. Compared each Korean highlight with its same-position Korean gloss and with every alternate ordering on the line. A line was promoted as a reversal only when the alternate permutation produced a strong reciprocal match; all promoted lines were then checked manually against the Korean sentence and Japanese sentence/glosses.
4. Searched separately for glosses that contain grammar endings, auxiliary-only highlights, dictionary phrases whose essential lexical material is outside the highlight, Korean/Japanese gloss disagreement, and unusually low sibling/source-line similarity. Every candidate below was manually reviewed in its full sentence and against its level sibling.
5. Treated ordinary conjugation and irregular forms such as `갔어요`/`가다`, `물었어요`/`묻다`, `봤어요`/`보다`, and `골랐어요`/`고르다` as valid, not mismatches.

The governing vocabulary rule is the current blueprint's `.s-w` contract: use words actually present on that line, highlight the inflected surface form, keep highlight count equal to entry count, and do not use particles/endings as vocabulary entries.

## High-confidence residual 1: reversed vocabulary blocks

On every line below, the two complete `.s-w` blocks are in the opposite order from the two `s-key` highlights. Reordering the whole blocks would repair both Korean and Japanese pairing without rewriting either gloss. The locators are source-line numbers (`L1`–`L5`).

| Exact lesson path below `courses/` | Reversed source lines |
| --- | --- |
| `talk-between-two-countries-advanced/lessons/06-workplace-culture/lesson.html` | L1 |
| `talk-between-two-countries-advanced/lessons/08-convenience-showdown/lesson.html` | L1 |
| `talk-between-two-countries-advanced/lessons/09-drama-vs-reality/lesson.html` | L2, L5 |
| `talk-between-two-countries-advanced/lessons/10-holiday-scenes/lesson.html` | L3, L4 |
| `talk-between-two-countries-intermediate/lessons/06-workplace-culture/lesson.html` | L1 |
| `talk-between-two-countries-intermediate/lessons/08-convenience-showdown/lesson.html` | L1 |
| `talk-between-two-countries-intermediate/lessons/09-drama-vs-reality/lesson.html` | L2, L5 |
| `talk-between-two-countries-intermediate/lessons/10-holiday-scenes/lesson.html` | L3, L4 |
| `talk-people-and-ties-advanced/lessons/01-choosing-friends/lesson.html` | L2 |
| `talk-people-and-ties-advanced/lessons/02-first-impression-changed/lesson.html` | L1, L4 |
| `talk-people-and-ties-advanced/lessons/03-do-you-believe-mbti/lesson.html` | L2, L3 |
| `talk-people-and-ties-advanced/lessons/04-doing-things-alone/lesson.html` | L1, L3, L4, L5 |
| `talk-people-and-ties-advanced/lessons/05-five-minutes-with-a-stranger/lesson.html` | L4 |
| `talk-people-and-ties-advanced/lessons/06-making-up-after-a-fight/lesson.html` | L1, L2, L3, L5 |
| `talk-people-and-ties-advanced/lessons/07-why-friends-decrease-with-age/lesson.html` | L1, L2, L3, L4, L5 |
| `talk-people-and-ties-intermediate/lessons/02-first-impression-changed/lesson.html` | L1, L4 |
| `talk-people-and-ties-intermediate/lessons/03-do-you-believe-mbti/lesson.html` | L2, L3 |
| `talk-people-and-ties-intermediate/lessons/04-doing-things-alone/lesson.html` | L1, L3, L4, L5 |
| `talk-people-and-ties-intermediate/lessons/05-five-minutes-with-a-stranger/lesson.html` | L4 |
| `talk-people-and-ties-intermediate/lessons/06-making-up-after-a-fight/lesson.html` | L1, L2, L3, L4, L5 |
| `talk-people-and-ties-intermediate/lessons/07-why-friends-decrease-with-age/lesson.html` | L1, L2, L3, L4, L5 |
| `talk-small-things-intermediate/lessons/06-stress-relief/lesson.html` | L2 |

Representative current pairings:

- `between-two-countries` Advanced 09 L2: highlights `화면 | 지나갔어요`; vocabulary `지나가다 / 通る | 화면 / 画面`.
- `people-and-ties` Advanced 01 L2: highlights `솔직하게 말했더니 | 사과했어요`; vocabulary `사과하다 / 謝る | 솔직하게 말하다 / 率直に話す`.
- `small-things` Intermediate 06 L2: highlights `살 생각이 없는 | 소스 병`; vocabulary `소스 병 / ソース瓶も | 살 생각이 없다 / 買うつもりがない`.

Counts by theme: 12 reversed lines in `between-two-countries`, 38 in `people-and-ties`, and 1 in `small-things`.

## High-confidence residual 2: fragment or meaning mismatch

`Lx.y` means source line x, vocabulary/highlight position y. Nine entries explicitly use a grammar ending as vocabulary; the others omit essential lexical material from the highlight or give a different contextual meaning. These require an editorial choice of a complete surface highlight and matching Korean/Japanese vocabulary entry, not merely reordering blocks.

| Exact lesson path below `courses/` | Locator | Current highlight | Current Korean / Japanese gloss | Defect |
| --- | --- | --- | --- | --- |
| `talk-between-two-countries-advanced/lessons/05-hidden-gem/lesson.html` | L1.2 | `했어요` | `말하다` / `言う` | Auxiliary fragment does not identify the reported-speech phrase or the glossed verb. |
| `talk-between-two-countries-intermediate/lessons/05-hidden-gem/lesson.html` | L1.2 | `했어요` | `말하다` / `言う` | Same sibling defect. |
| `talk-people-and-ties-advanced/lessons/01-choosing-friends/lesson.html` | L3.2 | `잡았어요` | `날짜를 잡다` / `日を決める` | The meaning “set a date” depends on `새 날짜도`, which is outside the highlight. |
| `talk-small-things-intermediate/lessons/10-cringe-memory/lesson.html` | L3.2 | `갔어요` | `친구에게 가다` / `友達のところへ行く` | The direction/person required by both glosses is outside the highlight. |
| `talk-what-if-advanced/lessons/05-one-food-for-life/lesson.html` | L3.2 | `있어요` | `-을 수도 있다` / `〜することもできる` | Grammar-ending entry; the highlighted auxiliary is not a complete vocabulary item. |
| `talk-what-if-advanced/lessons/05-one-food-for-life/lesson.html` | L5.2 | `몰라요` | `-을지도 모르다` / `かもしれない` | Grammar-ending entry; the highlighted auxiliary is not the glossed construction. |
| `talk-what-if-intermediate/lessons/05-one-food-for-life/lesson.html` | L5.2 | `몰라요` | `-을지도 모르다` / `かもしれない` | Same sibling defect. |
| `talk-what-if-intermediate/lessons/06-one-thing-free-for-life/lesson.html` | L2.2 | `돼요` | `-지 않아도 되다` / `〜しなくてもよい` | Grammar-ending entry; the highlight omits the construction it claims to gloss. |
| `talk-what-if-advanced/lessons/07-one-week-without-a-smartphone/lesson.html` | L1.2 | `나가서 하루 종일 쓰지 못한 적` | `배터리가 나가다` / `切れたこと` | Highlight includes an unglossed consequence while omitting `배터리가`; Japanese gloss is also only a fragment. |
| `talk-what-if-intermediate/lessons/07-one-week-without-a-smartphone/lesson.html` | L1.2 | `나가서 하루 동안 쓰지 못한 적` | `배터리가 나가다` / `バッテリーが切れる` | Highlight includes an unglossed consequence while omitting `배터리가`. |
| `talk-what-if-intermediate/lessons/08-ai-does-my-job/lesson.html` | L1.2 | `봤어요` | `보다` / `〜してみる` | Korean head says “see,” Japanese gives the auxiliary “try,” and the highlight is only the auxiliary half of `맡겨 봤어요`. |
| `talk-what-if-intermediate/lessons/08-ai-does-my-job/lesson.html` | L5.2 | `해요` | `-아/어야 하다` / `〜する必要がある` | Grammar-ending entry; `골라야 해요` is split across two highlights. |
| `talk-what-if-intermediate/lessons/09-if-i-were-an-animal/lesson.html` | L5.2 | `할` | `하다` / `言う` | Korean head and Japanese gloss disagree, and the highlight is only part of the reported-speech construction. |
| `talk-work-and-money-advanced/lessons/03-when-i-felt-successful/lesson.html` | L3.2 | `않았어요` | `걷지 않다` / `歩かない` | Negation auxiliary alone does not contain the glossed verb `걷다`. |
| `talk-work-and-money-advanced/lessons/03-when-i-felt-successful/lesson.html` | L4.2 | `쳤어요` | `박수를 치다` / `拍手する` | `치다` is ambiguous without the omitted object `박수를`. |
| `talk-work-and-money-advanced/lessons/04-what-i-am-learning-now/lesson.html` | L2.2 | `들어요` | `수업을 듣다` / `授業を受ける` | The contextual “take a class” phrase is not fully highlighted. |
| `talk-work-and-money-advanced/lessons/09-best-and-worst-bosses/lesson.html` | L3.2 | `있었어요` | `-을 수 있다` / `〜できる` | Grammar-ending entry; the highlighted auxiliary is not the glossed construction. |
| `talk-work-and-money-intermediate/lessons/02-proudest-work-moment/lesson.html` | L2.2 | `이었어요` | `-라고 하다` / `〜と言う` | Grammar gloss is factually unrelated to the copula in `열두 명이었어요`. |
| `talk-work-and-money-intermediate/lessons/03-when-i-felt-successful/lesson.html` | L4.2 | `쳤어요` | `박수를 치다` / `拍手する` | Same incomplete phrase as the Advanced sibling. |
| `talk-work-and-money-intermediate/lessons/03-when-i-felt-successful/lesson.html` | L5.2 | `들었어요` | `기분이 들다` / `気分になる` | The idiom’s essential noun `기분이` is outside the highlight. |
| `talk-work-and-money-intermediate/lessons/04-what-i-am-learning-now/lesson.html` | L2.2 | `들어요` | `수업을 듣다` / `授業を受ける` | Same incomplete phrase as the Advanced sibling. |
| `talk-work-and-money-intermediate/lessons/04-what-i-am-learning-now/lesson.html` | L5.2 | `있었어요` | `-을 수 있다` / `〜できる` | Grammar-ending entry; the highlighted auxiliary is not the glossed construction. |
| `talk-work-and-money-intermediate/lessons/06-if-i-had-another-job/lesson.html` | L1.2 | `들었어요` | `수업을 듣다` / `授業を受ける` | The contextual “take a class” phrase is not fully highlighted. |
| `talk-work-and-money-intermediate/lessons/06-if-i-had-another-job/lesson.html` | L4.2 | `싶어요` | `-고 싶다` / `〜したい` | Grammar-ending entry; the highlight omits `되고`. |
| `talk-work-and-money-intermediate/lessons/08-why-i-wanted-a-change/lesson.html` | L2.2 | `됐어요` | `계속되다` / `続く` | The lexical part `계속` is outside the highlight, so the highlight reads only as generic `되다`. |

## Advanced/Intermediate and source parity

- All 91 sibling pairs have matching source type, line count, and source-line IDs/options.
- The only key-count-vector difference is the lottery article: Advanced uses three entries on lines 3, 5, and 7; Intermediate uses three on line 3 and two on lines 5 and 7. Manual review found this to be legitimate level simplification, not missing scaffolding.
- Low-similarity sibling lines were manually reviewed. They preserve the same event or argument while shortening, splitting, or reordering details for Intermediate; no high-confidence source-story or article-argument divergence remained.
- Every Korean source line has one Japanese source line. Manual review of the promoted mismatch candidates found no standalone article/model sentence-parity defect beyond the vocabulary mappings listed above.

## Uncertain/editorial-call cases

These are plausible cleanup candidates, but the current meaning remains recoverable and the choice depends on how strictly “surface phrase” is interpreted. They were not counted as defects.

| Exact lesson path below `courses/` | Locator | Current highlight | Current Korean / Japanese gloss | Why uncertain |
| --- | --- | --- | --- | --- |
| `talk-between-two-countries-advanced/lessons/04-table-manners/lesson.html` | L4.1 | `다른 방향으로 놓여 있다는 걸` | `놓인 방향` / `置かれた向き` | Gloss paraphrases a much longer highlighted clause instead of naming its exact surface phrase, but the intended meaning is clear. |
| `talk-between-two-countries-intermediate/lessons/04-table-manners/lesson.html` | L4.1 | `다른 방향으로 놓여 있다는 걸` | `놓인 방향` / `置かれた向き` | Same sibling case. |
| `talk-what-if-advanced/lessons/03-be-someone-else-for-a-day/lesson.html` | L5.2 | `될 것` | `되다` / `〜ようになる` | `되다` can be treated as a conjugated word, but here it functions inside `보게 될 것 같아요`, so the highlight may be too fragmentary. |
| `talk-what-if-advanced/lessons/07-one-week-without-a-smartphone/lesson.html` | L4.2 | `됐어요` | `되다` / `〜ようになる` | Same lexical-word-versus-grammar-construction ambiguity in `바라보게 됐어요`. |
| `talk-what-if-intermediate/lessons/09-if-i-were-an-animal/lesson.html` | L4.2 | `해요` | `하다` / `する` | This is a valid conjugated verb, but `장난도` outside the highlight carries almost all of the useful lexical meaning. |
| `talk-work-and-money-intermediate/lessons/07-how-ai-changed-my-work/lesson.html` | L5.2 | `해요` | `하다` / `する` | Valid as a surface verb, but generic without the outside noun phrase `마지막 확인은`. |

## Verification

- `git diff --check`: passed with no output.
- Lesson HTML changes made by this audit: none.

## Application and final verification

Applied on 2026-08-11 after the generator added first-class `line.N.highlight.M.ko` locators.

- Created `reviews/cross-theme-vocabulary.issues.jsonl` against the then-current HTML and validated **328 issue fields** before editing.
- Repaired all **76 high-confidence line locations across 40 decks**.
  - 51 reversed lines: 204 cited fields, swapping both Korean and Japanese vocabulary fields at positions 1 and 2 while keeping each KO/JA block together.
  - 25 fragment/meaning lines: 124 cited highlight or vocabulary fields, using complete contiguous Korean surface spans and matched Korean/Japanese glosses.
- The six uncertain/editorial-call cases above were not included or changed.
- Preserved every full Korean and Japanese source sentence. A before/after projection comparison found exactly 328 changed fields, all cited by the issue file, with zero uncited changes and zero missing suggestions.

Final checks:

- Pre-edit issue validation: `✓ 328 proofreading issue(s) match the current HTML`.
- Post-edit issue verification: `✓ 328 proofreading issue suggestion(s) are applied`.
- Fresh 182-deck scaffold audit: 168 model stories, 14 articles, 938 source lines, 1,880 highlight/gloss pairs, 0 shape errors, 0 Advanced/Intermediate pair-shape errors, 0 reversed lines, and 0 grammar-ending glosses.
- Proofreading packets regenerated; `--check`: `✓ 182 decks · 10 packets are current`.
- `python3 -m unittest korean.tools.test_build_proofreading_packets`: 5 tests passed.
- Final `git diff --check`: passed with no output.
