"""Materialize bounded LLM-ready player context packets."""

from __future__ import annotations

import argparse
import logging
import os
import re
from dataclasses import dataclass

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.load import get_bigquery_project
from src.materialize_player_profiles import load_active_scoring_profile_ids


logger = logging.getLogger(__name__)

DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_SCORING_PROFILE = "ppr"
DEFAULT_LEAGUE_TYPE = "redraft"
DEFAULT_ROSTER_FORMAT = "one_qb"
OUTPUT_TABLE = "mart_llm_player_context_packet"
PACKET_TEXT_LIMIT = 8000
OPTIONAL_CONTEXT_TABLES = (
    "analytics_fraud_watch",
    "analytics_pigskin_rankings_history",
    "analytics_player_qb_splits",
    "analytics_context_events",
    "analytics_external_context_search_results",
)
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class SourceTableStatus:
    exists: bool
    columns: frozenset[str]


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def table_exists(client: bigquery.Client, dataset_id: str, table_name: str) -> bool:
    try:
        client.get_table(f"{client.project}.{dataset_id}.{table_name}")
        return True
    except NotFound:
        return False


def table_columns(client: bigquery.Client, dataset_id: str, table_name: str) -> frozenset[str]:
    table = client.get_table(f"{client.project}.{dataset_id}.{table_name}")
    return frozenset(field.name for field in table.schema)


def inspect_source_status(client: bigquery.Client, dataset_id: str) -> dict[str, SourceTableStatus]:
    status = {}
    for table_name in OPTIONAL_CONTEXT_TABLES:
        if table_exists(client, dataset_id, table_name):
            status[table_name] = SourceTableStatus(True, table_columns(client, dataset_id, table_name))
        else:
            status[table_name] = SourceTableStatus(False, frozenset())
    return status


