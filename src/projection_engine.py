"""Deterministic baseline projection engine.

This module creates versioned weekly, rest-of-season, and dynasty projection
outputs from curated marts only. It does not call an LLM or train a model.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
from datetime import datetime, timezone
from typing import Any

from google.cloud import bigquery

from src.load import get_bigquery_client
from src.model_runs import (
    create_model_run,
    create_source_freshness_snapshot,
    mark_model_run_complete,
    mark_model_run_failed,
)


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_SCORING_PROFILE = "ppr"
DEFAULT_LEAGUE_TYPE = "redraft"
DEFAULT_ROSTER_FORMAT = "one_qb"
DEFAULT_LIMIT = 250
MAX_LIMIT = 1000
MODEL_NAME = "baseline_projection_engine"
MODEL_VERSION = "v1"
RANK_SOURCE = "baseline_projection_engine_v1"
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("PROJECTION_ENGINE_MAX_BYTES_BILLED", "1000000000"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")

PROJECTION_SOURCE_TABLES = (
    "analytics_player_weekly_truth",
    "analytics_player_fantasy_points_by_profile",
    "compat_player_profiles_current",
    "compat_trade_player_history",
    "compat_trade_assets_current",
    "compat_sleeper_watch_candidates",
    "fraud_watch_packets",
    "sleeper_breakout_packets",
)

PROJECTION_CONFIG: dict[str, Any] = {
    "weekly": {
        "feature_config_version_id": "baseline_weekly_v1",
        "recent_points_weight": 0.52,
        "profile_points_weight": 0.18,
        "pigskin_projection_weight": 0.12,
        "role_weight": 0.08,
        "trend_weight": 0.05,
        "fraud_penalty_weight": 0.03,
        "breakout_weight": 0.02,
    },
    "ros": {
        "feature_config_version_id": "baseline_ros_v1",
        "weekly_baseline_weight": 0.70,
        "role_stability_weight": 0.12,
        "trend_weight": 0.08,
        "risk_penalty_weight": 0.06,
        "format_weight": 0.04,
    },
    "dynasty": {
        "feature_config_version_id": "baseline_dynasty_v1",
        "year_1_weight": 1.00,
        "year_2_weight": 0.65,
        "year_3_weight": 0.45,
        "age_curve_weight": 0.18,
        "market_value_weight": 0.15,
        "role_weight": 0.10,
        "tier_weight": 0.07,
    },
    "scoring_profile_factors": {
        "standard": 0.94,
        "half_ppr": 0.98,
        "ppr": 1.00,
    },
    "position_baselines": {
        "QB": 16.0,
        "RB": 9.0,
        "WR": 9.0,
        "TE": 6.5,
    },
    "replacement_rank": {
        "one_qb": {"QB": 12, "RB": 30, "WR": 36, "TE": 12},
        "superflex": {"QB": 24, "RB": 30, "WR": 36, "TE": 12},
        "two_qb": {"QB": 24, "RB": 30, "WR": 36, "TE": 12},
        "best_ball": {"QB": 18, "RB": 42, "WR": 54, "TE": 18},
    },
}


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def create_projection_model_run(
    horizon: str,
    season: int,
    week: int,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    feature_config_version_id: str | None = None,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, str]:
    """Create source freshness and a running model-run row."""

    horizon = _normalize_horizon(horizon)
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    feature_config_version_id = feature_config_version_id or PROJECTION_CONFIG[horizon]["feature_config_version_id"]
    source_freshness_snapshot_id = create_source_freshness_snapshot(
        client=client,
        dataset_id=dataset_id,
        source_table_names=PROJECTION_SOURCE_TABLES,
        max_value_table_names=PROJECTION_SOURCE_TABLES,
    )
    model_run_id = create_model_run(
        client=client,
        dataset_id=dataset_id,
        run_type=f"{horizon}_projection",
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        feature_config_version_id=feature_config_version_id,
        source_freshness_snapshot_id=source_freshness_snapshot_id,
        created_by="projection_engine",
        notes="Deterministic baseline projection run.",
    )
    return {
        "model_run_id": model_run_id,
        "feature_config_version_id": feature_config_version_id,
        "source_freshness_snapshot_id": source_freshness_snapshot_id,
    }


def build_weekly_projection_rows(
    season: int,
    week: int,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    limit: int | str | None = None,
) -> list[dict[str, Any]]:
    """Build weekly projection rows from curated compatibility objects."""

    _require_model_run_id(model_run_id)
    rows = _fetch_projection_features(
        client=client,
        dataset_id=dataset_id,
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=limit,
    )
    projected = [
        _weekly_projection_row(
            row,
            season=season,
            week=week,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            model_run_id=model_run_id,
        )
        for row in rows
    ]
    _apply_replacement_values(projected, roster_format_id, scoring_profile_id)
    return projected


def build_ros_projection_rows(
    season: int,
    week: int,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    limit: int | str | None = None,
) -> list[dict[str, Any]]:
    """Build rest-of-season projection rows from curated compatibility objects."""

    _require_model_run_id(model_run_id)
    rows = _fetch_projection_features(
        client=client,
        dataset_id=dataset_id,
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=limit,
    )
    projected = [
        _ros_projection_row(
            row,
            as_of_season=season,
            as_of_week=week,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            model_run_id=model_run_id,
        )
        for row in rows
    ]
    _apply_replacement_values(projected, roster_format_id, scoring_profile_id)
    return projected


def build_dynasty_projection_rows(
    season: int,
    week: int,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = "dynasty",
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    limit: int | str | None = None,
) -> list[dict[str, Any]]:
    """Build dynasty projection rows from curated compatibility objects."""

    _require_model_run_id(model_run_id)
    rows = _fetch_projection_features(
        client=client,
        dataset_id=dataset_id,
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=limit,
    )
    return [
        _dynasty_projection_row(
            row,
            as_of_season=season,
            as_of_week=week,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            model_run_id=model_run_id,
        )
        for row in rows
    ]


def calculate_weekly_projection(
    player_features: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Calculate one transparent weekly projection."""

    config = config or PROJECTION_CONFIG
    weekly_config = config["weekly"]
    position = str(player_features.get("position") or "").upper()
    scoring_profile_id = str(player_features.get("scoring_profile_id") or DEFAULT_SCORING_PROFILE)
    recent_points = _first_number(
        player_features.get("recent_points_per_game"),
        player_features.get("profile_fantasy_points_per_game"),
        player_features.get("fantasy_points_last_3"),
        config["position_baselines"].get(position, 7.0),
    )
    profile_points = _first_number(
        player_features.get("fantasy_points_last_3"),
        player_features.get("fantasy_points_last_5"),
        recent_points,
    )
    pigskin_projection = _first_number(player_features.get("pigskin_projection"), recent_points)
    role_score = _role_score(player_features)
    trend_score = _trend_score(player_features)
    fraud_risk_score = _clamp(_num(player_features.get("fraud_risk_score"), 0.0), 0.0, 100.0)
    breakout_score = _clamp(_num(player_features.get("breakout_score"), 0.0), 0.0, 100.0)
    scoring_factor = config["scoring_profile_factors"].get(scoring_profile_id, 1.0)
    superflex_factor = _roster_format_factor(player_features)

    mean = (
        recent_points * weekly_config["recent_points_weight"]
        + profile_points * weekly_config["profile_points_weight"]
        + pigskin_projection * weekly_config["pigskin_projection_weight"]
        + (role_score / 100.0) * recent_points * weekly_config["role_weight"]
        + (trend_score / 100.0) * recent_points * weekly_config["trend_weight"]
        - (fraud_risk_score / 100.0) * recent_points * weekly_config["fraud_penalty_weight"]
        + (breakout_score / 100.0) * recent_points * weekly_config["breakout_weight"]
    )
    mean = max(0.0, mean * scoring_factor * superflex_factor)
    risk_score = _risk_score(player_features, fraud_risk_score, role_score)
    distribution = calculate_projection_distribution_placeholder(mean, risk_score)
    confidence_score = _confidence_score(risk_score, player_features)
    return {
        "projected_points_mean": round(mean, 3),
        "projected_points_median": distribution["median"],
        "projected_points_floor": distribution["floor"],
        "projected_points_ceiling": distribution["ceiling"],
        "confidence_score": confidence_score,
        "risk_score": risk_score,
        "role_score": round(role_score, 3),
        "trend_score": round(trend_score, 3),
        "fraud_risk_score": round(fraud_risk_score, 3),
        "breakout_score": round(breakout_score, 3),
        "missing_data_flags": _projection_missing_flags(player_features),
    }


