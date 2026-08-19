# sandbox

The non-deployable review boundary between authoring and a real course.

**Nothing here can deploy.** `tools/model.py` discovers courses by walking
`courses/` and nothing else. Content becomes deployable only through an explicit
promotion into `courses/<language>/` after review.

## `authoring/`

`tools/sync-from-authoring.py` replaces this mirror from
`podo-curriculum-public`. Edit the upstream authoring repository, then sync again;
never edit the mirror directly.

| Path | What it is |
|---|---|
| `authoring/kr/tracks/` | Complete Korean curriculum under review: TOCs, generated briefs, blueprints, course plans, manifests and lesson HTML |
| `authoring/en/tracks/` | The same complete review tree for English |
| `authoring/kr/trial/` | Korean trial lessons, reports and assets before explicit promotion |
| `authoring/kr/interactive/` | Korean interaction-protocol material when it exists upstream |

The language code is the subject being taught, matching `courses/kr/` and
`courses/en/`. It is not the learner market; Japan-market English remains `en`
here and carries `countryCode: JP` in its course manifest.

Runtime references in mirrored HTML are repointed from upstream's `runtime/` to
this repository's `shared/`, so the review copy renders locally. Promotion tools
then flatten and bundle those dependencies for deployment.

`tools/import-trial-decks.py` and `tools/import-report-deck.py` deliberately read
the reviewed sandbox copy. They do not import directly from the external
authoring tree, so the sequence cannot skip review:

```text
podo-curriculum-public
        -> sync
sandbox/authoring/<language>/
        -> review and explicit promotion
courses/<language>/
```

## `archive/`

Superseded versions and design-variant explorations owned by this repository.
Unlike `authoring/`, this directory is not replaced by the sync.