def build_llm_packets_sql(
    *,
    project_id: str,
    dataset_id: str,
    source_status: dict[str, SourceTableStatus] | None = None,
) -> str:
    _validate_identifier(dataset_id, "dataset_id")
    source_status = source_status or {
        table_name: SourceTableStatus(False, frozenset())
        for table_name in OPTIONAL_CONTEXT_TABLES
    }
    flags = {
        table_name: "TRUE" if status.exists else "FALSE"
        for table_name, status in source_status.items()
    }
    return f"""
CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.{OUTPUT_TABLE}`
PARTITION BY DATE(updated_at)
CLUSTER BY player_id_internal, scoring_profile_id, position, team AS
WITH selected_profiles AS (
    SELECT scoring_profile_id
    FROM UNNEST(@scoring_profile_ids) AS scoring_profile_id
),
latest_profile_as_of AS (
    SELECT
        as_of_season,
        as_of_week
    FROM `{project_id}.{dataset_id}.compat_player_profiles_current`
    WHERE scoring_profile_id IN UNNEST(@scoring_profile_ids)
        AND (@season IS NULL OR as_of_season = @season)
        AND (@week IS NULL OR as_of_week <= @week)
    ORDER BY as_of_season DESC, as_of_week DESC
    LIMIT 1
),
latest_model_run AS (
    SELECT model_run_id
    FROM `{project_id}.{dataset_id}.model_runs`
    WHERE run_type = 'pigskin_rankings'
        AND status = 'complete'
    ORDER BY COALESCE(completed_at, created_at) DESC
    LIMIT 1
),
profiles AS (
    SELECT
        p.*,
        COALESCE(@league_type_id, p.league_type_id, '{DEFAULT_LEAGUE_TYPE}') AS packet_league_type_id,
        COALESCE(@roster_format_id, p.roster_format_id, '{DEFAULT_ROSTER_FORMAT}') AS packet_roster_format_id,
        COALESCE(@model_run_id, p.model_run_id, latest_model_run.model_run_id) AS packet_model_run_id
    FROM `{project_id}.{dataset_id}.compat_player_profiles_current` p
    JOIN latest_profile_as_of lpa
        ON p.as_of_season = lpa.as_of_season
        AND p.as_of_week = lpa.as_of_week
    LEFT JOIN latest_model_run ON TRUE
    WHERE p.scoring_profile_id IN UNNEST(@scoring_profile_ids)
        AND (@player_id_internal IS NULL OR p.player_id_internal = @player_id_internal OR p.source_player_key = @player_id_internal)
        AND p.position IN ('QB', 'RB', 'WR', 'TE')
),
ranked_trade AS (
    SELECT
        th.*,
        ROW_NUMBER() OVER(
            PARTITION BY COALESCE(th.player_id_internal, th.source_player_key), th.scoring_profile_id
            ORDER BY th.season DESC, th.week DESC
        ) AS rn
    FROM `{project_id}.{dataset_id}.compat_trade_player_history` th
    JOIN profiles p
        ON th.scoring_profile_id = p.scoring_profile_id
        AND (
            (p.player_id_internal IS NOT NULL AND th.player_id_internal = p.player_id_internal)
            OR (p.source_player_key IS NOT NULL AND th.source_player_key = p.source_player_key)
            OR (p.gsis_id IS NOT NULL AND th.source_player_key = p.gsis_id)
        )
        AND (
            th.season < p.as_of_season
            OR (th.season = p.as_of_season AND th.week <= p.as_of_week)
        )
),
trade_context AS (
    SELECT
        COALESCE(player_id_internal, source_player_key) AS player_profile_key,
        scoring_profile_id,
        MAX(IF(rn = 1, total_fantasy_points, NULL)) AS fantasy_points_last_1,
        AVG(IF(rn <= 8, total_fantasy_points, NULL)) AS fantasy_points_per_game_last_8,
        STDDEV(IF(rn <= 8, total_fantasy_points, NULL)) AS fantasy_points_volatility_last_8,
        TO_JSON_STRING(ARRAY_AGG(
            IF(
                rn <= 8,
                STRUCT(
                    season,
                    week,
                    team,
                    opponent,
                    total_fantasy_points,
                    targets,
                    carries,
                    receptions,
                    target_share,
                    rush_share,
                    air_yard_share,
                    red_zone_opportunities,
                    high_value_touches,
                    epa_summary_json,
                    qb_split_json,
                    game_environment_json,
                    missing_data_flags
                ),
                NULL
            )
            IGNORE NULLS
            ORDER BY season DESC, week DESC
            LIMIT 8
        )) AS recent_games_json
    FROM ranked_trade
    GROUP BY player_profile_key, scoring_profile_id
),
{_ranking_history_cte(project_id, dataset_id, source_status["analytics_pigskin_rankings_history"])},
{_fraud_context_cte(project_id, dataset_id, source_status["analytics_fraud_watch"])},
{_qb_context_cte(project_id, dataset_id, source_status["analytics_player_qb_splits"])},
{_context_events_cte(project_id, dataset_id, source_status["analytics_context_events"])},
{_external_context_cte(project_id, dataset_id, source_status["analytics_external_context_search_results"])},
assembled AS (
    SELECT
        TO_HEX(MD5(CONCAT(
            COALESCE(p.packet_model_run_id, 'missing-model-run'),
            '|',
            COALESCE(p.player_id_internal, p.source_player_key, p.display_name, 'missing-player'),
            '|',
            p.scoring_profile_id,
            '|',
            p.packet_league_type_id,
            '|',
            p.packet_roster_format_id,
            '|',
            CAST(p.as_of_season AS STRING),
            '|',
            CAST(p.as_of_week AS STRING)
        ))) AS packet_id,
        p.packet_model_run_id AS model_run_id,
        p.ranking_version,
        p.player_id_internal,
        p.source_player_key,
        p.display_name,
        p.position,
        p.current_team AS team,
        p.scoring_profile_id,
        p.packet_league_type_id AS league_type_id,
        p.packet_roster_format_id AS roster_format_id,
        p.as_of_season,
        p.as_of_week,
        TO_JSON_STRING(STRUCT(
            STRUCT(
                p.player_id_internal,
                p.source_player_key,
                p.display_name,
                p.full_name,
                p.current_team AS team,
                p.position,
                p.fantasy_positions,
                p.age,
                p.rookie_year,
                p.active_status
            ) AS identity,
            STRUCT(
                p.packet_model_run_id AS model_run_id,
                p.ranking_version,
                p.pigskin_rank_overall,
                p.pigskin_rank_position,
                p.pigskin_tier,
                p.pigskin_projection,
                p.pigskin_confidence,
                rh.ranking_history_json AS rank_movement,
                p.scoring_profile_id,
                p.packet_league_type_id AS league_type_id,
                p.packet_roster_format_id AS roster_format_id
            ) AS ranking_context,
            STRUCT(
                tc.fantasy_points_last_1,
                p.fantasy_points_last_3,
                p.fantasy_points_last_5,
                p.fantasy_points_last_8,
                p.fantasy_points_current_season,
                p.fantasy_points_per_game_current_season AS fantasy_points_per_game,
                p.total_fantasy_points_standard,
                p.total_fantasy_points_half_ppr,
                p.total_fantasy_points_ppr,
                tc.recent_games_json
            ) AS recent_fantasy_summary,
            STRUCT(
                p.snap_share_last_3,
                p.targets_last_3,
                p.target_share_last_3,
                p.carries_last_3,
                p.rush_share_last_3,
                p.receptions_last_3,
                p.air_yards_last_3,
                p.air_yard_share_last_3,
                p.red_zone_opportunities_last_3,
                p.high_value_touches_last_3,
                p.role_summary_json,
                CASE
                    WHEN p.target_share_last_3 >= 0.25 OR p.rush_share_last_3 >= 0.55 THEN 'role spike'
                    WHEN p.target_share_last_3 >= 0.18 OR p.rush_share_last_3 >= 0.40 THEN 'usable role'
                    WHEN p.targets_last_3 IS NULL AND p.carries_last_3 IS NULL THEN 'missing usage'
                    ELSE 'thin role'
                END AS usage_trend_label
            ) AS usage_summary,
            STRUCT(
                p.yards_per_carry_current_season,
                p.yards_per_target_current_season,
                p.yards_per_reception_current_season,
                p.catch_rate_current_season,
                p.td_rate_current_season AS td_dependency,
                p.epa_summary_json,
                p.efficiency_summary_json,
                IF(p.td_rate_current_season >= 0.25, ['td_dependency_warning'], []) AS regression_flags
            ) AS efficiency_summary,
            STRUCT(
                tc.recent_games_json AS recent_game_context,
                'upcoming weather and odds are not available in this packet yet' AS weather_odds_placeholder
            ) AS game_environment,
            STRUCT(
                qb.qb_context_json,
                'team offensive context is pending a dedicated team mart' AS team_context_placeholder,
                'teammate target competition is pending a dedicated team target tree mart' AS teammate_context_placeholder
            ) AS qb_and_team_context,
            STRUCT(
                fraud.fraud_context_json,
                'breakout score pending sleeper/breakout mart' AS breakout_placeholder,
                IF(p.td_rate_current_season >= 0.25, 'touchdown dependency risk', NULL) AS td_dependency_note,
                CASE
                    WHEN p.targets_last_3 + p.carries_last_3 < 10 AND p.fantasy_points_last_3 >= 25 THEN 'low-volume spike warning'
                    ELSE NULL
                END AS low_volume_spike_warning
            ) AS fraud_watch_context,
            STRUCT(
                tc.recent_games_json AS trade_history_summary,
                p.fantasy_points_per_game_current_season AS scoring_profile_value_summary,
                tc.fantasy_points_volatility_last_8 AS volatility_last_8,
                CASE
                    WHEN tc.fantasy_points_volatility_last_8 >= 8 THEN 'volatile weekly scoring'
                    WHEN tc.fantasy_points_volatility_last_8 IS NULL THEN 'missing volatility sample'
                    ELSE 'stable enough sample'
                END AS risk_note
            ) AS trade_context,
            STRUCT(
                ce.context_events_json,
                ext.external_leads_json,
                'external leads are supporting context, not verified truth alone' AS caveat
            ) AS external_context,
            STRUCT(
                CASE
                    WHEN p.pigskin_rank_position <= 24 AND p.fantasy_points_per_game_current_season < 10 THEN 'High Pigskin rank needs role or efficiency support because current fantasy scoring is light.'
                    WHEN p.pigskin_rank_position > 60 AND p.fantasy_points_per_game_current_season >= 14 THEN 'The market could argue the recent box score deserves more respect than the rank gives it.'
                    ELSE 'The strongest counterargument depends on missing context flags and current role stability.'
                END AS strongest_argument_against_model_take,
                'A materially different role, healthier QB context, changed depth chart, or new model_run_id should change the take.' AS what_data_would_change_the_take,
                IF(p.packet_model_run_id IS NULL, 'confidence limited by missing model_run_id', 'confidence depends on source freshness and missing flags') AS confidence_caveat
            ) AS counterarguments,
            ARRAY_CONCAT(
                [CONCAT(COALESCE(p.display_name, 'Unknown player'), ' packet is built from curated marts, not a box-score horoscope.')],
                IF(p.pigskin_rank_position IS NOT NULL, [CONCAT('Pigskin rank: ', CAST(p.pigskin_rank_position AS STRING), ', tier: ', COALESCE(p.pigskin_tier, 'unknown'))], []),
                IF(p.targets_last_3 IS NOT NULL, [CONCAT('Last 3 targets: ', CAST(ROUND(p.targets_last_3, 1) AS STRING))], []),
                IF(p.carries_last_3 IS NOT NULL, [CONCAT('Last 3 carries: ', CAST(ROUND(p.carries_last_3, 1) AS STRING))], []),
                IF(p.td_rate_current_season >= 0.25, ['Touchdown dependency is getting loud. Regression is waiting with receipts.'], []),
                IF(p.missing_data_flags IS NOT NULL AND p.missing_data_flags != '[]', ['There are missing-context flags, so the take should stay humble until the data catches up.'], [])
            ) AS snark_hooks,
            STRUCT(
                ['compat_player_profiles_current', 'compat_trade_player_history', 'model_runs'] AS required_sources,
                ['analytics_fraud_watch', 'analytics_pigskin_rankings_history', 'analytics_player_qb_splits', 'analytics_context_events', 'analytics_external_context_search_results'] AS optional_sources,
                p.source_freshness_json AS profile_source_freshness_json,
                p.packet_model_run_id AS model_run_id,
                CURRENT_TIMESTAMP() AS generated_at
            ) AS source_metadata
        )) AS packet_json,
        SUBSTR(CONCAT(
            'PLAYER: ', COALESCE(p.display_name, 'unknown'), ' | ', COALESCE(p.position, 'unknown'), ' | ', COALESCE(p.current_team, 'FA'), '\\n',
            'RANKING: Pigskin rank ', COALESCE(CAST(p.pigskin_rank_position AS STRING), 'missing'), ', tier ', COALESCE(p.pigskin_tier, 'missing'), ', model_run_id ', COALESCE(p.packet_model_run_id, 'missing'), '\\n',
            'FANTASY: current ', COALESCE(CAST(ROUND(p.fantasy_points_current_season, 2) AS STRING), 'missing'), ', PPG ', COALESCE(CAST(ROUND(p.fantasy_points_per_game_current_season, 2) AS STRING), 'missing'), ', last3 ', COALESCE(CAST(ROUND(p.fantasy_points_last_3, 2) AS STRING), 'missing'), ', last5 ', COALESCE(CAST(ROUND(p.fantasy_points_last_5, 2) AS STRING), 'missing'), '\\n',
            'USAGE: last3 targets ', COALESCE(CAST(ROUND(p.targets_last_3, 1) AS STRING), 'missing'), ', carries ', COALESCE(CAST(ROUND(p.carries_last_3, 1) AS STRING), 'missing'), ', target share ', COALESCE(CAST(ROUND(p.target_share_last_3, 3) AS STRING), 'missing'), ', rush share ', COALESCE(CAST(ROUND(p.rush_share_last_3, 3) AS STRING), 'missing'), '\\n',
            'EFFICIENCY: ypc ', COALESCE(CAST(ROUND(p.yards_per_carry_current_season, 2) AS STRING), 'missing'), ', ypt ', COALESCE(CAST(ROUND(p.yards_per_target_current_season, 2) AS STRING), 'missing'), ', catch rate ', COALESCE(CAST(ROUND(p.catch_rate_current_season, 3) AS STRING), 'missing'), ', td rate ', COALESCE(CAST(ROUND(p.td_rate_current_season, 3) AS STRING), 'missing'), '\\n',
            'FRAUD WATCH: ', COALESCE(fraud.fraud_context_json, 'missing'), '\\n',
            'QB CONTEXT: ', COALESCE(qb.qb_context_json, 'missing'), '\\n',
            'RECENT TRADE HISTORY: ', COALESCE(tc.recent_games_json, 'missing'), '\\n',
            'EXTERNAL CONTEXT: ', COALESCE(ce.context_events_json, 'missing events'), ' | ', COALESCE(ext.external_leads_json, 'missing leads'), '\\n',
            'COUNTERARGUMENT: ', CASE
                WHEN p.pigskin_rank_position <= 24 AND p.fantasy_points_per_game_current_season < 10 THEN 'High rank needs role or efficiency support because current fantasy scoring is light.'
                WHEN p.pigskin_rank_position > 60 AND p.fantasy_points_per_game_current_season >= 14 THEN 'Recent box score may deserve more respect than the rank gives it.'
                ELSE 'Check missing flags and role stability before turning the take into a sermon.'
            END, '\\n',
            'MISSING FLAGS: ', COALESCE(p.missing_data_flags, '[]')
        ), 1, {PACKET_TEXT_LIMIT}) AS packet_text,
        TO_JSON_STRING(STRUCT(
            p.source_freshness_json AS profile_source_freshness_json,
            {flags["analytics_fraud_watch"]} AS analytics_fraud_watch_available,
            {flags["analytics_pigskin_rankings_history"]} AS analytics_pigskin_rankings_history_available,
            {flags["analytics_player_qb_splits"]} AS analytics_player_qb_splits_available,
            {flags["analytics_context_events"]} AS analytics_context_events_available,
            {flags["analytics_external_context_search_results"]} AS analytics_external_context_search_results_available,
            CURRENT_TIMESTAMP() AS packet_generated_at
        )) AS source_freshness_json,
        TO_JSON_STRING(ARRAY(
            SELECT DISTINCT flag
            FROM UNNEST(ARRAY_CONCAT(
                IF(p.packet_model_run_id IS NULL, ['missing_model_run_id'], []),
                IF(p.player_id_internal IS NULL, ['missing_player_id_internal'], []),
                IF(p.source_player_key IS NULL, ['missing_source_player_key'], []),
                IF(tc.recent_games_json IS NULL, ['missing_trade_history_context'], []),
                IF(fraud.fraud_context_json IS NULL, ['missing_fraud_watch_context'], []),
                IF(qb.qb_context_json IS NULL, ['missing_qb_context'], []),
                IF(rh.ranking_history_json IS NULL, ['missing_ranking_history'], []),
                IF(ce.context_events_json IS NULL, ['missing_context_events'], []),
                IF(ext.external_leads_json IS NULL, ['missing_external_leads'], []),
                IF({flags["analytics_fraud_watch"]}, [], ['missing_analytics_fraud_watch_source']),
                IF({flags["analytics_pigskin_rankings_history"]}, [], ['missing_analytics_pigskin_rankings_history_source']),
                IF({flags["analytics_player_qb_splits"]}, [], ['missing_analytics_player_qb_splits_source']),
                IF({flags["analytics_context_events"]}, [], ['missing_analytics_context_events_source']),
                IF({flags["analytics_external_context_search_results"]}, ['temporary_name_join_external_leads'], ['missing_analytics_external_context_search_results_source'])
            )) AS flag
            WHERE flag IS NOT NULL
            ORDER BY flag
        )) AS missing_data_flags,
        CURRENT_TIMESTAMP() AS created_at,
        CURRENT_TIMESTAMP() AS updated_at
    FROM profiles p
    LEFT JOIN trade_context tc
        ON COALESCE(p.player_id_internal, p.source_player_key) = tc.player_profile_key
        AND p.scoring_profile_id = tc.scoring_profile_id
    LEFT JOIN ranking_history rh
        ON (
            p.source_player_key = rh.ranking_key
            OR p.gsis_id = rh.ranking_key
            OR p.sleeper_player_id = rh.ranking_key
        )
        AND p.position = rh.position
    LEFT JOIN fraud_context fraud
        ON p.source_player_key = fraud.player_key
        OR p.gsis_id = fraud.player_key
    LEFT JOIN qb_context qb
        ON p.source_player_key = qb.player_key
        OR p.gsis_id = qb.player_key
    LEFT JOIN context_events ce
        ON p.source_player_key = ce.event_player_key
        OR p.gsis_id = ce.event_player_key
        OR p.normalized_name = ce.event_name_key
    LEFT JOIN external_leads ext
        ON p.normalized_name = ext.external_name_key
)
SELECT
    packet_id,
    model_run_id,
    ranking_version,
    player_id_internal,
    source_player_key,
    display_name,
    position,
    team,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    as_of_season,
    as_of_week,
    packet_json,
    packet_text,
    CAST(CEIL(LENGTH(packet_text) / 4.0) AS INT64) AS token_estimate,
    source_freshness_json,
    missing_data_flags,
    created_at,
    updated_at
FROM assembled
"""


