# Korean release AI review

Review date: 2026-08-14

## Verdict and scope

The first-draft release set is complete: **480 of 480 in-scope lessons are written** across Hangul
(14), Core Patterns (116), Contextual Korean (140) and Free Talking (210). Pronunciation is
deliberately deferred and was not reviewed as release content.

This pass repaired confirmed structural and semantic defects, regenerated reviewer-friendly text
projections for every release track and re-ran the deterministic curriculum gates. It is intended
to remove avoidable low-quality work before native-speaker review; it does not replace the final
native judgment on naturalness, register and cultural nuance.

## Review method

- Parsed all 480 authored decks and checked page structure, local references, metadata, bilingual
  prompt presence, unique sync IDs, forbidden inline code and runtime-sensitive script parity.
- Audited every reorder answer for solvability, answer order and meaningful chunk count.
- Projected all learner-facing and tutor-facing text into course-sized packets with stable source,
  page and field locators so a reviewer never has to proofread raw HTML.
- Reviewed semantic candidate sets for prompt/answer workload, tutor-versus-learner ownership,
  reciprocal free-talk roles, repeated or empty content, real-form distractors and citation markup.
- Re-verified the existing Free Talking issue history, including superseded fixes and accepted
  sensitivity policies, against the current source.

## Applied repairs

- Repaired three Korean/Japanese tutor-script sentence-parity failures so runtime line pairing is
  deterministic.
- Rewrote 17 Core answer prompts that asked multiple questions above one answer area; each now asks
  for one explicit choice or one sentence.
- Corrected ambiguous ownership in Contextual and Free Talking tutor scripts, including first-person
  tutor references and learner-owned answers, reactions, boundaries and standards.
- Removed eight empty duplicate subtitle boxes from Contextual travel lessons.
- Clarified the Hangul tense-versus-aspirated listening task and moved its one-off inline styling
  into the shared trial stylesheet.
- Restored the complete approved Free Talking coaching and sensitivity language for money,
  nationality, difficult topics and learner skip/comfort boundaries.
- Generalized proofreading packet generation from Free Talking to all four release tracks, with
  regression tests for lesson counts, stable locators and rejection of deferred Pronunciation.
- Corrected seven additional high-confidence Core defects: past-tense parity in `-을 뿐만 아니라`,
  an overgeneralized `-느니` explanation, an ungrammatical learner question, two visible typos, an
  unrelated vowel-choice instruction and a choose-one distractor that was also valid Korean.
- Corrected four additional Contextual defects: the taught `또 ~네` form, listening-versus-watching
  continuity in a song recommendation, an incoherent lost-wallet/card example and an inconsistent
  four-chip row. Normalized the final two legacy Contextual page IDs and the ten shopping-course
  rule-card readings that were outside the runtime's styled selectors.
- Replaced the recurring Core role instruction `제가 하나 쪽을 읽을게요` with the clearer
  `제가 하나 역할을 읽을게요` in all 116 lessons, with matching Japanese role wording.

## Candidate adjudication

- **101 mixed-count reorder pages:** signed off. No answer exceeds four chunks, no answer is already
  solved, and all answers are reconstructable. Korean's agglutinative structure makes a shorter
  two- or three-unit answer legitimate beside a four-unit answer. These remain visible as warnings,
  while impossible, over-four and already-solved rows remain release errors.
- **275 real-form distractor candidates:** not defects as a class. The checker intentionally finds
  wrong options that are valid Korean elsewhere; the reviewed patterns are taught contrasts such
  as particles, register, tense and sentence type. Mechanical replacement with impossible Korean
  would often make the exercise worse. Native review should still flag any row where both options
  fit its specific sentence.
- **272 quote-format candidates:** retained for the editorial pass. This heuristic intentionally
  over-selects any Hangul embedded in Japanese prose, including role labels, form names and bare
  phonological material. It is useful as a packet filter but is not proof of a semantic defect;
  uncertain paired-language quotation was not mass-edited.
- **17 fixed learner questions in Contextual free talk:** signed off. These pages still complete the
  required reciprocal sequence (tutor asks, learner answers, learner asks, tutor answers); the
  learner question is prewritten rather than editable.

## Verification snapshot

- Course plan: 480/480 in-scope lessons written; Pronunciation 0/10 and deferred.
- Structure: 0 problems.
- Reorder reconstruction: 480 decks, 0 mismatches; 0 rows over four chunks.
- Shared deck validator: 480 release decks, 0 errors, 101 reviewed warnings.
- Free Talking audit: all 1,126 historical issue records applied or verifiably superseded; all 28
  Balance Games decks covered by the full-course audit.
- Packet generator, course-planner and shared deck-validator regression tests: 18 passing.
- Representative repaired decks from all four tracks render at 480px with no horizontal overflow,
  stray reading text or console errors. A 360px narrow-column pass on the densest reviewed Free
  Talking story also has no horizontal overflow.
- The repaired two-option Core question was exercised in the local runtime: the malformed option is
  rejected, the intended answer is accepted and the 480px phone frame remains overflow-free.

## Native-review handoff

Review the generated packets under `korean/proofreading/<track>/packets/`, not raw HTML. Prioritize
spoken Korean naturalness, Japanese equivalence, register, cultural assumptions and the small
candidate sets above. Report changes using each packet's source path, page ID and field name; apply
approved corrections to `lesson.html`, then regenerate the packets. The HTML remains the sole
editable source of truth.
