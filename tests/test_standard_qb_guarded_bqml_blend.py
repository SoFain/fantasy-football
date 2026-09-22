import unittest

from scripts.run_standard_qb_guarded_bqml_blend import (
    build_movement_sql,
    build_summary_sql,
)


class StandardQbGuardedBqmlBlendTests(unittest.TestCase):
    def setUp(self):
        self.summary_sql = build_summary_sql("project", "dataset", (2024, 2025))
        self.movement_sql = build_movement_sql("project", "dataset", (2024, 2025))

    def test_uses_advanced_standard_qb_models(self):
        self.assertIn("ranking_bqml_v2_adv_standard_qb_linear_points_advanced_v0", self.summary_sql)
        self.assertIn("ranking_bqml_v2_adv_standard_qb_logistic_bust_advanced_v0", self.summary_sql)
        self.assertIn("ML.PREDICT", self.summary_sql)

    def test_guarded_candidates_are_ninety_ten_rank_blends(self):
        self.assertIn("0.90 * control_rank + 0.10 * linear_rank", self.summary_sql)
        self.assertIn("0.90 * control_rank + 0.10 * logistic_rank", self.summary_sql)
        self.assertIn("0.90 * control_rank + 0.050 * linear_rank + 0.050 * logistic_rank", self.summary_sql)

    def test_query_is_leakage_safe_and_standard_qb_only(self):
        self.assertIn("advanced_dataset.position = 'QB'", self.summary_sql)
        self.assertIn("scoring_profile_id = 'standard'", self.summary_sql)
        self.assertIn("mart.source_window_end_season < mart.target_season", self.summary_sql)
        self.assertNotIn("2026", self.summary_sql)

    def test_query_has_no_write_statements(self):
        upper = self.summary_sql.upper()
        for keyword in ("INSERT INTO", "UPDATE ", "DELETE ", "MERGE ", "CREATE OR REPLACE"):
            self.assertNotIn(keyword, upper)

    def test_movement_audit_covers_cutlines_and_rushing_only_risers(self):
        self.assertIn("control_rank <= 6", self.movement_sql)
        self.assertIn("control_rank <= 12", self.movement_sql)
        self.assertIn("control_rank <= 24", self.movement_sql)
        self.assertIn("rushing_only_riser", self.movement_sql)
        self.assertIn("adv_passing_epa_per_dropback_3yr <= 0", self.movement_sql)

    def test_rejects_out_of_contract_seasons(self):
        with self.assertRaises(ValueError):
            build_summary_sql("project", "dataset", (2026,))

    def test_rejects_signal_weight_above_research_limit(self):
        with self.assertRaises(ValueError):
            build_summary_sql("project", "dataset", (2024,), signal_weight=0.41)


if __name__ == "__main__":
    unittest.main()
