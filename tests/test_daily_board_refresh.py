import unittest

from scripts.run_daily_board_refresh import ROW_CONTRACTS, matches_row_contract


class DailyBoardRefreshTest(unittest.TestCase):
    def test_standard_rb_contract_allows_bounded_formula_pool_changes(self):
        contract = ROW_CONTRACTS["standard"]["RB"]
        self.assertTrue(matches_row_contract(85, contract))
        self.assertTrue(matches_row_contract(86, contract))
        self.assertFalse(matches_row_contract(79, contract))

    def test_other_position_contracts_remain_exact(self):
        self.assertTrue(matches_row_contract(45, ROW_CONTRACTS["standard"]["QB"]))
        self.assertFalse(matches_row_contract(46, ROW_CONTRACTS["standard"]["QB"]))


if __name__ == "__main__":
    unittest.main()
