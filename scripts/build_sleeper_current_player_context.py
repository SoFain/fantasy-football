"""Build the review-only Sleeper current-player context layer for RB Fable v1.

Reuses the existing Sleeper client in src/sleeper_player_snapshot.py. One fetch,
cached to a local JSON file; the loader prefers the cache so the full player map
is never fetched repeatedly. Writes only research objects in the isolated
advanced-metrics dataset. Never touches production feature marts, identity
tables, live rankings, or the Fable formula score.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.sleeper_player_snapshot import SLEEPER_PLAYERS_URL, fetch_sleeper_players

DEFAULT_PROJECT = "fantasy-football-498121"
DEFAULT_DATASET = "fantasy_football_advanced_metrics"
DEFAULT_BRAIN_DATASET = "fantasy_football_brain"
TABLE_NAME = "sleeper_current_player_context"
DEFAULT_CACHE = Path(__file__).resolve().parents[1] / "output" / "sleeper_current_players_cache.json"
VIEW_FILE = Path(__file__).resolve().parents[1] / "bigquery" / "views" / "v_rb_fable_v1_current_context_review.sql"


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def build_context_rows(players: dict[str, Any], *, fetched_at: datetime) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sleeper_player_id, player in players.items():
        if not isinstance(player, dict):
            continue
        raw_json = _json_dumps(player)
        rows.append({
            "sleeper_player_id": str(sleeper_player_id),
            "full_name": player.get("full_name"),
            "first_name": player.get("first_name"),
            "last_name": player.get("last_name"),
            "search_full_name": player.get("search_full_name"),
            "gsis_id": (str(player["gsis_id"]).strip() if player.get("gsis_id") else None),
            "team": player.get("team"),
            "position": player.get("position"),
            "fantasy_positions_json": _json_dumps(player.get("fantasy_positions") or []),
            "status": player.get("status"),
            "injury_status": player.get("injury_status"),
            "injury_body_part": player.get("injury_body_part"),
            "injury_notes": player.get("injury_notes"),
            "depth_chart_position": player.get("depth_chart_position"),
            "depth_chart_order": player.get("depth_chart_order"),
            "years_exp": player.get("years_exp"),
            "age": player.get("age"),
            "active": player.get("active"),
            "metadata_json": _json_dumps(player.get("metadata") or {}),
            "raw_payload_hash": hashlib.sha256(raw_json.encode("utf-8")).hexdigest(),
            "source_url": SLEEPER_PLAYERS_URL,
            "fetched_at": fetched_at.isoformat(),
        })
    return rows


def load_players(cache_path: Path, *, refresh: bool) -> tuple[dict[str, Any], datetime, str]:
    if cache_path.exists() and not refresh:
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        return cached["players"], datetime.fromisoformat(cached["fetched_at"]), "cache"
    players = fetch_sleeper_players()
    fetched_at = datetime.now(timezone.utc)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps({"fetched_at": fetched_at.isoformat(), "source_url": SLEEPER_PLAYERS_URL, "players": players}),
        encoding="utf-8",
    )
    return players, fetched_at, "network"


def write_table(rows: list[dict[str, Any]], *, project: str, dataset: str) -> str:
    from google.cloud import bigquery

    client = bigquery.Client(project=project)
    table_id = f"{project}.{dataset}.{TABLE_NAME}"
    schema = [
        bigquery.SchemaField("sleeper_player_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("full_name", "STRING"),
        bigquery.SchemaField("first_name", "STRING"),
        bigquery.SchemaField("last_name", "STRING"),
        bigquery.SchemaField("search_full_name", "STRING"),
        bigquery.SchemaField("gsis_id", "STRING"),
        bigquery.SchemaField("team", "STRING"),
        bigquery.SchemaField("position", "STRING"),
        bigquery.SchemaField("fantasy_positions_json", "STRING"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("injury_status", "STRING"),
        bigquery.SchemaField("injury_body_part", "STRING"),
        bigquery.SchemaField("injury_notes", "STRING"),
        bigquery.SchemaField("depth_chart_position", "STRING"),
        bigquery.SchemaField("depth_chart_order", "INT64"),
        bigquery.SchemaField("years_exp", "INT64"),
        bigquery.SchemaField("age", "INT64"),
        bigquery.SchemaField("active", "BOOL"),
        bigquery.SchemaField("metadata_json", "STRING"),
        bigquery.SchemaField("raw_payload_hash", "STRING"),
        bigquery.SchemaField("source_url", "STRING"),
        bigquery.SchemaField("fetched_at", "TIMESTAMP"),
    ]
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=False,
    )
    client.load_table_from_json(rows, table_id, job_config=job_config).result()
    return table_id


def archive_snapshot(rows: list[dict[str, Any]], *, project: str, dataset: str, snapshot_date: str) -> str:
    """Append today's snapshot to the permanent history table, idempotently.

    Grain: snapshot_date + sleeper_player_id. Re-running the same date replaces that
    date's rows instead of duplicating them.
    """
    from google.cloud import bigquery

    client = bigquery.Client(project=project)
    table_id = f"{project}.{dataset}.sleeper_player_snapshot_history"
    schema = [bigquery.SchemaField("snapshot_date", "DATE", mode="REQUIRED")] + [
        bigquery.SchemaField(field, "STRING") if field not in (
            "depth_chart_order", "years_exp", "age") else bigquery.SchemaField(field, "INT64")
        for field in (
            "sleeper_player_id", "full_name", "first_name", "last_name", "search_full_name",
            "gsis_id", "team", "position", "fantasy_positions_json", "status", "injury_status",
            "injury_body_part", "injury_notes", "depth_chart_position", "depth_chart_order",
            "years_exp", "age", "metadata_json", "raw_payload_hash", "source_url",
        )
    ] + [
        bigquery.SchemaField("active", "BOOL"),
        bigquery.SchemaField("fetched_at", "TIMESTAMP"),
    ]
    try:
        client.get_table(table_id)
    except Exception:
        client.create_table(bigquery.Table(table_id, schema=schema))
    client.query(
        f"DELETE FROM `{table_id}` WHERE snapshot_date = @snapshot_date",
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("snapshot_date", "DATE", snapshot_date)]
        ),
    ).result()
    history_rows = [{**row, "snapshot_date": snapshot_date} for row in rows]
    job_config = bigquery.LoadJobConfig(schema=schema, write_disposition="WRITE_APPEND", autodetect=False)
    client.load_table_from_json(history_rows, table_id, job_config=job_config).result()
    return table_id


def deploy_status_changes_view(*, project: str, dataset: str) -> str:
    from google.cloud import bigquery

    client = bigquery.Client(project=project)
    view_id = f"{project}.{dataset}.v_sleeper_player_status_changes"
    client.query(f"""
