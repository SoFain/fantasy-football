from __future__ import annotations

import unittest

from scripts.build_gng_rank_context import (
    MAX_CONTEXT_LENGTH,
    build_context_rows,
    metric_summary,
    ordinal_percentile,
    rookie_context,
)


class GngRankContextTests(unittest.TestCase):
    def test_formats_ordinal_percentiles(self):
        self.assertEqual("1st percentile", ordinal_percentile(0.01))
        self.assertEqual("12th percentile", ordinal_percentile(0.12))
        self.assertEqual("83rd percentile", ordinal_percentile(0.83))

    def test_metric_summary_uses_signature_archetype_and_lowest_limiter(self):
        row = {
            "p_gng_weighted_opp": 0.90,
            "p_target_share": 0.85,
            "p_wopr": 0.70,
            "p_receiving_fd_expected": 0.60,
            "p_rushing_fd_expected": 0.10,
            "p_goal_line_opps": 0.80,
            "p_snap_share": 0.50,
        }

        summary, audit_metrics, missing = metric_summary("RB", "Running Back One", row)

        self.assertIn("Running Back One's GNG-weighted opportunity (90th percentile)", summary)
        self.assertIn("Receiving support comes from target share (85th percentile)", summary)
        self.assertIn("Expected rushing first downs (10th percentile) is the clear drag", summary)
        self.assertEqual("gng_weighted_opp", audit_metrics[0][0])
        self.assertEqual([], missing)

    def test_rookie_context_is_provisional_and_succinct(self):
        context = rookie_context("WR", "Rookie Receiver")

        self.assertIn("Rookie Receiver's rank is provisional", context)
        self.assertIn("only 0.2 per WR catch", context)
        self.assertIn("provisional", context)
        self.assertIn("NFL advanced metrics", context)
        self.assertLessEqual(len(context), MAX_CONTEXT_LENGTH)

    def test_same_position_context_changes_with_player_archetype(self):
        target_driven = {
            "p_gng_weighted_opp": 0.80,
            "p_target_share": 0.99,
            "p_wopr": 0.90,
            "p_receiving_fd_expected": 0.85,
            "p_rushing_fd_expected": 0.70,
            "p_goal_line_opps": 0.65,
            "p_snap_share": 0.75,
        }
        rushing_driven = {
            "p_gng_weighted_opp": 0.85,
            "p_target_share": 0.50,
            "p_wopr": 0.45,
            "p_receiving_fd_expected": 0.55,
            "p_rushing_fd_expected": 0.90,
            "p_goal_line_opps": 0.99,
            "p_snap_share": 0.80,
        }

        receiving_context, receiving_audit, _ = metric_summary(
            "RB", "Receiving Back", target_driven
        )
        rushing_context, rushing_audit, _ = metric_summary(
            "RB", "Power Back", rushing_driven
        )

        self.assertIn("pays only 0.1 per catch", receiving_context)
        self.assertIn("maps to GNG first-down scoring", rushing_context)
        self.assertNotEqual(receiving_context, rushing_context)
        self.assertEqual("target_share", receiving_audit[0][0])
        self.assertEqual("goal_line_opps", rushing_audit[0][0])

    def test_build_preserves_active_rank_and_formula(self):
        active = [
            {
                "position": "QB",
                "rank": 1,
                "player_id": "00-1",
                "player_name": "Quarterback One",
                "current_team": "BUF",
                "rank_source": "gng_formula",
                "model_name": "q4_gng_bonus_proxy",
            }
        ]
        metrics = [
            {
                "position": "QB",
                "player_id": "00-1",
                "profile": 10.0,
                "passing_yards": 4000.0,
                "passing_fd_expected": 20.0,
                "qb_rushing": 5.0,
                "qb_ngs_efficiency": 2.0,
                "passing_cpoe": 1.0,
                "attempts": 500.0,
            }
        ]

        rows = build_context_rows(active, metrics, "2026-07-14T00:00:00Z")

        self.assertEqual(1, rows[0]["rank"])
        self.assertEqual("q4_gng_bonus_proxy", rows[0]["formula_id"])
        self.assertEqual("current_formula_inputs", rows[0]["metric_source_status"])
        self.assertLessEqual(len(rows[0]["context"]), MAX_CONTEXT_LENGTH)


if __name__ == "__main__":
    unittest.main()
