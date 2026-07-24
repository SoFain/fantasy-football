import json
import unittest
from pathlib import Path

from src import coaching_staff_feed as feed
from src import ingest_coaching_staff as ingest


class FakeLoadJob:
    def result(self):
        return None


class FakeQueryJob:
    def __init__(self, rows):
        self._rows = rows

    def result(self):
        return self._rows


class FakeIngestClient:
    project = "test-project"

    def __init__(self):
        self.loaded = None

    def load_table_from_json(self, rows, table_id, job_config=None):
        self.loaded = (rows, table_id)
        return FakeLoadJob()


class ShippedCsvTest(unittest.TestCase):
    def test_shipped_csv_covers_full_grid(self):
        csv_path = Path(__file__).resolve().parents[1] / "data" / "coaching_staff.csv"
        rows = ingest.read_csv_rows(csv_path)
        # 32 teams x 8 roles, no more no less, and every team/role pair present.
        self.assertEqual(len(rows), 32 * 8)
        pairs = {(r["team_abbr"], r["role"]) for r in rows}
        self.assertEqual(len(pairs), 32 * 8)

    def test_shipped_csv_prepares_cleanly(self):
        csv_path = Path(__file__).resolve().parents[1] / "data" / "coaching_staff.csv"
        from src.coaching_staff import prepare_rows

        prepared = prepare_rows(ingest.read_csv_rows(csv_path), snapshot_at="t", source_url="u")
        self.assertEqual(len(prepared), 256)


class IngestTest(unittest.TestCase):
    def test_loads_full_grid_from_empty_named_csv(self, ):
        client = FakeIngestClient()
        result = ingest.load_coaching_staff(
            Path(__file__).resolve().parents[1] / "data" / "coaching_staff.csv",
            client=client,
        )
        self.assertEqual(result["row_count"], 256)
        # The shipped scaffold has no names yet, so every row is vacant.
        self.assertEqual(result["vacant"], 256)
        rows, table_id = client.loaded
        self.assertTrue(table_id.endswith("coaching_staff_current"))
        self.assertEqual(len(rows), 256)

    def test_missing_csv_raises(self):
        with self.assertRaises(FileNotFoundError):
            ingest.load_coaching_staff("does-not-exist.csv", client=FakeIngestClient())


def _staff_rows():
    return [
        {"team_abbr": "KC", "role": "head_coach", "role_title": "Head Coach", "role_rank": 1,
         "coach_name": "Andy Reid", "is_vacant": False, "verification_status": "verified"},
        {"team_abbr": "KC", "role": "offensive_coordinator", "role_title": "Offensive Coordinator", "role_rank": 3,
         "coach_name": None, "is_vacant": True, "verification_status": "pending"},
    ]


class FakeFeedClient:
    project = "test-project"

    def __init__(self, rows):
        self._rows = rows

    def query(self, sql, job_config=None):
        return FakeQueryJob(self._rows)


class FeedJobTest(unittest.TestCase):
    def _build(self, out_dir):
        import datetime

        return feed.build_coaching_staff_feed(
            out_dir=str(out_dir),
            client=FakeFeedClient(_staff_rows()),
            generated_at=datetime.datetime(2026, 7, 24, tzinfo=datetime.timezone.utc),
        )

    def test_writes_json_object_and_manifest_entry(self):
        out_dir = Path(__file__).resolve().parents[1] / "build" / "feeds" / "test_cs"
        result = self._build(out_dir)
        self.assertEqual(result["row_count"], 2)
        self.assertEqual(result["manifest_entry"]["dataset"], "coaching_staff")
        self.assertFalse(result["published"])  # no --publish, no GCS write

        # The object is valid JSON and content-addressed by its own sha256.
        object_path = Path(result["object_artifact"])
        content = object_path.read_bytes()
        parsed = json.loads(content)
        self.assertEqual(parsed["dataset"], "coaching_staff")
        from src.coaching_staff import sha256_hex

        self.assertEqual(result["sha256"], sha256_hex(content))
        self.assertIn(result["sha256"], result["object"])

        object_path.unlink()
        Path(result["manifest_entry_artifact"]).unlink()

    def test_object_name_is_content_addressed_under_datasets(self):
        out_dir = Path(__file__).resolve().parents[1] / "build" / "feeds" / "test_cs2"
        result = self._build(out_dir)
        self.assertTrue(result["object"].startswith("v1/datasets/coaching_staff/sha256-"))
        Path(result["object_artifact"]).unlink()
        Path(result["manifest_entry_artifact"]).unlink()

    def test_vacant_data_produces_a_warning(self):
        # The fake rows include a vacant OC, so the entry must warn.
        out_dir = Path(__file__).resolve().parents[1] / "build" / "feeds" / "test_cs3"
        result = self._build(out_dir)
        self.assertTrue(result["warnings"])
        Path(result["object_artifact"]).unlink()
        Path(result["manifest_entry_artifact"]).unlink()

    def test_empty_table_raises(self):
        with self.assertRaisesRegex(RuntimeError, "empty"):
            feed.build_coaching_staff_feed(out_dir="x", client=FakeFeedClient([]))


class JobWiringTest(unittest.TestCase):
    def test_jobs_registered(self):
        from src.job_runner import JOB_DISPATCHERS, VALID_JOB_NAMES

        for job in ("ingest-coaching-staff", "coaching-staff-feed"):
            self.assertIn(job, VALID_JOB_NAMES)
            self.assertIn(job, JOB_DISPATCHERS)

    def test_dry_run_ingest_touches_nothing(self):
        from src.job_runner import dispatch_ingest_coaching_staff, parse_args

        args = parse_args(["--job-name", "ingest-coaching-staff", "--dry-run"])
        result = dispatch_ingest_coaching_staff(args, None)
        self.assertTrue(result["dry_run"])
        self.assertTrue(result["csv"].endswith("coaching_staff.csv"))


if __name__ == "__main__":
    unittest.main()
