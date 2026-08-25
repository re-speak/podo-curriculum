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
| pill | the sub-family and the level — `ドラマ 1 · 中級`, `初級パターン 1`, `Business · B2` |
| title | the topic, in the language the course teaches |
| motif | one glossy object, bottom-anchored, unchanged |

The rail header above the carousel already names the track, so the pill names the
thing inside it that the header does not. A family that runs in a fixed order
(`드라마`, `케이팝`, `반말`) carries its position; `여행` does not, because
식당 · 쇼핑 · 숙소 · 길 are four places on one trip rather than four steps.

The level word is read out of `spec.title` rather than derived from `difficulty`,
so the cover and the line under it can never disagree.

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
python3 tools/authoring/course_covers/measure_motifs.py
```

Each fill is then the colour **furthest from that artwork's own colours in CIE
Lab**, at a depth set by how light the object is: the dark briefcase gets a light
ground, the pale phone a deep one. That second half is what keeps a pale object
from dissolving into a pale ground.

The distance has to be perceptual. The first version of this compared hue angles
and required 45°, and it produced a green ground behind the green-and-blue globes
of `countries` — 51° apart on paper, the same colour to look at. Greens sprawl
across 90–170° and still read as one thing; Lab says so and hue arithmetic does
not. The floor is now ΔE 45, below which the ground starts to swallow the object,
and every fill in the table clears it.

Two guards sit on top. Hues from about 9° to 94° turn to mud once they are deep
enough to hold white text — orange becomes brown, yellow becomes olive — so they
are only used when nothing else clears the floor. And each fill is also scored
against the fills already assigned, so two topics on the same rail stay tellable
apart once both have cleared their own artwork.

The table is committed rather than computed at generation time for two reasons:
`generate.py` stays free of a Pillow dependency (it only needs `rsvg-convert`),
and a reviewer can see the hues in the diff instead of trusting a measurement
they cannot see. Re-run `measure_motifs.py` and update the table only when a
motif PNG changes.

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
