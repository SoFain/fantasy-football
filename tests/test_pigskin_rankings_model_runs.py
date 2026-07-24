from __future__ import annotations

import unittest
from unittest.mock import patch

import pandas as pd

from src import generate_pigskin_rankings as rankings


class FakeClient:
    project = "test-project"


class FakeJob:
    def result(self):
        return None


class FakeTable:
    def __init__(self, schema):
        self.schema = schema


class FakeLoadClient:
    project = "test-project"

    def __init__(self):
        self.load_calls = []
        self.loaded_dataframes = []
        self.query_calls = []
        self.deleted_tables = []
        self.history_schema = [
            rankings.bigquery.SchemaField("ranking_version", "STRING"),
            rankings.bigquery.SchemaField("generated_at", "TIMESTAMP"),
            rankings.bigquery.SchemaField("adjudicated_at", "TIMESTAMP"),
            rankings.bigquery.SchemaField("position", "STRING"),
            rankings.bigquery.SchemaField("scoring_profile_id", "STRING"),
            rankings.bigquery.SchemaField("league_type_id", "STRING"),
            rankings.bigquery.SchemaField("roster_format_id", "STRING"),
        ]
        self.final_schema = [
            rankings.bigquery.SchemaField("ranking_version", "STRING"),
            rankings.bigquery.SchemaField("generated_at", "INTEGER"),
            rankings.bigquery.SchemaField("adjudicated_at", "INTEGER"),
        ]

    def get_table(self, table_id):
        if table_id.endswith(".analytics_pigskin_rankings_history"):
            return FakeTable(self.history_schema)
        if table_id.endswith(".analytics_pigskin_rankings"):
            return FakeTable(self.final_schema)
        raise AssertionError(f"unexpected table {table_id}")

    def load_table_from_dataframe(self, df, table_id, job_config):
        self.loaded_dataframes.append(df.copy())
        self.load_calls.append((table_id, job_config))
        return FakeJob()

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        return FakeJob()

    def delete_table(self, table_id, not_found_ok=False):
        self.deleted_tables.append((table_id, not_found_ok))


