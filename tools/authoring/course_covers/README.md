# Course cover generator

`generate.py` turns the current deployable catalog into 4:5 course covers. It is
the source of truth for layout and course-to-motif routing; do not hand-edit the
103 generated `courses/*/*/assets/cover.{svg,png}` pairs.

The visual grammar comes from Figma section `1367:5422` in file
`8ExQz3JLMk1cLAxgFDDA75`:

- 288×360 source art displayed at 144×180 in the catalog;
- 8 px catalog corner radius;
- Gmarket Sans Bold/Medium in the reference, mapped to the installed
  Pretendard family for complete Japanese, Korean, and Latin coverage;
- measured fills `#69CD73`, `#7637E0`, `#EE6619`, `#F37297`, `#1A2D5E`, and
  `#F0473D`;
- white title, 70%-white secondary copy, a quiet oversized backdrop mark, and
  one glossy toy-like object anchored low/right.

The motif PNGs were generated with the built-in image-generation tool. Every
prompt used the Figma six-object sheet as a style reference and this shared
frame:

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

Run:

```sh
python3 tools/authoring/course_covers/generate.py
python3 tools/authoring/course_covers/generate.py --check
```

The check re-renders every PNG, compares it byte-for-byte, verifies 864×1080,
and enforces the repository's 2 MiB cover limit.
