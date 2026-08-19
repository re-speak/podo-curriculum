# references

Durable source and evidence material used to design curriculum. Never deployed
and never packaged.

Curriculum-under-review does **not** belong here. TOCs, generated briefs,
blueprints, course manifests and lesson HTML stay together under
`sandbox/authoring/<language>/` until an explicit promotion puts a verified
course in `courses/<language>/`.

| Path | What it is |
|---|---|
| `kr/curricula/` | Derived pattern maps, clean text and page wireframes from the Korean textbooks studied |
| `kr/reports/` | Captures of other services' learner reports used as product-design evidence |
| `en/reference/` | English teaching philosophy, source hierarchy, grammar coverage and Japanese-L1 evidence |

The language code is the subject being taught, not the market. Japan-market
English material is `en` here and uses `countryCode: JP` when promoted as a
course.

These directories are mirrored from `podo-curriculum-public/{korean,english}` by
`tools/sync-from-authoring.py`. Edit the upstream source and re-sync; the mirror
is replaced wholesale.

Licensed textbook PDFs and `dekiru-kankokugo/page-images/` stay upstream. They
are large, private source material and nothing in the build reads them; only the
derived markdown and wireframe images are mirrored here.
