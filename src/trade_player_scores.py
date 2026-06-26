"""Deterministic Trade Analyzer score v0 builder."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_SCORING_PROFILE = "ppr"
DEFAULT_LEAGUE_TYPE = "redraft"
DEFAULT_ROSTER_FORMAT = "one_qb"
DEFAULT_MODEL_VERSION = "trade_score_v0"
DEFAULT_LIMIT = 100
MAX_LIMIT = 500
DEFAULT_SCORE_READ_LIMIT = 500
OUTPUT_TABLE = "trade_player_scores"
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("TRADE_PLAYER_SCORES_MAX_BYTES_BILLED", "1000000000"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")

SAFE_SOURCE_OBJECTS = (
    "compat_trade_assets_current",
    "compat_trade_player_history",
    "analytics_player_weekly_truth",
    "analytics_player_fantasy_points_by_profile",
    "analytics_fraud_watch",
    "projection_rankings_current",
    "projections_player_weekly",
)

MATERIALIZATION_POLICY_VERSION = "trade_score_v0_staging_review_policy"
LOW_CONFIDENCE_THRESHOLD = 70.0

COMPONENT_FIELDS = (
    "market_score",
    "projection_score",
    "recent_production_score",
    "role_usage_score",
    "positional_scarcity_score",
    "efficiency_score",
)

OUTPUT_FIELDS = (
    "score_run_id",
    "model_run_id",
    "model_version",
    "player_id",
    "player_name",
    "normalized_name",
    "position",
    "team",
    "season",
    "week",
    "scoring_profile_id",
    "league_type_id",
    "roster_format_id",
    "current_market_value",
    "projected_3_year_value",
    "market_score",
    "projection_score",
    "recent_production_score",
    "role_usage_score",
    "positional_scarcity_score",
    "efficiency_score",
    "normalized_risk_score",
    "fraud_score",
    "confidence_score",
    "trade_score",
    "score_tier",
    "source_freshness_json",
    "missing_flags_json",
    "component_json",
    "ranking_version",
    "feature_config_version_id",
    "created_by",
    "created_at",
)


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def build_trade_player_score_source_query(
    *,
    project_id: str,
    dataset_id: str,
    season: int | str,
    week: int | str,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int | str | None = None,
) -> tuple[str, bigquery.QueryJobConfig]:
    """Build the bounded source query from curated marts and compatibility views."""

    safe_limit = _clamp_limit(limit)
    table = lambda name: _table_id(project_id, dataset_id, name)
    sql = f"""
    WITH assets AS (
        SELECT
            player_id_internal,
            source_player_key,
            gsis_id,
            display_name,
            normalized_name,
            position,
            team,
            CAST(market_value AS FLOAT64) AS current_market_value,
            CAST(risk_adjusted_trade_value AS FLOAT64) AS risk_adjusted_trade_value,
            CAST(dynasty_value_placeholder AS FLOAT64) AS dynasty_value_placeholder,
            CAST(redraft_value_placeholder AS FLOAT64) AS redraft_value_placeholder,
            CAST(position_scarcity_score AS FLOAT64) AS asset_position_scarcity_score,
            CAST(pigskin_projection AS FLOAT64) AS pigskin_projection,
            CAST(pigskin_confidence AS FLOAT64) AS pigskin_confidence,
            CAST(pigskin_fraud_risk_score AS FLOAT64) AS pigskin_fraud_risk_score,
            model_run_id AS asset_model_run_id,
            ranking_version,
            source_freshness_json AS asset_source_freshness_json,
            missing_data_flags AS asset_missing_data_flags
        FROM `{table("compat_trade_assets_current")}`
        WHERE scoring_profile_id = @scoring_profile_id
            AND league_type_id = @league_type_id
            AND roster_format_id = @roster_format_id
    ),
    history_recent AS (
        SELECT
            COALESCE(player_id_internal, source_player_key) AS player_key,
            ANY_VALUE(player_display_name) AS history_player_name,
            AVG(total_fantasy_points) AS recent_points_per_game,
            AVG(snap_share) AS history_snap_share,
            AVG(target_share) AS history_target_share,
            AVG(rush_share) AS history_rush_share,
            AVG(high_value_touches) AS high_value_touches,
            AVG(yards_per_carry) AS yards_per_carry,
            AVG(yards_per_target) AS yards_per_target,
            AVG(yards_per_reception) AS yards_per_reception,
            AVG(catch_rate) AS catch_rate,
            COUNT(1) AS history_sample_size,
            ANY_VALUE(source_freshness_json) AS history_source_freshness_json,
            ANY_VALUE(missing_data_flags) AS history_missing_data_flags
        FROM `{table("compat_trade_player_history")}`
        WHERE scoring_profile_id = @scoring_profile_id
            AND season = @season
            AND week BETWEEN GREATEST(@week - 4, 1) AND @week
        GROUP BY player_key
    ),
    truth_recent AS (
        SELECT
            player_id AS player_key,
            AVG(fantasy_points_ppr) AS truth_recent_points,
            AVG(offense_pct) AS truth_snap_share,
            AVG(target_share) AS truth_target_share,
            AVG(carry_share) AS truth_rush_share,
            AVG(red_zone_touches) AS red_zone_touches,
            AVG(role_quality_score) AS role_quality_score,
            AVG(role_fragility_score) AS role_fragility_score
        FROM `{table("analytics_player_weekly_truth")}`
        WHERE season = @season
            AND week BETWEEN GREATEST(@week - 4, 1) AND @week
            AND position IN ('QB', 'RB', 'WR', 'TE')
        GROUP BY player_key
    ),
    fantasy_recent AS (
        SELECT
            COALESCE(player_id_internal, source_player_key) AS player_key,
            AVG(total_fantasy_points) AS profile_recent_points,
            COUNT(1) AS fantasy_profile_sample_size,
            ANY_VALUE(source_freshness_json) AS fantasy_source_freshness_json,
            ANY_VALUE(missing_data_flags) AS fantasy_missing_data_flags
        FROM `{table("analytics_player_fantasy_points_by_profile")}`
        WHERE scoring_profile_id = @scoring_profile_id
            AND season = @season
            AND week BETWEEN GREATEST(@week - 4, 1) AND @week
        GROUP BY player_key
    ),
    fraud_latest AS (
        SELECT * EXCEPT(rn)
        FROM (
            SELECT
                player_id AS player_key,
                CAST(fraud_score AS FLOAT64) AS source_fraud_score,
                fraud_label,
                analytical_verdict AS fraud_verdict,
                ROW_NUMBER() OVER (
                    PARTITION BY player_id
                    ORDER BY season DESC, week DESC
                ) AS rn
            FROM `{table("analytics_fraud_watch")}`
            WHERE season = @season
                AND week <= @week
        )
        WHERE rn = 1
    ),
    fraud_match AS (
        SELECT * EXCEPT(rn, match_priority)
        FROM (
            SELECT
                COALESCE(a.player_id_internal, a.source_player_key) AS asset_join_key,
                f.player_key AS fraud_join_key,
                CASE
                    WHEN a.source_player_key = f.player_key THEN 'source_player_key'
                    WHEN a.gsis_id = f.player_key THEN 'gsis_id'
                    WHEN a.player_id_internal = f.player_key THEN 'player_id_internal'
                    ELSE 'unknown'
                END AS fraud_join_strategy,
                f.source_fraud_score,
                f.fraud_label,
                f.fraud_verdict,
                CASE
                    WHEN a.source_player_key = f.player_key THEN 1
                    WHEN a.gsis_id = f.player_key THEN 2
                    WHEN a.player_id_internal = f.player_key THEN 3
                    ELSE 99
                END AS match_priority,
                ROW_NUMBER() OVER (
                    PARTITION BY COALESCE(a.player_id_internal, a.source_player_key)
                    ORDER BY
                        CASE
                            WHEN a.source_player_key = f.player_key THEN 1
                            WHEN a.gsis_id = f.player_key THEN 2
                            WHEN a.player_id_internal = f.player_key THEN 3
                            ELSE 99
                        END
                ) AS rn
            FROM assets a
            JOIN fraud_latest f
                ON a.source_player_key = f.player_key
                OR a.gsis_id = f.player_key
                OR a.player_id_internal = f.player_key
        )
        WHERE rn = 1
    ),
    projection_rows AS (
        SELECT
            r.player_id_internal AS projection_player_id_internal,
            w.source_player_key AS projection_source_player_key,
            r.display_name AS projection_display_name,
            LOWER(TRIM(REGEXP_REPLACE(r.display_name, r'[^a-z0-9]+', ' '))) AS projection_normalized_name,
            r.position AS projection_position,
            r.team AS projection_team,
            r.model_run_id AS projection_model_run_id,
            r.projection_horizon,
            r.rank_overall AS projection_rank_overall,
            r.rank_position AS projection_rank_position,
            r.tier AS projection_tier,
            COALESCE(r.as_of_season, r.season) AS projection_as_of_season,
            COALESCE(r.as_of_week, r.week) AS projection_as_of_week,
            CAST(r.projected_points_or_value AS FLOAT64) AS projected_points_or_value,
            CAST(r.replacement_value AS FLOAT64) AS projection_replacement_value,
            CAST(r.confidence_score AS FLOAT64) AS projection_confidence_score,
            CAST(r.risk_score AS FLOAT64) AS projection_risk_score,
            r.created_at AS projection_created_at,
            COUNT(*) OVER (
                PARTITION BY
                    LOWER(TRIM(REGEXP_REPLACE(r.display_name, r'[^a-z0-9]+', ' '))),
                    r.position,
                    r.team
            ) AS projection_name_team_count
        FROM `{table("projection_rankings_current")}` r
        LEFT JOIN `{table("projections_player_weekly")}` w
            ON r.model_run_id = w.model_run_id
            AND r.player_id_internal = w.player_id_internal
            AND r.season = w.season
            AND r.week = w.week
            AND r.scoring_profile_id = w.scoring_profile_id
            AND r.league_type_id = w.league_type_id
            AND r.roster_format_id = w.roster_format_id
        WHERE r.scoring_profile_id = @scoring_profile_id
            AND r.league_type_id = @league_type_id
            AND r.roster_format_id = @roster_format_id
            AND COALESCE(r.as_of_season, r.season) = @season
            AND COALESCE(r.as_of_week, r.week) <= @week
    ),
    projection_match AS (
        SELECT * EXCEPT(rn, match_priority)
        FROM (
            SELECT
                COALESCE(a.player_id_internal, a.source_player_key) AS asset_join_key,
                CASE
                    WHEN a.source_player_key = p.projection_source_player_key THEN a.source_player_key
                    WHEN a.gsis_id = p.projection_source_player_key THEN a.gsis_id
                    WHEN a.player_id_internal = p.projection_player_id_internal THEN a.player_id_internal
                    WHEN LOWER(a.display_name) = LOWER(p.projection_display_name)
                        AND a.position = p.projection_position
                        AND a.team = p.projection_team
                        AND p.projection_name_team_count = 1 THEN a.display_name
                    WHEN LOWER(TRIM(REGEXP_REPLACE(a.display_name, r'[^a-z0-9]+', ' '))) = p.projection_normalized_name
                        AND a.position = p.projection_position
                        AND a.team = p.projection_team
                        AND p.projection_name_team_count = 1 THEN a.normalized_name
                    ELSE NULL
                END AS projection_join_key,
                CASE
                    WHEN a.source_player_key = p.projection_source_player_key THEN 'source_player_key'
                    WHEN a.gsis_id = p.projection_source_player_key THEN 'gsis_id'
                    WHEN a.player_id_internal = p.projection_player_id_internal THEN 'player_id_internal'
                    WHEN LOWER(a.display_name) = LOWER(p.projection_display_name)
                        AND a.position = p.projection_position
                        AND a.team = p.projection_team
                        AND p.projection_name_team_count = 1 THEN 'exact_name_position_team'
                    WHEN LOWER(TRIM(REGEXP_REPLACE(a.display_name, r'[^a-z0-9]+', ' '))) = p.projection_normalized_name
                        AND a.position = p.projection_position
                        AND a.team = p.projection_team
                        AND p.projection_name_team_count = 1 THEN 'unique_normalized_name_position_team'
                    ELSE 'unknown'
                END AS projection_join_strategy,
                p.projection_model_run_id,
                p.projection_horizon,
                p.projection_rank_overall,
                p.projection_rank_position,
                p.projection_tier,
                p.projection_as_of_season,
                p.projection_as_of_week,
                p.projected_points_or_value,
                p.projection_replacement_value,
                p.projection_confidence_score,
                p.projection_risk_score,
                p.projection_created_at,
                CASE
                    WHEN a.source_player_key = p.projection_source_player_key THEN 1
                    WHEN a.gsis_id = p.projection_source_player_key THEN 2
                    WHEN a.player_id_internal = p.projection_player_id_internal THEN 3
                    WHEN LOWER(a.display_name) = LOWER(p.projection_display_name)
                        AND a.position = p.projection_position
                        AND a.team = p.projection_team
                        AND p.projection_name_team_count = 1 THEN 4
                    WHEN LOWER(TRIM(REGEXP_REPLACE(a.display_name, r'[^a-z0-9]+', ' '))) = p.projection_normalized_name
                        AND a.position = p.projection_position
                        AND a.team = p.projection_team
                        AND p.projection_name_team_count = 1 THEN 5
                    ELSE 99
                END AS match_priority,
                ROW_NUMBER() OVER (
                    PARTITION BY COALESCE(a.player_id_internal, a.source_player_key)
                    ORDER BY
                        CASE
                            WHEN a.source_player_key = p.projection_source_player_key THEN 1
                            WHEN a.gsis_id = p.projection_source_player_key THEN 2
                            WHEN a.player_id_internal = p.projection_player_id_internal THEN 3
                            WHEN LOWER(a.display_name) = LOWER(p.projection_display_name)
                                AND a.position = p.projection_position
                                AND a.team = p.projection_team
                                AND p.projection_name_team_count = 1 THEN 4
                            WHEN LOWER(TRIM(REGEXP_REPLACE(a.display_name, r'[^a-z0-9]+', ' '))) = p.projection_normalized_name
                                AND a.position = p.projection_position
                                AND a.team = p.projection_team
                                AND p.projection_name_team_count = 1 THEN 5
                            ELSE 99
                        END,
                        p.projection_as_of_week DESC,
                        p.projection_created_at DESC
                ) AS rn
            FROM assets a
            JOIN projection_rows p
                ON a.source_player_key = p.projection_source_player_key
                OR a.gsis_id = p.projection_source_player_key
                OR a.player_id_internal = p.projection_player_id_internal
                OR (
                    LOWER(a.display_name) = LOWER(p.projection_display_name)
                    AND a.position = p.projection_position
                    AND a.team = p.projection_team
                    AND p.projection_name_team_count = 1
                )
                OR (
                    LOWER(TRIM(REGEXP_REPLACE(a.display_name, r'[^a-z0-9]+', ' '))) = p.projection_normalized_name
                    AND a.position = p.projection_position
                    AND a.team = p.projection_team
                    AND p.projection_name_team_count = 1
                )
        )
        WHERE rn = 1
    )
    SELECT
        a.player_id_internal,
        a.source_player_key,
        a.gsis_id,
        COALESCE(a.display_name, h.history_player_name) AS player_name,
        a.normalized_name,
        a.position,
        a.team,
        @season AS season,
        @week AS week,
        @scoring_profile_id AS scoring_profile_id,
        @league_type_id AS league_type_id,
        @roster_format_id AS roster_format_id,
        a.current_market_value,
        COALESCE(
            a.dynasty_value_placeholder,
            p.projected_points_or_value,
            a.redraft_value_placeholder,
            a.risk_adjusted_trade_value,
            a.current_market_value
        ) AS projected_3_year_value,
        a.risk_adjusted_trade_value,
        a.asset_position_scarcity_score,
        a.pigskin_projection,
        a.pigskin_confidence,
        a.pigskin_fraud_risk_score,
        a.asset_model_run_id,
        a.ranking_version,
        a.asset_source_freshness_json,
        a.asset_missing_data_flags,
        h.recent_points_per_game,
        h.history_snap_share,
        h.history_target_share,
        h.history_rush_share,
        h.high_value_touches,
        h.yards_per_carry,
        h.yards_per_target,
        h.yards_per_reception,
        h.catch_rate,
        h.history_sample_size,
        h.history_source_freshness_json,
        h.history_missing_data_flags,
        t.truth_recent_points,
        t.truth_snap_share,
        t.truth_target_share,
        t.truth_rush_share,
        t.red_zone_touches,
        t.role_quality_score,
        t.role_fragility_score,
        fp.profile_recent_points,
        fp.fantasy_profile_sample_size,
        fp.fantasy_source_freshness_json,
        fp.fantasy_missing_data_flags,
        f.fraud_join_key,
        f.fraud_join_strategy,
        f.source_fraud_score,
        f.fraud_label,
        f.fraud_verdict,
        p.projection_join_key,
        p.projection_join_strategy,
        p.projection_model_run_id,
        p.projection_horizon,
        p.projection_rank_overall,
        p.projection_rank_position,
        p.projection_tier,
        p.projection_as_of_season,
        p.projection_as_of_week,
        p.projected_points_or_value,
        p.projection_replacement_value,
        p.projection_confidence_score,
        p.projection_risk_score,
        p.projection_created_at
    FROM assets a
    LEFT JOIN history_recent h
        ON COALESCE(a.player_id_internal, a.source_player_key) = h.player_key
    LEFT JOIN truth_recent t
        ON COALESCE(a.player_id_internal, a.source_player_key) = t.player_key
    LEFT JOIN fantasy_recent fp
        ON COALESCE(a.player_id_internal, a.source_player_key) = fp.player_key
    LEFT JOIN fraud_match f
        ON COALESCE(a.player_id_internal, a.source_player_key) = f.asset_join_key
    LEFT JOIN projection_match p
        ON COALESCE(a.player_id_internal, a.source_player_key) = p.asset_join_key
    ORDER BY a.current_market_value DESC NULLS LAST, a.display_name
    LIMIT @limit
    """
    return sql, _job_config([
        ("season", "INT64", _required_int(season, "season")),
        ("week", "INT64", _required_int(week, "week")),
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("limit", "INT64", safe_limit),
    ])


def fetch_trade_player_score_inputs(
    *,
    client: Any,
    dataset_id: str,
    season: int | str,
    week: int | str,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int | str | None = None,
) -> list[dict[str, Any]]:
    sql, job_config = build_trade_player_score_source_query(
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


def build_trade_player_score_rows(
    source_rows: list[dict[str, Any]],
    *,
    season: int | str,
    week: int | str,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_version: str = DEFAULT_MODEL_VERSION,
    score_run_id: str | None = None,
    created_by: str = "trade_player_scores",
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    now = now or datetime.now(timezone.utc)
    safe_season = _required_int(season, "season")
    safe_week = _required_int(week, "week")
    run_id = score_run_id or build_score_run_id(
        model_version=model_version,
        season=safe_season,
        week=safe_week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    normalized_rows = [dict(row) for row in source_rows]
    percentile_context = _percentile_context(normalized_rows)
    rows = [
        _build_score_row(
            row,
            percentile_context=percentile_context,
            season=safe_season,
            week=safe_week,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            model_version=model_version,
            score_run_id=run_id,
            created_by=created_by,
            now=now,
        )
        for row in normalized_rows
    ]
    return sorted(rows, key=lambda row: (row["trade_score"], row["player_name"] or ""), reverse=True)


def build_trade_player_scores(
    *,
    season: int | str,
    week: int | str,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_version: str = DEFAULT_MODEL_VERSION,
    limit: int | str | None = None,
    dry_run: bool = True,
    write: bool = False,
    client: Any | None = None,
    dataset_id: str | None = None,
    project_id: str | None = None,
    created_by: str = "trade_player_scores",
) -> dict[str, Any]:
    """Fetch safe inputs, calculate score rows, and optionally write them."""

    if write and dry_run:
        raise ValueError("--write cannot be combined with --dry-run")

    client = client or (bigquery.Client(project=project_id) if project_id else get_bigquery_client())
    dataset_id = dataset_id or get_bigquery_dataset()
    source_rows = fetch_trade_player_score_inputs(
        client=client,
        dataset_id=dataset_id,
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=limit,
    )
    score_rows = build_trade_player_score_rows(
        source_rows,
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        model_version=model_version,
        created_by=created_by,
    )
    materializable_rows = _materializable_score_rows(score_rows)
    materialization_policy = build_materialization_policy_summary(score_rows)
    wrote = False
    written_row_count = 0
    if write:
        written_row_count = save_trade_player_score_rows(materializable_rows, client=client, dataset_id=dataset_id)
        wrote = True
    return {
        "score_run_id": score_rows[0]["score_run_id"] if score_rows else build_score_run_id(
            model_version=model_version,
            season=season,
            week=week,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
        ),
        "source_row_count": len(source_rows),
        "score_row_count": len(score_rows),
        "materializable_player_row_count": len(materializable_rows),
        "excluded_row_count": materialization_policy["excluded_rows"],
        "excluded_pick_count": materialization_policy["excluded_pick_count"],
        "materialization_policy": materialization_policy,
        "written_row_count": written_row_count,
        "wrote": wrote,
        "dry_run": dry_run or not write,
        "rows": score_rows,
        "preview": build_preview(score_rows),
    }


def calculate_trade_score(
    *,
    market_score: float,
    projection_score: float,
    recent_production_score: float,
    role_usage_score: float,
    positional_scarcity_score: float,
    efficiency_score: float,
    normalized_risk_score: float,
    confidence_score: float,
) -> dict[str, float]:
    base_score = (
        0.40 * _clamp(market_score, 0.0, 100.0)
        + 0.20 * _clamp(projection_score, 0.0, 100.0)
        + 0.15 * _clamp(recent_production_score, 0.0, 100.0)
        + 0.10 * _clamp(role_usage_score, 0.0, 100.0)
        + 0.10 * _clamp(positional_scarcity_score, 0.0, 100.0)
        + 0.05 * _clamp(efficiency_score, 0.0, 100.0)
    )
    risk_adjustment = -10.0 * _clamp(normalized_risk_score, 0.0, 1.0)
    multiplier = confidence_multiplier(confidence_score)
    trade_score = _clamp((base_score + risk_adjustment) * multiplier, 0.0, 100.0)
    return {
        "base_score": round(base_score, 4),
        "risk_adjustment": round(risk_adjustment, 4),
        "confidence_multiplier": round(multiplier, 4),
        "trade_score": round(trade_score, 4),
    }


def confidence_multiplier(confidence_score: float) -> float:
    return _clamp(_num(confidence_score, 0.0) / 100.0, 0.70, 1.00)


def build_preview(rows: list[dict[str, Any]], examples: int = 5) -> dict[str, Any]:
    flag_counts: Counter[str] = Counter()
    for row in rows:
        flag_counts.update(_json_array(row.get("missing_flags_json")))
    sorted_rows = sorted(rows, key=lambda row: row.get("trade_score") or 0.0, reverse=True)
    top = sorted_rows[:examples]
    bottom = list(reversed(sorted_rows[-examples:])) if rows else []
    return {
        "row_count": len(rows),
        "top_examples": [_preview_row(row) for row in top],
        "bottom_examples": [_preview_row(row) for row in bottom],
        "missing_flag_counts": dict(sorted(flag_counts.items())),
    }


def build_materialization_policy_summary(rows: list[dict[str, Any]], examples: int = 25) -> dict[str, Any]:
    materializable_rows = _materializable_score_rows(rows)
    reason_counts: Counter[str] = Counter()
    for row in rows:
        reason_counts.update(materialization_exclusion_reasons(row))

    materializable_confidences = [
        _num(row.get("confidence_score"), None)
        for row in materializable_rows
        if _num(row.get("confidence_score"), None) is not None
    ]
    materializable_scores = [
        _num(row.get("trade_score"), None)
        for row in materializable_rows
        if _num(row.get("trade_score"), None) is not None
    ]
    sorted_materializable_rows = sorted(
        materializable_rows,
        key=lambda row: row.get("trade_score") or 0.0,
        reverse=True,
    )
    low_confidence_count = sum(
        1
        for value in materializable_confidences
        if value < LOW_CONFIDENCE_THRESHOLD
    )
    confidence_ge_threshold_count = sum(
        1
        for value in materializable_confidences
        if value >= LOW_CONFIDENCE_THRESHOLD
    )
    warnings = []
    if materializable_rows and confidence_ge_threshold_count == 0:
        warnings.append("all_materializable_rows_below_confidence_70")
    elif low_confidence_count:
        warnings.append("low_confidence_materializable_rows_present")

    return {
        "policy_version": MATERIALIZATION_POLICY_VERSION,
        "staging_review_only": True,
        "reason_counts_are_non_exclusive": True,
        "total_candidate_rows": len(rows),
        "materializable_rows": len(materializable_rows),
        "excluded_rows": len(rows) - len(materializable_rows),
        "excluded_pick_count": sum(1 for row in rows if _is_pick_score_row(row)),
        "excluded_missing_model_run_id": reason_counts.get("missing_model_run_id", 0),
        "excluded_stale_projection_context": reason_counts.get("stale_projection_context", 0),
        "excluded_missing_identity": reason_counts.get("missing_identity", 0),
        "excluded_invalid_trade_score": reason_counts.get("invalid_trade_score", 0),
        "excluded_missing_confidence": reason_counts.get("missing_confidence_score", 0),
        "excluded_other": 0,
        "excluded_reason_counts": dict(sorted(reason_counts.items())),
        "low_confidence_row_count": low_confidence_count,
        "confidence_ge_70_count": confidence_ge_threshold_count,
        "materializable_confidence": _stats(materializable_confidences),
        "materializable_trade_score": _stats(materializable_scores),
        "materializable_top_examples": [
            _preview_row(row)
            for row in sorted_materializable_rows[:examples]
        ],
        "materializable_bottom_examples": [
            _preview_row(row)
            for row in list(reversed(sorted_materializable_rows[-examples:]))
        ] if materializable_rows else [],
        "warnings": warnings,
    }


def _materializable_score_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if is_materializable_trade_score_row(row)]


def is_materializable_trade_score_row(row: dict[str, Any]) -> bool:
    return not materialization_exclusion_reasons(row)


def materialization_exclusion_reasons(row: dict[str, Any]) -> list[str]:
    flags = set(_json_array(row.get("missing_flags_json")))
    reasons = []
    if _is_pick_score_row(row):
        reasons.append("pick_row")
    if "draft_pick_score_lane_pending" in flags:
        reasons.append("draft_pick_score_lane_pending")
    if not _clean_str(row.get("model_run_id")):
        reasons.append("missing_model_run_id")
    if "stale_projection_context" in flags:
        reasons.append("stale_projection_context")
    if not _has_materialization_identity(row):
        reasons.append("missing_identity")
    trade_score = _num(row.get("trade_score"), None)
    if trade_score is None or trade_score < 0.0 or trade_score > 100.0:
        reasons.append("invalid_trade_score")
    confidence_score = _num(row.get("confidence_score"), None)
    if confidence_score is None:
        reasons.append("missing_confidence_score")
    return sorted(set(reasons))


def _has_materialization_identity(row: dict[str, Any]) -> bool:
    player_id = _clean_str(row.get("player_id"))
    if not player_id or player_id.startswith("unresolved:"):
        return False
    return "missing_player_id" not in _json_array(row.get("missing_flags_json"))


def _is_pick_score_row(row: dict[str, Any]) -> bool:
    if str(row.get("position") or "").upper() == "PICK":
        return True
    return "draft_pick_asset" in _json_array(row.get("missing_flags_json"))


def save_trade_player_score_rows(
    rows: list[dict[str, Any]],
    *,
    client: Any,
    dataset_id: str,
) -> int:
    if not rows:
        return 0

    target_table_id = _table_id(client.project, dataset_id, OUTPUT_TABLE)
    temp_name = f"{OUTPUT_TABLE}_staging_{_short_hash(str(datetime.now(timezone.utc)) + rows[0]['score_run_id'])}"
    temp_table_id = _table_id(client.project, dataset_id, temp_name)
    clean_rows = [{field: row.get(field) for field in OUTPUT_FIELDS} for row in rows]
    job_config = bigquery.LoadJobConfig(
        schema=_output_schema(),
        write_disposition=bigquery.WriteDisposition.WRITE_EMPTY,
    )
    try:
        load_job = client.load_table_from_json(clean_rows, temp_table_id, job_config=job_config)
        load_job.result()
        errors = getattr(load_job, "errors", None)
        if errors:
            raise RuntimeError(f"Failed to stage trade score rows: {errors}")

        update_fields = [
            field
            for field in OUTPUT_FIELDS
            if field not in (
                "model_version",
                "season",
                "week",
                "scoring_profile_id",
                "league_type_id",
                "roster_format_id",
                "player_id",
            )
        ]
        update_clause = ",\n        ".join(f"{field} = source.{field}" for field in update_fields)
        insert_fields = ", ".join(OUTPUT_FIELDS)
        insert_values = ", ".join(f"source.{field}" for field in OUTPUT_FIELDS)
        merge_sql = f"""
        MERGE `{target_table_id}` target
        USING `{temp_table_id}` source
        ON target.model_version = source.model_version
            AND target.season = source.season
            AND target.week = source.week
            AND target.scoring_profile_id = source.scoring_profile_id
            AND target.league_type_id = source.league_type_id
            AND target.roster_format_id = source.roster_format_id
            AND target.player_id = source.player_id
        WHEN MATCHED THEN
            UPDATE SET
                {update_clause}
        WHEN NOT MATCHED THEN
            INSERT ({insert_fields})
            VALUES ({insert_values})
        """
        client.query(merge_sql).result()
    finally:
        if hasattr(client, "delete_table"):
            client.delete_table(temp_table_id, not_found_ok=True)
    return len(rows)


def build_score_run_id(
    *,
    model_version: str,
    season: int | str,
    week: int | str,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
) -> str:
    key = "|".join([
        str(model_version),
        str(season),
        str(week),
        scoring_profile_id,
        league_type_id,
        roster_format_id,
    ])
    return f"trade-score-{_slug(model_version)}-{season}-w{week}-{_short_hash(key)}"


def safe_source_objects() -> tuple[str, ...]:
    return SAFE_SOURCE_OBJECTS


def get_current_trade_player_scores(
    *,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int | str | None = DEFAULT_SCORE_READ_LIMIT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Read current Trade Analyzer scores from the Streamlit-safe compatibility view."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_current_trade_player_scores_query(
        project_id=client.project,
        dataset_id=dataset_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=limit,
    )
    return _query_rows(client, sql, job_config)


def build_current_trade_player_scores_query(
    *,
    project_id: str,
    dataset_id: str,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    limit: int | str | None = DEFAULT_SCORE_READ_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    """Build the bounded score read query for UI use."""

    sql = f"""
    SELECT
        player_id,
        player_id_internal,
        player_name,
        normalized_name,
        position,
        team,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        current_market_value,
        projected_3_year_value,
        market_score,
        projection_score,
        recent_production_score,
        role_usage_score,
        positional_scarcity_score,
        efficiency_score,
        normalized_risk_score,
        fraud_score,
        confidence_score,
        trade_score,
        score_tier,
        source_freshness_json,
        missing_flags_json,
        component_json,
        model_version,
        model_run_id,
        ranking_version,
        feature_config_version_id,
        score_run_id,
        created_at
    FROM `{_table_id(project_id, dataset_id, "compat_trade_player_scores_current")}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
    ORDER BY trade_score DESC, player_name ASC
    LIMIT @limit
    """
    return sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("limit", "INT64", _clamp_limit(limit)),
    ])


def _build_score_row(
    row: dict[str, Any],
    *,
    percentile_context: dict[str, Any],
    season: int,
    week: int,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    model_version: str,
    score_run_id: str,
    created_by: str,
    now: datetime,
) -> dict[str, Any]:
    missing_flags = _missing_flags(row, target_week=week)
    if row.get("player_id_internal") in (None, "") and row.get("source_player_key"):
        missing_flags.append("source_player_key_used_as_player_id")

    market_score = _market_score(row, percentile_context)
    projection_score = _projection_score(row, percentile_context, missing_flags)
    recent_score = _recent_production_score(row, percentile_context, missing_flags)
    role_score = _role_usage_score(row, missing_flags)
    scarcity_score = _positional_scarcity_score(row, roster_format_id, missing_flags)
    efficiency_score = _efficiency_score(row, missing_flags)
    fraud_score = _fraud_score(row)
    normalized_risk_score = _normalized_risk_score(row, missing_flags, fraud_score)
    confidence_breakdown = _confidence_breakdown(row, missing_flags)
    confidence_score = confidence_breakdown["confidence_score"]
    formula = calculate_trade_score(
        market_score=market_score,
        projection_score=projection_score,
        recent_production_score=recent_score,
        role_usage_score=role_score,
        positional_scarcity_score=scarcity_score,
        efficiency_score=efficiency_score,
        normalized_risk_score=normalized_risk_score,
        confidence_score=confidence_score,
    )
    player_id = _clean_str(row.get("player_id_internal")) or _clean_str(row.get("source_player_key"))
    if not player_id:
        player_id = f"unresolved:{_short_hash(row.get('player_name') or row.get('normalized_name') or 'unknown')}"
        missing_flags.append("missing_player_id")

    model_run_id = _clean_str(row.get("projection_model_run_id")) or _clean_str(row.get("asset_model_run_id"))
    component_json = {
        "market_score": market_score,
        "projection_score": projection_score,
        "recent_production_score": recent_score,
        "role_usage_score": role_score,
        "positional_scarcity_score": scarcity_score,
        "efficiency_score": efficiency_score,
        "normalized_risk_score": normalized_risk_score,
        "fraud_score": fraud_score,
        "confidence_score": confidence_score,
        "base_score": formula["base_score"],
        "risk_adjustment": formula["risk_adjustment"],
        "confidence_multiplier": formula["confidence_multiplier"],
        "confidence_breakdown": confidence_breakdown,
        "projection_join": {
            "join_key": row.get("projection_join_key"),
            "join_strategy": row.get("projection_join_strategy"),
        },
        "fallbacks": _fallbacks(row, missing_flags),
        "source_objects": list(SAFE_SOURCE_OBJECTS),
    }
    return {
        "score_run_id": score_run_id,
        "model_run_id": model_run_id,
        "model_version": model_version,
        "player_id": player_id,
        "player_name": _clean_str(row.get("player_name")),
        "normalized_name": _clean_str(row.get("normalized_name")),
        "position": _clean_str(row.get("position")) or "UNK",
        "team": _clean_str(row.get("team")),
        "season": season,
        "week": week,
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "current_market_value": _num(row.get("current_market_value"), None),
        "projected_3_year_value": _num(row.get("projected_3_year_value"), None),
        "market_score": market_score,
        "projection_score": projection_score,
        "recent_production_score": recent_score,
        "role_usage_score": role_score,
        "positional_scarcity_score": scarcity_score,
        "efficiency_score": efficiency_score,
        "normalized_risk_score": normalized_risk_score,
        "fraud_score": fraud_score,
        "confidence_score": confidence_score,
        "trade_score": formula["trade_score"],
        "score_tier": _score_tier(formula["trade_score"]),
        "source_freshness_json": _json_dumps(_source_freshness(row)),
        "missing_flags_json": _json_dumps(sorted(set(missing_flags))),
        "component_json": _json_dumps(component_json),
        "ranking_version": _clean_str(row.get("ranking_version")),
        "feature_config_version_id": f"{model_version}_baseline",
        "created_by": created_by,
        "created_at": _timestamp(now),
    }


def _missing_flags(row: dict[str, Any], *, target_week: int | None = None) -> list[str]:
    flags = []
    flags.extend(_json_array(row.get("asset_missing_data_flags")))
    flags.extend(_json_array(row.get("history_missing_data_flags")))
    flags.extend(_json_array(row.get("fantasy_missing_data_flags")))
    if str(row.get("position") or "").upper() == "PICK":
        flags.append("draft_pick_asset")
        flags.append("draft_pick_score_lane_pending")
    if not row.get("player_id_internal"):
        flags.append("missing_player_id_internal")
    if _num(row.get("current_market_value"), None) is None:
        flags.append("missing_market_value")
    if _num(row.get("projected_3_year_value"), None) is None and _num(row.get("projection_rank_position"), None) is None:
        flags.append("missing_projection_context")
    has_model_run = bool(row.get("projection_model_run_id") or row.get("asset_model_run_id"))
    if has_model_run:
        flags = [flag for flag in flags if flag != "missing_model_run_id"]
    else:
        flags.append("missing_model_run_id")
    projection_join_strategy = _clean_str(row.get("projection_join_strategy"))
    if projection_join_strategy in {"source_player_key", "gsis_id", "player_id_internal"}:
        flags = [flag for flag in flags if flag != "temporary_name_join_identity"]
    elif projection_join_strategy in {"exact_name_position_team", "unique_normalized_name_position_team"}:
        flags.append("projection_name_fallback_used")
    projection_week = _num(row.get("projection_as_of_week"), None)
    safe_target_week = _num(target_week, None)
    if safe_target_week is None:
        safe_target_week = _num(row.get("week"), None)
    if row.get("projection_model_run_id") and projection_week is not None and safe_target_week is not None:
        if projection_week < safe_target_week:
            flags.append("stale_projection_context")
    if _num(row.get("recent_points_per_game"), None) is None and _num(row.get("profile_recent_points"), None) is None:
        flags.append("missing_recent_trade_history")
    if _num(row.get("history_snap_share"), None) is None and _num(row.get("truth_snap_share"), None) is None:
        flags.append("missing_snaps_last_3")
    has_fraud_context = (
        _num(row.get("source_fraud_score"), None) is not None
        or _num(row.get("pigskin_fraud_risk_score"), None) is not None
    )
    if has_fraud_context:
        flags = [flag for flag in flags if flag != "missing_fraud_context"]
    else:
        flags.append("missing_fraud_context")
    if _num(row.get("recent_points_per_game"), None) is None and _num(row.get("truth_recent_points"), None) is not None:
        flags.append("expected_points_proxy_used")
    return sorted(set(flags))


def _market_score(row: dict[str, Any], context: dict[str, Any]) -> float:
    value = _num(row.get("current_market_value"), None)
    if value is None:
        return 35.0
    percentile = _percentile_value(context, row, "current_market_value", value)
    if percentile is not None:
        return percentile
    return round(_clamp(value / 30000.0 * 100.0, 0.0, 100.0), 2)


def _projection_score(row: dict[str, Any], context: dict[str, Any], missing_flags: list[str]) -> float:
    value = _num(row.get("projected_3_year_value"), None)
    if value is not None:
        percentile = _percentile_value(context, row, "projected_3_year_value", value)
        if percentile is not None:
            return percentile
        return round(_clamp(value / 30000.0 * 100.0, 0.0, 100.0), 2)
    rank = _num(row.get("projection_rank_position"), None)
    if rank is not None:
        return round(_clamp(100.0 - (rank - 1.0) * 2.5, 10.0, 100.0), 2)
    pigskin_projection = _num(row.get("pigskin_projection"), None)
    if pigskin_projection is not None:
        missing_flags.append("projection_score_pigskin_projection_proxy")
        return round(_clamp(pigskin_projection, 0.0, 100.0), 2)
    return 45.0


def _recent_production_score(row: dict[str, Any], context: dict[str, Any], missing_flags: list[str]) -> float:
    value = _num(row.get("recent_points_per_game"), None)
    if value is None:
        value = _num(row.get("profile_recent_points"), None)
    if value is None:
        value = _num(row.get("truth_recent_points"), None)
        if value is not None:
            missing_flags.append("expected_points_proxy_used")
    if value is None:
        return 40.0
    percentile = _percentile_value(context, row, "recent_points_per_game", value)
    if percentile is not None:
        return percentile
    return round(_clamp(value / 25.0 * 100.0, 0.0, 100.0), 2)


def _role_usage_score(row: dict[str, Any], missing_flags: list[str]) -> float:
    snap = _num(row.get("history_snap_share"), None)
    if snap is None:
        snap = _num(row.get("truth_snap_share"), None)
    target = _num(row.get("history_target_share"), None)
    if target is None:
        target = _num(row.get("truth_target_share"), None)
    rush = _num(row.get("history_rush_share"), None)
    if rush is None:
        rush = _num(row.get("truth_rush_share"), None)
    touches = _num(row.get("high_value_touches"), None)
    if touches is None:
        touches = _num(row.get("red_zone_touches"), None)

    parts = []
    if snap is not None:
        parts.append(_clamp(snap * 100.0, 0.0, 100.0))
    if target is not None:
        parts.append(_clamp(target * 250.0, 0.0, 100.0))
    if rush is not None:
        parts.append(_clamp(rush * 220.0, 0.0, 100.0))
    if touches is not None:
        parts.append(_clamp(touches * 12.0, 0.0, 100.0))
    role_quality = _num(row.get("role_quality_score"), None)
    if role_quality is not None:
        parts.append(_clamp(role_quality, 0.0, 100.0))
    if not parts:
        missing_flags.append("role_usage_fallback_used")
        return 42.0
    return round(sum(parts) / len(parts), 2)


def _positional_scarcity_score(row: dict[str, Any], roster_format_id: str, missing_flags: list[str]) -> float:
    raw = _num(row.get("asset_position_scarcity_score"), None)
    if raw is None:
        missing_flags.append("missing_position_scarcity_score")
        raw_score = 50.0
    else:
        raw_score = _clamp(50.0 + raw * 25.0, 0.0, 100.0)
    position = str(row.get("position") or "").upper()
    if position == "QB" and roster_format_id in {"superflex", "two_qb"}:
        raw_score += 12.0
    elif position == "TE":
        raw_score += 4.0
    return round(_clamp(raw_score, 0.0, 100.0), 2)


def _efficiency_score(row: dict[str, Any], missing_flags: list[str]) -> float:
    position = str(row.get("position") or "").upper()
    yards_per_target = _num(row.get("yards_per_target"), None)
    yards_per_carry = _num(row.get("yards_per_carry"), None)
    yards_per_reception = _num(row.get("yards_per_reception"), None)
    catch_rate = _num(row.get("catch_rate"), None)
    parts = []
    if position in {"WR", "TE"}:
        if yards_per_target is not None:
            parts.append(_clamp(yards_per_target / 12.0 * 100.0, 0.0, 100.0))
        if yards_per_reception is not None:
            parts.append(_clamp(yards_per_reception / 18.0 * 100.0, 0.0, 100.0))
        if catch_rate is not None:
            parts.append(_clamp(catch_rate * 100.0, 0.0, 100.0))
    elif position == "RB":
        if yards_per_carry is not None:
            parts.append(_clamp(yards_per_carry / 6.0 * 100.0, 0.0, 100.0))
        if yards_per_target is not None:
            parts.append(_clamp(yards_per_target / 9.0 * 100.0, 0.0, 100.0))
    else:
        if yards_per_carry is not None:
            parts.append(_clamp(yards_per_carry / 8.0 * 100.0, 0.0, 100.0))
    if not parts:
        missing_flags.append("efficiency_fallback_used")
        return 50.0
    return round(sum(parts) / len(parts), 2)


def _fraud_score(row: dict[str, Any]) -> float:
    fraud = _num(row.get("source_fraud_score"), None)
    if fraud is None:
        fraud = _num(row.get("pigskin_fraud_risk_score"), None)
    return round(_clamp(fraud if fraud is not None else 0.0, 0.0, 100.0), 2)


def _normalized_risk_score(row: dict[str, Any], missing_flags: list[str], fraud_score: float) -> float:
    risk_values = [fraud_score / 100.0]
    projection_risk = _num(row.get("projection_risk_score"), None)
    if projection_risk is not None:
        risk_values.append(_clamp(projection_risk / 100.0, 0.0, 1.0))
    role_fragility = _num(row.get("role_fragility_score"), None)
    if role_fragility is not None:
        risk_values.append(_clamp(role_fragility / 100.0, 0.0, 1.0))
    missing_penalty = min(0.25, len(set(missing_flags)) * 0.025)
    risk = max(risk_values) + missing_penalty
    return round(_clamp(risk, 0.0, 1.0), 4)


def _confidence_breakdown(row: dict[str, Any], missing_flags: list[str]) -> dict[str, Any]:
    confidence = 92.0
    starting_confidence = confidence
    blend_steps = []
    projection_confidence = _num(row.get("projection_confidence_score"), None)
    if projection_confidence is not None:
        confidence = (confidence + _clamp(projection_confidence, 0.0, 100.0)) / 2.0
        blend_steps.append({
            "source": "projection_rankings_current",
            "value": round(_clamp(projection_confidence, 0.0, 100.0), 2),
            "confidence_after_blend": round(confidence, 2),
        })
    pigskin_confidence = _num(row.get("pigskin_confidence"), None)
    if pigskin_confidence is not None:
        confidence = (confidence + _clamp(pigskin_confidence, 0.0, 100.0)) / 2.0
        blend_steps.append({
            "source": "compat_trade_assets_current",
            "value": round(_clamp(pigskin_confidence, 0.0, 100.0), 2),
            "confidence_after_blend": round(confidence, 2),
        })
    sample_size = max(
        _num(row.get("history_sample_size"), 0.0) or 0.0,
        _num(row.get("fantasy_profile_sample_size"), 0.0) or 0.0,
    )
    sample_size_penalty = 8.0 if sample_size < 2 else 0.0
    if sample_size < 2:
        confidence -= 8.0
    missing_flag_count = len(set(missing_flags))
    missing_flag_penalty = min(35.0, missing_flag_count * 4.0)
    confidence -= missing_flag_penalty
    final_confidence = round(_clamp(confidence, 0.0, 100.0), 2)
    return {
        "starting_confidence": starting_confidence,
        "blend_steps": blend_steps,
        "sample_size": sample_size,
        "sample_size_penalty": sample_size_penalty,
        "missing_flag_count": missing_flag_count,
        "missing_flag_penalty": missing_flag_penalty,
        "confidence_score": final_confidence,
    }


def _confidence_score(row: dict[str, Any], missing_flags: list[str]) -> float:
    return _confidence_breakdown(row, missing_flags)["confidence_score"]


def _score_tier(score: float) -> str:
    if score >= 88:
        return "elite"
    if score >= 74:
        return "strong"
    if score >= 60:
        return "starter"
    if score >= 45:
        return "flex"
    if score >= 30:
        return "depth"
    return "avoid"


def _percentile_context(rows: list[dict[str, Any]]) -> dict[str, dict[str, list[float]]]:
    context: dict[str, dict[str, list[float]]] = {}
    for field in ("current_market_value", "projected_3_year_value", "recent_points_per_game"):
        context[field] = {}
        for row in rows:
            value = _num(row.get(field), None)
            if field == "recent_points_per_game" and value is None:
                value = _num(row.get("profile_recent_points"), None)
            if value is None:
                continue
            position = str(row.get("position") or "ALL").upper()
            context[field].setdefault(position, []).append(value)
    return context


def _percentile_value(context: dict[str, Any], row: dict[str, Any], field: str, value: float) -> float | None:
    position = str(row.get("position") or "ALL").upper()
    values = context.get(field, {}).get(position, [])
    if len(values) < 2:
        return None
    ordered = sorted(values)
    lower_count = sum(1 for candidate in ordered if candidate < value)
    equal_count = sum(1 for candidate in ordered if candidate == value)
    percentile = (lower_count + 0.5 * equal_count) / len(ordered) * 100.0
    return round(_clamp(percentile, 0.0, 100.0), 2)


def _source_freshness(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "sources": {
            "compat_trade_assets_current": _parse_json(row.get("asset_source_freshness_json"), None),
            "compat_trade_player_history": _parse_json(row.get("history_source_freshness_json"), None),
            "analytics_player_fantasy_points_by_profile": _parse_json(row.get("fantasy_source_freshness_json"), None),
            "analytics_fraud_watch": {
                "season": row.get("season"),
                "week": row.get("week"),
                "label": row.get("fraud_label"),
                "join_key": row.get("fraud_join_key"),
                "join_strategy": row.get("fraud_join_strategy"),
            },
            "projection_rankings_current": {
                "model_run_id": row.get("projection_model_run_id"),
                "projection_horizon": row.get("projection_horizon"),
                "as_of_season": row.get("projection_as_of_season"),
                "as_of_week": row.get("projection_as_of_week"),
                "created_at": _clean_str(row.get("projection_created_at")),
                "join_key": row.get("projection_join_key"),
                "join_strategy": row.get("projection_join_strategy"),
            },
        }
    }


def _fallbacks(row: dict[str, Any], missing_flags: list[str]) -> list[str]:
    fallbacks = []
    if "expected_points_proxy_used" in missing_flags:
        fallbacks.append("used analytics_player_weekly_truth fantasy_points_ppr as recent production proxy")
    if "missing_projection_context" in missing_flags:
        fallbacks.append("used neutral projection score")
    if "role_usage_fallback_used" in missing_flags:
        fallbacks.append("used neutral role usage score")
    if "efficiency_fallback_used" in missing_flags:
        fallbacks.append("used neutral efficiency score")
    if "missing_position_scarcity_score" in missing_flags:
        fallbacks.append("used neutral positional scarcity score")
    if row.get("source_player_key") and not row.get("player_id_internal"):
        fallbacks.append("used source_player_key as player_id with missing identity flag")
    if "projection_name_fallback_used" in missing_flags:
        fallbacks.append("attached projection context with unique player name fallback")
    return fallbacks


def _preview_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "player_id": row.get("player_id"),
        "player_name": row.get("player_name"),
        "position": row.get("position"),
        "team": row.get("team"),
        "trade_score": row.get("trade_score"),
        "score_tier": row.get("score_tier"),
        "confidence_score": row.get("confidence_score"),
        "missing_flags": _json_array(row.get("missing_flags_json"))[:8],
    }


def _stats(values: list[float | None]) -> dict[str, float | int | None]:
    clean_values = [float(value) for value in values if value is not None]
    if not clean_values:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "avg": None,
        }
    return {
        "count": len(clean_values),
        "min": round(min(clean_values), 4),
        "max": round(max(clean_values), 4),
        "avg": round(sum(clean_values) / len(clean_values), 4),
    }


def _output_schema() -> list[bigquery.SchemaField]:
    float_fields = {
        "current_market_value",
        "projected_3_year_value",
        "market_score",
        "projection_score",
        "recent_production_score",
        "role_usage_score",
        "positional_scarcity_score",
        "efficiency_score",
        "normalized_risk_score",
        "fraud_score",
        "confidence_score",
        "trade_score",
    }
    int_fields = {"season", "week"}
    timestamp_fields = {"created_at"}
    schema = []
    for field in OUTPUT_FIELDS:
        if field in float_fields:
            schema.append(bigquery.SchemaField(field, "FLOAT64"))
        elif field in int_fields:
            schema.append(bigquery.SchemaField(field, "INT64"))
        elif field in timestamp_fields:
            schema.append(bigquery.SchemaField(field, "TIMESTAMP"))
        else:
            schema.append(bigquery.SchemaField(field, "STRING"))
    return schema


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


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    if not IDENTIFIER_RE.match(table_name):
        raise ValueError(f"Unsafe BigQuery table name: {table_name}")
    return f"{project_id}.{dataset_id}.{table_name}"


def _row_to_dict(row: Any) -> dict[str, Any]:
    if hasattr(row, "items"):
        return dict(row.items())
    if isinstance(row, dict):
        return dict(row)
    return dict(row)


def _required_int(value: int | str | None, name: str) -> int:
    if value in (None, ""):
        raise ValueError(f"{name} is required")
    return int(value)


def _clamp_limit(value: int | str | None) -> int:
    try:
        parsed = int(value) if value is not None else DEFAULT_LIMIT
    except (TypeError, ValueError):
        parsed = DEFAULT_LIMIT
    return max(1, min(MAX_LIMIT, parsed))


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def _num(value: Any, default: float | None = 0.0) -> float | None:
    if value in (None, ""):
        return default
    try:
        if isinstance(value, float) and math.isnan(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _clean_str(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _json_array(value: Any) -> list[str]:
    parsed = _parse_json(value, [])
    if isinstance(parsed, list):
        return [str(item) for item in parsed if item not in (None, "")]
    return []


def _parse_json(value: Any, default: Any) -> Any:
    if value in (None, ""):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return default


def _timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _short_hash(value: Any) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:12]


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", value).strip("_").lower() or "score"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build deterministic Trade Analyzer score v0 rows.")
    parser.add_argument("--season", required=True, type=int)
    parser.add_argument("--week", required=True, type=int)
    parser.add_argument("--scoring-profile-id", default=DEFAULT_SCORING_PROFILE)
    parser.add_argument("--league-type-id", default=DEFAULT_LEAGUE_TYPE)
    parser.add_argument("--roster-format-id", default=DEFAULT_ROSTER_FORMAT)
    parser.add_argument("--model-version", default=DEFAULT_MODEL_VERSION)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dataset", default=get_bigquery_dataset())
    parser.add_argument("--project")
    args = parser.parse_args()

    dry_run = args.dry_run or not args.write
    result = build_trade_player_scores(
        season=args.season,
        week=args.week,
        scoring_profile_id=args.scoring_profile_id,
        league_type_id=args.league_type_id,
        roster_format_id=args.roster_format_id,
        model_version=args.model_version,
        limit=args.limit,
        dry_run=dry_run,
        write=args.write,
        dataset_id=args.dataset,
        project_id=args.project,
    )
    output = {
        key: value
        for key, value in result.items()
        if key != "rows"
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