def materialize_llm_packets(
    client: bigquery.Client,
    *,
    dataset_id: str = DEFAULT_DATASET,
    season: int | None = None,
    week: int | None = None,
    scoring_profile_ids: list[str] | tuple[str, ...] | None = None,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    player_id_internal: str | None = None,
    dry_run: bool = False,
) -> int:
    profile_ids = load_active_scoring_profile_ids(client, dataset_id, scoring_profile_ids or [DEFAULT_SCORING_PROFILE])
    source_status = inspect_source_status(client, dataset_id)
    missing_sources = [name for name, status in source_status.items() if not status.exists]
    if missing_sources:
        logger.warning("Optional LLM packet sources missing: %s", ", ".join(sorted(missing_sources)))
    sql = build_llm_packets_sql(project_id=client.project, dataset_id=dataset_id, source_status=source_status)
    job_config = bigquery.QueryJobConfig(
        dry_run=dry_run,
        use_query_cache=False,
        query_parameters=[
            bigquery.ArrayQueryParameter("scoring_profile_ids", "STRING", profile_ids),
            bigquery.ScalarQueryParameter("season", "INT64", season),
            bigquery.ScalarQueryParameter("week", "INT64", week),
            bigquery.ScalarQueryParameter("league_type_id", "STRING", league_type_id),
            bigquery.ScalarQueryParameter("roster_format_id", "STRING", roster_format_id),
            bigquery.ScalarQueryParameter("model_run_id", "STRING", model_run_id),
            bigquery.ScalarQueryParameter("player_id_internal", "STRING", player_id_internal),
        ],
    )
    job = client.query(sql, job_config=job_config)
    if dry_run:
        logger.info("Dry run bytes processed: %s", job.total_bytes_processed)
        return 0
    job.result()
    row_count = _count_output_rows(client, dataset_id)
    logger.info("Materialized %s rows in %s.%s.%s", row_count, client.project, dataset_id, OUTPUT_TABLE)
    return row_count


