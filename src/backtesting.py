"""Deterministic projection backtesting and evaluation jobs."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from google.cloud import bigquery

from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_SCORING_PROFILE = "ppr"
DEFAULT_LEAGUE_TYPE = "redraft"
DEFAULT_ROSTER_FORMAT = "one_qb"
BACKTEST_VERSION = "backtest_v1"
BACKTEST_CREATED_BY = "backtesting"
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("BACKTEST_MAX_BYTES_BILLED", "1000000000"))
MAX_SEASON_SPAN = int(os.environ.get("BACKTEST_MAX_SEASON_SPAN", "3"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")

BACKTEST_RUNS_TABLE = "backtest_runs"
PLAYER_WEEK_TABLE = "backtest_result_player_week"
SUMMARY_TABLE = "backtest_result_summary"
CALIBRATION_TABLE = "backtest_calibration_bins"


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def create_backtest_run(
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    backtest_run_id: str | None = None,
    model_run_id: str | None = None,
    backtest_name: str | None = None,
    backtest_version: str = BACKTEST_VERSION,
    projection_horizon: str = "weekly",
    season_start: int,
    season_end: int,
    week_start: int | None = None,
    week_end: int | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    feature_config_version_id: str | None = None,
    source_freshness_snapshot_id: str | None = None,
    created_by: str = BACKTEST_CREATED_BY,
    notes: str | None = None,
    allow_large_backtest: bool = False,
) -> str:
    """Insert a running backtest row and return its ID."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    projection_horizon = _normalize_horizon(projection_horizon)
    week_start, week_end = _normalize_week_range(week_start, week_end)
    _validate_backtest_window(season_start, season_end, week_start, week_end, allow_large_backtest)
    backtest_run_id = backtest_run_id or _generate_backtest_run_id(projection_horizon, season_start, season_end)

    sql = f"""
    INSERT INTO `{_table_id(client.project, dataset_id, BACKTEST_RUNS_TABLE)}` (
        backtest_run_id,
        model_run_id,
        backtest_name,
        backtest_version,
        projection_horizon,
        season_start,
        season_end,
        week_start,
        week_end,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        feature_config_version_id,
        source_freshness_snapshot_id,
        status,
        created_by,
        created_at,
        completed_at,
        error_message,
        notes
    )
    VALUES (
        @backtest_run_id,
        @model_run_id,
        @backtest_name,
        @backtest_version,
        @projection_horizon,
        @season_start,
        @season_end,
        @week_start,
        @week_end,
        @scoring_profile_id,
        @league_type_id,
        @roster_format_id,
        @feature_config_version_id,
        @source_freshness_snapshot_id,
        'running',
        @created_by,
        CURRENT_TIMESTAMP(),
        NULL,
        NULL,
        @notes
    )
    """
    client.query(sql, job_config=_job_config([
        ("backtest_run_id", "STRING", backtest_run_id),
        ("model_run_id", "STRING", model_run_id),
        ("backtest_name", "STRING", backtest_name or f"{projection_horizon}_{season_start}_{season_end}"),
        ("backtest_version", "STRING", backtest_version),
        ("projection_horizon", "STRING", projection_horizon),
        ("season_start", "INT64", int(season_start)),
        ("season_end", "INT64", int(season_end)),
        ("week_start", "INT64", week_start),
        ("week_end", "INT64", week_end),
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("feature_config_version_id", "STRING", feature_config_version_id),
        ("source_freshness_snapshot_id", "STRING", source_freshness_snapshot_id),
        ("created_by", "STRING", created_by),
        ("notes", "STRING", notes),
    ])).result()
    return backtest_run_id


def mark_backtest_run_complete(
    backtest_run_id: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    notes: str | None = None,
) -> None:
    """Mark a backtest complete."""

    _require_backtest_run_id(backtest_run_id)
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql = f"""
    UPDATE `{_table_id(client.project, dataset_id, BACKTEST_RUNS_TABLE)}`
    SET
        status = 'complete',
        completed_at = CURRENT_TIMESTAMP(),
        notes = IF(@notes IS NULL, notes, @notes)
    WHERE backtest_run_id = @backtest_run_id
    """
    client.query(sql, job_config=_job_config([
        ("backtest_run_id", "STRING", backtest_run_id),
        ("notes", "STRING", notes),
    ])).result()


