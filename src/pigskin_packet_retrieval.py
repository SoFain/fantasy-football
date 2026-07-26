"""Safe retrieval helpers for historical nflverse Pigskin packets."""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from google.cloud import bigquery

from src.llm_context_packets import (
    DEFAULT_LEAGUE_TYPE,
    DEFAULT_ROSTER_FORMAT,
    DEFAULT_SCORING_PROFILE,
    get_bigquery_dataset,
)
from src.load import get_bigquery_client


DEFAULT_MAX_BYTES_BILLED = int(
    os.environ.get("PIGSKIN_PACKET_RETRIEVAL_MAX_BYTES_BILLED", "1000000000")
)
DEFAULT_LIMIT = 10
MAX_LIMIT = 50
MIN_HISTORICAL_SEASON = 2014
MAX_HISTORICAL_SEASON = int(os.environ.get("PIGSKIN_PACKET_MAX_HISTORICAL_SEASON", "2025"))
PACKET_TEXT_LIMIT = 10000
SOURCE_VIEW = "compat_pigskin_player_context_current"
SOURCE_POLICY = "historical_nflverse_packet_context_only"
CURRENT_ROSTER_POLICY = (
    "Current roster/free-agent status must come from Sleeper/current roster source."
)
HISTORICAL_CONTEXT_WARNING = "Historical nflverse packet context only."

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")


