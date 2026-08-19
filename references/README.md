# references

Durable source and evidence material used to design curriculum. Never deployed
and never packaged.

Curriculum-under-review does **not** belong here. TOCs, generated briefs,
blueprints, course manifests and lesson HTML stay together under
`sandbox/drafts/<code>/` until an explicit promotion puts a verified
course in `courses/<language>/`.

| Path | What it is |
|---|---|
| `kr/curricula/` | Derived pattern maps, clean text and page wireframes from the Korean textbooks studied |
| `kr/reports/` | Captures of other services' learner reports used as product-design evidence |

The language code is the subject being taught, not the market. Japan-market
English material is `en` here and uses `countryCode: JP` when promoted as a
course.

What the authoring toolchain *generates* is not durable source and does not live
here — grammar maps, running lexicons and evidence ledgers are rebuilt from the
decks, so they sit with the drafts under `sandbox/drafts/<code>/reference/`.

Licensed textbook PDFs and `dekiru-kankokugo/page-images/` are not in this
repository at all. They are 726MB of private source material, one file past
GitHub's 100MB ceiling, and nothing in the build reads them; they stay in the
archived `podo-curriculum-public`. Only the derived markdown and wireframe images
came across.
