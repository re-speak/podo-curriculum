from __future__ import annotations

import pathlib
import re
import tempfile
import unittest

try:
    from tools.authoring.en import corpus_integrity as integrity
except ModuleNotFoundError:  # Direct `python path/to/test_corpus_integrity.py`.
    import corpus_integrity as integrity


AUDIT_ROOT = pathlib.Path("/virtual/repo")
ROOT = AUDIT_ROOT / "sandbox/drafts/en/tracks"
SHARED = "../../../../../../../../../shared/js/"


def path(track: str, course: str, number: int, slug: str) -> pathlib.Path:
    return ROOT / track / "courses" / course / "lessons" / f"{number:02d}-{slug}" / "lesson.html"


def render(deck_path: pathlib.Path, source: str) -> str:
    return source.replace("__LESSON_ID__", deck_path.parent.name)


def set_vocab(source: str, category: str, value: str) -> str:
    return re.sub(
        rf'(<meta name="podo:vocabulary:{category}" content=")[^"]*(">)',
        rf'\g<1>{value}\2',
        source,
        count=1,
    )


def article_rows(*, claims: bool = True, count: int = 10, sequential: bool = True, text: str = "ordinary text") -> str:
    rows = []
    for index in range(1, count + 1):
        option = f"s{index if sequential or index != 2 else 3}"
        claim = f' data-claim-id="claim-{index}"' if claims else ""
        rows.append(
            f'<div class="sent" data-sync-option="{option}"{claim}>'
            f'<span class="s-line">{text}</span>'
            '<span class="s-open"><span class="s-words"><b>gloss only</b></span></span>'
            "</div>"
        )
    return '<div data-page-id="article">' + "".join(rows) + "</div>"


def deck(
    review_id: str,
    *,
    new: str = "term|用語",
    recycled: str = "",
    productive: str = "term",
    proofread: str | None = "pending",
    curriculum: str | None = None,
    feedback_body: str = "",
    script_order: tuple[str, ...] = ("activities", "pager"),
    ft_claims: bool = True,
    ft_rows: int = 10,
    ft_sequential: bool = True,
) -> str:
    prefix = review_id.split("-", 1)[0]
    status = f'<meta name="podo:proofread-status" content="{proofread}">' if proofread else ""
    curriculum_meta = f'<meta name="podo:curriculum-status" content="{curriculum}">' if curriculum else ""
    scripts = {
        "activities": f'<script src="{SHARED}activities.js"></script>',
        "feedback": f'<script src="{SHARED}feedback.js"></script>',
        "freetalk": f'<script src="{SHARED}freetalk-activities.js"></script>',
        "pager": f'<script src="{SHARED}pager.js"></script>',
        "script-lines": f'<script src="{SHARED}script-lines.js"></script>',
        "spotlight": f'<script src="{SHARED}spotlight.js"></script>',
        "tutor-notes": f'<script src="{SHARED}tutor-notes.js"></script>',
        "highlight": f'<script src="{SHARED}highlight.js"></script>',
        "stamp": f'<script src="{SHARED}stamp.js"></script>',
    }
    if prefix == "FT":
        if script_order == ("activities", "pager"):
            script_order = (
                "activities", "feedback", "freetalk", "pager", "script-lines",
                "spotlight", "tutor-notes", "highlight", "stamp",
            )
        if not feedback_body:
            feedback_body = '<textarea data-fb="correction"></textarea>'
        body = article_rows(
            claims=ft_claims,
            count=ft_rows,
            sequential=ft_sequential,
            text=productive,
        )
    else:
        body = f'<div data-page-id="model"><span class="korean">{productive}</span></div>'
    return f"""<!doctype html><html><head>
<meta name="podo:review-id" content="{review_id}">
<meta name="podo:lesson-id" content="__LESSON_ID__">
{curriculum_meta}{status}
<meta name="podo:vocabulary-status" content="reviewed">
<meta name="podo:vocabulary:new" content="{new}">
<meta name="podo:vocabulary:recycled" content="{recycled}">
<meta name="podo:vocabulary:assumed" content="known|既知">
<meta name="podo:vocabulary:receptive" content="heard|聞く">
</head><body>{body}{feedback_body}{''.join(scripts[name] for name in script_order)}</body></html>"""


def superseded() -> tuple[pathlib.Path, str]:
    old = ROOT / integrity.SUPERSEDED_PROTOTYPE
    return old, deck("CTX-1", curriculum="superseded", proofread=None).replace(
        "__LESSON_ID__", old.parent.name
    )


def corpus(
    *items: tuple[pathlib.Path, str],
    briefs: dict[str, str] | None = None,
    pair_sense_exceptions=frozenset(),
):
    old_path, old_source = superseded()
    rendered = {item_path: render(item_path, source) for item_path, source in items}
    return integrity.audit_sources(
        {old_path: old_source, **rendered},
        tracks_root=ROOT,
        briefs=briefs or {},
        pair_sense_exceptions=pair_sense_exceptions,
    )


class PhraseMatcherTests(unittest.TestCase):
    def test_whole_token_matching_rejects_substrings(self) -> None:
        self.assertFalse(integrity.phrase_visible("timing", "The mistiming caused a delay."))
        self.assertFalse(integrity.phrase_visible("push back", "We should push backward slowly."))

    def test_reviewed_aliases_contractions_and_separable_forms_are_allowed(self) -> None:
        positives = (
            ("documentary", "I watched two documentaries."),
            ("fall through", "The plan fell through."),
            ("make up", "They made up after lunch."),
            ("plan", "We are planning the trip."),
            ("delay", "The flight was delayed."),
            ("do not", "I don't agree."),
            ("would rather", "I'd rather wait."),
            ("passport", "May I see your passports?"),
            ("small win", "Small wins still matter."),
            ("push back", "We can push it back."),
        )
        for term, text in positives:
            with self.subTest(term=term, text=text):
                self.assertTrue(integrity.phrase_visible(term, text))

    def test_unreviewed_or_substring_pseudo_inflections_are_rejected(self) -> None:
        negatives = (
            ("fall through", "It falled through."),
            ("worth it", "It was worth ited."),
            ("vocal range", "Her vocals range widely."),
            ("first impression", "Firsts impression matters."),
            ("fit", "The outfit is blue."),
            ("timing", "The mistiming caused a delay."),
            ("push back", "We should push backward slowly."),
        )
        for term, text in negatives:
            with self.subTest(term=term, text=text):
                self.assertFalse(integrity.phrase_visible(term, text))


class ProvenanceMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.owner_path = path("1-core-patterns", "core", 1, "owner")
        self.owner = deck("CORE-1", new="timing|タイミング", productive="timing")

    def _errors(self, dependent: str, *, number: int = 2, extra=()) -> list[str]:
        dependent_path = path("1-core-patterns", "core", number, "dependent")
        _, errors = corpus(
            (self.owner_path, self.owner),
            *extra,
            (dependent_path, deck(f"CORE-{number}", new="other|別", recycled=dependent, productive="timing other")),
        )
        return errors

    def test_wrong_japanese_owner_is_rejected(self) -> None:
        errors = self._errors("timing|時期|CORE-1")
        self.assertTrue(any("has Japanese '時期'" in error and "タイミング" in error for error in errors), errors)

    def test_nonexistent_owner_is_rejected(self) -> None:
        errors = self._errors("timing|タイミング|CORE-99")
        self.assertTrue(any("nonexistent active owner CORE-99" in error for error in errors), errors)

    def test_unreachable_owner_is_rejected(self) -> None:
        future_path = path("1-core-patterns", "core", 3, "future")
        future = deck("CORE-3", new="future term|将来", productive="future term")
        errors = self._errors("future term|将来|CORE-3", extra=((future_path, future),))
        self.assertTrue(any("CORE-3 is not reachable at CORE-2" in error for error in errors), errors)

    def test_duplicate_new_owner_is_rejected(self) -> None:
        duplicate_path = path("1-core-patterns", "core", 2, "duplicate")
        _, errors = corpus(
            (self.owner_path, self.owner),
            (duplicate_path, deck("CORE-2", new="timing|タイミング", productive="timing")),
        )
        self.assertTrue(any("duplicate new owner for 'timing'" in error for error in errors), errors)

    def test_contextual_entry_floor_blocks_later_core_owner(self) -> None:
        owner_path = path("1-core-patterns", "core", 5, "owner")
        context_path = path("2-contextual-english", "ctx", 1, "context")
        _, errors = corpus(
            (owner_path, self.owner.replace("CORE-1", "CORE-5")),
            (context_path, deck("CTX-1", new="request|依頼", recycled="timing|タイミング|CORE-5", productive="request timing")),
            briefs={"CTX-1": "- **Entry floor:** Core 4\n"},
        )
        self.assertTrue(any("CORE-5 is not reachable at CTX-1" in error for error in errors), errors)

    def test_freetalk_cannot_cite_a_contextual_owner(self) -> None:
        context_path = path("2-contextual-english", "ctx", 1, "context")
        ft_path = path("3-freetalking", "talk-accessible", 2, "topic")
        _, errors = corpus(
            (context_path, deck("CTX-1", new="timing|タイミング", productive="timing")),
            (ft_path, deck("FT-2", new="other|別", recycled="timing|タイミング|CTX-1", productive="other")),
            briefs={"CTX-1": "- **Entry floor:** Core 1\n"},
        )
        self.assertTrue(any("CTX-1 is not reachable at FT-2" in error for error in errors), errors)

    def test_freetalk_cannot_cite_core_above_entry_floor_53(self) -> None:
        owner_path = path("1-core-patterns", "core", 122, "owner")
        ft_path = path("3-freetalking", "talk-accessible", 56, "topic")
        _, errors = corpus(
            (owner_path, deck("CORE-122", new="framing|枠組み", productive="framing")),
            (ft_path, deck("FT-56", new="other|別", recycled="framing|枠組み|CORE-122", productive="other")),
        )
        self.assertTrue(any("CORE-122 is not reachable at FT-56" in error for error in errors), errors)

    def test_contextual_entry_floor_uses_injected_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tracks_root = pathlib.Path(directory)
            brief = tracks_root / "2-contextual-english/toc/CTX-1.md"
            brief.parent.mkdir(parents=True)
            brief.write_text("- **Entry floor:** Core 7\n", encoding="utf-8")
            ctx_path = tracks_root / "2-contextual-english/courses/ctx/lessons/01-context/lesson.html"
            source = deck("CTX-1").replace("__LESSON_ID__", ctx_path.parent.name)
            parsed, errors = integrity.parse_deck(ctx_path, source, tracks_root=tracks_root)
            self.assertFalse(errors)
            self.assertEqual(integrity._entry_floor(parsed, None, tracks_root), 7)


class OwnershipLaneMutationTests(unittest.TestCase):
    def test_reachable_prior_exact_bilingual_owner_is_rejected_in_each_lane(self) -> None:
        cases = []
        cases.append((
            "Core",
            ((path("1-core-patterns", "core", 1, "owner"), deck("CORE-1", new="term|用語", productive="term")),
             (path("1-core-patterns", "core", 2, "consumer"), deck("CORE-2", new="term|用語", productive="term"))),
            {},
        ))
        cases.append((
            "CTX",
            ((path("1-core-patterns", "core", 1, "owner"), deck("CORE-1", new="term|用語", productive="term")),
             (path("2-contextual-english", "ctx", 1, "consumer"), deck("CTX-1", new="term|用語", productive="term"))),
            {"CTX-1": "- **Entry floor:** Core 1\n"},
        ))
        for variant in ("accessible", "full"):
            cases.append((
                f"FT-{variant}",
                ((path("3-freetalking", f"talk-{variant}", 9, "owner"), deck("FT-9", new="term|用語", productive="term")),
                 (path("3-freetalking", f"talk-{variant}", 10, "consumer"), deck("FT-10", new="term|用語", productive="term"))),
                {},
            ))
        for label, items, briefs in cases:
            with self.subTest(label=label):
                _records, errors = corpus(*items, briefs=briefs)
                self.assertTrue(any("duplicate new owner for 'term'|用語" in error for error in errors), errors)

    def test_same_spelling_different_japanese_is_a_distinct_core_sense(self) -> None:
        owner = path("1-core-patterns", "core", 1, "charge-fee")
        later = path("1-core-patterns", "core", 2, "charge-device")
        _records, errors = corpus(
            (owner, deck("CORE-1", new="charge|料金", productive="charge")),
            (later, deck("CORE-2", new="charge|充電する", productive="charge")),
        )
        self.assertFalse(any("duplicate new owner for 'charge'" in error for error in errors), errors)

    def test_ft15_budget_duplicates_reachable_core53_owner(self) -> None:
        core = path("1-core-patterns", "core", 53, "budget-owner")
        a = path("3-freetalking", "talk-accessible", 15, "budget")
        f = path("3-freetalking", "talk-full", 15, "budget")
        _records, errors = corpus(
            (core, deck("CORE-53", new="budget|予算", productive="budget")),
            (a, deck("FT-15", new="budget|予算", productive="budget")),
            (f, deck("FT-15", new="budget|予算", productive="budget")),
        )
        duplicates = [error for error in errors if "duplicate new owner for 'budget'|予算" in error]
        self.assertEqual(len(duplicates), 2, errors)

    def test_same_variant_history_does_not_cross_between_a_and_f(self) -> None:
        a9 = path("3-freetalking", "talk-accessible", 9, "term")
        f10 = path("3-freetalking", "talk-full", 10, "term")
        _records, errors = corpus(
            (a9, deck("FT-9", new="term|用語", productive="term")),
            (f10, deck("FT-10", new="term|用語", productive="term")),
        )
        self.assertFalse(any("duplicate new owner for 'term'|用語" in error for error in errors), errors)


