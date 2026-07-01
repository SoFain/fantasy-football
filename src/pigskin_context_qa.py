"""Internal QA orchestration for Pigskin packet/current roster merge checks."""

from __future__ import annotations

import copy
from typing import Any

from src.pigskin_current_roster_lookup import lookup_current_roster_context
from src.pigskin_current_roster_merge import merge_historical_packet_with_current_roster
from src.pigskin_packet_retrieval import retrieve_historical_pigskin_packets


SOURCE = "pigskin_lookup_merge_qa"
SOURCE_POLICY = "internal_read_only_lookup_merge_qa_only"
UNSAFE_INPUT_KEYS = {"sql", "query", "sql_query", "raw_sql"}
CURRENT_ROSTER_IDENTITY_FIELDS = ("player_id_internal", "sleeper_player_id", "gsis_id", "player_name")
QA_POLICY = (
    "Historical packet evidence and current roster state are retrieved through "
    "separate bounded helpers, then merged only after both identities are deterministic."
)


def build_historical_packet_current_roster_context(
    packet_request: dict[str, Any] | None,
    current_roster_request: dict[str, Any] | None,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    """Return one read-only QA context from historical packet and current roster helpers."""

    packet_request_result = _as_request_dict(packet_request, "packet_request")
    if packet_request_result["status"] != "ok":
        return packet_request_result
    roster_request_result = _as_request_dict(current_roster_request, "current_roster_request")
    if roster_request_result["status"] != "ok":
        return roster_request_result

    safe_packet_request = packet_request_result["request"]
    safe_roster_request = roster_request_result["request"]
    unsafe_keys = _unsafe_keys(safe_packet_request, "packet_request") + _unsafe_keys(
        safe_roster_request,
        "current_roster_request",
    )
    if unsafe_keys:
        return _validation_error(
            "Arbitrary SQL/query input is not accepted by lookup merge QA.",
            blocked_reason="arbitrary_sql_not_allowed",
            unsafe_args=_dedupe(unsafe_keys),
            packet_request=safe_packet_request,
            current_roster_request=safe_roster_request,
        )

    if not _has_historical_window(safe_packet_request):
        return _validation_error(
            "Historical packet request requires explicit season or season_start/season_end.",
            blocked_reason="missing_historical_season_window",
            packet_request=safe_packet_request,
            current_roster_request=safe_roster_request,
        )

    if not _has_current_roster_identity(safe_roster_request):
        return _validation_error(
            "Current roster request requires bounded identity input.",
            blocked_reason="missing_current_roster_identity",
            packet_request=safe_packet_request,
            current_roster_request=safe_roster_request,
        )

    packet_result = retrieve_historical_pigskin_packets(
        client=client,
        dataset_id=dataset_id,
        **safe_packet_request,
    )
    packet_block = _packet_block_reason(packet_result)
    if packet_block:
        return _blocked_response(
            status="needs_identity_confirmation"
            if packet_block in {"packet_ambiguous", "historical_packet_not_deterministic"}
            else packet_result.get("status") or "historical_packet_unavailable",
            blocked_reason=packet_block,
            packet_result=packet_result,
            current_roster_result=None,
            packet_request=safe_packet_request,
            current_roster_request=safe_roster_request,
        )

    current_result = lookup_current_roster_context(
        client=client,
        dataset_id=dataset_id,
        **safe_roster_request,
    )
    current_block = _current_roster_block_reason(current_result)
    if current_block:
        return _blocked_response(
            status="needs_identity_confirmation"
            if current_block == "current_roster_ambiguous"
            else current_result.get("status") or "current_roster_unavailable",
            blocked_reason=current_block,
            packet_result=packet_result,
            current_roster_result=current_result,
            packet_request=safe_packet_request,
            current_roster_request=safe_roster_request,
        )

    current_payload = current_result.get("current_roster_context")
    if current_result.get("status") == "not_found":
        current_payload = {
            "unavailable": True,
            "source": current_result.get("source"),
            "warnings": current_result.get("warnings") or [],
        }

    merged_context = merge_historical_packet_with_current_roster(packet_result, current_payload)
    warnings = _dedupe(
        [QA_POLICY]
        + _as_list(packet_result.get("warnings"))
        + _as_list(current_result.get("warnings"))
        + _as_list(merged_context.get("warnings"))
    )

    return {
        "status": merged_context.get("status") or "unknown",
        "found": bool(merged_context.get("historical_context")),
        "source": SOURCE,
        "source_policy": SOURCE_POLICY,
        "qa_policy": QA_POLICY,
        "warnings": warnings,
        "merge_blocked": False,
        "blocked_reason": None,
        "packet_request": copy.deepcopy(safe_packet_request),
        "current_roster_request": copy.deepcopy(safe_roster_request),
        "packet_result": packet_result,
        "current_roster_result": current_result,
        "merged_context": merged_context,
        "historical_team": merged_context.get("historical_team"),
        "current_team": merged_context.get("current_team"),
        "current_roster_status": merged_context.get("current_roster_status"),
        "current_roster_source": merged_context.get("current_roster_source"),
        "current_roster_as_of": merged_context.get("current_roster_as_of"),
        "team_mismatch": merged_context.get("team_mismatch"),
        "packet_as_of_season": merged_context.get("packet_as_of_season"),
        "packet_as_of_week": merged_context.get("packet_as_of_week"),
        "source_freshness": merged_context.get("source_freshness"),
        "missing_data_flags": merged_context.get("missing_data_flags"),
        "blocked_metrics": merged_context.get("blocked_metrics") or [],
        "provenance": merged_context.get("provenance") or {},
    }


def _as_request_dict(value: dict[str, Any] | None, name: str) -> dict[str, Any]:
    if value is None:
        return {"status": "ok", "request": {}}
    if not isinstance(value, dict):
        return _validation_error(
            f"{name} must be a mapping.",
            blocked_reason="invalid_request_type",
            packet_request=value if name == "packet_request" else None,
            current_roster_request=value if name == "current_roster_request" else None,
        )
    return {"status": "ok", "request": copy.deepcopy(value)}


def _validation_error(
    error: str,
    *,
    blocked_reason: str,
    packet_request: Any = None,
    current_roster_request: Any = None,
    unsafe_args: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "status": "validation_error",
        "found": False,
        "source": SOURCE,
        "source_policy": SOURCE_POLICY,
        "qa_policy": QA_POLICY,
        "warnings": [QA_POLICY, error],
        "error": error,
        "merge_blocked": True,
        "blocked_reason": blocked_reason,
        "unsafe_args": unsafe_args or [],
        "packet_request": copy.deepcopy(packet_request),
        "current_roster_request": copy.deepcopy(current_roster_request),
        "packet_result": None,
        "current_roster_result": None,
        "merged_context": None,
    }


def _blocked_response(
    *,
    status: str,
    blocked_reason: str,
    packet_result: dict[str, Any] | None,
    current_roster_result: dict[str, Any] | None,
    packet_request: dict[str, Any],
    current_roster_request: dict[str, Any],
) -> dict[str, Any]:
    warnings = _dedupe(
        [QA_POLICY]
        + _as_list((packet_result or {}).get("warnings"))
        + _as_list((current_roster_result or {}).get("warnings"))
        + [f"Lookup merge QA blocked before merge: {blocked_reason}."]
    )
    return {
        "status": status,
        "found": False,
        "source": SOURCE,
        "source_policy": SOURCE_POLICY,
        "qa_policy": QA_POLICY,
        "warnings": warnings,
        "merge_blocked": True,
        "blocked_reason": blocked_reason,
        "packet_request": copy.deepcopy(packet_request),
        "current_roster_request": copy.deepcopy(current_roster_request),
        "packet_result": packet_result,
        "current_roster_result": current_roster_result,
        "merged_context": None,
        "historical_candidates": _candidate_list(packet_result),
        "current_roster_candidates": _candidate_list(current_roster_result),
    }


def _packet_block_reason(packet_result: dict[str, Any]) -> str | None:
    status = _clean(packet_result.get("status"))
    if status == "ambiguous" or packet_result.get("needs_identity_confirmation"):
        return "packet_ambiguous"
    if status != "ok":
        return "historical_packet_unavailable"
    if _selected_packet(packet_result) is None:
        return "historical_packet_not_deterministic"
    return None


def _current_roster_block_reason(current_result: dict[str, Any]) -> str | None:
    status = _clean(current_result.get("status"))
    if status == "ambiguous" or current_result.get("needs_identity_confirmation"):
        return "current_roster_ambiguous"
    if status in {"validation_error", "query_error"}:
        return "current_roster_lookup_failed"
    if status in {"ok", "not_found"}:
        return None
    return "current_roster_unavailable"


def _selected_packet(packet_result: dict[str, Any]) -> dict[str, Any] | None:
    packet = packet_result.get("packet")
    if isinstance(packet, dict):
        return packet
    packets = packet_result.get("packets")
    if isinstance(packets, list) and len(packets) == 1 and isinstance(packets[0], dict):
        return packets[0]
    return None


def _has_historical_window(packet_request: dict[str, Any]) -> bool:
    if _present(packet_request.get("season")):
        return True
    return _present(packet_request.get("season_start")) and _present(packet_request.get("season_end"))


def _has_current_roster_identity(current_roster_request: dict[str, Any]) -> bool:
    return any(_present(current_roster_request.get(field)) for field in CURRENT_ROSTER_IDENTITY_FIELDS)


def _unsafe_keys(value: Any, prefix: str) -> list[str]:
    if not isinstance(value, dict):
        return []
    unsafe: list[str] = []
    for key, item in value.items():
        path = f"{prefix}.{key}"
        if str(key).lower() in UNSAFE_INPUT_KEYS:
            unsafe.append(path)
        if isinstance(item, dict):
            unsafe.extend(_unsafe_keys(item, path))
    return unsafe


def _candidate_list(payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    candidates = payload.get("candidates") if isinstance(payload, dict) else None
    if isinstance(candidates, list):
        return [item for item in candidates if isinstance(item, dict)]
    return []


def _present(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip().lower()
    return cleaned or None


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


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
