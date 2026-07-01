"""Bounded read-only lookup for current roster context."""

from __future__ import annotations

import os
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from google.cloud import bigquery

from src.llm_context_packets import get_bigquery_dataset
from src.load import get_bigquery_client
from src.pigskin_current_roster_merge import (
    CURRENT_ROSTER_SOURCE_POLICY,
    merge_historical_packet_with_current_roster,
)


DEFAULT_MAX_BYTES_BILLED = int(
    os.environ.get("PIGSKIN_CURRENT_ROSTER_LOOKUP_MAX_BYTES_BILLED", "1000000000")
)
DEFAULT_LIMIT = 5
MAX_LIMIT = 25
SOURCE_POLICY = CURRENT_ROSTER_SOURCE_POLICY
LOOKUP_POLICY = (
    "Current roster/free-agent/current-team status must come from approved "
    "current roster or identity sources, never historical packet team."
)
APPROVED_SOURCES = (
    "player_identity_bridge",
    "dim_players_current",
    "sleeper_players_current",
    "sleeper_roster_players",
    "sleeper_available_players",
)
UNSAFE_INPUT_KEYS = {"sql", "query", "sql_query", "raw_sql"}
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")
STABLE_ID_FIELDS = ("player_id_internal", "sleeper_player_id", "gsis_id")


def lookup_current_roster_context(
    *,
    player_id_internal: str | None = None,
    sleeper_player_id: str | None = None,
    gsis_id: str | None = None,
    player_name: str | None = None,
    team: str | None = None,
    position: str | None = None,
    league_id: str | None = None,
    include_available_players: bool = False,
    limit: int | str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
    **extra_args: Any,
) -> dict[str, Any]:
    """Return one current roster payload or ambiguity candidates."""

    validation_error = _validate_lookup_request(
        player_id_internal=player_id_internal,
        sleeper_player_id=sleeper_player_id,
        gsis_id=gsis_id,
        player_name=player_name,
        limit=limit,
        extra_args=extra_args,
    )
    if validation_error:
        return validation_error

    query_client = client or get_bigquery_client()
    dataset = dataset_id or get_bigquery_dataset()
    safe_limit = _clamp_limit(limit)
    sql, job_config = build_current_roster_lookup_query(
        project_id=query_client.project,
        dataset_id=dataset,
        player_id_internal=_clean_optional(player_id_internal),
        sleeper_player_id=_clean_optional(sleeper_player_id),
        gsis_id=_clean_optional(gsis_id),
        player_name=_clean_optional(player_name),
        team=_clean_optional(team),
        position=_clean_optional(position),
        league_id=_clean_optional(league_id),
        include_available_players=include_available_players,
        limit=safe_limit,
    )

    try:
        result = query_client.query(sql, job_config=job_config).result()
        candidate_rows = [_row_to_dict(row) for row in result]
    except Exception as exc:
        return {
            "status": "query_error",
            "found": False,
            "source": "pigskin_current_roster_lookup",
            "source_policy": SOURCE_POLICY,
            "warnings": [LOOKUP_POLICY],
            "error": f"Failed to retrieve current roster context: {exc}",
            "request": _request_summary(
                player_id_internal=player_id_internal,
                sleeper_player_id=sleeper_player_id,
                gsis_id=gsis_id,
                player_name=player_name,
                team=team,
                position=position,
                league_id=league_id,
                include_available_players=include_available_players,
                limit=safe_limit,
            ),
        }

    return _response_from_candidate_rows(
        candidate_rows,
        request=_request_summary(
            player_id_internal=player_id_internal,
            sleeper_player_id=sleeper_player_id,
            gsis_id=gsis_id,
            player_name=player_name,
            team=team,
            position=position,
            league_id=league_id,
            include_available_players=include_available_players,
            limit=safe_limit,
        ),
    )


def merge_historical_packet_with_current_lookup(
    historical_result: dict[str, Any] | None,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    **lookup_args: Any,
) -> dict[str, Any]:
    """Lookup current roster state, then pass it to the pure merge layer."""

    current_result = lookup_current_roster_context(
        client=client,
        dataset_id=dataset_id,
        **lookup_args,
    )
    current_payload = current_result.get("current_roster_context")
    merged = merge_historical_packet_with_current_roster(historical_result, current_payload)
    merged["current_roster_lookup"] = current_result
    return merged