def _ranking_history_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return _empty_context_cte("ranking_history", "ranking_key", "position", "ranking_history_json")
    return f"""
ranking_history AS (
    SELECT
        COALESCE(player_id, sleeper_player_id, player_name) AS ranking_key,
        position,
        TO_JSON_STRING(ARRAY_AGG(STRUCT(
            model_run_id,
            ranking_version,
            rank AS pigskin_rank_position,
            tier AS pigskin_tier,
            ranking_score,
            confidence_score,
            generated_at
        ) ORDER BY generated_at DESC LIMIT 5)) AS ranking_history_json
    FROM `{project_id}.{dataset_id}.analytics_pigskin_rankings_history`
    GROUP BY ranking_key, position
)"""


def _fraud_context_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return _empty_context_cte("fraud_context", "player_key", "position", "fraud_context_json")
    return f"""
fraud_context AS (
    SELECT
        player_id AS player_key,
        position,
        TO_JSON_STRING(ARRAY_AGG(STRUCT(
            season,
            week,
            fraud_score,
            fraud_label,
            fraud_case,
            what_would_change_mind,
            fantasy_points_ppr,
            targets,
            carries,
            touchdown_dependency_rate,
            role_quality_score,
            role_fragility_score
        ) ORDER BY season DESC, week DESC, fraud_score DESC LIMIT 5)) AS fraud_context_json
    FROM `{project_id}.{dataset_id}.analytics_fraud_watch`
    GROUP BY player_key, position
)"""


