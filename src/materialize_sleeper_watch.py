"""Materialize the Sleeper Watch compatibility mart."""

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
OUTPUT_TABLE = "mart_sleeper_watch_candidates"
DEFAULT_SCORING_PROFILE = "ppr"
DEFAULT_LEAGUE_TYPE = "redraft"
DEFAULT_ROSTER_FORMAT = "one_qb"
SOURCE_TABLES = (
    "analytics_player_weekly_truth",
    "analytics_player_fantasy_points_by_profile",
    "analytics_pigskin_rankings",
    "analytics_fraud_watch",
    "analytics_game_environment",
    "dim_players_current",
    "player_identity_bridge",
    "sleeper_rosters",
    "sleeper_roster_players",
    "sleeper_available_players",
    "sleeper_players_current",
    "realtime_player_news",
    "scoring_profiles",
)
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
OUTPUT_COLUMNS_SQL = """
    player_id_internal,
    source_player_key,
    sleeper_player_id,
    display_name,
    normalized_name,
    position,
    fantasy_positions,
    team,
    opponent,
    age,
    active_status,
    season,
    week,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    league_id,
    model_run_id,
    ranking_version,
    rostered_rate,
    available_in_league_flag,
    rostered_in_league_flag,
    waiver_candidate_flag,
    starter_candidate_flag,
    sleeper_trending_add_count,
    sleeper_trending_drop_count,
    market_or_roster_context_json,
    fantasy_points_last_1,
    fantasy_points_last_3,
    fantasy_points_last_5,
    fantasy_points_per_game,
    snap_share_last_3,
    target_share_last_3,
    rush_share_last_3,
    targets_last_3,
    carries_last_3,
    receptions_last_3,
    air_yards_last_3,
    red_zone_opportunities_last_3,
    high_value_touches_last_3,
    usage_trend_score,
    role_growth_score,
    yards_per_target,
    yards_per_carry,
    yards_per_reception,
    catch_rate,
    td_dependency_score,
    expected_vs_actual_signal,
    fraud_risk_score,
    breakout_score,
    game_id,
    game_environment_json,
    opponent_fantasy_points_allowed_proxy,
    matchup_score,
    streamer_score,
    schedule_context_json,
    pigskin_rank_overall,
    pigskin_rank_position,
    pigskin_tier,
    pigskin_projection,
    pigskin_confidence,
    rank_vs_market_gap,
    pigskin_summary,
    candidate_reason,
    evidence_json,
    counterargument,
    snark_hook,
    source_freshness_json,
    missing_data_flags,
    created_at,
    updated_at
"""


@dataclass(frozen=True)
class SourceTableStatus:
    exists: bool
    row_count: int | None = None
    modified: datetime | None = None


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


def resolve_target_week(
    client: bigquery.Client,
    dataset_id: str,
    *,
    season: int | None = None,
    week: int | None = None,
) -> tuple[int | None, int | None]:
    if season is not None and week is not None:
        return int(season), int(week)
    if not table_status(client, dataset_id, "analytics_player_weekly_truth").exists:
        return season, week
    sql = f"""
    SELECT season, week
    FROM `{client.project}.{dataset_id}.analytics_player_weekly_truth`
    WHERE (@season IS NULL OR season = @season)
        AND (@week IS NULL OR week = @week)
    ORDER BY season DESC, week DESC
    LIMIT 1
    """
    rows = list(client.query(
        sql,
        job_config=bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("season", "INT64", season),
            bigquery.ScalarQueryParameter("week", "INT64", week),
        ]),
    ).result())
    if not rows:
        return season, week
    return int(rows[0].season), int(rows[0].week)


