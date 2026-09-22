import unittest
from pathlib import Path

from scripts.build_rb_fable_01_metric_layer import render_sql
from scripts.run_rb_fable_v12_backtest import evaluate_variant


ROOT = Path(__file__).resolve().parents[1]
SQL = (ROOT / "bigquery" / "views" / "v_rb_fable_v12_backtest_prep.sql").read_text()


class RbFableV12Test(unittest.TestCase):
    def test_sql_renders_and_uses_only_preseason_role_inputs(self):
        rendered = render_sql(
            ROOT / "bigquery" / "views" / "v_rb_fable_v12_backtest_prep.sql",
            "project",
            "advanced",
            "brain",
        )
        self.assertNotIn("{{", rendered)
        self.assertIn("week = 1", SQL)
        self.assertIn("target_season - 1", SQL)
        self.assertIn("season BETWEEN 2022 AND 2024", SQL)
        self.assertNotIn("2026", SQL)
        self.assertNotIn("sleeper", SQL.lower())
        self.assertNotIn("depth_chart", SQL.lower())

    def test_variants_are_separate_from_champion_score(self):
        self.assertIn("rb_fable_01_score + 0.03", SQL)
        self.assertIn("rb_fable_01_score + 0.05", SQL)
        self.assertIn("rb_fable_01_score + 0.08", SQL)
        self.assertIn("preseason_room_touch_share - source_room_touch_share", SQL)
        self.assertIn("rb_fable_01_score + 0.20 * projected_room_share_change", SQL)
        self.assertNotIn("CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_rb_fable_01", SQL)

    def test_variant_evaluator_aliases_score(self):
        rows = []
        for season in (2022, 2023, 2024):
            for rank in range(1, 41):
                rows.append({
                    "season": season,
                    "candidate_internal_player_id": f"{season}-{rank}",
                    "player_name": f"P{rank:02}",
                    "challenger": float(41 - rank),
                    "target_standard_ppg": float(41 - rank),
                    "target_standard_points": float((41 - rank) * 10),
                    "standard_receptions": 0.0,
                    "target_share": 0.0,
                })
        result = evaluate_variant(rows, "challenger")
        self.assertEqual(result["aggregate"]["average_top_12_hit_rate"], 1.0)
        self.assertEqual(result["aggregate"]["total_elite_misses"], 0)


if __name__ == "__main__":
    unittest.main()
