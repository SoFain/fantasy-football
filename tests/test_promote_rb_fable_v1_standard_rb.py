import unittest

from scripts.promote_rb_fable_v1_standard_rb import WRITE_GATE, build_statements


STATEMENTS = dict(build_statements(
    project="proj", brain="brain", metrics="metrics",
    version="rb-fable-v1-standard-test", run_id="run-test", selected_by="owner",
))


class PromoteRbFableV1Test(unittest.TestCase):
    def test_scope_is_standard_rb_only(self):
        for name in ("archive_prior_board", "deactivate_prior_board"):
            sql = STATEMENTS[name]
            self.assertIn("position = 'RB'", sql)
            self.assertIn("scoring_profile_id = 'standard'", sql)
        insert = STATEMENTS["insert_new_board"]
        self.assertIn("'RB' AS position", insert)
        self.assertIn("'standard' AS scoring_profile_id", insert)
        for other in ("'QB'", "'WR'", "'TE'", "half_ppr", "'ppr'", "gng", "keeper"):
            self.assertNotIn(other, insert.lower() if other.islower() else insert)

    def test_prior_board_archived_before_deactivation(self):
        names = [name for name, _ in build_statements(
            project="p", brain="b", metrics="m", version="v", run_id="r", selected_by="o")]
        self.assertLess(names.index("archive_prior_board"), names.index("deactivate_prior_board"))
        self.assertLess(names.index("deactivate_prior_board"), names.index("insert_new_board"))
        self.assertIn("NOT EXISTS", STATEMENTS["archive_prior_board"])  # idempotent archive

    def test_no_2026_outcomes_and_no_invented_metrics(self):
        insert = STATEMENTS["insert_new_board"]
        self.assertIn("season = 2025 AND rb_fable_01_score IS NOT NULL", insert)
        combined = " ".join(sql for sql in STATEMENTS.values()).lower()
        for banned in ("broken_tackle", "yac_above_expectation", "market_value", "route_share", "yprr"):
            self.assertNotIn(banned, combined)
        # 2026 appears only as the board season label, never as a stats/outcome filter.
        self.assertIn("2026 AS season", insert)
        self.assertNotIn("season = 2026", combined)

    def test_sleeper_context_is_display_only(self):
        insert = STATEMENTS["insert_new_board"]
        self.assertIn("rb_fable_01_score AS raw_ranking_score", insert)
        # The ranking order must come from the Fable score alone.
        self.assertIn("ORDER BY rb_fable_01_score DESC", insert)
        for field in ("injury_status", "depth_chart_order"):
            self.assertNotIn(f"{field} *", insert)
            self.assertNotIn(f"* {field}", insert)

    def test_write_gate_name(self):
        self.assertEqual(WRITE_GATE, "ALLOW_RB_FABLE_V1_STANDARD_RB_PROMOTION")


if __name__ == "__main__":
    unittest.main()