CREATE OR REPLACE VIEW `{view_id}` AS
WITH dates AS (
  SELECT ARRAY_AGG(DISTINCT snapshot_date ORDER BY snapshot_date DESC LIMIT 2) AS latest_two
  FROM `{project}.{dataset}.sleeper_player_snapshot_history`
),
newest AS (
  SELECT * FROM `{project}.{dataset}.sleeper_player_snapshot_history`, dates
  WHERE snapshot_date = latest_two[SAFE_OFFSET(0)]
),
previous AS (
  SELECT * FROM `{project}.{dataset}.sleeper_player_snapshot_history`, dates
  WHERE snapshot_date = latest_two[SAFE_OFFSET(1)]
)
SELECT
  newest.sleeper_player_id,
  newest.full_name,
  newest.position,
  newest.snapshot_date AS newest_snapshot_date,
  previous.snapshot_date AS previous_snapshot_date,
  previous.team AS previous_team, newest.team AS current_team,
  previous.status AS previous_status, newest.status AS current_status,
  previous.injury_status AS previous_injury_status, newest.injury_status AS current_injury_status,
  previous.depth_chart_order AS previous_depth_chart_order, newest.depth_chart_order AS current_depth_chart_order,
  IFNULL(previous.team, '') != IFNULL(newest.team, '') AS team_changed,
  IFNULL(previous.status, '') != IFNULL(newest.status, '') AS status_changed,
  IFNULL(previous.injury_status, '') != IFNULL(newest.injury_status, '') AS injury_changed,
  IFNULL(previous.depth_chart_order, -1) != IFNULL(newest.depth_chart_order, -1) AS depth_changed
FROM newest
LEFT JOIN previous USING (sleeper_player_id)
WHERE previous.snapshot_date IS NOT NULL
  AND (IFNULL(previous.team, '') != IFNULL(newest.team, '')
   OR IFNULL(previous.status, '') != IFNULL(newest.status, '')
   OR IFNULL(previous.injury_status, '') != IFNULL(newest.injury_status, '')
   OR IFNULL(previous.depth_chart_order, -1) != IFNULL(newest.depth_chart_order, -1))
""").result()
    return view_id


def deploy_review_view(*, project: str, dataset: str, brain_dataset: str) -> str:
    from google.cloud import bigquery

    sql = (
        VIEW_FILE.read_text(encoding="utf-8")
        .replace("{{PROJECT_ID}}", project)
        .replace("{{DATASET_ID}}", dataset)
        .replace("{{BRAIN_DATASET_ID}}", brain_dataset)
    )
    client = bigquery.Client(project=project)
    client.query(sql).result()
    return f"{project}.{dataset}.v_rb_fable_v1_current_context_review"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--brain-dataset", default=DEFAULT_BRAIN_DATASET)
    parser.add_argument("--cache-path", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--refresh", action="store_true", help="Force one network fetch even when the cache exists.")
    parser.add_argument("--archive", action="store_true",
                        help="Also append to sleeper_player_snapshot_history (weekly archive) and refresh the status-changes view.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Fetch/load cache and summarize without writing BigQuery.")
    mode.add_argument("--apply", action="store_true", help="Write the research table and review view.")
    args = parser.parse_args(argv)

    players, fetched_at, origin = load_players(args.cache_path, refresh=args.refresh)
    rows = build_context_rows(players, fetched_at=fetched_at)
    summary = {
        "players_origin": origin,
        "fetched_at": fetched_at.isoformat(),
        "total_rows": len(rows),
        "rb_rows": sum(1 for row in rows if row["position"] == "RB"),
        "cache_path": str(args.cache_path),
    }
    if args.apply:
        summary["table"] = write_table(rows, project=args.project, dataset=args.dataset)
        summary["view"] = deploy_review_view(
            project=args.project, dataset=args.dataset, brain_dataset=args.brain_dataset
        )
        if args.archive:
            snapshot_date = fetched_at.date().isoformat()
            summary["history_table"] = archive_snapshot(
                rows, project=args.project, dataset=args.dataset, snapshot_date=snapshot_date
            )
            summary["status_changes_view"] = deploy_status_changes_view(project=args.project, dataset=args.dataset)
            summary["snapshot_date"] = snapshot_date
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
