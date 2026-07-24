import unittest
from datetime import datetime, timezone

from src import detect_player_changes as dpc
from src.team_news_feeds import TEAM_FEEDS

FETCHED = datetime(2026, 9, 10, 11, 0, tzinfo=timezone.utc)

ATOM = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>James Cook limited in practice</title>
    <link href="https://example.com/1"/>
    <summary>Ankle.</summary>
    <published>2026-09-09T18:30:00Z</published>
  </entry>
  <entry>
    <title>Unrelated roster note</title>
    <link href="https://example.com/2"/>
    <summary>Nothing to see.</summary>
    <published>2026-09-09T19:00:00Z</published>
  </entry>
</feed>"""


class FakeResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self, text=ATOM):
        self.text = text
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append(url)
        return FakeResponse(self.text)


def _change(**overrides):
    change = {
        "sleeper_player_id": "1",
        "gsis_id": "00-001",
        "player_name": "James Cook",
        "position": "RB",
        "team": "BUF",
        "previous_team": "BUF",
        "field_name": "injury_status",
        "old_value": None,
        "new_value": "Questionable",
        "triggers_news_check": True,
    }
    change.update(overrides)
    return change


class CollectTeamNewsTest(unittest.TestCase):
    def test_fetches_only_affected_teams(self):
        session = FakeSession()
        dpc.collect_team_news([_change()], fetched_at=FETCHED, session=session)
        self.assertEqual(session.calls, [TEAM_FEEDS["BUF"]])

    def test_one_request_per_team_not_per_player(self):
        session = FakeSession()
        changes = [_change(sleeper_player_id=str(i), player_name=f"Player {i}") for i in range(6)]
        dpc.collect_team_news(changes, fetched_at=FETCHED, session=session)
        self.assertEqual(len(session.calls), 1)

    def test_team_change_fetches_both_teams(self):
        session = FakeSession()
        dpc.collect_team_news(
            [_change(field_name="team", team="KC", previous_team="BUF")],
            fetched_at=FETCHED, session=session,
        )
        self.assertEqual(sorted(session.calls), sorted([TEAM_FEEDS["BUF"], TEAM_FEEDS["KC"]]))

    def test_no_triggering_changes_makes_no_requests(self):
        session = FakeSession()
        news, matches = dpc.collect_team_news(
            [_change(triggers_news_check=False)], fetched_at=FETCHED, session=session
        )
        self.assertEqual(session.calls, [])
        self.assertEqual((news, matches), ([], []))

    def test_matches_carry_the_trigger_that_caused_the_fetch(self):
        news, matches = dpc.collect_team_news(
            [_change()], fetched_at=FETCHED, session=FakeSession()
        )
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["trigger_field"], "injury_status")
        self.assertEqual(matches[0]["trigger_new_value"], "Questionable")
        self.assertEqual(matches[0]["player_name"], "James Cook")

    def test_unmatched_items_still_recorded_with_zero_matches(self):
        news, _ = dpc.collect_team_news([_change()], fetched_at=FETCHED, session=FakeSession())
        self.assertEqual(len(news), 2)
        self.assertEqual(sorted(n["matched_player_count"] for n in news), [0, 1])

    def test_timestamps_serialized_for_load_job(self):
        news, matches = dpc.collect_team_news(
            [_change()], fetched_at=FETCHED, session=FakeSession()
        )
        self.assertIsInstance(news[0]["fetched_at"], str)
        self.assertIsInstance(matches[0]["fetched_at"], str)


class FakeQueryJob:
    def __init__(self, rows):
        self._rows = rows

    def result(self):
        return self._rows


class FakeLoadJob:
    def result(self):
        return None


class FakeClient:
    project = "test-project"

    def __init__(self, snapshots, rows_by_snapshot):
        self.snapshots = snapshots
        self.rows_by_snapshot = rows_by_snapshot
        self.loaded = {}

    def query(self, sql, job_config=None):
        if "DISTINCT snapshot_at" in sql:
            return FakeQueryJob([{"snapshot_at": s} for s in self.snapshots])
        wanted = job_config.query_parameters[0].value
        return FakeQueryJob(self.rows_by_snapshot[wanted])

    def load_table_from_json(self, rows, table_id, job_config=None):
        self.loaded.setdefault(table_id.split(".")[-1], []).extend(rows)
        return FakeLoadJob()


def _snapshot_row(**overrides):
    row = {
        "snapshot_at": None,
        "sleeper_player_id": "1",
        "gsis_id": "00-001",
        "player_name": "James Cook",
        "position": "RB",
        "team": "BUF",
        "status": "Active",
        "injury_status": None,
        "depth_chart_position": "RB",
        "depth_chart_order": 1,
        "active": True,
    }
    row.update(overrides)
    return row


class DetectPlayerChangesTest(unittest.TestCase):
    def _client(self, current_overrides):
        older = datetime(2026, 9, 9, 11, 0, tzinfo=timezone.utc)
        newer = datetime(2026, 9, 10, 11, 0, tzinfo=timezone.utc)
        return FakeClient(
            snapshots=[newer, older],
            rows_by_snapshot={
                older: [_snapshot_row(snapshot_at=older)],
                newer: [_snapshot_row(snapshot_at=newer, **current_overrides)],
            },
        )

    def test_requires_two_snapshots(self):
        client = FakeClient(snapshots=[datetime.now(timezone.utc)], rows_by_snapshot={})
        result = dpc.detect_player_changes(client=client, fetch_news=False)
        self.assertEqual(result["reason"], "insufficient_history")
        self.assertEqual(result["change_count"], 0)

    def test_writes_changes(self):
        client = self._client({"injury_status": "Questionable"})
        result = dpc.detect_player_changes(client=client, fetch_news=False)
        self.assertEqual(result["change_count"], 1)
        self.assertEqual(len(client.loaded["player_status_changes"]), 1)

    def test_dry_run_writes_nothing(self):
        client = self._client({"injury_status": "Questionable"})
        result = dpc.detect_player_changes(client=client, dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertEqual(client.loaded, {})

    def test_skip_news_records_changes_without_fetching(self):
        client = self._client({"injury_status": "Questionable"})
        dpc.detect_player_changes(client=client, fetch_news=False)
        self.assertNotIn("team_news_items", client.loaded)

    def test_reports_teams_to_check(self):
        client = self._client({"team": "KC"})
        result = dpc.detect_player_changes(client=client, fetch_news=False)
        self.assertEqual(result["teams_to_check"], ["BUF", "KC"])

    def test_no_changes_writes_nothing(self):
        client = self._client({})
        result = dpc.detect_player_changes(client=client, fetch_news=False)
        self.assertEqual(result["change_count"], 0)
        self.assertEqual(client.loaded, {})


class JobWiringTest(unittest.TestCase):
    def test_job_registered(self):
        from src.job_runner import JOB_DISPATCHERS, VALID_JOB_NAMES

        self.assertIn("detect-player-changes", VALID_JOB_NAMES)
        self.assertIn("detect-player-changes", JOB_DISPATCHERS)

    def test_skip_news_flag_parses(self):
        from src.job_runner import parse_args

        args = parse_args(["--job-name", "detect-player-changes", "--skip-news"])
        self.assertTrue(args.skip_news)


if __name__ == "__main__":
    unittest.main()
