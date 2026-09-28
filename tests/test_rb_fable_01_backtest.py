import unittest

from scripts.run_rb_fable_01_backtest import fold_summary, pairwise_win_rate, rank_values


class RbFable01BacktestTest(unittest.TestCase):
    def test_rank_values_handles_ties(self):
        self.assertEqual(rank_values([3.0, 2.0, 2.0, 1.0]), [1.0, 2.5, 2.5, 4.0])

    def test_pairwise_perfect_order(self):
        records = [
            {"rb_fable_01_score": 3.0, "target_standard_ppg": 12.0},
            {"rb_fable_01_score": 2.0, "target_standard_ppg": 10.0},
            {"rb_fable_01_score": 1.0, "target_standard_ppg": 8.0},
        ]
        self.assertEqual(pairwise_win_rate(records), 1.0)

    def test_fold_summary_is_bounded(self):
        records = []
        for index in range(1, 41):
            records.append({
                "candidate_internal_player_id": str(index), "player_name": f"P{index:02}",
                "rb_fable_01_score": float(41 - index), "target_standard_ppg": float(41 - index),
                "target_standard_points": float((41 - index) * 10), "standard_receptions": 0.0,
                "target_share": 0.0,
            })
        summary = fold_summary(records)
        self.assertEqual(summary["top_12_hit_rate"], 1.0)
        self.assertEqual(summary["pairwise_draft_win_rate"], 1.0)
        self.assertEqual(summary["elite_rb_miss_count"], 0)


if __name__ == "__main__":
    unittest.main()
