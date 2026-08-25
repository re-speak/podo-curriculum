# Course cover generator

`generate.py` turns the current deployable catalog into 4:5 course covers. It is
the source of truth for layout, colour and course-to-motif routing; do not
hand-edit the generated `courses/*/*/assets/cover.{svg,png}` pairs.

```sh
python3 tools/authoring/course_covers/generate.py
python3 tools/authoring/course_covers/generate.py --check
python3 tools/authoring/course_covers/generate.py --only kr/hangul-starter
```

The check re-renders every PNG, compares it byte-for-byte, verifies 864×1080,
and enforces the repository's 2 MiB cover limit.

## The cover is designed at 144×180

That is the size the student app draws it — a 144 px card, `aspect-[4/5]`, in a
horizontal carousel (`apps/web/src/features/subscribes/ui/lesson-thumbnail.tsx`).
Everything in `generate.py` is authored as that size × 6, so a 10 px label on the
card is 60 in the file. **Compose against 144 px, not against the 864 px render.**
The layout this replaced was composed at full size and carried an eyebrow
(`KR · CORE`), a language pill (`KO`) and a footer track label that landed at 7,
5.3 and 5 px on the card — three labels for two facts, none of them readable.

What a cover says now, top to bottom:

| | |
|---|---|
| pill | `family [position] · level` — `ドラマ 2 · 中級`, `パターン 7 · 中上級`, `旅行 1 · 中級` |
| title | the topic, in the language the course teaches |
| motif | one glossy object, bottom-anchored, unchanged |

**Both corpora use the same shape and the same chrome language.** The pill is
support text, and both corpora serve the JP market (`countryCode: JP`), so it is
Japanese on a Korean cover and Japanese on an English one; the title beside it is
the language being taught. Writing the English chrome in English was the first
attempt and it does not fit — `Upper Intermediate` alone is most of the 120 px a
pill has, and `Business 4 · Upper Intermediate` overflows by a third. `中上級` is
three characters, and it is the word on the filter chip a JP learner is reading.

The rail header above the carousel already names the track, so the pill names the
thing inside it that the header does not. A family that runs in a fixed order
carries its position — the core ladder, `ドラマ`, `K-POP`, `タメ口`, and the
English travel and business runs, which go A2 to C1 by `classLevel`. Korean
travel does not, because 식당 · 쇼핑 · 숙소 · 길 are four places on one trip
rather than four steps.

**The level word comes from `difficulty`, through `LEVEL_WORD`.** Those five
words are copied from podo-app's own level filter
(`apps/web/src/shared/config/i18n/messages/ja.json`,
`subscribeList.filters.level.*`), so the cover, the line under it and the filter
chip cannot disagree. It is also why CEFR is gone from the covers: `A2–B1` and
`B1+` are not buckets the filter has, so a course carrying one could not be
filtered to the level it claimed.

**The pill is sized from real font metrics.** `_ASCII_EM` holds Pretendard Bold's
advance widths, measured once and baked so this file needs no font library. A
guessed ratio is not good enough — estimating a space at .42 em when it is .23
is what made the pill stop hugging its text. There is no minimum pill size: the
pill fitting inside the card is the invariant, and a pill that would have to
shrink to fit is a label that is too long.

## Colour is a table, not a hash

Every fill is one solid colour, and every group of courses that belongs together
shares it. Nothing is a gradient of anything — a course and its neighbour differ
because they *are* different, not by a shade.

- **`CORE_BAND`** — one fill per level band, walking 148° → 180° → 208° → 240° →
  292° and deepening at each step. Hue says which band, depth says how far up.
- **`FAMILY_FILL`** — one fill per contextual sub-family. Set by hand, because a
  family's members use several different motifs and so have no single artwork to
  read a colour off.
- **`TALK_FILL`** — one fill per freetalking topic, the same at both levels.

## The computed fills

`TALK_FILL` and the `hangul` entry are derived from the artwork rather than
chosen. `measure_motifs.py` reports, per motif, its own colours — one per hue bin
it actually spends area on, weighted by saturation × lightness so highlights and
outlines do not vote — and the mean lightness of its opaque pixels.

```sh
python3 tools/authoring/course_covers/measure_motifs.py          # what it measured
python3 tools/authoring/course_covers/measure_motifs.py --fills  # the table to paste back
```

**The ground echoes the artwork.** It takes the artwork's own strongest colour and
deepens it until the object separates on lightness rather than on hue — a pink
phone on deep wine, a blue clock on teal, a green Hangul block on deep green.
Five of the seven hand-set `FAMILY_FILL` entries had already landed there by eye,
which is why drama, business and travel read as cohesive and nobody asked about
them.

How deep is not a taste call either: it comes from the object. The dark briefcase
of `work-money` averages 0.45 lightness and gets a light ground; the pale phone of
`romance` averages 0.81 and gets a much deeper one. That single rule is what lets
an echo stay an echo without the object dissolving into it.

Two things can stop an echo, and then the ground steps to the artwork's *next*
colour rather than to an unrelated one:

- **Mud.** Hues from about 9° to 94° turn to brown or olive once they are deep
  enough to hold white text, so a yellow lightbulb cannot have a yellow ground.
  It takes the purple of its own question marks instead — still a colour from the
  picture.
- **A sibling.** Two courses cannot ship the same fill, and the toy artwork is
  mostly blue and purple, so echoes cluster. They fan out *inside* the
  neighbourhood the artwork put them in: a band of four blues becomes four blues
  about twenty degrees apart, not a blue and a green. No fill currently moves more
  than 28° off its own artwork.

An earlier version did the opposite — it put each ground as far from its artwork
as CIE Lab allowed. That solved a real problem (a green ground behind green globes,
which 45° of hue clearance had let through) but it solved it by throwing away the
thing that made the hand-set fills work. Echo plus the depth rule handles both.

The table is committed rather than computed at generation time for two reasons:
`generate.py` stays free of a Pillow dependency (it only needs `rsvg-convert`),
and a reviewer can see the hues in the diff instead of trusting a measurement
they cannot see. Re-run `--fills` and paste when a motif PNG changes.

## The motifs

The motif PNGs were generated with the built-in image-generation tool. Every
prompt used the Figma six-object sheet (file `8ExQz3JLMk1cLAxgFDDA75`, section
`1367:5422`) as a style reference and this shared frame:

> A single compact course-cover object group in the reference's friendly
> dimensional vector / soft-3D molded-plastic style, with soft gradients,
> glossy highlights, a strong silhouette, generous transparent margin, no
> readable text, no logo, no watermark, and a genuinely transparent
> background.

The subject prompts, which are the repeatable prompt set, are the motif
filenames: Hangul blocks; interlocking pattern tiles; K-pop light stick and
headphones; romance phone and heart chats; travel suitcase/passport/pin;
dining cup/plate/fork; shopping bag/card; lodging key/pillow; business
laptop/chart; freetalk microphone/cards; X/O balance; two-country bridge;
work briefcase/coins; thinking light bulb; memories photos/clock; linked
people; and a what-if crystal ball.

Two motifs are shared by more than one live course inside the same family —
`people` covers both `친구` and `가족 & 일상` — which the old hash colouring hid
by accident. It is a routing gap, not a colour one, and it wants another piece of
art rather than another shade.
