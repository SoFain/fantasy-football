"""Create the review-only RB Fable v1.2 preseason-role backtest view."""

from __future__ import annotations

import argparse
from pathlib import Path

from build_rb_fable_01_metric_layer import render_sql


VIEW_FILE = "v_rb_fable_v12_backtest_prep.sql"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--brain-dataset", default="fantasy_football_brain")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    path = Path(__file__).resolve().parents[1] / "bigquery" / "views" / VIEW_FILE
    sql = render_sql(path, args.project, args.dataset, args.brain_dataset)
    if args.dry_run:
        print(f"{VIEW_FILE}: {len(sql)} bytes")
        return 0

    from google.cloud import bigquery

    bigquery.Client(project=args.project).query(sql).result()
    print(f"created {VIEW_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
