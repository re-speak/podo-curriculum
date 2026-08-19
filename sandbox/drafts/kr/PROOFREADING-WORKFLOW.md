# Curriculum proofreading workflow

This workflow defines both **complete lesson proofreading** and the narrower text-projection
workflow used for large editorial batches. The HTML remains the only source of truth. Generated
proofreading files are disposable views of that source and are never edited.

An unqualified request to **proofread a lesson, course or curriculum** means the complete review:
language, pedagogy, narrative/role logic, activity usefulness, interaction behavior and rendered
layout. Do not silently interpret “proofread” as spelling and translation only. A user may ask for
a narrower text-only, Japanese-only or visual-only pass explicitly.

The packet implementation covers all four release tracks. Tracks `1-hangul`, `2-core-patterns`
and `3-contextual-korean` use one packet per course. `4-freetalking` uses one theme containing the
Advanced and Intermediate versions together so level drift stays visible. The deferred
`5-pronunciation` track is not part of the current release or its proofreading gate.

## Complete lesson proofreading

Read `LESSON-CREATION-WORKFLOW.md`, the track's `lesson-blueprint.md`, the lesson brief and the
relevant canonical trial deck before judging a generated lesson. Then inspect **every page in
order as a learner**, not as disconnected HTML fragments. A pass must cover these dimensions:

1. **Outcome contract:** the goal presents the lesson's two observable outcomes distinctly; each
   outcome maps to one taught pattern and is earned again in the final application. A fluent tutor
   and a Japanese learner should both be able to say what the two takeaways are.
   For Contextual Korean, also reject legacy shell drift: the opening order is `episode-card` →
   `scene` → `lesson-goal` → `expressions`, the two targets use the canonical `.known-row`
   markup, and each target reappears verbatim in its `pN-teach .sent-hero`.
2. **Scene and roles:** dialogue is believable, every turn follows from the previous one, speaker
   ownership stays stable and narrative continuity agrees with adjacent episodes. Receptive lessons
   may reconstruct the partner's line, but instructions must say so and production must not quietly
   switch roles.
   Read the visible episode card as content too: course label, episode number, title and cast must
   match the lesson being audited. A copied cover from another course is a confirmed error even
   when metadata and the inner lesson are correct.
3. **Teaching:** each pattern receives a short Korean/Japanese meaning-and-use box on `pN-teach`;
   formation belongs on `pN-rule`, not a dark transition page. Explanations must be short enough to
   point at, accurate enough to prevent a false generalization and supported by the examples shown.
4. **Activity value:** every page does teaching or retrieval work. Closed activities retain four
   questions; reorder rows use up to four meaningful chunks presented out of answer order (a row
   that arrives already solved has no retrieval value); a choose page exists only for a real,
   taught distinction. Do not use grammatical alternatives whose choice needs untaught nuance, nor
   an obviously random character as a distractor. One prompt and one visible answer area must ask
   for the same amount of work.
   A retained choose page must use the runtime-wired `.choose-row .opt` contract; legacy
   `.choice-row` markup is a broken interaction even when its two alternatives look correct.
5. **Application and nuance:** the replay and completion reconstruct the opening scene. Contextual
   free talk is reciprocal—tutor asks, learner answers, learner asks, tutor gives an editable native
   answer. A native tip adds adjacent register, prosody, contraction, collocation or intensity; it
   does not repeat the lesson. The final 5–7-turn scene uses both outcomes and ends with a meaningful
   hook or, in a finale, real closure.
6. **Korean and Japanese:** Korean is natural spoken Korean at the promised level. Japanese carries
   the same agent, object, tense, register and emotional force; it must not leave an object implicit
   when doing so makes the Korean pattern ambiguous. Vocabulary glosses and highlighted spans agree
   with the complete sentence.
7. **Visual semantics:** the diagram must depict the rule it claims to teach. `.bt-word` holds a
   complete dictionary form or other whole word. `.bt-syl` holds exactly one Hangul syllable whose
   받침 or vowel is the visual evidence—never a multi-syllable stem squeezed into a syllable tile.
   One block means one invariant rule; multiple blocks mean genuine formation branches.
8. **Rendered behavior:** open the actual deck at a 480px lesson column and a 360px narrow column.
   Visit every page, scroll to its real bottom and test representative wrong and correct choices,
   all reorder answers, exact inputs, free-answer fields, reciprocal tutor fields and teaching mode.
   Check console errors, pager obstruction and both outer and **internal** collisions: text can stay
   inside a fixed tile's bounding box while wrapping across its 받침 seat, so `scrollWidth` alone is
   not proof of visual correctness.

Record exact page IDs and current/replacement text for content changes. Separate confirmed errors
from editorial alternatives that need a human decision. After applying fixes, repeat the affected
interaction and screenshot checks, run structural/reference validation and synchronize any
deployable copy derived from the authoring HTML.

