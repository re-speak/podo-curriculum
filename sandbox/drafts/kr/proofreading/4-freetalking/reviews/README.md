# Freetalking proofreading status

The original 182-deck freetalking curriculum has completed the compact-packet editorial workflow,
and the 28 Balance Games decks have completed their paired-course audit. Together these make the
210-deck Free Talking release scope. High-confidence corrections are applied in the source HTML.
Editorial calls that need product or author judgment remain unapplied and are consolidated in
[open-editorial-decisions.md](open-editorial-decisions.md).

## Applied review rounds

| Review | Deck field records |
| --- | ---: |
| [Between two countries](01-between-two-countries.issues.jsonl) | 82 |
| [Me lately](02-me-lately.issues.jsonl) | 99 |
| [Things I like](03-things-i-like.issues.jsonl) | 40 |
| [Small things](04-small-things.issues.jsonl) | 86 |
| [People and ties](05-people-and-ties.issues.jsonl) | 32 |
| [Love and marriage](06-love-and-marriage.issues.jsonl) | 69 |
| [Work and money](07-work-and-money.issues.jsonl) | 50 |
| [What came before](08-what-came-before.issues.jsonl) | 140 |
| [What if](09-what-if.issues.jsonl) | 53 |
| [Worth thinking about](10-worth-thinking-about.issues.jsonl) | 101 |
| [Cross-theme vocabulary](cross-theme-vocabulary.issues.jsonl) | 328 |
| [Accepted product decisions](accepted-decisions-2026-08.issues.jsonl) | 46 |
| **Total reviewed field records** | **1,126** |

The shared boilerplate review and accepted correction-mode policy produced four common fixes,
each propagated to the original 182 decks (728 string instances). Twenty-one first-pass vocabulary records
were subsequently improved by the cross-theme vocabulary round. Those records retain the original
audit history and use guarded `supersededBy` links to the final applied record.

## Final audits

- [Cross-theme language](cross-theme-language.md): titles, metadata, Korean/Japanese parity,
  duplicates and terminology.
- [Cross-theme sensitivity](cross-theme-sensitivity.md): all 18 deep-topic decks and all 144 deep
  question notes retain comfortable-range and skip safeguards.
- [Cross-theme vocabulary](cross-theme-vocabulary.md): highlight order, complete reusable chunks,
  gloss meaning and sibling shape.
- [Balance Games full-course audit](11-balance-games-full-course.md): all 28 additional decks,
  including level pairing, question quality, Korean/Japanese parity and sensitivity.
- [Open editorial decisions](open-editorial-decisions.md): three product decisions are now applied;
  the remaining 105 observations are consolidated without duplication into 27 decisions.

## Verification result

- All 1,126 issue records are either the current applied suggestion or are explicitly and
  verifiably superseded by a later applied record on the same field.
- All 210 decks and eleven generated Markdown packets are current.
- Static deck validation passes for page shape, metadata, IDs, local references, bilingual prompts,
  follow-ups, forbidden inline code and yomi.
- The packet generator/validator regression suite passes.
- Representative 480px browser checks pass for corrected vocabulary expansion, shared style copy,
  an opinion article and deep-topic skip guidance; no horizontal overflow or console errors were
  observed.
- `git diff --check` passes.

Only the explicitly accepted D01, D17 and D18 policies were promoted from the uncertain reviews.
The other 27 consolidated decisions remain unapplied.
