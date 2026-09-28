from __future__ import annotations

import unittest

from scripts.audit_current_player_ranking_coverage import (
    BLOCKING_TRACE_CODES,
    REVIEW_ONLY_TRACE_CODES,
    classify_omission,
    identity_keys,
    is_blocking_omission,
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

    def test_every_trace_code_has_exactly_one_gate_status(self) -> None:
        emitted = {
            "ROOKIE_SYSTEM_REQUIRED", "QB_COVERAGE_REVIEW", "NO_2025_SITUATIONAL_SOURCE_ROW",
            "IDENTITY_BRIDGE_COLLISION", "IDENTITY_BRIDGE_UNMAPPED",
            "BELOW_2025_FABLE_QUALIFICATION_THRESHOLD", "FABLE_FORMULA_TRANSFORM_DROPOUT",
            "NOT_IN_RECEPTION_CANDIDATE_TABLES", "POSITIONAL_PROMOTION_OR_BOARD_CUTOFF",
        }
        self.assertEqual(emitted, BLOCKING_TRACE_CODES | REVIEW_ONLY_TRACE_CODES)
        self.assertFalse(BLOCKING_TRACE_CODES & REVIEW_ONLY_TRACE_CODES)

    def test_judgment_codes_are_review_only_for_any_player(self) -> None:
        # MarShawn Lloyd (no 2025 sample) and Theo Wease (thin sample, slot
        # conflict) used to need named exceptions. Now the code decides.
        for trace_code in (
            "NO_2025_SITUATIONAL_SOURCE_ROW",
            "BELOW_2025_FABLE_QUALIFICATION_THRESHOLD",
            "QB_COVERAGE_REVIEW",
            "POSITIONAL_PROMOTION_OR_BOARD_CUTOFF",
        ):
            omission = {"player_name": "Any Veteran", "position": "RB", "years_exp": 4, "trace_code": trace_code}
            self.assertFalse(is_blocking_omission(omission), trace_code)

    def test_pipeline_loss_codes_block_established_players_only(self) -> None:
        for trace_code in sorted(BLOCKING_TRACE_CODES):
            veteran = {"player_name": "Any Veteran", "position": "WR", "years_exp": 3, "trace_code": trace_code}
            self.assertTrue(is_blocking_omission(veteran), trace_code)
            self.assertFalse(is_blocking_omission({**veteran, "years_exp": 0}), trace_code)
            self.assertFalse(is_blocking_omission({**veteran, "years_exp": None}), trace_code)

    def test_formula_row_without_reception_candidate_is_blocking_code(self) -> None:
        veteran = {"position": "WR", "years_exp": 5}
        code = classify_omission(veteran, {"coverage_method": None}, {"identity_accepted": True}, set())
        self.assertEqual("NOT_IN_RECEPTION_CANDIDATE_TABLES", code)
        self.assertTrue(is_blocking_omission({**veteran, "trace_code": code}))


if __name__ == "__main__":
    unittest.main()
