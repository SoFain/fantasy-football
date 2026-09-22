import unittest

import pandas as pd

from src.player_comps import COMP_FEATURES, calculate_player_comps


def _player(player_id, position="WR", **features):
    row = {
        "player_id": player_id,
        "player_display_name": f"Player {player_id}",
        "position": position,
        "team": "KC",
        "headshot": None,
    }
    for name in COMP_FEATURES:
        row[name] = features.get(name, 0.0)
    return row


class PlayerCompsTest(unittest.TestCase):
    def test_returns_empty_when_no_other_players_at_position(self):
        target = _player("p1", avg_ppr=10.0)
        df = pd.DataFrame([target])
        self.assertEqual(calculate_player_comps(target, df), [])

    def test_excludes_the_target_player(self):
        target = _player("p1", avg_ppr=10.0)
        df = pd.DataFrame([target, _player("p2", avg_ppr=11.0)])
        comps = calculate_player_comps(target, df)
        self.assertEqual([c["player_id"] for c in comps], ["p2"])

    def test_excludes_other_positions(self):
        target = _player("p1", position="WR", avg_ppr=10.0)
        df = pd.DataFrame([
            target,
            _player("p2", position="WR", avg_ppr=11.0),
            _player("p3", position="RB", avg_ppr=10.0),
        ])
        comps = calculate_player_comps(target, df)
        self.assertEqual([c["player_id"] for c in comps], ["p2"])

    def test_nearest_player_ranks_first(self):
        target = _player("p1", avg_ppr=10.0, avg_grade=90.0)
        df = pd.DataFrame([
            target,
            _player("far", avg_ppr=1.0, avg_grade=10.0),
            _player("near", avg_ppr=9.5, avg_grade=88.0),
        ])
        comps = calculate_player_comps(target, df)
        self.assertEqual(comps[0]["player_id"], "near")
        self.assertGreater(comps[0]["match_pct"], comps[1]["match_pct"])

    def test_identical_player_scores_100(self):
        target = _player("p1", avg_ppr=10.0, avg_grade=90.0)
        twin = _player("twin", avg_ppr=10.0, avg_grade=90.0)
        df = pd.DataFrame([target, twin])
        comps = calculate_player_comps(target, df)
        self.assertAlmostEqual(comps[0]["match_pct"], 100.0, places=6)

    def test_match_pct_stays_within_bounds(self):
        target = _player("p1", avg_ppr=100.0, avg_grade=100.0, avg_snap_share=1.0)
        df = pd.DataFrame([
            target,
            _player("low", avg_ppr=0.0, avg_grade=0.0, avg_snap_share=0.0),
            _player("mid", avg_ppr=50.0, avg_grade=50.0, avg_snap_share=0.5),
        ])
        for comp in calculate_player_comps(target, df):
            self.assertGreaterEqual(comp["match_pct"], 0.0)
            self.assertLessEqual(comp["match_pct"], 100.0)

    def test_respects_limit(self):
        target = _player("p1", avg_ppr=10.0)
        rows = [target] + [_player(f"p{i}", avg_ppr=float(i)) for i in range(2, 12)]
        comps = calculate_player_comps(target, pd.DataFrame(rows), limit=3)
        self.assertEqual(len(comps), 3)

    def test_null_features_are_treated_as_zero(self):
        target = _player("p1", avg_ppr=10.0)
        target["avg_grade"] = None
        other = _player("p2", avg_ppr=10.0)
        other["avg_grade"] = None
        comps = calculate_player_comps(target, pd.DataFrame([target, other]))
        self.assertAlmostEqual(comps[0]["match_pct"], 100.0, places=6)

    def test_constant_feature_contributes_no_distance(self):
        # Every player shares avg_snap_share, so it must not affect ranking.
        target = _player("p1", avg_ppr=10.0, avg_snap_share=0.7)
        df = pd.DataFrame([
            target,
            _player("a", avg_ppr=10.0, avg_snap_share=0.7),
            _player("b", avg_ppr=2.0, avg_snap_share=0.7),
        ])
        comps = calculate_player_comps(target, df)
        self.assertEqual(comps[0]["player_id"], "a")
        self.assertAlmostEqual(comps[0]["match_pct"], 100.0, places=6)

    def test_output_carries_display_columns(self):
        target = _player("p1", avg_ppr=10.0)
        df = pd.DataFrame([target, _player("p2", avg_ppr=9.0)])
        comp = calculate_player_comps(target, df)[0]
        for column in ("player_id", "player_display_name", "position", "team", "avg_grade", "avg_ppr"):
            self.assertIn(column, comp)


if __name__ == "__main__":
    unittest.main()
