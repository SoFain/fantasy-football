"""Run the bounded, read-only TE Fable v1.0a backtest."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path
from statistics import mean
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SCORE = "comparison_score"


VARIANTS = {
    "te_fable_v1a": "te_fable_v1a_score",
    "te_fable_v1a_no_man": "te_fable_v1a_no_man_score",
    "current_pigskin_same_cohort": "current_pigskin_candidate_score_v1",
    "prior_year_standard_ppg": "source_standard_ppg",
}
AGGREGATE_FIELDS = (
    "top_6_precision",
    "top_12_precision",
    "spearman_rank_correlation",
    "score_correlation",
    "points_captured_at_12",
    "ndcg_at_12",
    "pairwise_draft_win_rate",
    "band_regret",
)


def rank_values(values: list[float]) -> list[float]:
    ordered = sorted(range(len(values)), key=lambda index: values[index], reverse=True)
    ranks = [0.0] * len(values)
    cursor = 0
    while cursor < len(ordered):
        end = cursor + 1
        while end < len(ordered) and values[ordered[end]] == values[ordered[cursor]]:
            end += 1
        average_rank = (cursor + 1 + end) / 2
        for offset in range(cursor, end):
            ranks[ordered[offset]] = average_rank
        cursor = end
    return ranks


def pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) < 2 or len(left) != len(right):
        return None
    left_mean, right_mean = mean(left), mean(right)
    numerator = sum((x-left_mean)*(y-right_mean) for x,y in zip(left,right))
    denominator = math.sqrt(sum((x-left_mean)**2 for x in left)*sum((y-right_mean)**2 for y in right))
    return numerator/denominator if denominator else None


def pairwise_win_rate(records: list[dict[str, Any]]) -> float | None:
    comparisons = wins = 0
    for left, right in itertools.combinations(records, 2):
        predicted = left[SCORE]-right[SCORE]
        actual = left["target_standard_ppg"]-right["target_standard_ppg"]
        if predicted == 0 or actual == 0:
            continue
        comparisons += 1
        wins += (predicted > 0) == (actual > 0)
    return wins/comparisons if comparisons else None


def rank_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    predicted = sorted(records,key=lambda row:(-row[SCORE],row["player_name"]))
    actual = sorted(records,key=lambda row:(-row["target_standard_ppg"],-row["target_standard_points"],row["player_name"]))
    actual_ranks = {row["candidate_internal_player_id"]: index for index,row in enumerate(actual,1)}
    return [dict(row,predicted_rank=index,actual_cohort_rank=actual_ranks[row["candidate_internal_player_id"]]) for index,row in enumerate(predicted,1)]


def ndcg(records: list[dict[str, Any]], cutoff: int) -> float | None:
    predicted = sorted(records,key=lambda row:(-row[SCORE],row["player_name"]))[:cutoff]
    ideal = sorted(records,key=lambda row:(-row["target_standard_ppg"],row["player_name"]))[:cutoff]
    gain = lambda sequence: sum(max(row["target_standard_ppg"],0)/math.log2(index+2) for index,row in enumerate(sequence))
    denominator = gain(ideal)
    return gain(predicted)/denominator if denominator else None


def pick_band(rank: int) -> int:
    for band, cutoff in enumerate((6,12,24,36)):
        if rank <= cutoff:
            return band
    return 4


def points_captured(ranked: list[dict[str, Any]], cutoff: int) -> float | None:
    predicted = ranked[:min(cutoff,len(ranked))]
    actual = sorted(ranked,key=lambda row:row["actual_cohort_rank"])[:min(cutoff,len(ranked))]
    denominator = sum(row["target_standard_points"] for row in actual)
    return sum(row["target_standard_points"] for row in predicted)/denominator if denominator else None


def fold_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = rank_records(records)
    hit_rates = {}
    for cutoff in (6,12,24,36):
        selected = ranked[:min(cutoff,len(ranked))]
        hit_rates[f"top_{cutoff}_precision"] = sum(row["actual_cohort_rank"] <= cutoff for row in selected)/len(selected)
    scores = [row[SCORE] for row in ranked]
    actuals = [row["target_standard_ppg"] for row in ranked]
    return {
        **hit_rates,
        "complete_row_count":len(ranked),
        "spearman_rank_correlation":pearson(rank_values(scores),rank_values(actuals)),
        "score_correlation":pearson(scores,actuals),
        "points_captured_at_12":points_captured(ranked,12),
        "points_captured_at_24":points_captured(ranked,24),
        "ndcg_at_12":ndcg(ranked,12),
        "ndcg_at_24":ndcg(ranked,24),
        "pairwise_draft_win_rate":pairwise_win_rate(ranked),
        "band_regret":mean(max(0,pick_band(row["actual_cohort_rank"])-pick_band(row["predicted_rank"])) for row in ranked),
        "elite_wr_miss_count":sum(1 for row in ranked if row["actual_cohort_rank"] <= 12 and row["predicted_rank"] > 24),
        "predicted_top_12_bust_count":sum(1 for row in ranked if row["predicted_rank"] <= 12 and row["actual_cohort_rank"] > 36),
        "top_24":ranked[:24],
        "elite_misses":[row for row in ranked if row["actual_cohort_rank"] <= 18 and row["predicted_rank"] > 24],
    }


def evaluate_variant(rows: list[dict[str, Any]], score_column: str) -> dict[str, Any]:
    folds: dict[str, Any] = {}
    for input_season in (2022, 2023, 2024):
        records = []
        for row in rows:
            if row["season"] != input_season or row.get(score_column) is None:
                continue
            aliased = dict(row)
            aliased[SCORE] = row[score_column]
            records.append(aliased)
        folds[f"{input_season}_to_{input_season + 1}"] = fold_summary(records)
    summaries = list(folds.values())
    aggregate = {
        f"average_{field}": mean(summary[field] for summary in summaries if summary[field] is not None)
        for field in AGGREGATE_FIELDS
    }
    aggregate["total_complete_rows"] = sum(summary["complete_row_count"] for summary in summaries)
    aggregate["total_top12_busts"] = sum(summary["predicted_top_12_bust_count"] for summary in summaries)
    return {"folds": folds, "aggregate": aggregate}


def backtest(project: str, dataset: str) -> dict[str, Any]:
    from google.cloud import bigquery

    client = bigquery.Client(project=project)
    root = f"{project}.{dataset}"
    rows = [dict(row) for row in client.query(f"""
