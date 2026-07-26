import unittest

from scripts.run_ppr_fable_transfer_backtest import evaluate, summarize


class PprFableTransferBacktestTest(unittest.TestCase):
    def test_perfect_order(self):
        rows = [{"player_id": str(rank), "player_name": str(rank), "score": 40-rank, "target_ppg": 40-rank, "target_points": (40-rank)*10} for rank in range(1, 31)]
        result = summarize(rows)
        self.assertEqual(result["spearman"], 1.0)
        self.assertEqual(result["top12_precision"], 1.0)

    def test_evaluate_uses_three_folds(self):
        rows = []
        for season in (2022, 2023, 2024):
            rows.extend({"season": season, "player_id": f"{season}-{rank}", "player_name": str(rank), "candidate": 40-rank, "target_ppg": 40-rank, "target_points": (40-rank)*10} for rank in range(1, 31))
        self.assertEqual(len(evaluate(rows, "candidate")["folds"]), 3)


if __name__ == "__main__":
    unittest.main()
