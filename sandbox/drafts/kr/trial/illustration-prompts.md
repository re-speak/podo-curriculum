# Illustration prompts — trial deck curriculum pages

The curriculum pages currently use inline SVG (route map, cards). If we want real
illustrations, these prompts are written to match the existing art (mascot, mouth
diagrams, the praise stamp) so a new piece drops straight into the deck.

**The art keeps its bold outlines even though the page chrome no longer has any.** That is
deliberate, not a leftover: illustration is a separate layer from UI, sticker-like art reads
well on quiet cards, and softening it would orphan every asset already drawn. Do not "update"
these prompts to match `lesson-card.css`.

## Style block — prepend to every prompt

> Flat vector illustration, bold 3px black outlines, no gradients, no shadows except a
> hard offset black shadow. Palette strictly: black `#1C1C1C`, lime `#B5FD4C`, mid-green
> `#6ABE36`, pale green `#F2FCEC`, white, warm grey `#F5F5F5`. Rounded geometric shapes,
> generous white space, sticker-like. Friendly and confident, not childish. Square-ish
> composition, transparent background, no text or lettering anywhere in the image.

**Why "no text":** all copy is live HTML so it stays translatable and searchable. Art that
bakes in Korean or Japanese words can't be reused across the JP and KO versions.

---

## 1. `p-curri` — 커리큘럼 지도 (hero)

> A winding path climbing from the bottom-left to the top-right of the frame, with four
> milestone markers along it. Marker 1 at the base is a single letter block; marker 2 is
> three blocks forming a short sentence; marker 3 is a signpost pointing four ways;
> marker 4 at the summit is a small flag on a rounded hilltop. The path is lime, thick and
> rounded. Empty rolling hills behind in pale green.

Replaces or sits above the current SVG route.

## 2. `p-spine` — 한글 읽기

> Two puzzle-like rounded tiles snapping together into one square block, shown mid-motion
> with small motion ticks. The left tile is amber-yellow, the right is pink, the joined
> block sits on a white card with a hard black shadow. Simple, iconic, no faces.

Note: amber `#FFEEB8` / rose `#FFD7E5` are the deck's consonant/vowel seat colours — keep
them exactly so the illustration matches what the learner just did in the lesson.

## 3. `p-spine` — 핵심 패턴

> A stack of rounded blocks forming a staircase of five steps rising left to right, each
> step slightly larger than the last, with a small lime flag on the top step. A dotted
> guide line runs under the steps. Clean, architectural, no characters.

Sells "each lesson stands on the previous one" without words.

## 4. `p-world` — 상황별 한국어 (set of four icons, one prompt each)

Generate as **one 2×2 sheet** so the four share weight and line thickness.

> Four flat icons in one square 2×2 grid, evenly spaced, identical line weight:
> (top-left) a film clapperboard; (top-right) a handheld microphone with a small heart;
> (bottom-left) a paper aeroplane over a folded map; (bottom-right) two overlapping speech
> bubbles. Each icon sits on its own rounded white card with a black outline and a hard
> black offset shadow. Lime accents only.

Replaces the emoji currently used (🎬 🎤 ✈️ 💬), which render inconsistently across
devices and look out of place next to the drawn UI.

## 5. `p-free` — 프리토킹

> An open circular loop with no endpoint — a ring drawn as a rounded lime ribbon that
> fades out at one end, with small floating rounded speech bubbles orbiting it at
> different sizes. Suggests something ongoing rather than finished. No text.

## 6. `p-about` — 포도 수업 (optional warmth)

> A tutor and a learner as two simple rounded silhouettes facing each other across a
> tablet, seen from the side, connected by a lime speech ribbon that loops between them.
> Neutral, no facial detail, no ethnicity cues beyond neutral shapes.

Keep faceless — the lessons are audio-only, so art showing a visible face would promise
video we don't deliver.

---

## Delivery notes

- **Format:** SVG if the tool can produce it; otherwise PNG at 1024×1024 with a
  transparent background.
- **Where they go:** `korean/0-trial-class/art/` alongside `mouth/`.
- **Sizing:** the deck column is 480px wide with ~380px of usable width, so anything
  finer than a 3px stroke at that scale disappears.
- **Check before shipping:** view at 480px width, not full size. Most illustration detail
  that looks good at 1024px turns to mush in the card.

---

## What actually shipped (July 2026)

The four thin curriculum pages were merged into one long `#p-curri`. Art in use:

| File | Where | Note |
| --- | --- | --- |
| `p-curri.png` | hero at the top of the page | as prompted |
| `w-drama / w-kpop / w-travel / w-talk .png` | the four world rows | **sliced** from `p-world.png` (each 512px quadrant → 256px) |
| `p-free.png` | stage 4 | as prompted |
| `p-about.png` | unused so far | candidate for `#p-about` |

**Not used — `p-spine-hangul.png`:** the generator dropped the amber/rose seat colours and
returned a black-and-white puzzle icon, so it no longer matched the lesson the learner had
just done. The stage-1 visual is built in HTML instead (`.lt` / `.sq`), which is strictly
better here — it reuses the real seat variables, so it can never drift from the lesson.

**Not used — `p-spine-patterns.png`:** the staircase sells "it builds up", but stage 2 needed
to show *how a pattern works*, not that it gets harder. The live `.sent` / `.swaps` demo
(swap one word, keep the frame) does that; a picture can't.

**Lesson for future prompts:** anything whose job is to explain a *mechanic* should be built
in HTML, where it stays in sync with the design tokens. Reserve generated art for mood and
for objects (icons, scenes) that carry no teaching load.
