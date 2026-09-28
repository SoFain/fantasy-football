import unittest

from scripts.run_unified_fable_v1_top100_backtest import qb_detail_sql, spearman


class UnifiedFableV1Top100BacktestTest(unittest.TestCase):
    def test_spearman_perfect_order(self):
        self.assertAlmostEqual(spearman([1, 2, 3], [3.0, 2.0, 1.0]), 1.0)

    def test_qb_detail_sql_is_read_only_and_exposes_scored_rows(self):
        sql = qb_detail_sql("project", "dataset")
        self.assertIn("SELECT * FROM scored", sql)
        for mutation in ("INSERT ", "UPDATE ", "DELETE ", "MERGE ", "CREATE "):
            self.assertNotIn(mutation, sql.upper())


if __name__ == "__main__":
    unittest.main()
