"""Dry-run Pigskin context packets from nflverse advanced metrics."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from src.nflverse_backfill_plan import DEFAULT_DATASET, DEFAULT_PROJECT


PIGSKIN_PACKET_GATE = "ALLOW_PIGSKIN_PACKET_REFRESH"
PACKET_TARGET = "pigskin_player_context_packet_current"
DEFAULT_POSITIONS = ("QB", "RB", "WR", "TE")
SAFE_SOURCE_TABLES = (
    "player_recent_advanced_metrics_current",
    "player_role_usage_metrics_current",
    "player_week_advanced_metrics",
    "team_week_context_metrics",
    "qb_week_environment_metrics",
)
BLOCKED_DEPENDENCIES = (
    "raw_nflverse_",
    "play_by_play",
    "weekly_metrics",
    "player_rosters",
    "pigskin_player_context_packet_current",
    "compat_pigskin_player_context_current",
)
BLOCKED_METRICS = (
    "route_share",
    "yards_per_route_run",
    "targets_per_route_run",
    "first_read_share",
    "red_zone_usage",
    "high_value_touches",
    "touchdown_rates",
    "reception_flag_dependent_metrics",
    "true_pressure",
    "contact_yards",
    "alignment",
)
PACKET_COLUMNS = (
    "packet_version",
    "feature_run_id",
    "as_of_season",
    "as_of_week",
    "player_id_internal",
    "player_name",
    "position",
    "team",
    "scoring_profile_id",
    "league_type_id",
    "roster_format_id",
    "identity_json",
    "advanced_metrics_json",
    "recent_form_json",
    "team_context_json",
    "ranking_context_json",
    "projection_context_json",
    "trade_context_json",
    "risk_context_json",
    "source_freshness_json",
    "missing_data_flags",
    "packet_text",
    "packet_json",
    "created_at",
)
PACKET_GRAIN = (
    "packet_version",
    "as_of_season",
    "as_of_week",
    "player_id_internal",
    "scoring_profile_id",
    "league_type_id",
    "roster_format_id",
)


class PigskinPacketPlanError(RuntimeError):
    """Raised for unsafe Pigskin packet dry-run requests."""


@dataclass(frozen=True)
class PacketPlan:
    sql: str
    diagnostics_sql: str
    source_tables: tuple[str, ...]
    blocked_metrics: tuple[str, ...]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dry-run Pigskin packets from nflverse advanced metrics.")
    parser.add_argument("--dry-run", action="store_true", help="Run read-only packet diagnostics. Default.")
    parser.add_argument("--plan-only", action="store_true", help="Build SQL without querying BigQuery.")
    parser.add_argument("--write", action="store_true", help="Write Pigskin packets when the refresh gate is enabled.")
    parser.add_argument("--season-start", type=int, required=True)
    parser.add_argument("--season-end", type=int, required=True)
    parser.add_argument("--as-of-week", type=int)
    parser.add_argument("--position", action="append", choices=DEFAULT_POSITIONS)
    parser.add_argument("--player-name")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--packet-version", default="nflverse_pigskin_packet_v0_2014_001")
    parser.add_argument("--source-metric-version")
    parser.add_argument("--output-json")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args(argv)


def _table(project: str, dataset: str, table: str) -> str:
    return f"`{project}.{dataset}.{table}`"


def _quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _name_variants(name: str | None) -> tuple[str, ...]:
    if not name:
        return ()
    tokens = [re.sub(r"[^a-z0-9]", "", token.lower()) for token in name.split()]
    tokens = [token for token in tokens if token and token not in {"jr", "sr", "ii", "iii", "iv"}]
    if not tokens:
        return ()
    variants = {"".join(tokens)}
    if len(tokens) >= 2:
        variants.add(tokens[0][0] + tokens[-1])
    return tuple(sorted(variants))


def _position_filter(positions: tuple[str, ...]) -> str:
    quoted = ", ".join(_quote(position) for position in positions)
    return f"role.position IN ({quoted})"


def _bounds_filter(args: argparse.Namespace) -> str:
    clauses = [
        f"role.as_of_season BETWEEN {args.season_start} AND {args.season_end}",
    ]
    if args.as_of_week is not None:
        clauses.append(f"role.as_of_week = {args.as_of_week}")
    return " AND ".join(clauses)


def _player_name_filter(player_name: str | None) -> str:
    variants = _name_variants(player_name)
    if not variants:
        return "TRUE"
    normalized = "REGEXP_REPLACE(LOWER(COALESCE(pw.player_name, role.player_name)), r'[^a-z0-9]', '')"
    quoted = ", ".join(_quote(variant) for variant in variants)
    return f"{normalized} IN ({quoted})"


def candidate_cte(args: argparse.Namespace) -> str:
    positions = tuple(args.position or DEFAULT_POSITIONS)
    where_clauses = [
        _bounds_filter(args),
        _position_filter(positions),
        _player_name_filter(args.player_name),
        """(
      COALESCE(pw.targets, 0) > 0
      OR COALESCE(pw.carries, 0) > 0
      OR COALESCE(pw.weighted_opportunity, 0) > 0
      OR COALESCE(qb.dropbacks, 0) > 0
      OR COALESCE(qb.pass_attempts, 0) > 0
    )""",
    ]
    if args.source_metric_version:
        where_clauses.append(f"role.metric_version = {_quote(args.source_metric_version)}")
    where_sql = "\n    AND ".join(where_clauses)
    return f"""
