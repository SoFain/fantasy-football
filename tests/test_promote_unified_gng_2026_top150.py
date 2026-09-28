from __future__ import annotations

import unittest

from scripts.promote_unified_gng_2026_top150 import validate_active_position_rows


class PromoteUnifiedGng2026Top150Tests(unittest.TestCase):
    def test_validates_position_rank_and_formula_without_requiring_ranking_version(self):
        board = [{
            "player_id": "player-1",
            "player_name": "Player One",
            "position": "WR",
            "position_rank": 12,
            "formula_id": "GNG_WR_W1",
        }]
        active = [{
            "player_id": "player-1",
            "position": "WR",
            "rank": 12,
            "model_name": "GNG_WR_W1",
        }]

        validate_active_position_rows(board, active)

    def test_rejects_formula_drift(self):
        board = [{
            "player_id": "player-1",
            "player_name": "Player One",
            "position": "WR",
            "position_rank": 12,
            "formula_id": "GNG_WR_W1",
        }]
        active = [{
            "player_id": "player-1",
            "position": "WR",
            "rank": 12,
            "model_name": "different-formula",
        }]

        with self.assertRaisesRegex(ValueError, "does not match active positional rankings"):
            validate_active_position_rows(board, active)


if __name__ == "__main__":
    unittest.main()
