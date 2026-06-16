"""Materialize viewer-team context packets."""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.load import get_bigquery_project
from src.model_runs import get_latest_model_run


logger = logging.getLogger(__name__)

DEFAULT_DATASET = "fantasy_football_brain"
OUTPUT_TABLE = "mart_viewer_team_context"
DEFAULT_SCORING_PROFILE = "ppr"
DEFAULT_LEAGUE_TYPE = "redraft"
DEFAULT_ROSTER_FORMAT = "one_qb"
PACKET_TEXT_MAX_CHARS = 12000
SOURCE_TABLES = (
    "sleeper_leagues",
    "sleeper_rosters",
    "sleeper_roster_players",
    "sleeper_lineups",
    "sleeper_available_players",
    "sleeper_players_current",
    "sleeper_viewer_team_snapshots",
    "dim_players_current",
    "player_identity_bridge",
    "analytics_pigskin_rankings",
    "compat_trade_assets_current",
    "compat_sleeper_watch_candidates",
    "compat_player_profiles_current",
    "compat_trade_player_history",
    "llm_player_context_packet",
)
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
OUTPUT_COLUMNS_SQL = """
    context_id,
    league_id,
    season,
    week,
    viewer_roster_id,
    viewer_team_name,
    roster_rows_json,
    lineup_rows_json,
    waiver_rows_json,
    pigskin_evidence_json,
    rank_tier_json,
    source_freshness_json,
    missing_data_flags,
    created_at,
    updated_at,
    viewer_team_context_id,
    roster_id,
    manager_id,
    manager_display_name,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    model_run_id,
    ranking_version,
    snapshot_timestamp,
    packet_json,
    packet_text
"""


@dataclass(frozen=True)
class SourceTableStatus:
    exists: bool
    row_count: int | None = None
    modified: datetime | None = None


@dataclass(frozen=True)
class SnapshotContext:
    league_id: str
    season: int
    week: int
    snapshot_at: datetime


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def table_status(client: bigquery.Client, dataset_id: str, table_name: str) -> SourceTableStatus:
    try:
        table = client.get_table(f"{client.project}.{dataset_id}.{table_name}")
        return SourceTableStatus(True, table.num_rows, table.modified)
    except NotFound:
        return SourceTableStatus(False)


def inspect_source_status(client: bigquery.Client, dataset_id: str) -> dict[str, SourceTableStatus]:
    return {table_name: table_status(client, dataset_id, table_name) for table_name in SOURCE_TABLES}


def resolve_snapshot_context(
    client: bigquery.Client,
    dataset_id: str,
    *,
    league_id: str | None = None,
    roster_id: int | None = None,
    manager_id: str | None = None,
    season: int | None = None,
    week: int | None = None,
) -> SnapshotContext | None:
    if table_status(client, dataset_id, "sleeper_rosters").exists:
        sql = f"""
        SELECT league_id, season, week, MAX(snapshot_at) AS snapshot_at
        FROM `{client.project}.{dataset_id}.sleeper_rosters`
        WHERE (@league_id IS NULL OR league_id = @league_id)
            AND (@season IS NULL OR season = @season)
            AND (@week IS NULL OR week = @week)
            AND (@roster_id IS NULL OR roster_id = @roster_id)
            AND (@manager_id IS NULL OR owner_id = @manager_id)
        GROUP BY league_id, season, week
        ORDER BY snapshot_at DESC
        LIMIT 1
        """
    elif table_status(client, dataset_id, "sleeper_viewer_team_snapshots").exists:
        sql = f"""
        SELECT league_id, season, week, MAX(snapshot_at) AS snapshot_at
        FROM `{client.project}.{dataset_id}.sleeper_viewer_team_snapshots`
        WHERE (@league_id IS NULL OR league_id = @league_id)
            AND (@season IS NULL OR season = @season)
            AND (@week IS NULL OR week = @week)
            AND (@roster_id IS NULL OR viewer_roster_id = @roster_id)
            AND (@manager_id IS NULL OR viewer_owner_id = @manager_id)
        GROUP BY league_id, season, week
        ORDER BY snapshot_at DESC
        LIMIT 1
        """
    else:
        return None

    rows = list(client.query(
        sql,
        job_config=bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("league_id", "STRING", _clean_optional(league_id)),
            bigquery.ScalarQueryParameter("season", "INT64", season),
            bigquery.ScalarQueryParameter("week", "INT64", week),
            bigquery.ScalarQueryParameter("roster_id", "INT64", roster_id),
            bigquery.ScalarQueryParameter("manager_id", "STRING", _clean_optional(manager_id)),
        ]),
    ).result())
    if not rows:
        return None
    row = rows[0]
    return SnapshotContext(
        league_id=str(row.league_id),
        season=int(row.season),
        week=int(row.week),
        snapshot_at=row.snapshot_at,
    )


def resolve_model_run_id(
    client: bigquery.Client,
    dataset_id: str,
    *,
    model_run_id: str | None = None,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
) -> str | None:
    if model_run_id:
        return model_run_id
    try:
        latest = get_latest_model_run(
            client=client,
            dataset_id=dataset_id,
            run_type="pigskin_rankings",
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            status="complete",
        )
    except Exception as exc:
        logger.warning("Could not resolve latest Pigskin model run: %s", exc)
        return None
    return latest.get("model_run_id") if latest else None


