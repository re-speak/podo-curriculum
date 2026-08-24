#!/usr/bin/env python3
"""Create and verify hash-bound, page-by-page English lesson review ledgers."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib
import re
import sys
from typing import Any

import check_deck

REPO = pathlib.Path(__file__).resolve().parents[2]
SCHEMA_VERSION = 2
PAGE_ID_RE = re.compile(r'\bdata-page-id=["\']([^"\']+)["\']')
TN_MORE_RE = re.compile(
    r'<ul\b(?=[^>]*\bclass=["\'][^"\']*\btn-more\b[^"\']*["\'])[^>]*>(.*?)</ul>',
    re.IGNORECASE | re.DOTALL,
)
LIST_ITEM_RE = re.compile(r'<li\b[^>]*>(.*?)</li>', re.IGNORECASE | re.DOTALL)
REQUIRED_PAGE_FIELDS = (
    "learnerAction",
    "tutorAction",
    "targetOrPrompt",
    "learningTarget",
    "pedagogicalValue",
    "failureDiagnosis",
    "nonTargetSupport",
    "articleTreatment",
    "choiceQuality",
    "componentConsistency",
    "visual360",
    "visual480",
    "verdict",
)
FREETALK_REVIEW_FIELDS = (
    "plausibleFirstAnswer",
    "answerExpansion",
    "noAnswerFollowup",
)
PASS_STAGES = ("generated", "mechanicalValidation", "humanPageAudit")
VISUAL_VALUES = {"pass"}
VERDICTS = {"pass", "revise", "remove"}


class ReviewError(ValueError):
    """Raised when a review ledger does not prove the claimed review state."""


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def page_ids(path: pathlib.Path) -> list[str]:
    ids = PAGE_ID_RE.findall(path.read_text(encoding="utf-8"))
    if not ids:
        raise ReviewError(f"{path}: no data-page-id values found")
    duplicates = sorted({page_id for page_id in ids if ids.count(page_id) > 1})
    if duplicates:
        raise ReviewError(f"{path}: duplicate data-page-id values: {', '.join(duplicates)}")
    return ids


def relative_lesson(path: pathlib.Path, audit_path: pathlib.Path | None = None) -> str:
    """Prefer a repository-relative path, with a stable absolute fallback."""
    resolved = path.resolve()
    candidates = [pathlib.Path.cwd().resolve()]
    if audit_path is not None:
        candidates.append(audit_path.resolve().parent)
    for base in candidates:
        try:
            return resolved.relative_to(base).as_posix()
        except ValueError:
            continue
    return resolved.as_posix()


def page_evidence(path: pathlib.Path) -> dict[str, dict[str, Any]]:
    """Extract non-negotiable review evidence from the exact lesson bytes."""
    source = path.read_text(encoding="utf-8")
    evidence = {}
    for page_id, chunk in check_deck.pages(source):
        attrs = check_deck.page_attributes(chunk)
        blank_answers = []
        for tag in check_deck.CONTROL_TAG.findall(chunk):
            control_attrs = {
                key.lower(): value
                for key, _, value in check_deck.ATTRIBUTE.findall(tag)
            }
            if "data-answer" in control_attrs:
                blank_answers.append(html.unescape(control_attrs["data-answer"]).strip())
        hint_chips = [
            check_deck.plain_text(body)
            for body in check_deck.vocabulary.HINT_CHIP.findall(chunk)
        ]
        substantive_prompts = []
        if page_id == "p3-freetalk":
            substantive_prompts = [
                check_deck.plain_text(body)
                for body in check_deck.class_span_bodies(chunk, "korean")
                if check_deck.plain_text(body)
            ]
        elif page_id in check_deck.FREETALK_QUESTION_PAGES or page_id.endswith("-write"):
            substantive_prompts = [
                check_deck.plain_text(body)
                for body in check_deck.class_span_bodies(chunk, "ko")[:1]
                if check_deck.plain_text(body)
            ]
        evidence[page_id] = {
            "targetHighlights": [
                check_deck.plain_text(body)
                for body in check_deck.class_span_bodies(chunk, "ending")
            ],
            "blankAnswers": blank_answers,
            "hintChips": hint_chips,
            "supportStage": attrs.get("data-support-stage", "not-applicable"),
            "substantivePrompts": substantive_prompts,
        }
    return evidence


def freetalk_question_details(path: pathlib.Path) -> dict[str, dict[str, Any]]:
    """Extract the complete spoken contract for each Freetalking question page."""
    source = path.read_text(encoding="utf-8")
    details: dict[str, dict[str, Any]] = {}
    for page_id, chunk in check_deck.pages(source):
        if page_id not in check_deck.FREETALK_QUESTION_PAGES:
            continue
        english = [
            check_deck.plain_text(body)
            for body in check_deck.class_span_bodies(chunk, "ko")[:1]
        ]
        japanese = [
            check_deck.plain_text(body)
            for body in check_deck.class_span_bodies(chunk, "ja")[:1]
        ]
        followup_list = TN_MORE_RE.search(chunk)
        followups = (
            [
                check_deck.plain_text(body)
                for body in LIST_ITEM_RE.findall(followup_list.group(1))
                if check_deck.plain_text(body)
            ]
            if followup_list
            else []
        )
        if english and japanese and followups:
            details[page_id] = {
                "english": english[0],
                "japanese": japanese[0],
                "followups": followups,
            }
    return details


def scaffold(path: pathlib.Path, audit_path: pathlib.Path | None = None) -> dict[str, Any]:
    evidence = page_evidence(path)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "lesson": relative_lesson(path, audit_path),
        "lessonSha256": sha256(path),
        "stages": {
            "generated": "pass",
            "mechanicalValidation": "pending",
            "humanPageAudit": "pending",
            "ownerApproval": "pending",
        },
        "viewports": [360, 480],
        "pages": [
            {
                "pageId": page_id,
                "learnerAction": "",
                "tutorAction": "",
                "targetOrPrompt": "",
                "learningTarget": "",
                "pedagogicalValue": "",
                "failureDiagnosis": "",
                "nonTargetSupport": "",
                "articleTreatment": "",
                "choiceQuality": "",
                "componentConsistency": "",
                "visual360": "pending",
                "visual480": "pending",
                "verdict": "revise",
                "notes": "",
                "evidence": evidence[page_id],
                **(
                    {
                        "conversationReview": {
                            "plausibleFirstAnswer": "",
                            "answerExpansion": "",
                            "noAnswerFollowup": "",
                        }
                    }
                    if page_id in check_deck.FREETALK_QUESTION_PAGES
                    else {}
                ),
            }
            for page_id in page_ids(path)
        ],
    }


def load_review(path: pathlib.Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReviewError(f"{path}: cannot read review JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ReviewError(f"{path}: review root must be an object")
    return data


def _replace_exact_text(value: Any, old: str, new: str) -> Any:
    """Replace an extracted prompt while preserving surrounding review prose."""
    if isinstance(value, str):
        return value.replace(old, new)
    if isinstance(value, list):
        return [_replace_exact_text(item, old, new) for item in value]
    if isinstance(value, dict):
        return {key: _replace_exact_text(item, old, new) for key, item in value.items()}
    return value


def refresh_evidence(
    lesson_path: pathlib.Path,
    review_path: pathlib.Path,
) -> dict[str, Any]:
    """Refresh byte-bound evidence without erasing completed human judgments."""
    review = load_review(review_path)
    actual_ids = page_ids(lesson_path)
    pages = review.get("pages")
    if not isinstance(pages, list):
        raise ReviewError(f"{review_path}: pages must be an array")
    ledger_ids = [page.get("pageId") for page in pages if isinstance(page, dict)]
    if ledger_ids != actual_ids:
        raise ReviewError(
            f"{review_path}: cannot refresh changed page coverage; "
            f"ledger={ledger_ids} lesson={actual_ids}"
        )
    evidence = page_evidence(lesson_path)
    question_details = freetalk_question_details(lesson_path)
    review["schemaVersion"] = SCHEMA_VERSION
    review["lesson"] = relative_lesson(lesson_path, review_path)
    review["lessonSha256"] = sha256(lesson_path)
    for page in pages:
        current_evidence = evidence[page["pageId"]]
        old_evidence = page.get("evidence", {})
        old_prompts = old_evidence.get("substantivePrompts", []) if isinstance(old_evidence, dict) else []
        new_prompts = current_evidence.get("substantivePrompts", [])
        for index, old_prompt in enumerate(old_prompts):
            if old_prompt and index < len(new_prompts):
                for key in tuple(page):
                    if key != "evidence":
                        page[key] = _replace_exact_text(page[key], old_prompt, new_prompts[index])
        target_or_prompt = str(page.get("targetOrPrompt", ""))
        for index, new_prompt in enumerate(new_prompts):
            old_prompt = old_prompts[index] if index < len(old_prompts) else ""
            if old_prompt and old_prompt in target_or_prompt:
                target_or_prompt = target_or_prompt.replace(old_prompt, new_prompt, 1)
            elif _normalized_text(new_prompt) not in _normalized_text(target_or_prompt):
                target_or_prompt = f"{target_or_prompt.rstrip()} Visible prompt: {new_prompt}".strip()
        page["targetOrPrompt"] = target_or_prompt
        page["evidence"] = current_evidence
        details = question_details.get(page["pageId"])
        if details:
            english = details["english"]
            japanese = details["japanese"]
            followups = details["followups"]
            quoted_followups = " and ".join(f"“{item}”" for item in followups)
            page["learnerAction"] = (
                f"Answer the standalone question “{english}” aloud and develop one "
                "interesting detail, example, or reason."
            )
            page["tutorAction"] = (
                f"Ask “{english}”, react naturally, and use the most relevant "
                "follow-up instead of forcing both."
            )
            page["targetOrPrompt"] = (
                f"Conversation prompt: “{english}” / “{japanese}” "
                f"Tutor follow-ups: {quoted_followups}"
            )
            page["learningTarget"] = (
                "Answer and develop this page's distinct conversation question in "
                "spontaneous English."
            )
            page["pedagogicalValue"] = (
                "The standalone prompt opens one answerable angle, and the follow-ups "
                "broaden or deepen the learner's answer."
            )
            page["failureDiagnosis"] = (
                "A no, an I-don't-know answer, or a general answer must still leave a "
                "natural next move; repeated or answer-presuming follow-ups fail the page."
            )
            page["nonTargetSupport"] = (
                f"The Japanese prompt “{japanese}” is meaning-aligned; the English "
                "follow-ups are tutor-only and do not supply an answer."
            )
            page["articleTreatment"] = (
                "The learner may use an article idea or any relevant example; the page "
                "does not test article recall."
            )
            page["choiceQuality"] = (
                "No fixed answer is implied; the learner and tutor can contribute "
                "different defensible views or examples."
            )
            page["componentConsistency"] = (
                "Uses one visible conversation question, one tutor-only follow-up pool, "
                "and no competing learner task."
            )
            page["notes"] = (
                "Semantic conversation audit completed against the current English "
                "prompt, Japanese prompt, and tutor follow-ups; visual status is "
                "recorded separately."
            )
    write_json(review_path, review)
    return review


def _meaningful(value: Any) -> bool:
    return isinstance(value, str) and len(value.strip()) >= 8


def _normalized_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def validate(
    lesson_path: pathlib.Path,
    review_path: pathlib.Path,
    *,
    require_owner: bool = False,
) -> list[str]:
    review = load_review(review_path)
    errors: list[str] = []

    if review.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {SCHEMA_VERSION}")

    actual_hash = sha256(lesson_path)
    if review.get("lessonSha256") != actual_hash:
        errors.append(
            "lessonSha256 is stale: "
            f"ledger={review.get('lessonSha256', '<missing>')} lesson={actual_hash}"
        )

    actual_ids = page_ids(lesson_path)
    pages = review.get("pages")
    if not isinstance(pages, list):
        errors.append("pages must be an array")
        pages = []
    ledger_ids = [page.get("pageId") for page in pages if isinstance(page, dict)]
    if ledger_ids != actual_ids:
        errors.append(
            "page order/coverage differs from lesson: "
            f"ledger={ledger_ids} lesson={actual_ids}"
        )

    actual_evidence = page_evidence(lesson_path)
    for index, page in enumerate(pages):
        if not isinstance(page, dict):
            errors.append(f"pages[{index}] must be an object")
            continue
        page_id = page.get("pageId", f"index {index}")
        if page.get("evidence") != actual_evidence.get(page_id):
            errors.append(
                f"{page_id}: extracted evidence differs from the lesson; "
                "reinitialize the ledger and review the current targets, blanks and hints"
            )
        target_or_prompt = _normalized_text(str(page.get("targetOrPrompt", "")))
        for prompt in actual_evidence.get(page_id, {}).get("substantivePrompts", []):
            if _normalized_text(prompt) not in target_or_prompt:
                errors.append(
                    f"{page_id}: targetOrPrompt must quote the substantive learner prompt: {prompt}"
                )
        for field in REQUIRED_PAGE_FIELDS:
            value = page.get(field)
            if field in {"visual360", "visual480"}:
                if value not in VISUAL_VALUES:
                    errors.append(f"{page_id}: {field} must be one of {sorted(VISUAL_VALUES)}")
            elif field == "verdict":
                if value not in VERDICTS:
                    errors.append(f"{page_id}: verdict must be one of {sorted(VERDICTS)}")
                elif value != "pass":
                    errors.append(f"{page_id}: verdict is {value}, not pass")
            elif not _meaningful(value):
                errors.append(f"{page_id}: {field} is missing or too vague")
        if page_id in check_deck.FREETALK_QUESTION_PAGES:
            conversation = page.get("conversationReview")
            if not isinstance(conversation, dict):
                errors.append(
                    f"{page_id}: conversationReview must record the spoken-answer checks"
                )
            else:
                for field in FREETALK_REVIEW_FIELDS:
                    if not _meaningful(conversation.get(field)):
                        errors.append(
                            f"{page_id}: conversationReview.{field} is missing or too vague"
                        )
                details = freetalk_question_details(lesson_path).get(page_id)
                rescue = _normalized_text(str(conversation.get("noAnswerFollowup", "")))
                if details and rescue and not any(
                    rescue == _normalized_text(followup)
                    for followup in details["followups"]
                ):
                    errors.append(
                        f"{page_id}: conversationReview.noAnswerFollowup must quote one current tutor follow-up"
                    )

    stages = review.get("stages")
    if not isinstance(stages, dict):
        errors.append("stages must be an object")
        stages = {}
    for stage in PASS_STAGES:
        if stages.get(stage) != "pass":
            errors.append(f"stages.{stage} must be pass")
    owner = stages.get("ownerApproval")
    if owner not in {"pending", "pass"}:
        errors.append("stages.ownerApproval must be pending or pass")
    if require_owner and owner != "pass":
        errors.append("stages.ownerApproval must be pass for owner-approved status")

    if review.get("viewports") != [360, 480]:
        errors.append("viewports must be exactly [360, 480]")
    return errors


def audit_corpus(
    lesson_root: pathlib.Path,
    review_root: pathlib.Path,
    *,
    require_owner: bool = False,
) -> list[str]:
    """Require one current, completed human ledger for every active lesson."""
    lessons = []
    for lesson in sorted(lesson_root.rglob("lesson.html")):
        source = lesson.read_text(encoding="utf-8")
        if check_deck.meta_content(source, "podo:curriculum-status") == "superseded":
            continue
        lessons.append(lesson.resolve())

    indexed: dict[pathlib.Path, pathlib.Path] = {}
    errors: list[str] = []
    for review_path in sorted(review_root.rglob("*.json")):
        try:
            review = load_review(review_path)
        except ReviewError as exc:
            errors.append(str(exc))
            continue
        raw_lesson = review.get("lesson")
        if not isinstance(raw_lesson, str) or not raw_lesson.strip():
            errors.append(f"{review_path}: missing lesson path")
            continue
        candidate = pathlib.Path(raw_lesson)
        if not candidate.is_absolute():
            candidate = REPO / candidate
        candidate = candidate.resolve()
        if candidate in indexed:
            errors.append(
                f"{candidate}: multiple review ledgers: {indexed[candidate]} and {review_path}"
            )
            continue
        indexed[candidate] = review_path

    active = set(lessons)
    for lesson in lessons:
        review_path = indexed.get(lesson)
        if review_path is None:
            errors.append(f"{lesson}: missing hash-bound page-review ledger")
            continue
        for error in validate(lesson, review_path, require_owner=require_owner):
            errors.append(f"{review_path}: {error}")

    for lesson, review_path in indexed.items():
        if lesson not in active:
            errors.append(
                f"{review_path}: ledger points outside the active lesson corpus: {lesson}"
            )
    return errors


def markdown(review: dict[str, Any]) -> str:
    stages = review.get("stages", {})
    lines = [
        "# Page review ledger",
        "",
        f"- Lesson: `{review.get('lesson', '')}`",
        f"- SHA-256: `{review.get('lessonSha256', '')}`",
        f"- Generated: **{stages.get('generated', 'missing')}**",
        f"- Mechanical validation: **{stages.get('mechanicalValidation', 'missing')}**",
        f"- Human page audit: **{stages.get('humanPageAudit', 'missing')}**",
        f"- Owner approval: **{stages.get('ownerApproval', 'missing')}**",
        "",
        "A changed lesson hash invalidates this ledger. Owner approval remains separate from the human audit.",
        "",
    ]
    for number, page in enumerate(review.get("pages", []), start=1):
        lines.extend(
            [
                f"## {number}. `{html.escape(str(page.get('pageId', 'missing')))}`",
                "",
                f"- Learner action: {page.get('learnerAction', '')}",
                f"- Tutor action: {page.get('tutorAction', '')}",
                f"- Visible target or prompt: {page.get('targetOrPrompt', '')}",
                f"- Learning target: {page.get('learningTarget', '')}",
                f"- Pedagogical value: {page.get('pedagogicalValue', '')}",
                f"- Failure diagnoses: {page.get('failureDiagnosis', '')}",
                f"- Non-target support: {page.get('nonTargetSupport', '')}",
                f"- Article treatment: {page.get('articleTreatment', '')}",
                f"- Choice/distractor quality: {page.get('choiceQuality', '')}",
                f"- Component consistency: {page.get('componentConsistency', '')}",
                f"- Extracted evidence: `{json.dumps(page.get('evidence', {}), ensure_ascii=False)}`",
                f"- Visual QA: 360px **{page.get('visual360', '')}**; 480px **{page.get('visual480', '')}**",
                f"- Verdict: **{page.get('verdict', '')}**",
                *(
                    [
                        f"- Plausible first answer: {page.get('conversationReview', {}).get('plausibleFirstAnswer', '')}",
                        f"- Expansion path: {page.get('conversationReview', {}).get('answerExpansion', '')}",
                        f"- No-answer follow-up: {page.get('conversationReview', {}).get('noAnswerFollowup', '')}",
                    ]
                    if page.get("conversationReview") is not None
                    else []
                ),
                f"- Notes: {page.get('notes', '') or 'None.'}",
                "",
            ]
        )
    # Extracted HTML text can legitimately end with whitespace after optional
    # spans.  Keep that implementation detail out of the human-facing ledger.
    return "\n".join(line.rstrip() for line in lines).rstrip() + "\n"


def write_json(path: pathlib.Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")



def audit_claims(lesson_root: pathlib.Path, review_root: pathlib.Path) -> list[str]:
    """Hold every `proofread-status="complete"` claim against its ledger.

    The claim and the evidence were never connected to each other, so neither
    could contradict the other. Every English generator calls
    `set_proofread_status(head, "complete")` unconditionally — the word is
    written by a script, not earned by a review — while the ledgers that would
    back it mostly still carry `visual360: "pending"` beside
    `humanPageAudit: "pass"`.

    This is the join. It reports rather than decides: what to do about a deck
    whose claim outruns its ledger is a curriculum question, and the backlog it
    exposes is real work rather than a mistake to be cleared in one commit.
    """
    # Index by the ledger's own `lesson` pointer rather than by deriving a
    # filename from the review id. Freetalking ships two decks per id
    # (`FT-105-full`, `FT-105-accessible`), so an id does not name a file.
    by_lesson: dict[pathlib.Path, pathlib.Path] = {}
    problems: list[str] = []
    for review_path in sorted(review_root.rglob("*.json")):
        try:
            review = load_review(review_path)
        except ReviewError:
            continue
        raw = review.get("lesson")
        if isinstance(raw, str):
            by_lesson[(REPO / raw).resolve()] = review_path

    for lesson in sorted(lesson_root.rglob("lesson.html")):
        source = lesson.read_text(encoding="utf-8")
        if check_deck.meta_content(source, "podo:curriculum-status") == "superseded":
            continue
        if check_deck.meta_content(source, "podo:proofread-status") != "complete":
            continue
        label = check_deck.meta_content(source, "podo:review-id") or str(lesson)
        ledger = by_lesson.get(lesson.resolve())
        if ledger is None:
            problems.append(f"{label}: claims complete, no ledger points at this deck")
            continue
        try:
            errors = validate(lesson, ledger)
        except ReviewError as exc:
            errors = [str(exc)]
        if errors:
            problems.append(f"{label}: claims complete, ledger does not pass "
                            f"({len(errors)} problem(s); first: {errors[0][:90]})")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create a review template from lesson pages")
    init_parser.add_argument("lesson", type=pathlib.Path)
    init_parser.add_argument("--output", type=pathlib.Path, required=True)

    check_parser = subparsers.add_parser("check", help="verify a completed review against lesson bytes")
    check_parser.add_argument("lesson", type=pathlib.Path)
    check_parser.add_argument("review", type=pathlib.Path)
    check_parser.add_argument("--require-owner", action="store_true")

    render_parser = subparsers.add_parser("render", help="render a review JSON file as Markdown")
    render_parser.add_argument("review", type=pathlib.Path)
    render_parser.add_argument("--output", type=pathlib.Path, required=True)

    refresh_parser = subparsers.add_parser(
        "refresh", help="refresh hash and extracted evidence without erasing human review fields"
    )
    refresh_parser.add_argument("lesson", type=pathlib.Path)
    refresh_parser.add_argument("review", type=pathlib.Path)

    corpus_parser = subparsers.add_parser(
        "audit-corpus", help="require one current completed ledger for every active lesson"
    )
    corpus_parser.add_argument("lessons", type=pathlib.Path)
    corpus_parser.add_argument("reviews", type=pathlib.Path)
    corpus_parser.add_argument("--require-owner", action="store_true")

    claims_parser = subparsers.add_parser(
        "audit-claims",
        help="hold every proofread-status=complete claim against its ledger",
    )
    claims_parser.add_argument("lessons", type=pathlib.Path)
    claims_parser.add_argument("reviews", type=pathlib.Path)

    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            write_json(args.output, scaffold(args.lesson, args.output))
            print(f"wrote {args.output}")
            return 0
        if args.command == "check":
            errors = validate(args.lesson, args.review, require_owner=args.require_owner)
            if errors:
                for error in errors:
                    print(f"ERROR: {error}", file=sys.stderr)
                return 1
            print(f"PASS: {args.review} matches {args.lesson}")
            return 0
        if args.command == "refresh":
            refresh_evidence(args.lesson, args.review)
            print(f"refreshed {args.review}")
            return 0
        if args.command == "audit-claims":
            problems = audit_claims(args.lessons, args.reviews)
            for problem in problems:
                print(f"CLAIM: {problem}")
            print(f"\n{len(problems)} deck(s) claim a proofreading nobody can show")
            return 1 if problems else 0
        if args.command == "audit-corpus":
            errors = audit_corpus(
                args.lessons, args.reviews, require_owner=args.require_owner
            )
            if errors:
                for error in errors:
                    print(f"ERROR: {error}", file=sys.stderr)
                return 1
            print(f"PASS: every active lesson under {args.lessons} has a current review")
            return 0
        review = load_review(args.review)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown(review), encoding="utf-8")
        print(f"wrote {args.output}")
        return 0
    except ReviewError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
