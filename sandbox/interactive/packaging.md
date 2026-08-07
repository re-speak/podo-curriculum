# Packaging a lesson for lemonboard

How a lesson HTML file becomes something the 교재 admin can upload.

```sh
python3 interactive/build_lemonboard.py <deck>.html --out trial/lemonboard-build/<deck>
```

That produces `lesson.html`, `lesson.css`, every image, and a `.zip` of all three.

**One output folder per deck.** `lesson.html` and `lesson.css` are fixed names, so two
decks built into the same `--out` overwrite each other's preview and pile their images
into one directory (the zips survive; nothing else does). Give each deck its own folder
named after it — `trial/lemonboard-build/trial-1-hangul-short/`, `…/trial-2-patterns-short/`.
That folder is git-ignored on purpose: a committed zip goes stale the moment a shared
module changes, and the whole point of the shared modules is that they change.
Upload the zip in grape admin → 교재 등록/수정 → **html로 생성하기**, into the 수업용 and/or
예습용 slot. The same zip works in both.

## What the upload slot actually does

Grape (`admin/system/class_course/process/class_course_ps.php`) unpacks the zip to S3
under `lemonboard-html/{교재ID}/`, **flattening every entry into that one prefix**, and:

- renames the **first `.html`** and **first `.css`** it finds to `lecture.*` (수업용) or
  `prestudy.*` (예습용);
- **rewrites the stylesheet reference for you** — it replaces the css file's basename
  throughout the HTML with the slot's name, so one `<link>` is correct in both slots;
- uploads **every other entry under its basename** with a real content type — png, jpg,
  gif, svg, webp, mp3, woff, woff2, js, json are all mapped.

Three things follow, and the build script handles all three:

**One CSS, not two.** Decks load `runtime/css/lesson-card.css` plus the track's own sheet. They are
concatenated *in link order* so the cascade is unchanged, and any `@import` is hoisted to
line 1 where CSS requires it.

**One `<link>`, with a neutral name.** The script emits `lesson.css` and grape renames it
per slot. The output is also directly viewable in a browser, because the file on disk has
the same name the link points at.

**Images ride inside the zip.** Because the unpack flattens folders, `src="mouth/a.png"`
is rewritten to `src="a.png"` and `a.png` is added to the zip. **Basenames must be unique
across folders** — a collision is a hard error rather than a silently overwritten image.

## Remote references

The packager only bundles **local** files. A `<link>` or `src=` pointing at an absolute URL
is left exactly as written and listed in the build's `NOTE` line, so a deck can pull its
stylesheet, its scripts or its images from a CDN without the script fighting it. That is a
deliberate seam: shared code hosted once is fixed once, instead of being re-packaged into
every deck that already shipped.

## The build refuses to ship silent breakage

Only one spelling of each reference is rewritten: `<link rel="stylesheet" href="…">` in that
order with double quotes, and `src="…"` lowercase with double quotes. Anything else — `srcset`,
`src='…'`, `SRC=`, an href-first `<link>`, a `url()` inside CSS or a `style` attribute — would
be neither bundled nor rewritten, and would 404 from S3 while the build looked fine.

So the packager audits the output and **exits with an error** listing exactly what it found.
If you hit one, use the supported spelling rather than working around it.

## Gotchas

- **Reserved asset names.** `lesson.*` collides with the merged output, and `lecture.*` /
  `prestudy.*` are uploaded *after* the css, so they would overwrite the lesson at its S3 key.
  The script refuses to build if an asset uses one.
- **A local `@import` is not bundled** and the build fails rather than emitting a 404. Inline
  the file into one of the linked stylesheets instead.
- **HTML comments are scanned too.** The rewrites work on raw text, so an `<img src="…">`
  written inside a `<!-- -->` as an example still counts as a reference — and the build stops
  with "referenced images not on disk" if that example points at a file you haven't made yet.
  Put sample markup in a `.md` next to the asset instead of in the deck.
- **Re-run the build after any edit.** The zip is a snapshot; editing the source deck does
  not change an already-uploaded 교재.
- **HTML format skips the PDF pipeline entirely.** No page images and no lemonboard room
  pages are generated — the board loads your HTML directly. Admin allows one HTML 교재 per
  course.

## Files here

| File | What it is |
|---|---|
| [`interaction-protocol.md`](./interaction-protocol.md) | the `data-sync` contract — read before adding interactions |
| `build_lemonboard.py` | this packager; works on any deck in the repo |

Four shared add-ons drop into any deck with one `<script src>` line each. They register
their own kind, so none of them needs a lemonboard change; each is symmetric (either
person can use it) except where noted, and each falls back to doing nothing when the file
is opened outside the board. Their styling lives in `runtime/css/lesson-card.css`.

| Script | What it adds |
|---|---|
| `spotlight.js` | tap a block to ring it on both screens — "look here", one at a time. Stepping into a text box rings the block around it, so the other person can see which question is being answered |
| `highlight.js` | drag over text to leave a marker stroke on both screens; tap a stroke to erase it |
| `tutor-notes.js` | one free-typing note per page — invisible until the tutor writes in it, then read-only for the learner |
| `stamp.js` | the 참! 잘했어요 praise stamp |

Load order matters in two places: `tutor-notes.js` must come after the pager (which counts
`.phone` children as pages), and `highlight.js` after the ja→ko tooltip script (which reads
text nodes at load).
