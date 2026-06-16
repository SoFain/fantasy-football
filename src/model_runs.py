"""Helpers for reproducible model-run metadata in BigQuery."""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from google.cloud import bigquery

from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
MODEL_RUNS_TABLE = "model_runs"
SOURCE_FRESHNESS_TABLE = "source_freshness_snapshots"
BIGQUERY_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

DEFAULT_FRESHNESS_TABLES = (
    "play_by_play",
    "weekly_metrics",
    "analytics_player_weekly_truth",
    "analytics_pigskin_rankings",
    "analytics_fraud_watch",
    "player_rosters",
    "injury_reports",
    "weekly_snap_counts",
    "realtime_player_news",
    "sleeper_players_current",
    "sleeper_leagues",
    "sleeper_rosters",
    "sleeper_roster_players",
    "sleeper_available_players",
    "sleeper_viewer_team_snapshots",
)

DEFAULT_MAX_VALUE_TABLES = (
    "analytics_player_weekly_truth",
    "analytics_fraud_watch",
    "analytics_pigskin_rankings_candidates",
    "analytics_pigskin_rankings",
    "analytics_pigskin_rankings_history",
    "analytics_game_environment",
    "analytics_player_qb_weekly",
    "analytics_player_qb_splits",
)


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def create_model_run(
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    model_run_id: str | None = None,
    run_type: str,
    model_name: str | None = None,
    model_version: str | None = None,
    prompt_version: str | None = None,
    code_version: str | None = None,
    season: int | None = None,
    week: int | None = None,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    feature_config_version_id: str | None = None,
    source_freshness_snapshot_id: str | None = None,
    created_by: str | None = None,
    notes: str | None = None,
) -> str:
    """Insert a running model-run row and return its ID."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    model_run_id = model_run_id or _generate_model_run_id(run_type, season, week)

    sql = f"""
    INSERT INTO `{_table_id(client, dataset_id, MODEL_RUNS_TABLE)}` (
        model_run_id,
        run_type,
        model_name,
        model_version,
        prompt_version,
        code_version,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        feature_config_version_id,
        source_freshness_snapshot_id,
        status,
        created_by,
        created_at,
        completed_at,
        error_message,
        notes
    )
    VALUES (
        @model_run_id,
        @run_type,
        @model_name,
        @model_version,
        @prompt_version,
        @code_version,
        @season,
        @week,
        @scoring_profile_id,
        @league_type_id,
        @roster_format_id,
        @feature_config_version_id,
        @source_freshness_snapshot_id,
        'running',
        @created_by,
        CURRENT_TIMESTAMP(),
        NULL,
        NULL,
        @notes
    )
    """
    client.query(sql, job_config=_job_config([
        ("model_run_id", "STRING", model_run_id),
        ("run_type", "STRING", run_type),
        ("model_name", "STRING", model_name),
        ("model_version", "STRING", model_version),
        ("prompt_version", "STRING", prompt_version),
        ("code_version", "STRING", code_version),
        ("season", "INT64", season),
        ("week", "INT64", week),
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("feature_config_version_id", "STRING", feature_config_version_id),
        ("source_freshness_snapshot_id", "STRING", source_freshness_snapshot_id),
        ("created_by", "STRING", created_by),
        ("notes", "STRING", notes),
    ])).result()
    return model_run_id


def mark_model_run_complete(
    model_run_id: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    notes: str | None = None,
) -> None:
    """Mark a model run complete and stamp completion time."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql = f"""
    UPDATE `{_table_id(client, dataset_id, MODEL_RUNS_TABLE)}`
    SET
        status = 'complete',
        completed_at = CURRENT_TIMESTAMP(),
        notes = IF(@notes IS NULL, notes, @notes)
    WHERE model_run_id = @model_run_id
    """
    client.query(sql, job_config=_job_config([
        ("model_run_id", "STRING", model_run_id),
        ("notes", "STRING", notes),
    ])).result()


def mark_model_run_failed(
    model_run_id: str,
    error_message: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    notes: str | None = None,
) -> None:
    """Mark a model run failed, preserving the error text."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql = f"""
    UPDATE `{_table_id(client, dataset_id, MODEL_RUNS_TABLE)}`
    SET
        status = 'failed',
        completed_at = CURRENT_TIMESTAMP(),
        error_message = @error_message,
        notes = IF(@notes IS NULL, notes, @notes)
    WHERE model_run_id = @model_run_id
    """
    client.query(sql, job_config=_job_config([
        ("model_run_id", "STRING", model_run_id),
        ("error_message", "STRING", error_message),
        ("notes", "STRING", notes),
    ])).result()


def get_model_run(
    model_run_id: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any] | None:
    """Fetch one model-run row by ID."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql = f"""
    SELECT *
    FROM `{_table_id(client, dataset_id, MODEL_RUNS_TABLE)}`
    WHERE model_run_id = @model_run_id
    LIMIT 1
    """
    rows = client.query(sql, job_config=_job_config([
        ("model_run_id", "STRING", model_run_id),
    ])).result()
    return _first_row_as_dict(rows)


def get_latest_model_run(
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    run_type: str | None = None,
    season: int | None = None,
    week: int | None = None,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    status: str | None = "complete",
) -> dict[str, Any] | None:
    """Fetch the newest model-run row matching the provided filters."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    filters = []
    params = []
    for name, value, param_type in (
        ("run_type", run_type, "STRING"),
        ("season", season, "INT64"),
        ("week", week, "INT64"),
        ("scoring_profile_id", scoring_profile_id, "STRING"),
        ("league_type_id", league_type_id, "STRING"),
        ("roster_format_id", roster_format_id, "STRING"),
        ("status", status, "STRING"),
    ):
        if value is not None:
            filters.append(f"{name} = @{name}")
            params.append((name, param_type, value))

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""
    sql = f"""
    SELECT *
    FROM `{_table_id(client, dataset_id, MODEL_RUNS_TABLE)}`
    {where_clause}
    ORDER BY created_at DESC
    LIMIT 1
    """
    rows = client.query(sql, job_config=_job_config(params)).result()
    return _first_row_as_dict(rows)