## Why the projection is one-way

Automatically merging edited Markdown back into HTML would create two editable sources and make
it easy to overwrite markup or a newer correction. Instead:

1. HTML is projected into compact Markdown and JSONL.
2. Reviewers report proposed changes with an exact source hash and text locator.
3. The issue file is validated against the current HTML.
4. An editor applies approved changes to `lesson.html` explicitly.
5. The projection is regenerated and checked.

## Token-efficient projected audits

Use this pattern when many decks need the **same narrow human judgment**—for example quoted-form
boundaries, terminology consistency, Japanese parity, instruction clarity, vocabulary ownership,
chip boundaries or component misuse. Do not send complete HTML decks to reviewers when the target
can be represented as a few text fields.

1. **Filter mechanically first.** Parse the HTML once and select only plausible candidates with a
   deterministic rule. Export compact records such as
   `{source, pageId, field, current, pairedText, context}`. Keep the source path and exact current
   text so every proposed edit can be located without rereading the deck.
2. **Batch by course, not by file.** A course-sized packet gives enough local terminology and
   teaching context while avoiding repeated instructions for every lesson. Split only on disjoint
   source sets so parallel reviewers cannot edit the same line.
3. **Reviewers propose; they do not write.** Give reviewers the compact packet plus one short,
   explicit decision contract. Their output contains exact `current` and `suggested` strings (or
   old/new values for paired fields). They never open or modify `lesson.html`.
4. **Make the allowed mutation mechanically provable.** For a quote-only pass, removing the newly
   inserted quote characters from `suggested` must reproduce `current` byte-for-byte. For another
   audit, define an equally narrow invariant rather than relying on a reviewer saying it changed
   only the intended thing.
5. **Validate centrally before applying.** Reject stale or non-unique source text, malformed or
   unbalanced markup, no-ops, one-sided paired-language changes, wording drift and conflicting
   proposals for the same source field. Apply accepted edits from one coordinator using explicit
   paths, then run the repository's structural/runtime checks.
6. **Audit the skips.** A conservative first pass should prefer leaving an uncertain candidate
   alone. Give the skipped set—not the whole corpus—to a second reviewer, then inspect any large or
   surprising recovery before applying it. This catches false negatives without paying for a
   second full read.

The projection is disposable; the **extractor, decision contract and validator are the durable
method**. Save those in the repository when an audit will recur, but do not commit one-time packet
or proposal output. Static checks should enforce objective invariants; projected human review is
for questions where the same markup can be either correct or wrong depending on meaning.

For paired tutor scripts specifically, project the direct `.section-subtitle > .ko` and `.ja`
text plus `data-page-id`. Japanese prose containing a Hangul run is a strong citation-boundary
signal, but not proof: role names, register names and bare jamo used as phonological conditions can
legitimately remain unquoted. The canonical quote rules are in `AUTHORING.md`; sentence splitting
must agree with `runtime/js/script-lines.js`, including its quote-aware behavior.

If either the lesson hash or current field text changed after extraction, issue validation fails.
The reviewer then uses a newly generated packet instead of guessing how to merge stale prose.

## Generated artifacts

Run once for each release track:

```sh
for track in 1-hangul 2-core-patterns 3-contextual-korean 4-freetalking; do
  python3 korean/tools/build_proofreading_packets.py "korean/tracks/$track"
done
```

This writes one matching folder under `korean/proofreading/`. Tracks 1-3 contain course packets,
`lessons.jsonl`, `manifest.json` and a short README. Free Talking additionally includes paired
level packets and `boilerplate.md`:

| Artifact | Purpose |
| --- | --- |
| `packets/*.md` | One course per packet for tracks 1-3; one paired Advanced/Intermediate theme for Free Talking |
| `lessons.jsonl` | One lesson per line, containing exact `source` / `pageId` / `field` locators and source hashes |
| `boilerplate.md` | Every unique text variant from the repeated style and feedback pages omitted from theme packets |
| `manifest.json` | Counts, packet membership, source-set hashes and omitted-page signatures |

All packets retain exact source hashes and stable page/field locators. Free Talking's specialized
theme packets retain:

- three-language metadata titles;
- the goal, its three axes and Japanese support;
- every model-story or article line, translation, exact Korean highlight span and vocabulary gloss;
- model/article tutor guidance;
- the learner-facing talk introduction;
- all eight Korean/Japanese main questions;
- all eight tutor instructions and twenty-four follow-up questions.

They omit HTML attributes unrelated to locating text, CSS, JavaScript, assets, pager markup,
correction controls and repeated screen chrome. Omitted repeated text is still reviewable once in
`boilerplate.md`.

## Review batches and passes

