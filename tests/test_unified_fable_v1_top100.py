import unittest

from scripts.build_unified_fable_v1_top100 import (
    OVERALL_BOARD_SIZE,
    assert_position_order,
    fit_log_curve,
    interleave,
)


class UnifiedFableV1Top100Test(unittest.TestCase):
    def test_log_curve_fits_decreasing_points(self):
        a, b = fit_log_curve([(1, 20.0), (2, 17.0), (4, 14.0)])
        self.assertGreater(b, 0)
        self.assertAlmostEqual(a, 20.0, places=6)

    def test_interleave_preserves_every_position_queue(self):
        queues = {
            position: [{"player_id": f"{position}{rank}", "player_name": f"{position}{rank}"} for rank in range(1, 41)]
            for position in ("QB", "RB", "WR", "TE")
        }
        curves = {position: (20.0, 2.0) for position in queues}
        availability = {position: 1.0 for position in queues}
        board = interleave(queues, curves, availability)
        assert_position_order(board)
        self.assertEqual(len(board), OVERALL_BOARD_SIZE)

    def test_top_150_extension_preserves_the_prior_top_100_prefix(self):
        queues = {
            position: [{"player_id": f"{position}{rank}", "player_name": f"{position}{rank}"} for rank in range(1, 51)]
            for position in ("QB", "RB", "WR", "TE")
        }
        curves = {position: (20.0, 2.0) for position in queues}
        availability = {position: 1.0 for position in queues}

        previous = interleave(queues, curves, availability, limit=100)
        expanded = interleave(queues, curves, availability)

        self.assertEqual(OVERALL_BOARD_SIZE, len(expanded))
        self.assertEqual(
            [row["player_id"] for row in previous],
            [row["player_id"] for row in expanded[:100]],
        )

    def test_position_order_rejects_skip_ahead(self):
        with self.assertRaises(ValueError):
            assert_position_order([
                {"position": "RB", "position_rank": 1},
                {"position": "RB", "position_rank": 3},
            ])


if __name__ == "__main__":
    unittest.main()
