"""Deterministic trade review packet builder."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.build_player_identity import normalize_player_name
from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_SCORING_PROFILE = "ppr"
DEFAULT_LEAGUE_TYPE = "redraft"
DEFAULT_ROSTER_FORMAT = "one_qb"
MAX_ASSETS_PER_SIDE = 8
PACKET_TEXT_MAX_CHARS = 12000
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("TRADE_REVIEW_MAX_BYTES_BILLED", "1000000000"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")

TRADE_VALUE_CONFIG: dict[str, Any] = {
    "version": "trade_review_baseline_v1",
    "market_weight": 0.58,
    "rank_weight": 0.18,
    "recent_weight": 0.14,
    "role_weight": 0.05,
    "risk_weight": 45.0,
    "rank_anchor_value": 24000.0,
    "recent_points_multiplier": 165.0,
    "tie_delta_fraction": 0.025,
    "superflex_qb_multiplier": 1.22,
    "best_ball_wr_te_multiplier": 1.05,
    "dynasty_age_weight": 0.16,
    "redraft_age_weight": 0.03,
}

PACKET_KEYS = (
    "trade_summary",
    "verdict",
    "side_a_evidence",
    "side_b_evidence",
    "player_evidence",
    "roster_context",
    "counterarguments",
    "show_framing",
    "metadata",
)


class UnknownTradeAssetError(ValueError):
    """Raised when one or more requested trade assets cannot be resolved."""

    def __init__(self, unknown_assets: list[str]):
        self.unknown_assets = unknown_assets
        super().__init__(f"Unknown trade asset(s): {', '.join(unknown_assets)}")


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def normalize_trade_side(assets: Any) -> list[dict[str, str]]:
    """Normalize user-entered assets into lookup dictionaries."""

    if isinstance(assets, str):
        raw_assets: list[Any] = [item.strip() for item in assets.split(",")]
    elif assets is None:
        raw_assets = []
    else:
        raw_assets = list(assets)

    normalized: list[dict[str, str]] = []
    for asset in raw_assets:
        if isinstance(asset, dict):
            lookup = (
                asset.get("lookup")
                or asset.get("player_id_internal")
                or asset.get("source_player_key")
                or asset.get("sleeper_player_id")
                or asset.get("display_name")
                or asset.get("player_name")
            )
            label = asset.get("label") or asset.get("display_name") or asset.get("player_name") or lookup
        else:
            lookup = asset
            label = asset

        lookup_text = str(lookup or "").strip()
        if lookup_text:
            normalized.append({
                "lookup": lookup_text,
                "label": str(label or lookup_text).strip(),
                "normalized_lookup": normalize_player_name(lookup_text),
            })

    if len(normalized) > MAX_ASSETS_PER_SIDE:
        raise ValueError(f"Trade review supports at most {MAX_ASSETS_PER_SIDE} assets per side")
    return normalized


def resolve_trade_assets(
    assets: Any,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Resolve trade assets from curated compatibility objects."""

    normalized_assets = normalize_trade_side(assets)
    if not normalized_assets:
        return []

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_resolve_trade_assets_query(
        project_id=client.project,
        dataset_id=dataset_id,
        lookups=[asset["lookup"] for asset in normalized_assets],
        normalized_lookups=[asset["normalized_lookup"] for asset in normalized_assets],
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    rows = [_row_to_dict(row) for row in client.query(sql, job_config=job_config).result()]
    resolved: list[dict[str, Any]] = []
    unknown: list[str] = []
    used_keys: set[str] = set()

    for requested in normalized_assets:
        match = _best_match_for_lookup(rows, requested["lookup"], requested["normalized_lookup"], used_keys)
        if not match:
            unknown.append(requested["lookup"])
            continue
        match["requested_lookup"] = requested["lookup"]
        resolved.append(match)
        used_keys.add(_asset_dedupe_key(match))

    if unknown:
        raise UnknownTradeAssetError(unknown)
    return resolved


def build_resolve_trade_assets_query(
    *,
    project_id: str,
    dataset_id: str,
    lookups: list[str],
    normalized_lookups: list[str],
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
) -> tuple[str, bigquery.QueryJobConfig]:
    lower_lookups = [lookup.lower() for lookup in lookups]
    sql = f"""
    WITH profile_latest AS (
        SELECT * EXCEPT(rn)
        FROM (
            SELECT
                player_id_internal,
                source_player_key,
                sleeper_player_id,
                normalized_name,
                age AS profile_age,
                role_summary_json,
                epa_summary_json,
                pigskin_summary,
                prospect_summary_json,
                source_freshness_json AS profile_source_freshness_json,
                missing_data_flags AS profile_missing_data_flags,
                ROW_NUMBER() OVER(
                    PARTITION BY COALESCE(player_id_internal, source_player_key, sleeper_player_id, normalized_name), scoring_profile_id
                    ORDER BY as_of_season DESC, as_of_week DESC, refreshed_at DESC
                ) AS rn
            FROM `{_table_id(project_id, dataset_id, "compat_player_profiles_current")}`
            WHERE scoring_profile_id = @scoring_profile_id
        )
        WHERE rn = 1
    ),
    history_recent AS (
        SELECT
            player_id_internal,
            source_player_key,
            normalized_name,
            scoring_profile_id,
            AVG(total_fantasy_points) AS history_recent_points_per_game,
            AVG(target_share) AS history_target_share,
            AVG(rush_share) AS history_rush_share,
            AVG(high_value_touches) AS history_high_value_touches,
            ANY_VALUE(source_freshness_json) AS history_source_freshness_json,
            ANY_VALUE(missing_data_flags) AS history_missing_data_flags
        FROM `{_table_id(project_id, dataset_id, "compat_trade_player_history")}`
        WHERE scoring_profile_id = @scoring_profile_id
            AND recency_order <= 8
        GROUP BY player_id_internal, source_player_key, normalized_name, scoring_profile_id
    )
    SELECT
        ta.player_id_internal,
        ta.source_player_key,
        ta.sleeper_player_id,
        ta.gsis_id,
        ta.display_name,
        ta.market_player_name,
        ta.normalized_name,
        ta.position,
        ta.team,
        ta.age,
        ta.active_status,
        ta.market_value,
        ta.risk_adjusted_trade_value,
        ta.replacement_value_estimate,
        ta.scoring_profile_id,
        ta.league_type_id,
        ta.roster_format_id,
        ta.model_run_id,
        ta.ranking_version,
        ta.pigskin_rank_overall,
        ta.pigskin_rank_position,
        ta.pigskin_tier,
        ta.pigskin_projection,
        ta.pigskin_confidence,
        ta.pigskin_risk_score,
        ta.pigskin_breakout_score,
        ta.pigskin_fraud_risk_score,
        ta.recent_fantasy_points_per_game,
        ta.recent_usage_summary_json,
        ta.recent_trend_label,
        ta.position_scarcity_score,
        ta.trade_asset_summary_json,
        ta.source_freshness_json AS asset_source_freshness_json,
        ta.missing_data_flags AS asset_missing_data_flags,
        pp.profile_age,
        pp.role_summary_json,
        pp.epa_summary_json,
        pp.pigskin_summary,
        pp.prospect_summary_json,
        pp.profile_source_freshness_json,
        pp.profile_missing_data_flags,
        hr.history_recent_points_per_game,
        hr.history_target_share,
        hr.history_rush_share,
        hr.history_high_value_touches,
        hr.history_source_freshness_json,
        hr.history_missing_data_flags
    FROM `{_table_id(project_id, dataset_id, "compat_trade_assets_current")}` ta
    LEFT JOIN profile_latest pp
        ON (
            ta.player_id_internal IS NOT NULL
            AND pp.player_id_internal = ta.player_id_internal
        )
        OR (
            ta.source_player_key IS NOT NULL
            AND pp.source_player_key = ta.source_player_key
        )
        OR (
            ta.sleeper_player_id IS NOT NULL
            AND pp.sleeper_player_id = ta.sleeper_player_id
        )
        OR (
            ta.normalized_name IS NOT NULL
            AND pp.normalized_name = ta.normalized_name
        )
    LEFT JOIN history_recent hr
        ON (
            ta.player_id_internal IS NOT NULL
            AND hr.player_id_internal = ta.player_id_internal
        )
        OR (
            ta.source_player_key IS NOT NULL
            AND hr.source_player_key = ta.source_player_key
        )
        OR (
            ta.normalized_name IS NOT NULL
            AND hr.normalized_name = ta.normalized_name
        )
    WHERE ta.scoring_profile_id = @scoring_profile_id
        AND ta.league_type_id = @league_type_id
        AND ta.roster_format_id = @roster_format_id
        AND (
            ta.player_id_internal IN UNNEST(@lookups)
            OR ta.source_player_key IN UNNEST(@lookups)
            OR ta.sleeper_player_id IN UNNEST(@lookups)
            OR ta.gsis_id IN UNNEST(@lookups)
            OR LOWER(ta.display_name) IN UNNEST(@lower_lookups)
            OR LOWER(ta.market_player_name) IN UNNEST(@lower_lookups)
            OR ta.normalized_name IN UNNEST(@normalized_lookups)
        )
    QUALIFY ROW_NUMBER() OVER(
        PARTITION BY COALESCE(ta.player_id_internal, ta.source_player_key, ta.sleeper_player_id, ta.normalized_name)
        ORDER BY ta.market_value DESC, ta.pigskin_rank_position ASC, ta.display_name ASC
    ) = 1
    ORDER BY ta.market_value DESC, ta.pigskin_rank_position ASC, ta.display_name ASC
    """
    return sql, bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=[
            bigquery.ScalarQueryParameter("scoring_profile_id", "STRING", scoring_profile_id),
            bigquery.ScalarQueryParameter("league_type_id", "STRING", league_type_id),
            bigquery.ScalarQueryParameter("roster_format_id", "STRING", roster_format_id),
            bigquery.ArrayQueryParameter("lookups", "STRING", lookups),
            bigquery.ArrayQueryParameter("lower_lookups", "STRING", lower_lookups),
            bigquery.ArrayQueryParameter("normalized_lookups", "STRING", normalized_lookups),
        ],
    )