def build_sleeper_watch_sql(
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
WHERE season = @season
    AND week = @week
    AND scoring_profile_id = @scoring_profile_id
    AND league_type_id = @league_type_id
    AND roster_format_id = @roster_format_id
    AND (
        (@league_id IS NULL AND league_id IS NULL)
        OR league_id = @league_id
    );

INSERT INTO `{project_id}.{dataset_id}.{OUTPUT_TABLE}` (
{OUTPUT_COLUMNS_SQL}
)
WITH
{_truth_cte(project_id, dataset_id, source_status["analytics_player_weekly_truth"])},
target_context AS (
    SELECT
        COALESCE(@season, season) AS season,
        COALESCE(@week, week) AS week
    FROM truth_source
    WHERE (@season IS NULL OR season = @season)
        AND (@week IS NULL OR week = @week)
    ORDER BY season DESC, week DESC
    LIMIT 1
),
run_context AS (
    SELECT
        @scoring_profile_id AS scoring_profile_id,
        @league_type_id AS league_type_id,
        @roster_format_id AS roster_format_id,
        @league_id AS league_id,
        @model_run_id AS requested_model_run_id,
        @source_freshness_json AS source_freshness_json,
        CURRENT_TIMESTAMP() AS refreshed_at
),
truth_recent AS (
    SELECT
        t.*,
        ROW_NUMBER() OVER(
            PARTITION BY t.source_player_key, t.position
            ORDER BY t.season DESC, t.week DESC
        ) AS recency_order
    FROM truth_source t
    JOIN target_context tc
        ON t.season = tc.season
        AND t.week <= tc.week
    WHERE t.position IN ('QB', 'RB', 'WR', 'TE')
    QUALIFY recency_order <= 5
),
latest_truth AS (
    SELECT *
    FROM truth_recent
    WHERE recency_order = 1
),
{_profile_points_cte(project_id, dataset_id, source_status["analytics_player_fantasy_points_by_profile"])},
recent_usage AS (
    SELECT
        tr.source_player_key,
        tr.normalized_name,
        tr.position,
        AVG(IF(tr.recency_order <= 1, COALESCE(fp.total_fantasy_points, tr.fantasy_points_ppr), NULL)) AS fantasy_points_last_1,
        AVG(IF(tr.recency_order <= 3, COALESCE(fp.total_fantasy_points, tr.fantasy_points_ppr), NULL)) AS fantasy_points_last_3,
        AVG(IF(tr.recency_order <= 5, COALESCE(fp.total_fantasy_points, tr.fantasy_points_ppr), NULL)) AS fantasy_points_last_5,
        AVG(COALESCE(fp.total_fantasy_points, tr.fantasy_points_ppr)) AS fantasy_points_per_game,
        AVG(IF(tr.recency_order <= 3, tr.offense_pct, NULL)) AS snap_share_last_3,
        AVG(IF(tr.recency_order <= 3, tr.target_share, NULL)) AS target_share_last_3,
        AVG(IF(tr.recency_order <= 3, tr.carry_share, NULL)) AS rush_share_last_3,
        SUM(IF(tr.recency_order <= 3, tr.targets, 0)) AS targets_last_3,
        SUM(IF(tr.recency_order <= 3, tr.carries, 0)) AS carries_last_3,
        SUM(IF(tr.recency_order <= 3, tr.receptions, 0)) AS receptions_last_3,
        SUM(IF(tr.recency_order <= 3, tr.receiving_air_yards, 0)) AS air_yards_last_3,
        SUM(IF(tr.recency_order <= 3, tr.red_zone_touches, 0)) AS red_zone_opportunities_last_3,
        SUM(IF(tr.recency_order <= 3, COALESCE(tr.receptions, 0) + COALESCE(tr.red_zone_touches, 0), 0)) AS high_value_touches_last_3,
        AVG(IF(tr.recency_order <= 3, tr.wopr, NULL)) AS wopr_last_3,
        AVG(IF(tr.recency_order <= 3, tr.total_epa, NULL)) AS total_epa_last_3,
        MAX(IF(tr.recency_order = 1, tr.rolling_3_week_opportunities, NULL)) AS rolling_3_week_opportunities,
        MAX(IF(tr.recency_order = 1, tr.ppr_delta, NULL)) AS ppr_delta,
        MAX(IF(tr.recency_order = 1, tr.points_over_role_score, NULL)) AS expected_vs_actual_signal,
        MAX(IF(tr.recency_order = 1, tr.touchdown_dependency_rate, NULL)) AS touchdown_dependency_rate,
        MAX(IF(tr.recency_order = 1, tr.role_quality_score, NULL)) AS role_quality_score,
        MAX(IF(tr.recency_order = 1, tr.role_fragility_score, NULL)) AS role_fragility_score
    FROM truth_recent tr
    CROSS JOIN run_context rc
    LEFT JOIN profile_points fp
        ON fp.source_player_key = tr.source_player_key
        AND fp.season = tr.season
        AND fp.week = tr.week
        AND fp.scoring_profile_id = rc.scoring_profile_id
    GROUP BY tr.source_player_key, tr.normalized_name, tr.position
),
{_identity_cte(project_id, dataset_id, source_status)},
{_sleeper_current_cte(project_id, dataset_id, source_status["sleeper_players_current"])},
{_rankings_cte(project_id, dataset_id, source_status["analytics_pigskin_rankings"])},
{_fraud_cte(project_id, dataset_id, source_status["analytics_fraud_watch"])},
{_environment_cte(project_id, dataset_id, source_status["analytics_game_environment"])},
matchup_allowed AS (
    SELECT
        t.opponent AS opponent,
        t.position,
        AVG(t.fantasy_points_ppr) AS opponent_fantasy_points_allowed_proxy,
        PERCENT_RANK() OVER(
            PARTITION BY t.position
            ORDER BY AVG(t.fantasy_points_ppr)
        ) * 100 AS matchup_score
    FROM truth_source t
    JOIN target_context tc
        ON t.season = tc.season
        AND t.week <= tc.week
    WHERE t.position IN ('QB', 'RB', 'WR', 'TE')
        AND t.opponent IS NOT NULL
    GROUP BY t.opponent, t.position
),
{_roster_context_ctes(project_id, dataset_id, source_status)},
{_trending_cte(project_id, dataset_id, source_status["realtime_player_news"])},
base_candidates AS (
    SELECT
        COALESCE(id.player_id_internal, CONCAT('source:', lt.source_player_key)) AS player_id_internal,
        COALESCE(id.source_player_key, lt.source_player_key) AS source_player_key,
        COALESCE(id.sleeper_player_id, sc.sleeper_player_id) AS sleeper_player_id,
        COALESCE(id.display_name, sc.player_name, lt.display_name) AS display_name,
        COALESCE(id.normalized_name, lt.normalized_name) AS normalized_name,
        COALESCE(id.position, sc.position, lt.position) AS position,
        COALESCE(id.fantasy_positions, sc.fantasy_positions_json, lt.position) AS fantasy_positions,
        COALESCE(id.current_team, sc.team, lt.current_team, lt.team) AS team,
        lt.opponent,
        id.age AS age,
        COALESCE(id.active_status, sc.status, lt.roster_status) AS active_status,
        lt.season,
        lt.week,
        rc.scoring_profile_id,
        rc.league_type_id,
        rc.roster_format_id,
        rc.league_id,
        COALESCE(r.model_run_id, rc.requested_model_run_id) AS model_run_id,
        r.ranking_version,
        gr.rostered_rate,
        IF(rc.league_id IS NULL, NULL, COALESCE(la.available_in_league_flag, FALSE)) AS available_in_league_flag,
        IF(rc.league_id IS NULL, NULL, COALESCE(lr.rostered_in_league_flag, FALSE)) AS rostered_in_league_flag,
        IF(
            rc.league_id IS NULL,
            COALESCE(gr.rostered_rate <= 0.45, TRUE),
            COALESCE(la.available_in_league_flag, FALSE)
        ) AS waiver_candidate_flag,
        COALESCE(tn.sleeper_trending_add_count, 0) AS sleeper_trending_add_count,
        COALESCE(tn.sleeper_trending_drop_count, 0) AS sleeper_trending_drop_count,
        ru.fantasy_points_last_1,
        ru.fantasy_points_last_3,
        ru.fantasy_points_last_5,
        ru.fantasy_points_per_game,
        ru.snap_share_last_3,
        ru.target_share_last_3,
        ru.rush_share_last_3,
        ru.targets_last_3,
        ru.carries_last_3,
        ru.receptions_last_3,
        ru.air_yards_last_3,
        ru.red_zone_opportunities_last_3,
        ru.high_value_touches_last_3,
        LEAST(100, GREATEST(0,
            45
            + COALESCE(ru.ppr_delta, 0) * 2
            + COALESCE(ru.rolling_3_week_opportunities, 0) * 1.8
            + COALESCE(ru.wopr_last_3, 0) * 18
        )) AS usage_trend_score,
        LEAST(100, GREATEST(0,
            40
            + COALESCE(ru.role_quality_score, 0) * 0.8
            - COALESCE(ru.role_fragility_score, 0) * 0.35
            + COALESCE(ru.wopr_last_3, 0) * 20
        )) AS role_growth_score,
        SAFE_DIVIDE(lt.receiving_yards, NULLIF(lt.targets, 0)) AS yards_per_target,
        SAFE_DIVIDE(lt.rushing_yards, NULLIF(lt.carries, 0)) AS yards_per_carry,
        SAFE_DIVIDE(lt.receiving_yards, NULLIF(lt.receptions, 0)) AS yards_per_reception,
        SAFE_DIVIDE(lt.receptions, NULLIF(lt.targets, 0)) AS catch_rate,
        COALESCE(ru.touchdown_dependency_rate, lt.touchdown_dependency_rate) * 100 AS td_dependency_score,
        COALESCE(ru.expected_vs_actual_signal, lt.points_over_role_score) AS expected_vs_actual_signal,
        COALESCE(f.fraud_risk_score, lt.role_fragility_score) AS fraud_risk_score,
        env.game_id,
        env.game_environment_json,
        ma.opponent_fantasy_points_allowed_proxy,
        ma.matchup_score,
        r.pigskin_rank_overall,
        r.pigskin_rank_position,
        r.pigskin_tier,
        r.pigskin_projection,
        r.pigskin_confidence,
        r.pigskin_summary,
        rc.source_freshness_json,
        rc.refreshed_at,
        {source_flags["analytics_player_weekly_truth"]} AS analytics_player_weekly_truth_available,
        {source_flags["analytics_player_fantasy_points_by_profile"]} AS analytics_player_fantasy_points_by_profile_available,
        {source_flags["analytics_pigskin_rankings"]} AS analytics_pigskin_rankings_available,
        {source_flags["analytics_fraud_watch"]} AS analytics_fraud_watch_available,
        {source_flags["analytics_game_environment"]} AS analytics_game_environment_available,
        {source_flags["sleeper_rosters"]} AS sleeper_rosters_available,
        {source_flags["sleeper_roster_players"]} AS sleeper_roster_players_available,
        {source_flags["sleeper_available_players"]} AS sleeper_available_players_available,
        {source_flags["realtime_player_news"]} AS realtime_player_news_available,
        IF(id.player_id_internal IS NULL, 'source_key_fallback', 'canonical_identity') AS identity_match_method
    FROM latest_truth lt
    CROSS JOIN run_context rc
    LEFT JOIN recent_usage ru
        ON ru.source_player_key = lt.source_player_key
        AND ru.position = lt.position
    LEFT JOIN identity id
        ON (
            id.gsis_id IS NOT NULL
            AND id.gsis_id = lt.nflverse_player_id
        )
        OR (
            id.normalized_name = lt.normalized_name
            AND id.position = lt.position
        )
    LEFT JOIN sleeper_current sc
        ON (
            sc.gsis_id IS NOT NULL
            AND sc.gsis_id = lt.nflverse_player_id
        )
        OR (
            sc.normalized_name = lt.normalized_name
            AND sc.position = lt.position
        )
    LEFT JOIN rankings r
        ON (
            r.player_id IS NOT NULL
            AND r.player_id = lt.nflverse_player_id
            AND r.position = lt.position
        )
        OR (
            r.sleeper_player_id IS NOT NULL
            AND r.sleeper_player_id = COALESCE(id.sleeper_player_id, sc.sleeper_player_id)
            AND r.position = lt.position
        )
        OR (
            r.normalized_name = lt.normalized_name
            AND r.position = lt.position
        )
    LEFT JOIN fraud f
        ON f.normalized_name = lt.normalized_name
        AND f.position = lt.position
    LEFT JOIN game_environment env
        ON env.season = lt.season
        AND env.week = lt.week
        AND (
            (env.home_team = COALESCE(id.current_team, sc.team, lt.current_team, lt.team) AND env.away_team = lt.opponent)
            OR (env.away_team = COALESCE(id.current_team, sc.team, lt.current_team, lt.team) AND env.home_team = lt.opponent)
        )
    LEFT JOIN matchup_allowed ma
        ON ma.opponent = lt.opponent
        AND ma.position = lt.position
    LEFT JOIN global_roster_rates gr
        ON gr.sleeper_player_id = COALESCE(id.sleeper_player_id, sc.sleeper_player_id)
    LEFT JOIN league_rostered lr
        ON lr.sleeper_player_id = COALESCE(id.sleeper_player_id, sc.sleeper_player_id)
    LEFT JOIN league_available la
        ON la.sleeper_player_id = COALESCE(id.sleeper_player_id, sc.sleeper_player_id)
    LEFT JOIN trending tn
        ON tn.sleeper_player_id = COALESCE(id.sleeper_player_id, sc.sleeper_player_id)
        OR tn.gsis_id = lt.nflverse_player_id
),
scored AS (
    SELECT
        bc.*,
        SAFE_DIVIDE(
            (1 - COALESCE(bc.rostered_rate, 0.35)) * 100
            - COALESCE(CAST(bc.pigskin_rank_position AS FLOAT64), 160) * 0.15,
            1
        ) AS rank_vs_market_gap,
        LEAST(100, GREATEST(0,
            COALESCE(bc.role_growth_score, 40) * 0.24
            + COALESCE(bc.usage_trend_score, 40) * 0.18
            + COALESCE(bc.matchup_score, 50) * 0.18
            + COALESCE(100 - bc.rostered_rate * 100, 45) * 0.16
            + COALESCE(CAST(bc.sleeper_trending_add_count AS FLOAT64), 0) * 0.06
            - COALESCE(bc.fraud_risk_score, 30) * 0.10
        )) AS streamer_score,
        LEAST(100, GREATEST(0,
            COALESCE(bc.role_growth_score, 40) * 0.32
            + COALESCE(bc.usage_trend_score, 40) * 0.22
            + COALESCE(bc.target_share_last_3, 0) * 80
            + COALESCE(bc.rush_share_last_3, 0) * 55
            - COALESCE(bc.fraud_risk_score, 30) * 0.12
        )) AS breakout_score
    FROM base_candidates bc
)
SELECT
    player_id_internal,
    source_player_key,
    sleeper_player_id,
    display_name,
    normalized_name,
    position,
    fantasy_positions,
    team,
    opponent,
    age,
    active_status,
    season,
    week,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    league_id,
    model_run_id,
    ranking_version,
    rostered_rate,
    available_in_league_flag,
    rostered_in_league_flag,
    waiver_candidate_flag,
    streamer_score >= 58 AS starter_candidate_flag,
    sleeper_trending_add_count,
    sleeper_trending_drop_count,
    TO_JSON_STRING(STRUCT(
        rostered_rate AS rostered_rate,
        available_in_league_flag AS available_in_league_flag,
        rostered_in_league_flag AS rostered_in_league_flag,
        waiver_candidate_flag AS waiver_candidate_flag,
        sleeper_trending_add_count AS sleeper_trending_add_count,
        sleeper_trending_drop_count AS sleeper_trending_drop_count
    )) AS market_or_roster_context_json,
    fantasy_points_last_1,
    fantasy_points_last_3,
    fantasy_points_last_5,
    fantasy_points_per_game,
    snap_share_last_3,
    target_share_last_3,
    rush_share_last_3,
    targets_last_3,
    carries_last_3,
    receptions_last_3,
    air_yards_last_3,
    red_zone_opportunities_last_3,
    high_value_touches_last_3,
    usage_trend_score,
    role_growth_score,
    yards_per_target,
    yards_per_carry,
    yards_per_reception,
    catch_rate,
    td_dependency_score,
    expected_vs_actual_signal,
    fraud_risk_score,
    breakout_score,
    game_id,
    game_environment_json,
    opponent_fantasy_points_allowed_proxy,
    matchup_score,
    streamer_score,
    TO_JSON_STRING(STRUCT(
        season AS season,
        week AS week,
        opponent AS opponent,
        matchup_score AS matchup_score,
        game_id AS game_id
    )) AS schedule_context_json,
    pigskin_rank_overall,
    pigskin_rank_position,
    pigskin_tier,
    pigskin_projection,
    pigskin_confidence,
    rank_vs_market_gap,
    pigskin_summary,
    CONCAT(
        display_name,
        ' is a Sleeper Watch candidate because recent usage scored ',
        CAST(ROUND(COALESCE(usage_trend_score, 0), 1) AS STRING),
        ', role growth scored ',
        CAST(ROUND(COALESCE(role_growth_score, 0), 1) AS STRING),
        ', and matchup scored ',
        CAST(ROUND(COALESCE(matchup_score, 0), 1) AS STRING),
        '.'
    ) AS candidate_reason,
    TO_JSON_STRING(STRUCT(
        fantasy_points_last_3 AS fantasy_points_last_3,
        target_share_last_3 AS target_share_last_3,
        rush_share_last_3 AS rush_share_last_3,
        targets_last_3 AS targets_last_3,
        carries_last_3 AS carries_last_3,
        CAST(NULL AS FLOAT64) AS wopr,
        fraud_risk_score AS fraud_risk_score,
        breakout_score AS breakout_score,
        streamer_score AS streamer_score
    )) AS evidence_json,
    CASE
        WHEN fraud_risk_score >= 65 THEN 'The role may be more fragile than the box score says.'
        WHEN rostered_rate >= 0.75 THEN 'This may not be available in normal leagues.'
        WHEN fantasy_points_last_3 IS NULL THEN 'Recent fantasy evidence is incomplete.'
        ELSE 'The main risk is that the market notices before waivers run.'
    END AS counterargument,
    CASE
        WHEN fraud_risk_score >= 70 THEN 'Nice box score. Shame about the evidence.'
        WHEN streamer_score >= 70 THEN 'The waiver wire finally coughed up something useful.'
        WHEN breakout_score >= 70 THEN 'The usage is whispering before the box score starts yelling.'
        ELSE 'Not a league winner yet, but not waiver dust either.'
    END AS snark_hook,
    source_freshness_json,
    TO_JSON_STRING(ARRAY(
        SELECT DISTINCT flag
        FROM UNNEST(ARRAY_CONCAT(
            IF(player_id_internal IS NULL OR STARTS_WITH(player_id_internal, 'source:'), ['missing_canonical_player_id_internal'], []),
            IF(source_player_key IS NULL, ['missing_source_player_key'], []),
            IF(sleeper_player_id IS NULL, ['missing_sleeper_player_id'], []),
            IF(age IS NULL, ['missing_age'], []),
            IF(active_status IS NULL, ['missing_active_status'], []),
            IF(rostered_rate IS NULL, ['missing_rostered_rate'], []),
            IF(league_id IS NOT NULL AND available_in_league_flag IS NULL, ['missing_league_availability'], []),
            IF(model_run_id IS NULL, ['missing_model_run_id'], []),
            IF(ranking_version IS NULL, ['missing_pigskin_ranking_context'], []),
            IF(game_environment_json IS NULL, ['missing_game_environment'], []),
            IF(fraud_risk_score IS NULL, ['missing_fraud_context'], []),
            IF(NOT analytics_player_weekly_truth_available, ['missing_truth_source'], []),
            IF(NOT analytics_player_fantasy_points_by_profile_available, ['missing_scoring_profile_points_source'], []),
            IF(NOT analytics_pigskin_rankings_available, ['missing_rankings_source'], []),
            IF(NOT analytics_game_environment_available, ['missing_game_environment_source'], []),
            IF(NOT sleeper_rosters_available, ['missing_sleeper_rosters_source'], []),
            IF(NOT sleeper_roster_players_available, ['missing_sleeper_roster_players_source'], []),
            IF(NOT sleeper_available_players_available AND league_id IS NOT NULL, ['missing_sleeper_available_players_source'], []),
            IF(NOT realtime_player_news_available, ['missing_sleeper_trending_source'], []),
            IF(identity_match_method = 'source_key_fallback', ['temporary_source_key_identity'], [])
        )) AS flag
        WHERE flag IS NOT NULL
        ORDER BY flag
    )) AS missing_data_flags,
    refreshed_at AS created_at,
    refreshed_at AS updated_at
FROM scored
WHERE streamer_score IS NOT NULL
QUALIFY ROW_NUMBER() OVER(
    PARTITION BY player_id_internal, COALESCE(league_id, 'GLOBAL'), scoring_profile_id, season, week
    ORDER BY streamer_score DESC, breakout_score DESC, display_name ASC
) = 1
"""


def materialize_sleeper_watch(
    client: bigquery.Client,
    *,
    dataset_id: str = DEFAULT_DATASET,
    season: int | None = None,
    week: int | None = None,
    league_id: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    dry_run: bool = False,
) -> int:
    _validate_identifier(dataset_id, "dataset_id")
    resolved_season, resolved_week = resolve_target_week(
        client,
        dataset_id,
        season=season,
        week=week,
    )
    resolved_model_run_id = resolve_model_run_id(
        client,
        dataset_id,
        model_run_id=model_run_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    source_status = inspect_source_status(client, dataset_id)
    if not source_status["analytics_player_weekly_truth"].exists:
        logger.warning("analytics_player_weekly_truth is missing. Materializing an empty Sleeper Watch mart.")
    if league_id and not source_status["sleeper_available_players"].exists:
        logger.warning("League-specific availability requested, but sleeper_available_players is missing.")
    if not league_id:
        logger.info("No league_id provided. Materializing global Sleeper Watch candidates.")

    sql = build_sleeper_watch_sql(
        project_id=client.project,
        dataset_id=dataset_id,
        source_status=source_status,
    )
    job_config = bigquery.QueryJobConfig(
        dry_run=dry_run,
        use_query_cache=False,
        query_parameters=[
            bigquery.ScalarQueryParameter("season", "INT64", resolved_season),
            bigquery.ScalarQueryParameter("week", "INT64", resolved_week),
            bigquery.ScalarQueryParameter("league_id", "STRING", _clean_optional(league_id)),
            bigquery.ScalarQueryParameter("scoring_profile_id", "STRING", scoring_profile_id),
            bigquery.ScalarQueryParameter("league_type_id", "STRING", league_type_id),
            bigquery.ScalarQueryParameter("roster_format_id", "STRING", roster_format_id),
            bigquery.ScalarQueryParameter("model_run_id", "STRING", resolved_model_run_id),
            bigquery.ScalarQueryParameter("source_freshness_json", "STRING", source_freshness_json(source_status)),
        ],
    )
    logger.info(
        "Materializing %s for season=%s week=%s league_id=%s from source tables %s",
        OUTPUT_TABLE,
        resolved_season,
        resolved_week,
        league_id or "GLOBAL",
        ", ".join(sorted(name for name, status in source_status.items() if status.exists)),
    )
    job = client.query(sql, job_config=job_config)
    if dry_run:
        logger.info("Dry run bytes processed: %s", job.total_bytes_processed)
        return 0
    job.result()
    row_count = _count_output_rows(client, dataset_id)
    flagged_count = _count_flagged_rows(client, dataset_id)
    logger.info(
        "Materialized %s rows in %s.%s.%s; rows with missing-data flags=%s",
        row_count,
        client.project,
        dataset_id,
        OUTPUT_TABLE,
        flagged_count,
    )
    return row_count


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


def _truth_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return _empty_truth_cte()
    return f"""
truth_source AS (
    SELECT
        COALESCE(
            CAST(player_id AS STRING),
            CONCAT('name:', {_normalized_name_sql("player_display_name")}, ':', COALESCE(CAST(position AS STRING), 'UNK'), ':', COALESCE(CAST(current_team AS STRING), CAST(team AS STRING), 'UNK'))
        ) AS source_player_key,
        CAST(player_id AS STRING) AS nflverse_player_id,
        CAST(player_name AS STRING) AS player_name,
        CAST(player_display_name AS STRING) AS display_name,
        {_normalized_name_sql("player_display_name")} AS normalized_name,
        CAST(position AS STRING) AS position,
        CAST(team AS STRING) AS team,
        CAST(current_team AS STRING) AS current_team,
        CAST(opponent_team AS STRING) AS opponent,
        CAST(roster_status AS STRING) AS roster_status,
        CAST(season AS INT64) AS season,
        CAST(week AS INT64) AS week,
        SAFE_CAST(fantasy_points_ppr AS FLOAT64) AS fantasy_points_ppr,
        SAFE_CAST(targets AS FLOAT64) AS targets,
        SAFE_CAST(receptions AS FLOAT64) AS receptions,
        SAFE_CAST(receiving_yards AS FLOAT64) AS receiving_yards,
        SAFE_CAST(receiving_tds AS FLOAT64) AS receiving_tds,
        SAFE_CAST(receiving_air_yards AS FLOAT64) AS receiving_air_yards,
        SAFE_CAST(carries AS FLOAT64) AS carries,
        SAFE_CAST(rushing_yards AS FLOAT64) AS rushing_yards,
        SAFE_CAST(rushing_tds AS FLOAT64) AS rushing_tds,
        SAFE_CAST(target_share AS FLOAT64) AS target_share,
        SAFE_CAST(carry_share AS FLOAT64) AS carry_share,
        SAFE_CAST(wopr AS FLOAT64) AS wopr,
        SAFE_CAST(total_epa AS FLOAT64) AS total_epa,
        SAFE_CAST(red_zone_touches AS FLOAT64) AS red_zone_touches,
        SAFE_CAST(offense_pct AS FLOAT64) AS offense_pct,
        SAFE_CAST(touchdowns AS FLOAT64) AS touchdowns,
        SAFE_CAST(rolling_3_week_opportunities AS FLOAT64) AS rolling_3_week_opportunities,
        SAFE_CAST(ppr_delta AS FLOAT64) AS ppr_delta,
        SAFE_CAST(points_over_role_score AS FLOAT64) AS points_over_role_score,
        SAFE_CAST(touchdown_dependency_rate AS FLOAT64) AS touchdown_dependency_rate,
        SAFE_CAST(role_quality_score AS FLOAT64) AS role_quality_score,
        SAFE_CAST(role_fragility_score AS FLOAT64) AS role_fragility_score
    FROM `{project_id}.{dataset_id}.analytics_player_weekly_truth`
    WHERE season_type = 'REG'
)"""


def _empty_truth_cte() -> str:
    return """
truth_source AS (
    SELECT
        CAST(NULL AS STRING) AS source_player_key,
        CAST(NULL AS STRING) AS nflverse_player_id,
        CAST(NULL AS STRING) AS player_name,
        CAST(NULL AS STRING) AS display_name,
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS STRING) AS team,
        CAST(NULL AS STRING) AS current_team,
        CAST(NULL AS STRING) AS opponent,
        CAST(NULL AS STRING) AS roster_status,
        CAST(NULL AS INT64) AS season,
        CAST(NULL AS INT64) AS week,
        CAST(NULL AS FLOAT64) AS fantasy_points_ppr,
        CAST(NULL AS FLOAT64) AS targets,
        CAST(NULL AS FLOAT64) AS receptions,
        CAST(NULL AS FLOAT64) AS receiving_yards,
        CAST(NULL AS FLOAT64) AS receiving_tds,
        CAST(NULL AS FLOAT64) AS receiving_air_yards,
        CAST(NULL AS FLOAT64) AS carries,
        CAST(NULL AS FLOAT64) AS rushing_yards,
        CAST(NULL AS FLOAT64) AS rushing_tds,
        CAST(NULL AS FLOAT64) AS target_share,
        CAST(NULL AS FLOAT64) AS carry_share,
        CAST(NULL AS FLOAT64) AS wopr,
        CAST(NULL AS FLOAT64) AS total_epa,
        CAST(NULL AS FLOAT64) AS red_zone_touches,
        CAST(NULL AS FLOAT64) AS offense_pct,
        CAST(NULL AS FLOAT64) AS touchdowns,
        CAST(NULL AS FLOAT64) AS rolling_3_week_opportunities,
        CAST(NULL AS FLOAT64) AS ppr_delta,
        CAST(NULL AS FLOAT64) AS points_over_role_score,
        CAST(NULL AS FLOAT64) AS touchdown_dependency_rate,
        CAST(NULL AS FLOAT64) AS role_quality_score,
        CAST(NULL AS FLOAT64) AS role_fragility_score
    WHERE FALSE
)"""


def _profile_points_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return _empty_profile_points_cte()
    return f"""