def retrieve_historical_pigskin_packets(
    *,
    season: int | str | None = None,
    season_start: int | str | None = None,
    season_end: int | str | None = None,
    week: int | str | None = None,
    include_postseason: bool = False,
    player_id_internal: str | None = None,
    player_name: str | None = None,
    team: str | None = None,
    position: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int | str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    """Return safe historical packet results from the compatibility view."""

    validation_error = _validate_request(
        season=season,
        season_start=season_start,
        season_end=season_end,
        week=week,
    )
    if validation_error:
        return validation_error

    query_client = client or get_bigquery_client()
    dataset = _dataset(dataset_id)
    safe_limit = _clamp_limit(limit)
    resolved_start, resolved_end = _season_window(season, season_start, season_end)
    safe_week = _clean_int_optional(week)
    name_variants = _player_name_variants(player_name)
    policy_warnings = [HISTORICAL_CONTEXT_WARNING, CURRENT_ROSTER_POLICY]
    if not include_postseason:
        policy_warnings.append(
            "Postseason packet rows are excluded by the regular-season cutoff rule."
        )

    sql, job_config = build_historical_packet_query(
        project_id=query_client.project,
        dataset_id=dataset,
        season_start=resolved_start,
        season_end=resolved_end,
        week=safe_week,
        include_postseason=include_postseason,
        player_id_internal=_clean_optional(player_id_internal),
        player_name_variants=name_variants,
        team=_clean_optional(team),
        position=_clean_optional(position),
        scoring_profile_id=_clean_optional(scoring_profile_id) or DEFAULT_SCORING_PROFILE,
        league_type_id=_clean_optional(league_type_id) or DEFAULT_LEAGUE_TYPE,
        roster_format_id=_clean_optional(roster_format_id) or DEFAULT_ROSTER_FORMAT,
        limit=safe_limit,
    )
    try:
        result = query_client.query(sql, job_config=job_config).result()
        result_rows = [dict(row) for row in result]
    except Exception as exc:
        return {
            "status": "query_error",
            "found": False,
            "source": SOURCE_VIEW,
            "source_policy": SOURCE_POLICY,
            "warnings": policy_warnings,
            "error": f"Failed to retrieve historical Pigskin packet context: {exc}",
            "request": _request_summary(
                season_start=resolved_start,
                season_end=resolved_end,
                week=safe_week,
                include_postseason=include_postseason,
                player_id_internal=player_id_internal,
                player_name=player_name,
                team=team,
                position=position,
                limit=safe_limit,
            ),
        }

    if not result_rows:
        return _no_match_response(
            season_start=resolved_start,
            season_end=resolved_end,
            week=safe_week,
            include_postseason=include_postseason,
            player_id_internal=player_id_internal,
            player_name=player_name,
            team=team,
            position=position,
            limit=safe_limit,
            warnings=policy_warnings,
        )

    if not _clean_optional(player_id_internal) and _clean_optional(player_name):
        candidates = _candidate_rows(result_rows)
        if len(candidates) > 1:
            return {
                "status": "ambiguous",
                "found": False,
                "source": SOURCE_VIEW,
                "source_policy": SOURCE_POLICY,
                "historical_context_only": True,
                "current_roster_status_source_required": True,
                "current_roster_status_policy": CURRENT_ROSTER_POLICY,
                "warnings": policy_warnings
                + ["Player-name lookup matched multiple historical packet identities."],
                "candidate_count": len(candidates),
                "candidates": candidates,
                "request": _request_summary(
                    season_start=resolved_start,
                    season_end=resolved_end,
                    week=safe_week,
                    include_postseason=include_postseason,
                    player_id_internal=player_id_internal,
                    player_name=player_name,
                    team=team,
                    position=position,
                    limit=safe_limit,
                ),
            }

    packets = [normalize_historical_packet(row) for row in result_rows]
    return {
        "status": "ok",
        "found": True,
        "source": SOURCE_VIEW,
        "source_policy": SOURCE_POLICY,
        "historical_context_only": True,
        "current_roster_status_source_required": True,
        "current_roster_status_policy": CURRENT_ROSTER_POLICY,
        "warnings": policy_warnings,
        "row_count": len(packets),
        "packet": packets[0] if len(packets) == 1 else None,
        "packets": packets,
        "request": _request_summary(
            season_start=resolved_start,
            season_end=resolved_end,
            week=safe_week,
            include_postseason=include_postseason,
            player_id_internal=player_id_internal,
            player_name=player_name,
            team=team,
            position=position,
            limit=safe_limit,
        ),
    }


def build_historical_packet_query(
    *,
    project_id: str,
    dataset_id: str,
    season_start: int,
    season_end: int,
    week: int | None = None,
    include_postseason: bool = False,
    player_id_internal: str | None = None,
    player_name_variants: list[str] | None = None,
    team: str | None = None,
    position: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int = DEFAULT_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    """Build the only BigQuery query used by the historical retrieval layer."""

    table_id = _table_id(project_id, dataset_id, SOURCE_VIEW)
    variants = [variant.lower() for variant in (player_name_variants or []) if variant]
    sql = f"""
    SELECT
        as_of_season,
        as_of_week,
        player_id_internal,
        player_name,
        position,
        team,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        packet_version,
        feature_run_id,
        packet_text,
        packet_json,
        source_freshness_json,
        missing_data_flags,
        created_at
    FROM `{table_id}`
    WHERE as_of_season BETWEEN @season_start AND @season_end
        AND (@week IS NULL OR as_of_week = @week)
        -- The packet surface has no game-type field, so regular-season mode
        -- conservatively excludes playoff weeks by season-era cutoff.
        AND (
            @include_postseason
            OR as_of_week <= IF(as_of_season <= 2020, 17, 18)
        )
        AND scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
        AND (@player_id_internal IS NULL OR player_id_internal = @player_id_internal)
        AND (@team IS NULL OR UPPER(team) = UPPER(@team))
        AND (@position IS NULL OR UPPER(position) = UPPER(@position))
        AND (
            @player_name_variant_count = 0
            OR LOWER(player_name) IN UNNEST(@player_name_variants)
        )
    ORDER BY as_of_season DESC, as_of_week DESC, player_name ASC, player_id_internal ASC
    LIMIT @limit
    """
    return sql, _job_config(
        [
            ("season_start", "INT64", season_start),
            ("season_end", "INT64", season_end),
            ("week", "INT64", week),
            ("include_postseason", "BOOL", include_postseason),
            ("scoring_profile_id", "STRING", scoring_profile_id),
            ("league_type_id", "STRING", league_type_id),
            ("roster_format_id", "STRING", roster_format_id),
            ("player_id_internal", "STRING", player_id_internal),
            ("team", "STRING", team),
            ("position", "STRING", position),
            ("player_name_variant_count", "INT64", len(variants)),
            ("limit", "INT64", _clamp_limit(limit)),
        ],
        array_params=[("player_name_variants", "STRING", variants)],
    )


def normalize_historical_packet(packet_row: Any) -> dict[str, Any]:
    """Convert one compatibility-row packet into a historical-only shape."""

    row = _json_safe(dict(packet_row))
    packet_json, packet_warnings = _parse_json_with_warnings(
        row.get("packet_json"),
        field_name="packet_json",
    )
    source_freshness, freshness_warnings = _parse_json_with_warnings(
        row.get("source_freshness_json"),
        field_name="source_freshness_json",
    )
    missing_flags, missing_warnings = _parse_json_with_warnings(
        row.get("missing_data_flags"),
        field_name="missing_data_flags",
    )
    packet_json = packet_json if isinstance(packet_json, dict) else {}
    source_freshness = source_freshness if isinstance(source_freshness, dict) else {}
    missing_flags = missing_flags if missing_flags not in (None, "") else {}
    warnings = (
        _as_list(packet_json.get("warnings"))
        + packet_warnings
        + freshness_warnings
        + missing_warnings
        + [HISTORICAL_CONTEXT_WARNING, CURRENT_ROSTER_POLICY]
    )
    blocked_metrics = _as_list(packet_json.get("blocked_metrics"))
    source_metric_version = packet_json.get("source_metric_version")

    return {
        "found": True,
        "source": SOURCE_VIEW,
        "source_policy": SOURCE_POLICY,
        "historical_context_only": True,
        "current_roster_status_source_required": True,
        "current_roster_status_policy": CURRENT_ROSTER_POLICY,
        "as_of_season": row.get("as_of_season"),
        "as_of_week": row.get("as_of_week"),
        "display_name": row.get("player_name"),
        "player_id_internal": row.get("player_id_internal"),
        "historical_position": row.get("position"),
        "historical_team": row.get("team"),
        "scoring_profile_id": row.get("scoring_profile_id"),
        "league_type_id": row.get("league_type_id"),
        "roster_format_id": row.get("roster_format_id"),
        "packet_version": row.get("packet_version"),
        "feature_run_id": row.get("feature_run_id"),
        "source_metric_version": source_metric_version,
        "packet_text": str(row.get("packet_text") or "")[:PACKET_TEXT_LIMIT],
        "packet_json": packet_json,
        "source_freshness": source_freshness,
        "missing_data_flags": missing_flags,
        "blocked_metrics": blocked_metrics,
        "blocked_metric_policy": "blocked metrics are unavailable, not zero",
        "warnings": _dedupe_preserve_order(warnings),
        "created_at": row.get("created_at"),
    }


def _validate_request(
    *,
    season: int | str | None,
    season_start: int | str | None,
    season_end: int | str | None,
    week: int | str | None,
) -> dict[str, Any] | None:
    resolved_start, resolved_end = _season_window(season, season_start, season_end)
    if resolved_start is None or resolved_end is None:
        return _validation_error(
            "explicit season or bounded season_start/season_end is required"
        )
    if resolved_start > resolved_end:
        return _validation_error("season_start must be less than or equal to season_end")
    if (
        resolved_start < MIN_HISTORICAL_SEASON
        or resolved_end > MAX_HISTORICAL_SEASON
    ):
        return _validation_error(
            f"historical packet retrieval is bounded to {MIN_HISTORICAL_SEASON}-{MAX_HISTORICAL_SEASON}"
        )
    safe_week = _clean_int_optional(week)
    if week not in (None, "") and safe_week is None:
        return _validation_error("week must be an integer when provided")
    if safe_week is not None and not 1 <= safe_week <= 22:
        return _validation_error("week must be between 1 and 22")
    return None


def _validation_error(message: str) -> dict[str, Any]:
    return {
        "status": "validation_error",
        "found": False,
        "source": SOURCE_VIEW,
        "source_policy": SOURCE_POLICY,
        "historical_context_only": True,
        "current_roster_status_source_required": True,
        "current_roster_status_policy": CURRENT_ROSTER_POLICY,
        "warnings": [HISTORICAL_CONTEXT_WARNING, CURRENT_ROSTER_POLICY],
        "error": message,
    }


def _no_match_response(
    *,
    season_start: int,
    season_end: int,
    week: int | None,
    include_postseason: bool,
    player_id_internal: str | None,
    player_name: str | None,
    team: str | None,
    position: str | None,
    limit: int,
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "status": "not_found",
        "found": False,
        "source": SOURCE_VIEW,
        "source_policy": SOURCE_POLICY,
        "historical_context_only": True,
        "current_roster_status_source_required": True,
        "current_roster_status_policy": CURRENT_ROSTER_POLICY,
        "warnings": warnings,
        "packets": [],
        "row_count": 0,
        "request": _request_summary(
            season_start=season_start,
            season_end=season_end,
            week=week,
            include_postseason=include_postseason,
            player_id_internal=player_id_internal,
            player_name=player_name,
            team=team,
            position=position,
            limit=limit,
        ),
    }


def _request_summary(
    *,
    season_start: int,
    season_end: int,
    week: int | None,
    include_postseason: bool,
    player_id_internal: str | None,
    player_name: str | None,
    team: str | None,
    position: str | None,
    limit: int,
) -> dict[str, Any]:
    return {
        "season_start": season_start,
        "season_end": season_end,
        "week": week,
        "include_postseason": include_postseason,
        "player_id_internal": _clean_optional(player_id_internal),
        "player_name": _clean_optional(player_name),
        "team": _clean_optional(team),
        "position": _clean_optional(position),
        "limit": limit,
    }


def _candidate_rows(result_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, Any, Any, Any]] = set()
    candidates: list[dict[str, Any]] = []
    for row in result_rows:
        key = (
            row.get("player_id_internal"),
            row.get("player_name"),
            row.get("position"),
            row.get("team"),
        )
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            {
                "player_id_internal": row.get("player_id_internal"),
                "display_name": row.get("player_name"),
                "historical_position": row.get("position"),
                "historical_team": row.get("team"),
                "as_of_season": row.get("as_of_season"),
                "as_of_week": row.get("as_of_week"),
            }
        )
    return candidates