SELECT * FROM `{root}.v_te_fable_v1a_backtest_prep`
WHERE target_available
ORDER BY season, te_fable_v1a_score DESC
""").result()]
    result = {name: evaluate_variant(rows, column) for name, column in VARIANTS.items()}
    exact_overlap = [
        row for row in rows
        if row.get("te_fable_v1a_no_man_score") is not None
        and row.get("current_pigskin_candidate_score_v1") is not None
    ]
    result["same_cohort"] = {
        "te_fable_v1a_no_man": evaluate_variant(exact_overlap, "te_fable_v1a_no_man_score"),
        "current_pigskin_candidate_score_v1": evaluate_variant(exact_overlap, "current_pigskin_candidate_score_v1"),
    }
    result["readiness"] = [dict(row) for row in client.query(f"""
SELECT season AS input_season, season + 1 AS target_season,
  COUNT(*) AS qualified_count,
  COUNTIF(te_fable_v1a_score IS NOT NULL AND target_available) AS complete_count
FROM `{root}.v_te_fable_v1a_backtest_prep`
GROUP BY input_season, target_season
ORDER BY input_season
""").result()]
    result["current_board_top35"] = [dict(row) for row in client.query(f"""
SELECT *,
  RANK() OVER (ORDER BY te_fable_v1a_score DESC) AS fable_rank,
  RANK() OVER (ORDER BY te_fable_v1a_no_man_score DESC) AS no_man_rank
FROM `{root}.v_te_fable_v1a_scored_seasons`
WHERE season = 2025 AND te_fable_v1a_score IS NOT NULL
ORDER BY te_fable_v1a_score DESC
LIMIT 35
""").result()]
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    result = backtest(args.project, args.dataset)
    serialized = json.dumps(result, default=str, indent=2)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(serialized + "\n", encoding="utf-8")
    compact = {
        "readiness": result["readiness"],
        "variants": {
            name: {
                "aggregate": value["aggregate"],
                "folds": {
                    fold: {key: metric for key, metric in summary.items() if not isinstance(metric, list)}
                    for fold, summary in value["folds"].items()
                },
            }
            for name, value in result.items()
            if name in VARIANTS
        },
        "same_cohort": {
            name: {
                "aggregate": value["aggregate"],
                "folds": {
                    fold: {key: metric for key, metric in summary.items() if not isinstance(metric, list)}
                    for fold, summary in value["folds"].items()
                },
            }
            for name, value in result["same_cohort"].items()
        },
    }
    print(json.dumps(compact, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
