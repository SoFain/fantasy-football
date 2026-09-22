"""Dry-run planner for nflverse advanced metrics feature marts."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from src.nflverse_backfill_plan import DEFAULT_DATASET, DEFAULT_PROJECT


ADVANCED_METRICS_GATE = "ALLOW_ADVANCED_METRICS_MATERIALIZATION"
BASE_TARGETS = (
    "player_week_advanced_metrics",
    "team_week_context_metrics",
    "qb_week_environment_metrics",
)
CURRENT_TARGETS = (
    "player_recent_advanced_metrics_current",
    "player_role_usage_metrics_current",
)
TARGETS = BASE_TARGETS + CURRENT_TARGETS
STAGING_TABLES = (
    "stg_player_identity",
    "stg_game_context",
    "stg_player_week_stats",
    "stg_team_week_stats",
    "stg_play_player_events",
    "stg_participation_context",
)
BLOCKED_TABLES = (
    "play_by_play",
    "weekly_metrics",
    "raw_nflverse_",
    "pigskin_player_context_packet_current",
    "compat_pigskin_player_context_current",
)
DEFAULT_METRIC_VERSION = "nflverse_adv_v0_2014_dry_run"
SCORING_PROFILE_ID = "ppr"
LEAGUE_TYPE_ID = "redraft"
ROSTER_FORMAT_ID = "one_qb"
STATIC_BLOCKED_METRICS = (
    "route_share",
    "yards_per_route_run",
    "targets_per_route_run",
    "first_read_share",
    "true_pressure_to_sack",
    "yards_before_contact",
    "yards_after_contact",
    "slot_wide_inline_alignment",
    "red_zone_targets",
    "red_zone_carries",
    "red_zone_touches",
    "inside_10_carries",
    "inside_5_carries",
    "high_value_touches",
    "touchdown_rates",
    "reception_flag_dependent_metrics",
)
TARGET_COLUMNS = {
    "player_week_advanced_metrics": (
        "metric_version",
        "feature_run_id",
        "season",
        "week",
        "player_id_internal",
        "player_name",
        "position",
        "team",
        "opponent_team",
        "scoring_profile_id",
        "league_type_id",
        "roster_format_id",
        "targets",
        "carries",
        "opportunities",
        "target_share",
        "air_yards_share",
        "wopr",
        "adot",
        "racr",
        "weighted_opportunity",
        "carry_share",
        "opportunity_share",
        "red_zone_targets",
        "red_zone_carries",
        "red_zone_touches",
        "inside_10_carries",
        "inside_5_carries",
        "high_value_touches",
        "epa_total",
        "epa_per_opportunity",
        "success_rate",
        "cpoe",
        "explosive_rush_rate",
        "explosive_reception_rate",
        "snap_share",
        "injury_status",
        "depth_chart_role",
        "source_freshness_json",
        "missing_data_flags",
        "created_at",
    ),
    "team_week_context_metrics": (
        "metric_version",
        "feature_run_id",
        "season",
        "week",
        "team",
        "opponent_team",
        "plays",
        "seconds_per_play",
        "neutral_pass_rate",
        "pass_rate_over_expected",
        "team_epa_per_play",
        "pass_epa_per_play",
        "rush_epa_per_play",
        "team_success_rate",
        "red_zone_pass_rate",
        "red_zone_rush_rate",
        "opponent_epa_allowed",
        "opponent_pass_epa_allowed",
        "opponent_rush_epa_allowed",
        "opponent_funnel_label",
        "game_environment_json",
        "source_freshness_json",
        "missing_data_flags",
        "created_at",
    ),
    "qb_week_environment_metrics": (
        "metric_version",
        "feature_run_id",
        "season",
        "week",
        "qb_player_id_internal",
        "player_name",
        "team",
        "opponent_team",
        "dropbacks",
        "pass_attempts",
        "sacks",
        "scrambles",
        "designed_rushes",
        "epa_per_dropback",
        "passing_epa",
        "cpoe",
        "adot",
        "deep_attempt_rate",
        "sack_rate",
        "scramble_rate",
        "pass_rate_over_expected_context",
        "source_freshness_json",
        "missing_data_flags",
        "created_at",
    ),
}
TARGET_GRAINS = {
    "player_week_advanced_metrics": (
        "metric_version",
        "season",
        "week",
        "player_id_internal",
        "scoring_profile_id",
        "league_type_id",
        "roster_format_id",
        "team",
    ),
    "team_week_context_metrics": ("metric_version", "season", "week", "team"),
    "qb_week_environment_metrics": ("metric_version", "season", "week", "qb_player_id_internal", "team"),
}


class AdvancedMetricsPlanError(RuntimeError):
    """Raised for unsafe advanced metrics dry-run requests."""


@dataclass(frozen=True)
class TargetPlan:
    target: str
    source_tables: tuple[str, ...]
    sql: str
    diagnostic_sql: str
    warnings: tuple[str, ...]
    blocked_metrics: tuple[str, ...] = ()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dry-run nflverse advanced metrics feature-mart planner.")
    parser.add_argument("--dry-run", action="store_true", help="Build SQL and run read-only diagnostics. Default.")
    parser.add_argument("--plan-only", action="store_true", help="Alias for dry-run planning.")
    parser.add_argument("--write", action="store_true", help="Blocked in Phase 29.9.")
    parser.add_argument("--target", action="append", choices=TARGETS, help="Feature target to include. May be repeated.")
    parser.add_argument("--all-targets", action="store_true", help="Plan base and current-placeholder targets.")
    parser.add_argument("--season-start", type=int, required=True)
    parser.add_argument("--season-end", type=int, required=True)
    parser.add_argument("--week-start", type=int)
    parser.add_argument("--week-end", type=int)
    parser.add_argument("--project", default=os.environ.get("BQ_PROJECT") or DEFAULT_PROJECT)
    parser.add_argument("--dataset", default=os.environ.get("BQ_DATASET") or DEFAULT_DATASET)
    parser.add_argument("--metric-version", default=DEFAULT_METRIC_VERSION)
    parser.add_argument("--output-json", help="Optional path for the JSON dry-run summary.")
    parser.add_argument("--strict", action="store_true", help="Fail when a diagnostic query fails.")
    return parser.parse_args(argv)


def _table(project: str, dataset: str, table: str) -> str:
    return f"`{project}.{dataset}.{table}`"


def _bounds_sql(alias: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    prefix = f"{alias}." if alias else ""
    clauses = [f"{prefix}season BETWEEN {season_start} AND {season_end}"]
    if week_start is not None:
        clauses.append(f"{prefix}week >= {week_start}")
    if week_end is not None:
        clauses.append(f"{prefix}week <= {week_end}")
    return " AND ".join(clauses)


def selected_targets(args: argparse.Namespace) -> list[str]:
    if args.target and args.all_targets:
        raise AdvancedMetricsPlanError("Use either --target or --all-targets, not both.")
    if args.target:
        return list(dict.fromkeys(args.target))
    if args.all_targets:
        return list(TARGETS)
    return list(BASE_TARGETS)


def validate_request(args: argparse.Namespace) -> None:
    if args.week_start is not None and args.week_end is not None and args.week_start > args.week_end:
        raise AdvancedMetricsPlanError("--week-start cannot be greater than --week-end.")
    if args.season_start > args.season_end:
        raise AdvancedMetricsPlanError("--season-start cannot be greater than --season-end.")
    if args.write:
        write_targets = selected_targets(args)
        blocked_targets = [target for target in write_targets if target not in BASE_TARGETS]
        if blocked_targets:
            raise AdvancedMetricsPlanError(f"--write supports only base advanced metric targets, not: {', '.join(blocked_targets)}.")
        if os.environ.get(ADVANCED_METRICS_GATE, "").lower() != "true":
            raise AdvancedMetricsPlanError(f"{ADVANCED_METRICS_GATE} must be true to write advanced metrics.")


def source_field_audit_sql(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    event_filter = _bounds_sql("e", season_start, season_end, week_start, week_end)
    raw_filter = _bounds_sql("r", season_start, season_end, week_start, week_end)
    events = _table(project, dataset, "stg_play_player_events")
    raw_pbp = _table(project, dataset, "raw_nflverse_pbp")
    return f"""
