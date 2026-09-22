from __future__ import annotations

import json
import unittest
from pathlib import Path

from src import content_briefs


class FakeJob:
    def __init__(self, rows=None):
        self.rows = rows or []

    def result(self):
        return self.rows


class FakeClient:
    project = "test-project"

    def __init__(self, rows=None):
        self.rows = rows or []
        self.query_calls = []
        self.insert_calls = []

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        return FakeJob(self.rows)

    def insert_rows_json(self, table_id, rows):
        self.insert_calls.append((table_id, rows))
        return []


class FakeLoadJob:
    errors = None

    def result(self):
        return []


class FakeLoadClient(FakeClient):
    def __init__(self, rows=None):
        super().__init__(rows=rows)
        self.load_calls = []

    def load_table_from_json(self, rows, table_id, job_config=None):
        self.load_calls.append((table_id, rows, job_config))
        return FakeLoadJob()


def fraud_row(**overrides):
    row = {
        "packet_id": "fraud_1",
        "player_id_internal": "pid_1",
        "display_name": "Box Score Benny",
        "position": "WR",
        "team": "PIT",
        "recommended_take": "Benny is a touchdown mirage.",
        "packet_text": "Benny scored on thin usage while role quality fell.",
        "counterargument": "A route spike would matter.",
        "snark_hooks_json": "[\"The points are wearing a fake mustache.\"]",
        "confidence_score": 0.82,
        "source_freshness_json": "{\"table\":\"fraud_watch_packets\"}",
        "missing_data_flags": "[]",
    }
    row.update(overrides)
    return row


def breakout_row(**overrides):
    row = {
        "packet_id": "breakout_1",
        "player_id_internal": "pid_2",
        "display_name": "Usage Larry",
        "position": "RB",
        "team": "GB",
        "recommended_take": "Larry is getting the role before the market notices.",
        "packet_text": "Snap share, route rate, and touch share are climbing.",
        "counterargument": "The depth chart can still flatten him.",
        "snark_hooks_json": "[\"The market is still buffering.\"]",
        "confidence_score": 0.77,
        "source_freshness_json": "{\"table\":\"sleeper_breakout_packets\"}",
        "missing_data_flags": "[]",
    }
    row.update(overrides)
    return row


def ranking_row(**overrides):
    row = {
        "player_id_internal": "pid_3",
        "display_name": "Ranky McRankface",
        "position": "QB",
        "team": "SF",
        "projection_horizon": "ros",
        "rank_overall": 20,
        "rank_position": 8,
        "tier": "QB1",
        "projected_points_or_value": 285.5,
        "confidence_score": 0.74,
        "risk_score": 0.31,
        "source_freshness_json": "{\"table\":\"projection_rankings_current\"}",
        "missing_data_flags": "[]",
    }
    row.update(overrides)
    return row


def scorecard_row(**overrides):
    row = {
        "claim_grading_run_id": "grade_run_1",
        "source_id": "analyst_x",
        "source_name": "Analyst X",
        "source_type": "youtube",
        "graded_count": 12,
        "average_claim_accuracy": 0.42,
        "good_take_count": 2,
        "wrong_count": 7,
        "fraud_count": 3,
        "galaxy_brain_count": 0,
        "source_freshness_json": "{\"table\":\"claim_source_scorecards\"}",
        "missing_data_flags": "[]",
    }
    row.update(overrides)
    return row


