# The report viewer

`shared/view/report.html` — the trial report, opened outside the lesson room.

## Why it exists

The report is read twice. During the lesson the tutor and the learner read it
together on the deck; afterwards the learner opens it again in the app. Those have
to be the same document, and for a while they were not: podo-app carried its own
React re-implementation of the report, written from the Korean deck a week before
the English trial existed. The English half of it was therefore assembled from the
*Korea-market* English level test — a different level ladder, different course
list, a CEFR band that contradicted the deck's, and a goal map that read `t7` as
Lv.7 where English means Lv.8.

None of that was careless; it is what happens when one document has two
implementations and nothing compares them. So there is one implementation now, it
lives here with the tables it draws from, and the app embeds it.

## Contract

The host loads the viewer in an iframe and posts the stored snapshot in:

```
…/<runtime-tag>/view/report.html?lang=KR      Korean trial   (report-ja.js)
…/<runtime-tag>/view/report.html?lang=EN      English trial  (report-en.js)
```

`lang` is `le_level_test.language`, unchanged — the app already holds that value,
and renaming it in transit would create one more table to keep in step. `KO` is
accepted as the legacy spelling of `KR`.

| direction | message |
|---|---|
| viewer → host | `{source, type: "ready"}` — runtime loaded, send the snapshot |
| host → viewer | `{source, type: "render", requestId, snapshot}` |
| viewer → host | `{source, type: "rendered", requestId, ok, error?}` |
| viewer → host | `{source, type: "height", height}` — on every change |

`source` is `"podo-trial-report"`, the same constant `report-submit.js` uses to
send a report *out*. One report, one channel name, two directions.

The viewer replies only to the window that asked, at that window's origin. It does
not filter who may ask: it renders what it is handed and reads nothing of its own,
so an unknown embedder can only show itself its own data. Deciding that an iframe
really is the runtime is the host's job, not something the iframe can assert.

The snapshot is `podoReport.snapshot()` as stored in `le_level_test.report_snapshot`
— inputs only. Everything printed is recomputed here from the same tables the deck
used, which is the point: no stored result that can disagree with the tables.

## What restore() does that first-draw does not

- **Stamps `capturedAt`, not today.** A report reopened next week is still the
  record of the day it was made.
- **Locks the pace slider** (`body.report-view`). The number above it was agreed in
  the consultation; letting it move afterwards would silently change the plan.
- **Takes `plan.perWeek`, not `answers.pace`.** Those differ when the tutor and the
  learner settled on something other than the needs-page answer, and the plan is
  the later of the two.

## Keeping it from drifting again

`shared/view/report.html` is generated. `tools/report-viewer.py` lifts the
`.rep-page` block out of the shipped decks, drops the tutor-only blocks, and
rewrites runtime URLs to paths relative to the tag the viewer is published under.
`--check` runs inside `validate.py`, so a deck edit that leaves the viewer behind
fails the build rather than reaching a learner.

Two things the decks own are mirrored into the locale tables so the viewer can draw
them without carrying the tutor's controls:

- `BAND` — the five `.axq` `data-say` lines, which become the ✓ lines on the level
  card. These are product-specific in exactly the way that matters: Korean says
  「助詞と語尾」 where English says 「時制や冠詞」.
- `text.headline` — 「あなたの韓国語の実力を」 / 「あなたの英語の実力を」.

`report-viewer.py --check` compares both against the decks.

## Published runtime

The viewer cannot run directly from jsDelivr: repository HTML is returned as
`text/plain` with `X-Content-Type-Options: nosniff`. `publish-shared.py` therefore
publishes the complete versioned `shared/{view,css,js,assets}` tree to the GCS
mirror configured in `curriculum.yaml`. Keeping the complete tree together is
required because the generated viewer deliberately uses relative runtime URLs.
An existing version is byte-compared and never overwritten.

## Known, not fixed here

The report header reads 「体験レッスン・25分」 in every deck. That is right for the
English trial and wrong for the Korean one, which is 55 minutes
(`GT_CLASS_COURSE.LESSON_TIME`). It is deck copy, so the fix belongs in the draft
under `sandbox/drafts/kr/trial/` and a re-promotion — not in a generated file. The
viewer reproduces the deck faithfully, including this.