WITH events AS (
  SELECT *
  FROM {events} e
  WHERE {event_filter}
),
raw AS (
  SELECT raw_payload_json
  FROM {raw_pbp} r
  WHERE {raw_filter}
),
audit AS (
  SELECT 'stg_play_player_events.red_zone_flag' AS field_name, 'staging' AS source_layer, COUNT(1) AS source_rows, COUNTIF(red_zone_flag IS NOT NULL) AS non_null_count, COUNTIF(red_zone_flag) AS true_count, TRUE AS source_exists, 'blocked' AS v0_status FROM events
  UNION ALL SELECT 'stg_play_player_events.inside_10_flag', 'staging', COUNT(1), COUNTIF(inside_10_flag IS NOT NULL), COUNTIF(inside_10_flag), TRUE, 'blocked' FROM events
  UNION ALL SELECT 'stg_play_player_events.inside_5_flag', 'staging', COUNT(1), COUNTIF(inside_5_flag IS NOT NULL), COUNTIF(inside_5_flag), TRUE, 'blocked' FROM events
  UNION ALL SELECT 'stg_play_player_events.reception', 'staging', COUNT(1), COUNTIF(reception IS NOT NULL), COUNTIF(reception), TRUE, 'blocked' FROM events
  UNION ALL SELECT 'stg_play_player_events.touchdown', 'staging', COUNT(1), COUNTIF(touchdown IS NOT NULL), COUNTIF(touchdown), TRUE, 'blocked' FROM events
  UNION ALL SELECT 'stg_play_player_events.target', 'staging', COUNT(1), COUNTIF(target IS NOT NULL), COUNTIF(target), TRUE, 'safe' FROM events
  UNION ALL SELECT 'stg_play_player_events.pass_attempt', 'staging', COUNT(1), COUNTIF(pass_attempt IS NOT NULL), COUNTIF(pass_attempt), TRUE, 'safe' FROM events
  UNION ALL SELECT 'stg_play_player_events.rush_attempt', 'staging', COUNT(1), COUNTIF(rush_attempt IS NOT NULL), COUNTIF(rush_attempt), TRUE, 'safe' FROM events
  UNION ALL SELECT 'stg_play_player_events.air_yards', 'staging', COUNT(1), COUNTIF(air_yards IS NOT NULL), CAST(NULL AS INT64), TRUE, 'safe' FROM events
  UNION ALL SELECT 'stg_play_player_events.yards_gained', 'staging', COUNT(1), COUNTIF(yards_gained IS NOT NULL), CAST(NULL AS INT64), TRUE, 'safe' FROM events
  UNION ALL SELECT 'stg_play_player_events.epa', 'staging', COUNT(1), COUNTIF(epa IS NOT NULL), CAST(NULL AS INT64), TRUE, 'safe' FROM events
  UNION ALL SELECT 'stg_play_player_events.success', 'staging', COUNT(1), COUNTIF(success IS NOT NULL), CAST(NULL AS INT64), TRUE, 'safe' FROM events
  UNION ALL SELECT 'stg_play_player_events.cpoe', 'staging', COUNT(1), COUNTIF(cpoe IS NOT NULL), CAST(NULL AS INT64), TRUE, 'safe_with_nulls' FROM events
  UNION ALL SELECT 'stg_play_player_events.yardline_100', 'staging', COUNT(1), COUNTIF(yardline_100 IS NOT NULL), CAST(NULL AS INT64), TRUE, 'diagnostic_only' FROM events
  UNION ALL SELECT 'raw_nflverse_pbp.raw_payload_json.complete_pass', 'raw_audit_only', COUNT(1), COUNTIF(JSON_VALUE(raw_payload_json, '$.complete_pass') IS NOT NULL), COUNTIF(LOWER(JSON_VALUE(raw_payload_json, '$.complete_pass')) IN ('1', 'true')), TRUE, 'blocked_until_staging_mapping_review' FROM raw
  UNION ALL SELECT 'raw_nflverse_pbp.raw_payload_json.touchdown', 'raw_audit_only', COUNT(1), COUNTIF(JSON_VALUE(raw_payload_json, '$.touchdown') IS NOT NULL), COUNTIF(LOWER(JSON_VALUE(raw_payload_json, '$.touchdown')) IN ('1', 'true')), TRUE, 'blocked_until_staging_mapping_review' FROM raw
  UNION ALL SELECT 'raw_nflverse_pbp.raw_payload_json.pass_touchdown', 'raw_audit_only', COUNT(1), COUNTIF(JSON_VALUE(raw_payload_json, '$.pass_touchdown') IS NOT NULL), COUNTIF(LOWER(JSON_VALUE(raw_payload_json, '$.pass_touchdown')) IN ('1', 'true')), TRUE, 'blocked_until_staging_mapping_review' FROM raw
  UNION ALL SELECT 'raw_nflverse_pbp.raw_payload_json.rush_touchdown', 'raw_audit_only', COUNT(1), COUNTIF(JSON_VALUE(raw_payload_json, '$.rush_touchdown') IS NOT NULL), COUNTIF(LOWER(JSON_VALUE(raw_payload_json, '$.rush_touchdown')) IN ('1', 'true')), TRUE, 'blocked_until_staging_mapping_review' FROM raw
)
SELECT *
FROM audit
ORDER BY source_layer, field_name
"""


def _player_week_sql(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None, metric_version: str) -> str:
    p_filter = _bounds_sql("p", season_start, season_end, week_start, week_end)
    e_filter = _bounds_sql("e", season_start, season_end, week_start, week_end)
    part_filter = _bounds_sql("pc", season_start, season_end, week_start, week_end)
    pws = _table(project, dataset, "stg_player_week_stats")
    events = _table(project, dataset, "stg_play_player_events")
    teams = _table(project, dataset, "stg_team_week_stats")
    participation = _table(project, dataset, "stg_participation_context")
    return f"""
