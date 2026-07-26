"""Pure merge helpers for historical Pigskin packets and current roster state."""

from __future__ import annotations

import copy
import re
from typing import Any

from src.pigskin_packet_guardrails import (
    BLOCKED_METRIC_POLICY,
    CURRENT_ROSTER_DEFERRAL_POLICY,
    HISTORICAL_PACKET_SOURCE_POLICY,
    HISTORICAL_TEAM_NAMING_RULE,
    POSTSEASON_POLICY,
)


CURRENT_ROSTER_SOURCE_POLICY = "sleeper_or_current_roster_payload_required"
MERGE_POLICY = (
    "Sleeper/current roster payload is authoritative for current team, roster "
    "status, availability, and free-agent state. Historical packets are "
    "completed-season context only."
)
UNSAFE_INPUT_KEYS = {"sql", "sql_query", "query", "raw_sql"}
STABLE_ID_FIELDS = ("player_id_internal", "gsis_id", "sleeper_player_id")
CURRENT_TEAM_FIELDS = ("current_team", "team")
CURRENT_STATUS_FIELDS = (
    "current_roster_status",
    "roster_status",
    "status",
    "fantasy_availability",
    "availability",
)
CURRENT_SOURCE_FIELDS = ("current_roster_source", "source", "source_name")
CURRENT_AS_OF_FIELDS = (
    "current_roster_as_of",
    "as_of",
    "snapshot_at",
    "snapshot_timestamp",
    "updated_at",
)
RAW_GSIS_ID_RE = re.compile(r"^00-\d+$")