def _qb_context_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return _empty_context_cte("qb_context", "player_key", "position", "qb_context_json")
    return f"""
qb_context AS (
    SELECT
        player_id AS player_key,
        CAST(NULL AS STRING) AS position,
        TO_JSON_STRING(ARRAY_AGG(STRUCT(
            season,
            posteam,
            qb_name,
            weeks_with_targets,
            targets,
            receptions,
            catch_rate,
            yards_per_target,
            air_yards,
            adot,
            touchdowns,
            red_zone_targets,
            total_epa,
            epa_per_target,
            target_share_from_qb,
            sample_label
        ) ORDER BY season DESC, targets DESC LIMIT 5)) AS qb_context_json
    FROM `{project_id}.{dataset_id}.analytics_player_qb_splits`
    GROUP BY player_key
)"""


def _context_events_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return """
context_events AS (
    SELECT
        CAST(NULL AS STRING) AS event_player_key,
        CAST(NULL AS STRING) AS event_name_key,
        CAST(NULL AS STRING) AS context_events_json
    WHERE FALSE
)"""
    return f"""
context_events AS (
    SELECT
        COALESCE(affected_player_id, subject_player_id) AS event_player_key,
        {_normalized_name_sql("COALESCE(affected_player_name, subject_name)")} AS event_name_key,
        TO_JSON_STRING(ARRAY_AGG(STRUCT(
            season,
            start_week,
            end_week,
            team,
            event_type,
            causal_status,
            confidence_score,
            source_type,
            source_label,
            source_url,
            summary,
            analysis_instruction
        ) ORDER BY season DESC, start_week DESC, confidence_score DESC LIMIT 5)) AS context_events_json
    FROM `{project_id}.{dataset_id}.analytics_context_events`
    WHERE COALESCE(active, TRUE)
    GROUP BY event_player_key, event_name_key
)"""