def build_viewer_team_context_sql(
    *,
    project_id: str,
    dataset_id: str,
    source_status: dict[str, SourceTableStatus] | None = None,
) -> str:
    _validate_identifier(dataset_id, "dataset_id")
    source_status = source_status or {
        table_name: SourceTableStatus(False) for table_name in SOURCE_TABLES
    }
    source_flags = {
        table_name: "TRUE" if source_status.get(table_name, SourceTableStatus(False)).exists else "FALSE"
        for table_name in SOURCE_TABLES
    }
    return f"""
DELETE FROM `{project_id}.{dataset_id}.{OUTPUT_TABLE}`
WHERE league_id = @league_id
    AND season = @season
    AND week = @week
    AND (@roster_id IS NULL OR COALESCE(roster_id, viewer_roster_id) = @roster_id)
    AND scoring_profile_id = @scoring_profile_id
    AND league_type_id = @league_type_id
    AND roster_format_id = @roster_format_id;

INSERT INTO `{project_id}.{dataset_id}.{OUTPUT_TABLE}` (
{OUTPUT_COLUMNS_SQL}
)
WITH
run_context AS (
    SELECT
        @league_id AS league_id,
        @season AS season,
        @week AS week,
        @roster_id AS roster_id,
        @manager_id AS manager_id,
        @snapshot_timestamp AS snapshot_timestamp,
        @scoring_profile_id AS scoring_profile_id,
        @league_type_id AS league_type_id,
        @roster_format_id AS roster_format_id,
        @model_run_id AS requested_model_run_id,
        @source_freshness_json AS source_freshness_json,
        CURRENT_TIMESTAMP() AS refreshed_at
),
{_base_teams_ctes(project_id, dataset_id, source_status)},
{_identity_cte(project_id, dataset_id, source_status)},
{_rankings_cte(project_id, dataset_id, source_status["analytics_pigskin_rankings"])},
{_trade_assets_cte(project_id, dataset_id, source_status["compat_trade_assets_current"])},
{_player_profiles_cte(project_id, dataset_id, source_status["compat_player_profiles_current"])},
{_trade_history_cte(project_id, dataset_id, source_status["compat_trade_player_history"])},
{_llm_packets_cte(project_id, dataset_id, source_status["llm_player_context_packet"])},
{_roster_players_cte(project_id, dataset_id, source_status)},
{_waiver_candidates_cte(project_id, dataset_id, source_status["compat_sleeper_watch_candidates"])},
enriched_roster AS (
    SELECT
        rp.league_id,
        rp.season,
        rp.week,
        rp.roster_id,
        COALESCE(id.player_id_internal, CONCAT('source:', rp.source_player_key)) AS player_id_internal,
        rp.source_player_key,
        COALESCE(id.sleeper_player_id, rp.sleeper_player_id) AS sleeper_player_id,
        COALESCE(id.display_name, rp.player_name) AS display_name,
        COALESCE(id.normalized_name, rp.normalized_name) AS normalized_name,
        COALESCE(id.position, rp.position) AS position,
        COALESCE(id.current_team, rp.team) AS team,
        COALESCE(id.active_status, rp.status) AS active_status,
        rp.injury_status,
        rp.is_starter AS starter_flag,
        NOT COALESCE(rp.is_starter, FALSE) AS bench_flag,
        COALESCE(rp.is_taxi, FALSE) AS taxi_flag,
        COALESCE(rp.is_reserve, FALSE) AS reserve_flag,
        IF(COALESCE(rp.is_starter, FALSE), 'STARTER', IF(COALESCE(rp.is_reserve, FALSE), 'RESERVE', IF(COALESCE(rp.is_taxi, FALSE), 'TAXI', 'BENCH'))) AS lineup_slot,
        rp.week_points,
        r.ranking_version,
        r.model_run_id,
        r.pigskin_rank_overall,
        r.pigskin_rank_position,
        r.pigskin_tier,
        r.pigskin_projection,
        r.pigskin_confidence,
        ta.market_value AS trade_asset_value,
        th.recent_points,
        th.role_trend,
        pp.evidence_summary AS profile_evidence_summary,
        pp.breakout_score,
        pp.risk_score,
        lp.packet_text AS llm_packet_text,
        CASE
            WHEN id.player_id_internal IS NULL THEN 'temporary_source_key_identity'
            WHEN STARTS_WITH(id.player_id_internal, 'sleeper:') THEN 'sleeper_current_map_identity'
            WHEN rp.sleeper_player_id IS NOT NULL AND id.sleeper_player_id = rp.sleeper_player_id THEN 'sleeper'
            WHEN rp.gsis_id IS NOT NULL AND id.gsis_id = rp.gsis_id THEN 'gsis'
            ELSE 'identity'
        END AS identity_match_method
    FROM roster_players rp
    LEFT JOIN identity id
        ON (
            rp.sleeper_player_id IS NOT NULL
            AND id.sleeper_player_id = rp.sleeper_player_id
        )
        OR (
            rp.sleeper_player_id IS NULL
            AND
            rp.gsis_id IS NOT NULL
            AND id.gsis_id = rp.gsis_id
        )
        OR (
            rp.sleeper_player_id IS NULL
            AND rp.gsis_id IS NULL
            AND
            rp.normalized_name = id.normalized_name
            AND rp.position = id.position
        )
    LEFT JOIN rankings r
        ON (
            rp.gsis_id IS NOT NULL
            AND r.player_id = rp.gsis_id
            AND r.position = rp.position
        )
        OR (
            rp.sleeper_player_id IS NOT NULL
            AND r.sleeper_player_id = rp.sleeper_player_id
            AND r.position = rp.position
        )
        OR (
            rp.normalized_name = r.normalized_name
            AND rp.position = r.position
        )
    LEFT JOIN trade_assets ta
        ON (
            id.player_id_internal IS NOT NULL
            AND ta.player_id_internal = id.player_id_internal
        )
        OR (
            rp.sleeper_player_id IS NOT NULL
            AND ta.sleeper_player_id = rp.sleeper_player_id
        )
        OR (
            rp.normalized_name = ta.normalized_name
            AND rp.position = ta.position
        )
    LEFT JOIN trade_history th
        ON (
            id.player_id_internal IS NOT NULL
            AND th.player_id_internal = id.player_id_internal
        )
        OR (
            rp.source_player_key = th.source_player_key
        )
        OR (
            rp.normalized_name = th.normalized_name
            AND rp.position = th.position
        )
    LEFT JOIN player_profiles pp
        ON (
            id.player_id_internal IS NOT NULL
            AND pp.player_id_internal = id.player_id_internal
        )
        OR (
            rp.sleeper_player_id IS NOT NULL
            AND pp.sleeper_player_id = rp.sleeper_player_id
        )
        OR (
            rp.normalized_name = pp.normalized_name
            AND rp.position = pp.position
        )
    LEFT JOIN llm_packets lp
        ON (
            id.player_id_internal IS NOT NULL
            AND lp.player_id_internal = id.player_id_internal
        )
        OR (
            rp.source_player_key = lp.source_player_key
        )
),
team_packets AS (
    SELECT
        league_id,
        season,
        week,
        roster_id,
        ARRAY_AGG(STRUCT(
            player_id_internal,
            sleeper_player_id,
            display_name,
            position,
            team,
            active_status,
            lineup_slot,
            starter_flag,
            bench_flag,
            IF(injury_status IS NOT NULL AND LOWER(injury_status) NOT IN ('', 'healthy'), TRUE, FALSE) AS injured_flag,
            CAST(NULL AS INT64) AS bye_week,
            pigskin_rank_overall,
            pigskin_rank_position,
            pigskin_tier,
            pigskin_projection AS projected_points,
            trade_asset_value,
            recent_points,
            role_trend,
            risk_score,
            breakout_score,
            CAST(NULL AS FLOAT64) AS fraud_risk_score,
            COALESCE(profile_evidence_summary, SUBSTR(llm_packet_text, 1, 400)) AS evidence_summary,
            TO_JSON_STRING(ARRAY(
                SELECT DISTINCT flag
                FROM UNNEST(ARRAY_CONCAT(
                    IF(STARTS_WITH(player_id_internal, 'source:') OR STARTS_WITH(player_id_internal, 'sleeper:'), ['missing_canonical_player_id_internal'], []),
                    IF(sleeper_player_id IS NULL, ['missing_sleeper_player_id'], []),
                    IF(pigskin_rank_position IS NULL, ['missing_pigskin_rank'], []),
                    IF(trade_asset_value IS NULL, ['missing_trade_asset_value'], []),
                    IF(recent_points IS NULL, ['missing_recent_points'], []),
                    IF(identity_match_method = 'sleeper_current_map_identity', ['sleeper_current_map_identity'], []),
                    IF(identity_match_method = 'temporary_source_key_identity', ['temporary_source_key_identity'], [])
                )) AS flag
                WHERE flag IS NOT NULL
                ORDER BY flag
            )) AS missing_data_flags
        ) ORDER BY starter_flag DESC, position, display_name) AS roster_rows,
        ARRAY_AGG(IF(starter_flag, STRUCT(
            player_id_internal,
            sleeper_player_id,
            display_name,
            position,
            team,
            active_status,
            pigskin_rank_position,
            pigskin_tier,
            pigskin_projection AS projected_points,
            recent_points,
            risk_score
        ), NULL) IGNORE NULLS ORDER BY position, display_name) AS lineup_rows,
        ARRAY_AGG(IF(NOT starter_flag, STRUCT(
            player_id_internal,
            sleeper_player_id,
            display_name,
            position,
            team,
            pigskin_rank_position,
            pigskin_tier,
            trade_asset_value,
            recent_points,
            breakout_score
        ), NULL) IGNORE NULLS ORDER BY COALESCE(trade_asset_value, 0) DESC, display_name) AS bench_rows,
        ARRAY_AGG(IF(starter_flag AND (pigskin_rank_position IS NULL OR pigskin_rank_position > CASE position WHEN 'QB' THEN 18 WHEN 'RB' THEN 36 WHEN 'WR' THEN 48 WHEN 'TE' THEN 18 ELSE 50 END), STRUCT(
            display_name,
            position,
            pigskin_rank_position,
            pigskin_tier,
            recent_points,
            risk_score
        ), NULL) IGNORE NULLS ORDER BY position, pigskin_rank_position) AS weak_starter_slots,
        ARRAY_AGG(IF(NOT starter_flag AND COALESCE(trade_asset_value, 0) > 0, STRUCT(
            display_name,
            position,
            pigskin_rank_position,
            trade_asset_value
        ), NULL) IGNORE NULLS ORDER BY trade_asset_value DESC LIMIT 12) AS trade_chips,
        COUNTIF(position = 'QB') AS qb_count,
        COUNTIF(position = 'RB') AS rb_count,
        COUNTIF(position = 'WR') AS wr_count,
        COUNTIF(position = 'TE') AS te_count,
        COUNTIF(starter_flag) AS starter_count,
        COUNTIF(injury_status IS NOT NULL AND LOWER(injury_status) NOT IN ('', 'healthy')) AS injury_count,
        COUNTIF(pigskin_rank_position <= 50) AS top_50_rank_count,
        SUM(COALESCE(trade_asset_value, 0)) AS trade_value_total,
        COUNTIF(STARTS_WITH(player_id_internal, 'source:')) AS missing_identity_count,
        COUNTIF(STARTS_WITH(player_id_internal, 'source:') OR STARTS_WITH(player_id_internal, 'sleeper:')) AS missing_canonical_identity_count,
        ARRAY_AGG(DISTINCT ranking_version IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS ranking_version,
        ARRAY_AGG(DISTINCT model_run_id IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS model_run_id
    FROM enriched_roster
    GROUP BY league_id, season, week, roster_id
),
waiver_packets AS (
    SELECT
        rc.league_id,
        rc.season,
        rc.week,
        ARRAY_AGG(STRUCT(
            player_id_internal,
            sleeper_player_id,
            display_name,
            position,
            team,
            rostered_rate,
            waiver_candidate_flag,
            streamer_score,
            breakout_score,
            pigskin_rank_position,
            pigskin_tier,
            candidate_reason,
            missing_data_flags
        ) ORDER BY streamer_score DESC, breakout_score DESC, display_name LIMIT 40) AS waiver_rows
    FROM run_context rc
    JOIN waiver_candidates wc
        ON wc.season = rc.season
        AND wc.week = rc.week
        AND (
            wc.league_id = rc.league_id
            OR wc.league_id IS NULL
        )
    GROUP BY rc.league_id, rc.season, rc.week
),
final_packets AS (
    SELECT
        TO_HEX(MD5(CONCAT(bt.league_id, '|', CAST(bt.roster_id AS STRING), '|', CAST(bt.season AS STRING), '|', CAST(bt.week AS STRING), '|', rc.scoring_profile_id, '|', rc.league_type_id, '|', rc.roster_format_id))) AS viewer_team_context_id,
        bt.league_id,
        bt.roster_id,
        bt.manager_id,
        bt.manager_display_name,
        bt.season,
        bt.week,
        rc.scoring_profile_id,
        rc.league_type_id,
        rc.roster_format_id,
        COALESCE(tp.model_run_id, rc.requested_model_run_id) AS model_run_id,
        tp.ranking_version,
        bt.snapshot_at AS snapshot_timestamp,
        tp.roster_rows,
        tp.lineup_rows,
        tp.bench_rows,
        wp.waiver_rows,
        tp.weak_starter_slots,
        tp.trade_chips,
        tp.qb_count,
        tp.rb_count,
        tp.wr_count,
        tp.te_count,
        tp.starter_count,
        tp.injury_count,
        tp.top_50_rank_count,
        tp.trade_value_total,
        tp.missing_identity_count,
        tp.missing_canonical_identity_count,
        bt.league_name,
        bt.roster_positions_json,
        bt.scoring_settings_json,
        bt.raw_settings_json,
        bt.wins,
        bt.losses,
        bt.ties,
        bt.points_for,
        bt.points_against,
        bt.matchup_id,
        bt.matchup_points,
        rc.source_freshness_json,
        rc.refreshed_at
    FROM base_teams bt
    CROSS JOIN run_context rc
    LEFT JOIN team_packets tp
        ON tp.league_id = bt.league_id
        AND tp.season = bt.season
        AND tp.week = bt.week
        AND tp.roster_id = bt.roster_id
    LEFT JOIN waiver_packets wp
        ON wp.league_id = bt.league_id
        AND wp.season = bt.season
        AND wp.week = bt.week
),
packet_ready AS (
    SELECT
        fp.*,
        TO_JSON_STRING(ARRAY(
            SELECT DISTINCT flag
            FROM UNNEST(ARRAY_CONCAT(
                IF(roster_rows IS NULL, ['missing_roster_rows'], []),
                IF(lineup_rows IS NULL, ['missing_lineup_rows'], []),
                IF(waiver_rows IS NULL, ['missing_waiver_rows'], []),
                IF(model_run_id IS NULL, ['missing_model_run_id'], []),
                IF(ranking_version IS NULL, ['missing_ranking_version'], []),
                IF(missing_identity_count > 0, ['missing_player_identity_rows'], []),
                IF(missing_canonical_identity_count > 0, ['missing_canonical_player_identity_rows'], []),
                IF(NOT {source_flags["sleeper_rosters"]}, ['missing_sleeper_rosters_source'], []),
                IF(NOT {source_flags["sleeper_roster_players"]}, ['missing_sleeper_roster_players_source'], []),
                IF(NOT {source_flags["sleeper_lineups"]}, ['missing_sleeper_lineups_source'], []),
                IF(NOT {source_flags["sleeper_available_players"]}, ['missing_sleeper_available_players_source'], []),
                IF(NOT {source_flags["sleeper_players_current"]}, ['missing_sleeper_players_current_source'], []),
                IF(NOT {source_flags["compat_sleeper_watch_candidates"]}, ['missing_sleeper_watch_source'], []),
                IF(NOT {source_flags["compat_trade_assets_current"]}, ['missing_trade_asset_source'], []),
                IF(NOT {source_flags["analytics_pigskin_rankings"]}, ['missing_rankings_source'], [])
            )) AS flag
            WHERE flag IS NOT NULL
            ORDER BY flag
        )) AS missing_data_flags
    FROM final_packets fp
)
SELECT
    viewer_team_context_id AS context_id,
    league_id,
    season,
    week,
    roster_id AS viewer_roster_id,
    manager_display_name AS viewer_team_name,
    TO_JSON_STRING(roster_rows) AS roster_rows_json,
    TO_JSON_STRING(lineup_rows) AS lineup_rows_json,
    TO_JSON_STRING(waiver_rows) AS waiver_rows_json,
    TO_JSON_STRING(STRUCT(
        model_run_id AS model_run_id,
        ranking_version AS ranking_version,
        top_50_rank_count AS top_50_rank_count,
        missing_identity_count AS missing_identity_count,
        missing_canonical_identity_count AS missing_canonical_identity_count
    )) AS pigskin_evidence_json,
    TO_JSON_STRING(STRUCT(
        ranking_version AS ranking_version,
        top_50_rank_count AS top_50_rank_count
    )) AS rank_tier_json,
    source_freshness_json,
    missing_data_flags,
    refreshed_at AS created_at,
    refreshed_at AS updated_at,
    viewer_team_context_id,
    roster_id,
    manager_id,
    manager_display_name,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    model_run_id,
    ranking_version,
    snapshot_timestamp,
    TO_JSON_STRING(STRUCT(
        STRUCT(
            league_id AS league_id,
            league_name AS league_name,
            season AS season,
            week AS week,
            scoring_profile_id AS scoring_profile_id,
            league_type_id AS league_type_id,
            roster_format_id AS roster_format_id,
            roster_positions_json AS roster_positions,
            scoring_settings_json AS scoring_summary,
            CAST(NULL AS STRING) AS playoff_week_context
        ) AS league_context,
        STRUCT(
            roster_id AS roster_id,
            manager_id AS manager_id,
            manager_display_name AS manager_display_name,
            STRUCT(wins AS wins, losses AS losses, ties AS ties) AS current_record,
            points_for AS current_points_for,
            points_against AS current_points_against,
            STRUCT(matchup_id AS matchup_id, matchup_points AS matchup_points) AS matchup_context
        ) AS team_context,
        roster_rows AS roster_rows,
        STRUCT(
            lineup_rows AS current_starters,
            CAST(NULL AS STRING) AS recommended_starters_placeholder,
            CAST(NULL AS FLOAT64) AS projected_starter_total_placeholder,
            weak_starter_slots AS weak_starter_slots
        ) AS lineup_rows,
        STRUCT(
            bench_rows AS bench_assets,
            ARRAY(
                SELECT AS STRUCT item.*
                FROM UNNEST(bench_rows) item
                WHERE COALESCE(item.breakout_score, 0) >= 60
                LIMIT 10
            ) AS stash_candidates,
            CAST(NULL AS STRING) AS drop_candidates_placeholder,
            trade_chips AS trade_chips
        ) AS bench_rows,
        STRUCT(
            waiver_rows AS available_players,
            waiver_rows AS streamer_candidates,
            waiver_rows AS replacement_options_by_position,
            IF(waiver_rows IS NULL, ['missing_waiver_rows'], []) AS missing_data_flags
        ) AS waiver_rows,
        STRUCT(
            ARRAY(
                SELECT label
                FROM UNNEST([
                    IF(qb_count >= 2, 'QB depth', NULL),
                    IF(rb_count >= 5, 'RB depth', NULL),
                    IF(wr_count >= 5, 'WR depth', NULL),
                    IF(te_count >= 2, 'TE depth', NULL),
                    IF(top_50_rank_count >= 4, 'high-end Pigskin ranks', NULL)
                ]) AS label
                WHERE label IS NOT NULL
            ) AS positional_strengths,
            ARRAY(
                SELECT label
                FROM UNNEST([
                    IF(trade_value_total >= 10000, 'tradeable asset value', NULL),
                    IF(starter_count >= 8, 'full active lineup', NULL)
                ]) AS label
                WHERE label IS NOT NULL
            ) AS depth_strengths,
            trade_chips AS tradeable_surplus
        ) AS team_strengths,
        STRUCT(
            ARRAY(
                SELECT label
                FROM UNNEST([
                    IF(qb_count < 1, 'QB hole', NULL),
                    IF(rb_count < 3, 'RB depth hole', NULL),
                    IF(wr_count < 4, 'WR depth hole', NULL),
                    IF(te_count < 1, 'TE hole', NULL)
                ]) AS label
                WHERE label IS NOT NULL
            ) AS positional_holes,
            injury_count AS bye_injury_risk,
            weak_starter_slots AS low_ceiling_starters,
            ARRAY(
                SELECT AS STRUCT item.*
                FROM UNNEST(bench_rows) item
                WHERE COALESCE(item.pigskin_rank_position, 999) > 100
                LIMIT 12
            ) AS low_rank_bench_cloggers
        ) AS team_weaknesses,
        STRUCT(
            CAST(NULL AS STRING) AS start_sit_placeholder,
            waiver_rows AS waiver_priorities,
            CAST(NULL AS STRING) AS trade_targets,
            trade_chips AS sell_candidates,
            IF(league_type_id IN ('dynasty', 'keeper'), 'Check age curve and keepable contract context before moving youth.', NULL) AS dynasty_keeper_notes
        ) AS recommended_actions,
        STRUCT(
            ['sleeper_rosters', 'sleeper_roster_players', 'sleeper_lineups', 'sleeper_players_current', 'compat_sleeper_watch_candidates', 'compat_trade_assets_current', 'analytics_pigskin_rankings'] AS sources_used,
            source_freshness_json AS source_freshness,
            model_run_id AS model_run_id,
            ranking_version AS ranking_version,
            missing_data_flags AS missing_data_flags,
            IF(missing_identity_count = 0 AND model_run_id IS NOT NULL, 'medium', 'low') AS confidence
        ) AS evidence_metadata
    )) AS packet_json,
    SUBSTR(CONCAT(
        'Viewer Team Context: ', manager_display_name, ' in league ', league_id, ', week ', CAST(week AS STRING), '\\n',
        'Record: ', COALESCE(CAST(wins AS STRING), '?'), '-', COALESCE(CAST(losses AS STRING), '?'), '-', COALESCE(CAST(ties AS STRING), '0'), '\\n',
        'Roster rows: ', CAST(IFNULL(ARRAY_LENGTH(roster_rows), 0) AS STRING), '. Starters: ', CAST(IFNULL(ARRAY_LENGTH(lineup_rows), 0) AS STRING), '. Waiver candidates: ', CAST(IFNULL(ARRAY_LENGTH(waiver_rows), 0) AS STRING), '.\\n',
        'Weak starter slots: ', CAST(IFNULL(ARRAY_LENGTH(weak_starter_slots), 0) AS STRING), '. Trade chips: ', CAST(IFNULL(ARRAY_LENGTH(trade_chips), 0) AS STRING), '.\\n',
        'Missing identity rows: ', CAST(COALESCE(missing_identity_count, 0) AS STRING), '. Missing canonical identity rows: ', CAST(COALESCE(missing_canonical_identity_count, 0) AS STRING), '.'
    ), 1, {PACKET_TEXT_MAX_CHARS}) AS packet_text
FROM packet_ready
"""