def calculate_ros_projection(
    player_features: dict[str, Any],
    schedule_context: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Calculate one transparent rest-of-season projection."""

    weekly = calculate_weekly_projection(player_features, config)
    as_of_week = _int_or_default(schedule_context.get("as_of_week"), 1)
    remaining_games = max(0, _int_or_default(schedule_context.get("regular_season_weeks"), 17) - as_of_week)
    position_risk = _position_risk(player_features.get("position"))
    projected_games = max(0.0, remaining_games * (1.0 - weekly["risk_score"] / 250.0))
    ppg = weekly["projected_points_mean"] * (1.0 - position_risk / 500.0)
    total = ppg * projected_games
    return {
        "remaining_games": remaining_games,
        "projected_points_total": round(total, 3),
        "projected_points_per_game": round(ppg, 3),
        "projected_points_floor": round(weekly["projected_points_floor"] * projected_games, 3),
        "projected_points_ceiling": round(weekly["projected_points_ceiling"] * projected_games, 3),
        "projected_games_played": round(projected_games, 3),
        "confidence_score": weekly["confidence_score"],
        "risk_score": weekly["risk_score"],
        "role_score": weekly["role_score"],
        "trend_score": weekly["trend_score"],
        "missing_data_flags": weekly["missing_data_flags"],
    }


def calculate_dynasty_projection(
    player_profile: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Calculate one transparent dynasty value projection."""

    config = config or PROJECTION_CONFIG
    weekly = calculate_weekly_projection(player_profile, config)
    age_curve = _age_curve_adjustment(player_profile)
    lifecycle = _position_lifecycle_adjustment(player_profile)
    rookie = _rookie_or_prospect_adjustment(player_profile)
    stability = _contract_or_team_stability_adjustment(player_profile)
    market_value = _num(player_profile.get("market_value"), 0.0) / 1000.0
    dynasty_league_factor = 1.08 if player_profile.get("league_type_id") == "dynasty" else 1.0
    year_1 = max(0.0, weekly["projected_points_mean"] * 17.0 + market_value * 0.25)
    year_2 = max(0.0, year_1 * (1.0 + age_curve + lifecycle + rookie + stability) * 0.82)
    year_3 = max(0.0, year_2 * (1.0 + age_curve + lifecycle + stability) * 0.74)
    total = (year_1 + year_2 * 0.65 + year_3 * 0.45) * dynasty_league_factor
    risk_score = min(100.0, weekly["risk_score"] + max(0.0, -age_curve * 100.0))
    return {
        "year_1_value": round(year_1, 3),
        "year_2_value": round(year_2, 3),
        "year_3_value": round(year_3, 3),
        "total_dynasty_value": round(total, 3),
        "age_curve_adjustment": round(age_curve, 3),
        "position_lifecycle_adjustment": round(lifecycle, 3),
        "rookie_or_prospect_adjustment": round(rookie, 3),
        "contract_or_team_stability_adjustment": round(stability, 3),
        "confidence_score": _confidence_score(risk_score, player_profile),
        "risk_score": round(risk_score, 3),
        "role_score": weekly["role_score"],
        "trend_score": weekly["trend_score"],
        "missing_data_flags": weekly["missing_data_flags"],
    }


def calculate_projection_distribution_placeholder(mean: float, risk_score: float) -> dict[str, float]:
    risk = _clamp(_num(risk_score, 50.0), 0.0, 100.0)
    spread = 0.18 + risk / 250.0
    return {
        "median": round(max(0.0, mean * 0.97), 3),
        "floor": round(max(0.0, mean * (1.0 - spread)), 3),
        "ceiling": round(max(0.0, mean * (1.0 + spread * 1.35)), 3),
    }


def calculate_replacement_value_placeholder(
    rows: list[dict[str, Any]],
    roster_format_id: str,
    scoring_profile_id: str,
) -> dict[str, float]:
    """Return replacement baselines by position for the given row set."""

    del scoring_profile_id
    rank_map = PROJECTION_CONFIG["replacement_rank"].get(
        roster_format_id,
        PROJECTION_CONFIG["replacement_rank"][DEFAULT_ROSTER_FORMAT],
    )
    baselines: dict[str, float] = {}
    for position, replacement_rank in rank_map.items():
        values = sorted(
            (_projection_value(row) for row in rows if row.get("position") == position),
            reverse=True,
        )
        if not values:
            baselines[position] = PROJECTION_CONFIG["position_baselines"].get(position, 0.0)
        else:
            baselines[position] = values[min(replacement_rank - 1, len(values) - 1)]
    return baselines


def write_projection_rows(
    rows: list[dict[str, Any]],
    *,
    horizon: str,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, int]:
    """Write projection rows and current rankings for one model run."""

    if not rows:
        return {"projection_rows": 0, "ranking_rows": 0}
    _ensure_rows_have_model_run_id(rows)
    horizon = _normalize_horizon(horizon)
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    model_run_id = rows[0]["model_run_id"]
    table_name = _projection_table_name(horizon)
    delete_sql = f"""
    DELETE FROM `{_table_id(client.project, dataset_id, table_name)}`
    WHERE model_run_id = @model_run_id
    """
    client.query(delete_sql, job_config=_job_config([("model_run_id", "STRING", model_run_id)])).result()
    errors = client.insert_rows_json(_table_id(client.project, dataset_id, table_name), [_strip_runtime_fields(row) for row in rows])
    if errors:
        raise RuntimeError(f"Failed to insert {horizon} projection rows: {errors}")

    ranking_rows = build_projection_rankings(rows)
    delete_rankings_sql = f"""
    DELETE FROM `{_table_id(client.project, dataset_id, "projection_rankings_current")}`
    WHERE model_run_id = @model_run_id
        AND projection_horizon = @projection_horizon
    """
    client.query(delete_rankings_sql, job_config=_job_config([
        ("model_run_id", "STRING", model_run_id),
        ("projection_horizon", "STRING", horizon),
    ])).result()
    ranking_errors = client.insert_rows_json(
        _table_id(client.project, dataset_id, "projection_rankings_current"),
        ranking_rows,
    )
    if ranking_errors:
        raise RuntimeError(f"Failed to insert projection ranking rows: {ranking_errors}")
    return {"projection_rows": len(rows), "ranking_rows": len(ranking_rows)}


def build_projection_rankings(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build current ranking rows from projection outputs."""

    sorted_rows = sorted(rows, key=_projection_value, reverse=True)
    position_counts: dict[str, int] = {}
    ranking_rows = []
    for overall_rank, row in enumerate(sorted_rows, start=1):
        position = row.get("position") or "UNK"
        position_counts[position] = position_counts.get(position, 0) + 1
        ranking_rows.append({
            "model_run_id": row["model_run_id"],
            "projection_horizon": row["projection_horizon"],
            "player_id_internal": row.get("player_id_internal"),
            "display_name": row.get("display_name"),
            "position": row.get("position"),
            "team": row.get("team"),
            "season": row.get("season"),
            "week": row.get("week"),
            "as_of_season": row.get("as_of_season"),
            "as_of_week": row.get("as_of_week"),
            "scoring_profile_id": row["scoring_profile_id"],
            "league_type_id": row["league_type_id"],
            "roster_format_id": row["roster_format_id"],
            "rank_overall": overall_rank,
            "rank_position": position_counts[position],
            "tier": _tier(position_counts[position], row["projection_horizon"]),
            "projected_points_or_value": _projection_value(row),
            "replacement_value": row.get("replacement_value"),
            "confidence_score": row.get("confidence_score"),
            "risk_score": row.get("risk_score"),
            "rank_source": row.get("rank_source", RANK_SOURCE),
            "created_at": _utc_timestamp(),
        })
    return ranking_rows


def run_projection(
    *,
    horizon: str,
    season: int,
    week: int,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    feature_config_version_id: str | None = None,
    dry_run: bool = False,
    limit: int | str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    """Run a deterministic projection build."""

    horizon = _normalize_horizon(horizon)
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    run_context = {
        "model_run_id": "dry-run",
        "feature_config_version_id": feature_config_version_id or PROJECTION_CONFIG[horizon]["feature_config_version_id"],
        "source_freshness_snapshot_id": "dry-run",
    }
    if not dry_run:
        run_context = create_projection_model_run(
            horizon,
            season,
            week,
            scoring_profile_id,
            league_type_id,
            roster_format_id,
            feature_config_version_id,
            client=client,
            dataset_id=dataset_id,
        )

    try:
        rows = _build_rows_for_horizon(
            horizon=horizon,
            season=season,
            week=week,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            model_run_id=run_context["model_run_id"],
            client=client,
            dataset_id=dataset_id,
            limit=limit,
        )
        rankings = build_projection_rankings(rows)
        result = {
            "model_run_id": run_context["model_run_id"],
            "source_freshness_snapshot_id": run_context["source_freshness_snapshot_id"],
            "feature_config_version_id": run_context["feature_config_version_id"],
            "horizon": horizon,
            "projection_rows": len(rows),
            "ranking_rows": len(rankings),
            "rows": rows if dry_run else [],
            "rankings": rankings if dry_run else [],
        }
        if not dry_run:
            write_counts = write_projection_rows(rows, horizon=horizon, client=client, dataset_id=dataset_id)
            mark_model_run_complete(
                run_context["model_run_id"],
                client=client,
                dataset_id=dataset_id,
                notes=json.dumps(write_counts, sort_keys=True),
            )
            result.update(write_counts)
        return result
    except Exception as exc:
        if not dry_run:
            mark_model_run_failed(
                run_context["model_run_id"],
                str(exc),
                client=client,
                dataset_id=dataset_id,
            )
        raise


def _fetch_projection_features(
    *,
    client: Any | None,
    dataset_id: str | None,
    season: int,
    week: int,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    limit: int | str | None,
) -> list[dict[str, Any]]:
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_projection_feature_query(
        project_id=client.project,
        dataset_id=dataset_id,
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=limit,
    )
    return _query_rows(client, sql, job_config)


def build_projection_feature_query(
    *,
    project_id: str,
    dataset_id: str,
    season: int,
    week: int,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    limit: int | str | None = None,
) -> tuple[str, bigquery.QueryJobConfig]:
    """Build the safe feature query used by all projection horizons."""

    sql = f"""
    WITH history AS (
        SELECT *
        FROM `{_table_id(project_id, dataset_id, "compat_trade_player_history")}`
        WHERE scoring_profile_id = @scoring_profile_id
            AND season <= @season
            AND (season < @season OR week <= @week)
    ),
    recent AS (
        SELECT
            COALESCE(player_id_internal, source_player_key) AS player_key,
            ARRAY_AGG(player_id_internal IGNORE NULLS ORDER BY season DESC, week DESC LIMIT 1)[SAFE_OFFSET(0)] AS player_id_internal,
            ARRAY_AGG(source_player_key IGNORE NULLS ORDER BY season DESC, week DESC LIMIT 1)[SAFE_OFFSET(0)] AS source_player_key,
            ARRAY_AGG(player_display_name IGNORE NULLS ORDER BY season DESC, week DESC LIMIT 1)[SAFE_OFFSET(0)] AS display_name,
            ARRAY_AGG(position IGNORE NULLS ORDER BY season DESC, week DESC LIMIT 1)[SAFE_OFFSET(0)] AS position,
            ARRAY_AGG(team IGNORE NULLS ORDER BY season DESC, week DESC LIMIT 1)[SAFE_OFFSET(0)] AS team,
            ARRAY_AGG(opponent IGNORE NULLS ORDER BY season DESC, week DESC LIMIT 1)[SAFE_OFFSET(0)] AS opponent,
            AVG(IF(recency_order <= 3, total_fantasy_points, NULL)) AS recent_points_per_game,
            AVG(IF(recency_order <= 5, total_fantasy_points, NULL)) AS fantasy_points_last_5,
            AVG(IF(recency_order <= 8, total_fantasy_points, NULL)) AS fantasy_points_last_8,
            AVG(IF(recency_order <= 3, snap_share, NULL)) AS snap_share_last_3,
            AVG(IF(recency_order <= 3, target_share, NULL)) AS target_share_last_3,
            AVG(IF(recency_order <= 3, rush_share, NULL)) AS rush_share_last_3,
            AVG(IF(recency_order <= 3, high_value_touches, NULL)) AS high_value_touches_last_3,
            AVG(IF(recency_order <= 3, red_zone_opportunities, NULL)) AS red_zone_opportunities_last_3,
            AVG(IF(recency_order <= 3, role_quality_from_json, NULL)) AS role_quality_score,
            AVG(IF(recency_order <= 3, role_fragility_from_json, NULL)) AS role_fragility_score,
            AVG(IF(recency_order <= 3, total_epa_from_json, NULL)) AS total_epa_recent,
            ARRAY_AGG(game_environment_json IGNORE NULLS ORDER BY season DESC, week DESC LIMIT 1)[SAFE_OFFSET(0)] AS game_environment_json,
            ARRAY_AGG(source_freshness_json IGNORE NULLS ORDER BY season DESC, week DESC LIMIT 1)[SAFE_OFFSET(0)] AS history_source_freshness_json,
            ARRAY_AGG(missing_data_flags IGNORE NULLS ORDER BY season DESC, week DESC LIMIT 1)[SAFE_OFFSET(0)] AS history_missing_data_flags
        FROM (
            SELECT
                h.*,
                SAFE_CAST(JSON_VALUE(h.epa_summary_json, '$.total_epa') AS FLOAT64) AS total_epa_from_json,
                SAFE_CAST(JSON_VALUE(h.epa_summary_json, '$.role_quality_score') AS FLOAT64) AS role_quality_from_json,
                SAFE_CAST(JSON_VALUE(h.epa_summary_json, '$.role_fragility_score') AS FLOAT64) AS role_fragility_from_json
            FROM history h
        )
        WHERE recency_order <= 8
        GROUP BY player_key
    ),
    profiles AS (
        SELECT *
        FROM (
            SELECT
                p.*,
                ROW_NUMBER() OVER (
                    PARTITION BY COALESCE(player_id_internal, source_player_key), scoring_profile_id
                    ORDER BY as_of_season DESC, as_of_week DESC, refreshed_at DESC
                ) AS rn
            FROM `{_table_id(project_id, dataset_id, "compat_player_profiles_current")}` p
            WHERE scoring_profile_id = @scoring_profile_id
        )
        WHERE rn = 1
    ),
    assets AS (
        SELECT *
        FROM (
            SELECT
                a.*,
                ROW_NUMBER() OVER (
                    PARTITION BY COALESCE(player_id_internal, source_player_key), scoring_profile_id, league_type_id, roster_format_id
                    ORDER BY market_snapshot_date DESC, updated_at DESC
                ) AS rn
            FROM `{_table_id(project_id, dataset_id, "compat_trade_assets_current")}` a
            WHERE scoring_profile_id = @scoring_profile_id
                AND league_type_id = @league_type_id
                AND roster_format_id = @roster_format_id
        )
        WHERE rn = 1
    ),
    fraud AS (
        SELECT *
        FROM (
            SELECT
                f.*,
                ROW_NUMBER() OVER (
                    PARTITION BY COALESCE(player_id_internal, source_player_key, display_name)
                    ORDER BY season DESC, week DESC, updated_at DESC
                ) AS rn
            FROM `{_table_id(project_id, dataset_id, "fraud_watch_packets")}` f
            WHERE season <= @season
                AND (season < @season OR week <= @week)
                AND scoring_profile_id = @scoring_profile_id
                AND league_type_id = @league_type_id
                AND roster_format_id = @roster_format_id
        )
        WHERE rn = 1
    ),
    breakout AS (
        SELECT *
        FROM (
            SELECT
                b.*,
                ROW_NUMBER() OVER (
                    PARTITION BY COALESCE(player_id_internal, source_player_key, display_name)
                    ORDER BY season DESC, week DESC, updated_at DESC
                ) AS rn
            FROM `{_table_id(project_id, dataset_id, "sleeper_breakout_packets")}` b
            WHERE season <= @season
                AND (season < @season OR week <= @week)
                AND scoring_profile_id = @scoring_profile_id
                AND league_type_id = @league_type_id
                AND roster_format_id = @roster_format_id
        )
        WHERE rn = 1
    )
    SELECT
        COALESCE(r.player_id_internal, p.player_id_internal, a.player_id_internal) AS player_id_internal,
        COALESCE(r.source_player_key, p.source_player_key, a.source_player_key) AS source_player_key,
        COALESCE(r.display_name, p.display_name, a.display_name) AS display_name,
        COALESCE(r.position, p.position, a.position) AS position,
        COALESCE(r.team, p.current_team, a.team) AS team,
        r.opponent,
        @season AS season,
        @week AS week,
        @scoring_profile_id AS scoring_profile_id,
        @league_type_id AS league_type_id,
        @roster_format_id AS roster_format_id,
        r.recent_points_per_game,
        p.fantasy_points_per_game_current_season AS profile_fantasy_points_per_game,
        p.fantasy_points_last_3,
        COALESCE(p.fantasy_points_last_5, r.fantasy_points_last_5) AS fantasy_points_last_5,
        COALESCE(p.fantasy_points_last_8, r.fantasy_points_last_8) AS fantasy_points_last_8,
        COALESCE(p.snap_share_last_3, r.snap_share_last_3) AS snap_share_last_3,
        COALESCE(p.target_share_last_3, r.target_share_last_3) AS target_share_last_3,
        COALESCE(p.rush_share_last_3, r.rush_share_last_3) AS rush_share_last_3,
        COALESCE(p.high_value_touches_last_3, r.high_value_touches_last_3) AS high_value_touches_last_3,
        COALESCE(p.red_zone_opportunities_last_3, r.red_zone_opportunities_last_3) AS red_zone_opportunities_last_3,
        COALESCE(r.role_quality_score, SAFE_CAST(JSON_VALUE(p.role_summary_json, '$.role_quality_score') AS FLOAT64)) AS role_quality_score,
        COALESCE(r.role_fragility_score, SAFE_CAST(JSON_VALUE(p.role_summary_json, '$.role_fragility_score') AS FLOAT64)) AS role_fragility_score,
        r.total_epa_recent,
        p.age,
        p.rookie_year,
        p.active_status,
        p.bye_week,
        COALESCE(a.market_value, SAFE_CAST(NULL AS INT64)) AS market_value,
        a.risk_adjusted_trade_value,
        COALESCE(a.dynasty_value_placeholder, 0.0) AS dynasty_value_placeholder,
        COALESCE(a.replacement_value_estimate, 0.0) AS asset_replacement_value,
        COALESCE(a.pigskin_rank_overall, p.pigskin_rank_overall) AS pigskin_rank_overall,
        COALESCE(a.pigskin_rank_position, p.pigskin_rank_position) AS pigskin_rank_position,
        COALESCE(a.pigskin_tier, p.pigskin_tier) AS pigskin_tier,
        COALESCE(a.pigskin_projection, p.pigskin_projection) AS pigskin_projection,
        COALESCE(a.pigskin_confidence, p.pigskin_confidence) AS pigskin_confidence,
        COALESCE(f.fraud_score, a.pigskin_fraud_risk_score, 0.0) AS fraud_risk_score,
        COALESCE(b.breakout_score, a.pigskin_breakout_score, 0.0) AS breakout_score,
        r.game_environment_json,
        TO_JSON_STRING(STRUCT(
            r.history_source_freshness_json AS history_source,
            p.source_freshness_json AS profile_source,
            a.source_freshness_json AS asset_source,
            f.source_freshness_json AS fraud_packet_source,
            b.source_freshness_json AS breakout_packet_source
        )) AS source_freshness_json,
        TO_JSON_STRING(ARRAY(
            SELECT DISTINCT flag
            FROM UNNEST(ARRAY_CONCAT(
                IF(COALESCE(r.player_id_internal, p.player_id_internal, a.player_id_internal) IS NULL, ['missing_player_id_internal'], []),
                IF(r.recent_points_per_game IS NULL, ['missing_recent_points'], []),
                IF(p.player_id_internal IS NULL AND p.source_player_key IS NULL, ['missing_profile_context'], []),
                IF(a.player_id_internal IS NULL AND a.source_player_key IS NULL, ['missing_trade_asset_context'], []),
                IF(f.packet_id IS NULL, ['missing_fraud_packet'], []),
                IF(b.packet_id IS NULL, ['missing_breakout_packet'], []),
                IF(r.game_environment_json IS NULL, ['missing_game_environment'], []),
                IF(p.missing_data_flags IS NOT NULL AND p.missing_data_flags != '[]', ['profile_missing_flags_present'], []),
                IF(a.missing_data_flags IS NOT NULL AND a.missing_data_flags != '[]', ['asset_missing_flags_present'], [])
            )) AS flag
            WHERE flag IS NOT NULL
            ORDER BY flag
        )) AS missing_data_flags
    FROM recent r
    LEFT JOIN profiles p
        ON COALESCE(r.player_id_internal, r.source_player_key) = COALESCE(p.player_id_internal, p.source_player_key)
    LEFT JOIN assets a
        ON COALESCE(r.player_id_internal, r.source_player_key) = COALESCE(a.player_id_internal, a.source_player_key)
    LEFT JOIN fraud f
        ON COALESCE(r.player_id_internal, r.source_player_key, r.display_name) = COALESCE(f.player_id_internal, f.source_player_key, f.display_name)
    LEFT JOIN breakout b
        ON COALESCE(r.player_id_internal, r.source_player_key, r.display_name) = COALESCE(b.player_id_internal, b.source_player_key, b.display_name)
    WHERE COALESCE(r.position, p.position, a.position) IN ('QB', 'RB', 'WR', 'TE')
    ORDER BY r.recent_points_per_game DESC
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


def _weekly_projection_row(
    row: dict[str, Any],
    *,
    season: int,
    week: int,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    model_run_id: str,
) -> dict[str, Any]:
    features = dict(row)
    features.update({
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
    })
    projection = calculate_weekly_projection(features)
    now = _utc_timestamp()
    return {
        "model_run_id": model_run_id,
        "player_id_internal": row.get("player_id_internal"),
        "source_player_key": row.get("source_player_key"),
        "display_name": row.get("display_name"),
        "position": row.get("position"),
        "team": row.get("team"),
        "opponent": row.get("opponent"),
        "season": season,
        "week": week,
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "projection_horizon": "weekly",
        "projected_points_mean": projection["projected_points_mean"],
        "projected_points_median": projection["projected_points_median"],
        "projected_points_floor": projection["projected_points_floor"],
        "projected_points_ceiling": projection["projected_points_ceiling"],
        "projected_stat_json": _projected_stat_json(row, projection),
        "usage_projection_json": _usage_projection_json(row),
        "efficiency_projection_json": _efficiency_projection_json(row),
        "touchdown_projection_json": _touchdown_projection_json(row),
        "confidence_score": projection["confidence_score"],
        "risk_score": projection["risk_score"],
        "role_score": projection["role_score"],
        "trend_score": projection["trend_score"],
        "fraud_risk_score": projection["fraud_risk_score"],
        "breakout_score": projection["breakout_score"],
        "replacement_value": 0.0,
        "rank_source": RANK_SOURCE,
        "source_freshness_json": _source_freshness_json(row),
        "missing_data_flags": json.dumps(projection["missing_data_flags"], sort_keys=True),
        "created_at": now,
        "updated_at": now,
    }


def _ros_projection_row(
    row: dict[str, Any],
    *,
    as_of_season: int,
    as_of_week: int,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    model_run_id: str,
) -> dict[str, Any]:
    features = dict(row)
    features.update({
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
    })
    projection = calculate_ros_projection(features, {"as_of_week": as_of_week})
    now = _utc_timestamp()
    return {
        "model_run_id": model_run_id,
        "player_id_internal": row.get("player_id_internal"),
        "source_player_key": row.get("source_player_key"),
        "display_name": row.get("display_name"),
        "position": row.get("position"),
        "team": row.get("team"),
        "as_of_season": as_of_season,
        "as_of_week": as_of_week,
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "projection_horizon": "ros",
        "remaining_games": projection["remaining_games"],
        "projected_points_total": projection["projected_points_total"],
        "projected_points_per_game": projection["projected_points_per_game"],
        "projected_points_floor": projection["projected_points_floor"],
        "projected_points_ceiling": projection["projected_points_ceiling"],
        "projected_games_played": projection["projected_games_played"],
        "projected_stat_json": _projected_stat_json(row, projection),
        "value_json": json.dumps({"weekly_baseline": projection["projected_points_per_game"]}, sort_keys=True),
        "confidence_score": projection["confidence_score"],
        "risk_score": projection["risk_score"],
        "role_score": projection["role_score"],
        "trend_score": projection["trend_score"],
        "replacement_value": 0.0,
        "rank_source": RANK_SOURCE,
        "source_freshness_json": _source_freshness_json(row),
        "missing_data_flags": json.dumps(projection["missing_data_flags"], sort_keys=True),
        "created_at": now,
        "updated_at": now,
    }


def _dynasty_projection_row(
    row: dict[str, Any],
    *,
    as_of_season: int,
    as_of_week: int,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    model_run_id: str,
) -> dict[str, Any]:
    features = dict(row)
    features.update({
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
    })
    projection = calculate_dynasty_projection(features)
    now = _utc_timestamp()
    return {
        "model_run_id": model_run_id,
        "player_id_internal": row.get("player_id_internal"),
        "source_player_key": row.get("source_player_key"),
        "display_name": row.get("display_name"),
        "position": row.get("position"),
        "team": row.get("team"),
        "as_of_season": as_of_season,
        "as_of_week": as_of_week,
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "projection_horizon": "dynasty",
        "year_1_value": projection["year_1_value"],
        "year_2_value": projection["year_2_value"],
        "year_3_value": projection["year_3_value"],
        "total_dynasty_value": projection["total_dynasty_value"],
        "age_curve_adjustment": projection["age_curve_adjustment"],
        "position_lifecycle_adjustment": projection["position_lifecycle_adjustment"],
        "rookie_or_prospect_adjustment": projection["rookie_or_prospect_adjustment"],
        "contract_or_team_stability_adjustment": projection["contract_or_team_stability_adjustment"],
        "projected_stat_json": _projected_stat_json(row, projection),
        "value_json": json.dumps({"market_value": _num(row.get("market_value"), 0.0)}, sort_keys=True),
        "confidence_score": projection["confidence_score"],
        "risk_score": projection["risk_score"],
        "role_score": projection["role_score"],
        "trend_score": projection["trend_score"],
        "rank_source": RANK_SOURCE,
        "source_freshness_json": _source_freshness_json(row),
        "missing_data_flags": json.dumps(projection["missing_data_flags"], sort_keys=True),
        "created_at": now,
        "updated_at": now,
    }


def _build_rows_for_horizon(**kwargs: Any) -> list[dict[str, Any]]:
    horizon = kwargs.pop("horizon")
    if horizon == "weekly":
        return build_weekly_projection_rows(**kwargs)
    if horizon == "ros":
        return build_ros_projection_rows(**kwargs)
    if horizon == "dynasty":
        return build_dynasty_projection_rows(**kwargs)
    raise ValueError(f"Unsupported projection horizon: {horizon}")


def _apply_replacement_values(rows: list[dict[str, Any]], roster_format_id: str, scoring_profile_id: str) -> None:
    baselines = calculate_replacement_value_placeholder(rows, roster_format_id, scoring_profile_id)
    for row in rows:
        baseline = baselines.get(row.get("position") or "", 0.0)
        row["replacement_value"] = round(max(0.0, _projection_value(row) - baseline), 3)


def _role_score(row: dict[str, Any]) -> float:
    components = [
        _share_score(row.get("snap_share_last_3")),
        _share_score(row.get("target_share_last_3")),
        _share_score(row.get("rush_share_last_3")),
        _clamp(_num(row.get("role_quality_score"), 50.0), 0.0, 100.0),
        _clamp(100.0 - _num(row.get("role_fragility_score"), 50.0), 0.0, 100.0),
    ]
    return sum(components) / len(components)


def _trend_score(row: dict[str, Any]) -> float:
    last3 = _num(row.get("fantasy_points_last_3"), _num(row.get("recent_points_per_game"), 0.0))
    last8 = _num(row.get("fantasy_points_last_8"), last3)
    if last8 <= 0:
        return 50.0
    return _clamp(50.0 + ((last3 - last8) / max(last8, 1.0)) * 50.0, 0.0, 100.0)


def _risk_score(row: dict[str, Any], fraud_risk_score: float, role_score: float) -> float:
    missing_count = len(_json_array(row.get("missing_data_flags")))
    risk = 25.0 + fraud_risk_score * 0.35 + max(0.0, 55.0 - role_score) * 0.35 + missing_count * 3.0
    return round(_clamp(risk, 0.0, 100.0), 3)


def _confidence_score(risk_score: float, row: dict[str, Any]) -> float:
    pigskin_confidence = _num(row.get("pigskin_confidence"), 70.0)
    confidence = pigskin_confidence * 0.35 + (100.0 - risk_score) * 0.65
    return round(_clamp(confidence, 0.0, 100.0), 3)


def _position_risk(position: Any) -> float:
    return {"QB": 8.0, "RB": 18.0, "WR": 13.0, "TE": 16.0}.get(str(position or "").upper(), 15.0)


def _roster_format_factor(row: dict[str, Any]) -> float:
    position = str(row.get("position") or "").upper()
    roster_format_id = row.get("roster_format_id")
    if position == "QB" and roster_format_id in {"superflex", "two_qb"}:
        return 1.08
    return 1.0


def _age_curve_adjustment(row: dict[str, Any]) -> float:
    age = _num(row.get("age"), math.nan)
    position = str(row.get("position") or "").upper()
    if math.isnan(age):
        return 0.0
    peak = {"QB": 29.0, "RB": 24.0, "WR": 26.0, "TE": 27.0}.get(position, 26.0)
    if age <= peak:
        return min(0.10, (peak - age) * 0.015)
    decline = {"QB": 0.018, "RB": 0.055, "WR": 0.035, "TE": 0.03}.get(position, 0.035)
    return max(-0.30, -(age - peak) * decline)


def _position_lifecycle_adjustment(row: dict[str, Any]) -> float:
    position = str(row.get("position") or "").upper()
    role = _role_score(row)
    base = {"QB": 0.03, "RB": -0.02, "WR": 0.01, "TE": 0.00}.get(position, 0.0)
    return base + (role - 50.0) / 1000.0


def _rookie_or_prospect_adjustment(row: dict[str, Any]) -> float:
    rookie_year = _int_or_none(row.get("rookie_year"))
    season = _int_or_none(row.get("season"))
    if rookie_year is None or season is None:
        return 0.0
    experience = max(0, season - rookie_year)
    if experience <= 1:
        return 0.06
    if experience <= 3:
        return 0.03
    return 0.0


def _contract_or_team_stability_adjustment(row: dict[str, Any]) -> float:
    if row.get("active_status") and str(row.get("active_status")).lower() not in {"active", "act"}:
        return -0.08
    if row.get("team"):
        return 0.01
    return -0.03


def _projection_missing_flags(row: dict[str, Any]) -> list[str]:
    flags = set(_json_array(row.get("missing_data_flags")))
    if not row.get("player_id_internal"):
        flags.add("missing_player_id_internal")
    if row.get("recent_points_per_game") in (None, "") and row.get("fantasy_points_last_3") in (None, ""):
        flags.add("missing_recent_points")
    if row.get("snap_share_last_3") in (None, ""):
        flags.add("missing_snap_share")
    if row.get("fraud_risk_score") in (None, ""):
        flags.add("missing_fraud_risk")
    if row.get("breakout_score") in (None, ""):
        flags.add("missing_breakout_score")
    if row.get("game_environment_json") in (None, ""):
        flags.add("missing_game_environment")
    return sorted(flags)


def _projected_stat_json(row: dict[str, Any], projection: dict[str, Any]) -> str:
    return json.dumps({
        "baseline_points": projection.get("projected_points_mean")
            or projection.get("projected_points_per_game")
            or projection.get("year_1_value"),
        "recent_points_per_game": _num(row.get("recent_points_per_game"), None),
        "high_value_touches_last_3": _num(row.get("high_value_touches_last_3"), None),
        "red_zone_opportunities_last_3": _num(row.get("red_zone_opportunities_last_3"), None),
    }, sort_keys=True)


def _usage_projection_json(row: dict[str, Any]) -> str:
    return json.dumps({
        "snap_share_last_3": _num(row.get("snap_share_last_3"), None),
        "target_share_last_3": _num(row.get("target_share_last_3"), None),
        "rush_share_last_3": _num(row.get("rush_share_last_3"), None),
        "role_score": _role_score(row),
    }, sort_keys=True)


def _efficiency_projection_json(row: dict[str, Any]) -> str:
    return json.dumps({
        "total_epa_recent": _num(row.get("total_epa_recent"), None),
        "pigskin_projection": _num(row.get("pigskin_projection"), None),
        "pigskin_confidence": _num(row.get("pigskin_confidence"), None),
    }, sort_keys=True)


def _touchdown_projection_json(row: dict[str, Any]) -> str:
    return json.dumps({
        "red_zone_opportunities_last_3": _num(row.get("red_zone_opportunities_last_3"), None),
        "fraud_risk_score": _num(row.get("fraud_risk_score"), None),
    }, sort_keys=True)


def _source_freshness_json(row: dict[str, Any]) -> str:
    value = row.get("source_freshness_json")
    if value in (None, ""):
        return json.dumps({"sources": list(PROJECTION_SOURCE_TABLES), "missing_source_freshness": True}, sort_keys=True)
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)


def _projection_value(row: dict[str, Any]) -> float:
    return _num(
        row.get("projected_points_mean"),
        _num(row.get("projected_points_total"), _num(row.get("total_dynasty_value"), 0.0)),
    )


def _tier(rank_position: int, horizon: str) -> str:
    if horizon == "dynasty":
        if rank_position <= 5:
            return "cornerstone"
        if rank_position <= 12:
            return "core starter"
        if rank_position <= 30:
            return "useful asset"
        return "depth or bet"
    if rank_position <= 6:
        return "elite starter"
    if rank_position <= 12:
        return "front-line starter"
    if rank_position <= 24:
        return "starter"
    if rank_position <= 48:
        return "flex"
    return "depth"


def _strip_runtime_fields(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if not key.startswith("_")}


def _ensure_rows_have_model_run_id(rows: list[dict[str, Any]]) -> None:
    missing = [row.get("display_name") or row.get("player_id_internal") for row in rows if not row.get("model_run_id")]
    if missing:
        raise ValueError(f"Projection rows missing model_run_id: {missing[:3]}")


def _require_model_run_id(model_run_id: str | None) -> None:
    if not model_run_id:
        raise ValueError("Projection rows require model_run_id")


def _projection_table_name(horizon: str) -> str:
    return {
        "weekly": "projections_player_weekly",
        "ros": "projections_player_ros",
        "dynasty": "projections_player_dynasty",
    }[_normalize_horizon(horizon)]


def _query_rows(client: Any, sql: str, job_config: bigquery.QueryJobConfig) -> list[dict[str, Any]]:
    rows = client.query(sql, job_config=job_config).result()
    result = []
    for row in rows:
        if isinstance(row, dict):
            result.append(dict(row))
        elif hasattr(row, "items"):
            result.append(dict(row.items()))
        else:
            result.append(dict(row))
    return result


def _job_config(params: list[tuple[str, str, Any]]) -> bigquery.QueryJobConfig:
    return bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=[
            bigquery.ScalarQueryParameter(name, param_type, value)
            for name, param_type, value in params
        ],
    )


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    _validate_project_id(project_id)
    _validate_identifier(dataset_id, "dataset_id")
    _validate_identifier(table_name, "table_name")
    return f"{project_id}.{dataset_id}.{table_name}"