def mark_backtest_run_failed(
    backtest_run_id: str,
    error_message: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    notes: str | None = None,
) -> None:
    """Mark a backtest failed, preserving the original error text."""

    _require_backtest_run_id(backtest_run_id)
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql = f"""
    UPDATE `{_table_id(client.project, dataset_id, BACKTEST_RUNS_TABLE)}`
    SET
        status = 'failed',
        completed_at = CURRENT_TIMESTAMP(),
        error_message = @error_message,
        notes = IF(@notes IS NULL, notes, @notes)
    WHERE backtest_run_id = @backtest_run_id
    """
    client.query(sql, job_config=_job_config([
        ("backtest_run_id", "STRING", backtest_run_id),
        ("error_message", "STRING", str(error_message)),
        ("notes", "STRING", notes),
    ])).result()


def load_projection_rows(
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    model_run_id: str | None = None,
    horizon: str = "weekly",
    season_start: int,
    season_end: int,
    week_start: int | None = None,
    week_end: int | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    allow_large_backtest: bool = False,
) -> list[dict[str, Any]]:
    """Load projection outputs for evaluation from curated output tables."""

    horizon = _normalize_horizon(horizon)
    if horizon != "weekly":
        raise ValueError("Backtesting v1 supports weekly player-week projection evaluation only.")
    week_start, week_end = _normalize_week_range(week_start, week_end)
    _validate_backtest_window(season_start, season_end, week_start, week_end, allow_large_backtest)
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()

    filters = [
        "projection_horizon = @projection_horizon",
        "season BETWEEN @season_start AND @season_end",
        "week BETWEEN @week_start AND @week_end",
        "scoring_profile_id = @scoring_profile_id",
        "league_type_id = @league_type_id",
        "roster_format_id = @roster_format_id",
    ]
    params: list[tuple[str, str, Any]] = [
        ("projection_horizon", "STRING", horizon),
        ("season_start", "INT64", int(season_start)),
        ("season_end", "INT64", int(season_end)),
        ("week_start", "INT64", int(week_start)),
        ("week_end", "INT64", int(week_end)),
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
    ]
    if model_run_id:
        filters.append("model_run_id = @model_run_id")
        params.append(("model_run_id", "STRING", model_run_id))

    sql = f"""
    SELECT
        model_run_id,
        player_id_internal,
        source_player_key,
        display_name,
        position,
        team,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        projection_horizon,
        projected_points_mean AS projected_points,
        projected_points_floor AS projected_floor,
        projected_points_ceiling AS projected_ceiling,
        confidence_score,
        risk_score,
        rank_source,
        source_freshness_json,
        missing_data_flags,
        created_at
    FROM `{_table_id(client.project, dataset_id, "projections_player_weekly")}`
    WHERE {" AND ".join(filters)}
    """
    return _query_rows(client, sql, _job_config(params))


def load_actual_rows(
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    season_start: int,
    season_end: int,
    week_start: int | None = None,
    week_end: int | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    allow_large_backtest: bool = False,
) -> list[dict[str, Any]]:
    """Load historical fantasy actuals from the scoring-profile mart."""

    week_start, week_end = _normalize_week_range(week_start, week_end)
    _validate_backtest_window(season_start, season_end, week_start, week_end, allow_large_backtest)
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql = f"""
    SELECT
        player_id_internal,
        source_player_key,
        player_display_name AS display_name,
        team,
        opponent,
        position,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        total_fantasy_points AS actual_points,
        source_freshness_json,
        missing_data_flags
    FROM `{_table_id(client.project, dataset_id, "analytics_player_fantasy_points_by_profile")}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND season BETWEEN @season_start AND @season_end
        AND week BETWEEN @week_start AND @week_end
        AND (league_type_id IS NULL OR league_type_id = @league_type_id)
        AND (roster_format_id IS NULL OR roster_format_id = @roster_format_id)
    """
    return _query_rows(client, sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("season_start", "INT64", int(season_start)),
        ("season_end", "INT64", int(season_end)),
        ("week_start", "INT64", int(week_start)),
        ("week_end", "INT64", int(week_end)),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
    ]))


