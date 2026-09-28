"""Gated raw nflverse backfill executor.

The executor writes only to Phase 29 ``raw_nflverse_*`` tables. Dry-run mode
does not import or call nflreadpy.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import importlib.metadata
import json
import os
import socket
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

import pandas as pd

from src.nflverse_backfill_plan import (
    DEFAULT_DATASET,
    DEFAULT_FUTURE_HISTORICAL_GATE,
    DEFAULT_PROJECT,
    PRESETS,
    SOURCE_FAMILY_REGISTRY,
    PlanError,
    SourceFamily,
    build_plan,
)


CRITICAL_CORE_FAMILIES = {"schedules", "teams", "players", "weekly", "pbp"}
LEGACY_WRITE_TARGETS = {
    "play_by_play",
    "weekly_metrics",
    "player_rosters",
    "team_descriptions",
    "ngs_passing",
    "ngs_rushing",
    "ngs_receiving",
    "weekly_snap_counts",
    "injury_reports",
    "depth_charts",
}
STAGING_OR_FEATURE_TARGET_PREFIXES = ("stg_",)
BLOCKED_TARGETS = {
    "player_week_advanced_metrics",
    "team_week_context_metrics",
    "qb_week_environment_metrics",
    "pigskin_player_context_packet_current",
    "trade_player_scores",
    "trade_pick_scores",
}
NULLABLE_NATURAL_KEY_FIELDS: dict[str, set[str]] = {
    "injuries": {"report_status", "practice_status", "injury_notes"},
}
SOURCE_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "game_date": ("game_date", "gameday", "game_datetime"),
    "game_id": ("game_id", "old_game_id"),
    "team": ("team", "recent_team", "team_abbr"),
    "conference": ("conference", "team_conf"),
    "division": ("division", "team_division"),
    "player_id": (
        "player_id",
        "gsis_id",
        "nflverse_player_id",
        "gsis_it_id",
        "pfr_player_id",
        "pfr_id",
    ),
    "gsis_id": ("gsis_id", "player_id", "nflverse_player_id"),
    "nflverse_player_id": ("nflverse_player_id", "player_id", "gsis_id", "nfl_id"),
    "sleeper_player_id": ("sleeper_player_id", "sleeper_id"),
    "fantasy_player_id": ("fantasy_player_id", "fantasy_data_id", "fantasypros_id"),
    "platform": ("platform",),
    "platform_player_id": ("platform_player_id", "fantasy_player_id"),
    "player_name": ("player_name", "display_name", "full_name", "player_display_name", "player", "name"),
    "normalized_player_name": ("normalized_player_name", "merge_name", "display_name", "full_name", "player_name", "name"),
    "latest_team": ("latest_team", "team", "recent_team"),
    "opponent_team": ("opponent_team", "opponent"),
    "position": ("position", "position_group", "player_position"),
    "status": ("status", "status_description", "status_description_abbr"),
    "report_status": ("report_status", "game_status"),
    "game_status": ("game_status", "report_status"),
    "injury_notes": (
        "injury_notes",
        "report_primary_injury",
        "report_secondary_injury",
        "practice_primary_injury",
        "practice_secondary_injury",
    ),
    "depth_rank": ("depth_rank", "pos_rank"),
    "depth_role": ("depth_role", "pos_abb", "pos_name", "pos_grp"),
    "offense_snaps": ("offense_snaps", "offense", "offense_snap_count"),
    "offense_pct": ("offense_pct", "offense_pct_num", "offense_snap_pct"),
    "defense_snaps": ("defense_snaps", "defense", "defense_snap_count"),
    "st_snaps": ("st_snaps", "special_teams", "special_teams_snap_count"),
    "source_week": ("week",),
    "source_season": ("season",),
    "attempts": ("attempts", "rush_attempts"),
    "expected_yards": ("expected_yards", "expected_rush_yards"),
    "stacked_box_rate": ("stacked_box_rate", "percent_attempts_gte_eight_defenders"),
    "cpoe": ("cpoe", "completion_percentage_above_expectation"),
    "avg_air_yards": ("avg_air_yards", "avg_intended_air_yards"),
    "expected_yac": ("expected_yac", "avg_expected_yac"),
}
FF_PLAYERID_PLATFORM_COLUMNS: dict[str, str] = {
    "sleeper_id": "sleeper",
    "mfl_id": "mfl",
    "espn_id": "espn",
    "fleaflicker_id": "fleaflicker",
    "yahoo_id": "yahoo",
    "cbs_id": "cbs",
    "fantasy_data_id": "fantasy_data",
    "fantasypros_id": "fantasypros",
    "rotowire_id": "rotowire",
    "pff_id": "pff",
    "sportradar_id": "sportradar",
}
LIKELY_KEY_COLUMNS = (
    "season",
    "week",
    "game_id",
    "old_game_id",
    "player_id",
    "gsis_id",
    "nflverse_player_id",
    "pfr_player_id",
    "pfr_id",
    "sleeper_id",
    "mfl_id",
    "espn_id",
    "fleaflicker_id",
    "yahoo_id",
    "cbs_id",
    "fantasy_data_id",
    "platform",
    "platform_player_id",
    "team",
    "recent_team",
    "team_abbr",
    "position",
    "player_name",
    "display_name",
    "full_name",
    "player_display_name",
)
VOLATILE_HASH_FIELDS = {"loaded_at", "loaded_by", "source_refresh_id"}


class BackfillError(RuntimeError):
    """Raised when a backfill command is unsafe or failed."""


@dataclass(frozen=True)
class PreparedRows:
    dataframe: pd.DataFrame
    fetched_row_count: int
    prepared_row_count: int
    skipped_row_count: int
    warnings: list[str]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gated raw nflverse backfill executor.")
    parser.add_argument("--plan-only", action="store_true", help="Alias for dry-run planning. No loaders or writes.")
    parser.add_argument("--dry-run", action="store_true", help="Plan executor work. No loaders or writes.")
    parser.add_argument("--prepare-only", action="store_true", help="Fetch selected source families and prepare rows without writes.")
    parser.add_argument("--inspect-source-schema", action="store_true", help="Fetch selected source family schema summary without writes.")
    parser.add_argument("--write", action="store_true", help="Run gated live source fetch and raw-table merge.")
    parser.add_argument("--source-family", action="append", help="Source family to include. May be repeated or comma-separated.")
    parser.add_argument("--preset", choices=sorted(PRESETS), help="Source-family preset.")
    parser.add_argument("--season-start", type=int, help="First target season.")
    parser.add_argument("--season-end", type=int, help="Last target season.")
    parser.add_argument("--week-start", type=int, help="Reserved. Weekly refresh execution is blocked in Phase 29.6.")
    parser.add_argument("--week-end", type=int, help="Reserved. Weekly refresh execution is blocked in Phase 29.6.")
    parser.add_argument("--mode", choices=["historical_backfill", "weekly_refresh"], default="historical_backfill")
    parser.add_argument("--project", default=os.environ.get("BQ_PROJECT") or DEFAULT_PROJECT)
    parser.add_argument("--dataset", default=os.environ.get("BQ_DATASET") or DEFAULT_DATASET)
    parser.add_argument("--strict", action="store_true", help="Fail the command when any selected source family fails.")
    parser.add_argument(
        "--skip-source-family-on-error",
        action="store_true",
        help="Continue after optional source-family failure. Critical families still fail.",
    )
    return parser.parse_args(argv)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_json_value(value: Any) -> Any:
    if isinstance(value, (dict, list, tuple)):
        return value
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _safe_source_version() -> str:
    try:
        return importlib.metadata.version("nflreadpy")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def _selected_families(args: argparse.Namespace) -> list[str]:
    plan = build_plan(
        mode=args.mode,
        project=args.project,
        dataset=args.dataset,
        season_start=args.season_start,
        season_end=args.season_end,
        week_start=args.week_start,
        week_end=args.week_end,
        source_families=args.source_family,
        preset=args.preset,
        inspect_bigquery=False,
    )
    return list(plan["selected_source_families"])


def _validate_mode_request(args: argparse.Namespace) -> None:
    modes = [
        bool(args.write),
        bool(args.prepare_only),
        bool(args.inspect_source_schema),
        bool(args.dry_run or args.plan_only),
    ]
    if sum(1 for active in modes if active) > 1:
        raise BackfillError("Choose only one of --write, --prepare-only, --inspect-source-schema, or dry-run/plan-only.")
    if args.inspect_source_schema and (not args.source_family or args.preset):
        raise BackfillError("--inspect-source-schema requires explicit --source-family and does not accept presets.")
    if args.inspect_source_schema and args.mode != "historical_backfill":
        raise BackfillError("--inspect-source-schema only supports historical_backfill mode.")


def _validate_write_request(args: argparse.Namespace, selected: Iterable[str]) -> None:
    if not args.write:
        return
    if os.environ.get(DEFAULT_FUTURE_HISTORICAL_GATE) != "true":
        raise BackfillError(
            "ALLOW_NFLVERSE_HISTORICAL_BACKFILL must be true for live historical backfill writes"
        )
    if args.mode == "weekly_refresh":
        raise BackfillError("weekly_refresh execution is blocked in Phase 29.6.")
    if args.season_start is None or args.season_end is None:
        raise BackfillError("Explicit --season-start and --season-end are required for writes.")
    if not selected:
        raise BackfillError("At least one source family is required for writes.")
    for name in selected:
        family = SOURCE_FAMILY_REGISTRY[name]
        if not family.target_table.startswith("raw_nflverse_"):
            raise BackfillError(f"Unsafe target table for {name}: {family.target_table}")
        if family.target_table in LEGACY_WRITE_TARGETS:
            raise BackfillError(f"Legacy source table is not a valid target: {family.target_table}")
        if family.target_table in BLOCKED_TARGETS or family.target_table.startswith(STAGING_OR_FEATURE_TARGET_PREFIXES):
            raise BackfillError(f"Non-raw target is not allowed: {family.target_table}")


def _to_pandas(value: Any) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        return value
    if hasattr(value, "to_pandas"):
        return value.to_pandas()
    return pd.DataFrame(value)


def _call_loader(family: SourceFamily, seasons: list[int]) -> pd.DataFrame:
    import nflreadpy as nfl

    if family.source_family == "schedules":
        return _to_pandas(nfl.load_schedules(seasons))
    if family.source_family == "teams":
        return _to_pandas(nfl.load_teams())
    if family.source_family == "players":
        return _to_pandas(nfl.load_players())
    if family.source_family == "ff_playerids":
        return _to_pandas(nfl.load_ff_playerids())
    if family.source_family == "rosters":
        return _to_pandas(nfl.load_rosters(seasons))
    if family.source_family == "rosters_weekly":
        return _to_pandas(nfl.load_rosters_weekly(seasons))
    if family.source_family == "weekly":
        try:
            return _to_pandas(nfl.load_player_stats(seasons, summary_level="week"))
        except TypeError:
            return _to_pandas(nfl.load_player_stats(seasons))
    if family.source_family == "pbp":
        return _to_pandas(nfl.load_pbp(seasons))
    if family.source_family == "snap_counts":
        return _to_pandas(nfl.load_snap_counts(seasons))
    if family.source_family == "injuries":
        return _to_pandas(nfl.load_injuries(seasons))
    if family.source_family == "depth_charts":
        return _to_pandas(nfl.load_depth_charts(seasons))
    if family.source_family == "ngs_passing":
        return _to_pandas(nfl.load_nextgen_stats(seasons, stat_type="passing"))
    if family.source_family == "ngs_rushing":
        return _to_pandas(nfl.load_nextgen_stats(seasons, stat_type="rushing"))
    if family.source_family == "ngs_receiving":
        return _to_pandas(nfl.load_nextgen_stats(seasons, stat_type="receiving"))
    raise BackfillError(f"Live loader is not implemented for source family: {family.source_family}")


def _shape_value(value: Any) -> dict[str, Any]:
    if pd.isna(value):
        return {"present": False}
    text = str(value)
    return {
        "present": True,
        "type": type(value).__name__,
        "length": len(text),
        "numeric": text.isnumeric(),
    }


def source_schema_summary(df: pd.DataFrame, family: SourceFamily) -> dict[str, Any]:
    normalized = reshape_source_dataframe(df, family)
    original = _normalize_source_dataframe(df)
    likely_columns = [column for column in LIKELY_KEY_COLUMNS if column in normalized.columns]
    original_likely_columns = [column for column in LIKELY_KEY_COLUMNS if column in original.columns]
    key_columns = sorted(set(likely_columns) | set(original_likely_columns) | set(family.natural_key_fields))
    non_null_counts = {
        column: int(normalized[column].notna().sum())
        for column in key_columns
        if column in normalized.columns
    }
    examples = []
    if key_columns and not normalized.empty:
        example_columns = [column for column in key_columns if column in normalized.columns]
        for _, row in normalized[example_columns].head(5).iterrows():
            examples.append({column: _shape_value(row.get(column)) for column in example_columns})
    return {
        "source_family": family.source_family,
        "loader": family.loader,
        "fetched_row_count": int(len(original)),
        "normalized_row_count": int(len(normalized)),
        "columns": list(normalized.columns),
        "original_columns": list(original.columns),
        "dtypes": {column: str(dtype) for column, dtype in normalized.dtypes.items()},
        "likely_key_columns": key_columns,
        "non_null_counts": non_null_counts,
        "key_shape_examples": examples,
        "reshaped": family.source_family == "ff_playerids" and len(normalized) != len(original),
        "wrote": False,
    }


def _source_value(row: pd.Series, target_column: str) -> Any:
    candidate_columns = []
    if target_column in row.index:
        candidate_columns.append(target_column)
    candidate_columns.extend(alias for alias in SOURCE_COLUMN_ALIASES.get(target_column, ()) if alias in row.index)
    for column in candidate_columns:
        value = row[column]
        if not pd.isna(value):
            return value
    return None


def _normalize_source_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(column).strip() for column in out.columns]
    return out


def _reshape_ff_playerids(df: pd.DataFrame) -> pd.DataFrame:
    if "platform" in df.columns and "platform_player_id" in df.columns:
        return df

    platform_columns = [column for column in FF_PLAYERID_PLATFORM_COLUMNS if column in df.columns]
    if not platform_columns:
        return df

    base_columns = [
        column
        for column in df.columns
        if column not in platform_columns
    ]
    rows: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        for column in platform_columns:
            value = row.get(column)
            if pd.isna(value) or str(value).strip() == "":
                continue
            out = {base_column: row.get(base_column) for base_column in base_columns}
            out["platform"] = FF_PLAYERID_PLATFORM_COLUMNS[column]
            out["platform_player_id"] = value
            if out.get("sleeper_player_id") is None and column == "sleeper_id":
                out["sleeper_player_id"] = value
            if out.get("fantasy_player_id") is None and column in {"fantasy_data_id", "fantasypros_id"}:
                out["fantasy_player_id"] = value
            rows.append(out)
    return pd.DataFrame(rows)


def reshape_source_dataframe(df: pd.DataFrame, family: SourceFamily) -> pd.DataFrame:
    out = _normalize_source_dataframe(df)
    if family.source_family == "ff_playerids":
        return _reshape_ff_playerids(out)
    return out


def _raw_payload(row: pd.Series, source_columns: list[str]) -> str:
    return _json_dumps({column: _normalize_json_value(row.get(column)) for column in source_columns})


def _row_hash(row: pd.Series, family: SourceFamily, retained_columns: list[str]) -> str:
    payload = {
        "source_family": family.source_family,
        "target_table": family.target_table,
        "natural_key": {field: _normalize_json_value(row.get(field)) for field in family.natural_key_fields},
        "retained": {
            field: _normalize_json_value(row.get(field))
            for field in retained_columns
            if field not in VOLATILE_HASH_FIELDS and field != "row_hash"
        },
    }
    return hashlib.sha256(_json_dumps(payload).encode("utf-8")).hexdigest()


def _schema_field_type(field: Any) -> str:
    return str(getattr(field, "field_type", "") or getattr(field, "type", "")).upper()


def _coerce_to_schema(df: pd.DataFrame, schema: list[Any]) -> pd.DataFrame:
    out = df.copy()
    for field in schema:
        name = field.name
        if name not in out.columns:
            continue
        field_type = _schema_field_type(field)
        if field_type in {"INTEGER", "INT64"}:
            out[name] = pd.to_numeric(out[name], errors="coerce").astype("Int64")
        elif field_type in {"FLOAT", "FLOAT64", "NUMERIC", "BIGNUMERIC"}:
            out[name] = pd.to_numeric(out[name], errors="coerce")
        elif field_type in {"BOOLEAN", "BOOL"}:
            out[name] = out[name].astype("boolean")
        elif field_type == "TIMESTAMP":
            out[name] = pd.to_datetime(out[name], errors="coerce", utc=True)
        elif field_type == "STRING":
            out[name] = out[name].where(out[name].notna(), None).map(lambda value: None if value is None else str(value))
    return out


def prepare_rows(
    source_df: pd.DataFrame,
    family: SourceFamily,
    schema: list[Any],
    *,
    source_refresh_id: str,
    source_version: str,
    loaded_at: datetime,
    loaded_by: str,
    season_start: int,
    season_end: int,
) -> PreparedRows:
    fetched_row_count = int(len(source_df))
    source_df = reshape_source_dataframe(source_df, family)
    target_columns = [field.name for field in schema]
    source_columns = list(source_df.columns)
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []

    for _, source_row in source_df.iterrows():
        out: dict[str, Any] = {}
        for column in target_columns:
            out[column] = _source_value(source_row, column)
        out["source_system"] = "nflverse"
        out["source_loader"] = family.loader
        out["source_version"] = source_version
        if "source_season" in target_columns and out.get("source_season") is None and family.source_type != "static_snapshot":
            out["source_season"] = out.get("season")
        if "source_week" in target_columns and out.get("source_week") is None:
            out["source_week"] = out.get("week")
        out["source_refresh_id"] = source_refresh_id
        out["loaded_at"] = loaded_at
        out["loaded_by"] = loaded_by
        if "raw_payload_json" in target_columns:
            out["raw_payload_json"] = _raw_payload(source_row, source_columns)
        rows.append(out)

    prepared = pd.DataFrame(rows, columns=target_columns)
    skipped = 0
    if not prepared.empty:
        missing_key_mask = pd.Series(False, index=prepared.index)
        missing_key_counts: dict[str, int] = {}
        for key in family.natural_key_fields:
            if key not in prepared.columns:
                warnings.append(f"Natural key field is not in target schema and cannot be checked: {key}")
                continue
            if key in NULLABLE_NATURAL_KEY_FIELDS.get(family.source_family, set()):
                continue
            key_missing = prepared[key].isna()
            missing_key_counts[key] = int(key_missing.sum())
            missing_key_mask = missing_key_mask | key_missing
        skipped = int(missing_key_mask.sum())
        if skipped:
            prepared = prepared.loc[~missing_key_mask].copy()
            key_counts = ", ".join(
                f"{key}={count}" for key, count in missing_key_counts.items() if count
            )
            warnings.append(f"Skipped {skipped} rows with missing natural key values: {key_counts}.")
            if family.source_family == "weekly" and missing_key_counts.get("player_id"):
                warnings.append(
                    "Weekly skipped rows are missing player_id and should be treated as non-player or aggregate rows unless a safe source key is proven."
                )

        if family.source_type != "static_snapshot" and "season" in prepared.columns:
            before = len(prepared)
            prepared = prepared[
                (pd.to_numeric(prepared["season"], errors="coerce") >= season_start)
                & (pd.to_numeric(prepared["season"], errors="coerce") <= season_end)
            ].copy()
            removed = before - len(prepared)
            if removed:
                skipped += int(removed)
                warnings.append(f"Skipped {removed} rows outside requested season bounds.")

        key_subset = [key for key in family.natural_key_fields if key in prepared.columns]
        if key_subset:
            duplicate_mask = prepared.duplicated(subset=key_subset, keep="last")
            duplicate_count = int(duplicate_mask.sum())
            if duplicate_count:
                prepared = prepared.loc[~duplicate_mask].copy()
                skipped += duplicate_count
                warnings.append(f"Deduped {duplicate_count} source rows on natural key before merge.")

    retained_for_hash = [column for column in target_columns if column not in {"row_hash"}]
    if not prepared.empty:
        prepared["row_hash"] = [
            _row_hash(row, family, retained_for_hash) for _, row in prepared.iterrows()
        ]
    prepared = _coerce_to_schema(prepared, schema)
    return PreparedRows(
        dataframe=prepared,
        fetched_row_count=fetched_row_count,
        prepared_row_count=int(len(prepared)),
        skipped_row_count=skipped,
        warnings=warnings,
    )


def build_null_safe_merge_condition(key_fields: Iterable[str], target_alias: str = "target", source_alias: str = "source") -> str:
    conditions = []
    for key in key_fields:
        conditions.append(
            f"({target_alias}.`{key}` = {source_alias}.`{key}` OR "
            f"({target_alias}.`{key}` IS NULL AND {source_alias}.`{key}` IS NULL))"
        )
    return " AND ".join(conditions)


def build_merge_sql(
    *,
    project: str,
    dataset: str,
    target_table: str,
    temp_table: str,
    columns: list[str],
    key_fields: Iterable[str],
) -> str:
    condition = build_null_safe_merge_condition(key_fields)
    update_columns = [column for column in columns if column not in set(key_fields)]
    update_clause = ",\n        ".join(f"`{column}` = source.`{column}`" for column in update_columns)
    insert_columns = ", ".join(f"`{column}`" for column in columns)
    insert_values = ", ".join(f"source.`{column}`" for column in columns)
    return f"""
