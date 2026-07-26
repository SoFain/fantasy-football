from __future__ import annotations

import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from src import sleeper_player_snapshot as snapshot


class SleeperPlayerSnapshotTests(unittest.TestCase):
    def test_build_snapshot_rows_preserves_current_context_fields(self):
        rows = snapshot.build_snapshot_rows(
            {
                "123": {
                    "first_name": "Tyreek",
                    "last_name": "Hill",
                    "gsis_id": "00-0033040",
                    "position": "WR",
                    "team": None,
                    "active": True,
                    "status": "Active",
                    "injury_status": None,
                    "fantasy_positions": ["WR"],
                    "depth_chart_position": "WR",
                    "depth_chart_order": 1,
                    "search_rank": 10,
                    "years_exp": 10,
                }
            },
            snapshot_at=datetime(2026, 7, 5, 12, 0, tzinfo=timezone.utc),
            loaded_at=datetime(2026, 7, 5, 12, 0, tzinfo=timezone.utc),
            loaded_by="tester",
        )

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["snapshot_id"], "sleeper_players_20260705T120000Z")
        self.assertEqual(row["snapshot_year"], 2026)
        self.assertEqual(row["player_name"], "Tyreek Hill")
        self.assertEqual(row["gsis_id"], "00-0033040")
        self.assertIsNone(row["team"])
        self.assertIn('"WR"', row["fantasy_positions_json"])
        self.assertEqual(row["source_url"], snapshot.SLEEPER_PLAYERS_URL)
        self.assertTrue(row["row_hash"])

    def test_write_requires_sleeper_specific_gate(self):
        rows = snapshot.build_snapshot_rows(
            {"1": {"first_name": "Example", "last_name": "Player"}},
            snapshot_at=datetime(2026, 7, 5, tzinfo=timezone.utc),
            loaded_at=datetime(2026, 7, 5, tzinfo=timezone.utc),
            loaded_by="tester",
        )

        with patch.dict(os.environ, {"ALLOW_TRADE_SCORE_MATERIALIZATION": "true"}, clear=False):
            with self.assertRaisesRegex(PermissionError, snapshot.WRITE_GATE):
                snapshot.write_snapshot_rows(rows, project="test-project", dataset="test_dataset")

    def test_dry_run_cli_does_not_write(self):
        with patch.object(snapshot, "fetch_sleeper_players", return_value={"1": {"first_name": "A", "last_name": "B"}}):
            with patch.object(snapshot, "write_snapshot_rows", side_effect=AssertionError("write called")):
                code = snapshot.main(["--dry-run"])

        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