def evaluate_player_week_predictions(
    projection_rows: list[dict[str, Any]],
    actual_rows: list[dict[str, Any]],
    *,
    backtest_run_id: str,
) -> dict[str, Any]:
    """Compare weekly projection rows against matched player-week actual rows."""

    _require_backtest_run_id(backtest_run_id)
    projection_rows = [dict(row) for row in projection_rows]
    actual_rows = [dict(row) for row in actual_rows]
    if not projection_rows:
        return {
            "rows": [],
            "missing_projection_rows": True,
            "missing_actual_rows": 0,
            "unmatched_projection_rows": 0,
        }
    if not actual_rows:
        return {
            "rows": [],
            "missing_projection_rows": False,
            "missing_actual_rows": len(projection_rows),
            "unmatched_projection_rows": len(projection_rows),
        }

    _assign_ranks(projection_rows, "projected_points", "projected_rank_overall", "projected_rank_position")
    _assign_ranks(actual_rows, "actual_points", "actual_rank_overall", "actual_rank_position")
    actual_index = _build_actual_index(actual_rows)
    now = _utc_timestamp()
    result_rows: list[dict[str, Any]] = []
    unmatched = 0

    for projection in projection_rows:
        actual = _find_actual_row(projection, actual_index)
        if not actual:
            unmatched += 1
            continue
        projected_points = _num(projection.get("projected_points"), None)
        actual_points = _num(actual.get("actual_points"), None)
        if projected_points is None or actual_points is None:
            unmatched += 1
            continue
        position = projection.get("position") or actual.get("position")
        boom_threshold, bust_threshold = _thresholds(position)
        absolute_error = abs(projected_points - actual_points)
        projected_floor = _num(projection.get("projected_floor"), None)
        projected_ceiling = _num(projection.get("projected_ceiling"), None)
        actual_inside_range = (
            projected_floor is not None
            and projected_ceiling is not None
            and projected_floor <= actual_points <= projected_ceiling
        )
        projected_rank_overall = _int_or_none(projection.get("projected_rank_overall"))
        actual_rank_overall = _int_or_none(actual.get("actual_rank_overall"))
        projected_rank_position = _int_or_none(projection.get("projected_rank_position"))
        actual_rank_position = _int_or_none(actual.get("actual_rank_position"))
        flags = sorted(set(
            _json_array(projection.get("missing_data_flags"))
            + _json_array(actual.get("missing_data_flags"))
        ))
        result_json = {
            "projection_rank_source": projection.get("rank_source"),
            "projection_source_freshness_json": projection.get("source_freshness_json"),
            "actual_source_freshness_json": actual.get("source_freshness_json"),
            "future_leakage_check": "target_season_week_matched_actual_season_week",
        }
        result_rows.append({
            "backtest_run_id": backtest_run_id,
            "model_run_id": projection.get("model_run_id"),
            "player_id_internal": projection.get("player_id_internal") or actual.get("player_id_internal"),
            "source_player_key": projection.get("source_player_key") or actual.get("source_player_key"),
            "display_name": projection.get("display_name") or actual.get("display_name"),
            "position": position,
            "team": projection.get("team") or actual.get("team"),
            "season": int(projection["season"]),
            "week": int(projection["week"]),
            "scoring_profile_id": projection.get("scoring_profile_id") or actual.get("scoring_profile_id"),
            "league_type_id": projection.get("league_type_id") or actual.get("league_type_id") or DEFAULT_LEAGUE_TYPE,
            "roster_format_id": projection.get("roster_format_id") or actual.get("roster_format_id") or DEFAULT_ROSTER_FORMAT,
            "projection_horizon": projection.get("projection_horizon") or "weekly",
            "projected_points": round(projected_points, 3),
            "actual_points": round(actual_points, 3),
            "absolute_error": round(absolute_error, 3),
            "squared_error": round(absolute_error * absolute_error, 3),
            "projected_rank_overall": projected_rank_overall,
            "actual_rank_overall": actual_rank_overall,
            "projected_rank_position": projected_rank_position,
            "actual_rank_position": actual_rank_position,
            "rank_error_overall": _rank_error(projected_rank_overall, actual_rank_overall),
            "rank_error_position": _rank_error(projected_rank_position, actual_rank_position),
            "projected_floor": projected_floor,
            "projected_ceiling": projected_ceiling,
            "actual_inside_range": actual_inside_range,
            "boom_threshold": boom_threshold,
            "bust_threshold": bust_threshold,
            "projected_boom_flag": projected_points >= boom_threshold,
            "actual_boom_flag": actual_points >= boom_threshold,
            "projected_bust_flag": projected_points <= bust_threshold,
            "actual_bust_flag": actual_points <= bust_threshold,
            "result_json": json.dumps(result_json, sort_keys=True),
            "missing_data_flags": json.dumps(flags, sort_keys=True),
            "created_at": now,
        })

    return {
        "rows": result_rows,
        "missing_projection_rows": False,
        "missing_actual_rows": unmatched,
        "unmatched_projection_rows": unmatched,
    }


