from __future__ import annotations

import inspect
import json
import tempfile
import unittest
from pathlib import Path

from src import market_consensus


class FakeJob:
    def __init__(self, rows=None):
        self.rows = rows or []

    def result(self):
        return self.rows


class FakeClient:
    project = "test-project"

    def __init__(self, rows=None):
        self.rows = rows or []
        self.query_calls = []
        self.insert_calls = []

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        return FakeJob(self.rows)

    def insert_rows_json(self, table_id, rows):
        self.insert_calls.append((table_id, rows))
        return []


def identity_row(**overrides):
    row = {
        "player_id_internal": "pid_1",
        "gsis_id": "00-001",
        "sleeper_player_id": "sleeper_1",
        "fantasypros_id": "fp_1",
        "normalized_name": "ajbrown",
        "display_name": "A.J. Brown",
        "position": "WR",
        "current_team": "PHI",
    }
    row.update(overrides)
    return row


def market_row(**overrides):
    row = {
        "snapshot_id": "snap_1",
        "source_id": "manual_ecr",
        "player_id_internal": "pid_1",
        "source_player_key": "00-001",
        "source_player_name": "A.J. Brown",
        "display_name": "A.J. Brown",
        "position": "WR",
        "team": "PHI",
        "season": 2024,
        "week": 3,
        "scoring_profile_id": "ppr",
        "league_type_id": "redraft",
        "roster_format_id": "one_qb",
        "rank_overall": 10,
        "rank_position": 4,
        "projected_points": 17.0,
        "market_value": None,
        "adp": None,
        "baseline_type": "projection",
        "match_method": "source_player_key",
        "missing_data_flags": "[]",
    }
    row.update(overrides)
    return row