profile_points AS (
    SELECT
        source_player_key,
        player_id_internal,
        scoring_profile_id,
        season,
        week,
        total_fantasy_points
    FROM `{project_id}.{dataset_id}.analytics_player_fantasy_points_by_profile`
    WHERE scoring_profile_id = @scoring_profile_id
)"""


def _empty_profile_points_cte() -> str:
    return """
profile_points AS (
    SELECT
        CAST(NULL AS STRING) AS source_player_key,
        CAST(NULL AS STRING) AS player_id_internal,
        CAST(NULL AS STRING) AS scoring_profile_id,
        CAST(NULL AS INT64) AS season,
        CAST(NULL AS INT64) AS week,
        CAST(NULL AS FLOAT64) AS total_fantasy_points
    WHERE FALSE
)"""


def _identity_cte(
    project_id: str,
    dataset_id: str,
    source_status: dict[str, SourceTableStatus],
) -> str:
    dim_exists = source_status["dim_players_current"].exists
    bridge_exists = source_status["player_identity_bridge"].exists
    if dim_exists and bridge_exists:
        return f"""
identity AS (
    SELECT
        COALESCE(d.player_id_internal, b.player_id_internal) AS player_id_internal,
        COALESCE(d.gsis_id, b.gsis_id) AS gsis_id,
        COALESCE(d.sleeper_player_id, b.sleeper_player_id) AS sleeper_player_id,
        COALESCE(d.display_name, b.display_name) AS display_name,
        COALESCE(d.normalized_name, b.normalized_name) AS normalized_name,
        COALESCE(d.position, b.position) AS position,
        COALESCE(d.fantasy_positions, b.fantasy_positions) AS fantasy_positions,
        COALESCE(d.current_team, b.current_team) AS current_team,
        COALESCE(d.active_status, b.active_status) AS active_status,
        COALESCE(d.age, SAFE_DIVIDE(DATE_DIFF(CURRENT_DATE(), d.birth_date, DAY), 365.25)) AS age,
        COALESCE(d.gsis_id, b.gsis_id, d.sleeper_player_id, b.sleeper_player_id, d.player_id_internal, b.player_id_internal) AS source_player_key
    FROM `{project_id}.{dataset_id}.dim_players_current` d
    FULL OUTER JOIN `{project_id}.{dataset_id}.player_identity_bridge` b
        ON d.player_id_internal = b.player_id_internal
    WHERE COALESCE(d.position, b.position) IN ('QB', 'RB', 'WR', 'TE')
)"""
    if dim_exists:
        return f"""
