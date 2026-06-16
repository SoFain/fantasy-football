from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone

from google.api_core.exceptions import NotFound

from src.build_player_identity import (
    PlayerIdentityOverride,
    PlayerSourceRecord,
    build_identity_rows,
    fetch_source_records,
    normalize_player_name,
)


class MissingTablesClient:
    project = "test-project"

    def get_table(self, table_id):
        raise NotFound(f"missing {table_id}")


class PlayerIdentityTests(unittest.TestCase):
    def test_normalizes_difficult_names(self):
        cases = {
            "Amon-Ra St. Brown": "amonrastbrown",
            "Patrick Mahomes II": "patrickmahomes",
            "Brian Robinson Jr.": "brianrobinson",
            "De'Von Achane": "devonachane",
            "Jaxon Smith-Njigba": "jaxonsmithnjigba",
            "D.K. Metcalf": "dkmetcalf",
            "C.J. Stroud": "cjstroud",
            "Kenneth Walker III": "kennethwalker",
            "Travis Etienne Jr.": "travisetienne",
            "Puka Nacua": "pukanacua",
        }

        for raw_name, normalized in cases.items():
            self.assertEqual(normalize_player_name(raw_name), normalized)

    def test_manual_override_priority_wins(self):
        rows = build_identity_rows(
            [
                PlayerSourceRecord(
                    source="sleeper_players_current",
                    source_player_id="4034",
                    sleeper_player_id="4034",
                    display_name="Puka Nacua",
                    position="WR",
                    current_team="LAR",
                )
            ],
            [
                PlayerIdentityOverride(
                    source="sleeper",
                    source_player_id="4034",
                    player_id_internal="manual:puka-nacua",
                )
            ],
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        self.assertEqual(rows[0]["player_id_internal"], "manual:puka-nacua")
        self.assertEqual(rows[0]["match_method"], "manual_override")
        self.assertEqual(rows[0]["source_confidence"], 1.0)

    def test_exact_id_match_merges_sources(self):
        rows = build_identity_rows(
            [
                PlayerSourceRecord(
                    source="player_rosters",
                    source_player_id="00-0033536",
                    gsis_id="00-0033536",
                    display_name="Patrick Mahomes II",
                    position="QB",
                    current_team="KC",
                ),
                PlayerSourceRecord(
                    source="analytics_player_weekly_truth",
                    source_player_id="00-0033536",
                    gsis_id="00-0033536",
                    display_name="Patrick Mahomes",
                    position="QB",
                    current_team="KC",
                ),
            ],
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["gsis_id"], "00-0033536")
        self.assertGreaterEqual(rows[0]["source_confidence"], 0.95)
        self.assertIn("player_rosters", rows[0]["source_priority"])
        self.assertIn("analytics_player_weekly_truth", rows[0]["source_priority"])

    def test_normalized_name_team_position_fallback(self):
        rows = build_identity_rows(
            [
                PlayerSourceRecord(
                    source="sleeper_players_current",
                    display_name="D.K. Metcalf",
                    position="WR",
                    current_team="PIT",
                ),
                PlayerSourceRecord(
                    source="market_values",
                    display_name="DK Metcalf",
                    position="WR",
                    current_team="PIT",
                ),
            ],
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["normalized_name"], "dkmetcalf")
        self.assertGreaterEqual(rows[0]["source_confidence"], 0.82)

    def test_low_confidence_name_only_match_is_flagged(self):
        rows = build_identity_rows(
            [
                PlayerSourceRecord(
                    source="market_values",
                    display_name="Example Receiver",
                    position="WR",
                    current_team="LV",
                ),
                PlayerSourceRecord(
                    source="analytics_player_weekly_truth",
                    display_name="Example Receiver",
                    position="WR",
                ),
            ],
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        self.assertEqual(len(rows), 1)
        self.assertLess(rows[0]["source_confidence"], 0.8)
        self.assertIn("low_confidence_match", json.loads(rows[0]["missing_data_flags"]))

    def test_missing_optional_source_tables_are_skipped(self):
        records = fetch_source_records(MissingTablesClient(), "fantasy_football_brain")

        self.assertEqual(records, [])


if __name__ == "__main__":
    unittest.main()
