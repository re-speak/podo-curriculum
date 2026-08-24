#!/usr/bin/env python3
"""Static checks for lesson decks — the ones that otherwise fail silently.

    python3 tools/authoring/check_deck.py sandbox/drafts/en/tracks     # a tree
    python3 tools/authoring/check_deck.py path/to/lesson.html ...      # named decks
    python3 tools/authoring/check_deck.py --all                        # every deck in the repo

Why this exists
---------------
A deck can be valid HTML, pass every reference check, render without a console
error, and still be wrong on screen. Three defects in particular leave no
trace:

1. **Tutor script sentence parity.** `shared/js/script-lines.js` rebuilds the
   blue box as one sentence per line, each with its own translation underneath —
   but only when both sides have the same number of sentences. When they differ
   it deliberately does nothing, because mis-pairing would print "this
   translation belongs to this line" as a lie. The failure therefore looks like
   slightly ugly prose rather than anything broken. `AUTHORING.md` §2 has always
   required the two sides to be the same sentences; nothing enforced it.

2. **Reorder chunking consistency.** Four chunks is the ceiling and the working
   default. Mixed counts are an error in English authoring. Three chunks require
   an explicit human-review marker; meaningful prepositions may stand alone when
   placing that preposition is the learning operation. In Korean, mixed counts are a
   review candidate rather than proof of a defect: short agglutinative beginner
   sentences can honestly have two units beside a four-unit sentence. They are
   therefore warnings, while counts above four still fail.

3. **Reorder solvability.** A row can have the expected chip count while one
   chip is missing or belongs to another answer. This checker mirrors
   `activities.js`'s normalization and proves that some ordering of the chips in
   each English task block reconstructs that block's `data-a` exactly.

4. **Freetalking article contract.** Page 2 is a 10-to-15-row pre-study-only
   article, and every highlighted item must have one matching in-context gloss
   on its own row. Its class script asks one question about learner questions;
   it does not coach the learner to read, skim, tap or operate the page. A
   five-line tutor story, in-class catch-up direction or mismatched glossary
   silently changes the activity while still rendering plausibly.

5. **Freetalking tutor contract.** Tutor notes use English, question-page notes
   contain actual questions rather than duplicate filler, and the discussion
   style page keeps the approved direct wording and option order.

6. **English runtime and title identity.** English decks declare their target
   language so shared tutor controls localize correctly. Freetalking's visible
   opening title and document title preserve the authoritative generated brief
   instead of drifting into an improvised short label.

7. **Core production parity.** Model and replay keep the same turn sequence,
   roleplays use profile images, live Free Talk labels every real speaker, and
   completion targets remain visibly connected to their Japanese cues. Late
   inline blanks reuse controlled-fill targets exactly, leaving scene facts and
   slot vocabulary visible.

8. **Cross-language target highlighting.** Every Core and Contextual teaching
   or reading model highlights the same number of target units in English and
   Japanese. Controlled fills mark exactly one Japanese cue per blank, and
   compact word-choice activities mark one Japanese cue per decision.

9. **Contextual tutor operability.** Roleplay pages use profile images while
   live Tutor/Me exchange uses generic icons. Receptive `Understand` choices
   expose an English sense label as well as Japanese support, so an
   English-speaking tutor never has to interpret Japanese-only alternatives.

10. **Contextual frame boundaries.** Late replay and transfer phrase fields
    reuse the exact frame answers established on controlled fill pages. Scene
    facts and slot vocabulary stay visible outside the editable field instead
    of quietly turning a pattern check into whole-sentence recall.

11. **Meaningful reorder chips.** Punctuation-only chips, detached articles or
    prepositions and split suffixes are hard errors. A short frame with no
    honest three-unit build omits reorder instead of padding it.

12. **Generated spacing structure.** Repeated model rows use the design-system
    `model-list`, and phrase inputs live inside `answer-box > answer-fill` so
    wrapped controls inherit the tested vertical rhythm.

These are not caught by reading markup, which is why they are here rather than in a
checklist. A checklist item only reaches the writers who were told to read it.

Exit status is 1 if any ERROR was found. WARNs do not fail the run: they mark
things a human should look at and may legitimately sign off on.
"""

import argparse
import difflib
import html as html_lib
import pathlib
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from itertools import permutations

import vocabulary

REPO = pathlib.Path(__file__).resolve().parents[2]
# `promote.py` gives each deck of a lesson its own directory.
DECK_SLOTS = {"lecture", "prestudy"}

EN_END = ".!?"
JA_END = "。！？"
KO_END = ".!?"          # Korean decks punctuate the spoken line with ASCII too

TAG = re.compile(r"<[^>]+>")
PAGE_ID = re.compile(r'data-page-id="([^"]+)"')
SYNC_ID = re.compile(r'data-sync-id="([^"]+)"')
SUBTITLE = re.compile(r'<p class="section-subtitle([^"]*)"[^>]*>(.*?)</p>', re.S)
SPAN_KO = re.compile(r'<span class="ko">(.*?)</span>', re.S)
SPAN_JA = re.compile(r'<span class="ja">(.*?)</span>', re.S)
TASK_BLOCK = re.compile(r'<div class="task-block">')
CHOICE = re.compile(r'class="choice"')
SENT_ROW = re.compile(r'<div class="sent"')
S_KEY = re.compile(r'class="s-key"')
S_WORD = re.compile(r'class="s-w"')
ARTICLE_COACHING = re.compile(
    r"\b(?:tap|click|open|skim|look\s+at|read(?:ing)?\s+(?:it|this|the\s+article))\b",
    re.I,
)
TUTOR_NOTE_OPEN = re.compile(r'<div class="tutor-note">')
TUTOR_NOTE_BLOCK = re.compile(r'<div class="tutor-note">(.*?)</div>', re.S)
OPT_NOTE_BLOCK = re.compile(r'<ul class="opt-note">(.*?)</ul>', re.S)
FB_ADDS_BLOCK = re.compile(r'<div class="fb-adds">(.*?)</div>', re.S)
TN_CAP = re.compile(r'<span class="tn-cap">')
LIST_ITEM_BODY = re.compile(r'<li\b[^>]*>(.*?)</li>', re.S)
NON_ENGLISH_SCRIPT = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]")
FREETALK_QUESTION_PAGES = {"warm-1", "warm-2", *(f"q{i}" for i in range(1, 7))}
FREETALK_PAGES = [
    "lesson-goal", "article", "lesson-style", "talk-intro",
    "warm-1", "warm-2", "q1", "q2", "q3", "q4", "q5", "q6", "feedback",
]
FREETALK_STYLE_EN = "Please choose your preferred discussion style."
FREETALK_STYLE_JA = "希望する会話の進め方を選んでください。"
REORDER_SCRIPT_EN = "Let's put the words in order, then say the whole sentence out loud."
REORDER_SCRIPT_JA = "単語を順番に並べて、文をまるごと声に出して言ってみましょう。"
TRANSLATE_SCRIPT_EN = "Let's read the Japanese, then say it in English."
TRANSLATE_SCRIPT_JA = "日本語を見て、英語で言ってみましょう。"
SPAN_TAG = re.compile(r"<span\b[^>]*>|</span>", re.I)
SPAN_OPEN = re.compile(r"<span\b[^>]*>", re.I)
LOCAL_REF = re.compile(r'(?:href|src)="((?!https?:|data:|#)[^"]+)"')
INLINE_STYLE = re.compile(r"<style[\s>]")
INLINE_SCRIPT = re.compile(r"<script(?![^>]*\ssrc=)[^>]*>")
LEGACY_CONTROL = re.compile(
    r'<span class="(?:slot|answer-space)"\s+data-sync-id="([^"]+)"')
META_TAG = re.compile(r"<meta\b[^>]*>", re.I)
ATTRIBUTE = re.compile(r'''([\w:-]+)\s*=\s*(["'])(.*?)\2''', re.S)
DOCUMENT_TITLE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.I | re.S)
TRANSITION_TITLE = re.compile(
    r'<h2\b[^>]*class="[^"]*\btransition-title\b[^"]*"[^>]*>(.*?)</h2>',
    re.I | re.S,
)
TITLE_JA = re.compile(
    r'<span\b[^>]*class="[^"]*\btitle-ja\b[^"]*"[^>]*>.*?</span>',
    re.I | re.S,
)
TURN_OPEN = re.compile(r'<div class="turn\b')
OTHER_TURN_LINE = re.compile(
    r'<div class="turn other".*?<span class="korean">(.*?)</span>'
    r'<span class="translation">',
    re.S,
)
PROFILE_AVATAR = re.compile(r'<img class="avatar"(?:\s|>)')
WHO_OPEN = re.compile(r'<span class="who">')
ENDING = re.compile(r'class="ending"')
TARGET = re.compile(r'class="target"')
PHRASE_INPUT = re.compile(r'class="[^"]*\bphrase-input\b')
MODEL_LINES = re.compile(r'class=["\'][^"\']*\bmodel-lines\b')
SLOT_INPUT = re.compile(r'<input\b[^>]*class="[^"]*\bslot-input\b')
CONTROL_TAG = re.compile(r'<(?:input|textarea)\b[^>]*>', re.I)
GENERIC_AVATAR = re.compile(r'<span class="[^"]*\bavatar\b[^\"]*\bicon\b')
TAG_OPEN = re.compile(r'<(?:div|span)\b[^>]*>', re.I)
# The choice activity is one component under two names: English decks wrap it in
# `word-choice-list`, Korean decks in `choose-list`. Everything inside — the
# `choose-row` rows, the `opt` options, `data-correct` — is identical, so every
# rule that reads a choice page accepts either container.
CHOICE_LIST = re.compile(r'class="[^"]*\b(?:word-choice-list|choose-list)\b')
DATA_CORRECT = re.compile(r"\bdata-correct(?:\s|>|=)")
# Tracks whose decks teach one pattern per lesson and therefore carry the
# `p1/p2` read-and-choose arc these rules read. Korean numbers its tracks from
# the alphabet, English from the first pattern course, so the names differ.
PATTERN_TRACKS = {
    "1-core-patterns", "2-contextual-english",      # sandbox/drafts/en
    "2-core-patterns", "3-contextual-korean",       # sandbox/drafts/kr
}
GENERIC_CORE_FREETALK = re.compile(
    r"\b(?:use (?:both|the) (?:comparison )?patterns?|give the status|"
    r"ask the tutor|tutor's real answer)\b",
    re.I,
)
GENERIC_PATTERN_RULE = re.compile(
    r"Use the (?:second|complete) (?:frame|move)|make the practical result clear",
    re.I,
)
CONTEXTUAL_ROLEPLAY_AS_FREETALK = re.compile(
    r"\b(?:what would you (?:say|ask)|what would you tell (?:the|a) |"
    r"report (?:it|the)|describe one|ask (?:reception|the clerk|another passenger))\b",
    re.I,
)
FORCED_FREETALK_FRAME = re.compile(
    r"\b(?:use|using) (?:today['’]s |the )?"
    r"(?:pattern|frame|expression|sentence starter)\b",
    re.I,
)
TUTOR_READS_TARGET = re.compile(r"\bI(?:['’]ll| will) read\b", re.I)
QUOTED_OPEN_FRAME = re.compile(r"[\u201c\"]\s*[^\u201d\"]{2,}\s*[\u201d\"]")
GENERIC_OPEN_END = re.compile(
    r"\b(?:make|create) (?:your own|one) "
    r"(?:sentence|answer|request|question)\s*[.!?]?\s*$",
    re.I,
)
PATTERN_MEANING_OPERATION = re.compile(
    r"\b(?:read each|repeat each|choose (?:the|one|each)|"
    r"fill (?:the|each)|type (?:the|each)|write (?:the|each)|"
    r"listen to (?:the|each))\b",
    re.I,
)
# Articles and suffixes cannot stand as meaning units. Prepositions can: the
# approved Core pilot deliberately isolates "with", and CORE-12 isolates "at"
# because placing the time preposition is the retrieval operation being taught.
BOUND_REORDER_CHIPS = {"a", "an", "the", "er"}
NON_LEXICAL_HINTS = {
    "a", "an", "the", "am", "is", "are", "was", "were",
    "do", "does", "did", "can", "could", "will", "would",
    "have", "has", "had", "-s", "-es", "-ed", "-ing",
}
BRIEF_HEADING = re.compile(r"^#\s+((?:CORE|CTX|FT)-\d+)\s+·\s+(.+?)\s*$")
QUOTE_OPEN = "“‘「『"
QUOTE_CLOSE = "”’」』"


