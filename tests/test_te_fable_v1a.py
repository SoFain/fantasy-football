import unittest
from pathlib import Path

from scripts.build_te_fable_v1a_metric_layer import VIEW_FILES, render_sql
from scripts.run_te_fable_v1a_backtest import evaluate_variant


ROOT = Path(__file__).resolve().parents[1]
VIEW_DIR = ROOT / "bigquery" / "views"
ALL_SQL = "\n".join((VIEW_DIR / name).read_text() for name in VIEW_FILES)
FORMULA_SQL = "\n".join(
    (VIEW_DIR / name).read_text()
    for name in VIEW_FILES
    if name != "v_te_fable_v1a_rookie_candidates.sql"
)


class TeFableV1aSqlTest(unittest.TestCase):
    def test_templates_render(self):
        for name in VIEW_FILES:
            sql = render_sql(VIEW_DIR / name, "project", "advanced", "brain")
            self.assertNotIn("{{", sql)
            self.assertIn("project.advanced", sql)

    def test_formula_weights_and_ablation(self):
        sql = (VIEW_DIR / "v_te_fable_v1a_scored_seasons.sql").read_text()
        for term in (
            "0.22 * z_routes", "0.16 * z_target_share", "0.12 * z_rz_targets",
            "0.12 * z_tprr * target_efficiency_shrink",
            "0.08 * z_yprr * route_efficiency_shrink",
            "0.05 * z_man_yprr * vs_man_efficiency_shrink",
            "0.05 * z_epa_target * target_efficiency_shrink",
            "0.10 * z_blended_td", "0.04 * z_breakout", "0.03 * z_decline", "0.03 * z_games",
            "0.13 * z_yprr * route_efficiency_shrink",
        ):
            self.assertIn(term, sql)

    def test_primary_qualification_is_conservative(self):
        sql = (VIEW_DIR / "v_te_fable_v1a_metric_inputs.sql").read_text()
        self.assertIn("games_played >= 4 AND routes_run >= 100", sql)
        self.assertNotIn("games_played >= 4 OR", sql)

    def test_fixed_td_coefficient_and_shrinkage(self):
        sql = (VIEW_DIR / "v_te_fable_v1a_metric_inputs.sql").read_text()
        self.assertIn("0.14 AS fixed_rz_td_conversion", sql)
        for denominator in ("targets + 70", "routes_run + 70", "vs_man_routes_run + 70"):
            self.assertIn(denominator, sql)

    def test_point_in_time_and_no_live_inputs(self):
        splits = (VIEW_DIR / "v_te_fable_v1a_situational_splits.sql").read_text()
        self.assertIn("DATE(standard.season, 9, 1)", splits)
        prep = (VIEW_DIR / "v_te_fable_v1a_backtest_prep.sql").read_text()
        self.assertIn("season BETWEEN 2022 AND 2024", prep)
        self.assertIn("season BETWEEN 2022 AND 2025", prep)
        for banned in ("analytics_pigskin_rankings`", "sleeper_player_context_current", "gemini", "2026"):
            self.assertNotIn(banned, FORMULA_SQL.lower())

    def test_current_pigskin_comparison_uses_documented_weights(self):
        prep = (VIEW_DIR / "v_te_fable_v1a_backtest_prep.sql").read_text()
        for term in (
            "0.55 * analytical_grade_proxy",
            "0.15 * opportunity_score_proxy",
            "0.10 * efficiency_score_proxy",
            "0.10 * role_stability_score",
            "0.10 * profile_points_score",
        ):
            self.assertIn(term, prep)
        self.assertIn("GROUP BY target_season, player_id_internal", prep)

    def test_identity_fails_closed(self):
        bridge = (VIEW_DIR / "v_te_fable_v1a_identity_bridge.sql").read_text()
        self.assertIn("'TE'", bridge)
        self.assertIn("MULTIPLE_CANDIDATES", bridge)
        inputs = (VIEW_DIR / "v_te_fable_v1a_metric_inputs.sql").read_text()
        self.assertIn("NOT duplicate_identity_collision", inputs)

    def test_rookie_lane_is_review_only_and_unscored(self):
        sql = (VIEW_DIR / "v_te_fable_v1a_rookie_candidates.sql").read_text()
        self.assertIn("years_exp = 0", sql)
        self.assertIn("CAST(NULL AS FLOAT64) AS formula_score", sql)
        self.assertIn("college_production_missing", sql)
        self.assertIn("draft_capital_missing", sql)
        self.assertNotIn("analytics_pigskin_rankings`", sql)


class TeFableV1aMathTest(unittest.TestCase):
    def test_perfect_variant(self):
        rows = [{
            "season": season,
            "candidate_internal_player_id": f"{season}-{index}",
            "player_name": f"TE{index:02}",
            "candidate_score": float(40 - index),
            "target_standard_ppg": float(40 - index),
            "target_standard_points": float((40 - index) * 10),
        } for season in (2022, 2023, 2024) for index in range(1, 31)]
        result = evaluate_variant(rows, "candidate_score")
        self.assertEqual(result["aggregate"]["average_spearman_rank_correlation"], 1.0)
        self.assertEqual(result["aggregate"]["average_top_12_precision"], 1.0)

    def test_variant_skips_missing_scores(self):
        rows = [{
            "season": season,
            "candidate_internal_player_id": f"{season}-{index}",
            "player_name": f"TE{index:02}",
            "candidate_score": None if index == 30 else float(40 - index),
            "target_standard_ppg": float(40 - index),
            "target_standard_points": float((40 - index) * 10),
        } for season in (2022, 2023, 2024) for index in range(1, 31)]
        result = evaluate_variant(rows, "candidate_score")
        self.assertEqual(result["aggregate"]["total_complete_rows"], 87)


if __name__ == "__main__":
    unittest.main()
