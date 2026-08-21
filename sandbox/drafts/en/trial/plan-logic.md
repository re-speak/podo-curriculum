# Recommendation logic — ladder · duration · curriculum (English)

The English trial produces a report, but **it never shows one.** This document records the
tables that report is built from, and the split that keeps them out of the lesson.

The Korean equivalent is [`../../kr/trial/plan-logic.md`](../../kr/trial/plan-logic.md). Read it
first if you have not: the *shape* of the calculation is shared, and only the tables differ. This
file records the English tables and the places where English genuinely diverges.

## Who draws what

```
trial deck ──┬─ ニーズ把握 : the learner taps 学ぶきっかけ · ゴール · 学習ペース
             └─ 採点        : the tutor picks the level and the five areas, after goodbye
                    │
                    └── snapshot ──▶ le_level_test ──▶ podo-app draws the report
```

**The deck collects; the app renders.** The trial deck carries no level card, no radar, no
roadmap and no Japanese report prose. It ends with the lesson, a goodbye, and one tutor-only
scoring page placed *after* the farewell.

That is not a layout preference. An English trial is taught by an English-speaking tutor, and
the report is written in Japanese — so a tutor walking a learner through it is something we
cannot rely on, least of all for the beginner who needs the explanation most. Putting the
scoring after the goodbye also means the tutor is not doing paperwork while the learner
watches, and can take as long as the judgement deserves.

The learner reads the report afterwards, in the chat, in their own language.

> **So what are the tables below for?** Two things. They are the specification the app has to
> implement — the app owns the rendering and currently disagrees with it (see §7). And they are
> loaded by the deck as `shared/js/report-en.js`, which supplies `AREAS` and the level names the
> scoring page and the saved payload need, and keeps `report.js` from silently falling back to
> the *Korean* course tables if a roadmap is ever added to an English deck.

---

## 1. Materials — what the English tracks actually hold

Taken from the decks that exist under [`../tracks/`](../tracks/). When the curriculum grows, this
table is the first thing to fix.

| Track | Volume | Note |
| --- | --- | --- |
| **1-core-patterns** | **122 lessons** (11 courses) | Finite. This track is the measure of level. |
| **2-contextual-english** | **60 lessons** (10 courses, 2 areas) | Splits by motive — see below. |
| **3-freetalking** | 121 topics × 2 language loads | **No end** — topics keep being added. |
| **4-pronunciation** | 12 planned | **No decks.** Not offered in a recommendation. |

**There is no decoding track**, and that is the first divergence from Korean. Korean's ladder starts
with 14 한글 lessons because a Japanese learner genuinely cannot read the script on day one. A
Japanese learner reads the Latin alphabet on day one, so English has nothing below Core 1. The
English ladder therefore starts at Core rather than one rung below it.

### Core — the 11 courses in order

`classLevel` order is learning order. Cumulative counts are the whole basis of §2.

| # | `classLevel` | Course | Lessons | Cumulative | CEFR |
| ---: | --- | --- | ---: | ---: | --- |
| 1 | `100.010` | core-first-exchanges-1 | 11 | 11 | Pre-A1 · A1 |
| 2 | `100.020` | core-first-exchanges-2 | 13 | 24 | A1 |
| 3 | `100.030` | core-daily-life-and-past | 12 | 36 | A1 · A2 |
| 4 | `100.040` | core-plans-and-comparison | 11 | 47 | A1 · A2 |
| 5 | `100.050` | core-experience-and-ideas | 12 | 59 | A2 → B1 |
| 6 | `100.060` | core-careful-interaction | 11 | 70 | B1 |
| 7 | `100.070` | core-work-and-arrangements | 10 | 80 | B1+ |
| 8 | `100.080` | core-nuance-at-work | 11 | 91 | B1+ · B2 |
| 9 | `100.090` | core-diplomacy-and-reasoning | 11 | 102 | B2 |
| 10 | `100.100` | core-emphasis-and-tone | 10 | 112 | B2 · B2-C1 |
| 11 | `100.110` | core-advanced-stance | 10 | 122 | C1 |

### Contextual — by area

| Area | Courses | Lessons | Entry floor |
| --- | ---: | ---: | --- |
| **Travel** | 5 | 30 | Core 47 |
| **Business** | 5 | 30 | Core 70 |

**Entry floors are advice, not gates.** Above them a learner may enter at any time, and grammar
that runs ahead is learned as a whole chunk rather than derived. They are consulted only when
ordering a recommendation.

