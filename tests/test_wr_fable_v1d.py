import unittest
from pathlib import Path

from scripts.build_rb_fable_01_metric_layer import render_sql
from scripts.build_wr_fable_v1d_layer import VIEW_FILES


ROOT = Path(__file__).resolve().parents[1]
VIEW_DIR = ROOT / "bigquery" / "views"
INPUTS = (VIEW_DIR / "v_wr_fable_v1d_metric_inputs.sql").read_text()
SCORES = (VIEW_DIR / "v_wr_fable_v1d_scored_seasons.sql").read_text()
ENVIRONMENT = (VIEW_DIR / "v_wr_fable_v1d_team_environment.sql").read_text()
BACKTEST = (VIEW_DIR / "v_wr_fable_v1d_backtest_prep.sql").read_text()
CURRENT = (VIEW_DIR / "v_wr_fable_v1d_current_board.sql").read_text()
CURRENT_CANDIDATES = (VIEW_DIR / "v_wr_fable_v1_current_candidates.sql").read_text()
ALL_SQL = "\n".join((VIEW_DIR / name).read_text() for name in VIEW_FILES)


class WrFableV1dSqlTest(unittest.TestCase):
    def test_templates_render(self):
        for name in VIEW_FILES:
            rendered = render_sql(VIEW_DIR / name, "project", "advanced", "brain")
            self.assertNotIn("{{", rendered)

    def test_controlled_injury_matrix(self):
        for variant, threshold in (("I4", "13"), ("I7", "10"), ("I10", "7")):
            self.assertIn(f"STRUCT('{variant}' AS variant_id, {threshold} AS trigger_max_games)", INPUTS)
        self.assertIn("BETWEEN 9 AND 12 THEN 0.15", INPUTS)
        self.assertIn("BETWEEN 5 AND 8 THEN 0.30", INPUTS)
        self.assertIn("BETWEEN 3 AND 4 THEN 0.40", INPUTS)
        self.assertIn("paired.prior_adot_adjusted_catch_rate IS NULL THEN 0.0", INPUTS)
        self.assertIn("paired.prior_blended_td_per_game IS NULL THEN 0.0", INPUTS)

    def test_only_rates_are_blended(self):
        for metric in (
            "modified_wopr",
            "modified_ngt_targets_per_game",
            "modified_rz_targets_per_game",
            "modified_yprr",
            "modified_epa_per_target",
            "modified_yac_per_reception",
            "modified_adot_adjusted_catch_rate",
            "modified_blended_td_per_game",
        ):
            self.assertIn(metric, INPUTS)
        self.assertNotIn("prior_receiving_yards", INPUTS)
        self.assertNotIn("prior_receptions", INPUTS)
        self.assertNotIn("prior_receiving_touchdowns", INPUTS)

    def test_rookie_rule_is_source_backed_and_shrunk(self):
        self.assertIn("players.rookie_year", INPUTS)
        self.assertIn("MIN(season) AS first_nfl_season", INPUTS)
        self.assertIn("COALESCE(latest.rookie_year, latest.first_nfl_season) = latest.season", INPUTS)
        self.assertIn("routes_run + 90", INPUTS)
        self.assertIn("targets + 90", INPUTS)
        self.assertIn("rookie_limited_sample_flag", INPUTS)

    def test_v1_weights_and_reference_distributions_are_preserved(self):
        self.assertIn("v_wr_fable_v1_scored_seasons", SCORES)
        self.assertIn("COALESCE(baseline_v1_score, injury_candidate_score)", SCORES)
        self.assertIn("AS exclusion_only_score", SCORES)
        self.assertIn("prior_v1_score - prior_v1_age_availability_component + age_availability_component", SCORES)
        self.assertIn("AS carry_forward_replacement_score", SCORES)
        self.assertIn("AS rookie_review_score", SCORES)
        for weighted_term in (
            "0.30 * z_wopr",
            "0.12 * z_ngt_targets_per_game",
            "0.10 * z_rz_targets_per_game",
            "0.12 * z_yprr",
            "0.10 * z_blended_td_per_game",
            "0.03 * z_two_year_availability",
        ):
            self.assertIn(weighted_term, SCORES)

    def test_environment_definition_and_continuous_modifiers(self):
        for weighted_term in (
            "0.45 * z_qb_passing_epa_per_dropback",
            "0.25 * z_team_pass_epa_per_play",
            "0.15 * z_pass_attempts_per_game",
            "0.10 * z_offensive_points_per_game",
            "0.05 * z_win_percentage",
        ):
            self.assertIn(weighted_term, ENVIRONMENT)
        for multiplier in ("0.015 *", "0.025 *", "0.040 *"):
            self.assertIn(multiplier, BACKTEST)
        self.assertIn("LEAST(GREATEST(environment_delta, -1.5), 1.5)", BACKTEST)

    def test_historical_path_is_bounded_and_has_no_current_context(self):
        self.assertIn("season BETWEEN 2022 AND 2024", BACKTEST)
        self.assertIn("season BETWEEN 2023 AND 2025", BACKTEST)
        self.assertIn("week = 1", BACKTEST)
        self.assertNotIn("sleeper", BACKTEST.lower())
        self.assertNotIn("depth_chart", BACKTEST.lower())
        self.assertNotIn("2026 outcomes", ALL_SQL.lower())

    def test_current_sleeper_context_is_display_only(self):
        self.assertIn("sleeper_current_player_context", CURRENT)
        self.assertIn("sleeper_status", CURRENT)
        self.assertNotIn("alpha_role_adjustment", CURRENT)
        self.assertNotIn("depth_chart_order = 1 THEN", CURRENT)

    def test_no_forbidden_inputs_or_live_ranking_writes(self):
        lowered = ALL_SQL.lower()
        for banned in ("market_value", "end_zone_targets", "broken_tackle", "insert into", "merge `"):
            self.assertNotIn(banned, lowered)
        self.assertNotIn("create or replace table", lowered)

    def test_exclusion_only_rank_is_current_review_only(self):
        self.assertIn("ORDER BY exclusion_only_score DESC", CURRENT)
        self.assertIn("AS exclusion_only_rank", CURRENT)
        self.assertIn("AS carry_forward_replacement_rank", CURRENT)
        self.assertNotIn("exclusion_only_score +", CURRENT)

    def test_prior_score_replacement_keeps_rookies_separate(self):
        self.assertIn("NOT candidate_scores.rookie_limited_sample_flag", SCORES)
        self.assertIn("AS prior_score_carry_forward_eligible", SCORES)
        self.assertIn("AS carry_forward_replacement_score", SCORES)
        self.assertIn("AS rookie_review_score", SCORES)
        self.assertIn("PRIOR_QUALIFIED_VETERAN_CARRY_FORWARD", CURRENT_CANDIDATES)
        self.assertIn("source.prior_score_carry_forward_eligible", CURRENT_CANDIDATES)
        self.assertIn("NOT source.rookie_limited_sample_flag", CURRENT_CANDIDATES)
        self.assertNotIn("sleeper_current_player_context", CURRENT_CANDIDATES)


if __name__ == "__main__":
    unittest.main()
