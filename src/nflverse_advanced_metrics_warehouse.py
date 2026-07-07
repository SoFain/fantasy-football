#!/usr/bin/env python
"""Pipeline for the player-year advanced metrics warehouse."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_PROJECT = "fantasy-football-498121"
DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_METRIC_VERSION = "advanced_player_metrics_v0"


def _table(project: str, dataset: str, table_name: str) -> str:
    return f"`{project}.{dataset}.{table_name}`"


def _scalar_param(name: str, type_: str, value: Any) -> Any:
    from google.cloud import bigquery
    return bigquery.ScalarQueryParameter(name, type_, value)


def _query_job_config(params: list[Any]) -> Any:
    from google.cloud import bigquery
    return bigquery.QueryJobConfig(query_parameters=params)


def build_weekly_advanced_metrics_sql(project: str, dataset: str) -> str:
    return f"""
WITH goal_line_targets_cte AS (
  SELECT season, week, player_id_internal, team, COUNT(1) AS goal_line_targets
  FROM {_table(project, dataset, "stg_play_player_events")}
  WHERE event_type = 'target' AND yardline_100 <= 5
  GROUP BY 1, 2, 3, 4
),
weekly_source AS (
  SELECT
    @metric_version AS metric_version,
    CONCAT(@metric_version, '_', CAST(pws.season AS STRING)) AS feature_run_id,
    pws.season,
    pws.week,
    COALESCE(JSON_VALUE(raw.raw_payload_json, '$.season_type'), IF(pws.week >= 19, 'POST', 'REG')) AS season_type,
    pws.player_id_internal,
    pws.gsis_id,
    pws.player_name,
    pws.position,
    JSON_VALUE(raw.raw_payload_json, '$.position_group') AS position_group,
    pws.team,
    1 AS games,
    pws.targets,
    pws.receptions,
    pws.carries,
    CAST(JSON_VALUE(raw.raw_payload_json, '$.attempts') AS FLOAT64) AS attempts,
    COALESCE(CAST(JSON_VALUE(raw.raw_payload_json, '$.attempts') AS FLOAT64), 0) + COALESCE(CAST(JSON_VALUE(raw.raw_payload_json, '$.sacks') AS FLOAT64), 0) AS dropbacks,
    CAST(NULL AS FLOAT64) AS routes_run,
    CAST(NULL AS FLOAT64) AS pass_play_snaps,
    part.offense_snaps AS offensive_snaps,
    GREATEST(0.0, pws.receiving_yards) AS receiving_yards,
    COALESCE(pws.air_yards, opp.air_yards) AS receiving_air_yards,
    CAST(JSON_VALUE(raw.raw_payload_json, '$.receiving_yards_after_catch') AS FLOAT64) AS receiving_yards_after_catch,
    CAST(JSON_VALUE(raw.raw_payload_json, '$.receiving_epa') AS FLOAT64) AS receiving_epa,
    SAFE_DIVIDE(CAST(JSON_VALUE(raw.raw_payload_json, '$.receiving_epa') AS FLOAT64), NULLIF(pws.targets, 0)) AS receiving_epa_per_target,
    CAST(JSON_VALUE(raw.raw_payload_json, '$.receiving_first_downs') AS FLOAT64) AS receiving_first_downs,
    SAFE_DIVIDE(CAST(JSON_VALUE(raw.raw_payload_json, '$.receiving_first_downs') AS FLOAT64), NULLIF(pws.targets, 0)) AS receiving_first_down_rate,
    COALESCE(opp.target_share, SAFE_DIVIDE(pws.targets, NULLIF(opp.team_targets, 0))) AS target_share,
    COALESCE(opp.air_yards_share, SAFE_DIVIDE(pws.air_yards, NULLIF(opp.team_air_yards, 0))) AS air_yards_share,
    1.5 * COALESCE(opp.target_share, SAFE_DIVIDE(pws.targets, NULLIF(opp.team_targets, 0))) + 0.7 * COALESCE(opp.air_yards_share, SAFE_DIVIDE(pws.air_yards, NULLIF(opp.team_air_yards, 0))) AS wopr,
    SAFE_DIVIDE(pws.receiving_yards, NULLIF(COALESCE(pws.air_yards, opp.air_yards), 0)) AS racr,
    SAFE_DIVIDE(COALESCE(pws.air_yards, opp.air_yards), NULLIF(pws.targets, 0)) AS adot,
    opp.red_zone_targets,
    CAST(glt.goal_line_targets AS FLOAT64) AS goal_line_targets,
    CAST(NULL AS FLOAT64) AS end_zone_targets,
    CAST(NULL AS FLOAT64) AS yprr,
    CAST(NULL AS FLOAT64) AS tprr,
    CAST(NULL AS FLOAT64) AS receiving_first_downs_per_route,
    CAST(NULL AS FLOAT64) AS route_participation_rate,
    pws.rushing_yards,
    CAST(JSON_VALUE(raw.raw_payload_json, '$.rushing_epa') AS FLOAT64) AS rushing_epa,
    SAFE_DIVIDE(CAST(JSON_VALUE(raw.raw_payload_json, '$.rushing_epa') AS FLOAT64), NULLIF(pws.carries, 0)) AS rushing_epa_per_carry,
    CAST(JSON_VALUE(raw.raw_payload_json, '$.rushing_first_downs') AS FLOAT64) AS rushing_first_downs,
    SAFE_DIVIDE(CAST(JSON_VALUE(raw.raw_payload_json, '$.rushing_first_downs') AS FLOAT64), NULLIF(pws.carries, 0)) AS rushing_first_down_rate,
    opp.red_zone_carries,
    opp.inside_5_carries AS goal_line_carries,
    COALESCE(opp.red_zone_targets, 0) + COALESCE(opp.red_zone_carries, 0) AS red_zone_opportunities,
    COALESCE(glt.goal_line_targets, 0) + COALESCE(opp.inside_5_carries, 0) AS goal_line_opportunities,
    -- Weighted Opportunity calculations
    (COALESCE(opp.red_zone_targets, 0) * 1.47) + ((COALESCE(pws.targets, 0) - COALESCE(opp.red_zone_targets, 0)) * 0.67) + (COALESCE(opp.red_zone_carries, 0) * 1.28) + ((COALESCE(pws.carries, 0) - COALESCE(opp.red_zone_carries, 0)) * 0.47) AS weighted_opportunity_standard,
    (COALESCE(opp.red_zone_targets, 0) * 1.93) + ((COALESCE(pws.targets, 0) - COALESCE(opp.red_zone_targets, 0)) * 1.00) + (COALESCE(opp.red_zone_carries, 0) * 1.28) + ((COALESCE(pws.carries, 0) - COALESCE(opp.red_zone_carries, 0)) * 0.47) AS weighted_opportunity_half_ppr,
    (COALESCE(opp.red_zone_targets, 0) * 2.39) + ((COALESCE(pws.targets, 0) - COALESCE(opp.red_zone_targets, 0)) * 1.54) + (COALESCE(opp.red_zone_carries, 0) * 1.28) + ((COALESCE(pws.carries, 0) - COALESCE(opp.red_zone_carries, 0)) * 0.47) AS weighted_opportunity_ppr,
    (COALESCE(opp.red_zone_targets, 0) * 1.56) + ((COALESCE(pws.targets, 0) - COALESCE(opp.red_zone_targets, 0)) * 0.74) + (COALESCE(opp.red_zone_carries, 0) * 1.28) + ((COALESCE(pws.carries, 0) - COALESCE(opp.red_zone_carries, 0)) * 0.47) AS weighted_opportunity_gng_keeper,
    pws.passing_yards,
    CAST(JSON_VALUE(raw.raw_payload_json, '$.passing_epa') AS FLOAT64) AS passing_epa,
    SAFE_DIVIDE(CAST(JSON_VALUE(raw.raw_payload_json, '$.passing_epa') AS FLOAT64), NULLIF(CAST(JSON_VALUE(raw.raw_payload_json, '$.attempts') AS FLOAT64), 0)) AS passing_epa_per_attempt,
    SAFE_DIVIDE(CAST(JSON_VALUE(raw.raw_payload_json, '$.passing_epa') AS FLOAT64), NULLIF(COALESCE(CAST(JSON_VALUE(raw.raw_payload_json, '$.attempts') AS FLOAT64), 0) + COALESCE(CAST(JSON_VALUE(raw.raw_payload_json, '$.sacks') AS FLOAT64), 0), 0)) AS passing_epa_per_dropback,
    CAST(JSON_VALUE(raw.raw_payload_json, '$.passing_cpoe') AS FLOAT64) AS passing_cpoe,
    CAST(NULL AS FLOAT64) AS dakota,
    CAST(JSON_VALUE(raw.raw_payload_json, '$.passing_first_downs') AS FLOAT64) AS passing_first_downs,
    SAFE_DIVIDE(CAST(JSON_VALUE(raw.raw_payload_json, '$.passing_first_downs') AS FLOAT64), NULLIF(CAST(JSON_VALUE(raw.raw_payload_json, '$.attempts') AS FLOAT64), 0)) AS passing_first_down_rate,
    opp.qb_rushing_leverage_index AS qb_rushing_baseline_score,
    ngs.ngs_avg_separation,
    ngs.ngs_avg_cushion,
    ngs.ngs_yac_over_expected AS ngs_yac_above_expectation,
    ngs.ngs_efficiency AS ngs_rushing_efficiency,
    ngs.ngs_rush_yards_over_expected,
    ngs.ngs_rush_yards_over_expected_per_attempt AS ngs_rush_yards_over_expected_per_att,
    ngs.ngs_percent_attempts_gte_8_defenders AS ngs_box_count_rate,
    ngs.ngs_avg_time_to_throw AS ngs_qb_time_to_throw,
    ngs.ngs_aggressiveness AS ngs_qb_aggressiveness,
    ngs.ngs_cpoe AS ngs_qb_cpoe,
    part.offense_pct AS offensive_snap_share,
    role.depth_chart_role_score AS snap_role_stability,
    role.injury_risk_score AS availability_score,
    CAST(role.injury_report_count AS FLOAT64) AS injury_status_score,
    role.injury_risk_score AS injury_burden_score,
    CAST(role.out_status_count AS FLOAT64) AS missed_time_risk_score,
    'BLOCKED' AS route_metrics_source_status,
    IF(pws.season >= 2016, 'AVAILABLE', 'UNAVAILABLE') AS ngs_source_status,
    'AVAILABLE' AS participation_source_status,
    'UNAVAILABLE' AS contract_source_status,
    'UNAVAILABLE' AS pressure_coverage_source_status,
    -- JSON flags/freshness
    TO_JSON_STRING(STRUCT(
      pws.source_freshness_json AS core_stats_source,
      raw.loaded_at AS raw_loaded_at,
      part.source_freshness_json AS snap_source,
      ngs.created_at AS ngs_source_updated
    )) AS source_coverage_json,
    TO_JSON_STRING(STRUCT(
      (raw.player_id IS NULL) AS missing_raw_payload,
      (part.player_id_internal IS NULL) AS missing_participation,
      (ngs.player_id_internal IS NULL AND pws.season >= 2016) AS missing_ngs,
      (role.player_id_internal IS NULL) AS missing_injury_role
    )) AS missing_flags_json,
    TO_JSON_STRING(STRUCT(
      FALSE AS using_proxy_routes,
      FALSE AS using_proxy_pressures
    )) AS proxy_flags_json,
    TO_JSON_STRING(STRUCT(
      TRUE AS routes_run_blocked,
      TRUE AS yprr_blocked,
      TRUE AS tprr_blocked,
      TRUE AS pressure_epa_blocked,
      TRUE AS covered_receiver_epa_blocked
    )) AS blocked_flags_json,
    CURRENT_TIMESTAMP() AS generated_at
  FROM {_table(project, dataset, "stg_player_week_stats")} pws
  LEFT JOIN {_table(project, dataset, "raw_nflverse_weekly")} raw
    ON pws.season = raw.season
    AND pws.week = raw.week
    AND (pws.nflverse_player_id = raw.player_id OR pws.gsis_id = raw.player_id)
  LEFT JOIN {_table(project, dataset, "stg_participation_context")} part
    ON pws.season = part.season
    AND pws.week = part.week
    AND pws.player_id_internal = part.player_id_internal
  LEFT JOIN {_table(project, dataset, "player_week_opportunity_metrics")} opp
    ON pws.season = opp.season
    AND pws.week = opp.week
    AND pws.player_id_internal = opp.player_id_internal
  LEFT JOIN {_table(project, dataset, "player_week_ngs_metrics")} ngs
    ON pws.season = ngs.season
    AND pws.week = ngs.week
    AND pws.player_id_internal = ngs.player_id_internal
  LEFT JOIN {_table(project, dataset, "player_week_role_context_metrics")} role
    ON pws.season = role.season
    AND pws.week = role.week
    AND pws.player_id_internal = role.player_id_internal
  LEFT JOIN goal_line_targets_cte glt
    ON pws.season = glt.season
    AND pws.week = glt.week
    AND pws.player_id_internal = glt.player_id_internal
  WHERE pws.season BETWEEN @season_start AND @season_end
)
SELECT * FROM weekly_source
"""


def build_season_advanced_metrics_sql(project: str, dataset: str) -> str:
    # Aggregates weekly metrics into seasonal metrics, grouping by season and season_type (REG/POST)
    return f"""