WITH player_base AS (
  SELECT *
  FROM {pws} p
  WHERE {p_filter}
),
event_metrics AS (
  SELECT
    e.season,
    e.week,
    e.player_id_internal,
    e.team,
    SUM(IF(e.event_type IN ('receiver', 'rusher', 'passer'), e.epa, 0)) AS epa_total,
    COUNTIF(e.event_type IN ('receiver', 'rusher', 'passer')) AS eligible_event_count,
    COUNTIF(e.event_type IN ('receiver', 'rusher', 'passer') AND e.success > 0) AS successful_event_count,
    AVG(IF(e.cpoe IS NOT NULL AND e.event_type IN ('receiver', 'passer'), e.cpoe, NULL)) AS cpoe,
    COUNTIF(e.event_type = 'receiver' AND e.yards_gained >= 20) AS explosive_reception_events,
    COUNTIF(e.event_type = 'receiver') AS receiver_events,
    COUNTIF(e.event_type = 'rusher' AND e.yards_gained >= 10) AS explosive_rush_events,
    COUNTIF(e.event_type = 'rusher') AS rush_events,
    SUM(IF(e.event_type = 'target', e.air_yards, 0)) AS event_target_air_yards,
    COUNTIF(JSON_VALUE(e.missing_data_flags, '$.missing_identity_match') = 'true') AS event_missing_identity_count
  FROM {events} e
  WHERE {e_filter}
    AND e.event_type IN ('receiver', 'rusher', 'passer', 'target')
  GROUP BY 1, 2, 3, 4
),
participation AS (
  SELECT
    pc.season,
    pc.week,
    pc.player_id_internal,
    pc.team,
    MAX(pc.offense_pct) AS snap_share,
    COUNTIF(JSON_VALUE(pc.missing_data_flags, '$.missing_identity_match') = 'true') AS participation_missing_identity_count
  FROM {participation} pc
  WHERE {part_filter}
  GROUP BY 1, 2, 3, 4
),
metrics AS (
  SELECT
    '{metric_version}' AS metric_version,
    CONCAT('{metric_version}_', CAST(p.season AS STRING)) AS feature_run_id,
    p.season,
    p.week,
    p.player_id_internal,
    p.player_name,
    p.position,
    p.team,
    p.opponent_team,
    '{SCORING_PROFILE_ID}' AS scoring_profile_id,
    '{LEAGUE_TYPE_ID}' AS league_type_id,
    '{ROSTER_FORMAT_ID}' AS roster_format_id,
    p.targets,
    p.carries,
    COALESCE(p.carries, 0) + COALESCE(p.targets, 0) AS opportunities,
    SAFE_DIVIDE(p.targets, NULLIF(t.team_targets, 0)) AS target_share,
    LEAST(1.0, GREATEST(0.0, SAFE_DIVIDE(COALESCE(p.air_yards, e.event_target_air_yards), NULLIF(t.team_air_yards, 0)))) AS air_yards_share,
    1.5 * SAFE_DIVIDE(p.targets, NULLIF(t.team_targets, 0)) + 0.7 * LEAST(1.0, GREATEST(0.0, SAFE_DIVIDE(COALESCE(p.air_yards, e.event_target_air_yards), NULLIF(t.team_air_yards, 0)))) AS wopr,
    SAFE_DIVIDE(COALESCE(p.air_yards, e.event_target_air_yards), NULLIF(p.targets, 0)) AS adot,
    SAFE_DIVIDE(p.receiving_yards, NULLIF(COALESCE(p.air_yards, e.event_target_air_yards), 0)) AS racr,
    COALESCE(p.carries, 0) + 2.5 * COALESCE(p.targets, 0) AS weighted_opportunity,
    SAFE_DIVIDE(p.carries, NULLIF(t.rush_attempts, 0)) AS carry_share,
    SAFE_DIVIDE(COALESCE(p.carries, 0) + COALESCE(p.targets, 0), NULLIF(COALESCE(t.team_targets, 0) + COALESCE(t.rush_attempts, 0), 0)) AS opportunity_share,
    CAST(NULL AS FLOAT64) AS red_zone_targets,
    CAST(NULL AS FLOAT64) AS red_zone_carries,
    CAST(NULL AS FLOAT64) AS red_zone_touches,
    CAST(NULL AS FLOAT64) AS inside_10_carries,
    CAST(NULL AS FLOAT64) AS inside_5_carries,
    CAST(NULL AS FLOAT64) AS high_value_touches,
    e.epa_total,
    SAFE_DIVIDE(e.epa_total, NULLIF(COALESCE(p.carries, 0) + COALESCE(p.targets, 0), 0)) AS epa_per_opportunity,
    SAFE_DIVIDE(e.successful_event_count, NULLIF(e.eligible_event_count, 0)) AS success_rate,
    e.cpoe,
    SAFE_DIVIDE(e.explosive_rush_events, NULLIF(e.rush_events, 0)) AS explosive_rush_rate,
    SAFE_DIVIDE(e.explosive_reception_events, NULLIF(e.receiver_events, 0)) AS explosive_reception_rate,
    pc.snap_share,
    CAST(NULL AS STRING) AS injury_status,
    CAST(NULL AS STRING) AS depth_chart_role,
    TO_JSON_STRING(STRUCT(
      p.source_freshness_json AS player_week,
      t.source_freshness_json AS team_week,
      pc.snap_share IS NOT NULL AS participation_joined
    )) AS source_freshness_json,
    TO_JSON_STRING(STRUCT(
      JSON_VALUE(p.missing_data_flags, '$.missing_identity_match') = 'true' AS missing_identity_match,
      t.team IS NULL AS missing_team_context,
      pc.player_id_internal IS NULL AS missing_participation_context,
      COALESCE(t.team_targets, 0) = 0 AS zero_team_targets_denominator,
      COALESCE(t.team_air_yards, 0) = 0 AS zero_team_air_yards_denominator,
      COALESCE(t.rush_attempts, 0) = 0 AS zero_team_rush_attempts_denominator,
      COALESCE(t.team_targets, 0) + COALESCE(t.rush_attempts, 0) = 0 AS zero_team_opportunity_denominator,
      COALESCE(p.targets, 0) = 0 AS zero_player_targets_denominator,
      COALESCE(p.air_yards, e.event_target_air_yards, 0) = 0 AS zero_player_air_yards_denominator,
      p.air_yards IS NULL AND e.event_target_air_yards IS NULL AS missing_player_air_yards_source,
      COALESCE(p.carries, 0) + COALESCE(p.targets, 0) = 0 AS zero_player_opportunity_denominator,
      TRUE AS route_metrics_blocked,
      TRUE AS red_zone_high_value_metrics_blocked,
      TRUE AS injury_depth_context_unavailable
    )) AS missing_data_flags,
    CURRENT_TIMESTAMP() AS created_at
  FROM player_base p
  LEFT JOIN {teams} t
    ON p.season = t.season AND p.week = t.week AND p.team = t.team
  LEFT JOIN event_metrics e
    ON p.season = e.season AND p.week = e.week AND p.team = e.team AND p.player_id_internal = e.player_id_internal
  LEFT JOIN participation pc
    ON p.season = pc.season AND p.week = pc.week AND p.team = pc.team AND p.player_id_internal = pc.player_id_internal
)
SELECT *
FROM metrics
"""


def _player_week_diagnostics(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None, metric_version: str) -> str:
    sql = _player_week_sql(project, dataset, season_start, season_end, week_start, week_end, metric_version)
    source_filter = _bounds_sql("", season_start, season_end, week_start, week_end)
    return f"""