def materialize_viewer_team_context(
    client: bigquery.Client,
    *,
    dataset_id: str = DEFAULT_DATASET,
    league_id: str | None = None,
    roster_id: int | None = None,
    manager_id: str | None = None,
    season: int | None = None,
    week: int | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    dry_run: bool = False,
) -> int:
    _validate_identifier(dataset_id, "dataset_id")
    source_status = inspect_source_status(client, dataset_id)
    snapshot = resolve_snapshot_context(
        client,
        dataset_id,
        league_id=league_id,
        roster_id=roster_id,
        manager_id=manager_id,
        season=season,
        week=week,
    )
    if not snapshot:
        logger.warning("No Sleeper viewer-team snapshot context found. Nothing to materialize.")
        return 0

    resolved_model_run_id = resolve_model_run_id(
        client,
        dataset_id,
        model_run_id=model_run_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    sql = build_viewer_team_context_sql(
        project_id=client.project,
        dataset_id=dataset_id,
        source_status=source_status,
    )
    job_config = bigquery.QueryJobConfig(
        dry_run=dry_run,
        use_query_cache=False,
        query_parameters=[
            bigquery.ScalarQueryParameter("league_id", "STRING", snapshot.league_id),
            bigquery.ScalarQueryParameter("season", "INT64", snapshot.season),
            bigquery.ScalarQueryParameter("week", "INT64", snapshot.week),
            bigquery.ScalarQueryParameter("roster_id", "INT64", roster_id),
            bigquery.ScalarQueryParameter("manager_id", "STRING", _clean_optional(manager_id)),
            bigquery.ScalarQueryParameter("snapshot_timestamp", "TIMESTAMP", snapshot.snapshot_at),
            bigquery.ScalarQueryParameter("scoring_profile_id", "STRING", scoring_profile_id),
            bigquery.ScalarQueryParameter("league_type_id", "STRING", league_type_id),
            bigquery.ScalarQueryParameter("roster_format_id", "STRING", roster_format_id),
            bigquery.ScalarQueryParameter("model_run_id", "STRING", resolved_model_run_id),
            bigquery.ScalarQueryParameter("source_freshness_json", "STRING", source_freshness_json(source_status)),
        ],
    )
    logger.info(
        "Materializing %s for league_id=%s season=%s week=%s roster_id=%s from source tables %s",
        OUTPUT_TABLE,
        snapshot.league_id,
        snapshot.season,
        snapshot.week,
        roster_id or "ALL",
        ", ".join(sorted(name for name, status in source_status.items() if status.exists)),
    )
    job = client.query(sql, job_config=job_config)
    if dry_run:
        logger.info("Dry run bytes processed: %s", job.total_bytes_processed)
        return 0
    job.result()
    row_count = count_output_rows(
        client,
        dataset_id,
        league_id=snapshot.league_id,
        season=snapshot.season,
        week=snapshot.week,
        roster_id=roster_id,
        scoring_profile_id=scoring_profile_id,
    )
    packet_stats = packet_size_stats(
        client,
        dataset_id,
        league_id=snapshot.league_id,
        season=snapshot.season,
        week=snapshot.week,
        scoring_profile_id=scoring_profile_id,
    )
    logger.info(
        "Materialized %s viewer-team packets in %s.%s.%s; max packet text chars=%s",
        row_count,
        client.project,
        dataset_id,
        OUTPUT_TABLE,
        packet_stats.get("max_packet_text_chars"),
    )
    return row_count


def count_output_rows(
    client: bigquery.Client,
    dataset_id: str,
    *,
    league_id: str,
    season: int,
    week: int,
    roster_id: int | None,
    scoring_profile_id: str,
) -> int:
    rows = list(client.query(
        f"""
        SELECT COUNT(*) AS row_count
        FROM `{client.project}.{dataset_id}.{OUTPUT_TABLE}`
        WHERE league_id = @league_id
            AND season = @season
            AND week = @week
            AND scoring_profile_id = @scoring_profile_id
            AND (@roster_id IS NULL OR COALESCE(roster_id, viewer_roster_id) = @roster_id)
        """,
        job_config=bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
            bigquery.ScalarQueryParameter("season", "INT64", season),
            bigquery.ScalarQueryParameter("week", "INT64", week),
            bigquery.ScalarQueryParameter("roster_id", "INT64", roster_id),
            bigquery.ScalarQueryParameter("scoring_profile_id", "STRING", scoring_profile_id),
        ]),
    ).result())
    return int(rows[0].row_count) if rows else 0


