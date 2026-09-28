"""Standing rule (2026-09-27): no player-specific hand rules; judgment calls are logged, not blocking."""

import json
from pathlib import Path
import unittest
from tempfile import TemporaryDirectory

from scripts.promote_gng_2026_rankings import STRUCTURAL_PREFLIGHT, check_preflight, hard_review_sql
from src.review_log import append_review_items

ROOT = Path(__file__).resolve().parents[1]
# Pipeline code that decides who is ranked and where.
DECISION_PATHS = (
    "scripts/audit_current_player_ranking_coverage.py",
    "scripts/build_gng_2026_candidate_boards.py",
    "scripts/build_standard_wr_fable_v1_safety_review.py",
    "scripts/build_unified_gng_2026_top100.py",
    "scripts/promote_gng_2026_rankings.py",
    "scripts/promote_ppr_fable_v1_positional.py",
    "scripts/promote_standard_fable_v1_positional.py",
    "scripts/promote_standard_qb_guarded_75_25.py",
    "src/gng_sleeper_safety.py",
)
REMOVED_NAMES = (
    "A.J. Brown", "Justin Jefferson", "Garrett Wilson", "Stefon Diggs", "Deebo Samuel", "Keenan Allen",
    "Hunter Renfrow", "Gabe Davis", "Sterling Shepard", "Tyreek Hill", "Zach Ertz", "Theo Wease",
    "MarShawn Lloyd", "Caleb Williams", "DK Metcalf", "Zach Charbonnet", "Kimani Vidal",
    "Colby Parkinson", "Jeremiyah Love",
)
REMOVED_SYMBOLS = (
    "ranking_owner_decisions", "STANDARD_WR_ELITE_ORDER", "GNG_WATCHLIST_NAMES",
    "COVERAGE_GATE_REVIEW_ONLY_DECISIONS", "GNG_INJURED_STARTER_HARD_REVIEW_DECISIONS",
    "is_owner_approved_injured_starter", "apply_position_locked_floors", "acknowledge_crossings",
    "live_position_rank", "recommended_rank", "OWNER_APPROVED",
)


def passing_state(**overrides):
    return {**STRUCTURAL_PREFLIGHT, "hard_reviews": 0, **overrides}


class OwnerRulesRemovedTest(unittest.TestCase):
    def test_decision_code_has_no_player_names_or_owner_exception_symbols(self):
        self.assertFalse((ROOT / "src/ranking_owner_decisions.py").exists())
        self.assertFalse((ROOT / "scripts/publish_ppr_fable_v1_candidate_boards.py").exists())
        for relative in DECISION_PATHS:
            text = (ROOT / relative).read_text(encoding="utf-8")
            for token in (*REMOVED_NAMES, *REMOVED_SYMBOLS):
                self.assertNotIn(token, text, f"{token} in {relative}")

    def test_gng_hard_reviews_do_not_block_preflight(self):
        check_preflight(passing_state(hard_reviews=3))

    def test_gng_structural_preflight_still_blocks(self):
        for key, bad in (
            ("positional_rows", 259), ("unified_rows", 149), ("teamless_positional", 1),
            ("teamless_unified", 1), ("noncontiguous_positions", 1), ("queue_mismatches", 2),
        ):
            with self.assertRaises(RuntimeError, msg=key):
                check_preflight(passing_state(**{key: bad}))
        with self.assertRaises(RuntimeError):
            check_preflight({k: v for k, v in passing_state().items() if k != "queue_mismatches"})

    def test_gng_hard_review_query_reads_the_promoted_positional_board(self):
        sql = hard_review_sql("p", "m")
        self.assertIn("`p.m.gng_2026_positional_boards_with_rookies`", sql)
        self.assertIn("WHERE sleeper_hard_review", sql)

    def test_review_log_appends_json_lines_and_skips_empty(self):
        with TemporaryDirectory() as directory:
            log_dir = Path(directory) / "review-log"
            self.assertIsNone(append_review_items("gate", [], log_dir=log_dir))
            self.assertFalse(log_dir.exists())
            path = append_review_items("gate", [{"player_name": "A"}], log_dir=log_dir)
            append_review_items("gate", [{"player_name": "B"}], log_dir=log_dir)
            lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([line["player_name"] for line in lines], ["A", "B"])
        self.assertTrue(all(line["kind"] == "gate" and line["logged_at"] for line in lines))


if __name__ == "__main__":
    unittest.main()
