"""Test prior-qualified v1 score carry-forward for previously excluded WRs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_wr_fable_v1d_tests import (
    actual_rank_map,
    assert_baseline_reproduced,
    evaluate_variant,
    guardrails,
    rank_map,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_advanced_metrics")
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
    replacement_records = [dict(record) for record in client.query(f"""
SELECT
  season,
  candidate_internal_player_id,
  player_name,
  carry_forward_replacement_score,
  baseline_v1_score_available,
  prior_v1_score,
  prior_v1_age_availability_component,
  age_availability_component,
  prior_score_carry_forward_score,
  prior_score_carry_forward_eligible,
  target_standard_points,
  target_standard_ppg,
  target_standard_wr_rank
FROM `{root}.v_wr_fable_v1d_backtest_prep`
WHERE variant_id = 'I4'
  AND target_available
  AND carry_forward_replacement_score IS NOT NULL
ORDER BY season, carry_forward_replacement_score DESC
""").result()]
    rookie_review_records = [dict(record) for record in client.query(f"""
SELECT
  season,
  candidate_internal_player_id,
  player_name,
  rookie_review_score,
  target_standard_wr_rank
FROM `{root}.v_wr_fable_v1d_backtest_prep`
WHERE variant_id = 'I4'
  AND target_available
  AND rookie_review_score IS NOT NULL
ORDER BY season, rookie_review_score DESC
""").result()]

    changed_score_count = next(iter(client.query(f"""
SELECT COUNTIF(
  baseline_v1_score_available
  AND ABS(carry_forward_replacement_score - baseline_v1_score) > 1e-12
) AS changed_score_count
FROM `{root}.v_wr_fable_v1d_scored_seasons`
WHERE variant_id = 'I4' AND season BETWEEN 2022 AND 2025
""").result()))["changed_score_count"]
    if changed_score_count != 0:
        raise RuntimeError("Carry-forward replacement changed an existing v1 score")

    baseline = evaluate_variant(baseline_records, "wr_fable_v1_score")
    assert_baseline_reproduced(baseline["aggregate"])
    replacement = evaluate_variant(replacement_records, "carry_forward_replacement_score")
    replacement["guardrails"] = guardrails(replacement["aggregate"], baseline["aggregate"])
    replacement["all_guardrails_pass"] = all(replacement["guardrails"].values())

    baseline_keys = {
        (record["season"], record["candidate_internal_player_id"])
        for record in baseline_records
    }
    fixed_cohort = evaluate_variant(
        [
            record for record in replacement_records
            if (record["season"], record["candidate_internal_player_id"]) in baseline_keys
        ],
        "carry_forward_replacement_score",
    )
    for field, baseline_value in baseline["aggregate"].items():
        fixed_value = fixed_cohort["aggregate"][field]
        if isinstance(baseline_value, float):
            if abs(fixed_value - baseline_value) > 1e-12:
                raise RuntimeError(f"Fixed-cohort carry-forward mismatch for {field}")
        elif fixed_value != baseline_value:
            raise RuntimeError(f"Fixed-cohort carry-forward mismatch for {field}")

    predicted_ranks = {}
    actual_ranks = {}
    for season in (2022, 2023, 2024):
        fold_records = [record for record in replacement_records if record["season"] == season]
        predicted_ranks[season] = rank_map(fold_records, "carry_forward_replacement_score")
        actual_ranks[season] = actual_rank_map(fold_records)
    added_records = []
    for record in replacement_records:
        key = (record["season"], record["candidate_internal_player_id"])
        if key in baseline_keys:
            continue
        added_records.append({
            **record,
            "predicted_cohort_rank": predicted_ranks[record["season"]][record["candidate_internal_player_id"]],
            "actual_cohort_rank": actual_ranks[record["season"]][record["candidate_internal_player_id"]],
        })

    current_records = [dict(record) for record in client.query(f"""
SELECT
  candidate_internal_player_id,
  player_name,
  old_fable_rank,
  carry_forward_replacement_rank,
  current_standard_rank,
  games_played,
  routes_run,
  source_team,
  sleeper_current_team,
  sleeper_status,
  sleeper_injury_status,
  sleeper_depth_chart_order,
  baseline_v1_score_available,
  prior_v1_score,
  prior_v1_age_availability_component,
  age_availability_component,
  prior_score_carry_forward_score,
  carry_forward_replacement_score
FROM `{root}.v_wr_fable_v1d_current_board`
WHERE variant_id = 'I4'
  AND carry_forward_replacement_score IS NOT NULL
ORDER BY carry_forward_replacement_rank
""").result()]
    baseline_top40 = sorted(
        (record for record in current_records if record["old_fable_rank"] is not None),
        key=lambda record: record["old_fable_rank"],
    )[:40]
    replacement_top40 = sorted(
        current_records, key=lambda record: record["carry_forward_replacement_rank"]
    )[:40]
    included_ids = {
        record["candidate_internal_player_id"]
        for record in baseline_top40 + replacement_top40
    }
    comparison = sorted(
        (record for record in current_records if record["candidate_internal_player_id"] in included_ids),
        key=lambda record: min(
            value
            for value in (record["old_fable_rank"], record["carry_forward_replacement_rank"])
            if value is not None
        ),
    )

    result = {
        "baseline_reproduced": True,
        "changed_baseline_score_count": changed_score_count,
        "baseline": baseline,
        "fixed_cohort": fixed_cohort,
        "replacement": replacement,
        "added_records": added_records,
        "rookie_review_records": rookie_review_records,
        "current_review": {
            "baseline_top40_names": [record["player_name"] for record in baseline_top40],
            "replacement_top40_names": [record["player_name"] for record in replacement_top40],
            "comparison_union": comparison,
        },
    }
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, default=str, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "baseline_reproduced": result["baseline_reproduced"],
        "changed_baseline_score_count": changed_score_count,
        "baseline": baseline["aggregate"],
        "fixed_cohort": fixed_cohort["aggregate"],
        "replacement": {
            "aggregate": replacement["aggregate"],
            "guardrails": replacement["guardrails"],
            "all_guardrails_pass": replacement["all_guardrails_pass"],
        },
        "added_records": added_records,
        "rookie_review_count": len(rookie_review_records),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
