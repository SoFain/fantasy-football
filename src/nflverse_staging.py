"""Planner and gated writer for nflverse staging transforms.

The default mode is read-only. Live staging writes are reserved for explicit
Phase 29.8 authorization and are limited to canonical stg_* targets.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from src.nflverse_backfill_plan import DEFAULT_DATASET, DEFAULT_PROJECT


STAGING_MATERIALIZATION_GATE = "ALLOW_NFLVERSE_STAGING_MATERIALIZATION"
TARGETS = (
    "stg_player_identity",
    "stg_game_context",
    "stg_player_week_stats",
    "stg_team_week_stats",
    "stg_play_player_events",
    "stg_participation_context",
)
LEGACY_TABLES = (
    "play_by_play",
    "weekly_metrics",
    "player_rosters",
    "team_descriptions",
    "weekly_snap_counts",
)
FEATURE_TABLES = (
    "player_week_advanced_metrics",
    "team_week_context_metrics",
    "qb_week_environment_metrics",
    "pigskin_player_context_packet_current",
    "compat_pigskin_player_context_current",
)
TARGET_COLUMNS = {
    "stg_player_identity": (
        "player_id_internal",
        "nflverse_player_id",
        "gsis_id",
        "sleeper_player_id",
        "fantasy_player_id",
        "player_name",
        "normalized_player_name",
        "position",
        "team",
        "season",
        "week",
        "identity_confidence",
        "identity_source_json",
        "source_freshness_json",
        "missing_data_flags",
        "source_refresh_id",
        "created_at",
    ),
    "stg_game_context": (
        "season",
        "week",
        "game_id",
        "game_date",
        "home_team",
        "away_team",
        "stadium",
        "roof",
        "surface",
        "temp",
        "wind",
        "total_line",
        "spread_line",
        "source_freshness_json",
        "missing_data_flags",
        "source_refresh_id",
        "created_at",
    ),
    "stg_player_week_stats": (
        "season",
        "week",
        "player_id_internal",
        "nflverse_player_id",
        "gsis_id",
        "player_name",
        "position",
        "team",
        "opponent_team",
        "targets",
        "carries",
        "air_yards",
        "receiving_yards",
        "rushing_yards",
        "passing_yards",
        "receptions",
        "passing_tds",
        "rushing_tds",
        "receiving_tds",
        "source_freshness_json",
        "missing_data_flags",
        "source_refresh_id",
        "created_at",
    ),
    "stg_team_week_stats": (
        "season",
        "week",
        "team",
        "opponent_team",
        "plays",
        "pass_attempts",
        "rush_attempts",
        "team_targets",
        "team_air_yards",
        "epa_total",
        "epa_per_play",
        "success_rate",
        "neutral_pass_rate",
        "pass_rate_over_expected",
        "red_zone_pass_rate",
        "red_zone_rush_rate",
        "opponent_epa_allowed",
        "opponent_pass_epa_allowed",
        "opponent_rush_epa_allowed",
        "source_freshness_json",
        "missing_data_flags",
        "source_refresh_id",
        "created_at",
    ),
    "stg_play_player_events": (
        "season",
        "week",
        "game_id",
        "play_id",
        "event_type",
        "player_id_internal",
        "nflverse_player_id",
        "gsis_id",
        "team",
        "opponent_team",
        "posteam",
        "defteam",
        "yardline_100",
        "game_seconds_remaining",
        "score_differential",
        "epa",
        "success",
        "cpoe",
        "air_yards",
        "yards_gained",
        "pass_attempt",
        "rush_attempt",
        "target",
        "reception",
        "touchdown",
        "red_zone_flag",
        "inside_10_flag",
        "inside_5_flag",
        "source_freshness_json",
        "missing_data_flags",
        "source_refresh_id",
        "created_at",
    ),
    "stg_participation_context": (
        "season",
        "week",
        "game_id",
        "player_id_internal",
        "player_name",
        "position",
        "team",
        "offense_snaps",
        "offense_pct",
        "defense_snaps",
        "st_snaps",
        "participation_json",
        "has_true_route_source",
        "route_share",
        "source_freshness_json",
        "missing_data_flags",
        "source_refresh_id",
        "created_at",
    ),
}
TARGET_GRAINS = {
    "stg_player_identity": ("player_id_internal", "season", "week", "team"),
    "stg_game_context": ("season", "week", "game_id"),
    "stg_player_week_stats": ("season", "week", "player_id_internal", "team"),
    "stg_team_week_stats": ("season", "week", "team"),
    "stg_play_player_events": ("season", "week", "game_id", "play_id", "event_type", "player_id_internal", "team"),
    "stg_participation_context": ("season", "week", "game_id", "player_id_internal", "team"),
}


class StagingPlanError(RuntimeError):
    """Raised for unsafe staging planner requests."""


@dataclass(frozen=True)
class TargetPlan:
    target: str
    source_tables: tuple[str, ...]
    sql: str
    diagnostic_sql: str
    warnings: tuple[str, ...]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dry-run nflverse staging transform planner.")
    parser.add_argument("--dry-run", action="store_true", help="Build SQL and run read-only diagnostics. Default.")
    parser.add_argument("--plan-only", action="store_true", help="Alias for dry-run planning.")
    parser.add_argument("--write", action="store_true", help="Blocked in Phase 29.7.")
    parser.add_argument("--target", action="append", choices=TARGETS, help="Staging target to include. May be repeated.")
    parser.add_argument("--all-targets", action="store_true", help="Plan all staging targets.")
    parser.add_argument("--season-start", type=int, required=True)
    parser.add_argument("--season-end", type=int, required=True)
    parser.add_argument("--week-start", type=int)
    parser.add_argument("--week-end", type=int)
    parser.add_argument("--project", default=os.environ.get("BQ_PROJECT") or DEFAULT_PROJECT)
    parser.add_argument("--dataset", default=os.environ.get("BQ_DATASET") or DEFAULT_DATASET)
    parser.add_argument("--output-json", help="Optional path for the JSON dry-run summary.")
    parser.add_argument("--strict", action="store_true", help="Fail when a target diagnostic query fails.")
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


def identity_candidate_cte(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    roster_filter = _bounds_sql("rw", season_start, season_end, week_start, week_end)
    return f"""
