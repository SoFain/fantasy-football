import unittest

from scripts.inseason_gng_scoring import FIELDS, pbp_supplements, score_game


class GngScoringTest(unittest.TestCase):
    def row(self, **kwargs):
        return {**{field: 0 for field in FIELDS.values()}, 'position': 'QB', 'completions': 0, 'carries': 0, **kwargs}

    def test_yardage_tiers_do_not_stack(self):
        points, detail = score_game(self.row(passing_yards=400), {})
        self.assertEqual(points, 10)
        self.assertEqual(detail['bonus_pass_yd_300'], 0)
        self.assertEqual(detail['bonus_pass_yd_400'], 2)

    def test_returns_and_position_receptions(self):
        points, _ = score_game(self.row(position='WR', receptions=5, kickoff_return_yards=60, punt_return_yards=20), {})
        self.assertEqual(points, 6)

    def test_pick_six_stacks(self):
        points, _ = score_game(self.row(passing_interceptions=1), {'pass_int_td': 1})
        self.assertEqual(points, -6)

    def test_touchdown_not_awarded_first_down_bonus(self):
        points, detail = score_game(self.row(rushing_tds=1, rushing_first_downs=2), {})
        self.assertEqual(detail['rush_fd'], .1)
        self.assertEqual(points, 6.1)

    def test_missing_input_fails(self):
        with self.assertRaises(ValueError):
            score_game(self.row(kickoff_return_yards=None), {})

    def test_long_touchdown_and_nullified_play(self):
        play = {'game_id': 'game', 'pass_touchdown': 1, 'passing_yards': 55, 'receiving_yards': 55, 'passer_player_id': 'qb', 'receiver_player_id': 'wr'}
        data, flags = pbp_supplements([play, {**play, 'play_type': 'no_play'}])
        self.assertEqual(data[('game', 'qb')]['pass_td_50p'], 1)
        self.assertEqual(data[('game', 'wr')]['rec_td_50p'], 1)
        self.assertEqual(flags, [])


if __name__ == '__main__':
    unittest.main()
