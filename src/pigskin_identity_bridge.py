"""Internal read-only identity bridge for Pigskin packet QA."""

from __future__ import annotations

import os
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from google.cloud import bigquery

from src.llm_context_packets import get_bigquery_dataset
from src.load import get_bigquery_client
from src.pigskin_current_roster_merge import CURRENT_ROSTER_SOURCE_POLICY


DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("PIGSKIN_IDENTITY_BRIDGE_MAX_BYTES_BILLED", "1000000000"))
DEFAULT_LIMIT = 5
MAX_LIMIT = 25
SOURCE = "pigskin_identity_bridge"
SOURCE_POLICY = "internal_read_only_identity_resolution_only"
LOOKUP_POLICY = (
    "Current roster/free-agent/current-team status must come from approved current roster "
    "or identity sources, never historical packet team."
)
APPROVED_SOURCES = (
    "player_identity_bridge",
    "dim_players_current",
    "sleeper_players_current",
    "sleeper_roster_players",
    "sleeper_available_players",
)
FORBIDDEN_SOURCES = (
    "compat_viewer_team_context",
    "raw_nflverse_pbp",
    "weekly_metrics",
    "compat_pigskin_player_context_current",
)
UNSAFE_INPUT_KEYS = {"sql", "query", "sql_query", "raw_sql"}
STABLE_ID_FIELDS = ("player_id_internal", "sleeper_player_id", "gsis_id")
NAME_FIELDS = ("player_name", "full_name", "display_name", "compact_name")

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")
TOKEN_RE = re.compile(r"[a-z0-9]+")
RAW_GSIS_ID_RE = re.compile(r"^00-\d+$")


def resolve_player_identity(
    *,
    player_id_internal: str | None = None,
    sleeper_player_id: str | None = None,
    gsis_id: str | None = None,
    player_name: str | None = None,
    full_name: str | None = None,
    display_name: str | None = None,
    compact_name: str | None = None,
    team: str | None = None,
    position: str | None = None,
    season: int | str | None = None,
    week: int | str | None = None,
    league_id: str | None = None,
    include_available_players: bool = False,
    limit: int | str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
    **extra_args: Any,
) -> dict[str, Any]:
    """Resolve identity candidates from approved read-only sources."""

    validation_error = _validate_request(
        player_id_internal=player_id_internal,
        sleeper_player_id=sleeper_player_id,
        gsis_id=gsis_id,
        player_name=player_name,
        full_name=full_name,
        display_name=display_name,
        compact_name=compact_name,
        team=team,
        position=position,
        limit=limit,
        extra_args=extra_args,
    )
    if validation_error:
        return validation_error

    safe_limit = _clamp_limit(limit)
    query_client = client or get_bigquery_client()
    dataset = dataset_id or get_bigquery_dataset()
    sql, job_config = build_identity_bridge_query(
        project_id=query_client.project,
        dataset_id=dataset,
        player_id_internal=_clean_optional(player_id_internal),
        sleeper_player_id=_clean_optional(sleeper_player_id),
        gsis_id=_clean_optional(gsis_id),
        player_name=_clean_optional(player_name),
        full_name=_clean_optional(full_name),
        display_name=_clean_optional(display_name),
        compact_name=_clean_optional(compact_name),
        team=_clean_optional(team),
        position=_clean_optional(position),
        league_id=_clean_optional(league_id),
        include_available_players=include_available_players,
        limit=safe_limit,
    )

    request = _request_summary(
        player_id_internal=player_id_internal,
        sleeper_player_id=sleeper_player_id,
        gsis_id=gsis_id,
        player_name=player_name,
        full_name=full_name,
        display_name=display_name,
        compact_name=compact_name,
        team=team,
        position=position,
        season=season,
        week=week,
        league_id=league_id,
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
            "source": SOURCE,
            "source_policy": SOURCE_POLICY,
            "warnings": [LOOKUP_POLICY],
            "error": f"Failed to resolve player identity: {exc}",
            "request": request,
        }

    return _response_from_identity_rows(candidate_rows, request=request)