WITH role AS (
  SELECT *
  FROM {_table(args.project, args.dataset, "player_role_usage_metrics_current")} AS role
  WHERE {_bounds_filter(args)}
),
recent AS (
  SELECT *
  FROM {_table(args.project, args.dataset, "player_recent_advanced_metrics_current")}
),
player_week AS (
  SELECT *
  FROM {_table(args.project, args.dataset, "player_week_advanced_metrics")}
  WHERE season BETWEEN {args.season_start} AND {args.season_end}
),
team_context AS (
  SELECT *
  FROM {_table(args.project, args.dataset, "team_week_context_metrics")}
  WHERE season BETWEEN {args.season_start} AND {args.season_end}
),
qb_context AS (
  SELECT *
  FROM {_table(args.project, args.dataset, "qb_week_environment_metrics")}
  WHERE season BETWEEN {args.season_start} AND {args.season_end}
),
candidate AS (
  SELECT
    role.metric_version,
    role.feature_run_id,
    role.as_of_season,
    role.as_of_week,
    role.player_id_internal,
    COALESCE(pw.player_name, role.player_name) AS player_name,
    role.position,
    role.team,
    pw.opponent_team,
    role.scoring_profile_id,
    role.league_type_id,
    role.roster_format_id,
    pw.targets,
    pw.carries,
    pw.opportunities,
    pw.weighted_opportunity,
    role.target_share,
    role.carry_share,
    role.opportunity_share,
    role.snap_share,
    role.air_yards_share,
    role.wopr,
    pw.adot,
    pw.racr,
    pw.epa_total,
    pw.epa_per_opportunity,
    pw.success_rate,
    pw.cpoe,
    qb.dropbacks,
    qb.pass_attempts,
    qb.epa_per_dropback,
    qb.cpoe AS qb_cpoe,
    qb.adot AS qb_adot,
    qb.deep_attempt_rate,
    team.team_epa_per_play,
    team.team_success_rate,
    team.neutral_pass_rate,
    team.opponent_epa_allowed,
    role.source_freshness_json AS role_source_freshness_json,
    recent.source_freshness_json AS recent_source_freshness_json,
    pw.source_freshness_json AS player_week_source_freshness_json,
    qb.source_freshness_json AS qb_source_freshness_json,
    team.source_freshness_json AS team_source_freshness_json,
    role.missing_data_flags AS role_missing_data_flags,
    recent.missing_data_flags AS recent_missing_data_flags,
    pw.missing_data_flags AS player_week_missing_data_flags,
    qb.missing_data_flags AS qb_missing_data_flags,
    team.missing_data_flags AS team_missing_data_flags
  FROM role
  LEFT JOIN recent
    ON role.player_id_internal = recent.player_id_internal
    AND role.scoring_profile_id = recent.scoring_profile_id
    AND role.league_type_id = recent.league_type_id
    AND role.roster_format_id = recent.roster_format_id
  LEFT JOIN player_week AS pw
    ON role.player_id_internal = pw.player_id_internal
    AND role.as_of_season = pw.season
    AND role.as_of_week = pw.week
    AND role.team = pw.team
    AND role.scoring_profile_id = pw.scoring_profile_id
    AND role.league_type_id = pw.league_type_id
    AND role.roster_format_id = pw.roster_format_id
  LEFT JOIN qb_context AS qb
    ON role.player_id_internal = qb.qb_player_id_internal
    AND role.as_of_season = qb.season
    AND role.as_of_week = qb.week
    AND role.team = qb.team
  LEFT JOIN team_context AS team
    ON role.as_of_season = team.season
    AND role.as_of_week = team.week
    AND role.team = team.team
  WHERE {where_sql}
)
"""


def build_packet_sql(args: argparse.Namespace) -> str:
    limit = max(1, min(args.limit or 25, 500))
    return candidate_cte(args) + f"""
