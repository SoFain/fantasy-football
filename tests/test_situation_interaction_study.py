import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "run_situation_interaction_study",
    Path(__file__).resolve().parents[1] / "scripts" / "run_situation_interaction_study.py",
)
ia = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ia)


def _rows(seasons, per_season=40, interaction=0.3, winpct_effect=0.0):
    """Synthetic transitions with PLANTED effects: movers' QB slope is
    (0.05 + interaction); winpct_delta adds winpct_effect PPG per unit.
    No noise, so OLS must recover the planted values."""
    rows = []
    for season in seasons:
        for i in range(per_season):
            moved = i % 4 == 0
            qb_delta = ((i % 11) - 5) * 1.0  # -5..+5
            winpct_delta = (((i * 7) % 13) - 6) / 20.0 if moved else 0.0  # -0.3..+0.3
            prev = 6.0 + (i % 9)
            nxt = (
                1.0 + 0.8 * prev
                + (-1.0 if moved else 0.0)
                + 0.05 * qb_delta
                + (interaction * qb_delta if moved else 0.0)
                + winpct_effect * winpct_delta
            )
            rows.append({
                "situation_for_season": season, "position": "WR",
                "games_prev": 12 + (i % 5), "age_at_season": 23.0 + (i % 7),
                "team_changed": moved, "qb_changed": moved or qb_delta != 0,
                "ppg_prev": prev, "ppg_next": nxt, "qb_quality_delta": qb_delta,
                "gng_ppg_prev": prev, "gng_ppg_next": nxt, "qb_quality_delta_gng": qb_delta,
                "team_winpct_to": 0.5 + ((i % 5) - 2) / 20.0,
                "winpct_delta": winpct_delta,
            })
    return rows


class WinPctTest(unittest.TestCase):
    def test_build_team_winpct_counts_wins_and_ties(self):
        games = [
            {"season": 2024, "game_type": "REG", "home_team": "BUF", "away_team": "NYJ",
             "home_score": 30, "away_score": 10},
            {"season": 2024, "game_type": "REG", "home_team": "NYJ", "away_team": "BUF",
             "home_score": 20, "away_score": 20},
            {"season": 2024, "game_type": "POST", "home_team": "BUF", "away_team": "NYJ",
             "home_score": 3, "away_score": 40},  # playoffs excluded
        ]
        wp = ia.build_team_winpct(games)
        self.assertAlmostEqual(wp[(2024, "BUF")], 0.75)
        self.assertAlmostEqual(wp[(2024, "NYJ")], 0.25)

    def test_enrich_reports_coverage_and_zeroes_stayers(self):
        winpct = {(2019, "AAA"): 0.8, (2019, "BBB"): 0.3}
        rows = [
            {"situation_for_season": 2020, "team_from": "BBB", "team_to": "AAA", "team_changed": True},
            {"situation_for_season": 2020, "team_from": "AAA", "team_to": "AAA", "team_changed": False},
            {"situation_for_season": 2020, "team_from": "ZZZ", "team_to": "AAA", "team_changed": True},
        ]
        coverage = ia.enrich_with_team_quality(rows, winpct)
        self.assertAlmostEqual(coverage, 2 / 3)
        self.assertAlmostEqual(rows[0]["winpct_delta"], 0.5)
        self.assertEqual(rows[1]["winpct_delta"], 0.0)  # stayer: no delta by construction
        self.assertIsNone(rows[2]["team_winpct_to"])  # unknown origin drops the row


class InteractionRecoveryTest(unittest.TestCase):
    def test_recovers_planted_qb_interaction(self):
        cell = ia.study_cell(_rows(range(2016, 2026)), "WR", "standard")
        c = cell["coefficients"]
        self.assertAlmostEqual(c["team_x_qb"], 0.3, places=2)
        self.assertAlmostEqual(c["qb_delta"], 0.05, places=2)
        self.assertAlmostEqual(cell["mover_qb_slope_interaction"], 0.35, places=2)

    def test_recovers_planted_team_quality_effect(self):
        cell = ia.study_cell(_rows(range(2016, 2026), winpct_effect=2.0), "WR", "standard")
        self.assertAlmostEqual(cell["coefficients"]["winpct_delta"], 2.0, places=1)

    def test_mover_effect_arithmetic(self):
        coef = {"team_changed": -0.8, "qb_delta": 0.02, "team_x_qb": 0.1, "winpct_delta": 1.5}
        self.assertAlmostEqual(ia.mover_effect(coef, 5.0), -0.8 + 0.12 * 5.0)
        self.assertAlmostEqual(ia.mover_effect(coef, 5.0, 0.3), -0.8 + 0.12 * 5.0 + 0.45)

    def test_true_interaction_earns_repin_out_of_sample(self):
        cell = ia.study_cell(_rows(range(2016, 2026)), "WR", "standard")
        self.assertGreaterEqual(cell["n_years"], 4)
        self.assertTrue(cell["earns_repin"])
        self.assertNotEqual(cell["best_model"], "A_additive")

    def test_no_planted_effects_means_no_repin_pressure(self):
        cell = ia.study_cell(_rows(range(2016, 2026), interaction=0.0), "WR", "standard")
        self.assertAlmostEqual(cell["coefficients"]["team_x_qb"], 0.0, places=2)


if __name__ == "__main__":
    unittest.main()