def build_identity_bridge_query(
    *,
    project_id: str,
    dataset_id: str,
    player_id_internal: str | None = None,
    sleeper_player_id: str | None = None,
    gsis_id: str | None = None,
    player_name: str | None = None,
    full_name: str | None = None,
    display_name: str | None = None,
    compact_name: str | None = None,
    team: str | None = None,
    position: str | None = None,
    league_id: str | None = None,
    include_available_players: bool = False,
    limit: int = DEFAULT_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    """Build the only query used by the identity bridge."""

    player_identity_bridge = _table_id(project_id, dataset_id, "player_identity_bridge")
    dim_players_current = _table_id(project_id, dataset_id, "dim_players_current")
    sleeper_players_current = _table_id(project_id, dataset_id, "sleeper_players_current")
    sleeper_roster_players = _table_id(project_id, dataset_id, "sleeper_roster_players")
    sleeper_available_players = _table_id(project_id, dataset_id, "sleeper_available_players")
    name_values = _name_lookup_values(player_name, full_name, display_name)
    compact_values = _compact_lookup_values(player_name, full_name, display_name, compact_name)
    player_id_internal_variants = _player_id_internal_lookup_variants(player_id_internal)
    stable_filter_count = int(bool(player_id_internal_variants)) + sum(
        1 for value in (sleeper_player_id, gsis_id) if _clean_optional(value)
    )
    has_name_lookup = bool(name_values or compact_values)

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
            updated_at AS source_as_of,
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
            updated_at AS source_as_of,
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
            TO_JSON_STRING(STRUCT(IF(sp.team IS NULL, ['missing_current_team'], []) AS flags)) AS missing_data_flags,
            sp.snapshot_at AS source_as_of,
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
            TO_JSON_STRING(STRUCT(IF(rp.team IS NULL, ['missing_current_team'], []) AS flags)) AS missing_data_flags,
            rp.snapshot_at AS source_as_of,
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
            TO_JSON_STRING(STRUCT(IF(ap.team IS NULL, ['missing_current_team'], []) AS flags)) AS missing_data_flags,
            ap.snapshot_at AS source_as_of,
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
    normalized_candidates AS (
        SELECT
            *,
            TRIM(REGEXP_REPLACE(LOWER(COALESCE(display_name, full_name, normalized_name, '')), r'[^a-z0-9]+', ' ')) AS normalized_for_match,
            REGEXP_REPLACE(LOWER(COALESCE(display_name, full_name, normalized_name, '')), r'[^a-z0-9]+', '') AS compact_for_match,
            TRIM(REGEXP_REPLACE(LOWER(COALESCE(normalized_name, '')), r'[^a-z0-9]+', ' ')) AS stored_normalized_for_match,
            REGEXP_REPLACE(LOWER(COALESCE(normalized_name, '')), r'[^a-z0-9]+', '') AS stored_compact_for_match
        FROM all_candidates
    ),
    enriched_candidates AS (
        SELECT
            *,
            ARRAY_REVERSE(SPLIT(normalized_for_match, ' '))[SAFE_OFFSET(0)] AS last_name_for_match,
            SPLIT(normalized_for_match, ' ')[SAFE_OFFSET(0)] AS first_name_for_match
        FROM normalized_candidates
    ),
    filtered_candidates AS (
        SELECT
            *,
            CONCAT(SUBSTR(first_name_for_match, 1, 1), '.', last_name_for_match) AS compact_display_name,
            CONCAT(SUBSTR(first_name_for_match, 1, 1), last_name_for_match) AS compact_display_name_no_dot
        FROM enriched_candidates
        WHERE (
                @stable_filter_count = 0
                OR (
                    ARRAY_LENGTH(@player_id_internal_variants) > 0
                    AND player_id_internal IN UNNEST(@player_id_internal_variants)
                )
                OR (@sleeper_player_id IS NOT NULL AND sleeper_player_id = @sleeper_player_id)
                OR (@gsis_id IS NOT NULL AND gsis_id = @gsis_id)
            )
            AND (
                @has_name_lookup = FALSE
                OR normalized_for_match IN UNNEST(@normalized_names)
                OR compact_for_match IN UNNEST(@normalized_names)
                OR stored_normalized_for_match IN UNNEST(@normalized_names)
                OR stored_compact_for_match IN UNNEST(@normalized_names)
                OR CONCAT(SUBSTR(first_name_for_match, 1, 1), '.', last_name_for_match) IN UNNEST(@compact_names)
                OR CONCAT(SUBSTR(first_name_for_match, 1, 1), last_name_for_match) IN UNNEST(@compact_names)
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
        normalized_for_match,
        compact_display_name,
        position,
        current_team,
        current_roster_status,
        league_id,
        roster_id,
        source_freshness_json,
        missing_data_flags,
        source_as_of,
        fantasy_availability,
        free_agent
    FROM filtered_candidates
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY
            source_name,
            COALESCE(player_id_internal, CONCAT('sleeper:', sleeper_player_id), CONCAT('gsis:', gsis_id), CONCAT('name:', normalized_for_match))
        ORDER BY source_as_of DESC NULLS LAST, display_name ASC
    ) = 1
    ORDER BY
        COALESCE(player_id_internal, sleeper_player_id, gsis_id, normalized_for_match),
        source_priority ASC,
        source_as_of DESC NULLS LAST
    LIMIT @limit
    """

    query_parameters: list[Any] = [
        bigquery.ArrayQueryParameter(
            "player_id_internal_variants",
            "STRING",
            player_id_internal_variants,
        ),
        bigquery.ScalarQueryParameter("sleeper_player_id", "STRING", sleeper_player_id),
        bigquery.ScalarQueryParameter("gsis_id", "STRING", gsis_id),
        bigquery.ScalarQueryParameter("team", "STRING", team),
        bigquery.ScalarQueryParameter("position", "STRING", position),
        bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
        bigquery.ScalarQueryParameter("include_available_players", "BOOL", bool(include_available_players)),
        bigquery.ScalarQueryParameter("stable_filter_count", "INT64", stable_filter_count),
        bigquery.ScalarQueryParameter("has_name_lookup", "BOOL", has_name_lookup),
        bigquery.ScalarQueryParameter("limit", "INT64", _clamp_limit(limit)),
        bigquery.ArrayQueryParameter("normalized_names", "STRING", name_values),
        bigquery.ArrayQueryParameter("compact_names", "STRING", compact_values),
    ]
    return sql, bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=query_parameters,
    )


def _player_id_internal_lookup_variants(player_id_internal: str | None) -> list[str]:
    cleaned = _clean_optional(player_id_internal)
    if not cleaned:
        return []
    variants = [cleaned]
    if RAW_GSIS_ID_RE.fullmatch(cleaned):
        variants.append(f"gsis:{cleaned}")
    elif cleaned.startswith("gsis:"):
        raw_gsis = cleaned.removeprefix("gsis:")
        if RAW_GSIS_ID_RE.fullmatch(raw_gsis):
            variants.append(raw_gsis)
    return _dedupe(variants)


def reconcile_packet_and_current_identity(
    historical_packet: dict[str, Any] | None,
    current_roster_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return explicit identity diagnostics for one packet/current pairing."""

    packet = historical_packet or {}
    current = current_roster_payload or {}
    packet_ids = _stable_ids(packet)
    current_ids = _stable_ids(current)
    base = {
        "source": SOURCE,
        "source_policy": SOURCE_POLICY,
        "historical_display_name": _clean_optional(packet.get("display_name") or packet.get("player_name")),
        "current_display_name": _clean_optional(
            current.get("display_name") or current.get("player_name") or current.get("full_name")
        ),
        "historical_team": _clean_optional(packet.get("historical_team") or packet.get("team")),
        "current_team": _clean_optional(current.get("current_team") or current.get("team")),
        "stable_ids": {"historical": packet_ids, "current": current_ids},
        "mismatch_diagnostics": [],
        "warnings": [LOOKUP_POLICY],
    }
    if not packet:
        return {
            **base,
            "status": "historical_packet_unavailable",
            "needs_identity_confirmation": True,
            "blocked_reason": "historical_packet_unavailable",
        }
    if not current or current.get("unavailable"):
        return {
            **base,
            "status": "current_roster_source_gap",
            "needs_identity_confirmation": True,
            "blocked_reason": "approved_current_roster_source_unavailable",
            "warnings": base["warnings"]
            + ["Current roster state is unavailable and was not inferred from historical packet team."],
        }

    mismatch_diagnostics = explain_identity_mismatch(packet, current)
    if mismatch_diagnostics:
        return {
            **base,
            "status": "needs_identity_confirmation",
            "needs_identity_confirmation": True,
            "blocked_reason": "stable_id_mismatch",
            "mismatch_diagnostics": mismatch_diagnostics,
            "warnings": base["warnings"] + ["Historical packet and current roster stable IDs do not reconcile."],
        }

    compared_fields = [
        field
        for field in STABLE_ID_FIELDS
        if packet_ids.get(field)
        and current_ids.get(field)
        and _stable_id_values_match(field, packet_ids[field], current_ids[field])
    ]
    if compared_fields:
        return {
            **base,
            "status": "identity_match",
            "needs_identity_confirmation": False,
            "matched_stable_id_fields": compared_fields,
        }

    return {
        **base,
        "status": "weak_identity_match",
        "needs_identity_confirmation": True,
        "blocked_reason": "no_shared_stable_id",
        "warnings": base["warnings"]
        + ["No shared stable ID was available; name/team alignment is not identity authority."],
    }


def explain_identity_mismatch(
    historical_packet: dict[str, Any] | None,
    current_roster_payload: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Explain stable ID disagreements without choosing a side."""

    packet_ids = _stable_ids(historical_packet or {})
    current_ids = _stable_ids(current_roster_payload or {})
    diagnostics = []
    for field in STABLE_ID_FIELDS:
        packet_value = packet_ids.get(field)
        current_value = current_ids.get(field)
        if packet_value and current_value and not _stable_id_values_match(
            field,
            packet_value,
            current_value,
        ):
            diagnostics.append(
                {
                    "field": field,
                    "historical_value": packet_value,
                    "current_value": current_value,
                    "resolution": "needs_identity_confirmation",
                }
            )
    return diagnostics


def _stable_id_values_match(field: str, left: str, right: str) -> bool:
    left_values = _stable_id_comparison_values(field, left)
    right_values = _stable_id_comparison_values(field, right)
    return bool(left_values & right_values)


def _stable_id_comparison_values(field: str, value: str) -> set[str]:
    cleaned = _clean_optional(value)
    if not cleaned:
        return set()
    if field == "player_id_internal":
        return set(_player_id_internal_lookup_variants(cleaned))
    return {cleaned}


def normalize_player_name(value: Any) -> str | None:
    """Normalize a display/full name for conservative matching."""

    text = _clean_optional(value)
    if not text:
        return None
    normalized = " ".join(TOKEN_RE.findall(text.lower()))
    return normalized or None


def build_compact_display_variants(*names: Any) -> list[str]:
    """Return compact display variants like t.hill and thill."""

    variants: set[str] = set()
    for name in names:
        text = _clean_optional(name)
        if not text:
            continue
        normalized = normalize_player_name(text)
        if not normalized:
            continue
        tokens = normalized.split()
        compact_input = re.sub(r"[^a-z0-9]+", "", text.lower())
        if compact_input:
            variants.add(compact_input)
        if len(tokens) >= 2:
            first = tokens[0]
            last = tokens[-1]
            variants.add(f"{first[:1]}.{last}")
            variants.add(f"{first[:1]}{last}")
            if len(tokens) > 2:
                initials = "".join(token[:1] for token in tokens[:-1] if token)
                if initials:
                    variants.add(f"{initials}.{last}")
                    variants.add(f"{initials}{last}")
    return sorted(variants)


def _response_from_identity_rows(
    candidate_rows: list[dict[str, Any]],
    *,
    request: dict[str, Any],
) -> dict[str, Any]:
    warnings = [LOOKUP_POLICY] + _lookup_normalization_warnings(request)
    if not candidate_rows:
        return {
            "status": "not_found",
            "found": False,
            "source": SOURCE,
            "source_policy": SOURCE_POLICY,
            "warnings": warnings + ["No approved identity/current roster source matched the bounded lookup."],
            "candidates": [],
            "candidate_count": 0,
            "needs_identity_confirmation": False,
            "request": request,
        }

    groups = _candidate_groups(candidate_rows)
    candidates = [_candidate_from_group(group) for group in groups]
    conflicted = [candidate for candidate in candidates if candidate.get("identity_conflicts")]
    if len(candidates) > 1:
        return {
            "status": "ambiguous",
            "found": False,
            "source": SOURCE,
            "source_policy": SOURCE_POLICY,
            "warnings": warnings + ["Identity bridge matched multiple candidate identities."],
            "candidates": candidates,
            "candidate_count": len(candidates),
            "selected_identity": None,
            "needs_identity_confirmation": True,
            "request": request,
        }
    if conflicted:
        return {
            "status": "needs_identity_confirmation",
            "found": False,
            "source": SOURCE,
            "source_policy": SOURCE_POLICY,
            "warnings": warnings + ["Approved sources returned conflicting stable IDs."],
            "candidates": candidates,
            "candidate_count": len(candidates),
            "selected_identity": None,
            "needs_identity_confirmation": True,
            "mismatch_diagnostics": conflicted[0].get("identity_conflicts"),
            "request": request,
        }
    selected = candidates[0]
    return {
        "status": "ok",
        "found": True,
        "source": SOURCE,
        "source_policy": SOURCE_POLICY,
        "warnings": _dedupe(warnings + selected.get("warnings", [])),
        "selected_identity": selected,
        "candidates": [],
        "candidate_count": 1,
        "needs_identity_confirmation": False,
        "identity_sources": selected.get("identity_sources"),
        "stable_ids": selected.get("stable_ids"),
        "full_name": selected.get("full_name"),
        "display_name": selected.get("display_name"),
        "compact_display_names": selected.get("compact_display_names"),
        "current_team": selected.get("current_team"),
        "active_status": selected.get("active_status"),
        "provenance": selected.get("provenance"),
        "request": request,
    }


def _candidate_groups(candidate_rows: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    groups: list[dict[str, Any]] = []
    for row in candidate_rows:
        identifiers = _identifier_set(row)
        matched = [group for group in groups if identifiers & group["identifiers"]]
        if not matched:
            groups.append({"identifiers": set(identifiers), "rows": [row]})
            continue
        primary = matched[0]
        primary["rows"].append(row)
        primary["identifiers"].update(identifiers)
        for group in matched[1:]:
            primary["rows"].extend(group["rows"])
            primary["identifiers"].update(group["identifiers"])
            groups.remove(group)
    return [group["rows"] for group in groups]


def _candidate_from_group(group: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(group, key=lambda row: int(row.get("source_priority") or 999))
    identity_row = _first_source_role(ordered, "identity") or ordered[0]
    current_row = (
        _first_source_role(ordered, "league_rostered")
        or _first_source_role(ordered, "league_available")
        or _first_source_role(ordered, "global_current")
        or identity_row
    )
    stable_id_values = _stable_id_values(ordered)
    identity_conflicts = [
        {
            "field": field,
            "values": values,
            "resolution": "needs_identity_confirmation",
        }
        for field, values in stable_id_values.items()
        if len(values) > 1
    ]
    stable_ids = {
        field: values[0]
        for field, values in stable_id_values.items()
        if len(values) == 1
    }
    compact_names = _dedupe(
        [
            item
            for row in ordered
            for item in build_compact_display_variants(
                row.get("display_name"),
                row.get("full_name"),
                row.get("compact_display_name"),
            )
            if item
        ]
    )
    current_team = _clean_optional(current_row.get("current_team"))
    warnings = []
    if current_team is None:
        warnings.append("Current team is unknown in approved current roster sources.")

    return {
        "stable_ids": stable_ids,
        "identity_conflicts": identity_conflicts,
        "full_name": _clean_optional(identity_row.get("full_name") or current_row.get("full_name")),
        "display_name": _clean_optional(identity_row.get("display_name") or current_row.get("display_name")),
        "compact_display_names": compact_names,
        "position": _clean_optional(identity_row.get("position") or current_row.get("position")),
        "current_team": current_team,
        "active_status": _clean_optional(current_row.get("current_roster_status")),
        "current_roster_source": _clean_optional(current_row.get("source_name")),
        "current_roster_as_of": _stringify(current_row.get("source_as_of")),
        "fantasy_availability": _clean_optional(current_row.get("fantasy_availability")),
        "free_agent": bool(current_row.get("free_agent")),
        "identity_sources": [
            row.get("source_name") for row in ordered if row.get("source_role") == "identity"
        ],
        "provenance": _provenance(ordered),
        "warnings": warnings,
    }


def _validate_request(
    *,
    player_id_internal: str | None,
    sleeper_player_id: str | None,
    gsis_id: str | None,
    player_name: str | None,
    full_name: str | None,
    display_name: str | None,
    compact_name: str | None,
    team: str | None,
    position: str | None,
    limit: int | str | None,
    extra_args: dict[str, Any],
) -> dict[str, Any] | None:
    unsafe_keys = _unsafe_keys(extra_args)
    if unsafe_keys:
        return _validation_error(
            "Arbitrary SQL/query input is not accepted by identity bridge.",
            extra={"blocked_reason": "arbitrary_sql_not_allowed", "unsafe_args": unsafe_keys},
        )
    if extra_args:
        return _validation_error(
            "Unknown lookup arguments are not accepted by identity bridge.",
            extra={"unknown_args": sorted(extra_args)},
        )
    stable_values = (player_id_internal, sleeper_player_id, gsis_id)
    name_values = (player_name, full_name, display_name, compact_name)
    has_stable = any(_clean_optional(value) for value in stable_values)
    has_name = any(_clean_optional(value) for value in name_values)
    if not has_stable and not has_name:
        if _clean_optional(team) or _clean_optional(position):
            return _validation_error("Team and position may narrow a lookup, but are not identity fields.")
        return _validation_error("At least one stable ID or name input is required.")
    if has_name and not has_stable and limit is None:
        return _validation_error("limit is required for name or compact-name lookup.")
    return None


def _validation_error(message: str, *, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    response = {
        "status": "validation_error",
        "found": False,
        "source": SOURCE,
        "source_policy": SOURCE_POLICY,
        "warnings": [LOOKUP_POLICY],
        "error": message,
        "candidates": [],
        "candidate_count": 0,
        "needs_identity_confirmation": False,
    }
    response.update(extra or {})
    return response


def _name_lookup_values(*names: Any) -> list[str]:
    values: set[str] = set()
    for name in names:
        normalized = normalize_player_name(name)
        if normalized:
            values.add(normalized)
            values.add(normalized.replace(" ", ""))
    return sorted(values)


def _compact_lookup_values(*names: Any) -> list[str]:
    values: set[str] = set()
    for name in names:
        values.update(build_compact_display_variants(name))
    return sorted(value for value in values if value)


def _request_summary(
    *,
    player_id_internal: str | None,
    sleeper_player_id: str | None,
    gsis_id: str | None,
    player_name: str | None,
    full_name: str | None,
    display_name: str | None,
    compact_name: str | None,
    team: str | None,
    position: str | None,
    season: int | str | None,
    week: int | str | None,
    league_id: str | None,
    include_available_players: bool,
    limit: int,
) -> dict[str, Any]:
    player_id_internal_variants = _player_id_internal_lookup_variants(player_id_internal)
    summary = {
        "player_id_internal": _clean_optional(player_id_internal),
        "sleeper_player_id": _clean_optional(sleeper_player_id),
        "gsis_id": _clean_optional(gsis_id),
        "player_name": _clean_optional(player_name),
        "full_name": _clean_optional(full_name),
        "display_name": _clean_optional(display_name),
        "compact_name": _clean_optional(compact_name),
        "team": _clean_optional(team),
        "position": _clean_optional(position),
        "season": _clean_optional(season),
        "week": _clean_optional(week),
        "league_id": _clean_optional(league_id),
        "include_available_players": bool(include_available_players),
        "limit": _clamp_limit(limit),
    }
    if player_id_internal_variants:
        summary["player_id_internal_lookup_variants"] = player_id_internal_variants
    return summary


def _lookup_normalization_warnings(request: dict[str, Any]) -> list[str]:
    variants = request.get("player_id_internal_lookup_variants")
    if not isinstance(variants, list) or len(variants) <= 1:
        return []
    return [
        "player_id_internal lookup included raw/prefixed GSIS variants for read-only matching."
    ]


def _identifier_set(row: dict[str, Any]) -> set[str]:
    identifiers = {
        f"{field}:{_clean_optional(row.get(field))}"
        for field in STABLE_ID_FIELDS
        if _clean_optional(row.get(field))
    }
    if identifiers:
        return identifiers
    normalized = normalize_player_name(row.get("display_name") or row.get("full_name"))
    return {f"name:{normalized or 'unknown'}"}


def _stable_id_values(rows_for_candidate: list[dict[str, Any]]) -> dict[str, list[str]]:
    values: dict[str, set[str]] = {field: set() for field in STABLE_ID_FIELDS}
    for row in rows_for_candidate:
        for field in STABLE_ID_FIELDS:
            value = _clean_optional(row.get(field))
            if value:
                values[field].add(value)
    return {field: sorted(field_values) for field, field_values in values.items() if field_values}


def _stable_ids(payload: dict[str, Any]) -> dict[str, str]:
    nested = payload.get("stable_ids") if isinstance(payload.get("stable_ids"), dict) else {}
    return {
        field: value
        for field in STABLE_ID_FIELDS
        if (value := _clean_optional(payload.get(field) or nested.get(field)))
    }


def _first_source_role(rows_for_candidate: list[dict[str, Any]], role: str) -> dict[str, Any] | None:
    for row in rows_for_candidate:
        if row.get("source_role") == role:
            return row
    return None


def _provenance(rows_for_candidate: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source": row.get("source_name"),
            "source_role": row.get("source_role"),
            "source_priority": row.get("source_priority"),
            "source_as_of": _stringify(row.get("source_as_of")),
            "source_freshness_json": row.get("source_freshness_json"),
            "missing_data_flags": row.get("missing_data_flags"),
        }
        for row in rows_for_candidate
    ]


def _unsafe_keys(value: Any, prefix: str = "") -> list[str]:
    if not isinstance(value, dict):
        return []
    unsafe: list[str] = []
    for key, item in value.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if str(key).lower() in UNSAFE_INPUT_KEYS:
            unsafe.append(path)
        if isinstance(item, dict):
            unsafe.extend(_unsafe_keys(item, path))
    return unsafe


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


__all__ = [
    "APPROVED_SOURCES",
    "CURRENT_ROSTER_SOURCE_POLICY",
    "FORBIDDEN_SOURCES",
    "build_compact_display_variants",
    "build_identity_bridge_query",
    "explain_identity_mismatch",
    "normalize_player_name",
    "reconcile_packet_and_current_identity",
    "resolve_player_identity",
]
