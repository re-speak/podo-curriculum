# references

Planning and source material. Never deployed, never packaged.

**One directory per subject language**, named with the same code as
`courses/<code>/` — `kr` is the Korean curriculum, `en` the English one. The code
is the subject being taught, not the market: English for Japan-market learners is
`en` here and `countryCode: JP` on the course.

That split is not filing tidiness. Both languages number their tracks from 1 and
both keep them in `tracks/*/table-of-contents.md`, so a shared directory would
have `2-core-patterns` mean two different things — and a re-sync would resolve it
by whichever language ran last, without saying so.

## kr — Korean

| Path | What it is |
|---|---|
| `kr/tracks/` | the five track table-of-contents plans — the curriculum design these courses are built from. Each track also carries its `toc/` shards and its `lesson-blueprint.md` |
| `kr/curricula/` | derived pattern maps, clean text and page wireframes from the textbooks we studied — できる韓国語, 세종한국어, K-Village, TEMO |
| `kr/reports/` | screen captures of other services' learner reports — Mobbin, uphone — used to design the 체험 리포트 |

## en — English

Being built. No course ships from it yet; the plan lands here first.

| Path | What it is |
|---|---|
| `en/tracks/` | the four track plans — core patterns, contextual English, freetalking, pronunciation |
| `en/reference/` | the design record: teaching philosophy, the source hierarchy the curriculum is drawn from, the grammar coverage map, and the JP-L1 difficulty inventory that sets what is hard for these learners |

## Where it comes from

Mirrored from `podo-curriculum-public/{korean,english}` by
`tools/sync-from-authoring.py`. That tree is the upstream; re-syncing replaces
these directories wholesale, so **edit them there, not here.**

**The textbook scans themselves stay upstream.** 41 PDFs and the
`dekiru-kankokugo/page-images/` directory come to 726MB of the 1.0GB in
`korean/references/curricula`. They are licensed source material, they are large,
and nothing in the build reads them — only the derived markdown and the wireframe
PNGs are mirrored here.