class VisibilityAndStatusMutationTests(unittest.TestCase):
    def test_metadata_and_gloss_only_vocabulary_is_not_productively_visible(self) -> None:
        ft_path = path("3-freetalking", "talk", 10, "metadata-only")
        source = deck("FT-10", new="timing|タイミング", productive="ordinary text")
        source = source.replace("<b>gloss only</b>", "<b>timing</b>")
        _, errors = corpus((ft_path, source))
        self.assertTrue(any("new term 'timing' is absent" in error for error in errors), errors)

    def test_recycled_vocabulary_does_not_require_productive_visibility(self) -> None:
        owner_path = path("1-core-patterns", "core", 1, "owner")
        dependent_path = path("1-core-patterns", "core", 2, "dependent")
        _, errors = corpus(
            (owner_path, deck("CORE-1", new="timing|タイミング", productive="timing")),
            (dependent_path, deck("CORE-2", new="other|別", recycled="timing|タイミング|CORE-1", productive="other")),
        )
        self.assertFalse(any("recycled term" in error for error in errors), errors)

    def test_hidden_inert_tutor_private_and_japanese_support_do_not_count(self) -> None:
        active = path("1-core-patterns", "core", 1, "hidden")
        source = deck("CORE-1", new="timing|タイミング", productive="ordinary")
        source = source.replace(
            "</body>",
            '<span hidden class="korean">timing</span>'
            '<span aria-hidden="true" class="korean">timing</span>'
            '<span aria-hidden=" \tTrUe\u2003 " class="korean">timing</span>'
            '<span style="dIsPlAy:\t\n NoNe" class="korean">timing</span>'
            '<span style="ViSiBiLiTy:\u00a0HiDdEn" class="korean">timing</span>'
            '<div inert><span class="korean">timing</span></div>'
            '<noscript><span class="korean">timing</span></noscript>'
            '<div class="tutor-note"><span class="korean">timing</span></div>'
            '<span class="translation">timing</span></body>',
        )
        _, errors = corpus((active, source))
        self.assertTrue(any("new term 'timing' is absent" in error for error in errors), errors)

    def test_visible_answer_frame_and_direct_hint_scaffold_count(self) -> None:
        for label, extra in (
            ("frame", '<span class="answer-label">Use timing in your answer.</span>'),
            ("hint", '<span class="hint-chip">タイミング:timing</span>'),
        ):
            with self.subTest(label=label):
                active = path("1-core-patterns", "core", 1, label)
                source = deck("CORE-1", new="timing|タイミング", productive="ordinary")
                source = source.replace("</body>", extra + "</body>")
                _, errors = corpus((active, source))
                self.assertFalse(any("new term 'timing' is absent" in error for error in errors), errors)

    def test_only_a_production_page_prompt_counts_as_productive_scaffolding(self) -> None:
        for page_id, expected_visible in (("p1-write", True), ("lesson-goal", False)):
            with self.subTest(page_id=page_id):
                active = path("1-core-patterns", "core", 1, page_id)
                source = deck("CORE-1", new="timing|タイミング", productive="ordinary")
                prompt = (
                    f'<div data-page-id="{page_id}"><p class="section-subtitle">'
                    '<span class="ko">Use timing in your answer.</span></p></div>'
                )
                source = source.replace("</body>", prompt + "</body>")
                _, errors = corpus((active, source))
                absent = any("new term 'timing' is absent" in error for error in errors)
                self.assertEqual(absent, not expected_visible, errors)

    def test_inert_productive_prompt_and_article_rows_do_not_count(self) -> None:
        active = path("1-core-patterns", "core", 1, "inert-prompt")
        source = deck("CORE-1", new="timing|タイミング", productive="ordinary")
        source = source.replace(
            "</body>",
            '<div inert><div data-page-id="p1-write"><p class="section-subtitle">'
            '<span class="ko">Use timing.</span></p></div></div></body>',
        )
        _, errors = corpus((active, source))
        self.assertTrue(any("new term 'timing' is absent" in error for error in errors), errors)

        ft_path = path("3-freetalking", "talk-accessible", 10, "inert-row")
        ft_source = deck("FT-10")
        hidden_row = (
            '<div inert><div class="sent" data-sync-option="s11" data-claim-id="claim-11">'
            '<span class="s-line">term</span></div></div>'
        )
        ft_source = ft_source.replace('</div><textarea data-fb="correction">', hidden_row + '</div><textarea data-fb="correction">', 1)
        parsed, parse_errors = integrity.parse_deck(ft_path, render(ft_path, ft_source), tracks_root=ROOT)
        self.assertFalse(parse_errors)
        self.assertEqual(len(parsed.article_rows), 10)

    def test_active_deck_missing_status_is_reported(self) -> None:
        active = path("1-core-patterns", "core", 1, "missing-status")
        _, errors = corpus((active, deck("CORE-1", proofread=None)))
        self.assertTrue(any("active deck needs exactly one pending/complete proofread status" in error for error in errors), errors)

    def test_superseded_prototype_is_the_sole_status_exemption(self) -> None:
        old_path, old_source = superseded()
        active = path("1-core-patterns", "core", 1, "active")
        records, errors = integrity.audit_sources(
            {old_path: old_source, active: render(active, deck("CORE-1"))},
            tracks_root=ROOT,
            briefs={},
        )
        self.assertEqual(sum(record.superseded for record in records), 1)
        self.assertFalse(any(old_path.name in error and "proofread status" in error for error in errors), errors)

    def test_release_mode_rejects_pending(self) -> None:
        old_path, old_source = superseded()
        active = path("1-core-patterns", "core", 1, "pending")
        _, errors = integrity.audit_sources(
            {old_path: old_source, active: render(active, deck("CORE-1", proofread="pending"))},
            tracks_root=ROOT,
            briefs={},
            status_mode="release",
        )
        self.assertTrue(any("exactly one complete proofread status" in error for error in errors), errors)

    def test_unknown_curriculum_status_is_rejected(self) -> None:
        active = path("1-core-patterns", "core", 1, "unknown")
        _, errors = corpus((active, deck("CORE-1", curriculum="draft")))
        self.assertTrue(any("unknown podo:curriculum-status 'draft'" in error for error in errors), errors)