def meta_content(source, name):
    """Read a meta value without depending on attribute order.

    Entities are resolved, so a title holding `&amp;` or `&#x27;` compares
    equal to the text it stands for rather than to its markup.
    """
    for tag in META_TAG.findall(source):
        attrs = {key.lower(): value for key, _, value in ATTRIBUTE.findall(tag)}
        if attrs.get("name") == name:
            return html_lib.unescape(attrs.get("content", ""))
    return None


def control_answers(source, class_name):
    """Return normalized data-answer values for controls with one CSS class."""
    answers = []
    for tag in CONTROL_TAG.findall(source):
        attrs = {key.lower(): value for key, _, value in ATTRIBUTE.findall(tag)}
        classes = attrs.get("class", "").split()
        answer = attrs.get("data-answer")
        if class_name in classes and answer is not None:
            answers.append(html_lib.unescape(answer).strip().casefold())
    return answers


def sentences(text, enders, *, spaced):
    """Split exactly like shared/js/script-lines.js.

    Quoted teaching expressions often contain punctuation that is not the end
    of the tutor's sentence. Korean also requires whitespace after a real
    sentence ending; Japanese does not.
    """
    plain = html_lib.unescape(TAG.sub("", text))
    out, current, depth = [], [], 0
    for index, char in enumerate(plain):
        current.append(char)
        if char in QUOTE_OPEN:
            depth += 1
        elif char in QUOTE_CLOSE and depth:
            depth -= 1
        if depth or char not in enders:
            continue
        ends = index + 1 >= len(plain) or plain[index + 1].isspace()
        if not spaced or ends:
            sentence = "".join(current).strip()
            if sentence:
                out.append(sentence)
            current = []
    remainder = "".join(current).strip()
    if remainder:
        out.append(remainder)
    return out or [plain.strip()]


def pages(html):
    """Split a deck into (page_id, chunk) by data-page-id boundaries."""
    marks = [(m.start(), m.group(1)) for m in PAGE_ID.finditer(html)]
    for i, (pos, pid) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(html)
        yield pid, html[pos:end]


def page_attributes(chunk):
    """Return attributes from the page root whose opening tag `pages()` trims.

    A page chunk begins at the `data-page-id` attribute rather than at the
    surrounding `<div`.  Reading the first nested element therefore silently
    loses page-level contracts such as support stage.  Keep this helper paired
    with `pages()` so evidence and validation inspect the actual page root.
    """
    prefix = chunk.split(">", 1)[0]
    return {key.lower(): value for key, _, value in ATTRIBUTE.findall(prefix)}


def span_body(source, start):
    """Return the inner HTML of the span whose opening tag ends at start."""
    depth = 1
    for match in SPAN_TAG.finditer(source, start):
        depth += -1 if match.group(0).lower() == "</span>" else 1
        if depth == 0:
            return source[start:match.start()]
    return source[start:]


def class_span_bodies(source, class_name):
    """Return inner HTML for spans containing one exact class token."""
    out = []
    for match in SPAN_OPEN.finditer(source):
        attrs = {key.lower(): value for key, _, value in ATTRIBUTE.findall(match.group(0))}
        if class_name in attrs.get("class", "").split():
            out.append(span_body(source, match.end()))
    return out


def class_tag_count(source, *required):
    """Count div/span opening tags containing every required class token."""
    wanted = set(required)
    count = 0
    for match in TAG_OPEN.finditer(source):
        attrs = {key.lower(): value for key, _, value in ATTRIBUTE.findall(match.group(0))}
        if wanted.issubset(set(attrs.get("class", "").split())):
            count += 1
    return count


def target_highlight_issues(page_chunks):
    """Require exact bilingual cue coverage through the pattern ladder."""
    errors = []

    for page_id, chunk in page_chunks.items():
        if not re.fullmatch(r"p[12]-(?:teach|read)", page_id):
            continue
        english = class_span_bodies(chunk, "korean")
        japanese = class_span_bodies(chunk, "translation")
        if len(english) != len(japanese):
            errors.append(
                f"{page_id}: {len(english)} English model row(s) but "
                f"{len(japanese)} Japanese row(s)"
            )
            continue
        for index, (en_row, ja_row) in enumerate(zip(english, japanese), start=1):
            en_targets = class_tag_count(en_row, "ending")
            ja_targets = class_tag_count(ja_row, "ending")
            # English can express one frame in several non-contiguous pieces
            # while Japanese maps the same meaning to one contiguous phrase.
            # Require visible cueing on both sides; do not pretend the two
            # languages must have the same number of spans.
            if not en_targets or not ja_targets:
                errors.append(
                    f"{page_id} row {index}: mirrored target highlights differ "
                    f"(EN={en_targets} JA={ja_targets})"
                )

    for page_id, chunk in page_chunks.items():
        if not re.fullmatch(r"p[12]-fill", page_id):
            continue
        blocks = TASK_BLOCK.split(chunk)[1:]
        uncued = sum(
            bool(SLOT_INPUT.search(block)) and not class_tag_count(block, "target")
            for block in blocks
        )
        if uncued:
            errors.append(
                f"{page_id}: {uncued} controlled question(s) have no exact Japanese .target"
            )

    for page_id, chunk in page_chunks.items():
        if not re.fullmatch(r"p[12]-choose", page_id) or "word-choice-list" not in chunk:
            continue
        decisions = class_tag_count(chunk, "choose-row", "word-choice")
        cues = sum(
            class_tag_count(body, "ending")
            for body in class_span_bodies(chunk, "translation")
        )
        if decisions != cues:
            errors.append(
                f"{page_id}: each word-level choice needs one Japanese highlight "
                f"(choices={decisions} cues={cues})"
            )

    for page_id in ("p3-model",):
        chunk = page_chunks.get(page_id, "")
        if not chunk:
            continue
        english = class_span_bodies(chunk, "korean")
        japanese = class_span_bodies(chunk, "translation")
        for index, (en_row, ja_row) in enumerate(zip(english, japanese), start=1):
            en_targets = class_tag_count(en_row, "ending")
            ja_targets = class_tag_count(ja_row, "ending")
            if (en_targets or ja_targets) and (not en_targets or not ja_targets):
                errors.append(
                    f"{page_id} row {index}: mirrored target highlights differ "
                    f"(EN={en_targets} JA={ja_targets})"
                )
    return errors


def _normalized_targets(source, class_name):
    return tuple(
        plain_text(body)
        .replace("’", "'")
        .casefold()
        .rstrip(".,!?。！？、")
        for body in class_span_bodies(source, class_name)
    )


def controlled_target_alignment_issues(page_chunks):
    """Prove that controlled blanks retrieve the frame taught on the read page.

    Merely having a highlighted Japanese cue is insufficient: the failed Core
    and Contextual pilots highlighted lexical content and then treated that
    content as the lesson target.  Compare exact row-level evidence instead.
    """
    errors = []
    for part in (1, 2):
        read_id = f"p{part}-read"
        fill_id = f"p{part}-fill"
        read = page_chunks.get(read_id, "")
        fill = page_chunks.get(fill_id, "")
        if not read or not fill:
            continue

        english_rows = class_span_bodies(read, "korean")
        fill_rows = TASK_BLOCK.split(fill)[1:]
        if len(fill_rows) != len(english_rows):
            errors.append(
                f"{fill_id}: {len(fill_rows)} fill rows but {len(english_rows)} "
                f"canonical rows on {read_id}"
            )
            continue

        for index, (english, fill_row) in enumerate(
            zip(english_rows, fill_rows), start=1
        ):
            taught_english = _normalized_targets(english, "ending")
            blank_answers = tuple(
                answer.replace("’", "'").casefold().rstrip(".,!?")
                for answer in control_answers(fill_row, "slot-input")
            )
            if not blank_answers or any(
                answer not in taught_english for answer in blank_answers
            ):
                errors.append(
                    f"{fill_id} row {index}: blank answers {blank_answers!r} do not "
                    f"belong to taught target segments {taught_english!r} on {read_id} — keep "
                    "vocabulary visible and blank only the practiced frame"
                )

            fill_japanese = _normalized_targets(fill_row, "target")
            if len(fill_japanese) != len(blank_answers):
                errors.append(
                    f"{fill_id} row {index}: Japanese target cue count "
                    f"({len(fill_japanese)}) does not match blank count "
                    f"({len(blank_answers)})"
                )
    return errors


