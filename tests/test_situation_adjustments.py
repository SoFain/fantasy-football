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
    def test_coefficients_match_the_signed_off_v1_study(self):
        # Owner-approved 2026-07-25: WR keeps v0; RB standard gains the QB
        # interaction; TE gains team quality both scales; RB gng keeps v0.
        self.assertEqual(adj.EFFECTS["standard"]["WR"], {"team": -0.778, "qb": 0.022})
        self.assertEqual(adj.EFFECTS["standard"]["RB"]["qb_mover_extra"], 0.1096)
        self.assertEqual(adj.EFFECTS["standard"]["TE"]["winpct_mover"], -0.483)
        self.assertEqual(adj.EFFECTS["gng"]["TE"]["winpct_mover"], -0.449)
        self.assertEqual(adj.EFFECTS["gng"]["RB"], {"team": -0.328, "qb": 0.057})
        self.assertEqual(adj.CODE, "SITUATION_V1")

    def test_rb_standard_qb_upgrade_is_a_mover_phenomenon(self):
        # Mover slope = qb + extra; stayer slope ~ 0, so a stayer QB upgrade
        # lands under the dead-band and never moves.
        rows = _board(mover_at=10, mover_delta_qb=5.0)
        plan = adj.plan_board(rows, "standard", "RB")
        mover = next(p for p in plan["all"] if p["row"]["player_id"] == "p10")
        self.assertAlmostEqual(mover["qb_slope"], -0.0035 + 0.1096)
        self.assertAlmostEqual(mover["delta_ppg"], -0.527 + 0.1061 * 5.0, places=3)
        stayer_rows = _board()
        stayer_rows[5]["qb_changed"] = True
        stayer_rows[5]["qb_delta"] = 5.0
        self.assertEqual(adj.plan_board(stayer_rows, "standard", "RB")["adjusted"], [])

    def test_te_mover_applies_the_record_differential(self):
        # CHI (0.6471) -> NYJ (0.1765): a big drop in destination record is a
        # POSITIVE adjustment for a TE (winpct_mover is negative).
        rows = _board(mover_at=8)
        rows[7]["team_from"], rows[7]["team_to"] = "CHI", "NYJ"
        plan = adj.plan_board(rows, "standard", "TE")
        mover = next(p for p in plan["all"] if p["row"]["player_id"] == "p8")
        self.assertAlmostEqual(mover["wp_delta"], 0.1765 - 0.6471, places=4)
        self.assertAlmostEqual(
            mover["delta_ppg"], -0.485 - 0.483 * (0.1765 - 0.6471), places=3
        )

    def test_unknown_team_codes_skip_the_record_term(self):
        plan = adj.plan_board(_board(mover_at=8), "standard", "TE")  # AAA->BBB
        mover = next(p for p in plan["all"] if p["row"]["player_id"] == "p8")
        self.assertIsNone(mover["wp_delta"])
        self.assertAlmostEqual(mover["delta_ppg"], -0.485, places=3)

    def test_sleeper_coded_destination_normalizes(self):
        self.assertEqual(adj.winpct("LAR"), adj.winpct("LA"))
        self.assertEqual(len(adj.WINPCT_2025), 32)
        self.assertTrue(all(0.0 <= v <= 1.0 for v in adj.WINPCT_2025.values()))

    def test_gng_moves_mirror_to_the_pipeline_source_table(self):
        # The GNG unified builder/promoter read boards_with_rookies; without
        # the mirror, stage 6's artifact-vs-active preflight fails the day.
        import inspect

        src = inspect.getsource(adj.write)
        self.assertIn("gng_2026_positional_boards_with_rookies", adj.GNG_MIRROR)
        self.assertIn("GNG_MIRROR", src)
        self.assertIn("s.scoring_profile_id = 'gng_keeper'", src)

    def test_apply_is_env_gated(self):
        import inspect

        self.assertIn("ALLOW_SITUATION_ADJUSTMENTS", inspect.getsource(adj.main))


if __name__ == "__main__":
    unittest.main()