class FeedbackMutationTests(unittest.TestCase):
    def _issues(self, source: str) -> list[str]:
        deck_path = path("1-core-patterns", "core", 1, "feedback")
        source = source.replace("__LESSON_ID__", deck_path.parent.name)
        parsed, parse_errors = integrity.parse_deck(deck_path, source, tracks_root=ROOT)
        self.assertFalse(parse_errors)
        self.assertIsNotNone(parsed)
        return integrity._feedback_issues(parsed)

    def test_markup_shaped_inert_text_and_attribute_values_do_not_count(self) -> None:
        fake = """
<!-- <div data-fb="comment"></div> -->
<script>const fake = `<div data-fb="script"></div>`;</script>
<template><div data-fb="template"></div></template>
<div data-example="data-fb='attribute'"></div>
<div hidden data-fb="hidden"></div>
<div aria-hidden="true" data-fb="aria-hidden"></div>
<noscript><div data-fb="noscript"></div><script src="{SHARED}feedback.js"></script></noscript>
"""
        source = deck("CORE-1", feedback_body=fake.format(SHARED=SHARED))
        issues = self._issues(source)
        self.assertEqual(len(issues), 1, issues)
        self.assertIn("inline script is not canonical", issues[0])

    def test_missing_duplicate_and_misordered_feedback_scripts_are_rejected(self) -> None:
        control = '<div data-fb="answer"></div>'
        cases = {
            "missing": deck("CORE-1", feedback_body=control),
            "duplicate": deck("CORE-1", feedback_body=control, script_order=("activities", "feedback", "feedback", "pager")),
            "order": deck("CORE-1", feedback_body=control, script_order=("feedback", "activities", "pager")),
        }
        for name, source in cases.items():
            with self.subTest(name=name):
                self.assertTrue(self._issues(source))

    def test_feedback_script_without_real_control_is_rejected(self) -> None:
        source = deck("CORE-1", script_order=("activities", "feedback", "pager"))
        self.assertTrue(any("without a live data-fb" in issue for issue in self._issues(source)))

    def test_duplicate_activities_script_is_rejected(self) -> None:
        source = deck("CORE-1", script_order=("activities", "activities", "pager"))
        self.assertTrue(any("exactly 1 activities.js" in issue for issue in self._issues(source)))

    def test_freetalk_requires_its_runtime_in_exact_order(self) -> None:
        ft_path = path("3-freetalking", "talk-accessible", 10, "runtime")
        control = '<div data-fb="answer"></div>'
        source = deck(
            "FT-10",
            feedback_body=control,
            script_order=("activities", "freetalk", "feedback", "pager"),
        )
        source = source.replace("__LESSON_ID__", ft_path.parent.name)
        parsed, parse_errors = integrity.parse_deck(ft_path, source, tracks_root=ROOT)
        self.assertFalse(parse_errors)
        self.assertTrue(any("activities.js < feedback.js < freetalk-activities.js < pager.js" in issue for issue in integrity._feedback_issues(parsed)))

    def test_every_freetalk_tail_script_is_required_once_and_in_order(self) -> None:
        ft_path = path("3-freetalking", "talk-accessible", 10, "runtime-tail")
        canonical_order = [
            "activities", "feedback", "freetalk", "pager", "script-lines",
            "spotlight", "tutor-notes", "highlight", "stamp",
        ]

        def issues(source: str) -> list[str]:
            parsed, parse_errors = integrity.parse_deck(
                ft_path,
                render(ft_path, source),
                tracks_root=ROOT,
            )
            self.assertFalse(parse_errors)
            return integrity._feedback_issues(parsed)

        self.assertEqual(issues(deck("FT-10")), [])
        for tail in ("script-lines", "spotlight", "tutor-notes", "highlight", "stamp"):
            with self.subTest(tail=tail, mutation="missing"):
                order = tuple(item for item in canonical_order if item != tail)
                self.assertTrue(any(f"exactly 1 {tail}.js" in issue for issue in issues(deck("FT-10", script_order=order))))
            with self.subTest(tail=tail, mutation="duplicate"):
                index = canonical_order.index(tail)
                order = tuple(canonical_order[:index + 1] + [tail] + canonical_order[index + 1:])
                self.assertTrue(any(f"exactly 1 {tail}.js" in issue for issue in issues(deck("FT-10", script_order=order))))
            with self.subTest(tail=tail, mutation="order"):
                order = [item for item in canonical_order if item != tail]
                order.insert(0, tail)
                self.assertTrue(any("script order must be" in issue for issue in issues(deck("FT-10", script_order=tuple(order)))))

    def test_freetalk_rejects_unknown_external_script_anywhere(self) -> None:
        ft_path = path("3-freetalking", "talk-accessible", 10, "extra-script")
        canonical = deck("FT-10")
        unknown = f'<script src="{SHARED}unknown.js"></script>'
        anchors = (
            ("before", f'<script src="{SHARED}activities.js"></script>'),
            ("between", f'<script src="{SHARED}pager.js"></script>'),
            ("after", "</body>"),
        )
        for label, anchor in anchors:
            with self.subTest(label=label):
                source = canonical.replace(anchor, unknown + anchor, 1)
                parsed, parse_errors = integrity.parse_deck(
                    ft_path,
                    render(ft_path, source),
                    tracks_root=ROOT,
                )
                self.assertFalse(parse_errors)
                issues = integrity._feedback_issues(parsed)
                self.assertTrue(any("external script sequence must be exactly" in issue for issue in issues), issues)

    def test_inert_script_shaped_markup_does_not_change_freetalk_sequence(self) -> None:
        ft_path = path("3-freetalking", "talk-accessible", 10, "inert-script")
        fake = (
            f'<!-- <script src="{SHARED}unknown.js"></script> -->'
            f'<template><script src="{SHARED}unknown.js"></script></template>'
            f'<noscript><script src="{SHARED}unknown.js"></script></noscript>'
        )
        source = deck("FT-10").replace("</body>", fake + "</body>")
        parsed, parse_errors = integrity.parse_deck(ft_path, render(ft_path, source), tracks_root=ROOT)
        self.assertFalse(parse_errors)
        self.assertEqual(integrity._feedback_issues(parsed), [])

    def test_script_execution_survives_head_and_visibility_wrappers(self) -> None:
        ft_path = path("3-freetalking", "talk-accessible", 10, "script-execution")
        activity = f'<script src="{SHARED}activities.js"></script>'
        stamp = f'<script src="{SHARED}stamp.js"></script>'
        unknown = f'<script src="{SHARED}unknown.js"></script>'
        wrappers = {
            "head": None,
            "hidden": ("<div hidden>", "</div>"),
            "inert": ("<div inert>", "</div>"),
            "aria-hidden": ('<div aria-hidden="true">', "</div>"),
            "display-none": ('<div style="display:none">', "</div>"),
        }

        def place(base: str, content: str, wrapper) -> str:
            if wrapper is None:
                return base.replace("</head>", content + "</head>", 1)
            opening, closing = wrapper
            return base.replace(activity, opening + content + closing, 1)

        def issues(source: str) -> list[str]:
            parsed, parse_errors = integrity.parse_deck(
                ft_path,
                render(ft_path, source),
                tracks_root=ROOT,
            )
            self.assertFalse(parse_errors)
            return integrity._feedback_issues(parsed)

        canonical = deck("FT-10")
        for label, wrapper in wrappers.items():
            with self.subTest(wrapper=label, mutation="valid-relocation"):
                base = canonical.replace(activity, "", 1) if wrapper is None else canonical
                self.assertEqual(issues(place(base, activity, wrapper)), [])
            with self.subTest(wrapper=label, mutation="missing"):
                self.assertTrue(any("external script sequence" in issue for issue in issues(canonical.replace(activity, "", 1))))
            with self.subTest(wrapper=label, mutation="duplicate"):
                base = canonical.replace(activity, "", 1) if wrapper is None else canonical
                source = place(base, activity + activity, wrapper)
                self.assertTrue(any("external script sequence" in issue for issue in issues(source)))
            with self.subTest(wrapper=label, mutation="unknown"):
                base = canonical.replace(activity, "", 1) if wrapper is None else canonical
                source = place(base, activity + unknown, wrapper)
                self.assertTrue(any("external script sequence" in issue for issue in issues(source)))
            with self.subTest(wrapper=label, mutation="order"):
                base = canonical.replace(stamp, "", 1)
                if wrapper is None:
                    source = base.replace("</head>", stamp + "</head>", 1)
                else:
                    opening, closing = wrapper
                    source = base.replace(activity, opening + stamp + closing + activity, 1)
                self.assertTrue(any("external script sequence" in issue for issue in issues(source)))

    def test_shared_script_identity_rejects_hostile_lookalike_sources(self) -> None:
        ft_path = path("3-freetalking", "talk-accessible", 10, "script-identity")
        canonical = deck("FT-10")
        valid = f'<script src="{SHARED}activities.js"></script>'
        hostile = (
            '<script src="https://evil.example/shared/js/activities.js"></script>',
            f'<script src="{SHARED}activities.js?x=1"></script>',
            f'<script src="{SHARED}activities.js#x"></script>',
            f'<script src="{SHARED}activities.js?"></script>',
            f'<script src="{SHARED}activities.js#"></script>',
            f'<script src="{SHARED}activities.js?#"></script>',
            f'<script src="{SHARED}acti\tvities.js"></script>',
            f'<script src="{SHARED}acti\rvities.js"></script>',
            f'<script src="{SHARED}acti\nvities.js"></script>',
            f'<script src="{SHARED}activities.js\t"></script>',
            f'<script src="{SHARED}activities.js\r"></script>',
            f'<script src="{SHARED}activities.js\n"></script>',
            '<script src="../../other/activities.js"></script>',
            '<script src="/shared/js/activities.js"></script>',
            f'<script src="{SHARED}./activities.js"></script>',
            f'<script src="{SHARED.replace("shared/js/", "x/../shared/js/")}activities.js"></script>',
            f'<script src="{SHARED.replace("shared/js/", "shared//js/")}activities.js"></script>',
            f'<script src="{SHARED.replace("shared/js/", "shared/x/../js/")}activities.js"></script>',
            f'<script src="{SHARED.replace("/", chr(92))}activities.js"></script>',
        )
        for src in hostile:
            with self.subTest(src=src):
                parsed, parse_errors = integrity.parse_deck(
                    ft_path,
                    render(ft_path, canonical.replace(valid, src, 1)),
                    tracks_root=ROOT,
                )
                self.assertFalse(parse_errors)
                issues = integrity._feedback_issues(parsed)
                self.assertTrue(any("noncanonical shared script src" in issue for issue in issues), issues)

        parsed, parse_errors = integrity.parse_deck(
            ft_path,
            render(ft_path, canonical),
            tracks_root=ROOT,
            audit_root=AUDIT_ROOT,
        )
        self.assertFalse(parse_errors)
        for depth in (0, 1, 2, 8, 10):
            with self.subTest(depth=depth):
                src = "../" * depth + "shared/js/activities.js"
                self.assertIsNone(integrity._canonical_shared_script_name(parsed, src))
                mutation = f'<script src="{src}"></script>'
                mutated, mutation_errors = integrity.parse_deck(
                    ft_path,
                    render(ft_path, canonical.replace(valid, mutation, 1)),
                    tracks_root=ROOT,
                    audit_root=AUDIT_ROOT,
                )
                self.assertFalse(mutation_errors)
                self.assertTrue(
                    any(
                        "noncanonical shared script src" in issue
                        for issue in integrity._feedback_issues(mutated)
                    )
                )
        self.assertEqual(
            integrity._canonical_shared_script_name(parsed, SHARED + "activities.js"),
            "activities.js",
        )

    def test_external_script_requires_src_only_and_normal_paired_tag(self) -> None:
        canonical = deck("CORE-1")
        valid = f'<script src="{SHARED}activities.js"></script>'
        mutations = {
            "self-closing": f'<script src="{SHARED}activities.js"/>',
            "async": f'<script src="{SHARED}activities.js" async></script>',
            "defer": f'<script defer src="{SHARED}activities.js"></script>',
            "type": f'<script src="{SHARED}activities.js" type="text/javascript"></script>',
            "nomodule": f'<script src="{SHARED}activities.js" nomodule></script>',
            "arbitrary": f'<script src="{SHARED}activities.js" data-runtime="x"></script>',
            "duplicate-src": (
                f'<script src="{SHARED}activities.js" '
                f'src="{SHARED}activities.js"></script>'
            ),
            "unclosed": f'<script src="{SHARED}activities.js">',
            "inline": '<script>window.notCanonical = true;</script>',
        }
        for name, replacement in mutations.items():
            with self.subTest(name=name):
                if name == "unclosed":
                    pager = f'<script src="{SHARED}pager.js"></script>'
                    source = canonical.replace(
                        pager,
                        f'<script src="{SHARED}pager.js">',
                        1,
                    )
                else:
                    source = canonical.replace(valid, replacement, 1)
                issues = self._issues(source)
                if name == "inline":
                    self.assertTrue(any("inline script" in issue for issue in issues), issues)
                elif name in {"self-closing", "unclosed"}:
                    self.assertTrue(any("normal paired tag" in issue for issue in issues), issues)
                else:
                    self.assertTrue(any("exactly one src attribute" in issue for issue in issues), issues)


