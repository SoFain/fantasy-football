"""Create the review-only TE Fable v1.0a BigQuery views."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

VIEW_FILES = (
    "v_te_fable_v1a_identity_bridge.sql",
    "v_te_fable_v1a_situational_splits.sql",
    "v_te_fable_v1a_metric_inputs.sql",
    "v_te_fable_v1a_scored_seasons.sql",
    "v_te_fable_v1a_backtest_prep.sql",
    "v_te_fable_v1a_rookie_candidates.sql",
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

    from google.cloud import bigquery

    client = bigquery.Client(project=args.project)
    for name, sql in statements:
        client.query(sql).result()
        print(f"created {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