identity AS (
    SELECT
        player_id_internal,
        gsis_id,
        sleeper_player_id,
        display_name,
        normalized_name,
        position,
        fantasy_positions,
        current_team,
        active_status,
        age,
        COALESCE(gsis_id, sleeper_player_id, player_id_internal) AS source_player_key
    FROM `{project_id}.{dataset_id}.dim_players_current`
    WHERE position IN ('QB', 'RB', 'WR', 'TE')
)"""
    if bridge_exists:
        return f"""
identity AS (
    SELECT
        player_id_internal,
        gsis_id,
        sleeper_player_id,
        display_name,
        normalized_name,
        position,
        fantasy_positions,
        current_team,
        active_status,
        CAST(NULL AS FLOAT64) AS age,
        COALESCE(gsis_id, sleeper_player_id, player_id_internal) AS source_player_key
    FROM `{project_id}.{dataset_id}.player_identity_bridge`
    WHERE position IN ('QB', 'RB', 'WR', 'TE')
)"""
    return _empty_identity_cte()


def _empty_identity_cte() -> str:
    return """
identity AS (
    SELECT
        CAST(NULL AS STRING) AS player_id_internal,
        CAST(NULL AS STRING) AS gsis_id,
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS STRING) AS display_name,
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS STRING) AS fantasy_positions,
        CAST(NULL AS STRING) AS current_team,
        CAST(NULL AS STRING) AS active_status,
        CAST(NULL AS FLOAT64) AS age,
        CAST(NULL AS STRING) AS source_player_key
    WHERE FALSE
)"""


def _sleeper_current_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return _empty_sleeper_current_cte()
    return f"""
