import unittest

from src.gng_sleeper_safety import is_owner_approved_injured_starter
from src.ranking_owner_decisions import GNG_INJURED_STARTER_HARD_REVIEW_DECISIONS


def caleb(**overrides):
    row = {
        "position": "QB",
        "player_name": "Caleb Williams",
        "sleeper_active": True,
        "sleeper_status": "Active",
        "sleeper_team": "CHI",
        "sleeper_injury_status": "Out",
        "sleeper_depth_chart_order": 3,
        "sleeper_review_flags_json": '["QB_BACKUP_ROLE_REVIEW","INJURY_UNCERTAIN"]',
    }
    row.update(overrides)
    return row


class InjuredStarterHardReviewTest(unittest.TestCase):
    def approved(self, row):
        return is_owner_approved_injured_starter(row, GNG_INJURED_STARTER_HARD_REVIEW_DECISIONS)

    def test_injured_starter_depth_drop_is_approved(self):
        self.assertTrue(self.approved(caleb()))
        self.assertTrue(self.approved(caleb(sleeper_injury_status="Questionable", sleeper_depth_chart_order=2)))

    def test_exception_expires_outside_its_bounds(self):
        self.assertFalse(self.approved(caleb(sleeper_injury_status=None)), "healthy backup is a real review")
        self.assertFalse(self.approved(caleb(sleeper_injury_status="IR")))
        self.assertFalse(self.approved(caleb(sleeper_team="NYJ")))
        self.assertFalse(self.approved(caleb(sleeper_depth_chart_order=4)))
        self.assertFalse(self.approved(caleb(sleeper_depth_chart_order=1)))
        self.assertFalse(self.approved(caleb(sleeper_status="Inactive")))
        self.assertFalse(self.approved(caleb(sleeper_active=False)))
        self.assertFalse(self.approved(caleb(sleeper_review_flags_json='["QB_BACKUP_ROLE_REVIEW","INJURY_UNCERTAIN","SLEEPER_ROSTER_REVIEW"]')))
        self.assertFalse(self.approved(caleb(sleeper_review_flags_json="not json")))

    def test_other_players_are_not_covered(self):
        self.assertFalse(self.approved(caleb(player_name="Tyson Bagent")))
        self.assertFalse(self.approved(caleb(position="WR")))


if __name__ == "__main__":
    unittest.main()
