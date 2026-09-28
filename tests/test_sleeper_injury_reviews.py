from __future__ import annotations

from datetime import datetime, timezone
import unittest

from src.sleeper_injury_reviews import build_injury_review_events


class SleeperInjuryReviewTests(unittest.TestCase):
    def test_new_out_status_creates_a_pending_no_rank_change_review(self):
        events = build_injury_review_events(
            {"123": "Questionable"},
            [{
                "sleeper_player_id": "123",
                "player_name": "Example Player",
                "team": "ATL",
                "position": "WR",
                "injury_status": "OUT",
            }],
            datetime(2026, 7, 10, 14, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["previous_injury_status"], "QUESTIONABLE")
        self.assertEqual(events[0]["review_status"], "PENDING")
        self.assertTrue(events[0]["requires_pigskin_investigation"])
        self.assertEqual(events[0]["ranking_action"], "NO_AUTOMATIC_RANK_CHANGE")

    def test_questionable_status_does_not_create_a_review(self):
        events = build_injury_review_events(
            {"123": ""},
            [{"sleeper_player_id": "123", "injury_status": "Questionable"}],
            datetime(2026, 7, 10, 14, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(events, [])

    def test_unchanged_ir_status_does_not_duplicate_a_review(self):
        events = build_injury_review_events(
            {"123": "IR"},
            [{"sleeper_player_id": "123", "injury_status": "IR"}],
            datetime(2026, 7, 10, 14, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(events, [])


if __name__ == "__main__":
    unittest.main()