class FreetalkClaimMutationTests(unittest.TestCase):
    def _claim_errors(self, ft_path: pathlib.Path, source: str) -> list[str]:
        source = source.replace("__LESSON_ID__", ft_path.parent.name)
        parsed, errors = integrity.parse_deck(ft_path, source, tracks_root=ROOT)
        self.assertFalse(errors)
        return integrity._freetalk_claim_issues(parsed)

    def test_waiver_set_is_exactly_twenty_paths(self) -> None:
        self.assertEqual(len(integrity.LEGACY_FT_CLAIM_WAIVERS), 20)
        self.assertTrue(all(relative.endswith("/lesson.html") for relative in integrity.LEGACY_FT_CLAIM_WAIVERS))

    def test_unauthorized_legacy_claim_waiver_is_rejected(self) -> None:
        modern = path("3-freetalking", "talk", 10, "modern")
        errors = self._claim_errors(modern, deck("FT-10", ft_claims=False))
        self.assertTrue(any("modern Freetalking" in error for error in errors), errors)

    def test_exact_legacy_path_keeps_row_and_option_contracts(self) -> None:
        relative = sorted(integrity.LEGACY_FT_CLAIM_WAIVERS)[0]
        legacy = ROOT / relative
        review_id = integrity.LEGACY_FT_CLAIM_WAIVERS[relative]
        source = deck(review_id, ft_claims=False)
        self.assertEqual(self._claim_errors(legacy, source), [])
        bad_rows = self._claim_errors(legacy, deck(review_id, ft_claims=False, ft_rows=9))
        self.assertTrue(any("10–15" in error for error in bad_rows), bad_rows)
        bad_options = self._claim_errors(legacy, deck(review_id, ft_claims=False, ft_sequential=False))
        self.assertTrue(any("sequential" in error for error in bad_options), bad_options)
        partial = deck(review_id, ft_claims=False).replace(
            'data-sync-option="s1"',
            'data-sync-option="s1" data-claim-id="partial"',
            1,
        )
        self.assertTrue(any("requires exactly zero" in error for error in self._claim_errors(legacy, partial)))

