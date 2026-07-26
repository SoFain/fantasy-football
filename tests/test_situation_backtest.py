import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "backtest_situation_effects",
    Path(__file__).resolve().parents[1] / "scripts" / "backtest_situation_effects.py",
)
bt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bt)


def _rows(season: int, count: int, movers_every: int = 5) -> list[dict]:
    """Deterministic synthetic transitions: next PPG is a known linear rule."""
    rows = []
    for i in range(count):
        moved = i % movers_every == 0
        prev = 5.0 + (i % 12)
        rows.append({
            "situation_for_season": season, "position": "WR",
            "games_prev": 10 + (i % 7), "age_at_season": 22.0 + (i % 8),
            "team_changed": moved, "qb_changed": moved,
            "ppg_prev": prev, "ppg_next": 1.0 + 0.8 * prev - (1.5 if moved else 0.0),
            "qb_quality_delta": 2.0 if moved else None,
            "gng_ppg_prev": prev, "gng_ppg_next": 0.5 + 0.7 * prev,
            "qb_quality_delta_gng": None,
        })
    return rows


class OlsTest(unittest.TestCase):
    def test_recovers_planted_coefficients(self):
        import numpy as np

        rows = _rows(2019, 60)
        x, y = bt.design(rows, "standard", bt.BASELINE_FEATURES)
        beta = bt.fit(x, y)
        pred = x @ beta
        self.assertLess(float(np.abs(pred - y).max()), 1.6)  # mover shift is the only miss

    def test_spearman_endpoints_and_ties(self):
        import numpy as np

        self.assertAlmostEqual(bt.spearman(np.array([1.0, 2, 3]), np.array([10.0, 20, 30])), 1.0)
        self.assertAlmostEqual(bt.spearman(np.array([1.0, 2, 3]), np.array([30.0, 20, 10])), -1.0)
        self.assertEqual(bt.spearman(np.array([1.0, 1, 1]), np.array([1.0, 2, 3])), 0.0)


class WalkForwardTest(unittest.TestCase):
    def test_temporal_split_counts(self):
        # Train is strictly prior seasons; the holdout year never leaks in.
        rows = []
        for season in (2016, 2017, 2018, 2019):
            rows.extend(_rows(season, 30))
        rows.extend(_rows(2020, 25))

        result = bt.walk_forward(rows, "WR", "standard")
        self.assertEqual([y["season"] for y in result["years"]], [2020])
        self.assertEqual(result["years"][0]["n_train"], 120)
        self.assertEqual(result["years"][0]["n_test"], 25)
        self.assertEqual(result["years"][0]["n_movers"], 5)

    def test_thin_years_are_skipped_not_fabricated(self):
        rows = _rows(2016, 30) + _rows(2020, 25)  # only 30 train rows: below floor
        result = bt.walk_forward(rows, "WR", "standard")
        self.assertEqual(result["years"], [])


if __name__ == "__main__":
    unittest.main()
