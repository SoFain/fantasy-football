"""Backtest five frozen Standard WR formula candidates without writing rankings.

The primary lane uses a fixed prior-season Fable cohort and next-season Standard
total points. A six-game PPG lane is retained only for comparison with the older
WR Fable v1 reports.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from itertools import combinations
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_wr_fable_v1_backtest import pearson, rank_values


BASELINE = "wr_fable_v1_score"
CORE_CANDIDATES: dict[str, tuple[tuple[str, float, str | None], ...]] = {
    "s1_opportunity_efficiency_trim": (
        ("z_wopr", 0.34, None),
        ("z_ngt_tgt", 0.16, None),
        ("z_rz_tgt", 0.12, None),
        ("z_yprr", 0.14, "route_efficiency_shrink"),
        ("z_epa_per_target", 0.03, "target_efficiency_shrink"),
        ("z_yac_per_reception", 0.01, "target_efficiency_shrink"),
        ("z_adot_adjusted_catch_rate", 0.02, "target_efficiency_shrink"),
        ("z_blended_td", 0.10, None),
        ("z_breakout_window", 0.03, None),
        ("z_decline_penalty", 0.025, None),
        ("z_games_rate", 0.025, None),
    ),
    "s2_standard_td_balance": (
        ("z_wopr", 0.30, None),
        ("z_ngt_tgt", 0.14, None),
        ("z_rz_tgt", 0.15, None),
        ("z_yprr", 0.14, "route_efficiency_shrink"),
        ("z_epa_per_target", 0.03, "target_efficiency_shrink"),
        ("z_yac_per_reception", 0.01, "target_efficiency_shrink"),
        ("z_adot_adjusted_catch_rate", 0.02, "target_efficiency_shrink"),
        ("z_blended_td", 0.14, None),
        ("z_breakout_window", 0.03, None),
        ("z_decline_penalty", 0.02, None),
        ("z_games_rate", 0.02, None),
    ),
}
BLEND_CANDIDATES: dict[str, tuple[tuple[str, float], ...]] = {
    "s3_ppr_opportunity_transfer": (
        ("z_baseline", 0.75),
        ("z_weighted_ppr_pg", 0.25),
    ),
    "s4_half_ppr_role_balance": (
        ("z_baseline", 0.70),
        ("z_weighted_half_pg", 0.20),
        ("z_snap_role_stability", 0.10),
    ),
    "s5_standard_role_floor": (
        ("z_baseline", 0.65),
        ("z_weighted_standard_pg", 0.20),
        ("z_snap_role_stability", 0.10),
        ("z_receiving_first_down_rate", 0.05),
    ),
}
CANDIDATE_DEFINITIONS = {
    "s1_opportunity_efficiency_trim": {
        "hypothesis": "Move weight from weak per-target YAC, EPA, and catch residuals into earned opportunity and YPRR.",
        "source_family": "Fable situational metrics",
        "terms": CORE_CANDIDATES["s1_opportunity_efficiency_trim"],
    },
    "s2_standard_td_balance": {
        "hypothesis": "Standard scoring should put more weight on red-zone opportunity and regressed touchdowns than reception-adjacent efficiency.",
        "source_family": "Fable situational metrics",
        "terms": CORE_CANDIDATES["s2_standard_td_balance"],
    },
    "s3_ppr_opportunity_transfer": {
        "hypothesis": "PPR-weighted opportunity per game may capture durable target earning even when the target outcome is Standard points.",
        "source_family": "player_season_advanced_metrics PPR weighted opportunity",
        "terms": BLEND_CANDIDATES["s3_ppr_opportunity_transfer"],
    },
    "s4_half_ppr_role_balance": {
        "hypothesis": "Half-PPR opportunity plus snap-role stability may retain volume signal without leaning fully into reception value.",
        "source_family": "player_season_advanced_metrics Half-PPR opportunity and role stability",
        "terms": BLEND_CANDIDATES["s4_half_ppr_role_balance"],
    },
    "s5_standard_role_floor": {
        "hypothesis": "Standard weighted opportunity, role stability, and first-down conversion may reduce fragile volume ranks.",
        "source_family": "player_season_advanced_metrics Standard opportunity, role, and first downs",
        "terms": BLEND_CANDIDATES["s5_standard_role_floor"],
    },
}
ADVANCED_FIELDS = (
    "weighted_standard_pg",
    "weighted_half_pg",
    "weighted_ppr_pg",
    "snap_role_stability",
    "receiving_first_down_rate",
)
VARIANTS = (BASELINE, *CANDIDATE_DEFINITIONS)
AGGREGATE_FIELDS = (
    "top_12_precision",
    "top_24_precision",
    "spearman_rank_correlation",
    "pairwise_draft_win_rate",
    "points_captured_at_12",
    "points_captured_at_24",
    "ndcg_at_12",
    "ndcg_at_24",
    "band_regret",
)


def build_query(project: str, brain_dataset: str, metrics_dataset: str) -> str:
    return f"""
