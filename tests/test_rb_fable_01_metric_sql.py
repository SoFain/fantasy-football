import unittest
from pathlib import Path

from scripts.build_rb_fable_01_metric_layer import VIEW_FILES, render_sql


ROOT = Path(__file__).resolve().parents[1]


class RbFable01MetricSqlTest(unittest.TestCase):
    def test_all_view_templates_render(self):
        for name in VIEW_FILES:
            sql = render_sql(ROOT / "bigquery" / "views" / name, "project", "advanced", "brain")
            self.assertNotIn("{{", sql)
            self.assertIn("project.advanced", sql)

    def test_formula_weights_and_season_local_zscores(self):
        sql = (ROOT / "bigquery" / "views" / "v_rb_fable_01_backtest_prep.sql").read_text()
        inputs_sql = (ROOT / "bigquery" / "views" / "v_rb_fable_01_metric_inputs.sql").read_text()
        for weight in ("0.30", "0.13", "0.12", "0.08", "0.06", "0.05", "0.04", "0.10", "0.03"):
            self.assertIn(weight, sql)
        self.assertIn("PARTITION BY season", sql)
        # Phase 34.4 refinement: volume-conditioned age penalty (elite-volume protection).
        self.assertIn("0.05 * z_age_penalty * (1 - 0.6 * LEAST(GREATEST((z_ngt_tpg - 0.75) / 0.75, 0), 1))", sql)
        self.assertIn("standard_rushes + 125", inputs_sql)
        self.assertIn("standard_touches + 125", inputs_sql)

    def test_no_future_leakage_or_invented_metrics(self):
        sql = "\n".join((ROOT / "bigquery" / "views" / name).read_text().lower() for name in VIEW_FILES)
        self.assertIn("scored.season + 1", sql)
        self.assertIn("season between 2022 and 2024", sql)
        self.assertNotIn("2026", sql)
        self.assertNotIn("broken_tackle", sql)
        self.assertNotIn("yac_above_expectation", sql)
        self.assertNotIn("market_value", sql)

    def test_identity_matches_fail_closed(self):
        sql = (ROOT / "bigquery" / "views" / "situational_identity_bridge_review.sql").read_text()
        self.assertIn("MULTIPLE_CANDIDATES", sql)
        self.assertIn("duplicate_identity_collision", sql)
        self.assertIn("UNMAPPED", sql)


if __name__ == "__main__":
    unittest.main()
