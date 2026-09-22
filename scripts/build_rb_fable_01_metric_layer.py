"""Create the review-only RB Fable 01 BigQuery views."""

from __future__ import annotations

import argparse
from pathlib import Path

from google.cloud import bigquery


VIEW_FILES = (
    "situational_identity_bridge_review.sql",
    "v_rb_fable_01_situational_splits.sql",
    "v_rb_fable_01_metric_inputs.sql",
    "v_rb_fable_01_scored_seasons.sql",
    "v_rb_fable_01_backtest_prep.sql",
)


def render_sql(path: Path, project: str, dataset: str, brain_dataset: str) -> str:
    return (
        path.read_text(encoding="utf-8")
        .replace("{{PROJECT_ID}}", project)
        .replace("{{DATASET_ID}}", dataset)
        .replace("{{BRAIN_DATASET_ID}}", brain_dataset)
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

    client = bigquery.Client(project=args.project)
    for name, sql in statements:
        client.query(sql).result()
        print(f"created {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