The floors come from the courses' own declared levels: Travel opens at `ctx-travel-arrivals-transport`
(A2–B1), which is where Core sits at lesson 47; Business opens at `ctx-business-workplace-essentials`
(B1), which is Core 70. Freetalking is floored at Core 70 as well — the accessible variant is
written for B1, and below that the correction loop has nothing to correct.

---

## 2. Level → lessons already covered (`DONE`)

The overall level 1–10 the tutor picks on the scoring page is converted into "how many lessons is this
person effectively past". Everything downstream is one subtraction against this table.

| Lv | Cumulative | Anchor | CEFR | TOEIC L&R |
| ---: | ---: | --- | --- | --- |
| 1 | 0 | before Core | Pre-A1 | 〜220 |
| 2 | 11 | Core course 1 done | A1 | 220–350 |
| 3 | 24 | Core course 2 done | A1+ | 350–450 |
| 4 | 47 | Core course 4 done | A2 | 450–550 |
| 5 | 70 | Core course 6 done | B1 | 550–650 |
| 6 | 91 | Core course 8 done | B1+ | 650–730 |
| 7 | 112 | Core course 10 done | B2 | 730–800 |
| 8 | 122 | **Core complete** | B2+ | 800–860 |
| 9 | 152 | + one Contextual area | C1 | 860–930 |
| 10 | 182 | + both Contextual areas | C1+ | 930〜 |

**Every anchor is a real course boundary.** No level lands in the middle of a course, because a
tutor who is asked "why 91?" has to be able to point at something.

> **The Lv7 → Lv8 step is 10 lessons where every other step is 20-odd.** That is not a rounding
> error: the last Core course (`core-advanced-stance`) is 10 lessons long, and Lv8 is defined as
> Core complete. Smoothing it would mean anchoring Lv8 somewhere inside course 11, which buys an
> even-looking table at the cost of the one property that makes the table defensible. The Korean
> version of this document records the opposite trade — an anchor that was smoothed and now
> disagrees with its own level copy — and it is worth not repeating.

**TOEIC is a signpost, not a claim.** It is in the table because it is the scale this market
actually reads; it measures reading and listening, and this is a speaking course. **Whatever
renders these bands must print that caveat beside them** — the report must never tell a learner
what their TOEIC score *is*. The ladder position is the tutor's call about speaking; the score
band is only what that position usually travels with. This is now the app's obligation, since
the app is what draws the card.

**Remaining volume** is the difference between the goal level and the current one. A tutor can
pick a goal below the current level (mis-tap, or a learner already past their own goal), so there
is a floor.

```
remaining lessons = max(6, DONE[goal Lv] − DONE[current Lv])
```

---

## 3. Duration — five-month floor

```
months = max(5, round(remaining lessons ÷ (per week × 4.3)))
```

- **4.3** = weeks in a month (52 ÷ 12).
- **Per week** comes from the 学習ペース answer the learner taps in the trial, which offers 1–5.
  The report the app draws carries a 1–7 slider so the number can be revisited later; the deck
  no longer has one, because the deck no longer shows the plan.
- **The five-month floor is sales policy, not arithmetic.** Plenty of combinations compute to two
  months (a near goal at 5×/week). Do not "fix" the formula to remove the floor — removing it
  removes the policy.
- When the floor binds, **the lesson count and the duration do not agree** — 45 lessons at 5×/week
  is arithmetically two months and we still say five. In Korean a tutor absorbs that question live.
  No one does here: the learner reads the plan alone, in the chat. So whatever draws the card has
  to answer it in print — the extra time is review and free talking.

Because the floor is five months and there are at most four stops, **the axis is always months.**

---

## 4. Which courses are recommended

Three inputs decide, in this order — **current level** (what is skipped), **goal** (how far), and
**motive** (what gets laid down). The sequence is always:

```
Core patterns  →  (Contextual, by motive)  →  (Freetalking)
```

**1) Level removes what is already behind the learner.**

| Course | Dropped when |
| --- | --- |
| Core patterns | Lv 8 or above (Core is complete by definition at Lv8) |

Korean drops two courses here; English drops one, because there is no 한글 track to drop.

**2) Motive picks the Contextual area.** The goal card sets distance only.

| 学ぶきっかけ | Course laid down |
| --- | --- |
| 仕事で使う | Contextual · Business |
| 海外出張・駐在 | Contextual · Business |
| 旅行 | Contextual · Travel |
| TOEIC・試験 | Freetalking |
| 自己啓発 | Freetalking |

