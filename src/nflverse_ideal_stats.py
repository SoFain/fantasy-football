"""Bounded ffopportunity ingest and ideal-stat derivation for ranking research."""

from __future__ import annotations

import argparse
import json
import os
import socket
import uuid
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

import pandas as pd


DEFAULT_PROJECT = "fantasy-football-498121"
DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_SOURCE_VERSION = "ffopportunity_weekly_latest"
DEFAULT_SOURCE_REFRESH_ID = "ffopportunity-weekly"
DEFAULT_PBP_SOURCE_VERSION = "ffopportunity_pbp_latest"
DEFAULT_PBP_SOURCE_REFRESH_ID = "ffopportunity-pbp"
DEFAULT_SEASON_START = 2014
DEFAULT_SEASON_END = 2025
WRITE_GATE = "ALLOW_NFLVERSE_IDEAL_STATS_INGEST"
RAW_TABLE = "raw_ffopportunity_weekly"
DERIVED_TABLE = "player_week_ideal_opportunity_metrics"
RAW_PBP_PASS_TABLE = "raw_ffopportunity_pbp_pass"
RAW_PBP_RUSH_TABLE = "raw_ffopportunity_pbp_rush"
PBP_DERIVED_TABLE = "player_week_pbp_opportunity_metrics"

RAW_COLUMNS = (
    "source_version",
    "season",
    "week",
    "game_id",
    "source_player_id",
    "player_id_internal",
    "player_name",
    "team",
    "position",
    "pass_attempt",
    "rec_attempt",
    "rush_attempt",
    "pass_fantasy_points_exp",
    "rec_fantasy_points_exp",
    "rush_fantasy_points_exp",
    "total_fantasy_points_exp",
    "pass_fantasy_points",
    "rec_fantasy_points",
    "rush_fantasy_points",
    "total_fantasy_points",
    "pass_fantasy_points_diff",
    "rec_fantasy_points_diff",
    "rush_fantasy_points_diff",
    "total_fantasy_points_diff",
    "pass_fantasy_points_exp_team",
    "rec_fantasy_points_exp_team",
    "rush_fantasy_points_exp_team",
    "total_fantasy_points_exp_team",
    "raw_payload_json",
    "source_refresh_id",
    "loaded_at",
    "loaded_by",
)

RAW_PBP_PASS_COLUMNS = (
    "source_version",
    "season",
    "week",
    "game_id",
    "play_id",
    "passer_player_id",
    "passer_player_id_internal",
    "passer_name",
    "passer_position",
    "receiver_player_id",
    "receiver_player_id_internal",
    "receiver_name",
    "receiver_position",
    "team",
    "pass_attempt",
    "complete_pass",
    "air_yards",
    "receiving_yards",
    "yards_after_catch",
    "pass_touchdown",
    "interception",
    "first_down_pass",
    "two_point_attempt",
    "two_point_converted",
    "yardline_100",
    "goal_to_go",
    "pass_completion_exp",
    "yards_after_catch_exp",
    "yardline_exp",
    "pass_touchdown_exp",
    "pass_first_down_exp",
    "pass_interception_exp",
    "two_point_conv_exp",
    "raw_payload_json",
    "source_refresh_id",
    "loaded_at",
    "loaded_by",
)

RAW_PBP_RUSH_COLUMNS = (
    "source_version",
    "season",
    "week",
    "game_id",
    "play_id",
    "rusher_player_id",
    "rusher_player_id_internal",
    "rusher_name",
    "position",
    "team",
    "rush_attempt",
    "rushing_yards",
    "rush_touchdown",
    "first_down_rush",
    "two_point_attempt",
    "two_point_converted",
    "yardline_100",
    "goal_to_go",
    "rushing_yards_exp",
    "rushing_td_exp",
    "rushing_fd_exp",
    "rush_yards_exp",
    "rush_touchdown_exp",
    "rush_first_down_exp",
    "two_point_conv_exp",
    "qb_scramble",
    "raw_payload_json",
    "source_refresh_id",
    "loaded_at",
    "loaded_by",
)


def table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    return f"{project_id}.{dataset_id}.{table_name}"


