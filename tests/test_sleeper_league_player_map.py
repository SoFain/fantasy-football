import json
import unittest

from src import ingest_sleeper_league as isl


class FakeJob:
    def __init__(self, rows):
        self._rows = rows

    def result(self):
        return self._rows


class FakeClient:
    project = "test-project"

    def __init__(self, rows):
        self._rows = rows
        self.queries = []

    def query(self, sql, job_config=None):
        self.queries.append(sql)
        return FakeJob(self._rows)


def _row(pid="1042", **overrides):
    row = {
        "sleeper_player_id": pid,
        "player_name": "James Cook",
        "position": "RB",
        "team": "BUF",
        "gsis_id": "00-0036223",
        "status": "Active",
        "injury_status": None,
        "depth_chart_position": "RB",
        "depth_chart_order": 1,
        "active": True,
        "fantasy_positions_json": json.dumps(["RB"]),
    }
    row.update(overrides)
    return row


class LoadPlayersMapFromWarehouseTest(unittest.TestCase):
    def test_reads_from_current_snapshot_table(self):
        client = FakeClient([_row()])
        isl.load_players_map_from_warehouse(client)
        self.assertIn("sleeper_players_current", client.queries[0])

    def test_never_calls_players_endpoint(self):
        # The whole point: this path must not touch /players/. It has no network
        # dependency at all, only the warehouse client.
        client = FakeClient([_row()])
        result = isl.load_players_map_from_warehouse(client)
        self.assertEqual(len(client.queries), 1)
        self.assertIn("1042", result)

    def test_keyed_by_string_id(self):
        client = FakeClient([_row(pid=2403)])
        result = isl.load_players_map_from_warehouse(client)
        self.assertIn("2403", result)

    def test_full_name_available_for_player_name_helper(self):
        client = FakeClient([_row()])
        result = isl.load_players_map_from_warehouse(client)
        self.assertEqual(isl.player_name(result["1042"]), "James Cook")

    def test_parses_fantasy_positions_json(self):
        client = FakeClient([_row(fantasy_positions_json=json.dumps(["RB", "WR"]))])
        result = isl.load_players_map_from_warehouse(client)
        self.assertEqual(result["1042"]["fantasy_positions"], ["RB", "WR"])

    def test_bad_fantasy_positions_json_becomes_empty(self):
        client = FakeClient([_row(fantasy_positions_json="{not json")])
        result = isl.load_players_map_from_warehouse(client)
        self.assertEqual(result["1042"]["fantasy_positions"], [])

    def test_null_fantasy_positions_json(self):
        client = FakeClient([_row(fantasy_positions_json=None)])
        result = isl.load_players_map_from_warehouse(client)
        self.assertEqual(result["1042"]["fantasy_positions"], [])

    def test_carries_fields_build_records_needs(self):
        client = FakeClient([_row(injury_status="Questionable")])
        entry = isl.load_players_map_from_warehouse(client)["1042"]
        for key in ("position", "team", "gsis_id", "status", "injury_status", "depth_chart_order"):
            self.assertIn(key, entry)
        self.assertEqual(entry["injury_status"], "Questionable")

    def test_empty_snapshot_yields_empty_map(self):
        self.assertEqual(isl.load_players_map_from_warehouse(FakeClient([])), {})


if __name__ == "__main__":
    unittest.main()
