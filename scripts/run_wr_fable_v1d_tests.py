"""Run the bounded Phase 35.1D WR Fable modification matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_wr_fable_v1_backtest import SCORE, fold_summary


INPUT_SEASONS = (2022, 2023, 2024)
INJURY_VARIANTS = ("I4", "I7", "I10")
ENVIRONMENT_COLUMNS = {
    "E15": "injury_e15_score",
    "E25": "injury_e25_score",
    "E40": "injury_e40_score",
}
AGGREGATE_FIELDS = (
    "top_6_precision",
    "top_12_precision",
    "top_24_precision",
    "top_36_precision",
    "spearman_rank_correlation",
    "score_correlation",
    "points_captured_at_12",
    "points_captured_at_24",
    "ndcg_at_12",
    "ndcg_at_24",
    "pairwise_draft_win_rate",
    "band_regret",
)
EXPECTED_BASELINE = {
    # Rebased after the repaired historical situational rows and the verified
    # Marvin Harrison Jr. source-ID mapping expanded the fixed v1 cohort.
    "average_spearman_rank_correlation": 0.7578443584290112,
    "average_top_6_precision": 0.2777777777777778,
    "average_top_12_precision": 0.6388888888888888,
    "average_top_24_precision": 0.625,
    "average_points_captured_at_12": 0.9171685687193792,
    "average_points_captured_at_24": 0.8928079474487497,
    "average_ndcg_at_24": 0.8499654296154608,
    "average_pairwise_draft_win_rate": 0.7777796816170666,
    "average_band_regret": 0.23323254720150507,
    "total_elite_misses": 8,
    "total_top12_busts": 2,
    "total_complete_rows": 364,
}
HISTORICAL_AUDIT_NAMES = {
    "Keenan Allen",
    "A.J. Brown",
    "Mike Evans",
    "Deebo Samuel",
    "Tee Higgins",
    "Chris Godwin",
    "Terry McLaurin",
    "Nico Collins",
    "Chris Olave",
    "Christian Watson",
}
CURRENT_AUDIT_NAMES = HISTORICAL_AUDIT_NAMES | {
    "Malik Nabers",
    "Tyreek Hill",
    "Jaxon Smith-Njigba",
    "Davante Adams",
    "DK Metcalf",
    "Rashee Rice",
    "Stefon Diggs",
}


def evaluate_variant(source_records: list[dict[str, Any]], score_column: str) -> dict[str, Any]:
    folds: dict[str, dict[str, Any]] = {}
    for input_season in INPUT_SEASONS:
        records = []
        for record in source_records:
            if record["season"] != input_season or record.get(score_column) is None:
                continue
            aliased = dict(record)
            aliased[SCORE] = record[score_column]
            records.append(aliased)
        folds[f"{input_season}_to_{input_season + 1}"] = fold_summary(records)

    summaries = list(folds.values())
    aggregate = {
        f"average_{field}": mean(summary[field] for summary in summaries if summary[field] is not None)
        for field in AGGREGATE_FIELDS
    }
    aggregate["total_elite_misses"] = sum(summary["elite_wr_miss_count"] for summary in summaries)
    aggregate["total_top12_busts"] = sum(
        summary["predicted_top_12_bust_count"] for summary in summaries
    )
    aggregate["total_complete_rows"] = sum(summary["complete_row_count"] for summary in summaries)
    return {"folds": folds, "aggregate": aggregate}


def assert_baseline_reproduced(aggregate: dict[str, Any]) -> None:
    for field, expected in EXPECTED_BASELINE.items():
        actual = aggregate[field]
        if isinstance(expected, float):
            if abs(actual - expected) > 1e-12:
                raise RuntimeError(f"WR Fable v1 baseline mismatch for {field}: {actual} != {expected}")
        elif actual != expected:
            raise RuntimeError(f"WR Fable v1 baseline mismatch for {field}: {actual} != {expected}")


def guardrails(candidate: dict[str, Any], baseline: dict[str, Any]) -> dict[str, bool]:
    return {
        "top12_decline_within_0_01": candidate["average_top_12_precision"]
        >= baseline["average_top_12_precision"] - 0.01,
        "points12_decline_within_0_01": candidate["average_points_captured_at_12"]
        >= baseline["average_points_captured_at_12"] - 0.01,
        "ndcg24_decline_within_0_01": candidate["average_ndcg_at_24"]
        >= baseline["average_ndcg_at_24"] - 0.01,
        "pairwise_decline_within_0_01": candidate["average_pairwise_draft_win_rate"]
        >= baseline["average_pairwise_draft_win_rate"] - 0.01,
        "elite_misses_not_increased": candidate["total_elite_misses"]
        <= baseline["total_elite_misses"],
        "top12_busts_not_increased": candidate["total_top12_busts"]
        <= baseline["total_top12_busts"],
        "coverage_improved": candidate["total_complete_rows"] > baseline["total_complete_rows"],
    }


def rank_map(records: list[dict[str, Any]], score_column: str) -> dict[str, int]:
    ordered = sorted(records, key=lambda record: (-record[score_column], record["player_name"]))
    return {record["candidate_internal_player_id"]: index for index, record in enumerate(ordered, 1)}


def actual_rank_map(records: list[dict[str, Any]]) -> dict[str, int]:
    ordered = sorted(
        records,
        key=lambda record: (
            -record["target_standard_ppg"],
            -record["target_standard_points"],
            record["player_name"],
        ),
    )
    return {record["candidate_internal_player_id"]: index for index, record in enumerate(ordered, 1)}


def crossed_cutline(before: int, after: int, cutline: int) -> bool:
    return (before <= cutline < after) or (after <= cutline < before)


def movement_audit(
    selected_records: list[dict[str, Any]], environment_column: str
) -> list[dict[str, Any]]:
    adjustment_column = environment_column.removeprefix("injury_").removesuffix("_score") + "_adjustment"
    output: list[dict[str, Any]] = []
    for season in INPUT_SEASONS:
        fold_records = [record for record in selected_records if record["season"] == season]
        before_ranks = rank_map(fold_records, "injury_candidate_score")
        after_ranks = rank_map(fold_records, environment_column)
        actual_ranks = actual_rank_map(fold_records)
        for record in fold_records:
            if not record["team_changed"]:
                continue
            player_id = record["candidate_internal_player_id"]
            before = before_ranks[player_id]
            after = after_ranks[player_id]
            if not (
                abs(after - before) >= 3
                or crossed_cutline(before, after, 12)
                or crossed_cutline(before, after, 24)
            ):
                continue
            actual = actual_ranks[player_id]
            before_distance = abs(before - actual)
            after_distance = abs(after - actual)
            output.append(
                {
                    "fold": f"{season}_to_{season + 1}",
                    "player_name": record["player_name"],
                    "source_team": record["source_team"],
                    "destination_team": record["destination_team"],
                    "source_environment_score": record["source_environment_score"],
                    "destination_environment_score": record["destination_environment_score"],
                    "environment_delta": record["environment_delta"],
                    "modifier_amount": record[adjustment_column],
                    "rank_before": before,
                    "rank_after": after,
                    "actual_target_finish": record["target_standard_wr_rank"],
                    "movement_result": (
                        "helped" if after_distance < before_distance
                        else "hurt" if after_distance > before_distance
                        else "flat"
                    ),
                }
            )
    return output


def named_historical_audit(selected_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for season in INPUT_SEASONS:
        fold_records = [record for record in selected_records if record["season"] == season]
        rank_columns = {
            "injury_rank": "injury_candidate_score",
            "e15_rank": "injury_e15_score",
            "e25_rank": "injury_e25_score",
            "e40_rank": "injury_e40_score",
        }
        rank_maps = {
            output_name: rank_map(fold_records, score_column)
            for output_name, score_column in rank_columns.items()
        }
        for record in fold_records:
            if record["player_name"] not in HISTORICAL_AUDIT_NAMES:
                continue
            player_id = record["candidate_internal_player_id"]
            audit_record = {
                key: record.get(key)
                for key in (
                    "season",
                    "player_name",
                    "source_team",
                    "destination_team",
                    "team_changed",
                    "source_environment_score",
                    "destination_environment_score",
                    "environment_delta",
                    "e15_adjustment",
                    "e25_adjustment",
                    "e40_adjustment",
                    "target_standard_wr_rank",
                )
            }
            audit_record.update(
                {output_name: ranks[player_id] for output_name, ranks in rank_maps.items()}
            )
            output.append(audit_record)
    return output


def current_review(
    current_records: list[dict[str, Any]], environment_variant: str
) -> dict[str, Any]:
    adjustment_column = f"{environment_variant.lower()}_adjustment"
    environment_rank_column = f"injury_{environment_variant.lower()}_rank"
    for record in current_records:
        record["environment_candidate_score"] = (
            record["injury_candidate_score"] + record[adjustment_column]
        )
        record["environment_candidate_rank"] = record[environment_rank_column]
        reasons = []
        if record["rookie_limited_sample_flag"]:
            reasons.append("ROOKIE_LIMITED_SAMPLE")
        if record["prior_season_weight"] > 0:
            reasons.append(f"conditional blend {record['prior_season_weight']:.0%} prior")
        if record[adjustment_column]:
            reasons.append(f"environment {record[adjustment_column]:+.3f}")
        if not reasons:
            reasons.append("baseline rates; availability separate")
        record["movement_reason"] = "; ".join(reasons)

    baseline_top40 = sorted(
        (record for record in current_records if record["old_fable_rank"] is not None),
        key=lambda record: record["old_fable_rank"],
    )[:40]
    injury_top40 = sorted(current_records, key=lambda record: record["injury_candidate_rank"])[:40]
    environment_top40 = sorted(
        current_records, key=lambda record: record["environment_candidate_rank"]
    )[:40]
    included_ids = {
        record["candidate_internal_player_id"]
        for record in baseline_top40 + injury_top40 + environment_top40
    }
    comparison = sorted(
        (record for record in current_records if record["candidate_internal_player_id"] in included_ids),
        key=lambda record: min(
            value
            for value in (
                record["old_fable_rank"],
                record["injury_candidate_rank"],
                record["environment_candidate_rank"],
            )
            if value is not None
        ),
    )
    named = {
        record["player_name"]: record
        for record in current_records
        if record["player_name"] in CURRENT_AUDIT_NAMES
    }
    return {
        "baseline_top40_names": [record["player_name"] for record in baseline_top40],
        "injury_top40_names": [record["player_name"] for record in injury_top40],
        "environment_top40_names": [record["player_name"] for record in environment_top40],
        "comparison_union": comparison,
        "named_audits": named,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--selected-injury-variant", choices=INJURY_VARIANTS)
    parser.add_argument("--selected-environment-variant", choices=tuple(ENVIRONMENT_COLUMNS), default="E15")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    from google.cloud import bigquery

    client = bigquery.Client(project=args.project)
    root = f"{args.project}.{args.dataset}"
    baseline_records = [dict(record) for record in client.query(f"""
