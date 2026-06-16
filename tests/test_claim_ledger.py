from __future__ import annotations

import json
import unittest

from src import claim_ledger


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


def identity_row(**overrides):
    row = {
        "player_id_internal": "pid_1",
        "gsis_id": "00-001",
        "sleeper_player_id": "sleeper_1",
        "fantasypros_id": "fp_1",
        "normalized_name": "ajbrown",
        "display_name": "A.J. Brown",
        "full_name": "A.J. Brown",
        "position": "WR",
        "current_team": "PHI",
    }
    row.update(overrides)
    return row


class ClaimLedgerTests(unittest.TestCase):
    def test_register_claim_source_dry_run_builds_source_object(self):
        result = claim_ledger.register_claim_source(
            source_id="Analyst-X",
            source_name="Analyst X",
            source_type="youtube",
            dry_run=True,
        )

        self.assertTrue(result["dry_run"])
        self.assertEqual(result["source"]["source_id"], "analyst_x")
        self.assertEqual(result["source"]["source_type"], "youtube")
        self.assertTrue(result["source"]["active"])

    def test_create_claim_dry_run_stores_model_run_and_players(self):
        result = claim_ledger.create_fantasy_claim(
            source_id="analyst_x",
            source_name="Analyst X",
            claim_text="A.J. Brown is a league winner",
            claim_type="breakout",
            claim_direction="positive",
            season=2025,
            week=4,
            players=["A.J. Brown"],
            model_run_id_at_claim="run_123",
            identity_rows=[identity_row()],
            dry_run=True,
        )

        self.assertTrue(result["dry_run"])
        self.assertEqual(result["claim"]["model_run_id_at_claim"], "run_123")
        self.assertEqual(result["claim"]["player_ids_json"], json.dumps(["pid_1"], separators=(",", ":")))
        self.assertEqual(result["players"][0]["player_id_internal"], "pid_1")

    def test_resolve_exact_player(self):
        result = claim_ledger.resolve_claim_players(
            [{"player_id_internal": "pid_1", "display_name": "A.J. Brown"}],
            identity_rows=[identity_row()],
        )

        self.assertEqual(result["resolved_players"][0]["player_id_internal"], "pid_1")
        self.assertEqual(result["resolved_players"][0]["match_method"], "player_id_internal")
        self.assertEqual(result["disambiguation"], [])

    def test_ambiguous_player_returns_disambiguation(self):
        result = claim_ledger.resolve_claim_players(
            ["Mike Williams"],
            identity_rows=[
                identity_row(
                    player_id_internal="pid_2",
                    normalized_name="mikewilliams",
                    display_name="Mike Williams",
                    position="WR",
                    current_team="LAC",
                ),
                identity_row(
                    player_id_internal="pid_3",
                    normalized_name="mikewilliams",
                    display_name="Mike Williams",
                    position="WR",
                    current_team="PIT",
                ),
            ],
        )

        self.assertEqual(result["resolved_players"][0]["match_method"], "ambiguous")
        self.assertEqual(len(result["disambiguation"]), 1)
        self.assertEqual(len(result["disambiguation"][0]["candidates"]), 2)

    def test_infer_weekly_window(self):
        window = claim_ledger.infer_evaluation_window(
            claim_id="claim_1",
            time_horizon="weekly",
            season=2025,
            week=4,
        )

        self.assertEqual(window["start_season"], 2025)
        self.assertEqual(window["start_week"], 4)
        self.assertEqual(window["end_season"], 2025)
        self.assertEqual(window["end_week"], 4)

    def test_infer_ros_window(self):
        window = claim_ledger.infer_evaluation_window(
            claim_id="claim_1",
            time_horizon="ros",
            season=2025,
            week=6,
        )

        self.assertEqual(window["start_week"], 6)
        self.assertEqual(window["end_week"], 18)
        self.assertEqual(window["evaluation_status"], "pending")

    def test_infer_dynasty_window_placeholder(self):
        window = claim_ledger.infer_evaluation_window(
            claim_id="claim_1",
            time_horizon="dynasty",
            season=2025,
        )

        self.assertEqual(window["end_season"], 2027)
        self.assertIsNone(window["end_week"])

    def test_reviewed_claims_require_review_fields(self):
        with self.assertRaisesRegex(ValueError, "claim_direction"):
            claim_ledger.create_fantasy_claim(
                source_id="analyst_x",
                source_name="Analyst X",
                claim_text="A.J. Brown is a league winner",
                claim_type="breakout",
                season=2025,
                review_status="reviewed",
                players=["A.J. Brown"],
                identity_rows=[identity_row()],
                dry_run=True,
            )

    def test_graded_claims_are_immutable_without_correction_status(self):
        with self.assertRaisesRegex(ValueError, "Graded claims are immutable"):
            claim_ledger.update_claim_status(
                "claim_1",
                "reviewed",
                current_claim={
                    "claim_id": "claim_1",
                    "source_id": "analyst_x",
                    "source_name": "Analyst X",
                    "claim_text": "A.J. Brown is a league winner",
                    "claim_type": "breakout",
                    "claim_direction": "positive",
                    "time_horizon": "weekly",
                    "season": 2025,
                    "review_status": "graded",
                    "player_ids_json": "[\"pid_1\"]",
                },
                dry_run=True,
            )

    def test_graded_claims_can_move_to_correction_status(self):
        result = claim_ledger.update_claim_status(
            "claim_1",
            "correction",
            current_claim={
                "claim_id": "claim_1",
                "source_id": "analyst_x",
                "source_name": "Analyst X",
                "claim_text": "A.J. Brown is a league winner",
                "claim_type": "breakout",
                "claim_direction": "positive",
                "time_horizon": "weekly",
                "season": 2025,
                "review_status": "graded",
                "player_ids_json": "[\"pid_1\"]",
            },
            dry_run=True,
        )

        self.assertEqual(result["review_status"], "correction")

    def test_add_claim_players_respects_graded_lock(self):
        with self.assertRaisesRegex(ValueError, "Graded claims are immutable"):
            claim_ledger.add_claim_players(
                claim_id="claim_1",
                players=["A.J. Brown"],
                current_claim={"claim_id": "claim_1", "review_status": "graded"},
                identity_rows=[identity_row()],
                dry_run=True,
            )


if __name__ == "__main__":
    unittest.main()