def merge_historical_packet_with_current_roster(
    historical_result: dict[str, Any] | None,
    current_roster_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge safe historical packet context with supplied current roster state."""

    unsafe_keys = _unsafe_keys(historical_result) + _unsafe_keys(current_roster_payload)
    if unsafe_keys:
        return _base_response(
            status="validation_error",
            warnings=["Arbitrary SQL/query input is not accepted by the merge layer."],
            extra={
                "blocked_reason": "arbitrary_sql_not_allowed",
                "unsafe_args": _dedupe(unsafe_keys),
            },
        )

    historical_result = copy.deepcopy(historical_result or {})
    current_roster_payload = copy.deepcopy(current_roster_payload or {})
    warnings = _dedupe(
        _as_list(historical_result.get("warnings"))
        + _as_list(current_roster_payload.get("warnings"))
        + [MERGE_POLICY, CURRENT_ROSTER_DEFERRAL_POLICY]
    )

    if _is_ambiguous_packet(historical_result):
        return _base_response(
            status="needs_identity_confirmation",
            warnings=_dedupe(
                warnings
                + ["Historical packet lookup is ambiguous; current roster merge was not selected."]
            ),
            extra={
                "needs_identity_confirmation": True,
                "historical_context": None,
                "current_roster_context": None,
                "historical_candidates": historical_result.get("candidates") or [],
                "current_roster_candidates": _candidate_list(current_roster_payload),
                "provenance": _provenance(None, None),
            },
        )

    packet = _selected_packet(historical_result)
    if not packet:
        return _base_response(
            status="historical_context_unavailable",
            warnings=_dedupe(warnings + ["Historical packet context is unavailable."]),
            extra={
                "historical_context": None,
                "current_roster_context": _normalize_current_roster_context(current_roster_payload),
                "provenance": _provenance(None, current_roster_payload),
            },
        )

    packet = _strip_current_team(copy.deepcopy(packet))
    current_candidates = _candidate_list(current_roster_payload)
    if len(current_candidates) > 1 or _clean(current_roster_payload.get("status")) == "ambiguous":
        return _merge_response(
            status="needs_identity_confirmation",
            packet=packet,
            current_context=None,
            warnings=_dedupe(
                warnings
                + ["Current roster lookup returned multiple candidates; require player ID, team, or position."]
            ),
            current_roster_payload=current_roster_payload,
            needs_identity_confirmation=True,
            current_roster_candidates=current_candidates,
        )

    current_context = _normalize_current_roster_context(current_roster_payload)
    identity_status = _identity_status(packet, current_context)
    if identity_status == "mismatch":
        return _merge_response(
            status="needs_identity_confirmation",
            packet=packet,
            current_context=current_context,
            warnings=_dedupe(
                warnings
                + ["Current roster identity does not match historical packet identity."]
            ),
            current_roster_payload=current_roster_payload,
            needs_identity_confirmation=True,
        )

    if current_context is None:
        return _merge_response(
            status="current_roster_unavailable",
            packet=packet,
            current_context=None,
            warnings=_dedupe(
                warnings
                + ["Current roster payload is missing; current team/status was not inferred from packet team."]
            ),
            current_roster_payload=current_roster_payload,
        )

    caution = []
    if identity_status == "weak":
        caution.append(
            "Current roster identity lacks a stable ID match; treat name/team alignment as needing confirmation."
        )

    return _merge_response(
        status="ok",
        packet=packet,
        current_context=current_context,
        warnings=_dedupe(warnings + caution),
        current_roster_payload=current_roster_payload,
    )


def _merge_response(
    *,
    status: str,
    packet: dict[str, Any],
    current_context: dict[str, Any] | None,
    warnings: list[str],
    current_roster_payload: dict[str, Any],
    needs_identity_confirmation: bool = False,
    current_roster_candidates: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    historical_team = packet.get("historical_team")
    current_team = current_context.get("current_team") if current_context else None
    team_mismatch = bool(historical_team and current_team and historical_team != current_team)
    mismatch_warning = (
        ["Historical team and current roster team differ; preserve both with provenance."]
        if team_mismatch
        else []
    )
    if current_context and _is_free_agent_context(current_context):
        mismatch_warning.append(
            "Current roster source says free agent; historical packet shows prior usage only."
        )

    return _base_response(
        status=status,
        warnings=_dedupe(warnings + mismatch_warning),
        extra={
            "historical_context": packet,
            "current_roster_context": current_context,
            "provenance": _provenance(packet, current_roster_payload),
            "needs_identity_confirmation": needs_identity_confirmation,
            "historical_team": historical_team,
            "current_team": current_team,
            "team_mismatch": team_mismatch,
            "current_roster_status": (
                current_context.get("current_roster_status") if current_context else None
            ),
            "current_roster_source": (
                current_context.get("current_roster_source") if current_context else None
            ),
            "current_roster_as_of": (
                current_context.get("current_roster_as_of") if current_context else None
            ),
            "packet_as_of_season": packet.get("as_of_season"),
            "packet_as_of_week": packet.get("as_of_week"),
            "blocked_metric_policy": BLOCKED_METRIC_POLICY,
            "source_freshness": packet.get("source_freshness"),
            "missing_data_flags": packet.get("missing_data_flags"),
            "blocked_metrics": packet.get("blocked_metrics") or [],
            "packet_warnings": packet.get("warnings") or [],
            "current_roster_candidates": current_roster_candidates or [],
        },
    )


def _base_response(
    *,
    status: str,
    warnings: list[str],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    response = {
        "status": status,
        "historical_source_policy": HISTORICAL_PACKET_SOURCE_POLICY,
        "current_roster_source_policy": CURRENT_ROSTER_SOURCE_POLICY,
        "current_status_policy": CURRENT_ROSTER_DEFERRAL_POLICY,
        "historical_team_naming_rule": HISTORICAL_TEAM_NAMING_RULE,
        "postseason_policy": POSTSEASON_POLICY,
        "warnings": _dedupe(warnings),
    }
    response.update(extra or {})
    return response


def _selected_packet(historical_result: dict[str, Any]) -> dict[str, Any] | None:
    packet = historical_result.get("packet")
    if isinstance(packet, dict):
        return packet
    packets = historical_result.get("packets")
    if isinstance(packets, list) and len(packets) == 1 and isinstance(packets[0], dict):
        return packets[0]
    return None


def _is_ambiguous_packet(historical_result: dict[str, Any]) -> bool:
    return (
        _clean(historical_result.get("status")) == "ambiguous"
        or len(_candidate_list(historical_result)) > 1
    )


def _normalize_current_roster_context(payload: dict[str, Any]) -> dict[str, Any] | None:
    if not payload or payload.get("unavailable"):
        return None
    source = _first(payload, CURRENT_SOURCE_FIELDS) or "current_roster_payload"
    context = {
        "player_id_internal": _clean(payload.get("player_id_internal")),
        "gsis_id": _clean(payload.get("gsis_id")),
        "sleeper_player_id": _clean(payload.get("sleeper_player_id")),
        "display_name": _clean(
            payload.get("display_name") or payload.get("player_name") or payload.get("full_name")
        ),
        "position": _clean(payload.get("position")),
        "current_team": _clean(_first(payload, CURRENT_TEAM_FIELDS)),
        "current_roster_status": _clean(_first(payload, CURRENT_STATUS_FIELDS)),
        "current_roster_source": source,
        "current_roster_as_of": _first(payload, CURRENT_AS_OF_FIELDS),
        "snapshot_id": _clean(payload.get("snapshot_id") or payload.get("snapshot_key")),
        "fantasy_availability": _clean(payload.get("fantasy_availability") or payload.get("availability")),
        "free_agent": bool(payload.get("free_agent")) if payload.get("free_agent") is not None else None,
        "warnings": _as_list(payload.get("warnings")),
    }
    if not any(context.get(field) for field in STABLE_ID_FIELDS + ("display_name", "current_team")):
        return None
    return context


def _identity_status(packet: dict[str, Any], current_context: dict[str, Any] | None) -> str:
    if current_context is None:
        return "missing"
    compared = False
    for field in STABLE_ID_FIELDS:
        packet_value = _clean(packet.get(field))
        current_value = _clean(current_context.get(field))
        if packet_value and current_value:
            compared = True
            if not _stable_id_values_match(field, packet_value, current_value):
                return "mismatch"
    if compared:
        return "match"
    return "weak"


def _stable_id_values_match(field: str, left: str, right: str) -> bool:
    left_values = _stable_id_comparison_values(field, left)
    right_values = _stable_id_comparison_values(field, right)
    return bool(left_values & right_values)


def _stable_id_comparison_values(field: str, value: str) -> set[str]:
    cleaned = _clean(value)
    if not cleaned:
        return set()
    if field != "player_id_internal":
        return {cleaned}
    values = {cleaned}
    if RAW_GSIS_ID_RE.fullmatch(cleaned):
        values.add(f"gsis:{cleaned}")
    elif cleaned.startswith("gsis:"):
        raw_gsis = cleaned.removeprefix("gsis:")
        if RAW_GSIS_ID_RE.fullmatch(raw_gsis):
            values.add(raw_gsis)
    return values


def _provenance(
    packet: dict[str, Any] | None,
    current_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    current_payload = current_payload or {}
    return {
        "historical_source": "compat_pigskin_player_context_current" if packet else None,
        "historical_source_policy": HISTORICAL_PACKET_SOURCE_POLICY,
        "packet_version": packet.get("packet_version") if packet else None,
        "feature_run_id": packet.get("feature_run_id") if packet else None,
        "source_metric_version": packet.get("source_metric_version") if packet else None,
        "packet_as_of_season": packet.get("as_of_season") if packet else None,
        "packet_as_of_week": packet.get("as_of_week") if packet else None,
        "packet_created_at": packet.get("created_at") if packet else None,
        "current_roster_source": _first(current_payload, CURRENT_SOURCE_FIELDS),
        "current_roster_snapshot_id": current_payload.get("snapshot_id")
        or current_payload.get("snapshot_key"),
        "current_roster_as_of": _first(current_payload, CURRENT_AS_OF_FIELDS),
        "merge_policy": MERGE_POLICY,
    }


def _candidate_list(payload: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = payload.get("candidates") if isinstance(payload, dict) else None
    if isinstance(candidates, list):
        return [item for item in candidates if isinstance(item, dict)]
    return []


def _is_free_agent_context(current_context: dict[str, Any]) -> bool:
    status_parts = [
        current_context.get("current_roster_status"),
        current_context.get("fantasy_availability"),
    ]
    if current_context.get("free_agent") is True:
        return True
    return any("free" in str(part).lower() or "available" in str(part).lower() for part in status_parts if part)


def _unsafe_keys(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return []
    return [key for key in value if str(key).lower() in UNSAFE_INPUT_KEYS]


def _strip_current_team(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_current_team(item)
            for key, item in value.items()
            if key != "current_team"
        }
    if isinstance(value, list):
        return [_strip_current_team(item) for item in value]
    return value


def _first(payload: dict[str, Any], fields: tuple[str, ...]) -> Any:
    for field in fields:
        value = payload.get(field)
        if value not in (None, ""):
            return value
    return None


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


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