def _external_context_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return """
external_leads AS (
    SELECT
        CAST(NULL AS STRING) AS external_name_key,
        CAST(NULL AS STRING) AS external_leads_json
    WHERE FALSE
)"""
    return f"""
external_leads AS (
    SELECT
        {_normalized_name_sql("player_name")} AS external_name_key,
        TO_JSON_STRING(ARRAY_AGG(STRUCT(
            searched_at,
            result_rank,
            title,
            link,
            display_link,
            snippet,
            source_type,
            provider,
            source_name
        ) ORDER BY searched_at DESC, result_rank ASC LIMIT 5)) AS external_leads_json
    FROM `{project_id}.{dataset_id}.analytics_external_context_search_results`
    GROUP BY external_name_key
)"""


def _empty_context_cte(cte_name: str, key_column: str, position_column: str, json_column: str) -> str:
    return f"""
{cte_name} AS (
    SELECT
        CAST(NULL AS STRING) AS {key_column},
        CAST(NULL AS STRING) AS {position_column},
        CAST(NULL AS STRING) AS {json_column}
    WHERE FALSE
)"""


def _normalized_name_sql(expr: str) -> str:
    return (
        "REGEXP_REPLACE("
        f"REGEXP_REPLACE(LOWER(COALESCE({expr}, '')), r'\\s+(jr|sr|ii|iii|iv|v)\\.?$', ''), "
        "r'[^a-z0-9]+', '')"
    )