WITH planned AS ({sql})
SELECT
  COUNT(1) AS planned_row_count,
  (SELECT COUNT(1) FROM {_table(project, dataset, "stg_player_week_stats")} WHERE {source_filter}) AS source_row_count,
  (
    SELECT COUNT(1)
    FROM (
      SELECT metric_version, season, week, player_id_internal, scoring_profile_id, league_type_id, roster_format_id, team, COUNT(1) AS row_count
      FROM planned
      GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
      HAVING row_count > 1
    )
  ) AS duplicate_key_count,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.missing_identity_match') = 'true') AS missing_identity_count,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.missing_team_context') = 'true') AS missing_team_context_count,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.zero_team_targets_denominator') = 'true') AS zero_team_targets_denominator_count,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.zero_team_air_yards_denominator') = 'true') AS zero_team_air_yards_denominator_count,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.zero_team_opportunity_denominator') = 'true') AS zero_team_opportunity_denominator_count,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.zero_player_opportunity_denominator') = 'true') AS zero_player_opportunity_denominator_count,
  COUNTIF(target_share IS NULL) AS target_share_null_count,
  COUNTIF(air_yards_share IS NULL) AS air_yards_share_null_count,
  COUNTIF(wopr IS NULL) AS wopr_null_count,
  COUNTIF(epa_per_opportunity IS NULL) AS epa_per_opportunity_null_count,
  COUNTIF(snap_share IS NULL) AS snap_share_null_count,
  COUNTIF(red_zone_touches IS NULL) AS red_zone_high_value_metrics_blocked_count,
  COUNTIF(source_freshness_json IS NULL) AS missing_source_freshness_count,
  COUNTIF(missing_data_flags IS NULL) AS missing_flags_count
FROM planned
"""


def _team_week_sql(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None, metric_version: str) -> str:
    team_filter = _bounds_sql("t", season_start, season_end, week_start, week_end)
    teams = _table(project, dataset, "stg_team_week_stats")
    games = _table(project, dataset, "stg_game_context")
    return f"""
