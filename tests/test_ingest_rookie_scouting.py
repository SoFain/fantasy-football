import unittest
from pathlib import Path

import pandas as pd

from src.ingest_rookie_scouting import (
    REQUIRED_COLUMNS,
    SCHEMA,
    prepare_rookie_scouting_frame,
)

SAMPLE_CSV = Path(__file__).resolve().parents[1] / "data" / "sample_rookie_scouting.csv"


def _row(**overrides):
    row = {
        "season": 2024,
        "player_name": "Test Player",
        "position": "WR",
        "college": "Ohio State",
        "yards_after_contact_per_attempt": 1.0,
        "yards_per_route_run": 2.0,
        "college_target_share": 30.0,
        "catch_radius_grade": 90.0,
        "success_rate_vs_man": 70.0,
        "success_rate_vs_zone": 75.0,
        "success_rate_vs_press": 72.0,
        "avg_separation_inches": 3.0,
        "data_source": "test",
    }
    row.update(overrides)
    return row


class PrepareRookieScoutingFrameTest(unittest.TestCase):
    def test_sample_csv_matches_schema(self):
        # The shipped fixture must load without column mapping.
        out = prepare_rookie_scouting_frame(pd.read_csv(SAMPLE_CSV))
        self.assertEqual(list(out.columns), [field.name for field in SCHEMA])
        self.assertGreater(len(out), 0)

    def test_missing_required_column_raises(self):
        df = pd.DataFrame([_row()]).drop(columns=["player_name"])
        with self.assertRaisesRegex(ValueError, "player_name"):
            prepare_rookie_scouting_frame(df)

    def test_unknown_columns_are_dropped(self):
        df = pd.DataFrame([_row(scouting_notes="ignore me")])
        out = prepare_rookie_scouting_frame(df)
        self.assertNotIn("scouting_notes", out.columns)

    def test_absent_optional_columns_are_filled(self):
        df = pd.DataFrame([_row()]).drop(columns=["college", "avg_separation_inches"])
        out = prepare_rookie_scouting_frame(df)
        self.assertIn("college", out.columns)
        self.assertTrue(pd.isna(out.iloc[0]["avg_separation_inches"]))

    def test_non_numeric_season_raises(self):
        df = pd.DataFrame([_row(season="rookie year")])
        with self.assertRaisesRegex(ValueError, "non-numeric season"):
            prepare_rookie_scouting_frame(df)

    def test_blank_player_name_raises(self):
        df = pd.DataFrame([_row(player_name="   ")])
        with self.assertRaisesRegex(ValueError, "empty player_name"):
            prepare_rookie_scouting_frame(df)

    def test_numeric_strings_are_coerced(self):
        df = pd.DataFrame([_row(season="2024", yards_per_route_run="3.5")])
        out = prepare_rookie_scouting_frame(df)
        self.assertEqual(int(out.iloc[0]["season"]), 2024)
        self.assertAlmostEqual(out.iloc[0]["yards_per_route_run"], 3.5)

    def test_unparseable_float_becomes_null_not_error(self):
        # A bad optional metric should not fail the whole load.
        df = pd.DataFrame([_row(catch_radius_grade="n/a")])
        out = prepare_rookie_scouting_frame(df)
        self.assertTrue(pd.isna(out.iloc[0]["catch_radius_grade"]))

    def test_player_name_is_stripped(self):
        df = pd.DataFrame([_row(player_name="  Marvin Harrison Jr.  ")])
        out = prepare_rookie_scouting_frame(df)
        self.assertEqual(out.iloc[0]["player_name"], "Marvin Harrison Jr.")

    def test_required_columns_match_schema(self):
        self.assertEqual(set(REQUIRED_COLUMNS), {"season", "player_name"})


class JobRunnerWiringTest(unittest.TestCase):
    def test_job_is_registered(self):
        from src.job_runner import JOB_DISPATCHERS, VALID_JOB_NAMES

        self.assertIn("ingest-rookie-scouting", VALID_JOB_NAMES)
        self.assertIn("ingest-rookie-scouting", JOB_DISPATCHERS)

    def test_dry_run_does_not_touch_bigquery(self):
        from src.job_runner import dispatch_ingest_rookie_scouting, parse_args

        args = parse_args(["--job-name", "ingest-rookie-scouting", "--dry-run"])
        result = dispatch_ingest_rookie_scouting(args, None)
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["row_count"], 0)
        self.assertTrue(result["csv"].endswith("sample_rookie_scouting.csv"))


if __name__ == "__main__":
    unittest.main()