def packet_size_stats(
    client: bigquery.Client,
    dataset_id: str,
    *,
    league_id: str,
    season: int,
    week: int,
    scoring_profile_id: str,
) -> dict[str, int | None]:
    rows = list(client.query(
        f"""
        SELECT
            MAX(LENGTH(packet_json)) AS max_packet_json_chars,
            MAX(LENGTH(packet_text)) AS max_packet_text_chars
        FROM `{client.project}.{dataset_id}.{OUTPUT_TABLE}`
        WHERE league_id = @league_id
            AND season = @season
            AND week = @week
            AND scoring_profile_id = @scoring_profile_id
        """,
        job_config=bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
            bigquery.ScalarQueryParameter("season", "INT64", season),
            bigquery.ScalarQueryParameter("week", "INT64", week),
            bigquery.ScalarQueryParameter("scoring_profile_id", "STRING", scoring_profile_id),
        ]),
    ).result())
    if not rows:
        return {"max_packet_json_chars": None, "max_packet_text_chars": None}
    return {
        "max_packet_json_chars": rows[0].max_packet_json_chars,
        "max_packet_text_chars": rows[0].max_packet_text_chars,
    }


def source_freshness_json(source_status: dict[str, SourceTableStatus]) -> str:
    payload: dict[str, dict[str, Any]] = {}
    for table_name, status in source_status.items():
        payload[table_name] = {
            "exists": status.exists,
            "row_count": status.row_count,
            "modified": status.modified.isoformat() if status.modified else None,
        }
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    return json.dumps(payload, sort_keys=True)