SELECT
  '{metric_version}' AS metric_version,
  CONCAT('{metric_version}_', CAST(t.season AS STRING)) AS feature_run_id,
  t.season,
  t.week,
  t.team,
  t.opponent_team,
  t.plays,
  CAST(NULL AS FLOAT64) AS seconds_per_play,
  t.neutral_pass_rate,
  CAST(NULL AS FLOAT64) AS pass_rate_over_expected,
  t.epa_per_play AS team_epa_per_play,
  CAST(NULL AS FLOAT64) AS pass_epa_per_play,
  CAST(NULL AS FLOAT64) AS rush_epa_per_play,
  t.success_rate AS team_success_rate,
  CAST(NULL AS FLOAT64) AS red_zone_pass_rate,
  CAST(NULL AS FLOAT64) AS red_zone_rush_rate,
  t.opponent_epa_allowed,
  t.opponent_pass_epa_allowed,
  t.opponent_rush_epa_allowed,
  CAST(NULL AS STRING) AS opponent_funnel_label,
  TO_JSON_STRING(STRUCT(
    g.game_id AS game_id,
    g.game_date AS game_date,
    g.stadium AS stadium,
    g.roof AS roof,
    g.surface AS surface,
    g.temp AS temp,
    g.wind AS wind,
    g.total_line AS total_line,
    g.spread_line AS spread_line
  )) AS game_environment_json,
  TO_JSON_STRING(STRUCT(t.source_freshness_json AS team_week, g.source_freshness_json AS game_context)) AS source_freshness_json,
  TO_JSON_STRING(STRUCT(
    g.game_id IS NULL AS missing_game_context,
    t.opponent_epa_allowed IS NULL AS missing_opponent_context,
    TRUE AS seconds_per_play_blocked_clock_fields_not_modeled,
    TRUE AS pass_rate_over_expected_unavailable,
    TRUE AS pass_rush_epa_split_unavailable,
    TRUE AS red_zone_rates_blocked_source_field_review
  )) AS missing_data_flags,
  CURRENT_TIMESTAMP() AS created_at
FROM {teams} t
LEFT JOIN {games} g
  ON t.season = g.season
  AND t.week = g.week
  AND (
    (t.team = g.home_team AND t.opponent_team = g.away_team)
    OR (t.team = g.away_team AND t.opponent_team = g.home_team)
  )
WHERE {team_filter}
"""


def _team_week_diagnostics(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None, metric_version: str) -> str:
    sql = _team_week_sql(project, dataset, season_start, season_end, week_start, week_end, metric_version)
    source_filter = _bounds_sql("", season_start, season_end, week_start, week_end)
    return f"""
WITH planned AS ({sql})
SELECT
  COUNT(1) AS planned_row_count,
  (SELECT COUNT(1) FROM {_table(project, dataset, "stg_team_week_stats")} WHERE {source_filter}) AS source_row_count,
  (
    SELECT COUNT(1)
    FROM (
      SELECT metric_version, season, week, team, COUNT(1) AS row_count
      FROM planned
      GROUP BY 1, 2, 3, 4
      HAVING row_count > 1
    )
  ) AS duplicate_key_count,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.missing_game_context') = 'true') AS missing_game_context_count,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.missing_opponent_context') = 'true') AS missing_opponent_context_count,
  COUNTIF(seconds_per_play IS NULL) AS null_pace_count,
  COUNTIF(pass_rate_over_expected IS NULL) AS null_pass_rate_over_expected_count,
  COUNTIF(team_epa_per_play IS NOT NULL) AS epa_coverage_count,
  COUNTIF(team_success_rate IS NOT NULL) AS success_coverage_count,
  COUNTIF(red_zone_pass_rate IS NULL AND red_zone_rush_rate IS NULL) AS red_zone_metrics_blocked_count,
  COUNTIF(source_freshness_json IS NULL) AS missing_source_freshness_count,
  COUNTIF(missing_data_flags IS NULL) AS missing_flags_count
FROM planned
"""


def _qb_week_sql(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None, metric_version: str) -> str:
    e_filter = _bounds_sql("e", season_start, season_end, week_start, week_end)
    events = _table(project, dataset, "stg_play_player_events")
    pws = _table(project, dataset, "stg_player_week_stats")
    teams = _table(project, dataset, "stg_team_week_stats")
    return f"""
WITH passer_events AS (
  SELECT
    e.season,
    e.week,
    e.player_id_internal,
    e.team,
    ANY_VALUE(e.opponent_team) AS opponent_team,
    COUNTIF(e.pass_attempt) AS pass_attempts,
    COUNT(1) AS dropbacks,
    SUM(e.epa) AS passing_epa,
    AVG(e.cpoe) AS cpoe,
    AVG(e.air_yards) AS adot,
    SAFE_DIVIDE(COUNTIF(e.air_yards >= 20), NULLIF(COUNT(1), 0)) AS deep_attempt_rate,
    COUNTIF(JSON_VALUE(e.missing_data_flags, '$.missing_identity_match') = 'true') AS missing_identity_event_count
  FROM {events} e
  WHERE {e_filter}
    AND e.event_type = 'passer'
  GROUP BY 1, 2, 3, 4
)
SELECT
  '{metric_version}' AS metric_version,
  CONCAT('{metric_version}_', CAST(pe.season AS STRING)) AS feature_run_id,
  pe.season,
  pe.week,
  pe.player_id_internal AS qb_player_id_internal,
  p.player_name,
  pe.team,
  COALESCE(p.opponent_team, pe.opponent_team) AS opponent_team,
  CAST(pe.dropbacks AS FLOAT64) AS dropbacks,
  CAST(pe.pass_attempts AS FLOAT64) AS pass_attempts,
  CAST(NULL AS FLOAT64) AS sacks,
  CAST(NULL AS FLOAT64) AS scrambles,
  CAST(NULL AS FLOAT64) AS designed_rushes,
  SAFE_DIVIDE(pe.passing_epa, NULLIF(pe.dropbacks, 0)) AS epa_per_dropback,
  pe.passing_epa,
  pe.cpoe,
  pe.adot,
  pe.deep_attempt_rate,
  CAST(NULL AS FLOAT64) AS sack_rate,
  CAST(NULL AS FLOAT64) AS scramble_rate,
  CAST(NULL AS FLOAT64) AS pass_rate_over_expected_context,
  TO_JSON_STRING(STRUCT(p.source_freshness_json AS player_week, t.source_freshness_json AS team_context)) AS source_freshness_json,
  TO_JSON_STRING(STRUCT(
    p.player_id_internal IS NULL AS missing_qb_identity,
    pe.dropbacks = 0 AS zero_dropback_denominator,
    pe.cpoe IS NULL AS cpoe_unavailable,
    pe.passing_epa IS NULL AS epa_unavailable,
    TRUE AS sack_field_unavailable,
    TRUE AS scramble_field_unavailable,
    TRUE AS designed_rush_split_unavailable,
    TRUE AS pass_rate_over_expected_unavailable
  )) AS missing_data_flags,
  CURRENT_TIMESTAMP() AS created_at
