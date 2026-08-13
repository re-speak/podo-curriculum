# sandbox

Experiments, half-built decks, design variants, anything not yet a course.

**Nothing here can deploy.** `tools/model.py` discovers courses by walking
`courses/` and nothing else — there is no flag that widens it. So this is not a
convention you have to remember; an experiment cannot reach production by being
renamed or copied into the wrong place.

It *is* committed, on purpose. Experiments that only exist on one laptop can't be
reviewed, referred back to, or picked up by someone else.

| Path | What it is |
|---|---|
| `trial/` | the 체험수업 decks as authored — `lessons/` (the short decks that became `courses/kr/hangul-trial-test`), `full-trials/`, `reports/`, `assets/`, `lemonboard-build/` |
| `track-samples/` | one sample lesson per track, under the subject-language code — `kr/` today; `en/` appears when the English tracks grow one |
| `interactive/` | the authoring tree's own packaging and interaction-protocol notes, plus its lemonboard build script |
| `archive/` | superseded versions and design-variant explorations |

`trial/`, `track-samples/` and `interactive/` are mirrored from
`podo-curriculum-public`. That tree is the upstream and re-syncing replaces them
wholesale — edit them there, not here. `archive/` is this repo's own.

`trial/` and `interactive/` are Korean's alone and carry no language code, unlike
`track-samples/` and everything under `references/`. Korean is the only language
with a 체험 tree upstream, and `import-trial-decks.py` and `import-report-deck.py`
both address these paths directly. A second language growing a 체험 tree needs
them namespaced first — see the docstring in `tools/sync-from-authoring.py`.

**`trial/lessons/` is the unflattened original of a deployed course.** The copies
under `courses/kr/hangul-trial-test/` are not the same files: they share one
`runtime/` here and are self-contained there, and their input controls are
written into the markup rather than built at load. Read
[`../CLAUDE.md`](../CLAUDE.md) on `data-sync` before assuming the two are
interchangeable.

Promote something by moving it into `courses/<lang>/<course>/lessons/<NN-slug>/`
and giving it a `lesson.yaml`. That move is the promotion — there is no flag to flip.

## viewers/

`deck-index.html` (upstream's `korean/index.html`) and `viewer.html` browse decks
by relative path. **All 31 of deck-index's links are dead here.** They address the
upstream `tracks/…` layout, and this repo splits that content three ways —
`courses/`, `sandbox/track-samples/kr/`, `references/kr/`. The sync repoints `runtime/`
refs so the mirrored *decks* render; it does not rewrite this index, because
there is no single directory left for it to point at.

Use it upstream, or repoint it at `courses/<lang>/<course>/lessons/` if it turns
out to be worth having here.
