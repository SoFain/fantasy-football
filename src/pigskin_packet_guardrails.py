"""Guardrails for future Pigskin historical packet tool exposure."""

from __future__ import annotations

import copy
import os
from typing import Any

from src import pigskin_packet_retrieval


HISTORICAL_PACKET_TOOL_ENV = "USE_PIGSKIN_HISTORICAL_PACKET_TOOL"

HISTORICAL_PACKET_SOURCE_POLICY = "historical_nflverse_packet_context_only"
CURRENT_ROSTER_DEFERRAL_POLICY = (
    "Current roster/free-agent status must come from Sleeper/current roster source."
)
HISTORICAL_TEAM_NAMING_RULE = (
    "Packet team is historical_team. It is never current_team."
)
COMPACT_NAME_AMBIGUITY_RULE = (
    "Compact display-name collisions must return candidates, not a selected player."
)
BLOCKED_METRIC_POLICY = "Blocked metrics are unavailable, not zero."
POSTSEASON_POLICY = (
    "Week 22 is postseason/historical context and is excluded unless include_postseason is true."
)

PIGSKIN_HISTORICAL_PACKET_PROMPT_GUARDRAIL = """

    ### Historical nflverse Packet Guardrail ###
    Historical nflverse packet context is completed-season evidence only.
    It does not answer current roster, free-agent, dynasty availability, injury/status, or current-team questions.
    For 2026-facing roster/status questions, use Sleeper/current roster source.
    If historical nflverse packet context is provided, label the packet season and week.
    Treat packet team as historical team. Never describe packet team as current team.
    If historical team and current roster team differ, state both with provenance.
    If current roster source says free agent, say the packet shows prior historical usage only.
    If player lookup is ambiguous, require player ID, team, or position before taking a data-backed position.
    Blocked metrics are unavailable, not zero.
    Week 22 is postseason/historical and should be excluded from regular-season fantasy analysis unless explicitly requested.
    Do not call historical packet lookup unless a future enabled tool is present in the provided tool list.
"""

SAFE_HISTORICAL_PACKET_TOOL_DESCRIPTION = (
    "Load bounded historical nflverse Pigskin packet context as completed-season "
    "evidence only. Requires explicit season or season_start/season_end. Returns "
    "historical_team, source freshness, missing-data flags, unavailable blocked "
    "metrics, and ambiguity candidates. Does not answer current roster, "
    "free-agent, or current-team status."
)

REQUEST_BLOCKED_REASONS = {
    "missing_historical_window": "season or season_start/season_end is required",
    "missing_current_roster_identity": (
        "player_id_internal or player_name is required for current roster identity"
    ),
    "arbitrary_sql_not_allowed": "arbitrary SQL is not accepted by this wrapper",
}

ALLOWED_TOOL_ARGS = {
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
}


def historical_packet_tool_enabled() -> bool:
    """Return whether the future model-visible historical packet tool is enabled."""

    return os.environ.get(HISTORICAL_PACKET_TOOL_ENV, "").strip().lower() == "true"