WITH weekly AS (
  SELECT *
  FROM {_table(project, dataset, "player_week_advanced_metrics")}
  WHERE season BETWEEN @season_start AND @season_end
    AND metric_version = @metric_version
),
team_totals AS (
  SELECT
    season,
    week,
    team,
    team_targets,
    team_air_yards,
    rush_attempts
  FROM {_table(project, dataset, "player_week_opportunity_metrics")}
  GROUP BY 1, 2, 3, 4, 5, 6
),
season_team_totals AS (
  -- Sum team totals over the season for active weeks of multi-team players
  SELECT
    w.season,
    w.season_type,
    w.player_id_internal,
    SUM(t.team_targets) AS season_team_targets,
    SUM(t.team_air_yards) AS season_team_air_yards,
    SUM(t.rush_attempts) AS season_team_rush_attempts
  FROM weekly w
  LEFT JOIN team_totals t
    ON w.season = t.season
    AND w.week = t.week
    AND w.team = t.team
  GROUP BY 1, 2, 3
),
season_base AS (
  SELECT
    w.metric_version,
    CURRENT_TIMESTAMP() AS generated_at,
    w.season,
    w.season_type,
    w.player_id_internal,
    ANY_VALUE(w.gsis_id) AS gsis_id,
    ANY_VALUE(w.player_name) AS player_name,
    w.position,
    ANY_VALUE(w.position_group) AS position_group,
    -- Handle traded players: show the team they played for in the latest week of the season
    ARRAY_AGG(w.team ORDER BY w.week DESC LIMIT 1)[OFFSET(0)] AS team,
    TO_JSON_STRING(ARRAY_AGG(DISTINCT w.team ORDER BY w.team)) AS teams_json,
    SUM(w.games) AS games,
    SUM(w.targets) AS targets,
    SUM(w.receptions) AS receptions,
    SUM(w.carries) AS carries,
    SUM(w.attempts) AS attempts,
    SUM(w.dropbacks) AS dropbacks,
    CAST(NULL AS FLOAT64) AS routes_run,
    CAST(NULL AS FLOAT64) AS pass_play_snaps,
    SUM(w.offensive_snaps) AS offensive_snaps,
    SUM(w.receiving_yards) AS receiving_yards,
    SUM(w.receiving_air_yards) AS receiving_air_yards,
    SUM(w.receiving_yards_after_catch) AS receiving_yards_after_catch,
    SUM(w.receiving_epa) AS receiving_epa,
    SUM(w.receiving_first_downs) AS receiving_first_downs,
    SUM(w.red_zone_targets) AS red_zone_targets,
    SUM(w.goal_line_targets) AS goal_line_targets,
    CAST(NULL AS FLOAT64) AS end_zone_targets,
    CAST(NULL AS FLOAT64) AS yprr,
    CAST(NULL AS FLOAT64) AS tprr,
    CAST(NULL AS FLOAT64) AS receiving_first_downs_per_route,
    CAST(NULL AS FLOAT64) AS route_participation_rate,
    SUM(w.rushing_yards) AS rushing_yards,
    SUM(w.rushing_epa) AS rushing_epa,
    SUM(w.rushing_first_downs) AS rushing_first_downs,
    SUM(w.red_zone_carries) AS red_zone_carries,
    SUM(w.goal_line_carries) AS goal_line_carries,
    SUM(w.red_zone_opportunities) AS red_zone_opportunities,
    SUM(w.goal_line_opportunities) AS goal_line_opportunities,
    SUM(w.passing_yards) AS passing_yards,
    SUM(w.passing_epa) AS passing_epa,
    SUM(w.passing_first_downs) AS passing_first_downs,
    AVG(w.passing_cpoe) AS passing_cpoe,
    CAST(NULL AS FLOAT64) AS dakota,
    AVG(w.qb_rushing_baseline_score) AS qb_rushing_baseline_score,
    AVG(w.ngs_avg_separation) AS ngs_avg_separation,
    AVG(w.ngs_avg_cushion) AS ngs_avg_cushion,
    AVG(w.ngs_yac_above_expectation) AS ngs_yac_above_expectation,
    AVG(w.ngs_rushing_efficiency) AS ngs_rushing_efficiency,
    AVG(w.ngs_rush_yards_over_expected) AS ngs_rush_yards_over_expected,
    AVG(w.ngs_rush_yards_over_expected_per_att) AS ngs_rush_yards_over_expected_per_att,
    AVG(w.ngs_box_count_rate) AS ngs_box_count_rate,
    AVG(w.ngs_qb_time_to_throw) AS ngs_qb_time_to_throw,
    AVG(w.ngs_qb_aggressiveness) AS ngs_qb_aggressiveness,
    AVG(w.ngs_qb_cpoe) AS ngs_qb_cpoe,
    AVG(w.offensive_snap_share) AS offensive_snap_share,
    AVG(w.snap_role_stability) AS snap_role_stability,
    AVG(w.availability_score) AS availability_score,
    SUM(w.injury_status_score) AS injury_status_score,
    AVG(w.injury_burden_score) AS injury_burden_score,
    SUM(w.missed_time_risk_score) AS missed_time_risk_score,
    'BLOCKED' AS route_metrics_source_status,
    ANY_VALUE(w.ngs_source_status) AS ngs_source_status,
    ANY_VALUE(w.participation_source_status) AS participation_source_status,
    ANY_VALUE(w.contract_source_status) AS contract_source_status,
    ANY_VALUE(w.pressure_coverage_source_status) AS pressure_coverage_source_status,
    -- JSON metadata
    TO_JSON_STRING(STRUCT(
      'player_week_advanced_metrics' AS season_source_table,
      COUNT(DISTINCT w.week) AS weeks_aggregated
    )) AS source_coverage_json,
    TO_JSON_STRING(STRUCT(
      COUNTIF(JSON_VALUE(w.missing_flags_json, '$.missing_raw_payload') = 'true') > 0 AS has_weeks_missing_raw,
      COUNTIF(JSON_VALUE(w.missing_flags_json, '$.missing_participation') = 'true') > 0 AS has_weeks_missing_participation
    )) AS missing_flags_json,
    TO_JSON_STRING(STRUCT(
      FALSE AS using_proxy_routes,
      FALSE AS using_proxy_pressures
    )) AS proxy_flags_json,
    TO_JSON_STRING(STRUCT(
      TRUE AS routes_run_blocked,
      TRUE AS yprr_blocked,
      TRUE AS tprr_blocked,
      TRUE AS pressure_epa_blocked,
      TRUE AS covered_receiver_epa_blocked
    )) AS blocked_flags_json
  FROM weekly w
  GROUP BY 1, 3, 4, 5, 8
),
season_calculated AS (
  SELECT
    sb.*,
    SAFE_DIVIDE(sb.receiving_epa, NULLIF(sb.targets, 0)) AS receiving_epa_per_target,
    SAFE_DIVIDE(sb.receiving_first_downs, NULLIF(sb.targets, 0)) AS receiving_first_down_rate,
    SAFE_DIVIDE(sb.targets, NULLIF(stt.season_team_targets, 0)) AS target_share,
    SAFE_DIVIDE(sb.receiving_air_yards, NULLIF(stt.season_team_air_yards, 0)) AS air_yards_share,
    SAFE_DIVIDE(sb.receiving_yards, NULLIF(sb.receiving_air_yards, 0)) AS racr,
    SAFE_DIVIDE(sb.receiving_air_yards, NULLIF(sb.targets, 0)) AS adot,
    SAFE_DIVIDE(sb.rushing_epa, NULLIF(sb.carries, 0)) AS rushing_epa_per_carry,
    SAFE_DIVIDE(sb.rushing_first_downs, NULLIF(sb.carries, 0)) AS rushing_first_down_rate,
    SAFE_DIVIDE(sb.passing_epa, NULLIF(sb.attempts, 0)) AS passing_epa_per_attempt,
    SAFE_DIVIDE(sb.passing_epa, NULLIF(sb.dropbacks, 0)) AS passing_epa_per_dropback,
    SAFE_DIVIDE(sb.passing_first_downs, NULLIF(sb.attempts, 0)) AS passing_first_down_rate,
    -- Weighted Opportunity calculations (PPR, Half PPR, Standard, GNG Keeper)
    (COALESCE(sb.red_zone_targets, 0) * 1.47) + ((COALESCE(sb.targets, 0) - COALESCE(sb.red_zone_targets, 0)) * 0.67) + (COALESCE(sb.red_zone_carries, 0) * 1.28) + ((COALESCE(sb.carries, 0) - COALESCE(sb.red_zone_carries, 0)) * 0.47) AS weighted_opportunity_standard,
    (COALESCE(sb.red_zone_targets, 0) * 1.93) + ((COALESCE(sb.targets, 0) - COALESCE(sb.red_zone_targets, 0)) * 1.00) + (COALESCE(sb.red_zone_carries, 0) * 1.28) + ((COALESCE(sb.carries, 0) - COALESCE(sb.red_zone_carries, 0)) * 0.47) AS weighted_opportunity_half_ppr,
    (COALESCE(sb.red_zone_targets, 0) * 2.39) + ((COALESCE(sb.targets, 0) - COALESCE(sb.red_zone_targets, 0)) * 1.54) + (COALESCE(sb.red_zone_carries, 0) * 1.28) + ((COALESCE(sb.carries, 0) - COALESCE(sb.red_zone_carries, 0)) * 0.47) AS weighted_opportunity_ppr,
    (COALESCE(sb.red_zone_targets, 0) * 1.56) + ((COALESCE(sb.targets, 0) - COALESCE(sb.red_zone_targets, 0)) * 0.74) + (COALESCE(sb.red_zone_carries, 0) * 1.28) + ((COALESCE(sb.carries, 0) - COALESCE(sb.red_zone_carries, 0)) * 0.47) AS weighted_opportunity_gng_keeper
  FROM season_base sb
  LEFT JOIN season_team_totals stt
    ON sb.season = stt.season
    AND sb.season_type = stt.season_type
    AND sb.player_id_internal = stt.player_id_internal
)
SELECT
  metric_version,
  generated_at,
  season,
  season_type,
  player_id_internal,
  gsis_id,
  player_name,
  position,
  position_group,
  team,
  teams_json,
  source_coverage_json,
  missing_flags_json,
  proxy_flags_json,
  blocked_flags_json,
  games,
  targets,
  receptions,
  carries,
  attempts,
  dropbacks,
  routes_run,
  pass_play_snaps,
  offensive_snaps,
  receiving_yards,
  receiving_air_yards,
  receiving_yards_after_catch,
  receiving_epa,
  receiving_epa_per_target,
  receiving_first_downs,
  receiving_first_down_rate,
  target_share,
  air_yards_share,
  1.5 * COALESCE(target_share, 0) + 0.7 * COALESCE(air_yards_share, 0) AS wopr,
  racr,
  adot,
  red_zone_targets,
  goal_line_targets,
  end_zone_targets,
  yprr,
  tprr,
  receiving_first_downs_per_route,
  route_participation_rate,
  rushing_yards,
  rushing_epa,
  rushing_epa_per_carry,
  rushing_first_downs,
  rushing_first_down_rate,
  red_zone_carries,
  goal_line_carries,
  red_zone_opportunities,
  goal_line_opportunities,
  weighted_opportunity_standard,
  weighted_opportunity_half_ppr,
  weighted_opportunity_ppr,
  weighted_opportunity_gng_keeper,
  passing_yards,
  passing_epa,
  passing_epa_per_attempt,
  passing_epa_per_dropback,
  passing_cpoe,
  dakota,
  passing_first_downs,
  passing_first_down_rate,
  qb_rushing_baseline_score,
  ngs_avg_separation,
  ngs_avg_cushion,
  ngs_yac_above_expectation,
  ngs_rushing_efficiency,
  ngs_rush_yards_over_expected,
  ngs_rush_yards_over_expected_per_att,
  ngs_box_count_rate,
  ngs_qb_time_to_throw,
  ngs_qb_aggressiveness,
  ngs_qb_cpoe,
  offensive_snap_share,
  snap_role_stability,
  availability_score,
  injury_status_score,
  injury_burden_score,
  missed_time_risk_score,
  route_metrics_source_status,
  ngs_source_status,
  participation_source_status,
  contract_source_status,
  pressure_coverage_source_status