SELECT *
FROM candidate
ORDER BY
  CASE position WHEN 'QB' THEN 1 WHEN 'RB' THEN 2 WHEN 'WR' THEN 3 WHEN 'TE' THEN 4 ELSE 9 END,
  COALESCE(weighted_opportunity, 0) DESC,
  COALESCE(dropbacks, 0) DESC,
  player_name
LIMIT {limit}
"""


def build_diagnostics_sql(args: argparse.Namespace) -> str:
    return candidate_cte(args) + """
SELECT
  COUNT(1) AS candidate_count,
  COUNTIF(position = 'QB') AS qb_count,
  COUNTIF(position = 'RB') AS rb_count,
  COUNTIF(position = 'WR') AS wr_count,
  COUNTIF(position = 'TE') AS te_count,
  COUNTIF(player_id_internal IS NULL) AS missing_identity_rows,
  COUNTIF(role_source_freshness_json IS NULL) AS missing_source_freshness_rows,
  COUNTIF(role_missing_data_flags IS NULL) AS missing_flags_rows,
  COUNTIF(wopr IS NULL) AS null_wopr_rows,
  COUNTIF(air_yards_share IS NULL) AS null_air_yards_share_rows,
  COUNTIF(snap_share IS NULL) AS null_snap_share_rows,
  COUNTIF(epa_per_opportunity IS NULL) AS null_epa_per_opportunity_rows,
  COUNTIF(success_rate IS NULL) AS null_success_rate_rows,
  COUNTIF(COALESCE(cpoe, qb_cpoe) IS NULL) AS null_cpoe_rows,
  COUNTIF(JSON_VALUE(player_week_missing_data_flags, '$.zero_player_opportunity_denominator') = 'true') AS sample_size_warning_rows,
  COUNTIF(JSON_VALUE(player_week_missing_data_flags, '$.missing_identity_match') = 'true') AS missing_identity_flag_rows,
  COUNTIF(JSON_VALUE(qb_missing_data_flags, '$.missing_qb_identity') = 'true') AS missing_qb_identity_flag_rows
FROM candidate
"""


def build_position_diagnostics_sql(args: argparse.Namespace) -> str:
    return candidate_cte(args) + """
SELECT
  position,
  COUNT(1) AS candidate_count,
  COUNTIF(wopr IS NULL) AS null_wopr_rows,
  COUNTIF(air_yards_share IS NULL) AS null_air_yards_share_rows,
  COUNTIF(snap_share IS NULL) AS null_snap_share_rows,
  COUNTIF(epa_per_opportunity IS NULL) AS null_epa_per_opportunity_rows,
  COUNTIF(success_rate IS NULL) AS null_success_rate_rows,
  COUNTIF(COALESCE(cpoe, qb_cpoe) IS NULL) AS null_cpoe_rows,
  COUNTIF(JSON_VALUE(player_week_missing_data_flags, '$.zero_player_opportunity_denominator') = 'true') AS sample_size_warning_rows
FROM candidate
GROUP BY position
ORDER BY position
"""


def build_view_diagnostics_sql(project: str, dataset: str) -> str:
    return f"""
WITH objects AS (
  SELECT
    'player_recent_advanced_metrics_current' AS table_name,
    as_of_season,
    as_of_week,
    player_id_internal,
    position,
    source_freshness_json,
    missing_data_flags
  FROM {_table(project, dataset, "player_recent_advanced_metrics_current")}
  UNION ALL
  SELECT
    'player_role_usage_metrics_current' AS table_name,
    as_of_season,
    as_of_week,
    player_id_internal,
    position,
    source_freshness_json,
    missing_data_flags
  FROM {_table(project, dataset, "player_role_usage_metrics_current")}
)
SELECT
  table_name,
  COUNT(1) AS row_count,
  MIN(as_of_season) AS min_season,
  MAX(as_of_season) AS max_season,
  MIN(as_of_week) AS min_as_of_week,
  MAX(as_of_week) AS max_as_of_week,
  COUNTIF(position IN ('QB', 'RB', 'WR', 'TE')) AS fantasy_position_rows,
  COUNTIF(position NOT IN ('QB', 'RB', 'WR', 'TE') OR position IS NULL) AS non_fantasy_rows,
  COUNTIF(player_id_internal IS NULL) AS missing_identity_rows,
  COUNTIF(source_freshness_json IS NULL) AS missing_source_freshness_rows,
  COUNTIF(missing_data_flags IS NULL) AS missing_flags_rows
