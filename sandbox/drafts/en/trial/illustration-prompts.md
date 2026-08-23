# Artwork still to draw — English trial

The English trial reuses the Korean trial's art wherever the picture means the same thing
(the ten level illustrations, the five assessment-area icons, the PODO characters). This file
lists only the pictures that are **missing or standing in for something else**, so nobody has to
diff two asset folders to find out.

The rule the deck follows is in `shared/ux-philosophy.md`: one picture means one thing. A course
or motive with no picture of its own falls back to a `✓` on purpose (`doMark()` in `report.js`) —
that is the correct empty state. Filling it with a borrowed picture is worse than leaving it,
because it breaks the promise for every picture that *is* right.

## 1. `reasons/assign.png` — 海外出張・駐在 · **currently a duplicate**

**This is the one real defect in the current asset set.** The motive list has six rows and five
honest icons; `assign` is presently a byte copy of `reasons/work.png` (the brown briefcase), so
two rows in a six-row chooser look identical.

Both rows genuinely are about work, and their labels are unambiguous, so the deck is usable — but
a chooser whose rows differ only in text is exactly the failure `ux-philosophy.md` describes under
*Several questions must look like several questions*.

> **Prompt** — 3D rendered icon, 512×512, transparent background, soft studio lighting, matte
> plastic finish, same family as `reasons/work.png` and `reasons/travel.png`. A brown briefcase
> with a small pale-blue paper aeroplane banking away from it, or a briefcase with a boarding
> pass tucked under the handle. It must read as *work that travels* at 40px, and must not be
> confusable with the orange suitcase (`travel.png`) or the plain briefcase (`work.png`).

## 2. Course scene photographs — deliberately absent

The Korean report lays three scene photographs behind the sample dialogue of each contextual
course (`.pic-src`, `art.pics`). The English `COURSE` entries in `report-en.js` carry **no**
`pics` and no `face`, so those cards fall back to the plain two-turn dialogue with the neutral
role icon.

That is the intended state for now, not an oversight. The Korean photographs are of Korean
scenes; borrowing them would put a Seoul street behind an English travel course. When English
scene photography exists, add `pics: [...]` to the `travel` and `business` entries and a matching
`.pic-src` block in each deck.

## 3. Course icons — two of four are `✓`

| Course | Icon | Where it comes from |
| --- | --- | --- |
| `core` | `course-icons/ic-core.png` | reused — the picture is a generic pattern card |
| `free` | `course-icons/ic-free.png` | reused — generic speech bubbles |
| `travel` | `reasons/travel.png` | the course *is* the motive, so it borrows the motive's icon by design |
| `business` | `reasons/work.png` | same — the course is the motive |

`ic-goal.png` is the arrival marker on the last roadmap stop. Nothing here needs new art; the
table is recorded so the next person does not "fix" the two borrowed ones.