def translation_support_issues(page_chunks):
    """Validate the required target-v2 support contract and hint boundaries."""
    errors = []
    for page_id, chunk in page_chunks.items():
        if not re.fullmatch(r"p[12]-translate", page_id):
            continue
        attrs = page_attributes(chunk)
        contract = attrs.get("data-scaffolding-contract")
        stage = attrs.get("data-support-stage")
        blocks = TASK_BLOCK.split(chunk)[1:]

        for index, block in enumerate(blocks, start=1):
            try:
                hints = vocabulary.hint_words(block)
            except vocabulary.VocabularyError:
                # The deck-wide vocabulary check reports the malformed chip.
                hints = set()
            banned = sorted(hints & NON_LEXICAL_HINTS)
            if banned:
                errors.append(
                    f"{page_id} row {index}: non-lexical hint chip(s) "
                    f"{', '.join(banned)} — articles, auxiliaries and inflections "
                    "must be retrieved, not hinted"
                )

        if contract is None:
            errors.append(
                f"{page_id}: translation production must declare "
                'data-scaffolding-contract="target-v2" and an explicit support stage'
            )
            continue
        if contract != "target-v2":
            errors.append(f"{page_id}: unknown scaffolding contract {contract!r}")
            continue
        if stage not in {"supported", "checkpoint"}:
            errors.append(
                f"{page_id}: target-v2 requires data-support-stage=\"supported\" "
                "or \"checkpoint\""
            )
            continue
        page_hint_count = 0
        for index, block in enumerate(blocks, start=1):
            hints = vocabulary.hint_words(block)
            page_hint_count += len(hints)
            if stage == "checkpoint" and hints:
                errors.append(
                    f"{page_id} row {index}: checkpoint production must not carry hints"
                )
        if stage == "supported" and not page_hint_count:
            errors.append(
                f"{page_id}: supported production needs at least one useful lexical hint; "
                "use checkpoint only when all non-target language is deliberately retrieved"
            )
    return errors


def choice_branch_coverage_issues(page_chunks):
    """Require a choice activity to make both taught alternatives earn their keep.

    Four copies of the same answer are visually interactive but pedagogically
    inert: after the first row the learner can tap by position without reading.
    This objective gate complements the human review of distractor plausibility.
    """
    errors = []
    for page_id, chunk in page_chunks.items():
        if not re.fullmatch(r"p[12]-choose", page_id) or not CHOICE_LIST.search(chunk):
            continue
        correct = []
        for match in SPAN_OPEN.finditer(chunk):
            attrs = {
                key.lower(): value for key, _, value in ATTRIBUTE.findall(match.group(0))
            }
            if (
                "opt" not in attrs.get("class", "").split()
                or not DATA_CORRECT.search(match.group(0))
            ):
                continue
            correct.append(plain_text(span_body(chunk, match.end())).casefold())
        if len(correct) >= 2 and len(set(correct)) < 2:
            errors.append(
                f"{page_id}: every row has the same correct branch {correct[0]!r} — "
                "vary the correct alternative or replace the activity with a decision that teaches something"
            )
    return errors


def choice_row_correct_slots(chunk):
    """Return which slot holds the correct option in each row, in page order.

    A row is any element carrying the `choose-row` class; its options are the
    `opt` spans between it and the next row.  Returns None — decline to judge —
    unless every row is a clean two-way choice with exactly one correct option,
    because a page mixing widths has no single "position" to be predictable in.
    """
    starts = []
    for match in TAG_OPEN.finditer(chunk):
        attrs = {key.lower(): value for key, _, value in ATTRIBUTE.findall(match.group(0))}
        if "choose-row" in attrs.get("class", "").split():
            starts.append(match.start())
    slots = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(chunk)
        correct = []
        for match in SPAN_OPEN.finditer(chunk, start, end):
            attrs = {
                key.lower(): value for key, _, value in ATTRIBUTE.findall(match.group(0))
            }
            if "opt" in attrs.get("class", "").split():
                correct.append(bool(DATA_CORRECT.search(match.group(0))))
        if len(correct) != 2 or sum(correct) != 1:
            return None
        slots.append(correct.index(True))
    return slots


# The tutor announcing they will read the visible model first, in either
# language. English's own `pilot_operating_issues` already refuses this, but it
# refuses it with an English regex, so the rule stopped at the language border —
# and Korean spent a week with three different answers for one page type.
TUTOR_READS_MODEL = re.compile(
    r"\bI(?:['’]ll| will) read\b"
    r"|제가\s*(?:먼저\s*)?(?:한\s*줄씩\s*)?읽"
    r"|먼저\s*제가\s*읽"
    r"|따라\s*읽어",
    re.I,
)


def learner_reads_model_issues(page_chunks):
    """On a page whose models are already printed, the learner reads them.

    Not the tutor first and the learner after. The model is visible and the
    learner can decode it, so the first round spends class time re-doing what
    the page already did — and `ux-philosophy.md` allows exactly two exceptions,
    a sound the learner cannot yet produce and a dialogue where the two hold
    different roles. Neither is a `-read` page: those are four printed model
    sentences with nothing to distinguish and nobody to play.
    """
    errors = []
    for page_id, chunk in page_chunks.items():
        if not re.fullmatch(r"p[12]-read", page_id):
            continue
        subtitles = SUBTITLE.findall(chunk)
        if not subtitles:
            continue
        spoken = SPAN_KO.search(subtitles[0][1])
        if spoken and TUTOR_READS_MODEL.search(plain_text(spoken.group(1))):
            errors.append(
                f"{page_id}: the tutor reads the model before the learner — the "
                "model is already on screen, so the learner reads it. Invite them "
                "to read it themselves instead"
            )
    return errors


def choice_position_issues(page_chunks):
    """Require the answer to move down the page in a way position cannot predict.

    A choice row asks the learner to read a sentence and decide.  The moment the
    correct option sits in the same slot every time, the sentence stops being
    read at all: the learner discovers on row two that the left pill is always
    right and taps four times without looking, scoring full marks having learned
    nothing.  `choice_branch_coverage_issues` does not catch this — it compares
    the option *strings*, so a page can alternate two genuinely different
    branches and still park the correct one on the left every row.

    Alternating is the same defect one step later.  Left, right, left, right is
    a rule the learner picks up just as fast, and picking it up is more
    rewarding than reading, so it displaces the reading sooner.  Anything the
    previous row does not predict is fine; the sequence does not have to be
    random, only unlearnable at a glance.

    Only two-option pages with three or more rows are judged: two rows cannot
    establish a pattern, and a page whose rows differ in width has no consistent
    position to be answerable by.
    """
    errors = []
    for page_id, chunk in page_chunks.items():
        if not re.fullmatch(r"p[12]-choose", page_id) or not CHOICE_LIST.search(chunk):
            continue
        slots = choice_row_correct_slots(chunk)
        if slots is None or len(slots) < 3:
            continue
        sequence = " ".join(("left", "right")[slot] for slot in slots)
        if len(set(slots)) == 1:
            errors.append(
                f"{page_id}: the correct option is on the {('left', 'right')[slots[0]]} "
                f"in every row ({sequence}) — the page can be answered by position "
                "without reading it. Move the correct option so its slot changes "
                "down the page"
            )
        elif all(a != b for a, b in zip(slots, slots[1:])):
            errors.append(
                f"{page_id}: the correct option alternates slot on every row "
                f"({sequence}) — position is still the answer, one step later. "
                "Break the alternation so a row cannot be answered from the one "
                "above it"
            )
    return errors


EXEMPLAR_TOKEN = re.compile(r"[\w'’-]+|[^\w\s]")
# Levels whose band is defined as pre-generative, in either track's vocabulary.
PRE_GENERATIVE_LEVELS = {"pre-a1", "왕초급"}


def exemplar_varying_regions(sentences):
    """Align the exemplars and return each one's varying token span.

    The shared prefix and suffix are the fixed frame; what is left in the
    middle is the part the learner actually has to supply.
    """
    rows = [EXEMPLAR_TOKEN.findall(s) for s in sentences]
    shortest = min(len(r) for r in rows)
    head = 0
    while head < shortest and len({r[head].casefold() for r in rows}) == 1:
        head += 1
    tail = 0
    while tail < shortest - head and len({r[len(r) - 1 - tail].casefold() for r in rows}) == 1:
        tail += 1
    return [r[head:len(r) - tail] for r in rows]


def exemplar_variation_issues(page_chunks, *, level):
    """Require a teaching set to vary in more than one word.

    Four exemplars that differ in exactly one aligned token are a substitution
    drill, not a pattern: the learner swaps a noun into a frame that never
    changes shape. Usage-based work on construction learning is explicit that
    this is worse than merely unhelpful — high token frequency with *low* type
    frequency inhibits generalisation, because the exemplars form a tight
    cluster and get stored as one phrase instead of a slot (Bybee 1995; Suttle
    and Goldberg 2011). `teaching-philosophy.md` §2 already requires "several
    natural completions"; this is that requirement made checkable.

    Pre-A1 is exempt. The CEFR Companion Volume defines that band as one where
    the learner "has not yet acquired generative capacity, but relies upon a
    repertoire of words and formulaic expressions", so a rehearsed set is the
    intended experience there. From A1 — "the lowest level of generative
    language use ... rather than relying purely on a very finite rehearsed,
    lexically organised repertoire of situation-specific phrases" — it is a
    defect.

    Korean decks do not band by CEFR; they band 왕초급 · 초급 · 초중급 · 중급 ·
    중고급 · 고급. 왕초급 is that same pre-generative band under another name —
    the learner is still assembling a rehearsed repertoire and has no slot to
    generalise into — so it is exempt for the identical reason, and 초급 upward
    is not.

    Only the `-read` pages are checked. `-teach` draws its examples from the
    same authored rows, so checking both would report one defect twice.
    """
    if (level or "").strip().casefold() in PRE_GENERATIVE_LEVELS:
        return []
    errors = []
    for page_id, chunk in page_chunks.items():
        if not re.fullmatch(r"p[12]-read", page_id):
            continue
        # class_span_bodies counts nesting; a plain regex stops at the first
        # </span> and silently truncates every sentence to its taught span.
        sentences = [plain_text(body) for body in class_span_bodies(chunk, "korean")]
        sentences = [s for s in sentences if s]
        if len(sentences) < 3:
            continue
        varying = exemplar_varying_regions(sentences)
        if max(len(span) for span in varying) > 1:
            continue
        # A page may declare that its frame is honestly fixed, the same way a
        # three-chip reorder declares `data-chunk-review="meaningful"`. The case
        # this exists for is a first-course lesson whose only available subject
        # is the first person: varying the frame there would spend grammar a
        # later lesson owns, and the noun swap really is the lesson. Writing the
        # marker is the author saying so on the record — it is not a way to make
        # the check quiet, and a page that could vary its frame must.
        if 'data-exemplar-review="frame-fixed"' in chunk:
            continue
        swapped = ", ".join(" ".join(span) or "—" for span in varying)
        errors.append(
            f"{page_id}: the exemplars differ in one word only ({swapped}) — "
            "a substitution drill entrenches the frame as a phrase instead of "
            "teaching the slot. Vary the form the pattern actually alternates "
            "(subject and agreement, a/an, singular/plural, tense), not just the noun"
        )
    return errors


def reorder_norm(source):
    """Normalize exactly like shared/js/activities.js before grading."""
    plain = html_lib.unescape(TAG.sub("", source))
    return re.sub(r"[\s　?？.。!！,、·~〜…]", "", plain)


def plain_text(source):
    """Collapse markup and whitespace for human-language comparisons."""
    return re.sub(r"\s+", " ", html_lib.unescape(TAG.sub("", source))).strip()


