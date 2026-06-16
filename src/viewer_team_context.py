"""Safe access helpers for viewer-team context packets."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_SCORING_PROFILE = "ppr"
DEFAULT_LEAGUE_TYPE = "redraft"
DEFAULT_ROSTER_FORMAT = "one_qb"
DEFAULT_LIMIT = 50
MAX_LIMIT = 100
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("VIEWER_TEAM_CONTEXT_MAX_BYTES_BILLED", "1000000000"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")
PACKET_KEYS = (
    "league_context",
    "team_context",
    "roster_rows",
    "lineup_rows",
    "bench_rows",
    "waiver_rows",
    "team_strengths",
    "team_weaknesses",
    "recommended_actions",
    "evidence_metadata",
)


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def get_viewer_team_context(
    league_id: str,
    *,
    roster_id: int | str | None = None,
    manager_id: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    """Return one viewer-team packet or a clean unavailable response."""
    if not _clean_optional(league_id):
        raise ValueError("league_id is required")
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_viewer_team_context_query(
        project_id=client.project,
        dataset_id=dataset_id,
        league_id=league_id,
        roster_id=roster_id,
        manager_id=manager_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    rows = _query_rows(client, sql, job_config)
    if not rows:
        return unavailable_viewer_team_context(
            league_id=league_id,
            roster_id=roster_id,
            manager_id=manager_id,
            reason="viewer_team_context_not_materialized",
        )
    row = rows[0]
    row["packet"] = normalize_packet_json(row.get("packet_json"))
    return row


def list_viewer_team_contexts(
    *,
    league_id: str | None = None,
    season: int | str | None = None,
    week: int | str | None = None,
    limit: int | str | None = DEFAULT_LIMIT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """List available viewer-team context packets."""
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_list_viewer_team_contexts_query(
        project_id=client.project,
        dataset_id=dataset_id,
        league_id=league_id,
        season=season,
        week=week,
        limit=limit,
    )
    return _query_rows(client, sql, job_config)


def get_viewer_team_summary(
    league_id: str,
    *,
    roster_id: int | str | None = None,
    manager_id: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    """Return a compact summary for a viewer-team packet."""
    context = get_viewer_team_context(
        league_id,
        roster_id=roster_id,
        manager_id=manager_id,
        scoring_profile_id=scoring_profile_id,
        client=client,
        dataset_id=dataset_id,
    )
    if context.get("unavailable"):
        return context
    packet = context.get("packet") or {}
    roster_rows = packet.get("roster_rows") or []
    waiver_section = packet.get("waiver_rows") or {}
    waiver_rows = waiver_section.get("available_players") if isinstance(waiver_section, dict) else []
    return {
        "viewer_team_context_id": context.get("viewer_team_context_id"),
        "league_id": context.get("league_id"),
        "roster_id": context.get("roster_id"),
        "manager_display_name": context.get("manager_display_name"),
        "season": context.get("season"),
        "week": context.get("week"),
        "roster_count": len(roster_rows),
        "waiver_count": len(waiver_rows or []),
        "packet_text": context.get("packet_text"),
        "missing_data_flags": context.get("missing_data_flags"),
    }


def build_viewer_team_context_query(
    *,
    project_id: str,
    dataset_id: str,
    league_id: str,
    roster_id: int | str | None = None,
    manager_id: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
) -> tuple[str, bigquery.QueryJobConfig]:
    sql = f"""
    SELECT {VIEWER_TEAM_CONTEXT_SELECT_LIST}
    FROM `{_table_id(project_id, dataset_id, "compat_viewer_team_context")}`
    WHERE league_id = @league_id
        AND scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
        AND (@roster_id IS NULL OR roster_id = @roster_id)
        AND (@manager_id IS NULL OR manager_id = @manager_id)
    ORDER BY season DESC, week DESC, snapshot_timestamp DESC
    LIMIT 1
    """
    return sql, _job_config([
        ("league_id", "STRING", _clean_optional(league_id)),
        ("roster_id", "INT64", _clean_int(roster_id)),
        ("manager_id", "STRING", _clean_optional(manager_id)),
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
    ])


def build_list_viewer_team_contexts_query(
    *,
    project_id: str,
    dataset_id: str,
    league_id: str | None = None,
    season: int | str | None = None,
    week: int | str | None = None,
    limit: int | str | None = DEFAULT_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    sql = f"""
    SELECT
        viewer_team_context_id,
        league_id,
        roster_id,
        manager_id,
        manager_display_name,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        model_run_id,
        ranking_version,
        snapshot_timestamp,
        missing_data_flags,
        created_at,
        updated_at
    FROM `{_table_id(project_id, dataset_id, "compat_viewer_team_context")}`
    WHERE (@league_id IS NULL OR league_id = @league_id)
        AND (@season IS NULL OR season = @season)
        AND (@week IS NULL OR week = @week)
    ORDER BY season DESC, week DESC, league_id, roster_id
    LIMIT @limit
    """
    return sql, _job_config([
        ("league_id", "STRING", _clean_optional(league_id)),
        ("season", "INT64", _clean_int(season)),
        ("week", "INT64", _clean_int(week)),
        ("limit", "INT64", _clamp_limit(limit)),
    ])


def normalize_packet_json(packet_json: str | dict[str, Any] | None) -> dict[str, Any]:
    """Return packet JSON with every required top-level section present."""
    if isinstance(packet_json, dict):
        packet = dict(packet_json)
    elif packet_json:
        try:
            parsed = json.loads(packet_json)
            packet = parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            packet = {}
    else:
        packet = {}
    for key in PACKET_KEYS:
        packet.setdefault(key, [] if key.endswith("_rows") or key in {"team_strengths", "team_weaknesses", "recommended_actions"} else {})
    return packet


def unavailable_viewer_team_context(
    *,
    league_id: str,
    roster_id: int | str | None = None,
    manager_id: str | None = None,
    reason: str,
) -> dict[str, Any]:
    packet = normalize_packet_json(None)
    packet["evidence_metadata"] = {
        "missing_data_flags": [reason],
        "confidence": "unavailable",
    }
    return {
        "unavailable": True,
        "reason": reason,
        "league_id": league_id,
        "roster_id": _clean_int(roster_id),
        "manager_id": _clean_optional(manager_id),
        "packet": packet,
        "packet_json": json.dumps(packet, sort_keys=True),
        "packet_text": "Viewer-team context is not materialized for this league or roster.",
        "missing_data_flags": json.dumps([reason]),
    }


VIEWER_TEAM_CONTEXT_SELECT_LIST = """
        viewer_team_context_id,
        league_id,
        roster_id,
        manager_id,
        manager_display_name,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        model_run_id,
        ranking_version,
        snapshot_timestamp,
        packet_json,
        packet_text,
        source_freshness_json,
        missing_data_flags,
        created_at,
        updated_at
"""


def _query_rows(client: Any, sql: str, job_config: bigquery.QueryJobConfig) -> list[dict[str, Any]]:
    try:
        rows = client.query(sql, job_config=job_config).result()
    except NotFound:
        return []
    return [_row_to_dict(row) for row in rows]


def _job_config(params: list[tuple[str, str, Any]]) -> bigquery.QueryJobConfig:
    return bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=[
            bigquery.ScalarQueryParameter(name, type_name, value)
            for name, type_name, value in params
        ],
    )


def _row_to_dict(row: Any) -> dict[str, Any]:
    if hasattr(row, "items"):
        return dict(row.items())
    if isinstance(row, dict):
        return dict(row)
    return dict(row)


def _clamp_limit(value: int | str | None) -> int:
    try:
        parsed = int(value) if value is not None else DEFAULT_LIMIT
    except (TypeError, ValueError):
        parsed = DEFAULT_LIMIT
    return max(1, min(MAX_LIMIT, parsed))


def _clean_int(value: int | str | None) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _clean_optional(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    if not IDENTIFIER_RE.match(table_name):
        raise ValueError(f"Unsafe BigQuery table name: {table_name}")
    return f"{project_id}.{dataset_id}.{table_name}"