class IdentityMutationTests(unittest.TestCase):
    def test_duplicate_live_ids_are_rejected(self) -> None:
        source = deck("CORE-1").replace(
            "</body>",
            '<div data-page-id="model" data-sync-id="same" data-fb="same"></div>'
            '<div data-sync-id="same" data-fb="same"></div></body>',
        ).replace(
            f'<script src="{SHARED}pager.js"></script>',
            f'<script src="{SHARED}feedback.js"></script>'
            f'<script src="{SHARED}pager.js"></script>',
        )
        active = path("1-core-patterns", "core", 1, "duplicates")
        _, errors = corpus((active, source))
        self.assertTrue(any("duplicate page id" in error for error in errors), errors)
        self.assertTrue(any("duplicate sync id" in error for error in errors), errors)
        self.assertTrue(any("duplicate feedback id" in error for error in errors), errors)

    def test_review_id_must_match_track_and_path_number(self) -> None:
        wrong_track = path("1-core-patterns", "core", 1, "wrong-track")
        _, errors = corpus((wrong_track, deck("CTX-1")))
        self.assertTrue(any("does not match track" in error for error in errors), errors)
        wrong_number = path("1-core-patterns", "core", 2, "wrong-number")
        _, errors = corpus((wrong_number, deck("CORE-1")))
        self.assertTrue(any("path number/slug does not match CORE-1" in error for error in errors), errors)

    def test_review_id_requires_canonical_ascii_positive_integer(self) -> None:
        active = path("1-core-patterns", "core", 1, "canonical-id")
        valid = render(active, deck("CORE-1"))
        for bad in ("CORE-01", "CORE-０１", "CORE-0", "CORE--1", " CORE-1", "CORE-1 "):
            with self.subTest(review_id=bad):
                source = valid.replace('content="CORE-1"', f'content="{bad}"', 1)
                parsed, errors = integrity.parse_deck(active, source, tracks_root=ROOT)
                self.assertIsNone(parsed)
                self.assertTrue(any("valid podo:review-id" in error for error in errors), errors)

        alias_path = path("1-core-patterns", "core", 2, "alias")
        alias = render(alias_path, deck("CORE-2")).replace('content="CORE-2"', 'content="CORE-01"', 1)
        records, errors = integrity.audit_sources(
            {active: valid, alias_path: alias},
            tracks_root=ROOT,
            briefs={},
        )
        self.assertEqual([record.review_id for record in records], ["CORE-1"])
        self.assertTrue(any("valid podo:review-id" in error for error in errors), errors)

    def test_lesson_path_prefix_is_exact_canonical_ascii_width(self) -> None:
        for dirname in (
            "1-topic",
            "001-topic",
            "０１-topic",
            "01-",
            "01-Topic",
            "01-topic_name",
            "01-topic--name",
            "01-topic.name",
            ".01-topic",
            "01-.hidden",
        ):
            with self.subTest(dirname=dirname):
                active = ROOT / "1-core-patterns/courses/core/lessons" / dirname / "lesson.html"
                source = deck("CORE-1").replace("__LESSON_ID__", dirname)
                _parsed, errors = integrity.parse_deck(active, source, tracks_root=ROOT)
                self.assertTrue(any("lesson path number/slug does not match CORE-1" in error for error in errors), errors)

        active = ROOT / "1-core-patterns/courses/core/lessons/100-valid-topic/lesson.html"
        source = deck("CORE-100").replace("__LESSON_ID__", "100-valid-topic")
        parsed, errors = integrity.parse_deck(active, source, tracks_root=ROOT)
        self.assertIsNotNone(parsed)
        self.assertFalse(any("lesson path number/slug" in error for error in errors), errors)

    def test_lesson_id_must_be_unique_and_match_directory(self) -> None:
        active = path("1-core-patterns", "core", 1, "identity")
        valid = render(active, deck("CORE-1"))
        cases = {
            "missing": re.sub(r'<meta name="podo:lesson-id"[^>]*>\n?', "", valid),
            "wrong": valid.replace('content="01-identity"', 'content="01-wrong"'),
            "duplicate": valid.replace(
                '<meta name="podo:lesson-id" content="01-identity">',
                '<meta name="podo:lesson-id" content="01-identity">'
                '<meta name="podo:lesson-id" content="01-identity">',
            ),
        }
        for name, source in cases.items():
            with self.subTest(name=name):
                _parsed, errors = integrity.parse_deck(active, source, tracks_root=ROOT)
                self.assertTrue(any("exactly one podo:lesson-id matching" in error for error in errors), errors)

    def test_arbitrary_superseded_record_is_rejected(self) -> None:
        wrong_path = path("2-contextual-english", "retired", 99, "prototype")
        wrong = render(wrong_path, deck("CTX-99", curriculum="superseded", proofread=None))
        _records, errors = integrity.audit_sources(
            {wrong_path: wrong},
            tracks_root=ROOT,
            briefs={},
        )
        self.assertTrue(any("sole canonical CTX-1 prototype" in error for error in errors), errors)

    def test_metadata_inside_fallback_or_hidden_subtrees_is_absent(self) -> None:
        active = path("1-core-patterns", "core", 1, "metadata")
        valid = render(active, deck("CORE-1"))
        metas = {
            "review": ('<meta name="podo:review-id" content="CORE-1">', "expected exactly one valid podo:review-id"),
            "lesson": ('<meta name="podo:lesson-id" content="01-metadata">', "expected exactly one podo:lesson-id"),
            "proofread": ('<meta name="podo:proofread-status" content="pending">', "proofread status"),
            "vocab-status": ('<meta name="podo:vocabulary-status" content="reviewed">', "reviewed vocabulary status"),
            "vocab-new": ('<meta name="podo:vocabulary:new" content="term|用語">', "podo:vocabulary:new"),
        }
        wrappers = {
            "noscript": ("<noscript>", "</noscript>"),
            "hidden": ("<div hidden>", "</div>"),
            "inert": ("<div inert>", "</div>"),
            "aria-hidden": ('<div aria-hidden="true">', "</div>"),
            "aria-hidden-whitespace": ('<div aria-hidden=" \tTrUe\u2003 ">', "</div>"),
            "display-whitespace": ('<div style="dIsPlAy:\t\n NoNe">', "</div>"),
            "visibility-unicode-space": ('<div style="ViSiBiLiTy:\u00a0HiDdEn">', "</div>"),
        }
        for meta_name, (meta, expected) in metas.items():
            for wrapper_name, (opening, closing) in wrappers.items():
                with self.subTest(meta=meta_name, wrapper=wrapper_name):
                    self.assertIn(meta, valid)
                    source = valid.replace(meta, opening + meta + closing, 1)
                    _records, errors = integrity.audit_sources(
                        {active: source},
                        tracks_root=ROOT,
                        briefs={},
                    )
                    self.assertTrue(any(expected in error for error in errors), errors)

    def test_hidden_ids_do_not_count_or_conflict_with_live_ids(self) -> None:
        active = path("1-core-patterns", "core", 1, "hidden-ids")
        source = render(active, deck("CORE-1"))
        source = source.replace(
            "</body>",
            '<div hidden data-page-id="model" data-sync-id="hidden-sync" '
            'data-fb="hidden-fb" data-claim-id="hidden-claim"></div>'
            '<div inert data-sync-id="inert-sync"></div>'
            '<div aria-hidden="true" data-sync-id="aria-sync"></div>'
            '<div aria-hidden=" \tTrUe\u2003 " data-sync-id="aria-space-sync"></div>'
            '<div style="dIsPlAy:\t\n NoNe" data-sync-id="style-tab-sync"></div>'
            '<div style="ViSiBiLiTy:\u00a0HiDdEn" data-sync-id="style-unicode-sync"></div></body>',
        )
        parsed, parse_errors = integrity.parse_deck(active, source, tracks_root=ROOT)
        self.assertFalse(parse_errors)
        self.assertEqual(parsed.ids.get("page"), ["model"])
        self.assertNotIn("hidden-sync", parsed.ids.get("sync", []))
        self.assertNotIn("hidden-fb", parsed.ids.get("feedback", []))
        self.assertNotIn("hidden-claim", parsed.ids.get("claim", []))
        self.assertNotIn("aria-space-sync", parsed.ids.get("sync", []))
        self.assertNotIn("style-tab-sync", parsed.ids.get("sync", []))
        self.assertNotIn("style-unicode-sync", parsed.ids.get("sync", []))
        self.assertEqual(integrity._id_issues(parsed), [])
        self.assertEqual(parsed.feedback_controls, [])

    def test_same_english_cannot_appear_in_two_categories(self) -> None:
        active = path("1-core-patterns", "core", 1, "categories")
        _, errors = corpus((active, deck("CORE-1", new="term|用語", recycled="term|用語|CORE-1")))
        self.assertTrue(any("appears in both new and recycled" in error for error in errors), errors)


