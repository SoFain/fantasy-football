from pathlib import Path
import re
import unittest

from src import trade_pick_scores


REPO_ROOT = Path(__file__).resolve().parents[1]
MIGRATION = REPO_ROOT / "bigquery" / "migrations" / "0026__trade_pick_score_v0.sql"
CONTRACTS = [
    REPO_ROOT / "bigquery" / "contracts" / "trade_pick_scores.md",
    REPO_ROOT / "bigquery" / "contracts" / "trade_pick_scores_current.md",
    REPO_ROOT / "bigquery" / "contracts" / "compat_trade_pick_scores_current.md",
]
VIEWS = [
    REPO_ROOT / "bigquery" / "views" / "trade_pick_scores_current.sql",
    REPO_ROOT / "bigquery" / "views" / "compat_trade_pick_scores_current.sql",
]
VALIDATIONS = sorted((REPO_ROOT / "bigquery" / "validations").glob("*trade_pick_scores*.sql"))


class TradePickScoreContractTests(unittest.TestCase):
    def test_migration_exists_and_is_additive(self):
        sql = MIGRATION.read_text(encoding="utf-8").lower()

        self.assertIn("create table if not exists", sql)
        self.assertIn("trade_pick_scores", sql)
        self.assertIn("create or replace view", sql)
        self.assertNotRegex(sql, r"\b(drop|delete|truncate)\b")

    def test_migration_does_not_alter_player_score_table(self):
        sql = MIGRATION.read_text(encoding="utf-8").lower()

        self.assertNotRegex(sql, r"alter\s+table\s+`?[^`\s]*trade_player_scores")
        self.assertNotRegex(sql, r"insert\s+into\s+`?[^`\s]*trade_player_scores")
        self.assertNotRegex(sql, r"merge\s+`?[^`\s]*trade_player_scores")

    def test_contracts_exist_and_document_pick_lane_boundaries(self):
        for path in CONTRACTS:
            self.assertTrue(path.exists(), path)
            text = path.read_text(encoding="utf-8").lower()
            self.assertIn("draft-pick", text)
            self.assertIn("not a player", text)
            self.assertIn("college", text)
            self.assertIn("default-off", text)

    def test_views_do_not_reference_raw_or_source_tables(self):
        forbidden = re.compile(
            r"\b(from|join)\s+`?[^`\s]*(draft_picks|college_player_stats|rookie_scouting_metrics|source_[a-z0-9_]*|raw_[a-z0-9_]*)",
            re.IGNORECASE,
        )
        for path in VIEWS:
            sql = path.read_text(encoding="utf-8")
            self.assertNotRegex(sql, forbidden)

        compat_sql = (REPO_ROOT / "bigquery" / "views" / "compat_trade_pick_scores_current.sql").read_text(encoding="utf-8")
        self.assertIn("trade_pick_scores_current", compat_sql)

    def test_validation_files_reference_pick_scores(self):
        self.assertGreaterEqual(len(VALIDATIONS), 10)
        joined = "\n".join(path.read_text(encoding="utf-8") for path in VALIDATIONS)

        self.assertIn("trade_pick_scores", joined)
        self.assertIn("compat_trade_pick_scores_current", joined)
        self.assertIn("draft_picks", joined)
        self.assertIn("college_player_stats", joined)
        self.assertIn("rookie_scouting_metrics", joined)

    def test_write_mode_still_fails_closed_without_pick_gate(self):
        with self.assertRaisesRegex(PermissionError, "ALLOW_TRADE_PICK_SCORE_MATERIALIZATION must be true"):
            trade_pick_scores.build_trade_pick_scores(
                client=object(),
                dataset_id="fantasy_football_brain",
                write=True,
            )


if __name__ == "__main__":
    unittest.main()
