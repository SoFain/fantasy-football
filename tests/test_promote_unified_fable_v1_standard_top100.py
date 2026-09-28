import os
import unittest
from unittest.mock import patch

from scripts import promote_unified_fable_v1_standard_top100 as promotion


class PromoteUnifiedFableV1StandardTop100Test(unittest.TestCase):
    def test_write_gate_is_named_and_default_off(self):
        self.assertEqual(promotion.WRITE_GATE, "ALLOW_UNIFIED_FABLE_V1_TOP100_PROMOTION")
        with patch.dict(os.environ, {}, clear=True):
            self.assertNotEqual(os.environ.get(promotion.WRITE_GATE), "true")

    def test_schema_keeps_overall_and_position_rank_separate(self):
        names = {field.name for field in promotion.schema()}
        self.assertIn("overall_rank", names)
        self.assertIn("position_rank", names)
        self.assertIn("qb_backtest_proxy_disclosed", names)

    def test_active_position_validation_rejects_stale_wr_queue(self):
        board = [{
            "player_id": "ajb",
            "player_name": "A.J. Brown",
            "position": "WR",
            "position_rank": 15,
            "ranking_version": "stale-wr",
        }]
        active = [{
            "player_id": "ajb",
            "position": "WR",
            "rank": 7,
            "ranking_version": "current-wr",
        }]

        with self.assertRaisesRegex(ValueError, "does not match active positional rankings"):
            promotion.validate_active_position_ranks(board, active)


if __name__ == "__main__":
    unittest.main()
