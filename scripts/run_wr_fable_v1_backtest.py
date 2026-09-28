"""Run the bounded, read-only WR Fable v1 backtest and current-board extract."""

from __future__ import annotations

import argparse
import json
import math
import sys
from itertools import combinations
from pathlib import Path
from statistics import mean
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_rb_fable_01_backtest import pairwise_win_rate as _rb_pairwise  # noqa: F401 (parity reference)


SCORE = "wr_fable_v1_score"


def rank_values(values: list[float], *, reverse: bool = True) -> list[float]:
    ordered = sorted(range(len(values)), key=lambda index: values[index], reverse=reverse)
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
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right))
    denominator = math.sqrt(sum((x - left_mean) ** 2 for x in left) * sum((y - right_mean) ** 2 for y in right))
    return numerator / denominator if denominator else None


def spearman(left: list[float], right: list[float]) -> float | None:
    return pearson(rank_values(left), rank_values(right))


def pairwise_win_rate(records: list[dict[str, Any]]) -> float | None:
    comparisons = wins = 0
    for a, b in combinations(records, 2):
        predicted_delta = a[SCORE] - b[SCORE]
        actual_delta = a["target_standard_ppg"] - b["target_standard_ppg"]
        if predicted_delta == 0 or actual_delta == 0:
            continue
        comparisons += 1
        wins += (predicted_delta > 0) == (actual_delta > 0)
    return wins / comparisons if comparisons else None


def ndcg(records: list[dict[str, Any]], cutoff: int) -> float | None:
    predicted = sorted(records, key=lambda row: (-row[SCORE], row["player_name"]))[:cutoff]
    ideal = sorted(records, key=lambda row: (-row["target_standard_ppg"], row["player_name"]))[:cutoff]
    discounted = lambda seq: sum(max(row["target_standard_ppg"], 0.0) / math.log2(i + 2) for i, row in enumerate(seq))
    ideal_gain = discounted(ideal)
    return discounted(predicted) / ideal_gain if ideal_gain else None


def pick_band(rank: int) -> int:
    for band, cutoff in enumerate((6, 12, 24, 36)):
        if rank <= cutoff:
            return band
    return 4


def rank_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    predicted = sorted(records, key=lambda row: (-row[SCORE], row["player_name"]))
    actual = sorted(records, key=lambda row: (-row["target_standard_ppg"], -row["target_standard_points"], row["player_name"]))
    actual_ranks = {row["candidate_internal_player_id"]: index for index, row in enumerate(actual, 1)}
    output = []
    for predicted_rank, row in enumerate(predicted, 1):
        enriched = dict(row)
        enriched["predicted_rank"] = predicted_rank
        enriched["actual_cohort_rank"] = actual_ranks[row["candidate_internal_player_id"]]
        output.append(enriched)
    return output


def points_captured(ranked: list[dict[str, Any]], cutoff: int) -> float | None:
    predicted_top = ranked[: min(cutoff, len(ranked))]
    actual_top = sorted(ranked, key=lambda row: row["actual_cohort_rank"])[: min(cutoff, len(ranked))]
    denominator = sum(row["target_standard_points"] for row in actual_top)
    return sum(row["target_standard_points"] for row in predicted_top) / denominator if denominator else None


def fold_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = rank_records(records)
    hit_rates = {}
    for cutoff in (6, 12, 24, 36):
        selected = ranked[: min(cutoff, len(ranked))]
        hit_rates[f"top_{cutoff}_precision"] = sum(row["actual_cohort_rank"] <= cutoff for row in selected) / len(selected)
    scores = [row[SCORE] for row in ranked]
    actuals = [row["target_standard_ppg"] for row in ranked]
    return {
        **hit_rates,
        "complete_row_count": len(ranked),
        "spearman_rank_correlation": spearman(scores, actuals),
        "score_correlation": pearson(scores, actuals),
        "points_captured_at_12": points_captured(ranked, 12),
        "points_captured_at_24": points_captured(ranked, 24),
        "ndcg_at_12": ndcg(ranked, 12),
        "ndcg_at_24": ndcg(ranked, 24),
        "pairwise_draft_win_rate": pairwise_win_rate(ranked),
        "band_regret": mean(max(0, pick_band(row["actual_cohort_rank"]) - pick_band(row["predicted_rank"])) for row in ranked),
        "elite_misses": [row for row in ranked if row["actual_cohort_rank"] <= 12 and row["predicted_rank"] > 24],
        "elite_wr_miss_count": sum(1 for row in ranked if row["actual_cohort_rank"] <= 12 and row["predicted_rank"] > 24),
        "top12_busts": [row for row in ranked if row["predicted_rank"] <= 12 and row["actual_cohort_rank"] > 36],
        "predicted_top_12_bust_count": sum(1 for row in ranked if row["predicted_rank"] <= 12 and row["actual_cohort_rank"] > 36),
        "top_24": ranked[:24],
    }


