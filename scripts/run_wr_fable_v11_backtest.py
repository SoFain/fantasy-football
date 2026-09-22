"""Backtest WR Fable v1.1 (blend, and blend + team-environment modifier), read-only.

Evaluates each variant with the same fold machinery as WR Fable v1 by aliasing the
variant score into the v1 score key before scoring.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_wr_fable_v1_backtest import SCORE, fold_summary

VARIANTS = {
    "v11_blend": "wr_fable_v11_score",
    "v11_blend_env": "wr_fable_v11_env_score",
}
AGG_FIELDS = (
    "top_6_precision", "top_12_precision", "top_24_precision", "top_36_precision",
    "spearman_rank_correlation", "score_correlation", "points_captured_at_12", "points_captured_at_24",
    "ndcg_at_12", "ndcg_at_24", "pairwise_draft_win_rate", "band_regret",
)


def evaluate_variant(rows: list[dict[str, Any]], score_column: str) -> dict[str, Any]:
    folds = {}
    for input_season in (2022, 2023, 2024):
        records = []
        for row in rows:
            if row["season"] != input_season or row[score_column] is None:
                continue
            aliased = dict(row)
            aliased[SCORE] = row[score_column]
            records.append(aliased)
        folds[f"{input_season}_to_{input_season + 1}"] = fold_summary(records)
    summaries = list(folds.values())
    aggregate = {f"average_{name}": mean(s[name] for s in summaries if s[name] is not None) for name in AGG_FIELDS}
    aggregate["total_elite_misses"] = sum(s["elite_wr_miss_count"] for s in summaries)
    aggregate["total_top12_busts"] = sum(s["predicted_top_12_bust_count"] for s in summaries)
    aggregate["total_complete_rows"] = sum(s["complete_row_count"] for s in summaries)
    return {"folds": folds, "aggregate": aggregate}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    from google.cloud import bigquery

    client = bigquery.Client(project=args.project)
    rows = [dict(row) for row in client.query(f"""
SELECT * FROM `{args.project}.{args.dataset}.v_wr_fable_v11_backtest_prep`
WHERE target_available AND wr_fable_v11_score IS NOT NULL
ORDER BY season, wr_fable_v11_score DESC
""").result()]

    result = {name: evaluate_variant(rows, column) for name, column in VARIANTS.items()}
    result["carry_forward_counts"] = {
        season: sum(1 for row in rows if row["season"] == season and row.get("carry_forward_eligible"))
        for season in (2022, 2023, 2024)
    }
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, default=str, indent=2) + "\n", encoding="utf-8")
    compact = {
        name: {
            "aggregate": variant["aggregate"],
            "folds": {fold: {k: v for k, v in summary.items() if not isinstance(v, list)} for fold, summary in variant["folds"].items()},
        }
        for name, variant in result.items() if name in VARIANTS
    }
    compact["carry_forward_counts"] = result["carry_forward_counts"]
    print(json.dumps(compact, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
