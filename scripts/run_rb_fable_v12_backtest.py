"""Compare RB Fable v1.2 preseason-role variants against the Phase 34.4 champion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_rb_fable_01_backtest import fold_summary


VARIANTS = {
    "champion": "rb_fable_01_score",
    "room_share_003": "rb_fable_v12_score_003",
    "room_share_005": "rb_fable_v12_score_005",
    "room_share_008": "rb_fable_v12_score_008",
    "room_delta_010": "rb_fable_v12_delta_score_010",
    "room_delta_020": "rb_fable_v12_delta_score_020",
    "room_delta_030": "rb_fable_v12_delta_score_030",
}
AGGREGATE_FIELDS = (
    "top_6_hit_rate",
    "top_12_hit_rate",
    "top_24_hit_rate",
    "top_36_hit_rate",
    "points_captured_rate_at_24",
    "ndcg_at_24",
    "pairwise_draft_win_rate",
    "pick_band_regret",
)


def evaluate_variant(rows: list[dict[str, Any]], score_column: str) -> dict[str, Any]:
    folds = {}
    for season in (2022, 2023, 2024):
        records = []
        for row in rows:
            if row["season"] != season or row.get(score_column) is None:
                continue
            record = dict(row)
            record["rb_fable_01_score"] = row[score_column]
            records.append(record)
        folds[f"{season}_to_{season + 1}"] = fold_summary(records)
    summaries = list(folds.values())
    aggregate = {
        f"average_{field}": mean(summary[field] for summary in summaries if summary[field] is not None)
        for field in AGGREGATE_FIELDS
    }
    aggregate["total_elite_misses"] = sum(summary["elite_rb_miss_count"] for summary in summaries)
    aggregate["total_top12_busts"] = sum(len(summary["failed_top_players"]) for summary in summaries)
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
SELECT * FROM `{args.project}.{args.dataset}.v_rb_fable_v12_backtest_prep`
WHERE target_available AND rb_fable_01_score IS NOT NULL
ORDER BY season, rb_fable_01_score DESC
""").result()]
    result = {name: evaluate_variant(rows, column) for name, column in VARIANTS.items()}
    result["coverage"] = {
        "rows": len(rows),
        "destination_team": sum(row.get("destination_team") is not None for row in rows),
        "room_share": sum(row.get("preseason_room_touch_share") is not None for row in rows),
        "team_changed": sum(bool(row.get("team_changed")) for row in rows),
    }
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, default=str, indent=2) + "\n", encoding="utf-8")
    compact = {
        name: variant["aggregate"] for name, variant in result.items() if name in VARIANTS
    }
    compact["coverage"] = result["coverage"]
    print(json.dumps(compact, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