Motives are multi-select, and **at most two contextual courses** are laid down; beyond that the
roadmap stops being an order and becomes a list. The first motive chosen goes **last**, because the
final stop is the destination and the report would otherwise name one goal and draw another.

> The five motives are work-weighted on purpose. English has five Business courses and five Travel
> courses and nothing else, so a motive that cannot reach one of those two reaches Freetalking.
> 「TOEIC・試験」 lands on Freetalking rather than on a study-skills course because none exists —
> what the curriculum can honestly offer an exam candidate is Core's grammar spine (always laid
> first anyway) plus volume of speech.

**3) A goal of Lv 8 or above always ends in Freetalking.** That height is not reached by stacking
more patterns; it is reached by volume of production. So the contextual courses drop to one and
the last stop goes to Freetalking.

If everything filters out, the last course is kept. **The recommendation is never an empty card.**

---

## 5. Where the stops fall

### Core is not a course you finish before starting

Same premise as Korean, and it matters more here: Core is 122 lessons spanning Pre-A1 to C1, but
the learner does **not** finish it before the interesting material starts. They take as much as
they need, move into Contextual or Freetalking, and **the rest of Core continues alongside.**

"As much as they need" is the entry floor from §1.

| Next course | Core needed first |
| --- | ---: |
| Contextual · Travel | 47 |
| Contextual · Business | 70 |
| Freetalking | 70 |

So the length Core occupies on the roadmap is **not 122 — it is "next course's entry floor minus
lessons already done."** Same level and same goal, different motive, different branch point.

> Lv 2 · goal Lv 7 · 3×/week → both are 9-month plans, but
> **Travel branches at month 3** and **Business at month 6**.

Only when Core is the last course (no Contextual, no Freetalking) does it count lessons all the way
to the goal level.

### Course lengths

| Course | Length | Source |
| --- | ---: | --- |
| Core patterns | **variable** | next course's entry floor − lessons already done |
| Contextual · Travel | 30 | 5 courses × 6 |
| Contextual · Business | 30 | 5 courses × 6 |
| Freetalking | 40 *(nominal)* | **Endless track.** A "this much at a time" figure, not a volume |

### A stop marks where a course *starts*

```
position of stop i = min(0.92, (lengths of courses 1..i−1) ÷ remaining lessons)
time of stop i     = total months × position of stop i
first stop         = 0    (now)
last stop          = 1.0  (arrival)
```

The denominator is **remaining lessons**, not the sum of course lengths. Dividing by the latter
inflates each earlier course when the courses behind it are short, which draws a learner with a
*lower* entry floor branching *later*. That has actually been shipped once, in Korean.

The last stop is not a course but the arrival: it carries the level reached, what that level does,
and the motive the learner picked at the start.

---

## 6. Where to change things

| What | Where |
| --- | --- |
| level → cumulative lessons | `report-en.js` → `DONE` |
| level names, CEFR, TOEIC band | `report-en.js` → `LV` |
| the five assessment areas | `report-en.js` → `AREAS` — **tutor-facing, so English** |
| goal card → arrival level | `report-en.js` → `GOALS` |
| motive → contextual course | `report-en.js` → `WHY_COURSE` |
| course names, lengths, artwork | `report-en.js` → `COURSE` |
| entry floors | `report-en.js` → `ENTRY` |
| the tutor's scoring copy | `report-en.js` → `submitText`, `missingLabel` |
| what the tutor actually sees | `tools/authoring/en/build_trial_decks.py` → `LEVEL_RUNGS`, `AXES` |
| duration, five-month floor | `report.js` → `months()` — **shared with Korean** |

`AREAS` is the one table that flipped language. In the Korean trial those names are printed in
the learner's report; here the report is not in the deck, so the only place they appear is the
tutor's scoring chips. The Japanese names the learner eventually reads belong to the app.

Everything else in `report-en.js` is data for the report the app draws. Do not fork `report.js`
— there is exactly one renderer, and the two products differ only by the tables handed to it.

## 7. Still open

- **podo-app does not implement this ladder yet.** Its English branch
  (`level-test-report-v2.tsx`) belongs to the *Korea-market* English product and recommends
  courses that do not exist in `courses/en/` — `alphabet`, `media`, `conversation`,
  `discussion` — on a CEFR-only scale. Both markets store `language: 'EN'`, so the app has to
  branch on `reportSnapshot.kind`; this product sends `podo-english-trial-report`.
- **The cohort averages in `AVG` are estimates, not measurements.** They shape the radar the
  app draws. Replace them once real numbers exist.