FROM season_calculated
"""


def build_source_coverage_sql(project: str, dataset: str) -> str:
    # Inserts descriptive row audits of metric source coverage by season into player_metric_source_coverage
    return f"""
WITH weekly AS (
  SELECT *
  FROM {_table(project, dataset, "player_week_advanced_metrics")}
  WHERE season BETWEEN @season_start AND @season_end
    AND metric_version = @metric_version
),
metrics_unpivoted AS (
  SELECT season, 'WOPR' AS metric_name, wopr AS value FROM weekly
  UNION ALL SELECT season, 'EPA (Receiving)', receiving_epa FROM weekly
  UNION ALL SELECT season, 'EPA (Rushing)', rushing_epa FROM weekly
  UNION ALL SELECT season, 'EPA (Passing)', passing_epa FROM weekly
  UNION ALL SELECT season, 'YPRR', yprr FROM weekly
  UNION ALL SELECT season, 'TPRR', tprr FROM weekly
  UNION ALL SELECT season, 'Snap Share', offensive_snap_share FROM weekly
  UNION ALL SELECT season, 'Weighted Opportunity (PPR)', weighted_opportunity_ppr FROM weekly
  UNION ALL SELECT season, 'NGS Separation', ngs_avg_separation FROM weekly
  UNION ALL SELECT season, 'NGS Cushion', ngs_avg_cushion FROM weekly
)
SELECT
  @metric_version AS metric_version,
  season,
  metric_name,
  CASE
    -- Route metrics are permanently blocked
    WHEN metric_name IN ('YPRR', 'TPRR') THEN 'BLOCKED'
    -- NGS starts in 2016
    WHEN metric_name IN ('NGS Separation', 'NGS Cushion') AND season < 2016 THEN 'UNAVAILABLE'
    -- All other metrics are available back to 2014
    ELSE 'AVAILABLE'
  END AS source_status,
  COUNT(1) AS coverage_count,
  COUNTIF(value IS NOT NULL) AS non_null_count,
  CURRENT_TIMESTAMP() AS created_at