def compute_summary_metrics(result_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate player-week results into overall, position, and week summaries."""

    if not result_rows:
        return []
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in result_rows:
        base_key = (
            row.get("backtest_run_id"),
            row.get("model_run_id"),
            row.get("projection_horizon"),
            row.get("scoring_profile_id"),
            row.get("league_type_id"),
            row.get("roster_format_id"),
            row.get("market_source_id"),
        )
        for suffix in (
            (None, None, None, "overall"),
            (row.get("position"), None, None, "position"),
            (None, row.get("season"), row.get("week"), "week"),
        ):
            key = base_key + suffix
            groups.setdefault(key, []).append(row)
    return [_summary_row(key, rows) for key, rows in sorted(groups.items(), key=lambda item: str(item[0]))]


def compute_calibration_bins(result_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Bucket projected points and compare average projected to average actual."""

    if not result_rows:
        return []
    bins = [
        ("0_to_5", 0.0, 5.0),
        ("5_to_10", 5.0, 10.0),
        ("10_to_15", 10.0, 15.0),
        ("15_to_20", 15.0, 20.0),
        ("20_plus", 20.0, None),
    ]
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in result_rows:
        projected = _num(row.get("projected_points"), None)
        if projected is None:
            continue
        bin_name, bin_min, bin_max = _find_bin(projected, bins)
        base_key = (
            row.get("backtest_run_id"),
            row.get("model_run_id"),
            row.get("projection_horizon"),
            row.get("scoring_profile_id"),
            row.get("league_type_id"),
            row.get("roster_format_id"),
        )
        for position in (None, row.get("position")):
            key = base_key + (position, bin_name, bin_min, bin_max)
            grouped.setdefault(key, []).append(row)
    now = _utc_timestamp()
    output = []
    for key, rows in sorted(grouped.items(), key=lambda item: str(item[0])):
        (
            backtest_run_id,
            model_run_id,
            horizon,
            scoring_profile_id,
            league_type_id,
            roster_format_id,
            position,
            bin_name,
            bin_min,
            bin_max,
        ) = key
        avg_projected = _mean(row.get("projected_points") for row in rows)
        avg_actual = _mean(row.get("actual_points") for row in rows)
        avg_error = None if avg_projected is None or avg_actual is None else avg_projected - avg_actual
        output.append({
            "backtest_run_id": backtest_run_id,
            "model_run_id": model_run_id,
            "projection_horizon": horizon,
            "scoring_profile_id": scoring_profile_id,
            "league_type_id": league_type_id,
            "roster_format_id": roster_format_id,
            "position": position,
            "bin_name": bin_name,
            "bin_min": bin_min,
            "bin_max": bin_max,
            "player_count": len(rows),
            "avg_projected": _round(avg_projected),
            "avg_actual": _round(avg_actual),
            "avg_error": _round(avg_error),
            "calibration_json": json.dumps({"bin_rule": "projected_points"}, sort_keys=True),
            "created_at": now,
        })
    return output


def write_backtest_results(
    *,
    player_week_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    calibration_rows: list[dict[str, Any]],
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, int]:
    """Write backtest result rows after enforcing backtest lineage."""

    for row_set, label in (
        (player_week_rows, "player_week_rows"),
        (summary_rows, "summary_rows"),
        (calibration_rows, "calibration_rows"),
    ):
        _ensure_backtest_run_id(row_set, label)
    counts = {
        "player_week_rows": len(player_week_rows),
        "summary_rows": len(summary_rows),
        "calibration_rows": len(calibration_rows),
    }
    if dry_run:
        return counts
    if not player_week_rows and not summary_rows and not calibration_rows:
        return counts

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    backtest_run_id = _first_backtest_run_id(player_week_rows, summary_rows, calibration_rows)
    _delete_existing_backtest_results(client, dataset_id, backtest_run_id)
    _insert_rows(client, dataset_id, PLAYER_WEEK_TABLE, player_week_rows)
    _insert_rows(client, dataset_id, SUMMARY_TABLE, summary_rows)
    _insert_rows(client, dataset_id, CALIBRATION_TABLE, calibration_rows)
    return counts


def run_backtest(
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    model_run_id: str | None = None,
    horizon: str = "weekly",
    season_start: int,
    season_end: int,
    week_start: int | None = None,
    week_end: int | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    backtest_name: str | None = None,
    market_source_id: str | None = None,
    dry_run: bool = False,
    allow_large_backtest: bool = False,
) -> dict[str, Any]:
    """Run a deterministic weekly projection backtest."""

    horizon = _normalize_horizon(horizon)
    week_start, week_end = _normalize_week_range(week_start, week_end)
    _validate_backtest_window(season_start, season_end, week_start, week_end, allow_large_backtest)
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    model_context = _get_model_run_context(client, dataset_id, model_run_id) if model_run_id and not dry_run else {}
    backtest_run_id = "dry-run"
    if not dry_run:
        backtest_run_id = create_backtest_run(
            client=client,
            dataset_id=dataset_id,
            model_run_id=model_run_id,
            backtest_name=backtest_name,
            projection_horizon=horizon,
            season_start=season_start,
            season_end=season_end,
            week_start=week_start,
            week_end=week_end,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            feature_config_version_id=model_context.get("feature_config_version_id"),
            source_freshness_snapshot_id=model_context.get("source_freshness_snapshot_id"),
            allow_large_backtest=allow_large_backtest,
        )

    try:
        projection_rows = load_projection_rows(
            client=client,
            dataset_id=dataset_id,
            model_run_id=model_run_id,
            horizon=horizon,
            season_start=season_start,
            season_end=season_end,
            week_start=week_start,
            week_end=week_end,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            allow_large_backtest=allow_large_backtest,
        )
        actual_rows = load_actual_rows(
            client=client,
            dataset_id=dataset_id,
            season_start=season_start,
            season_end=season_end,
            week_start=week_start,
            week_end=week_end,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            allow_large_backtest=allow_large_backtest,
        )
        evaluation = evaluate_player_week_predictions(
            projection_rows,
            actual_rows,
            backtest_run_id=backtest_run_id,
        )
        player_week_rows = evaluation["rows"]
        market_row_count = 0
        if market_source_id and player_week_rows:
            from src.market_consensus import compare_projection_to_market, get_current_market_baseline

            market_rows = get_current_market_baseline(
                client=client,
                dataset_id=dataset_id,
                source_id=market_source_id,
                scoring_profile_id=scoring_profile_id,
                league_type_id=league_type_id,
                roster_format_id=roster_format_id,
                limit=5000,
            )
            market_row_count = len(market_rows)
            market_comparison = compare_projection_to_market(player_week_rows, market_rows)
            player_week_rows = market_comparison["rows"]
        summary_rows = compute_summary_metrics(player_week_rows)
        calibration_rows = compute_calibration_bins(player_week_rows)
        missing_flags = _run_missing_flags(projection_rows, actual_rows, evaluation)
        if market_source_id and market_row_count == 0:
            missing_flags.append("missing_market_baseline_rows")

        if not player_week_rows:
            message = f"No matched player-week rows produced. missing_data_flags={json.dumps(missing_flags, sort_keys=True)}"
            if not dry_run:
                mark_backtest_run_failed(
                    backtest_run_id,
                    message,
                    client=client,
                    dataset_id=dataset_id,
                    notes=json.dumps({"missing_data_flags": missing_flags}, sort_keys=True),
                )
            return {
                "backtest_run_id": backtest_run_id,
                "model_run_id": model_run_id,
                "status": "failed",
                "missing_data_flags": missing_flags,
                "projection_rows": len(projection_rows),
                "actual_rows": len(actual_rows),
                "market_rows": market_row_count,
                "player_week_rows": 0,
                "summary_rows": 0,
                "calibration_rows": 0,
            }

        write_counts = write_backtest_results(
            player_week_rows=player_week_rows,
            summary_rows=summary_rows,
            calibration_rows=calibration_rows,
            client=client,
            dataset_id=dataset_id,
            dry_run=dry_run,
        )
        if not dry_run:
            mark_backtest_run_complete(
                backtest_run_id,
                client=client,
                dataset_id=dataset_id,
                notes=json.dumps(write_counts | {"missing_data_flags": missing_flags}, sort_keys=True),
            )
        return {
            "backtest_run_id": backtest_run_id,
            "model_run_id": model_run_id,
            "status": "dry_run" if dry_run else "complete",
            "missing_data_flags": missing_flags,
            "projection_rows": len(projection_rows),
            "actual_rows": len(actual_rows),
            "market_rows": market_row_count,
            **write_counts,
            "rows": player_week_rows if dry_run else [],
            "summary": summary_rows if dry_run else [],
            "calibration_bins": calibration_rows if dry_run else [],
        }
    except Exception as exc:
        if not dry_run:
            mark_backtest_run_failed(
                backtest_run_id,
                str(exc),
                client=client,
                dataset_id=dataset_id,
            )
        raise


def _summary_row(key: tuple[Any, ...], rows: list[dict[str, Any]]) -> dict[str, Any]:
    (
        backtest_run_id,
        model_run_id,
        horizon,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        market_source_id,
        position,
        season,
        week,
        group_type,
    ) = key
    projected = [_num(row.get("projected_points"), 0.0) for row in rows]
    actual = [_num(row.get("actual_points"), 0.0) for row in rows]
    errors = [_num(row.get("absolute_error"), 0.0) for row in rows]
    squared_errors = [_num(row.get("squared_error"), 0.0) for row in rows]
    rank_errors_overall = [_num(row.get("rank_error_overall"), None) for row in rows]
    rank_errors_position = [_num(row.get("rank_error_position"), None) for row in rows]
    projected_top_12 = [row for row in rows if _int_or_none(row.get("projected_rank_overall")) is not None and row["projected_rank_overall"] <= 12]
    projected_top_24 = [row for row in rows if _int_or_none(row.get("projected_rank_overall")) is not None and row["projected_rank_overall"] <= 24]
    projected_boom = [row for row in rows if row.get("projected_boom_flag")]
    projected_bust = [row for row in rows if row.get("projected_bust_flag")]
    ranged = [row for row in rows if row.get("projected_floor") is not None and row.get("projected_ceiling") is not None]
    summary = {
        "backtest_run_id": backtest_run_id,
        "model_run_id": model_run_id,
        "projection_horizon": horizon,
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "position": position,
        "season": season,
        "week": week,
        "player_count": len(rows),
        "mae": _round(_mean(errors)),
        "rmse": _round(math.sqrt(_mean(squared_errors) or 0.0)),
        "mean_bias": _round(_mean(p - a for p, a in zip(projected, actual))),
        "rank_mae_overall": _round(_mean(value for value in rank_errors_overall if value is not None)),
        "rank_mae_position": _round(_mean(value for value in rank_errors_position if value is not None)),
        "spearman_proxy": _round(_spearman_proxy(rows)),
        "top_12_hit_rate": _round(_hit_rate(projected_top_12, 12)),
        "top_24_hit_rate": _round(_hit_rate(projected_top_24, 24)),
        "boom_precision": _round(_precision(projected_boom, "actual_boom_flag")),
        "bust_precision": _round(_precision(projected_bust, "actual_bust_flag")),
        "range_calibration_rate": _round(_precision(ranged, "actual_inside_range")),
        "summary_json": json.dumps({"group_type": group_type}, sort_keys=True),
        "created_at": _utc_timestamp(),
    }
    if market_source_id:
        market_errors = [_num(row.get("market_absolute_error"), None) for row in rows]
        market_errors = [value for value in market_errors if value is not None]
        model_errors = [_num(row.get("absolute_error"), None) for row in rows if row.get("market_absolute_error") is not None]
        market_rank_errors = [_num(row.get("market_rank_error_overall"), None) for row in rows]
        market_rank_errors = [value for value in market_rank_errors if value is not None]
        model_rank_errors = [_num(row.get("rank_error_overall"), None) for row in rows if row.get("market_rank_error_overall") is not None]
        better_rows = [row for row in rows if row.get("model_better_than_market") is not None]
        summary.update({
            "market_source_id": market_source_id,
            "model_vs_market_mae_delta": _delta(_mean(model_errors), _mean(market_errors)),
            "model_vs_market_rank_delta": _delta(_mean(model_rank_errors), _mean(market_rank_errors)),
            "model_better_than_market_rate": _round(_precision(better_rows, "model_better_than_market")),
        })
    return summary


def _assign_ranks(
    rows: list[dict[str, Any]],
    value_key: str,
    overall_field: str,
    position_field: str,
) -> None:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in rows:
        key = (
            row.get("model_run_id"),
            row.get("season"),
            row.get("week"),
            row.get("scoring_profile_id"),
            row.get("league_type_id"),
            row.get("roster_format_id"),
        )
        groups.setdefault(key, []).append(row)
    for group_rows in groups.values():
        position_counts: dict[str, int] = {}
        sorted_rows = sorted(group_rows, key=lambda row: _num(row.get(value_key), -9999.0) or -9999.0, reverse=True)
        for overall_rank, row in enumerate(sorted_rows, start=1):
            position = str(row.get("position") or "UNK")
            position_counts[position] = position_counts.get(position, 0) + 1
            row[overall_field] = overall_rank
            row[position_field] = position_counts[position]


def _build_actual_index(rows: list[dict[str, Any]]) -> dict[tuple[Any, ...], dict[str, Any]]:
    index: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        for key in _identity_keys(row):
            index.setdefault(key, row)
    return index


def _find_actual_row(projection: dict[str, Any], index: dict[tuple[Any, ...], dict[str, Any]]) -> dict[str, Any] | None:
    for key in _identity_keys(projection):
        if key in index:
            return index[key]
    return None


def _identity_keys(row: dict[str, Any]) -> list[tuple[Any, ...]]:
    season = _int_or_none(row.get("season"))
    week = _int_or_none(row.get("week"))
    scoring_profile_id = row.get("scoring_profile_id")
    position = row.get("position")
    keys = []
    if row.get("player_id_internal"):
        keys.append(("internal", row.get("player_id_internal"), season, week, scoring_profile_id))
    if row.get("source_player_key"):
        keys.append(("source", row.get("source_player_key"), season, week, scoring_profile_id))
    display_name = _normalize_name(row.get("display_name") or row.get("player_display_name"))
    if display_name and position:
        keys.append(("name_position", display_name, str(position).upper(), season, week, scoring_profile_id))
    return keys


def _get_model_run_context(client: Any, dataset_id: str, model_run_id: str | None) -> dict[str, Any]:
    if not model_run_id:
        return {}
    sql = f"""
    SELECT feature_config_version_id, source_freshness_snapshot_id
    FROM `{_table_id(client.project, dataset_id, "model_runs")}`
    WHERE model_run_id = @model_run_id
    LIMIT 1
    """
    rows = _query_rows(client, sql, _job_config([("model_run_id", "STRING", model_run_id)]))
    return rows[0] if rows else {}


def _delete_existing_backtest_results(client: Any, dataset_id: str, backtest_run_id: str) -> None:
    for table_name in (PLAYER_WEEK_TABLE, SUMMARY_TABLE, CALIBRATION_TABLE):
        sql = f"""
        DELETE FROM `{_table_id(client.project, dataset_id, table_name)}`
        WHERE backtest_run_id = @backtest_run_id
        """
        client.query(sql, job_config=_job_config([("backtest_run_id", "STRING", backtest_run_id)])).result()


def _insert_rows(client: Any, dataset_id: str, table_name: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    errors = client.insert_rows_json(_table_id(client.project, dataset_id, table_name), rows)
    if errors:
        raise RuntimeError(f"Failed to insert {table_name}: {errors}")


def _query_rows(client: Any, sql: str, job_config: bigquery.QueryJobConfig) -> list[dict[str, Any]]:
    rows = client.query(sql, job_config=job_config).result()
    result = []
    for row in rows:
        if isinstance(row, dict):
            result.append(dict(row))
        elif hasattr(row, "items"):
            result.append(dict(row.items()))
        else:
            result.append(dict(row))
    return result


def _job_config(params: list[tuple[str, str, Any]]) -> bigquery.QueryJobConfig:
    return bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=[
            bigquery.ScalarQueryParameter(name, param_type, value)
            for name, param_type, value in params
        ],
    )


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    _validate_project_id(project_id)
    _validate_identifier(dataset_id, "dataset_id")
    _validate_identifier(table_name, "table_name")
    return f"{project_id}.{dataset_id}.{table_name}"


def _validate_identifier(value: str, label: str) -> None:
    if not IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"Invalid BigQuery {label}: {value!r}")