FROM passer_events pe
LEFT JOIN {pws} p
  ON pe.season = p.season
  AND pe.week = p.week
  AND pe.team = p.team
  AND pe.player_id_internal = p.player_id_internal
  AND p.position = 'QB'
LEFT JOIN {teams} t
  ON pe.season = t.season AND pe.week = t.week AND pe.team = t.team
"""


def _qb_week_diagnostics(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None, metric_version: str) -> str:
    sql = _qb_week_sql(project, dataset, season_start, season_end, week_start, week_end, metric_version)
    source_filter = _bounds_sql("", season_start, season_end, week_start, week_end)
    return f"""
WITH planned AS ({sql})
SELECT
  COUNT(1) AS planned_row_count,
  (SELECT COUNT(1) FROM {_table(project, dataset, "stg_play_player_events")} WHERE {source_filter} AND event_type = 'passer') AS source_row_count,
  (
    SELECT COUNT(1)
    FROM (
      SELECT metric_version, season, week, qb_player_id_internal, team, COUNT(1) AS row_count
      FROM planned
      GROUP BY 1, 2, 3, 4, 5
      HAVING row_count > 1
    )
  ) AS duplicate_key_count,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.missing_qb_identity') = 'true') AS missing_qb_identity_count,
  COUNTIF(dropbacks IS NULL OR dropbacks = 0) AS null_dropback_count,
  COUNTIF(cpoe IS NOT NULL) AS cpoe_coverage_count,
  COUNTIF(passing_epa IS NOT NULL) AS epa_coverage_count,
  COUNTIF(deep_attempt_rate IS NOT NULL) AS deep_attempt_coverage_count,
  COUNTIF(sacks IS NULL) AS sack_field_unavailable_count,
  COUNTIF(scrambles IS NULL) AS scramble_field_unavailable_count,
  COUNTIF(source_freshness_json IS NULL) AS missing_source_freshness_count,
  COUNTIF(missing_data_flags IS NULL) AS missing_flags_count
FROM planned
"""


def _current_placeholder_sql(project: str, dataset: str, target: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    source_filter = _bounds_sql("p", season_start, season_end, week_start, week_end)
    return f"""
SELECT
  '{target}' AS target,
  'requires player_week_advanced_metrics base rows before rolling current materialization' AS plan_note,
  COUNT(1) AS available_base_rows,
  MIN(p.season) AS min_base_season,
  MAX(p.season) AS max_base_season
FROM {_table(project, dataset, "player_week_advanced_metrics")} p
WHERE {source_filter}
"""


def _current_placeholder_diagnostics(project: str, dataset: str, target: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    sql = _current_placeholder_sql(project, dataset, target, season_start, season_end, week_start, week_end)
    return f"""
WITH placeholder AS ({sql})
SELECT
  0 AS planned_row_count,
  available_base_rows AS source_row_count,
  0 AS duplicate_key_count,
  available_base_rows AS base_rows_available,
  IF(available_base_rows = 0, 1, 0) AS missing_base_rows,
  'requires player_week_advanced_metrics base rows first; rolling windows planned for season-to-date, last 3, last 5, and last 8' AS placeholder_note