FROM metrics_unpivoted
GROUP BY 1, 2, 3, 4
"""


def run_pipeline(
    client: Any,
    project: str,
    dataset: str,
    season_start: int,
    season_end: int,
    metric_version: str,
    write: bool = False,
) -> dict[str, Any]:
    params = [
        _scalar_param("season_start", "INT64", season_start),
        _scalar_param("season_end", "INT64", season_end),
        _scalar_param("metric_version", "STRING", metric_version),
    ]

    print(f"Planning advanced metrics warehouse backfill...")
    print(f"Season range: {season_start} to {season_end}")
    print(f"Metric version: {metric_version}")
    print(f"Write execution authorized: {write}")

    weekly_insert = f"""
    INSERT INTO {_table(project, dataset, "player_week_advanced_metrics")} (
      metric_version, feature_run_id, season, week, season_type, player_id_internal, gsis_id,
      player_name, position, position_group, team, games, targets, receptions, carries,
      attempts, dropbacks, routes_run, pass_play_snaps, offensive_snaps, receiving_yards,
      receiving_air_yards, receiving_yards_after_catch, receiving_epa, receiving_epa_per_target,
      receiving_first_downs, receiving_first_down_rate, target_share, air_yards_share,
      wopr, racr, adot, red_zone_targets, goal_line_targets, end_zone_targets, yprr, tprr,
      receiving_first_downs_per_route, route_participation_rate, rushing_yards, rushing_epa,
      rushing_epa_per_carry, rushing_first_downs, rushing_first_down_rate, red_zone_carries,
      goal_line_carries, red_zone_opportunities, goal_line_opportunities, weighted_opportunity_standard,
      weighted_opportunity_half_ppr, weighted_opportunity_ppr, weighted_opportunity_gng_keeper,
      passing_yards, passing_epa, passing_epa_per_attempt, passing_epa_per_dropback,
      passing_cpoe, dakota, passing_first_downs, passing_first_down_rate, qb_rushing_baseline_score,
      ngs_avg_separation, ngs_avg_cushion, ngs_yac_above_expectation, ngs_rushing_efficiency,
      ngs_rush_yards_over_expected, ngs_rush_yards_over_expected_per_att, ngs_box_count_rate,
      ngs_qb_time_to_throw, ngs_qb_aggressiveness, ngs_qb_cpoe, offensive_snap_share,
      snap_role_stability, availability_score, injury_status_score, injury_burden_score,
      missed_time_risk_score, route_metrics_source_status, ngs_source_status, participation_source_status,
      contract_source_status, pressure_coverage_source_status, source_coverage_json, missing_flags_json,
      proxy_flags_json, blocked_flags_json, generated_at
    )
    {build_weekly_advanced_metrics_sql(project, dataset)}
    """

    season_insert = f"""
    INSERT INTO {_table(project, dataset, "player_season_advanced_metrics")} (
      metric_version, generated_at, season, season_type, player_id_internal, gsis_id,
      player_name, position, position_group, team, teams_json, source_coverage_json,
      missing_flags_json, proxy_flags_json, blocked_flags_json, games, targets, receptions,
      carries, attempts, dropbacks, routes_run, pass_play_snaps, offensive_snaps,
      receiving_yards, receiving_air_yards, receiving_yards_after_catch, receiving_epa,
      receiving_epa_per_target, receiving_first_downs, receiving_first_down_rate, target_share,
      air_yards_share, wopr, racr, adot, red_zone_targets, goal_line_targets, end_zone_targets,
      yprr, tprr, receiving_first_downs_per_route, route_participation_rate, rushing_yards,
      rushing_epa, rushing_epa_per_carry, rushing_first_downs, rushing_first_down_rate,
      red_zone_carries, goal_line_carries, red_zone_opportunities, goal_line_opportunities,
      weighted_opportunity_standard, weighted_opportunity_half_ppr, weighted_opportunity_ppr,
      weighted_opportunity_gng_keeper, passing_yards, passing_epa, passing_epa_per_attempt,
      passing_epa_per_dropback, passing_cpoe, dakota, passing_first_downs, passing_first_down_rate,
      qb_rushing_baseline_score, ngs_avg_separation, ngs_avg_cushion, ngs_yac_above_expectation,
      ngs_rushing_efficiency, ngs_rush_yards_over_expected, ngs_rush_yards_over_expected_per_att,
      ngs_box_count_rate, ngs_qb_time_to_throw, ngs_qb_aggressiveness, ngs_qb_cpoe,
      offensive_snap_share, snap_role_stability, availability_score, injury_status_score,
      injury_burden_score, missed_time_risk_score, route_metrics_source_status, ngs_source_status,
      participation_source_status, contract_source_status, pressure_coverage_source_status
    )
    {build_season_advanced_metrics_sql(project, dataset)}
    """

    coverage_insert = f"""
    INSERT INTO {_table(project, dataset, "player_metric_source_coverage")} (
      metric_version, season, metric_name, source_status, coverage_count, non_null_count, created_at
    )
    {build_source_coverage_sql(project, dataset)}
    """

    results = {}
    if write:
        # Bounded deletes first to prevent duplicate rows on rerun
        print("Executing bounded deletes...")
        client.query(
            f"DELETE FROM {_table(project, dataset, 'player_week_advanced_metrics')} WHERE metric_version = @metric_version AND season BETWEEN @season_start AND @season_end",
            job_config=_query_job_config(params)
        ).result()
        client.query(
            f"DELETE FROM {_table(project, dataset, 'player_season_advanced_metrics')} WHERE metric_version = @metric_version AND season BETWEEN @season_start AND @season_end",
            job_config=_query_job_config(params)
        ).result()
        client.query(
            f"DELETE FROM {_table(project, dataset, 'player_metric_source_coverage')} WHERE metric_version = @metric_version AND season BETWEEN @season_start AND @season_end",
            job_config=_query_job_config(params)
        ).result()

        print("Executing weekly insert...")
        weekly_job = client.query(weekly_insert, job_config=_query_job_config(params))
        weekly_job.result()
        results["weekly_rows_written"] = weekly_job.num_dml_affected_rows

        print("Executing seasonal insert...")
        season_job = client.query(season_insert, job_config=_query_job_config(params))
        season_job.result()
        results["season_rows_written"] = season_job.num_dml_affected_rows

        print("Executing coverage audit insert...")
        coverage_job = client.query(coverage_insert, job_config=_query_job_config(params))
        coverage_job.result()
        results["coverage_rows_written"] = coverage_job.num_dml_affected_rows

        print("Backfill materialization complete.")
    else:
        print("Dry run: compiling SQL plans.")
        results["status"] = "dry_run_success"

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Player-year advanced metrics warehouse backfiller.")
    parser.add_argument("--season-start", type=int, default=2014)
    parser.add_argument("--season-end", type=int, default=2025)
    parser.add_argument("--metric-version", default=DEFAULT_METRIC_VERSION)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--project", default=os.environ.get("BQ_PROJECT") or DEFAULT_PROJECT)
    parser.add_argument("--dataset", default=os.environ.get("BQ_DATASET") or DEFAULT_DATASET)
    args = parser.parse_args()

    from google.cloud import bigquery
    client = bigquery.Client(project=args.project)

    try:
        results = run_pipeline(
            client=client,
            project=args.project,
            dataset=args.dataset,
            season_start=args.season_start,
            season_end=args.season_end,
            metric_version=args.metric_version,
            write=args.write
        )
        print(json.dumps(results, indent=2))
        return 0
    except Exception as exc:
        print(f"Error executing pipeline: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
