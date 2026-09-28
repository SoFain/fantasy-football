"""Run the bounded, read-only RB Fable 01 backtest."""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

from google.cloud import bigquery


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


def ndcg(records: list[dict[str, Any]], cutoff: int = 24) -> float | None:
    predicted = sorted(records, key=lambda row: (-row["rb_fable_01_score"], row["player_name"]))[:cutoff]
    ideal = sorted(records, key=lambda row: (-row["target_standard_ppg"], row["player_name"]))[:cutoff]
    discounted = lambda sequence: sum(max(row["target_standard_ppg"], 0.0) / math.log2(index + 2) for index, row in enumerate(sequence))
    ideal_gain = discounted(ideal)
    return discounted(predicted) / ideal_gain if ideal_gain else None


def pairwise_win_rate(records: list[dict[str, Any]]) -> float | None:
    comparisons = wins = 0
    for left, right in itertools.combinations(records, 2):
        predicted_delta = left["rb_fable_01_score"] - right["rb_fable_01_score"]
        actual_delta = left["target_standard_ppg"] - right["target_standard_ppg"]
        if predicted_delta == 0 or actual_delta == 0:
            continue
        comparisons += 1
        wins += (predicted_delta > 0) == (actual_delta > 0)
    return wins / comparisons if comparisons else None


def pick_band(rank: int) -> int:
    for band, cutoff in enumerate((6, 12, 24, 36)):
        if rank <= cutoff:
            return band
    return 4


def rank_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    predicted = sorted(records, key=lambda row: (-row["rb_fable_01_score"], row["player_name"]))
    actual = sorted(records, key=lambda row: (-row["target_standard_ppg"], -row["target_standard_points"], row["player_name"]))
    actual_ranks = {row["candidate_internal_player_id"]: index for index, row in enumerate(actual, 1)}
    output = []
    for predicted_rank, row in enumerate(predicted, 1):
        enriched = dict(row)
        enriched["predicted_rank"] = predicted_rank
        enriched["actual_cohort_rank"] = actual_ranks[row["candidate_internal_player_id"]]
        output.append(enriched)
    return output


