import unittest
from datetime import datetime, timedelta, timezone

from src import generate_pigskin_rankings as gpr


class FakeJob:
    def __init__(self, row):
        self._row = row

    def result(self):
        return iter([self._row])


class Row:
    def __init__(self, latest, n):
        self.latest = latest
        self.n = n


class FakeClient:
    project = "test-project"

    def __init__(self, latest, n=100):
        self._row = Row(latest, n)
        self.queries = 0

    def query(self, sql, job_config=None):
        self.queries += 1
        return FakeJob(self._row)


class RequireCurrentSleeperPoolTest(unittest.TestCase):
    def test_passes_when_snapshot_is_today(self):
        today = datetime.now(timezone.utc).date()
        # No exception is the pass condition.
        gpr.require_current_sleeper_pool(FakeClient(latest=today), "d")

    def test_raises_when_snapshot_is_stale(self):
        yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
        with self.assertRaisesRegex(RuntimeError, "stale"):
            gpr.require_current_sleeper_pool(FakeClient(latest=yesterday), "d")

    def test_raises_when_snapshot_is_empty(self):
        with self.assertRaisesRegex(RuntimeError, "empty"):
            gpr.require_current_sleeper_pool(FakeClient(latest=None, n=0), "d")

    def test_stale_downgrades_to_warning_in_dry_run(self):
        yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
        # allow_stale should swallow the failure so a dry run can proceed.
        gpr.require_current_sleeper_pool(FakeClient(latest=yesterday), "d", allow_stale=True)

    def test_empty_downgrades_to_warning_in_dry_run(self):
        gpr.require_current_sleeper_pool(FakeClient(latest=None, n=0), "d", allow_stale=True)


if __name__ == "__main__":
    unittest.main()
