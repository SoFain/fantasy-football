import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "apply_situation_adjustments",
    Path(__file__).resolve().parents[1] / "scripts" / "apply_situation_adjustments.py",
)
adj = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(adj)


def _board(n=20, mover_at=None, mover_delta_qb=0.0, ppg_step=0.3):
    """Synthetic board: descending scores and PPG; optional mover at one rank."""
    rows = []
    for rank in range(1, n + 1):
        moved = mover_at == rank
        rows.append({
            "player_id": f"p{rank}", "player_name": f"Player {rank}", "rank": rank,
            "ranking_score": 99.0 - rank, "llm_adjustment_code": None,
            "team_changed": moved if mover_at else (False if mover_at is None else False),
            "team_from": "AAA", "team_to": "BBB", "qb_changed": moved,
            "qb_to": "Some QB", "qb_delta": mover_delta_qb if moved else 0.0,
            "ppg_prev": 12.0 - rank * ppg_step,
            "flags_json": '["NEW_TEAM"]' if moved else "[]",
            "metric_basis": "2025_AAA",
        })
    return rows


class PlanTest(unittest.TestCase):
    def test_scope_is_the_studied_surface(self):
        # Owner doctrine: QB boards untouched; only the two validated scales.
        self.assertEqual(adj.POSITIONS, ("WR", "RB", "TE"))
        self.assertEqual(set(adj.PROFILE_SCALE), {"standard", "gng_keeper"})

    def test_ladder_is_preserved_and_contiguous(self):
        plan = adj.plan_board(_board(mover_at=10), "standard", "WR")
        self.assertEqual(adj.validate_plan(plan), [])
        new_scores = sorted(p["new_score"] for p in plan["all"])
        old_scores = sorted(p["row"]["ranking_score"] for p in plan["all"])
        self.assertEqual(new_scores, old_scores)
        self.assertEqual(sorted(p["new_rank"] for p in plan["all"]), list(range(1, 21)))

    def test_mover_moves_down_and_others_ripple(self):
        plan = adj.plan_board(_board(mover_at=10), "standard", "WR")
        mover = next(p for p in plan["all"] if p["row"]["player_id"] == "p10")
        self.assertGreater(mover["new_rank"], 10)  # WR team change is negative
        displaced = next(p for p in plan["all"] if p["new_rank"] == 10)
        self.assertEqual(displaced["slots"], 0)  # neighbor rippled, not adjusted

    def test_cap_bounds_extreme_deltas(self):
        # Flat board (tiny density) + team change + big QB downgrade: uncapped
        # this would be a huge move; the cap holds it to 4 slots.
        plan = adj.plan_board(
            _board(mover_at=5, mover_delta_qb=-10.0, ppg_step=0.01), "standard", "WR"
        )
        mover = next(p for p in plan["all"] if p["row"]["player_id"] == "p5")
        self.assertEqual(mover["target"] - mover["old_rank"], adj.CAP_SLOTS)

    def test_dead_band_swallows_noise(self):
        # +0.07 PPG (qb-only, no team change) is below MIN_DELTA_PPG: no move
        # even where the density floor would otherwise grant a slot.
        rows = _board(ppg_step=0.01)
        rows[7]["qb_changed"] = True
        rows[7]["qb_delta"] = 3.0  # 3.0 * 0.022 = 0.066 PPG
        plan = adj.plan_board(rows, "standard", "WR")
        self.assertEqual([p for p in plan["adjusted"]], [])

    def test_density_floor_never_divides_by_flat_or_inverted_regions(self):
        rows = _board(mover_at=3)
        for r in rows:
            r["ppg_prev"] = 8.0  # perfectly flat
        plan = adj.plan_board(rows, "standard", "WR")
        mover = next(p for p in plan["all"] if p["row"]["player_id"] == "p3")
        self.assertEqual(mover["target"] - mover["old_rank"], adj.CAP_SLOTS)  # floor + cap

    def test_missing_situation_row_means_no_move(self):
        rows = _board()
        for r in rows:
            r["team_changed"] = None  # rookie: no situation row
            r["qb_delta"] = None
        plan = adj.plan_board(rows, "standard", "WR")
        self.assertEqual(plan["adjusted"], [])

    def test_provenance_only_on_moved_rows_and_self_describing(self):
        plan = adj.plan_board(_board(mover_at=10), "standard", "WR")
        staged = [adj.provenance(p, "standard", "WR") for p in plan["all"]]
        moved = [s for s in staged if s["moved"]]
        still = [s for s in staged if not s["moved"]]
        self.assertTrue(all(s["detail"] and "->" in s["detail"] for s in moved))
        self.assertTrue(all(s["detail"] is None and s["note"] is None for s in still))

    def test_validate_plan_catches_score_tampering(self):
        plan = adj.plan_board(_board(mover_at=10), "standard", "WR")
        plan["all"][0]["new_score"] = 123.0
        self.assertTrue(any("score multiset" in p for p in adj.validate_plan(plan)))


class PolicyPinTest(unittest.TestCase):
    def test_coefficients_match_the_signed_off_study(self):
        self.assertEqual(adj.EFFECTS["standard"]["WR"], (-0.778, 0.022))
        self.assertEqual(adj.EFFECTS["gng"]["RB"], (-0.328, 0.057))

    def test_apply_is_env_gated(self):
        import inspect

        self.assertIn("ALLOW_SITUATION_ADJUSTMENTS", inspect.getsource(adj.main))


if __name__ == "__main__":
    unittest.main()