FROM placeholder
"""


def build_target_plan(
    target: str,
    project: str,
    dataset: str,
    season_start: int,
    season_end: int,
    week_start: int | None,
    week_end: int | None,
    metric_version: str = DEFAULT_METRIC_VERSION,
) -> TargetPlan:
    if target == "player_week_advanced_metrics":
        return TargetPlan(
            target=target,
            source_tables=("stg_player_week_stats", "stg_play_player_events", "stg_team_week_stats", "stg_participation_context", "stg_player_identity"),
            sql=_player_week_sql(project, dataset, season_start, season_end, week_start, week_end, metric_version),
            diagnostic_sql=_player_week_diagnostics(project, dataset, season_start, season_end, week_start, week_end, metric_version),
            warnings=("Route metrics and red-zone/high-value-touch metrics are blocked in v0.",),
            blocked_metrics=STATIC_BLOCKED_METRICS,
        )
    if target == "team_week_context_metrics":
        return TargetPlan(
            target=target,
            source_tables=("stg_team_week_stats", "stg_game_context"),
            sql=_team_week_sql(project, dataset, season_start, season_end, week_start, week_end, metric_version),
            diagnostic_sql=_team_week_diagnostics(project, dataset, season_start, season_end, week_start, week_end, metric_version),
            warnings=("seconds_per_play, pass_rate_over_expected, pass/rush EPA split, and red-zone rates remain null pending source-field review.",),
            blocked_metrics=("seconds_per_play", "pass_rate_over_expected", "pass_epa_per_play", "rush_epa_per_play", "red_zone_pass_rate", "red_zone_rush_rate"),
        )
    if target == "qb_week_environment_metrics":
        return TargetPlan(
            target=target,
            source_tables=("stg_play_player_events", "stg_player_week_stats", "stg_team_week_stats", "stg_player_identity"),
            sql=_qb_week_sql(project, dataset, season_start, season_end, week_start, week_end, metric_version),
            diagnostic_sql=_qb_week_diagnostics(project, dataset, season_start, season_end, week_start, week_end, metric_version),
            warnings=("Sack, scramble, designed-rush, and pass-rate-over-expected fields are unavailable in v0.",),
            blocked_metrics=("sacks", "scrambles", "designed_rushes", "sack_rate", "scramble_rate", "pass_rate_over_expected_context"),
        )
    if target in CURRENT_TARGETS:
        return TargetPlan(
            target=target,
            source_tables=("player_week_advanced_metrics",),
            sql=_current_placeholder_sql(project, dataset, target, season_start, season_end, week_start, week_end),
            diagnostic_sql=_current_placeholder_diagnostics(project, dataset, target, season_start, season_end, week_start, week_end),
            warnings=("Current rolling metrics are placeholders until base player_week_advanced_metrics rows exist.",),
            blocked_metrics=("season_to_date", "last_3", "last_5", "last_8"),
        )
    raise AdvancedMetricsPlanError(f"Unknown advanced metrics target: {target}")


def _row_to_dict(row: Any) -> dict[str, Any]:
    if hasattr(row, "items"):
        return dict(row.items())
    if hasattr(row, "_asdict"):
        return dict(row._asdict())
    return dict(row)


def query_one(client: Any, sql: str) -> dict[str, Any]:
    rows = list(client.query(sql).result())
    if not rows:
        return {}
    return _row_to_dict(rows[0])


def query_many(client: Any, sql: str) -> list[dict[str, Any]]:
    return [_row_to_dict(row) for row in client.query(sql).result()]


def _null_safe_equals(left: str, right: str) -> str:
    return f"({left} = {right} OR ({left} IS NULL AND {right} IS NULL))"


def build_merge_sql(plan: TargetPlan, project: str, dataset: str) -> str:
    if plan.target not in TARGET_COLUMNS or plan.target not in TARGET_GRAINS:
        raise AdvancedMetricsPlanError(f"Unsupported advanced metrics write target: {plan.target}")
    source_sql = plan.sql.strip().rstrip(";")
    columns = TARGET_COLUMNS[plan.target]
    keys = TARGET_GRAINS[plan.target]
    on_clause = "\n  AND ".join(_null_safe_equals(f"T.`{key}`", f"S.`{key}`") for key in keys)
    update_columns = [column for column in columns if column not in keys]
    update_clause = ",\n    ".join(f"`{column}` = S.`{column}`" for column in update_columns)
    insert_columns = ", ".join(f"`{column}`" for column in columns)
    insert_values = ", ".join(f"S.`{column}`" for column in columns)
    return f"""
MERGE {_table(project, dataset, plan.target)} AS T
USING (
{source_sql}
) AS S
ON {on_clause}
WHEN MATCHED THEN UPDATE SET
    {update_clause}
WHEN NOT MATCHED THEN INSERT ({insert_columns})
VALUES ({insert_values})
"""


def _assert_safe_write_plan(plan: TargetPlan) -> None:
    if plan.target not in BASE_TARGETS:
        raise AdvancedMetricsPlanError(f"Blocked non-base advanced metrics write target: {plan.target}")
    for source in plan.source_tables:
        if source not in STAGING_TABLES:
            raise AdvancedMetricsPlanError(f"Blocked non-staging feature source for {plan.target}: {source}")
    for blocked in BLOCKED_TABLES:
        if blocked in plan.sql:
            raise AdvancedMetricsPlanError(f"Blocked unsafe dependency in {plan.target} SQL: {blocked}")
    if any(token in plan.sql.upper() for token in ("INSERT ", "MERGE ", "DELETE ", "TRUNCATE")):
        raise AdvancedMetricsPlanError(f"Blocked write token inside source SELECT for {plan.target}.")


def _post_write_sql(plan: TargetPlan, project: str, dataset: str, season_start: int, season_end: int, metric_version: str) -> str:
    keys = TARGET_GRAINS[plan.target]
    key_select = ", ".join(f"`{key}`" for key in keys)
    return f"""
WITH duplicate_keys AS (
  SELECT {key_select}, COUNT(1) AS row_count
  FROM {_table(project, dataset, plan.target)}
  WHERE season BETWEEN {season_start} AND {season_end}
    AND metric_version = '{metric_version}'
  GROUP BY {key_select}
  HAVING row_count > 1
)
SELECT
  COUNT(1) AS bounded_row_count,
  COUNTIF(season = 2014) AS rows_2014,
  MIN(season) AS min_season,
  MAX(season) AS max_season,
  MIN(week) AS min_week,
  MAX(week) AS max_week,
  COUNT(DISTINCT metric_version) AS metric_version_count,
  COUNT(DISTINCT feature_run_id) AS feature_run_id_count,
  COUNTIF(source_freshness_json IS NULL) AS missing_source_freshness_rows,
  COUNTIF(missing_data_flags IS NULL) AS missing_flags_rows,
  (SELECT COUNT(1) FROM duplicate_keys) AS duplicate_key_count
FROM {_table(project, dataset, plan.target)}
WHERE season BETWEEN {season_start} AND {season_end}
  AND metric_version = '{metric_version}'
