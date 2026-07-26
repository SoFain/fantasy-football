from __future__ import annotations

from pathlib import Path
import re
import unittest

from src import pigskin_context_tools


REPO_ROOT = Path(__file__).resolve().parents[1]
VIEWS_DIR = REPO_ROOT / "bigquery" / "views"
CONTRACTS_DIR = REPO_ROOT / "bigquery" / "contracts"
APP = REPO_ROOT / "app.py"


class PigskinAdvancedMetricsContractTests(unittest.TestCase):
    def test_compatibility_views_do_not_read_raw_or_source_tables(self):
        forbidden = re.compile(
            r"\b(from|join)\s+`?[^`\s]*(raw_nflverse_|play_by_play|weekly_metrics|ngs_|ftn_charting|weekly_snap_counts|injury_reports|depth_charts|source_|raw_)",
            re.IGNORECASE,
        )
        for name in [
            "player_recent_advanced_metrics_current.sql",
            "player_role_usage_metrics_current.sql",
            "compat_pigskin_player_context_current.sql",
        ]:
            path = VIEWS_DIR / name
            self.assertTrue(path.exists(), path)
            sql = path.read_text(encoding="utf-8")
            self.assertNotRegex(sql, forbidden)

    def test_compat_contract_forbids_raw_dependencies(self):
        text = (CONTRACTS_DIR / "compat_pigskin_player_context_current.md").read_text(encoding="utf-8").lower()

        for token in [
            "raw_nflverse_*",
            "play_by_play",
            "weekly_metrics",
            "ngs_*",
            "ftn_charting",
            "weekly_snap_counts",
            "injury_reports",
            "depth_charts",
            "source_*",
            "raw_*",
        ]:
            self.assertIn(token, text)
        self.assertIn("read-only", text)
        self.assertIn("no request-time writes", text)

    def test_pigskin_tool_declarations_do_not_expose_sql(self):
        declarations = pigskin_context_tools.get_pigskin_context_tool_declarations()
        rendered = repr(declarations).lower()

        self.assertNotIn("execute_bigquery_sql", rendered)
        self.assertNotIn("sql_query", rendered)
        self.assertNotIn("raw_nflverse_", rendered)
        self.assertNotIn("weekly_metrics", rendered)
        self.assertNotIn("play_by_play", rendered)

    def test_streamlit_does_not_reference_new_request_time_write_targets(self):
        app_text = APP.read_text(encoding="utf-8").lower()

        self.assertNotIn("insert into `{{project_id}}.{{dataset_id}}.player_week_advanced_metrics", app_text)
        self.assertNotIn("merge `{{project_id}}.{{dataset_id}}.player_week_advanced_metrics", app_text)
        self.assertNotIn("pigskin_player_context_packet_current`", app_text)


if __name__ == "__main__":
    unittest.main()