FROM objects
GROUP BY table_name
ORDER BY table_name
"""


def _string_array_sql(values: tuple[str, ...]) -> str:
    return "[" + ", ".join(_quote(value) for value in values) + "]"


def build_write_source_sql(args: argparse.Namespace) -> str:
    blocked_metrics_sql = _string_array_sql(BLOCKED_METRICS)
    return candidate_cte(args) + f"""
SELECT
  {_quote(args.packet_version)} AS packet_version,
  feature_run_id,
  as_of_season,
  as_of_week,
  player_id_internal,
  player_name,
  position,
  team,
  scoring_profile_id,
  league_type_id,
  roster_format_id,
  TO_JSON_STRING(STRUCT(
    player_id_internal AS player_id_internal,
    player_name AS player_name,
    position AS position,
    team AS team,
    as_of_season AS season,
    as_of_week AS as_of_week,
    IF(player_id_internal IS NULL, 'warning', 'matched') AS identity_confidence
  )) AS identity_json,
  TO_JSON_STRING(STRUCT(
    metric_version AS source_metric_version,
    targets AS targets,
    carries AS carries,
    opportunities AS opportunities,
    weighted_opportunity AS weighted_opportunity,
    target_share AS target_share,
    carry_share AS carry_share,
    opportunity_share AS opportunity_share,
    snap_share AS snap_share,
    air_yards_share AS air_yards_share,
    wopr AS wopr,
    adot AS adot,
    racr AS racr,
    epa_total AS epa_total,
    epa_per_opportunity AS epa_per_opportunity,
    success_rate AS success_rate,
    cpoe AS cpoe
  )) AS advanced_metrics_json,
  TO_JSON_STRING(STRUCT(
    metric_version AS source_metric_version,
    'current_view_latest_row' AS sample_window,
    as_of_week AS as_of_week,
    role_missing_data_flags AS sample_size_flags
  )) AS recent_form_json,
  TO_JSON_STRING(STRUCT(
    team_epa_per_play AS team_epa_per_play,
    team_success_rate AS team_success_rate,
    neutral_pass_rate AS neutral_pass_rate,
    opponent_epa_allowed AS opponent_epa_allowed,
    TRUE AS pass_rate_over_expected_unavailable
  )) AS team_context_json,
  TO_JSON_STRING(STRUCT(TRUE AS unavailable_in_phase_29_12)) AS ranking_context_json,
  TO_JSON_STRING(STRUCT(TRUE AS unavailable_in_phase_29_12)) AS projection_context_json,
  TO_JSON_STRING(STRUCT(TRUE AS unavailable_in_phase_29_12)) AS trade_context_json,
  TO_JSON_STRING(STRUCT(TRUE AS unavailable_in_phase_29_12)) AS risk_context_json,
  TO_JSON_STRING(STRUCT(
    role_source_freshness_json AS role,
    recent_source_freshness_json AS recent,
    player_week_source_freshness_json AS player_week,
    qb_source_freshness_json AS qb,
    team_source_freshness_json AS team
  )) AS source_freshness_json,
  TO_JSON_STRING(STRUCT(
    role_missing_data_flags AS role,
    recent_missing_data_flags AS recent,
    player_week_missing_data_flags AS player_week,
    qb_missing_data_flags AS qb,
    team_missing_data_flags AS team,
    {blocked_metrics_sql} AS blocked_metric_flags,
    ARRAY(
      SELECT warning
      FROM UNNEST([
        IF(player_id_internal IS NULL, 'missing identity', NULL),
        IF(wopr IS NULL OR air_yards_share IS NULL, 'missing WOPR or air yards share', NULL),
        IF(snap_share IS NULL, 'missing snap share', NULL),
        IF(epa_per_opportunity IS NULL AND epa_per_dropback IS NULL, 'missing EPA efficiency', NULL),
        IF(position = 'QB' AND (dropbacks IS NULL OR pass_attempts IS NULL), 'missing QB environment sample', NULL),
        IF(JSON_VALUE(player_week_missing_data_flags, '$.zero_player_opportunity_denominator') = 'true', 'sample size warning', NULL)
      ]) AS warning
      WHERE warning IS NOT NULL
    ) AS packet_warnings
  )) AS missing_data_flags,
  CONCAT(
    COALESCE(player_name, 'Unknown player'), ' (', COALESCE(position, 'UNK'), ', ', COALESCE(team, 'UNK'), ') as of ',
    COALESCE(CAST(as_of_season AS STRING), 'null'), ' week ',
    COALESCE(CAST(as_of_week AS STRING), 'null'), ': weighted opportunity ', COALESCE(CAST(weighted_opportunity AS STRING), 'null'),
    ', target share ', COALESCE(CAST(target_share AS STRING), 'null'),
    ', WOPR ', COALESCE(CAST(wopr AS STRING), 'null'),
    ', EPA/opportunity ', COALESCE(CAST(epa_per_opportunity AS STRING), 'null'),
    IF(position = 'QB', CONCAT(', EPA/dropback ', COALESCE(CAST(epa_per_dropback AS STRING), 'null')), '')
  ) AS packet_text,
  TO_JSON_STRING(STRUCT(
    STRUCT(
      player_id_internal AS player_id_internal,
      player_name AS player_name,
      position AS position,
      team AS team,
      as_of_season AS season,
      as_of_week AS as_of_week,
      IF(player_id_internal IS NULL, 'warning', 'matched') AS identity_confidence
    ) AS identity,
    STRUCT(
      opportunities AS opportunities,
      targets AS targets,
      carries AS carries,
      weighted_opportunity AS weighted_opportunity,
      target_share AS target_share,
      carry_share AS carry_share,
      opportunity_share AS opportunity_share,
      snap_share AS snap_share
    ) AS usage_summary,
    STRUCT(
      air_yards_share AS air_yards_share,
      wopr AS wopr,
      adot AS adot,
      racr AS racr,
      IF(wopr IS NULL, 'missing source or no receiving sample', NULL) AS missing_reason
    ) AS receiving_air_yards,
    STRUCT(
      epa_total AS epa_total,
      epa_per_opportunity AS epa_per_opportunity,
      success_rate AS success_rate,
      cpoe AS cpoe
    ) AS efficiency_summary,
    STRUCT(
      dropbacks AS dropbacks,
      pass_attempts AS pass_attempts,
      epa_per_dropback AS epa_per_dropback,
      qb_cpoe AS cpoe,
      qb_adot AS adot,
      deep_attempt_rate AS deep_attempt_rate,
      TRUE AS sack_unavailable,
      TRUE AS scramble_unavailable
    ) AS qb_context,
    STRUCT(
      team_epa_per_play AS team_epa_per_play,
      team_success_rate AS team_success_rate,
      neutral_pass_rate AS neutral_pass_rate,
      opponent_epa_allowed AS opponent_epa_allowed,
      TRUE AS pass_rate_over_expected_unavailable
    ) AS team_context,
    {blocked_metrics_sql} AS blocked_metrics,
    STRUCT(
      role_source_freshness_json AS role,
      recent_source_freshness_json AS recent,
      player_week_source_freshness_json AS player_week,
      qb_source_freshness_json AS qb,
      team_source_freshness_json AS team
    ) AS source_freshness,
    metric_version AS source_metric_version,
    ARRAY(
      SELECT warning
      FROM UNNEST([
        IF(player_id_internal IS NULL, 'missing identity', NULL),
        IF(wopr IS NULL OR air_yards_share IS NULL, 'missing WOPR or air yards share', NULL),
        IF(snap_share IS NULL, 'missing snap share', NULL),
        IF(epa_per_opportunity IS NULL AND epa_per_dropback IS NULL, 'missing EPA efficiency', NULL),
        IF(position = 'QB' AND (dropbacks IS NULL OR pass_attempts IS NULL), 'missing QB environment sample', NULL),
        IF(JSON_VALUE(player_week_missing_data_flags, '$.zero_player_opportunity_denominator') = 'true', 'sample size warning', NULL)
      ]) AS warning
      WHERE warning IS NOT NULL
    ) AS warnings
  )) AS packet_json,
  CURRENT_TIMESTAMP() AS created_at
