# sandbox

Where lessons are written, and the reason a draft cannot reach a learner by accident.

**Nothing here can deploy.** `tools/model.py` discovers courses by walking
`courses/` and nothing else — `sandbox/` is not kept out by an exclusion list that
could drift, it is simply never reached. A draft becomes deployable only by being
named in a `promotion.yaml` and promoted into `courses/<language>/`.

## `drafts/`

The complete curriculum under authoring. This tree **is** the source. Authoring
moved into this repository on 2026-08-19 and `sync-from-authoring.py` was deleted
with the move rather than deprecated; `podo-curriculum-public` is now a frozen
archive holding only the licensed textbook scans, and nothing syncs from it.

| Path | What it is |
|---|---|
| `drafts/kr/tracks/` | Korean curriculum: TOCs, generated briefs, blueprints, course plans and lesson HTML |
| `drafts/kr/trial/` | Korean trial decks and reports, plus the illustration assets the tracks borrow |
| `drafts/en/tracks/` | the same tree for English |
| `drafts/en/{catalog,reference}/` | the English catalogue pages and the audits behind the course cut |
| `drafts/{kr,en}/*.md` | the authoring contract for that language — read `AGENTS.md` before writing a deck |

The language code is the subject being taught, matching `courses/kr/` and
`courses/en/`. It is not the learner market: Japan-market English is `en` here and
carries `countryCode: JP` in its `course.yaml`. That country code is what keeps it
clear of the Korea-market English catalogue grape already holds under the same
`LANG_TYPE` — both are `PODO`/`EN`, and only `COUNTRY_CODE` separates them in the
natural key.

## From a draft to a course

A course draft is a directory holding `course.yaml` and
`lessons/<NN-slug>/lesson.html`. `promotion.yaml` sits beside them and names what
ships — that manifest is the reviewable part of a promotion.

```sh
python3 tools/authoring/kr/check_structure.py     # while writing
python3 tools/make-promotion.py --lang en         # derive promotion.yaml from the decks
python3 tools/promote.py --check                  # what would ship
python3 tools/promote.py                          # write courses/
python3 tools/repoint-shared.py && python3 tools/validate.py
```

**Promotion copies; it does not move.** A draft stays here after it ships and
remains the thing you edit. `promote.py` clears and rewrites
`courses/<lang>/<slug>/lessons/` on every run and never writes to `sandbox/`, so
promoting twice gives the same tree and fixing a typo is: edit the draft, promote
again.

Adding a lesson to a course that already shipped is the same motion — write the
deck under the draft's `lessons/`, regenerate the manifest, promote. `week` is the
lesson's position in the manifest and must run 1..N with no gaps, because
`CLASS_WEEK` is contiguous.

`promote.py` will not create `courses/<lang>/<slug>/course.yaml`; the target course
has to exist first. That is deliberate — a course's identity (`classLevel`,
`lessonTime`, `countryCode`: the natural key grape matches a row by) and its
`enabled` flag stay a human act. `tools/make-promotion.py --scaffold-target` copies
the draft's `course.yaml` into place for a course that has none, and refuses if the
draft is already `enabled: true`.

## `archive/`

Superseded decks and design-variant explorations. Nothing reads it; it is kept so a
direction that was tried and dropped can still be found.
