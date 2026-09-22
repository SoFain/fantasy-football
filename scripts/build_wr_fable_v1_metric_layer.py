"""Create the review-only WR Fable v1 BigQuery views."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_rb_fable_01_metric_layer import render_sql

VIEW_FILES = (
    "v_wr_fable_v1_identity_bridge.sql",
    "v_wr_fable_v1_situational_splits.sql",
    "v_wr_fable_v1_metric_inputs.sql",
    "v_wr_fable_v1_scored_seasons.sql",
    "v_wr_fable_v1_backtest_prep.sql",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--brain-dataset", default="fantasy_football_brain")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    view_dir = Path(__file__).resolve().parents[1] / "bigquery" / "views"
    statements = [(name, render_sql(view_dir / name, args.project, args.dataset, args.brain_dataset)) for name in VIEW_FILES]
    if args.dry_run:
        for name, sql in statements:
            print(f"{name}: {len(sql)} bytes")
        return 0

    from google.cloud import bigquery

    client = bigquery.Client(project=args.project)
    for name, sql in statements:
        client.query(sql).result()
        print(f"created {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
