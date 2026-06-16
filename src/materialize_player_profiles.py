"""Materialize the current player-profile compatibility mart."""

from __future__ import annotations

import argparse
import logging
import os
import re
from dataclasses import dataclass
from typing import Any

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.load import get_bigquery_project


logger = logging.getLogger(__name__)

DEFAULT_DATASET = "fantasy_football_brain"
OUTPUT_TABLE = "mart_player_profiles_current"
DEFAULT_PROFILE_IDS = ("standard", "half_ppr", "ppr")
OPTIONAL_SOURCE_TABLES = (
    "player_contracts",
    "depth_charts",
    "college_player_stats",
    "rookie_scouting_metrics",
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
    for table_name in OPTIONAL_SOURCE_TABLES:
        if table_exists(client, dataset_id, table_name):
            status[table_name] = SourceTableStatus(True, table_columns(client, dataset_id, table_name))
        else:
            status[table_name] = SourceTableStatus(False, frozenset())
    return status


def load_active_scoring_profile_ids(
    client: bigquery.Client,
    dataset_id: str,
    requested_profile_ids: list[str] | tuple[str, ...] | None = None,
) -> list[str]:
    if requested_profile_ids:
        return list(dict.fromkeys(requested_profile_ids))
    if not table_exists(client, dataset_id, "scoring_profiles"):
        return list(DEFAULT_PROFILE_IDS)
    sql = f"""
    SELECT scoring_profile_id
    FROM `{client.project}.{dataset_id}.scoring_profiles`
    WHERE COALESCE(active, TRUE)
    ORDER BY scoring_profile_id
    """
    rows = list(client.query(sql).result())
    profile_ids = [row.scoring_profile_id for row in rows]
    return profile_ids or list(DEFAULT_PROFILE_IDS)


def build_player_profiles_sql(
    *,
    project_id: str,
    dataset_id: str,
    source_status: dict[str, SourceTableStatus] | None = None,
) -> str:
    _validate_identifier(dataset_id, "dataset_id")
    source_status = source_status or {
        table_name: SourceTableStatus(False, frozenset())
        for table_name in OPTIONAL_SOURCE_TABLES
    }
    contract_cte = _contract_summary_cte(project_id, dataset_id, source_status["player_contracts"])
    depth_cte = _depth_chart_summary_cte(project_id, dataset_id, source_status["depth_charts"])
    college_cte = _college_summary_cte(project_id, dataset_id, source_status["college_player_stats"])
    rookie_cte = _rookie_scouting_summary_cte(project_id, dataset_id, source_status["rookie_scouting_metrics"])
    source_flags = {
        table_name: "TRUE" if status.exists else "FALSE"
        for table_name, status in source_status.items()
    }

    return f"""
CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.{OUTPUT_TABLE}`
PARTITION BY DATE(refreshed_at)
CLUSTER BY player_id_internal, position, current_team, scoring_profile_id AS
WITH selected_profiles AS (
    SELECT scoring_profile_id
    FROM UNNEST(@scoring_profile_ids) AS scoring_profile_id
),
latest_available AS (
    SELECT
        season,
        week
    FROM `{project_id}.{dataset_id}.analytics_player_fantasy_points_by_profile`
    WHERE scoring_profile_id IN UNNEST(@scoring_profile_ids)
        AND (@season IS NULL OR season = @season)
        AND (@week IS NULL OR week <= @week)
    ORDER BY season DESC, week DESC
    LIMIT 1
),
run_context AS (
    SELECT
        COALESCE(@season, latest_available.season) AS as_of_season,
        COALESCE(@week, latest_available.week) AS as_of_week,
        CURRENT_TIMESTAMP() AS refreshed_at
    FROM latest_available
),
identity AS (
    SELECT
        COALESCE(d.player_id_internal, b.player_id_internal) AS player_id_internal,
        COALESCE(d.gsis_id, b.gsis_id) AS gsis_id,
        COALESCE(d.sleeper_player_id, b.sleeper_player_id) AS sleeper_player_id,
        COALESCE(d.pfr_id, b.pfr_id) AS pfr_id,
        COALESCE(d.espn_id, b.espn_id) AS espn_id,
        COALESCE(d.yahoo_id, b.yahoo_id) AS yahoo_id,
        COALESCE(d.display_name, b.display_name) AS display_name,
        COALESCE(d.full_name, b.full_name) AS full_name,
        COALESCE(d.normalized_name, b.normalized_name) AS normalized_name,
        COALESCE(d.position, b.position) AS position,
        COALESCE(d.fantasy_positions, b.fantasy_positions) AS fantasy_positions,
        COALESCE(d.current_team, b.current_team) AS current_team,
        COALESCE(d.active_status, b.active_status) AS active_status,
        COALESCE(d.rookie_year, b.rookie_year) AS rookie_year,
        COALESCE(d.birth_date, b.birth_date) AS birth_date,
        d.age AS age,
        COALESCE(d.gsis_id, b.gsis_id, d.sleeper_player_id, b.sleeper_player_id, d.pfr_id, b.pfr_id, d.player_id_internal, b.player_id_internal) AS source_player_key,
        COALESCE(d.source_freshness_json, b.source_freshness_json) AS identity_source_freshness_json,
        COALESCE(d.missing_data_flags, b.missing_data_flags) AS identity_missing_data_flags
    FROM `{project_id}.{dataset_id}.dim_players_current` d
    FULL OUTER JOIN `{project_id}.{dataset_id}.player_identity_bridge` b
        ON d.player_id_internal = b.player_id_internal
    WHERE COALESCE(d.position, b.position) IN ('QB', 'RB', 'WR', 'TE')
),
scoring_seed AS (
    SELECT DISTINCT
        fp.player_id_internal,
        fp.source_player_key AS gsis_id,
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS STRING) AS pfr_id,
        CAST(NULL AS STRING) AS espn_id,
        CAST(NULL AS STRING) AS yahoo_id,
        fp.player_display_name AS display_name,
        fp.player_display_name AS full_name,
        REGEXP_REPLACE(
            REGEXP_REPLACE(LOWER(COALESCE(fp.player_display_name, '')), r'\\s+(jr|sr|ii|iii|iv|v)\\.?$', ''),
            r'[^a-z0-9]+',
            ''
        ) AS normalized_name,
        fp.position,
        CAST(NULL AS STRING) AS fantasy_positions,
        fp.team AS current_team,
        CAST(NULL AS STRING) AS active_status,
        CAST(NULL AS INT64) AS rookie_year,
        CAST(NULL AS DATE) AS birth_date,
        CAST(NULL AS FLOAT64) AS age,
        fp.source_player_key AS source_player_key,
        CAST(NULL AS STRING) AS identity_source_freshness_json,
        CAST(NULL AS STRING) AS identity_missing_data_flags
    FROM `{project_id}.{dataset_id}.analytics_player_fantasy_points_by_profile` fp
    JOIN run_context rc
        ON fp.season = rc.as_of_season
        AND fp.week <= rc.as_of_week
    WHERE fp.position IN ('QB', 'RB', 'WR', 'TE')
        AND fp.scoring_profile_id IN UNNEST(@scoring_profile_ids)
),
base_player_seed AS (
    SELECT * FROM identity
    UNION ALL
    SELECT ss.*
    FROM scoring_seed ss
    WHERE NOT EXISTS (
        SELECT 1
        FROM identity i
        WHERE ss.player_id_internal = i.player_id_internal
    )
    AND NOT EXISTS (
        SELECT 1
        FROM identity i
        WHERE ss.source_player_key = i.source_player_key
    )
    AND NOT EXISTS (
        SELECT 1
        FROM identity i
        WHERE ss.source_player_key = i.gsis_id
    )
    AND NOT EXISTS (
        SELECT 1
        FROM identity i
        WHERE ss.source_player_key = i.sleeper_player_id
    )
),
base_players AS (
    SELECT
        bps.*,
        sp.scoring_profile_id
    FROM base_player_seed bps
    CROSS JOIN selected_profiles sp
),
matched_scoring AS (
    SELECT
        COALESCE(bp.player_id_internal, bp.source_player_key) AS player_profile_key,
        bp.scoring_profile_id,
        fp.season,
        fp.week,
        fp.total_fantasy_points
    FROM base_players bp
    JOIN run_context rc ON TRUE
    JOIN `{project_id}.{dataset_id}.analytics_player_fantasy_points_by_profile` fp
        ON fp.scoring_profile_id = bp.scoring_profile_id
        AND (
            (bp.player_id_internal IS NOT NULL AND fp.player_id_internal = bp.player_id_internal)
            OR (bp.source_player_key IS NOT NULL AND fp.source_player_key = bp.source_player_key)
            OR (bp.gsis_id IS NOT NULL AND fp.source_player_key = bp.gsis_id)
            OR (bp.sleeper_player_id IS NOT NULL AND fp.source_player_key = bp.sleeper_player_id)
        )
        AND (
            fp.season < rc.as_of_season
            OR (fp.season = rc.as_of_season AND fp.week <= rc.as_of_week)
        )
),
current_scoring AS (
    SELECT
        player_profile_key,
        scoring_profile_id,
        SUM(total_fantasy_points) AS fantasy_points_current_season,
        AVG(total_fantasy_points) AS fantasy_points_per_game_current_season,
        COUNT(DISTINCT week) AS scored_games_current_season
    FROM matched_scoring
    JOIN run_context rc ON TRUE
    WHERE season = rc.as_of_season
    GROUP BY player_profile_key, scoring_profile_id
),
ranked_scoring AS (
    SELECT
        *,
        ROW_NUMBER() OVER(
            PARTITION BY player_profile_key, scoring_profile_id
            ORDER BY season DESC, week DESC
        ) AS rn
    FROM matched_scoring
),
rolling_scoring AS (
    SELECT
        player_profile_key,
        scoring_profile_id,
        SUM(IF(rn <= 3, total_fantasy_points, 0)) AS fantasy_points_last_3,
        SUM(IF(rn <= 5, total_fantasy_points, 0)) AS fantasy_points_last_5,
        SUM(IF(rn <= 8, total_fantasy_points, 0)) AS fantasy_points_last_8
    FROM ranked_scoring
    GROUP BY player_profile_key, scoring_profile_id
),
profile_totals AS (
    SELECT
        COALESCE(bp.player_id_internal, bp.source_player_key) AS player_profile_key,
        SUM(IF(fp.scoring_profile_id = 'standard', fp.total_fantasy_points, 0)) AS total_fantasy_points_standard,
        SUM(IF(fp.scoring_profile_id = 'half_ppr', fp.total_fantasy_points, 0)) AS total_fantasy_points_half_ppr,
        SUM(IF(fp.scoring_profile_id = 'ppr', fp.total_fantasy_points, 0)) AS total_fantasy_points_ppr
    FROM base_player_seed bp
    JOIN run_context rc ON TRUE
    LEFT JOIN `{project_id}.{dataset_id}.analytics_player_fantasy_points_by_profile` fp
        ON (
            (bp.player_id_internal IS NOT NULL AND fp.player_id_internal = bp.player_id_internal)
            OR (bp.source_player_key IS NOT NULL AND fp.source_player_key = bp.source_player_key)
            OR (bp.gsis_id IS NOT NULL AND fp.source_player_key = bp.gsis_id)
            OR (bp.sleeper_player_id IS NOT NULL AND fp.source_player_key = bp.sleeper_player_id)
        )
        AND fp.season = rc.as_of_season
        AND fp.week <= rc.as_of_week
    GROUP BY player_profile_key
),
matched_truth AS (
    SELECT
        COALESCE(bp.player_id_internal, bp.source_player_key) AS player_profile_key,
        t.season,
        t.week,
        t.fantasy_points_ppr,
        t.targets,
        t.receptions,
        t.carries,
        t.target_share,
        t.carry_share,
        t.receiving_air_yards,
        t.air_yards_share,
        t.red_zone_touches,
        t.offense_pct,
        t.passing_yards,
        t.passing_tds,
        t.rushing_yards,
        t.rushing_tds,
        t.receiving_yards,
        t.receiving_tds,
        t.passing_epa,
        t.rushing_epa,
        t.receiving_epa,
        t.total_epa,
        t.opportunity_score,
        t.efficiency_score,
        t.role_quality_score,
        t.role_fragility_score,
        t.wopr,
        t.analytical_grade
    FROM base_player_seed bp
    JOIN run_context rc ON TRUE
    JOIN `{project_id}.{dataset_id}.analytics_player_weekly_truth` t
        ON (
            (bp.source_player_key IS NOT NULL AND t.player_id = bp.source_player_key)
            OR (bp.gsis_id IS NOT NULL AND t.player_id = bp.gsis_id)
            OR (bp.player_id_internal IS NOT NULL AND t.player_id = bp.player_id_internal)
        )
        AND t.season_type = 'REG'
        AND (
            t.season < rc.as_of_season
            OR (t.season = rc.as_of_season AND t.week <= rc.as_of_week)
        )
),
truth_current AS (
    SELECT
        player_profile_key,
        COUNT(DISTINCT week) AS games_played_current_season,
        MAX(season) AS last_seen_season,
        MAX(week) AS last_seen_week,
        SAFE_DIVIDE(SUM(rushing_yards), NULLIF(SUM(carries), 0)) AS yards_per_carry_current_season,
        SAFE_DIVIDE(SUM(receiving_yards), NULLIF(SUM(targets), 0)) AS yards_per_target_current_season,
        SAFE_DIVIDE(SUM(receiving_yards), NULLIF(SUM(receptions), 0)) AS yards_per_reception_current_season,
        SAFE_DIVIDE(SUM(receptions), NULLIF(SUM(targets), 0)) AS catch_rate_current_season,
        SAFE_DIVIDE(
            SUM(COALESCE(passing_tds, 0) + COALESCE(rushing_tds, 0) + COALESCE(receiving_tds, 0)),
            NULLIF(SUM(COALESCE(targets, 0) + COALESCE(carries, 0)), 0)
        ) AS td_rate_current_season,
        AVG(passing_epa) AS avg_passing_epa,
        SUM(passing_epa) AS season_passing_epa,
        AVG(rushing_epa) AS avg_rushing_epa,
        SUM(rushing_epa) AS season_rushing_epa,
        AVG(receiving_epa) AS avg_receiving_epa,
        SUM(receiving_epa) AS season_receiving_epa,
        AVG(total_epa) AS avg_total_epa,
        SUM(total_epa) AS season_total_epa,
        AVG(opportunity_score) AS avg_opportunity_score,
        AVG(efficiency_score) AS avg_efficiency_score,
        AVG(role_quality_score) AS avg_role_quality_score,
        AVG(role_fragility_score) AS avg_role_fragility_score,
        AVG(wopr) AS avg_wopr,
        AVG(analytical_grade) AS avg_analytical_grade
    FROM matched_truth
    JOIN run_context rc ON TRUE
    WHERE season = rc.as_of_season
    GROUP BY player_profile_key
),
ranked_truth AS (
    SELECT
        *,
        ROW_NUMBER() OVER(PARTITION BY player_profile_key ORDER BY season DESC, week DESC) AS rn
    FROM matched_truth
),
truth_recent AS (
    SELECT
        player_profile_key,
        SUM(IF(rn <= 3, targets, 0)) AS targets_last_3,
        AVG(IF(rn <= 3, target_share, NULL)) AS target_share_last_3,
        SUM(IF(rn <= 3, carries, 0)) AS carries_last_3,
        AVG(IF(rn <= 3, carry_share, NULL)) AS rush_share_last_3,
        SUM(IF(rn <= 3, receptions, 0)) AS receptions_last_3,
        SUM(IF(rn <= 3, receiving_air_yards, 0)) AS air_yards_last_3,
        AVG(IF(rn <= 3, air_yards_share, NULL)) AS air_yard_share_last_3,
        SUM(IF(rn <= 3, red_zone_touches, 0)) AS red_zone_opportunities_last_3,
        SUM(IF(rn <= 3, COALESCE(receptions, 0) + COALESCE(red_zone_touches, 0), 0)) AS high_value_touches_last_3,
        AVG(IF(rn <= 3, offense_pct, NULL)) AS snap_share_last_3,
        AVG(IF(rn <= 3, wopr, NULL)) AS wopr_last_3,
        AVG(IF(rn <= 3, opportunity_score, NULL)) AS opportunity_score_last_3,
        AVG(IF(rn <= 3, efficiency_score, NULL)) AS efficiency_score_last_3,
        AVG(IF(rn <= 3, role_quality_score, NULL)) AS role_quality_score_last_3,
        AVG(IF(rn <= 3, role_fragility_score, NULL)) AS role_fragility_score_last_3
    FROM ranked_truth
    GROUP BY player_profile_key
),
rankings AS (
    SELECT *
    FROM (
        SELECT
            player_id,
            sleeper_player_id,
            player_name,
            position,
            current_team,
            model_run_id,
            ranking_version,
            rank AS pigskin_rank_position,
            tier AS pigskin_tier,
            ranking_score AS pigskin_projection,
            confidence_score AS pigskin_confidence,
            pigskin_verdict AS pigskin_summary,
            rank_rationale,
            TO_JSON_STRING(STRUCT(
                candidate_rank AS candidate_rank,
                raw_ranking_score AS raw_ranking_score,
                depth_chart_penalty AS depth_chart_penalty,
                rank_source AS rank_source,
                adjudicated_at AS adjudicated_at
            )) AS pigskin_movement_json,
            ROW_NUMBER() OVER(
                PARTITION BY COALESCE(player_id, sleeper_player_id, player_name), position
                ORDER BY generated_at DESC, rank ASC
            ) AS rn
        FROM `{project_id}.{dataset_id}.analytics_pigskin_rankings`
        WHERE COALESCE(is_active, TRUE)
    )
    WHERE rn = 1
),
{contract_cte},
{depth_cte},
{college_cte},
{rookie_cte}
SELECT
    bp.player_id_internal,
    bp.source_player_key,
    bp.sleeper_player_id,
    bp.gsis_id,
    bp.pfr_id,
    bp.espn_id,
    bp.yahoo_id,
    bp.display_name,
    bp.full_name,
    bp.normalized_name,
    bp.position,
    bp.fantasy_positions,
    bp.current_team,
    bp.active_status,
    bp.rookie_year,
    bp.birth_date,
    COALESCE(bp.age, SAFE_DIVIDE(DATE_DIFF(CURRENT_DATE(), bp.birth_date, DAY), 365.25)) AS age,
    rc.as_of_season,
    rc.as_of_week,
    bp.scoring_profile_id,
    CAST(NULL AS STRING) AS league_type_id,
    CAST(NULL AS STRING) AS roster_format_id,
    tc.last_seen_season,
    tc.last_seen_week,
    tc.games_played_current_season,
    CAST(NULL AS INT64) AS bye_week,
    cs.fantasy_points_current_season,
    cs.fantasy_points_per_game_current_season,
    rs.fantasy_points_last_3,
    rs.fantasy_points_last_5,
    rs.fantasy_points_last_8,
    pt.total_fantasy_points_standard,
    pt.total_fantasy_points_half_ppr,
    pt.total_fantasy_points_ppr,
    RANK() OVER(
        PARTITION BY bp.scoring_profile_id, bp.position
        ORDER BY COALESCE(cs.fantasy_points_current_season, -999999) DESC
    ) AS position_rank_by_profile,
    RANK() OVER(
        PARTITION BY bp.scoring_profile_id
        ORDER BY COALESCE(cs.fantasy_points_current_season, -999999) DESC
    ) AS overall_rank_by_profile,
    CAST(NULL AS FLOAT64) AS snaps_last_3,
    tr.snap_share_last_3,
    tr.targets_last_3,
    tr.target_share_last_3,
    tr.carries_last_3,
    tr.rush_share_last_3,
    tr.receptions_last_3,
    tr.air_yards_last_3,
    tr.air_yard_share_last_3,
    tr.red_zone_opportunities_last_3,
    tr.high_value_touches_last_3,
    TO_JSON_STRING(STRUCT(
        tr.wopr_last_3 AS wopr_last_3,
        tr.opportunity_score_last_3 AS opportunity_score_last_3,
        tr.efficiency_score_last_3 AS efficiency_score_last_3,
        tr.role_quality_score_last_3 AS role_quality_score_last_3,
        tr.role_fragility_score_last_3 AS role_fragility_score_last_3,
        tc.avg_wopr AS current_season_wopr,
        tc.avg_role_quality_score AS current_season_role_quality,
        tc.avg_role_fragility_score AS current_season_role_fragility
    )) AS role_summary_json,
    tc.yards_per_carry_current_season,
    tc.yards_per_target_current_season,
    tc.yards_per_reception_current_season,
    tc.catch_rate_current_season,
    tc.td_rate_current_season,
    TO_JSON_STRING(STRUCT(
        tc.avg_passing_epa AS avg_passing_epa,
        tc.season_passing_epa AS season_passing_epa,
        tc.avg_rushing_epa AS avg_rushing_epa,
        tc.season_rushing_epa AS season_rushing_epa,
        tc.avg_receiving_epa AS avg_receiving_epa,
        tc.season_receiving_epa AS season_receiving_epa,
        tc.avg_total_epa AS avg_total_epa,
        tc.season_total_epa AS season_total_epa
    )) AS epa_summary_json,
    TO_JSON_STRING(STRUCT(
        tc.avg_opportunity_score AS avg_opportunity_score,
        tc.avg_efficiency_score AS avg_efficiency_score,
        tc.avg_analytical_grade AS avg_analytical_grade
    )) AS efficiency_summary_json,
    r.model_run_id,
    r.ranking_version,
    CAST(NULL AS INT64) AS pigskin_rank_overall,
    r.pigskin_rank_position,
    r.pigskin_tier,
    r.pigskin_projection,
    r.pigskin_confidence,
    COALESCE(r.pigskin_summary, r.rank_rationale) AS pigskin_summary,
    r.pigskin_movement_json,
    c.contract_summary_json,
    d.depth_chart_summary_json,
    col.college_summary_json,
    rook.rookie_scouting_summary_json,
    CASE
        WHEN col.college_summary_json IS NULL AND rook.rookie_scouting_summary_json IS NULL THEN NULL
        ELSE TO_JSON_STRING(STRUCT(
            col.college_summary_json AS college_summary_json,
            rook.rookie_scouting_summary_json AS rookie_scouting_summary_json
        ))
    END AS prospect_summary_json,
    TO_JSON_STRING(STRUCT(
        'mart_player_profiles_current' AS mart,
        'dim_players_current' AS identity_dimension,
        'player_identity_bridge' AS identity_bridge,
        'analytics_player_weekly_truth' AS weekly_evidence,
        'analytics_player_fantasy_points_by_profile' AS scoring_source,
        'analytics_pigskin_rankings' AS ranking_source,
        {source_flags["player_contracts"]} AS player_contracts_available,
        {source_flags["depth_charts"]} AS depth_charts_available,
        {source_flags["college_player_stats"]} AS college_player_stats_available,
        {source_flags["rookie_scouting_metrics"]} AS rookie_scouting_metrics_available,
        rc.as_of_season AS as_of_season,
        rc.as_of_week AS as_of_week,
        rc.refreshed_at AS refreshed_at
    )) AS source_freshness_json,
    TO_JSON_STRING(ARRAY(
        SELECT DISTINCT flag
        FROM UNNEST(ARRAY_CONCAT(
            IF(bp.player_id_internal IS NULL, ['missing_player_id_internal'], []),
            IF(bp.source_player_key IS NULL, ['missing_source_player_key'], []),
            IF(bp.sleeper_player_id IS NULL, ['missing_sleeper_player_id'], []),
            IF(bp.gsis_id IS NULL, ['missing_gsis_id'], []),
            IF(cs.fantasy_points_current_season IS NULL, ['missing_current_season_scoring'], []),
            IF(tc.games_played_current_season IS NULL, ['missing_weekly_truth'], []),
            IF(r.ranking_version IS NULL, ['missing_pigskin_rank'], []),
            IF(c.contract_summary_json IS NULL, ['missing_contract_summary'], []),
            IF(d.depth_chart_summary_json IS NULL, ['missing_depth_chart_summary'], []),
            IF(col.college_summary_json IS NULL, ['missing_college_summary'], []),
            IF(rook.rookie_scouting_summary_json IS NULL, ['missing_rookie_scouting_summary'], []),
            IF({source_flags["player_contracts"]}, [], ['missing_player_contracts_source']),
            IF({source_flags["depth_charts"]}, [], ['missing_depth_charts_source']),
            IF({source_flags["college_player_stats"]}, ['temporary_name_join_college_summary'], ['missing_college_player_stats_source']),
            IF({source_flags["rookie_scouting_metrics"]}, ['temporary_name_join_rookie_scouting_summary'], ['missing_rookie_scouting_metrics_source']),
            ['missing_bye_week', 'missing_snaps_last_3']
        )) AS flag
        WHERE flag IS NOT NULL
        ORDER BY flag
    )) AS missing_data_flags,
    rc.refreshed_at AS created_at,
    rc.refreshed_at AS refreshed_at
FROM base_players bp
JOIN run_context rc ON TRUE
LEFT JOIN current_scoring cs
    ON COALESCE(bp.player_id_internal, bp.source_player_key) = cs.player_profile_key
    AND bp.scoring_profile_id = cs.scoring_profile_id
LEFT JOIN rolling_scoring rs
    ON COALESCE(bp.player_id_internal, bp.source_player_key) = rs.player_profile_key
    AND bp.scoring_profile_id = rs.scoring_profile_id
LEFT JOIN profile_totals pt
    ON COALESCE(bp.player_id_internal, bp.source_player_key) = pt.player_profile_key
LEFT JOIN truth_current tc
    ON COALESCE(bp.player_id_internal, bp.source_player_key) = tc.player_profile_key
LEFT JOIN truth_recent tr
    ON COALESCE(bp.player_id_internal, bp.source_player_key) = tr.player_profile_key
LEFT JOIN rankings r
    ON (
        bp.gsis_id IS NOT NULL
        AND r.player_id = bp.gsis_id
        AND r.position = bp.position
    )
    OR (
        bp.sleeper_player_id IS NOT NULL
        AND r.sleeper_player_id = bp.sleeper_player_id
        AND r.position = bp.position
    )
LEFT JOIN contract_summary c
    ON bp.player_id_internal = c.player_id_internal
LEFT JOIN depth_chart_summary d
    ON bp.player_id_internal = d.player_id_internal
LEFT JOIN college_summary col
    ON bp.player_id_internal = col.player_id_internal
LEFT JOIN rookie_scouting_summary rook
    ON bp.player_id_internal = rook.player_id_internal
WHERE bp.position IN ('QB', 'RB', 'WR', 'TE')
    AND COALESCE(bp.display_name, bp.full_name, bp.source_player_key) IS NOT NULL
"""


def materialize_player_profiles(
    client: bigquery.Client,
    *,
    dataset_id: str = DEFAULT_DATASET,
    season: int | None = None,
    week: int | None = None,
    scoring_profile_ids: list[str] | tuple[str, ...] | None = None,
    dry_run: bool = False,
) -> int:
    profile_ids = load_active_scoring_profile_ids(client, dataset_id, scoring_profile_ids)
    source_status = inspect_source_status(client, dataset_id)
    missing_sources = [name for name, status in source_status.items() if not status.exists]
    if missing_sources:
        logger.warning("Optional profile sources missing: %s", ", ".join(sorted(missing_sources)))
    sql = build_player_profiles_sql(
        project_id=client.project,
        dataset_id=dataset_id,
        source_status=source_status,
    )
    job_config = bigquery.QueryJobConfig(
        dry_run=dry_run,
        use_query_cache=False,
        query_parameters=[
            bigquery.ArrayQueryParameter("scoring_profile_ids", "STRING", profile_ids),
            bigquery.ScalarQueryParameter("season", "INT64", season),
            bigquery.ScalarQueryParameter("week", "INT64", week),
        ],
    )
    job = client.query(sql, job_config=job_config)
    if dry_run:
        logger.info("Dry run bytes processed: %s", job.total_bytes_processed)
        return 0
    job.result()
    row_count = _count_output_rows(client, dataset_id)
    logger.info(
        "Materialized %s rows in %s.%s.%s for profiles %s",
        row_count,
        client.project,
        dataset_id,
        OUTPUT_TABLE,
        ",".join(profile_ids),
    )
    return row_count


def _count_output_rows(client: bigquery.Client, dataset_id: str) -> int:
    sql = f"SELECT COUNT(*) AS row_count FROM `{client.project}.{dataset_id}.{OUTPUT_TABLE}`"
    rows = list(client.query(sql).result())
    return int(rows[0].row_count) if rows else 0


def _contract_summary_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists or "gsis_id" not in status.columns:
        return _empty_summary_cte("contract_summary", "contract_summary_json")
    where_sql = "WHERE COALESCE(c.is_active, TRUE)" if "is_active" in status.columns else ""
    return f"""
contract_summary AS (
    SELECT
        id.player_id_internal,
        TO_JSON_STRING(STRUCT(
            {_any_value_expr("c", status.columns, "value", "contract_value", "FLOAT64")},
            {_any_value_expr("c", status.columns, "apy", "contract_apy", "FLOAT64")},
            {_any_value_expr("c", status.columns, "guaranteed", "contract_guaranteed", "FLOAT64")},
            {_any_value_expr("c", status.columns, "year_signed", "contract_year_signed", "INT64")}
        )) AS contract_summary_json
    FROM `{project_id}.{dataset_id}.player_contracts` c
    JOIN identity id
        ON c.gsis_id = id.gsis_id
    {where_sql}
    GROUP BY id.player_id_internal
)"""


def _depth_chart_summary_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists or "gsis_id" not in status.columns:
        return _empty_summary_cte("depth_chart_summary", "depth_chart_summary_json")
    return f"""
depth_chart_summary AS (
    SELECT
        id.player_id_internal,
        TO_JSON_STRING(ARRAY_AGG(STRUCT(
            {_plain_expr("d", status.columns, "pos_abb", "depth_position", "STRING")},
            {_plain_expr("d", status.columns, "pos_rank", "depth_rank", "INT64")},
            {_plain_expr("d", status.columns, "team", "team", "STRING")},
            {_plain_expr("d", status.columns, "dt", "depth_date", "STRING")}
        ) LIMIT 3)) AS depth_chart_summary_json
    FROM `{project_id}.{dataset_id}.depth_charts` d
    JOIN identity id
        ON d.gsis_id = id.gsis_id
    GROUP BY id.player_id_internal
)"""


def _college_summary_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists or "player_name" not in status.columns:
        return _empty_summary_cte("college_summary", "college_summary_json")
    name_key = _normalized_name_sql("c.player_name")
    return f"""
college_summary AS (
    SELECT
        id.player_id_internal,
        TO_JSON_STRING(STRUCT(
            {_any_value_expr("c", status.columns, "team", "college_team", "STRING")},
            {_any_value_expr("c", status.columns, "conference", "college_conference", "STRING")},
            {_any_value_expr("c", status.columns, "games", "college_games", "FLOAT64")},
            {_any_value_expr("c", status.columns, "passing_yards", "college_passing_yards", "FLOAT64")},
            {_any_value_expr("c", status.columns, "passing_tds", "college_passing_tds", "FLOAT64")},
            {_any_value_expr("c", status.columns, "rushing_yards", "college_rushing_yards", "FLOAT64")},
            {_any_value_expr("c", status.columns, "rushing_tds", "college_rushing_tds", "FLOAT64")},
            {_any_value_expr("c", status.columns, "receptions", "college_receptions", "FLOAT64")},
            {_any_value_expr("c", status.columns, "receiving_yards", "college_receiving_yards", "FLOAT64")},
            {_any_value_expr("c", status.columns, "receiving_tds", "college_receiving_tds", "FLOAT64")}
        )) AS college_summary_json
    FROM `{project_id}.{dataset_id}.college_player_stats` c
    JOIN identity id
        ON {name_key} = id.normalized_name
    GROUP BY id.player_id_internal
)"""


def _rookie_scouting_summary_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists or "player_name" not in status.columns:
        return _empty_summary_cte("rookie_scouting_summary", "rookie_scouting_summary_json")
    name_key = _normalized_name_sql("r.player_name")
    return f"""
rookie_scouting_summary AS (
    SELECT
        id.player_id_internal,
        TO_JSON_STRING(STRUCT(
            {_any_value_expr("r", status.columns, "yards_after_contact_per_attempt", "yards_after_contact_per_attempt", "FLOAT64")},
            {_any_value_expr("r", status.columns, "yards_per_route_run", "yards_per_route_run", "FLOAT64")},
            {_any_value_expr("r", status.columns, "college_target_share", "college_target_share", "FLOAT64")},
            {_any_value_expr("r", status.columns, "catch_radius_grade", "catch_radius_grade", "FLOAT64")},
            {_any_value_expr("r", status.columns, "success_rate_vs_man", "success_rate_vs_man", "FLOAT64")},
            {_any_value_expr("r", status.columns, "success_rate_vs_zone", "success_rate_vs_zone", "FLOAT64")},
            {_any_value_expr("r", status.columns, "success_rate_vs_press", "success_rate_vs_press", "FLOAT64")},
            {_any_value_expr("r", status.columns, "avg_separation_inches", "avg_separation_inches", "FLOAT64")},
            {_any_value_expr("r", status.columns, "data_source", "scouting_source", "STRING")}
        )) AS rookie_scouting_summary_json
    FROM `{project_id}.{dataset_id}.rookie_scouting_metrics` r
    JOIN identity id
        ON {name_key} = id.normalized_name
    GROUP BY id.player_id_internal
)"""


def _empty_summary_cte(cte_name: str, json_column: str) -> str:
    return f"""
{cte_name} AS (
    SELECT
        CAST(NULL AS STRING) AS player_id_internal,
        CAST(NULL AS STRING) AS {json_column}
    WHERE FALSE
)"""


def _any_value_expr(alias: str, columns: frozenset[str], source: str, output: str, type_name: str) -> str:
    if source in columns:
        return f"ANY_VALUE(CAST({alias}.{source} AS {type_name})) AS {output}"
    return f"CAST(NULL AS {type_name}) AS {output}"


def _plain_expr(alias: str, columns: frozenset[str], source: str, output: str, type_name: str) -> str:
    if source in columns:
        return f"CAST({alias}.{source} AS {type_name}) AS {output}"
    return f"CAST(NULL AS {type_name}) AS {output}"


def _normalized_name_sql(expr: str) -> str:
    return (
        "REGEXP_REPLACE("
        f"REGEXP_REPLACE(LOWER(COALESCE({expr}, '')), r'\\s+(jr|sr|ii|iii|iv|v)\\.?$', ''), "
        "r'[^a-z0-9]+', '')"
    )


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
    parser = argparse.ArgumentParser(description="Materialize current player profile mart.")
    parser.add_argument("--project", default=get_bigquery_project())
    parser.add_argument("--dataset", default=get_bigquery_dataset())
    parser.add_argument("--season", type=int)
    parser.add_argument("--week", type=int)
    parser.add_argument("--scoring-profile-id", action="append")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log-level", default=os.environ.get("LOG_LEVEL", "INFO"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    client = bigquery.Client(project=args.project)
    row_count = materialize_player_profiles(
        client,
        dataset_id=args.dataset,
        season=args.season,
        week=args.week,
        scoring_profile_ids=_parse_profile_ids(args.scoring_profile_id),
        dry_run=args.dry_run,
    )
    print(f"{OUTPUT_TABLE} rows materialized: {row_count}")


if __name__ == "__main__":
    main()
