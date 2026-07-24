import unittest

from scripts.promote_standard_fable_v1_positional import build_sql


class StandardFablePositionalPromotionTest(unittest.TestCase):
    def setUp(self):
        self.sql = build_sql("project", "brain", "metrics", "version")

    def test_rb_verdict_explains_workload_scoring_and_efficiency(self):
        self.assertIn("non-garbage-time touches per game", self.sql)
        self.assertIn("target share", self.sql)
        self.assertIn("red-zone touches", self.sql)
        self.assertIn("EPA per touch", self.sql)

    def test_wr_verdict_explains_opportunity_efficiency_and_risk(self):
        self.assertIn("v_wr_fable_v1_current_candidates", self.sql)
        self.assertIn("WOPR", self.sql)
        self.assertIn("non-garbage-time targets per game", self.sql)
        self.assertIn("YPRR", self.sql)
        self.assertIn("Availability is the clear risk", self.sql)
        self.assertIn("receives veteran coverage", self.sql)

    def test_wr_repair_provenance_survives_future_promotions(self):
        self.assertIn("prior availability component", self.sql)
        self.assertIn("current two-year availability component", self.sql)
        self.assertIn("MARVIN_HARRISON_JR_SOURCE_ID", self.sql)
        self.assertIn("formula weights unchanged", self.sql)

    def test_te_verdict_explains_opportunity_efficiency_and_risk(self):
        self.assertIn("routes per game", self.sql)
        self.assertIn("red-zone targets per game", self.sql)
        self.assertIn("targets per route", self.sql)
        self.assertIn("YPRR", self.sql)
        self.assertIn("blended TDs per game", self.sql)

    def test_old_rank_only_placeholders_are_removed(self):
        self.assertNotIn("RB Fable v1 ranks %s at RB%d", self.sql)
        self.assertNotIn("WR Fable v1 ranks %s at WR%d", self.sql)
        self.assertNotIn("TE Fable v1.0a ranks %s at TE%d", self.sql)

    def test_elite_guardrail_preserves_order_without_freezing_rank_numbers(self):
        self.assertIn(
            "STRING_AGG(player_name, '|' ORDER BY rank) = 'A.J. Brown|Justin Jefferson|Garrett Wilson'",
            self.sql,
        )
        self.assertNotIn("STRUCT('A.J. Brown' AS player_name, 13 AS expected_rank)", self.sql)


if __name__ == "__main__":
    unittest.main()