sleeper_current AS (
    SELECT * EXCEPT(rn)
    FROM (
        SELECT
            sleeper_player_id,
            gsis_id,
            player_name,
            {_normalized_name_sql("player_name")} AS normalized_name,
            position,
            team,
            active,
            status,
            injury_status,
            fantasy_positions_json,
            depth_chart_position,
            depth_chart_order,
            search_rank,
            years_exp,
            ROW_NUMBER() OVER(
                PARTITION BY sleeper_player_id
                ORDER BY snapshot_at DESC
            ) AS rn
        FROM `{project_id}.{dataset_id}.sleeper_players_current`
        WHERE position IN ('QB', 'RB', 'WR', 'TE')
    )
    WHERE rn = 1
)"""


def _empty_sleeper_current_cte() -> str:
    return """
sleeper_current AS (
    SELECT
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS STRING) AS gsis_id,
        CAST(NULL AS STRING) AS player_name,
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS STRING) AS team,
        CAST(NULL AS BOOL) AS active,
        CAST(NULL AS STRING) AS status,
        CAST(NULL AS STRING) AS injury_status,
        CAST(NULL AS STRING) AS fantasy_positions_json,
        CAST(NULL AS STRING) AS depth_chart_position,
        CAST(NULL AS INT64) AS depth_chart_order,
        CAST(NULL AS INT64) AS search_rank,
        CAST(NULL AS INT64) AS years_exp
    WHERE FALSE
)"""


def _rankings_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return _empty_rankings_cte()
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
            CAST(NULL AS INT64) AS pigskin_rank_overall,
            rank AS pigskin_rank_position,
            tier AS pigskin_tier,
            ranking_score AS pigskin_projection,
            confidence_score AS pigskin_confidence,
            rank_rationale AS pigskin_summary,
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


def _empty_rankings_cte() -> str:
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
        CAST(NULL AS FLOAT64) AS pigskin_confidence,
        CAST(NULL AS STRING) AS pigskin_summary
    WHERE FALSE
)"""


