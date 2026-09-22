import unittest
import pandas as pd
from scripts.inseason_rankings import choose_models, predicted_rate, PROFILES, remaining_team_schedule


class InseasonRankingsTests(unittest.TestCase):
    def test_team_aliases_cannot_create_false_byes(self):
        schedule=pd.DataFrame([dict(home_team='LA',away_team='WAS',week=3),dict(home_team='JAX',away_team='LA',week=4)])
        self.assertEqual(list(remaining_team_schedule(schedule,'LAR',2).week),[3,4])
        self.assertEqual(list(remaining_team_schedule(schedule,'WSH',2).week),[3])
        self.assertEqual(list(remaining_team_schedule(schedule,'JAC',2).week),[4])
        with self.assertRaises(ValueError):remaining_team_schedule(schedule,'UNKNOWN',2)

    def test_observations_and_prior_blend(self):
        self.assertEqual(predicted_rate(30, 2, 10, 2), 12.5)
        self.assertEqual(predicted_rate(30, 2, 10, 0), 15)
        self.assertEqual(predicted_rate(30, 2, 10, 1000000), 10)
        self.assertEqual(predicted_rate(0, 0, 10, 0), 10)

    def test_holdout_does_not_choose_parameter(self):
        rows=[]
        for profile in PROFILES:
            for horizon in ('weekly','ros'):
                for k,train,holdout in [(0,3,1),(2,1,3),(1000000,4,4)]:
                    for split,mae in [('train_2016_2024',train),('holdout_2025',holdout)]:
                        rows.append(dict(profile=profile,horizon=horizon,k=k,split=split,mae=mae))
        selected=choose_models(rows)
        self.assertEqual(selected['ppr']['weekly']['k'],2)
        self.assertFalse(selected['ppr']['weekly']['validated'])
