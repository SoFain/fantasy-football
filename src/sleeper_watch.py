"""Safe access helpers for Sleeper Watch candidates."""

from __future__ import annotations

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
MAX_LIMIT = 250
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("SLEEPER_WATCH_MAX_BYTES_BILLED", "1000000000"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def get_sleeper_watch_candidates(
    *,
    league_id: str | None = None,
    position: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int | str | None = DEFAULT_LIMIT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return Sleeper Watch candidates from the compatibility view."""
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_sleeper_watch_candidates_query(
        project_id=client.project,
        dataset_id=dataset_id,
        league_id=league_id,
        position=position,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=limit,
    )
    return _query_rows(client, sql, job_config)


def get_streamer_candidates(
    *,
    league_id: str | None = None,
    position: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    limit: int | str | None = 25,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return waiver or streamer candidates with usable candidate scores."""
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_sleeper_watch_candidates_query(
        project_id=client.project,
        dataset_id=dataset_id,
        league_id=league_id,
        position=position,
        scoring_profile_id=scoring_profile_id,
        limit=limit,
        score_mode="streamer",
    )
    return _query_rows(client, sql, job_config)


def get_breakout_candidates_for_sleeper_watch(
    *,
    league_id: str | None = None,
    position: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    limit: int | str | None = 25,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return candidates ranked by breakout score for Sleeper Watch."""
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_sleeper_watch_candidates_query(
        project_id=client.project,
        dataset_id=dataset_id,
        league_id=league_id,
        position=position,
        scoring_profile_id=scoring_profile_id,
        limit=limit,
        score_mode="breakout",
    )
    return _query_rows(client, sql, job_config)


def build_sleeper_watch_candidates_query(
    *,
    project_id: str,
    dataset_id: str,
    league_id: str | None = None,
    position: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int | str | None = DEFAULT_LIMIT,
    score_mode: str = "watch",
) -> tuple[str, bigquery.QueryJobConfig]:
    order_field = _score_order_field(score_mode)
    extra_filter = ""
    if score_mode == "streamer":
        extra_filter = "AND streamer_score IS NOT NULL AND COALESCE(waiver_candidate_flag, TRUE)"
    elif score_mode == "breakout":
        extra_filter = "AND breakout_score IS NOT NULL"

    sql = f"""
    SELECT {SLEEPER_WATCH_SELECT_LIST}
    FROM `{_table_id(project_id, dataset_id, "compat_sleeper_watch_candidates")}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
        AND (@position IS NULL OR position = @position)
        AND (
            (@league_id IS NULL AND league_id IS NULL)
            OR (@league_id IS NOT NULL AND (league_id = @league_id OR league_id IS NULL))
        )
        {extra_filter}
    QUALIFY ROW_NUMBER() OVER(
        PARTITION BY player_id_internal, scoring_profile_id
        ORDER BY IF(@league_id IS NOT NULL AND league_id = @league_id, 0, 1), {order_field} DESC, display_name ASC
    ) = 1
    ORDER BY {order_field} DESC, streamer_score DESC, breakout_score DESC, display_name ASC
    LIMIT @limit
    """
    return sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("position", "STRING", _clean_optional(position)),
        ("league_id", "STRING", _clean_optional(league_id)),
        ("limit", "INT64", _clamp_limit(limit)),
    ])


SLEEPER_WATCH_SELECT_LIST = """
        player_id_internal,
        source_player_key,
        sleeper_player_id,
        display_name,
        normalized_name,
        position,
        fantasy_positions,
        team,
        opponent,
        age,
        active_status,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        league_id,
        model_run_id,
        ranking_version,
        rostered_rate,
        available_in_league_flag,
        rostered_in_league_flag,
        waiver_candidate_flag,
        starter_candidate_flag,
        sleeper_trending_add_count,
        sleeper_trending_drop_count,
        market_or_roster_context_json,
        fantasy_points_last_1,
        fantasy_points_last_3,
        fantasy_points_last_5,
        fantasy_points_per_game,
        snap_share_last_3,
        target_share_last_3,
        rush_share_last_3,
        targets_last_3,
        carries_last_3,
        receptions_last_3,
        air_yards_last_3,
        red_zone_opportunities_last_3,
        high_value_touches_last_3,
        usage_trend_score,
        role_growth_score,
        yards_per_target,
        yards_per_carry,
        yards_per_reception,
        catch_rate,
        td_dependency_score,
        expected_vs_actual_signal,
        fraud_risk_score,
        breakout_score,
        game_id,
        game_environment_json,
        opponent_fantasy_points_allowed_proxy,
        matchup_score,
        streamer_score,
        schedule_context_json,
        pigskin_rank_overall,
        pigskin_rank_position,
        pigskin_tier,
        pigskin_projection,
        pigskin_confidence,
        rank_vs_market_gap,
        pigskin_summary,
        candidate_reason,
        evidence_json,
        counterargument,
        snark_hook,
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


def _score_order_field(score_mode: str) -> str:
    if score_mode == "breakout":
        return "breakout_score"
    return "streamer_score"


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