def is_write_authorized(env: Mapping[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return source.get(WRITE_GATE, "").strip().lower() == "true"


def require_write_authorization(env: Mapping[str, str] | None = None) -> None:
    if not is_write_authorized(env):
        raise PermissionError(f"{WRITE_GATE} must be true to ingest ideal stats")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _loaded_by() -> str:
    user = os.environ.get("USERNAME") or os.environ.get("USER") or "unknown"
    return f"{user}@{socket.gethostname()}"


def _safe_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(number):
        return None
    return number


def _safe_int(value: Any) -> int | None:
    number = _safe_float(value)
    if number is None:
        return None
    return int(number)


def _safe_str(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def _json_row(row: Mapping[str, Any]) -> str:
    payload = {}
    for key, value in row.items():
        if pd.isna(value):
            payload[key] = None
        elif hasattr(value, "item"):
            payload[key] = value.item()
        else:
            payload[key] = value
    return json.dumps(payload, sort_keys=True, default=str)


def load_ffopportunity_weekly(seasons: list[int] | tuple[int, ...]) -> pd.DataFrame:
    import nflreadpy as nfl

    frame = nfl.load_ff_opportunity(seasons=list(seasons), stat_type="weekly")
    if hasattr(frame, "to_pandas"):
        return frame.to_pandas()
    return pd.DataFrame(frame)


def load_ffopportunity_pbp(seasons: list[int] | tuple[int, ...], *, stat_type: str) -> pd.DataFrame:
    if stat_type not in {"pbp_pass", "pbp_rush"}:
        raise ValueError("stat_type must be pbp_pass or pbp_rush")
    import nflreadpy as nfl

    frame = nfl.load_ff_opportunity(seasons=list(seasons), stat_type=stat_type)
    if hasattr(frame, "to_pandas"):
        return frame.to_pandas()
    return pd.DataFrame(frame)


def normalize_ffopportunity_weekly(
    frame: pd.DataFrame,
    *,
    source_version: str = DEFAULT_SOURCE_VERSION,
    source_refresh_id: str | None = None,
    loaded_at: datetime | None = None,
    loaded_by: str | None = None,
) -> pd.DataFrame:
    loaded_at = loaded_at or _now()
    loaded_by = loaded_by or _loaded_by()
    source_refresh_id = source_refresh_id or f"{DEFAULT_SOURCE_REFRESH_ID}-{loaded_at.strftime('%Y%m%dT%H%M%SZ')}"
    records: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        source_player_id = _safe_str(row.get("player_id"))
        season = _safe_int(row.get("season"))
        week = _safe_int(row.get("week"))
        position = _safe_str(row.get("position"))
        if not source_player_id or season is None or week is None or not position:
            continue
        records.append(
            {
                "source_version": source_version,
                "season": season,
                "week": week,
                "game_id": _safe_str(row.get("game_id")),
                "source_player_id": source_player_id,
                "player_id_internal": f"gsis:{source_player_id}",
                "player_name": _safe_str(row.get("full_name")),
                "team": _safe_str(row.get("posteam")),
                "position": position.upper(),
                "pass_attempt": _safe_float(row.get("pass_attempt")),
                "rec_attempt": _safe_float(row.get("rec_attempt")),
                "rush_attempt": _safe_float(row.get("rush_attempt")),
                "pass_fantasy_points_exp": _safe_float(row.get("pass_fantasy_points_exp")),
                "rec_fantasy_points_exp": _safe_float(row.get("rec_fantasy_points_exp")),
                "rush_fantasy_points_exp": _safe_float(row.get("rush_fantasy_points_exp")),
                "total_fantasy_points_exp": _safe_float(row.get("total_fantasy_points_exp")),
                "pass_fantasy_points": _safe_float(row.get("pass_fantasy_points")),
                "rec_fantasy_points": _safe_float(row.get("rec_fantasy_points")),
                "rush_fantasy_points": _safe_float(row.get("rush_fantasy_points")),
                "total_fantasy_points": _safe_float(row.get("total_fantasy_points")),
                "pass_fantasy_points_diff": _safe_float(row.get("pass_fantasy_points_diff")),
                "rec_fantasy_points_diff": _safe_float(row.get("rec_fantasy_points_diff")),
                "rush_fantasy_points_diff": _safe_float(row.get("rush_fantasy_points_diff")),
                "total_fantasy_points_diff": _safe_float(row.get("total_fantasy_points_diff")),
                "pass_fantasy_points_exp_team": _safe_float(row.get("pass_fantasy_points_exp_team")),
                "rec_fantasy_points_exp_team": _safe_float(row.get("rec_fantasy_points_exp_team")),
                "rush_fantasy_points_exp_team": _safe_float(row.get("rush_fantasy_points_exp_team")),
                "total_fantasy_points_exp_team": _safe_float(row.get("total_fantasy_points_exp_team")),
                "raw_payload_json": _json_row(row),
                "source_refresh_id": source_refresh_id,
                "loaded_at": loaded_at,
                "loaded_by": loaded_by,
            }
        )
    return pd.DataFrame.from_records(records, columns=RAW_COLUMNS)


def normalize_ffopportunity_pbp_pass(
    frame: pd.DataFrame,
    *,
    source_version: str = DEFAULT_PBP_SOURCE_VERSION,
    source_refresh_id: str | None = None,
    loaded_at: datetime | None = None,
    loaded_by: str | None = None,
) -> pd.DataFrame:
    loaded_at = loaded_at or _now()
    loaded_by = loaded_by or _loaded_by()
    source_refresh_id = source_refresh_id or f"{DEFAULT_PBP_SOURCE_REFRESH_ID}-pass-{loaded_at.strftime('%Y%m%dT%H%M%SZ')}"
    records: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        season = _safe_int(row.get("season"))
        week = _safe_int(row.get("week"))
        game_id = _safe_str(row.get("game_id"))
        play_id = _safe_int(row.get("play_id"))
        if season is None or week is None or not game_id or play_id is None:
            continue
        passer_id = _safe_str(row.get("passer_player_id"))
        receiver_id = _safe_str(row.get("receiver_player_id"))
        if not passer_id and not receiver_id:
            continue
        records.append(
            {
                "source_version": source_version,
                "season": season,
                "week": week,
                "game_id": game_id,
                "play_id": play_id,
                "passer_player_id": passer_id,
                "passer_player_id_internal": f"gsis:{passer_id}" if passer_id else None,
                "passer_name": _safe_str(row.get("passer_full_name")),
                "passer_position": (_safe_str(row.get("passer_position")) or "").upper() or None,
                "receiver_player_id": receiver_id,
                "receiver_player_id_internal": f"gsis:{receiver_id}" if receiver_id else None,
                "receiver_name": _safe_str(row.get("receiver_full_name")),
                "receiver_position": (_safe_str(row.get("receiver_position")) or "").upper() or None,
                "team": _safe_str(row.get("posteam")),
                "pass_attempt": _safe_float(row.get("pass_attempt")),
                "complete_pass": _safe_float(row.get("complete_pass")),
                "air_yards": _safe_float(row.get("air_yards")),
                "receiving_yards": _safe_float(row.get("receiving_yards")),
                "yards_after_catch": _safe_float(row.get("yards_after_catch")),
                "pass_touchdown": _safe_float(row.get("pass_touchdown")),
                "interception": _safe_float(row.get("interception")),
                "first_down_pass": _safe_float(row.get("first_down_pass")),
                "two_point_attempt": _safe_float(row.get("two_point_attempt")),
                "two_point_converted": _safe_float(row.get("two_point_converted")),
                "yardline_100": _safe_float(row.get("yardline_100")),
                "goal_to_go": _safe_float(row.get("goal_to_go")),
                "pass_completion_exp": _safe_float(row.get("pass_completion_exp")),
                "yards_after_catch_exp": _safe_float(row.get("yards_after_catch_exp")),
                "yardline_exp": _safe_float(row.get("yardline_exp")),
                "pass_touchdown_exp": _safe_float(row.get("pass_touchdown_exp")),
                "pass_first_down_exp": _safe_float(row.get("pass_first_down_exp")),
                "pass_interception_exp": _safe_float(row.get("pass_interception_exp")),
                "two_point_conv_exp": _safe_float(row.get("two_point_conv_exp")),
                "raw_payload_json": _json_row(row),
                "source_refresh_id": source_refresh_id,
                "loaded_at": loaded_at,
                "loaded_by": loaded_by,
            }
        )
    return pd.DataFrame.from_records(records, columns=RAW_PBP_PASS_COLUMNS)


def normalize_ffopportunity_pbp_rush(
    frame: pd.DataFrame,
    *,
    source_version: str = DEFAULT_PBP_SOURCE_VERSION,
    source_refresh_id: str | None = None,
    loaded_at: datetime | None = None,
    loaded_by: str | None = None,
) -> pd.DataFrame:
    loaded_at = loaded_at or _now()
    loaded_by = loaded_by or _loaded_by()
    source_refresh_id = source_refresh_id or f"{DEFAULT_PBP_SOURCE_REFRESH_ID}-rush-{loaded_at.strftime('%Y%m%dT%H%M%SZ')}"
    records: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        season = _safe_int(row.get("season"))
        week = _safe_int(row.get("week"))
        game_id = _safe_str(row.get("game_id"))
        play_id = _safe_int(row.get("play_id"))
        rusher_id = _safe_str(row.get("rusher_player_id"))
        if season is None or week is None or not game_id or play_id is None or not rusher_id:
            continue
        records.append(
            {
                "source_version": source_version,
                "season": season,
                "week": week,
                "game_id": game_id,
                "play_id": play_id,
                "rusher_player_id": rusher_id,
                "rusher_player_id_internal": f"gsis:{rusher_id}",
                "rusher_name": _safe_str(row.get("full_name")),
                "position": (_safe_str(row.get("position")) or "").upper() or None,
                "team": _safe_str(row.get("posteam")),
                "rush_attempt": _safe_float(row.get("rush_attempt")),
                "rushing_yards": _safe_float(row.get("rushing_yards")),
                "rush_touchdown": _safe_float(row.get("rush_touchdown")),
                "first_down_rush": _safe_float(row.get("first_down_rush")),
                "two_point_attempt": _safe_float(row.get("two_point_attempt")),
                "two_point_converted": _safe_float(row.get("two_point_converted")),
                "yardline_100": _safe_float(row.get("yardline_100")),
                "goal_to_go": _safe_float(row.get("goal_to_go")),
                "rushing_yards_exp": _safe_float(row.get("rushing_yards_exp")),
                "rushing_td_exp": _safe_float(row.get("rushing_td_exp")),
                "rushing_fd_exp": _safe_float(row.get("rushing_fd_exp")),
                "rush_yards_exp": _safe_float(row.get("rush_yards_exp")),
                "rush_touchdown_exp": _safe_float(row.get("rush_touchdown_exp")),
                "rush_first_down_exp": _safe_float(row.get("rush_first_down_exp")),
                "two_point_conv_exp": _safe_float(row.get("two_point_conv_exp")),
                "qb_scramble": _safe_float(row.get("qb_scramble")),
                "raw_payload_json": _json_row(row),
                "source_refresh_id": source_refresh_id,
                "loaded_at": loaded_at,
                "loaded_by": loaded_by,
            }
        )
    return pd.DataFrame.from_records(records, columns=RAW_PBP_RUSH_COLUMNS)


def build_raw_delete_sql(*, project_id: str, dataset_id: str) -> str:
    return f"""
DELETE FROM `{table_id(project_id, dataset_id, RAW_TABLE)}`
WHERE season BETWEEN @season_start AND @season_end
  AND source_version = @source_version
""".strip()


def build_ideal_metrics_delete_sql(*, project_id: str, dataset_id: str) -> str:
    return f"""
DELETE FROM `{table_id(project_id, dataset_id, DERIVED_TABLE)}`
WHERE season BETWEEN @season_start AND @season_end
  AND source_version = @source_version
""".strip()


def build_pbp_raw_delete_sql(*, project_id: str, dataset_id: str, table_name: str) -> str:
    if table_name not in {RAW_PBP_PASS_TABLE, RAW_PBP_RUSH_TABLE}:
        raise ValueError("table_name must be a PBP ffopportunity raw table")
    return f"""
DELETE FROM `{table_id(project_id, dataset_id, table_name)}`
WHERE season BETWEEN @season_start AND @season_end
  AND source_version = @source_version
""".strip()


def build_pbp_metrics_delete_sql(*, project_id: str, dataset_id: str) -> str:
    return f"""
DELETE FROM `{table_id(project_id, dataset_id, PBP_DERIVED_TABLE)}`
WHERE season BETWEEN @season_start AND @season_end
  AND source_version = @source_version
""".strip()


def build_pbp_metrics_insert_sql(*, project_id: str, dataset_id: str) -> str:
    pass_table = table_id(project_id, dataset_id, RAW_PBP_PASS_TABLE)
    rush_table = table_id(project_id, dataset_id, RAW_PBP_RUSH_TABLE)
    target_table = table_id(project_id, dataset_id, PBP_DERIVED_TABLE)
    return f"""
INSERT INTO `{target_table}` (
  source_version,
  pbp_metric_run_id,
  season,
  week,
  player_id_internal,
  player_name,
  team,
  position,
  receiving_xfp_pbp,
  target_xfp,
  air_xfp,
  red_zone_target_xfp,
  goal_line_target_xfp,
  high_value_target_xfp,
  receiving_touchdown_xfp,
  receiving_xfp_share,
  passing_xfp_pbp,
  rushing_xfp_pbp,
  red_zone_rush_xfp,
  goal_line_rush_xfp,
  high_value_rush_xfp,
  rushing_touchdown_xfp,
  rushing_xfp_share,
  receiving_first_down_exp_pbp,
  rushing_first_down_exp_pbp,
  passing_first_down_exp_pbp,
  high_value_first_down_opportunity_score,
  receiving_chain_mover_score,
  rushing_chain_mover_score,
  high_value_xfp_score,
  red_zone_xfp_score,
  goal_line_xfp_score,
  receiving_vs_rushing_xfp_split,
  opportunity_quality_score,
  missing_flags_json,
  source_provenance_json,
  source_updated_at,
  created_at
)
WITH pass_receiver AS (
  SELECT
    source_version,
    season,
    week,
    receiver_player_id_internal AS player_id_internal,
    ANY_VALUE(receiver_name) AS player_name,
    ANY_VALUE(team) AS team,
    ANY_VALUE(receiver_position) AS position,
    SUM(
      COALESCE(pass_completion_exp, 0.0)
      + COALESCE(pass_first_down_exp, 0.0)
      + COALESCE(pass_touchdown_exp, 0.0) * 6.0
      + COALESCE(two_point_conv_exp, 0.0) * 2.0
      + GREATEST(COALESCE(air_yards, 0.0), 0.0) * 0.05
      + GREATEST(COALESCE(yards_after_catch_exp, 0.0), 0.0) * 0.05
    ) AS receiving_xfp_pbp,
    SUM(COALESCE(pass_completion_exp, 0.0) + COALESCE(pass_first_down_exp, 0.0)) AS target_xfp,
    SUM(GREATEST(COALESCE(air_yards, 0.0), 0.0) * 0.05) AS air_xfp,
    SUM(IF(yardline_100 <= 20,
      COALESCE(pass_completion_exp, 0.0) + COALESCE(pass_first_down_exp, 0.0) + COALESCE(pass_touchdown_exp, 0.0) * 6.0,
      0.0
    )) AS red_zone_target_xfp,
    SUM(IF(yardline_100 <= 5 OR goal_to_go = 1,
      COALESCE(pass_completion_exp, 0.0) + COALESCE(pass_touchdown_exp, 0.0) * 6.0,
      0.0
    )) AS goal_line_target_xfp,
    SUM(IF(yardline_100 <= 20 OR COALESCE(pass_touchdown_exp, 0.0) >= 0.20 OR COALESCE(air_yards, 0.0) >= 20,
      COALESCE(pass_completion_exp, 0.0) + COALESCE(pass_first_down_exp, 0.0) + COALESCE(pass_touchdown_exp, 0.0) * 6.0,
      0.0
    )) AS high_value_target_xfp,
    SUM(COALESCE(pass_touchdown_exp, 0.0) * 6.0) AS receiving_touchdown_xfp,
    SUM(COALESCE(pass_first_down_exp, 0.0)) AS receiving_first_down_exp_pbp,
    MAX(loaded_at) AS source_updated_at
  FROM `{pass_table}`
  WHERE season BETWEEN @season_start AND @season_end
    AND source_version = @source_version
    AND receiver_player_id_internal IS NOT NULL
  GROUP BY source_version, season, week, receiver_player_id_internal
),
pass_passer AS (
  SELECT
    source_version,
    season,
    week,
    passer_player_id_internal AS player_id_internal,
    ANY_VALUE(passer_name) AS player_name,
    ANY_VALUE(team) AS team,
    ANY_VALUE(passer_position) AS position,
    SUM(
      GREATEST(COALESCE(air_yards, 0.0), 0.0) * 0.04
      + COALESCE(pass_touchdown_exp, 0.0) * 4.0
      - COALESCE(pass_interception_exp, 0.0) * 2.0
      + COALESCE(pass_first_down_exp, 0.0) * 0.5
    ) AS passing_xfp_pbp,
    SUM(COALESCE(pass_first_down_exp, 0.0)) AS passing_first_down_exp_pbp,
    MAX(loaded_at) AS source_updated_at
  FROM `{pass_table}`
  WHERE season BETWEEN @season_start AND @season_end
    AND source_version = @source_version
    AND passer_player_id_internal IS NOT NULL
  GROUP BY source_version, season, week, passer_player_id_internal
),
rush_player AS (
  SELECT
    source_version,
    season,
    week,
    rusher_player_id_internal AS player_id_internal,
    ANY_VALUE(rusher_name) AS player_name,
    ANY_VALUE(team) AS team,
    ANY_VALUE(position) AS position,
    SUM(
      GREATEST(COALESCE(rushing_yards_exp, rush_yards_exp, 0.0), 0.0) * 0.1
      + COALESCE(rushing_td_exp, rush_touchdown_exp, 0.0) * 6.0
      + COALESCE(rushing_fd_exp, rush_first_down_exp, 0.0) * 0.5
      + COALESCE(two_point_conv_exp, 0.0) * 2.0
    ) AS rushing_xfp_pbp,
    SUM(IF(yardline_100 <= 20,
      GREATEST(COALESCE(rushing_yards_exp, rush_yards_exp, 0.0), 0.0) * 0.1
      + COALESCE(rushing_td_exp, rush_touchdown_exp, 0.0) * 6.0
      + COALESCE(rushing_fd_exp, rush_first_down_exp, 0.0) * 0.5,
      0.0
    )) AS red_zone_rush_xfp,
    SUM(IF(yardline_100 <= 5 OR goal_to_go = 1,
      GREATEST(COALESCE(rushing_yards_exp, rush_yards_exp, 0.0), 0.0) * 0.1
      + COALESCE(rushing_td_exp, rush_touchdown_exp, 0.0) * 6.0,
      0.0
    )) AS goal_line_rush_xfp,
    SUM(IF(yardline_100 <= 20 OR COALESCE(rushing_td_exp, rush_touchdown_exp, 0.0) >= 0.20,
      GREATEST(COALESCE(rushing_yards_exp, rush_yards_exp, 0.0), 0.0) * 0.1
      + COALESCE(rushing_td_exp, rush_touchdown_exp, 0.0) * 6.0
      + COALESCE(rushing_fd_exp, rush_first_down_exp, 0.0) * 0.5,
      0.0
    )) AS high_value_rush_xfp,
    SUM(COALESCE(rushing_td_exp, rush_touchdown_exp, 0.0) * 6.0) AS rushing_touchdown_xfp,
    SUM(COALESCE(rushing_fd_exp, rush_first_down_exp, 0.0)) AS rushing_first_down_exp_pbp,
    MAX(loaded_at) AS source_updated_at
  FROM `{rush_table}`
  WHERE season BETWEEN @season_start AND @season_end
    AND source_version = @source_version
    AND rusher_player_id_internal IS NOT NULL
  GROUP BY source_version, season, week, rusher_player_id_internal
),
combined AS (
  SELECT
    source_version,
    season,
    week,
    player_id_internal,
    player_name,
    team,
    position,
    receiving_xfp_pbp,
    target_xfp,
    air_xfp,
    red_zone_target_xfp,
    goal_line_target_xfp,
    high_value_target_xfp,
    receiving_touchdown_xfp,
    receiving_first_down_exp_pbp,
    CAST(NULL AS FLOAT64) AS passing_xfp_pbp,
    CAST(NULL AS FLOAT64) AS passing_first_down_exp_pbp,
    CAST(NULL AS FLOAT64) AS rushing_xfp_pbp,
    CAST(NULL AS FLOAT64) AS rushing_first_down_exp_pbp,
    CAST(NULL AS FLOAT64) AS red_zone_rush_xfp,
    CAST(NULL AS FLOAT64) AS goal_line_rush_xfp,
    CAST(NULL AS FLOAT64) AS high_value_rush_xfp,
    CAST(NULL AS FLOAT64) AS rushing_touchdown_xfp,
    source_updated_at
  FROM pass_receiver
  UNION ALL
  SELECT
    source_version,
    season,
    week,
    player_id_internal,
    player_name,
    team,
    position,
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    passing_xfp_pbp,
    passing_first_down_exp_pbp,
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    source_updated_at
  FROM pass_passer
  UNION ALL
  SELECT
    source_version,
    season,
    week,
    player_id_internal,
    player_name,
    team,
    position,
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    CAST(NULL AS FLOAT64),
    rushing_xfp_pbp,
    rushing_first_down_exp_pbp,
    red_zone_rush_xfp,
    goal_line_rush_xfp,
    high_value_rush_xfp,
    rushing_touchdown_xfp,
    source_updated_at
  FROM rush_player
),
weekly AS (
  SELECT
    source_version,
    season,
    week,
    player_id_internal,
    ANY_VALUE(player_name) AS player_name,
    ANY_VALUE(team) AS team,
    ANY_VALUE(position) AS position,
    SUM(receiving_xfp_pbp) AS receiving_xfp_pbp,
    SUM(target_xfp) AS target_xfp,
    SUM(air_xfp) AS air_xfp,
    SUM(red_zone_target_xfp) AS red_zone_target_xfp,
    SUM(goal_line_target_xfp) AS goal_line_target_xfp,
    SUM(high_value_target_xfp) AS high_value_target_xfp,
    SUM(receiving_touchdown_xfp) AS receiving_touchdown_xfp,
    SUM(receiving_first_down_exp_pbp) AS receiving_first_down_exp_pbp,
    SUM(passing_xfp_pbp) AS passing_xfp_pbp,
    SUM(passing_first_down_exp_pbp) AS passing_first_down_exp_pbp,
    SUM(rushing_xfp_pbp) AS rushing_xfp_pbp,
    SUM(rushing_first_down_exp_pbp) AS rushing_first_down_exp_pbp,
    SUM(red_zone_rush_xfp) AS red_zone_rush_xfp,
    SUM(goal_line_rush_xfp) AS goal_line_rush_xfp,
    SUM(high_value_rush_xfp) AS high_value_rush_xfp,
    SUM(rushing_touchdown_xfp) AS rushing_touchdown_xfp,
    MAX(source_updated_at) AS source_updated_at
  FROM combined
  GROUP BY source_version, season, week, player_id_internal
),
team_week_totals AS (
  SELECT
    source_version,
    season,
    week,
    team,
    SUM(receiving_xfp_pbp) AS team_receiving_xfp_pbp,
    SUM(rushing_xfp_pbp) AS team_rushing_xfp_pbp
  FROM weekly
  GROUP BY source_version, season, week, team
)
SELECT
  weekly.source_version,
  @pbp_metric_run_id AS pbp_metric_run_id,
  weekly.season,
  weekly.week,
  REGEXP_REPLACE(weekly.player_id_internal, r'^gsis:', '') AS player_id_internal,
  weekly.player_name,
  weekly.team,
  weekly.position,
  weekly.receiving_xfp_pbp,
  weekly.target_xfp,
  weekly.air_xfp,
  weekly.red_zone_target_xfp,
  weekly.goal_line_target_xfp,
  weekly.high_value_target_xfp,
  weekly.receiving_touchdown_xfp,
  SAFE_DIVIDE(weekly.receiving_xfp_pbp, NULLIF(team_week_totals.team_receiving_xfp_pbp, 0)) AS receiving_xfp_share,
  weekly.passing_xfp_pbp,
  weekly.rushing_xfp_pbp,
  weekly.red_zone_rush_xfp,
  weekly.goal_line_rush_xfp,
  weekly.high_value_rush_xfp,
  weekly.rushing_touchdown_xfp,
  SAFE_DIVIDE(weekly.rushing_xfp_pbp, NULLIF(team_week_totals.team_rushing_xfp_pbp, 0)) AS rushing_xfp_share,
  weekly.receiving_first_down_exp_pbp,
  weekly.rushing_first_down_exp_pbp,
  weekly.passing_first_down_exp_pbp,
  LEAST(100.0, GREATEST(0.0, (
    COALESCE(weekly.receiving_first_down_exp_pbp, 0.0)
    + COALESCE(weekly.rushing_first_down_exp_pbp, 0.0)
    + COALESCE(weekly.passing_first_down_exp_pbp, 0.0)
  ) * 10.0)) AS high_value_first_down_opportunity_score,
  LEAST(100.0, GREATEST(0.0, COALESCE(weekly.receiving_first_down_exp_pbp, 0.0) * 12.0)) AS receiving_chain_mover_score,
  LEAST(100.0, GREATEST(0.0, COALESCE(weekly.rushing_first_down_exp_pbp, 0.0) * 12.0)) AS rushing_chain_mover_score,
  LEAST(100.0, GREATEST(0.0, (COALESCE(weekly.high_value_target_xfp, 0.0) + COALESCE(weekly.high_value_rush_xfp, 0.0)) * 8.0)) AS high_value_xfp_score,
  LEAST(100.0, GREATEST(0.0, (COALESCE(weekly.red_zone_target_xfp, 0.0) + COALESCE(weekly.red_zone_rush_xfp, 0.0)) * 8.0)) AS red_zone_xfp_score,
  LEAST(100.0, GREATEST(0.0, (COALESCE(weekly.goal_line_target_xfp, 0.0) + COALESCE(weekly.goal_line_rush_xfp, 0.0)) * 12.0)) AS goal_line_xfp_score,
  SAFE_DIVIDE(weekly.receiving_xfp_pbp, NULLIF(COALESCE(weekly.receiving_xfp_pbp, 0.0) + COALESCE(weekly.rushing_xfp_pbp, 0.0), 0)) AS receiving_vs_rushing_xfp_split,
  LEAST(100.0, GREATEST(0.0, (
    COALESCE(weekly.receiving_xfp_pbp, 0.0)
    + COALESCE(weekly.rushing_xfp_pbp, 0.0)
    + COALESCE(weekly.passing_xfp_pbp, 0.0)
  ) * 4.0)) AS opportunity_quality_score,
  TO_JSON_STRING(STRUCT(
    weekly.receiving_xfp_pbp IS NULL AS receiving_pbp_missing,
    weekly.rushing_xfp_pbp IS NULL AS rushing_pbp_missing,
    weekly.passing_xfp_pbp IS NULL AS passing_pbp_missing,
    weekly.receiving_first_down_exp_pbp IS NULL AS receiving_first_down_proxy_missing,
    weekly.rushing_first_down_exp_pbp IS NULL AS rushing_first_down_proxy_missing,
    weekly.passing_first_down_exp_pbp IS NULL AS passing_first_down_proxy_missing,
    FALSE AS yardline_context_unavailable,
    TRUE AS exact_ffopportunity_fantasy_points_exp_unavailable,
    'derived from source expected component columns, not official fantasy xFP' AS xfp_proxy_policy
  )) AS missing_flags_json,
  TO_JSON_STRING(STRUCT(
    'raw_ffopportunity_pbp_pass' AS pass_source_table,
    'raw_ffopportunity_pbp_rush' AS rush_source_table,
    @source_version AS source_version,
    @season_start AS season_start,
    @season_end AS season_end,
    'source seasons only; target season excluded by feature mart' AS leakage_policy
  )) AS source_provenance_json,
  weekly.source_updated_at,
  CURRENT_TIMESTAMP() AS created_at
FROM weekly
LEFT JOIN team_week_totals
  ON weekly.source_version = team_week_totals.source_version
 AND weekly.season = team_week_totals.season
 AND weekly.week = team_week_totals.week
 AND weekly.team = team_week_totals.team
""".strip()


def build_ideal_metrics_insert_sql(*, project_id: str, dataset_id: str) -> str:
    raw_table = table_id(project_id, dataset_id, RAW_TABLE)
    target_table = table_id(project_id, dataset_id, DERIVED_TABLE)
    metrics_table = table_id(project_id, dataset_id, "player_week_advanced_metrics")
    participation_table = table_id(project_id, dataset_id, "stg_participation_context")
    return f"""
INSERT INTO `{target_table}` (
  source_version,
  ideal_metric_run_id,
  season,
  week,
  player_id_internal,
  player_name,
  team,
  position,
  expected_fantasy_points,
  expected_rushing_points,
  expected_receiving_points,
  expected_passing_points,
  fantasy_points,
  fantasy_points_over_expectation,
  xfp_share,
  xfp_score,
  high_value_xfp_score,
  offensive_snap_share,
  snap_count,
  snap_share_trend,
  role_stability_from_snaps,
  target_share,
  air_yards_share,
  wopr,
  receiving_role_dominance_xfp,
  receiving_xfp_per_snap,
  rush_xfp,
  receiving_xfp,
  high_value_touch_xfp,
  goal_line_usage_score,
  red_zone_usage_score,
  qb_ngs_efficiency_score,
  injury_risk_score,
  depth_chart_role_score,
  missing_flags_json,
  source_provenance_json,
  source_updated_at,
  created_at
)
WITH xfp AS (
  SELECT
    source_version,
    season,
    week,
    player_id_internal,
    ANY_VALUE(player_name) AS player_name,
    ANY_VALUE(team) AS team,
    ANY_VALUE(position) AS position,
    SUM(total_fantasy_points_exp) AS expected_fantasy_points,
    SUM(rush_fantasy_points_exp) AS expected_rushing_points,
    SUM(rec_fantasy_points_exp) AS expected_receiving_points,
    SUM(pass_fantasy_points_exp) AS expected_passing_points,
    SUM(total_fantasy_points) AS fantasy_points,
    SUM(total_fantasy_points_diff) AS fantasy_points_over_expectation,
    SUM(rush_fantasy_points_exp) AS rush_xfp,
    SUM(rec_fantasy_points_exp) AS receiving_xfp,
    SUM(COALESCE(rush_fantasy_points_exp, 0) + COALESCE(rec_fantasy_points_exp, 0)) AS high_value_touch_xfp,
    MAX(loaded_at) AS source_updated_at
  FROM `{raw_table}`
  WHERE season BETWEEN @season_start AND @season_end
    AND source_version = @source_version
  GROUP BY source_version, season, week, player_id_internal
),
team_xfp AS (
  SELECT
    source_version,
    season,
    week,
    team,
    SUM(GREATEST(COALESCE(expected_fantasy_points, 0), 0)) AS team_expected_fantasy_points
  FROM xfp
  GROUP BY source_version, season, week, team
),
metrics AS (
  SELECT
    season,
    week,
    player_id_internal,
    position,
    AVG(target_share) AS target_share,
    AVG(air_yards_share) AS air_yards_share,
    AVG(wopr) AS wopr,
    AVG(snap_share) AS snap_share,
    AVG(cpoe) AS cpoe,
    AVG(red_zone_touches) AS red_zone_touches,
    AVG(inside_5_carries) AS inside_5_carries,
    ANY_VALUE(missing_data_flags) AS metrics_missing_flags
  FROM `{metrics_table}`
  WHERE season BETWEEN @season_start AND @season_end
    AND scoring_profile_id = 'ppr'
    AND league_type_id = 'redraft'
    AND roster_format_id = 'one_qb'
  GROUP BY season, week, player_id_internal, position
),
participation AS (
  SELECT
    season,
    week,
    player_id_internal,
    SUM(offense_snaps) AS snap_count,
    AVG(offense_pct) AS offense_pct,
    ANY_VALUE(missing_data_flags) AS participation_missing_flags
  FROM `{participation_table}`
  WHERE season BETWEEN @season_start AND @season_end
  GROUP BY season, week, player_id_internal
),
joined AS (
  SELECT
    xfp.*,
    SAFE_DIVIDE(GREATEST(COALESCE(xfp.expected_fantasy_points, 0), 0), NULLIF(team_xfp.team_expected_fantasy_points, 0)) AS xfp_share,
    metrics.target_share,
    metrics.air_yards_share,
    metrics.wopr,
    COALESCE(participation.offense_pct, metrics.snap_share) AS offensive_snap_share,
    participation.snap_count,
    metrics.cpoe,
    metrics.red_zone_touches,
    metrics.inside_5_carries,
    metrics.metrics_missing_flags,
    participation.participation_missing_flags
  FROM xfp
  LEFT JOIN team_xfp
    ON xfp.source_version = team_xfp.source_version
   AND xfp.season = team_xfp.season
   AND xfp.week = team_xfp.week
   AND xfp.team = team_xfp.team
  LEFT JOIN metrics
    ON xfp.season = metrics.season
   AND xfp.week = metrics.week
   AND REGEXP_REPLACE(xfp.player_id_internal, r'^gsis:', '') = REGEXP_REPLACE(metrics.player_id_internal, r'^gsis:', '')
   AND xfp.position = metrics.position
  LEFT JOIN participation
    ON xfp.season = participation.season
   AND xfp.week = participation.week
   AND REGEXP_REPLACE(xfp.player_id_internal, r'^gsis:', '') = REGEXP_REPLACE(participation.player_id_internal, r'^gsis:', '')
)
SELECT
  source_version,
  @ideal_metric_run_id AS ideal_metric_run_id,
  season,
  week,
  player_id_internal,
  player_name,
  team,
  position,
  expected_fantasy_points,
  expected_rushing_points,
  expected_receiving_points,
  expected_passing_points,
  fantasy_points,
  fantasy_points_over_expectation,
  xfp_share,
  LEAST(100.0, GREATEST(0.0, expected_fantasy_points * 6.0)) AS xfp_score,
  LEAST(100.0, GREATEST(0.0, high_value_touch_xfp * 8.0)) AS high_value_xfp_score,
  offensive_snap_share,
  snap_count,
  AVG(offensive_snap_share) OVER (
    PARTITION BY player_id_internal
    ORDER BY season, week
    ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
  ) - AVG(offensive_snap_share) OVER (
    PARTITION BY player_id_internal
    ORDER BY season, week
    ROWS BETWEEN 7 PRECEDING AND 4 PRECEDING
  ) AS snap_share_trend,
  LEAST(100.0, GREATEST(0.0, COALESCE(offensive_snap_share, 0) * 100.0 - COALESCE(STDDEV(offensive_snap_share) OVER (
    PARTITION BY player_id_internal
    ORDER BY season, week
    ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
  ), 0.0) * 100.0)) AS role_stability_from_snaps,
  target_share,
  air_yards_share,
  wopr,
  LEAST(100.0, GREATEST(0.0, COALESCE(xfp_share, 0) * 100.0 + COALESCE(target_share, 0) * 35.0 + COALESCE(wopr, 0) * 20.0)) AS receiving_role_dominance_xfp,
  SAFE_DIVIDE(receiving_xfp, NULLIF(snap_count, 0)) AS receiving_xfp_per_snap,
  rush_xfp,
  receiving_xfp,
  high_value_touch_xfp,
  LEAST(100.0, GREATEST(0.0, COALESCE(inside_5_carries, 0) * 12.0)) AS goal_line_usage_score,
  LEAST(100.0, GREATEST(0.0, COALESCE(red_zone_touches, 0) * 4.0)) AS red_zone_usage_score,
  CASE
    WHEN position = 'QB' AND cpoe IS NOT NULL THEN LEAST(100.0, GREATEST(0.0, 50.0 + cpoe * 5.0))
    ELSE NULL
  END AS qb_ngs_efficiency_score,
  CAST(NULL AS FLOAT64) AS injury_risk_score,
  CAST(NULL AS FLOAT64) AS depth_chart_role_score,
  TO_JSON_STRING(STRUCT(
    expected_fantasy_points IS NULL AS expected_fantasy_points_missing,
    xfp_share IS NULL AS xfp_share_missing,
    offensive_snap_share IS NULL AS offensive_snap_share_missing,
    snap_count IS NULL AS snap_count_missing,
    target_share IS NULL AS target_share_missing,
    TRUE AS true_route_share_missing_flag,
    TRUE AS first_read_share_missing_flag,
    TRUE AS direct_injury_context_unavailable,
    TRUE AS direct_depth_chart_context_unavailable,
    position = 'QB' AND cpoe IS NULL AS qb_ngs_efficiency_missing,
    metrics_missing_flags AS metrics_missing_flags,
    participation_missing_flags AS participation_missing_flags
  )) AS missing_flags_json,
  TO_JSON_STRING(STRUCT(
    'ffopportunity' AS expected_fantasy_source,
    'raw_ffopportunity_weekly' AS raw_xfp_table,
    'player_week_advanced_metrics' AS role_source_table,
    'stg_participation_context' AS snap_source_table,
    'source seasons are weekly rows only; feature mart excludes target season' AS leakage_policy
  )) AS source_provenance_json,
  source_updated_at,
  CURRENT_TIMESTAMP() AS created_at
FROM joined
""".strip()


def _bigquery_params(season_start: int, season_end: int, source_version: str, ideal_metric_run_id: str | None = None) -> list[Any]:
    from google.cloud import bigquery

    params: list[Any] = [
        bigquery.ScalarQueryParameter("season_start", "INT64", int(season_start)),
        bigquery.ScalarQueryParameter("season_end", "INT64", int(season_end)),
        bigquery.ScalarQueryParameter("source_version", "STRING", source_version),
    ]
    if ideal_metric_run_id is not None:
        params.append(bigquery.ScalarQueryParameter("ideal_metric_run_id", "STRING", ideal_metric_run_id))
    return params


def _pbp_bigquery_params(
    season_start: int,
    season_end: int,
    source_version: str,
    pbp_metric_run_id: str | None = None,
) -> list[Any]:
    from google.cloud import bigquery

    params = _bigquery_params(season_start, season_end, source_version)
    if pbp_metric_run_id is not None:
        params.append(bigquery.ScalarQueryParameter("pbp_metric_run_id", "STRING", pbp_metric_run_id))
    return params


def dry_run_summary(frame: pd.DataFrame) -> dict[str, Any]:
    if frame.empty:
        return {
            "source_row_count": 0,
            "normalized_row_count": 0,
            "season_min": None,
            "season_max": None,
            "position_counts": {},
            "expected_points_columns_present": False,
        }
    return {
        "source_row_count": int(len(frame)),
        "season_min": int(frame["season"].min()),
        "season_max": int(frame["season"].max()),
        "week_min": int(frame["week"].min()),
        "week_max": int(frame["week"].max()),
        "position_counts": {str(k): int(v) for k, v in frame["position"].value_counts().to_dict().items()},
        "expected_points_columns_present": all(
            column in frame.columns
            for column in ("total_fantasy_points_exp", "rush_fantasy_points_exp", "rec_fantasy_points_exp", "pass_fantasy_points_exp")
        ),
    }


def write_raw_ffopportunity_weekly(
    *,
    client: Any,
    frame: pd.DataFrame,
    project_id: str,
    dataset_id: str,
    season_start: int,
    season_end: int,
    source_version: str,
) -> dict[str, Any]:
    from google.cloud import bigquery

    require_write_authorization()
    delete_job_config = bigquery.QueryJobConfig(
        query_parameters=_bigquery_params(season_start, season_end, source_version)
    )
    client.query(build_raw_delete_sql(project_id=project_id, dataset_id=dataset_id), job_config=delete_job_config).result()
    if frame.empty:
        return {"deleted_season_start": season_start, "deleted_season_end": season_end, "written_row_count": 0}
    load_job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
    client.load_table_from_dataframe(
        frame,
        table_id(project_id, dataset_id, RAW_TABLE),
        job_config=load_job_config,
    ).result()
    return {"deleted_season_start": season_start, "deleted_season_end": season_end, "written_row_count": int(len(frame))}


def write_raw_ffopportunity_pbp(
    *,
    client: Any,
    frame: pd.DataFrame,
    project_id: str,
    dataset_id: str,
    season_start: int,
    season_end: int,
    source_version: str,
    stat_type: str,
) -> dict[str, Any]:
    from google.cloud import bigquery

    if stat_type not in {"pbp_pass", "pbp_rush"}:
        raise ValueError("stat_type must be pbp_pass or pbp_rush")
    require_write_authorization()
    table_name = RAW_PBP_PASS_TABLE if stat_type == "pbp_pass" else RAW_PBP_RUSH_TABLE
    delete_job_config = bigquery.QueryJobConfig(query_parameters=_bigquery_params(season_start, season_end, source_version))
    client.query(
        build_pbp_raw_delete_sql(project_id=project_id, dataset_id=dataset_id, table_name=table_name),
        job_config=delete_job_config,
    ).result()
    if frame.empty:
        return {"stat_type": stat_type, "deleted_season_start": season_start, "deleted_season_end": season_end, "written_row_count": 0}
    load_job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
    client.load_table_from_dataframe(
        frame,
        table_id(project_id, dataset_id, table_name),
        job_config=load_job_config,
    ).result()
    return {
        "stat_type": stat_type,
        "target_table": table_id(project_id, dataset_id, table_name),
        "deleted_season_start": season_start,
        "deleted_season_end": season_end,
        "written_row_count": int(len(frame)),
    }


def refresh_ideal_metrics(
    *,
    client: Any,
    project_id: str,
    dataset_id: str,
    season_start: int,
    season_end: int,
    source_version: str,
    ideal_metric_run_id: str,
) -> dict[str, Any]:
    from google.cloud import bigquery

    require_write_authorization()
    params = _bigquery_params(season_start, season_end, source_version, ideal_metric_run_id)
    job_config = bigquery.QueryJobConfig(query_parameters=params)
    client.query(build_ideal_metrics_delete_sql(project_id=project_id, dataset_id=dataset_id), job_config=job_config).result()
    insert_job = client.query(build_ideal_metrics_insert_sql(project_id=project_id, dataset_id=dataset_id), job_config=job_config)
    insert_job.result()
    count_sql = f"""
SELECT COUNT(*) AS row_count
FROM `{table_id(project_id, dataset_id, DERIVED_TABLE)}`
WHERE season BETWEEN @season_start AND @season_end
  AND source_version = @source_version
""".strip()
    count_rows = list(client.query(count_sql, job_config=job_config).result())
    row_count = int(dict(count_rows[0]).get("row_count", 0)) if count_rows else 0
    return {"ideal_metric_run_id": ideal_metric_run_id, "derived_row_count": row_count}


def refresh_pbp_metrics(
    *,
    client: Any,
    project_id: str,
    dataset_id: str,
    season_start: int,
    season_end: int,
    source_version: str,
    pbp_metric_run_id: str,
) -> dict[str, Any]:
    from google.cloud import bigquery

    require_write_authorization()
    params = _pbp_bigquery_params(season_start, season_end, source_version, pbp_metric_run_id)
    job_config = bigquery.QueryJobConfig(query_parameters=params)
    client.query(build_pbp_metrics_delete_sql(project_id=project_id, dataset_id=dataset_id), job_config=job_config).result()
    insert_job = client.query(build_pbp_metrics_insert_sql(project_id=project_id, dataset_id=dataset_id), job_config=job_config)
    insert_job.result()
    count_sql = f"""
SELECT COUNT(*) AS row_count
FROM `{table_id(project_id, dataset_id, PBP_DERIVED_TABLE)}`
WHERE season BETWEEN @season_start AND @season_end
  AND source_version = @source_version
""".strip()
    count_rows = list(client.query(count_sql, job_config=job_config).result())
    row_count = int(dict(count_rows[0]).get("row_count", 0)) if count_rows else 0
    return {"pbp_metric_run_id": pbp_metric_run_id, "derived_row_count": row_count}


def run(
    *,
    season_start: int,
    season_end: int,
    source_version: str,
    project_id: str,
    dataset_id: str,
    write: bool,
    derive: bool,
) -> dict[str, Any]:
    seasons = list(range(int(season_start), int(season_end) + 1))
    source = load_ffopportunity_weekly(seasons)
    normalized = normalize_ffopportunity_weekly(source, source_version=source_version)
    result: dict[str, Any] = {
        "dry_run": not write,
        "write": write,
        "derive": derive,
        "project_id": project_id,
        "dataset_id": dataset_id,
        "source_table": RAW_TABLE,
        "derived_table": DERIVED_TABLE,
        "source_summary": dry_run_summary(source),
        "normalized_summary": dry_run_summary(normalized),
    }
    if not write:
        return result
    require_write_authorization()
    from google.cloud import bigquery

    client = bigquery.Client(project=project_id)
    result["raw_write_summary"] = write_raw_ffopportunity_weekly(
        client=client,
        frame=normalized,
        project_id=project_id,
        dataset_id=dataset_id,
        season_start=season_start,
        season_end=season_end,
        source_version=source_version,
    )
    if derive:
        result["derived_write_summary"] = refresh_ideal_metrics(
            client=client,
            project_id=project_id,
            dataset_id=dataset_id,
            season_start=season_start,
            season_end=season_end,
            source_version=source_version,
            ideal_metric_run_id=f"ideal-stats-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}",
        )
    return result


def run_pbp(
    *,
    season_start: int,
    season_end: int,
    source_version: str,
    project_id: str,
    dataset_id: str,
    write: bool,
    derive: bool,
    stat_types: tuple[str, ...] = ("pbp_pass", "pbp_rush"),
) -> dict[str, Any]:
    seasons = list(range(int(season_start), int(season_end) + 1))
    result: dict[str, Any] = {
        "dry_run": not write,
        "write": write,
        "derive": derive,
        "project_id": project_id,
        "dataset_id": dataset_id,
        "source_version": source_version,
        "raw_tables": [RAW_PBP_PASS_TABLE if stat_type == "pbp_pass" else RAW_PBP_RUSH_TABLE for stat_type in stat_types],
        "derived_table": PBP_DERIVED_TABLE,
        "lanes": {},
    }
    normalized_by_type: dict[str, pd.DataFrame] = {}
    for stat_type in stat_types:
        source = load_ffopportunity_pbp(seasons, stat_type=stat_type)
        if stat_type == "pbp_pass":
            normalized = normalize_ffopportunity_pbp_pass(source, source_version=source_version)
            identity_column = "receiver_player_id_internal"
            position_column = "receiver_position"
        else:
            normalized = normalize_ffopportunity_pbp_rush(source, source_version=source_version)
            identity_column = "rusher_player_id_internal"
            position_column = "position"
        normalized_by_type[stat_type] = normalized
        result["lanes"][stat_type] = {
            "source_row_count": int(len(source)),
            "normalized_row_count": int(len(normalized)),
            "mapped_row_count": int(normalized[identity_column].notna().sum()) if identity_column in normalized else 0,
            "season_min": int(normalized["season"].min()) if not normalized.empty else None,
            "season_max": int(normalized["season"].max()) if not normalized.empty else None,
            "position_counts": {str(k): int(v) for k, v in normalized.get(position_column, pd.Series(dtype=str)).value_counts().to_dict().items()},
        }
    if not write:
        return result
    require_write_authorization()
    from google.cloud import bigquery

    client = bigquery.Client(project=project_id)
    result["raw_write_summary"] = {}
    for stat_type, normalized in normalized_by_type.items():
        result["raw_write_summary"][stat_type] = write_raw_ffopportunity_pbp(
            client=client,
            frame=normalized,
            project_id=project_id,
            dataset_id=dataset_id,
            season_start=season_start,
            season_end=season_end,
            source_version=source_version,
            stat_type=stat_type,
        )
    if derive:
        result["derived_write_summary"] = refresh_pbp_metrics(
            client=client,
            project_id=project_id,
            dataset_id=dataset_id,
            season_start=season_start,
            season_end=season_end,
            source_version=source_version,
            pbp_metric_run_id=f"pbp-ideal-stats-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}",
        )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest ffopportunity weekly xFP and derive ideal ranking stats.")
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--season-start", type=int, default=DEFAULT_SEASON_START)
    parser.add_argument("--season-end", type=int, default=DEFAULT_SEASON_END)
    parser.add_argument("--source-version", default=DEFAULT_SOURCE_VERSION)
    parser.add_argument("--mode", choices=("weekly", "pbp"), default="weekly")
    parser.add_argument("--pbp-stat-type", choices=("pbp_all", "pbp_pass", "pbp_rush"), default="pbp_all")
    parser.add_argument("--write", action="store_true", help="Write bounded raw rows. Requires ALLOW_NFLVERSE_IDEAL_STATS_INGEST=true.")
    parser.add_argument("--derive", action="store_true", help="Refresh derived ideal metrics after raw ingest. Requires --write.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and normalize only.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.derive and not args.write:
        raise SystemExit("--derive requires --write")
    if args.mode == "pbp":
        source_version = args.source_version
        if source_version == DEFAULT_SOURCE_VERSION:
            source_version = DEFAULT_PBP_SOURCE_VERSION
        stat_types = ("pbp_pass", "pbp_rush") if args.pbp_stat_type == "pbp_all" else (args.pbp_stat_type,)
        result = run_pbp(
            season_start=args.season_start,
            season_end=args.season_end,
            source_version=source_version,
            project_id=args.project,
            dataset_id=args.dataset,
            write=bool(args.write),
            derive=bool(args.derive),
            stat_types=stat_types,
        )
    else:
        result = run(
            season_start=args.season_start,
            season_end=args.season_end,
            source_version=args.source_version,
            project_id=args.project,
            dataset_id=args.dataset,
            write=bool(args.write),
            derive=bool(args.derive),
        )
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