def reorder_solvability_errors(page_id, chunk):
    """Find English reorder task blocks whose chips cannot build data-a."""
    errors = []
    for block in TASK_BLOCK.split(chunk)[1:]:
        zone = None
        for match in SPAN_OPEN.finditer(block):
            attrs = {key.lower(): value for key, _, value in ATTRIBUTE.findall(match.group(0))}
            classes = attrs.get("class", "").split()
            if "build-zone" in classes and attrs.get("data-sync-kind") == "order":
                zone = (match, attrs)
                break
        if zone is None:
            continue

        match, attrs = zone
        sync_id = attrs.get("data-sync-id", "unnamed reorder")
        if "data-a" not in attrs:
            errors.append(f"{page_id}: {sync_id} reorder build-zone has no data-a")
            continue

        chips = []
        for choice in SPAN_OPEN.finditer(block, match.end()):
            choice_attrs = {
                key.lower(): value for key, _, value in ATTRIBUTE.findall(choice.group(0))
            }
            if "choice" in choice_attrs.get("class", "").split():
                raw = plain_text(span_body(block, choice.end()))
                word = raw.strip(".,?!").casefold()
                if not raw or re.fullmatch(r"[^A-Za-z0-9]+", raw):
                    errors.append(
                        f"{page_id}: {sync_id} has punctuation-only chip {raw!r} — "
                        "attach punctuation to a meaning chunk"
                    )
                elif word in BOUND_REORDER_CHIPS:
                    errors.append(
                        f"{page_id}: {sync_id} has bound-word chip {raw!r} — "
                        "attach it to the phrase it belongs to"
                    )
                chips.append(reorder_norm(raw))

        if not chips:
            errors.append(f"{page_id}: {sync_id} reorder build-zone has no chips")
            continue

        answer = reorder_norm(attrs["data-a"])
        if not any("".join(order) == answer for order in permutations(chips)):
            errors.append(
                f"{page_id}: {sync_id} chips cannot reconstruct data-a "
                f"(answer={answer!r}, chips={chips!r})"
            )
    return errors


