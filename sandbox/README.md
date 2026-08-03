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
| `trial/` | the four 체험수업 decks, reports and onboarding screens |
| `track-samples/` | one sample lesson per track — core patterns, contextual, drama |
| `archive/` | superseded versions and design-variant explorations |

Promote something by moving it into `courses/<lang>/<course>/lessons/<NN-slug>/`
and giving it a `lesson.yaml`. That move is the promotion — there is no flag to flip.
