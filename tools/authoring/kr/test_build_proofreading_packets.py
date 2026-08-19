#!/usr/bin/env python3
"""Regression tests for the compact lesson proofreading projection."""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import build_proofreading_packets as packets


class ProofreadingPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.track = packets.KOREAN / "tracks" / "4-freetalking"
        cls.outputs, cls.records = packets.build_outputs(cls.track)

    def test_full_freetalking_projection_is_complete_and_compact(self):
        authored_decks = list((self.track / "courses").glob(
            "talk-*/lessons/*/lesson.html"
        ))
        self.assertEqual(len(self.records), len(authored_decks))
        theme_numbers = {record["themeNumber"] for record in self.records}
        self.assertEqual(
            len([path for path in self.outputs if path.parts[0] == "packets"]),
            len(theme_numbers),
        )
        json_records = [
            json.loads(line)
            for line in self.outputs[pathlib.Path("lessons.jsonl")].splitlines()
        ]
        self.assertEqual(len(json_records), len(authored_decks))
        self.assertTrue(all(len(record["sourceSha256"]) == 64
                            for record in json_records))

        first_packet = self.outputs[
            pathlib.Path("packets/01-between-two-countries.md")
        ]
        self.assertIn("# 프리토킹 교정 패킷 01 · 두 나라 사이", first_packet)
        self.assertIn("### 고급", first_packet)
        self.assertIn("### 중급", first_packet)
        self.assertIn("`question.ko`", first_packet)
        self.assertIn("`line.1.highlight.1.ko`", first_packet)
        self.assertNotIn("<script", first_packet)
        self.assertNotIn("data-sync-id", first_packet)

    def test_generic_release_tracks_have_complete_course_packets(self):
        expected = {
            "1-hangul": (14, 1),
            "2-core-patterns": (116, 12),
            "3-contextual-korean": (140, 14),
        }
        for track_name, (deck_count, packet_count) in expected.items():
            with self.subTest(track=track_name):
                track = packets.KOREAN / "tracks" / track_name
                outputs, records = packets.build_outputs(track)
                self.assertEqual(len(records), deck_count)
                self.assertEqual(
                    len([path for path in outputs if path.parts[0] == "packets"]),
                    packet_count,
                )
                self.assertTrue(all(record["pageContexts"] for record in records))
                for record in records:
                    locators = [
                        (entry["pageId"], entry["field"])
                        for entry in record["entries"]
                    ]
                    self.assertEqual(len(locators), len(set(locators)))

    def test_generic_packet_retains_titles_scripts_dialogue_and_task_text(self):
        track = packets.KOREAN / "tracks" / "2-core-patterns"
        outputs, records = packets.build_outputs(track)
        first = records[0]
        fields = {entry["field"] for entry in first["entries"]}
        self.assertIn("title.ko", fields)
        self.assertTrue(any(field.startswith("tutorScript.") for field in fields))
        self.assertTrue(any(field.startswith("text.") for field in fields))
        self.assertTrue(any(field.startswith("task.") for field in fields))
        packet_path = next(path for path in outputs if path.parts[0] == "packets")
        packet = outputs[packet_path]
        self.assertNotIn("<script", packet)
        self.assertNotIn("data-sync-id", packet)

    def test_pronunciation_is_outside_current_release_packet_scope(self):
        track = packets.KOREAN / "tracks" / "5-pronunciation"
        with self.assertRaisesRegex(ValueError, "release packets cover tracks 1-4"):
            packets.build_outputs(track)

    def test_generated_output_check_detects_stale_packet(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = pathlib.Path(temporary)
            packets.write_outputs(output, self.outputs)
            self.assertEqual(packets.check_outputs(output, self.outputs), [])

            packet = output / "packets" / "01-between-two-countries.md"
            packet.write_text(packet.read_text(encoding="utf-8") + "stale\n",
                              encoding="utf-8")
            errors = packets.check_outputs(output, self.outputs)
            self.assertEqual(errors, [f"stale {packet}"])

    def test_issue_validation_uses_hash_locator_and_current_text(self):
        record = self.records[0]
        entry = next(item for item in record["entries"]
                     if item["pageId"] == "q1" and item["field"] == "question.ko")
        issue = {
            "source": record["source"],
            "sourceSha256": record["sourceSha256"],
            "pageId": entry["pageId"],
            "field": entry["field"],
            "current": entry["text"],
            "suggested": entry["text"] + " 수정",
            "category": "ko-naturalness",
            "severity": "warning",
            "reason": "테스트 제안",
        }
        with tempfile.TemporaryDirectory() as temporary:
            issue_path = pathlib.Path(temporary) / "issues.jsonl"
            issue_path.write_text(
                json.dumps(issue, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            self.assertEqual(packets.validate_issues(issue_path, self.records), 1)

            issue["current"] = "stale text"
            issue_path.write_text(
                json.dumps(issue, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "current text is stale"):
                packets.validate_issues(issue_path, self.records)

    def test_applied_issue_verification_uses_suggested_text_not_old_hash(self):
        record = self.records[0]
        entry = next(item for item in record["entries"]
                     if item["pageId"] == "q1" and item["field"] == "question.ko")
        issue = {
            "source": record["source"],
            "sourceSha256": "0" * 64,
            "pageId": entry["pageId"],
            "field": entry["field"],
            "current": "이전 질문",
            "suggested": entry["text"],
            "category": "ko-naturalness",
            "severity": "warning",
            "reason": "적용 검증 테스트",
        }
        with tempfile.TemporaryDirectory() as temporary:
            issue_path = pathlib.Path(temporary) / "issues.jsonl"
            issue_path.write_text(
                json.dumps(issue, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            self.assertEqual(
                packets.validate_issues(issue_path, self.records, applied=True), 1
            )

            issue["suggested"] = entry["text"] + " 미적용"
            issue_path.write_text(
                json.dumps(issue, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "suggestion is not applied"):
                packets.validate_issues(issue_path, self.records, applied=True)

    def test_applied_issue_can_be_explicitly_superseded_by_a_later_round(self):
        record = self.records[0]
        entry = next(item for item in record["entries"]
                     if item["pageId"] == "q1" and item["field"] == "question.ko")
        first_suggestion = "첫 번째 교정"
        issue = {
            "source": record["source"],
            "sourceSha256": "0" * 64,
            "pageId": entry["pageId"],
            "field": entry["field"],
            "current": "원문",
            "suggested": first_suggestion,
            "category": "ko-naturalness",
            "severity": "warning",
            "reason": "첫 번째 검토",
            "supersededBy": "later.issues.jsonl:1",
        }
        later = dict(issue)
        later.update({
            "current": first_suggestion,
            "suggested": entry["text"],
            "reason": "더 완전한 후속 검토",
        })
        later.pop("supersededBy")
        with tempfile.TemporaryDirectory() as temporary:
            issue_path = pathlib.Path(temporary) / "issues.jsonl"
            later_path = pathlib.Path(temporary) / "later.issues.jsonl"
            issue_path.write_text(json.dumps(issue, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
            later_path.write_text(json.dumps(later, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
            self.assertEqual(
                packets.validate_issues(issue_path, self.records, applied=True), 1
            )
            later["suggested"] = entry["text"] + " 미적용"
            later_path.write_text(json.dumps(later, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "superseding issue .* is not applied"):
                packets.validate_issues(issue_path, self.records, applied=True)

    def test_hash_refresh_requires_unchanged_current_text(self):
        record = self.records[0]
        entry = next(item for item in record["entries"]
                     if item["pageId"] == "q1" and item["field"] == "question.ko")
        issue = {
            "source": record["source"],
            "sourceSha256": "0" * 64,
            "pageId": entry["pageId"],
            "field": entry["field"],
            "current": entry["text"],
            "suggested": entry["text"] + " 수정",
            "category": "ko-naturalness",
            "severity": "warning",
            "reason": "해시 갱신 테스트",
        }
        with tempfile.TemporaryDirectory() as temporary:
            issue_path = pathlib.Path(temporary) / "issues.jsonl"
            issue_path.write_text(
                json.dumps(issue, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            self.assertEqual(
                packets.refresh_issue_hashes(issue_path, self.records), 1
            )
            refreshed = json.loads(issue_path.read_text(encoding="utf-8"))
            self.assertEqual(refreshed["sourceSha256"], record["sourceSha256"])
            self.assertEqual(packets.validate_issues(issue_path, self.records), 1)

            issue["current"] = "충돌한 이전 문장"
            issue_path.write_text(
                json.dumps(issue, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "current text is stale"):
                packets.refresh_issue_hashes(issue_path, self.records)


if __name__ == "__main__":
    unittest.main()
