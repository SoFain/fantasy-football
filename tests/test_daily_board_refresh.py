import unittest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

from scripts.run_daily_board_refresh import ROW_CONTRACTS, matches_row_contract, assert_context_fresh


class DailyBoardRefreshTest(unittest.TestCase):
    def test_standard_rb_contract_allows_bounded_formula_pool_changes(self):
        contract = ROW_CONTRACTS["standard"]["RB"]
        self.assertTrue(matches_row_contract(85, contract))
        self.assertTrue(matches_row_contract(86, contract))
        self.assertFalse(matches_row_contract(79, contract))

    def test_other_position_contracts_remain_exact(self):
        self.assertTrue(matches_row_contract(45, ROW_CONTRACTS["standard"]["QB"]))
        self.assertFalse(matches_row_contract(46, ROW_CONTRACTS["standard"]["QB"]))

    def test_evening_eastern_snapshot_remains_fresh_across_utc_midnight(self):
        now = datetime(2026, 9, 22, 2, tzinfo=timezone.utc)
        with patch('scripts.run_daily_board_refresh.datetime') as clock, patch('scripts.run_daily_board_refresh.bq_rows') as query:
            clock.now.return_value = now
            query.return_value = [{'fetched_at': now - timedelta(hours=15)}]
            assert_context_fresh()
            query.return_value = [{'fetched_at': now - timedelta(hours=27)}]
            with self.assertRaises(RuntimeError):
                assert_context_fresh()


if __name__ == "__main__":
    unittest.main()
