"""Publish the validated unified Standard overall board as an additive production table."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

from google.cloud import bigquery

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_unified_fable_v1_top100 import OVERALL_BOARD_SIZE


WRITE_GATE = "ALLOW_UNIFIED_FABLE_V1_TOP100_PROMOTION"
BOARD_VERSION = "unified-fable-v1-standard-active-wr-20260713"


def load_board(path: Path) -> list[dict]:
    board = json.loads(path.read_text(encoding="utf-8"))["board"]
    if len(board) != OVERALL_BOARD_SIZE or len({row["player_id"] for row in board}) != OVERALL_BOARD_SIZE:
        raise ValueError(f"board must contain exactly {OVERALL_BOARD_SIZE} unique player IDs")
    for position in ("QB", "RB", "WR", "TE"):
        ranks = [row["position_rank"] for row in board if row["position"] == position]
        if ranks != list(range(1, len(ranks) + 1)):
            raise ValueError(f"{position} ranks are not contiguous")
    return board


def schema() -> list[bigquery.SchemaField]:
    return [
        bigquery.SchemaField("board_version", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("generated_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("scoring_profile_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("overall_rank", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("player_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("player_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("current_team", "STRING"),
        bigquery.SchemaField("position", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("position_rank", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("projected_ppg", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("replacement_rank", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("replacement_ppg", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("vorp", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("availability_multiplier", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("onesie_multiplier", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("adjusted_vorp", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("position_source_version", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("position_rank_source", "STRING"),
        bigquery.SchemaField("risk_flags", "STRING"),
        bigquery.SchemaField("qb_backtest_proxy_disclosed", "BOOL", mode="REQUIRED"),
    ]


def rows_for_load(
    board: list[dict], generated_at: datetime, board_version: str = BOARD_VERSION
) -> list[dict]:
    return [{
        "board_version": board_version,
        "generated_at": generated_at.isoformat(),
        "scoring_profile_id": "standard",
        "overall_rank": row["overall_rank"],
        "player_id": row["player_id"],
        "player_name": row["player_name"],
        "current_team": row.get("current_team"),
        "position": row["position"],
        "position_rank": row["position_rank"],
        "projected_ppg": row["projected_ppg"],
        "replacement_rank": row["replacement_rank"],
        "replacement_ppg": row["replacement_ppg"],
        "vorp": row["vorp"],
        "availability_multiplier": row["availability_multiplier"],
        "onesie_multiplier": row["onesie_multiplier"],
        "adjusted_vorp": row["adjusted_vorp"],
        "position_source_version": row.get("ranking_version") or "unknown",
        "position_rank_source": row.get("rank_source"),
        "risk_flags": row.get("risk_flags"),
        "qb_backtest_proxy_disclosed": True,
    } for row in board]


def validate_active_position_ranks(board: list[dict], active_rows: list[dict]) -> None:
    active = {
        (row["position"], row["player_id"]): (row["rank"], row["ranking_version"])
        for row in active_rows
    }
    mismatches = []
    for row in board:
        current = active.get((row["position"], row["player_id"]))
        if current != (row["position_rank"], row.get("ranking_version")):
            mismatches.append({
                "player_name": row["player_name"],
                "position": row["position"],
                "board_rank": row["position_rank"],
                "board_version": row.get("ranking_version"),
                "active": current,
            })
    if mismatches:
        raise ValueError(f"board does not match active positional rankings: {mismatches[:5]}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    parser.add_argument("--board", type=Path, default=Path("output/unified-fable-v1-standard-top150.json"))
    parser.add_argument("--board-version")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    board_version = args.board_version or datetime.now(timezone.utc).strftime(
        "unified-fable-v1-standard-%Y%m%d%H%M%S"
    )
    board = load_board(args.board)
    client = bigquery.Client(project=args.project)
    active_rows = [dict(row) for row in client.query(f"""
SELECT player_id, position, rank, ranking_version
FROM `{args.project}.{args.dataset}.analytics_pigskin_rankings`
WHERE is_active
  AND scoring_profile_id = 'standard'
  AND position IN ('QB', 'RB', 'WR', 'TE')
QUALIFY ROW_NUMBER() OVER (PARTITION BY position, player_id ORDER BY generated_at DESC) = 1
""").result()]
    validate_active_position_ranks(board, active_rows)
    if not args.apply:
        print(json.dumps({
            "board_version": board_version,
            "rows": len(board),
            "active_position_ranks_valid": True,
            "writes": False,
        }, indent=2))
        return 0
    if os.environ.get(WRITE_GATE, "").lower() != "true":
        raise RuntimeError(f"{WRITE_GATE}=true is required")

    current_id = f"{args.project}.{args.dataset}.unified_draft_rankings_current"
    history_id = f"{args.project}.{args.dataset}.unified_draft_rankings_history"
    current_schema = schema()
    client.create_table(bigquery.Table(current_id, schema=current_schema), exists_ok=True)
    history_schema = current_schema + [bigquery.SchemaField("archived_at", "TIMESTAMP", mode="REQUIRED")]
    client.create_table(bigquery.Table(history_id, schema=history_schema), exists_ok=True)
    client.query(f"""
INSERT INTO `{history_id}`
SELECT live_rows.*, CURRENT_TIMESTAMP() AS archived_at
FROM `{current_id}` AS live_rows
WHERE NOT EXISTS (
  SELECT 1 FROM `{history_id}` AS history
  WHERE history.board_version = live_rows.board_version
    AND history.player_id = live_rows.player_id
)
""").result()
    client.query(f"DELETE FROM `{current_id}` WHERE scoring_profile_id = 'standard'").result()
    rows = rows_for_load(board, datetime.now(timezone.utc), board_version)
    load_job = client.load_table_from_json(
        rows,
        current_id,
        job_config=bigquery.LoadJobConfig(
            schema=current_schema,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        ),
    )
    load_job.result()
    if load_job.errors:
        raise RuntimeError(f"BigQuery load failed: {load_job.errors}")
    count = next(iter(client.query(f"SELECT COUNT(*) AS row_count FROM `{current_id}` WHERE board_version='{board_version}'").result()))["row_count"]
    if count != OVERALL_BOARD_SIZE:
        raise RuntimeError(f"post-write row count is {count}, expected {OVERALL_BOARD_SIZE}")
    print(json.dumps({"board_version": board_version, "rows": count, "writes": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