MERGE `{project}.{dataset}.{target_table}` target
USING `{project}.{dataset}.{temp_table}` source
ON {condition}
WHEN MATCHED AND target.`row_hash` != source.`row_hash` THEN
  UPDATE SET
        {update_clause}
WHEN NOT MATCHED THEN
  INSERT ({insert_columns})
  VALUES ({insert_values})
"""


def _count_rows(client: Any, project: str, dataset: str, table_name: str, where: str | None = None) -> int:
    sql = f"SELECT COUNT(1) AS row_count FROM `{project}.{dataset}.{table_name}`"
    if where:
        sql += f" WHERE {where}"
    rows = list(client.query(sql).result())
    return int(rows[0].row_count)


def _duplicate_key_count(client: Any, project: str, dataset: str, table_name: str, key_fields: Iterable[str]) -> int:
    key_expr = ", ".join(f"`{key}`" for key in key_fields)
    sql = f"""
    SELECT COUNT(1) AS duplicate_key_groups
    FROM (
      SELECT {key_expr}, COUNT(1) AS row_count
      FROM `{project}.{dataset}.{table_name}`
      GROUP BY {key_expr}
      HAVING COUNT(1) > 1
    )
    """
    rows = list(client.query(sql).result())
    return int(rows[0].duplicate_key_groups)


def _load_temp_and_merge(
    client: Any,
    *,
    project: str,
    dataset: str,
    family: SourceFamily,
    prepared: pd.DataFrame,
    schema: list[Any],
    source_refresh_id: str,
) -> tuple[int, int, int]:
    from google.cloud import bigquery

    if prepared.empty:
        return 0, _count_rows(client, project, dataset, family.target_table), 0

    temp_table = f"__tmp_{family.target_table}_{source_refresh_id.replace('-', '_')}"
    columns = [field.name for field in schema]
    table_id = f"{project}.{dataset}.{temp_table}"
    target_id = f"{project}.{dataset}.{family.target_table}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        schema=schema,
        autodetect=False,
    )
    client.load_table_from_dataframe(prepared[columns], table_id, job_config=job_config).result()
    try:
        merge_sql = build_merge_sql(
            project=project,
            dataset=dataset,
            target_table=family.target_table,
            temp_table=temp_table,
            columns=columns,
            key_fields=family.natural_key_fields,
        )
        merge_job = client.query(merge_sql)
        merge_job.result()
        affected = int(getattr(merge_job, "num_dml_affected_rows", 0) or 0)
    finally:
        client.delete_table(table_id, not_found_ok=True)

    target_count_after = _count_rows(client, project, dataset, family.target_table)
    duplicate_count = _duplicate_key_count(client, project, dataset, family.target_table, family.natural_key_fields)
    client.get_table(target_id)
    return affected, target_count_after, duplicate_count


def _build_source_refresh_id(preset: str | None, season_start: int, season_end: int) -> str:
    stamp = _utc_now().strftime("%Y%m%dT%H%M%SZ")
    label = preset or "source_family"
    return f"nflverse_{label}_{season_start}_{season_end}_{stamp}"


def dry_run_summary(args: argparse.Namespace, selected: list[str]) -> dict[str, Any]:
    plan = build_plan(
        mode=args.mode,
        project=args.project,
        dataset=args.dataset,
        season_start=args.season_start,
        season_end=args.season_end,
        week_start=args.week_start,
        week_end=args.week_end,
        source_families=args.source_family,
        preset=args.preset,
        inspect_bigquery=False,
    )
    return {
        "wrote": False,
        "dry_run": True,
        "source_families_attempted": selected,
        "source_family_plans": plan["source_family_plans"],
        "warnings": plan["global_warnings"],
        "next_required_phase": "Authorized 2014 core smoke write with ALLOW_NFLVERSE_HISTORICAL_BACKFILL=true.",
    }


def inspect_source_schema(args: argparse.Namespace, selected: list[str]) -> dict[str, Any]:
    seasons = list(range(int(args.season_start), int(args.season_end) + 1))
    summaries = []
    for name in selected:
        family = SOURCE_FAMILY_REGISTRY[name]
        source_df = _call_loader(family, seasons)
        summaries.append(source_schema_summary(source_df, family))
    return {
        "wrote": False,
        "dry_run": False,
        "inspect_source_schema": True,
        "season_start": args.season_start,
        "season_end": args.season_end,
        "source_families_attempted": selected,
        "schema_summaries": summaries,
    }


def prepare_only_summary(args: argparse.Namespace, selected: list[str]) -> dict[str, Any]:
    from google.cloud import bigquery

    client = bigquery.Client(project=args.project)
    source_refresh_id = _build_source_refresh_id(args.preset, int(args.season_start), int(args.season_end))
    source_version = _safe_source_version()
    loaded_at = _utc_now()
    loaded_by = f"{getpass.getuser()}@{socket.gethostname()}"
    seasons = list(range(int(args.season_start), int(args.season_end) + 1))
    summaries = []
    for name in selected:
        family = SOURCE_FAMILY_REGISTRY[name]
        table = client.get_table(f"{args.project}.{args.dataset}.{family.target_table}")
        source_df = _call_loader(family, seasons)
        prepared = prepare_rows(
            source_df,
            family,
            table.schema,
            source_refresh_id=source_refresh_id,
            source_version=source_version,
            loaded_at=loaded_at,
            loaded_by=loaded_by,
            season_start=int(args.season_start),
            season_end=int(args.season_end),
        )
        summaries.append(
            {
                "source_family": name,
                "loader": family.loader,
                "target_table": family.target_table,
                "fetched_row_count": prepared.fetched_row_count,
                "prepared_row_count": prepared.prepared_row_count,
                "skipped_row_count": prepared.skipped_row_count,
                "target_columns": list(prepared.dataframe.columns),
                "warnings": prepared.warnings,
            }
        )
    return {
        "wrote": False,
        "dry_run": False,
        "prepare_only": True,
        "source_refresh_id": source_refresh_id,
        "source_families_attempted": selected,
        "family_summaries": summaries,
    }


def execute_write(args: argparse.Namespace, selected: list[str]) -> dict[str, Any]:
    from google.cloud import bigquery

    start_time = time.time()
    client = bigquery.Client(project=args.project)
    source_refresh_id = _build_source_refresh_id(args.preset, int(args.season_start), int(args.season_end))
    source_version = _safe_source_version()
    loaded_at = _utc_now()
    loaded_by = f"{getpass.getuser()}@{socket.gethostname()}"
    seasons = list(range(int(args.season_start), int(args.season_end) + 1))

    attempted: list[str] = []
    succeeded: list[str] = []
    skipped: list[str] = []
    failed: list[str] = []
    critical_failures: list[str] = []
    family_summaries: list[dict[str, Any]] = []

    for name in selected:
        family = SOURCE_FAMILY_REGISTRY[name]
        attempted.append(name)
        summary = {
            "source_family": name,
            "loader": family.loader,
            "target_table": family.target_table,
            "season_start": args.season_start,
            "season_end": args.season_end,
            "source_refresh_id": source_refresh_id,
            "fetched_row_count": 0,
            "prepared_row_count": 0,
            "written_or_merged_row_count": 0,
            "skipped_row_count": 0,
            "target_row_count_after": None,
            "duplicate_key_count_after": None,
            "warnings": [],
            "errors": [],
        }
        try:
            table = client.get_table(f"{args.project}.{args.dataset}.{family.target_table}")
            source_df = _call_loader(family, seasons)
            prepared = prepare_rows(
                source_df,
                family,
                table.schema,
                source_refresh_id=source_refresh_id,
                source_version=source_version,
                loaded_at=loaded_at,
                loaded_by=loaded_by,
                season_start=int(args.season_start),
                season_end=int(args.season_end),
            )
            summary["fetched_row_count"] = prepared.fetched_row_count
            summary["prepared_row_count"] = prepared.prepared_row_count
            summary["skipped_row_count"] = prepared.skipped_row_count
            summary["warnings"].extend(prepared.warnings)
            affected, target_count_after, duplicate_count = _load_temp_and_merge(
                client,
                project=args.project,
                dataset=args.dataset,
                family=family,
                prepared=prepared.dataframe,
                schema=table.schema,
                source_refresh_id=source_refresh_id,
            )
            summary["written_or_merged_row_count"] = affected
            summary["target_row_count_after"] = target_count_after
            summary["duplicate_key_count_after"] = duplicate_count
            succeeded.append(name)
        except Exception as exc:
            summary["errors"].append(str(exc))
            failed.append(name)
            if name in CRITICAL_CORE_FAMILIES:
                critical_failures.append(name)
            if name in CRITICAL_CORE_FAMILIES:
                family_summaries.append(summary)
                break
            skipped.append(name)
        family_summaries.append(summary)

    elapsed = round(time.time() - start_time, 3)
    return {
        "wrote": True,
        "dry_run": False,
        "source_refresh_id": source_refresh_id,
        "source_families_attempted": attempted,
        "source_families_succeeded": succeeded,
        "source_families_skipped": skipped,
        "source_families_failed": failed,
        "critical_failures": critical_failures,
        "gate_used": DEFAULT_FUTURE_HISTORICAL_GATE,
        "gate_removed": False,
        "elapsed_seconds": elapsed,
        "family_summaries": family_summaries,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.plan_only:
        args.dry_run = True
    try:
        _validate_mode_request(args)
        selected = _selected_families(args)
        _validate_write_request(args, selected)
        if args.inspect_source_schema:
            summary = inspect_source_schema(args, selected)
            code = 0
        elif args.prepare_only:
            summary = prepare_only_summary(args, selected)
            code = 0
        elif args.write:
            summary = execute_write(args, selected)
            code = 1 if summary["critical_failures"] else 0
        else:
            summary = dry_run_summary(args, selected)
            code = 0
    except (BackfillError, PlanError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