def reason_for_rank(row: dict[str, Any]) -> str:
    components = {
        "opportunity": row.get("opportunity_component"),
        "efficiency": row.get("efficiency_component"),
        "TD blend": row.get("scoring_component"),
        "age/availability": row.get("age_availability_component"),
    }
    available = {name: value for name, value in components.items() if value is not None}
    if not available:
        return "components unavailable"
    leader = max(available, key=available.get)
    return f"{leader} led ({available[leader]:+.3f})"


def backtest(project: str, dataset: str) -> dict[str, Any]:
    from google.cloud import bigquery

    client = bigquery.Client(project=project)
    root = f"{project}.{dataset}"
    forward = [dict(row) for row in client.query(f"""
SELECT * FROM `{root}.v_wr_fable_v1_backtest_prep`
WHERE {SCORE} IS NOT NULL AND target_available
ORDER BY season, {SCORE} DESC
""").result()]
    readiness = [dict(row) for row in client.query(f"""
SELECT season AS input_season, target_season, COUNT(*) AS qualified_count,
  COUNTIF({SCORE} IS NOT NULL) AS complete_score_count,
  COUNTIF(target_available) AS complete_target_count,
  COUNTIF({SCORE} IS NOT NULL AND target_available) AS complete_score_target_count
FROM `{root}.v_wr_fable_v1_backtest_prep`
GROUP BY input_season, target_season ORDER BY input_season
""").result()]
    current_board = [dict(row) for row in client.query(f"""
SELECT *, RANK() OVER (ORDER BY {SCORE} DESC) AS fable_rank
FROM `{root}.v_wr_fable_v1_scored_seasons`
WHERE season = 2025 AND {SCORE} IS NOT NULL
ORDER BY {SCORE} DESC
LIMIT 40
""").result()]

    folds = {}
    for input_season in (2022, 2023, 2024):
        records = [row for row in forward if row["season"] == input_season]
        folds[f"{input_season}_to_{input_season + 1}"] = fold_summary(records)
    summaries = list(folds.values())
    aggregate_fields = (
        "top_6_precision", "top_12_precision", "top_24_precision", "top_36_precision",
        "spearman_rank_correlation", "score_correlation", "points_captured_at_12", "points_captured_at_24",
        "ndcg_at_12", "ndcg_at_24", "pairwise_draft_win_rate", "band_regret",
    )
    aggregate = {f"average_{name}": mean(s[name] for s in summaries if s[name] is not None) for name in aggregate_fields}
    aggregate["total_elite_misses"] = sum(s["elite_wr_miss_count"] for s in summaries)
    aggregate["total_top12_busts"] = sum(s["predicted_top_12_bust_count"] for s in summaries)
    aggregate["total_complete_rows"] = sum(s["complete_row_count"] for s in summaries)
    return {"readiness": readiness, "forward_folds": folds, "aggregate": aggregate, "current_board_top40": current_board}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    result = backtest(args.project, args.dataset)
    for fold in result["forward_folds"].values():
        for row in fold["top_24"]:
            row["reason"] = reason_for_rank(row)
    for row in result["current_board_top40"]:
        row["reason"] = reason_for_rank(row)
    serialized = json.dumps(result, default=str, indent=2)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(serialized + "\n", encoding="utf-8")
    compact = {
        "readiness": result["readiness"],
        "aggregate": result["aggregate"],
        "folds": {
            name: {key: value for key, value in fold.items() if not isinstance(value, list)}
            for name, fold in result["forward_folds"].items()
        },
    }
    print(json.dumps(compact, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