def _base_teams_ctes(
    project_id: str,
    dataset_id: str,
    source_status: dict[str, SourceTableStatus],
) -> str:
    if source_status["sleeper_rosters"].exists:
        league_join = _league_join_sql(project_id, dataset_id, source_status["sleeper_leagues"].exists)
        matchup_join = _matchup_join_sql(project_id, dataset_id, source_status)
        return f"""
base_teams AS (
    SELECT
        r.league_id,
        r.season,
        r.week,
        r.snapshot_at,
        r.roster_id,
        r.owner_id AS manager_id,
        COALESCE(r.team_name, r.display_name, r.username, CONCAT('Roster ', CAST(r.roster_id AS STRING))) AS manager_display_name,
        r.wins,
        r.losses,
        r.ties,
        r.points_for,
        r.points_against,
        r.raw_settings_json,
        league_context.league_name,
        league_context.roster_positions_json,
        league_context.scoring_settings_json,
        matchup_context.matchup_id,
        matchup_context.points AS matchup_points
    FROM `{project_id}.{dataset_id}.sleeper_rosters` r
    CROSS JOIN run_context rc
    {league_join}
    {matchup_join}
    WHERE r.league_id = rc.league_id
        AND r.season = rc.season
        AND r.week = rc.week
        AND r.snapshot_at = rc.snapshot_timestamp
        AND (rc.roster_id IS NULL OR r.roster_id = rc.roster_id)
        AND (rc.manager_id IS NULL OR r.owner_id = rc.manager_id)
)"""
    if source_status["sleeper_viewer_team_snapshots"].exists:
        return f"""
base_teams AS (
    SELECT
        s.league_id,
        s.season,
        s.week,
        s.snapshot_at,
        s.viewer_roster_id AS roster_id,
        s.viewer_owner_id AS manager_id,
        COALESCE(s.viewer_team_name, s.viewer_display_name, s.viewer_username, CONCAT('Roster ', CAST(s.viewer_roster_id AS STRING))) AS manager_display_name,
        CAST(NULL AS INT64) AS wins,
        CAST(NULL AS INT64) AS losses,
        CAST(NULL AS INT64) AS ties,
        CAST(NULL AS FLOAT64) AS points_for,
        CAST(NULL AS FLOAT64) AS points_against,
        CAST(NULL AS STRING) AS raw_settings_json,
        CAST(NULL AS STRING) AS league_name,
        CAST(NULL AS STRING) AS roster_positions_json,
        CAST(NULL AS STRING) AS scoring_settings_json,
        s.matchup_id,
        s.points AS matchup_points
    FROM `{project_id}.{dataset_id}.sleeper_viewer_team_snapshots` s
    CROSS JOIN run_context rc
    WHERE s.league_id = rc.league_id
        AND s.season = rc.season
        AND s.week = rc.week
        AND s.snapshot_at = rc.snapshot_timestamp
        AND (rc.roster_id IS NULL OR s.viewer_roster_id = rc.roster_id)
        AND (rc.manager_id IS NULL OR s.viewer_owner_id = rc.manager_id)
)"""
    return """
base_teams AS (
    SELECT
        CAST(NULL AS STRING) AS league_id,
        CAST(NULL AS INT64) AS season,
        CAST(NULL AS INT64) AS week,
        CAST(NULL AS TIMESTAMP) AS snapshot_at,
        CAST(NULL AS INT64) AS roster_id,
        CAST(NULL AS STRING) AS manager_id,
        CAST(NULL AS STRING) AS manager_display_name,
        CAST(NULL AS INT64) AS wins,
        CAST(NULL AS INT64) AS losses,
        CAST(NULL AS INT64) AS ties,
        CAST(NULL AS FLOAT64) AS points_for,
        CAST(NULL AS FLOAT64) AS points_against,
        CAST(NULL AS STRING) AS raw_settings_json,
        CAST(NULL AS STRING) AS league_name,
        CAST(NULL AS STRING) AS roster_positions_json,
        CAST(NULL AS STRING) AS scoring_settings_json,
        CAST(NULL AS INT64) AS matchup_id,
        CAST(NULL AS FLOAT64) AS matchup_points
    WHERE FALSE
)"""