def _validate_project_id(value: str) -> None:
    if not PROJECT_ID_RE.fullmatch(value):
        raise ValueError(f"Invalid BigQuery project_id: {value!r}")


def _normalize_horizon(horizon: str) -> str:
    normalized = str(horizon or "").strip().lower().replace("_", "-")
    aliases = {"rest-of-season": "ros", "rest_of_season": "ros"}
    normalized = aliases.get(normalized, normalized)
    if normalized not in {"weekly", "ros", "dynasty"}:
        raise ValueError(f"Unsupported projection horizon: {horizon!r}")
    return normalized


def _normalize_week_range(week_start: int | None, week_end: int | None) -> tuple[int, int]:
    start = 1 if week_start is None else int(week_start)
    end = 18 if week_end is None else int(week_end)
    return start, end


def _validate_backtest_window(
    season_start: int,
    season_end: int,
    week_start: int,
    week_end: int,
    allow_large_backtest: bool,
) -> None:
    season_start = int(season_start)
    season_end = int(season_end)
    week_start = int(week_start)
    week_end = int(week_end)
    if season_start > season_end:
        raise ValueError("season_start must be less than or equal to season_end")
    if week_start > week_end:
        raise ValueError("week_start must be less than or equal to week_end")
    if week_start < 1 or week_end > 18:
        raise ValueError("Backtesting v1 supports NFL regular-season week range 1-18")
    if not allow_large_backtest and season_end - season_start + 1 > MAX_SEASON_SPAN:
        raise ValueError("Backtest season span is too large. Pass allow_large_backtest for explicit large runs.")