def _validate_identifier(value: str, label: str) -> None:
    if not IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"Invalid BigQuery {label}: {value!r}")


def _validate_project_id(value: str) -> None:
    if not PROJECT_ID_RE.fullmatch(value):
        raise ValueError(f"Invalid BigQuery project_id: {value!r}")


def _normalize_horizon(horizon: str) -> str:
    normalized = str(horizon or "").strip().lower().replace("_", "-")
    aliases = {"rest-of-season": "ros", "rest_of_season": "ros"}
    normalized = aliases.get(normalized, normalized)
    if normalized not in {"weekly", "ros", "dynasty"}:
        raise ValueError(f"Unsupported projection horizon: {horizon!r}")
    return normalized


def _clamp_limit(value: int | str | None) -> int:
    try:
        limit = int(value) if value is not None else DEFAULT_LIMIT
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT
    return max(1, min(limit, MAX_LIMIT))


def _clean_int(value: Any) -> int:
    parsed = _int_or_none(value)
    if parsed is None:
        raise ValueError(f"Expected integer value, got {value!r}")
    return parsed


def _int_or_default(value: Any, default: int) -> int:
    parsed = _int_or_none(value)
    return parsed if parsed is not None else default


def _int_or_none(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _num(value: Any, default: float | None = 0.0) -> float | None:
    if value in (None, ""):
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(parsed) or math.isinf(parsed):
        return default
    return parsed


def _first_number(*values: Any) -> float:
    for value in values:
        parsed = _num(value, None)
        if parsed is not None:
            return parsed
    return 0.0


def _share_score(value: Any) -> float:
    parsed = _num(value, None)
    if parsed is None:
        return 40.0
    if parsed <= 1.0:
        parsed *= 100.0
    return _clamp(parsed, 0.0, 100.0)


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def _json_array(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed if item is not None]


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build deterministic projection outputs.")
    parser.add_argument("--horizon", required=True, choices=("weekly", "ros", "dynasty"))
    parser.add_argument("--season", required=True, type=int)
    parser.add_argument("--week", required=True, type=int)
    parser.add_argument("--scoring-profile", default=DEFAULT_SCORING_PROFILE)
    parser.add_argument("--league-type", default=DEFAULT_LEAGUE_TYPE)
    parser.add_argument("--roster-format", default=DEFAULT_ROSTER_FORMAT)
    parser.add_argument("--feature-config-version-id")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_projection(
        horizon=args.horizon,
        season=args.season,
        week=args.week,
        scoring_profile_id=args.scoring_profile,
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        feature_config_version_id=args.feature_config_version_id,
        dry_run=args.dry_run,
        limit=args.limit,
    )
    print(json.dumps(result, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
