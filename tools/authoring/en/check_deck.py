#!/usr/bin/env python3
"""Static checks for lesson decks — the ones that otherwise fail silently.

    python3 tools/authoring/en/check_deck.py sandbox/drafts/en/tracks            # a tree
    python3 tools/authoring/en/check_deck.py path/to/lesson.html ...   # named decks
    python3 tools/authoring/en/check_deck.py --all                     # every deck in the repo

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
   default. Mixed counts are an error in English authoring. In Korean they are a
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
   completion targets remain visibly connected to their Japanese cues.

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
from itertools import permutations

import vocabulary

REPO = pathlib.Path(__file__).resolve().parents[3]

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
SLOT_INPUT = re.compile(r'<input\b[^>]*class="[^"]*\bslot-input\b')
CONTROL_TAG = re.compile(r'<(?:input|textarea)\b[^>]*>', re.I)
GENERIC_AVATAR = re.compile(r'<span class="[^"]*\bavatar\b[^\"]*\bicon\b')
TAG_OPEN = re.compile(r'<(?:div|span)\b[^>]*>', re.I)
GENERIC_CORE_FREETALK = re.compile(
    r"\b(?:use (?:both|the) (?:comparison )?patterns?|give the status|"
    r"ask the tutor|tutor's real answer)\b",
    re.I,
)
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
            if not en_targets or en_targets != ja_targets:
                errors.append(
                    f"{page_id} row {index}: mirrored target highlights differ "
                    f"(EN={en_targets} JA={ja_targets})"
                )

    for page_id, chunk in page_chunks.items():
        if not re.fullmatch(r"p[12]-fill", page_id):
            continue
        inputs = len(SLOT_INPUT.findall(chunk))
        cues = class_tag_count(chunk, "target")
        if inputs and inputs != cues:
            errors.append(
                f"{page_id}: each controlled blank needs one exact Japanese .target "
                f"(inputs={inputs} targets={cues})"
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
            if (en_targets or ja_targets) and en_targets != ja_targets:
                errors.append(
                    f"{page_id} row {index}: mirrored target highlights differ "
                    f"(EN={en_targets} JA={ja_targets})"
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
                chips.append(reorder_norm(span_body(block, choice.end())))

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
    return errors


def core_production_issues(page_chunks):
    """Protect the production ladder established by the approved Core pilots."""
    errors = []
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
        phrase_inputs = len(PHRASE_INPUT.findall(complete))
        targets = len(TARGET.findall(complete))
        if phrase_inputs and targets != phrase_inputs:
            errors.append(
                "p3-complete: each phrase input needs one exact Japanese .target "
                f"(inputs={phrase_inputs} targets={targets})"
            )

    freetalk = page_chunks.get("p3-freetalk", "")
    if freetalk:
        turns = len(TURN_OPEN.findall(freetalk))
        speakers = len(WHO_OPEN.findall(freetalk))
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
        errors.extend(live_tutor_answer_issues("p3-freetalk", freetalk))
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
        phrase_inputs = len(PHRASE_INPUT.findall(complete))
        targets = class_tag_count(complete, "target")
        if phrase_inputs and phrase_inputs != targets:
            errors.append(
                "p3-complete: each phrase input needs one exact Japanese .target "
                f"(inputs={phrase_inputs} targets={targets})"
            )

    live = page_chunks.get("p3-freetalk", "")
    if live:
        turns = len(TURN_OPEN.findall(live))
        icons = len(GENERIC_AVATAR.findall(live))
        profiles = len(PROFILE_AVATAR.findall(live))
        if turns and (icons != turns or profiles):
            errors.append(
                f"p3-freetalk: live Tutor/Me exchange needs generic icons on every turn "
                f"(turns={turns} icons={icons} profiles={profiles})"
            )
        errors.extend(live_tutor_answer_issues("p3-freetalk", live))

    transfer = page_chunks.get("transfer-scene", "")
    if transfer:
        phrase_inputs = len(PHRASE_INPUT.findall(transfer))
        targets = class_tag_count(transfer, "target")
        if phrase_inputs and phrase_inputs != targets:
            errors.append(
                "transfer-scene: each phrase input needs one exact Japanese .target "
                f"(inputs={phrase_inputs} targets={targets})"
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
    if "<textarea" in chunk and "Tutor's answer" not in chunk:
        return [
            f"{page_id}: tutor-editable answer field needs the English label "
            '"Tutor\'s answer"; Japanese may remain as learner support'
        ]
    return []


def partner_turns(chunk):
    """Return normalized visible partner lines from one dialogue page."""
    return [plain_text(body) for body in OTHER_TURN_LINE.findall(chunk)]


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
        if similarity > 0.90:
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
    elif "lessons" in path.parts and lesson_id != path.parent.name:
        # The id must equal its directory only for a deck placed in a course, which
        # is what the production importer reads. A track-root sample-lesson.html is
        # a cut of the canonical trial deck and has no course directory to match.
        errs.append(f"podo:lesson-id {lesson_id!r} != directory {path.parent.name!r}")
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
            errs.extend(target_highlight_issues(page_chunks))
            errs.extend(core_production_issues(page_chunks))
        if "2-contextual-english" in path.parts:
            errs.extend(target_highlight_issues(page_chunks))
            errs.extend(contextual_production_issues(
                page_chunks,
                enforce_frame_boundaries=(
                    meta_content(html, "podo:curriculum-status") != "superseded"
                ),
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
        elif is_english and counts[0] == 3:
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
            targets += sorted(p for p in r.rglob("*.html")
                              if "_archive" not in p.parts and p.name != "viewer.html")
        elif r.exists():
            targets.append(r)
        else:
            print(f"! no such path: {r}", file=sys.stderr)

    decks = [p for p in targets if PAGE_ID.search(p.read_text(encoding="utf-8"))]
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

    print(f"\n{len(decks)} deck(s) checked · {n_err} error(s) · {n_warn} warning(s)")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
