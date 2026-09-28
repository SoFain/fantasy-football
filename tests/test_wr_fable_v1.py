import unittest
from pathlib import Path

from scripts.build_wr_fable_v1_metric_layer import VIEW_FILES
from scripts.build_rb_fable_01_metric_layer import render_sql
from scripts.run_wr_fable_v1_backtest import fold_summary, pick_band, spearman

ROOT = Path(__file__).resolve().parents[1]
VIEW_DIR = ROOT / "bigquery" / "views"
ALL_SQL = "\n".join((VIEW_DIR / name).read_text() for name in VIEW_FILES)


class WrFableV1SqlTest(unittest.TestCase):
    def test_all_view_templates_render(self):
        for name in VIEW_FILES:
            sql = render_sql(VIEW_DIR / name, "project", "advanced", "brain")
            self.assertNotIn("{{", sql)
            self.assertIn("project.advanced", sql)

    def test_formula_weights_and_shrinkage(self):
        sql = (VIEW_DIR / "v_wr_fable_v1_scored_seasons.sql").read_text()
        for term in (
            "0.30 * z_wopr", "0.12 * z_ngt_tgt", "0.10 * z_rz_tgt",
            "0.12 * z_yprr * route_efficiency_shrink",
            "0.06 * z_epa_per_target * target_efficiency_shrink",
            "0.05 * z_yac_per_reception * target_efficiency_shrink",
            "0.05 * z_adot_adjusted_catch_rate * target_efficiency_shrink",
            "0.10 * z_blended_td",
            "0.04 * z_breakout_window", "0.03 * z_decline_penalty", "0.03 * z_games_rate",
        ):
            self.assertIn(term, sql)
        self.assertIn("PARTITION BY season", sql)
        inputs = (VIEW_DIR / "v_wr_fable_v1_metric_inputs.sql").read_text()
        self.assertIn("routes_run + 60", inputs)
        self.assertIn("targets + 60", inputs)

    def test_wopr_is_derived_and_units_normalized(self):
        inputs = (VIEW_DIR / "v_wr_fable_v1_metric_inputs.sql").read_text()
        self.assertIn("1.5 * (splits.target_share / 100.0) + 0.7 * splits.air_yards_share", inputs)
        # Stored WOPR only as cross-check, never the canonical input.
        self.assertNotIn("stored_wopr_weekly_avg AS wopr", ALL_SQL)

    def test_rz_td_fallback_is_labeled_and_no_end_zone_invention(self):
        inputs = (VIEW_DIR / "v_wr_fable_v1_metric_inputs.sql").read_text()
        splits = (VIEW_DIR / "v_wr_fable_v1_situational_splits.sql").read_text()
        self.assertIn("league_wr_rz_td_conversion", inputs)
        self.assertIn("NOT end-zone", inputs)
        self.assertIn("red_zone_structural_fallback", splits)
        self.assertIn("sourced_red_zone_targets", splits)
        self.assertIn("ADVANCED_TARGETS_PBP_TDS", splits)
        self.assertIn("event_type = 'target' AND yardline_100 <= 20 AND touchdown", splits)
        self.assertIn("CASE WHEN splits.red_zone_structural_fallback", inputs)
        self.assertIn("non_garbage_structural_fallback", splits)
        self.assertIn("sourced_non_garbage_targets", splits)
        self.assertIn("PBP_WP_5_95", splits)
        self.assertIn("JSON_VALUE(raw_payload_json, '$.wp')", splits)
        self.assertIn("CASE WHEN splits.non_garbage_structural_fallback", inputs)
        self.assertNotIn("end_zone_targets", ALL_SQL.lower())

    def test_qualification_and_null_safety(self):
        inputs = (VIEW_DIR / "v_wr_fable_v1_metric_inputs.sql").read_text()
        self.assertIn("games_played >= 6 OR targets >= 40", inputs)
        self.assertIn("CASE WHEN splits.targets > 0", inputs)
        self.assertIn("CASE WHEN splits.receptions > 0", inputs)
        # No zero-filling of the core efficiency inputs.
        self.assertNotIn("IFNULL(splits.total_epa", inputs)
        self.assertNotIn("COALESCE(splits.targets, 0)", inputs)

    def test_no_future_leakage(self):
        prep = (VIEW_DIR / "v_wr_fable_v1_backtest_prep.sql").read_text()
        self.assertIn("season BETWEEN 2022 AND 2024", prep)
        self.assertIn("season BETWEEN 2023 AND 2025", prep)
        self.assertIn("scored.season + 1", prep)
        self.assertNotIn("2026", ALL_SQL)
        for banned in ("market_value", "sleeper_current_player_context", "broken_tackle"):
            self.assertNotIn(banned, ALL_SQL.lower())

    def test_identity_fails_closed(self):
        bridge = (VIEW_DIR / "v_wr_fable_v1_identity_bridge.sql").read_text()
        for token in ("MULTIPLE_CANDIDATES", "UNMAPPED", "duplicate_identity_collision", "'WR'"):
            self.assertIn(token, bridge)
        inputs = (VIEW_DIR / "v_wr_fable_v1_metric_inputs.sql").read_text()
        self.assertIn("'VERIFIED', 'EXACT_SLUG_MATCH', 'NAME_TEAM_SEASON_MATCH'", inputs)
        self.assertIn("NOT duplicate_identity_collision", inputs)

    def test_marvin_harrison_source_identity_override_is_narrow_and_auditable(self):
        bridge = (VIEW_DIR / "v_wr_fable_v1_identity_bridge.sql").read_text()
        for token in (
            "'d96487d'",
            "'marvin-harrison'",
            "'00-0039849'",
            "'MARVIN_HARRISON_JR_SOURCE_ID'",
            "identity_override_applied",
            "NOT identity_override_applied",
        ):
            self.assertIn(token, bridge)


class WrFableV1BacktestMathTest(unittest.TestCase):
    def test_spearman_perfect_and_reversed(self):
        self.assertAlmostEqual(spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertAlmostEqual(spearman([1, 2, 3, 4], [40, 30, 20, 10]), -1.0)

    def test_pick_band(self):
        self.assertEqual([pick_band(r) for r in (1, 6, 7, 12, 13, 24, 25, 36, 37)], [0, 0, 1, 1, 2, 2, 3, 3, 4])

    def test_fold_summary_bounds(self):
        records = [{
            "candidate_internal_player_id": str(i), "player_name": f"W{i:02}",
            "wr_fable_v1_score": float(50 - i), "target_standard_ppg": float(50 - i),
            "target_standard_points": float((50 - i) * 10),
        } for i in range(1, 49)]
        summary = fold_summary(records)
        self.assertEqual(summary["top_12_precision"], 1.0)
        self.assertEqual(summary["spearman_rank_correlation"], 1.0)
        self.assertEqual(summary["elite_wr_miss_count"], 0)
        self.assertEqual(summary["predicted_top_12_bust_count"], 0)


if __name__ == "__main__":
    unittest.main()
