import unittest

from scripts.run_gng_advanced_hypotheses import player_audit, weighted_average
from scripts.run_gng_position_candidate_expansion import ROUND1_CANDIDATES, ROUND2_CANDIDATES, percent_ranks
from src.gng_sleeper_safety import apply_sleeper_safety
from scripts.build_gng_2026_candidate_boards import FORMULAS, LIMITS, build_query
from scripts.build_unified_gng_2026_top100 import REPLACEMENT, apply_position_locked_floors, apply_position_locked_overall_floor
from scripts.promote_gng_2026_rankings import build_sql as build_gng_promotion_sql


class GngAdvancedHypothesesTest(unittest.TestCase):
    def test_weighted_average_renormalizes_present_inputs(self):
        row = {"complete": 0.8, "missing": None}
        self.assertEqual(weighted_average(row, (("complete", 0.25), ("missing", 0.75))), 0.8)

    def test_weighted_average_returns_none_without_inputs(self):
        self.assertIsNone(weighted_average({"missing": None}, (("missing", 1.0),)))

    def test_player_audit_returns_names_and_ranks(self):
        rows = [
            {
                "player_id": str(rank),
                "player_name": f"Player {rank}",
                "score": 50 - rank,
                "target_ppg": 100 if rank == 30 else 50 - rank,
                "target_points": 100,
            }
            for rank in range(1, 31)
        ]
        audit = player_audit(rows)
        self.assertEqual(audit["elite_misses"][0]["player_name"], "Player 30")
        self.assertEqual(audit["elite_misses"][0]["predicted_rank"], 30)

    def test_expansion_has_five_candidates_per_position(self):
        self.assertEqual({position: len(candidates) for position, candidates in ROUND1_CANDIDATES.items()}, {"QB": 5, "RB": 5, "WR": 5})
        self.assertEqual({position: len(candidates) for position, candidates in ROUND2_CANDIDATES.items()}, {"RB": 5, "WR": 5})

    def test_percent_ranks_exclude_nulls_from_rank_population(self):
        rows = [{"metric": None}, {"metric": 10}, {"metric": 20}]
        self.assertEqual(percent_ranks(rows, "metric"), {1: 0.0, 2: 1.0})

    def test_sleeper_safety_flags_inactive_players_without_adjustment(self):
        result = apply_sleeper_safety({"sleeper_active": False, "sleeper_team": None, "sleeper_status": "Inactive"})
        self.assertTrue(result["sleeper_hard_review"])
        self.assertEqual(result["sleeper_role_adjustment"], 0.0)
        self.assertIn("SLEEPER_ROSTER_REVIEW", result["sleeper_review_flags"])

    def test_sleeper_injury_is_flagged_without_score_penalty(self):
        result = apply_sleeper_safety({"sleeper_active": True, "sleeper_team": "ATL", "sleeper_status": "Active", "sleeper_depth_chart_order": 1, "sleeper_injury_status": "Questionable"})
        self.assertFalse(result["sleeper_hard_review"])
        self.assertEqual(result["sleeper_role_adjustment"], 0.02)
        self.assertIn("INJURY_UNCERTAIN", result["sleeper_review_flags"])

    def test_2026_board_contract_uses_locked_formulas_and_limits(self):
        self.assertEqual({position: formula[0] for position, formula in FORMULAS.items()}, {
            "QB": "q4_gng_bonus_proxy", "RB": "r7_h1_r2_compromise",
            "WR": "w10_h5_floor_first", "TE": "h5_stability_hybrid",
        })
        self.assertEqual(LIMITS, {"QB": 45, "RB": 80, "WR": 100, "TE": 35})

    def test_2026_board_query_uses_prior_seasons_and_sleeper(self):
        sql = build_query("project", "brain", "metrics")
        self.assertIn("season BETWEEN 2023 AND 2025", sql)
        self.assertIn("v_ranking_post_formula_safety", sql)
        self.assertIn("post_formula_adjustment sleeper_role_adjustment", sql)
        self.assertNotIn("target_fantasy_points", sql)

    def test_gng_unified_replacement_contract(self):
        self.assertEqual(REPLACEMENT, {"QB": 13, "RB": 36, "WR": 55, "TE": 12})

    def test_rookie_floor_preserves_position_order(self):
        board=[
            {"overall_rank":1,"player_id":"rb1","player_name":"RB One","position":"RB","position_rank":1,"adjusted_vorp":5.0},
            {"overall_rank":2,"player_id":"love","player_name":"Jeremiyah Love","position":"RB","position_rank":2,"adjusted_vorp":4.0},
            {"overall_rank":3,"player_id":"rb3","player_name":"RB Three","position":"RB","position_rank":3,"adjusted_vorp":3.0},
            {"overall_rank":4,"player_id":"wr1","player_name":"WR One","position":"WR","position_rank":1,"adjusted_vorp":2.0},
            {"overall_rank":5,"player_id":"wr2","player_name":"WR Two","position":"WR","position_rank":2,"adjusted_vorp":1.0},
        ]
        adjusted=apply_position_locked_overall_floor(board,player_name="Jeremiyah Love",minimum_overall=4)
        self.assertEqual([row["player_id"] for row in adjusted],["rb1","wr1","wr2","love","rb3"])

    def test_multiple_position_floors_compose(self):
        board=[
            {"overall_rank":1,"player_id":"rb1","player_name":"RB One","position":"RB","position_rank":1},
            {"overall_rank":2,"player_id":"love","player_name":"Jeremiyah Love","position":"RB","position_rank":2},
            {"overall_rank":3,"player_id":"qb1","player_name":"QB One","position":"QB","position_rank":1},
            {"overall_rank":4,"player_id":"hurts","player_name":"Jalen Hurts","position":"QB","position_rank":2},
            {"overall_rank":5,"player_id":"wr1","player_name":"WR One","position":"WR","position_rank":1},
        ]
        adjusted=apply_position_locked_floors(board,{"Jeremiyah Love":4,"Jalen Hurts":5})
        self.assertEqual(next(row["overall_rank"] for row in adjusted if row["player_id"]=="love"),4)
        self.assertEqual(next(row["overall_rank"] for row in adjusted if row["player_id"]=="hurts"),5)

    def test_gng_promotion_is_profile_scoped_and_transactional(self):
        sql=build_gng_promotion_sql("project","brain","metrics","version")
        self.assertIn("BEGIN TRANSACTION",sql)
        self.assertIn("scoring_profile_id='gng_keeper'",sql)
        self.assertIn("CAST(sleeper_player_id AS STRING)",sql)
        self.assertIn("COMMIT TRANSACTION",sql)


if __name__ == "__main__":
    unittest.main()