def build_current_roster_lookup_query(
    *,
    project_id: str,
    dataset_id: str,
    player_id_internal: str | None = None,
    sleeper_player_id: str | None = None,
    gsis_id: str | None = None,
    player_name: str | None = None,
    team: str | None = None,
    position: str | None = None,
    league_id: str | None = None,
    include_available_players: bool = False,
    limit: int = DEFAULT_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    """Build the only BigQuery query used by the current roster lookup helper."""

    player_identity_bridge = _table_id(project_id, dataset_id, "player_identity_bridge")
    dim_players_current = _table_id(project_id, dataset_id, "dim_players_current")
    sleeper_players_current = _table_id(project_id, dataset_id, "sleeper_players_current")
    sleeper_roster_players = _table_id(project_id, dataset_id, "sleeper_roster_players")
    sleeper_available_players = _table_id(project_id, dataset_id, "sleeper_available_players")

    sql = f"""
    WITH identity_bridge AS (
        SELECT
            'player_identity_bridge' AS source_name,
            10 AS source_priority,
            'identity' AS source_role,
            player_id_internal,
            gsis_id,
            sleeper_player_id,
            full_name,
            display_name,
            normalized_name,
            position,
            current_team,
            active_status AS current_roster_status,
            CAST(NULL AS STRING) AS league_id,
            CAST(NULL AS INT64) AS roster_id,
            source_freshness_json,
            missing_data_flags,
            updated_at AS current_roster_as_of,
            CAST(NULL AS STRING) AS fantasy_availability,
            FALSE AS free_agent
        FROM `{player_identity_bridge}`
    ),
    dim_current AS (
        SELECT
            'dim_players_current' AS source_name,
            20 AS source_priority,
            'identity' AS source_role,
            player_id_internal,
            gsis_id,
            sleeper_player_id,
            full_name,
            display_name,
            normalized_name,
            position,
            current_team,
            active_status AS current_roster_status,
            CAST(NULL AS STRING) AS league_id,
            CAST(NULL AS INT64) AS roster_id,
            source_freshness_json,
            missing_data_flags,
            updated_at AS current_roster_as_of,
            CAST(NULL AS STRING) AS fantasy_availability,
            FALSE AS free_agent
        FROM `{dim_players_current}`
    ),
    sleeper_global AS (
        SELECT
            'sleeper_players_current' AS source_name,
            30 AS source_priority,
            'global_current' AS source_role,
            COALESCE(pib.player_id_internal, dim.player_id_internal) AS player_id_internal,
            sp.gsis_id,
            sp.sleeper_player_id,
            COALESCE(pib.full_name, dim.full_name, sp.player_name) AS full_name,
            COALESCE(pib.display_name, dim.display_name, sp.player_name) AS display_name,
            COALESCE(pib.normalized_name, dim.normalized_name, LOWER(sp.player_name)) AS normalized_name,
            sp.position,
            sp.team AS current_team,
            sp.status AS current_roster_status,
            CAST(NULL AS STRING) AS league_id,
            CAST(NULL AS INT64) AS roster_id,
            TO_JSON_STRING(STRUCT(sp.snapshot_at AS sleeper_players_current_snapshot_at)) AS source_freshness_json,
            TO_JSON_STRING(STRUCT(
                IF(sp.team IS NULL, ['missing_current_team'], []) AS flags
            )) AS missing_data_flags,
            sp.snapshot_at AS current_roster_as_of,
            CAST(NULL AS STRING) AS fantasy_availability,
            IF(LOWER(COALESCE(sp.status, '')) IN ('free_agent', 'available'), TRUE, FALSE) AS free_agent
        FROM `{sleeper_players_current}` sp
        LEFT JOIN `{player_identity_bridge}` pib
            ON (
                (sp.sleeper_player_id IS NOT NULL AND pib.sleeper_player_id = sp.sleeper_player_id)
                OR (sp.gsis_id IS NOT NULL AND pib.gsis_id = sp.gsis_id)
            )
        LEFT JOIN `{dim_players_current}` dim
            ON (
                (sp.sleeper_player_id IS NOT NULL AND dim.sleeper_player_id = sp.sleeper_player_id)
                OR (sp.gsis_id IS NOT NULL AND dim.gsis_id = sp.gsis_id)
            )
        WHERE sp.snapshot_at = (SELECT MAX(snapshot_at) FROM `{sleeper_players_current}`)
    ),
    sleeper_rostered AS (
        SELECT
            'sleeper_roster_players' AS source_name,
            40 AS source_priority,
            'league_rostered' AS source_role,
            COALESCE(pib.player_id_internal, dim.player_id_internal) AS player_id_internal,
            rp.gsis_id,
            rp.sleeper_player_id,
            COALESCE(pib.full_name, dim.full_name, rp.player_name) AS full_name,
            COALESCE(pib.display_name, dim.display_name, rp.player_name) AS display_name,
            COALESCE(pib.normalized_name, dim.normalized_name, LOWER(rp.player_name)) AS normalized_name,
            rp.position,
            rp.team AS current_team,
            rp.status AS current_roster_status,
            rp.league_id,
            rp.roster_id,
            TO_JSON_STRING(STRUCT(rp.snapshot_at AS sleeper_roster_players_snapshot_at)) AS source_freshness_json,
            TO_JSON_STRING(STRUCT(
                IF(rp.team IS NULL, ['missing_current_team'], []) AS flags
            )) AS missing_data_flags,
            rp.snapshot_at AS current_roster_as_of,
            'rostered' AS fantasy_availability,
            FALSE AS free_agent
        FROM `{sleeper_roster_players}` rp
        LEFT JOIN `{player_identity_bridge}` pib
            ON (
                (rp.sleeper_player_id IS NOT NULL AND pib.sleeper_player_id = rp.sleeper_player_id)
                OR (rp.gsis_id IS NOT NULL AND pib.gsis_id = rp.gsis_id)
            )
        LEFT JOIN `{dim_players_current}` dim
            ON (
                (rp.sleeper_player_id IS NOT NULL AND dim.sleeper_player_id = rp.sleeper_player_id)
                OR (rp.gsis_id IS NOT NULL AND dim.gsis_id = rp.gsis_id)
            )
        WHERE @league_id IS NOT NULL
            AND rp.league_id = @league_id
            AND rp.snapshot_at = (
                SELECT MAX(snapshot_at)
                FROM `{sleeper_roster_players}`
                WHERE league_id = @league_id
            )
    ),
    sleeper_available AS (
        SELECT
            'sleeper_available_players' AS source_name,
            50 AS source_priority,
            'league_available' AS source_role,
            COALESCE(pib.player_id_internal, dim.player_id_internal) AS player_id_internal,
            ap.gsis_id,
            ap.sleeper_player_id,
            COALESCE(pib.full_name, dim.full_name, ap.player_name) AS full_name,
            COALESCE(pib.display_name, dim.display_name, ap.player_name) AS display_name,
            COALESCE(pib.normalized_name, dim.normalized_name, LOWER(ap.player_name)) AS normalized_name,
            ap.position,
            ap.team AS current_team,
            COALESCE(ap.status, 'available') AS current_roster_status,
            ap.league_id,
            CAST(NULL AS INT64) AS roster_id,
            TO_JSON_STRING(STRUCT(ap.snapshot_at AS sleeper_available_players_snapshot_at)) AS source_freshness_json,
            TO_JSON_STRING(STRUCT(
                IF(ap.team IS NULL, ['missing_current_team'], []) AS flags
            )) AS missing_data_flags,
            ap.snapshot_at AS current_roster_as_of,
            'available' AS fantasy_availability,
            TRUE AS free_agent
        FROM `{sleeper_available_players}` ap
        LEFT JOIN `{player_identity_bridge}` pib
            ON (
                (ap.sleeper_player_id IS NOT NULL AND pib.sleeper_player_id = ap.sleeper_player_id)
                OR (ap.gsis_id IS NOT NULL AND pib.gsis_id = ap.gsis_id)
            )
        LEFT JOIN `{dim_players_current}` dim
            ON (
                (ap.sleeper_player_id IS NOT NULL AND dim.sleeper_player_id = ap.sleeper_player_id)
                OR (ap.gsis_id IS NOT NULL AND dim.gsis_id = ap.gsis_id)
            )
        WHERE @include_available_players
            AND @league_id IS NOT NULL
            AND ap.league_id = @league_id
            AND ap.snapshot_at = (
                SELECT MAX(snapshot_at)
                FROM `{sleeper_available_players}`
                WHERE league_id = @league_id
            )
    ),
    all_candidates AS (
        SELECT * FROM identity_bridge
        UNION ALL
        SELECT * FROM dim_current
        UNION ALL
        SELECT * FROM sleeper_global
        UNION ALL
        SELECT * FROM sleeper_rostered
        UNION ALL
        SELECT * FROM sleeper_available
    ),
    filtered_candidates AS (
        SELECT *
        FROM all_candidates
        WHERE (
                @player_id_internal IS NULL
                OR player_id_internal = @player_id_internal
            )
            AND (
                @sleeper_player_id IS NULL
                OR sleeper_player_id = @sleeper_player_id
            )
            AND (
                @gsis_id IS NULL
                OR gsis_id = @gsis_id
            )
            AND (
                @normalized_name IS NULL
                OR normalized_name = @normalized_name
                OR LOWER(display_name) = @normalized_name
                OR LOWER(full_name) = @normalized_name
            )
            AND (@team IS NULL OR UPPER(current_team) = UPPER(@team))
            AND (@position IS NULL OR UPPER(position) = UPPER(@position))
    )
    SELECT
        source_name,
        source_priority,
        source_role,
        player_id_internal,
        gsis_id,
        sleeper_player_id,
        full_name,
        display_name,
        normalized_name,
        position,
        current_team,
        current_roster_status,
        league_id,
        roster_id,
        source_freshness_json,
        missing_data_flags,
        current_roster_as_of,
        fantasy_availability,
        free_agent
    FROM filtered_candidates
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY
            source_name,
            COALESCE(player_id_internal, CONCAT('sleeper:', sleeper_player_id), CONCAT('gsis:', gsis_id), CONCAT('name:', normalized_name))
        ORDER BY current_roster_as_of DESC NULLS LAST, display_name ASC
    ) = 1
    ORDER BY
        COALESCE(player_id_internal, sleeper_player_id, gsis_id, normalized_name),
        source_priority ASC,
        current_roster_as_of DESC NULLS LAST
    LIMIT @limit
    """

    return sql, _job_config(
        [
            ("player_id_internal", "STRING", player_id_internal),
            ("sleeper_player_id", "STRING", sleeper_player_id),
            ("gsis_id", "STRING", gsis_id),
            ("normalized_name", "STRING", _normalize_name(player_name)),
            ("team", "STRING", team),
            ("position", "STRING", position),
            ("league_id", "STRING", league_id),
            ("include_available_players", "BOOL", bool(include_available_players)),
            ("limit", "INT64", _clamp_limit(limit)),
        ]
    )


def _response_from_candidate_rows(
    candidate_rows: list[dict[str, Any]],
    *,
    request: dict[str, Any],
) -> dict[str, Any]:
    warnings = [LOOKUP_POLICY]
    if not candidate_rows:
        return {
            "status": "not_found",
            "found": False,
            "source": "pigskin_current_roster_lookup",
            "source_policy": SOURCE_POLICY,
            "warnings": warnings + ["No approved current roster source matched the bounded lookup."],
            "candidates": [],
            "candidate_count": 0,
            "needs_identity_confirmation": False,
            "request": request,
        }

    groups = _candidate_groups(candidate_rows)
    candidates = [_candidate_from_group(group) for group in groups]
    if len(candidates) > 1:
        return {
            "status": "ambiguous",
            "found": False,
            "source": "pigskin_current_roster_lookup",
            "source_policy": SOURCE_POLICY,
            "warnings": warnings
            + ["Current roster lookup matched multiple candidate identities."],
            "candidates": candidates,
            "candidate_count": len(candidates),
            "needs_identity_confirmation": True,
            "request": request,
        }

    context = candidates[0]
    return {
        "status": "ok",
        "found": True,
        "source": "pigskin_current_roster_lookup",
        "source_policy": SOURCE_POLICY,
        "warnings": _dedupe(warnings + context.get("warnings", [])),
        "current_roster_context": context,
        "candidates": [],
        "candidate_count": 1,
        "needs_identity_confirmation": False,
        "current_team": context.get("current_team"),
        "current_roster_status": context.get("current_roster_status"),
        "current_roster_source": context.get("current_roster_source"),
        "current_roster_as_of": context.get("current_roster_as_of"),
        "sleeper_player_id": context.get("sleeper_player_id"),
        "gsis_id": context.get("gsis_id"),
        "player_id_internal": context.get("player_id_internal"),
        "full_name": context.get("full_name"),
        "display_name": context.get("display_name"),
        "position": context.get("position"),
        "availability_context": context.get("availability_context"),
        "request": request,
    }


def _candidate_groups(candidate_rows: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in candidate_rows:
        key = _identity_key(row)
        groups.setdefault(key, []).append(row)
    return list(groups.values())


def _candidate_from_group(group: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(group, key=lambda row: int(row.get("source_priority") or 999))
    identity_row = _first_source_role(ordered, "identity") or ordered[0]
    global_row = _first_source_role(ordered, "global_current")
    roster_row = _first_source_role(ordered, "league_rostered")
    available_row = _first_source_role(ordered, "league_available")

    state_row = available_row or roster_row or global_row or identity_row
    team_row = global_row or state_row
    availability_row = roster_row or available_row
    warnings: list[str] = []
    if team_row.get("current_team") is None:
        warnings.append("Current team is unknown in approved current roster sources.")
    if availability_row and global_row and availability_row.get("source_name") != global_row.get("source_name"):
        warnings.append("League availability context is preserved separately from global current player state.")

    context = {
        "player_id_internal": _clean_optional(
            identity_row.get("player_id_internal") or state_row.get("player_id_internal")
        ),
        "gsis_id": _clean_optional(identity_row.get("gsis_id") or state_row.get("gsis_id")),
        "sleeper_player_id": _clean_optional(
            identity_row.get("sleeper_player_id") or state_row.get("sleeper_player_id")
        ),
        "full_name": _clean_optional(identity_row.get("full_name") or state_row.get("full_name")),
        "display_name": _clean_optional(
            identity_row.get("display_name") or state_row.get("display_name")
        ),
        "position": _clean_optional(identity_row.get("position") or state_row.get("position")),
        "current_team": _clean_optional(team_row.get("current_team")),
        "current_roster_status": _current_status(state_row, availability_row),
        "current_roster_source": _clean_optional(state_row.get("source_name")),
        "current_roster_as_of": _stringify(state_row.get("current_roster_as_of")),
        "fantasy_availability": _fantasy_availability(availability_row),
        "free_agent": _is_free_agent(state_row, availability_row),
        "current_roster_source_policy": SOURCE_POLICY,
        "source_policy": SOURCE_POLICY,
        "source_freshness_json": state_row.get("source_freshness_json"),
        "missing_data_flags": state_row.get("missing_data_flags"),
        "availability_context": _availability_context(availability_row),
        "identity_sources": [
            row.get("source_name")
            for row in ordered
            if row.get("source_role") == "identity"
        ],
        "provenance": _provenance(ordered),
        "warnings": warnings,
    }
    return context


def _current_status(
    current_row: dict[str, Any],
    availability_row: dict[str, Any] | None,
) -> str | None:
    if availability_row and availability_row.get("source_role") == "league_available":
        return _clean_optional(availability_row.get("current_roster_status")) or "available"
    return _clean_optional(current_row.get("current_roster_status")) or "unknown"


def _fantasy_availability(row: dict[str, Any] | None) -> str | None:
    if not row:
        return None
    return _clean_optional(row.get("fantasy_availability")) or _clean_optional(row.get("source_role"))


def _is_free_agent(
    current_row: dict[str, Any],
    availability_row: dict[str, Any] | None,
) -> bool:
    if availability_row and availability_row.get("source_role") == "league_available":
        return True
    values = [
        current_row.get("current_roster_status"),
        current_row.get("fantasy_availability"),
        current_row.get("free_agent"),
    ]
    return any(
        str(value).lower() in {"true", "free_agent", "available", "free agent"}
        for value in values
        if value is not None
    )


def _availability_context(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    return {
        "source": row.get("source_name"),
        "league_id": row.get("league_id"),
        "roster_id": row.get("roster_id"),
        "fantasy_availability": _fantasy_availability(row),
        "current_roster_status": _clean_optional(row.get("current_roster_status")),
        "current_roster_as_of": _stringify(row.get("current_roster_as_of")),
    }


def _provenance(rows_for_candidate: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source": row.get("source_name"),
            "source_role": row.get("source_role"),
            "source_priority": row.get("source_priority"),
            "current_roster_as_of": _stringify(row.get("current_roster_as_of")),
            "source_freshness_json": row.get("source_freshness_json"),
            "missing_data_flags": row.get("missing_data_flags"),
        }
        for row in rows_for_candidate
    ]


def _first_source_role(rows_for_candidate: list[dict[str, Any]], role: str) -> dict[str, Any] | None:
    for row in rows_for_candidate:
        if row.get("source_role") == role:
            return row
    return None


def _identity_key(row: dict[str, Any]) -> str:
    for field in STABLE_ID_FIELDS:
        value = _clean_optional(row.get(field))
        if value:
            return f"{field}:{value}"
    return f"name:{_normalize_name(row.get('display_name') or row.get('full_name')) or 'unknown'}"


def _validate_lookup_request(
    *,
    player_id_internal: str | None,
    sleeper_player_id: str | None,
    gsis_id: str | None,
    player_name: str | None,
    limit: int | str | None,
    extra_args: dict[str, Any],
) -> dict[str, Any] | None:
    unsafe_keys = [key for key in extra_args if str(key).lower() in UNSAFE_INPUT_KEYS]
    if unsafe_keys:
        return _validation_error(
            "Arbitrary SQL/query input is not accepted by current roster lookup.",
            extra={"blocked_reason": "arbitrary_sql_not_allowed", "unsafe_args": unsafe_keys},
        )
    if extra_args:
        return _validation_error(
            "Unknown lookup arguments are not accepted by current roster lookup.",
            extra={"unknown_args": sorted(extra_args)},
        )
    if not any(
        _clean_optional(value)
        for value in (player_id_internal, sleeper_player_id, gsis_id, player_name)
    ):
        return _validation_error("At least one bounded identity input is required.")
    if _clean_optional(player_name) and not any(
        _clean_optional(value) for value in (player_id_internal, sleeper_player_id, gsis_id)
    ) and limit is None:
        return _validation_error("limit is required for player_name lookup.")
    return None


def _validation_error(message: str, *, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    response = {
        "status": "validation_error",
        "found": False,
        "source": "pigskin_current_roster_lookup",
        "source_policy": SOURCE_POLICY,
        "warnings": [LOOKUP_POLICY],
        "error": message,
        "candidates": [],
        "candidate_count": 0,
        "needs_identity_confirmation": False,
    }
    response.update(extra or {})
    return response


def _request_summary(
    *,
    player_id_internal: str | None,
    sleeper_player_id: str | None,
    gsis_id: str | None,
    player_name: str | None,
    team: str | None,
    position: str | None,
    league_id: str | None,
    include_available_players: bool,
    limit: int,
) -> dict[str, Any]:
    return {
        "player_id_internal": _clean_optional(player_id_internal),
        "sleeper_player_id": _clean_optional(sleeper_player_id),
        "gsis_id": _clean_optional(gsis_id),
        "player_name": _clean_optional(player_name),
        "team": _clean_optional(team),
        "position": _clean_optional(position),
        "league_id": _clean_optional(league_id),
        "include_available_players": bool(include_available_players),
        "limit": _clamp_limit(limit),
    }


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


def _normalize_name(value: Any) -> str | None:
    text = _clean_optional(value)
    if not text:
        return None
    return re.sub(r"\s+", " ", text.lower()).strip()


def _clean_optional(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _stringify(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return str(value)


def _dedupe(values: list[Any]) -> list[Any]:
    seen: set[str] = set()
    result: list[Any] = []
    for value in values:
        key = repr(value)
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    if not IDENTIFIER_RE.match(table_name):
        raise ValueError(f"Unsafe BigQuery table name: {table_name}")
    return f"{project_id}.{dataset_id}.{table_name}"
