"""Safe access helpers for current player-profile context."""

from __future__ import annotations

import os
import re
from typing import Any

from google.cloud import bigquery

from src.build_player_identity import normalize_player_name
from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_SCORING_PROFILE = "ppr"
DEFAULT_SEARCH_LIMIT = 25
DEFAULT_LIST_LIMIT = 5000
MAX_SEARCH_LIMIT = 100
MAX_LIST_LIMIT = 10000
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("PLAYER_PROFILES_MAX_BYTES_BILLED", "1000000000"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def get_player_profile(
    *,
    player_id_internal: str | None = None,
    player_name: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any] | None:
    """Return one current profile row from the compatibility view."""

    if not player_id_internal and not player_name:
        raise ValueError("player_id_internal or player_name is required")

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_player_profile_query(
        project_id=client.project,
        dataset_id=dataset_id,
        player_id_internal=player_id_internal,
        player_name=player_name,
        scoring_profile_id=scoring_profile_id,
    )
    rows = list(client.query(sql, job_config=job_config).result())
    return dict(rows[0]) if rows else None


def search_player_profiles(
    query: str,
    *,
    position: str | None = None,
    team: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    limit: int = DEFAULT_SEARCH_LIMIT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Search current profile rows from the compatibility view."""

    if not str(query or "").strip():
        return []

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_player_profile_search_query(
        project_id=client.project,
        dataset_id=dataset_id,
        query=query,
        position=position,
        team=team,
        scoring_profile_id=scoring_profile_id,
        limit=limit,
    )
    rows = client.query(sql, job_config=job_config).result()
    return [dict(row) for row in rows]


def list_player_profiles(
    *,
    position: str | None = None,
    team: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    limit: int = DEFAULT_LIST_LIMIT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return current profile rows from the compatibility view."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_player_profiles_list_query(
        project_id=client.project,
        dataset_id=dataset_id,
        position=position,
        team=team,
        scoring_profile_id=scoring_profile_id,
        limit=limit,
    )
    rows = client.query(sql, job_config=job_config).result()
    return [dict(row) for row in rows]


def build_player_profile_query(
    *,
    project_id: str,
    dataset_id: str,
    player_id_internal: str | None = None,
    player_name: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
) -> tuple[str, bigquery.QueryJobConfig]:
    normalized_name = normalize_player_name(player_name)
    table_id = _table_id(project_id, dataset_id, "compat_player_profiles_current")
    sql = f"""
    SELECT
        {PROFILE_SELECT_LIST}
    FROM `{table_id}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND (
            (@player_id_internal IS NOT NULL AND player_id_internal = @player_id_internal)
            OR (@player_id_internal IS NOT NULL AND source_player_key = @player_id_internal)
            OR (@player_name IS NOT NULL AND LOWER(display_name) = LOWER(@player_name))
            OR (@normalized_name IS NOT NULL AND normalized_name = @normalized_name)
        )
    ORDER BY as_of_season DESC, as_of_week DESC, pigskin_rank_position ASC
    LIMIT 1
    """
    return sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("player_id_internal", "STRING", player_id_internal),
        ("player_name", "STRING", player_name),
        ("normalized_name", "STRING", normalized_name or None),
    ])


def build_player_profile_search_query(
    *,
    project_id: str,
    dataset_id: str,
    query: str,
    position: str | None = None,
    team: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    limit: int = DEFAULT_SEARCH_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    normalized_query = normalize_player_name(query)
    safe_limit = _clamp_limit(limit)
    table_id = _table_id(project_id, dataset_id, "compat_player_profiles_current")
    sql = f"""
    SELECT
        {PROFILE_SELECT_LIST}
    FROM `{table_id}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND (@position IS NULL OR position = @position)
        AND (@team IS NULL OR current_team = @team)
        AND (
            LOWER(display_name) LIKE CONCAT('%', LOWER(@query), '%')
            OR LOWER(full_name) LIKE CONCAT('%', LOWER(@query), '%')
            OR normalized_name LIKE CONCAT('%', @normalized_query, '%')
            OR player_id_internal = @query
            OR source_player_key = @query
        )
    ORDER BY
        CASE WHEN normalized_name = @normalized_query THEN 0 ELSE 1 END,
        pigskin_rank_position ASC,
        fantasy_points_per_game_current_season DESC,
        display_name ASC
    LIMIT @limit
    """
    return sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("position", "STRING", position),
        ("team", "STRING", team),
        ("query", "STRING", str(query).strip()),
        ("normalized_query", "STRING", normalized_query or None),
        ("limit", "INT64", safe_limit),
    ])


def build_player_profiles_list_query(
    *,
    project_id: str,
    dataset_id: str,
    position: str | None = None,
    team: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    limit: int = DEFAULT_LIST_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    table_id = _table_id(project_id, dataset_id, "compat_player_profiles_current")
    safe_limit = _clamp_list_limit(limit)
    sql = f"""
    SELECT
        {PROFILE_SELECT_LIST}
    FROM `{table_id}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND (@position IS NULL OR position = @position)
        AND (@team IS NULL OR current_team = @team)
    ORDER BY
        position,
        pigskin_rank_position ASC,
        fantasy_points_per_game_current_season DESC,
        display_name ASC
    LIMIT @limit
    """
    return sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("position", "STRING", position),
        ("team", "STRING", team),
        ("limit", "INT64", safe_limit),
    ])


PROFILE_SELECT_LIST = """
        player_id_internal,
        source_player_key,
        sleeper_player_id,
        gsis_id,
        pfr_id,
        espn_id,
        yahoo_id,
        display_name,
        full_name,
        normalized_name,
        position,
        fantasy_positions,
        current_team,
        active_status,
        rookie_year,
        birth_date,
        age,
        as_of_season,
        as_of_week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        last_seen_season,
        last_seen_week,
        games_played_current_season,
        bye_week,
        fantasy_points_current_season,
        fantasy_points_per_game_current_season,
        fantasy_points_last_3,
        fantasy_points_last_5,
        fantasy_points_last_8,
        total_fantasy_points_standard,
        total_fantasy_points_half_ppr,
        total_fantasy_points_ppr,
        position_rank_by_profile,
        overall_rank_by_profile,
        snaps_last_3,
        snap_share_last_3,
        targets_last_3,
        target_share_last_3,
        carries_last_3,
        rush_share_last_3,
        receptions_last_3,
        air_yards_last_3,
        air_yard_share_last_3,
        red_zone_opportunities_last_3,
        high_value_touches_last_3,
        role_summary_json,
        yards_per_carry_current_season,
        yards_per_target_current_season,
        yards_per_reception_current_season,
        catch_rate_current_season,
        td_rate_current_season,
        epa_summary_json,
        efficiency_summary_json,
        model_run_id,
        ranking_version,
        pigskin_rank_overall,
        pigskin_rank_position,
        pigskin_tier,
        pigskin_projection,
        pigskin_confidence,
        pigskin_summary,
        pigskin_movement_json,
        contract_summary_json,
        depth_chart_summary_json,
        college_summary_json,
        rookie_scouting_summary_json,
        prospect_summary_json,
        source_freshness_json,
        missing_data_flags,
        created_at,
        refreshed_at
"""


def _job_config(params: list[tuple[str, str, Any]]) -> bigquery.QueryJobConfig:
    return bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=[
            bigquery.ScalarQueryParameter(name, type_name, value)
            for name, type_name, value in params
        ]
    )


def _clamp_limit(value: int | str | None) -> int:
    try:
        parsed = int(value) if value is not None else DEFAULT_SEARCH_LIMIT
    except (TypeError, ValueError):
        parsed = DEFAULT_SEARCH_LIMIT
    return max(1, min(MAX_SEARCH_LIMIT, parsed))


def _clamp_list_limit(value: int | str | None) -> int:
    try:
        parsed = int(value) if value is not None else DEFAULT_LIST_LIMIT
    except (TypeError, ValueError):
        parsed = DEFAULT_LIST_LIMIT
    return max(1, min(MAX_LIST_LIMIT, parsed))


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    if not IDENTIFIER_RE.match(table_name):
        raise ValueError(f"Unsafe BigQuery table name: {table_name}")
    return f"{project_id}.{dataset_id}.{table_name}"
