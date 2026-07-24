"""Build deterministic public JSON snapshots from canonical ranking rows."""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Iterable, Mapping


SCHEMA_VERSION = "1.2"
SCORING_PROFILES = ("standard", "ppr", "half_ppr", "gng_keeper")
POSITIONS = ("QB", "RB", "WR", "TE")
OVERALL_BOARD_SIZE = 150


def normalize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, Mapping):
        return {str(key): normalize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize_value(item) for item in value]
    return value


def row_dicts(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [normalize_value(dict(row)) for row in rows]


def validate_profile_rows(
    scoring_profile_id: str,
    overall_rows: list[dict[str, Any]],
    positional_rows: list[dict[str, Any]],
) -> None:
    if scoring_profile_id not in SCORING_PROFILES:
        raise ValueError(f"Unsupported scoring profile: {scoring_profile_id}")
    if len(overall_rows) != OVERALL_BOARD_SIZE:
        raise ValueError(
            f"{scoring_profile_id} overall board must contain {OVERALL_BOARD_SIZE} rows; found {len(overall_rows)}"
        )

    overall_ranks = [int(row["overall_rank"]) for row in overall_rows]
    if sorted(overall_ranks) != list(range(1, OVERALL_BOARD_SIZE + 1)):
        raise ValueError(
            f"{scoring_profile_id} overall ranks are not contiguous 1-{OVERALL_BOARD_SIZE}"
        )

    overall_ids = [str(row.get("player_id") or "").strip() for row in overall_rows]
    if any(not player_id for player_id in overall_ids):
        raise ValueError(f"{scoring_profile_id} overall board contains a missing player_id")
    if len(set(overall_ids)) != OVERALL_BOARD_SIZE:
        raise ValueError(f"{scoring_profile_id} overall board contains duplicate player_id values")
    teamless_overall = [
        str(row.get("player_name") or row.get("player_id") or "unknown")
        for row in overall_rows
        if row.get("current_board_rank_eligible") is False
        or not str(row.get("current_team") or "").strip()
    ]
    if teamless_overall:
        raise ValueError(
            f"{scoring_profile_id} overall board contains teamless players: "
            + ", ".join(teamless_overall)
        )

    board_versions = {str(row.get("board_version") or "").strip() for row in overall_rows}
    if len(board_versions) != 1 or "" in board_versions:
        raise ValueError(f"{scoring_profile_id} overall board must have one non-empty board_version")

    position_groups: dict[str, list[dict[str, Any]]] = {position: [] for position in POSITIONS}
    seen_keys: set[tuple[str, str]] = set()
    for row in positional_rows:
        position = str(row.get("position") or "").upper()
        player_id = str(row.get("player_id") or "").strip()
        if position not in position_groups:
            raise ValueError(f"{scoring_profile_id} contains unsupported position {position!r}")
        if not player_id:
            raise ValueError(f"{scoring_profile_id} {position} board contains a missing player_id")
        if row.get("current_board_rank_eligible") is False or not str(
            row.get("current_team") or ""
        ).strip():
            raise ValueError(
                f"{scoring_profile_id} {position} board contains teamless player "
                f"{row.get('player_name') or player_id}"
            )
        key = (position, player_id)
        if key in seen_keys:
            raise ValueError(f"{scoring_profile_id} contains duplicate active positional row {key}")
        seen_keys.add(key)
        position_groups[position].append(row)

    for position, rows in position_groups.items():
        if not rows:
            raise ValueError(f"{scoring_profile_id} is missing the active {position} board")
        ranks = sorted(int(row["rank"]) for row in rows)
        if ranks != list(range(1, len(rows) + 1)):
            raise ValueError(f"{scoring_profile_id} {position} ranks are not contiguous")

    missing_rationale = [
        str(row.get("player_name") or row.get("player_id") or "unknown")
        for row in positional_rows
        if not str(row.get("rank_rationale") or "").strip()
    ]
    if missing_rationale:
        raise ValueError(
            f"{scoring_profile_id} positional rows are missing scientific rank rationale: "
            + ", ".join(missing_rationale)
        )

    if scoring_profile_id == "gng_keeper":
        missing_context = [
            str(row.get("player_name") or row.get("player_id") or "unknown")
            for row in positional_rows
            if not str(row.get("ranking_context") or "").strip()
        ]
        if missing_context:
            raise ValueError(
                "gng_keeper positional rows are missing GNG context: "
                + ", ".join(missing_context)
            )
        oversized_context = [
            str(row.get("player_name") or row.get("player_id") or "unknown")
            for row in positional_rows
            if len(str(row.get("ranking_context") or "")) > 320
        ]
        if oversized_context:
            raise ValueError(
                "gng_keeper positional rows exceed the 320-character context limit: "
                + ", ".join(oversized_context)
            )


def _unique_values(rows: list[dict[str, Any]], key: str) -> list[Any]:
    values = {row.get(key) for row in rows if row.get(key) not in (None, "")}
    return sorted(values, key=str)


def _position_formula(
    position: str,
    positional_rows: list[dict[str, Any]],
    overall_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    position_rows = [row for row in positional_rows if row["position"] == position]
    overall_position_rows = [row for row in overall_rows if row["position"] == position]
    return {
        "ranking_versions": _unique_values(position_rows, "ranking_version"),
        "rank_sources": _unique_values(position_rows, "rank_source"),
        "model_names": _unique_values(position_rows, "model_name"),
        "prompt_versions": _unique_values(position_rows, "prompt_version"),
        "unified_source_versions": _unique_values(overall_position_rows, "position_source_version"),
        "unified_rank_sources": _unique_values(overall_position_rows, "position_rank_source"),
    }


def _public_positional_player(
    row: dict[str, Any], *, include_gng_context: bool = False
) -> dict[str, Any]:
    player = {
        "rank": int(row["rank"]),
        "player_id": row["player_id"],
        "player_name": row["player_name"],
        "team": row.get("current_team"),
        "position": row["position"],
        "tier": row.get("tier"),
        "pigskin_score": row.get("ranking_score"),
        "confidence_score": row.get("confidence_score"),
        "pigskin_verdict": row.get("pigskin_verdict"),
        "rank_rationale": row.get("rank_rationale"),
        "risk_flags": row.get("risk_flags"),
        "what_would_change_mind": row.get("what_would_change_mind"),
        "roster_status": row.get("roster_status"),
        "ranking_eligibility": row.get("ranking_eligibility"),
        "adjustment": {
            "code": row.get("llm_adjustment_code"),
            "detail": row.get("llm_adjustment_detail"),
            "rank_delta": row.get("llm_rank_delta"),
        },
    }
    if include_gng_context:
        player["context"] = row["ranking_context"]
    return player


def build_profile_payload(
    *,
    project_id: str,
    dataset_id: str,
    scoring_profile_id: str,
    overall_rows: Iterable[Mapping[str, Any]],
    positional_rows: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    overall = row_dicts(overall_rows)
    positional = row_dicts(positional_rows)
    for row in overall:
        row["position"] = str(row["position"]).upper()
    for row in positional:
        row["position"] = str(row["position"]).upper()

    validate_profile_rows(scoring_profile_id, overall, positional)
    overall.sort(key=lambda row: int(row["overall_rank"]))
    positional.sort(key=lambda row: (POSITIONS.index(row["position"]), int(row["rank"])))
    positional_by_player = {
        (row["position"], str(row["player_id"])): row for row in positional
    }

    overall_players = []
    for row in overall:
        context = positional_by_player.get((row["position"], str(row["player_id"])))
        player = {
            "overall_rank": int(row["overall_rank"]),
            "player_id": row["player_id"],
            "player_name": row["player_name"],
            "team": row.get("current_team"),
            "position": row["position"],
            "position_rank": int(row["position_rank"]),
            "positional_context_status": "current" if context is not None else "missing",
            "tier": context.get("tier") if context else None,
            "pigskin_score": context.get("ranking_score") if context else None,
            "pigskin_verdict": context.get("pigskin_verdict") if context else None,
            "rank_rationale": context.get("rank_rationale") if context else None,
            "risk_flags": row.get("risk_flags")
            or (context.get("risk_flags") if context else None),
            "projected_ppg": row.get("projected_ppg"),
            "vorp": row.get("vorp"),
            "adjusted_vorp": row.get("adjusted_vorp"),
            "adjustment": {
                "code": context.get("llm_adjustment_code") if context else None,
                "detail": context.get("llm_adjustment_detail") if context else None,
                "rank_delta": context.get("llm_rank_delta") if context else None,
            },
        }
        if scoring_profile_id == "gng_keeper":
            player["context"] = context.get("ranking_context") if context else None
        overall_players.append(player)

    generated_values = _unique_values(overall + positional, "generated_at")
    position_payloads = {}
    for position in POSITIONS:
        players = [
            _public_positional_player(
                row,
                include_gng_context=scoring_profile_id == "gng_keeper",
            )
            for row in positional
            if row["position"] == position
        ]
        position_payloads[position] = {"count": len(players), "players": players}

    missing_context = [
        {
            "overall_rank": player["overall_rank"],
            "player_id": player["player_id"],
            "player_name": player["player_name"],
            "position": player["position"],
        }
        for player in overall_players
        if player["positional_context_status"] == "missing"
    ]
    warnings = []
    if missing_context:
        warnings.append(
            {
                "code": "missing_active_positional_context",
                "count": len(missing_context),
                "players": missing_context,
            }
        )

    source = {
        "project_id": project_id,
        "dataset_id": dataset_id,
        "overall_table": "unified_draft_rankings_current",
        "positional_table": "analytics_pigskin_rankings",
    }
    if scoring_profile_id == "gng_keeper":
        source["context_table"] = (
            "fantasy_football_advanced_metrics.gng_2026_rank_context"
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "scoring_profile_id": scoring_profile_id,
        "board_version": overall[0]["board_version"],
        "source_generated_at": max(generated_values) if generated_values else None,
        "source": source,
        "formulas": {
            position: _position_formula(position, positional, overall) for position in POSITIONS
        },
        "warnings": warnings,
        "overall": {"count": len(overall_players), "players": overall_players},
        "positions": position_payloads,
    }


def json_bytes(payload: Mapping[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