def _run_missing_flags(
    projection_rows: list[dict[str, Any]],
    actual_rows: list[dict[str, Any]],
    evaluation: dict[str, Any],
) -> list[str]:
    flags = []
    if not projection_rows:
        flags.append("missing_projection_rows")
    if not actual_rows:
        flags.append("missing_actual_rows")
    if evaluation.get("unmatched_projection_rows"):
        flags.append("unmatched_projection_rows")
    return flags


def _ensure_backtest_run_id(rows: list[dict[str, Any]], label: str) -> None:
    missing = [index for index, row in enumerate(rows) if not row.get("backtest_run_id")]
    if missing:
        raise ValueError(f"{label} missing backtest_run_id at row indexes {missing[:5]}")


def _first_backtest_run_id(*row_sets: list[dict[str, Any]]) -> str:
    for rows in row_sets:
        for row in rows:
            backtest_run_id = row.get("backtest_run_id")
            if backtest_run_id:
                return str(backtest_run_id)
    raise ValueError("No backtest_run_id found in result rows")


def _require_backtest_run_id(backtest_run_id: str | None) -> None:
    if not backtest_run_id:
        raise ValueError("Backtest rows require backtest_run_id")


def _thresholds(position: Any) -> tuple[float, float]:
    position = str(position or "").upper()
    boom = {"QB": 24.0, "RB": 20.0, "WR": 20.0, "TE": 15.0}.get(position, 18.0)
    bust = {"QB": 12.0, "RB": 8.0, "WR": 8.0, "TE": 6.0}.get(position, 8.0)
    return boom, bust


