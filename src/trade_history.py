"""Safe access helpers for Trade Lab player-history context."""

from __future__ import annotations

import os
import re
from typing import Any

import pandas as pd
from google.cloud import bigquery

from src.build_player_identity import normalize_player_name
from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_SCORING_PROFILE = "ppr"
DEFAULT_HISTORY_LIMIT = 24
MAX_HISTORY_LIMIT = 100
MAX_SEASONS_BACK = 10
DEFAULT_MAX_BYTES_BILLED = int(
    os.environ.get("PIGSKIN_CONTEXT_MAX_BYTES_BILLED", "1000000000")
)
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def get_trade_player_history(
    *,
    player_id_internal: str | None = None,
    player_name: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    seasons_back: int = 2,
    limit: int = DEFAULT_HISTORY_LIMIT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> pd.DataFrame:
    """Return recent Trade Lab history from the compatibility view."""

    if not player_id_internal and not player_name:
        raise ValueError("player_id_internal or player_name is required")

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_trade_player_history_query(
        project_id=client.project,
        dataset_id=dataset_id,
        player_id_internal=player_id_internal,
        player_name=player_name,
        scoring_profile_id=scoring_profile_id,
        seasons_back=seasons_back,
        limit=limit,
    )
    return client.query(sql, job_config=job_config).result().to_dataframe()


def resolve_trade_player_lookup(
    lookup: str,
    *,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    limit: int = 5,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Resolve a user-entered player name or ID against compat history."""

    if not str(lookup or "").strip():
        return []

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_trade_player_lookup_query(
        project_id=client.project,
        dataset_id=dataset_id,
        lookup=lookup,
        scoring_profile_id=scoring_profile_id,
        limit=limit,
    )
    rows = client.query(sql, job_config=job_config).result()
    return [dict(row) for row in rows]


def build_trade_player_history_query(
    *,
    project_id: str,
    dataset_id: str,
    player_id_internal: str | None = None,
    player_name: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    seasons_back: int = 2,
    limit: int = DEFAULT_HISTORY_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    """Build a parameterized query for recent player history."""

    normalized_name = normalize_player_name(player_name)
    safe_limit = _clamp_limit(limit)
    safe_seasons_back = _clamp_int(seasons_back, 0, MAX_SEASONS_BACK)
    table_id = _table_id(project_id, dataset_id, "compat_trade_player_history")
    sql = f"""
    SELECT
        player_id_internal,
        source_player_key,
        player_display_name,
        normalized_name,
        position,
        team,
        opponent,
        season,
        week,
        scoring_profile_id,
        total_fantasy_points,
        passing_points,
        rushing_points,
        receiving_points,
        reception_points,
        turnover_points,
        bonus_points,
        fantasy_points_ppr,
        fantasy_points_half_ppr,
        fantasy_points_standard,
        snap_share,
        targets,
        receptions,
        carries,
        target_share,
        rush_share,
        air_yards,
        air_yard_share,
        red_zone_opportunities,
        high_value_touches,
        passing_yards,
        passing_tds,
        interceptions,
        rushing_yards,
        rushing_tds,
        receiving_yards,
        receiving_tds,
        yards_per_carry,
        yards_per_target,
        yards_per_reception,
        catch_rate,
        epa_summary_json,
        qb_split_json,
        game_id,
        home_away,
        game_environment_json,
        opponent_context_json,
        model_run_id,
        ranking_version,
        pigskin_rank_overall,
        pigskin_rank_position,
        pigskin_tier,
        recency_order,
        source_freshness_json,
        missing_data_flags,
        refreshed_at
    FROM `{table_id}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND season >= EXTRACT(YEAR FROM CURRENT_DATE()) - @seasons_back
        AND (
            (@player_id_internal IS NOT NULL AND player_id_internal = @player_id_internal)
            OR (@player_id_internal IS NOT NULL AND source_player_key = @player_id_internal)
            OR (@player_name IS NOT NULL AND LOWER(player_display_name) = LOWER(@player_name))
            OR (@normalized_name IS NOT NULL AND normalized_name = @normalized_name)
        )
    ORDER BY season DESC, week DESC
    LIMIT @limit
    """
    return sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("seasons_back", "INT64", safe_seasons_back),
        ("player_id_internal", "STRING", player_id_internal),
        ("player_name", "STRING", player_name),
        ("normalized_name", "STRING", normalized_name or None),
        ("limit", "INT64", safe_limit),
    ])


def build_trade_player_lookup_query(
    *,
    project_id: str,
    dataset_id: str,
    lookup: str,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    limit: int = 5,
) -> tuple[str, bigquery.QueryJobConfig]:
    """Build a parameterized lookup query for Trade Lab player selection."""

    safe_limit = _clamp_limit(limit)
    normalized_lookup = normalize_player_name(lookup)
    table_id = _table_id(project_id, dataset_id, "compat_trade_player_history")
    sql = f"""
    SELECT
        player_id_internal,
        source_player_key,
        player_display_name,
        normalized_name,
        position,
        team,
        MAX(season) AS latest_season,
        MAX(week) AS latest_week,
        ANY_VALUE(model_run_id) AS model_run_id,
        ANY_VALUE(ranking_version) AS ranking_version,
        ANY_VALUE(pigskin_rank_position) AS pigskin_rank_position,
        ANY_VALUE(pigskin_tier) AS pigskin_tier
    FROM `{table_id}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND (
            player_id_internal = @lookup
            OR source_player_key = @lookup
            OR LOWER(player_display_name) = LOWER(@lookup)
            OR normalized_name = @normalized_lookup
        )
    GROUP BY
        player_id_internal,
        source_player_key,
        player_display_name,
        normalized_name,
        position,
        team
    ORDER BY latest_season DESC, latest_week DESC, player_display_name
    LIMIT @limit
    """
    return sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("lookup", "STRING", str(lookup).strip()),
        ("normalized_lookup", "STRING", normalized_lookup or None),
        ("limit", "INT64", safe_limit),
    ])


def _job_config(params: list[tuple[str, str, Any]]) -> bigquery.QueryJobConfig:
    return bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=[
            bigquery.ScalarQueryParameter(name, type_name, value)
            for name, type_name, value in params
        ]
    )


def _clamp_limit(value: int | str | None) -> int:
    return _clamp_int(value if value is not None else DEFAULT_HISTORY_LIMIT, 1, MAX_HISTORY_LIMIT)


def _clamp_int(value: int | str | None, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value) if value is not None else minimum
    except (TypeError, ValueError):
        parsed = minimum
    return max(minimum, min(maximum, parsed))


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    if not IDENTIFIER_RE.match(table_name):
        raise ValueError(f"Unsafe BigQuery table name: {table_name}")
    return f"{project_id}.{dataset_id}.{table_name}"
