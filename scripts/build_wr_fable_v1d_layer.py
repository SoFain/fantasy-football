"""Build the Phase 35.1D research-only WR Fable modified-formula views."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_rb_fable_01_metric_layer import render_sql


ROOT = Path(__file__).resolve().parents[1]
VIEW_DIR = ROOT / "bigquery" / "views"
VIEW_FILES = (
    "v_wr_fable_v1d_team_environment.sql",
    "v_wr_fable_v1d_metric_inputs.sql",
    "v_wr_fable_v1d_scored_seasons.sql",
    "v_wr_fable_v1d_backtest_prep.sql",
    "v_wr_fable_v1d_current_board.sql",
    "v_wr_fable_v1_current_candidates.sql",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--brain-dataset", default="fantasy_football_brain")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    statements = [
        (
            name,
            render_sql(VIEW_DIR / name, args.project, args.dataset, args.brain_dataset),
        )
        for name in VIEW_FILES
    ]
    if not args.apply:
        for name, sql in statements:
            print(f"-- {name}\n{sql}\n")
        return 0

    from google.cloud import bigquery

    client = bigquery.Client(project=args.project)
    for name, sql in statements:
        client.query(sql).result()
        print(f"applied {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
