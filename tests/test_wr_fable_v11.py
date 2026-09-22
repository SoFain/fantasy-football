import unittest
from pathlib import Path

from scripts.build_wr_fable_v11_layer import VIEW_FILES
from scripts.build_rb_fable_01_metric_layer import render_sql

ROOT = Path(__file__).resolve().parents[1]
VIEW_DIR = ROOT / "bigquery" / "views"
ALL_SQL = "\n".join((VIEW_DIR / name).read_text() for name in VIEW_FILES)
INPUTS = (VIEW_DIR / "v_wr_fable_v11_metric_inputs.sql").read_text()
PREP = (VIEW_DIR / "v_wr_fable_v11_backtest_prep.sql").read_text()
BOARD = (VIEW_DIR / "v_wr_fable_v11_current_board.sql").read_text()
ENV = (VIEW_DIR / "v_wr_team_environment.sql").read_text()


class WrFableV11SqlTest(unittest.TestCase):
    def test_templates_render(self):
        for name in VIEW_FILES:
            sql = render_sql(VIEW_DIR / name, "project", "advanced", "brain")
            self.assertNotIn("{{", sql)

    def test_dynamic_blend_weights_and_caps(self):
        self.assertIn("SAFE_DIVIDE(paired.routes_run, paired.routes_run + 200), 0.35), 0.70", INPUTS)
        self.assertIn("LEAST(latest_weight_raw, 0.70) AS opportunity_latest_weight", INPUTS)
        self.assertIn("LEAST(latest_weight_raw, 0.60) AS efficiency_latest_weight", INPUTS)
        # No prior season -> latest-only weight of 1.0, never invented prior values.
        self.assertIn("WHEN paired.prev_qualified IS NULL THEN 1.0", INPUTS)

    def test_rates_blended_not_totals(self):
        for blended in ("b_wopr", "b_ngt_tgt_pg", "b_rz_tgt_pg", "b_yprr", "b_epa_per_target",
                        "b_yac_per_reception", "b_adot_adjusted_catch_rate", "b_blended_td_per_game"):
            self.assertIn(blended, INPUTS)
        # Raw totals must not be blended.
        self.assertNotIn("prev_receiving_yards", INPUTS)
        self.assertNotIn("targets + prev_targets AS", INPUTS)

    def test_carry_forward_eligibility(self):
        self.assertIn("games_played >= 3 OR routes_run >= 75", INPUTS)
        self.assertIn("carry_forward_eligible", INPUTS)

    def test_availability_separated(self):
        self.assertIn("0.70 * games_played_rate + 0.30 * prev_games_played_rate", INPUTS)
        scored = (VIEW_DIR / "v_wr_fable_v11_scored_seasons.sql").read_text()
        self.assertIn("z_two_year_availability", scored)
        self.assertIn("0.03 * z_two_year_availability", scored)

    def test_environment_weights(self):
        for weight in ("0.35 *", "0.20 *", "0.15 *", "0.10 *"):
            self.assertIn(weight, ENV)
        self.assertIn("qb_passing_epa_per_dropback", ENV)
        self.assertIn("win_percentage", ENV)
        self.assertIn("stg_play_player_events", ENV)
        self.assertIn("AND pass_attempt", ENV)

    def test_backtest_leakage_safety(self):
        # Destination = target-season Week 1 roster; environment from input season only.
        self.assertIn("week = 1", PREP)
        self.assertIn("env_source.season = enriched.season", PREP)
        self.assertIn("env_destination.season = enriched.season", PREP)
        self.assertIn("season BETWEEN 2022 AND 2024", PREP)
        self.assertNotIn("2026", ALL_SQL)
        # Alpha-role (Sleeper) modifier must not appear in the backtest prep.
        self.assertNotIn("sleeper", PREP.lower())
        self.assertNotIn("depth_chart", PREP.lower())

    def test_current_board_adjustments_capped(self):
        self.assertIn("-0.08), 0.08", BOARD)
        self.assertIn("WHEN enriched.sleeper_depth_chart_order = 1 THEN 0.03", BOARD)
        self.assertIn("WHEN enriched.sleeper_depth_chart_order >= 3 THEN -0.03", BOARD)
        self.assertIn("alpha_role_review_flag", BOARD)
        self.assertIn("0.05 * situation_bucket", BOARD)
        self.assertIn("normalized_name_count = 1", BOARD)
        self.assertIn("sleeper.gsis_id IS NULL", BOARD)

    def test_no_fabricated_metrics(self):
        for banned in ("end_zone_targets", "broken_tackle", "market_value"):
            self.assertNotIn(banned, ALL_SQL.lower())


class SleeperArchiveTest(unittest.TestCase):
    def test_archive_functions_exist_and_idempotent(self):
        source = (ROOT / "scripts" / "build_sleeper_current_player_context.py").read_text()
        self.assertIn("sleeper_player_snapshot_history", source)
        self.assertIn("DELETE FROM `{table_id}` WHERE snapshot_date = @snapshot_date", source)
        self.assertIn("v_sleeper_player_status_changes", source)
        self.assertIn("previous.snapshot_date IS NOT NULL", source)
        self.assertIn("--archive", source.replace('"', ""))


if __name__ == "__main__":
    unittest.main()
