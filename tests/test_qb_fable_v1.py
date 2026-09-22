import unittest

from scripts.run_qb_fable_v1_backtest import build_qb_fable_v1_sql


class QbFableV1Tests(unittest.TestCase):
    def setUp(self):
        self.sql = build_qb_fable_v1_sql("project", "dataset")

    def test_uses_raw_nflverse_pbp_and_standard_targets(self):
        self.assertIn("raw_nflverse_pbp", self.sql)
        self.assertIn("analytics_player_fantasy_points_by_profile", self.sql)
        self.assertIn("scoring_profile_id = 'standard'", self.sql)
        self.assertIn("COALESCE(league_type_id, 'redraft') = 'redraft'", self.sql)

    def test_compares_fable_with_same_cohort_prior_year_points(self):
        self.assertIn("'prior_year_standard_ppg' AS candidate_id", self.sql)
        self.assertIn("PARTITION BY input_season, candidate_id", self.sql)

    def test_includes_two_passing_heavier_research_variants(self):
        self.assertIn("'qb_fable_balanced' AS candidate_id", self.sql)
        self.assertIn("'qb_fable_passing' AS candidate_id", self.sql)
        self.assertIn("0.18 * COALESCE(z_epa_per_dropback", self.sql)

    def test_formula_excludes_kneels_and_garbage_time(self):
        self.assertIn("COALESCE(qb_kneel, 0) = 0", self.sql)
        self.assertIn("wp BETWEEN 0.05 AND 0.95", self.sql)

    def test_formula_uses_exact_documented_weights(self):
        for weight in ("0.20", "0.12", "0.08", "0.13", "0.09", "0.07", "0.06", "0.10", "0.05", "0.04", "0.03"):
            self.assertIn(f"{weight} *", self.sql)

    def test_shrinkage_and_td_regression_are_present(self):
        self.assertIn("SAFE_DIVIDE(dropbacks, dropbacks + 200)", self.sql)
        self.assertIn("+ 40)", self.sql)
        self.assertIn("0.045 * SAFE_DIVIDE(passing.pass_attempts", self.sql)
        self.assertIn("0.20 * SAFE_DIVIDE(COALESCE(rushing.goal_to_go_rush_attempts", self.sql)

    def test_backtest_is_next_season_and_leakage_safe(self):
        self.assertIn("passing.season + 1 AS target_season", self.sql)
        self.assertIn("target_points.season = passing.season + 1", self.sql)
        self.assertIn("passing.dropbacks >= 200", self.sql)
        self.assertIn("source_player_key AS player_id_internal", self.sql)

    def test_has_no_write_statements(self):
        upper = self.sql.upper()
        for keyword in ("INSERT INTO", "UPDATE ", "DELETE ", "MERGE ", "CREATE OR REPLACE"):
            self.assertNotIn(keyword, upper)


if __name__ == "__main__":
    unittest.main()