def _rank_error(projected_rank: int | None, actual_rank: int | None) -> int | None:
    if projected_rank is None or actual_rank is None:
        return None
    return abs(projected_rank - actual_rank)


def _find_bin(value: float, bins: list[tuple[str, float, float | None]]) -> tuple[str, float, float | None]:
    for bin_name, bin_min, bin_max in bins:
        if value >= bin_min and (bin_max is None or value < bin_max):
            return bin_name, bin_min, bin_max
    return bins[-1]


def _hit_rate(rows: list[dict[str, Any]], cutoff: int) -> float | None:
    if not rows:
        return None
    hits = 0
    for row in rows:
        actual_rank = _int_or_none(row.get("actual_rank_overall"))
        if actual_rank is not None and actual_rank <= cutoff:
            hits += 1
    return hits / len(rows)


def _precision(rows: list[dict[str, Any]], actual_flag: str) -> float | None:
    if not rows:
        return None
    return sum(1 for row in rows if row.get(actual_flag)) / len(rows)


def _spearman_proxy(rows: list[dict[str, Any]]) -> float | None:
    pairs = [
        (_int_or_none(row.get("projected_rank_overall")), _int_or_none(row.get("actual_rank_overall")))
        for row in rows
    ]
    pairs = [(p, a) for p, a in pairs if p is not None and a is not None]
    n = len(pairs)
    if n < 2:
        return None
    squared_distance = sum((p - a) ** 2 for p, a in pairs)
    denominator = n * ((n * n) - 1)
    if denominator == 0:
        return None
    return 1.0 - (6.0 * squared_distance / denominator)


