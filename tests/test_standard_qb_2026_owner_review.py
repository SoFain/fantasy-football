import unittest

from scripts.run_standard_qb_2026_owner_review import (
    assign_guarded_consensus_ranks,
    build_owner_review_sql,
    summarize,
)


class StandardQb2026OwnerReviewTests(unittest.TestCase):
    def setUp(self):
        self.sql = build_owner_review_sql("project", "dataset")

    def test_is_standard_qb_read_only(self):
        self.assertIn("scoring_profile_id = 'standard'", self.sql)
        self.assertIn("rankings.position = 'QB'", self.sql)
        upper = self.sql.upper()
        for keyword in ("INSERT INTO", "UPDATE ", "DELETE ", "MERGE ", "CREATE OR REPLACE"):
            self.assertNotIn(keyword, upper)

    def test_uses_live_and_deterministic_control_ranks(self):
        self.assertIn("rankings.rank AS live_rank", self.sql)
        self.assertIn("COALESCE(rankings.candidate_rank, rankings.rank) AS anchor_rank", self.sql)

    def test_uses_latest_leakage_safe_pre_2026_features(self):
        self.assertIn("target_season <= 2025", self.sql)
        self.assertIn("source_window_end_season < 2026", self.sql)
        self.assertIn("ORDER BY target_season DESC, target_week DESC", self.sql)

    def test_builds_exact_challenger_weights(self):
        self.assertIn("0.75 * live_board.anchor_rank", self.sql)
        self.assertIn("0.125 * scaled_signals.linear_scaled_rank", self.sql)
        self.assertIn("0.125 * scaled_signals.logistic_scaled_rank", self.sql)
        self.assertIn("0.70 * live_board.anchor_rank", self.sql)
        self.assertIn("0.30 * scaled_signals.linear_scaled_rank", self.sql)

    def test_missing_history_and_rookies_use_deterministic_lane(self):
        self.assertIn("rookie_deterministic_lane", self.sql)
        self.assertIn("missing_history_deterministic_lane", self.sql)
        self.assertIn("THEN live_board.anchor_rank", self.sql)

    def test_has_movement_cutline_and_rushing_tripwires(self):
        self.assertIn("consensus_rushing_only_riser", self.sql)
        self.assertIn("consensus_qb6_crossing", self.sql)
        self.assertIn("consensus_qb12_crossing", self.sql)
        self.assertIn("consensus_qb24_crossing", self.sql)
        self.assertIn("passing_epa_per_dropback <= 0", self.sql)
        self.assertIn("passing_cpoe <= 0", self.sql)

    def test_exact_guarded_assignment_locks_missing_rows_and_blocks_weak_cutline_rise(self):
        board = []
        for rank in range(1, 9):
            board.append(
                {
                    "player_id": str(rank),
                    "player_name": f"QB {rank}",
                    "anchor_rank": rank,
                    "live_rank": rank,
                    "consensus_75_25_rank": 1 if rank == 7 else rank,
                    "has_bqml_features": rank == 7,
                    "passing_epa_per_dropback": -0.1 if rank == 7 else None,
                    "passing_cpoe": -1.0 if rank == 7 else None,
                }
            )
        result = assign_guarded_consensus_ranks(board)
        self.assertEqual(sorted(record["guarded_consensus_rank"] for record in result), list(range(1, 9)))
        weak_qb = next(record for record in result if record["player_id"] == "7")
        self.assertEqual(weak_qb["guarded_consensus_rank"], 7)
        self.assertFalse(weak_qb["guarded_qb6_crossing"])
        for record in result:
            if record["player_id"] != "7":
                self.assertEqual(record["guarded_consensus_rank"], record["anchor_rank"])

    def test_depth_chart_buckets_put_backups_after_starters(self):
        board = []
        for rank in range(1, 6):
            board.append(
                {
                    "player_id": str(rank),
                    "player_name": f"QB {rank}",
                    "anchor_rank": rank,
                    "live_rank": rank,
                    "consensus_75_25_rank": 1 if rank >= 4 else rank,
                    "has_bqml_features": True,
                    "passing_epa_per_dropback": 0.1,
                    "passing_cpoe": 1.0,
                    "sleeper_depth_chart_order": 2 if rank == 4 else (3 if rank == 5 else 1),
                }
            )
        result = assign_guarded_consensus_ranks(board)
        ranks = {record["player_id"]: record["guarded_consensus_rank"] for record in result}
        self.assertEqual(ranks["4"], 4)
        self.assertEqual(ranks["5"], 5)

    def test_summary_counts_board_tripwires(self):
        board = [
            {
                "ranking_version": "v",
                "model_run_id": "run",
                "has_bqml_features": True,
                "review_lane": "returning_player_bqml_lane",
                "consensus_movement_from_anchor": 3,
                "linear_movement_from_anchor": 4,
                "guarded_movement_from_anchor": 2,
                "guarded_consensus_rank": 2,
                "consensus_movement_review": True,
                "linear_movement_review": True,
                "guarded_movement_review": False,
                "consensus_rushing_only_riser": False,
                "linear_rushing_only_riser": True,
                "guarded_weak_passing_riser": False,
                "consensus_qb6_crossing": True,
                "consensus_qb12_crossing": False,
                "consensus_qb24_crossing": False,
                "linear_qb6_crossing": False,
                "linear_qb12_crossing": True,
                "linear_qb24_crossing": False,
                "guarded_qb6_crossing": False,
                "guarded_qb12_crossing": False,
                "guarded_qb24_crossing": False,
            }
        ]
        result = summarize(board)
        self.assertEqual(result["player_count"], 1)
        self.assertEqual(result["linear_max_movement"], 4)
        self.assertEqual(result["guarded_max_movement"], 2)
        self.assertEqual(result["linear_rushing_only_riser_count"], 1)
        self.assertEqual(result["duplicate_guarded_rank_count"], 0)


if __name__ == "__main__":
    unittest.main()
