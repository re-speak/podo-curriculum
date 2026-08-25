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
| viewer → host | `{source, type: "render-complete", requestId}` — fonts, images and final layout are stable |

`source` is `"podo-trial-report"`, the same constant `report-submit.js` uses to
send a report *out*. One report, one channel name, two directions.

The viewer replies only to the window that asked, at that window's origin. It does
not filter who may ask: it renders what it is handed and reads nothing of its own,
so an unknown embedder can only show itself its own data. Deciding that an iframe
really is the runtime is the host's job, not something the iframe can assert.

The host selects only `capturedAt`, `answers`, `assessment`, and `plan` from the stored
snapshot. The viewer needs no student identity, deck metadata, or other report fields.
Everything printed is recomputed here from the same tables the deck used.

The host embeds the page with `sandbox="allow-scripts"` and no `allow-same-origin`.
That gives the document an opaque origin, blocks navigation/forms/plugins, and makes a
nested frame structurally unable to impersonate the direct iframe window. The host
accepts messages only from that exact `contentWindow` with the opaque `null` origin.

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

## Why the 項目別診断 headings are nouns

The two headings used to be verdicts — 「よくできています！」 and 「もう一歩です！」 — and
both wrapped on every phone. 「よくできています！」 is 132px of text where the heading
box offers 82px at a 360px viewport and 98px at 393px, so it broke mid-word into
「よくできてい／ます！」. The chips under it used to break the same way; that was a layout
bug and `trial.css` fixes it. The headings could not be fixed the same way, because the
deficit is 50px and every margin worth shaving on that row adds up to about 15px: report
page padding 20→16 (+4), card 20→16 (+4), box 12→10 (+4), icon gap 4→2 (+2). Buying the
rest would narrow every other card on the page.

So it was a copy question, not a CSS one. Measured at the shipped 16px/800/-.02em:

| heading | width | one line from |
|---|---:|---|
| よくできています！ | 132px | 480 only |
| もう一歩です！ | 105px | 430 |
| のばすところ | 88px | 375 |
| **いいところ** | **73px** | **every width** |
| **改善点** | **47px** | **every width** |

「いいところ」／「改善点」 is the shipped pair. Both stand on one line from 360px up with the
icon beside the words, so neither box gains height and the two boxes stay the same height —
which matters, because they sit side by side and the chips start under the heading.

**The verdict wording is what forced the branch, and the branch is what forced the
wrapping.** A verdict can be false: when the learner's *best* axis is still below the
average line — always true of a beginner whose top axis is Lv.1~2, the most common trial
result — 「よくできています！」 is not a true sentence, so the heading had to swap to
「いちばん強いところ」, and the mirror case (a learner whose weakest axis is already above
average) had to swap to 「もっと伸ばせます」. Those replacements were nine and eight
characters, so the most common report got the widest heading.

A noun names what is in the box instead of judging the learner, and a name cannot be
false in either direction. That removes the reason the swap existed, so `renderAspects()`
sets one heading per box unconditionally and there is no second pair of strings to keep
inside the width.

Like the header below, this is deck copy. It lives in the four decks under
`sandbox/drafts/kr/trial/full-trials/` and reaches the viewer through a re-promotion and
`report-viewer.py` — not by editing a generated file. The two strings are also in the
locale tables (`report-ja.js`, `report-en.js`) as `goodTitle` / `weakTitle`, because the
runtime rewrites the heading on every render; the deck markup and the table have to agree.
The older prototypes under `sandbox/drafts/kr/trial/reports/` still carry the original
Korean wording and are not promoted.

## Known, not fixed here

The report header reads 「体験レッスン・25分」 in every deck. That is right for the
English trial and wrong for the Korean one, which is 55 minutes
(`GT_CLASS_COURSE.LESSON_TIME`). It is deck copy, so the fix belongs in the draft
under `sandbox/drafts/kr/trial/` and a re-promotion — not in a generated file. The
viewer reproduces the deck faithfully, including this.