def _fraud_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return _empty_fraud_cte()
    return f"""
fraud AS (
    SELECT
        {_normalized_name_sql("player_display_name")} AS normalized_name,
        position,
        MAX(fraud_score) AS fraud_risk_score
    FROM `{project_id}.{dataset_id}.analytics_fraud_watch`
    GROUP BY normalized_name, position
)"""


def _empty_fraud_cte() -> str:
    return """
fraud AS (
    SELECT
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS FLOAT64) AS fraud_risk_score
    WHERE FALSE
)"""


def _environment_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return _empty_environment_cte()
    return f"""
game_environment AS (
    SELECT
        season,
        week,
        game_id,
        home_team,
        away_team,
        TO_JSON_STRING(STRUCT(
            stadium AS stadium,
            roof AS roof,
            surface AS surface,
            temp_f AS temp_f,
            wind_mph AS wind_mph,
            weather_text AS weather_text,
            is_indoor_or_closed AS is_indoor_or_closed,
            environment_risk_level AS environment_risk_level,
            fantasy_environment_note AS fantasy_environment_note
        )) AS game_environment_json
    FROM `{project_id}.{dataset_id}.analytics_game_environment`
)"""


def _empty_environment_cte() -> str:
    return """
game_environment AS (
    SELECT
        CAST(NULL AS INT64) AS season,
        CAST(NULL AS INT64) AS week,
        CAST(NULL AS STRING) AS game_id,
        CAST(NULL AS STRING) AS home_team,
        CAST(NULL AS STRING) AS away_team,
        CAST(NULL AS STRING) AS game_environment_json
    WHERE FALSE
)"""


