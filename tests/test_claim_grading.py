from __future__ import annotations

import json
import unittest

from src import claim_grading


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


def claim_row(**overrides):
    row = {
        "claim_id": "claim_1",
        "source_id": "analyst_x",
        "source_name": "Analyst X",
        "claim_source_type": "youtube",
        "claim_text": "Start A.J. Brown",
        "claim_type": "start",
        "claim_direction": "start",
        "time_horizon": "weekly",
        "primary_player_id_internal": "pid_1",
        "primary_display_name": "A.J. Brown",
        "primary_position": "WR",
        "season": 2025,
        "week": 4,
        "evaluation_window_id": "claim_1:weekly:2025:4:2025:4",
        "start_season": 2025,
        "start_week": 4,
        "end_season": 2025,
        "end_week": 4,
        "scoring_profile_id": "ppr",
        "league_type_id": "redraft",
        "roster_format_id": "one_qb",
    }
    row.update(overrides)
    return row


def actual_row(**overrides):
    row = {
        "player_id_internal": "pid_1",
        "display_name": "A.J. Brown",
        "position": "WR",
        "actual_points": 22.0,
        "actual_rank_overall": 12,
        "actual_rank_position": 6,
    }
    row.update(overrides)
    return row


class ClaimGradingTests(unittest.TestCase):
    def test_start_claim_grading(self):
        grade = claim_grading.grade_claim(
            claim=claim_row(),
            actual_outcome=actual_row(),
            claim_grading_run_id="run_1",
        )

        self.assertEqual(grade["verdict"], "good_take")
        self.assertEqual(grade["claim_accuracy_score"], 1.0)

    def test_sit_claim_grading(self):
        grade = claim_grading.grade_claim(
            claim=claim_row(claim_type="sit", claim_direction="sit"),
            actual_outcome=actual_row(actual_points=4.0, actual_rank_overall=190, actual_rank_position=80),
            claim_grading_run_id="run_1",
        )

        self.assertEqual(grade["verdict"], "good_take")
        self.assertGreaterEqual(grade["claim_accuracy_score"], 0.9)

    def test_breakout_claim_grading(self):
        grade = claim_grading.grade_claim(
            claim=claim_row(claim_type="breakout", claim_direction="positive"),
            actual_outcome=actual_row(actual_points=24.0, actual_rank_overall=8, actual_rank_position=4),
            claim_grading_run_id="run_1",
        )

        self.assertEqual(grade["verdict"], "good_take")
        self.assertEqual(grade["claim_accuracy_score"], 1.0)

    def test_fraud_claim_grading(self):
        grade = claim_grading.grade_claim(
            claim=claim_row(claim_type="fraud", claim_direction="negative"),
            actual_outcome=actual_row(actual_points=26.0, actual_rank_overall=6, actual_rank_position=3),
            pigskin_snapshot={"projected_points": 25.0, "rank_overall": 7},
            claim_grading_run_id="run_1",
        )

        self.assertEqual(grade["verdict"], "fraud")
        self.assertLessEqual(grade["claim_accuracy_score"], 0.25)
        self.assertGreater(grade["pigskin_accuracy_score"], 0.8)

    def test_ranking_claim_grading(self):
        grade = claim_grading.grade_claim(
            claim=claim_row(claim_type="ranking", claim_direction="positive", claimed_rank=10),
            actual_outcome=actual_row(actual_rank_overall=12),
            claim_grading_run_id="run_1",
        )

        self.assertEqual(grade["verdict"], "good_take")
        self.assertGreater(grade["claim_accuracy_score"], 0.8)

    def test_dynasty_insufficient_data_is_inconclusive(self):
        grade = claim_grading.grade_claim(
            claim=claim_row(claim_type="dynasty", time_horizon="dynasty"),
            actual_outcome=actual_row(),
            claim_grading_run_id="run_1",
        )
        flags = json.loads(grade["missing_data_flags"])

        self.assertEqual(grade["verdict"], "inconclusive")
        self.assertIn("insufficient_dynasty_window", flags)

    def test_verdict_assignment(self):
        self.assertEqual(
            claim_grading.assign_verdict(
                claim_accuracy_score=0.9,
                pigskin_accuracy_score=0.4,
                market_accuracy_score=0.5,
                confidence_score=0.8,
                missing_data_flags=[],
            ),
            "galaxy_brain",
        )
        self.assertEqual(
            claim_grading.assign_verdict(
                claim_accuracy_score=None,
                missing_data_flags=["missing_actual_outcome"],
            ),
            "inconclusive",
        )

    def test_source_scorecard_aggregation(self):
        grades = [
            claim_grading.grade_claim(
                claim=claim_row(claim_id="claim_1"),
                actual_outcome=actual_row(),
                claim_grading_run_id="run_1",
            ),
            claim_grading.grade_claim(
                claim=claim_row(claim_id="claim_2", claim_type="fraud", claim_direction="negative"),
                actual_outcome=actual_row(actual_points=26.0, actual_rank_overall=6, actual_rank_position=3),
                pigskin_snapshot={"projected_points": 25.0, "rank_overall": 7},
                claim_grading_run_id="run_1",
            ),
        ]

        scorecards = claim_grading.build_claim_source_scorecards(grades, claim_grading_run_id="run_1")

        self.assertEqual(len(scorecards), 1)
        self.assertEqual(scorecards[0]["claim_count"], 2)
        self.assertEqual(scorecards[0]["good_take_count"], 1)
        self.assertEqual(scorecards[0]["fraud_count"], 1)
        self.assertEqual(scorecards[0]["source_type"], "youtube")

    def test_missing_actuals_flag(self):
        grade = claim_grading.grade_claim(
            claim=claim_row(),
            actual_outcome=None,
            claim_grading_run_id="run_1",
        )
        flags = json.loads(grade["missing_data_flags"])

        self.assertEqual(grade["verdict"], "inconclusive")
        self.assertIn("missing_actual_outcome", flags)

    def test_no_grade_without_claim_grading_run_id(self):
        with self.assertRaisesRegex(ValueError, "claim_grading_run_id is required"):
            claim_grading.grade_claim(
                claim=claim_row(),
                actual_outcome=actual_row(),
                claim_grading_run_id="",
            )

    def test_load_actual_outcomes_uses_curated_actuals(self):
        client = FakeClient()

        claim_grading.load_actual_outcomes(
            player_ids=["pid_1"],
            start_season=2025,
            start_week=4,
            end_season=2025,
            end_week=4,
            client=client,
            dataset_id="test_dataset",
        )

        sql, job_config = client.query_calls[0]
        params = {param.name: param.value for param in job_config.query_parameters if hasattr(param, "value")}
        self.assertIn("analytics_player_fantasy_points_by_profile", sql)
        self.assertNotIn("weekly_metrics", sql)
        self.assertEqual(params["start_season"], 2025)

    def test_run_claim_grading_dry_run(self):
        result = claim_grading.run_claim_grading(
            claims=[claim_row()],
            actuals_by_claim_id={"claim_1": actual_row()},
            pigskin_by_claim_id={"claim_1": None},
            market_by_claim_id={"claim_1": None},
            dry_run=True,
        )

        self.assertTrue(result["dry_run"])
        self.assertEqual(result["grade_count"], 1)
        self.assertEqual(result["scorecard_count"], 1)


if __name__ == "__main__":
    unittest.main()
