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


class MarketContextFeedTest(unittest.TestCase):
    @staticmethod
    def _row(profile, position, name, rank, sleeper_id, search_rank):
        return {
            "scoring_profile_id": profile, "position": position, "player_id": f"00-{sleeper_id}",
            "sleeper_player_id": sleeper_id, "player_name": name, "current_team": "T",
            "pigskin_position_rank": rank, "pigskin_tier": "starter", "ranking_version": "v",
            "sleeper_search_rank": search_rank, "search_rank_position_rank": 190 + rank,
            "search_rank_overall_rank": 500 + rank, "market_snapshot_at": "2026-07-26",
        }

    def test_adp_basis_and_cohort_fallback(self):
        from src.market_context_feed import build_dataset

        rows = [
            self._row("standard", "TE", "Alpha", 1, "1", 10),
            self._row("standard", "TE", "Beta", 2, "2", 40),
            self._row("standard", "TE", "Gamma", 3, "3", 20),
        ]
        market = {"season": "2026", "trending_add": [], "trending_drop": [],
                  "adp_by_player": {"1": {"adp_std": 20.0}, "2": {"adp_std": 15.0}}}
        dataset = build_dataset(rows, market, source_generated_at="2026-07-26T00:00:00Z")
        players = {p["player_name"]: p for p in dataset["profiles"]["standard"]["players"]}
        # ADP basis: Beta (15.0) ranks TE1, Alpha (20.0) TE2.
        self.assertEqual(players["Beta"]["market_position_rank"], 1)
        self.assertEqual(players["Alpha"]["market_position_rank"], 2)
        self.assertEqual(players["Alpha"]["market_source_id"], "sleeper_adp_std")
        # Fallback ranks within the 3-player board cohort, never the global pool rank.
        self.assertEqual(players["Gamma"]["market_source_id"], "sleeper_search_rank")
        self.assertEqual(players["Gamma"]["market_position_rank"], 2)
        self.assertLessEqual(players["Gamma"]["market_position_rank"], len(rows))

    def test_profile_adp_field_mapping_and_gng_proxy_label(self):
        from src.market_context_feed import PROFILE_ADP_FIELDS

        self.assertEqual(PROFILE_ADP_FIELDS["standard"][0], "adp_std")
        self.assertEqual(PROFILE_ADP_FIELDS["ppr"][0], "adp_ppr")
        self.assertEqual(PROFILE_ADP_FIELDS["half_ppr"][0], "adp_half_ppr")
        self.assertIn("proxy", PROFILE_ADP_FIELDS["gng_keeper"][1])

    def test_gap_bucket_edges(self):
        from src.market_context_feed import gap_bucket

        self.assertEqual(gap_bucket(None), "NO_MARKET_SIGNAL")
        self.assertEqual(gap_bucket(10), "PIGSKIN_MUCH_HIGHER")
        self.assertEqual(gap_bucket(4), "PIGSKIN_HIGHER")
        self.assertEqual(gap_bucket(0), "ALIGNED")
        self.assertEqual(gap_bucket(-4), "MARKET_HIGHER")
        self.assertEqual(gap_bucket(-10), "MARKET_MUCH_HIGHER")


if __name__ == "__main__":
    unittest.main()
