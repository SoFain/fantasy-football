"""Deterministic segment packet builders for Fraud Watch and Sleeper Breakouts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
from datetime import datetime, timezone
from typing import Any

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.load import get_bigquery_client
from src.model_runs import get_latest_model_run


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_SCORING_PROFILE = "ppr"
DEFAULT_LEAGUE_TYPE = "redraft"
DEFAULT_ROSTER_FORMAT = "one_qb"
DEFAULT_PACKET_LIMIT = 25
MAX_PACKET_LIMIT = 100
PACKET_TEXT_MAX_CHARS = 12000
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("SEGMENT_PACKETS_MAX_BYTES_BILLED", "1000000000"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")

FRAUD_PACKET_KEYS = (
    "identity",
    "ranking_context",
    "fraud_claim",
    "evidence",
    "counterargument",
    "what_would_change_the_take",
    "show_framing",
    "snark_hooks",
    "source_metadata",
)
BREAKOUT_PACKET_KEYS = (
    "identity",
    "ranking_context",
    "breakout_claim",
    "evidence",
    "counterargument",
    "what_would_change_the_take",
    "show_framing",
    "snark_hooks",
    "source_metadata",
)

FRAUD_BREAKOUT_CONFIG: dict[str, Any] = {
    "version": "segment_packets_baseline_v1",
    "fraud": {
        "points_over_expected_weight": 0.22,
        "td_dependency_weight": 0.18,
        "low_usage_weight": 0.16,
        "efficiency_outlier_weight": 0.14,
        "declining_role_weight": 0.12,
        "market_hype_weight": 0.10,
        "role_instability_weight": 0.08,
    },
    "breakout": {
        "role_growth_weight": 0.22,
        "usage_trend_weight": 0.18,
        "opportunity_weight": 0.16,
        "underperformance_weight": 0.14,
        "availability_weight": 0.10,
        "matchup_weight": 0.10,
        "market_discount_weight": 0.10,
    },
}


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def build_fraud_watch_packets(
    season: int | str | None = None,
    week: int | str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    limit: int | str | None = None,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Build deterministic Fraud Watch packets from curated marts."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    safe_limit = _clamp_limit(limit)
    effective_model_run_id = model_run_id or _latest_model_run_id(
        client=client,
        dataset_id=dataset_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    sql, job_config = build_fraud_watch_source_query(
        project_id=client.project,
        dataset_id=dataset_id,
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=safe_limit,
    )
    rows = _query_rows(client, sql, job_config)
    packets = [
        _build_fraud_packet(
            row,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            model_run_id=effective_model_run_id or row.get("model_run_id"),
        )
        for row in rows
    ]
    return sorted(packets, key=lambda packet: packet["fraud_score"] or 0.0, reverse=True)[:safe_limit]


def build_sleeper_breakout_packets(
    season: int | str | None = None,
    week: int | str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    limit: int | str | None = None,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Build deterministic Sleeper Breakout packets from curated marts."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    safe_limit = _clamp_limit(limit)
    effective_model_run_id = model_run_id or _latest_model_run_id(
        client=client,
        dataset_id=dataset_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    sql, job_config = build_sleeper_breakout_source_query(
        project_id=client.project,
        dataset_id=dataset_id,
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=safe_limit,
    )
    rows = _query_rows(client, sql, job_config)
    packets = [
        _build_breakout_packet(
            row,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            model_run_id=effective_model_run_id or row.get("model_run_id"),
        )
        for row in rows
    ]
    return sorted(packets, key=lambda packet: packet["breakout_score"] or 0.0, reverse=True)[:safe_limit]


def build_fraud_watch_source_query(
    *,
    project_id: str,
    dataset_id: str,
    season: int | str | None = None,
    week: int | str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int | str | None = None,
) -> tuple[str, bigquery.QueryJobConfig]:
    sql = f"""
    WITH fraud AS (
        SELECT
            f.*,
            REGEXP_REPLACE(
                REGEXP_REPLACE(LOWER(COALESCE(f.player_display_name, f.player_name, '')), r'\\s+(jr|sr|ii|iii|iv|v)\\.?$', ''),
                r'[^a-z0-9]+',
                ''
            ) AS normalized_name
        FROM `{_table_id(project_id, dataset_id, "analytics_fraud_watch")}` f
        WHERE (@season IS NULL OR f.season = @season)
            AND (@week IS NULL OR f.week = @week)
    ),
    assets AS (
        SELECT *
        FROM `{_table_id(project_id, dataset_id, "compat_trade_assets_current")}`
        WHERE scoring_profile_id = @scoring_profile_id
            AND league_type_id = @league_type_id
            AND roster_format_id = @roster_format_id
    ),
    profiles AS (
        SELECT *
        FROM `{_table_id(project_id, dataset_id, "compat_player_profiles_current")}`
        WHERE scoring_profile_id = @scoring_profile_id
    )
    SELECT
        COALESCE(a.player_id_internal, p.player_id_internal) AS player_id_internal,
        COALESCE(f.player_id, a.source_player_key, p.source_player_key) AS source_player_key,
        COALESCE(f.player_display_name, f.player_name, a.display_name, p.display_name) AS display_name,
        f.position,
        COALESCE(f.current_team, f.team, a.team, p.current_team) AS team,
        f.opponent_team AS opponent,
        f.season,
        f.week,
        @scoring_profile_id AS scoring_profile_id,
        @league_type_id AS league_type_id,
        @roster_format_id AS roster_format_id,
        a.model_run_id,
        a.ranking_version,
        a.pigskin_rank_overall,
        a.pigskin_rank_position,
        a.pigskin_tier,
        a.market_value,
        a.market_value_rank_position,
        a.pigskin_projection,
        a.pigskin_confidence,
        f.fantasy_points_ppr AS actual_points_recent,
        GREATEST(0.0, f.fantasy_points_ppr - COALESCE(f.points_over_role_score, 0.0)) AS expected_points_recent,
        COALESCE(f.points_over_role_score, 0.0) AS points_over_expected_recent,
        f.opportunity_score AS usage_score,
        f.role_quality_score,
        100.0 - COALESCE(f.role_fragility_score, 0.0) AS role_stability_score,
        COALESCE(f.touchdown_dependency_rate, 0.0) * 100.0 AS td_dependency_score,
        COALESCE(f.fantasy_points_per_opportunity, 0.0) * 20.0 AS efficiency_outlier_score,
        GREATEST(0.0, COALESCE(a.pigskin_rank_position, 999) - COALESCE(a.market_value_rank_position, 999)) AS rank_vs_value_gap,
        f.fraud_score AS source_fraud_score,
        f.fraud_label,
        f.fraud_case,
        f.what_would_change_mind,
        f.skill_player_opportunities,
        f.target_share,
        f.wopr,
        f.offense_pct,
        f.touchdowns,
        f.role_fragility_score,
        f.analytical_verdict,
        f.primary_qb_name,
        a.source_freshness_json AS asset_source_freshness_json,
        p.source_freshness_json AS profile_source_freshness_json,
        a.missing_data_flags AS asset_missing_data_flags,
        p.missing_data_flags AS profile_missing_data_flags
    FROM fraud f
    LEFT JOIN assets a
        ON (
            f.player_id IS NOT NULL
            AND a.source_player_key = f.player_id
        )
        OR (
            f.normalized_name = a.normalized_name
            AND f.position = a.position
        )
    LEFT JOIN profiles p
        ON (
            a.player_id_internal IS NOT NULL
            AND p.player_id_internal = a.player_id_internal
        )
        OR (
            f.player_id IS NOT NULL
            AND p.source_player_key = f.player_id
        )
        OR (
            f.normalized_name = p.normalized_name
            AND f.position = p.position
        )
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY f.season, f.week, f.player_id, f.player_name, f.position
        ORDER BY a.market_value DESC, a.pigskin_rank_position ASC
    ) = 1
    ORDER BY f.fraud_score DESC, f.season DESC, f.week DESC
    LIMIT @limit
    """
    return sql, _job_config([
        ("season", "INT64", _clean_int(season)),
        ("week", "INT64", _clean_int(week)),
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("limit", "INT64", _clamp_limit(limit)),
    ])


def build_sleeper_breakout_source_query(
    *,
    project_id: str,
    dataset_id: str,
    season: int | str | None = None,
    week: int | str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int | str | None = None,
) -> tuple[str, bigquery.QueryJobConfig]:
    sql = f"""
    SELECT
        player_id_internal,
        source_player_key,
        sleeper_player_id,
        display_name,
        position,
        team,
        opponent,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        model_run_id,
        ranking_version,
        pigskin_rank_overall,
        pigskin_rank_position,
        pigskin_tier,
        pigskin_projection,
        pigskin_confidence,
        fantasy_points_last_3 AS actual_points_recent,
        fantasy_points_per_game,
        snap_share_last_3,
        target_share_last_3,
        rush_share_last_3,
        targets_last_3,
        carries_last_3,
        receptions_last_3,
        red_zone_opportunities_last_3,
        high_value_touches_last_3,
        usage_trend_score,
        role_growth_score,
        expected_vs_actual_signal AS underperformance_signal,
        rostered_rate,
        IF(COALESCE(available_in_league_flag, FALSE), 100.0, GREATEST(0.0, 100.0 - COALESCE(rostered_rate, 100.0))) AS availability_score,
        matchup_score,
        GREATEST(0.0, COALESCE(rank_vs_market_gap, 0.0)) AS market_discount_score,
        breakout_score AS source_breakout_score,
        candidate_reason,
        evidence_json,
        counterargument,
        snark_hook,
        game_environment_json,
        source_freshness_json,
        missing_data_flags
    FROM `{_table_id(project_id, dataset_id, "compat_sleeper_watch_candidates")}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
        AND (@season IS NULL OR season = @season)
        AND (@week IS NULL OR week = @week)
        AND breakout_score IS NOT NULL
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY COALESCE(player_id_internal, source_player_key, sleeper_player_id, display_name), scoring_profile_id
        ORDER BY breakout_score DESC, streamer_score DESC, display_name ASC
    ) = 1
    ORDER BY breakout_score DESC, streamer_score DESC, display_name ASC
    LIMIT @limit
    """
    return sql, _job_config([
        ("season", "INT64", _clean_int(season)),
        ("week", "INT64", _clean_int(week)),
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("limit", "INT64", _clamp_limit(limit)),
    ])


def calculate_fraud_score(row: dict[str, Any], config: dict[str, Any] | None = None) -> float:
    """Calculate deterministic fraud score from curated row features."""

    weights = (config or FRAUD_BREAKOUT_CONFIG)["fraud"]
    points_over_expected = _bounded_score(_num(row.get("points_over_expected_recent"), 0.0), 0.0, 25.0)
    td_dependency = _bounded_score(_num(row.get("td_dependency_score"), 0.0), 0.0, 100.0)
    usage = _bounded_score(_num(row.get("usage_score"), 0.0), 0.0, 100.0)
    low_usage = max(0.0, 100.0 - usage) if _num(row.get("actual_points_recent"), 0.0) >= 10 else 0.0
    efficiency = _bounded_score(_num(row.get("efficiency_outlier_score"), 0.0), 0.0, 100.0)
    declining_role = _bounded_score(_num(row.get("role_fragility_score"), 0.0), 0.0, 100.0)
    market_hype = _bounded_score(_num(row.get("rank_vs_value_gap"), 0.0), 0.0, 50.0)
    role_instability = max(0.0, 100.0 - _bounded_score(_num(row.get("role_stability_score"), 50.0), 0.0, 100.0))
    score = (
        points_over_expected * weights["points_over_expected_weight"]
        + td_dependency * weights["td_dependency_weight"]
        + low_usage * weights["low_usage_weight"]
        + efficiency * weights["efficiency_outlier_weight"]
        + declining_role * weights["declining_role_weight"]
        + market_hype * weights["market_hype_weight"]
        + role_instability * weights["role_instability_weight"]
    )
    return round(max(0.0, min(100.0, score)), 3)


def calculate_breakout_score(row: dict[str, Any], config: dict[str, Any] | None = None) -> float:
    """Calculate deterministic breakout score from curated row features."""

    weights = (config or FRAUD_BREAKOUT_CONFIG)["breakout"]
    role_growth = _bounded_score(_num(row.get("role_growth_score"), 0.0), 0.0, 100.0)
    usage_trend = _bounded_score(_num(row.get("usage_trend_score"), 0.0), 0.0, 100.0)
    opportunity = _bounded_score(
        _num(row.get("high_value_touches_last_3"), 0.0) * 8.0
        + _num(row.get("targets_last_3"), 0.0) * 2.0
        + _num(row.get("carries_last_3"), 0.0),
        0.0,
        100.0,
    )
    underperformance = _bounded_score(_num(row.get("underperformance_signal"), 0.0), 0.0, 100.0)
    availability = _bounded_score(_num(row.get("availability_score"), 0.0), 0.0, 100.0)
    matchup = _bounded_score(_num(row.get("matchup_score"), 0.0), 0.0, 100.0)
    market_discount = _bounded_score(_num(row.get("market_discount_score"), 0.0), 0.0, 50.0)
    score = (
        role_growth * weights["role_growth_weight"]
        + usage_trend * weights["usage_trend_weight"]
        + opportunity * weights["opportunity_weight"]
        + underperformance * weights["underperformance_weight"]
        + availability * weights["availability_weight"]
        + matchup * weights["matchup_weight"]
        + market_discount * weights["market_discount_weight"]
    )
    return round(max(0.0, min(100.0, score)), 3)


def save_fraud_watch_packets(
    packets: list[dict[str, Any]],
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[str]:
    return _save_packets("fraud_watch_packets", packets, client=client, dataset_id=dataset_id)


def save_sleeper_breakout_packets(
    packets: list[dict[str, Any]],
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[str]:
    return _save_packets("sleeper_breakout_packets", packets, client=client, dataset_id=dataset_id)


def get_fraud_watch_packets(
    *,
    season: int | str | None = None,
    week: int | str | None = None,
    position: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int | str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    return _get_packets(
        "fraud_watch_packets",
        "fraud_score",
        season=season,
        week=week,
        position=position,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=limit,
        client=client,
        dataset_id=dataset_id,
    )


def get_sleeper_breakout_packets(
    *,
    season: int | str | None = None,
    week: int | str | None = None,
    position: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int | str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    return _get_packets(
        "sleeper_breakout_packets",
        "breakout_score",
        season=season,
        week=week,
        position=position,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=limit,
        client=client,
        dataset_id=dataset_id,
    )


def _build_fraud_packet(
    row: dict[str, Any],
    *,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    model_run_id: str | None,
) -> dict[str, Any]:
    fraud_score = calculate_fraud_score(row, FRAUD_BREAKOUT_CONFIG)
    now = _utc_timestamp()
    missing_flags = _fraud_missing_flags(row, model_run_id)
    confidence_score = _confidence_score(fraud_score, missing_flags)
    packet_id = _packet_id(
        "fraud",
        model_run_id,
        row.get("player_id_internal") or row.get("source_player_key") or row.get("display_name"),
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        row.get("season"),
        row.get("week"),
    )
    recommended_take = _fraud_take(row, fraud_score)
    snark_hooks = _fraud_snark_hooks(row, fraud_score)
    packet_json = {
        "identity": _identity(row),
        "ranking_context": _ranking_context(row, model_run_id),
        "fraud_claim": {
            "recommended_take": recommended_take,
            "fraud_score": fraud_score,
            "label": row.get("fraud_label"),
        },
        "evidence": {
            "actual_vs_expected": {
                "actual_points_recent": _num(row.get("actual_points_recent"), None),
                "expected_points_recent": _num(row.get("expected_points_recent"), None),
                "points_over_expected_recent": _num(row.get("points_over_expected_recent"), None),
            },
            "low_volume_production": {
                "usage_score": _num(row.get("usage_score"), None),
                "skill_player_opportunities": _num(row.get("skill_player_opportunities"), None),
                "offense_pct": _num(row.get("offense_pct"), None),
            },
            "td_dependency": _num(row.get("td_dependency_score"), None),
            "efficiency_outliers": _num(row.get("efficiency_outlier_score"), None),
            "declining_role": {
                "role_stability_score": _num(row.get("role_stability_score"), None),
                "role_fragility_score": _num(row.get("role_fragility_score"), None),
            },
            "rank_value_mismatch": {
                "market_hype_score": _num(row.get("rank_vs_value_gap"), None),
                "rank_vs_value_gap": _num(row.get("rank_vs_value_gap"), None),
            },
        },
        "counterargument": _clean_optional(row.get("fraud_case")) or "The production might be real if the role stabilizes.",
        "what_would_change_the_take": _clean_optional(row.get("what_would_change_mind")) or "Better repeatable role evidence would soften the take.",
        "show_framing": {
            "clean_take": recommended_take,
            "confidence_caveat": _confidence_caveat(confidence_score, missing_flags),
            "recommended_script_framing": "Lead with the box-score trap, then prove whether the role actually paid for it.",
        },
        "snark_hooks": snark_hooks,
        "source_metadata": _source_metadata(row, missing_flags, "fraud_watch"),
    }
    return {
        "packet_id": packet_id,
        "model_run_id": model_run_id,
        "ranking_version": row.get("ranking_version"),
        "player_id_internal": row.get("player_id_internal"),
        "source_player_key": row.get("source_player_key"),
        "display_name": row.get("display_name"),
        "position": row.get("position"),
        "team": row.get("team"),
        "season": _int_or_none(row.get("season")),
        "week": _int_or_none(row.get("week")),
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "fraud_score": fraud_score,
        "confidence_score": confidence_score,
        "actual_points_recent": _num(row.get("actual_points_recent"), None),
        "expected_points_recent": _num(row.get("expected_points_recent"), None),
        "points_over_expected_recent": _num(row.get("points_over_expected_recent"), None),
        "usage_score": _num(row.get("usage_score"), None),
        "role_stability_score": _num(row.get("role_stability_score"), None),
        "td_dependency_score": _num(row.get("td_dependency_score"), None),
        "efficiency_outlier_score": _num(row.get("efficiency_outlier_score"), None),
        "market_hype_score": _num(row.get("rank_vs_value_gap"), None),
        "rank_vs_value_gap": _num(row.get("rank_vs_value_gap"), None),
        "recommended_take": recommended_take,
        "packet_json": json.dumps(packet_json, sort_keys=True),
        "packet_text": _packet_text(packet_json, "fraud_claim"),
        "snark_hooks_json": json.dumps(snark_hooks, sort_keys=True),
        "counterargument": packet_json["counterargument"],
        "source_freshness_json": json.dumps(_source_freshness(row, "fraud_watch"), sort_keys=True),
        "missing_data_flags": json.dumps(missing_flags, sort_keys=True),
        "created_at": now,
        "updated_at": now,
        "packet": packet_json,
    }


def _build_breakout_packet(
    row: dict[str, Any],
    *,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    model_run_id: str | None,
) -> dict[str, Any]:
    breakout_score = calculate_breakout_score(row, FRAUD_BREAKOUT_CONFIG)
    now = _utc_timestamp()
    missing_flags = _breakout_missing_flags(row, model_run_id)
    confidence_score = _confidence_score(breakout_score, missing_flags)
    packet_id = _packet_id(
        "breakout",
        model_run_id,
        row.get("player_id_internal") or row.get("source_player_key") or row.get("display_name"),
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        row.get("season"),
        row.get("week"),
    )
    recommended_take = _breakout_take(row, breakout_score)
    snark_hooks = _breakout_snark_hooks(row, breakout_score)
    packet_json = {
        "identity": _identity(row),
        "ranking_context": _ranking_context(row, model_run_id),
        "breakout_claim": {
            "recommended_take": recommended_take,
            "breakout_score": breakout_score,
            "candidate_reason": row.get("candidate_reason"),
        },
        "evidence": {
            "rising_snaps": _num(row.get("snap_share_last_3"), None),
            "rising_target_or_rush_share": {
                "target_share_last_3": _num(row.get("target_share_last_3"), None),
                "rush_share_last_3": _num(row.get("rush_share_last_3"), None),
            },
            "high_value_touches": _num(row.get("high_value_touches_last_3"), None),
            "expected_points_above_actual": _num(row.get("underperformance_signal"), None),
            "roster_market_discount": {
                "rostered_rate": _num(row.get("rostered_rate"), None),
                "availability_score": _num(row.get("availability_score"), None),
                "market_discount_score": _num(row.get("market_discount_score"), None),
            },
            "matchup_context": {
                "opponent": row.get("opponent"),
                "matchup_score": _num(row.get("matchup_score"), None),
                "game_environment_json": row.get("game_environment_json"),
            },
        },
        "counterargument": _clean_optional(row.get("counterargument")) or "Breakouts are fragile until usage growth survives another week.",
        "what_would_change_the_take": "A role snapback, injury news, or market repricing would change the breakout case.",
        "show_framing": {
            "clean_take": recommended_take,
            "confidence_caveat": _confidence_caveat(confidence_score, missing_flags),
            "recommended_script_framing": "Lead with the role-growth signal, then ask whether the market is asleep.",
        },
        "snark_hooks": snark_hooks,
        "source_metadata": _source_metadata(row, missing_flags, "sleeper_breakout"),
    }
    return {
        "packet_id": packet_id,
        "model_run_id": model_run_id,
        "ranking_version": row.get("ranking_version"),
        "player_id_internal": row.get("player_id_internal"),
        "source_player_key": row.get("source_player_key"),
        "display_name": row.get("display_name"),
        "position": row.get("position"),
        "team": row.get("team"),
        "opponent": row.get("opponent"),
        "season": _int_or_none(row.get("season")),
        "week": _int_or_none(row.get("week")),
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "breakout_score": breakout_score,
        "confidence_score": confidence_score,
        "role_growth_score": _num(row.get("role_growth_score"), None),
        "usage_trend_score": _num(row.get("usage_trend_score"), None),
        "opportunity_score": _opportunity_score(row),
        "underperformance_signal": _num(row.get("underperformance_signal"), None),
        "rostered_rate": _num(row.get("rostered_rate"), None),
        "availability_score": _num(row.get("availability_score"), None),
        "matchup_score": _num(row.get("matchup_score"), None),
        "market_discount_score": _num(row.get("market_discount_score"), None),
        "recommended_take": recommended_take,
        "packet_json": json.dumps(packet_json, sort_keys=True),
        "packet_text": _packet_text(packet_json, "breakout_claim"),
        "snark_hooks_json": json.dumps(snark_hooks, sort_keys=True),
        "counterargument": packet_json["counterargument"],
        "source_freshness_json": json.dumps(_source_freshness(row, "sleeper_breakout"), sort_keys=True),
        "missing_data_flags": json.dumps(missing_flags, sort_keys=True),
        "created_at": now,
        "updated_at": now,
        "packet": packet_json,
    }


def _save_packets(
    table_name: str,
    packets: list[dict[str, Any]],
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[str]:
    if not packets:
        return []
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    packet_ids = [packet["packet_id"] for packet in packets]
    delete_sql = f"""
    DELETE FROM `{_table_id(client.project, dataset_id, table_name)}`
    WHERE packet_id IN UNNEST(@packet_ids)
    """
    client.query(
        delete_sql,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ArrayQueryParameter("packet_ids", "STRING", packet_ids)]
        ),
    ).result()
    rows = [_insert_row(packet) for packet in packets]
    errors = client.insert_rows_json(_table_id(client.project, dataset_id, table_name), rows)
    if errors:
        raise RuntimeError(f"Failed to insert {table_name} rows: {errors}")
    return packet_ids


def _get_packets(
    table_name: str,
    score_field: str,
    *,
    season: int | str | None = None,
    week: int | str | None = None,
    position: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int | str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql = f"""
    SELECT *
    FROM `{_table_id(client.project, dataset_id, table_name)}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
        AND (@season IS NULL OR season = @season)
        AND (@week IS NULL OR week = @week)
        AND (@position IS NULL OR position = @position)
    ORDER BY {score_field} DESC, season DESC, week DESC, display_name ASC
    LIMIT @limit
    """
    rows = _query_rows(client, sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("season", "INT64", _clean_int(season)),
        ("week", "INT64", _clean_int(week)),
        ("position", "STRING", _clean_optional(position)),
        ("limit", "INT64", _clamp_limit(limit)),
    ]))
    for row in rows:
        row["packet"] = _parse_json(row.get("packet_json"), {})
    return rows


def _insert_row(packet: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in packet.items() if key != "packet"}


def _fraud_missing_flags(row: dict[str, Any], model_run_id: str | None) -> list[str]:
    flags = set(_json_array(row.get("asset_missing_data_flags")))
    flags.update(_json_array(row.get("profile_missing_data_flags")))
    if not model_run_id:
        flags.add("missing_model_run_id")
    if row.get("expected_points_recent") in (None, ""):
        flags.add("missing_expected_points")
    else:
        flags.add("expected_points_proxy_used")
    if row.get("rank_vs_value_gap") in (None, ""):
        flags.add("missing_rank_value_gap")
    if row.get("td_dependency_score") in (None, ""):
        flags.add("missing_td_dependency")
    return sorted(flags)


def _breakout_missing_flags(row: dict[str, Any], model_run_id: str | None) -> list[str]:
    flags = set(_json_array(row.get("missing_data_flags")))
    if not model_run_id:
        flags.add("missing_model_run_id")
    if row.get("underperformance_signal") in (None, ""):
        flags.add("missing_expected_points")
    if row.get("rostered_rate") in (None, ""):
        flags.add("missing_rostered_rate")
    if row.get("matchup_score") in (None, ""):
        flags.add("missing_matchup_context")
    return sorted(flags)


def _source_freshness(row: dict[str, Any], packet_type: str) -> dict[str, Any]:
    if packet_type == "sleeper_breakout":
        return {
            "compat_sleeper_watch_candidates": _freshness_summary(row.get("source_freshness_json")),
        }
    return {
        "analytics_fraud_watch": {
            "season": row.get("season"),
            "week": row.get("week"),
        },
        "compat_trade_assets_current": _freshness_summary(row.get("asset_source_freshness_json")),
        "compat_player_profiles_current": _freshness_summary(row.get("profile_source_freshness_json")),
    }


def _source_metadata(row: dict[str, Any], missing_flags: list[str], packet_type: str) -> dict[str, Any]:
    sources = ["analytics_fraud_watch", "compat_trade_assets_current", "compat_player_profiles_current"]
    if packet_type == "sleeper_breakout":
        sources = ["compat_sleeper_watch_candidates"]
    return {
        "packet_type": packet_type,
        "sources_used": sources,
        "source_freshness": _source_freshness(row, packet_type),
        "missing_data_flags": missing_flags,
        "config": FRAUD_BREAKOUT_CONFIG,
    }


def _identity(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "player_id_internal": row.get("player_id_internal"),
        "source_player_key": row.get("source_player_key"),
        "sleeper_player_id": row.get("sleeper_player_id"),
        "display_name": row.get("display_name"),
        "position": row.get("position"),
        "team": row.get("team"),
        "opponent": row.get("opponent"),
        "season": row.get("season"),
        "week": row.get("week"),
    }


def _ranking_context(row: dict[str, Any], model_run_id: str | None) -> dict[str, Any]:
    return {
        "model_run_id": model_run_id,
        "ranking_version": row.get("ranking_version"),
        "pigskin_rank_overall": row.get("pigskin_rank_overall"),
        "pigskin_rank_position": row.get("pigskin_rank_position"),
        "pigskin_tier": row.get("pigskin_tier"),
        "pigskin_projection": row.get("pigskin_projection"),
        "pigskin_confidence": row.get("pigskin_confidence"),
    }


def _fraud_take(row: dict[str, Any], score: float) -> str:
    name = row.get("display_name") or "This player"
    label = row.get("fraud_label") or "fraud watch"
    if score >= 70:
        return f"{name} is a full-blown {label}. The points are louder than the role."
    if score >= 50:
        return f"{name} belongs on Fraud Watch. The role needs to catch up before we buy it."
    return f"{name} is a monitor candidate, not a conviction take yet."


def _breakout_take(row: dict[str, Any], score: float) -> str:
    name = row.get("display_name") or "This player"
    if score >= 70:
        return f"{name} is a real breakout target. The usage trend is doing more work than the market."
    if score >= 50:
        return f"{name} is a sleeper watch candidate with enough role growth to matter."
    return f"{name} is a watch-list player, not a victory lap."


def _fraud_snark_hooks(row: dict[str, Any], score: float) -> list[str]:
    name = row.get("display_name") or "This player"
    return [
        f"{name} is asking us to pay steakhouse prices for drive-through role quality.",
        "The box score is yelling. The usage is whispering from another room.",
        f"Fraud score: {score:.1f}. That is not a receipt, that is a warning label.",
    ]


def _breakout_snark_hooks(row: dict[str, Any], score: float) -> list[str]:
    name = row.get("display_name") or "This player"
    return [
        f"{name} is sitting where lazy managers stop scrolling.",
        "The market is late, which is adorable and useful.",
        f"Breakout score: {score:.1f}. That is the kind of signal meatbags call luck two weeks too late.",
    ]


def _packet_text(packet: dict[str, Any], claim_key: str) -> str:
    claim = packet[claim_key]["recommended_take"]
    identity = packet["identity"]
    lines = [
        f"{identity.get('display_name')} ({identity.get('position')}, {identity.get('team')})",
        claim,
        f"Counterargument: {packet['counterargument']}",
        f"What would change it: {packet['what_would_change_the_take']}",
        f"Script frame: {packet['show_framing']['recommended_script_framing']}",
        "Hooks: " + " | ".join(packet["snark_hooks"]),
    ]
    return "\n".join(lines)[:PACKET_TEXT_MAX_CHARS]


def _confidence_score(score: float, missing_flags: list[str]) -> float:
    missing_penalty = min(0.35, len(missing_flags) * 0.025)
    score_bonus = min(0.25, score / 400.0)
    return round(max(0.2, min(0.95, 0.55 + score_bonus - missing_penalty)), 3)


def _confidence_caveat(confidence: float, missing_flags: list[str]) -> str:
    if missing_flags:
        return f"Confidence is capped by missing data: {', '.join(missing_flags[:6])}."
    if confidence >= 0.75:
        return "Confidence is strong for a deterministic packet."
    return "Confidence is moderate until the next role sample confirms it."


def _opportunity_score(row: dict[str, Any]) -> float:
    return _bounded_score(
        _num(row.get("high_value_touches_last_3"), 0.0) * 8.0
        + _num(row.get("targets_last_3"), 0.0) * 2.0
        + _num(row.get("carries_last_3"), 0.0),
        0.0,
        100.0,
    )


def _latest_model_run_id(
    *,
    client: Any,
    dataset_id: str,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
) -> str | None:
    try:
        row = get_latest_model_run(
            client=client,
            dataset_id=dataset_id,
            run_type="pigskin_rankings",
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            status="complete",
        )
        return row.get("model_run_id") if row else None
    except Exception:
        return None


def _save_delete_query(client: Any, dataset_id: str, table_name: str, packet_ids: list[str]) -> tuple[str, bigquery.QueryJobConfig]:
    sql = f"""
    DELETE FROM `{_table_id(client.project, dataset_id, table_name)}`
    WHERE packet_id IN UNNEST(@packet_ids)
    """
    return sql, bigquery.QueryJobConfig(
        query_parameters=[bigquery.ArrayQueryParameter("packet_ids", "STRING", packet_ids)]
    )


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


def _clamp_limit(value: int | str | None) -> int:
    try:
        parsed = int(value) if value is not None else DEFAULT_PACKET_LIMIT
    except (TypeError, ValueError):
        parsed = DEFAULT_PACKET_LIMIT
    return max(1, min(MAX_PACKET_LIMIT, parsed))


def _clean_int(value: int | str | None) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _clean_optional(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


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


def _bounded_score(value: float | None, minimum: float, maximum: float) -> float:
    if value is None:
        return 0.0
    if maximum <= minimum:
        return 0.0
    return round(max(0.0, min(100.0, ((value - minimum) / (maximum - minimum)) * 100.0)), 3)


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
    return {key: parsed[key] for key in allowed_keys if key in parsed and parsed[key] not in (None, "")}


def _packet_id(*parts: Any) -> str:
    raw = "|".join(str(part or "") for part in parts)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    if not IDENTIFIER_RE.match(table_name):
        raise ValueError(f"Unsafe BigQuery table name: {table_name}")
    return f"{project_id}.{dataset_id}.{table_name}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build deterministic segment packets.")
    parser.add_argument("--packet-type", choices=("fraud-watch", "sleeper-breakout"), required=True)
    parser.add_argument("--season")
    parser.add_argument("--week")
    parser.add_argument("--scoring-profile", default=DEFAULT_SCORING_PROFILE)
    parser.add_argument("--league-type", default=DEFAULT_LEAGUE_TYPE)
    parser.add_argument("--roster-format", default=DEFAULT_ROSTER_FORMAT)
    parser.add_argument("--limit", default=DEFAULT_PACKET_LIMIT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.packet_type == "fraud-watch":
        packets = build_fraud_watch_packets(
            season=args.season,
            week=args.week,
            scoring_profile_id=args.scoring_profile,
            league_type_id=args.league_type,
            roster_format_id=args.roster_format,
            limit=args.limit,
        )
        if args.dry_run:
            print(json.dumps([packet["packet"] for packet in packets], indent=2, sort_keys=True))
            return
        print(json.dumps(save_fraud_watch_packets(packets), sort_keys=True))
        return

    packets = build_sleeper_breakout_packets(
        season=args.season,
        week=args.week,
        scoring_profile_id=args.scoring_profile,
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        limit=args.limit,
    )
    if args.dry_run:
        print(json.dumps([packet["packet"] for packet in packets], indent=2, sort_keys=True))
        return
    print(json.dumps(save_sleeper_breakout_packets(packets), sort_keys=True))


if __name__ == "__main__":
    main()