class _PhraseInputParser(HTMLParser):
    """Track real ancestors of editable phrase fields in static markup."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.issues = []

    def handle_starttag(self, tag, attrs):
        classes = set(dict(attrs).get("class", "").split())
        if "phrase-input" in classes:
            ancestors = set().union(*(item[1] for item in self.stack)) if self.stack else set()
            if "answer-box" not in ancestors or not ({"answer-fill", "answer-space"} & ancestors):
                self.issues.append(
                    "phrase-input is outside the canonical answer-box with an "
                    "answer-fill/answer-space wrapper"
                )
        if tag not in self.VOID:
            self.stack.append((tag, classes))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return


def phrase_input_structure_issues(source):
    parser = _PhraseInputParser()
    parser.feed(source)
    return parser.issues


def article_structure_issues(chunk):
    """Return errors/warnings for one English Freetalking pre-study article."""
    errors, warnings = [], []
    subtitles = SUBTITLE.findall(chunk)
    script = SPAN_KO.search(subtitles[0][1]) if subtitles else None
    if not script:
        errors.append("article: missing English tutor script")
    else:
        spoken = html_lib.unescape(TAG.sub("", script.group(1))).strip()
        if len(sentences(script.group(1), EN_END, spaced=True)) != 1 or not spoken.endswith("?"):
            errors.append(
                "article: class script must be one question asking whether the learner "
                "has questions about the pre-study article"
            )
        if "question" not in spoken.casefold():
            errors.append("article: class script must ask whether the learner has questions")
        if ARTICLE_COACHING.search(spoken):
            errors.append(
                "article: class script coaches page use or in-class reading — ask only "
                "whether the learner has questions"
            )
    rows = SENT_ROW.split(chunk)[1:]
    if not 10 <= len(rows) <= 15:
        errors.append(
            f"article: {len(rows)} sentence rows — use 10 to 15, not a short tutor model"
        )
    for index, row in enumerate(rows, start=1):
        keys = len(S_KEY.findall(row))
        words = len(S_WORD.findall(row))
        if keys != words:
            errors.append(
                f"article row {index}: {keys} highlighted item(s) but {words} gloss(es)"
            )
        if words > 2:
            warnings.append(
                f"article row {index}: {words} glosses — zero to two is normal; "
                "confirm every item can genuinely block comprehension"
            )
    return errors, warnings


def freetalk_question_note_issues(page_id, chunk):
    """Require follow-up-only private notes on Freetalking question pages."""
    errors = []
    note = TUTOR_NOTE_OPEN.search(chunk)
    cap = TN_CAP.search(chunk, note.end()) if note else None
    if not note or not cap:
        return [f"{page_id}: tutor note must contain a Follow up list"]

    preamble = html_lib.unescape(TAG.sub("", chunk[note.end():cap.start()])).strip()
    if preamble:
        errors.append(
            f"{page_id}: tutor note has coaching before the follow-ups — question-page "
            "notes contain follow-up questions only"
        )

    feedback_start = chunk.find('<div class="fb"', cap.end())
    note_tail = chunk[cap.end():feedback_start if feedback_start >= 0 else len(chunk)]
    followups = [plain_text(body) for body in LIST_ITEM_BODY.findall(note_tail)]
    count = len(followups)
    if not 2 <= count <= 3:
        errors.append(f"{page_id}: tutor note has {count} follow-ups — use two or three")
    for index, followup in enumerate(followups, start=1):
        if not followup.endswith("?"):
            errors.append(
                f"{page_id}: follow-up {index} is not a question: {followup!r}"
            )

    normalized = [re.sub(r"[^a-z0-9]+", " ", item.casefold()).strip() for item in followups]
    duplicates = [item for item, number in Counter(normalized).items() if item and number > 1]
    if duplicates:
        errors.append(f"{page_id}: duplicate follow-up question(s)")

    subtitles = SUBTITLE.findall(chunk)
    script = SPAN_KO.search(subtitles[0][1]) if subtitles else None
    if script:
        spoken = plain_text(script.group(1))
        if spoken.count("?") + spoken.count("？") > 1:
            errors.append(
                f"{page_id}: printed prompt contains more than one question — keep one "
                "talking job on the page and move the rest to follow-ups"
            )
        main_question = re.sub(
            r"[^a-z0-9]+", " ", spoken.casefold()
        ).strip()
        if main_question and main_question in normalized:
            errors.append(f"{page_id}: a follow-up repeats the printed question")
    return errors


def freetalk_tutor_language_issues(html):
    """Tutor-only guidance in every English track must not use Japanese or Korean."""
    errors = []
    blocks = (
        TUTOR_NOTE_BLOCK.findall(html)
        + OPT_NOTE_BLOCK.findall(html)
        + FB_ADDS_BLOCK.findall(html)
    )
    for index, body in enumerate(blocks, start=1):
        if NON_ENGLISH_SCRIPT.search(plain_text(body)):
            errors.append(
                f"tutor-only block {index}: contains Japanese or Korean script — "
                "English-course tutor guidance is written for English-speaking tutors"
            )
    return errors


def pattern_meaning_issues(page_id, chunk):
    """Keep English meaning/use boxes to one concise bilingual sentence."""
    errors = []
    for cls, body in SUBTITLE.findall(chunk):
        if "pattern-meaning" not in cls:
            continue
        en, ja = SPAN_KO.search(body), SPAN_JA.search(body)
        if not en or not ja:
            errors.append(f"{page_id}: pattern-meaning needs English and Japanese lines")
            continue
        en_count = len(sentences(en.group(1), EN_END, spaced=True))
        ja_count = len(sentences(ja.group(1), JA_END, spaced=False))
        if en_count != 1 or ja_count != 1:
            errors.append(
                f"{page_id}: pattern-meaning must be one concise sentence per language "
                f"(EN={en_count} JA={ja_count})"
            )
        if NON_ENGLISH_SCRIPT.search(plain_text(en.group(1))):
            errors.append(f"{page_id}: Japanese or Korean appears in the English tutor line")
        if re.search(r"\b(?:CORE|CTX|FT)[- ]?\d+\b|\blesson\s+\d+\b", plain_text(en.group(1)), re.I):
            errors.append(f"{page_id}: lesson-number reference in learner/tutor-facing copy")
        if PATTERN_MEANING_OPERATION.search(plain_text(en.group(1))):
            errors.append(
                f"{page_id}: pattern-meaning mixes teaching copy with an activity "
                "instruction — keep meaning/use in the blue line and the learner "
                "operation in the tutor note or activity page"
            )
    return errors


def core_production_issues(page_chunks):
    """Protect the production ladder established by the approved Core pilots."""
    errors = []
    controlled_frames = {
        answer
        for page_id in ("p1-fill", "p2-fill")
        for answer in control_answers(page_chunks.get(page_id, ""), "slot-input")
    }
    roleplay_pages = ("p3-model", "p3-complete", "in-the-wild")
    for page_id in roleplay_pages:
        chunk = page_chunks.get(page_id)
        if not chunk:
            continue
        turns = len(TURN_OPEN.findall(chunk))
        profiles = len(PROFILE_AVATAR.findall(chunk))
        if turns and profiles != turns:
            errors.append(
                f"{page_id}: roleplay has {turns} turns but {profiles} profile images — "
                "use a profile image for every roleplay turn"
            )

    model = page_chunks.get("p3-model", "")
    complete = page_chunks.get("p3-complete", "")
    if model and complete:
        model_turns = len(TURN_OPEN.findall(model))
        complete_turns = len(TURN_OPEN.findall(complete))
        if model_turns and not 5 <= model_turns <= 7:
            errors.append(
                "p3-model: Core conversation has "
                f"{model_turns} turns — use a purposeful 5–7-turn exchange with an "
                "opening, answer-dependent follow-up and resolved ending"
            )
        if model_turns != complete_turns:
            errors.append(
                "p3-complete: turn count differs from p3-model "
                f"(model={model_turns} complete={complete_turns}) — replay the same conversation"
            )
        if partner_turns(model) != partner_turns(complete):
            errors.append(
                "p3-complete: partner lines differ from p3-model — replay the exact "
                "conversation instead of shortening or rewriting the partner turns"
            )
        if model_turns and not ENDING.search(model):
            errors.append("p3-model: missing mirrored target highlights")
        learner_input_turns = [
            turn for turn in re.split(r'(?=<div class="turn\b)', complete)
            if re.match(r'<div class="turn me"', turn) and PHRASE_INPUT.search(turn)
        ]
        uncued_turns = sum(not TARGET.search(turn) for turn in learner_input_turns)
        if uncued_turns:
            errors.append(
                "p3-complete: each learner completion turn needs an exact Japanese .target "
                f"(uncued turns={uncued_turns})"
            )

    if controlled_frames:
        for page_id in ("p3-complete", "in-the-wild"):
            for answer in control_answers(page_chunks.get(page_id, ""), "phrase-input"):
                if answer not in controlled_frames:
                    errors.append(
                        f"{page_id}: phrase input {answer!r} is not an exact controlled "
                        "target — keep scene facts and slot vocabulary visible outside "
                        "the editable field"
                    )

    freetalk = page_chunks.get("p3-freetalk", "")
    if freetalk:
        turns = len(TURN_OPEN.findall(freetalk))
        speakers = len(WHO_OPEN.findall(freetalk))
        if turns < 3:
            errors.append(
                "p3-freetalk: Free Talk needs a reciprocal Tutor/Me exchange — "
                "tutor asks, learner answers and asks back, tutor gives a real answer"
            )
        if turns != speakers:
            errors.append(
                f"p3-freetalk: {turns} turns but {speakers} speaker labels — "
                "show Tutor or Me on every live turn"
            )
        if GENERIC_CORE_FREETALK.search(plain_text(freetalk)):
            errors.append(
                "p3-freetalk: generic production instruction — print the actual target "
                "scaffold, ask-back question, and tutor-answer label"
            )
        prompts = partner_turns(freetalk)
        if not prompts:
            subtitles = SUBTITLE.findall(freetalk)
            script = SPAN_KO.search(subtitles[0][1]) if subtitles else None
            if script:
                prompts = [plain_text(script.group(1))]
        if not prompts or not prompts[0].rstrip().endswith("?"):
            errors.append(
                "p3-freetalk: first Tutor turn must be a real relevant question"
            )
        elif CONTEXTUAL_ROLEPLAY_AS_FREETALK.search(prompts[0]):
            errors.append(
                "p3-freetalk: first Tutor question is disguised pattern production "
                "or roleplay — ask a personal, preference, or experience question"
            )
        learner_questions = []
        for turn in re.split(r'(?=<div class="turn\b)', freetalk):
            if not re.match(r'<div class="turn me"', turn):
                continue
            learner_questions.extend(
                plain_text(body)
                for class_name in ("korean", "answer-label")
                for body in class_span_bodies(turn, class_name)
                if "?" in plain_text(body) or "？" in plain_text(body)
            )
        if not learner_questions:
            errors.append(
                "p3-freetalk: learner needs a visible natural ask-back question"
            )
        if FORCED_FREETALK_FRAME.search(prompts[0] if prompts else plain_text(freetalk)):
            errors.append(
                "p3-freetalk: do not force today's frame in Free Talk — invite it "
                "only when it fits the real conversation"
            )
        errors.extend(live_tutor_answer_issues("p3-freetalk", freetalk))
    return errors


def core_canonical_shape_issues(page_chunks):
    """Reject the exact structural shortcuts that made generated Core pages hollow.

    This is intentionally narrower than pedagogical proofreading. It proves the
    canonical teaching and closing components are present; a human still has to
    judge whether their content is useful, natural, and sequenced well.
    """
    errors = []
    ordered = list(page_chunks)
    if not ordered or ordered[-1] != "native-tip":
        errors.append("Core lesson must end with native-tip")

    required = (
        "lesson-goal",
        "part1-intro",
        "p1-teach",
        "p1-read",
        "p1-rule",
        "p1-fill",
        "p1-translate",
        "p1-write",
        "part2-intro",
        "p2-teach",
        "p2-read",
        "p2-rule",
        "p2-fill",
        "p2-translate",
        "p2-write",
        "part3-intro",
        "p3-model",
        "p3-complete",
        "p3-freetalk",
        "in-the-wild",
        "native-tip",
    )
    missing = [page_id for page_id in required if page_id not in page_chunks]
    if missing:
        errors.append("Core lesson is missing canonical pages: " + ", ".join(missing))

    for part in (1, 2):
        choose_id = f"p{part}-choose"
        choose = page_chunks.get(choose_id, "")
        if (
            choose
            and "word-choice-list" not in choose
            and 'data-choice-scope="whole-sentence"' not in choose
        ):
            errors.append(
                f"{choose_id}: choose at the smallest meaningful unit with .word-choice; "
                "full-sentence options require an explicit data-choice-scope=\"whole-sentence\" "
                "because the alternatives genuinely differ across the whole sentence"
            )

        teach_id = f"p{part}-teach"
        teach = page_chunks.get(teach_id, "")
        if not teach:
            errors.append(f"{teach_id}: missing canonical teaching page")
        else:
            if "pattern-meaning" not in teach:
                errors.append(f"{teach_id}: missing meaning-and-use block")
            if class_tag_count(teach, "sent-hero") != 1:
                errors.append(f"{teach_id}: needs one main pattern block (.sent-hero)")
            if class_tag_count(teach, "sent-more") != 1:
                errors.append(f"{teach_id}: needs the canonical example block (.sent-more)")
            models = len(class_span_bodies(teach, "korean"))
            if models != 3:
                errors.append(
                    f"{teach_id}: expected one main model plus two examples, found {models}"
                )

        rule_id = f"p{part}-rule"
        rule = page_chunks.get(rule_id, "")
        if not rule:
            errors.append(f"{rule_id}: missing visual formation page")
        elif not (
            class_tag_count(rule, "batchim", "ending-rule")
            or class_tag_count(rule, "irregular-pair-grid")
        ):
            errors.append(
                f"{rule_id}: prose/examples are not a formation diagram — use the "
                "canonical visual rule component"
            )

    native = page_chunks.get("native-tip", "")
    if not native:
        errors.append("native-tip: missing final adjacent-use page")
    else:
        text = plain_text(native)
        if "Two useful extras" in text or "使える表現" in text:
            errors.append(
                "native-tip: generic extra expressions are not a native tip — teach "
                "one adjacent register, softening, contraction, prosody, collocation, "
                "or intensity choice"
            )
        if not (
            class_tag_count(native, "nuance-compare")
            or 'data-native-tip-kind=' in native
        ):
            errors.append(
                "native-tip: mark a real adjacent-use component with .nuance-compare "
                "or data-native-tip-kind"
            )
    return errors


def smallest_unit_choice_issues(page_chunks):
    """Catch the mechanical forms of whole-sentence choices.

    Whether a contrast is pedagogically worthwhile still requires proofreading.
    This gate prevents a generator from hiding an entire sentence inside each
    option when the stable sentence frame should be printed once around it.
    """
    errors = []
    for page_id, chunk in page_chunks.items():
        if "word-choice-list" not in chunk:
            continue
        for index, body in enumerate(class_span_bodies(chunk, "opt"), start=1):
            option = plain_text(body)
            words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", option)
            if re.search(r"[.!?]$", option) or len(words) > 3:
                errors.append(
                    f"{page_id}: option {index} {option!r} is sentence-sized — print "
                    "the stable sentence once and make only the smallest teachable unit selectable"
                )
    return errors


def contextual_production_issues(page_chunks, *, enforce_frame_boundaries=True):
    """Protect roleplay identity and English-only tutor operability."""
    errors = []
    controlled_frames = {
        answer
        for page_id in ("p1-fill", "p2-fill")
        for answer in control_answers(page_chunks.get(page_id, ""), "slot-input")
    }
    for page_id in ("scene", "p3-model", "p3-complete", "transfer-scene"):
        chunk = page_chunks.get(page_id, "")
        if not chunk:
            continue
        turns = len(TURN_OPEN.findall(chunk))
        profiles = len(PROFILE_AVATAR.findall(chunk))
        if turns and profiles != turns:
            errors.append(
                f"{page_id}: roleplay has {turns} turns but {profiles} profile images — "
                "use a profile image for every scene character"
            )

    situation = page_chunks.get("situation-card", "")
    if situation:
        cast = class_tag_count(situation, "cast-row")
        profiles = len(PROFILE_AVATAR.findall(situation))
        if cast and profiles != cast:
            errors.append(
                f"situation-card: {cast} cast rows but {profiles} profile images — "
                "the cast must match the roleplay"
            )

    model = page_chunks.get("p3-model", "")
    complete = page_chunks.get("p3-complete", "")
    scene = page_chunks.get("scene", "")
    scene_turns = len(TURN_OPEN.findall(scene)) if scene else 0
    if scene_turns and not 5 <= scene_turns <= 9:
        errors.append(
            f"scene: Contextual conversation has {scene_turns} turns — use a "
            "purposeful 5–9-turn scene with setup, response and resolution"
        )
    if model and complete:
        model_turns = len(TURN_OPEN.findall(model))
        complete_turns = len(TURN_OPEN.findall(complete))
        if scene_turns and model_turns != scene_turns:
            errors.append(
                "p3-model: turn count differs from the opening scene "
                f"(scene={scene_turns} model={model_turns}) — replay the complete scene"
            )
        if model_turns != complete_turns:
            errors.append(
                "p3-complete: turn count differs from p3-model "
                f"(model={model_turns} complete={complete_turns})"
            )
        if partner_turns(model) != partner_turns(complete):
            errors.append(
                "p3-complete: partner lines differ from p3-model — replay the exact "
                "conversation instead of shortening or rewriting the partner turns"
            )
        learner_input_turns = [
            turn for turn in re.split(r'(?=<div class="turn\b)', complete)
            if re.match(r'<div class="turn me"', turn) and PHRASE_INPUT.search(turn)
        ]
        uncued_turns = sum(not class_tag_count(turn, "target") for turn in learner_input_turns)
        if uncued_turns:
            errors.append(
                "p3-complete: each learner completion turn needs an exact Japanese .target "
                f"(uncued turns={uncued_turns})"
            )

    live = page_chunks.get("p3-freetalk", "")
    if live:
        turns = len(TURN_OPEN.findall(live))
        icons = len(GENERIC_AVATAR.findall(live))
        profiles = len(PROFILE_AVATAR.findall(live))
        if turns < 3:
            errors.append(
                "p3-freetalk: Free Talk needs a reciprocal Tutor/Me exchange — "
                "tutor asks, learner answers and asks back, tutor gives a real answer"
            )
        if turns and (icons != turns or profiles):
            errors.append(
                f"p3-freetalk: live Tutor/Me exchange needs generic icons on every turn "
                f"(turns={turns} icons={icons} profiles={profiles})"
            )
        prompts = partner_turns(live)
        if not prompts or not prompts[0].rstrip().endswith("?"):
            errors.append(
                "p3-freetalk: first Tutor turn must be an actual relevant question — "
                "do not label an imperative or another roleplay-production task Free Talk"
            )
        elif CONTEXTUAL_ROLEPLAY_AS_FREETALK.search(prompts[0]):
            errors.append(
                "p3-freetalk: first Tutor question is another scripted roleplay-production "
                "task — ask an interesting personal, preference, or experience question instead"
            )
        learner_questions = []
        for turn in re.split(r'(?=<div class="turn\b)', live):
            if not re.match(r'<div class="turn me"', turn):
                continue
            learner_questions.extend(
                plain_text(body)
                for class_name in ("korean", "answer-label")
                for body in class_span_bodies(turn, class_name)
                if "?" in plain_text(body) or "？" in plain_text(body)
            )
        if not learner_questions:
            errors.append(
                "p3-freetalk: learner needs a visible natural ask-back question"
            )
        if FORCED_FREETALK_FRAME.search(prompts[0] if prompts else plain_text(live)):
            errors.append(
                "p3-freetalk: do not force today's frame in Free Talk — invite it "
                "only when it fits the real conversation"
            )
        errors.extend(live_tutor_answer_issues("p3-freetalk", live))

    transfer = page_chunks.get("transfer-scene", "")
    if transfer:
        learner_input_turns = [
            turn for turn in re.split(r'(?=<div class="turn\b)', transfer)
            if re.match(r'<div class="turn me"', turn) and PHRASE_INPUT.search(turn)
        ]
        uncued_turns = sum(not class_tag_count(turn, "target") for turn in learner_input_turns)
        if uncued_turns:
            errors.append(
                "transfer-scene: each learner completion turn needs an exact Japanese .target "
                f"(uncued turns={uncued_turns})"
            )

    if enforce_frame_boundaries and controlled_frames:
        for page_id in ("p3-complete", "transfer-scene"):
            for answer in control_answers(page_chunks.get(page_id, ""), "phrase-input"):
                if answer not in controlled_frames:
                    errors.append(
                        f"{page_id}: phrase input {answer!r} is not an exact controlled "
                        "frame — keep scene facts and slot vocabulary visible outside "
                        "the editable field"
                    )

    understand = page_chunks.get("understand", "")
    if understand:
        rows = class_tag_count(understand, "choose-row", "receptive-choice")
        options = class_tag_count(understand, "opt")
        english_senses = class_tag_count(understand, "choice-en")
        if rows != 4:
            errors.append(
                f"understand: expected four receptive meaning checks, found {rows}"
            )
        if options != english_senses:
            errors.append(
                "understand: every meaning option needs a concise English sense label "
                f"for the tutor (options={options} English labels={english_senses})"
            )
    return errors


def freetalk_inventory_issues(source):
    """Require the canonical 13-page Freetalking order with no stale page kind."""
    actual = [page_id for page_id, _ in pages(source)]
    if actual == FREETALK_PAGES:
        return []
    return [
        "Freetalking page inventory/order must be "
        + " > ".join(FREETALK_PAGES)
        + "; got "
        + " > ".join(actual)
    ]


def freetalk_style_issues(chunk):
    """Keep the approved direct style-selection wording and option order."""
    errors = []
    subtitles = SUBTITLE.findall(chunk)
    body = subtitles[0][1] if subtitles else ""
    en, ja = SPAN_KO.search(body), SPAN_JA.search(body)
    spoken = plain_text(en.group(1)) if en else ""
    support = plain_text(ja.group(1)) if ja else ""
    if spoken != FREETALK_STYLE_EN or support != FREETALK_STYLE_JA:
        errors.append(
            "lesson-style: use the canonical direct script and Japanese support from the "
            "Freetalking blueprint"
        )

    discussion = chunk.find("Discussion first")
    correction = chunk.find("Correction first")
    if discussion < 0 or correction < 0 or discussion > correction:
        errors.append(
            "lesson-style: options must be Discussion first, then Correction first"
        )
    if "Fluency first" in chunk:
        errors.append("lesson-style: use Discussion first, not Fluency first")
    return errors


def freetalk_conversation_issues(page_chunks):
    """Protect the question pool from becoming a scripted interview."""
    errors = []
    intro = page_chunks.get("talk-intro", "")
    if intro:
        subtitles = SUBTITLE.findall(intro)
        body = subtitles[0][1] if subtitles else ""
        english = SPAN_KO.search(body)
        spoken = plain_text(english.group(1)).casefold() if english else ""
        note = plain_text(" ".join(TUTOR_NOTE_BLOCK.findall(intro))).casefold()
        if not (
            "every question" in spoken
            and "interesting" in spoken
            and "react" in note
            and "share" in note
            and "skip" in note
        ):
            errors.append(
                "talk-intro: frame the pages as a flexible question pool; follow the "
                "learner's most interesting answer, react or share briefly, and skip freely"
            )

    prompts = {}
    followup_sets = {}
    for page_id in FREETALK_QUESTION_PAGES:
        chunk = page_chunks.get(page_id, "")
        if not chunk:
            continue
        subtitles = SUBTITLE.findall(chunk)
        body = subtitles[0][1] if subtitles else ""
        english = SPAN_KO.search(body)
        prompt = plain_text(english.group(1)) if english else ""
        if prompt.count("?") > 1:
            errors.append(
                f"{page_id}: visible prompt contains {prompt.count('?')} questions — "
                "give the learner one clear talking job and move optional probes to tutor follow-ups"
            )
        key = re.sub(r"[^a-z0-9]+", " ", prompt.casefold()).strip()
        if key:
            if key in prompts:
                errors.append(
                    f"{page_id}: repeats the main prompt from {prompts[key]} — every page "
                    "needs a distinct conversational move"
                )
            else:
                prompts[key] = page_id

        followups = tuple(
            re.sub(r"[^a-z0-9]+", " ", plain_text(item).casefold()).strip()
            for item in LIST_ITEM_BODY.findall(chunk)
            if plain_text(item)
        )
        if followups:
            if followups in followup_sets:
                errors.append(
                    f"{page_id}: repeats the complete follow-up set from "
                    f"{followup_sets[followups]} — write probes for this prompt's actual idea"
                )
            else:
                followup_sets[followups] = page_id
    return errors


def pilot_operating_issues(page_chunks, *, track):
    """Enforce only objective regressions from the owner-approved pilot pass.

    Naturalness, page usefulness and whether a Free Talk tangent is interesting
    remain human decisions. These checks cover markup or exact shared operations
    whose intended behavior is no longer ambiguous.
    """
    errors = []
    goal = page_chunks.get("lesson-goal", "")
    if goal:
        if class_tag_count(goal, "known-row"):
            errors.append(
                "lesson-goal: remove example/outcome rows — state the can-do and "
                "have the learner read the title once"
            )
        subtitles = SUBTITLE.findall(goal)
        english = SPAN_KO.search(subtitles[0][1]) if subtitles else None
        spoken = plain_text(english.group(1)) if english else ""
        if not ("read" in spoken.casefold() and "title" in spoken.casefold()):
            errors.append(
                "lesson-goal: the spoken script must ask the learner to read the title aloud"
            )
        if len(sentences(english.group(1) if english else "", EN_END, spaced=True)) < 2:
            errors.append(
                "lesson-goal: state one useful can-do before asking the learner to "
                "read the title aloud"
            )

    if track == "contextual" and "situation-card" in page_chunks:
        errors.append(
            "situation-card: remove the duplicate overview — use one goal page, then start the scene"
        )

    if track == "contextual" and "scene" in page_chunks:
        scene = page_chunks["scene"]
        subtitles = SUBTITLE.findall(scene)
        english = SPAN_KO.search(subtitles[0][1]) if subtitles else None
        spoken = plain_text(english.group(1)) if english else ""
        explicit_roles = (
            re.search(r"\byou(?:['’]re| are)\b", spoken, re.I)
            and re.search(r"\bI(?:['’]ll be|['’]m| am)\b", spoken, re.I)
        )
        if not explicit_roles:
            errors.append(
                "scene: spoken setup must name the learner's role and tutor's role "
                "explicitly (You're the ...; I'll be the ...)"
            )
        if len(re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?", spoken)) > 30:
            errors.append(
                "scene: role setup is too long — name both roles and begin the roleplay"
            )

    for page_id, chunk in page_chunks.items():
        subtitles = SUBTITLE.findall(chunk)
        body = subtitles[0][1] if subtitles else ""
        en = SPAN_KO.search(body)
        ja = SPAN_JA.search(body)
        spoken = plain_text(en.group(1)) if en else ""
        support = plain_text(ja.group(1)) if ja else ""

        if re.fullmatch(r"p[12]-read|expressions", page_id):
            if "read" not in spoken.casefold() or TUTOR_READS_TARGET.search(spoken):
                errors.append(
                    f"{page_id}: learner reading is the default — tell the learner "
                    "to read the visible English aloud"
                )
        if page_id == "understand":
            note = plain_text(" ".join(TUTOR_NOTE_BLOCK.findall(chunk)))
            explicit_listening = (
                TUTOR_READS_TARGET.search(spoken)
                or ("listen" in spoken.casefold() and "read" in note.casefold())
            )
            if "choose" not in spoken.casefold() or not explicit_listening:
                errors.append(
                    "understand: explicitly say that the tutor reads each English "
                    "line and the learner listens and chooses its meaning"
                )

        if "reorder" in page_id and spoken:
            if spoken != REORDER_SCRIPT_EN or support != REORDER_SCRIPT_JA:
                errors.append(
                    f"{page_id}: use the approved shared reorder script, then have "
                    "the learner say the whole sentence aloud"
                )
        if "translate" in page_id and spoken:
            if spoken != TRANSLATE_SCRIPT_EN or support != TRANSLATE_SCRIPT_JA:
                errors.append(
                    f"{page_id}: use the approved shared translate script"
                )
            note = plain_text(" ".join(TUTOR_NOTE_BLOCK.findall(chunk)))
            if not ("type" in note.casefold() and "complete" in note.casefold()):
                errors.append(
                    f"{page_id}: tell the tutor to type the learner's complete English sentence"
                )
        if re.fullmatch(r"p[12]-fill", page_id) and spoken:
            lower = spoken.casefold()
            if not (
                ("whole sentence" in lower or "whole request" in lower)
                and "missing words" in lower
            ):
                errors.append(
                    f"{page_id}: tell the learner to say the whole sentence, including "
                    "the missing words"
                )
            note = plain_text(" ".join(TUTOR_NOTE_BLOCK.findall(chunk))).casefold()
            if not ("type only" in note and "missing words" in note):
                errors.append(
                    f"{page_id}: tell the tutor to type only the missing words"
                )
        if re.fullmatch(r"p[12]-choose", page_id) and spoken:
            lower = spoken.casefold()
            if not (
                "choose" in lower
                and "read" in lower
                and ("complete sentence" in lower or "whole sentence" in lower)
            ):
                errors.append(
                    f"{page_id}: choosing must end with the learner reading the complete sentence aloud"
                )

        if "fb-task" in chunk:
            errors.append(
                f"{page_id}: remove the repeated task inside the response component"
            )
        if re.fullmatch(r"p[12]-write", page_id) and 'data-fb="' not in chunk:
            errors.append(
                f"{page_id}: capture the learner's spoken answer with the shared feedback "
                "component, without repeating the task inside the response box"
            )
        if re.fullmatch(r"p[12]-write", page_id):
            if not QUOTED_OPEN_FRAME.search(spoken):
                errors.append(
                    f"{page_id}: print the exact target frame in the open-production script"
                )
            if (
                "make your own sentence" in spoken.casefold()
                or GENERIC_OPEN_END.search(spoken)
            ):
                errors.append(
                    f"{page_id}: generic open-production copy does not name the "
                    "communicative job — say what the learner should use the frame to do"
                )
            note = plain_text(" ".join(TUTOR_NOTE_BLOCK.findall(chunk))).casefold()
            if not (
                "learner" in note
                and "aloud" in note
                and ("capture" in note or "type" in note)
            ):
                errors.append(
                    f"{page_id}: have the learner answer aloud before the tutor "
                    "captures or types the sentence"
                )
        for fb_tag in re.findall(r'<div\b[^>]*class="[^"]*\bfb\b[^"]*"[^>]*data-fb="[^"]+"[^>]*>', chunk):
            if 'data-fb-spoken-label="Student\'s sentence"' not in fb_tag:
                errors.append(
                    f"{page_id}: feedback capture must be labelled Student's sentence"
                )

    return errors


def title_identity_issues(source, expected):
    """Keep a deck's first visible title aligned with its authoritative brief."""
    errors = []
    document = DOCUMENT_TITLE.search(source)
    document_text = plain_text(document.group(1)) if document else ""
    if not (
        document_text == f"{expected} — PODO English"
        or document_text.startswith(f"{expected} · ")
    ):
        errors.append(
            f"opening: document title must begin with the brief title {expected!r}"
        )

    visible = TRANSITION_TITLE.search(source)
    visible_body = TITLE_JA.sub("", visible.group(1)) if visible else ""
    visible_text = plain_text(visible_body)
    if visible_text != expected:
        errors.append(
            f"opening: visible title {visible_text!r} does not match the brief title "
            f"{expected!r}"
        )
    return errors