Use the ten theme packets as the only parallel work boundary. Do not split Advanced and
Intermediate: their adjacency is what makes level drift visible. A reviewer may make several
passes over one packet, but every finding goes into one issue JSONL file for that review round.

Recommended passes:

1. **Korean naturalness:** spoken phrasing, ambiguity, double questions and awkward follow-ups.
2. **Japanese parity:** direct meaning, tone, omissions and vocabulary-gloss consistency.
3. **Question ladder:** concrete warm-up through difficult opinion and a true closing reversal.
4. **Level pairing:** same intent and adult interest, with genuinely lower processing burden in Intermediate.
5. **Repetition:** duplicated stories, main questions or conspicuous follow-ups inside the theme.
6. **Sensitivity:** assumptions, stereotyping, advice or judgment; every `[깊게]` lesson must preserve its range/skip contract.

After the ten packet reviews, run one cross-theme pass over `lessons.jsonl` for repeated strings
and terminology. Structural HTML, runtime behavior and mobile layout remain separate QA jobs;
this text projection does not replace them.

## Review issue format

Store one JSON object per line. Copy `sourceSha256`, `source`, `pageId`, `field` and `current`
exactly from the packet/JSONL. `suggested` contains only the replacement for that one field.

```json
{"source":"korean/tracks/4-freetalking/courses/talk-me-lately-advanced/lessons/01-worth-the-money/lesson.html","sourceSha256":"<64 hex characters>","pageId":"q4","field":"question.ko","current":"현재 질문","suggested":"제안하는 질문","category":"ko-naturalness","severity":"warning","reason":"말할 때 목적어가 불분명하다."}
```

Allowed severities are `error`, `warning` and `suggestion`. Useful categories include
`ko-naturalness`, `ja-parity`, `vocabulary`, `pedagogy`, `level`, `repetition`, `sensitivity`
and `metadata`.

Validate a completed issue file before applying anything:

```sh
python3 korean/tools/build_proofreading_packets.py \
  korean/tracks/4-freetalking \
  --validate-issues path/to/issues.jsonl
```

Validation rejects malformed JSON, missing fields, unknown locators, stale HTML hashes, stale
current text, no-op suggestions and unknown severity values. It never edits lesson files.

If a shared-text or other non-overlapping edit changes a lesson's whole-file hash while review is
in progress, do not hand-edit the hashes. Refresh them with the guarded mode below. It updates
only `sourceSha256`, and only after every cited locator still contains the exact stored `current`
text; any overlapping content edit makes the command fail without writing the issue file.

```sh
python3 korean/tools/build_proofreading_packets.py \
  korean/tracks/4-freetalking \
  --refresh-issue-hashes path/to/issues.jsonl
```

## Applying an approved round

1. Validate and triage the combined issue JSONL. Resolve conflicting suggestions before editing.
2. Edit only the cited source fields in `lesson.html`; paired Korean/Japanese changes normally
   require two explicit issues so neither language changes silently.
3. Verify that every approved suggestion landed in the cited field. This post-edit mode expects
   the stored source hash to be historical and checks `suggested` rather than `current`:

   ```sh
   python3 korean/tools/build_proofreading_packets.py \
     korean/tracks/4-freetalking \
     --verify-applied path/to/issues.jsonl
   ```

   If a later reviewed round improves the same field again, keep the earlier audit record and add
   `"supersededBy":"later.issues.jsonl:LINE"`. Verification accepts that chain only when the
   referenced record cites the same locator, starts from the earlier suggestion, and its final
   suggestion is the text currently in the HTML. This prevents a legitimate second-pass repair
   from making the first audit look unapplied without allowing stale suggestions to be waived.

4. Run the structural/reference checks for all affected release tracks and `git diff --check`.
5. Regenerate the affected packets.
6. Prove they are current:

   ```sh
   python3 korean/tools/build_proofreading_packets.py \
     korean/tracks/4-freetalking --check
   ```

7. Re-run representative 480px browser QA for any correction that materially changes line length,
   article density or a deep-topic instruction.

The round is complete only when issue validation happened before editing, the HTML checks pass,
and `--check` reports every in-scope deck and packet current. The release-wide denominator is 480
decks: 14 Hangul, 116 Core Patterns, 140 Contextual Korean and 210 Free Talking.

Packet generation itself also enforces the static deck shell: exact page/source shape, metadata,
unique sync IDs, resolved local `href`/`src` references, eight nonempty bilingual main prompts,
three nonempty follow-ups per prompt, no yomi, and no inline CSS or JavaScript. Main prompts and
follow-ups may legitimately be instructions such as `아침부터 순서대로 이야기해 주세요.` rather
than questions. This keeps the final `--check` from proving text freshness while silently accepting
a structurally damaged deck.
