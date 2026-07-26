import unittest
from datetime import date
from unittest.mock import patch

from src import ingest_news


class _SentinelCalled(Exception):
    """Raised by the patched fetch so a test can prove the guard let it through."""


class FakeJob:
    def __init__(self, n):
        self._n = n

    def result(self):
        return iter([type("Row", (), {"n": self._n})()])


class FakeClient:
    project = "test-project"

    def __init__(self, count=0, raise_on_query=None):
        self.count = count
        self.raise_on_query = raise_on_query
        self.queries = 0

    def query(self, sql, job_config=None):
        self.queries += 1
        if self.raise_on_query:
            raise self.raise_on_query
        return FakeJob(self.count)


class SnapshotExistsTodayTest(unittest.TestCase):
    def test_true_when_rows_present(self):
        self.assertTrue(ingest_news._snapshot_exists_today(FakeClient(count=1500), date(2026, 9, 10)))

    def test_false_when_empty(self):
        self.assertFalse(ingest_news._snapshot_exists_today(FakeClient(count=0), date(2026, 9, 10)))

    def test_false_when_table_missing(self):
        # First run after the migration: the query errors, and we proceed.
        client = FakeClient(raise_on_query=RuntimeError("Not found: Table"))
        self.assertFalse(ingest_news._snapshot_exists_today(client, date(2026, 9, 10)))


class OncePerDayGuardTest(unittest.TestCase):
    def test_skips_when_snapshot_exists(self):
        client = FakeClient(count=2000)
        with patch.object(ingest_news, "sleeper_get", side_effect=_SentinelCalled):
            # No exception means the players endpoint was never hit.
            self.assertIsNone(ingest_news.load_realtime_news(client=client))

    def test_proceeds_when_no_snapshot(self):
        client = FakeClient(count=0)
        with patch.object(ingest_news, "sleeper_get", side_effect=_SentinelCalled):
            with self.assertRaises(_SentinelCalled):
                ingest_news.load_realtime_news(client=client)

    def test_force_overrides_existing_snapshot(self):
        client = FakeClient(count=2000)
        with patch.object(ingest_news, "sleeper_get", side_effect=_SentinelCalled):
            with self.assertRaises(_SentinelCalled):
                ingest_news.load_realtime_news(client=client, force=True)


class EndpointTest(unittest.TestCase):
    def test_players_endpoint_filters_active(self):
        # Sleeper's active=true returns only active players and a smaller payload.
        self.assertIn("active=true", ingest_news.PLAYERS_ENDPOINT)
        self.assertTrue(ingest_news.PLAYERS_ENDPOINT.endswith("/players/nfl?active=true"))


if __name__ == "__main__":
    unittest.main()
