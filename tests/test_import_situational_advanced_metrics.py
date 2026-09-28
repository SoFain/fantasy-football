import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.import_situational_advanced_metrics import (
    METRICS,
    Source,
    metric_dictionary,
    parse_number,
    read_source,
)


class SituationalAdvancedMetricsImportTest(unittest.TestCase):
    def test_parse_number_preserves_percent_scale_and_removes_commas(self):
        self.assertEqual(parse_number("1,653"), 1653.0)
        self.assertEqual(parse_number("44.41"), 44.41)
        self.assertEqual(parse_number("44.41%"), 44.41)

    def test_rb_dictionary_does_not_fabricate_blocked_metrics(self):
        rb_names = {row["metric_name"] for row in metric_dictionary() if row["position"] == "RB"}
        self.assertIn("yards_after_contact", rb_names)
        self.assertIn("yac", rb_names)
        self.assertNotIn("broken_tackles", rb_names)
        self.assertNotIn("yac_above_expectation", rb_names)
        self.assertNotIn("yprr", rb_names)

    def test_wr_te_route_metrics_are_source_backed(self):
        route_rows = [row for row in metric_dictionary() if row["position"] in {"WR", "TE"} and row["is_route_metric"]]
        self.assertEqual({row["metric_name"] for row in route_rows}, {"routes_run", "targets_per_route_run", "yprr"})
        self.assertTrue(all(row["is_source_backed"] for row in route_rows))

    def test_read_source_preserves_raw_json_and_builds_exact_long_count(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "qb.db"
            stats = {raw_key: "1,000" if raw_key == "Pass Yards" else 1 for raw_key, *_ in METRICS["QB"]}
            stats_json = json.dumps(stats, separators=(",", ":"))
            connection = sqlite3.connect(path)
            try:
                connection.execute("CREATE TABLE qb_stats (id INTEGER, season INTEGER, refinement TEXT, refinement_label TEXT, rank INTEGER, player_id TEXT, player_name TEXT, player_slug TEXT, team TEXT, stats_json TEXT)")
                connection.execute("INSERT INTO qb_stats VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (1, 2025, "standard", "Standard", 1, "local-1", "Test Player", "test-player", "TST", stats_json))
                connection.commit()
            finally:
                connection.close()
            imported = read_source(Source("QB", path, "qb_stats"), datetime.now(timezone.utc))
            self.assertEqual(imported["raw"][0]["stats_json"], stats_json)
            self.assertEqual(imported["wide"][0]["pass_yards"], 1000.0)
            self.assertEqual(len(imported["long"]), len(METRICS["QB"]))


if __name__ == "__main__":
    unittest.main()