def _league_join_sql(project_id: str, dataset_id: str, exists: bool) -> str:
    if not exists:
        return """
LEFT JOIN (
    SELECT
        CAST(NULL AS STRING) AS league_id,
        CAST(NULL AS INT64) AS season,
        CAST(NULL AS INT64) AS week,
        CAST(NULL AS STRING) AS league_name,
        CAST(NULL AS STRING) AS roster_positions_json,
        CAST(NULL AS STRING) AS scoring_settings_json
    WHERE FALSE
) league_context
    ON FALSE"""
    return f"""
LEFT JOIN (
    SELECT * EXCEPT(rn)
    FROM (
        SELECT
            league_id,
            season,
            week,
            name AS league_name,
            roster_positions_json,
            scoring_settings_json,
            ROW_NUMBER() OVER(PARTITION BY league_id, season, week ORDER BY snapshot_at DESC) AS rn
        FROM `{project_id}.{dataset_id}.sleeper_leagues`
    )
    WHERE rn = 1
) league_context
    ON league_context.league_id = r.league_id
    AND league_context.season = r.season
    AND league_context.week = r.week"""


def _matchup_join_sql(
    project_id: str,
    dataset_id: str,
    source_status: dict[str, SourceTableStatus],
) -> str:
    if not source_status.get("sleeper_lineups", SourceTableStatus(False)).exists:
        return """
LEFT JOIN (
    SELECT
        CAST(NULL AS STRING) AS league_id,
        CAST(NULL AS INT64) AS week,
        CAST(NULL AS INT64) AS roster_id,
        CAST(NULL AS INT64) AS matchup_id,
        CAST(NULL AS FLOAT64) AS points
    WHERE FALSE
) matchup_context
    ON FALSE"""
    return f"""
LEFT JOIN (
    SELECT
        league_id,
        week,
        roster_id,
        ANY_VALUE(matchup_id) AS matchup_id,
        SUM(points) AS points
    FROM `{project_id}.{dataset_id}.sleeper_lineups`
    GROUP BY league_id, week, roster_id
) matchup_context
    ON matchup_context.league_id = r.league_id
    AND matchup_context.week = r.week
    AND matchup_context.roster_id = r.roster_id"""