def freetalk_title_issues(source, expected):
    """Backward-compatible name for the shared title identity contract."""
    return title_identity_issues(source, expected)


def catalogue_title_issues(source, expected):
    """Require the three catalogue names a deployed lesson row needs.

    GT_CLASS_COURSE stores BOOK_NAME (ko), EN_BOOK_NAME and JP_BOOK_NAME, and
    the app picks one by the learner's locale — so for this Japanese-market
    track `ja` is the name actually on screen. A deck that ships without them
    reaches the catalogue unnamed, and nothing downstream can invent a title.
    """
    errors = []
    for lang in ("ko", "en", "ja"):
        if not (meta_content(source, f"podo:title-{lang}") or "").strip():
            errors.append(
                f'missing <meta name="podo:title-{lang}"> — the deck is the source '
                f"of its own name in all three catalogue columns"
            )
    written = (meta_content(source, "podo:title-en") or "").strip()
    if expected and written and written != expected:
        errors.append(
            f"podo:title-en {written!r} does not match the brief title {expected!r}"
        )
    return errors


def english_brief_title(path, review_id):
    """Read the generated brief heading for the English track containing path."""
    track = next(
        (part for part in path.parts if part in {
            "1-core-patterns", "2-contextual-english", "3-freetalking"
        }),
        None,
    )
    if not track:
        return None
    brief = REPO / "sandbox/drafts/en" / "tracks" / track / "toc" / f"{review_id}.md"
    if not brief.is_file():
        return None
    first = brief.read_text(encoding="utf-8").splitlines()[0]
    match = BRIEF_HEADING.fullmatch(first)
    if not match or match.group(1) != review_id:
        return None
    return match.group(2)


