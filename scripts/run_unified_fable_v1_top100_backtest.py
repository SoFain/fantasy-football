"""Run leakage-safe pooled realized-VORP folds for the unified Standard top-100."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
import sys
from typing import Any

from google.cloud import bigquery

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_unified_fable_v1_top100 import POSITIONS, REPLACEMENT_RANK, fit_log_curve, interleave
from scripts.run_qb_fable_v1_backtest import build_qb_fable_v1_sql
from scripts.run_rb_fable_01_backtest import pearson, rank_values


def spearman(predicted_order: list[float], realized_values: list[float]) -> float | None:
    return pearson(rank_values(predicted_order, reverse=False), rank_values(realized_values))


def qb_detail_sql(project: str, dataset: str) -> str:
    prefix = build_qb_fable_v1_sql(project, dataset).split("candidate_scores AS (", 1)[0]
    if not prefix.rstrip().endswith(","):
        raise ValueError("QB SQL structure changed before candidate_scores")
    return prefix.rstrip()[:-1] + "\nSELECT * FROM scored ORDER BY input_season, qb_fable_v1_score DESC"


def evaluate_fold(
    input_season: int,
    scored_rows: list[dict[str, Any]],
    historical: list[dict[str, Any]],
    replacement_rank: dict[str, int],
) -> dict[str, Any]:
    curves = {}
    availability = {}
    for position in POSITIONS:
        replacement = replacement_rank[position]
        curve_rows = [
            row for row in historical
            if row["season"] <= input_season and row["position"] == position
            and row["position_rank"] <= max(replacement + 12, 24)
        ]
        curves[position] = fit_log_curve([(row["position_rank"], row["standard_ppg"]) for row in curve_rows])
        cohort = [
            row for row in historical
            if row["season"] <= input_season and row["position"] == position
            and row["position_rank"] <= replacement
        ]
        availability[position] = mean(min(row["games_played"] / 17, 1.0) for row in cohort)

    fold_rows = [row for row in scored_rows if row["season"] == input_season and row.get("target_standard_ppg") is not None]
    queues = {
        position: [
            {"player_id": row["player_id"], "player_name": row["player_name"], "target_standard_ppg": row["target_standard_ppg"]}
            for row in sorted((item for item in fold_rows if item["position"] == position), key=lambda item: (-item["score"], item["player_name"]))
        ]
        for position in POSITIONS
    }
    full_board = interleave(queues, curves, availability, limit=len(fold_rows), replacement_rank=replacement_rank)

    target_season = input_season + 1
    actual_by_position = {
        position: sorted(
            (row for row in historical if row["season"] == target_season and row["position"] == position),
            key=lambda row: row["position_rank"],
        )
        for position in POSITIONS
    }
    actual_replacement = {
        position: actual_by_position[position][replacement_rank[position] - 1]["standard_ppg"]
        for position in POSITIONS
    }
    evaluated = []
    for row in full_board:
        realized_vorp = row["target_standard_ppg"] - actual_replacement[row["position"]]
        evaluated.append({**row, "realized_vorp": realized_vorp})
    ideal = sorted(evaluated, key=lambda row: (-row["realized_vorp"], row["player_id"]))
    actual_ranks = {row["player_id"]: rank for rank, row in enumerate(ideal, 1)}
    for row in evaluated:
        row["actual_pooled_rank"] = actual_ranks[row["player_id"]]

    hit_rates = {}
    for cutoff in (24, 50, 100):
        selected = evaluated[: min(cutoff, len(evaluated))]
        hit_rates[f"top_{cutoff}_hit_rate"] = sum(row["actual_pooled_rank"] <= cutoff for row in selected) / len(selected)
    ideal_vorp = sum(max(row["realized_vorp"], 0.0) for row in ideal[: min(100, len(ideal))])
    selected_vorp = sum(max(row["realized_vorp"], 0.0) for row in evaluated[:100])
    predicted_ranks = [float(row["overall_rank"]) for row in evaluated]
    realized = [row["realized_vorp"] for row in evaluated]
    return {
        "input_season": input_season,
        "target_season": target_season,
        "complete_rows": len(evaluated),
        "selected_rows": min(100, len(evaluated)),
        "composition": {position: sum(row["position"] == position for row in evaluated[:100]) for position in POSITIONS},
        "realized_vorp_spearman": spearman(predicted_ranks, realized),
        "positive_vorp_captured_at_100": selected_vorp / ideal_vorp if ideal_vorp else None,
        **hit_rates,
        "bottom_20_misses": sorted(evaluated, key=lambda row: row["actual_pooled_rank"])[:20],
        "top_20_busts": sorted(evaluated[:20], key=lambda row: -row["actual_pooled_rank"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    parser.add_argument("--metrics-dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--json-output", type=Path, default=Path("output/unified-fable-v1-standard-top100-backtest.json"))
    args = parser.parse_args()
    client = bigquery.Client(project=args.project)

    historical = [dict(row) for row in client.query(f"""