class PigskinRankingModelRunTests(unittest.TestCase):
    def test_default_position_limits_use_owner_approved_te35_depth(self):
        self.assertEqual(rankings.DEFAULT_POSITION_LIMITS["QB"], 45)
        self.assertEqual(rankings.DEFAULT_POSITION_LIMITS["RB"], 80)
        self.assertEqual(rankings.DEFAULT_POSITION_LIMITS["WR"], 100)
        self.assertEqual(rankings.DEFAULT_POSITION_LIMITS["TE"], 35)
        self.assertEqual(rankings.get_position_limit("TE", None), 35)

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
        materialize.assert_called_once_with(
            fake_client,
            dataset_id="test_dataset",
            dry_run=False,
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
        )
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

    def test_model_cannot_overwrite_deterministic_presentation_fields(self):
        row = rankings.build_final_row(
            {
                "rank": 2,
                "ranking_score": 95,
                "tier": "elite",
                "pigskin_verdict": "Deterministic verdict.",
                "rank_rationale": "Formula components.",
                "risk_flags": "SOURCE_FLAG",
                "what_would_change_mind": "Verified role change.",
                "data_snapshot_label": "snapshot",
            },
            {
                "tier": "deep or watchlist",
                "pigskin_verdict": "Model rewrite.",
                "rank_rationale": "Model rewrite.",
                "risk_flags": "MODEL_FLAG",
                "what_would_change_mind": "Anything.",
                "adjustment_code": "NO_ADJUSTMENT",
                "requested_rank_delta": 0,
            },
            "version",
            "model",
            {
                "model_run_id": "run",
                "scoring_profile_id": "standard",
                "league_type_id": "redraft",
                "roster_format_id": "one_qb",
                "feature_config_version_id": None,
                "source_freshness_snapshot_id": "fresh",
                "prompt_version": "guarded",
            },
        )
        self.assertEqual(row["tier"], "elite")
        self.assertEqual(row["pigskin_verdict"], "Deterministic verdict.")
        self.assertEqual(row["rank_rationale"], "Formula components.")
        self.assertEqual(row["risk_flags"], "SOURCE_FLAG")
        self.assertEqual(row["what_would_change_mind"], "Verified role change.")

    def test_injury_adjustment_requires_a_matching_games_missed_range(self):
        row = rankings.build_final_row(
            {"rank": 8, "ranking_score": 72, "data_snapshot_label": "snapshot"},
            {
                "requested_rank_delta": -4,
                "adjustment_code": "INJURY_3_5",
                "adjustment_detail": "Expected absence suppresses early-season availability.",
                "adjustment_evidence": "source=team estimate; expected_games_missed=4",
                "estimated_regular_season_games_missed": 4,
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

        rankings.validate_adjustment(row)
        self.assertEqual(row["llm_rank_delta"], -4)
        self.assertEqual(row["ranking_score"], 72)

    def test_injury_adjustment_fails_closed_without_a_matching_games_missed_range(self):
        row = {
            "llm_adjustment_code": "INJURY_3_5",
            "llm_rank_delta": -4,
            "llm_estimated_games_missed": None,
            "llm_adjustment_detail": "Injury concern.",
            "llm_adjustment_evidence": "Sleeper injury status only",
        }

        with self.assertRaisesRegex(ValueError, "estimated_regular_season_games_missed"):
            rankings.validate_adjustment(row)

    def test_suspension_adjustment_requires_source_backed_games_missed(self):
        row = {
            "llm_adjustment_code": "SUSPENSION_3_5",
            "llm_rank_delta": -3,
            "llm_estimated_games_missed": 4,
            "llm_adjustment_detail": "League suspension removes four regular-season games.",
            "llm_adjustment_evidence": "source=league transaction; games=4",
        }

        rankings.validate_adjustment(row)

    def test_suspension_rationale_preserves_formula_and_absence_provenance(self):
        rationale = rankings.build_scientific_rank_rationale({
            "position": "RB",
            "candidate_rank": 6,
            "rank": 10,
            "rank_rationale": "Formula v3 placed the player at RB6.",
            "llm_adjustment_code": "SUSPENSION_3_5",
            "llm_adjustment_detail": "League suspension removes four games.",
            "llm_adjustment_evidence": "source=league transaction; announced=2026-07-19",
            "llm_estimated_games_missed": 4,
            "llm_rank_delta": -4,
        })

        self.assertIn("Formula v3 placed the player at RB6.", rationale)
        self.assertIn("Post-formula suspension adjustment", rationale)
        self.assertIn("Estimated regular-season games missed: 4", rationale)
        self.assertIn("announced=2026-07-19", rationale)
        self.assertIn("Candidate RB6 became final RB10 (-4 ranks)", rationale)

    def test_final_rationale_preserves_formula_and_explains_injury_movement(self):
        candidates = pd.DataFrame([
            {
                "player_id": f"p{i}", "player_name": f"Player {i}", "position": "WR",
                "rank": i, "ranking_score": 100 - i,
                "rank_rationale": f"Formula v2 placed Player {i} at WR{i}.",
                "data_snapshot_label": "snapshot", "sleeper_injury_status": None,
            }
            for i in range(1, 4)
        ])
        payload = {"rankings": [
            {
                "player_id": "p1", "adjustment_code": "INJURY_1_2", "requested_rank_delta": -2,
                "adjustment_detail": "Team timetable projects a two-game absence.",
                "adjustment_evidence": "source=team announcement; expected_games_missed=2",
                "estimated_regular_season_games_missed": 2,
            },
            {"player_id": "p2", "adjustment_code": "NO_ADJUSTMENT", "requested_rank_delta": 0},
            {"player_id": "p3", "adjustment_code": "NO_ADJUSTMENT", "requested_rank_delta": 0},
        ]}
        rows = rankings.normalize_model_rankings(
            "WR", candidates, payload, "v2", "test-model",
            {
                "model_run_id": "run", "scoring_profile_id": "standard",
                "league_type_id": "redraft", "roster_format_id": "one_qb",
                "feature_config_version_id": None, "source_freshness_snapshot_id": "fresh",
                "prompt_version": "scientific-adjustment-v1",
            },
        )
        adjusted = next(row for row in rows if row["player_id"] == "p1")

        self.assertIn("Formula v2 placed Player 1 at WR1.", adjusted["rank_rationale"])
        self.assertIn("Post-formula injury adjustment", adjusted["rank_rationale"])
        self.assertIn("Estimated regular-season games missed: 2", adjusted["rank_rationale"])
        self.assertIn("source=team announcement", adjusted["rank_rationale"])
        self.assertIn("Candidate WR1 became final WR2 (-1 ranks)", adjusted["rank_rationale"])

    def test_no_adjustment_cannot_move_a_rank(self):
        row = {
            "llm_adjustment_code": "NO_ADJUSTMENT",
            "llm_rank_delta": 1,
            "llm_estimated_games_missed": None,
            "llm_adjustment_detail": "",
            "llm_adjustment_evidence": "",
        }

        with self.assertRaisesRegex(ValueError, "NO_ADJUSTMENT permits"):
            rankings.validate_adjustment(row)

    def test_prompt_forbids_discretionary_formula_reinterpretation(self):
        frame = pd.DataFrame([{
            "player_id": "p1", "player_name": "Player One", "current_team": "A",
            "sleeper_team": "A", "sleeper_active": True, "sleeper_status": "Active",
            "sleeper_depth_chart_position": "TE", "sleeper_depth_chart_order": 1,
            "rank": 1, "ranking_score": 90, "raw_ranking_score": 1.0, "depth_chart_penalty": 0,
            "avg_profile_points": 10, "avg_ppr": 10, "avg_grade": 80, "avg_opportunity": 80,
            "avg_efficiency": 80, "avg_epa_per_opportunity": 0.1, "season_total_epa": 10,
            "season_passing_epa": 0, "season_rushing_epa": 0, "season_receiving_epa": 10,
            "avg_role_quality": 80, "avg_role_fragility": 10, "avg_wopr": 0.5,
            "latest_season_wopr": 0.5, "previous_season_wopr": 0.4, "two_years_ago_wopr": 0.3,
            "avg_target_share": 0.2, "latest_season_target_share": 0.2,
            "previous_season_target_share": 0.2, "avg_carry_share": 0,
            "latest_season_carry_share": 0, "previous_season_carry_share": 0,
            "latest_season_ppr": 10, "previous_season_ppr": 9, "risk_flags": "",
            "rank_rationale": "deterministic formula evidence", "sleeper_injury_status": "Questionable",
        }])
        prompt = rankings.build_prompt("TE", frame, "v1", "standard")
        self.assertIn("exception-repair layer", prompt)
        self.assertIn("requested_rank_delta", prompt)
        self.assertIn("Questionable status alone has zero rank effect", prompt)
        self.assertNotIn("SUSTAINABILITY_UP", prompt)

    def test_model_requests_are_applied_by_deterministic_reorder(self):
        candidates = pd.DataFrame([
            {"player_id": f"p{i}", "rank": i, "ranking_score": 100 - i, "data_snapshot_label": "snapshot"}
            for i in range(1, 5)
        ])
        payload = {"rankings": [
            {"player_id": "p1", "adjustment_code": "NO_ADJUSTMENT", "requested_rank_delta": 0},
            {"player_id": "p2", "adjustment_code": "NO_ADJUSTMENT", "requested_rank_delta": 0},
            {"player_id": "p3", "adjustment_code": "NO_ADJUSTMENT", "requested_rank_delta": 0},
            {"player_id": "p4", "adjustment_code": "CURRENT_ROLE_UPGRADE", "requested_rank_delta": 2,
             "adjustment_detail": "Verified starter role.", "adjustment_evidence": "depth=1"},
        ]}
        rows = rankings.normalize_model_rankings("TE", candidates, payload, "v1", "model", {
            "model_run_id": "run", "scoring_profile_id": "standard", "league_type_id": "redraft",
            "roster_format_id": "one_qb", "feature_config_version_id": None,
            "source_freshness_snapshot_id": "fresh", "prompt_version": "guarded",
        })
        by_id = {row["player_id"]: row for row in rows}
        self.assertEqual(by_id["p4"]["rank"], 3)
        self.assertEqual(by_id["p4"]["llm_adjustment_code"], "CURRENT_ROLE_UPGRADE")
        self.assertEqual(by_id["p3"]["llm_adjustment_code"], "ORDER_REBALANCE")

    def test_questionable_status_cannot_drive_injury_movement(self):
        row = {
            "llm_adjustment_code": "INJURY_1_2", "llm_rank_delta": -1,
            "llm_estimated_games_missed": 1, "llm_adjustment_detail": "Questionable.",
            "llm_adjustment_evidence": "Sleeper status", "sleeper_injury_status": "Questionable",
        }
        with self.assertRaisesRegex(ValueError, "Questionable status cannot move"):
            rankings.validate_adjustment(row)

    def test_final_pool_candidate_omission_is_rejected(self):
        candidates = pd.DataFrame([
            {"player_id": "p1", "rank": 1, "ranking_score": 90, "data_snapshot_label": "snapshot"},
            {"player_id": "p2", "rank": 2, "ranking_score": 80, "data_snapshot_label": "snapshot"},
        ])
        payload = {
            "rankings": [
                {"player_id": "p1", "rank": 1, "ranking_score": 90},
            ]
        }

        with self.assertRaisesRegex(ValueError, "omitted 1 candidates"):
            rankings.normalize_model_rankings(
                "TE",
                candidates,
                payload,
                "rank-v1",
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

    def test_write_rankings_replaces_only_matching_profile_scope(self):
        client = FakeLoadClient()
        rows = [{
            "ranking_version": "pigskin-llm-test",
            "generated_at": pd.Timestamp("2026-07-03T06:00:00Z"),
            "adjudicated_at": pd.Timestamp("2026-07-03T06:00:00Z"),
            "position": "QB",
            "scoring_profile_id": "ppr",
            "league_type_id": "redraft",
            "roster_format_id": "one_qb",
        }]

        rankings.write_rankings(client, "test_dataset", rows)

        self.assertEqual(len(client.load_calls), 2)
        staging_table_id, staging_config = client.load_calls[0]
        history_table_id, history_config = client.load_calls[1]
        self.assertIn(".analytics_pigskin_rankings_staging_", staging_table_id)
        self.assertTrue(history_table_id.endswith(".analytics_pigskin_rankings_history"))
        self.assertEqual(staging_config.write_disposition, rankings.bigquery.WriteDisposition.WRITE_EMPTY)
        self.assertEqual(history_config.write_disposition, rankings.bigquery.WriteDisposition.WRITE_APPEND)
        self.assertEqual(len(client.query_calls), 2)
        delete_sql, delete_config = client.query_calls[0]
        insert_sql, insert_config = client.query_calls[1]
        self.assertIn("DELETE FROM `test-project.test_dataset.analytics_pigskin_rankings`", delete_sql)
        self.assertIn("target_board.scoring_profile_id IN UNNEST(@scoring_profile_ids)", delete_sql)
        self.assertIn("target_board.league_type_id IN UNNEST(@league_type_ids)", delete_sql)
        self.assertIn("target_board.roster_format_id IN UNNEST(@roster_format_ids)", delete_sql)
        self.assertIn("target_board.position IN UNNEST(@positions)", delete_sql)
        self.assertIn("INSERT INTO `test-project.test_dataset.analytics_pigskin_rankings`", insert_sql)
        self.assertIsNone(insert_config)
        params = {param.name: param.values for param in delete_config.query_parameters}
        self.assertEqual(params["scoring_profile_ids"], ["ppr"])
        self.assertEqual(params["league_type_ids"], ["redraft"])
        self.assertEqual(params["roster_format_ids"], ["one_qb"])
        self.assertEqual(params["positions"], ["QB"])
        self.assertEqual(client.deleted_tables, [(staging_table_id, True)])

        final_loads = [
            table_id for table_id, config in client.load_calls
            if table_id.endswith(".analytics_pigskin_rankings")
            and config.write_disposition == rankings.bigquery.WriteDisposition.WRITE_TRUNCATE
        ]
        self.assertEqual(final_loads, [])
        schema_by_name = {field.name: field.field_type for field in staging_config.schema}
        self.assertEqual(schema_by_name["generated_at"], "TIMESTAMP")
        self.assertEqual(schema_by_name["adjudicated_at"], "TIMESTAMP")

    def test_write_rankings_drops_candidate_only_columns_before_load(self):
        client = FakeLoadClient()
        rankings.write_rankings(client, "test_dataset", [{
            "ranking_version": "pigskin-llm-test",
            "generated_at": pd.Timestamp("2026-07-03T06:00:00Z"),
            "adjudicated_at": pd.Timestamp("2026-07-03T06:00:00Z"),
            "position": "TE",
            "scoring_profile_id": "half_ppr",
            "league_type_id": "redraft",
            "roster_format_id": "one_qb",
            "avg_profile_points": 14.876,
        }])

        self.assertEqual(len(client.loaded_dataframes), 2)
        for loaded_df in client.loaded_dataframes:
            self.assertEqual(list(loaded_df.columns), [field.name for field in client.history_schema])
            self.assertNotIn("avg_profile_points", loaded_df.columns)

    def test_write_rankings_standard_scope_does_not_delete_ppr(self):
        client = FakeLoadClient()
        rankings.write_rankings(client, "test_dataset", [{
            "ranking_version": "pigskin-llm-test",
            "generated_at": pd.Timestamp("2026-07-03T06:00:00Z"),
            "adjudicated_at": pd.Timestamp("2026-07-03T06:00:00Z"),
            "position": "RB",
            "scoring_profile_id": "standard",
            "league_type_id": "redraft",
            "roster_format_id": "one_qb",
        }])

        params = {param.name: param.values for param in client.query_calls[0][1].query_parameters}
        self.assertEqual(params["scoring_profile_ids"], ["standard"])
        self.assertNotIn("ppr", params["scoring_profile_ids"])

    def test_write_rankings_gng_scope_does_not_delete_ppr(self):
        client = FakeLoadClient()
        rankings.write_rankings(client, "test_dataset", [{
            "ranking_version": "pigskin-llm-test",
            "generated_at": pd.Timestamp("2026-07-03T06:00:00Z"),
            "adjudicated_at": pd.Timestamp("2026-07-03T06:00:00Z"),
            "position": "TE",
            "scoring_profile_id": "gng_keeper",
            "league_type_id": "keeper",
            "roster_format_id": "superflex",
        }])

        params = {param.name: param.values for param in client.query_calls[0][1].query_parameters}
        self.assertEqual(params["scoring_profile_ids"], ["gng_keeper"])
        self.assertNotIn("ppr", params["scoring_profile_ids"])

    def test_write_rankings_rejects_missing_profile_scope_fields(self):
        client = FakeLoadClient()
        rows = [{
            "ranking_version": "pigskin-llm-test",
            "generated_at": pd.Timestamp("2026-07-03T06:00:00Z"),
            "adjudicated_at": pd.Timestamp("2026-07-03T06:00:00Z"),
            "position": "QB",
        }]

        with self.assertRaisesRegex(RuntimeError, "position and profile scope fields"):
            rankings.write_rankings(client, "test_dataset", rows)

        self.assertEqual(client.load_calls, [])
        self.assertEqual(client.query_calls, [])

    def test_candidate_query_filters_selected_scoring_profile(self):
        class QueryClient:
            project = "test-project"

            def __init__(self):
                self.calls = []

            def query(self, sql, job_config=None):
                self.calls.append((sql, job_config))

                class ResultJob:
                    def result(self):
                        return self

                    def to_dataframe(self):
                        return pd.DataFrame()

                return ResultJob()

        client = QueryClient()
        rankings.fetch_candidates(client, "test_dataset", "TE", 60, scoring_profile_id="gng_keeper")

        sql, job_config = client.calls[0]
        self.assertIn("scoring_profile_id = @scoring_profile_id", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["scoring_profile_id"], "gng_keeper")

    def test_prompt_uses_selected_scoring_profile_label(self):
        df = pd.DataFrame([{
            "player_id": "p1",
            "player_name": "Player One",
            "current_team": "ARI",
            "sleeper_team": "ARI",
            "sleeper_active": True,
            "sleeper_status": "Active",
            "sleeper_depth_chart_position": "TE",
            "sleeper_depth_chart_order": 1,
            "rank": 1,
            "ranking_score": 90,
            "raw_ranking_score": 91,
            "depth_chart_penalty": 0,
            "avg_profile_points": 12.5,
            "avg_ppr": 11.5,
            "avg_grade": 80,
            "avg_opportunity": 70,
            "avg_efficiency": 60,
            "avg_epa_per_opportunity": 0.2,
            "season_total_epa": 10,
            "season_passing_epa": 0,
            "season_rushing_epa": 0,
            "season_receiving_epa": 10,
            "avg_role_quality": 70,
            "avg_role_fragility": 20,
            "avg_wopr": 0.5,
            "latest_season_wopr": 0.5,
            "previous_season_wopr": 0.4,
            "two_years_ago_wopr": 0.3,
            "avg_target_share": 0.2,
            "latest_season_target_share": 0.2,
            "previous_season_target_share": 0.18,
            "avg_carry_share": 0,
            "latest_season_carry_share": 0,
            "previous_season_carry_share": 0,
            "latest_season_ppr": 12,
            "previous_season_ppr": 10,
            "risk_flags": "no major Pigskin ranking flag",
        }])

        prompt = rankings.build_prompt("TE", df, "rank-v1", scoring_profile_id="gng_keeper")

        self.assertIn("official 2026 GNG Keeper TE rankings", prompt)
        self.assertIn("profile_pts_pg=12.50", prompt)

    def test_profile_aware_replace_design_does_not_use_global_truncate(self):
        delete_sql, insert_sql = rankings.build_profile_aware_rankings_replace_sql(
            "test-project",
            "test_dataset",
            "staging_board",
        )
        combined = f"{delete_sql}\n{insert_sql}"

        self.assertIn("scoring_profile_id", combined)
        self.assertIn("league_type_id", combined)
        self.assertIn("roster_format_id", combined)
        self.assertIn("@scoring_profile_ids", combined)
        self.assertIn("@league_type_ids", combined)
        self.assertIn("@roster_format_ids", combined)
        self.assertIn("@positions", combined)
        self.assertNotIn(" AS rows", combined)
        self.assertNotIn("WRITE_TRUNCATE", combined)
        self.assertNotIn("TRUNCATE TABLE", combined)

    def test_candidate_historical_metrics_gap_query_uses_neutral_aliases(self):
        sql = rankings.build_candidate_historical_metrics_gap_query(
            "test-project",
            "test_dataset",
            scoring_profile_id="ppr",
        )

        self.assertIn("player_week_advanced_metrics", sql)
        self.assertIn("metric_week_count", sql)
        self.assertIn("candidate.scoring_profile_id = @scoring_profile_id", sql)
        self.assertNotIn(" AS rows", sql)


if __name__ == "__main__":
    unittest.main()