def _mean(values: Any) -> float | None:
    parsed = [_num(value, None) for value in values]
    parsed = [value for value in parsed if value is not None]
    if not parsed:
        return None
    return sum(parsed) / len(parsed)


def _round(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 4)


def _delta(model_value: float | None, market_value: float | None) -> float | None:
    if model_value is None or market_value is None:
        return None
    return _round(model_value - market_value)


def _num(value: Any, default: float | None = 0.0) -> float | None:
    if value in (None, ""):
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(parsed) or math.isinf(parsed):
        return default
    return parsed


def _int_or_none(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _json_array(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed if item is not None]


def _normalize_name(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _generate_backtest_run_id(horizon: str, season_start: int, season_end: int) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"backtest-{horizon}-{season_start}-{season_end}-{stamp}-{uuid.uuid4().hex[:8]}"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic projection backtests.")
    parser.add_argument("--model-run-id")
    parser.add_argument("--horizon", choices=("weekly", "ros", "dynasty"), default="weekly")
    parser.add_argument("--season-start", required=True, type=int)
    parser.add_argument("--season-end", required=True, type=int)
    parser.add_argument("--week-start", type=int)
    parser.add_argument("--week-end", type=int)
    parser.add_argument("--scoring-profile", default=DEFAULT_SCORING_PROFILE)
    parser.add_argument("--league-type", default=DEFAULT_LEAGUE_TYPE)
    parser.add_argument("--roster-format", default=DEFAULT_ROSTER_FORMAT)
    parser.add_argument("--backtest-name")
    parser.add_argument("--market-source-id")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-large-backtest", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    result = run_backtest(
        model_run_id=args.model_run_id,
        horizon=args.horizon,
        season_start=args.season_start,
        season_end=args.season_end,
        week_start=args.week_start,
        week_end=args.week_end,
        scoring_profile_id=args.scoring_profile,
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        backtest_name=args.backtest_name,
        market_source_id=args.market_source_id,
        dry_run=args.dry_run,
        allow_large_backtest=args.allow_large_backtest,
    )
    print(json.dumps(result, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