class FreetalkPairMutationTests(unittest.TestCase):
    def _pair(
        self,
        accessible: str,
        full: str,
        *,
        number: int = 10,
        pair_sense_exceptions=frozenset(),
    ) -> list[str]:
        a_path = path("3-freetalking", "talk-accessible", number, "topic")
        f_path = path("3-freetalking", "talk-full", number, "topic")
        _, errors = corpus(
            (a_path, accessible),
            (f_path, full),
            pair_sense_exceptions=pair_sense_exceptions,
        )
        return errors

    def test_reviewed_variant_specific_inventory_differences_are_allowed(self) -> None:
        cases = []
        a = set_vocab(deck("FT-9", new="", productive="regret"), "receptive", "regret|後悔する")
        f = deck("FT-9", new="regret|後悔する", productive="regret")
        cases.append((9, "regret A-receptive/F-new", a, f))

        a = deck("FT-16", new="nervousness|緊張", productive="nervousness")
        f = set_vocab(deck("FT-16", new="", productive="nervousness"), "receptive", "nervousness|緊張")
        cases.append((16, "nervousness A-new/F-receptive", a, f))

        a = deck("FT-20", new="emergency|緊急時", productive="emergency")
        f = set_vocab(deck("FT-20", new="", productive="emergency"), "assumed", "emergency|緊急時")
        cases.append((20, "emergency A-new/F-assumed", a, f))

        a = deck("FT-11", new="streaming|動画配信", productive="streaming")
        f = deck("FT-11", new="", productive="ordinary")
        cases.append((11, "streaming A-only", a, f))

        for number, label, accessible, full in cases:
            with self.subTest(label=label):
                errors = self._pair(accessible, full, number=number)
                self.assertFalse(any(
                    "accessible/full new" in error
                    or "accessible/full recycled" in error
                    or "new in one variant" in error
                    for error in errors
                ), errors)

    def test_new_and_legitimate_sibling_recycled_history_is_allowed(self) -> None:
        owner_f_path = path("3-freetalking", "talk-full", 9, "term-owner")
        a_path = path("3-freetalking", "talk-accessible", 10, "topic")
        f_path = path("3-freetalking", "talk-full", 10, "topic")
        _records, errors = corpus(
            (owner_f_path, deck("FT-9", new="term|用語", productive="term")),
            (a_path, deck("FT-10", new="term|用語", productive="term")),
            (f_path, deck("FT-10", new="other|別", recycled="term|用語|FT-9", productive="other")),
        )
        self.assertFalse(any("new in one variant" in error for error in errors), errors)
        self.assertFalse(any("recycled 'term'" in error or "owner FT-9 does not declare 'term'" in error for error in errors), errors)

    def test_unreviewed_cross_variant_japanese_sense_is_rejected(self) -> None:
        accessible = deck("FT-10", new="draft|下書き", productive="draft")
        full = set_vocab(deck("FT-10", new="", productive="draft"), "assumed", "draft|すきま風")
        errors = self._pair(accessible, full)
        self.assertTrue(any("'draft' has unreviewed sense rows" in error for error in errors), errors)

    def test_exact_reviewed_cross_variant_sense_exception_is_allowed(self) -> None:
        accessible = deck("FT-10", new="charge|料金", productive="charge")
        full = set_vocab(deck("FT-10", new="", productive="charge"), "assumed", "charge|充電する")
        exception = frozenset({
            ("FT-10", "charge", ("new", "料金", ""), ("assumed", "充電する", "")),
        })
        errors = self._pair(accessible, full, pair_sense_exceptions=exception)
        self.assertFalse(any("'charge' has unreviewed sense rows" in error for error in errors), errors)

        near_miss = frozenset({
            ("FT-10", "charge", ("new", "料金", ""), ("assumed", "充電", "")),
        })
        errors = self._pair(accessible, full, pair_sense_exceptions=near_miss)
        self.assertTrue(any("'charge' has unreviewed sense rows" in error for error in errors), errors)

    def test_production_pair_sense_exception_set_is_empty(self) -> None:
        self.assertEqual(integrity.FT_PAIR_SENSE_EXCEPTIONS, frozenset())

    def test_recycled_freetalk_owner_resolution_is_variant_aware(self) -> None:
        owner_a_path = path("3-freetalking", "talk-accessible", 9, "owner")
        owner_f_path = path("3-freetalking", "talk-full", 9, "owner")
        consumer_a_path = path("3-freetalking", "talk-accessible", 10, "consumer")
        consumer_f_path = path("3-freetalking", "talk-full", 10, "consumer")
        _, errors = corpus(
            (owner_a_path, deck("FT-9", new="regret|後悔する", productive="regret")),
            (owner_f_path, deck("FT-9", new="remorse|自責の念", productive="remorse")),
            (consumer_a_path, deck("FT-10", new="other|別", recycled="remorse|自責の念|FT-9", productive="other")),
            (consumer_f_path, deck("FT-10", new="other|別", recycled="regret|後悔する|FT-9", productive="other")),
        )
        self.assertTrue(any("owner FT-9 does not declare 'remorse'" in error for error in errors), errors)
        self.assertTrue(any("owner FT-9 does not declare 'regret'" in error for error in errors), errors)

    def test_mismatched_claim_order_is_rejected(self) -> None:
        accessible = deck("FT-10")
        full = deck("FT-10").replace('data-claim-id="claim-1"', 'data-claim-id="swap"', 1)
        errors = self._pair(accessible, full)
        self.assertTrue(any("ordered claim ids differ" in error for error in errors), errors)

    def test_legacy_claim_waiver_must_be_symmetric(self) -> None:
        relative = next(
            relative for relative, review_id in integrity.LEGACY_FT_CLAIM_WAIVERS.items()
            if review_id == "FT-1" and "-accessible/" in relative
        )
        a_path = ROOT / relative
        f_path = path("3-freetalking", "talk-between-two-countries-full", 1, "this-surprised-me-copy")
        _, errors = corpus(
            (a_path, deck("FT-1", ft_claims=False)),
            (f_path, deck("FT-1", ft_claims=True)),
        )
        self.assertTrue(any("legacy claim waiver must be symmetric" in error for error in errors), errors)