def _player_name_variants(player_name: str | None) -> list[str]:
    text = _clean_optional(player_name)
    if not text:
        return []
    variants = {text.lower()}
    compacted = re.sub(r"\s+", " ", text.replace("'", "")).strip()
    parts = compacted.split()
    if len(parts) >= 2:
        last_name = parts[-1]
        first_token = parts[0].rstrip(".")
        if first_token:
            variants.add(f"{first_token[0]}.{last_name}".lower())
    variants.add(re.sub(r"\s+", "", compacted).lower())
    return sorted(variants)


def _season_window(
    season: int | str | None,
    season_start: int | str | None,
    season_end: int | str | None,
) -> tuple[int | None, int | None]:
    safe_season = _clean_int_optional(season)
    if safe_season is not None:
        return safe_season, safe_season
    safe_start = _clean_int_optional(season_start)
    safe_end = _clean_int_optional(season_end)
    if safe_start is None or safe_end is None:
        return None, None
    return safe_start, safe_end


def _parse_json_with_warnings(value: Any, *, field_name: str) -> tuple[Any, list[str]]:
    if value in (None, ""):
        return None, []
    parsed = _parse_json_once(value)
    if parsed is _UNPARSEABLE:
        return None, [f"{field_name} could not be parsed"]
    if isinstance(parsed, str) and parsed.strip().startswith(("{", "[")):
        nested = _parse_json_once(parsed)
        if nested is _UNPARSEABLE:
            return parsed, [f"{field_name} nested JSON could not be parsed"]
        return nested, []
    return parsed, []


