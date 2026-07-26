"""Capture a point-in-time Sleeper NFL players snapshot.

This lane is for current roster/status context only. It does not call Sleeper
league APIs and does not write ranking outputs.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import socket
import sys
from datetime import datetime, timezone
from typing import Any

import requests


DEFAULT_PROJECT = "fantasy-football-498121"
DEFAULT_DATASET = "fantasy_football_brain"
SLEEPER_PLAYERS_URL = "https://api.sleeper.app/v1/players/nfl"
WRITE_GATE = "ALLOW_SLEEPER_2026_SNAPSHOT"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _row_hash(row: dict[str, Any]) -> str:
    payload = {key: value for key, value in row.items() if key not in {"loaded_at", "row_hash"}}
    return hashlib.sha256(_json_dumps(payload).encode("utf-8")).hexdigest()


def fetch_sleeper_players(*, timeout_seconds: int = 30) -> dict[str, Any]:
    response = requests.get(SLEEPER_PLAYERS_URL, timeout=timeout_seconds)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Sleeper players response must be a JSON object keyed by player ID.")
    return payload


def build_snapshot_rows(
    players: dict[str, Any],
    *,
    snapshot_at: datetime,
    loaded_at: datetime,
    loaded_by: str,
    source_version: str = "sleeper_players_nfl_v1",
) -> list[dict[str, Any]]:
    snapshot_id = snapshot_at.strftime("sleeper_players_%Y%m%dT%H%M%SZ")
    rows: list[dict[str, Any]] = []
    for sleeper_player_id, player in players.items():
        if not isinstance(player, dict):
            continue
        first_name = player.get("first_name")
        last_name = player.get("last_name")
        player_name = (
            " ".join(part for part in [first_name, last_name] if part).strip()
            or player.get("full_name")
            or player.get("search_full_name")
            or player.get("metadata", {}).get("full_name")
        )
        row = {
            "snapshot_id": snapshot_id,
            "snapshot_at": snapshot_at,
            "snapshot_year": snapshot_at.year,
            "sleeper_player_id": str(sleeper_player_id),
            "gsis_id": _string_or_none(player.get("gsis_id")),
            "sportradar_id": _string_or_none(player.get("sportradar_id")),
            "fantasy_data_id": _string_or_none(player.get("fantasy_data_id")),
            "player_name": player_name,
            "first_name": first_name,
            "last_name": last_name,
            "search_full_name": player.get("search_full_name"),
            "position": player.get("position"),
            "team": player.get("team"),
            "active": player.get("active"),
            "status": player.get("status"),
            "injury_status": player.get("injury_status"),
            "fantasy_positions_json": _json_dumps(player.get("fantasy_positions") or []),
            "depth_chart_position": player.get("depth_chart_position"),
            "depth_chart_order": player.get("depth_chart_order"),
            "search_rank": player.get("search_rank"),
            "years_exp": player.get("years_exp"),
            "metadata_json": _json_dumps(player.get("metadata") or {}),
            "raw_payload_json": _json_dumps(player),
            "source_system": "sleeper",
            "source_url": SLEEPER_PLAYERS_URL,
            "source_version": source_version,
            "loaded_at": loaded_at,
            "loaded_by": loaded_by,
            "row_hash": None,
        }
        row["row_hash"] = _row_hash(row)
        rows.append(row)
    return rows


def summarize_rows(rows: list[dict[str, Any]], *, wrote: bool, project: str, dataset: str) -> dict[str, Any]:
    fantasy_rows = [row for row in rows if row.get("position") in {"QB", "RB", "WR", "TE", "K", "DEF"}]
    status_counts: dict[str, int] = {}
    team_counts: dict[str, int] = {}
    for row in rows:
        status = row.get("status") or "missing"
        team = row.get("team") or "missing"
        status_counts[status] = status_counts.get(status, 0) + 1
        team_counts[team] = team_counts.get(team, 0) + 1
    return {
        "wrote": wrote,
        "snapshot_id": rows[0]["snapshot_id"] if rows else None,
        "snapshot_at": rows[0]["snapshot_at"].isoformat() if rows else None,
        "source_url": SLEEPER_PLAYERS_URL,
        "total_player_rows": len(rows),
        "fantasy_position_rows": len(fantasy_rows),
        "status_counts": dict(sorted(status_counts.items())),
        "team_count": len(team_counts),
        "target_table": f"{project}.{dataset}.raw_sleeper_players_snapshot",
        "context_view": f"{project}.{dataset}.sleeper_player_context_current",
    }


def write_snapshot_rows(rows: list[dict[str, Any]], *, project: str, dataset: str) -> int:
    if os.environ.get(WRITE_GATE) != "true":
        raise PermissionError(f"{WRITE_GATE} must be true to write Sleeper player snapshots")
    if not rows:
        return 0

    from google.cloud import bigquery

    client = bigquery.Client(project=project)
    table_id = f"{project}.{dataset}.raw_sleeper_players_snapshot"
    snapshot_id = rows[0]["snapshot_id"]
    client.query(
        f"DELETE FROM `{table_id}` WHERE snapshot_id = @snapshot_id",
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("snapshot_id", "STRING", snapshot_id)]
        ),
    ).result()

    table = client.get_table(table_id)
    json_rows = []
    for row in rows:
        json_row = row.copy()
        for timestamp_column in ("snapshot_at", "loaded_at"):
            if isinstance(json_row.get(timestamp_column), datetime):
                json_row[timestamp_column] = json_row[timestamp_column].isoformat()
        json_rows.append(json_row)
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        schema=table.schema,
        autodetect=False,
    )
    client.load_table_from_json(json_rows, table_id, job_config=job_config).result()
    return len(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture a current Sleeper NFL players snapshot.")
    parser.add_argument("--project", default=os.environ.get("BQ_PROJECT", DEFAULT_PROJECT))
    parser.add_argument("--dataset", default=os.environ.get("BQ_DATASET", DEFAULT_DATASET))
    parser.add_argument("--dry-run", action="store_true", help="Fetch and summarize without writing BigQuery rows.")
    parser.add_argument("--write", action="store_true", help=f"Write snapshot rows when {WRITE_GATE}=true.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.write and args.dry_run:
        print("--write and --dry-run cannot be combined", file=sys.stderr)
        return 2
    try:
        snapshot_at = _utc_now()
        loaded_at = snapshot_at
        loaded_by = f"{getpass.getuser()}@{socket.gethostname()}"
        players = fetch_sleeper_players()
        rows = build_snapshot_rows(players, snapshot_at=snapshot_at, loaded_at=loaded_at, loaded_by=loaded_by)
        written_count = 0
        if args.write:
            written_count = write_snapshot_rows(rows, project=args.project, dataset=args.dataset)
        summary = summarize_rows(rows, wrote=bool(args.write), project=args.project, dataset=args.dataset)
        summary["written_row_count"] = written_count
        summary["write_gate"] = WRITE_GATE
        print(json.dumps(summary, indent=2, sort_keys=True, default=str))
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