ff_bridge AS (
  SELECT
    nflverse_player_id,
    ARRAY_AGG(gsis_id IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS gsis_id,
    ARRAY_AGG(sleeper_player_id IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS sleeper_player_id,
    ARRAY_AGG(fantasy_player_id IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS fantasy_player_id,
    ARRAY_AGG(JSON_VALUE(raw_payload_json, '$.pfr_id') IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS pfr_id,
    ARRAY_AGG(player_name IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS player_name
  FROM {_table(project, dataset, "raw_nflverse_ff_playerids")}
  GROUP BY nflverse_player_id
),
raw_player_bridge AS (
  SELECT
    nflverse_player_id,
    gsis_id,
    sleeper_player_id,
    fantasy_player_id,
    JSON_VALUE(raw_payload_json, '$.pfr_id') AS pfr_id,
    player_name,
    normalized_player_name,
    position,
    latest_team
  FROM {_table(project, dataset, "raw_nflverse_players")}
),
identity_candidates AS (
  SELECT
    COALESCE(rw.player_id, rw.gsis_id, p.gsis_id, f.gsis_id, p.nflverse_player_id, f.nflverse_player_id) AS player_id_internal,
    COALESCE(p.nflverse_player_id, f.nflverse_player_id, rw.player_id) AS nflverse_player_id,
    COALESCE(rw.gsis_id, p.gsis_id, f.gsis_id, rw.player_id) AS gsis_id,
    COALESCE(p.sleeper_player_id, f.sleeper_player_id) AS sleeper_player_id,
    COALESCE(p.fantasy_player_id, f.fantasy_player_id) AS fantasy_player_id,
    COALESCE(rw.player_name, p.player_name, f.player_name) AS player_name,
    COALESCE(
      p.normalized_player_name,
      LOWER(REGEXP_REPLACE(TRIM(COALESCE(rw.player_name, p.player_name, f.player_name)), r'[^a-z0-9]+', ' '))
    ) AS normalized_player_name,
    COALESCE(rw.position, p.position) AS position,
    COALESCE(rw.team, p.latest_team) AS team,
    rw.season,
    rw.week,
    COALESCE(p.pfr_id, f.pfr_id) AS pfr_id,
    CASE
      WHEN COALESCE(rw.gsis_id, p.gsis_id, f.gsis_id, rw.player_id) IS NOT NULL THEN 0.95
      WHEN COALESCE(p.nflverse_player_id, f.nflverse_player_id) IS NOT NULL THEN 0.85
      ELSE 0.60
    END AS identity_confidence,
    TO_JSON_STRING(STRUCT(
      'rosters_weekly' AS primary_source,
      p.nflverse_player_id AS raw_players_nflverse_player_id,
      f.nflverse_player_id AS ff_playerids_nflverse_player_id,
      COALESCE(p.pfr_id, f.pfr_id) AS pfr_id,
      TRUE AS no_name_only_join
    )) AS identity_source_json,
    TO_JSON_STRING(STRUCT(
      MAX(rw.loaded_at) OVER () AS latest_raw_loaded_at,
      'raw_nflverse_rosters_weekly' AS freshness_source
    )) AS source_freshness_json,
    TO_JSON_STRING(STRUCT(
      COALESCE(rw.player_id, rw.gsis_id, p.gsis_id, f.gsis_id, p.nflverse_player_id, f.nflverse_player_id) IS NULL AS missing_player_id,
      COALESCE(rw.position, p.position) IS NULL AS missing_position,
      COALESCE(rw.team, p.latest_team) IS NULL AS missing_team,
      COALESCE(p.pfr_id, f.pfr_id) IS NULL AS missing_pfr_id
    )) AS missing_data_flags,
    rw.source_refresh_id AS source_refresh_id,
    CURRENT_TIMESTAMP() AS created_at
  FROM {_table(project, dataset, "raw_nflverse_rosters_weekly")} rw
  LEFT JOIN raw_player_bridge p
    ON rw.gsis_id = p.gsis_id OR rw.player_id = p.gsis_id OR rw.player_id = p.nflverse_player_id
  LEFT JOIN ff_bridge f
    ON rw.gsis_id = f.gsis_id OR rw.player_id = f.gsis_id OR rw.player_id = f.nflverse_player_id
  WHERE {roster_filter}
)
"""


def _identity_select(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    cte = identity_candidate_cte(project, dataset, season_start, season_end, week_start, week_end)
    return f"""
WITH {cte}
SELECT
  player_id_internal,
  nflverse_player_id,
  gsis_id,
  sleeper_player_id,
  fantasy_player_id,
  player_name,
  normalized_player_name,
  position,
  team,
  season,
  week,
  identity_confidence,
  identity_source_json,
  source_freshness_json,
  missing_data_flags,
  source_refresh_id,
  created_at
FROM identity_candidates
WHERE player_id_internal IS NOT NULL
"""


def _identity_diagnostics(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    sql = _identity_select(project, dataset, season_start, season_end, week_start, week_end)
    roster_filter = _bounds_sql("", season_start, season_end, week_start, week_end)
    return f"""
WITH planned AS ({sql})
SELECT
  (SELECT COUNT(1) FROM planned) AS planned_row_count,
  (SELECT COUNT(1) FROM {_table(project, dataset, "raw_nflverse_players")}) AS unique_raw_players,
  (SELECT COUNT(DISTINCT gsis_id) FROM {_table(project, dataset, "raw_nflverse_players")} WHERE gsis_id IS NOT NULL) AS unique_gsis_ids,
  (SELECT COUNT(DISTINCT JSON_VALUE(raw_payload_json, '$.pfr_id')) FROM {_table(project, dataset, "raw_nflverse_players")} WHERE JSON_VALUE(raw_payload_json, '$.pfr_id') IS NOT NULL) AS unique_pfr_ids,
  (SELECT COUNT(DISTINCT sleeper_player_id) FROM {_table(project, dataset, "raw_nflverse_ff_playerids")} WHERE sleeper_player_id IS NOT NULL) AS unique_sleeper_ids,
  (SELECT COUNT(DISTINCT player_id) FROM {_table(project, dataset, "raw_nflverse_rosters")} WHERE {roster_filter}) AS raw_roster_ids,
  (SELECT COUNT(DISTINCT player_id) FROM {_table(project, dataset, "raw_nflverse_rosters_weekly")} WHERE {roster_filter}) AS weekly_roster_ids,
  COUNTIF(position IS NULL) AS missing_position_count,
  COUNTIF(team IS NULL) AS missing_team_count,
  COUNTIF(identity_confidence >= 0.95) AS high_confidence_rows,
  COUNTIF(identity_confidence < 0.95) AS lower_confidence_rows,
  (
    SELECT COUNT(1)
    FROM (
      SELECT player_id_internal, season, week, team, COUNT(1) AS row_count
      FROM planned
      GROUP BY 1, 2, 3, 4
      HAVING row_count > 1
    )
  ) AS duplicate_key_count,
  COUNTIF(player_id_internal IS NULL) AS ambiguous_identity_count
FROM planned
"""


def _game_context_select(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    source_filter = _bounds_sql("s", season_start, season_end, week_start, week_end)
    return f"""
SELECT
  s.season,
  s.week,
  s.game_id,
  s.game_date,
  s.home_team,
  s.away_team,
  s.stadium,
  s.roof,
  s.surface,
  s.temp,
  s.wind,
  s.total_line,
  s.spread_line,
  TO_JSON_STRING(STRUCT(s.loaded_at AS latest_raw_loaded_at, s.source_loader AS source_loader)) AS source_freshness_json,
  TO_JSON_STRING(STRUCT(
    s.home_team IS NULL AS missing_home_team,
    s.away_team IS NULL AS missing_away_team,
    s.game_date IS NULL AS missing_game_date,
    s.stadium IS NULL AS missing_stadium,
    s.roof IS NULL AS missing_roof,
    s.surface IS NULL AS missing_surface,
    s.total_line IS NULL AS missing_total_line,
    s.spread_line IS NULL AS missing_spread_line
  )) AS missing_data_flags,
  s.source_refresh_id,
  CURRENT_TIMESTAMP() AS created_at
FROM {_table(project, dataset, "raw_nflverse_schedules")} s
WHERE {source_filter}
"""


def _game_context_diagnostics(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    sql = _game_context_select(project, dataset, season_start, season_end, week_start, week_end)
    return f"""
WITH planned AS ({sql})
SELECT
  COUNT(1) AS planned_row_count,
  COUNT(1) AS source_row_count,
  COUNTIF(home_team IS NULL OR away_team IS NULL) AS missing_team_count,
  COUNTIF(game_date IS NULL) AS missing_game_date_count,
  COUNTIF(stadium IS NULL) AS missing_stadium_count,
  COUNTIF(roof IS NULL) AS missing_roof_count,
  COUNTIF(surface IS NULL) AS missing_surface_count,
  COUNTIF(total_line IS NULL) AS missing_total_line_count,
  COUNTIF(spread_line IS NULL) AS missing_spread_line_count,
  (
    SELECT COUNT(1)
    FROM (
      SELECT season, week, game_id, COUNT(1) AS row_count
      FROM planned
      GROUP BY 1, 2, 3
      HAVING row_count > 1
    )
  ) AS duplicate_key_count
FROM planned
"""


def _player_week_select(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    weekly_filter = _bounds_sql("w", season_start, season_end, week_start, week_end)
    cte = identity_candidate_cte(project, dataset, season_start, season_end, week_start, week_end)
    return f"""
WITH {cte}
SELECT
  w.season,
  w.week,
  COALESCE(i.player_id_internal, w.player_id) AS player_id_internal,
  i.nflverse_player_id,
  COALESCE(i.gsis_id, w.player_id) AS gsis_id,
  w.player_name,
  COALESCE(w.position, i.position) AS position,
  w.team,
  w.opponent_team,
  w.targets,
  w.carries,
  w.air_yards,
  w.receiving_yards,
  w.rushing_yards,
  w.passing_yards,
  w.receptions,
  w.passing_tds,
  w.rushing_tds,
  w.receiving_tds,
  TO_JSON_STRING(STRUCT(w.loaded_at AS latest_raw_loaded_at, w.source_loader AS source_loader)) AS source_freshness_json,
  TO_JSON_STRING(STRUCT(
    i.player_id_internal IS NULL AS missing_identity_match,
    w.team IS NULL AS missing_team,
    COALESCE(w.position, i.position) IS NULL AS missing_position,
    w.week >= 19 AS postseason_or_playoff_week
  )) AS missing_data_flags,
  w.source_refresh_id,
  CURRENT_TIMESTAMP() AS created_at
FROM {_table(project, dataset, "raw_nflverse_weekly")} w
LEFT JOIN identity_candidates i
  ON w.season = i.season
  AND w.week = i.week
  AND w.team = i.team
  AND (w.player_id = i.player_id_internal OR w.player_id = i.gsis_id OR w.player_id = i.nflverse_player_id)
WHERE {weekly_filter}
  AND w.player_id IS NOT NULL
"""


def _player_week_diagnostics(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    sql = _player_week_select(project, dataset, season_start, season_end, week_start, week_end)
    source_filter = _bounds_sql("", season_start, season_end, week_start, week_end)
    return f"""
WITH planned AS ({sql})
SELECT
  COUNT(1) AS planned_row_count,
  (SELECT COUNT(1) FROM {_table(project, dataset, "raw_nflverse_weekly")} WHERE {source_filter}) AS source_row_count,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.missing_identity_match') = 'true') AS missing_identity_count,
  COUNTIF(team IS NULL) AS missing_team_count,
  COUNTIF(position IS NULL) AS missing_position_count,
  COUNTIF(week >= 19) AS postseason_week_rows,
  COUNTIF(targets IS NOT NULL OR carries IS NOT NULL OR passing_yards IS NOT NULL OR receiving_yards IS NOT NULL OR rushing_yards IS NOT NULL) AS fantasy_stat_input_rows,
  (
    SELECT COUNT(1)
    FROM (
      SELECT season, week, player_id_internal, team, COUNT(1) AS row_count
      FROM planned
      GROUP BY 1, 2, 3, 4
      HAVING row_count > 1
    )
  ) AS duplicate_key_count
FROM planned
"""


def _team_week_select(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    pbp_filter = _bounds_sql("p", season_start, season_end, week_start, week_end)
    return f"""
WITH team_plays AS (
  SELECT
    p.season,
    p.week,
    p.posteam AS team,
    p.defteam AS opponent_team,
    COUNT(1) AS plays,
    COUNTIF(p.play_type = 'pass') AS pass_attempts,
    COUNTIF(p.play_type = 'run') AS rush_attempts,
    COUNTIF(p.receiver_player_id IS NOT NULL) AS team_targets,
    SUM(p.air_yards) AS team_air_yards,
    SUM(p.epa) AS epa_total,
    AVG(p.epa) AS epa_per_play,
    AVG(p.success) AS success_rate,
    SAFE_DIVIDE(COUNTIF(p.play_type = 'pass' AND ABS(COALESCE(p.score_differential, 0)) <= 7 AND p.game_seconds_remaining BETWEEN 120 AND 3300), COUNTIF(ABS(COALESCE(p.score_differential, 0)) <= 7 AND p.game_seconds_remaining BETWEEN 120 AND 3300)) AS neutral_pass_rate,
    CAST(NULL AS FLOAT64) AS pass_rate_over_expected,
    SAFE_DIVIDE(COUNTIF(p.red_zone_flag AND p.play_type = 'pass'), COUNTIF(p.red_zone_flag)) AS red_zone_pass_rate,
    SAFE_DIVIDE(COUNTIF(p.red_zone_flag AND p.play_type = 'run'), COUNTIF(p.red_zone_flag)) AS red_zone_rush_rate,
    MAX(p.source_refresh_id) AS source_refresh_id,
    MAX(p.loaded_at) AS latest_loaded_at
  FROM {_table(project, dataset, "raw_nflverse_pbp")} p
  WHERE {pbp_filter}
    AND p.posteam IS NOT NULL
  GROUP BY 1, 2, 3, 4
),
opponent_allowed AS (
  SELECT
    season,
    week,
    opponent_team AS team,
    AVG(epa_per_play) AS opponent_epa_allowed,
    AVG(SAFE_DIVIDE(epa_total, NULLIF(pass_attempts, 0))) AS opponent_pass_epa_allowed,
    AVG(SAFE_DIVIDE(epa_total, NULLIF(rush_attempts, 0))) AS opponent_rush_epa_allowed
  FROM team_plays
  GROUP BY 1, 2, 3
)
SELECT
  t.season,
  t.week,
  t.team,
  t.opponent_team,
  t.plays,
  t.pass_attempts,
  t.rush_attempts,
  t.team_targets,
  t.team_air_yards,
  t.epa_total,
  t.epa_per_play,
  t.success_rate,
  t.neutral_pass_rate,
  t.pass_rate_over_expected,
  t.red_zone_pass_rate,
  t.red_zone_rush_rate,
  o.opponent_epa_allowed,
  o.opponent_pass_epa_allowed,
  o.opponent_rush_epa_allowed,
  TO_JSON_STRING(STRUCT(t.latest_loaded_at AS latest_raw_loaded_at, 'raw_nflverse_pbp' AS freshness_source)) AS source_freshness_json,
  TO_JSON_STRING(STRUCT(t.plays = 0 AS zero_play_denominator, t.pass_rate_over_expected IS NULL AS pass_rate_over_expected_unavailable)) AS missing_data_flags,
  t.source_refresh_id,
  CURRENT_TIMESTAMP() AS created_at
FROM team_plays t
LEFT JOIN opponent_allowed o
  ON t.season = o.season AND t.week = o.week AND t.team = o.team
"""


def _team_week_diagnostics(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    sql = _team_week_select(project, dataset, season_start, season_end, week_start, week_end)
    source_filter = _bounds_sql("", season_start, season_end, week_start, week_end)
    return f"""
WITH planned AS ({sql})
SELECT
  COUNT(1) AS planned_row_count,
  (SELECT COUNT(1) FROM {_table(project, dataset, "raw_nflverse_pbp")} WHERE {source_filter}) AS source_row_count,
  SUM(plays) AS offense_play_count,
  SUM(pass_attempts) AS pass_attempts,
  SUM(rush_attempts) AS rush_attempts,
  SUM(team_targets) AS team_targets,
  SUM(team_air_yards) AS team_air_yards,
  SUM(epa_total) AS epa_total,
  AVG(success_rate) AS avg_success_rate,
  COUNTIF(neutral_pass_rate IS NOT NULL) AS neutral_script_rows,
  COUNTIF(red_zone_pass_rate IS NOT NULL OR red_zone_rush_rate IS NOT NULL) AS red_zone_rows,
  COUNTIF(opponent_epa_allowed IS NOT NULL) AS opponent_defensive_rows,
  (
    SELECT COUNT(1)
    FROM (
      SELECT season, week, team, COUNT(1) AS row_count
      FROM planned
      GROUP BY 1, 2, 3
      HAVING row_count > 1
    )
  ) AS duplicate_key_count
FROM planned
"""


def _play_events_select(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    pbp_filter = _bounds_sql("p", season_start, season_end, week_start, week_end)
    cte = identity_candidate_cte(project, dataset, season_start, season_end, week_start, week_end)
    event_template = """
  SELECT
    p.season,
    p.week,
    p.game_id,
    p.play_id,
    {event_type} AS event_type,
    {player_id} AS source_player_id,
    {team} AS team,
    {opponent_team} AS opponent_team,
    p.posteam,
    p.defteam,
    p.yardline_100,
    p.game_seconds_remaining,
    p.score_differential,
    p.epa,
    p.success,
    p.cpoe,
    p.air_yards,
    p.yards_gained,
    p.play_type = 'pass' AS pass_attempt,
    p.play_type = 'run' AS rush_attempt,
    {target_flag} AS target,
    {reception_flag} AS reception,
    {touchdown_flag} AS touchdown,
    p.red_zone_flag,
    p.inside_10_flag,
    p.inside_5_flag,
    p.source_refresh_id,
    p.loaded_at,
    p.source_loader
  FROM {pbp_table} p
  WHERE {pbp_filter} AND {where_clause}
"""
    pbp_table = _table(project, dataset, "raw_nflverse_pbp")
    parts = [
        event_template.format(event_type="'passer'", player_id="p.passer_player_id", team="p.posteam", opponent_team="p.defteam", target_flag="FALSE", reception_flag="FALSE", touchdown_flag="SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.pass_touchdown') AS INT64) = 1", pbp_table=pbp_table, pbp_filter=pbp_filter, where_clause="p.passer_player_id IS NOT NULL"),
        event_template.format(event_type="'receiver'", player_id="p.receiver_player_id", team="p.posteam", opponent_team="p.defteam", target_flag="p.play_type = 'pass'", reception_flag="SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.complete_pass') AS INT64) = 1", touchdown_flag="SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.pass_touchdown') AS INT64) = 1 OR SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.touchdown') AS INT64) = 1", pbp_table=pbp_table, pbp_filter=pbp_filter, where_clause="p.receiver_player_id IS NOT NULL"),
        event_template.format(event_type="'target'", player_id="p.receiver_player_id", team="p.posteam", opponent_team="p.defteam", target_flag="TRUE", reception_flag="SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.complete_pass') AS INT64) = 1", touchdown_flag="SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.pass_touchdown') AS INT64) = 1 OR SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.touchdown') AS INT64) = 1", pbp_table=pbp_table, pbp_filter=pbp_filter, where_clause="p.receiver_player_id IS NOT NULL AND p.play_type = 'pass'"),
        event_template.format(event_type="'rusher'", player_id="p.rusher_player_id", team="p.posteam", opponent_team="p.defteam", target_flag="FALSE", reception_flag="FALSE", touchdown_flag="SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.rush_touchdown') AS INT64) = 1 OR SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.touchdown') AS INT64) = 1", pbp_table=pbp_table, pbp_filter=pbp_filter, where_clause="p.rusher_player_id IS NOT NULL"),
        event_template.format(event_type="'reception'", player_id="p.receiver_player_id", team="p.posteam", opponent_team="p.defteam", target_flag="TRUE", reception_flag="TRUE", touchdown_flag="SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.pass_touchdown') AS INT64) = 1 OR SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.touchdown') AS INT64) = 1", pbp_table=pbp_table, pbp_filter=pbp_filter, where_clause="p.receiver_player_id IS NOT NULL AND SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.complete_pass') AS INT64) = 1"),
        event_template.format(event_type="'touchdown'", player_id="COALESCE(p.receiver_player_id, p.rusher_player_id, p.passer_player_id)", team="p.posteam", opponent_team="p.defteam", target_flag="p.receiver_player_id IS NOT NULL", reception_flag="SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.complete_pass') AS INT64) = 1", touchdown_flag="TRUE", pbp_table=pbp_table, pbp_filter=pbp_filter, where_clause="SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.touchdown') AS INT64) = 1 AND COALESCE(p.receiver_player_id, p.rusher_player_id, p.passer_player_id) IS NOT NULL"),
        event_template.format(event_type="'team_play'", player_id="CONCAT('TEAM:', p.posteam)", team="p.posteam", opponent_team="p.defteam", target_flag="FALSE", reception_flag="FALSE", touchdown_flag="SAFE_CAST(JSON_VALUE(p.raw_payload_json, '$.touchdown') AS INT64) = 1", pbp_table=pbp_table, pbp_filter=pbp_filter, where_clause="p.posteam IS NOT NULL"),
    ]
    union_sql = "\nUNION ALL\n".join(parts)
    return f"""
WITH {cte},
event_source AS (
{union_sql}
)
SELECT
  e.season,
  e.week,
  e.game_id,
  e.play_id,
  e.event_type,
  COALESCE(i.player_id_internal, e.source_player_id) AS player_id_internal,
  i.nflverse_player_id,
  COALESCE(i.gsis_id, e.source_player_id) AS gsis_id,
  e.team,
  e.opponent_team,
  e.posteam,
  e.defteam,
  e.yardline_100,
  e.game_seconds_remaining,
  e.score_differential,
  e.epa,
  e.success,
  e.cpoe,
  e.air_yards,
  e.yards_gained,
  e.pass_attempt,
  e.rush_attempt,
  e.target,
  e.reception,
  e.touchdown,
  e.red_zone_flag,
  e.inside_10_flag,
  e.inside_5_flag,
  TO_JSON_STRING(STRUCT(e.loaded_at AS latest_raw_loaded_at, e.source_loader AS source_loader)) AS source_freshness_json,
  TO_JSON_STRING(STRUCT(i.player_id_internal IS NULL AND NOT STARTS_WITH(e.source_player_id, 'TEAM:') AS missing_identity_match)) AS missing_data_flags,
  e.source_refresh_id,
  CURRENT_TIMESTAMP() AS created_at
FROM event_source e
LEFT JOIN identity_candidates i
  ON e.season = i.season
  AND e.week = i.week
  AND e.team = i.team
  AND (e.source_player_id = i.player_id_internal OR e.source_player_id = i.gsis_id OR e.source_player_id = i.nflverse_player_id)
"""


def _play_events_diagnostics(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    sql = _play_events_select(project, dataset, season_start, season_end, week_start, week_end)
    source_filter = _bounds_sql("", season_start, season_end, week_start, week_end)
    return f"""
WITH planned AS ({sql})
SELECT
  COUNT(1) AS planned_row_count,
  (SELECT COUNT(1) FROM {_table(project, dataset, "raw_nflverse_pbp")} WHERE {source_filter}) AS source_row_count,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.missing_identity_match') = 'true') AS missing_identity_count,
  COUNTIF(event_type = 'receiver') AS receiver_event_rows,
  COUNTIF(event_type = 'rusher') AS rusher_event_rows,
  COUNTIF(event_type = 'passer') AS passer_event_rows,
  COUNTIF(event_type = 'target') AS target_event_rows,
  COUNTIF(event_type = 'reception') AS reception_event_rows,
  COUNTIF(event_type = 'touchdown') AS touchdown_event_rows,
  COUNTIF(epa IS NOT NULL) AS epa_non_null_rows,
  COUNTIF(success IS NOT NULL) AS success_non_null_rows,
  COUNTIF(red_zone_flag) AS red_zone_event_rows,
  COUNTIF(inside_10_flag) AS inside_10_event_rows,
  COUNTIF(inside_5_flag) AS inside_5_event_rows,
  (
    SELECT COUNT(1)
    FROM (
      SELECT season, week, game_id, play_id, event_type, player_id_internal, team, COUNT(1) AS row_count
      FROM planned
      GROUP BY 1, 2, 3, 4, 5, 6, 7
      HAVING row_count > 1
    )
  ) AS duplicate_key_count
FROM planned
"""


def _participation_select(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    snap_filter = _bounds_sql("s", season_start, season_end, week_start, week_end)
    cte = identity_candidate_cte(project, dataset, season_start, season_end, week_start, week_end)
    return f"""
WITH {cte}
SELECT
  s.season,
  s.week,
  s.game_id,
  COALESCE(i.player_id_internal, s.player_id) AS player_id_internal,
  s.player_name,
  s.position,
  s.team,
  s.offense_snaps,
  s.offense_pct,
  s.defense_snaps,
  s.st_snaps,
  TO_JSON_STRING(STRUCT(
    s.offense_snaps AS offense_snaps,
    s.offense_pct AS offense_pct,
    s.defense_snaps AS defense_snaps,
    s.st_snaps AS st_snaps,
    s.player_id AS raw_pfr_player_id
  )) AS participation_json,
  FALSE AS has_true_route_source,
  CAST(NULL AS FLOAT64) AS route_share,
  TO_JSON_STRING(STRUCT(s.loaded_at AS latest_raw_loaded_at, s.source_loader AS source_loader)) AS source_freshness_json,
  TO_JSON_STRING(STRUCT(
    s.player_id IS NULL AS missing_raw_pfr_player_id,
    i.player_id_internal IS NULL AS missing_identity_match,
    TRUE AS route_share_blocked_without_true_route_source
  )) AS missing_data_flags,
  s.source_refresh_id,
  CURRENT_TIMESTAMP() AS created_at
FROM {_table(project, dataset, "raw_nflverse_snap_counts")} s
LEFT JOIN identity_candidates i
  ON s.season = i.season
  AND s.week = i.week
  AND s.team = i.team
  AND s.player_id = i.pfr_id
WHERE {snap_filter}
"""


def _participation_diagnostics(project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> str:
    sql = _participation_select(project, dataset, season_start, season_end, week_start, week_end)
    source_filter = _bounds_sql("", season_start, season_end, week_start, week_end)
    return f"""
WITH planned AS ({sql})
SELECT
  COUNT(1) AS planned_row_count,
  (SELECT COUNT(1) FROM {_table(project, dataset, "raw_nflverse_snap_counts")} WHERE {source_filter}) AS source_row_count,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.missing_identity_match') = 'true') AS missing_identity_count,
  COUNTIF(JSON_VALUE(participation_json, '$.raw_pfr_player_id') IS NOT NULL) AS rows_with_pfr_id,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.missing_identity_match') = 'false') AS rows_matched_by_pfr_id,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.missing_identity_match') = 'true') AS rows_unmatched_by_pfr_id,
  COUNTIF(offense_pct IS NOT NULL) AS offense_pct_rows,
  MIN(offense_pct) AS min_offense_pct,
  MAX(offense_pct) AS max_offense_pct,
  MIN(offense_snaps) AS min_offense_snaps,
  MAX(offense_snaps) AS max_offense_snaps,
  COUNTIF(route_share IS NOT NULL) AS route_share_non_null_rows,
  COUNTIF(has_true_route_source) AS true_route_source_rows,
  (
    SELECT COUNT(1)
    FROM (
      SELECT season, week, game_id, player_id_internal, team, COUNT(1) AS row_count
      FROM planned
      GROUP BY 1, 2, 3, 4, 5
      HAVING row_count > 1
    )
  ) AS duplicate_key_count
FROM planned
"""


def build_target_plan(target: str, project: str, dataset: str, season_start: int, season_end: int, week_start: int | None, week_end: int | None) -> TargetPlan:
    if target == "stg_player_identity":
        return TargetPlan(
            target=target,
            source_tables=("raw_nflverse_players", "raw_nflverse_ff_playerids", "raw_nflverse_rosters_weekly"),
            sql=_identity_select(project, dataset, season_start, season_end, week_start, week_end),
            diagnostic_sql=_identity_diagnostics(project, dataset, season_start, season_end, week_start, week_end),
            warnings=("No name-only identity joins are used.",),
        )
    if target == "stg_game_context":
        return TargetPlan(
            target=target,
            source_tables=("raw_nflverse_schedules", "raw_nflverse_teams", "raw_nflverse_pbp"),
            sql=_game_context_select(project, dataset, season_start, season_end, week_start, week_end),
            diagnostic_sql=_game_context_diagnostics(project, dataset, season_start, season_end, week_start, week_end),
            warnings=(),
        )
    if target == "stg_player_week_stats":
        return TargetPlan(
            target=target,
            source_tables=("raw_nflverse_weekly", "raw_nflverse_rosters_weekly"),
            sql=_player_week_select(project, dataset, season_start, season_end, week_start, week_end),
            diagnostic_sql=_player_week_diagnostics(project, dataset, season_start, season_end, week_start, week_end),
            warnings=("Legacy weekly_metrics is not used.",),
        )
    if target == "stg_team_week_stats":
        return TargetPlan(
            target=target,
            source_tables=("raw_nflverse_pbp", "raw_nflverse_schedules"),
            sql=_team_week_select(project, dataset, season_start, season_end, week_start, week_end),
            diagnostic_sql=_team_week_diagnostics(project, dataset, season_start, season_end, week_start, week_end),
            warnings=("pass_rate_over_expected remains null in staging until a model source exists.",),
        )
    if target == "stg_play_player_events":
        return TargetPlan(
            target=target,
            source_tables=("raw_nflverse_pbp", "raw_nflverse_rosters_weekly"),
            sql=_play_events_select(project, dataset, season_start, season_end, week_start, week_end),
            diagnostic_sql=_play_events_diagnostics(project, dataset, season_start, season_end, week_start, week_end),
            warnings=("Route metrics are not created in play-player events.",),
        )
    if target == "stg_participation_context":
        return TargetPlan(
            target=target,
            source_tables=("raw_nflverse_snap_counts", "raw_nflverse_rosters_weekly", "raw_nflverse_ff_playerids", "raw_nflverse_players"),
            sql=_participation_select(project, dataset, season_start, season_end, week_start, week_end),
            diagnostic_sql=_participation_diagnostics(project, dataset, season_start, season_end, week_start, week_end),
            warnings=("snap_counts uses PFR IDs for 2014; route_share stays null and has_true_route_source stays false.",),
        )
    raise StagingPlanError(f"Unknown staging target: {target}")


def selected_targets(args: argparse.Namespace) -> list[str]:
    if args.target and args.all_targets:
        raise StagingPlanError("Use either --target or --all-targets, not both.")
    if args.target:
        return list(dict.fromkeys(args.target))
    return list(TARGETS)


def validate_request(args: argparse.Namespace) -> None:
    if args.week_start is not None and args.week_end is not None and args.week_start > args.week_end:
        raise StagingPlanError("--week-start cannot be greater than --week-end.")
    if args.season_start > args.season_end:
        raise StagingPlanError("--season-start cannot be greater than --season-end.")
    if args.write and os.environ.get(STAGING_MATERIALIZATION_GATE, "").lower() != "true":
        raise StagingPlanError(f"{STAGING_MATERIALIZATION_GATE} must be true to write nflverse staging rows.")


def _null_safe_equals(left: str, right: str) -> str:
    return f"({left} = {right} OR ({left} IS NULL AND {right} IS NULL))"


def build_merge_sql(plan: TargetPlan, project: str, dataset: str) -> str:
    if plan.target not in TARGET_COLUMNS or plan.target not in TARGET_GRAINS:
        raise StagingPlanError(f"Unsupported staging write target: {plan.target}")
    columns = TARGET_COLUMNS[plan.target]
    keys = TARGET_GRAINS[plan.target]
    source_sql = plan.sql.strip().rstrip(";")
    merge_target = _table(project, dataset, plan.target)
    on_clause = "\n  AND ".join(_null_safe_equals(f"T.`{key}`", f"S.`{key}`") for key in keys)
    update_columns = [column for column in columns if column not in keys]
    update_clause = ",\n    ".join(f"`{column}` = S.`{column}`" for column in update_columns)
    insert_columns = ", ".join(f"`{column}`" for column in columns)
    insert_values = ", ".join(f"S.`{column}`" for column in columns)
    return f"""
MERGE {merge_target} AS T
USING (
{source_sql}
) AS S
ON {on_clause}
WHEN MATCHED THEN UPDATE SET
    {update_clause}
WHEN NOT MATCHED THEN INSERT ({insert_columns})
VALUES ({insert_values})
"""


def _post_write_sql(plan: TargetPlan, project: str, dataset: str, season_start: int, season_end: int) -> str:
    target = _table(project, dataset, plan.target)
    keys = TARGET_GRAINS[plan.target]
    key_select = ", ".join(f"`{key}`" for key in keys)
    return f"""
WITH duplicate_keys AS (
  SELECT {key_select}, COUNT(1) AS row_count
  FROM {target}
  WHERE season BETWEEN {season_start} AND {season_end}
  GROUP BY {key_select}
  HAVING row_count > 1
)
SELECT
  COUNT(1) AS bounded_row_count,
  COUNTIF(season = 2014) AS rows_2014,
  MIN(season) AS min_season,
  MAX(season) AS max_season,
  COUNTIF(source_freshness_json IS NULL) AS missing_source_freshness_rows,
  COUNTIF(missing_data_flags IS NULL) AS missing_flags_rows,
  (SELECT COUNT(1) FROM duplicate_keys) AS duplicate_key_count
FROM {target}
WHERE season BETWEEN {season_start} AND {season_end}
"""


def _assert_safe_write_plan(plan: TargetPlan) -> None:
    if plan.target not in TARGETS:
        raise StagingPlanError(f"Blocked non-staging write target: {plan.target}")
    for source in plan.source_tables:
        if not source.startswith("raw_nflverse_"):
            raise StagingPlanError(f"Blocked non-raw staging source for {plan.target}: {source}")
    combined_sql = f"{plan.sql}\n{plan.diagnostic_sql}"
    for blocked in (*LEGACY_TABLES, *FEATURE_TABLES):
        if f".{blocked}`" in combined_sql or f"`{blocked}`" in combined_sql:
            raise StagingPlanError(f"Blocked unsafe source dependency for {plan.target}: {blocked}")


def write_target(client: Any, plan: TargetPlan, project: str, dataset: str, season_start: int, season_end: int) -> dict[str, Any]:
    _assert_safe_write_plan(plan)
    merge_sql = build_merge_sql(plan, project, dataset)
    job = client.query(merge_sql)
    list(job.result())
    verification = query_one(client, _post_write_sql(plan, project, dataset, season_start, season_end))
    return {
        "target": plan.target,
        "write_sql_kind": "MERGE",
        "dml_affected_rows": getattr(job, "num_dml_affected_rows", None),
        "post_write": verification,
    }


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


def readiness_from_diagnostics(target: str, diagnostics: dict[str, Any], warnings: list[str]) -> str:
    duplicate_count = int(diagnostics.get("duplicate_key_count") or 0)
    planned_rows = int(diagnostics.get("planned_row_count") or 0)
    if planned_rows == 0:
        return "blocked"
    if duplicate_count:
        return "needs mapping fix"
    if warnings:
        return "ready with warnings"
    return "ready"


def build_summary(
    args: argparse.Namespace,
    *,
    client_factory: Callable[[], Any] | None = None,
    run_diagnostics: bool = True,
) -> dict[str, Any]:
    validate_request(args)
    targets = selected_targets(args)
    plans = [
        build_target_plan(target, args.project, args.dataset, args.season_start, args.season_end, args.week_start, args.week_end)
        for target in targets
    ]
    client = None
    if run_diagnostics or args.write:
        if client_factory is None:
            from google.cloud import bigquery

            client_factory = lambda: bigquery.Client(project=args.project)
        client = client_factory()

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
                "warnings": warnings,
                "recommended_write_readiness": readiness,
            }
        )
    write_results: list[dict[str, Any]] = []
    if args.write:
        if client is None:
            raise StagingPlanError("A BigQuery client is required for staging writes.")
        for plan, target_summary in zip(plans, target_summaries):
            if target_summary["recommended_write_readiness"] == "blocked":
                raise StagingPlanError(f"{plan.target} has zero planned rows and will not be written.")
            if int(target_summary.get("duplicate_key_count") or 0) != 0:
                raise StagingPlanError(f"{plan.target} has duplicate planned grain rows and will not be written.")
            write_results.append(write_target(client, plan, args.project, args.dataset, args.season_start, args.season_end))
        results_by_target = {result["target"]: result for result in write_results}
        for target_summary in target_summaries:
            target_summary["write_result"] = results_by_target.get(target_summary["target"])
    return {
        "dry_run": not args.write,
        "wrote": args.write,
        "phase": "29.8" if args.write else "29.7",
        "write_gate": STAGING_MATERIALIZATION_GATE,
        "selected_staging_targets": targets,
        "season_start": args.season_start,
        "season_end": args.season_end,
        "week_start": args.week_start,
        "week_end": args.week_end,
        "project": args.project,
        "dataset": args.dataset,
        "target_summaries": target_summaries,
        "write_results": write_results,
        "warnings": [
            (
                "Phase 29.8 staging writes were authorized by ALLOW_NFLVERSE_STAGING_MATERIALIZATION."
                if args.write
                else "Default mode is read-only. Staging writes require an authorized Phase 29.8 gate."
            ),
            "Raw raw_nflverse_* tables remain internal and are not Pigskin or UI surfaces.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = build_summary(args)
    except StagingPlanError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    output = json.dumps(summary, indent=2, sort_keys=True, default=str)
    if args.output_json:
        Path(args.output_json).write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
