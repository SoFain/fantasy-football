import unittest

from scripts.adjudicate_te_fable_v1a_standard_te import summarize


class GuardedTeAdjudicationTest(unittest.TestCase):
    def test_summary_separates_repairs_from_order_rebalance(self):
        rows = [
            {"player_name":"A","candidate_rank":1,"rank":1,"llm_rank_delta":0,"llm_adjustment_code":"NO_ADJUSTMENT","llm_adjustment_detail":"","llm_adjustment_evidence":""},
            {"player_name":"B","candidate_rank":3,"rank":2,"llm_rank_delta":1,"llm_adjustment_code":"CURRENT_ROLE_UPGRADE","llm_adjustment_detail":"Starter","llm_adjustment_evidence":"depth=1"},
            {"player_name":"C","candidate_rank":2,"rank":3,"llm_rank_delta":-1,"llm_adjustment_code":"ORDER_REBALANCE","llm_adjustment_detail":"Mechanical","llm_adjustment_evidence":"application"},
        ]
        result = summarize(rows)
        self.assertEqual(result["moved_count"], 2)
        self.assertEqual(result["substantive_adjustment_count"], 1)
        self.assertEqual(result["total_absolute_movement"], 2)


if __name__ == "__main__":
    unittest.main()