class ExpectedManifestMutationTests(unittest.TestCase):
    def test_deleting_terminal_deck_or_track_is_rejected(self) -> None:
        core = path("1-core-patterns", "core", 1, "one")
        ctx = path("2-contextual-english", "ctx", 1, "one")
        ft_a = path("3-freetalking", "talk-accessible", 1, "one")
        ft_f = path("3-freetalking", "talk-full", 1, "one")
        old_path, old_source = superseded()
        records, _ = integrity.audit_sources(
            {
                old_path: old_source,
                core: render(core, deck("CORE-1")),
                ctx: render(ctx, deck("CTX-1")),
                ft_a: render(ft_a, deck("FT-1")),
                ft_f: render(ft_f, deck("FT-1")),
            },
            tracks_root=ROOT,
            briefs={"CTX-1": "- **Entry floor:** Core 1\n"},
        )
        errors = integrity._logical_inventory_issues(
            records,
            expected={
                "1-core-patterns": frozenset({1, 2}),
                "2-contextual-english": frozenset({1}),
                "3-freetalking": frozenset({1}),
            },
        )
        self.assertTrue(any("CORE expected manifest differs" in error and "2" in error for error in errors), errors)
        without_ft = [record for record in records if record.track != "3-freetalking"]
        errors = integrity._logical_inventory_issues(
            without_ft,
            expected={
                "1-core-patterns": frozenset({1}),
                "2-contextual-english": frozenset({1}),
                "3-freetalking": frozenset({1}),
            },
        )
        self.assertTrue(any("FT expected manifest differs" in error for error in errors), errors)


class CurrentCorpusIntegrityTests(unittest.TestCase):
    def test_selector_finds_exact_current_inventory_and_green_status(self) -> None:
        records, errors = integrity.audit_corpus()
        self.assertEqual(len(records), 425)
        self.assertEqual(sum(not record.superseded for record in records), 424)
        self.assertEqual(sum(record.superseded for record in records), 1)
        superseded = [record for record in records if record.superseded]
        self.assertEqual(superseded[0].relative, integrity.SUPERSEDED_PROTOTYPE)
        self.assertEqual(errors, [])

    def test_current_corpus_diagnostic_is_green_after_repairs(self) -> None:
        _records, errors = integrity.audit_corpus()
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
