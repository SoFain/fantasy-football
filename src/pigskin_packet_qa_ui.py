"""Read-only helpers for the Pigskin packet/current roster QA UI."""

from __future__ import annotations

from typing import Any

from src.pigskin_context_qa import build_historical_packet_current_roster_context


UNSAFE_QA_INPUT_KEYS = {"sql", "query", "sql_query", "raw_sql"}
PACKET_REQUEST_FIELDS = (
    "season",
    "season_start",
    "season_end",
    "week",
    "include_postseason",
    "player_id_internal",
    "player_name",
    "team",
    "position",
    "scoring_profile_id",
    "league_type_id",
    "roster_format_id",
    "limit",
)
CURRENT_ROSTER_REQUEST_FIELDS = (
    "player_id_internal",
    "sleeper_player_id",
    "gsis_id",
    "player_name",
    "league_id",
    "include_available_players",
    "limit",
)


def pigskin_packet_qa_ui_policy() -> str:
    return (
        "Read-only QA only. Historical packet team is historical_team, not current_team. "
        "Current roster status must come from approved current roster sources."
    )


def build_pigskin_packet_qa_requests(form_values: dict[str, Any]) -> dict[str, Any]:
    """Split form values into bounded packet and current-roster requests."""

    unsafe_keys = sorted(key for key in form_values if key.lower() in UNSAFE_QA_INPUT_KEYS)
    if unsafe_keys:
        return {
            "status": "validation_error",
            "blocked_reason": "arbitrary_sql_not_allowed",
            "error": "Arbitrary SQL/query input is not accepted by Pigskin packet QA UI.",
            "unsafe_args": unsafe_keys,
            "packet_request": {},
            "current_roster_request": {},
        }

    packet_request = {
        key: _clean_value(form_values.get(key))
        for key in PACKET_REQUEST_FIELDS
        if _clean_value(form_values.get(key)) is not None
    }
    current_roster_request = {
        key: _clean_value(form_values.get(key))
        for key in CURRENT_ROSTER_REQUEST_FIELDS
        if _clean_value(form_values.get(key)) is not None
    }
    return {
        "status": "ok",
        "packet_request": packet_request,
        "current_roster_request": current_roster_request,
    }


def run_pigskin_packet_qa_lookup(
    form_values: dict[str, Any],
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    """Run the deterministic QA helper and return a display summary."""

    request_result = build_pigskin_packet_qa_requests(form_values)
    if request_result["status"] != "ok":
        return summarize_pigskin_packet_qa_result(request_result)

    result = build_historical_packet_current_roster_context(
        request_result["packet_request"],
        request_result["current_roster_request"],
        client=client,
        dataset_id=dataset_id,
    )
    return summarize_pigskin_packet_qa_result(result)


def summarize_pigskin_packet_qa_result(result: dict[str, Any]) -> dict[str, Any]:
    """Flatten the QA result into fields the Streamlit panel can render safely."""

    merged = _dict_or_empty(result.get("merged_context"))
    historical = _dict_or_empty(merged.get("historical_context"))
    current = _dict_or_empty(merged.get("current_roster_context"))
    packet_result = _dict_or_empty(result.get("packet_result"))
    current_result = _dict_or_empty(result.get("current_roster_result"))
    selected_packet = _dict_or_empty(packet_result.get("packet"))

    historical_team = result.get("historical_team") or merged.get("historical_team") or historical.get("historical_team")
    current_team = result.get("current_team") or merged.get("current_team") or current.get("current_team")
    warnings = _dedupe(
        _as_list(result.get("warnings"))
        + _as_list(packet_result.get("warnings"))
        + _as_list(current_result.get("warnings"))
        + _as_list(merged.get("warnings"))
    )
    blocked_metrics = (
        result.get("blocked_metrics")
        or merged.get("blocked_metrics")
        or historical.get("blocked_metrics")
        or selected_packet.get("blocked_metrics")
        or []
    )

    return {
        "status": result.get("status") or "unknown",
        "blocked_reason": result.get("blocked_reason"),
        "historical_team": historical_team,
        "current_team": current_team,
        "current_roster_status": result.get("current_roster_status") or merged.get("current_roster_status") or current.get("current_roster_status"),
        "current_roster_source": result.get("current_roster_source") or merged.get("current_roster_source") or current.get("source"),
        "current_roster_as_of": result.get("current_roster_as_of") or merged.get("current_roster_as_of") or current.get("as_of"),
        "packet_season": result.get("packet_as_of_season") or merged.get("packet_as_of_season") or historical.get("as_of_season") or selected_packet.get("as_of_season"),
        "packet_week": result.get("packet_as_of_week") or merged.get("packet_as_of_week") or historical.get("as_of_week") or selected_packet.get("as_of_week"),
        "warnings": warnings,
        "historical_candidates": result.get("historical_candidates") or packet_result.get("candidates") or [],
        "current_roster_candidates": result.get("current_roster_candidates") or current_result.get("candidates") or [],
        "blocked_metrics": blocked_metrics,
        "blocked_metric_policy": result.get("blocked_metric_policy") or merged.get("blocked_metric_policy") or historical.get("blocked_metric_policy") or "Blocked metrics are unavailable, not zero.",
        "source_freshness": result.get("source_freshness") or merged.get("source_freshness") or historical.get("source_freshness"),
        "missing_data_flags": result.get("missing_data_flags") or merged.get("missing_data_flags") or historical.get("missing_data_flags"),
        "identity_diagnostics": result.get("identity_diagnostics") or merged.get("identity_diagnostics"),
        "safe_wording": pigskin_packet_qa_ui_policy(),
        "raw_result": result,
    }


def _clean_value(value: Any) -> Any | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return value if value not in (None, "") else None


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _dedupe(values: list[Any]) -> list[Any]:
    seen: set[str] = set()
    output: list[Any] = []
    for value in values:
        key = str(value)
        if key not in seen:
            seen.add(key)
            output.append(value)
    return output
