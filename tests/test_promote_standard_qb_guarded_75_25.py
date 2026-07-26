import unittest

from scripts.promote_standard_qb_guarded_75_25 import build_promotion_sql, validate_board


class PromoteStandardQbGuardedTests(unittest.TestCase):
    def test_sql_is_scoped_and_archives_before_replace(self):
        sql = build_promotion_sql(
            [self._record()],
            project="project",
            dataset="dataset",
            ranking_version="new-version",
            model_run_id="new-run",
            prior_ranking_version="old-version",
        )
        self.assertIn("analytics_pigskin_rankings_history", sql)
        self.assertIn("position='QB' AND scoring_profile_id='standard'", sql)
        self.assertIn("league_type_id='redraft'", sql)
        self.assertIn("roster_format_id='one_qb'", sql)
        self.assertIn("BEGIN TRANSACTION", sql)
        self.assertIn("COMMIT TRANSACTION", sql)

    def test_sql_records_no_llm_and_depth_guards(self):
        sql = build_promotion_sql(
            [self._record()],
            project="project",
            dataset="dataset",
            ranking_version="new-version",
            model_run_id="new-run",
            prior_ranking_version="old-version",
        )
        self.assertIn("deterministic-no-llm", sql)
        self.assertIn("NO_ADJUSTMENT", sql)
        self.assertIn("sleeper_depth_chart_order=2 AND rank<33", sql)
        self.assertIn("sleeper_depth_chart_order>=3 AND rank<44", sql)

    def test_validation_rejects_depth_two_above_qb33(self):
        board = [self._record() for _ in range(45)]
        for rank, record in enumerate(board, start=1):
            record.update(
                player_id=str(rank),
                player_name=f"QB {rank}",
                guarded_consensus_rank=rank,
                anchor_rank=rank,
                consensus_75_25_rank=rank,
                linear_70_30_rank=rank,
                guarded_movement_from_anchor=0,
                consensus_movement_from_anchor=0,
                linear_movement_from_anchor=0,
                consensus_movement_review=False,
                linear_movement_review=False,
                guarded_movement_review=False,
                consensus_rushing_only_riser=False,
                linear_rushing_only_riser=False,
                guarded_weak_passing_riser=False,
                consensus_qb6_crossing=False,
                consensus_qb12_crossing=False,
                consensus_qb24_crossing=False,
                linear_qb6_crossing=False,
                linear_qb12_crossing=False,
                linear_qb24_crossing=False,
                guarded_qb6_crossing=False,
                guarded_qb12_crossing=False,
                guarded_qb24_crossing=False,
            )
        board[0]["sleeper_depth_chart_order"] = 2
        with self.assertRaises(RuntimeError):
            validate_board(board)

    @staticmethod
    def _record():
        return {
            "player_id": "00-1",
            "player_name": "Player",
            "guarded_consensus_rank": 1,
            "anchor_rank": 1,
            "consensus_75_25_rank": 1,
            "linear_70_30_rank": 1,
            "consensus_priority": 1.0,
            "passing_epa_per_dropback": 0.1,
            "passing_cpoe": 1.0,
            "qb_rushing_baseline": 10.0,
            "sleeper_depth_chart_order": 1,
            "review_lane": "returning_player_bqml_lane",
            "ranking_version": "old-version",
            "has_bqml_features": True,
            "guarded_movement_from_anchor": 0,
            "guarded_weak_passing_riser": False,
            "guarded_qb6_crossing": False,
            "guarded_qb12_crossing": False,
            "guarded_qb24_crossing": False,
        }


if __name__ == "__main__":
    unittest.main()