def calculate_trade_asset_value(asset_row: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Calculate deterministic values for one asset."""

    context = context or {}
    scoring_profile_id = context.get("scoring_profile_id", DEFAULT_SCORING_PROFILE)
    league_type_id = context.get("league_type_id", DEFAULT_LEAGUE_TYPE)
    roster_format_id = context.get("roster_format_id", DEFAULT_ROSTER_FORMAT)
    position = str(asset_row.get("position") or "").upper()
    age = _num(asset_row.get("age"), _num(asset_row.get("profile_age"), None))
    market_value = _num(asset_row.get("risk_adjusted_trade_value"), _num(asset_row.get("market_value"), 0.0))
    raw_market_value = _num(asset_row.get("market_value"), market_value)
    rank_value = _rank_value(asset_row.get("pigskin_rank_overall"), asset_row.get("pigskin_rank_position"), position)
    recent_points = _num(
        asset_row.get("recent_fantasy_points_per_game"),
        _num(asset_row.get("history_recent_points_per_game"), 0.0),
    )
    role_value = _role_trend_value(asset_row.get("recent_trend_label"))
    risk_score = _risk_score(asset_row)
    format_multiplier = _roster_format_multiplier(position, roster_format_id)
    age_multiplier = _age_multiplier(position, age, league_type_id)
    league_multiplier = 1.04 if league_type_id in {"dynasty", "keeper"} and age is not None and age <= 25 else 1.0

    short_term = (
        market_value * 0.50
        + rank_value * 0.16
        + recent_points * TRADE_VALUE_CONFIG["recent_points_multiplier"] * 0.28
        + role_value
        - risk_score * TRADE_VALUE_CONFIG["risk_weight"]
    ) * format_multiplier
    ros = (
        market_value * TRADE_VALUE_CONFIG["market_weight"]
        + rank_value * TRADE_VALUE_CONFIG["rank_weight"]
        + recent_points * TRADE_VALUE_CONFIG["recent_points_multiplier"] * 0.17
        + role_value * TRADE_VALUE_CONFIG["role_weight"]
        - risk_score * TRADE_VALUE_CONFIG["risk_weight"]
    ) * format_multiplier
    dynasty = ros * age_multiplier * league_multiplier

    if league_type_id == "dynasty":
        blended = short_term * 0.15 + ros * 0.35 + dynasty * 0.50
    elif league_type_id == "keeper":
        blended = short_term * 0.25 + ros * 0.40 + dynasty * 0.35
    else:
        blended = short_term * 0.45 + ros * 0.45 + dynasty * 0.10

    return {
        "market_value": round(raw_market_value, 3),
        "short_term_value": round(max(0.0, short_term), 3),
        "ros_value": round(max(0.0, ros), 3),
        "dynasty_value": round(max(0.0, dynasty), 3),
        "value": round(max(0.0, blended), 3),
        "risk_score": round(max(0.0, risk_score), 3),
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "formula_version": TRADE_VALUE_CONFIG["version"],
        "components": {
            "market_value": market_value,
            "rank_value": rank_value,
            "recent_points_per_game": recent_points,
            "role_value": role_value,
            "format_multiplier": format_multiplier,
            "age_multiplier": age_multiplier,
            "risk_score": risk_score,
        },
    }


def build_trade_review_packet(
    side_a: Any,
    side_b: Any,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    *,
    league_id: str | None = None,
    roster_id: str | int | None = None,
    model_run_id: str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic trade review packet from curated data."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    context = {
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "league_id": _clean_optional(league_id),
        "roster_id": _clean_optional(roster_id),
    }
    resolved_a = resolve_trade_assets(
        side_a,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        client=client,
        dataset_id=dataset_id,
    )
    resolved_b = resolve_trade_assets(
        side_b,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        client=client,
        dataset_id=dataset_id,
    )
    if not resolved_a or not resolved_b:
        raise ValueError("Both trade sides must include at least one resolved asset")

    comparison = compare_trade_sides(resolved_a, resolved_b, context)
    trade_review_id = _new_trade_review_id()
    now = _utc_timestamp()
    effective_model_run_id = model_run_id or _first_non_empty(
        [asset.get("model_run_id") for asset in resolved_a + resolved_b]
    )
    ranking_version = _first_non_empty([asset.get("ranking_version") for asset in resolved_a + resolved_b])
    source_freshness = _source_freshness_payload(resolved_a + resolved_b)
    missing_flags = _packet_missing_flags(resolved_a + resolved_b, effective_model_run_id)

    packet_json = _build_packet_json(
        trade_review_id=trade_review_id,
        side_a=resolved_a,
        side_b=resolved_b,
        comparison=comparison,
        context=context,
        model_run_id=effective_model_run_id,
        ranking_version=ranking_version,
        source_freshness=source_freshness,
        missing_flags=missing_flags,
    )
    packet_text = _build_packet_text(packet_json)

    return {
        "trade_review_id": trade_review_id,
        "created_at": now,
        "updated_at": now,
        "model_run_id": effective_model_run_id,
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "league_id": _clean_optional(league_id),
        "roster_id": _clean_optional(roster_id),
        "side_a": resolved_a,
        "side_b": resolved_b,
        "comparison": comparison,
        "packet": packet_json,
        "packet_json": json.dumps(packet_json, sort_keys=True),
        "packet_text": packet_text,
        "source_freshness_json": json.dumps(source_freshness, sort_keys=True),
        "missing_data_flags": json.dumps(missing_flags, sort_keys=True),
        "request_row": _request_row(trade_review_id, resolved_a, resolved_b, context, effective_model_run_id, now),
        "packet_row": _packet_row(trade_review_id, comparison, context, effective_model_run_id, packet_json, packet_text, source_freshness, missing_flags, now),
        "player_rows": _player_rows(trade_review_id, "A", resolved_a, context, now)
        + _player_rows(trade_review_id, "B", resolved_b, context, now),
    }


def compare_trade_sides(
    side_a: list[dict[str, Any]],
    side_b: list[dict[str, Any]],
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare two already-resolved trade sides."""

    context = context or {}
    scored_a = [_with_value(asset, context) for asset in side_a]
    scored_b = [_with_value(asset, context) for asset in side_b]
    totals_a = _side_totals(scored_a)
    totals_b = _side_totals(scored_b)
    value_delta = round(totals_a["value"] - totals_b["value"], 3)
    winner = _winner(value_delta, totals_a["value"], totals_b["value"])
    confidence = _confidence_score(value_delta, totals_a["value"], totals_b["value"], scored_a + scored_b)
    return {
        "side_a_assets": scored_a,
        "side_b_assets": scored_b,
        "side_a": totals_a,
        "side_b": totals_b,
        "value_delta": value_delta,
        "recommended_winner": winner,
        "confidence_score": confidence,
        "short_term_winner": _winner(totals_a["short_term_value"] - totals_b["short_term_value"], totals_a["short_term_value"], totals_b["short_term_value"]),
        "ros_winner": _winner(totals_a["ros_value"] - totals_b["ros_value"], totals_a["ros_value"], totals_b["ros_value"]),
        "dynasty_winner": _winner(totals_a["dynasty_value"] - totals_b["dynasty_value"], totals_a["dynasty_value"], totals_b["dynasty_value"]),
    }


def save_trade_review_packet(
    packet: dict[str, Any],
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> str:
    """Persist a built trade review packet."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    for table_name, rows in (
        ("trade_review_requests", [packet["request_row"]]),
        ("trade_review_packets", [packet["packet_row"]]),
        ("trade_review_packet_players", packet["player_rows"]),
    ):
        errors = client.insert_rows_json(_table_id(client.project, dataset_id, table_name), rows)
        if errors:
            raise RuntimeError(f"Failed to insert {table_name} rows for {packet['trade_review_id']}: {errors}")
    return packet["trade_review_id"]


def get_trade_review_packet(
    trade_review_id: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any] | None:
    """Fetch one saved trade review packet and its player rows."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    packet_sql = f"""
    SELECT *
    FROM `{_table_id(client.project, dataset_id, "trade_review_packets")}`
    WHERE trade_review_id = @trade_review_id
    ORDER BY updated_at DESC
    LIMIT 1
    """
    player_sql = f"""
    SELECT *
    FROM `{_table_id(client.project, dataset_id, "trade_review_packet_players")}`
    WHERE trade_review_id = @trade_review_id
    ORDER BY side, display_name
    """
    job_config = _job_config([("trade_review_id", "STRING", trade_review_id)])
    packet_rows = _query_rows(client, packet_sql, job_config)
    if not packet_rows:
        return None
    packet = packet_rows[0]
    packet["packet"] = _parse_json(packet.get("packet_json"), {})
    packet["player_rows"] = _query_rows(client, player_sql, job_config)
    return packet


def _build_packet_json(
    *,
    trade_review_id: str,
    side_a: list[dict[str, Any]],
    side_b: list[dict[str, Any]],
    comparison: dict[str, Any],
    context: dict[str, Any],
    model_run_id: str | None,
    ranking_version: str | None,
    source_freshness: dict[str, Any],
    missing_flags: list[str],
) -> dict[str, Any]:
    side_a_names = [_asset_name(asset) for asset in side_a]
    side_b_names = [_asset_name(asset) for asset in side_b]
    winner = comparison["recommended_winner"]
    clean_take = _clean_take(winner, side_a_names, side_b_names, comparison["value_delta"])
    return {
        "trade_summary": {
            "trade_review_id": trade_review_id,
            "side_a_assets": side_a_names,
            "side_b_assets": side_b_names,
            "scoring_profile_id": context.get("scoring_profile_id"),
            "league_type_id": context.get("league_type_id"),
            "roster_format_id": context.get("roster_format_id"),
            "league_id": context.get("league_id"),
            "roster_id": context.get("roster_id"),
            "model_run_id": model_run_id,
        },
        "verdict": {
            "winner": winner,
            "value_delta": comparison["value_delta"],
            "confidence": comparison["confidence_score"],
            "short_term_winner": comparison["short_term_winner"],
            "ros_winner": comparison["ros_winner"],
            "dynasty_winner": comparison["dynasty_winner"],
            "best_ball_ceiling_note": _best_ball_note(context, side_a + side_b),
            "superflex_effect": _superflex_note(context, side_a + side_b),
        },
        "side_a_evidence": _side_evidence("A", comparison["side_a_assets"], comparison["side_a"], context),
        "side_b_evidence": _side_evidence("B", comparison["side_b_assets"], comparison["side_b"], context),
        "player_evidence": [_player_evidence(asset, context) for asset in comparison["side_a_assets"] + comparison["side_b_assets"]],
        "roster_context": {
            "viewer_team_context_available": bool(context.get("league_id") and context.get("roster_id")),
            "league_id": context.get("league_id"),
            "roster_id": context.get("roster_id"),
            "starters_gained_lost": "pending_viewer_team_fit_wiring",
            "bench_replacement": "pending_viewer_team_fit_wiring",
            "roster_construction_notes": "Viewer-team packet can be joined later for exact roster fit.",
            "bye_injury_placeholders": "pending_schedule_and_injury_context",
        },
        "counterarguments": {
            "best_argument_for_side_a": _counterargument("A", comparison["side_a_assets"], comparison["side_a"]),
            "best_argument_for_side_b": _counterargument("B", comparison["side_b_assets"], comparison["side_b"]),
            "what_data_could_change_verdict": "Updated rankings, injury status, role change, or a material market-value move.",
        },
        "show_framing": {
            "clean_take": clean_take,
            "snark_hooks": _snark_hooks(winner, side_a_names, side_b_names),
            "meatbag_disagreement_angle": "If consensus disagrees, force it to explain the actual role and value math.",
            "confidence_caveat": _confidence_caveat(comparison["confidence_score"], missing_flags),
            "recommended_script_framing": f"Lead with the winner, then cross-examine the losing side with value, role, and risk.",
        },
        "metadata": {
            "model_run_id": model_run_id,
            "ranking_version": ranking_version,
            "sources_used": [
                "compat_trade_assets_current",
                "compat_trade_player_history",
                "compat_player_profiles_current",
            ],
            "source_freshness": source_freshness,
            "missing_data_flags": missing_flags,
            "value_config": TRADE_VALUE_CONFIG,
        },
    }


def _with_value(asset: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    scored = dict(asset)
    scored["value_result"] = calculate_trade_asset_value(asset, context)
    return scored


def _side_totals(assets: list[dict[str, Any]]) -> dict[str, float]:
    if not assets:
        return {
            "value": 0.0,
            "short_term_value": 0.0,
            "ros_value": 0.0,
            "dynasty_value": 0.0,
            "risk_score": 0.0,
        }
    return {
        "value": round(sum(asset["value_result"]["value"] for asset in assets), 3),
        "short_term_value": round(sum(asset["value_result"]["short_term_value"] for asset in assets), 3),
        "ros_value": round(sum(asset["value_result"]["ros_value"] for asset in assets), 3),
        "dynasty_value": round(sum(asset["value_result"]["dynasty_value"] for asset in assets), 3),
        "risk_score": round(sum(asset["value_result"]["risk_score"] for asset in assets) / len(assets), 3),
    }


def _player_rows(
    trade_review_id: str,
    side: str,
    assets: list[dict[str, Any]],
    context: dict[str, Any],
    created_at: str,
) -> list[dict[str, Any]]:
    rows = []
    for asset in assets:
        value_result = asset.get("value_result") or calculate_trade_asset_value(asset, context)
        evidence = _player_evidence({**asset, "value_result": value_result}, context)
        rows.append({
            "trade_review_id": trade_review_id,
            "side": side,
            "player_id_internal": asset.get("player_id_internal"),
            "source_player_key": asset.get("source_player_key"),
            "display_name": _asset_name(asset),
            "position": asset.get("position"),
            "team": asset.get("team"),
            "scoring_profile_id": context.get("scoring_profile_id"),
            "league_type_id": context.get("league_type_id"),
            "roster_format_id": context.get("roster_format_id"),
            "market_value": value_result["market_value"],
            "pigskin_rank_overall": _int_or_none(asset.get("pigskin_rank_overall")),
            "pigskin_rank_position": _int_or_none(asset.get("pigskin_rank_position")),
            "pigskin_tier": asset.get("pigskin_tier"),
            "recent_points_per_game": value_result["components"]["recent_points_per_game"],
            "short_term_value": value_result["short_term_value"],
            "ros_value": value_result["ros_value"],
            "dynasty_value": value_result["dynasty_value"],
            "risk_score": value_result["risk_score"],
            "evidence_json": json.dumps(evidence, sort_keys=True),
            "missing_data_flags": json.dumps(_asset_missing_flags(asset), sort_keys=True),
            "created_at": created_at,
        })
    return rows


def _packet_row(
    trade_review_id: str,
    comparison: dict[str, Any],
    context: dict[str, Any],
    model_run_id: str | None,
    packet_json: dict[str, Any],
    packet_text: str,
    source_freshness: dict[str, Any],
    missing_flags: list[str],
    timestamp: str,
) -> dict[str, Any]:
    return {
        "trade_review_id": trade_review_id,
        "model_run_id": model_run_id,
        "scoring_profile_id": context.get("scoring_profile_id"),
        "league_type_id": context.get("league_type_id"),
        "roster_format_id": context.get("roster_format_id"),
        "league_id": context.get("league_id"),
        "roster_id": context.get("roster_id"),
        "side_a_value": comparison["side_a"]["value"],
        "side_b_value": comparison["side_b"]["value"],
        "side_a_short_term_value": comparison["side_a"]["short_term_value"],
        "side_b_short_term_value": comparison["side_b"]["short_term_value"],
        "side_a_ros_value": comparison["side_a"]["ros_value"],
        "side_b_ros_value": comparison["side_b"]["ros_value"],
        "side_a_dynasty_value": comparison["side_a"]["dynasty_value"],
        "side_b_dynasty_value": comparison["side_b"]["dynasty_value"],
        "side_a_risk_score": comparison["side_a"]["risk_score"],
        "side_b_risk_score": comparison["side_b"]["risk_score"],
        "value_delta": comparison["value_delta"],
        "recommended_winner": comparison["recommended_winner"],
        "confidence_score": comparison["confidence_score"],
        "packet_json": json.dumps(packet_json, sort_keys=True),
        "packet_text": packet_text,
        "source_freshness_json": json.dumps(source_freshness, sort_keys=True),
        "missing_data_flags": json.dumps(missing_flags, sort_keys=True),
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def _request_row(
    trade_review_id: str,
    side_a: list[dict[str, Any]],
    side_b: list[dict[str, Any]],
    context: dict[str, Any],
    model_run_id: str | None,
    timestamp: str,
) -> dict[str, Any]:
    return {
        "trade_review_id": trade_review_id,
        "model_run_id": model_run_id,
        "request_source": "trade_review_packets_helper",
        "league_id": context.get("league_id"),
        "roster_id": context.get("roster_id"),
        "scoring_profile_id": context.get("scoring_profile_id"),
        "league_type_id": context.get("league_type_id"),
        "roster_format_id": context.get("roster_format_id"),
        "side_a_json": json.dumps([asset.get("requested_lookup") or _asset_name(asset) for asset in side_a], sort_keys=True),
        "side_b_json": json.dumps([asset.get("requested_lookup") or _asset_name(asset) for asset in side_b], sort_keys=True),
        "request_context_json": json.dumps(context, sort_keys=True),
        "created_by": "trade_review_packets_helper",
        "created_at": timestamp,
        "status": "complete",
        "error_message": None,
    }


def _side_evidence(side: str, assets: list[dict[str, Any]], totals: dict[str, float], context: dict[str, Any]) -> dict[str, Any]:
    return {
        "side": side,
        "player_rows": [_player_summary(asset) for asset in assets],
        "total_value": totals["value"],
        "short_term_value": totals["short_term_value"],
        "ros_value": totals["ros_value"],
        "dynasty_value": totals["dynasty_value"],
        "positional_scarcity": _positional_scarcity_note(assets, context),
        "risks": [_risk_note(asset) for asset in assets if _risk_score(asset) > 0],
        "upside": [_upside_note(asset) for asset in assets],
        "roster_fit": "pending_viewer_team_context_join" if context.get("league_id") else "not_requested",
    }


def _player_evidence(asset: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    value_result = asset.get("value_result") or calculate_trade_asset_value(asset, context)
    return {
        "identity": {
            "player_id_internal": asset.get("player_id_internal"),
            "source_player_key": asset.get("source_player_key"),
            "sleeper_player_id": asset.get("sleeper_player_id"),
            "display_name": _asset_name(asset),
            "position": asset.get("position"),
            "team": asset.get("team"),
        },
        "trade_asset_value": value_result["market_value"],
        "ranking_context": {
            "pigskin_rank_overall": asset.get("pigskin_rank_overall"),
            "pigskin_rank_position": asset.get("pigskin_rank_position"),
            "pigskin_tier": asset.get("pigskin_tier"),
            "ranking_version": asset.get("ranking_version"),
        },
        "recent_production": {
            "recent_points_per_game": value_result["components"]["recent_points_per_game"],
            "history_recent_points_per_game": asset.get("history_recent_points_per_game"),
        },
        "usage_trend": {
            "recent_trend_label": asset.get("recent_trend_label"),
            "target_share": asset.get("history_target_share"),
            "rush_share": asset.get("history_rush_share"),
            "high_value_touches": asset.get("history_high_value_touches"),
        },
        "risk_fraud_breakout_context": {
            "risk_score": value_result["risk_score"],
            "pigskin_fraud_risk_score": asset.get("pigskin_fraud_risk_score"),
            "pigskin_breakout_score": asset.get("pigskin_breakout_score"),
        },
        "age_dynasty_context": {
            "age": asset.get("age") or asset.get("profile_age"),
            "dynasty_value": value_result["dynasty_value"],
            "age_multiplier": value_result["components"]["age_multiplier"],
        },
        "counterargument": _player_counterargument(asset),
        "formula": value_result,
        "missing_data_flags": _asset_missing_flags(asset),
    }


def _build_packet_text(packet: dict[str, Any]) -> str:
    verdict = packet["verdict"]
    summary = packet["trade_summary"]
    side_a = ", ".join(summary["side_a_assets"])
    side_b = ", ".join(summary["side_b_assets"])
    lines = [
        f"Trade Review: Side A gives {side_a}. Side B gives {side_b}.",
        f"Verdict: {verdict['winner']} wins by {verdict['value_delta']} value points with {verdict['confidence']} confidence.",
        f"Short term winner: {verdict['short_term_winner']}. Rest of season winner: {verdict['ros_winner']}. Dynasty winner: {verdict['dynasty_winner']}.",
        packet["show_framing"]["clean_take"],
        packet["counterarguments"]["what_data_could_change_verdict"],
    ]
    return "\n".join(lines)[:PACKET_TEXT_MAX_CHARS]


def _best_match_for_lookup(
    rows: list[dict[str, Any]],
    lookup: str,
    normalized_lookup: str,
    used_keys: set[str],
) -> dict[str, Any] | None:
    matches = [
        row for row in rows
        if _asset_dedupe_key(row) not in used_keys and _row_matches_lookup(row, lookup, normalized_lookup)
    ]
    if not matches:
        return None
    return sorted(matches, key=lambda row: (_num(row.get("market_value"), 0.0), -_num(row.get("pigskin_rank_position"), 9999.0)), reverse=True)[0]


def _row_matches_lookup(row: dict[str, Any], lookup: str, normalized_lookup: str) -> bool:
    lower_lookup = lookup.lower()
    direct_fields = (
        row.get("player_id_internal"),
        row.get("source_player_key"),
        row.get("sleeper_player_id"),
        row.get("gsis_id"),
    )
    if any(str(value or "") == lookup for value in direct_fields):
        return True
    name_fields = (row.get("display_name"), row.get("market_player_name"))
    if any(str(value or "").lower() == lower_lookup for value in name_fields):
        return True
    return str(row.get("normalized_name") or "") == normalized_lookup


def _asset_dedupe_key(asset: dict[str, Any]) -> str:
    return str(
        asset.get("player_id_internal")
        or asset.get("source_player_key")
        or asset.get("sleeper_player_id")
        or asset.get("normalized_name")
        or asset.get("display_name")
    )


def _asset_name(asset: dict[str, Any]) -> str:
    return str(asset.get("display_name") or asset.get("market_player_name") or asset.get("requested_lookup") or "Unknown")


def _rank_value(overall_rank: Any, position_rank: Any, position: str) -> float:
    rank = _num(overall_rank, None)
    if rank is None:
        rank = _num(position_rank, None)
        if rank is None:
            return 0.0
        position_anchor = {"QB": 36, "RB": 72, "WR": 96, "TE": 48}.get(position, 72)
        return max(0.0, (position_anchor - rank) / position_anchor) * TRADE_VALUE_CONFIG["rank_anchor_value"] * 0.75
    return max(0.0, (240.0 - rank) / 240.0) * TRADE_VALUE_CONFIG["rank_anchor_value"]


def _role_trend_value(label: Any) -> float:
    text = str(label or "").lower()
    if any(token in text for token in ("rising", "up", "improving", "surging", "earned")):
        return 650.0
    if any(token in text for token in ("falling", "down", "fragile", "thin", "declining")):
        return -650.0
    return 0.0


def _risk_score(asset: dict[str, Any]) -> float:
    values = [
        _num(asset.get("pigskin_risk_score"), None),
        _num(asset.get("pigskin_fraud_risk_score"), None),
    ]
    values = [value for value in values if value is not None]
    return max(values) if values else 0.0


def _roster_format_multiplier(position: str, roster_format_id: str) -> float:
    if roster_format_id in {"superflex", "two_qb"} and position == "QB":
        return TRADE_VALUE_CONFIG["superflex_qb_multiplier"]
    if roster_format_id == "best_ball" and position in {"WR", "TE"}:
        return TRADE_VALUE_CONFIG["best_ball_wr_te_multiplier"]
    return 1.0


def _age_multiplier(position: str, age: float | None, league_type_id: str) -> float:
    if age is None:
        return 1.0
    weight = TRADE_VALUE_CONFIG["dynasty_age_weight"] if league_type_id in {"dynasty", "keeper"} else TRADE_VALUE_CONFIG["redraft_age_weight"]
    if position == "RB":
        curve = 0.12 if age <= 24 else 0.03 if age <= 26 else -0.12 if age <= 28 else -0.25
    elif position == "WR":
        curve = 0.10 if age <= 25 else 0.03 if age <= 28 else -0.08 if age <= 30 else -0.18
    elif position == "TE":
        curve = 0.07 if age <= 26 else 0.02 if age <= 30 else -0.08
    elif position == "QB":
        curve = 0.06 if age <= 28 else 0.02 if age <= 34 else -0.08 if age <= 37 else -0.18
    else:
        curve = 0.0
    return max(0.65, 1.0 + curve * (weight / TRADE_VALUE_CONFIG["dynasty_age_weight"]))


def _winner(delta: float, side_a_value: float, side_b_value: float) -> str:
    baseline = max(abs(side_a_value), abs(side_b_value), 1.0)
    if abs(delta) <= baseline * TRADE_VALUE_CONFIG["tie_delta_fraction"]:
        return "even"
    return "side_a" if delta > 0 else "side_b"


def _confidence_score(delta: float, side_a_value: float, side_b_value: float, assets: list[dict[str, Any]]) -> float:
    baseline = max(abs(side_a_value), abs(side_b_value), 1.0)
    delta_confidence = min(0.35, abs(delta) / baseline)
    missing_penalty = min(0.25, sum(len(_asset_missing_flags(asset)) for asset in assets) * 0.015)
    return round(max(0.25, min(0.95, 0.58 + delta_confidence - missing_penalty)), 3)


def _packet_missing_flags(assets: list[dict[str, Any]], model_run_id: str | None) -> list[str]:
    flags = set()
    if not model_run_id:
        flags.add("missing_model_run_id")
    for asset in assets:
        flags.update(_asset_missing_flags(asset))
    return sorted(flags)


def _asset_missing_flags(asset: dict[str, Any]) -> list[str]:
    flags = set()
    if asset.get("market_value") in (None, ""):
        flags.add("missing_market_value")
    if asset.get("pigskin_rank_position") in (None, ""):
        flags.add("missing_pigskin_rank")
    if asset.get("recent_fantasy_points_per_game") in (None, "") and asset.get("history_recent_points_per_game") in (None, ""):
        flags.add("missing_recent_points")
    for field in ("asset_missing_data_flags", "profile_missing_data_flags", "history_missing_data_flags"):
        flags.update(_json_array(asset.get(field)))
    return sorted(flag for flag in flags if flag)


def _source_freshness_payload(assets: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sources": {
            "compat_trade_assets_current": _freshness_summary(
                _first_non_empty(asset.get("asset_source_freshness_json") for asset in assets)
            ),
            "compat_player_profiles_current": _freshness_summary(
                _first_non_empty(asset.get("profile_source_freshness_json") for asset in assets)
            ),
            "compat_trade_player_history": _freshness_summary(
                _first_non_empty(asset.get("history_source_freshness_json") for asset in assets)
            ),
        }
    }


def _player_summary(asset: dict[str, Any]) -> dict[str, Any]:
    value = asset["value_result"]
    return {
        "display_name": _asset_name(asset),
        "position": asset.get("position"),
        "team": asset.get("team"),
        "value": value["value"],
        "short_term_value": value["short_term_value"],
        "ros_value": value["ros_value"],
        "dynasty_value": value["dynasty_value"],
        "risk_score": value["risk_score"],
        "pigskin_rank_position": asset.get("pigskin_rank_position"),
        "pigskin_tier": asset.get("pigskin_tier"),
    }


def _positional_scarcity_note(assets: list[dict[str, Any]], context: dict[str, Any]) -> str:
    positions = {str(asset.get("position") or "").upper() for asset in assets}
    if context.get("roster_format_id") in {"superflex", "two_qb"} and "QB" in positions:
        return "QB value is boosted by roster format."
    if "TE" in positions:
        return "TE value depends heavily on tier separation."
    return "No special positional scarcity adjustment beyond baseline config."


def _risk_note(asset: dict[str, Any]) -> str:
    return f"{_asset_name(asset)} carries a risk score of {_risk_score(asset):.1f}."


def _upside_note(asset: dict[str, Any]) -> str:
    breakout = _num(asset.get("pigskin_breakout_score"), 0.0)
    if breakout >= 70:
        return f"{_asset_name(asset)} has a real upside flag, not just vibes."
    return f"{_asset_name(asset)} needs value from role, market, or rank more than pure breakout juice."


def _counterargument(side: str, assets: list[dict[str, Any]], totals: dict[str, float]) -> str:
    names = ", ".join(_asset_name(asset) for asset in assets)
    return f"Best case for side {side}: {names} consolidates into {totals['value']:.1f} total value if role and health hold."


def _player_counterargument(asset: dict[str, Any]) -> str:
    if _risk_score(asset) >= 60:
        return "The risk case is loud enough that market value may be flattering the player."
    if _num(asset.get("pigskin_rank_position"), 999) <= 12:
        return "The pushback is price, not profile. Elite ranks still need context."
    return "The skeptical case is that this player is a useful piece, not a league-swinging answer."


def _best_ball_note(context: dict[str, Any], assets: list[dict[str, Any]]) -> str | None:
    if context.get("roster_format_id") != "best_ball":
        return None
    receivers = [asset for asset in assets if asset.get("position") in {"WR", "TE"}]
    if receivers:
        return "Best ball slightly boosts volatile pass catchers with weekly ceiling profiles."
    return "Best ball format requested, but no clear ceiling pass-catcher adjustment was triggered."


def _superflex_note(context: dict[str, Any], assets: list[dict[str, Any]]) -> str | None:
    if context.get("roster_format_id") not in {"superflex", "two_qb"}:
        return None
    qbs = [asset for asset in assets if asset.get("position") == "QB"]
    if qbs:
        return "QB assets receive a format multiplier because replacement value is harsher."
    return "Superflex format requested, but neither side includes a QB."


def _clean_take(winner: str, side_a_names: list[str], side_b_names: list[str], delta: float) -> str:
    if winner == "even":
        return "This is close enough that roster fit should break the tie. Congratulations, the spreadsheet has feelings now."
    winning_names = side_a_names if winner == "side_a" else side_b_names
    losing_names = side_b_names if winner == "side_a" else side_a_names
    return f"Take {', '.join(winning_names)} over {', '.join(losing_names)}. The value gap is {delta:.1f}, so pretending this is a coin flip is meatbag theater."


def _snark_hooks(winner: str, side_a_names: list[str], side_b_names: list[str]) -> list[str]:
    if winner == "even":
        return ["No obvious robbery here, which is rude to content creators.", "Make the roster-fit argument or stop yelling."]
    winners = side_a_names if winner == "side_a" else side_b_names
    return [
        f"The winning side is {', '.join(winners)}, and the math is not asking politely.",
        "If consensus hates it, check whether consensus is just box-score cosplay.",
    ]


def _confidence_caveat(confidence: float, missing_flags: list[str]) -> str:
    if missing_flags:
        return f"Confidence is capped by missing data: {', '.join(missing_flags[:6])}."
    if confidence >= 0.8:
        return "Confidence is strong for a deterministic packet."
    return "Confidence is moderate because trade value is close or profile evidence is mixed."


def _query_rows(client: Any, sql: str, job_config: bigquery.QueryJobConfig) -> list[dict[str, Any]]:
    try:
        rows = client.query(sql, job_config=job_config).result()
    except NotFound:
        return []
    return [_row_to_dict(row) for row in rows]


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


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    if not IDENTIFIER_RE.match(table_name):
        raise ValueError(f"Unsafe BigQuery table name: {table_name}")
    return f"{project_id}.{dataset_id}.{table_name}"


def _num(value: Any, default: float | None = 0.0) -> float | None:
    if value in (None, ""):
        return default
    try:
        if isinstance(value, float) and math.isnan(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _int_or_none(value: Any) -> int | None:
    number = _num(value, None)
    return int(number) if number is not None else None


def _clean_optional(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _json_array(value: Any) -> list[str]:
    parsed = _parse_json(value, [])
    if isinstance(parsed, list):
        return [str(item) for item in parsed if item]
    return []


def _parse_json(value: Any, default: Any) -> Any:
    if value in (None, ""):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(str(value))
    except json.JSONDecodeError:
        return default


def _freshness_summary(value: Any) -> dict[str, Any]:
    parsed = _parse_json(value, {})
    if not isinstance(parsed, dict):
        return {}
    allowed_keys = (
        "refreshed_at",
        "market_snapshot_timestamp",
        "market_snapshot_date",
        "as_of_season",
        "as_of_week",
        "scoring_profile_id",
    )
    return {
        key: parsed[key]
        for key in allowed_keys
        if key in parsed and parsed[key] not in (None, "")
    }


def _first_non_empty(values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def _new_trade_review_id() -> str:
    return f"trade_review_{uuid.uuid4().hex}"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a deterministic trade review packet.")
    parser.add_argument("--side-a", required=True, help="Comma-separated side A assets.")
    parser.add_argument("--side-b", required=True, help="Comma-separated side B assets.")
    parser.add_argument("--scoring-profile", default=DEFAULT_SCORING_PROFILE)
    parser.add_argument("--league-type", default=DEFAULT_LEAGUE_TYPE)
    parser.add_argument("--roster-format", default=DEFAULT_ROSTER_FORMAT)
    parser.add_argument("--league-id")
    parser.add_argument("--roster-id")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    packet = build_trade_review_packet(
        args.side_a,
        args.side_b,
        scoring_profile_id=args.scoring_profile,
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        league_id=args.league_id,
        roster_id=args.roster_id,
    )
    if args.dry_run:
        print(json.dumps(packet["packet"], indent=2, sort_keys=True))
        return
    trade_review_id = save_trade_review_packet(packet)
    print(trade_review_id)


if __name__ == "__main__":
    main()
