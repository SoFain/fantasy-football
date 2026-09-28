"""Read-only helpers for backtest dashboard output tables."""

from __future__ import annotations

import os
import re
from typing import Any

from google.cloud import bigquery

from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_LIMIT = 50
MAX_LIMIT = 500
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("BACKTEST_READERS_MAX_BYTES_BILLED", "1000000000"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")

BACKTEST_RUNS_TABLE = "backtest_runs"
SUMMARY_TABLE = "backtest_result_summary"
PLAYER_WEEK_TABLE = "backtest_result_player_week"
CALIBRATION_TABLE = "backtest_calibration_bins"

READABLE_BACKTEST_TABLES = frozenset(
    {
        BACKTEST_RUNS_TABLE,
        SUMMARY_TABLE,
        PLAYER_WEEK_TABLE,
        CALIBRATION_TABLE,
    }
)

SORT_OPTIONS = {
    "absolute_error_desc": "absolute_error DESC, display_name ASC",
    "absolute_error_asc": "absolute_error ASC, display_name ASC",
    "actual_points_desc": "actual_points DESC, display_name ASC",
    "projected_points_desc": "projected_points DESC, display_name ASC",
    "rank_error_desc": "ABS(rank_error_overall) DESC, display_name ASC",
    "rank_error_position_desc": "ABS(rank_error_position) DESC, display_name ASC",
    "week_desc": "season DESC, week DESC, display_name ASC",
}


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def list_backtest_runs(
    status: str | None = None,
    limit: int = DEFAULT_LIMIT,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return recent backtest run ledger rows."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_list_backtest_runs_query(
        project_id=client.project,
        dataset_id=dataset_id,
        status=status,
        limit=limit,
    )
    return _query_rows(client, sql, job_config)


def get_backtest_run(
    backtest_run_id: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any] | None:
    """Return one backtest run by ID."""

    if not _clean_optional(backtest_run_id):
        raise ValueError("backtest_run_id is required")
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_get_backtest_run_query(
        project_id=client.project,
        dataset_id=dataset_id,
        backtest_run_id=backtest_run_id,
    )
    rows = _query_rows(client, sql, job_config)
    return rows[0] if rows else None


def get_backtest_summary(
    backtest_run_id: str | None = None,
    model_run_id: str | None = None,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    position: str | None = None,
    projection_horizon: str | None = None,
    season: int | None = None,
    week: int | None = None,
    limit: int = MAX_LIMIT,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return summary rows from the backtest result summary table."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_backtest_summary_query(
        project_id=client.project,
        dataset_id=dataset_id,
        backtest_run_id=backtest_run_id,
        model_run_id=model_run_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        position=position,
        projection_horizon=projection_horizon,
        season=season,
        week=week,
        limit=limit,
    )
    return _query_rows(client, sql, job_config)


def get_backtest_player_errors(
    backtest_run_id: str,
    position: str | None = None,
    limit: int = 100,
    sort_by: str = "absolute_error_desc",
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return capped player-week misses or hits for one backtest run."""

    if not _clean_optional(backtest_run_id):
        raise ValueError("backtest_run_id is required")
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_backtest_player_errors_query(
        project_id=client.project,
        dataset_id=dataset_id,
        backtest_run_id=backtest_run_id,
        position=position,
        limit=limit,
        sort_by=sort_by,
    )
    return _query_rows(client, sql, job_config)


def get_backtest_calibration(
    backtest_run_id: str,
    position: str | None = None,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return calibration buckets for one backtest run."""

    if not _clean_optional(backtest_run_id):
        raise ValueError("backtest_run_id is required")
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_backtest_calibration_query(
        project_id=client.project,
        dataset_id=dataset_id,
        backtest_run_id=backtest_run_id,
        position=position,
    )
    return _query_rows(client, sql, job_config)


def get_backtest_leaderboard(
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    projection_horizon: str | None = None,
    limit: int = DEFAULT_LIMIT,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return model-run quality rows aggregated from backtest summaries."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_backtest_leaderboard_query(
        project_id=client.project,
        dataset_id=dataset_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        projection_horizon=projection_horizon,
        limit=limit,
    )
    return _query_rows(client, sql, job_config)


def export_backtest_summary_markdown(
    backtest_run_id: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> str:
    """Return a markdown summary for one backtest run."""

    run = get_backtest_run(backtest_run_id, client=client, dataset_id=dataset_id)
    summary_rows = get_backtest_summary(
        backtest_run_id=backtest_run_id,
        client=client,
        dataset_id=dataset_id,
    )
    if not run and not summary_rows:
        return f"# Backtest Summary\n\nNo backtest summary rows found for `{backtest_run_id}`.\n"

    overall = _find_overall_summary(summary_rows)
    lines = [
        "# Backtest Summary",
        "",
        f"- backtest_run_id: `{backtest_run_id}`",
        f"- model_run_id: `{(run or {}).get('model_run_id') or (overall or {}).get('model_run_id') or 'unknown'}`",
        f"- projection_horizon: `{(run or {}).get('projection_horizon') or (overall or {}).get('projection_horizon') or 'unknown'}`",
        f"- scoring_profile_id: `{(run or {}).get('scoring_profile_id') or (overall or {}).get('scoring_profile_id') or 'unknown'}`",
        f"- league_type_id: `{(run or {}).get('league_type_id') or (overall or {}).get('league_type_id') or 'unknown'}`",
        f"- roster_format_id: `{(run or {}).get('roster_format_id') or (overall or {}).get('roster_format_id') or 'unknown'}`",
        "",
    ]
    if overall:
        lines.extend(
            [
                "## Key Metrics",
                "",
                f"- sample size: `{overall.get('player_count')}`",
                f"- MAE: `{_format_metric(overall.get('mae'))}`",
                f"- RMSE: `{_format_metric(overall.get('rmse'))}`",
                f"- bias: `{_format_metric(overall.get('mean_bias'))}`",
                f"- rank MAE overall: `{_format_metric(overall.get('rank_mae_overall'))}`",
                f"- top 12 hit rate: `{_format_metric(overall.get('top_12_hit_rate'))}`",
                f"- top 24 hit rate: `{_format_metric(overall.get('top_24_hit_rate'))}`",
                f"- boom precision: `{_format_metric(overall.get('boom_precision'))}`",
                f"- bust precision: `{_format_metric(overall.get('bust_precision'))}`",
                f"- calibration rate: `{_format_metric(overall.get('range_calibration_rate'))}`",
                "",
            ]
        )
    else:
        lines.extend(["No overall summary row found.", ""])
    return "\n".join(lines)


def build_list_backtest_runs_query(
    *,
    project_id: str,
    dataset_id: str,
    status: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    sql = f"""
    SELECT
        backtest_run_id,
        model_run_id,
        backtest_name,
        backtest_version,
        projection_horizon,
        season_start,
        season_end,
        week_start,
        week_end,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        status,
        created_by,
        created_at,
        completed_at,
        error_message,
        notes
    FROM `{_table_id(project_id, dataset_id, BACKTEST_RUNS_TABLE)}`
    WHERE @status IS NULL OR status = @status
    ORDER BY created_at DESC
    LIMIT @limit
    """
    return sql, _job_config(
        [
            ("status", "STRING", _clean_optional(status)),
            ("limit", "INT64", _clamp_limit(limit)),
        ]
    )


def build_get_backtest_run_query(
    *,
    project_id: str,
    dataset_id: str,
    backtest_run_id: str,
) -> tuple[str, bigquery.QueryJobConfig]:
    sql = f"""
    SELECT
        backtest_run_id,
        model_run_id,
        backtest_name,
        backtest_version,
        projection_horizon,
        season_start,
        season_end,
        week_start,
        week_end,
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
    FROM `{_table_id(project_id, dataset_id, BACKTEST_RUNS_TABLE)}`
    WHERE backtest_run_id = @backtest_run_id
    LIMIT 1
    """
    return sql, _job_config([("backtest_run_id", "STRING", backtest_run_id)])


def build_backtest_summary_query(
    *,
    project_id: str,
    dataset_id: str,
    backtest_run_id: str | None = None,
    model_run_id: str | None = None,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    position: str | None = None,
    projection_horizon: str | None = None,
    season: int | None = None,
    week: int | None = None,
    limit: int = MAX_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    sql = f"""
    SELECT
        backtest_run_id,
        model_run_id,
        projection_horizon,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        position,
        season,
        week,
        player_count,
        mae,
        rmse,
        mean_bias,
        rank_mae_overall,
        rank_mae_position,
        spearman_proxy,
        top_12_hit_rate,
        top_24_hit_rate,
        boom_precision,
        bust_precision,
        range_calibration_rate,
        summary_json,
        created_at
    FROM `{_table_id(project_id, dataset_id, SUMMARY_TABLE)}`
    WHERE (@backtest_run_id IS NULL OR backtest_run_id = @backtest_run_id)
        AND (@model_run_id IS NULL OR model_run_id = @model_run_id)
        AND (@scoring_profile_id IS NULL OR scoring_profile_id = @scoring_profile_id)
        AND (@league_type_id IS NULL OR league_type_id = @league_type_id)
        AND (@roster_format_id IS NULL OR roster_format_id = @roster_format_id)
        AND (@position IS NULL OR position = @position)
        AND (@projection_horizon IS NULL OR projection_horizon = @projection_horizon)
        AND (@season IS NULL OR season = @season)
        AND (@week IS NULL OR week = @week)
    ORDER BY created_at DESC, position ASC, season DESC, week DESC
    LIMIT @limit
    """
    return sql, _job_config(
        [
            ("backtest_run_id", "STRING", _clean_optional(backtest_run_id)),
            ("model_run_id", "STRING", _clean_optional(model_run_id)),
            ("scoring_profile_id", "STRING", _clean_optional(scoring_profile_id)),
            ("league_type_id", "STRING", _clean_optional(league_type_id)),
            ("roster_format_id", "STRING", _clean_optional(roster_format_id)),
            ("position", "STRING", _clean_optional(position)),
            ("projection_horizon", "STRING", _clean_optional(projection_horizon)),
            ("season", "INT64", _int_or_none(season)),
            ("week", "INT64", _int_or_none(week)),
            ("limit", "INT64", _clamp_limit(limit)),
        ]
    )


def build_backtest_player_errors_query(
    *,
    project_id: str,
    dataset_id: str,
    backtest_run_id: str,
    position: str | None = None,
    limit: int = 100,
    sort_by: str = "absolute_error_desc",
) -> tuple[str, bigquery.QueryJobConfig]:
    order_by = _sort_clause(sort_by)
    sql = f"""
    SELECT
        backtest_run_id,
        model_run_id,
        player_id_internal,
        source_player_key,
        display_name,
        position,
        team,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        projection_horizon,
        projected_points,
        actual_points,
        absolute_error,
        squared_error,
        projected_rank_overall,
        actual_rank_overall,
        projected_rank_position,
        actual_rank_position,
        rank_error_overall,
        rank_error_position,
        projected_floor,
        projected_ceiling,
        actual_inside_range,
        projected_boom_flag,
        actual_boom_flag,
        projected_bust_flag,
        actual_bust_flag,
        result_json,
        missing_data_flags,
        created_at
    FROM `{_table_id(project_id, dataset_id, PLAYER_WEEK_TABLE)}`
    WHERE backtest_run_id = @backtest_run_id
        AND (@position IS NULL OR position = @position)
    ORDER BY {order_by}
    LIMIT @limit
    """
    return sql, _job_config(
        [
            ("backtest_run_id", "STRING", backtest_run_id),
            ("position", "STRING", _clean_optional(position)),
            ("limit", "INT64", _clamp_limit(limit)),
        ]
    )


def build_backtest_calibration_query(
    *,
    project_id: str,
    dataset_id: str,
    backtest_run_id: str,
    position: str | None = None,
) -> tuple[str, bigquery.QueryJobConfig]:
    sql = f"""
    SELECT
        backtest_run_id,
        model_run_id,
        projection_horizon,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        position,
        bin_name,
        bin_min,
        bin_max,
        player_count,
        avg_projected,
        avg_actual,
        avg_error,
        calibration_json,
        created_at
    FROM `{_table_id(project_id, dataset_id, CALIBRATION_TABLE)}`
    WHERE backtest_run_id = @backtest_run_id
        AND (@position IS NULL OR position = @position)
    ORDER BY position ASC, bin_min ASC, bin_name ASC
    LIMIT @limit
    """
    return sql, _job_config(
        [
            ("backtest_run_id", "STRING", backtest_run_id),
            ("position", "STRING", _clean_optional(position)),
            ("limit", "INT64", MAX_LIMIT),
        ]
    )


def build_backtest_leaderboard_query(
    *,
    project_id: str,
    dataset_id: str,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    projection_horizon: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    sql = f"""
    SELECT
        backtest_run_id,
        model_run_id,
        projection_horizon,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        SUM(player_count) AS sample_size,
        AVG(mae) AS avg_mae,
        AVG(rmse) AS avg_rmse,
        AVG(mean_bias) AS avg_bias,
        AVG(rank_mae_overall) AS avg_rank_error,
        AVG(top_12_hit_rate) AS avg_top_12_hit_rate,
        AVG(top_24_hit_rate) AS avg_top_24_hit_rate,
        AVG(range_calibration_rate) AS avg_calibration_rate,
        MAX(created_at) AS latest_summary_at
    FROM `{_table_id(project_id, dataset_id, SUMMARY_TABLE)}`
    WHERE position IS NULL
        AND season IS NULL
        AND week IS NULL
        AND (@scoring_profile_id IS NULL OR scoring_profile_id = @scoring_profile_id)
        AND (@league_type_id IS NULL OR league_type_id = @league_type_id)
        AND (@roster_format_id IS NULL OR roster_format_id = @roster_format_id)
        AND (@projection_horizon IS NULL OR projection_horizon = @projection_horizon)
    GROUP BY
        backtest_run_id,
        model_run_id,
        projection_horizon,
        scoring_profile_id,
        league_type_id,
        roster_format_id
    ORDER BY avg_mae ASC, avg_rmse ASC, latest_summary_at DESC
    LIMIT @limit
    """
    return sql, _job_config(
        [
            ("scoring_profile_id", "STRING", _clean_optional(scoring_profile_id)),
            ("league_type_id", "STRING", _clean_optional(league_type_id)),
            ("roster_format_id", "STRING", _clean_optional(roster_format_id)),
            ("projection_horizon", "STRING", _clean_optional(projection_horizon)),
            ("limit", "INT64", _clamp_limit(limit)),
        ]
    )


def _query_rows(client: Any, sql: str, job_config: bigquery.QueryJobConfig) -> list[dict[str, Any]]:
    rows = client.query(sql, job_config=job_config).result()
    return [_row_to_dict(row) for row in rows]


def _job_config(params: list[tuple[str, str, Any]]) -> bigquery.QueryJobConfig:
    return bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=[
            bigquery.ScalarQueryParameter(name, type_name, value)
            for name, type_name, value in params
        ],
    )


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if table_name not in READABLE_BACKTEST_TABLES:
        raise ValueError(f"Unsupported backtest reader table: {table_name}")
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    return f"{project_id}.{dataset_id}.{table_name}"


def _row_to_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return dict(row)
    if hasattr(row, "items"):
        return dict(row.items())
    return dict(row)


def _clamp_limit(value: int | str | None) -> int:
    try:
        parsed = int(value) if value is not None else DEFAULT_LIMIT
    except (TypeError, ValueError):
        parsed = DEFAULT_LIMIT
    return max(1, min(MAX_LIMIT, parsed))


def _clean_optional(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _int_or_none(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _sort_clause(sort_by: str) -> str:
    try:
        return SORT_OPTIONS[sort_by]
    except KeyError as exc:
        raise ValueError(f"Unsupported backtest player error sort: {sort_by}") from exc


def _find_overall_summary(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    for row in rows:
        if row.get("position") is None and row.get("season") is None and row.get("week") is None:
            return row
    return rows[0] if rows else None


def _format_metric(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return str(value)
