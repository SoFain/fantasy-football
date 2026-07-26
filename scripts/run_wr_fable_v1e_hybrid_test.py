"""Test the exclusion-only WR Fable hybrid recommended after Phase 35.1D."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_wr_fable_v1d_tests import (
    actual_rank_map,
    assert_baseline_reproduced,
    evaluate_variant,
    guardrails,
    rank_map,
)


AUDIT_NAMES = {
    "Malik Nabers",
    "Tyreek Hill",
    "Rashee Rice",
    "Mike Evans",
    "Garrett Wilson",
    "Chris Godwin",
    "Christian Watson",
    "Tetairoa McMillan",
    "Emeka Egbuka",
}


def current_review(records: list[dict[str, Any]]) -> dict[str, Any]:
    baseline_top40 = sorted(
        (record for record in records if record["old_fable_rank"] is not None),
        key=lambda record: record["old_fable_rank"],
    )[:40]
    hybrid_top40 = sorted(records, key=lambda record: record["exclusion_only_rank"])[:40]
    included_ids = {
        record["candidate_internal_player_id"] for record in baseline_top40 + hybrid_top40
    }
    comparison = sorted(
        (record for record in records if record["candidate_internal_player_id"] in included_ids),
        key=lambda record: min(
            value
            for value in (record["old_fable_rank"], record["exclusion_only_rank"])
            if value is not None
        ),
    )
    return {
        "baseline_top40_names": [record["player_name"] for record in baseline_top40],
        "hybrid_top40_names": [record["player_name"] for record in hybrid_top40],
        "comparison_union": comparison,
        "named_audits": {
            record["player_name"]: record
            for record in records
            if record["player_name"] in AUDIT_NAMES
        },
    }


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
    hybrid_records = [dict(record) for record in client.query(f"""
SELECT
  season,
  candidate_internal_player_id,
  player_name,
  exclusion_only_score,
  baseline_v1_score_available,
  prior_season_weight,
  rookie_limited_sample_flag,
  target_standard_points,
  target_standard_ppg,
  target_standard_wr_rank
FROM `{root}.v_wr_fable_v1d_backtest_prep`
WHERE variant_id = 'I4'
  AND target_available
  AND exclusion_only_score IS NOT NULL
ORDER BY season, exclusion_only_score DESC
""").result()]

    preservation = next(iter(client.query(f"""
SELECT
  COUNTIF(
    baseline_v1_score_available
    AND ABS(exclusion_only_score - baseline_v1_score) > 1e-12
  ) AS changed_baseline_score_count
FROM `{root}.v_wr_fable_v1d_scored_seasons`
WHERE variant_id = 'I4' AND season BETWEEN 2022 AND 2025
""").result()))
    if preservation["changed_baseline_score_count"] != 0:
        raise RuntimeError("Exclusion-only hybrid changed an existing WR Fable v1 score")

    baseline = evaluate_variant(baseline_records, "wr_fable_v1_score")
    assert_baseline_reproduced(baseline["aggregate"])
    hybrid = evaluate_variant(hybrid_records, "exclusion_only_score")
    hybrid["guardrails"] = guardrails(hybrid["aggregate"], baseline["aggregate"])
    hybrid["all_guardrails_pass"] = all(hybrid["guardrails"].values())

    baseline_keys = {
        (record["season"], record["candidate_internal_player_id"])
        for record in baseline_records
    }
    fixed_cohort_records = [
        record for record in hybrid_records
        if (record["season"], record["candidate_internal_player_id"]) in baseline_keys
    ]
    fixed_cohort = evaluate_variant(fixed_cohort_records, "exclusion_only_score")
    for field, baseline_value in baseline["aggregate"].items():
        fixed_value = fixed_cohort["aggregate"][field]
        if isinstance(baseline_value, float):
            if abs(fixed_value - baseline_value) > 1e-12:
                raise RuntimeError(f"Fixed-cohort hybrid mismatch for {field}")
        elif fixed_value != baseline_value:
            raise RuntimeError(f"Fixed-cohort hybrid mismatch for {field}")

    predicted_ranks = {}
    actual_ranks = {}
    for season in (2022, 2023, 2024):
        fold_records = [record for record in hybrid_records if record["season"] == season]
        predicted_ranks[season] = rank_map(fold_records, "exclusion_only_score")
        actual_ranks[season] = actual_rank_map(fold_records)
    added_records = [
        {
            "season": record["season"],
            "player_name": record["player_name"],
            "prior_season_weight": record["prior_season_weight"],
            "rookie_limited_sample_flag": record["rookie_limited_sample_flag"],
            "target_standard_wr_rank": record["target_standard_wr_rank"],
            "predicted_cohort_rank": predicted_ranks[record["season"]][record["candidate_internal_player_id"]],
            "actual_cohort_rank": actual_ranks[record["season"]][record["candidate_internal_player_id"]],
        }
        for record in hybrid_records
        if (record["season"], record["candidate_internal_player_id"]) not in baseline_keys
    ]

    current_records = [dict(record) for record in client.query(f"""
SELECT
  candidate_internal_player_id,
  player_name,
  old_fable_rank,
  exclusion_only_rank,
  current_standard_rank,
  games_played,
  routes_run,
  prior_season_available,
  prior_season_weight,
  rookie_limited_sample_flag,
  age_availability_component,
  source_team,
  sleeper_current_team,
  sleeper_status,
  sleeper_injury_status,
  sleeper_depth_chart_order,
  baseline_v1_score_available,
  baseline_v1_score,
  injury_candidate_score,
  exclusion_only_score
FROM `{root}.v_wr_fable_v1d_current_board`
WHERE variant_id = 'I4'
ORDER BY exclusion_only_rank
""").result()]

    result = {
        "baseline_reproduced": True,
        "changed_baseline_score_count": preservation["changed_baseline_score_count"],
        "baseline": baseline,
        "fixed_cohort": fixed_cohort,
        "hybrid": hybrid,
        "added_records": added_records,
        "current_review": current_review(current_records),
    }
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, default=str, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "baseline_reproduced": result["baseline_reproduced"],
        "changed_baseline_score_count": result["changed_baseline_score_count"],
        "baseline": baseline["aggregate"],
        "fixed_cohort": fixed_cohort["aggregate"],
        "hybrid": {
            "aggregate": hybrid["aggregate"],
            "guardrails": hybrid["guardrails"],
            "all_guardrails_pass": hybrid["all_guardrails_pass"],
        },
        "added_records": added_records,
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
