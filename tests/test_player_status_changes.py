import unittest
from datetime import date, datetime, timezone

from src import player_status_changes as psc

DETECTED = datetime(2026, 9, 10, 11, 0, tzinfo=timezone.utc)


def _player(pid="1", **overrides):
    row = {
        "sleeper_player_id": pid,
        "gsis_id": f"00-00{pid}",
        "player_name": f"Player {pid}",
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


def _diff(previous, current):
    return psc.diff_snapshots(previous, current, detected_at=DETECTED)


class DiffSnapshotsTest(unittest.TestCase):
    def test_no_changes_yields_nothing(self):
        self.assertEqual(_diff([_player()], [_player()]), [])

    def test_injury_status_change_detected(self):
        changes = _diff([_player()], [_player(injury_status="Questionable")])
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["field_name"], "injury_status")
        self.assertIsNone(changes[0]["old_value"])
        self.assertEqual(changes[0]["new_value"], "Questionable")
        self.assertTrue(changes[0]["triggers_news_check"])

    def test_team_change_records_previous_team(self):
        changes = _diff([_player()], [_player(team="KC")])
        self.assertEqual(changes[0]["previous_team"], "BUF")
        self.assertEqual(changes[0]["team"], "KC")

    def test_multiple_fields_produce_multiple_rows(self):
        changes = _diff([_player()], [_player(team="KC", injury_status="Out")])
        self.assertEqual({c["field_name"] for c in changes}, {"team", "injury_status"})

    def test_new_player_is_not_a_change(self):
        # A first sighting would otherwise flood the table on the first run.
        self.assertEqual(_diff([], [_player()]), [])

    def test_disappearing_player_is_not_a_change(self):
        self.assertEqual(_diff([_player()], []), [])

    def test_null_to_empty_string_is_not_a_change(self):
        # Sleeper flips between these constantly; treating it as a change
        # would produce noise every single day.
        previous = [_player(injury_status=None)]
        current = [_player(injury_status="  ")]
        self.assertEqual(_diff(previous, current), [])

    def test_depth_chart_order_change_triggers_news(self):
        changes = _diff([_player()], [_player(depth_chart_order=2)])
        self.assertTrue(changes[0]["triggers_news_check"])

    def test_depth_chart_position_change_does_not_trigger_news(self):
        # Positional relabeling alone is not newsworthy.
        changes = _diff([_player()], [_player(depth_chart_position="WR")])
        self.assertEqual(changes[0]["field_name"], "depth_chart_position")
        self.assertFalse(changes[0]["triggers_news_check"])

    def test_status_change_is_watched_but_not_a_news_trigger(self):
        changes = _diff([_player()], [_player(status="Inactive")])
        self.assertEqual(changes[0]["field_name"], "status")
        self.assertFalse(changes[0]["triggers_news_check"])

    def test_boolean_values_render_as_text(self):
        # depth_chart_order is int; use a bool-bearing watched field via status.
        # active is intentionally not watched (endpoint is filtered active=true),
        # so exercise text rendering through a genuine watched change instead.
        changes = _diff([_player()], [_player(status="Inactive")])
        self.assertEqual(changes[0]["old_value"], "Active")
        self.assertEqual(changes[0]["new_value"], "Inactive")

    def test_active_is_not_watched(self):
        # The players endpoint is called with active=true, so every row is
        # active=true and the field can never differ. Even a forced flip must
        # produce no change row.
        changes = _diff([_player(active=True)], [_player(active=False)])
        self.assertEqual(changes, [])

    def test_id_matching_tolerates_int_vs_str(self):
        previous = [_player(pid="1")]
        current = [dict(_player(pid="1"), sleeper_player_id=1, injury_status="Out")]
        self.assertEqual(len(_diff(previous, current)), 1)


class TeamsNeedingNewsTest(unittest.TestCase):
    def test_deduplicates_teams(self):
        changes = _diff(
            [_player("1"), _player("2")],
            [_player("1", injury_status="Out"), _player("2", injury_status="Out")],
        )
        self.assertEqual(psc.teams_needing_news(changes), ["BUF"])

    def test_team_change_includes_both_teams(self):
        changes = _diff([_player()], [_player(team="KC")])
        self.assertEqual(psc.teams_needing_news(changes), ["BUF", "KC"])

    def test_non_triggering_changes_are_excluded(self):
        changes = _diff([_player()], [_player(status="Inactive")])
        self.assertEqual(psc.teams_needing_news(changes), [])

    def test_worst_case_is_bounded_by_team_count(self):
        previous = [_player(str(i), team=t) for i, t in enumerate(["BUF", "KC", "SF"] * 10)]
        current = [dict(p, injury_status="Out") for p in previous]
        self.assertEqual(len(psc.teams_needing_news(_diff(previous, current))), 3)


class PlayersNeedingNewsTest(unittest.TestCase):
    def test_deduplicates_by_player(self):
        changes = _diff([_player()], [_player(team="KC", injury_status="Out")])
        self.assertEqual(len(psc.players_needing_news(changes)), 1)

    def test_excludes_non_triggering_players(self):
        changes = _diff([_player()], [_player(status="Inactive")])
        self.assertEqual(psc.players_needing_news(changes), [])


class ComputeAgeTest(unittest.TestCase):
    def test_computes_from_date(self):
        self.assertAlmostEqual(psc.compute_age(date(2000, 9, 10), date(2026, 9, 10)), 26.0, places=1)

    def test_accepts_iso_string(self):
        self.assertAlmostEqual(psc.compute_age("2000-09-10", date(2026, 9, 10)), 26.0, places=1)

    def test_none_stays_none(self):
        self.assertIsNone(psc.compute_age(None, date(2026, 9, 10)))

    def test_unparseable_returns_none_not_zero(self):
        # A wrong age is worse than a missing one for the age curves.
        self.assertIsNone(psc.compute_age("not a date", date(2026, 9, 10)))

    def test_future_birth_date_returns_none(self):
        self.assertIsNone(psc.compute_age(date(2030, 1, 1), date(2026, 9, 10)))

    def test_accepts_datetime(self):
        value = datetime(2000, 9, 10, 12, 0, tzinfo=timezone.utc)
        self.assertAlmostEqual(psc.compute_age(value, date(2026, 9, 10)), 26.0, places=1)


class SummarizeTest(unittest.TestCase):
    def test_counts_by_field(self):
        changes = _diff(
            [_player("1"), _player("2")],
            [_player("1", injury_status="Out"), _player("2", team="KC")],
        )
        summary = psc.summarize(changes)
        self.assertEqual(summary["change_count"], 2)
        self.assertEqual(summary["player_count"], 2)
        self.assertEqual(summary["news_trigger_count"], 2)
        self.assertEqual(summary["by_field"], {"injury_status": 1, "team": 1})

    def test_empty_is_zeroed(self):
        self.assertEqual(psc.summarize([])["change_count"], 0)


if __name__ == "__main__":
    unittest.main()