class MarketConsensusTests(unittest.TestCase):
    def test_register_market_source_dry_run_builds_source_object(self):
        result = market_consensus.register_market_source(
            source_id="FantasyPros-ECR-Manual",
            source_name="FantasyPros ECR Manual",
            source_type="ecr",
            access_method="csv",
            license_notes="Manual export only.",
            dry_run=True,
        )

        self.assertTrue(result["dry_run"])
        self.assertEqual(result["source"]["source_id"], "fantasypros_ecr_manual")
        self.assertEqual(result["source"]["source_type"], "ecr")
        self.assertFalse(result["source"]["automated_allowed"])

    def test_csv_normalization_maps_common_columns(self):
        rows = market_consensus.normalize_market_rows(
            [
                {
                    "Player": "A.J. Brown",
                    "POS": "WR",
                    "Team": "PHI",
                    "Rank": "5",
                    "Projected_Points": "18.5",
                    "ADP": "12.3",
                }
            ],
            snapshot_id="snap_1",
            source_id="manual_adp",
            season=2025,
            week=1,
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source_player_name"], "A.J. Brown")
        self.assertEqual(rows[0]["position"], "WR")
        self.assertEqual(rows[0]["rank_overall"], 5)
        self.assertEqual(rows[0]["projected_points"], 18.5)
        self.assertEqual(rows[0]["adp"], 12.3)
        self.assertEqual(rows[0]["snapshot_id"], "snap_1")
        self.assertEqual(rows[0]["source_id"], "manual_adp")

    def test_player_resolution_exact_id(self):
        rows = market_consensus.normalize_market_rows(
            [{"player_id_internal": "pid_1", "player": "A.J. Brown", "position": "WR"}],
            snapshot_id="snap_1",
            source_id="manual_ecr",
            season=2025,
        )

        resolved = market_consensus.resolve_market_players(rows, identity_rows=[identity_row()])

        self.assertEqual(resolved[0]["player_id_internal"], "pid_1")
        self.assertEqual(resolved[0]["match_method"], "player_id_internal")

    def test_player_resolution_name_fallback_sets_flag(self):
        rows = market_consensus.normalize_market_rows(
            [{"player": "A.J. Brown", "position": "WR", "team": "PHI"}],
            snapshot_id="snap_1",
            source_id="manual_ecr",
            season=2025,
        )

        resolved = market_consensus.resolve_market_players(rows, identity_rows=[identity_row()])
        flags = json.loads(resolved[0]["missing_data_flags"])

        self.assertEqual(resolved[0]["player_id_internal"], "pid_1")
        self.assertEqual(resolved[0]["match_method"], "name_team_position")
        self.assertIn("identity_name_fallback_match", flags)

    def test_unknown_player_retained_with_missing_flag(self):
        rows = market_consensus.normalize_market_rows(
            [{"player": "Mystery Player", "position": "WR", "team": "FA"}],
            snapshot_id="snap_1",
            source_id="manual_ecr",
            season=2025,
        )

        resolved = market_consensus.resolve_market_players(rows, identity_rows=[identity_row()])
        flags = json.loads(resolved[0]["missing_data_flags"])

        self.assertEqual(resolved[0]["match_method"], "unmatched")
        self.assertIsNone(resolved[0]["player_id_internal"])
        self.assertTrue(resolved[0]["source_player_key"].startswith("name:"))
        self.assertIn("missing_player_id_internal", flags)

    def test_snapshot_id_required(self):
        with self.assertRaisesRegex(ValueError, "snapshot_id is required"):
            market_consensus.normalize_market_rows(
                [{"player": "A.J. Brown"}],
                snapshot_id="",
                source_id="manual_ecr",
                season=2025,
            )

    def test_duplicate_source_rows_are_deduped_and_flagged(self):
        rows = market_consensus.normalize_market_rows(
            [
                {"player": "A.J. Brown", "position": "WR", "team": "PHI", "rank": "5"},
                {"player": "A.J. Brown", "position": "WR", "team": "PHI", "rank": "5"},
            ],
            snapshot_id="snap_1",
            source_id="manual_ecr",
            season=2025,
        )
        flags = json.loads(rows[0]["missing_data_flags"])

        self.assertEqual(len(rows), 1)
        self.assertIn("duplicate_source_row_dropped", flags)

    def test_ingest_csv_dry_run_reads_local_file_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "market.csv"
            path.write_text("Player,POS,Team,Projected_Points\nA.J. Brown,WR,PHI,18.5\n", encoding="utf-8")

            result = market_consensus.ingest_market_consensus_csv(
                path,
                source_id="manual_projection",
                season=2025,
                week=1,
                scoring_profile_id="ppr",
                identity_rows=[identity_row()],
                dry_run=True,
            )

        self.assertTrue(result["dry_run"])
        self.assertEqual(result["row_count"], 1)
        self.assertEqual(result["rows"][0]["player_id_internal"], "pid_1")

    def test_compare_projection_to_market(self):
        projection_rows = [
            {
                "player_id_internal": "pid_1",
                "display_name": "A.J. Brown",
                "position": "WR",
                "season": 2024,
                "week": 3,
                "scoring_profile_id": "ppr",
                "actual_points": 20.0,
                "projected_points": 18.0,
                "absolute_error": 2.0,
                "actual_rank_overall": 8,
                "rank_error_overall": 1,
                "result_json": "{}",
                "missing_data_flags": "[]",
            }
        ]

        result = market_consensus.compare_projection_to_market(projection_rows, [market_row(projected_points=14.0)])

        row = result["rows"][0]
        self.assertEqual(result["matched_market_rows"], 1)
        self.assertEqual(row["market_absolute_error"], 6.0)
        self.assertTrue(row["model_better_than_market"])
        self.assertEqual(result["summary"]["model_vs_market_mae_delta"], -4.0)

    def test_no_scraping_or_network_helpers_present(self):
        source = inspect.getsource(market_consensus)

        self.assertNotIn("requests.", source)
        self.assertNotIn("urlopen", source)
        self.assertNotIn("BeautifulSoup", source)


if __name__ == "__main__":
    unittest.main()
