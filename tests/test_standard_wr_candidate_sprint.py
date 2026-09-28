import unittest

from scripts.run_standard_wr_candidate_sprint import (
    ADVANCED_FIELDS,
    BASELINE,
    BLEND_CANDIDATES,
    CANDIDATE_DEFINITIONS,
    CORE_CANDIDATES,
    build_query,
    evaluate_variant,
    score_rows,
)


def base_row(player_id: str, baseline: float, advanced: float | None) -> dict:
    return {
        "season": 2022,
        "candidate_internal_player_id": player_id,
        "player_name": player_id,
        "team": "TST",
        "z_wopr": baseline,
        "z_ngt_tgt": baseline,
        "z_rz_tgt": baseline,
        "z_yprr": baseline,
        "z_epa_per_target": baseline,
        "z_yac_per_reception": baseline,
        "z_adot_adjusted_catch_rate": baseline,
        "z_blended_td": baseline,
        "z_breakout_window": baseline,
        "z_decline_penalty": baseline,
        "z_games_rate": baseline,
        "route_efficiency_shrink": 1.0,
        "target_efficiency_shrink": 1.0,
        BASELINE: baseline,
        "target_roster_eligible": True,
        "target_games": 17,
        "target_standard_points": 100.0,
        "target_standard_ppg": 10.0,
        **{field: advanced for field in ADVANCED_FIELDS},
    }


class StandardWrCandidateSprintTest(unittest.TestCase):
    def test_five_candidates_and_weights_are_frozen(self):
        self.assertEqual(len(CANDIDATE_DEFINITIONS), 5)
        for terms in CORE_CANDIDATES.values():
            self.assertAlmostEqual(sum(weight for _, weight, _ in terms), 1.0)
        for terms in BLEND_CANDIDATES.values():
            self.assertAlmostEqual(sum(weight for _, weight in terms), 1.0)

    def test_unknown_advanced_values_are_neutral_not_raw_zero(self):
        rows = [base_row("low", -1.0, 1.0), base_row("mid", 0.0, None), base_row("high", 1.0, 3.0)]
        scored, coverage = score_rows(rows)
        middle = next(row for row in scored if row["player_name"] == "mid")
        self.assertEqual(middle["z_weighted_ppr_pg"], 0.0)
        self.assertEqual(middle["s3_ppr_opportunity_transfer"], 0.0)
        self.assertEqual(coverage["weighted_ppr_pg"]["2022"]["missing"], 1)

    def test_query_is_read_only_and_uses_prior_to_next_season_join(self):
        sql = build_query("project", "brain", "metrics")
        self.assertIn("target.season = scored.season + 1", sql)
        self.assertIn("status IN ('ACT', 'RES', 'PUP', 'SUS', 'NWT', 'INA')", sql)
        self.assertIn("target_roster.season = scored.season + 1", sql)
        self.assertIn("scoring_profile_id = 'standard'", sql)
        upper = sql.upper()
        for token in ("CREATE ", "INSERT ", "UPDATE ", "DELETE ", "MERGE "):
            self.assertNotIn(token, upper)

    def test_primary_lane_keeps_zero_game_rostered_players(self):
        rows = []
        for season in (2022, 2023, 2024):
            for rank in range(1, 16):
                rows.append({
                    "season": season,
                    "candidate_internal_player_id": f"{season}-{rank}",
                    "player_name": f"W{rank:02}",
                    BASELINE: float(20 - rank),
                    "target_roster_eligible": rank != 15,
                    "target_games": 0 if rank == 14 else 17,
                    "target_standard_points": 0.0 if rank == 14 else float(20 - rank),
                    "target_standard_ppg": None if rank == 14 else float(20 - rank),
                })
        primary = evaluate_variant(rows, BASELINE, minimum_target_games=0)
        continuity = evaluate_variant(rows, BASELINE, minimum_target_games=6)
        self.assertEqual(primary["aggregate"]["total_rows"], 42)
        self.assertEqual(continuity["aggregate"]["total_rows"], 39)


if __name__ == "__main__":
    unittest.main()
