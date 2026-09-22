"""Test fast, leakage-safe transfers of locked Fable formulas to next-season PPR outcomes."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean
import sys
from typing import Any

from google.cloud import bigquery

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_rb_fable_01_backtest import pairwise_win_rate, pearson, rank_values


def ndcg(rows: list[dict[str, Any]], cutoff: int = 24) -> float | None:
    predicted = sorted(rows, key=lambda row: (-row["score"], row["player_name"]))[:cutoff]
    ideal = sorted(rows, key=lambda row: (-row["target_ppg"], row["player_name"]))[:cutoff]
    gain = lambda values: sum(max(row["target_ppg"], 0) / math.log2(index + 2) for index, row in enumerate(values))
    denominator = gain(ideal)
    return gain(predicted) / denominator if denominator else None


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    predicted = sorted(rows, key=lambda row: (-row["score"], row["player_name"]))
    actual = sorted(rows, key=lambda row: (-row["target_ppg"], row["player_name"]))
    actual_rank = {row["player_id"]: rank for rank, row in enumerate(actual, 1)}
    ranked = [{**row, "predicted_rank": rank, "actual_rank": actual_rank[row["player_id"]]} for rank, row in enumerate(predicted, 1)]
    top12 = ranked[:12]
    top24 = ranked[:24]
    actual12 = actual[:12]
    actual24 = actual[:24]
    score_values = [row["score"] for row in ranked]
    actual_values = [row["target_ppg"] for row in ranked]
    return {
        "rows": len(ranked),
        "spearman": pearson(rank_values(score_values), rank_values(actual_values)),
        "pairwise": pairwise_win_rate([{"rb_fable_01_score": row["score"], "target_standard_ppg": row["target_ppg"]} for row in ranked]),
        "top12_precision": sum(row["actual_rank"] <= 12 for row in top12) / len(top12),
        "top24_precision": sum(row["actual_rank"] <= 24 for row in top24) / len(top24),
        "points_at_12": sum(row["target_points"] for row in top12) / sum(row["target_points"] for row in actual12),
        "points_at_24": sum(row["target_points"] for row in top24) / sum(row["target_points"] for row in actual24),
        "ndcg_at_24": ndcg(ranked),
        "elite_misses": sum(row["actual_rank"] <= 12 and row["predicted_rank"] > 24 for row in ranked),
        "top12_busts": sum(row["predicted_rank"] <= 12 and row["actual_rank"] > 36 for row in ranked),
    }


def evaluate(rows: list[dict[str, Any]], score_field: str) -> dict[str, Any]:
    folds = {}
    for season in (2022, 2023, 2024):
        fold_rows = [{**row, "score": row[score_field]} for row in rows if row["season"] == season and row.get(score_field) is not None]
        folds[f"{season}_to_{season + 1}"] = summarize(fold_rows)
    aggregate_fields = ("spearman", "pairwise", "top12_precision", "top24_precision", "points_at_12", "points_at_24", "ndcg_at_24")
    aggregate = {f"average_{field}": mean(fold[field] for fold in folds.values()) for field in aggregate_fields}
    aggregate["total_elite_misses"] = sum(fold["elite_misses"] for fold in folds.values())
    aggregate["total_top12_busts"] = sum(fold["top12_busts"] for fold in folds.values())
    return {"aggregate": aggregate, "folds": folds}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    parser.add_argument("--metrics-dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--scoring-profile", choices=("ppr", "half_ppr", "gng_keeper"), default="ppr")
    parser.add_argument("--json-output", type=Path, default=Path("output/ppr-fable-v1-transfer-backtest.json"))
    args = parser.parse_args()
    client = bigquery.Client(project=args.project)
    specs = {
        "RB": ("v_rb_fable_01_scored_seasons", "rb_fable_01_score"),
        "WR": ("v_wr_fable_v1_scored_seasons", "wr_fable_v1_score"),
        "TE": ("v_te_fable_v1a_scored_seasons", "te_fable_v1a_no_man_score"),
    }
    result = {}
    for position, (view, base_score) in specs.items():
        extra = """
  scored.rb_fable_01_score + 0.03 * scored.z_target_share - 0.03 * scored.z_ngt_tpg AS rb_ppr_shift_003,
  scored.rb_fable_01_score + 0.05 * scored.z_target_share - 0.05 * scored.z_ngt_tpg AS rb_ppr_shift_005,
  scored.rb_fable_01_score + 0.01 * scored.z_target_share - 0.01 * scored.z_ngt_tpg AS rb_ppr_shift_001,
  scored.rb_fable_01_score + 0.02 * scored.z_target_share - 0.02 * scored.z_ngt_tpg AS rb_ppr_shift_002,
  scored.rb_fable_01_score + 0.04 * scored.z_target_share - 0.04 * scored.z_ngt_tpg AS rb_ppr_shift_004,
""" if position == "RB" else ""
        rows = [dict(row) for row in client.query(f"""
WITH target AS (
  SELECT season, source_player_key AS player_id, COUNT(*) AS games,
    SUM(total_fantasy_points) AS target_points,
    SAFE_DIVIDE(SUM(total_fantasy_points), COUNT(*)) AS target_ppg
  FROM `{args.project}.{args.dataset}.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id='{args.scoring_profile}' AND position='{position}' AND season BETWEEN 2023 AND 2025 AND week BETWEEN 1 AND 18
  GROUP BY season, player_id HAVING games >= 6
)
SELECT scored.season, scored.candidate_internal_player_id AS player_id, scored.player_name,
  scored.{base_score} AS base_score,
  {extra}
  target.target_points, target.target_ppg
FROM `{args.project}.{args.metrics_dataset}.{view}` AS scored
JOIN target ON target.season=scored.season+1 AND target.player_id=scored.candidate_internal_player_id
WHERE scored.season BETWEEN 2022 AND 2024 AND scored.{base_score} IS NOT NULL
""").result()]
        result[f"{position.lower()}_base"] = evaluate(rows, "base_score")
        if position == "RB":
            result["rb_shift_001"] = evaluate(rows, "rb_ppr_shift_001")
            result["rb_shift_002"] = evaluate(rows, "rb_ppr_shift_002")
            result["rb_shift_003"] = evaluate(rows, "rb_ppr_shift_003")
            result["rb_shift_004"] = evaluate(rows, "rb_ppr_shift_004")
            result["rb_shift_005"] = evaluate(rows, "rb_ppr_shift_005")
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, indent=2, default=str)+"\n", encoding="utf-8")
    print(json.dumps({name: value["aggregate"] for name, value in result.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