def fold_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = rank_records(records)
    hit_rates = {}
    for cutoff in (6, 12, 24, 36):
        selected = ranked[: min(cutoff, len(ranked))]
        hit_rates[f"top_{cutoff}_hit_rate"] = sum(row["actual_cohort_rank"] <= cutoff for row in selected) / len(selected)
    predicted_top = ranked[: min(24, len(ranked))]
    actual_top = sorted(ranked, key=lambda row: row["actual_cohort_rank"])[: min(24, len(ranked))]
    actual_top_points = sum(row["target_standard_points"] for row in actual_top)
    points_captured = sum(row["target_standard_points"] for row in predicted_top) / actual_top_points if actual_top_points else None
    band_regret = mean(max(0, pick_band(row["actual_cohort_rank"]) - pick_band(row["predicted_rank"])) for row in ranked)
    elite_misses = [row for row in ranked if row["actual_cohort_rank"] <= 12 and row["predicted_rank"] > 24]
    receiving_misses = [row for row in ranked if row["actual_cohort_rank"] <= 24 and row["predicted_rank"] > 24 and ((row.get("standard_receptions") or 0) >= 40 or (row.get("target_share") or 0) >= 10)]
    score_values = [row["rb_fable_01_score"] for row in ranked]
    actual_values = [row["target_standard_ppg"] for row in ranked]
    return {
        **hit_rates,
        "points_captured_rate_at_24": points_captured,
        "ndcg_at_24": ndcg(ranked),
        "pairwise_draft_win_rate": pairwise_win_rate(ranked),
        "pick_band_regret": band_regret,
        "elite_rb_miss_count": len(elite_misses),
        "receiving_back_miss_count": len(receiving_misses),
        "extreme_movement_count": None,
        "score_actual_correlation": pearson(score_values, actual_values),
        "rank_actual_correlation": pearson(rank_values(score_values), rank_values(actual_values)),
        "complete_row_count": len(ranked),
        "top_25": ranked[:25],
        "failed_top_players": [row for row in ranked if row["predicted_rank"] <= 12 and row["actual_cohort_rank"] > 36],
        "elite_misses": elite_misses,
        "receiving_misses": receiving_misses,
        "efficiency_boosted": sorted(ranked, key=lambda row: row.get("efficiency_component") or -999, reverse=True)[:5],
        "age_availability_punished": sorted(ranked, key=lambda row: row.get("age_availability_component") or 0)[:5],
        "receiving_usage_helped": sorted(ranked, key=lambda row: row.get("z_target_share") or -999, reverse=True)[:5],
        "negative_run_risk_watch": sorted(ranked, key=lambda row: row.get("tfl_pct") or -999, reverse=True)[:5],
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


def query_records(client: bigquery.Client, sql: str) -> list[dict[str, Any]]:
    return [dict(row) for row in client.query(sql).result()]


def backtest(project: str, dataset: str, brain_dataset: str) -> dict[str, Any]:
    root = f"{project}.{dataset}"
    brain = f"{project}.{brain_dataset}"
    forward = query_records(client := bigquery.Client(project=project), f"""
SELECT * FROM `{root}.v_rb_fable_01_backtest_prep`
WHERE rb_fable_01_score IS NOT NULL AND target_available
ORDER BY season, rb_fable_01_score DESC
""")
    readiness = query_records(client, f"""
SELECT season AS input_season, target_season, COUNT(*) AS qualified_count,
  COUNTIF(rb_fable_01_score IS NOT NULL) AS complete_score_count,
  COUNTIF(target_available) AS complete_target_count,
  COUNTIF(rb_fable_01_score IS NOT NULL AND target_available) AS complete_score_target_count
FROM `{root}.v_rb_fable_01_backtest_prep`
GROUP BY input_season, target_season ORDER BY input_season
""")
    same_season = query_records(client, f"""
WITH actual AS (
  SELECT season, source_player_key AS target_player_id, COUNT(*) AS target_games,
    SUM(total_fantasy_points) AS target_standard_points,
    SAFE_DIVIDE(SUM(total_fantasy_points), COUNT(*)) AS target_standard_ppg
  FROM `{brain}.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id = 'standard' AND position = 'RB'
    AND season BETWEEN 2022 AND 2025 AND week BETWEEN 1 AND 18
  GROUP BY season, target_player_id
), eligible AS (
  SELECT * FROM actual WHERE target_games >= 6
), ranked AS (
  SELECT *,
    DENSE_RANK() OVER (PARTITION BY season ORDER BY target_standard_ppg DESC, target_standard_points DESC) AS target_standard_rb_rank
  FROM eligible
)
SELECT scored.*, ranked.target_games, ranked.target_standard_points, ranked.target_standard_ppg,
  ranked.target_standard_rb_rank
FROM `{root}.v_rb_fable_01_scored_seasons` AS scored
JOIN ranked
  ON ranked.season = scored.season
 AND ranked.target_player_id = scored.candidate_internal_player_id
WHERE scored.rb_fable_01_score IS NOT NULL
ORDER BY scored.season, scored.rb_fable_01_score DESC
""")

    folds = {}
    for input_season in (2022, 2023, 2024):
        records = [row for row in forward if row["season"] == input_season]
        folds[f"{input_season}_to_{input_season + 1}"] = fold_summary(records)
    summaries = list(folds.values())
    aggregate_fields = ("top_6_hit_rate", "top_12_hit_rate", "top_24_hit_rate", "top_36_hit_rate", "points_captured_rate_at_24", "ndcg_at_24", "pairwise_draft_win_rate", "pick_band_regret")
    aggregate = {f"average_{name}": mean(summary[name] for summary in summaries if summary[name] is not None) for name in aggregate_fields}
    aggregate["total_elite_misses"] = sum(summary["elite_rb_miss_count"] for summary in summaries)
    aggregate["total_complete_rows"] = sum(summary["complete_row_count"] for summary in summaries)

    descriptive = {}
    for season in (2022, 2023, 2024, 2025):
        ranked = rank_records([dict(row, target_season=season) for row in same_season if row["season"] == season])
        descriptive[str(season)] = ranked[:25]
    return {
        "readiness": readiness,
        "forward_folds": folds,
        "aggregate": aggregate,
        "descriptive_top_25": descriptive,
        "baseline_status": {
            "current_pigskin": "HISTORICAL CURRENT PIGSKIN BASELINE UNAVAILABLE",
            "prior_episode": "PRIOR EPISODE FORMULA BASELINE UNAVAILABLE",
        },
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def board_table(records: Iterable[dict[str, Any]], *, forward: bool) -> list[str]:
    lines = ["| Rank | Player | Team | Score | Actual finish | Labels | Actual points | Touches | Rush | Rec | Yards | TD | YAC/rush | EPA/touch | Success | Explosive | 1st down | TFL | Box YPC | Avail | Age penalty | Reason |", "|---:|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for row in records:
        actual_rank = row.get("target_standard_rb_rank") or row.get("actual_cohort_rank")
        labels = "/".join(f"T{cutoff}" for cutoff in (6, 12, 24, 36) if actual_rank is not None and actual_rank <= cutoff) or "-"
        total_yards = (row.get("standard_rush_yards") or 0) + (row.get("standard_receiving_yards") or 0)
        total_td = (row.get("standard_rush_td") or 0) + (row.get("standard_receiving_td") or 0)
        lines.append("| " + " | ".join((
            str(row["predicted_rank"]), row["player_name"], row.get("team") or "-", fmt(row["rb_fable_01_score"]),
            fmt(actual_rank, 0), labels, fmt(row.get("target_standard_points"), 1), fmt(row.get("standard_touches"), 0),
            fmt(row.get("standard_rushes"), 0), fmt(row.get("standard_receptions"), 0), fmt(total_yards, 0), fmt(total_td, 0),
            fmt(row.get("yac_per_rush")), fmt(row.get("epa_per_touch")), fmt(row.get("success_pct"), 1),
            fmt(row.get("explosive_pct"), 1), fmt(row.get("first_down_pct"), 1), fmt(row.get("tfl_pct"), 1),
            fmt(row.get("box_adjusted_ypc")), fmt(row.get("games_played_rate")), fmt(row.get("age_penalty"), 0), reason_for_rank(row)
        )) + " |")
    return lines


def markdown(result: dict[str, Any]) -> str:
    lines = ["# RB Fable 01 Backtest Results", "", "RB Fable 01 is evaluated on prior-season metrics against next-season Standard PPG. The 2022-2025 same-season boards below are descriptive only.", "", "## Forward Predictive Summary", "", "| Fold | Rows | Top 6 | Top 12 | Top 24 | Top 36 | Points captured | NDCG@24 | Pairwise | Band regret | Score corr | Rank corr | Elite misses |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for fold, summary in result["forward_folds"].items():
        lines.append(f"| {fold.replace('_to_', ' to ')} | {summary['complete_row_count']} | {fmt(summary['top_6_hit_rate'])} | {fmt(summary['top_12_hit_rate'])} | {fmt(summary['top_24_hit_rate'])} | {fmt(summary['top_36_hit_rate'])} | {fmt(summary['points_captured_rate_at_24'])} | {fmt(summary['ndcg_at_24'])} | {fmt(summary['pairwise_draft_win_rate'])} | {fmt(summary['pick_band_regret'])} | {fmt(summary['score_actual_correlation'])} | {fmt(summary['rank_actual_correlation'])} | {summary['elite_rb_miss_count']} |")
    lines += ["", "## Predictive Top 25 Boards"]
    for fold, summary in result["forward_folds"].items():
        lines += ["", f"### {fold.replace('_to_', ' to ')}", ""] + board_table(summary["top_25"], forward=True)
    lines += ["", "## Miss And Component Audit"]
    for fold, summary in result["forward_folds"].items():
        lines += ["", f"### {fold.replace('_to_', ' to ')}", ""]
        failed = ", ".join(f"{row['player_name']} (pred {row['predicted_rank']}, cohort actual {row['actual_cohort_rank']})" for row in summary["failed_top_players"]) or "None"
        misses = ", ".join(f"{row['player_name']} (pred {row['predicted_rank']}, cohort actual {row['actual_cohort_rank']})" for row in summary["elite_misses"]) or "None"
        efficiency = ", ".join(row["player_name"] for row in summary["efficiency_boosted"])
        punished = ", ".join(row["player_name"] for row in summary["age_availability_punished"])
        receiving = ", ".join(row["player_name"] for row in summary["receiving_usage_helped"])
        negative_run = ", ".join(row["player_name"] for row in summary["negative_run_risk_watch"])
        lines += [
            f"- Failed predicted top-12: {failed}.",
            f"- Actual elite misses outside predicted top 24: {misses}.",
            f"- Largest efficiency lifts: {efficiency}.",
            f"- Strongest age/availability penalties: {punished}.",
            f"- Strongest receiving-usage support: {receiving}.",
            f"- Highest TFL-risk watch: {negative_run}. TFL is diagnostic only and is not a Fable score component.",
        ]
    lines += ["", "## Same-Season Descriptive Boards", "", "**DESCRIPTIVE ONLY - NOT A FORWARD-LOOKING BACKTEST**"]
    for season, records in result["descriptive_top_25"].items():
        lines += ["", f"### {season}", ""] + board_table(records, forward=False)
    lines += ["", "## Baselines", "", f"- {result['baseline_status']['current_pigskin']}", f"- {result['baseline_status']['prior_episode']}", "", "## Show-Ready Talking Points", "", "- The formula is dominated by role and non-garbage-time volume, as designed.", "- Efficiency is visible but shrunk, so low-volume outliers cannot control the board.", "- Missing red-zone or age inputs fail closed instead of becoming invented zeroes.", "- The honest comparison is against actual outcomes because valid historical baselines are unavailable.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--brain-dataset", default="fantasy_football_brain")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()
    result = backtest(args.project, args.dataset, args.brain_dataset)
    serialized = json.dumps(result, default=str, indent=2)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(serialized + "\n", encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"readiness": result["readiness"], "aggregate": result["aggregate"], "baseline_status": result["baseline_status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
