"""Parameterized context tools for Pigskin chat."""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Callable

from google.cloud import bigquery

from src.llm_context_packets import (
    DEFAULT_LEAGUE_TYPE,
    DEFAULT_ROSTER_FORMAT,
    DEFAULT_SCORING_PROFILE,
    get_bigquery_dataset,
    get_player_context_packet as load_player_context_packet,
    search_player_context_packets,
)
from src.load import get_bigquery_client
from src.trade_history import get_trade_player_history as load_trade_player_history


logger = logging.getLogger(__name__)

DEFAULT_MAX_BYTES_BILLED = int(
    os.environ.get("PIGSKIN_CONTEXT_MAX_BYTES_BILLED", "1000000000")
)
MAX_SEARCH_LIMIT = 25
MAX_RANKINGS_LIMIT = 100
MAX_FRAUD_LIMIT = 50
MAX_HISTORY_LIMIT = 64
MAX_COMPARE_PLAYERS = 6
MAX_LEADS_LIMIT = 25

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")


def get_pigskin_context_tool_declarations() -> list[dict[str, Any]]:
    """Return the only model-visible Pigskin context tools."""

    return [
        {
            "name": "get_player_context_packet",
            "description": (
                "Load one curated Pigskin player context packet with ranking, role, "
                "recent evidence, source freshness, and missing-data flags."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "player_name": {"type": "string"},
                    "player_id_internal": {"type": "string"},
                    "scoring_profile_id": {"type": "string"},
                    "league_type_id": {"type": "string"},
                    "roster_format_id": {"type": "string"},
                    "model_run_id": {"type": "string"},
                },
            },
        },
        {
            "name": "search_players",
            "description": "Resolve player names or IDs against curated Pigskin context packets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "position": {"type": "string"},
                    "team": {"type": "string"},
                    "scoring_profile_id": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "required": ["query"],
            },
        },
        {
            "name": "get_rankings_slice",
            "description": "Load Pigskin-owned active rankings for a position, season, phase, or format.",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {"type": "string"},
                    "season": {"type": "integer"},
                    "ranking_phase": {"type": "string"},
                    "format": {"type": "string"},
                    "limit": {"type": "integer"},
                },
            },
        },
        {
            "name": "get_fraud_watch_candidates",
            "description": "Load curated Fraud Watch candidates ranked by box-score spike risk.",
            "parameters": {
                "type": "object",
                "properties": {
                    "season": {"type": "integer"},
                    "week": {"type": "integer"},
                    "position": {"type": "string"},
                    "player_name": {"type": "string"},
                    "limit": {"type": "integer"},
                },
            },
        },
        {
            "name": "get_trade_player_history",
            "description": "Load capped curated player-week trade history from the compatibility view.",
            "parameters": {
                "type": "object",
                "properties": {
                    "player_name": {"type": "string"},
                    "player_id_internal": {"type": "string"},
                    "scoring_profile_id": {"type": "string"},
                    "seasons_back": {"type": "integer"},
                    "limit": {"type": "integer"},
                },
            },
        },
        {
            "name": "compare_players",
            "description": "Compare up to six players using curated Pigskin context packets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "player_names": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "scoring_profile_id": {"type": "string"},
                    "league_type_id": {"type": "string"},
                    "roster_format_id": {"type": "string"},
                },
                "required": ["player_names"],
            },
        },
        {
            "name": "get_context_event_leads",
            "description": (
                "Load curated context events and stored external leads for injuries, "
                "team changes, usage changes, coaching context, and verification checks."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "player_name": {"type": "string"},
                    "team": {"type": "string"},
                    "event_type": {"type": "string"},
                    "season": {"type": "integer"},
                    "limit": {"type": "integer"},
                },
            },
        },
    ]