def freetalk_brief_title(review_id):
    """Read the generated brief heading that mirrors the authoritative TOC."""
    return english_brief_title(
        REPO / "sandbox/drafts/en" / "tracks" / "3-freetalking", review_id
    )


def live_tutor_answer_issues(page_id, chunk):
    """Require an English label on an editable field owned by the tutor."""
    turns = re.split(r'(?=<div class="turn\b)', chunk)
    tutor_inputs = [
        turn for turn in turns
        if re.match(r'<div class="turn other"', turn) and "<textarea" in turn
    ]
    # Small unit tests and legacy fragments may call this helper without the
    # dialogue wrapper; in that case the supplied fragment is the tutor field.
    if not any('<div class="turn' in turn for turn in turns) and "<textarea" in chunk:
        tutor_inputs = [chunk]
    missing = sum("Tutor's answer" not in plain_text(turn) for turn in tutor_inputs)
    if missing:
        return [
            f"{page_id}: {missing} tutor-editable answer field(s) need the English "
            'label "Tutor\'s answer"; Japanese may remain as learner support'
        ]
    return []


def partner_turns(chunk):
    """Return normalized visible partner lines from one dialogue page."""
    lines = []
    for turn in re.split(r'(?=<div class="turn\b)', chunk):
        if not re.match(r'<div class="turn other"', turn):
            continue
        bodies = class_span_bodies(turn, "korean")
        if bodies:
            lines.append(plain_text(bodies[0]))
    return lines


def freetalk_article_lines(source):
    """Return the visible English sentence rows from one Freetalking article."""
    article = dict(pages(source)).get("article", "")
    return [
        plain_text(body)
        for body in re.findall(
            r'<span class="s-ko">(.*?)<span class="s-mark"', article, re.S
        )
    ]


def freetalk_article_glosses(source):
    """Return normalized English glossary heads from one Freetalking article."""
    article = dict(pages(source)).get("article", "")
    return {
        plain_text(body).casefold()
        for body in re.findall(r'<span class="s-w"><b>(.*?)</b>', article, re.S)
    }


def freetalk_pair_issues(decks):
    """Compare full/accessible siblings so simplification changes language, not ideas."""
    groups = {}
    for path in decks:
        if "en" not in path.parts or "3-freetalking" not in path.parts:
            continue
        source = path.read_text(encoding="utf-8")
        review_id = meta_content(source, "podo:review-id")
        level = (meta_content(source, "podo:level") or "").casefold()
        kind = "accessible" if "accessible" in level else "full" if "full" in level else None
        if review_id and kind:
            groups.setdefault(review_id, {})[kind] = (path, source)

    errors, warnings = {}, {}
    for review_id, pair in groups.items():
        if set(pair) != {"full", "accessible"}:
            continue
        full_path, full = pair["full"]
        accessible_path, accessible = pair["accessible"]
        full_lines = freetalk_article_lines(full)
        accessible_lines = freetalk_article_lines(accessible)
        if len(full_lines) != len(accessible_lines):
            errors.setdefault(accessible_path, []).append(
                f"{review_id}: accessible/full articles have different row counts "
                f"({len(accessible_lines)} vs {len(full_lines)}) — preserve the same claims"
            )
        similarity = difflib.SequenceMatcher(
            None, " ".join(full_lines).casefold(), " ".join(accessible_lines).casefold()
        ).ratio()
        # Exact parity is valid when the canonical Full article is already
        # accessible. Warn only about cosmetic rewrites that claim to simplify
        # without materially lowering the load.
        if full_lines != accessible_lines and similarity > 0.90:
            warnings.setdefault(accessible_path, []).append(
                f"{review_id}: accessible article is {similarity:.0%} text-identical to full — "
                "confirm vocabulary and clause load were genuinely lowered"
            )
        full_glosses = freetalk_article_glosses(full)
        accessible_glosses = freetalk_article_glosses(accessible)
        overlap = len(full_glosses & accessible_glosses) / len(full_glosses) if full_glosses else 0
        if overlap > 0.70:
            warnings.setdefault(accessible_path, []).append(
                f"{review_id}: accessible article reuses {overlap:.0%} of the full glossary — "
                "shorter sentences do not compensate for unchanged rare vocabulary"
            )
    return errors, warnings


