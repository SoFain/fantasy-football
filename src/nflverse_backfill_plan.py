"""Dry-run-only nflverse historical backfill planner.

This module deliberately does not import or call nflreadpy. It describes the
source families, target raw tables, and follow-on validation work needed before
a future authorized backfill.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


DEFAULT_PROJECT = "fantasy-football-498121"
DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_HISTORICAL_START = 2014
DEFAULT_FUTURE_HISTORICAL_GATE = "ALLOW_NFLVERSE_HISTORICAL_BACKFILL"
DEFAULT_FUTURE_WEEKLY_GATE = "ALLOW_NFLVERSE_WEEKLY_REFRESH"
METADATA_FIELDS = [
    "source_system",
    "source_loader",
    "source_version",
    "source_season",
    "source_week",
    "source_refresh_id",
    "loaded_at",
    "loaded_by",
    "row_hash",
    "raw_payload_json",
]


@dataclass(frozen=True)
class SourceFamily:
    source_family: str
    loader: str
    target_table: str
    source_type: str
    default_historical_start_season: int
    default_historical_end_policy: str
    minimum_recommended_first_backfill_season: int
    known_limited_range: str | None
    supports_week_filter: bool
    natural_key_fields: tuple[str, ...]
    partition_field: str | None
    clustering_fields: tuple[str, ...]
    required_metadata_fields: tuple[str, ...]
    downstream_staging_tables: tuple[str, ...]
    validation_patterns: tuple[str, ...]
    future_authorization_gate: str
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class TableInspection:
    table_exists: bool | None
    current_row_count: int | None
    existing_coverage: dict[str, Any] | None
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _sf(
    source_family: str,
    loader: str,
    target_table: str,
    source_type: str,
    natural_key_fields: Iterable[str],
    clustering_fields: Iterable[str],
    downstream_staging_tables: Iterable[str],
    validation_patterns: Iterable[str],
    *,
    partition_field: str | None = "season",
    supports_week_filter: bool = False,
    default_historical_start_season: int = DEFAULT_HISTORICAL_START,
    minimum_recommended_first_backfill_season: int = DEFAULT_HISTORICAL_START,
    known_limited_range: str | None = None,
    warnings: Iterable[str] = (),
) -> SourceFamily:
    return SourceFamily(
        source_family=source_family,
        loader=loader,
        target_table=target_table,
        source_type=source_type,
        default_historical_start_season=default_historical_start_season,
        default_historical_end_policy="explicit --season-end required",
        minimum_recommended_first_backfill_season=minimum_recommended_first_backfill_season,
        known_limited_range=known_limited_range,
        supports_week_filter=supports_week_filter,
        natural_key_fields=tuple(natural_key_fields),
        partition_field=partition_field,
        clustering_fields=tuple(clustering_fields),
        required_metadata_fields=tuple(METADATA_FIELDS),
        downstream_staging_tables=tuple(downstream_staging_tables),
        validation_patterns=tuple(validation_patterns),
        future_authorization_gate=DEFAULT_FUTURE_HISTORICAL_GATE,
        warnings=tuple(warnings),
    )


SOURCE_FAMILY_REGISTRY: dict[str, SourceFamily] = {
    "pbp": _sf(
        "pbp",
        "nflreadpy.load_pbp",
        "raw_nflverse_pbp",
        "season_range",
        ["season", "week", "game_id", "play_id"],
        ["week", "game_id", "posteam", "defteam"],
        ["stg_play_player_events", "stg_team_week_stats", "qb_week_environment_metrics"],
        ["raw_nflverse", "stg_", "advanced_metrics"],
        warnings=["Loader is season-level. Week planning is post-load merge planning, not week-bounded extraction."],
    ),
    "weekly": _sf(
        "weekly",
        "nflreadpy.load_player_stats",
        "raw_nflverse_weekly",
        "season_range",
        ["season", "week", "player_id", "team"],
        ["week", "player_id", "team", "position"],
        ["stg_player_week_stats", "player_week_advanced_metrics"],
        ["raw_nflverse", "stg_", "advanced_metrics"],
        warnings=["Loader is season-level. Week planning is post-load merge planning, not week-bounded extraction."],
    ),
    "rosters": _sf(
        "rosters",
        "nflreadpy.load_rosters",
        "raw_nflverse_rosters",
        "season_range",
        ["season", "player_id", "team"],
        ["player_id", "gsis_id", "team", "position"],
        ["stg_player_identity"],
        ["raw_nflverse", "stg_"],
    ),
    "rosters_weekly": _sf(
        "rosters_weekly",
        "nflreadpy.load_rosters_weekly",
        "raw_nflverse_rosters_weekly",
        "season_range",
        ["season", "week", "player_id", "team"],
        ["week", "player_id", "team", "position"],
        ["stg_player_identity"],
        ["raw_nflverse", "stg_"],
        warnings=["Loader is season-level with week rows. Week planning should filter after extraction in a future merge step."],
    ),
    "players": _sf(
        "players",
        "nflreadpy.load_players",
        "raw_nflverse_players",
        "static_snapshot",
        ["nflverse_player_id"],
        ["nflverse_player_id", "gsis_id", "sleeper_player_id", "normalized_player_name"],
        ["stg_player_identity"],
        ["raw_nflverse", "stg_"],
        partition_field=None,
    ),
    "ff_playerids": _sf(
        "ff_playerids",
        "nflreadpy.load_ff_playerids",
        "raw_nflverse_ff_playerids",
        "static_snapshot",
        ["nflverse_player_id", "platform", "platform_player_id"],
        ["nflverse_player_id", "gsis_id", "sleeper_player_id", "platform_player_id"],
        ["stg_player_identity"],
        ["raw_nflverse", "stg_"],
        partition_field=None,
    ),
    "schedules": _sf(
        "schedules",
        "nflreadpy.load_schedules",
        "raw_nflverse_schedules",
        "season_range",
        ["season", "week", "game_id"],
        ["week", "game_id", "home_team", "away_team"],
        ["stg_game_context", "team_week_context_metrics", "qb_week_environment_metrics"],
        ["raw_nflverse", "stg_", "advanced_metrics"],
        warnings=["Schedule rows include week, but loader is season-level."],
    ),
    "teams": _sf(
        "teams",
        "nflreadpy.load_teams",
        "raw_nflverse_teams",
        "static_snapshot",
        ["team"],
        ["team"],
        ["stg_game_context", "stg_team_week_stats"],
        ["raw_nflverse", "stg_"],
        partition_field=None,
    ),
    "team_stats": _sf(
        "team_stats",
        "nflreadpy.load_team_stats",
        "raw_nflverse_team_stats",
        "season_range",
        ["season", "week", "team"],
        ["week", "team"],
        ["stg_team_week_stats", "team_week_context_metrics"],
        ["raw_nflverse", "stg_", "advanced_metrics"],
        warnings=["Loader is season-level. Use as an enrichment source after core PBP and schedules are loaded."],
    ),
    "injuries": _sf(
        "injuries",
        "nflreadpy.load_injuries",
        "raw_nflverse_injuries",
        "season_range",
        ["season", "week", "team", "gsis_id", "report_status", "practice_status", "injury_notes"],
        ["week", "team", "gsis_id"],
        ["stg_player_identity", "pigskin_player_context_packet_current"],
        ["raw_nflverse", "stg_", "compat_pigskin"],
        warnings=["Loader is season-level. Injury context must remain missing-flagged when unavailable."],
    ),
    "depth_charts": _sf(
        "depth_charts",
        "nflreadpy.load_depth_charts",
        "raw_nflverse_depth_charts",
        "season_range",
        ["season", "week", "team", "gsis_id", "position", "depth_rank"],
        ["team", "gsis_id", "position"],
        ["stg_participation_context", "player_role_usage_metrics_current"],
        ["raw_nflverse", "stg_", "advanced_metrics"],
        warnings=["Depth chart rows may be season-loaded and should be week-filtered only after schema inspection."],
    ),
    "snap_counts": _sf(
        "snap_counts",
        "nflreadpy.load_snap_counts",
        "raw_nflverse_snap_counts",
        "season_range",
        ["season", "week", "game_id", "player_id", "team"],
        ["week", "player_id", "team", "position"],
        ["stg_participation_context", "player_role_usage_metrics_current"],
        ["raw_nflverse", "stg_", "advanced_metrics"],
        warnings=["Snap share is valid from snap counts. Route share still needs a true route source."],
    ),
    "participation": _sf(
        "participation",
        "nflreadpy.load_participation",
        "raw_nflverse_participation",
        "season_range",
        ["season", "week", "game_id", "player_id", "team"],
        ["week", "game_id", "player_id", "team"],
        ["stg_participation_context", "player_role_usage_metrics_current"],
        ["raw_nflverse", "stg_", "advanced_metrics"],
        warnings=["Do not create route share without verified true route source columns."],
    ),
    "ngs_passing": _sf(
        "ngs_passing",
        "nflreadpy.load_nextgen_stats:passing",
        "raw_nflverse_ngs_passing",
        "season_limited",
        ["season", "week", "player_gsis_id", "team"],
        ["week", "player_gsis_id", "team"],
        ["qb_week_environment_metrics", "player_week_advanced_metrics"],
        ["raw_nflverse", "advanced_metrics"],
        minimum_recommended_first_backfill_season=2016,
        known_limited_range="2016+",
        warnings=["NGS is expected to be 2016+ only. Earlier target seasons should be skipped with missing-data flags."],
    ),
    "ngs_rushing": _sf(
        "ngs_rushing",
        "nflreadpy.load_nextgen_stats:rushing",
        "raw_nflverse_ngs_rushing",
        "season_limited",
        ["season", "week", "player_gsis_id", "team"],
        ["week", "player_gsis_id", "team"],
        ["player_week_advanced_metrics"],
        ["raw_nflverse", "advanced_metrics"],
        minimum_recommended_first_backfill_season=2016,
        known_limited_range="2016+",
        warnings=["NGS is expected to be 2016+ only. Earlier target seasons should be skipped with missing-data flags."],
    ),
    "ngs_receiving": _sf(
        "ngs_receiving",
        "nflreadpy.load_nextgen_stats:receiving",
        "raw_nflverse_ngs_receiving",
        "season_limited",
        ["season", "week", "player_gsis_id", "team"],
        ["week", "player_gsis_id", "team"],
        ["player_week_advanced_metrics"],
        ["raw_nflverse", "advanced_metrics"],
        minimum_recommended_first_backfill_season=2016,
        known_limited_range="2016+",
        warnings=["NGS is expected to be 2016+ only. Earlier target seasons should be skipped with missing-data flags."],
    ),
    "ftn_charting": _sf(
        "ftn_charting",
        "nflreadpy.load_ftn_charting",
        "raw_nflverse_ftn_charting",
        "season_limited",
        ["season", "week", "game_id", "play_id", "player_id"],
        ["week", "game_id", "play_id"],
        ["stg_play_player_events", "player_week_advanced_metrics"],
        ["raw_nflverse", "advanced_metrics"],
        minimum_recommended_first_backfill_season=2022,
        known_limited_range="2022+",
        warnings=["FTN is expected to be 2022+ only. Pressure-like fields stay source-labeled until true pressure source is proven."],
    ),
    "draft_picks": _sf(
        "draft_picks",
        "nflreadpy.load_draft_picks",
        "raw_nflverse_draft_picks",
        "season_range",
        ["season", "team", "player_id", "draft_round", "draft_pick"],
        ["player_id", "team", "position"],
        ["stg_player_identity"],
        ["raw_nflverse", "stg_"],
    ),
}


PRESETS: dict[str, tuple[str, ...]] = {
    "core_historical": (
        "schedules",
        "teams",
        "players",
        "ff_playerids",
        "rosters",
        "rosters_weekly",
        "weekly",
        "pbp",
        "snap_counts",
    ),
    "role_context": ("injuries", "depth_charts", "participation", "snap_counts"),
    "tier2_enrichment": (
        "ngs_passing",
        "ngs_rushing",
        "ngs_receiving",
        "ftn_charting",
        "team_stats",
        "draft_picks",
    ),
    "all": tuple(SOURCE_FAMILY_REGISTRY),
}


class PlanError(ValueError):
    """Raised when planner input is unsafe or incomplete."""


class BigQueryPlanInspector:
    """Read-only, best-effort BigQuery table inspector."""

    def __init__(self, project: str, dataset: str):
        from google.cloud import bigquery

        self._bigquery = bigquery
        self.client = bigquery.Client(project=project)
        self.project = project
        self.dataset = dataset

    def inspect(self, family: SourceFamily, season_start: int, season_end: int) -> TableInspection:
        table_id = f"{self.project}.{self.dataset}.{family.target_table}"
        try:
            table = self.client.get_table(table_id)
        except Exception as exc:  # pragma: no cover - depends on live credentials.
            return TableInspection(
                table_exists=False,
                current_row_count=None,
                existing_coverage=None,
                warnings=(f"BigQuery table inspection failed for {family.target_table}: {exc}",),
            )

        row_count = getattr(table, "num_rows", None)
        columns = {field.name for field in table.schema}
        coverage: dict[str, Any] | None = None
        warnings: list[str] = []

        if "season" in columns:
            if "week" in columns:
                week_select = "MIN(week) AS min_week, MAX(week) AS max_week, COUNT(DISTINCT week) AS distinct_weeks"
            else:
                week_select = "NULL AS min_week, NULL AS max_week, NULL AS distinct_weeks"
            sql = f"""
            SELECT
              season,
              COUNT(1) AS row_count,
              {week_select}
            FROM `{table_id}`
            WHERE season BETWEEN @season_start AND @season_end
            GROUP BY season
            ORDER BY season
            LIMIT 25
            """
            job_config = self._bigquery.QueryJobConfig(
                query_parameters=[
                    self._bigquery.ScalarQueryParameter("season_start", "INT64", season_start),
                    self._bigquery.ScalarQueryParameter("season_end", "INT64", season_end),
                ]
            )
            try:
                rows = [dict(row) for row in self.client.query(sql, job_config=job_config).result()]
                coverage = {
                    "season_field": "season",
                    "covered_seasons": rows,
                    "coverage_row_limit": 25,
                }
            except Exception as exc:  # pragma: no cover - depends on live credentials.
                warnings.append(f"Coverage query failed for {family.target_table}: {exc}")
        else:
            coverage = {
                "season_field": None,
                "covered_seasons": [],
                "note": "Static snapshot or no season column. Row count only.",
            }

        return TableInspection(
            table_exists=True,
            current_row_count=row_count,
            existing_coverage=coverage,
            warnings=tuple(warnings),
        )


def _normalize_source_families(values: Iterable[str] | None) -> list[str]:
    families: list[str] = []
    for value in values or []:
        for item in value.split(","):
            normalized = item.strip()
            if normalized:
                families.append(normalized)
    return families


def select_source_families(
    *,
    source_families: Iterable[str] | None = None,
    preset: str | None = None,
    all_source_families: bool = False,
) -> list[str]:
    selected: list[str] = []
    if all_source_families:
        selected.extend(PRESETS["all"])
    if preset:
        if preset not in PRESETS:
            raise PlanError(f"Unknown preset: {preset}")
        selected.extend(PRESETS[preset])
    selected.extend(_normalize_source_families(source_families))
    if not selected:
        selected.extend(PRESETS["core_historical"])

    deduped: list[str] = []
    for family in selected:
        if family not in SOURCE_FAMILY_REGISTRY:
            raise PlanError(f"Unknown source family: {family}")
        if family not in deduped:
            deduped.append(family)
    return deduped


def _validate_bounds(
    *,
    mode: str,
    season_start: int | None,
    season_end: int | None,
    week_start: int | None,
    week_end: int | None,
) -> tuple[int, int]:
    if season_start is None or season_end is None:
        raise PlanError("Explicit --season-start and --season-end are required.")
    if season_start > season_end:
        raise PlanError("--season-start must be <= --season-end.")
    if season_start < 1999:
        raise PlanError("Season range must start at 1999 or later.")
    if season_end > 2050:
        raise PlanError("Season range must end at 2050 or earlier.")

    if mode == "weekly_refresh":
        if week_start is None or week_end is None:
            raise PlanError("weekly_refresh mode requires explicit --week-start and --week-end.")
        if season_start != season_end:
            raise PlanError("weekly_refresh mode requires one explicit season.")
        if week_start > week_end:
            raise PlanError("--week-start must be <= --week-end.")
        if week_start < 1 or week_end > 23:
            raise PlanError("Week range must be between 1 and 23.")
    return season_start, season_end


def _target_seasons(family: SourceFamily, season_start: int, season_end: int) -> list[int]:
    start = max(season_start, family.minimum_recommended_first_backfill_season)
    if family.source_type == "static_snapshot":
        return []
    if start > season_end:
        return []
    return list(range(start, season_end + 1))


def _week_behavior(family: SourceFamily, mode: str, week_start: int | None, week_end: int | None) -> tuple[list[int] | None, str, list[str]]:
    warnings: list[str] = []
    if mode == "weekly_refresh":
        weeks = list(range(int(week_start), int(week_end) + 1)) if week_start is not None and week_end is not None else None
        if family.supports_week_filter:
            return weeks, "week-bounded planning supported by registry", warnings
        warnings.append("Source loader is season-level. Future weekly refresh must load season data and merge only impacted weeks.")
        return weeks, "season-level loader, impacted-week merge required later", warnings

    if week_start is not None or week_end is not None:
        if family.supports_week_filter:
            weeks = list(range(int(week_start), int(week_end) + 1)) if week_start is not None and week_end is not None else None
            return weeks, "historical plan includes requested week subset", warnings
        warnings.append("historical_backfill mode ignores week bounds for this season-level loader.")
        return None, "week bounds ignored for historical season-level plan", warnings

    return None, "no week filter requested", warnings


def build_plan(
    *,
    mode: str = "historical_backfill",
    project: str = DEFAULT_PROJECT,
    dataset: str = DEFAULT_DATASET,
    season_start: int | None = None,
    season_end: int | None = None,
    week_start: int | None = None,
    week_end: int | None = None,
    source_families: Iterable[str] | None = None,
    preset: str | None = None,
    all_source_families: bool = False,
    inspect_bigquery: bool = True,
    inspector: Any | None = None,
) -> dict[str, Any]:
    season_start, season_end = _validate_bounds(
        mode=mode,
        season_start=season_start,
        season_end=season_end,
        week_start=week_start,
        week_end=week_end,
    )
    selected = select_source_families(
        source_families=source_families,
        preset=preset,
        all_source_families=all_source_families,
    )

    global_warnings: list[str] = [
        "Phase 29.5 planner only. No nflverse loaders are called and no BigQuery rows are written.",
        "Raw raw_nflverse_* tables are not Pigskin/UI-safe surfaces.",
    ]
    if mode == "weekly_refresh":
        global_warnings.append("Weekly refresh is planning-only. Live weekly writes are not implemented in Phase 29.5.")

    if inspect_bigquery and inspector is None:
        try:
            inspector = BigQueryPlanInspector(project, dataset)
        except Exception as exc:
            global_warnings.append(f"BigQuery inspection unavailable: {exc}")

    per_family = []
    blocked_sources: list[dict[str, Any]] = []
    for name in selected:
        family = SOURCE_FAMILY_REGISTRY[name]
        target_seasons = _target_seasons(family, season_start, season_end)
        target_weeks, week_filter_behavior, week_warnings = _week_behavior(family, mode, week_start, week_end)
        warnings = list(family.warnings) + week_warnings
        if family.source_type != "static_snapshot" and not target_seasons:
            warning = (
                f"No target seasons remain after applying limited range {family.known_limited_range}."
                if family.known_limited_range
                else "No target seasons selected."
            )
            warnings.append(warning)
            blocked_sources.append({"source_family": name, "reason": warning})

        inspection = TableInspection(None, None, None, ("BigQuery inspection not requested.",))
        if inspector is not None:
            inspection = inspector.inspect(family, season_start, season_end)
            warnings.extend(inspection.warnings)

        per_family.append(
            {
                "source_family": family.source_family,
                "loader": family.loader,
                "target_table": family.target_table,
                "table_exists": inspection.table_exists,
                "current_row_count": inspection.current_row_count,
                "existing_coverage": inspection.existing_coverage,
                "target_seasons": target_seasons,
                "target_weeks": target_weeks,
                "source_type": family.source_type,
                "known_limited_range": family.known_limited_range,
                "supports_week_filter": family.supports_week_filter,
                "week_filter_behavior": week_filter_behavior,
                "natural_key_fields": list(family.natural_key_fields),
                "required_metadata_fields": list(family.required_metadata_fields),
                "partition_field": family.partition_field,
                "clustering_fields": list(family.clustering_fields),
                "downstream_staging_tables": list(family.downstream_staging_tables),
                "validation_patterns": list(family.validation_patterns),
                "future_authorization_gate": (
                    DEFAULT_FUTURE_WEEKLY_GATE if mode == "weekly_refresh" else family.future_authorization_gate
                ),
                "warnings": warnings,
            }
        )

    return {
        "dry_run": True,
        "mode": mode,
        "project": project,
        "dataset": dataset,
        "season_start": season_start,
        "season_end": season_end,
        "week_start": week_start,
        "week_end": week_end,
        "selected_source_families": selected,
        "skipped_source_families": [name for name in SOURCE_FAMILY_REGISTRY if name not in selected],
        "source_family_plans": per_family,
        "global_warnings": global_warnings,
        "blocked_sources": blocked_sources,
        "next_required_phase": "Authorized Phase 29 historical backfill implementation with idempotent writes.",
    }


def plan_to_text(plan: dict[str, Any]) -> str:
    lines = [
        "nflverse backfill plan",
        f"dry_run: {plan['dry_run']}",
        f"mode: {plan['mode']}",
        f"project.dataset: {plan['project']}.{plan['dataset']}",
        f"season range: {plan['season_start']}-{plan['season_end']}",
        f"week range: {plan['week_start']}-{plan['week_end']}",
        f"selected source families: {', '.join(plan['selected_source_families'])}",
        "",
        "global warnings:",
    ]
    lines.extend(f"- {warning}" for warning in plan["global_warnings"])
    lines.append("")
    lines.append("source family plans:")
    for item in plan["source_family_plans"]:
        lines.extend(
            [
                f"- {item['source_family']}:",
                f"  loader: {item['loader']}",
                f"  target_table: {item['target_table']}",
                f"  table_exists: {item['table_exists']}",
                f"  current_row_count: {item['current_row_count']}",
                f"  target_seasons: {item['target_seasons']}",
                f"  target_weeks: {item['target_weeks']}",
                f"  week_filter_behavior: {item['week_filter_behavior']}",
                f"  natural_key_fields: {', '.join(item['natural_key_fields'])}",
                f"  validation_patterns: {', '.join(item['validation_patterns'])}",
                f"  future_authorization_gate: {item['future_authorization_gate']}",
            ]
        )
        if item["warnings"]:
            lines.append("  warnings:")
            lines.extend(f"    - {warning}" for warning in item["warnings"])
    if plan["blocked_sources"]:
        lines.append("")
        lines.append("blocked sources:")
        for blocked in plan["blocked_sources"]:
            lines.append(f"- {blocked['source_family']}: {blocked['reason']}")
    lines.append("")
    lines.append(f"next_required_phase: {plan['next_required_phase']}")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dry-run-only nflverse backfill planner.")
    parser.add_argument("--plan-only", action="store_true", help="Required in Phase 29.5. Produce a non-mutating plan.")
    parser.add_argument("--source-family", action="append", help="Source family to include. May be repeated or comma-separated.")
    parser.add_argument("--all-source-families", action="store_true", help="Plan all registered source families.")
    parser.add_argument("--preset", choices=sorted(PRESETS), help="Source-family preset.")
    parser.add_argument("--season-start", type=int, help="First target season.")
    parser.add_argument("--season-end", type=int, help="Last target season.")
    parser.add_argument("--week-start", type=int, help="First target week for weekly_refresh planning.")
    parser.add_argument("--week-end", type=int, help="Last target week for weekly_refresh planning.")
    parser.add_argument("--mode", choices=["historical_backfill", "weekly_refresh"], default="historical_backfill")
    parser.add_argument("--project", default=os.environ.get("BQ_PROJECT") or DEFAULT_PROJECT)
    parser.add_argument("--dataset", default=os.environ.get("BQ_DATASET") or DEFAULT_DATASET)
    parser.add_argument("--output-json", type=Path, help="Optional path for writing the plan JSON.")
    parser.add_argument("--strict", action="store_true", help="Fail if any source is blocked by range limits.")
    parser.add_argument(
        "--skip-bigquery-inspection",
        action="store_true",
        help="Skip read-only table existence, row count, and coverage inspection.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.plan_only:
        gate = DEFAULT_FUTURE_WEEKLY_GATE if args.mode == "weekly_refresh" else DEFAULT_FUTURE_HISTORICAL_GATE
        print(
            f"Live execution is not implemented in Phase 29.5. "
            f"Future execution would require {gate}=true and a separate authorized phase.",
            file=sys.stderr,
        )
        return 2

    try:
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
            all_source_families=args.all_source_families,
            inspect_bigquery=not args.skip_bigquery_inspection,
        )
    except PlanError as exc:
        print(f"Plan error: {exc}", file=sys.stderr)
        return 2

    if args.strict and plan["blocked_sources"]:
        print(json.dumps(plan, indent=2, sort_keys=True))
        print("Strict mode failed: blocked source families present.", file=sys.stderr)
        return 2

    if args.output_json:
        args.output_json.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote plan JSON: {args.output_json}")

    print(plan_to_text(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
