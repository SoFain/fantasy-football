import unittest

from scripts.build_ranking_post_formula_safety import render_sql, validation_sql
from scripts.build_standard_wr_fable_v1_safety_review import build_query, build_watchlist_query
from src.ranking_owner_decisions import (
    GNG_WATCHLIST_NAMES,
    STANDARD_WR_ELITE_ORDER,
)


class RankingPostFormulaSafetyTest(unittest.TestCase):
    def test_shared_view_keeps_current_context_out_of_formula_views(self):
        sql = render_sql("project", "metrics")
        self.assertIn("`project.metrics.sleeper_current_player_context`", sql)
        self.assertIn("`project.fantasy_football_brain.player_identity_bridge`", sql)
        self.assertIn(
            "COALESCE(context.gsis_id, identity_bridge.bridge_gsis_id, identity_by_name.bridge_gsis_id)",
            sql,
        )
        self.assertIn("identity_by_name.gsis_id_count = 1", sql)
        self.assertNotIn("scored_seasons", sql)
        self.assertNotIn("v_wr_fable", sql)

    def test_adjustments_are_bounded_and_injury_is_review_only(self):
        sql = render_sql("project", "metrics")
        self.assertIn("THEN 0.02", sql)
        self.assertIn("THEN -0.04", sql)
        self.assertIn("IF(injury_status IS NOT NULL, 'INJURY_UNCERTAIN', NULL)", sql)
        self.assertNotIn("injury_status IS NOT NULL THEN", sql)
        self.assertIn("post_formula_adjustment NOT IN (-0.04, 0.0, 0.02)", validation_sql("p", "d"))
        self.assertIn("team IS NOT NULL AS current_board_rank_eligible", sql)
        self.assertIn("WHEN team IS NULL THEN 'teamless_unranked'", sql)

    def test_standard_wr_review_ranks_on_raw_score_plus_shared_adjustment(self):
        sql = build_query("project", "metrics")
        self.assertIn("v_ranking_post_formula_safety", sql)
        self.assertIn("v_wr_fable_v1_current_candidates", sql)
        self.assertIn("formula_score + post_formula_adjustment AS post_formula_score", sql)
        self.assertIn("COALESCE(safety.sleeper_hard_review, TRUE)", sql)
        self.assertIn("analytics_pigskin_rankings", sql)
        self.assertIn("occupied_ranks[SAFE_OFFSET(0)]", sql)
        self.assertIn("occupied_ranks[SAFE_OFFSET(1)]", sql)
        self.assertIn("occupied_ranks[SAFE_OFFSET(2)]", sql)
        self.assertIn("OWNER_APPROVED_ELITE_ORDER", sql)
        self.assertIn("WHERE final_rank <= 100", sql)

    def test_elite_order_is_shared_and_teamless_is_structural(self):
        self.assertEqual(
            STANDARD_WR_ELITE_ORDER,
            ("A.J. Brown", "Justin Jefferson", "Garrett Wilson"),
        )
        self.assertIn("Gabe Davis", GNG_WATCHLIST_NAMES)
        self.assertIn("Sterling Shepard", GNG_WATCHLIST_NAMES)
        watchlist_sql = build_watchlist_query("project", "metrics")
        self.assertIn("TEAMLESS_UNRANKED", watchlist_sql)
        self.assertIn("WHERE teamless_unranked", watchlist_sql)
        self.assertNotIn("Stefon Diggs", watchlist_sql)


if __name__ == "__main__":
    unittest.main()