def check(path):
    """Return (errors, warnings) for one deck."""
    html = path.read_text(encoding="utf-8")
    errs, warns = [], []
    is_english = "sandbox/drafts/en/tracks" in path.as_posix()

    # ---- identity and metadata -------------------------------------------
    if meta_content(html, "google") != "notranslate":
        errs.append("missing <meta name=\"google\" content=\"notranslate\"> — "
                    "Chrome will auto-translate and mangle the mixed content")
    lesson_id = meta_content(html, "podo:lesson-id")
    if lesson_id is None:
        errs.append("missing podo:lesson-id")
    elif "lessons" in path.parts:
        # The id must equal its lesson directory only for a deck placed in a
        # course, which is what the production importer reads. A track-root
        # sample-lesson.html is a cut of the canonical trial deck and has no
        # course directory to match.
        #
        # A draft sits at `lessons/<slug>/lesson.html`, but `promote.py` writes
        # each deck into its own slot — `lessons/<slug>/{lecture,prestudy}/
        # index.html` — so under `courses/` the lesson directory is the
        # grandparent. Comparing against the parent there called every promoted
        # deck in the repo broken (1802 of them), which is how `--all` came to
        # be unusable and why nothing ran the content gate over `courses/`.
        owner = path.parent
        if owner.name in DECK_SLOTS:
            owner = owner.parent
        # A trial source sits flat at `trial/lessons/<name>.html` with no
        # directory of its own, so there is no lesson directory to disagree with.
        if owner.name != "lessons" and lesson_id != owner.name:
            errs.append(f"podo:lesson-id {lesson_id!r} != directory {owner.name!r}")
    review_id = meta_content(html, "podo:review-id")
    if is_english and not (review_id and re.fullmatch(r"(?:CORE|CTX|FT)-\d+", review_id)):
        errs.append("missing or invalid podo:review-id — use the stable TOC id")
    if is_english and meta_content(html, "podo:target-language") != "en":
        errs.append(
            'missing <meta name="podo:target-language" content="en"> — shared '
            "tutor controls will fall back to Korean"
        )
    if (
        is_english
        and review_id
        and meta_content(html, "podo:curriculum-status") != "superseded"
        and path.is_relative_to(REPO / "sandbox/drafts/en" / "tracks")
    ):
        expected_title = english_brief_title(path, review_id)
        if expected_title is None:
            errs.append("deck has no readable generated brief title for its review id")
        else:
            errs.extend(title_identity_issues(html, expected_title))
        errs.extend(catalogue_title_issues(html, expected_title))

    # ---- references resolve ----------------------------------------------
    for ref in sorted(set(LOCAL_REF.findall(html))):
        if not (path.parent / ref).exists():
            errs.append(f"broken ref: {ref}")

    # ---- unique ids -------------------------------------------------------
    for label, rx in (("page", PAGE_ID), ("sync", SYNC_ID)):
        dupes = [k for k, n in Counter(rx.findall(html)).items() if n > 1]
        if dupes:
            errs.append(f"duplicate {label} id(s): {', '.join(sorted(dupes))}")

    # ---- deck ships no CSS or JS of its own -------------------------------
    if INLINE_STYLE.search(html):
        errs.append("inline <style> — component CSS belongs in the shared runtime")
    if INLINE_SCRIPT.search(html):
        errs.append("inline <script> — behaviour belongs in the shared runtime")
    legacy_controls = LEGACY_CONTROL.findall(html)
    if legacy_controls:
        errs.append(
            "runtime-promoted control shell(s): "
            + ", ".join(legacy_controls[:3])
            + " — write the input, textarea, or build-zone directly in HTML"
        )

    # ---- English decks carry no readings ----------------------------------
    if is_english:
        if MODEL_LINES.search(html):
            errs.append(
                "unstyled .model-lines component — use the design-system .model-list "
                "so repeated rows receive the standard vertical gap"
            )
        errs.extend(phrase_input_structure_issues(html))
        for page_id, chunk in pages(html):
            if re.fullmatch(r"p[12]-rule", page_id) and GENERIC_PATTERN_RULE.search(
                plain_text(chunk)
            ):
                errs.append(
                    f"{page_id}: generic rule copy does not explain this pattern — "
                    "write the pattern-specific form/meaning point and show its example"
                )
        body = html.partition("<body>")[2]
        visible_body_source = re.sub(r"<!--.*?-->", "", body, flags=re.S)
        if re.search(r"[가-힣]", visible_body_source):
            errs.append(
                "visible Korean text in an English deck — learner support is Japanese "
                "and tutor operating copy is English"
            )
        if 'class="yomi"' in html:
            errs.append("`.yomi` in an English deck — katakana over English installs "
                        "the error instead of scaffolding the word (see english/AGENTS.md)")
        if re.search(r"<script[^>]*yomi\.js", html):
            errs.append("English deck loads yomi.js")

        # ---- vocabulary ownership and load -------------------------------
        try:
            vocab = vocabulary.parse(html, source=path)
        except vocabulary.VocabularyError as exc:
            errs.append(str(exc).removeprefix(f"{path}: "))
        else:
            if vocab["status"] != "reviewed":
                errs.append(
                    f"vocabulary status is {vocab['status']!r} — classify the deck's "
                    "new, recycled, assumed-known and receptive-only words"
                )
            if not any(vocab["categories"].values()):
                errs.append(
                    "vocabulary ownership is empty — a reviewed authored deck must "
                    "classify the content words it relies on"
                )
            capped_track = any(part in {"1-core-patterns", "2-contextual-english"} for part in path.parts)
            load = vocabulary.load_result(vocab) if capped_track else None
            if load:
                (warns if load[0] == "warning" else errs).append(load[1])
            declared = {
                entry["english"].casefold()
                for entries in vocab["categories"].values()
                for entry in entries
            }
            try:
                hints = vocabulary.hint_words(html)
            except vocabulary.VocabularyError as exc:
                errs.append(str(exc))
            else:
                undeclared = sorted(hints - declared)
                if undeclared:
                    errs.append(
                        "hint-chip vocabulary missing from the ownership declaration: "
                        + ", ".join(undeclared)
                    )

        # Tutor-only operating copy is for English-speaking tutors in every
        # track, not just in Freetalking.
        errs.extend(freetalk_tutor_language_issues(html))
        for page_id, chunk in pages(html):
            errs.extend(pattern_meaning_issues(page_id, chunk))
        page_chunks = dict(pages(html))
        if "1-core-patterns" in path.parts:
            errs.extend(pilot_operating_issues(page_chunks, track="core"))
            errs.extend(target_highlight_issues(page_chunks))
            errs.extend(controlled_target_alignment_issues(page_chunks))
            errs.extend(translation_support_issues(page_chunks))
            errs.extend(core_production_issues(page_chunks))
            proofread_status = meta_content(html, "podo:proofread-status")
            if proofread_status == "pending":
                warns.append(
                    "content proofreading is pending — do not present this deck for owner "
                    "review or include it in a completed batch"
                )
            elif proofread_status == "complete":
                errs.extend(core_canonical_shape_issues(page_chunks))
                errs.extend(smallest_unit_choice_issues(page_chunks))
        if "2-contextual-english" in path.parts:
            errs.extend(pilot_operating_issues(page_chunks, track="contextual"))
            errs.extend(target_highlight_issues(page_chunks))
            errs.extend(controlled_target_alignment_issues(page_chunks))
            errs.extend(translation_support_issues(page_chunks))
            errs.extend(contextual_production_issues(
                page_chunks,
                enforce_frame_boundaries=(
                    meta_content(html, "podo:curriculum-status") != "superseded"
                ),
            ))

    # ---- 0 · variation gates, both languages ------------------------------
    # The pattern tracks of both languages write the same pages: `p1/p2-read`
    # model rows in `<span class="korean">`, `p1/p2-choose` rows of `opt`
    # options marked `data-correct`. Only the container class differs, which
    # CHOICE_LIST absorbs, so these rules are language-neutral and run on
    # every pattern deck rather than on the English ones alone.
    if PATTERN_TRACKS.intersection(path.parts):
        variation_chunks = dict(pages(html))
        errs.extend(choice_branch_coverage_issues(variation_chunks))
        errs.extend(choice_position_issues(variation_chunks))
        errs.extend(learner_reads_model_issues(variation_chunks))
        errs.extend(exemplar_variation_issues(
            variation_chunks, level=meta_content(html, "podo:level")
        ))

    # ---- 1 · tutor script sentence parity ---------------------------------
    for pid, chunk in pages(html):
        for cls, body in SUBTITLE.findall(chunk):
            if "pattern-meaning" in cls:
                continue          # owns its own pairing; script-lines.js skips it
            ko, ja = SPAN_KO.search(body), SPAN_JA.search(body)
            if not (ko and ja):
                continue
            a = sentences(ko.group(1), EN_END if is_english else KO_END,
                          spaced=True)
            b = sentences(ja.group(1), JA_END, spaced=False)
            if len(a) != len(b):
                errs.append(
                    f"{pid}: tutor script sentence counts differ "
                    f"({'EN' if is_english else 'KO'}={len(a)} JA={len(b)}) — script-lines.js "
                    f"will silently leave the box unsplit")

    # ---- 2 · reorder chunking consistency ---------------------------------
    for pid, chunk in pages(html):
        if "reorder" not in pid:
            continue
        blocks = TASK_BLOCK.split(chunk)[1:]
        counts = [len(CHOICE.findall(b)) for b in blocks]
        if not counts:
            continue
        if len(set(counts)) > 1:
            (errs if is_english else warns).append(
                f"{pid}: mixed chip counts {counts} on one page — four is the "
                f"ceiling and working default, three is allowed only when a "
                f"sentence honestly holds three, and the criterion must be the "
                f"same down the page; Korean rows require semantic sign-off")
        elif counts[0] > 4:
            errs.append(f"{pid}: {counts[0]} chips — four is the ceiling")
        elif (
            is_english
            and counts[0] == 3
            and 'data-chunk-review="meaningful"' not in chunk
        ):
            warns.append(
                f"{pid}: three chips per sentence — four is the English working "
                "default; confirm there is genuinely no fourth meaning unit"
            )
        elif counts[0] < 3:
            warns.append(f"{pid}: {counts[0]} chips per sentence — confirm no "
                         f"fourth unit is glued to a neighbour")
        if is_english:
            errs.extend(reorder_solvability_errors(pid, chunk))

    # ---- 4–5 · English Freetalking contracts -----------------------------
    if is_english and "3-freetalking" in path.parts:
        page_chunks = dict(pages(html))
        errs.extend(pilot_operating_issues(page_chunks, track="freetalking"))
        errs.extend(freetalk_conversation_issues(page_chunks))
        errs.extend(freetalk_inventory_issues(html))
        if "article" not in page_chunks:
            errs.append(
                "Freetalking deck is missing data-page-id=\"article\" — page 2 is a "
                "pre-study article, not a tutor-read model story"
            )
        else:
            article_errors, article_warnings = article_structure_issues(
                page_chunks["article"]
            )
            errs.extend(article_errors)
            warns.extend(article_warnings)
        if "lesson-style" not in page_chunks:
            errs.append('Freetalking deck is missing data-page-id="lesson-style"')
        else:
            errs.extend(freetalk_style_issues(page_chunks["lesson-style"]))
        for page_id in sorted(FREETALK_QUESTION_PAGES):
            if page_id not in page_chunks:
                errs.append(f"Freetalking deck is missing question page {page_id!r}")
                continue
            errs.extend(freetalk_question_note_issues(page_id, page_chunks[page_id]))

    return errs, warns


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="deck files or directories to scan")
    ap.add_argument("--all", action="store_true", help="scan every deck in the repo")
    args = ap.parse_args()

    targets = []
    # resolve() so a relative argument still reports a repo-relative path below
    roots = [REPO] if args.all else [pathlib.Path(p).resolve() for p in args.paths]
    if not roots:
        ap.error("give a path, or --all")
    for r in roots:
        if r.is_dir():
            # `sandbox/archive/` is retired experiments — "not part of the read
            # path: never cite one as precedent, never copy markup out of one".
            # The exclusion named `_archive`, a directory that no longer exists,
            # so 46 findings in retired files were counted against every run.
            targets += sorted(p for p in r.rglob("*.html")
                              if not {"_archive", "archive"} & set(p.parts)
                              and p.name != "viewer.html"
                              and not p.name.startswith("_"))
        elif r.exists():
            targets.append(r)
        else:
            print(f"! no such path: {r}", file=sys.stderr)

    decks = [p for p in targets if PAGE_ID.search(p.read_text(encoding="utf-8"))]

    # A deck marked `superseded` is kept as a record of a shape the curriculum
    # moved away from, and it is not promoted into `courses/`. Holding it to the
    # contract it was replaced *for* reports real differences that nobody should
    # act on, and a gate that always prints thirty findings is a gate people
    # learn to ignore. Say it was skipped rather than skipping it silently.
    retired = [d for d in decks
               if meta_content(d.read_text(encoding="utf-8"),
                               "podo:curriculum-status") == "superseded"]
    decks = [d for d in decks if d not in retired]

    pair_errors, pair_warnings = freetalk_pair_issues(decks)
    n_err = n_warn = 0
    for deck in decks:
        errs, warns = check(deck)
        errs.extend(pair_errors.get(deck, []))
        warns.extend(pair_warnings.get(deck, []))
        n_err += len(errs)
        n_warn += len(warns)
        if errs or warns:
            try:
                label = deck.relative_to(REPO)
            except ValueError:
                label = deck
            print(f"\n{label}")
            for e in errs:
                print(f"  ✗ {e}")
            for w in warns:
                print(f"  ! {w}")

    retired_note = f" · {len(retired)} superseded deck(s) skipped" if retired else ""
    print(f"\n{len(decks)} deck(s) checked · {n_err} error(s) · {n_warn} warning(s)"
          + retired_note)
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