WITH player_seasons AS (
  SELECT season, position, source_player_key AS player_id, COUNT(*) AS games_played,
    SAFE_DIVIDE(SUM(total_fantasy_points), COUNT(*)) AS standard_ppg
  FROM `{args.project}.{args.dataset}.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id='standard' AND position IN ('QB','RB','WR','TE')
    AND season BETWEEN 2022 AND 2025 AND week BETWEEN 1 AND 18
  GROUP BY season, position, player_id HAVING games_played >= 6
)
SELECT *, ROW_NUMBER() OVER (PARTITION BY season, position ORDER BY standard_ppg DESC, player_id) AS position_rank
FROM player_seasons
""").result()]

    scored_rows = []
    sources = (
        ("RB", "v_rb_fable_01_backtest_prep", "candidate_internal_player_id", "player_name", "rb_fable_01_score"),
        ("WR", "v_wr_fable_v1_backtest_prep", "candidate_internal_player_id", "player_name", "wr_fable_v1_score"),
        ("TE", "v_te_fable_v1a_backtest_prep", "candidate_internal_player_id", "player_name", "te_fable_v1a_no_man_score"),
    )
    for position, view, player_id, player_name, score in sources:
        rows = client.query(f"""
SELECT season, {player_id} AS player_id, {player_name} AS player_name,
  {score} AS score, target_standard_ppg
FROM `{args.project}.{args.metrics_dataset}.{view}`
WHERE target_available AND {score} IS NOT NULL
""").result()
        scored_rows.extend({**dict(row), "position": position} for row in rows)
    qb_rows = client.query(qb_detail_sql(args.project, args.dataset)).result()
    scored_rows.extend({
        "season": row["input_season"], "player_id": row["player_id_internal"],
        "player_name": row.get("player_name") or row["player_id_internal"], "position": "QB",
        "score": row["qb_fable_v1_score"], "target_standard_ppg": row["target_standard_ppg"],
    } for row in map(dict, qb_rows))

    variants = {
        "selected_rb34_te9": {"QB": 13, "RB": 34, "WR": 40, "TE": 9},
        "rb32_te9": {"QB": 13, "RB": 32, "WR": 40, "TE": 9},
        "rb36_te9": {"QB": 13, "RB": 36, "WR": 40, "TE": 9},
        "rb34_te10": {"QB": 13, "RB": 34, "WR": 40, "TE": 10},
        "rb34_te11": {"QB": 13, "RB": 34, "WR": 40, "TE": 11},
    }
    result = {"variants": {}}
    for name, replacement in variants.items():
        folds = [evaluate_fold(season, scored_rows, historical, replacement) for season in (2022, 2023, 2024)]
        aggregate = {
            "average_realized_vorp_spearman": mean(fold["realized_vorp_spearman"] for fold in folds),
            "average_positive_vorp_captured_at_100": mean(fold["positive_vorp_captured_at_100"] for fold in folds),
            "average_top_24_hit_rate": mean(fold["top_24_hit_rate"] for fold in folds),
            "average_top_50_hit_rate": mean(fold["top_50_hit_rate"] for fold in folds),
            "average_top_100_hit_rate": mean(fold["top_100_hit_rate"] for fold in folds),
            "qb_proxy": "QB Fable v1 prior-season queue; active guarded 75/25 QB lacks matching three-fold preseason rows",
        }
        result["variants"][name] = {"replacement_rank": replacement, "aggregate": aggregate, "folds": folds}
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({name: value["aggregate"] for name, value in result["variants"].items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