_UNPARSEABLE = object()


def _parse_json_once(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return _UNPARSEABLE
    return value


def _as_list(value: Any) -> list[Any]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _dedupe_preserve_order(values: list[Any]) -> list[Any]:
    seen: set[str] = set()
    deduped: list[Any] = []
    for value in values:
        key = json.dumps(_json_safe(value), sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(value)
    return deduped


def _job_config(
    params: list[tuple[str, str, Any]],
    *,
    array_params: list[tuple[str, str, list[Any]]] | None = None,
) -> bigquery.QueryJobConfig:
    query_parameters: list[Any] = [
        bigquery.ScalarQueryParameter(name, type_name, value)
        for name, type_name, value in params
    ]
    for name, type_name, values in array_params or []:
        query_parameters.append(bigquery.ArrayQueryParameter(name, type_name, values))
    return bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=query_parameters,
    )


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    if not IDENTIFIER_RE.match(table_name):
        raise ValueError(f"Unsafe BigQuery table name: {table_name}")
    return f"{project_id}.{dataset_id}.{table_name}"


def _dataset(dataset_id: str | None) -> str:
    dataset = dataset_id or get_bigquery_dataset()
    if not IDENTIFIER_RE.match(dataset):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset}")
    return dataset


def _clamp_limit(value: int | str | None) -> int:
    try:
        parsed = int(value) if value is not None else DEFAULT_LIMIT
    except (TypeError, ValueError):
        parsed = DEFAULT_LIMIT
    return max(1, min(MAX_LIMIT, parsed))


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
