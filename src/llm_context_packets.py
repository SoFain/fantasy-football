"""Safe access helpers for LLM player context packets."""

from __future__ import annotations

import json
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
DEFAULT_SEARCH_LIMIT = 10
DEFAULT_RANKED_LIMIT = 50
MAX_LIMIT = 100
PACKET_TEXT_LIMIT = 8000
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


def get_player_context_packet(
    *,
    player_id_internal: str | None = None,
    player_name: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    """Return one normalized packet or a clean missing-packet response."""

    if not player_id_internal and not player_name:
        raise ValueError("player_id_internal or player_name is required")

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_player_context_packet_query(
        project_id=client.project,
        dataset_id=dataset_id,
        player_id_internal=player_id_internal,
        player_name=player_name,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        model_run_id=model_run_id,
    )
    try:
        rows = list(client.query(sql, job_config=job_config).result())
    except Exception as exc:
        raise RuntimeError(f"Failed to load LLM player context packet: {exc}") from exc
    if not rows:
        return missing_packet_response(player_id_internal=player_id_internal, player_name=player_name)
    return normalize_packet_for_llm(rows[0])


def search_player_context_packets(
    query: str,
    *,
    position: str | None = None,
    team: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    limit: int = DEFAULT_SEARCH_LIMIT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Search packet rows by player name or ID."""

    if not str(query or "").strip():
        return []

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_search_context_packets_query(
        project_id=client.project,
        dataset_id=dataset_id,
        query=query,
        position=position,
        team=team,
        scoring_profile_id=scoring_profile_id,
        limit=limit,
    )
    rows = client.query(sql, job_config=job_config).result()
    return [normalize_packet_for_llm(row) for row in rows]


def get_ranked_context_packets(
    *,
    position: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int = DEFAULT_RANKED_LIMIT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return ranked packet rows for a board or batch prompt."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_ranked_context_packets_query(
        project_id=client.project,
        dataset_id=dataset_id,
        position=position,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=limit,
    )
    rows = client.query(sql, job_config=job_config).result()
    return [normalize_packet_for_llm(row) for row in rows]


def normalize_packet_for_llm(packet_row: Any) -> dict[str, Any]:
    """Convert a BigQuery packet row into a stable prompt-ready shape."""

    row = dict(packet_row)
    packet_json = _parse_json(row.get("packet_json")) or {}
    missing_flags = _parse_json(row.get("missing_data_flags")) or []
    source_freshness = _parse_json(row.get("source_freshness_json")) or {}
    packet_text = str(row.get("packet_text") or "")[:PACKET_TEXT_LIMIT]
    return {
        "found": True,
        "packet_id": row.get("packet_id"),
        "model_run_id": row.get("model_run_id"),
        "ranking_version": row.get("ranking_version"),
        "player_id_internal": row.get("player_id_internal"),
        "source_player_key": row.get("source_player_key"),
        "display_name": row.get("display_name"),
        "position": row.get("position"),
        "team": row.get("team"),
        "scoring_profile_id": row.get("scoring_profile_id"),
        "league_type_id": row.get("league_type_id"),
        "roster_format_id": row.get("roster_format_id"),
        "as_of_season": row.get("as_of_season"),
        "as_of_week": row.get("as_of_week"),
        "packet_json": _with_required_packet_keys(packet_json),
        "packet_text": packet_text,
        "token_estimate": row.get("token_estimate") or _estimate_tokens(packet_text),
        "source_freshness": source_freshness,
        "missing_data_flags": missing_flags,
    }


def missing_packet_response(player_id_internal: str | None = None, player_name: str | None = None) -> dict[str, Any]:
    lookup = player_id_internal or player_name or "unknown"
    return {
        "found": False,
        "packet_id": None,
        "player_id_internal": player_id_internal,
        "display_name": player_name,
        "packet_json": _with_required_packet_keys({}),
        "packet_text": f"No LLM player context packet found for {lookup}. Run the packet materializer or check identity mapping.",
        "token_estimate": 0,
        "source_freshness": {},
        "missing_data_flags": ["packet_not_found"],
    }


def build_player_context_packet_query(
    *,
    project_id: str,
    dataset_id: str,
    player_id_internal: str | None = None,
    player_name: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
) -> tuple[str, bigquery.QueryJobConfig]:
    normalized_name = normalize_player_name(player_name)
    table_id = _table_id(project_id, dataset_id, "llm_player_context_packet")
    sql = f"""
    SELECT {PACKET_SELECT_LIST}
    FROM `{table_id}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
        AND (@model_run_id IS NULL OR model_run_id = @model_run_id)
        AND (
            (@player_id_internal IS NOT NULL AND player_id_internal = @player_id_internal)
            OR (@player_id_internal IS NOT NULL AND source_player_key = @player_id_internal)
            OR (@player_name IS NOT NULL AND LOWER(display_name) = LOWER(@player_name))
            OR (@normalized_name IS NOT NULL AND REGEXP_REPLACE(REGEXP_REPLACE(LOWER(display_name), r'\\s+(jr|sr|ii|iii|iv|v)\\.?$', ''), r'[^a-z0-9]+', '') = @normalized_name)
        )
    ORDER BY as_of_season DESC, as_of_week DESC, model_run_id DESC
    LIMIT 1
    """
    return sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("model_run_id", "STRING", model_run_id),
        ("player_id_internal", "STRING", player_id_internal),
        ("player_name", "STRING", player_name),
        ("normalized_name", "STRING", normalized_name or None),
    ])


def build_search_context_packets_query(
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
    table_id = _table_id(project_id, dataset_id, "llm_player_context_packet")
    sql = f"""
    SELECT {PACKET_SELECT_LIST}
    FROM `{table_id}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND (@position IS NULL OR position = @position)
        AND (@team IS NULL OR team = @team)
        AND (
            LOWER(display_name) LIKE CONCAT('%', LOWER(@query), '%')
            OR source_player_key = @query
            OR player_id_internal = @query
            OR REGEXP_REPLACE(REGEXP_REPLACE(LOWER(display_name), r'\\s+(jr|sr|ii|iii|iv|v)\\.?$', ''), r'[^a-z0-9]+', '') LIKE CONCAT('%', @normalized_query, '%')
        )
    ORDER BY as_of_season DESC, as_of_week DESC, token_estimate DESC, display_name ASC
    LIMIT @limit
    """
    return sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("position", "STRING", position),
        ("team", "STRING", team),
        ("query", "STRING", str(query).strip()),
        ("normalized_query", "STRING", normalized_query or None),
        ("limit", "INT64", _clamp_limit(limit)),
    ])


def build_ranked_context_packets_query(
    *,
    project_id: str,
    dataset_id: str,
    position: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int = DEFAULT_RANKED_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    table_id = _table_id(project_id, dataset_id, "llm_player_context_packet")
    sql = f"""
    SELECT {PACKET_SELECT_LIST}
    FROM `{table_id}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
        AND (@position IS NULL OR position = @position)
    ORDER BY
        JSON_VALUE(packet_json, '$.ranking_context.pigskin_rank_position') IS NULL,
        SAFE_CAST(JSON_VALUE(packet_json, '$.ranking_context.pigskin_rank_position') AS INT64),
        display_name ASC
    LIMIT @limit
    """
    return sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("position", "STRING", position),
        ("limit", "INT64", _clamp_limit(limit)),
    ])


PACKET_SELECT_LIST = """
        packet_id,
        model_run_id,
        ranking_version,
        player_id_internal,
        source_player_key,
        display_name,
        position,
        team,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        as_of_season,
        as_of_week,
        packet_json,
        packet_text,
        token_estimate,
        source_freshness_json,
        missing_data_flags,
        created_at,
        updated_at
"""


REQUIRED_PACKET_KEYS = (
    "identity",
    "ranking_context",
    "recent_fantasy_summary",
    "usage_summary",
    "efficiency_summary",
    "game_environment",
    "qb_and_team_context",
    "fraud_watch_context",
    "trade_context",
    "external_context",
    "counterarguments",
    "snark_hooks",
    "source_metadata",
)


def _with_required_packet_keys(packet_json: dict[str, Any]) -> dict[str, Any]:
    packet = dict(packet_json)
    for key in REQUIRED_PACKET_KEYS:
        if key not in packet:
            packet[key] = [] if key == "snark_hooks" else {}
    return packet


def _parse_json(value: Any) -> Any:
    if value in (None, ""):
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return None


def _estimate_tokens(text: str) -> int:
    return int((len(text) + 3) / 4)


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
    return max(1, min(MAX_LIMIT, parsed))


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    if not IDENTIFIER_RE.match(table_name):
        raise ValueError(f"Unsafe BigQuery table name: {table_name}")
    return f"{project_id}.{dataset_id}.{table_name}"