def _identity_cte(
    project_id: str,
    dataset_id: str,
    source_status: dict[str, SourceTableStatus],
) -> str:
    dim_exists = source_status["dim_players_current"].exists
    bridge_exists = source_status["player_identity_bridge"].exists
    sleeper_exists = source_status["sleeper_players_current"].exists
    if dim_exists and bridge_exists:
        base_identity = f"""
base_identity AS (
    SELECT
        COALESCE(d.player_id_internal, b.player_id_internal) AS player_id_internal,
        COALESCE(d.gsis_id, b.gsis_id) AS gsis_id,
        COALESCE(d.sleeper_player_id, b.sleeper_player_id) AS sleeper_player_id,
        COALESCE(d.display_name, b.display_name) AS display_name,
        COALESCE(d.normalized_name, b.normalized_name) AS normalized_name,
        COALESCE(d.position, b.position) AS position,
        COALESCE(d.current_team, b.current_team) AS current_team,
        COALESCE(d.active_status, b.active_status) AS active_status
    FROM `{project_id}.{dataset_id}.dim_players_current` d
    FULL OUTER JOIN `{project_id}.{dataset_id}.player_identity_bridge` b
        ON d.player_id_internal = b.player_id_internal
    WHERE COALESCE(d.position, b.position) IN ('QB', 'RB', 'WR', 'TE')
)"""
    elif dim_exists:
        base_identity = f"""
base_identity AS (
    SELECT player_id_internal, gsis_id, sleeper_player_id, display_name, normalized_name, position, current_team, active_status
    FROM `{project_id}.{dataset_id}.dim_players_current`
    WHERE position IN ('QB', 'RB', 'WR', 'TE')
)"""
    elif bridge_exists:
        base_identity = f"""
base_identity AS (
    SELECT player_id_internal, gsis_id, sleeper_player_id, display_name, normalized_name, position, current_team, active_status
    FROM `{project_id}.{dataset_id}.player_identity_bridge`
    WHERE position IN ('QB', 'RB', 'WR', 'TE')
)"""
    else:
        base_identity = """
base_identity AS (
    SELECT
        CAST(NULL AS STRING) AS player_id_internal,
        CAST(NULL AS STRING) AS gsis_id,
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS STRING) AS display_name,
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS STRING) AS current_team,
        CAST(NULL AS STRING) AS active_status
    WHERE FALSE
)"""
    if not sleeper_exists:
        return f"""
{base_identity},
identity AS (
    SELECT * FROM base_identity
)"""

    return f"""
{base_identity},
sleeper_identity AS (
    SELECT
        COALESCE(b.player_id_internal, CONCAT('sleeper:', s.sleeper_player_id)) AS player_id_internal,
        COALESCE(b.gsis_id, s.gsis_id) AS gsis_id,
        s.sleeper_player_id AS sleeper_player_id,
        COALESCE(b.display_name, s.player_name) AS display_name,
        COALESCE(b.normalized_name, {_normalized_name_sql("s.player_name")}) AS normalized_name,
        COALESCE(b.position, s.position) AS position,
        COALESCE(b.current_team, s.team) AS current_team,
        COALESCE(b.active_status, s.status, IF(s.active, 'Active', 'Inactive')) AS active_status
    FROM `{project_id}.{dataset_id}.sleeper_players_current` s
    LEFT JOIN base_identity b
        ON (
            s.sleeper_player_id IS NOT NULL
            AND b.sleeper_player_id = s.sleeper_player_id
        )
        OR (
            s.gsis_id IS NOT NULL
            AND b.gsis_id = s.gsis_id
        )
        OR (
            {_normalized_name_sql("s.player_name")} = b.normalized_name
            AND s.position = b.position
            AND (b.current_team IS NULL OR s.team IS NULL OR b.current_team = s.team)
        )
    WHERE s.position IN ('QB', 'RB', 'WR', 'TE')
),
identity_union AS (
    SELECT * FROM base_identity
    UNION ALL
    SELECT * FROM sleeper_identity
),
identity AS (
    SELECT * EXCEPT(rn)
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY COALESCE(sleeper_player_id, gsis_id, player_id_internal, CONCAT(normalized_name, ':', position, ':', COALESCE(current_team, '')))
                ORDER BY IF(STARTS_WITH(player_id_internal, 'sleeper:'), 1, 0), player_id_internal
            ) AS rn
        FROM identity_union
    )
    WHERE rn = 1
)"""


def _rankings_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return """
rankings AS (
    SELECT
        CAST(NULL AS STRING) AS player_id,
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS STRING) AS model_run_id,
        CAST(NULL AS STRING) AS ranking_version,
        CAST(NULL AS INT64) AS pigskin_rank_overall,
        CAST(NULL AS INT64) AS pigskin_rank_position,
        CAST(NULL AS STRING) AS pigskin_tier,
        CAST(NULL AS FLOAT64) AS pigskin_projection,
        CAST(NULL AS FLOAT64) AS pigskin_confidence
    WHERE FALSE
)"""
    return f"""
rankings AS (
    SELECT * EXCEPT(rn)
    FROM (
        SELECT
            player_id,
            sleeper_player_id,
            {_normalized_name_sql("player_name")} AS normalized_name,
            position,
            model_run_id,
            ranking_version,
            rank AS pigskin_rank_overall,
            rank AS pigskin_rank_position,
            tier AS pigskin_tier,
            ranking_score AS pigskin_projection,
            confidence_score AS pigskin_confidence,
            ROW_NUMBER() OVER(
                PARTITION BY COALESCE(player_id, sleeper_player_id, {_normalized_name_sql("player_name")}), position
                ORDER BY generated_at DESC, rank ASC
            ) AS rn
        FROM `{project_id}.{dataset_id}.analytics_pigskin_rankings`
        WHERE COALESCE(is_active, TRUE)
            AND (@model_run_id IS NULL OR model_run_id = @model_run_id)
    )
    WHERE rn = 1
)"""


def _trade_assets_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return """
trade_assets AS (
    SELECT
        CAST(NULL AS STRING) AS player_id_internal,
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS FLOAT64) AS market_value
    WHERE FALSE
)"""
    return f"""
trade_assets AS (
    SELECT
        player_id_internal,
        sleeper_player_id,
        normalized_name,
        position,
        risk_adjusted_trade_value AS market_value
    FROM `{project_id}.{dataset_id}.compat_trade_assets_current`
    WHERE scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
)"""


def _player_profiles_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return """
player_profiles AS (
    SELECT
        CAST(NULL AS STRING) AS player_id_internal,
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS STRING) AS evidence_summary,
        CAST(NULL AS FLOAT64) AS breakout_score,
        CAST(NULL AS FLOAT64) AS risk_score
    WHERE FALSE
)"""
    return f"""
player_profiles AS (
    SELECT
        player_id_internal,
        sleeper_player_id,
        normalized_name,
        position,
        COALESCE(pigskin_summary, role_summary_json) AS evidence_summary,
        pigskin_projection AS breakout_score,
        CAST(JSON_VALUE(role_summary_json, '$.role_fragility_score') AS FLOAT64) AS risk_score
    FROM `{project_id}.{dataset_id}.compat_player_profiles_current`
    WHERE scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
)"""


def _trade_history_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return """
trade_history AS (
    SELECT
        CAST(NULL AS STRING) AS player_id_internal,
        CAST(NULL AS STRING) AS source_player_key,
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS FLOAT64) AS recent_points,
        CAST(NULL AS STRING) AS role_trend
    WHERE FALSE
)"""
    return f"""
trade_history AS (
    SELECT
        player_id_internal,
        source_player_key,
        normalized_name,
        position,
        AVG(total_fantasy_points) AS recent_points,
        CASE
            WHEN AVG(total_fantasy_points) >= 16 THEN 'ceiling'
            WHEN AVG(total_fantasy_points) >= 10 THEN 'usable'
            ELSE 'thin'
        END AS role_trend
    FROM `{project_id}.{dataset_id}.compat_trade_player_history`
    WHERE scoring_profile_id = @scoring_profile_id
        AND recency_order <= 5
    GROUP BY player_id_internal, source_player_key, normalized_name, position
)"""


