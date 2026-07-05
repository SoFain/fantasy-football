import os
import unittest
from datetime import datetime, timezone

import pandas as pd

from src import nflverse_ideal_stats as ideal
from src import ranking_formula_backtests as rfb


class NflverseIdealStatsTests(unittest.TestCase):
    def test_write_gate_fails_closed(self):
        with self.assertRaisesRegex(PermissionError, "ALLOW_NFLVERSE_IDEAL_STATS_INGEST"):
            ideal.require_write_authorization(env={})

    def test_unrelated_ranking_gate_does_not_authorize_ideal_ingest(self):
        with self.assertRaisesRegex(PermissionError, "ALLOW_NFLVERSE_IDEAL_STATS_INGEST"):
            ideal.require_write_authorization(env={"ALLOW_RANKING_FORMULA_BACKTEST_WRITE": "true"})

    def test_normalize_ffopportunity_weekly_outputs_contract_columns(self):
        frame = pd.DataFrame(
            [
                {
                    "season": "2024",
                    "week": 1.0,
                    "game_id": "2024_01_ARI_BUF",
                    "player_id": "00-0035228",
                    "full_name": "Kyler Murray",
                    "posteam": "ARI",
                    "position": "QB",
                    "pass_fantasy_points_exp": 11.68,
                    "rec_fantasy_points_exp": 0.0,
                    "rush_fantasy_points_exp": 3.23,
                    "total_fantasy_points_exp": 14.91,
                    "total_fantasy_points": 16.18,
                    "total_fantasy_points_diff": 1.27,
                }
            ]
        )
        normalized = ideal.normalize_ffopportunity_weekly(
            frame,
            source_version="test_version",
            source_refresh_id="test-refresh",
            loaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            loaded_by="tester",
        )
        self.assertEqual(list(normalized.columns), list(ideal.RAW_COLUMNS))
        self.assertEqual(normalized.loc[0, "player_id_internal"], "gsis:00-0035228")
        self.assertEqual(normalized.loc[0, "source_version"], "test_version")

    def test_raw_delete_sql_is_bounded_not_global_truncate(self):
        sql = ideal.build_raw_delete_sql(project_id="p", dataset_id="d").lower()
        self.assertIn("where season between @season_start and @season_end", sql)
        self.assertIn("source_version = @source_version", sql)
        self.assertNotIn("truncate", sql)

    def test_ideal_insert_sql_uses_safe_sources_and_flags_proxies(self):
        sql = ideal.build_ideal_metrics_insert_sql(project_id="p", dataset_id="d")
        lowered = sql.lower()
        self.assertIn("raw_ffopportunity_weekly", sql)
        self.assertIn("player_week_advanced_metrics", sql)
        self.assertIn("stg_participation_context", sql)
        self.assertIn("true_route_share_missing_flag", sql)
        self.assertIn("direct_injury_context_unavailable", sql)
        self.assertNotIn("analytics_pigskin_rankings", lowered)
        self.assertNotIn("ranking_formula_champions", lowered)

    def test_feature_mart_consumes_ideal_stats_without_target_season_leakage(self):
        sql = rfb.build_feature_mart_insert_sql(project_id="p", dataset_id="d")
        self.assertIn("player_week_ideal_opportunity_metrics", sql)
        self.assertIn("ideal.source_version = 'ffopportunity_weekly_latest'", sql)
        self.assertIn("metrics.season < @target_season", sql)
        self.assertIn("xfp_score_3yr", sql)
        self.assertIn("ideal_missing_flags", sql)

    def test_ideal_diagnostic_candidates_are_position_specific(self):
        candidates = rfb.ideal_stats_diagnostic_tournament_candidates()
        self.assertEqual({row["position"] for row in candidates}, {"QB", "RB", "WR", "TE"})
        joined = "\n".join(row["formula_json"] for row in candidates)
        self.assertIn("xfp_score_3yr", joined)
        self.assertIn("receiving_role_dominance_xfp_3yr", joined)

    def test_ideal_features_are_allowed_and_mapped(self):
        for feature in ("xfp_score_3yr", "high_value_xfp_score_3yr", "receiving_role_dominance_xfp_3yr"):
            self.assertIn(feature, rfb.FEATURE_SOURCE_MAP)
        self.assertIn("player_week_ideal_opportunity_metrics", rfb.ALLOWED_INPUT_TABLES)

    def test_summary_write_sql_accepts_ideal_candidates_without_detail_rows(self):
        sql = rfb.build_sql_native_tournament_summary_write_sql(
            project_id="p",
            dataset_id="d",
            target_seasons=(2024, 2025),
            scoring_profile_ids=("ppr",),
            positions=("QB", "RB", "WR", "TE"),
            backtest_run_id_prefix="ranking_backtest_sql_native_ideal_stats_diagnostics_v0",
            formula_version="ranking_backtest_sql_native_ideal_stats_diagnostics_v0",
            candidate_rows=rfb.ideal_stats_diagnostic_tournament_candidates(),
        )
        lowered = sql.lower()
        self.assertIn("ranking_backtest_sql_native_ideal_stats_diagnostics_v0", sql)
        self.assertIn("ranking_backtest_candidate_summaries", sql)
        self.assertIn("ranking_backtest_runs", sql)
        self.assertNotIn("ranking_backtest_results", lowered)
        self.assertNotIn("analytics_pigskin_rankings", lowered)
        self.assertNotIn("ranking_formula_champions", lowered)


if __name__ == "__main__":
    unittest.main()
