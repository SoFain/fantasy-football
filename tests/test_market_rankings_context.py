import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEW = (ROOT / "bigquery" / "views" / "v_market_rankings_context.sql").read_text()

# Every ranking-producing surface: formula views, candidate builders, promoters,
# unified-board builders, and the safety layer. None may read market context.
RANKING_PRODUCER_GLOBS = (
    "bigquery/views/v_rb_fable*.sql",
    "bigquery/views/v_wr_fable*.sql",
    "bigquery/views/v_te_fable*.sql",
    "bigquery/views/v_qb_*.sql",
    "scripts/promote_*.py",
    "scripts/build_unified_*.py",
    "scripts/build_gng_2026_candidate_boards.py",
    "scripts/apply_situation_adjustments.py",
    "scripts/run_daily_board_refresh.py",
)
MARKET_TOKENS = ("v_market_rankings_context", "market_consensus_player_values")


class MarketContextIsolationTest(unittest.TestCase):
    def test_no_ranking_producer_reads_market_context(self):
        for pattern in RANKING_PRODUCER_GLOBS:
            for path in ROOT.glob(pattern):
                content = path.read_text(encoding="utf-8", errors="replace")
                for token in MARKET_TOKENS:
                    self.assertNotIn(
                        token, content,
                        f"{path.name} references {token}: market data must never feed a ranking surface",
                    )

    def test_formula_views_do_not_use_search_rank_as_input(self):
        # Rookie review lanes are an owner-approved exception: they explicitly declare
        # themselves "not a fantasy ranking or live-board source" and may order their
        # review lists by market perception. Scoring formula views may not.
        for pattern in ("bigquery/views/v_rb_fable*.sql", "bigquery/views/v_wr_fable*.sql", "bigquery/views/v_te_fable*.sql"):
            for path in ROOT.glob(pattern):
                if "rookie" in path.name:
                    header = path.read_text(encoding="utf-8", errors="replace").splitlines()[0].lower()
                    self.assertIn("not a fantasy ranking", header, f"{path.name} rookie lane must declare review-only status")
                    continue
                content = path.read_text(encoding="utf-8", errors="replace").lower()
                self.assertNotIn("search_rank", content, f"{path.name} must not consume Sleeper search_rank")

    def test_context_view_is_read_only_display(self):
        self.assertIn("REVIEW/CONTENT EVIDENCE ONLY", VIEW)
        self.assertIn("CREATE OR REPLACE VIEW", VIEW)
        for banned in ("INSERT", "UPDATE ", "DELETE", "MERGE"):
            self.assertNotIn(banned, VIEW)
        # Direction of flow: board ranks join market ranks for display; the view
        # exposes deltas and buckets, never a score adjustment.
        self.assertIn("market_delta", VIEW)
        self.assertIn("market_gap_bucket", VIEW)
        self.assertNotIn("adjust", VIEW.lower())

    def test_gap_buckets_cover_both_directions(self):
        for bucket in ("PIGSKIN_MUCH_HIGHER", "PIGSKIN_HIGHER", "MARKET_MUCH_HIGHER", "MARKET_HIGHER", "ALIGNED", "NO_MARKET_SIGNAL"):
            self.assertIn(bucket, VIEW)


if __name__ == "__main__":
    unittest.main()