def get_historical_packet_tool_declarations(*, enabled: bool | None = None) -> list[dict[str, Any]]:
    """Return the future tool declaration only when explicitly enabled by caller."""

    if enabled is None:
        enabled = historical_packet_tool_enabled()
    if not enabled:
        return []
    return [
        {
            "name": "get_historical_pigskin_packet_context",
            "description": SAFE_HISTORICAL_PACKET_TOOL_DESCRIPTION,
            "parameters": {
                "type": "object",
                "properties": {
                    "season": {"type": "integer"},
                    "season_start": {"type": "integer"},
                    "season_end": {"type": "integer"},
                    "week": {"type": "integer"},
                    "include_postseason": {"type": "boolean"},
                    "player_id_internal": {"type": "string"},
                    "player_name": {"type": "string"},
                    "team": {"type": "string"},
                    "position": {"type": "string"},
                    "scoring_profile_id": {"type": "string"},
                    "league_type_id": {"type": "string"},
                    "roster_format_id": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "anyOf": [
                    {"required": ["season"]},
                    {"required": ["season_start", "season_end"]},
                ],
                "oneOf": [
                    {"required": ["player_id_internal"]},
                    {"required": ["player_name"]},
                ],
            },
        }
    ]


def execute_historical_packet_context_lookup(
    args: dict[str, Any] | None,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    """Map future tool args to safe retrieval without making the tool visible."""

    args = dict(args or {})
    unsafe_keys = sorted(key for key in args if key not in ALLOWED_TOOL_ARGS)
    sql_keys = sorted(key for key in unsafe_keys if "sql" in key.lower())
    if sql_keys:
        return _blocked_response("arbitrary_sql_not_allowed", unsafe_keys=unsafe_keys)
    if not _has_historical_window(args):
        return _blocked_response("missing_historical_window", unsafe_keys=unsafe_keys)
    if not _has_current_roster_identity(args):
        return _blocked_response("missing_current_roster_identity", unsafe_keys=unsafe_keys)

    safe_args = {key: value for key, value in args.items() if key in ALLOWED_TOOL_ARGS}
    from src import pigskin_context_qa

    current_roster_request = _current_roster_request_from_tool_args(safe_args)
    result = pigskin_context_qa.build_historical_packet_current_roster_context(
        safe_args,
        current_roster_request,
        client=client,
        dataset_id=dataset_id,
    )
    guarded = enforce_historical_packet_result_guardrails(result)
    if unsafe_keys:
        warnings = guarded.setdefault("warnings", [])
        warnings.append(f"Ignored unsupported args: {', '.join(unsafe_keys)}")
    return guarded


def enforce_historical_packet_result_guardrails(result: dict[str, Any]) -> dict[str, Any]:
    """Apply output policy so historical packet results cannot masquerade as current state."""

    guarded = _remove_packet_current_team(copy.deepcopy(result))
    guarded["source_policy"] = HISTORICAL_PACKET_SOURCE_POLICY
    guarded["historical_context_only"] = True
    guarded["current_roster_status_source_required"] = True
    guarded["current_roster_status_policy"] = CURRENT_ROSTER_DEFERRAL_POLICY
    guarded["historical_team_naming_rule"] = HISTORICAL_TEAM_NAMING_RULE
    guarded["blocked_metric_policy"] = BLOCKED_METRIC_POLICY
    warnings = guarded.setdefault("warnings", [])
    for warning in [
        "Historical nflverse packet context only.",
        CURRENT_ROSTER_DEFERRAL_POLICY,
        HISTORICAL_TEAM_NAMING_RULE,
    ]:
        if warning not in warnings:
            warnings.append(warning)
    return guarded


def _has_historical_window(args: dict[str, Any]) -> bool:
    if args.get("season") not in (None, ""):
        return True
    return args.get("season_start") not in (None, "") and args.get("season_end") not in (None, "")


def _has_current_roster_identity(args: dict[str, Any]) -> bool:
    return args.get("player_id_internal") not in (None, "") or args.get("player_name") not in (
        None,
        "",
    )


def _current_roster_request_from_tool_args(args: dict[str, Any]) -> dict[str, Any]:
    request: dict[str, Any] = {}
    for key in ("player_id_internal", "player_name", "limit"):
        if args.get(key) not in (None, ""):
            request[key] = args[key]
    if request.get("player_name") and not request.get("player_id_internal") and not request.get("limit"):
        request["limit"] = 5
    return request


def _blocked_response(reason: str, *, unsafe_keys: list[str] | None = None) -> dict[str, Any]:
    return enforce_historical_packet_result_guardrails(
        {
            "status": "validation_error",
            "found": False,
            "error": REQUEST_BLOCKED_REASONS[reason],
            "blocked_reason": reason,
            "unsafe_args": unsafe_keys or [],
            "source": pigskin_packet_retrieval.SOURCE_VIEW,
            "warnings": [REQUEST_BLOCKED_REASONS[reason]],
        }
    )


def _remove_packet_current_team(value: dict[str, Any]) -> dict[str, Any]:
    for key in ("packet", "packets", "candidates", "historical_candidates"):
        if key in value:
            value[key] = _remove_current_team(value[key])
    packet_result = value.get("packet_result")
    if isinstance(packet_result, dict):
        value["packet_result"] = _remove_current_team(packet_result)
    merged_context = value.get("merged_context")
    if isinstance(merged_context, dict) and "historical_context" in merged_context:
        merged_context["historical_context"] = _remove_current_team(
            merged_context["historical_context"]
        )
    return value


def _remove_current_team(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _remove_current_team(item)
            for key, item in value.items()
            if key != "current_team"
        }
    if isinstance(value, list):
        return [_remove_current_team(item) for item in value]
    return value