def _roster_context_ctes(
    project_id: str,
    dataset_id: str,
    source_status: dict[str, SourceTableStatus],
) -> str:
    rosters_exist = source_status["sleeper_rosters"].exists
    roster_players_exist = source_status["sleeper_roster_players"].exists
    available_exist = source_status["sleeper_available_players"].exists
    if not rosters_exist or not roster_players_exist:
        return _empty_roster_context_ctes(available_exists=available_exist, project_id=project_id, dataset_id=dataset_id)
    available_cte = _league_available_cte(project_id, dataset_id) if available_exist else _empty_league_available_cte()
    return f"""
latest_roster_snapshot AS (
    SELECT MAX(snapshot_at) AS snapshot_at
    FROM `{project_id}.{dataset_id}.sleeper_rosters`
    WHERE (@league_id IS NULL OR league_id = @league_id)
),
total_leagues AS (
    SELECT COUNT(DISTINCT league_id) AS total_leagues_count
    FROM `{project_id}.{dataset_id}.sleeper_rosters`
    WHERE snapshot_at = (SELECT snapshot_at FROM latest_roster_snapshot)
),
global_roster_rates AS (
    SELECT
        rp.sleeper_player_id,
        SAFE_DIVIDE(COUNT(DISTINCT rp.league_id), NULLIF((SELECT total_leagues_count FROM total_leagues), 0)) AS rostered_rate
    FROM `{project_id}.{dataset_id}.sleeper_roster_players` rp
    WHERE rp.snapshot_at = (SELECT snapshot_at FROM latest_roster_snapshot)
    GROUP BY rp.sleeper_player_id
),
league_rostered AS (
    SELECT
        sleeper_player_id,
        TRUE AS rostered_in_league_flag
    FROM `{project_id}.{dataset_id}.sleeper_roster_players`
    WHERE @league_id IS NOT NULL
        AND league_id = @league_id
        AND snapshot_at = (SELECT snapshot_at FROM latest_roster_snapshot)
    GROUP BY sleeper_player_id
),
{available_cte}"""


