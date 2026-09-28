from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from src import materialize_role_context as role_context


class MaterializeRoleContextTests(unittest.TestCase):
    def test_dry_run_does_not_require_gate(self):
        with patch.dict(os.environ, {role_context.WRITE_GATE: ""}, clear=False):
            code = role_context.main(["--season-start", "2014", "--season-end", "2025", "--dry-run"])

        self.assertEqual(code, 0)

    def test_write_without_gate_fails_closed(self):
        with patch.dict(os.environ, {role_context.WRITE_GATE: ""}, clear=False):
            code = role_context.main(["--season-start", "2014", "--season-end", "2025", "--write"])

        self.assertEqual(code, 2)

    def test_sql_uses_injury_source_and_keeps_depth_unavailable(self):
        sql = role_context.build_role_context_sql("project", "dataset")

        self.assertIn("raw_nflverse_injuries", sql)
        self.assertIn("raw_nflverse_depth_charts", sql)
        self.assertIn("COALESCE(identity_bridge.player_id_internal, CONCAT('gsis:', injury_source.gsis_id))", sql)
        self.assertIn("injury_status_score", sql)
        self.assertIn("injury_burden_score", sql)
        self.assertIn("missed_time_risk_score", sql)
        self.assertIn("availability_score", sql)
        self.assertIn("identity_mapping_method", sql)
        self.assertIn("identity_mapping_confidence", sql)
        self.assertIn("using_exact_gsis_fallback_identity", sql)
        self.assertIn("CAST(NULL AS FLOAT64) AS depth_chart_role_score", sql)
        self.assertIn("historical_depth_chart_context_unavailable", sql)
        self.assertNotIn("analytics_pigskin_rankings", sql)
        self.assertNotIn("ranking_formula_champions", sql)


if __name__ == "__main__":
    unittest.main()
