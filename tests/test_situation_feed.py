import json
import unittest
from pathlib import Path

from src import situation_feed as sf


def _row(**overrides):
    row = {
        "gsis_id": "00-0031111", "sleeper_player_id": "5859", "player_name": "D.J. Moore",
        "position": "WR", "stats_season": 2025, "team_from": "CHI", "team_to": "BUF",
        "team_changed": True, "qb_from": "Caleb Williams", "qb_to": "Josh Allen",
        "qb_quality_from": 19.42, "qb_quality_to": 24.29, "qb_quality_delta": 4.87,
        "qb_changed": True, "age_at_season": 29.4, "head_coach": "Joe Brady",
        "offensive_coordinator": "Pete Carmichael", "hc_changed": True, "oc_changed": None,
        "flags_json": '["NEW_TEAM","QB_CHANGED","QB_UPGRADE_MAJOR","NEW_HC"]',
        "metric_basis": "2025_CHI", "games_prev": 17, "ppg_prev": 7.19,
        "games_2025": 17, "std_ppg_2025": 7.19, "ppr_ppg_2025": 10.13, "gng_ppg_2025": 5.15,
        "gng_ppg_prev": 5.15, "qb_quality_from_gng": 15.2, "qb_quality_to_gng": 19.33,
        "qb_quality_delta_gng": 4.13,
        "targets_per_game": 5.0, "target_share_pct": 16.1, "wopr": 0.381,
        "carries_per_game": 0.88, "red_zone_touches_per_game": 0.76,
        "touchdowns_2025": 8, "epa_per_opportunity": 0.062,
        "opportunity_score": None, "efficiency_score": None, "passing_epa_per_week": None,
    }
    row.update(overrides)
    return row


class PlayerEntryTest(unittest.TestCase):
    def test_situation_shape(self):
        entry = sf.player_entry(_row())
        s = entry["situation"]
        self.assertEqual((s["team_2025"], s["team"]), ("CHI", "BUF"))
        # GNG parity: both scoring scales ride together.
        self.assertAlmostEqual(s["qb_quality_delta_gng_ppg"], 4.13)
        self.assertAlmostEqual(entry["metrics"]["gng_ppg"], 5.15)
        self.assertTrue(s["team_changed"] and s["qb_changed"] and s["hc_changed"])
        self.assertEqual(s["metric_basis"], "2025_CHI")
        self.assertIn("NEW_HC", s["flags"])
        self.assertAlmostEqual(s["qb_quality_delta_ppg"], 4.87)

    def test_metrics_drop_nulls(self):
        entry = sf.player_entry(_row())
        self.assertNotIn("opportunity_score", entry["metrics"])
        self.assertEqual(entry["metrics"]["target_share_pct"], 16.1)

    def test_bad_flags_json_degrades_to_empty(self):
        entry = sf.player_entry(_row(flags_json="{broken"))
        self.assertEqual(entry["situation"]["flags"], [])


class BuildDatasetTest(unittest.TestCase):
    def test_counts(self):
        rows = [_row(), _row(gsis_id="x", team_changed=False, flags_json="[]")]
        ds = sf.build_dataset(rows, source_generated_at="t")
        self.assertEqual(ds["player_count"], 2)
        self.assertEqual(ds["team_changed_count"], 1)
        self.assertEqual(ds["flagged_count"], 1)

    def test_content_addressing_is_stable(self):
        from src.coaching_staff import canonical_json_bytes, sha256_hex

        ds = sf.build_dataset([_row()], source_generated_at="fixed")
        self.assertEqual(
            sha256_hex(canonical_json_bytes(ds)), sha256_hex(canonical_json_bytes(ds))
        )


class ArtifactTest(unittest.TestCase):
    def test_shipped_artifact_matches_its_digest(self):
        # The artifact the wrapper uploads must be self-consistent.
        from src.coaching_staff import sha256_hex

        feeds = Path(__file__).resolve().parents[1] / "build" / "feeds"
        obj, entry = feeds / "player_situation.json", feeds / "player_situation.manifest-entry.json"
        if not (obj.exists() and entry.exists()):
            self.skipTest("feed artifacts not built in this checkout")
        meta = json.loads(entry.read_text(encoding="utf-8"))
        self.assertEqual(meta["sha256"], sha256_hex(obj.read_bytes()))
        self.assertIn(meta["sha256"], meta["object"])


class JobWiringTest(unittest.TestCase):
    def test_jobs_registered(self):
        from src.job_runner import JOB_DISPATCHERS, VALID_JOB_NAMES

        self.assertIn("situation-feed", VALID_JOB_NAMES)
        self.assertIn("situation-feed", JOB_DISPATCHERS)

    def test_history_season_routes(self):
        from src.job_runner import dispatch_ingest_coaching_staff, parse_args

        args = parse_args(["--job-name", "ingest-coaching-staff", "--history-season", "2025", "--dry-run"])
        result = dispatch_ingest_coaching_staff(args, None)
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["season"], 2025)
        self.assertTrue(result["csv"].endswith("coaching_staff_2025.csv"))


if __name__ == "__main__":
    unittest.main()
