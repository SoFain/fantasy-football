"""Safe access helpers for current trade asset context."""

from __future__ import annotations

import os
import re
from typing import Any

from google.cloud import bigquery

from src.build_player_identity import normalize_player_name
from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_SCORING_PROFILE = "ppr"
DEFAULT_LEAGUE_TYPE = "redraft"
DEFAULT_ROSTER_FORMAT = "one_qb"
DEFAULT_LIMIT = 100
MAX_LIMIT = 250
MAX_COMPARE_ASSETS = 12
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("TRADE_ASSETS_MAX_BYTES_BILLED", "1000000000"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def get_trade_assets(
    *,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    position: str | None = None,
    search: str | None = None,
    limit: int = DEFAULT_LIMIT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return current trade assets from the compatibility view."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_trade_assets_query(
        project_id=client.project,
        dataset_id=dataset_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        position=position,
        search=search,
        limit=limit,
    )
    rows = client.query(sql, job_config=job_config).result()
    return [_row_to_dict(row) for row in rows]


def get_trade_asset(
    *,
    player_id_internal: str | None = None,
    player_name: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any] | None:
    """Return one trade asset by canonical ID or player name."""

    if not player_id_internal and not player_name:
        raise ValueError("player_id_internal or player_name is required")

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_trade_asset_query(
        project_id=client.project,
        dataset_id=dataset_id,
        player_id_internal=player_id_internal,
        player_name=player_name,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    rows = client.query(sql, job_config=job_config).result()
    for row in rows:
        return _row_to_dict(row)
    return None


def compare_trade_assets(
    player_ids_or_names: list[str] | tuple[str, ...],
    *,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return a capped set of comparable trade assets."""

    lookups = [str(value).strip() for value in player_ids_or_names if str(value or "").strip()]
    if len(lookups) > MAX_COMPARE_ASSETS:
        raise ValueError(f"compare_trade_assets supports at most {MAX_COMPARE_ASSETS} assets")
    if not lookups:
        return []

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_compare_trade_assets_query(
        project_id=client.project,
        dataset_id=dataset_id,
        lookups=lookups,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    rows = client.query(sql, job_config=job_config).result()
    return [_row_to_dict(row) for row in rows]


def build_trade_assets_query(
    *,
    project_id: str,
    dataset_id: str,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    position: str | None = None,
    search: str | None = None,
    limit: int | str | None = DEFAULT_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    normalized_search = normalize_player_name(search)
    sql = f"""
    SELECT {TRADE_ASSET_SELECT_LIST}
    FROM `{_table_id(project_id, dataset_id, "compat_trade_assets_current")}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
        AND (@position IS NULL OR position = @position)
        AND (
            @search IS NULL
            OR LOWER(display_name) LIKE CONCAT('%', LOWER(@search), '%')
            OR LOWER(market_player_name) LIKE CONCAT('%', LOWER(@search), '%')
            OR normalized_name LIKE CONCAT('%', @normalized_search, '%')
            OR player_id_internal = @search
            OR source_player_key = @search
        )
    ORDER BY market_value DESC, pigskin_rank_position ASC, display_name ASC
    LIMIT @limit
    """
    return sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("position", "STRING", _clean_optional(position)),
        ("search", "STRING", _clean_optional(search)),
        ("normalized_search", "STRING", normalized_search or None),
        ("limit", "INT64", _clamp_limit(limit)),
    ])


def build_trade_asset_query(
    *,
    project_id: str,
    dataset_id: str,
    player_id_internal: str | None = None,
    player_name: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
) -> tuple[str, bigquery.QueryJobConfig]:
    normalized_name = normalize_player_name(player_name)
    sql = f"""
    SELECT {TRADE_ASSET_SELECT_LIST}
    FROM `{_table_id(project_id, dataset_id, "compat_trade_assets_current")}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
        AND (
            (@player_id_internal IS NOT NULL AND player_id_internal = @player_id_internal)
            OR (@player_id_internal IS NOT NULL AND source_player_key = @player_id_internal)
            OR (@player_name IS NOT NULL AND LOWER(display_name) = LOWER(@player_name))
            OR (@player_name IS NOT NULL AND LOWER(market_player_name) = LOWER(@player_name))
            OR (@normalized_name IS NOT NULL AND normalized_name = @normalized_name)
        )
    ORDER BY market_value DESC, pigskin_rank_position ASC, display_name ASC
    LIMIT 1
    """
    return sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("player_id_internal", "STRING", _clean_optional(player_id_internal)),
        ("player_name", "STRING", _clean_optional(player_name)),
        ("normalized_name", "STRING", normalized_name or None),
    ])


def build_compare_trade_assets_query(
    *,
    project_id: str,
    dataset_id: str,
    lookups: list[str],
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
) -> tuple[str, bigquery.QueryJobConfig]:
    normalized_lookups = [normalize_player_name(value) for value in lookups]
    sql = f"""
    SELECT {TRADE_ASSET_SELECT_LIST}
    FROM `{_table_id(project_id, dataset_id, "compat_trade_assets_current")}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
        AND (
            player_id_internal IN UNNEST(@lookups)
            OR source_player_key IN UNNEST(@lookups)
            OR LOWER(display_name) IN UNNEST(@lower_lookups)
            OR LOWER(market_player_name) IN UNNEST(@lower_lookups)
            OR normalized_name IN UNNEST(@normalized_lookups)
        )
    QUALIFY ROW_NUMBER() OVER(
        PARTITION BY COALESCE(player_id_internal, source_player_key, normalized_name)
        ORDER BY market_value DESC, pigskin_rank_position ASC
    ) = 1
    ORDER BY market_value DESC, pigskin_rank_position ASC, display_name ASC
    """
    return sql, bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=[
            bigquery.ScalarQueryParameter("scoring_profile_id", "STRING", scoring_profile_id),
            bigquery.ScalarQueryParameter("league_type_id", "STRING", league_type_id),
            bigquery.ScalarQueryParameter("roster_format_id", "STRING", roster_format_id),
            bigquery.ArrayQueryParameter("lookups", "STRING", lookups),
            bigquery.ArrayQueryParameter("lower_lookups", "STRING", [value.lower() for value in lookups]),
            bigquery.ArrayQueryParameter("normalized_lookups", "STRING", normalized_lookups),
        ],
    )


TRADE_ASSET_SELECT_LIST = """
        player_id_internal,
        source_player_key,
        sleeper_player_id,
        gsis_id,
        pfr_id,
        display_name,
        normalized_name,
        position,
        fantasy_positions,
        team,
        age,
        rookie_year,
        active_status,
        market_source,
        market_player_id,
        market_player_name,
        market_value,
        market_value_raw,
        market_value_rank_overall,
        market_value_rank_position,
        market_tier,
        market_snapshot_date,
        market_snapshot_timestamp,
        market_format_label,
        market_scoring_label,
        market_league_type_label,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        model_run_id,
        ranking_version,
        pigskin_rank_overall,
        pigskin_rank_position,
        pigskin_tier,
        pigskin_projection,
        pigskin_confidence,
        pigskin_risk_score,
        pigskin_breakout_score,
        pigskin_fraud_risk_score,
        recent_fantasy_points_per_game,
        recent_usage_summary_json,
        recent_trend_label,
        position_scarcity_score,
        replacement_value_estimate,
        dynasty_value_placeholder,
        redraft_value_placeholder,
        risk_adjusted_trade_value,
        trade_asset_summary_json,
        source_freshness_json,
        missing_data_flags,
        created_at,
        updated_at
"""


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