FROM candidate
"""


def _null_safe_equals(left: str, right: str) -> str:
    return f"({left} = {right} OR ({left} IS NULL AND {right} IS NULL))"


def build_merge_sql(args: argparse.Namespace) -> str:
    source_sql = build_write_source_sql(args).strip().rstrip(";")
    _assert_safe_sql(source_sql)
    columns = PACKET_COLUMNS
    keys = PACKET_GRAIN
    on_clause = "\n  AND ".join(_null_safe_equals(f"T.`{key}`", f"S.`{key}`") for key in keys)
    update_columns = [column for column in columns if column not in keys]
    update_clause = ",\n    ".join(f"`{column}` = S.`{column}`" for column in update_columns)
    insert_columns = ", ".join(f"`{column}`" for column in columns)
    insert_values = ", ".join(f"S.`{column}`" for column in columns)
    return f"""
MERGE {_table(args.project, args.dataset, PACKET_TARGET)} AS T
USING (
{source_sql}
) AS S
ON {on_clause}
WHEN MATCHED THEN UPDATE SET
    {update_clause}
WHEN NOT MATCHED THEN INSERT ({insert_columns})
VALUES ({insert_values})
"""


def post_write_sql(args: argparse.Namespace) -> str:
    return f"""
WITH duplicate_keys AS (
  SELECT
    packet_version,
    as_of_season,
    as_of_week,
    player_id_internal,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    COUNT(1) AS row_count
  FROM {_table(args.project, args.dataset, PACKET_TARGET)}
  WHERE as_of_season BETWEEN {args.season_start} AND {args.season_end}
    AND packet_version = {_quote(args.packet_version)}
  GROUP BY 1, 2, 3, 4, 5, 6, 7
  HAVING row_count > 1
)
SELECT
  COUNT(1) AS bounded_row_count,
  MIN(as_of_season) AS min_source_season,
  MAX(as_of_season) AS max_source_season,
  MIN(as_of_week) AS min_as_of_week,
  MAX(as_of_week) AS max_as_of_week,
  COUNT(DISTINCT packet_version) AS packet_version_count,
  COUNT(DISTINCT JSON_VALUE(packet_json, '$.source_metric_version')) AS source_metric_version_count,
  COUNTIF(packet_json IS NULL) AS missing_packet_json_count,
  COUNTIF(packet_text IS NULL) AS missing_packet_text_count,
  COUNTIF(source_freshness_json IS NULL) AS missing_source_freshness_count,
  COUNTIF(JSON_VALUE(missing_data_flags, '$.blocked_metric_flags[0]') IS NULL) AS missing_blocked_metric_flag_count,
  COUNTIF(JSON_QUERY_ARRAY(packet_json, '$.warnings') IS NOT NULL AND ARRAY_LENGTH(JSON_QUERY_ARRAY(packet_json, '$.warnings')) > 0) AS rows_with_packet_warnings,
  (SELECT COUNT(1) FROM duplicate_keys) AS duplicate_packet_grain_count