SELECT
  season,
  candidate_internal_player_id,
  player_name,
  wr_fable_v1_score,
  target_standard_points,
  target_standard_ppg
FROM `{root}.v_wr_fable_v1_backtest_prep`
WHERE wr_fable_v1_score IS NOT NULL AND target_available
ORDER BY season, wr_fable_v1_score DESC
""").result()]
    modified_records = [dict(record) for record in client.query(f"""
SELECT
  season,
  variant_id,
  candidate_internal_player_id,
  player_name,
  source_team,
  destination_team,
  team_changed,
  source_environment_score,
  destination_environment_score,
  environment_delta,
  injury_candidate_score,
  e15_adjustment,
  e25_adjustment,
  e40_adjustment,
  injury_e15_score,
  injury_e25_score,
  injury_e40_score,
  target_standard_points,
  target_standard_ppg,
  target_standard_wr_rank
FROM `{root}.v_wr_fable_v1d_backtest_prep`
WHERE target_available
ORDER BY season, variant_id, injury_candidate_score DESC
""").result()]

    baseline = evaluate_variant(baseline_records, "wr_fable_v1_score")
    assert_baseline_reproduced(baseline["aggregate"])
    injury_results = {}
    for variant in INJURY_VARIANTS:
        candidate_records = [record for record in modified_records if record["variant_id"] == variant]
        evaluated = evaluate_variant(candidate_records, "injury_candidate_score")
        evaluated["guardrails"] = guardrails(evaluated["aggregate"], baseline["aggregate"])
        evaluated["all_guardrails_pass"] = all(evaluated["guardrails"].values())
        injury_results[variant] = evaluated

    result: dict[str, Any] = {
        "baseline_reproduced": True,
        "baseline": baseline,
        "injury_variants": injury_results,
    }

    if args.selected_injury_variant:
        selected_records = [
            record for record in modified_records
            if record["variant_id"] == args.selected_injury_variant
        ]
        environment_results = {}
        movement = {}
        for variant, score_column in ENVIRONMENT_COLUMNS.items():
            evaluated = evaluate_variant(selected_records, score_column)
            evaluated["guardrails"] = guardrails(evaluated["aggregate"], baseline["aggregate"])
            evaluated["all_guardrails_pass"] = all(evaluated["guardrails"].values())
            environment_results[variant] = evaluated
            movement[variant] = movement_audit(selected_records, score_column)

        current_records = [dict(record) for record in client.query(f"""