def _empty_roster_context_ctes(*, available_exists: bool, project_id: str, dataset_id: str) -> str:
    available_cte = _league_available_cte(project_id, dataset_id) if available_exists else _empty_league_available_cte()
    return f"""
latest_roster_snapshot AS (
    SELECT CAST(NULL AS TIMESTAMP) AS snapshot_at
    WHERE FALSE
),
total_leagues AS (
    SELECT CAST(NULL AS INT64) AS total_leagues_count
),
global_roster_rates AS (
    SELECT
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS FLOAT64) AS rostered_rate
    WHERE FALSE
),
league_rostered AS (
    SELECT
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS BOOL) AS rostered_in_league_flag
    WHERE FALSE
),
{available_cte}"""


def _league_available_cte(project_id: str, dataset_id: str) -> str:
    return f"""
league_available AS (
    SELECT
        sleeper_player_id,
        TRUE AS available_in_league_flag
    FROM `{project_id}.{dataset_id}.sleeper_available_players`
    WHERE @league_id IS NOT NULL
        AND league_id = @league_id
        AND snapshot_at = (
            SELECT MAX(snapshot_at)
            FROM `{project_id}.{dataset_id}.sleeper_available_players`
            WHERE league_id = @league_id
        )
    GROUP BY sleeper_player_id
)"""


def _empty_league_available_cte() -> str:
    return """
league_available AS (
    SELECT
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS BOOL) AS available_in_league_flag
    WHERE FALSE
)"""


def _trending_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return _empty_trending_cte()
    return f"""
trending AS (
    SELECT
        CAST(player_id AS STRING) AS sleeper_player_id,
        CAST(gsis_id AS STRING) AS gsis_id,
        SUM(IF(trend_type = 'ADD', trend_count, 0)) AS sleeper_trending_add_count,
        SUM(IF(trend_type = 'DROP', trend_count, 0)) AS sleeper_trending_drop_count
    FROM `{project_id}.{dataset_id}.realtime_player_news`
    GROUP BY sleeper_player_id, gsis_id
)"""


def _empty_trending_cte() -> str:
    return """
trending AS (
    SELECT
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS STRING) AS gsis_id,
        CAST(NULL AS INT64) AS sleeper_trending_add_count,
        CAST(NULL AS INT64) AS sleeper_trending_drop_count
    WHERE FALSE
)"""


def _count_output_rows(client: bigquery.Client, dataset_id: str) -> int:
    rows = list(client.query(
        f"SELECT COUNT(*) AS row_count FROM `{client.project}.{dataset_id}.{OUTPUT_TABLE}`"
    ).result())
    return int(rows[0].row_count) if rows else 0


def _count_flagged_rows(client: bigquery.Client, dataset_id: str) -> int:
    rows = list(client.query(
        f"""
        SELECT COUNT(*) AS row_count
        FROM `{client.project}.{dataset_id}.{OUTPUT_TABLE}`
        WHERE missing_data_flags IS NOT NULL
            AND missing_data_flags != '[]'
        """
    ).result())
    return int(rows[0].row_count) if rows else 0


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


def _parse_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize Sleeper Watch candidate mart.")
    parser.add_argument("--project", default=get_bigquery_project())
    parser.add_argument("--dataset", default=get_bigquery_dataset())
    parser.add_argument("--season", type=int)
    parser.add_argument("--week", type=int)
    parser.add_argument("--league-id")
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
    row_count = materialize_sleeper_watch(
        client,
        dataset_id=args.dataset,
        season=args.season,
        week=args.week,
        league_id=args.league_id,
        scoring_profile_id=args.scoring_profile_id,
        league_type_id=args.league_type_id,
        roster_format_id=args.roster_format_id,
        model_run_id=args.model_run_id,
        dry_run=args.dry_run,
    )
    print(f"{OUTPUT_TABLE} rows materialized: {row_count}")


if __name__ == "__main__":
    main()
