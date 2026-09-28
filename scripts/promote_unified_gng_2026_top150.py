"""Publish only the validated unified GNG Top 150 without rewriting positional rows."""

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
from scripts.promote_unified_fable_v1_standard_top100 import schema


WRITE_GATE = "ALLOW_UNIFIED_GNG_2026_TOP150_PROMOTION"


def validate_active_position_rows(board: list[dict], active_rows: list[dict]) -> None:
    active = {
        (str(row["position"]), str(row["player_id"])): (int(row["rank"]), str(row["model_name"]))
        for row in active_rows
    }
    mismatches = []
    for row in board:
        expected = (int(row["position_rank"]), str(row.get("formula_id") or ""))
        current = active.get((str(row["position"]), str(row["player_id"])))
        if current != expected:
            mismatches.append({
                "player_name": row["player_name"],
                "position": row["position"],
                "board": expected,
                "active": current,
            })
    if mismatches:
        raise ValueError(f"GNG board does not match active positional rankings: {mismatches[:5]}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    parser.add_argument("--board", type=Path, default=Path("output/unified-gng-2026-top150.json"))
    parser.add_argument("--board-version")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    board_version = args.board_version or datetime.now(timezone.utc).strftime(
        "unified-gng-keeper-2026-%Y%m%d%H%M%S"
    )
    board = json.loads(args.board.read_text(encoding="utf-8"))["board"]
    if len(board) != OVERALL_BOARD_SIZE or len({row["player_id"] for row in board}) != OVERALL_BOARD_SIZE:
        raise ValueError(f"board must contain {OVERALL_BOARD_SIZE} unique players")
    if any(not str(row.get("current_team") or "").strip() for row in board):
        raise ValueError("unified GNG board contains a teamless player")

    client = bigquery.Client(project=args.project)
    active_rows = [dict(row) for row in client.query(f"""
SELECT player_id, position, rank, model_name
FROM `{args.project}.{args.dataset}.analytics_pigskin_rankings`
WHERE is_active
  AND scoring_profile_id = 'gng_keeper'
  AND position IN ('QB', 'RB', 'WR', 'TE')
QUALIFY ROW_NUMBER() OVER (PARTITION BY position, player_id ORDER BY generated_at DESC) = 1
""").result()]
    validate_active_position_rows(board, active_rows)

    if not args.apply:
        print(json.dumps({
            "board_version": board_version,
            "rows": len(board),
            "active_position_ranks_valid": True,
            "positional_rows_unchanged": True,
            "writes": False,
        }, indent=2))
        return 0
    if os.environ.get(WRITE_GATE, "").lower() != "true":
        raise RuntimeError(f"{WRITE_GATE}=true is required")

    current = f"{args.project}.{args.dataset}.unified_draft_rankings_current"
    history = f"{args.project}.{args.dataset}.unified_draft_rankings_history"
    current_schema = schema()
    client.create_table(bigquery.Table(current, schema=current_schema), exists_ok=True)
    client.create_table(
        bigquery.Table(
            history,
            schema=current_schema + [bigquery.SchemaField("archived_at", "TIMESTAMP", mode="REQUIRED")],
        ),
        exists_ok=True,
    )
    client.query(f"""
INSERT INTO `{history}`
SELECT live_rows.*, CURRENT_TIMESTAMP()
FROM `{current}` AS live_rows
WHERE live_rows.scoring_profile_id = 'gng_keeper'
  AND NOT EXISTS (
    SELECT 1 FROM `{history}` AS archived
    WHERE archived.board_version = live_rows.board_version
      AND archived.player_id = live_rows.player_id
  )
""").result()
    client.query(f"DELETE FROM `{current}` WHERE scoring_profile_id = 'gng_keeper'").result()

    now = datetime.now(timezone.utc).isoformat()
    payload = [{
        "board_version": board_version,
        "generated_at": now,
        "scoring_profile_id": "gng_keeper",
        "overall_rank": row["overall_rank"],
        "player_id": row["player_id"],
        "player_name": row["player_name"],
        "current_team": row["current_team"],
        "position": row["position"],
        "position_rank": row["position_rank"],
        "projected_ppg": row["projected_ppg"],
        "replacement_rank": row["replacement_rank"],
        "replacement_ppg": row["replacement_ppg"],
        "vorp": row["vorp"],
        "availability_multiplier": row["availability_multiplier"],
        "onesie_multiplier": row["onesie_multiplier"],
        "adjusted_vorp": row["adjusted_vorp"],
        "position_source_version": row["formula_id"],
        "position_rank_source": row.get("rank_source"),
        "risk_flags": row.get("guardrail_labels"),
        "qb_backtest_proxy_disclosed": False,
    } for row in board]
    load_job = client.load_table_from_json(
        payload,
        current,
        job_config=bigquery.LoadJobConfig(
            schema=current_schema,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        ),
    )
    load_job.result()
    if load_job.errors:
        raise RuntimeError(f"BigQuery load failed: {load_job.errors}")

    count = next(iter(client.query(f"""
SELECT COUNT(*) AS row_count
FROM `{current}`
WHERE scoring_profile_id = 'gng_keeper' AND board_version = @board_version
""", job_config=bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("board_version", "STRING", board_version)
    ])).result()))["row_count"]
    if count != OVERALL_BOARD_SIZE:
        raise RuntimeError(f"expected {OVERALL_BOARD_SIZE} rows, got {count}")
    print(json.dumps({
        "board_version": board_version,
        "rows": count,
        "positional_rows_unchanged": True,
        "writes": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