SELECT
  candidate_internal_player_id,
  player_name,
  source_team,
  sleeper_current_team,
  old_fable_rank,
  injury_candidate_rank,
  injury_e15_rank,
  injury_e25_rank,
  injury_e40_rank,
  current_standard_rank,
  games_played,
  routes_run,
  prior_season_available,
  prior_season_weight,
  rookie_limited_sample_flag,
  age_availability_component,
  source_environment_score,
  destination_environment_score,
  environment_delta,
  e15_adjustment,
  e25_adjustment,
  e40_adjustment,
  injury_candidate_score,
  sleeper_status,
  sleeper_injury_status,
  sleeper_depth_chart_order
FROM `{root}.v_wr_fable_v1d_current_board`
WHERE variant_id = @variant_id
ORDER BY injury_candidate_rank
""", job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("variant_id", "STRING", args.selected_injury_variant)]
        )).result()]
        result.update(
            {
                "selected_injury_variant": args.selected_injury_variant,
                "environment_variants": environment_results,
                "environment_movement_audit": movement,
                "historical_named_audit": named_historical_audit(selected_records),
                "selected_environment_variant": args.selected_environment_variant,
                "current_review": current_review(current_records, args.selected_environment_variant),
            }
        )

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, default=str, indent=2) + "\n", encoding="utf-8")

    compact = {
        "baseline_reproduced": result["baseline_reproduced"],
        "baseline": result["baseline"]["aggregate"],
        "injury_variants": {
            variant: {
                "aggregate": evaluated["aggregate"],
                "guardrails": evaluated["guardrails"],
                "all_guardrails_pass": evaluated["all_guardrails_pass"],
            }
            for variant, evaluated in injury_results.items()
        },
    }
    if args.selected_injury_variant:
        compact["selected_injury_variant"] = args.selected_injury_variant
        compact["environment_variants"] = {
            variant: {
                "aggregate": evaluated["aggregate"],
                "guardrails": evaluated["guardrails"],
                "all_guardrails_pass": evaluated["all_guardrails_pass"],
                "movement_count": len(result["environment_movement_audit"][variant]),
            }
            for variant, evaluated in result["environment_variants"].items()
        }
    print(json.dumps(compact, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
