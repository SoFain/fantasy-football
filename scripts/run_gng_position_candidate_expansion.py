"""Test five predeclared advanced GNG candidates for QB, RB, and WR."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
import sys

from google.cloud import bigquery

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.run_gng_advanced_hypotheses import player_audit, weighted_average
from scripts.run_ppr_fable_transfer_backtest import summarize


ROUND1_CANDIDATES = {
    "QB": {
        "q1_dual_threat": {"profile": .30, "opportunity": .15, "efficiency": .10, "role": .10, "passing_epa": .10, "qb_ngs_efficiency": .10, "passing_cpoe": .05, "qb_rushing": .10},
        "q2_passing_quality": {"profile": .30, "opportunity": .15, "passing_epa": .15, "qb_ngs_efficiency": .15, "passing_cpoe": .10, "passing_fd_expected": .10, "role": .05},
        "q3_volume_stability": {"profile": .35, "opportunity": .20, "role": .15, "dropbacks": .10, "snap_share": .10, "availability": .10},
        "q4_gng_bonus_proxy": {"profile": .30, "passing_yards": .15, "passing_fd_expected": .15, "qb_rushing": .15, "qb_ngs_efficiency": .10, "passing_cpoe": .05, "attempts": .10},
        "q5_balanced_advanced": {"profile": .30, "opportunity": .15, "efficiency": .08, "role": .08, "passing_epa": .10, "qb_ngs_efficiency": .10, "passing_fd_expected": .07, "qb_rushing": .07, "snap_share": .05},
    },
    "RB": {
        "r1_gng_high_value": {"profile": .35, "gng_weighted_opp": .30, "xfp_share": .10, "goal_line_opps": .10, "rushing_fd_expected": .05, "receiving_fd_expected": .05, "snap_share": .05},
        "r2_dual_use": {"profile": .30, "gng_weighted_opp": .25, "target_share": .10, "wopr": .08, "receiving_fd_expected": .07, "rushing_fd_expected": .07, "goal_line_opps": .08, "snap_share": .05},
        "r3_rushing_quality": {"profile": .35, "gng_weighted_opp": .25, "rushing_epa": .10, "rushing_fd_expected": .10, "ngs_ryoe_score": .08, "ngs_rush_eff_score": .07, "goal_line_opps": .05},
        "r4_role_durability": {"profile": .35, "gng_weighted_opp": .20, "role": .10, "snap_share": .10, "snap_stability": .10, "availability": .10, "goal_line_opps": .05},
        "r5_balanced_advanced": {"profile": .35, "gng_weighted_opp": .25, "xfp_share": .08, "goal_line_opps": .07, "target_share": .05, "rushing_fd_expected": .05, "rushing_epa": .05, "snap_share": .05, "availability": .05},
    },
    "WR": {
        "w1_route_earning": {"profile": .25, "gng_weighted_opp": .20, "target_share": .12, "wopr": .10, "target_share_slope": .08, "wopr_slope": .08, "receiving_fd_expected": .10, "snap_stability": .07},
        "w2_air_yard_alpha": {"profile": .25, "gng_weighted_opp": .20, "wopr": .15, "air_yards_share": .12, "target_share": .10, "ngs_receiving_eff": .08, "adot": .05, "role": .05},
        "w3_chain_mover": {"profile": .25, "gng_weighted_opp": .20, "receiving_fd_expected": .15, "high_value_fd": .10, "receiving_epa": .10, "target_share": .10, "snap_share": .05, "opportunity_quality": .05},
        "w4_explosive_quality": {"profile": .25, "gng_weighted_opp": .20, "air_yards_share": .10, "racr": .08, "adot": .07, "ngs_separation_score": .08, "ngs_yac_score": .07, "ngs_receiving_eff": .08, "snap_stability": .07},
        "w5_role_stability_plus": {"profile": .25, "gng_weighted_opp": .20, "xfp_share": .10, "target_share": .10, "target_share_slope": .08, "snap_share": .08, "snap_stability": .07, "availability": .05, "receiving_fd_expected": .07},
    },
}

ROUND2_CANDIDATES = {
    "RB": {
        "r6_safe_dual_use": {"profile": .35, "gng_weighted_opp": .25, "target_share": .08, "wopr": .05, "receiving_fd_expected": .05, "rushing_fd_expected": .05, "goal_line_opps": .07, "role": .05, "snap_stability": .05, "availability": .05},
        "r7_h1_r2_compromise": {"profile": .65, "gng_weighted_opp": .125, "target_share": .05, "wopr": .04, "receiving_fd_expected": .035, "rushing_fd_expected": .035, "goal_line_opps": .04, "snap_share": .025},
        "r8_role_guarded_r2": {"profile": .30, "gng_weighted_opp": .25, "target_share": .08, "wopr": .05, "receiving_fd_expected": .05, "rushing_fd_expected": .05, "goal_line_opps": .07, "role": .05, "snap_share": .05, "snap_stability": .05, "availability": .05},
        "r9_high_value_floor": {"profile": .40, "gng_weighted_opp": .25, "xfp_share": .08, "goal_line_opps": .07, "receiving_fd_expected": .05, "rushing_fd_expected": .05, "role": .05, "snap_share": .05},
        "r10_efficiency_capped": {"profile": .40, "gng_weighted_opp": .25, "target_share": .05, "goal_line_opps": .07, "rushing_fd_expected": .05, "rushing_epa": .03, "ngs_ryoe_score": .03, "role": .05, "snap_share": .04, "availability": .03},
    },
    "WR": {
        "w6_h5_air_overlay": {"profile": .25, "gng_weighted_opp": .20, "xfp_share": .08, "opportunity_quality": .08, "snap_share": .07, "snap_stability": .07, "availability": .05, "receiving_fd_expected": .07, "wopr": .05, "air_yards_share": .04, "adot": .02, "ngs_receiving_eff": .02},
        "w7_h5_earning_overlay": {"profile": .25, "gng_weighted_opp": .20, "xfp_share": .08, "opportunity_quality": .08, "snap_share": .07, "snap_stability": .07, "availability": .05, "receiving_fd_expected": .08, "target_share": .06, "wopr": .03, "target_share_slope": .02, "wopr_slope": .01},
        "w8_h5_chain_overlay": {"profile": .25, "gng_weighted_opp": .20, "xfp_share": .08, "opportunity_quality": .08, "snap_share": .07, "snap_stability": .07, "availability": .05, "receiving_fd_expected": .10, "high_value_fd": .05, "receiving_epa": .03, "target_share": .02},
        "w9_h5_ngs_overlay": {"profile": .25, "gng_weighted_opp": .20, "xfp_share": .08, "opportunity_quality": .08, "snap_share": .07, "snap_stability": .07, "availability": .05, "receiving_fd_expected": .07, "ngs_receiving_eff": .05, "ngs_separation_score": .04, "ngs_yac_score": .04},
        "w10_h5_floor_first": {"profile": .30, "gng_weighted_opp": .20, "xfp_share": .10, "opportunity_quality": .08, "snap_share": .08, "snap_stability": .08, "availability": .06, "receiving_fd_expected": .05, "target_share": .03, "wopr": .02},
    },
}

BASELINES = {
    "QB": {"profile": .45, "opportunity": .30, "efficiency": .15, "role": .10},
    "RB": {"profile": 1.0},
    "WR": {"profile": .25, "gng_weighted_opp": .20, "first_down_any": .10, "xfp_share": .10, "opportunity_quality": .10, "snap_share": .08, "snap_stability": .07, "availability": .05, "ngs_any": .05},
}


def percent_ranks(rows, field):
    present = sorted((row[field], index) for index, row in enumerate(rows) if row.get(field) is not None)
    denominator = max(len(present) - 1, 1)
    ranks = {}
    first = 0
    while first < len(present):
        last = first + 1
        while last < len(present) and present[last][0] == present[first][0]:
            last += 1
        for _, index in present[first:last]:
            ranks[index] = first / denominator
        first = last
    return ranks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    parser.add_argument("--output", type=Path, default=Path("output/gng-position-candidate-expansion.json"))
    parser.add_argument("--round", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    client = bigquery.Client(project=args.project)
    sql = f"""