def create_source_freshness_snapshot(
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    source_table_names: list[str] | tuple[str, ...] | None = None,
    max_rows_for_column_scan: int = 250_000,
    max_value_table_names: list[str] | tuple[str, ...] | None = None,
) -> str:
    """Capture bounded source freshness metadata and return the snapshot ID."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    source_table_names = tuple(source_table_names or DEFAULT_FRESHNESS_TABLES)
    max_value_table_names = tuple(max_value_table_names or DEFAULT_MAX_VALUE_TABLES)
    snapshot_id = _generate_source_freshness_snapshot_id()
    snapshot = _build_source_freshness_snapshot(
        client=client,
        dataset_id=dataset_id,
        source_table_names=source_table_names,
        max_rows_for_column_scan=max_rows_for_column_scan,
        max_value_table_names=max_value_table_names,
    )

    sql = f"""
    INSERT INTO `{_table_id(client, dataset_id, SOURCE_FRESHNESS_TABLE)}`
        (source_freshness_snapshot_id, snapshot_json, created_at)
    SELECT
        @source_freshness_snapshot_id,
        PARSE_JSON(@snapshot_json),
        CURRENT_TIMESTAMP()
    """
    client.query(sql, job_config=_job_config([
        ("source_freshness_snapshot_id", "STRING", snapshot_id),
        ("snapshot_json", "STRING", json.dumps(snapshot, sort_keys=True)),
    ])).result()
    return snapshot_id


def _build_source_freshness_snapshot(
    *,
    client: Any,
    dataset_id: str,
    source_table_names: tuple[str, ...],
    max_rows_for_column_scan: int,
    max_value_table_names: tuple[str, ...],
) -> dict[str, Any]:
    _validate_bigquery_identifier(dataset_id, "dataset_id")
    source_table_names = tuple(dict.fromkeys(
        _validate_bigquery_identifier(table_name, "source_table_name")
        for table_name in source_table_names
    ))
    max_value_table_names = tuple(dict.fromkeys(
        _validate_bigquery_identifier(table_name, "max_value_table_name")
        for table_name in max_value_table_names
    ))
    max_value_table_set = set(max_value_table_names)
    metadata = _fetch_table_metadata(client, dataset_id, source_table_names)
    columns = _fetch_table_columns(client, dataset_id, source_table_names)
    snapshot_tables = []

    for table_name in source_table_names:
        table_meta = metadata.get(table_name)
        table_columns = columns.get(table_name, set())
        row = {
            "table_name": table_name,
            "exists": table_meta is not None,
            "row_count": table_meta.get("row_count") if table_meta else None,
            "last_modified_time": table_meta.get("last_modified_time") if table_meta else None,
            "missing_table": table_meta is None,
            "season_column_present": "season" in table_columns,
            "week_column_present": "week" in table_columns,
            "max_season": None,
            "max_week": None,
            "max_values_skipped": True,
            "max_values_skip_reason": "not_checked",
            "max_values_error": None,
        }
        if _should_scan_max_values(table_name, row, max_rows_for_column_scan, max_value_table_set):
            row.update(_fetch_max_values(client, dataset_id, table_name, table_columns))
        else:
            row["max_values_skip_reason"] = _max_values_skip_reason(
                table_name,
                row,
                max_rows_for_column_scan,
                max_value_table_set,
            )
        snapshot_tables.append(row)

    return {
        "created_at": _utc_timestamp(),
        "dataset_id": dataset_id,
        "max_rows_for_column_scan": max_rows_for_column_scan,
        "max_value_table_names": sorted(max_value_table_set),
        "tables": snapshot_tables,
    }


def _fetch_table_metadata(
    client: Any,
    dataset_id: str,
    source_table_names: tuple[str, ...],
) -> dict[str, dict[str, Any]]:
    sql = f"""
    SELECT
        table_id AS table_name,
        row_count,
        CAST(TIMESTAMP_MILLIS(last_modified_time) AS STRING) AS last_modified_time
    FROM `{client.project}.{dataset_id}.__TABLES__`
    WHERE table_id IN UNNEST(@table_names)
    """
    rows = client.query(sql, job_config=bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("table_names", "STRING", list(source_table_names))
        ]
    )).result()
    return {
        row.table_name: {
            "row_count": row.row_count,
            "last_modified_time": row.last_modified_time,
        }
        for row in rows
    }


def _fetch_table_columns(
    client: Any,
    dataset_id: str,
    source_table_names: tuple[str, ...],
) -> dict[str, set[str]]:
    sql = f"""
    SELECT table_name, column_name
    FROM `{client.project}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name IN UNNEST(@table_names)
        AND column_name IN ('season', 'week')
    """
    rows = client.query(sql, job_config=bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("table_names", "STRING", list(source_table_names))
        ]
    )).result()
    columns: dict[str, set[str]] = {}
    for row in rows:
        columns.setdefault(row.table_name, set()).add(row.column_name)
    return columns


def _fetch_max_values(
    client: Any,
    dataset_id: str,
    table_name: str,
    table_columns: set[str],
) -> dict[str, Any]:
    selected = []
    if "season" in table_columns:
        selected.append("MAX(season) AS max_season")
    if "week" in table_columns:
        selected.append("MAX(week) AS max_week")
    try:
        row = next(iter(client.query(
            f"SELECT {', '.join(selected)} FROM `{_table_id(client, dataset_id, table_name)}`"
        ).result()), None)
        return {
            "max_season": getattr(row, "max_season", None) if row else None,
            "max_week": getattr(row, "max_week", None) if row else None,
            "max_values_skipped": False,
            "max_values_skip_reason": None,
            "max_values_error": None,
        }
    except Exception as exc:
        return {
            "max_values_skipped": True,
            "max_values_skip_reason": "query_error",
            "max_values_error": str(exc),
        }


def _should_scan_max_values(
    table_name: str,
    row: dict[str, Any],
    max_rows_for_column_scan: int,
    max_value_table_names: set[str],
) -> bool:
    if row["missing_table"]:
        return False
    if table_name not in max_value_table_names:
        return False
    if not row["season_column_present"] and not row["week_column_present"]:
        return False
    row_count = row["row_count"]
    return row_count is not None and row_count <= max_rows_for_column_scan


def _max_values_skip_reason(
    table_name: str,
    row: dict[str, Any],
    max_rows_for_column_scan: int,
    max_value_table_names: set[str],
) -> str:
    if row["missing_table"]:
        return "missing_table"
    if table_name not in max_value_table_names:
        return "not_allowlisted"
    if not row["season_column_present"] and not row["week_column_present"]:
        return "no_season_or_week_column"
    row_count = row["row_count"]
    if row_count is None:
        return "unknown_row_count"
    if row_count > max_rows_for_column_scan:
        return "row_count_over_limit"
    return "not_checked"


def _job_config(params: list[tuple[str, str, Any]]) -> bigquery.QueryJobConfig:
    return bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(name, param_type, value)
            for name, param_type, value in params
        ]
    )


def _table_id(client: Any, dataset_id: str, table_name: str) -> str:
    _validate_bigquery_identifier(dataset_id, "dataset_id")
    _validate_bigquery_identifier(table_name, "table_name")
    return f"{client.project}.{dataset_id}.{table_name}"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _generate_model_run_id(run_type: str, season: int | None, week: int | None) -> str:
    parts = [_safe_id_part(run_type), str(season or "na"), str(week or "na")]
    parts.append(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parts.append(uuid.uuid4().hex[:8])
    return "-".join(parts)


def _generate_source_freshness_snapshot_id() -> str:
    return f"freshness-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"


def _safe_id_part(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_]+", "-", value.strip().lower())
    return value.strip("-") or "model-run"


def _validate_bigquery_identifier(value: str, label: str) -> str:
    if not BIGQUERY_IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"Invalid BigQuery {label}: {value!r}")
    return value


def _first_row_as_dict(rows: Any) -> dict[str, Any] | None:
    for row in rows:
        if hasattr(row, "items"):
            return dict(row.items())
        if isinstance(row, dict):
            return row
        return dict(row)
    return None