def execute_pigskin_context_tool(
    tool_name: str,
    args: dict[str, Any] | None,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    """Execute one model-visible context tool with logging and safe defaults."""

    args = dict(args or {})
    handlers: dict[str, Callable[..., dict[str, Any]]] = {
        "get_player_context_packet": get_player_context_packet_tool,
        "search_players": search_players_tool,
        "get_rankings_slice": get_rankings_slice_tool,
        "get_fraud_watch_candidates": get_fraud_watch_candidates_tool,
        "get_trade_player_history": get_trade_player_history_tool,
        "compare_players": compare_players_tool,
        "get_context_event_leads": get_context_event_leads_tool,
    }
    if tool_name not in handlers:
        raise ValueError(f"Unknown Pigskin context tool: {tool_name}")

    logger.info(
        "pigskin_context_tool_called",
        extra={
            "tool_name": tool_name,
            "args": _loggable_args(args),
            "dataset_id": dataset_id or get_bigquery_dataset(),
        },
    )
    try:
        result = handlers[tool_name](client=client, dataset_id=dataset_id, **args)
    except Exception:
        logger.exception(
            "pigskin_context_tool_failed",
            extra={
                "tool_name": tool_name,
                "args": _loggable_args(args),
                "dataset_id": dataset_id or get_bigquery_dataset(),
            },
        )
        raise
    return _json_safe(
        {
            "tool_name": tool_name,
            "status": "ok",
            "result": result,
        }
    )


def get_player_context_packet_tool(
    *,
    player_id_internal: str | None = None,
    player_name: str | None = None,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    model_run_id: str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    packet = load_player_context_packet(
        player_id_internal=_clean_optional(player_id_internal),
        player_name=_clean_optional(player_name),
        scoring_profile_id=_clean_optional(scoring_profile_id) or DEFAULT_SCORING_PROFILE,
        league_type_id=_clean_optional(league_type_id) or DEFAULT_LEAGUE_TYPE,
        roster_format_id=_clean_optional(roster_format_id) or DEFAULT_ROSTER_FORMAT,
        model_run_id=_clean_optional(model_run_id),
        client=client,
        dataset_id=dataset_id,
    )
    if packet.get("found"):
        return packet

    candidates: list[dict[str, Any]] = []
    if player_name:
        candidates = search_players_tool(
            query=player_name,
            scoring_profile_id=scoring_profile_id,
            limit=5,
            client=client,
            dataset_id=dataset_id,
        )["players"]
    packet["candidate_matches"] = candidates
    return packet


def search_players_tool(
    *,
    query: str,
    position: str | None = None,
    team: str | None = None,
    scoring_profile_id: str | None = None,
    limit: int | str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    safe_limit = _clamp_limit(limit, 1, MAX_SEARCH_LIMIT, 10)
    packets = search_player_context_packets(
        str(query or "").strip(),
        position=_clean_optional(position),
        team=_clean_optional(team),
        scoring_profile_id=_clean_optional(scoring_profile_id) or DEFAULT_SCORING_PROFILE,
        limit=safe_limit,
        client=client,
        dataset_id=dataset_id,
    )
    players = [
        {
            "player_id_internal": packet.get("player_id_internal"),
            "source_player_key": packet.get("source_player_key"),
            "display_name": packet.get("display_name"),
            "position": packet.get("position"),
            "team": packet.get("team"),
            "model_run_id": packet.get("model_run_id"),
            "ranking_version": packet.get("ranking_version"),
            "as_of_season": packet.get("as_of_season"),
            "as_of_week": packet.get("as_of_week"),
            "missing_data_flags": packet.get("missing_data_flags"),
        }
        for packet in packets
    ]
    return {"players": players, "row_count": len(players), "limit": safe_limit}


def get_rankings_slice_tool(
    *,
    position: str | None = None,
    season: int | str | None = None,
    ranking_phase: str | None = None,
    format: str | None = None,
    limit: int | str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    safe_limit = _clamp_limit(limit, 1, MAX_RANKINGS_LIMIT, 50)
    query_client = _client(client)
    dataset = _dataset(dataset_id)
    sql = f"""
    SELECT
        model_run_id,
        ranking_version,
        generated_at,
        adjudicated_at,
        season,
        ranking_phase,
        format,
        position,
        `rank` AS pigskin_rank,
        tier,
        player_id,
        player_name,
        current_team,
        roster_status,
        sleeper_player_id,
        sleeper_team,
        sleeper_active,
        sleeper_status,
        ranking_eligibility,
        rank_source,
        confidence_score,
        avg_ppr,
        avg_opportunity,
        avg_efficiency,
        avg_total_epa,
        avg_passing_epa,
        avg_rushing_epa,
        avg_receiving_epa,
        avg_wopr,
        latest_season_wopr,
        previous_season_wopr,
        pigskin_verdict,
        rank_rationale,
        risk_flags,
        what_would_change_mind,
        data_snapshot_label
    FROM `{_table_id(query_client.project, dataset, "analytics_pigskin_rankings")}`
    WHERE is_active = TRUE
        AND (@position IS NULL OR position = @position)
        AND (@season IS NULL OR season = @season)
        AND (@ranking_phase IS NULL OR ranking_phase = @ranking_phase)
        AND (@format IS NULL OR format = @format)
    ORDER BY position, `rank`
    LIMIT @limit
    """
    rows = _query_records(
        sql,
        [
            ("position", "STRING", _clean_optional(position)),
            ("season", "INT64", _clean_int_optional(season)),
            ("ranking_phase", "STRING", _clean_optional(ranking_phase)),
            ("format", "STRING", _clean_optional(format)),
            ("limit", "INT64", safe_limit),
        ],
        client=query_client,
        query_name="get_rankings_slice",
    )
    return {"rankings": rows, "row_count": len(rows), "limit": safe_limit}


def get_fraud_watch_candidates_tool(
    *,
    season: int | str | None = None,
    week: int | str | None = None,
    position: str | None = None,
    player_name: str | None = None,
    limit: int | str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    safe_limit = _clamp_limit(limit, 1, MAX_FRAUD_LIMIT, 25)
    query_client = _client(client)
    dataset = _dataset(dataset_id)
    sql = f"""
    SELECT
        season,
        week,
        player_name,
        position,
        team,
        current_team,
        fantasy_points_ppr,
        skill_player_opportunities,
        target_share,
        wopr,
        offense_pct,
        touchdowns,
        touchdown_dependency_rate,
        role_quality_score,
        points_over_role_score,
        role_fragility_score,
        fraud_score,
        fraud_label,
        fraud_case,
        what_would_change_mind
    FROM `{_table_id(query_client.project, dataset, "analytics_fraud_watch")}`
    WHERE (@season IS NULL OR season = @season)
        AND (@week IS NULL OR week = @week)
        AND (@position IS NULL OR position = @position)
        AND (
            @player_name IS NULL
            OR LOWER(player_name) LIKE CONCAT('%', LOWER(@player_name), '%')
        )
    ORDER BY season DESC, week DESC, fraud_score DESC
    LIMIT @limit
    """
    rows = _query_records(
        sql,
        [
            ("season", "INT64", _clean_int_optional(season)),
            ("week", "INT64", _clean_int_optional(week)),
            ("position", "STRING", _clean_optional(position)),
            ("player_name", "STRING", _clean_optional(player_name)),
            ("limit", "INT64", safe_limit),
        ],
        client=query_client,
        query_name="get_fraud_watch_candidates",
    )
    return {"candidates": rows, "row_count": len(rows), "limit": safe_limit}


def get_trade_player_history_tool(
    *,
    player_id_internal: str | None = None,
    player_name: str | None = None,
    scoring_profile_id: str | None = None,
    seasons_back: int | str | None = None,
    limit: int | str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    safe_limit = _clamp_limit(limit, 1, MAX_HISTORY_LIMIT, 24)
    df = load_trade_player_history(
        player_id_internal=_clean_optional(player_id_internal),
        player_name=_clean_optional(player_name),
        scoring_profile_id=_clean_optional(scoring_profile_id) or DEFAULT_SCORING_PROFILE,
        seasons_back=_clamp_limit(seasons_back, 0, 10, 2),
        limit=safe_limit,
        client=client,
        dataset_id=dataset_id,
    )
    records = _dataframe_records(df)
    return {"history": records, "row_count": len(records), "limit": safe_limit}


def compare_players_tool(
    *,
    player_names: list[str],
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    cleaned_names = [
        name.strip() for name in (player_names or []) if str(name or "").strip()
    ][:MAX_COMPARE_PLAYERS]
    if not cleaned_names:
        raise ValueError("player_names must include at least one player")

    comparisons = []
    for player_name in cleaned_names:
        packet = get_player_context_packet_tool(
            player_name=player_name,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            client=client,
            dataset_id=dataset_id,
        )
        comparisons.append(_comparison_row(packet))
    return {"players": comparisons, "row_count": len(comparisons)}


def get_context_event_leads_tool(
    *,
    player_name: str | None = None,
    team: str | None = None,
    event_type: str | None = None,
    season: int | str | None = None,
    limit: int | str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    safe_limit = _clamp_limit(limit, 1, MAX_LEADS_LIMIT, 10)
    context_rows = _query_context_events(
        player_name=player_name,
        team=team,
        event_type=event_type,
        season=season,
        limit=safe_limit,
        client=client,
        dataset_id=dataset_id,
    )
    external_rows = _query_external_leads(
        player_name=player_name,
        team=team,
        season=season,
        limit=safe_limit,
        client=client,
        dataset_id=dataset_id,
    )
    return {
        "context_events": context_rows,
        "external_leads": external_rows,
        "external_lead_policy": "stored search leads are not verified truth unless the linked source supports the claim",
        "row_count": len(context_rows) + len(external_rows),
        "limit_per_source": safe_limit,
    }


def _query_context_events(
    *,
    player_name: str | None,
    team: str | None,
    event_type: str | None,
    season: int | str | None,
    limit: int,
    client: Any | None,
    dataset_id: str | None,
) -> list[dict[str, Any]]:
    query_client = _client(client)
    dataset = _dataset(dataset_id)
    sql = f"""
    SELECT
        event_id,
        season,
        start_week,
        end_week,
        team,
        event_type,
        subject_player_id,
        subject_name,
        subject_position,
        affected_player_id,
        affected_player_name,
        affected_unit,
        causal_status,
        confidence_score,
        source_type,
        source_label,
        source_url,
        summary,
        analysis_instruction,
        active
    FROM `{_table_id(query_client.project, dataset, "analytics_context_events")}`
    WHERE active = TRUE
        AND (@season IS NULL OR season = @season)
        AND (@team IS NULL OR team = @team)
        AND (@event_type IS NULL OR event_type = @event_type)
        AND (
            @player_name IS NULL
            OR LOWER(subject_name) LIKE CONCAT('%', LOWER(@player_name), '%')
            OR LOWER(affected_player_name) LIKE CONCAT('%', LOWER(@player_name), '%')
        )
    ORDER BY season DESC, start_week DESC, event_type
    LIMIT @limit
    """
    return _query_records(
        sql,
        [
            ("season", "INT64", _clean_int_optional(season)),
            ("team", "STRING", _clean_optional(team)),
            ("event_type", "STRING", _clean_optional(event_type)),
            ("player_name", "STRING", _clean_optional(player_name)),
            ("limit", "INT64", limit),
        ],
        client=query_client,
        query_name="get_context_events",
    )


def _query_external_leads(
    *,
    player_name: str | None,
    team: str | None,
    season: int | str | None,
    limit: int,
    client: Any | None,
    dataset_id: str | None,
) -> list[dict[str, Any]]:
    query_client = _client(client)
    dataset = _dataset(dataset_id)
    sql = f"""
    SELECT
        searched_at,
        player_name,
        query,
        result_rank,
        title,
        link,
        display_link,
        snippet,
        source_type,
        provider,
        source_name
    FROM `{_table_id(query_client.project, dataset, "analytics_external_context_search_results")}`
    WHERE (@player_name IS NULL OR LOWER(player_name) LIKE CONCAT('%', LOWER(@player_name), '%') OR LOWER(query) LIKE CONCAT('%', LOWER(@player_name), '%'))
        AND (@team IS NULL OR LOWER(query) LIKE CONCAT('%', LOWER(@team), '%'))
        AND (@season IS NULL OR query LIKE CONCAT('%', CAST(@season AS STRING), '%'))
    ORDER BY searched_at DESC, result_rank ASC
    LIMIT @limit
    """
    return _query_records(
        sql,
        [
            ("player_name", "STRING", _clean_optional(player_name)),
            ("team", "STRING", _clean_optional(team)),
            ("season", "INT64", _clean_int_optional(season)),
            ("limit", "INT64", limit),
        ],
        client=query_client,
        query_name="get_external_context_leads",
    )


def _query_records(
    sql: str,
    params: list[tuple[str, str, Any]],
    *,
    client: Any | None,
    query_name: str,
) -> list[dict[str, Any]]:
    query_client = _client(client)
    job_config = bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=[
            bigquery.ScalarQueryParameter(name, type_name, value)
            for name, type_name, value in params
        ],
    )
    rows = query_client.query(sql, job_config=job_config).result()
    records = [_json_safe(dict(row)) for row in rows]
    logger.info(
        "pigskin_context_query_complete",
        extra={"query_name": query_name, "row_count": len(records)},
    )
    return records


def _comparison_row(packet: dict[str, Any]) -> dict[str, Any]:
    packet_json = packet.get("packet_json") or {}
    ranking = packet_json.get("ranking_context") or {}
    usage = packet_json.get("usage_summary") or {}
    efficiency = packet_json.get("efficiency_summary") or {}
    return {
        "found": packet.get("found", False),
        "display_name": packet.get("display_name"),
        "position": packet.get("position"),
        "team": packet.get("team"),
        "model_run_id": packet.get("model_run_id"),
        "ranking_version": packet.get("ranking_version"),
        "pigskin_rank_position": ranking.get("pigskin_rank_position"),
        "pigskin_tier": ranking.get("pigskin_tier"),
        "rank_rationale": ranking.get("rank_rationale"),
        "risk_flags": ranking.get("risk_flags"),
        "usage_summary": usage,
        "efficiency_summary": efficiency,
        "missing_data_flags": packet.get("missing_data_flags", []),
    }


def _dataframe_records(df: Any) -> list[dict[str, Any]]:
    if df is None:
        return []
    records = df.to_dict(orient="records")
    return [_json_safe(record) for record in records]


def _client(client: Any | None) -> Any:
    return client or get_bigquery_client()


def _dataset(dataset_id: str | None) -> str:
    dataset = dataset_id or get_bigquery_dataset()
    if not IDENTIFIER_RE.match(dataset):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset}")
    return dataset


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    if not IDENTIFIER_RE.match(table_name):
        raise ValueError(f"Unsafe BigQuery table name: {table_name}")
    return f"{project_id}.{dataset_id}.{table_name}"


def _clamp_limit(value: int | str | None, minimum: int, maximum: int, default: int) -> int:
    try:
        parsed = int(value) if value is not None else default
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


def _clean_int_optional(value: int | str | None) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _clean_optional(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, "item"):
        try:
            return _json_safe(value.item())
        except (TypeError, ValueError):
            pass
    try:
        if value != value:
            return None
    except TypeError:
        return None
    return value


def _loggable_args(args: dict[str, Any]) -> str:
    return json.dumps(_json_safe(args), sort_keys=True)[:2000]
