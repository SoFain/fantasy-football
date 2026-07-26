from __future__ import annotations

import unittest

from scripts.audit_current_player_ranking_coverage import (
    classify_omission,
    identity_keys,
    live_frontline_players,
    normalize_name,
)


class CurrentPlayerRankingCoverageTest(unittest.TestCase):
    def test_name_normalization_ignores_punctuation_and_suffix(self) -> None:
        self.assertEqual("marvinharrison", normalize_name("Marvin Harrison Jr."))
        self.assertEqual("djmoore", normalize_name("D.J. Moore"))

    def test_identity_keys_prefer_ids_but_keep_name_fallback(self) -> None:
        self.assertEqual(
            [("WR", "id:00-0039849"), ("WR", "id:11628"), ("WR", "name:marvinharrison")],
            identity_keys("Marvin Harrison Jr.", "WR", "gsis:00-0039849", "sleeper:11628"),
        )

    def test_frontline_universe_requires_current_depth_order_one(self) -> None:
        players = {
            "1": {"full_name": "Starter", "position": "WR", "team": "BUF", "active": True, "status": "Active", "depth_chart_order": 1, "years_exp": 2},
            "2": {"full_name": "Backup", "position": "WR", "team": "BUF", "active": True, "status": "Active", "depth_chart_order": 2, "years_exp": 2},
            "3": {"full_name": "Free Agent", "position": "RB", "team": None, "active": True, "status": "Active", "depth_chart_order": 1, "years_exp": 3},
        }
        self.assertEqual(["Starter"], [row["player_name"] for row in live_frontline_players(players)])

    def test_classifier_separates_threshold_identity_and_rookie_gaps(self) -> None:
        veteran = {"position": "WR", "years_exp": 2}
        rookie = {"position": "WR", "years_exp": 0}
        self.assertEqual(
            "BELOW_2025_FABLE_QUALIFICATION_THRESHOLD",
            classify_omission(veteran, None, {"identity_accepted": True, "formula_eligible": False}, set()),
        )
        self.assertEqual(
            "IDENTITY_BRIDGE_COLLISION",
            classify_omission(veteran, None, {"duplicate_identity_collision": True}, set()),
        )
        self.assertEqual("ROOKIE_SYSTEM_REQUIRED", classify_omission(rookie, None, None, set()))
        self.assertEqual(
            "POSITIONAL_PROMOTION_OR_BOARD_CUTOFF",
            classify_omission(
                veteran,
                {"coverage_method": "PRIOR_QUALIFIED_VETERAN_CARRY_FORWARD"},
                {"identity_accepted": True, "formula_eligible": False},
                {"ppr", "half_ppr"},
            ),
        )


if __name__ == "__main__":
    unittest.main()