FROM {_table(args.project, args.dataset, PACKET_TARGET)}
WHERE as_of_season BETWEEN {args.season_start} AND {args.season_end}
  AND packet_version = {_quote(args.packet_version)}
"""


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


def _json_or_none(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _warnings_for(row: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if row.get("player_id_internal") is None:
        warnings.append("missing identity")
    if row.get("wopr") is None or row.get("air_yards_share") is None:
        warnings.append("missing WOPR or air yards share")
    if row.get("snap_share") is None:
        warnings.append("missing snap share")
    if row.get("epa_per_opportunity") is None and row.get("epa_per_dropback") is None:
        warnings.append("missing EPA efficiency")
    if row.get("position") == "QB" and (row.get("dropbacks") is None or row.get("pass_attempts") is None):
        warnings.append("missing QB environment sample")
    player_flags = _json_or_none(row.get("player_week_missing_data_flags"))
    if isinstance(player_flags, dict) and player_flags.get("zero_player_opportunity_denominator"):
        warnings.append("sample size warning")
    return warnings


def packet_json_for_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "identity": {
            "player_id_internal": row.get("player_id_internal"),
            "player_name": row.get("player_name"),
            "position": row.get("position"),
            "team": row.get("team"),
            "season": row.get("as_of_season"),
            "as_of_week": row.get("as_of_week"),
            "identity_confidence": "warning" if row.get("player_id_internal") is None else "matched",
        },
        "usage_summary": {
            "opportunities": row.get("opportunities"),
            "targets": row.get("targets"),
            "carries": row.get("carries"),
            "weighted_opportunity": row.get("weighted_opportunity"),
            "target_share": row.get("target_share"),
            "carry_share": row.get("carry_share"),
            "opportunity_share": row.get("opportunity_share"),
            "snap_share": row.get("snap_share"),
        },
        "receiving_air_yards": {
            "air_yards_share": row.get("air_yards_share"),
            "wopr": row.get("wopr"),
            "adot": row.get("adot"),
            "racr": row.get("racr"),
            "missing_reason": "missing source or no receiving sample" if row.get("wopr") is None else None,
        },
        "efficiency_summary": {
            "epa_total": row.get("epa_total"),
            "epa_per_opportunity": row.get("epa_per_opportunity"),
            "success_rate": row.get("success_rate"),
            "cpoe": row.get("cpoe"),
        },
        "qb_context": {
            "dropbacks": row.get("dropbacks"),
            "pass_attempts": row.get("pass_attempts"),
            "epa_per_dropback": row.get("epa_per_dropback"),
            "cpoe": row.get("qb_cpoe"),
            "adot": row.get("qb_adot"),
            "deep_attempt_rate": row.get("deep_attempt_rate"),
            "sack_unavailable": True,
            "scramble_unavailable": True,
        },
        "team_context": {
            "team_epa_per_play": row.get("team_epa_per_play"),
            "team_success_rate": row.get("team_success_rate"),
            "neutral_pass_rate": row.get("neutral_pass_rate"),
            "opponent_epa_allowed": row.get("opponent_epa_allowed"),
            "pass_rate_over_expected_unavailable": True,
        },
        "blocked_metrics": list(BLOCKED_METRICS),
        "source_freshness": {
            "role": _json_or_none(row.get("role_source_freshness_json")),
            "recent": _json_or_none(row.get("recent_source_freshness_json")),
            "player_week": _json_or_none(row.get("player_week_source_freshness_json")),
            "qb": _json_or_none(row.get("qb_source_freshness_json")),
            "team": _json_or_none(row.get("team_source_freshness_json")),
        },
        "warnings": _warnings_for(row),
    }


def packet_text_for_row(row: dict[str, Any], packet_json: dict[str, Any]) -> str:
    name = row.get("player_name") or "Unknown player"
    position = row.get("position") or "UNK"
    team = row.get("team") or "UNK"
    bits = [
        f"{name} ({position}, {team}) as of {row.get('as_of_season')} week {row.get('as_of_week')}:",
        f"weighted opportunity {row.get('weighted_opportunity')}",
        f"target share {row.get('target_share')}",
        f"WOPR {row.get('wopr')}",
        f"EPA/opportunity {row.get('epa_per_opportunity')}",
    ]
    if position == "QB":
        bits.append(f"EPA/dropback {row.get('epa_per_dropback')}")
    if packet_json["warnings"]:
        bits.append("warnings: " + ", ".join(packet_json["warnings"]))
    return " ".join(bits)


def packet_preview_for_row(row: dict[str, Any]) -> dict[str, Any]:
    packet_json = packet_json_for_row(row)
    return {
        "player_name": row.get("player_name"),
        "position": row.get("position"),
        "team": row.get("team"),
        "as_of_week": row.get("as_of_week"),
        "packet_json": packet_json,
        "packet_text": packet_text_for_row(row, packet_json),
    }


def _assert_safe_sql(sql: str) -> None:
    for blocked in BLOCKED_DEPENDENCIES:
        if blocked in sql:
            raise PigskinPacketPlanError(f"Blocked unsafe packet dependency: {blocked}")
    if any(token in sql.upper() for token in ("INSERT ", "MERGE ", "DELETE ", "TRUNCATE", "UPDATE ")):
        raise PigskinPacketPlanError("Blocked write token in packet dry-run SQL.")


def validate_request(args: argparse.Namespace) -> None:
    if args.season_start > args.season_end:
        raise PigskinPacketPlanError("--season-start cannot be greater than --season-end")
    if args.limit is not None and args.limit <= 0:
        raise PigskinPacketPlanError("--limit must be positive")
    if args.write and args.plan_only:
        raise PigskinPacketPlanError("--write cannot be combined with --plan-only")
    if args.write and os.environ.get(PIGSKIN_PACKET_GATE) != "true":
        raise PigskinPacketPlanError(f"{PIGSKIN_PACKET_GATE} must be true to write Pigskin packets.")


def build_plan(args: argparse.Namespace) -> PacketPlan:
    sql = build_packet_sql(args)
    diagnostics_sql = build_diagnostics_sql(args)
    combined = "\n".join([sql, diagnostics_sql])
    _assert_safe_sql(combined)
    return PacketPlan(
        sql=sql,
        diagnostics_sql=diagnostics_sql,
        source_tables=SAFE_SOURCE_TABLES,
        blocked_metrics=BLOCKED_METRICS,
    )


def build_summary(
    args: argparse.Namespace,
    *,
    client_factory: Callable[[], Any] | None = None,
    run_diagnostics: bool = True,
) -> dict[str, Any]:
    validate_request(args)
    plan = build_plan(args)
    packet_rows: list[dict[str, Any]] = []
    diagnostics: dict[str, Any] = {}
    position_diagnostics: list[dict[str, Any]] = []
    view_diagnostics: list[dict[str, Any]] = []
    write_result: dict[str, Any] | None = None
    errors: list[str] = []
    if (run_diagnostics or args.write) and not args.plan_only:
        if client_factory is None:
            from google.cloud import bigquery

            client_factory = lambda: bigquery.Client(project=args.project)
        client = client_factory()
        try:
            diagnostics = query_one(client, plan.diagnostics_sql)
            position_diagnostics = query_many(client, build_position_diagnostics_sql(args))
            view_diagnostics = query_many(client, build_view_diagnostics_sql(args.project, args.dataset))
            packet_rows = query_many(client, plan.sql)
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
            if args.strict:
                raise
        if args.write:
            if errors:
                raise PigskinPacketPlanError("Packet diagnostics failed; refusing to write.")
            if int(diagnostics.get("candidate_count") or 0) == 0:
                raise PigskinPacketPlanError("No packet candidates found; refusing to write.")
            merge_sql = build_merge_sql(args)
            job = client.query(merge_sql)
            list(job.result())
            post_write = query_one(client, post_write_sql(args))
            write_result = {
                "target": PACKET_TARGET,
                "write_sql_kind": "MERGE",
                "dml_affected_rows": getattr(job, "num_dml_affected_rows", None),
                "post_write": post_write,
            }
    packet_examples = [packet_preview_for_row(row) for row in packet_rows]
    return {
        "dry_run": not args.write,
        "wrote": bool(args.write),
        "phase": "29.12" if args.write else "29.11",
        "future_write_gate": PIGSKIN_PACKET_GATE,
        "write_supported": True,
        "project": args.project,
        "dataset": args.dataset,
        "packet_target": PACKET_TARGET,
        "packet_version": args.packet_version,
        "source_metric_version": args.source_metric_version,
        "season_start": args.season_start,
        "season_end": args.season_end,
        "as_of_week": args.as_of_week,
        "positions": list(args.position or DEFAULT_POSITIONS),
        "player_name": args.player_name,
        "limit": max(1, min(args.limit or 25, 500)),
        "candidate_universe": "QB/RB/WR/TE with at least one offensive opportunity or QB environment sample.",
        "source_tables": list(plan.source_tables),
        "blocked_dependencies": list(BLOCKED_DEPENDENCIES),
        "blocked_metrics": list(plan.blocked_metrics),
        "packet_sql": plan.sql.strip(),
        "diagnostics_sql": plan.diagnostics_sql.strip(),
        "diagnostics": diagnostics,
        "position_diagnostics": position_diagnostics,
        "view_diagnostics": view_diagnostics,
        "packet_examples": packet_examples,
        "write_result": write_result,
        "errors": errors,
        "warnings": [
            (
                "Phase 29.12 Pigskin packet writes were authorized by ALLOW_PIGSKIN_PACKET_REFRESH."
                if args.write
                else "Phase 29.11 is read-only and dry-run only."
            ),
            "Pigskin packet writes are limited to pigskin_player_context_packet_current.",
            "Packet SQL reads current/base feature marts only, not raw or legacy source tables.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = build_summary(args, run_diagnostics=not args.plan_only)
    except PigskinPacketPlanError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    output = json.dumps(summary, indent=2, sort_keys=True, default=str)
    if args.output_json:
        Path(args.output_json).write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