def _count_output_rows(client: bigquery.Client, dataset_id: str) -> int:
    sql = f"SELECT COUNT(*) AS row_count FROM `{client.project}.{dataset_id}.{OUTPUT_TABLE}`"
    rows = list(client.query(sql).result())
    return int(rows[0].row_count) if rows else 0


def _validate_identifier(value: str, label: str) -> None:
    if not IDENTIFIER_RE.match(value):
        raise ValueError(f"Unsafe BigQuery {label}: {value}")


def _parse_profile_ids(values: list[str] | None) -> list[str] | None:
    if not values:
        return None
    profile_ids = []
    for value in values:
        profile_ids.extend(item.strip() for item in value.split(",") if item.strip())
    return profile_ids or None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize LLM-ready player context packets.")
    parser.add_argument("--project", default=get_bigquery_project())
    parser.add_argument("--dataset", default=get_bigquery_dataset())
    parser.add_argument("--season", type=int)
    parser.add_argument("--week", type=int)
    parser.add_argument("--scoring-profile-id", action="append")
    parser.add_argument("--league-type-id", default=DEFAULT_LEAGUE_TYPE)
    parser.add_argument("--roster-format-id", default=DEFAULT_ROSTER_FORMAT)
    parser.add_argument("--model-run-id")
    parser.add_argument("--player-id-internal")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log-level", default=os.environ.get("LOG_LEVEL", "INFO"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    client = bigquery.Client(project=args.project)
    row_count = materialize_llm_packets(
        client,
        dataset_id=args.dataset,
        season=args.season,
        week=args.week,
        scoring_profile_ids=_parse_profile_ids(args.scoring_profile_id),
        league_type_id=args.league_type_id,
        roster_format_id=args.roster_format_id,
        model_run_id=args.model_run_id,
        player_id_internal=args.player_id_internal,
        dry_run=args.dry_run,
    )
    print(f"{OUTPUT_TABLE} rows materialized: {row_count}")


if __name__ == "__main__":
    main()