class ContentBriefTests(unittest.TestCase):
    def test_fraud_watch_brief_builder(self):
        brief = content_briefs.build_fraud_watch_brief(
            season=2025,
            week=7,
            packets=[fraud_row()],
        )

        self.assertEqual(brief["brief"]["brief_type"], "fraud_watch_show")
        self.assertEqual(len(brief["items"]), 1)
        self.assertIn("Benny", brief["items"][0]["title"])
        self.assertIn("llm_prompt_payload_json", brief["brief_json"])

    def test_sleeper_breakout_brief_builder(self):
        brief = content_briefs.build_sleeper_breakout_brief(
            season=2025,
            week=7,
            packets=[breakout_row()],
        )

        self.assertEqual(brief["brief"]["brief_type"], "sleeper_breakout_show")
        self.assertIn("Usage Larry", brief["items"][0]["title"])
        self.assertIn("counterargument", brief["items"][0])

    def test_rankings_debate_brief_builder(self):
        brief = content_briefs.build_rankings_debate_brief(
            season=2025,
            week=7,
            ranking_rows=[ranking_row()],
        )

        self.assertEqual(brief["brief"]["brief_type"], "rankings_debate_show")
        self.assertIn("QB8", brief["items"][0]["claim"])

    def test_meatbag_accountability_brief_builder(self):
        brief = content_briefs.build_meatbag_accountability_brief(
            season=2025,
            week=7,
            scorecard_rows=[scorecard_row()],
        )

        self.assertEqual(brief["brief"]["brief_type"], "meatbag_accountability_show")
        self.assertIn("Analyst X", brief["items"][0]["title"])
        self.assertEqual(brief["items"][0]["item_type"], "claim")

    def test_full_weekly_show_prep_builder(self):
        fraud = content_briefs.build_fraud_watch_brief(season=2025, week=7, packets=[fraud_row()])
        breakout = content_briefs.build_sleeper_breakout_brief(season=2025, week=7, packets=[breakout_row()])

        brief = content_briefs.build_full_weekly_show_prep(
            season=2025,
            week=7,
            source_briefs=[fraud, breakout],
        )

        self.assertEqual(brief["brief"]["brief_type"], "full_weekly_show_prep")
        self.assertEqual(len(brief["items"]), 2)
        self.assertIn("Fraud Watch Show Brief", brief["items"][0]["title"])

    def test_item_caps(self):
        rows = [fraud_row(packet_id=f"fraud_{index}", display_name=f"Player {index}") for index in range(20)]

        brief = content_briefs.build_fraud_watch_brief(
            season=2025,
            week=7,
            packets=rows,
            limit=99,
        )

        self.assertEqual(len(brief["items"]), content_briefs.ITEM_CAPS["fraud_watch_show"])

    def test_token_estimate_bounds(self):
        rows = [
            fraud_row(
                packet_id=f"fraud_{index}",
                display_name=f"Player {index}",
                packet_text="Evidence " * 1000,
            )
            for index in range(8)
        ]

        brief = content_briefs.build_fraud_watch_brief(season=2025, week=7, packets=rows, limit=8)

        self.assertLessEqual(brief["brief"]["token_estimate"], content_briefs.MAX_TOKEN_ESTIMATE)
        self.assertLessEqual(len(brief["brief"]["brief_text"]), content_briefs.MAX_BRIEF_TEXT_CHARS)

    def test_source_freshness_included(self):
        brief = content_briefs.build_fraud_watch_brief(season=2025, week=7, packets=[fraud_row()])
        freshness = json.loads(brief["brief"]["source_freshness_json"])

        self.assertEqual(freshness["item_count"], 1)
        self.assertEqual(freshness["sources"][0]["table"], "fraud_watch_packets")

    def test_missing_flags_included(self):
        brief = content_briefs.build_fraud_watch_brief(
            season=2025,
            week=7,
            packets=[fraud_row(missing_data_flags="[\"missing_market_context\"]")],
        )
        flags = json.loads(brief["brief"]["missing_data_flags"])

        self.assertIn("missing_market_context", flags)

    def test_no_raw_table_references(self):
        client = FakeClient(rows=[fraud_row()])

        content_briefs.build_fraud_watch_brief(
            season=2025,
            week=7,
            client=client,
            dataset_id="test_dataset",
        )

        sql = client.query_calls[0][0]
        self.assertIn("fraud_watch_packets", sql)
        self.assertNotIn("weekly_metrics", sql)
        self.assertNotIn("play_by_play", sql)
        self.assertNotIn("sleeper_roster_players", sql)
        self.assertNotIn("market_values", sql)

    def test_ranking_loader_dedupes_player_rows(self):
        client = FakeClient(rows=[])

        content_briefs.build_weekly_streamers_brief(
            season=2025,
            week=1,
            client=client,
            dataset_id="test_dataset",
        )

        sql = client.query_calls[0][0]
        self.assertIn("projection_rankings_current", sql)
        self.assertIn("QUALIFY ROW_NUMBER()", sql)
        self.assertIn("PARTITION BY COALESCE(player_id_internal", sql)

    def test_llm_prompt_payload_is_deterministic(self):
        first = content_briefs.build_fraud_watch_brief(season=2025, week=7, packets=[fraud_row()])
        second = content_briefs.build_fraud_watch_brief(season=2025, week=7, packets=[fraud_row()])

        self.assertEqual(
            first["brief_json"]["llm_prompt_payload_json"],
            second["brief_json"]["llm_prompt_payload_json"],
        )

    def test_builder_source_does_not_call_llms(self):
        source = Path("src/content_briefs.py").read_text(encoding="utf-8")

        for forbidden in ("google.genai", "openai", "generate_content"):
            self.assertNotIn(forbidden, source)

    def test_demo_brief_marker_requires_guard(self):
        source = Path("src/content_briefs.py").read_text(encoding="utf-8")

        if "DEMO BRIEF - DO NOT USE FOR PUBLIC CONTENT" in source:
            self.assertIn("ENABLE_DEMO_CONTENT_BRIEFS", source)

    def test_save_content_brief_dry_run(self):
        brief = content_briefs.build_fraud_watch_brief(season=2025, week=7, packets=[fraud_row()])

        result = content_briefs.save_content_brief(brief, dry_run=True)

        self.assertTrue(result["dry_run"])
        self.assertEqual(result["item_count"], 1)

    def test_save_content_brief_uses_load_job_for_reviewable_rows(self):
        client = FakeLoadClient()
        brief = content_briefs.build_fraud_watch_brief(season=2025, week=7, packets=[fraud_row()])

        result = content_briefs.save_content_brief(brief, client=client, dataset_id="test_dataset")

        self.assertFalse(result["dry_run"])
        self.assertEqual(len(client.load_calls), 3)
        self.assertEqual(client.insert_calls, [])


if __name__ == "__main__":
    unittest.main()