"""


def write_target(client: Any, plan: TargetPlan, project: str, dataset: str, season_start: int, season_end: int, metric_version: str) -> dict[str, Any]:
    _assert_safe_write_plan(plan)
    merge_sql = build_merge_sql(plan, project, dataset)
    job = client.query(merge_sql)
    list(job.result())
    verification = query_one(client, _post_write_sql(plan, project, dataset, season_start, season_end, metric_version))
    return {
        "target": plan.target,
        "write_sql_kind": "MERGE",
        "dml_affected_rows": getattr(job, "num_dml_affected_rows", None),
        "post_write": verification,
    }


def _sql_contains_blocked_dependency(sql: str) -> bool:
    return any(blocked in sql for blocked in BLOCKED_TABLES)


def readiness_from_diagnostics(target: str, diagnostics: dict[str, Any], warnings: list[str]) -> str:
    planned_rows = int(diagnostics.get("planned_row_count") or 0)
    duplicate_count = int(diagnostics.get("duplicate_key_count") or 0)
    if duplicate_count:
        return "blocked"
    if target in CURRENT_TARGETS:
        return "blocked" if int(diagnostics.get("base_rows_available") or 0) == 0 else "ready with warnings"
    if planned_rows == 0:
        return "blocked"
    if warnings:
        return "ready with warnings"
    return "ready"


def metric_availability_matrix(audit_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_field = {row.get("field_name"): row for row in audit_rows}
    return [
        {"metric": "target_share", "status": "safe", "source": "stg_player_week_stats.targets / stg_team_week_stats.team_targets"},
        {"metric": "air_yards_share", "status": "safe", "source": "stg_player_week_stats.air_yards / stg_team_week_stats.team_air_yards"},
        {"metric": "wopr", "status": "safe", "source": "1.5 * target_share + 0.7 * air_yards_share"},
        {"metric": "snap_share", "status": "safe_with_identity_warnings", "source": "stg_participation_context.offense_pct"},
        {"metric": "epa_per_opportunity", "status": "safe_with_denominator_flags", "source": "stg_play_player_events.epa"},
        {"metric": "cpoe", "status": "safe_with_nulls", "source": "stg_play_player_events.cpoe"},
        {"metric": "route_share", "status": "blocked", "source": "no true route source"},
        {"metric": "red_zone_touches", "status": "blocked", "source": by_field.get("stg_play_player_events.red_zone_flag", {}).get("v0_status", "blocked")},
        {"metric": "touchdown_rates", "status": "blocked", "source": by_field.get("stg_play_player_events.touchdown", {}).get("v0_status", "blocked")},
        {"metric": "reception_flag_dependent_metrics", "status": "blocked", "source": by_field.get("stg_play_player_events.reception", {}).get("v0_status", "blocked")},
    ]


def build_summary(
    args: argparse.Namespace,
    *,
    client_factory: Callable[[], Any] | None = None,
    run_diagnostics: bool = True,
) -> dict[str, Any]:
    validate_request(args)
    targets = selected_targets(args)
    plans = [
        build_target_plan(target, args.project, args.dataset, args.season_start, args.season_end, args.week_start, args.week_end, args.metric_version)
        for target in targets
    ]
    for plan in plans:
        if plan.target in BASE_TARGETS and _sql_contains_blocked_dependency(plan.sql):
            raise AdvancedMetricsPlanError(f"Blocked unsafe dependency in {plan.target} SQL.")

    client = None
    source_field_audit: list[dict[str, Any]] = []
    if run_diagnostics or args.write:
        if client_factory is None:
            from google.cloud import bigquery

            client_factory = lambda: bigquery.Client(project=args.project)
        client = client_factory()
        if not args.write:
            source_field_audit = query_many(
                client,
                source_field_audit_sql(args.project, args.dataset, args.season_start, args.season_end, args.week_start, args.week_end),
            )

    target_summaries = []
    for plan in plans:
        diagnostics: dict[str, Any] = {}
        errors: list[str] = []
        if run_diagnostics and client is not None:
            try:
                diagnostics = query_one(client, plan.diagnostic_sql)
            except Exception as exc:
                errors.append(f"{type(exc).__name__}: {exc}")
                if args.strict:
                    raise
        warnings = list(plan.warnings)
        if errors:
            warnings.extend(errors)
        readiness = readiness_from_diagnostics(plan.target, diagnostics, warnings)
        target_summaries.append(
            {
                "target": plan.target,
                "source_tables": list(plan.source_tables),
                "planned_sql": plan.sql.strip(),
                "diagnostic_sql": plan.diagnostic_sql.strip(),
                "diagnostics": diagnostics,
                "planned_row_count": diagnostics.get("planned_row_count"),
                "source_row_count": diagnostics.get("source_row_count"),
                "duplicate_key_count": diagnostics.get("duplicate_key_count"),
                "blocked_metrics": list(plan.blocked_metrics),
                "warnings": warnings,
                "recommended_write_readiness": readiness,
            }
        )
    write_results: list[dict[str, Any]] = []
    if args.write:
        if client is None:
            raise AdvancedMetricsPlanError("A BigQuery client is required for advanced metrics writes.")
        for plan, target_summary in zip(plans, target_summaries):
            if target_summary["recommended_write_readiness"] == "blocked":
                raise AdvancedMetricsPlanError(f"{plan.target} is blocked and will not be written.")
            if int(target_summary.get("duplicate_key_count") or 0) != 0:
                raise AdvancedMetricsPlanError(f"{plan.target} has duplicate planned grain rows and will not be written.")
            write_results.append(
                write_target(client, plan, args.project, args.dataset, args.season_start, args.season_end, args.metric_version)
            )
        results_by_target = {result["target"]: result for result in write_results}
        for target_summary in target_summaries:
            target_summary["write_result"] = results_by_target.get(target_summary["target"])

    return {
        "dry_run": not args.write,
        "wrote": args.write,
        "phase": "29.10" if args.write else "29.9",
        "future_write_gate": ADVANCED_METRICS_GATE,
        "selected_targets": targets,
        "season_start": args.season_start,
        "season_end": args.season_end,
        "week_start": args.week_start,
        "week_end": args.week_end,
        "metric_version": args.metric_version,
        "project": args.project,
        "dataset": args.dataset,
        "source_field_audit": source_field_audit,
        "metric_availability_matrix": metric_availability_matrix(source_field_audit),
        "blocked_metrics": list(STATIC_BLOCKED_METRICS),
        "target_summaries": target_summaries,
        "write_results": write_results,
        "warnings": [
            (
                "Phase 29.10 base advanced metrics writes were authorized by ALLOW_ADVANCED_METRICS_MATERIALIZATION."
                if args.write
                else "Phase 29.9 is dry-run only. Feature writes require a separate authorized Phase 29.10."
            ),
            "Feature SQL for base targets uses staging tables, not legacy or raw source tables.",
            "Pigskin packet refresh remains out of scope.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = build_summary(args)
    except AdvancedMetricsPlanError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    output = json.dumps(summary, indent=2, sort_keys=True, default=str)
    if args.output_json:
        Path(args.output_json).write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
