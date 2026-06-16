from __future__ import annotations

import unittest
from unittest.mock import patch

import pandas as pd

from src import generate_pigskin_rankings as rankings


class FakeClient:
    project = "test-project"


class PigskinRankingModelRunTests(unittest.TestCase):
    def test_successful_generation_creates_complete_model_run_and_writes_metadata(self):
        fake_client = FakeClient()
        candidates = pd.DataFrame([{"player_id": "p1"}])

        def fake_generate_position_rows(api_key, model_name, position, candidates_df, ranking_version, run_metadata):
            return [{
                "player_id": "p1",
                "rank": 1,
                "ranking_version": ranking_version,
                "model_run_id": run_metadata["model_run_id"],
                "scoring_profile_id": run_metadata["scoring_profile_id"],
                "league_type_id": run_metadata["league_type_id"],
                "roster_format_id": run_metadata["roster_format_id"],
                "feature_config_version_id": run_metadata["feature_config_version_id"],
                "source_freshness_snapshot_id": run_metadata["source_freshness_snapshot_id"],
            }]

        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}), \
            patch.object(rankings.bigquery, "Client", return_value=fake_client), \
            patch.object(rankings, "materialize_pigskin_rankings") as materialize, \
            patch.object(rankings, "fetch_generation_context", return_value={"season": 2026, "week": None}), \
            patch.object(rankings, "create_source_freshness_snapshot", return_value="fresh-1") as snapshot, \
            patch.object(rankings, "create_model_run", return_value="run-1") as create_run, \
            patch.object(rankings, "get_code_version", return_value="abc123"), \
            patch.object(rankings, "fetch_candidates", return_value=candidates), \
            patch.object(rankings, "generate_position_rows", side_effect=fake_generate_position_rows), \
            patch.object(rankings, "write_rankings") as write_rankings, \
            patch.object(rankings, "mark_model_run_complete") as mark_complete, \
            patch.object(rankings, "mark_model_run_failed") as mark_failed:

            ranking_version, row_count = rankings.generate_rankings(
                dataset_id="test_dataset",
                project_id="test-project",
                model_name="test-model",
                model_version="v-test",
                prompt_version="prompt-test",
                scoring_profile_id="ppr",
                league_type_id="redraft",
                roster_format_id="one_qb",
                feature_config_version_id="config-1",
                positions=["QB"],
            )

        self.assertTrue(ranking_version.startswith("pigskin-llm-"))
        self.assertEqual(row_count, 1)
        materialize.assert_called_once_with(fake_client, dataset_id="test_dataset", dry_run=False)
        snapshot.assert_called_once()
        create_run.assert_called_once()
        create_kwargs = create_run.call_args.kwargs
        self.assertEqual(create_kwargs["run_type"], "pigskin_rankings")
        self.assertEqual(create_kwargs["model_name"], "test-model")
        self.assertEqual(create_kwargs["model_version"], "v-test")
        self.assertEqual(create_kwargs["prompt_version"], "prompt-test")
        self.assertEqual(create_kwargs["code_version"], "abc123")
        self.assertEqual(create_kwargs["season"], 2026)
        self.assertEqual(create_kwargs["scoring_profile_id"], "ppr")
        self.assertEqual(create_kwargs["league_type_id"], "redraft")
        self.assertEqual(create_kwargs["roster_format_id"], "one_qb")
        self.assertEqual(create_kwargs["feature_config_version_id"], "config-1")
        self.assertEqual(create_kwargs["source_freshness_snapshot_id"], "fresh-1")

        rows = write_rankings.call_args.args[2]
        self.assertEqual(rows[0]["model_run_id"], "run-1")
        self.assertEqual(rows[0]["ranking_version"], ranking_version)
        self.assertEqual(rows[0]["scoring_profile_id"], "ppr")
        mark_complete.assert_called_once()
        mark_failed.assert_not_called()

    def test_generation_failure_marks_model_run_failed_and_reraises_original(self):
        fake_client = FakeClient()
        candidates = pd.DataFrame([{"player_id": "p1"}])

        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}), \
            patch.object(rankings.bigquery, "Client", return_value=fake_client), \
            patch.object(rankings, "materialize_pigskin_rankings"), \
            patch.object(rankings, "fetch_generation_context", return_value={"season": 2026, "week": None}), \
            patch.object(rankings, "create_source_freshness_snapshot", return_value="fresh-1"), \
            patch.object(rankings, "create_model_run", return_value="run-1"), \
            patch.object(rankings, "get_code_version", return_value="abc123"), \
            patch.object(rankings, "fetch_candidates", return_value=candidates), \
            patch.object(rankings, "generate_position_rows", side_effect=RuntimeError("model exploded")), \
            patch.object(rankings, "write_rankings") as write_rankings, \
            patch.object(rankings, "mark_model_run_complete") as mark_complete, \
            patch.object(rankings, "mark_model_run_failed") as mark_failed:

            with self.assertRaisesRegex(RuntimeError, "model exploded"):
                rankings.generate_rankings(
                    dataset_id="test_dataset",
                    project_id="test-project",
                    positions=["QB"],
                )

        write_rankings.assert_not_called()
        mark_complete.assert_not_called()
        mark_failed.assert_called_once()
        self.assertEqual(mark_failed.call_args.args[0], "run-1")
        self.assertIn("model exploded", mark_failed.call_args.args[1])

    def test_build_final_row_preserves_ranking_version_and_adds_model_run_id(self):
        row = rankings.build_final_row(
            {
                "rank": 12,
                "ranking_score": 77.7,
                "tier": "starter",
                "pigskin_verdict": "fine",
                "rank_rationale": "role",
                "risk_flags": "none",
                "what_would_change_mind": "usage",
                "data_snapshot_label": "stats_through_2025",
            },
            {
                "rank": 3,
                "ranking_score": 91.2,
                "tier": "elite",
                "pigskin_verdict": "real profile",
            },
            "pigskin-llm-test",
            "test-model",
            {
                "model_run_id": "run-1",
                "scoring_profile_id": "ppr",
                "league_type_id": "redraft",
                "roster_format_id": "one_qb",
                "feature_config_version_id": None,
                "source_freshness_snapshot_id": "fresh-1",
                "prompt_version": "prompt-test",
            },
        )

        self.assertEqual(row["ranking_version"], "pigskin-llm-test")
        self.assertEqual(row["model_run_id"], "run-1")
        self.assertEqual(row["prompt_version"], "prompt-test")
        self.assertEqual(row["candidate_rank"], 12)


if __name__ == "__main__":
    unittest.main()