WITH mart AS (
 SELECT target_season,position,player_id_internal player_id,ANY_VALUE(player_name) player_name,
  AVG(profile_points_score) profile,AVG(opportunity_score_proxy) opportunity,AVG(efficiency_score_proxy) efficiency,
  AVG(role_stability_score) role,AVG(xfp_share_3yr) xfp_share,AVG(opportunity_quality_score_3yr) opportunity_quality,
  AVG(passing_first_down_exp_pbp_3yr) passing_fd_expected,AVG(receiving_first_down_exp_pbp_3yr) receiving_fd_expected,
  AVG(rushing_first_down_exp_pbp_3yr) rushing_fd_expected,AVG(qb_ngs_efficiency_score_3yr) qb_ngs_efficiency,
  AVG(ngs_rush_yards_over_expected_score_3yr) ngs_ryoe_score,AVG(ngs_rushing_efficiency_score_3yr) ngs_rush_eff_score,
  AVG(ngs_catch_over_expected_score_3yr) ngs_catch_oe,AVG(ngs_separation_score_3yr) ngs_separation_score,
  AVG(ngs_yac_over_expected_score_3yr) ngs_yac_score,AVG(ngs_receiving_efficiency_score_3yr) ngs_receiving_eff,
  AVG(high_value_first_down_opportunity_score_3yr) high_value_fd,AVG(target_share_slope_3yr) target_share_slope,
  AVG(wopr_slope_3yr) wopr_slope,
  SUM(target_fantasy_points) target_points,AVG(target_fantasy_points) target_ppg,COUNTIF(target_fantasy_points IS NOT NULL) target_games
 FROM `{args.project}.{args.dataset}.ranking_backtest_feature_mart`
 WHERE scoring_profile_id='gng_keeper' AND target_season BETWEEN 2023 AND 2025
  AND source_window_end_season<target_season AND position IN ('QB','RB','WR')
 GROUP BY target_season,position,player_id HAVING target_games>=6
), adv AS (
 SELECT season,player_id_internal player_id,
  weighted_opportunity_gng_keeper gng_weighted_opp, passing_epa_per_dropback passing_epa, dakota,
  passing_cpoe, passing_first_down_rate passing_fd_rate, qb_rushing_baseline_score qb_rushing,
  passing_yards, attempts, dropbacks, offensive_snap_share snap_share, snap_role_stability snap_stability,
  availability_score availability, goal_line_opportunities goal_line_opps, rushing_first_down_rate,
  receiving_first_down_rate, target_share, wopr, rushing_epa_per_carry rushing_epa,
  ngs_rush_yards_over_expected_per_att ngs_ryoe_pa, -ngs_rushing_efficiency ngs_rush_eff,
  yprr,tprr,route_participation_rate route_participation,receiving_first_downs_per_route receiving_fd_per_route,
  receiving_epa_per_target receiving_epa,air_yards_share,end_zone_targets,adot,racr,
  ngs_avg_separation ngs_separation,ngs_yac_above_expectation ngs_yac_oe,
  COALESCE(receiving_first_down_rate,rushing_first_down_rate,passing_first_down_rate) first_down_any,
  COALESCE(ngs_yac_above_expectation,ngs_rush_yards_over_expected_per_att,ngs_qb_cpoe) ngs_any
 FROM `{args.project}.{args.dataset}.player_season_advanced_metrics`
 WHERE metric_version='advanced_player_metrics_v1' AND season_type='REG' AND season BETWEEN 2022 AND 2024
)
SELECT mart.*,adv.* EXCEPT(season,player_id)
FROM mart LEFT JOIN adv ON adv.season=mart.target_season-1 AND adv.player_id=mart.player_id
"""
    rows = [dict(row) for row in client.query(sql).result()]
    candidates_by_position = ROUND1_CANDIDATES if args.round == 1 else ROUND2_CANDIDATES
    positions = tuple(candidates_by_position)
    results = {"round": args.round, "candidate_definitions": candidates_by_position, "coverage": {}, "results": {}, "scored_rows": []}
    for position in positions:
        position_rows = [row for row in rows if row["position"] == position]
        fields = set(BASELINES[position])
        for weights in candidates_by_position[position].values():
            fields.update(weights)
        results["coverage"][position] = {field: sum(row.get(field) is not None for row in position_rows) for field in sorted(fields)}
        candidates = {"baseline": BASELINES[position], **candidates_by_position[position]}
        for season in (2023, 2024, 2025):
            fold = [row for row in position_rows if row["target_season"] == season]
            for field in fields:
                ranks = percent_ranks(fold, field)
                for index, row in enumerate(fold):
                    row[f"p_{field}"] = ranks.get(index)
            for candidate, weights in candidates.items():
                for row in fold:
                    row[candidate] = weighted_average(row, tuple((f"p_{field}", weight) for field, weight in weights.items()))
        for candidate in candidates:
            folds = {}
            audits = {}
            for source_season in (2022, 2023, 2024):
                fold_rows = [{"player_id": row["player_id"], "player_name": row["player_name"], "score": row[candidate], "target_ppg": row["target_ppg"], "target_points": row["target_points"]} for row in position_rows if row["target_season"] == source_season + 1]
                key = f"{source_season}_to_{source_season + 1}"
                folds[key] = summarize(fold_rows)
                audits[key] = player_audit(fold_rows)
            metrics = ("spearman", "pairwise", "top12_precision", "top24_precision", "points_at_12", "points_at_24", "ndcg_at_24")
            aggregate = {f"average_{metric}": mean(fold[metric] for fold in folds.values()) for metric in metrics}
            aggregate["total_elite_misses"] = sum(fold["elite_misses"] for fold in folds.values())
            aggregate["total_top12_busts"] = sum(fold["top12_busts"] for fold in folds.values())
            results["results"][f"{position}_{candidate}"] = {"aggregate": aggregate, "folds": folds, "player_audit": audits}
        for row in position_rows:
            results["scored_rows"].append({"season":row["target_season"]-1,"position":position,"player_id":row["player_id"],"player_name":row["player_name"],"target_ppg":row["target_ppg"],**{candidate:row[candidate] for candidate in candidates}})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value["aggregate"] for key, value in results["results"].items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