WITH scored AS (
  SELECT *
  FROM `{project}.{metrics_dataset}.v_wr_fable_v1_scored_seasons`
  WHERE season BETWEEN 2022 AND 2025
    AND {BASELINE} IS NOT NULL
),
target AS (
  SELECT
    season,
    source_player_key AS player_id,
    COUNT(*) AS target_games,
    SUM(total_fantasy_points) AS target_standard_points,
    SAFE_DIVIDE(SUM(total_fantasy_points), COUNT(*)) AS target_standard_ppg
  FROM `{project}.{brain_dataset}.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id = 'standard'
    AND position = 'WR'
    AND season BETWEEN 2023 AND 2025
    AND week BETWEEN 1 AND 18
  GROUP BY season, player_id
),
target_roster AS (
  SELECT season, gsis_id AS player_id
  FROM `{project}.{brain_dataset}.raw_nflverse_rosters_weekly`
  WHERE season BETWEEN 2023 AND 2025
    AND week = 1
    AND position = 'WR'
    AND status IN ('ACT', 'RES', 'PUP', 'SUS', 'NWT', 'INA')
  GROUP BY season, player_id
)
SELECT
  scored.season,
  scored.candidate_internal_player_id,
  scored.player_name,
  scored.team,
  scored.z_wopr,
  scored.z_ngt_tgt,
  scored.z_rz_tgt,
  scored.z_yprr,
  scored.z_epa_per_target,
  scored.z_yac_per_reception,
  scored.z_adot_adjusted_catch_rate,
  scored.z_blended_td,
  scored.z_breakout_window,
  scored.z_decline_penalty,
  scored.z_games_rate,
  scored.route_efficiency_shrink,
  scored.target_efficiency_shrink,
  scored.{BASELINE},
  target_roster.player_id IS NOT NULL AS target_roster_eligible,
  COALESCE(target.target_games, 0) AS target_games,
  COALESCE(target.target_standard_points, 0.0) AS target_standard_points,
  target.target_standard_ppg,
  SAFE_DIVIDE(advanced.weighted_opportunity_standard, NULLIF(advanced.games, 0)) AS weighted_standard_pg,
  SAFE_DIVIDE(advanced.weighted_opportunity_half_ppr, NULLIF(advanced.games, 0)) AS weighted_half_pg,
  SAFE_DIVIDE(advanced.weighted_opportunity_ppr, NULLIF(advanced.games, 0)) AS weighted_ppr_pg,
  advanced.snap_role_stability,
  advanced.receiving_first_down_rate
FROM scored
LEFT JOIN target
  ON target.season = scored.season + 1
 AND target.player_id = scored.candidate_internal_player_id
LEFT JOIN target_roster
  ON target_roster.season = scored.season + 1
 AND target_roster.player_id = scored.candidate_internal_player_id
LEFT JOIN `{project}.{brain_dataset}.player_season_advanced_metrics` AS advanced
  ON advanced.season = scored.season
 AND advanced.player_id_internal = scored.candidate_internal_player_id
 AND advanced.season_type = 'REG'
 AND advanced.position = 'WR'
 AND advanced.metric_version = 'advanced_player_metrics_v1'
ORDER BY scored.season, scored.player_name
"""


def _seasonal_z_scores(rows: list[dict[str, Any]], field: str) -> tuple[list[float], int]:
    values = [float(row[field]) for row in rows if row.get(field) is not None]
    if not values:
        return [0.0] * len(rows), 0
    center = mean(values)
    spread = pstdev(values)
    return [
        0.0 if row.get(field) is None or spread == 0 else (float(row[field]) - center) / spread
        for row in rows
    ], len(values)


def _core_candidate_score(row: dict[str, Any], terms: tuple[tuple[str, float, str | None], ...]) -> float:
    score = 0.0
    for field, weight, shrink_field in terms:
        value = row[field]
        if value is None:
            raise ValueError(f"{field} is unexpectedly null on a complete Fable row")
        shrink = 1.0 if shrink_field is None else float(row[shrink_field])
        score += weight * float(value) * shrink
    return score


def score_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    coverage: dict[str, Any] = {}
    for season in (2022, 2023, 2024, 2025):
        season_rows = [dict(row) for row in rows if int(row["season"]) == season]
        if not season_rows:
            continue
        feature_fields = (BASELINE, *ADVANCED_FIELDS)
        for field in feature_fields:
            z_values, present = _seasonal_z_scores(season_rows, field)
            z_field = "z_baseline" if field == BASELINE else f"z_{field}"
            for row, z_value in zip(season_rows, z_values):
                row[z_field] = z_value
            coverage.setdefault(field, {})[str(season)] = {
                "present": present,
                "total": len(season_rows),
                "missing": len(season_rows) - present,
            }
        for row in season_rows:
            for candidate, terms in CORE_CANDIDATES.items():
                row[candidate] = _core_candidate_score(row, terms)
            for candidate, terms in BLEND_CANDIDATES.items():
                row[candidate] = sum(weight * row[field] for field, weight in terms)
        scored.extend(season_rows)
    return scored, coverage


def _pairwise_win_rate(rows: list[dict[str, Any]], score_field: str, target_field: str) -> float | None:
    wins = comparisons = 0
    for left, right in combinations(rows, 2):
        predicted_delta = left[score_field] - right[score_field]
        actual_delta = left[target_field] - right[target_field]
        if predicted_delta == 0 or actual_delta == 0:
            continue
        comparisons += 1
        wins += (predicted_delta > 0) == (actual_delta > 0)
    return wins / comparisons if comparisons else None


def _ndcg(rows: list[dict[str, Any]], score_field: str, target_field: str, cutoff: int) -> float | None:
    predicted = sorted(rows, key=lambda row: (-row[score_field], row["player_name"]))[:cutoff]
    ideal = sorted(rows, key=lambda row: (-row[target_field], row["player_name"]))[:cutoff]
    gain = lambda values: sum(max(row[target_field], 0.0) / math.log2(index + 2) for index, row in enumerate(values))
    denominator = gain(ideal)
    return gain(predicted) / denominator if denominator else None


def _band(rank: int) -> int:
    for index, cutoff in enumerate((6, 12, 24, 36)):
        if rank <= cutoff:
            return index
    return 4


def summarize_fold(rows: list[dict[str, Any]], score_field: str, target_field: str) -> dict[str, Any]:
    predicted = sorted(rows, key=lambda row: (-row[score_field], row["player_name"]))
    actual = sorted(rows, key=lambda row: (-row[target_field], row["player_name"]))
    actual_ranks = {row["candidate_internal_player_id"]: rank for rank, row in enumerate(actual, 1)}
    ranked = [
        {**row, "predicted_rank": rank, "actual_rank": actual_ranks[row["candidate_internal_player_id"]]}
        for rank, row in enumerate(predicted, 1)
    ]

    def points_captured(cutoff: int) -> float | None:
        selected = ranked[: min(cutoff, len(ranked))]
        ideal = actual[: min(cutoff, len(actual))]
        denominator = sum(row[target_field] for row in ideal)
        return sum(row[target_field] for row in selected) / denominator if denominator else None

    top12 = ranked[: min(12, len(ranked))]
    top24 = ranked[: min(24, len(ranked))]
    scores = [row[score_field] for row in ranked]
    targets = [row[target_field] for row in ranked]
    elite_misses = [row for row in ranked if row["actual_rank"] <= 12 and row["predicted_rank"] > 24]
    top12_busts = [row for row in ranked if row["predicted_rank"] <= 12 and row["actual_rank"] > 36]
    compact = lambda values: [
        {
            "player_name": row["player_name"],
            "predicted_rank": row["predicted_rank"],
            "actual_rank": row["actual_rank"],
            "target_games": row["target_games"],
            "target_standard_points": row["target_standard_points"],
            "target_standard_ppg": row["target_standard_ppg"],
        }
        for row in values
    ]
    return {
        "row_count": len(ranked),
        "top_12_hits": sum(row["actual_rank"] <= 12 for row in top12),
        "top_12_precision": sum(row["actual_rank"] <= 12 for row in top12) / len(top12),
        "top_24_precision": sum(row["actual_rank"] <= 24 for row in top24) / len(top24),
        "spearman_rank_correlation": pearson(rank_values(scores), rank_values(targets)),
        "pairwise_draft_win_rate": _pairwise_win_rate(ranked, score_field, target_field),
        "points_captured_at_12": points_captured(12),
        "points_captured_at_24": points_captured(24),
        "ndcg_at_12": _ndcg(ranked, score_field, target_field, 12),
        "ndcg_at_24": _ndcg(ranked, score_field, target_field, 24),
        "band_regret": mean(max(0, _band(row["actual_rank"]) - _band(row["predicted_rank"])) for row in ranked),
        "elite_miss_count": len(elite_misses),
        "top12_bust_count": len(top12_busts),
        "elite_misses": compact(elite_misses),
        "top12_busts": compact(top12_busts),
    }


def evaluate_variant(rows: list[dict[str, Any]], score_field: str, *, minimum_target_games: int) -> dict[str, Any]:
    folds = {}
    for season in (2022, 2023, 2024):
        fold_rows = [
            row for row in rows
            if row["season"] == season
            and row["target_roster_eligible"]
            and row["target_games"] >= minimum_target_games
        ]
        target_field = "target_standard_ppg" if minimum_target_games else "target_standard_points"
        folds[f"{season}_to_{season + 1}"] = summarize_fold(fold_rows, score_field, target_field)
    aggregate = {
        f"average_{field}": mean(fold[field] for fold in folds.values())
        for field in AGGREGATE_FIELDS
    }
    aggregate["total_top_12_hits"] = sum(fold["top_12_hits"] for fold in folds.values())
    aggregate["total_elite_misses"] = sum(fold["elite_miss_count"] for fold in folds.values())
    aggregate["total_top12_busts"] = sum(fold["top12_bust_count"] for fold in folds.values())
    aggregate["total_rows"] = sum(fold["row_count"] for fold in folds.values())
    return {"aggregate": aggregate, "folds": folds}


def replacement_assessment(primary_results: dict[str, Any]) -> dict[str, Any]:
    baseline = primary_results[BASELINE]
    baseline_aggregate = baseline["aggregate"]
    assessments = {}
    for candidate in CANDIDATE_DEFINITIONS:
        result = primary_results[candidate]
        aggregate = result["aggregate"]
        ndcg_fold_deltas = [
            result["folds"][fold]["ndcg_at_24"] - baseline["folds"][fold]["ndcg_at_24"]
            for fold in baseline["folds"]
        ]
        checks = {
            "ndcg_at_24_gain_at_least_0_010": aggregate["average_ndcg_at_24"] >= baseline_aggregate["average_ndcg_at_24"] + 0.010,
            "ndcg_wins_two_folds": sum(delta > 0 for delta in ndcg_fold_deltas) >= 2,
            "no_ndcg_fold_worse_than_0_020": min(ndcg_fold_deltas) >= -0.020,
            "top_12_hits_do_not_decline": aggregate["total_top_12_hits"] >= baseline_aggregate["total_top_12_hits"],
            "ordering_gain": (
                aggregate["average_pairwise_draft_win_rate"] >= baseline_aggregate["average_pairwise_draft_win_rate"] + 0.005
                or aggregate["average_spearman_rank_correlation"] >= baseline_aggregate["average_spearman_rank_correlation"] + 0.010
            ),
            "points_at_24_do_not_decline": aggregate["average_points_captured_at_24"] >= baseline_aggregate["average_points_captured_at_24"],
            "elite_misses_do_not_increase": aggregate["total_elite_misses"] <= baseline_aggregate["total_elite_misses"],
            "top12_busts_do_not_increase": aggregate["total_top12_busts"] <= baseline_aggregate["total_top12_busts"],
            "coverage_does_not_decline": aggregate["total_rows"] == baseline_aggregate["total_rows"],
        }
        assessments[candidate] = {
            "replacement_ready": all(checks.values()),
            "checks": checks,
            "deltas": {
                field: aggregate[field] - baseline_aggregate[field]
                for field in (
                    "average_pairwise_draft_win_rate",
                    "average_spearman_rank_correlation",
                    "average_top_12_precision",
                    "average_points_captured_at_24",
                    "average_ndcg_at_24",
                )
            },
            "ndcg_at_24_fold_deltas": ndcg_fold_deltas,
        }
    return assessments


def current_board_comparison(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    current = [row for row in rows if row["season"] == 2025]
    rank_maps = {
        variant: {
            row["candidate_internal_player_id"]: rank
            for rank, row in enumerate(sorted(current, key=lambda item: (-item[variant], item["player_name"])), 1)
        }
        for variant in VARIANTS
    }
    return [
        {
            "player_name": row["player_name"],
            "team": row["team"],
            **{f"{variant}_rank": rank_maps[variant][row["candidate_internal_player_id"]] for variant in VARIANTS},
        }
        for row in sorted(current, key=lambda item: rank_maps[BASELINE][item["candidate_internal_player_id"]])
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--brain-dataset", default="fantasy_football_brain")
    parser.add_argument("--metrics-dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--json-output", type=Path, default=Path("output/standard-wr-five-candidate-backtest.json"))
    args = parser.parse_args()

    from google.cloud import bigquery

    client = bigquery.Client(project=args.project)
    source_rows = [
        dict(row) for row in client.query(build_query(args.project, args.brain_dataset, args.metrics_dataset)).result()
    ]
    rows, coverage = score_rows(source_rows)
    total_points = {variant: evaluate_variant(rows, variant, minimum_target_games=0) for variant in VARIANTS}
    ppg_six_game = {variant: evaluate_variant(rows, variant, minimum_target_games=6) for variant in VARIANTS}
    result = {
        "status": "retrospective_screening_only",
        "candidate_definitions": CANDIDATE_DEFINITIONS,
        "missing_treatment": "Unknown advanced values receive the input-season mean after z-scoring (neutral z=0) and remain counted in coverage.",
        "primary_objective": "next-season Standard total points for eligible Week 1 WRs from a fixed prior-season Fable-score cohort; missing target rows count as zero points",
        "continuity_objective": "next-season Standard PPG for players with at least six target-season games",
        "coverage": coverage,
        "total_points_fixed_cohort": total_points,
        "ppg_six_game_continuity": ppg_six_game,
        "replacement_assessment": replacement_assessment(total_points),
        "current_2026_board_comparison": current_board_comparison(rows),
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
    compact = {
        "total_points": {variant: result["aggregate"] for variant, result in total_points.items()},
        "ppg_six_game": {variant: result["aggregate"] for variant, result in ppg_six_game.items()},
        "replacement_assessment": result["replacement_assessment"],
    }
    print(json.dumps(compact, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