def _llm_packets_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return """
llm_packets AS (
    SELECT
        CAST(NULL AS STRING) AS player_id_internal,
        CAST(NULL AS STRING) AS source_player_key,
        CAST(NULL AS STRING) AS packet_text
    WHERE FALSE
)"""
    return f"""
llm_packets AS (
    SELECT
        player_id_internal,
        source_player_key,
        packet_text
    FROM `{project_id}.{dataset_id}.llm_player_context_packet`
    WHERE scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
)"""


def _roster_players_cte(
    project_id: str,
    dataset_id: str,
    source_status: dict[str, SourceTableStatus],
) -> str:
    if not source_status["sleeper_roster_players"].exists:
        return """
roster_players AS (
    SELECT
        CAST(NULL AS STRING) AS league_id,
        CAST(NULL AS INT64) AS season,
        CAST(NULL AS INT64) AS week,
        CAST(NULL AS INT64) AS roster_id,
        CAST(NULL AS STRING) AS owner_id,
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS STRING) AS gsis_id,
        CAST(NULL AS STRING) AS player_name,
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS STRING) AS team,
        CAST(NULL AS STRING) AS status,
        CAST(NULL AS STRING) AS injury_status,
        CAST(NULL AS BOOL) AS is_starter,
        CAST(NULL AS BOOL) AS is_taxi,
        CAST(NULL AS BOOL) AS is_reserve,
        CAST(NULL AS FLOAT64) AS week_points,
        CAST(NULL AS STRING) AS source_player_key
    WHERE FALSE
)"""
    lineup_points = "lp.points" if source_status["sleeper_lineups"].exists else "CAST(NULL AS FLOAT64)"
    lineup_join = f"""
LEFT JOIN `{project_id}.{dataset_id}.sleeper_lineups` lp
    ON lp.league_id = rp.league_id
    AND lp.season = rp.season
    AND lp.week = rp.week
    AND lp.roster_id = rp.roster_id
    AND lp.sleeper_player_id = rp.sleeper_player_id
    AND lp.snapshot_at = rp.snapshot_at
""" if source_status["sleeper_lineups"].exists else ""
    return f"""
roster_players AS (
    SELECT
        rp.league_id,
        rp.season,
        rp.week,
        rp.roster_id,
        rp.owner_id,
        rp.sleeper_player_id,
        rp.gsis_id,
        rp.player_name,
        {_normalized_name_sql("rp.player_name")} AS normalized_name,
        rp.position,
        rp.team,
        rp.status,
        rp.injury_status,
        rp.is_starter,
        rp.is_taxi,
        rp.is_reserve,
        {lineup_points} AS week_points,
        COALESCE(rp.gsis_id, rp.sleeper_player_id, CONCAT('name:', {_normalized_name_sql("rp.player_name")}, ':', COALESCE(rp.position, 'UNK'))) AS source_player_key
    FROM `{project_id}.{dataset_id}.sleeper_roster_players` rp
    JOIN base_teams bt
        ON bt.league_id = rp.league_id
        AND bt.season = rp.season
        AND bt.week = rp.week
        AND bt.roster_id = rp.roster_id
        AND bt.snapshot_at = rp.snapshot_at
    {lineup_join}
    WHERE rp.position IN ('QB', 'RB', 'WR', 'TE')
)"""


def _waiver_candidates_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return """
waiver_candidates AS (
    SELECT
        CAST(NULL AS STRING) AS player_id_internal,
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS STRING) AS display_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS STRING) AS team,
        CAST(NULL AS INT64) AS season,
        CAST(NULL AS INT64) AS week,
        CAST(NULL AS STRING) AS league_id,
        CAST(NULL AS FLOAT64) AS rostered_rate,
        CAST(NULL AS BOOL) AS waiver_candidate_flag,
        CAST(NULL AS FLOAT64) AS streamer_score,
        CAST(NULL AS FLOAT64) AS breakout_score,
        CAST(NULL AS INT64) AS pigskin_rank_position,
        CAST(NULL AS STRING) AS pigskin_tier,
        CAST(NULL AS STRING) AS candidate_reason,
        CAST(NULL AS STRING) AS missing_data_flags
    WHERE FALSE
)"""
    return f"""
waiver_candidates AS (
    SELECT
        player_id_internal,
        sleeper_player_id,
        display_name,
        position,
        team,
        season,
        week,
        league_id,
        rostered_rate,
        waiver_candidate_flag,
        streamer_score,
        breakout_score,
        pigskin_rank_position,
        pigskin_tier,
        candidate_reason,
        missing_data_flags
    FROM `{project_id}.{dataset_id}.compat_sleeper_watch_candidates`
    WHERE scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
        AND COALESCE(waiver_candidate_flag, TRUE)
)"""


def _normalized_name_sql(expr: str) -> str:
    return (
        "REGEXP_REPLACE("
        f"REGEXP_REPLACE(LOWER(COALESCE({expr}, '')), r'\\s+(jr|sr|ii|iii|iv|v)\\.?$', ''), "
        "r'[^a-z0-9]+', '')"
    )


def _validate_identifier(value: str, label: str) -> None:
    if not IDENTIFIER_RE.match(value):
        raise ValueError(f"Unsafe BigQuery {label}: {value}")


def _clean_optional(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize viewer-team context packets.")
    parser.add_argument("--project", default=get_bigquery_project())
    parser.add_argument("--dataset", default=get_bigquery_dataset())
    parser.add_argument("--league-id")
    parser.add_argument("--roster-id", type=int)
    parser.add_argument("--manager-id")
    parser.add_argument("--season", type=int)
    parser.add_argument("--week", type=int)
    parser.add_argument("--scoring-profile-id", default=DEFAULT_SCORING_PROFILE)
    parser.add_argument("--league-type-id", default=DEFAULT_LEAGUE_TYPE)
    parser.add_argument("--roster-format-id", default=DEFAULT_ROSTER_FORMAT)
    parser.add_argument("--model-run-id")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log-level", default=os.environ.get("LOG_LEVEL", "INFO"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    client = bigquery.Client(project=args.project)
    row_count = materialize_viewer_team_context(
        client,
        dataset_id=args.dataset,
        league_id=args.league_id,
        roster_id=args.roster_id,
        manager_id=args.manager_id,
        season=args.season,
        week=args.week,
        scoring_profile_id=args.scoring_profile_id,
        league_type_id=args.league_type_id,
        roster_format_id=args.roster_format_id,
        model_run_id=args.model_run_id,
        dry_run=args.dry_run,
    )
    print(f"{OUTPUT_TABLE} rows materialized: {row_count}")


if __name__ == "__main__":
    main()
