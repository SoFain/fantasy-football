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


def _parse_profile_ids(values: list[str] | None) -> list[str] | None:
    if not values:
        return None
    profile_ids = []
    for value in values:
        profile_ids.extend(item.strip() for item in value.split(",") if item.strip())
    return profile_ids or None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize profile-aware fantasy points.")
    parser.add_argument("--project", default=get_bigquery_project())
    parser.add_argument("--dataset", default=get_bigquery_dataset())
    parser.add_argument("--season", type=int)
    parser.add_argument("--week", type=int)
    parser.add_argument("--scoring-profile-id", action="append")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-large-query", action="store_true")
    parser.add_argument("--log-level", default=os.environ.get("LOG_LEVEL", "INFO"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    client = bigquery.Client(project=args.project)
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
