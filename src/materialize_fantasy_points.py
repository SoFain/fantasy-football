"""Materialize fantasy points by scoring profile."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from google.api_core.exceptions import NotFound
from google.cloud import bigquery

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.bigquery_guardrails import query_to_dataframe, run_bigquery_query
from src.build_player_identity import normalize_player_name
from src.fantasy_scoring import calculate_fantasy_breakdown, load_scoring_profiles
from src.load import get_bigquery_project

logger = logging.getLogger("materialize_fantasy_points")

DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_PROFILE_IDS = ("standard", "half_ppr", "ppr")
OUTPUT_TABLE = "analytics_player_fantasy_points_by_profile"
HISTORICAL_NFLVERSE_REQUIRED_FIELDS = (
    "passing_yards",
    "passing_tds",
    "interceptions",
    "passing_2pt_conversions",
    "rushing_yards",
    "rushing_tds",
    "rushing_2pt_conversions",
    "receptions",
    "receiving_yards",
    "receiving_tds",
    "receiving_2pt_conversions",
    "fumbles_lost",
    "return_tds",
)
HISTORICAL_NFLVERSE_GNG_REQUIRED_FIELDS = (
    "passing_completions",
    "sacks_taken",
    "rushing_attempts",
    "rushing_first_downs",
    "receiving_first_downs",
)
SKILL_POSITIONS = ("QB", "RB", "WR", "TE")


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


def table_columns(client: bigquery.Client, dataset_id: str, table_name: str) -> set[str]:
    table = client.get_table(f"{client.project}.{dataset_id}.{table_name}")
    return {field.name for field in table.schema}


def _expr(columns: set[str], names: list[str], alias: str, type_name: str = "STRING") -> str:
    for name in names:
        if name in columns:
            return f"CAST({name} AS {type_name}) AS {alias}"
    return f"CAST(NULL AS {type_name}) AS {alias}"


def _select_source_table(client: bigquery.Client, dataset_id: str) -> str:
    if table_exists(client, dataset_id, "analytics_player_weekly_truth"):
        return "analytics_player_weekly_truth"
    if table_exists(client, dataset_id, "weekly_metrics"):
        return "weekly_metrics"
    raise RuntimeError("Neither analytics_player_weekly_truth nor weekly_metrics exists.")


def _where_clause(columns: set[str], season: int | None, week: int | None) -> str:
    filters = []
    if season is not None:
        filters.append("season = @season")
    if week is not None:
        filters.append("week = @week")
    if "season_type" in columns:
        filters.append("season_type = 'REG'")
    return "WHERE " + " AND ".join(filters) if filters else ""


def _bounded_where_clause(
    *,
    season_start: int,
    season_end: int,
    week_start: int | None,
    week_end: int | None,
    positions: tuple[str, ...],
    alias: str = "s",
) -> tuple[str, list[bigquery.ScalarQueryParameter | bigquery.ArrayQueryParameter]]:
    filters = [
        f"{alias}.season BETWEEN @season_start AND @season_end",
        f"{alias}.position IN UNNEST(@positions)",
    ]
    query_parameters: list[bigquery.ScalarQueryParameter | bigquery.ArrayQueryParameter] = [
        bigquery.ScalarQueryParameter("season_start", "INT64", int(season_start)),
        bigquery.ScalarQueryParameter("season_end", "INT64", int(season_end)),
        bigquery.ArrayQueryParameter("positions", "STRING", list(positions)),
    ]
    if week_start is not None:
        filters.append(f"{alias}.week >= @week_start")
        query_parameters.append(bigquery.ScalarQueryParameter("week_start", "INT64", int(week_start)))
    if week_end is not None:
        filters.append(f"{alias}.week <= @week_end")
        query_parameters.append(bigquery.ScalarQueryParameter("week_end", "INT64", int(week_end)))
    return " AND ".join(filters), query_parameters


def _json_float_expr(json_column: str, path: str) -> str:
    return f"SAFE_CAST(JSON_VALUE({json_column}, '$.{path}') AS FLOAT64)"


def build_historical_nflverse_stat_sql(
    project_id: str,
    dataset_id: str,
    *,
    season_start: int,
    season_end: int,
    week_start: int | None = 1,
    week_end: int | None = 18,
    positions: tuple[str, ...] = SKILL_POSITIONS,
) -> tuple[str, list[bigquery.ScalarQueryParameter | bigquery.ArrayQueryParameter]]:
    """Build the read-only historical nflverse stat query used for target scoring."""

    filters, query_parameters = _bounded_where_clause(
        season_start=season_start,
        season_end=season_end,
        week_start=week_start,
        week_end=week_end,
        positions=positions,
        alias="s",
    )
    raw_table = f"`{project_id}.{dataset_id}.raw_nflverse_weekly`"
    stg_table = f"`{project_id}.{dataset_id}.stg_player_week_stats`"
    return f"""
    SELECT
        s.player_id_internal,
        COALESCE(s.nflverse_player_id, s.gsis_id, s.player_id_internal) AS source_player_key,
        s.player_name AS player_display_name,
        s.team,
        s.opponent_team AS opponent,
        s.position,
        s.season,
        s.week,
        s.passing_yards,
        s.passing_tds,
        {_json_float_expr("w.raw_payload_json", "passing_interceptions")} AS interceptions,
        {_json_float_expr("w.raw_payload_json", "passing_2pt_conversions")} AS passing_2pt_conversions,
        s.rushing_yards,
        s.rushing_tds,
        {_json_float_expr("w.raw_payload_json", "rushing_2pt_conversions")} AS rushing_2pt_conversions,
        s.receptions,
        s.receiving_yards,
        s.receiving_tds,
        {_json_float_expr("w.raw_payload_json", "receiving_2pt_conversions")} AS receiving_2pt_conversions,
        (
            {_json_float_expr("w.raw_payload_json", "rushing_fumbles_lost")}
            + {_json_float_expr("w.raw_payload_json", "receiving_fumbles_lost")}
            + {_json_float_expr("w.raw_payload_json", "sack_fumbles_lost")}
        ) AS fumbles_lost,
        (
            {_json_float_expr("w.raw_payload_json", "special_teams_tds")}
            + {_json_float_expr("w.raw_payload_json", "fumble_recovery_tds")}
        ) AS return_tds,
        {_json_float_expr("w.raw_payload_json", "completions")} AS passing_completions,
        {_json_float_expr("w.raw_payload_json", "sacks_suffered")} AS sacks_taken,
        s.carries AS rushing_attempts,
        {_json_float_expr("w.raw_payload_json", "rushing_first_downs")} AS rushing_first_downs,
        {_json_float_expr("w.raw_payload_json", "receiving_first_downs")} AS receiving_first_downs,
        w.raw_payload_json AS source_payload_json
    FROM {stg_table} s
    JOIN {raw_table} w
      ON s.season = w.season
      AND s.week = w.week
      AND s.team = w.team
      AND COALESCE(s.nflverse_player_id, s.gsis_id, s.player_id_internal) = w.player_id
    WHERE {filters}
      AND JSON_VALUE(w.raw_payload_json, '$.season_type') = 'REG'
    """, query_parameters


def fetch_historical_nflverse_stat_rows(
    client: bigquery.Client,
    dataset_id: str,
    *,
    season_start: int,
    season_end: int,
    week_start: int | None = 1,
    week_end: int | None = 18,
    positions: tuple[str, ...] = SKILL_POSITIONS,
    allow_large_query: bool = False,
) -> pd.DataFrame:
    sql, query_parameters = build_historical_nflverse_stat_sql(
        client.project,
        dataset_id,
        season_start=season_start,
        season_end=season_end,
        week_start=week_start,
        week_end=week_end,
        positions=positions,
    )
    frame = query_to_dataframe(
        client,
        sql,
        component="fantasy_points",
        query_name="fetch_historical_nflverse_weekly",
        query_parameters=query_parameters,
        allow_large_query=allow_large_query,
    )
    logger.info("Fetched %s historical nflverse stat rows", len(frame))
    return frame


def missing_required_scoring_fields(stat_row: dict[str, Any]) -> list[str]:
    missing = []
    for field in HISTORICAL_NFLVERSE_REQUIRED_FIELDS:
        value = stat_row.get(field)
        if _is_missing_value(value):
            missing.append(field)
    return missing


def _is_missing_value(value: Any) -> bool:
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def validate_complete_scoring_source(
    stat_frame: pd.DataFrame,
    *,
    scoring_profile_ids: tuple[str, ...] = (),
) -> dict[str, Any]:
    required_fields = list(HISTORICAL_NFLVERSE_REQUIRED_FIELDS)
    if "gng_keeper" in scoring_profile_ids:
        required_fields.extend(HISTORICAL_NFLVERSE_GNG_REQUIRED_FIELDS)
    missing_counts = {field: int(stat_frame[field].isna().sum()) if field in stat_frame else len(stat_frame) for field in required_fields}
    missing_fields = {field: count for field, count in missing_counts.items() if count}
    if missing_fields:
        return {
            "complete": False,
            "row_count": int(len(stat_frame)),
            "missing_field_counts": missing_fields,
        }
    return {
        "complete": True,
        "row_count": int(len(stat_frame)),
        "missing_field_counts": {},
    }


def fetch_stat_rows(
    client: bigquery.Client,
    dataset_id: str,
    *,
    season: int | None = None,
    week: int | None = None,
    allow_large_query: bool = False,
) -> tuple[pd.DataFrame, str]:
    source_table = _select_source_table(client, dataset_id)
    columns = table_columns(client, dataset_id, source_table)
    query_parameters = []
    if season is not None:
        query_parameters.append(bigquery.ScalarQueryParameter("season", "INT64", int(season)))
    if week is not None:
        query_parameters.append(bigquery.ScalarQueryParameter("week", "INT64", int(week)))
    select_exprs = [
        _expr(columns, ["player_id", "gsis_id"], "source_player_key"),
        _expr(columns, ["player_display_name", "player_full_name", "player_name", "display_name"], "player_display_name"),
        _expr(columns, ["team", "recent_team"], "team"),
        _expr(columns, ["opponent_team", "opponent"], "opponent"),
        _expr(columns, ["position"], "position"),
        "CAST(season AS INT64) AS season",
        "CAST(week AS INT64) AS week",
        _expr(columns, ["passing_yards"], "passing_yards", "FLOAT64"),
        _expr(columns, ["passing_tds"], "passing_tds", "FLOAT64"),
        _expr(columns, ["interceptions"], "interceptions", "FLOAT64"),
        _expr(columns, ["passing_2pt_conversions", "passing_2pt"], "passing_2pt_conversions", "FLOAT64"),
        _expr(columns, ["rushing_yards"], "rushing_yards", "FLOAT64"),
        _expr(columns, ["rushing_tds"], "rushing_tds", "FLOAT64"),
        _expr(columns, ["rushing_2pt_conversions", "rushing_2pt"], "rushing_2pt_conversions", "FLOAT64"),
        _expr(columns, ["receptions"], "receptions", "FLOAT64"),
        _expr(columns, ["receiving_yards"], "receiving_yards", "FLOAT64"),
        _expr(columns, ["receiving_tds"], "receiving_tds", "FLOAT64"),
        _expr(columns, ["receiving_2pt_conversions", "receiving_2pt"], "receiving_2pt_conversions", "FLOAT64"),
        _expr(columns, ["fumbles_lost", "lost_fumbles"], "fumbles_lost", "FLOAT64"),
        _expr(columns, ["return_tds"], "return_tds", "FLOAT64"),
    ]
    sql = f"""
    SELECT
        {", ".join(select_exprs)}
    FROM `{client.project}.{dataset_id}.{source_table}`
    {_where_clause(columns, season, week)}
    """
    frame = query_to_dataframe(
        client,
        sql,
        component="fantasy_points",
        query_name=f"fetch_{source_table}",
        query_parameters=query_parameters,
        allow_large_query=allow_large_query,
    )
    logger.info("Fetched %s rows from %s", len(frame), source_table)
    return frame, source_table


def fetch_identity_rows(client: bigquery.Client, dataset_id: str) -> pd.DataFrame:
    source_table = None
    if table_exists(client, dataset_id, "player_identity_bridge"):
        source_table = "player_identity_bridge"
    elif table_exists(client, dataset_id, "dim_players_current"):
        source_table = "dim_players_current"
    if not source_table:
        logger.info("No identity bridge table found. Materializing with source keys only.")
        return pd.DataFrame()

    sql = f"""
    SELECT
        player_id_internal,
        gsis_id,
        sleeper_player_id,
        normalized_name,
        position,
        current_team
    FROM `{client.project}.{dataset_id}.{source_table}`
    """
    frame = query_to_dataframe(
        client,
        sql,
        component="fantasy_points",
        query_name=f"fetch_{source_table}",
    )
    logger.info("Fetched %s identity rows from %s", len(frame), source_table)
    return frame


def _identity_maps(identity_frame: pd.DataFrame) -> dict[str, Any]:
    maps: dict[str, Any] = {
        "gsis": {},
        "sleeper": {},
        "name_team_position": {},
        "name_position": {},
    }
    if identity_frame.empty:
        return maps
    for row in identity_frame.to_dict("records"):
        internal_id = row.get("player_id_internal")
        if not internal_id:
            continue
        gsis_id = row.get("gsis_id")
        sleeper_id = row.get("sleeper_player_id")
        normalized_name = row.get("normalized_name")
        position = row.get("position")
        team = row.get("current_team")
        if gsis_id:
            maps["gsis"][str(gsis_id)] = internal_id
        if sleeper_id:
            maps["sleeper"][str(sleeper_id)] = internal_id
        if normalized_name and position and team:
            maps["name_team_position"][(normalized_name, str(team), str(position))] = internal_id
        if normalized_name and position:
            maps["name_position"].setdefault((normalized_name, str(position)), set()).add(internal_id)
    return maps


def _match_identity(stat_row: dict[str, Any], maps: dict[str, Any]) -> str | None:
    if stat_row.get("player_id_internal"):
        return str(stat_row["player_id_internal"])

    source_player_key = stat_row.get("source_player_key")
    if source_player_key and str(source_player_key) in maps["gsis"]:
        return maps["gsis"][str(source_player_key)]
    if source_player_key and str(source_player_key) in maps["sleeper"]:
        return maps["sleeper"][str(source_player_key)]

    normalized_name = normalize_player_name(stat_row.get("player_display_name"))
    team = str(stat_row.get("team") or "")
    position = str(stat_row.get("position") or "")
    if normalized_name and team and position:
        internal_id = maps["name_team_position"].get((normalized_name, team, position))
        if internal_id:
            return internal_id
    if normalized_name and position:
        candidates = maps["name_position"].get((normalized_name, position), set())
        if len(candidates) == 1:
            return next(iter(candidates))
    return None


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _clean_source_key(row: dict[str, Any]) -> str:
    if row.get("source_player_key"):
        return str(row["source_player_key"])
    normalized_name = normalize_player_name(row.get("player_display_name"))
    position = row.get("position") or "UNK"
    team = row.get("team") or "UNK"
    return f"name:{normalized_name}|{position}|{team}"


def build_fantasy_point_rows(
    stat_frame: pd.DataFrame,
    profiles: dict[str, dict[str, Any]],
    identity_frame: pd.DataFrame | None = None,
    *,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    source_table: str = "analytics_player_weekly_truth",
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    now = now or datetime.now(timezone.utc)
    maps = _identity_maps(identity_frame if identity_frame is not None else pd.DataFrame())
    rows = []
    for stat_row in stat_frame.to_dict("records"):
        source_player_key = _clean_source_key(stat_row)
        player_id_internal = _match_identity(stat_row, maps)
        for profile_id, profile in profiles.items():
            breakdown = calculate_fantasy_breakdown(stat_row, profile)
            missing_flags = list(breakdown["missing_data_flags"])
            if not player_id_internal:
                missing_flags.append("missing_player_id_internal")
            scoring_breakdown = {
                key: breakdown[key]
                for key in (
                    "passing_points",
                    "rushing_points",
                    "receiving_points",
                    "reception_points",
                    "turnover_points",
                    "bonus_points",
                    "kicker_points",
                    "dst_points",
                    "total_fantasy_points",
                )
            }
            rows.append({
                "player_id_internal": player_id_internal,
                "source_player_key": source_player_key,
                "player_display_name": stat_row.get("player_display_name"),
                "team": stat_row.get("team"),
                "opponent": stat_row.get("opponent"),
                "position": stat_row.get("position"),
                "season": int(stat_row["season"]),
                "week": int(stat_row["week"]),
                "scoring_profile_id": profile_id,
                "league_type_id": league_type_id,
                "roster_format_id": roster_format_id,
                "passing_points": float(breakdown["passing_points"]),
                "rushing_points": float(breakdown["rushing_points"]),
                "receiving_points": float(breakdown["receiving_points"]),
                "reception_points": float(breakdown["reception_points"]),
                "turnover_points": float(breakdown["turnover_points"]),
                "bonus_points": float(breakdown["bonus_points"]),
                "kicker_points": float(breakdown["kicker_points"]),
                "dst_points": float(breakdown["dst_points"]),
                "total_fantasy_points": float(breakdown["total_fantasy_points"]),
                "scoring_breakdown_json": _json_dumps(scoring_breakdown),
                "source_stat_json": _json_dumps(breakdown["source_stats"]),
                "source_freshness_json": _json_dumps({"source_table": source_table, "generated_at": now.isoformat()}),
                "missing_data_flags": _json_dumps(sorted(set(missing_flags))),
                "created_at": now,
                "updated_at": now,
            })
    return rows


def _output_schema() -> list[bigquery.SchemaField]:
    return [
        bigquery.SchemaField("player_id_internal", "STRING"),
        bigquery.SchemaField("source_player_key", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("player_display_name", "STRING"),
        bigquery.SchemaField("team", "STRING"),
        bigquery.SchemaField("opponent", "STRING"),
        bigquery.SchemaField("position", "STRING"),
        bigquery.SchemaField("season", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("week", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("scoring_profile_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("league_type_id", "STRING"),
        bigquery.SchemaField("roster_format_id", "STRING"),
        bigquery.SchemaField("passing_points", "FLOAT"),
        bigquery.SchemaField("rushing_points", "FLOAT"),
        bigquery.SchemaField("receiving_points", "FLOAT"),
        bigquery.SchemaField("reception_points", "FLOAT"),
        bigquery.SchemaField("turnover_points", "FLOAT"),
        bigquery.SchemaField("bonus_points", "FLOAT"),
        bigquery.SchemaField("kicker_points", "FLOAT"),
        bigquery.SchemaField("dst_points", "FLOAT"),
        bigquery.SchemaField("total_fantasy_points", "FLOAT"),
        bigquery.SchemaField("scoring_breakdown_json", "STRING"),
        bigquery.SchemaField("source_stat_json", "STRING"),
        bigquery.SchemaField("source_freshness_json", "STRING"),
        bigquery.SchemaField("missing_data_flags", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
    ]


def _merge_output_rows(client: bigquery.Client, dataset_id: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        logger.warning("No fantasy point rows built. Skipping write.")
        return

    target_table_id = f"{client.project}.{dataset_id}.{OUTPUT_TABLE}"
    temp_table_id = f"{client.project}.{dataset_id}.{OUTPUT_TABLE}_staging_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    frame = pd.DataFrame(rows)
    job_config = bigquery.LoadJobConfig(
        schema=_output_schema(),
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    try:
        load_job = client.load_table_from_dataframe(frame, temp_table_id, job_config=job_config)
        load_job.result()
        fields = [field.name for field in _output_schema()]
        update_clause = ",\n        ".join(f"{field} = source.{field}" for field in fields if field not in ("source_player_key", "season", "week", "scoring_profile_id"))
        insert_fields = ", ".join(fields)
        insert_values = ", ".join(f"source.{field}" for field in fields)
        merge_sql = f"""
        MERGE `{target_table_id}` target
        USING `{temp_table_id}` source
        ON target.source_player_key = source.source_player_key
            AND target.season = source.season
            AND target.week = source.week
            AND target.scoring_profile_id = source.scoring_profile_id
        WHEN MATCHED THEN
            UPDATE SET
                {update_clause}
        WHEN NOT MATCHED THEN
            INSERT ({insert_fields})
            VALUES ({insert_values})
        """
        run_bigquery_query(
            client,
            merge_sql,
            component="fantasy_points",
            query_name="merge_fantasy_points_by_profile",
            allow_large_query=True,
        )
        logger.info("Merged %s rows into %s", len(rows), target_table_id)
    finally:
        client.delete_table(temp_table_id, not_found_ok=True)


def materialize_fantasy_points(
    client: bigquery.Client,
    *,
    dataset_id: str = DEFAULT_DATASET,
    season: int | None = None,
    week: int | None = None,
    scoring_profile_ids: list[str] | tuple[str, ...] | None = None,
    dry_run: bool = False,
    allow_large_query: bool = False,
) -> list[dict[str, Any]]:
    profile_ids = tuple(scoring_profile_ids or DEFAULT_PROFILE_IDS)
    profiles = load_scoring_profiles(client, dataset_id, profile_ids=profile_ids)
    missing_profiles = set(profile_ids) - set(profiles)
    if missing_profiles:
        raise RuntimeError(f"Missing scoring profiles: {', '.join(sorted(missing_profiles))}")

    stat_frame, source_table = fetch_stat_rows(
        client,
        dataset_id,
        season=season,
        week=week,
        allow_large_query=allow_large_query,
    )
    identity_frame = fetch_identity_rows(client, dataset_id)
    rows = build_fantasy_point_rows(
        stat_frame,
        profiles,
        identity_frame,
        source_table=source_table,
    )
    logger.info(
        "Built %s fantasy point rows from %s for profiles %s",
        len(rows),
        source_table,
        ",".join(sorted(profiles)),
    )
    if not dry_run:
        _merge_output_rows(client, dataset_id, rows)
    return rows


def materialize_historical_nflverse_fantasy_points(
    client: bigquery.Client,
    *,
    dataset_id: str = DEFAULT_DATASET,
    season_start: int,
    season_end: int,
    week_start: int | None = 1,
    week_end: int | None = 18,
    positions: tuple[str, ...] = SKILL_POSITIONS,
    scoring_profile_ids: list[str] | tuple[str, ...] | None = None,
    dry_run: bool = False,
    allow_large_query: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    profile_ids = tuple(scoring_profile_ids or DEFAULT_PROFILE_IDS)
    profiles = load_scoring_profiles(client, dataset_id, profile_ids=profile_ids)
    missing_profiles = set(profile_ids) - set(profiles)
    if missing_profiles:
        raise RuntimeError(f"Missing scoring profiles: {', '.join(sorted(missing_profiles))}")

    stat_frame = fetch_historical_nflverse_stat_rows(
        client,
        dataset_id,
        season_start=season_start,
        season_end=season_end,
        week_start=week_start,
        week_end=week_end,
        positions=positions,
        allow_large_query=allow_large_query,
    )
    source_validation = validate_complete_scoring_source(stat_frame, scoring_profile_ids=profile_ids)
    if not source_validation["complete"]:
        details = ", ".join(
            f"{field}={count}"
            for field, count in sorted(source_validation["missing_field_counts"].items())
        )
        raise RuntimeError(
            "Historical nflverse scoring source is incomplete; "
            f"missing required stat fields: {details}"
        )

    rows = build_fantasy_point_rows(
        stat_frame,
        profiles,
        identity_frame=pd.DataFrame(),
        source_table="raw_nflverse_weekly",
    )
    summary = {
        "source_table": "raw_nflverse_weekly",
        "season_start": season_start,
        "season_end": season_end,
        "week_start": week_start,
        "week_end": week_end,
        "positions": list(positions),
        "scoring_profile_ids": sorted(profiles),
        "source_row_count": int(len(stat_frame)),
        "built_row_count": int(len(rows)),
        "source_validation": source_validation,
    }
    logger.info(
        "Built %s historical nflverse fantasy point rows from %s source rows",
        len(rows),
        len(stat_frame),
    )
    if not dry_run:
        _merge_output_rows(client, dataset_id, rows)
    return rows, summary


def _parse_profile_ids(values: list[str] | None) -> list[str] | None:
    if not values:
        return None
    profile_ids = []
    for value in values:
        profile_ids.extend(item.strip() for item in value.split(",") if item.strip())
    return profile_ids or None


def _parse_positions(values: list[str] | None) -> tuple[str, ...]:
    if not values:
        return SKILL_POSITIONS
    positions = []
    for value in values:
        positions.extend(item.strip().upper() for item in value.split(",") if item.strip())
    invalid = sorted(set(positions) - set(SKILL_POSITIONS))
    if invalid:
        raise ValueError(f"Unsupported position filters: {', '.join(invalid)}")
    return tuple(dict.fromkeys(positions)) or SKILL_POSITIONS


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize profile-aware fantasy points.")
    parser.add_argument("--project", default=get_bigquery_project())
    parser.add_argument("--dataset", default=get_bigquery_dataset())
    parser.add_argument("--source", choices=("auto", "historical-nflverse"), default="auto")
    parser.add_argument("--season", type=int)
    parser.add_argument("--season-start", type=int)
    parser.add_argument("--season-end", type=int)
    parser.add_argument("--week", type=int)
    parser.add_argument("--week-start", type=int, default=1)
    parser.add_argument("--week-end", type=int, default=18)
    parser.add_argument("--position", action="append")
    parser.add_argument("--scoring-profile-id", action="append")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-large-query", action="store_true")
    parser.add_argument("--log-level", default=os.environ.get("LOG_LEVEL", "INFO"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    client = bigquery.Client(project=args.project)
    if args.source == "historical-nflverse":
        season_start = args.season_start if args.season_start is not None else args.season
        season_end = args.season_end if args.season_end is not None else args.season
        if season_start is None or season_end is None:
            raise SystemExit("--source historical-nflverse requires --season or --season-start/--season-end")
        rows, summary = materialize_historical_nflverse_fantasy_points(
            client,
            dataset_id=args.dataset,
            season_start=season_start,
            season_end=season_end,
            week_start=args.week_start,
            week_end=args.week_end,
            positions=_parse_positions(args.position),
            scoring_profile_ids=_parse_profile_ids(args.scoring_profile_id),
            dry_run=args.dry_run,
            allow_large_query=args.allow_large_query,
        )
        print(json.dumps({**summary, "dry_run": bool(args.dry_run), "wrote": not args.dry_run}, sort_keys=True))
        print(f"{OUTPUT_TABLE} rows built: {len(rows)}")
        return

    rows = materialize_fantasy_points(
        client,
        dataset_id=args.dataset,
        season=args.season,
        week=args.week,
        scoring_profile_ids=_parse_profile_ids(args.scoring_profile_id),
        dry_run=args.dry_run,
        allow_large_query=args.allow_large_query,
    )
    print(f"{OUTPUT_TABLE} rows built: {len(rows)}")


if __name__ == "__main__":
    main()
