"""Deterministic claim grading for the Meatbag Claim Ledger.

This module does not call LLMs, scrape sources, or expose raw warehouse tables.
It grades manual claims against curated actuals, Pigskin projections, and market
baselines where available.
"""

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
DEFAULT_GRADING_VERSION = "claim_grading_v1"
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("CLAIM_GRADING_MAX_BYTES_BILLED", "1000000000"))

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")

RUNS_TABLE = "claim_grading_runs"
GRADES_TABLE = "claim_grades"
SCORECARDS_TABLE = "claim_source_scorecards"

CLAIMS_TABLE = "fantasy_claims"
CLAIM_PLAYERS_TABLE = "fantasy_claim_players"
WINDOWS_TABLE = "claim_evaluation_windows"

ALLOWED_STATUSES = {"created", "running", "completed", "failed"}
ALLOWED_VERDICTS = {"good_take", "lucky", "wrong", "fraud", "galaxy_brain", "inconclusive"}


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def create_claim_grading_run(
    *,
    claim_grading_run_id: str | None = None,
    grading_name: str = "manual_claim_grading",
    grading_version: str = DEFAULT_GRADING_VERSION,
    season: int | None = None,
    week: int | None = None,
    model_run_id: str | None = None,
    scoring_profile_id: str | None = DEFAULT_SCORING_PROFILE,
    league_type_id: str | None = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str | None = DEFAULT_ROSTER_FORMAT,
    status: str = "created",
    created_by: str = "claim_grading",
    notes: str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Create a claim-grading run row."""

    status = _validate_choice(status, ALLOWED_STATUSES, "status")
    claim_grading_run_id = claim_grading_run_id or _generate_run_id(grading_version, season, week)
    row = {
        "claim_grading_run_id": claim_grading_run_id,
        "grading_name": grading_name,
        "grading_version": grading_version,
        "season": _int_or_none(season),
        "week": _int_or_none(week),
        "model_run_id": model_run_id,
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "status": status,
        "created_by": created_by,
        "created_at": _utc_timestamp(),
        "completed_at": None,
        "error_message": None,
        "notes": notes,
    }
    if dry_run:
        return row

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    _insert_rows(client, dataset_id, RUNS_TABLE, [row])
    return row


def load_claims_ready_to_grade(
    *,
    claim_id: str | None = None,
    season: int | None = None,
    week: int | None = None,
    limit: int = 250,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Load reviewed claims and their primary player/window context."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    where = ["claims.review_status IN ('ready_to_grade', 'reviewed')"]
    params: list[tuple[str, str, Any]] = [("limit", "INT64", max(1, min(int(limit), 1000)))]
    if claim_id:
        where = ["claims.claim_id = @claim_id"]
        params.append(("claim_id", "STRING", claim_id))
    if season is not None:
        where.append("claims.season = @season")
        params.append(("season", "INT64", int(season)))
    if week is not None:
        where.append("(claims.week IS NULL OR claims.week <= @week)")
        where.append("(windows.end_week IS NULL OR windows.end_week <= @week)")
        params.append(("week", "INT64", int(week)))

    sql = f"""
    WITH primary_players AS (
        SELECT * EXCEPT(row_num)
        FROM (
            SELECT
                player_rows.*,
                ROW_NUMBER() OVER (
                    PARTITION BY claim_id
                    ORDER BY
                        CASE player_role_in_claim
                            WHEN 'subject' THEN 0
                            WHEN 'trade_receive' THEN 1
                            WHEN 'trade_send' THEN 2
                            ELSE 9
                        END,
                        display_name
                ) AS row_num
            FROM `{_table_id(client.project, dataset_id, CLAIM_PLAYERS_TABLE)}` player_rows
        )
        WHERE row_num = 1
    )
    SELECT
        claims.*,
        windows.evaluation_window_id,
        windows.start_season,
        windows.start_week,
        windows.end_season,
        windows.end_week,
        windows.evaluation_status,
        players.player_id_internal AS primary_player_id_internal,
        players.source_player_key AS primary_source_player_key,
        players.display_name AS primary_display_name,
        players.position AS primary_position,
        players.team AS primary_team,
        players.claimed_rank AS player_claimed_rank,
        players.claimed_projection AS player_claimed_projection,
        players.claimed_value AS player_claimed_value
    FROM `{_table_id(client.project, dataset_id, CLAIMS_TABLE)}` claims
    JOIN `{_table_id(client.project, dataset_id, WINDOWS_TABLE)}` windows
        ON claims.claim_id = windows.claim_id
    LEFT JOIN primary_players players
        ON claims.claim_id = players.claim_id
    WHERE {" AND ".join(where)}
    ORDER BY claims.claimed_at ASC
    LIMIT @limit
    """
    return _query_rows(client, sql, _job_config(params))


def load_actual_outcomes(
    *,
    player_ids: list[str],
    start_season: int,
    end_season: int,
    start_week: int | None = None,
    end_week: int | None = None,
    scoring_profile_id: str | None = DEFAULT_SCORING_PROFILE,
    league_type_id: str | None = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str | None = DEFAULT_ROSTER_FORMAT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Load aggregated actual outcomes from curated scoring-profile actuals."""

    player_ids = sorted({str(player_id) for player_id in player_ids if player_id})
    if not player_ids:
        return []
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql = f"""
    WITH base AS (
        SELECT
            player_id_internal,
            source_player_key,
            player_display_name AS display_name,
            position,
            team,
            season,
            week,
            scoring_profile_id,
            league_type_id,
            roster_format_id,
            total_fantasy_points AS actual_points,
            source_freshness_json,
            missing_data_flags
        FROM `{_table_id(client.project, dataset_id, "analytics_player_fantasy_points_by_profile")}`
        WHERE season BETWEEN @start_season AND @end_season
          AND (@start_week IS NULL OR season > @start_season OR week >= @start_week)
          AND (@end_week IS NULL OR season < @end_season OR week <= @end_week)
          AND (@scoring_profile_id IS NULL OR scoring_profile_id = @scoring_profile_id)
          AND (@league_type_id IS NULL OR league_type_id IS NULL OR league_type_id = @league_type_id)
          AND (@roster_format_id IS NULL OR roster_format_id IS NULL OR roster_format_id = @roster_format_id)
    ),
    aggregated AS (
        SELECT
            player_id_internal,
            ANY_VALUE(source_player_key) AS source_player_key,
            ANY_VALUE(display_name) AS display_name,
            ANY_VALUE(position) AS position,
            ARRAY_AGG(team IGNORE NULLS ORDER BY season DESC, week DESC LIMIT 1)[SAFE_OFFSET(0)] AS team,
            SUM(actual_points) AS actual_points,
            COUNT(*) AS actual_games,
            MAX(season) AS latest_season,
            MAX(week) AS latest_week,
            ARRAY_AGG(source_freshness_json IGNORE NULLS ORDER BY season DESC, week DESC LIMIT 1)[SAFE_OFFSET(0)] AS source_freshness_json,
            TO_JSON_STRING(ARRAY_CONCAT_AGG(IFNULL(JSON_EXTRACT_ARRAY(missing_data_flags), []))) AS missing_data_flags
        FROM base
        GROUP BY player_id_internal
    ),
    ranked AS (
        SELECT
            *,
            RANK() OVER (ORDER BY actual_points DESC) AS actual_rank_overall,
            RANK() OVER (PARTITION BY position ORDER BY actual_points DESC) AS actual_rank_position
        FROM aggregated
    )
    SELECT *
    FROM ranked
    WHERE player_id_internal IN UNNEST(@player_ids)
    """
    return _query_rows(
        client,
        sql,
        _job_config(
            [
                ("start_season", "INT64", int(start_season)),
                ("end_season", "INT64", int(end_season)),
                ("start_week", "INT64", _int_or_none(start_week)),
                ("end_week", "INT64", _int_or_none(end_week)),
                ("scoring_profile_id", "STRING", scoring_profile_id),
                ("league_type_id", "STRING", league_type_id),
                ("roster_format_id", "STRING", roster_format_id),
            ],
            arrays=[("player_ids", "STRING", player_ids)],
        ),
    )


def load_pigskin_snapshot_at_claim(
    *,
    claim: dict[str, Any],
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any] | None:
    """Load Pigskin projection/rank context from curated projection rankings."""

    player_id = claim.get("primary_player_id_internal")
    if not player_id:
        return _claim_rank_fallback(claim, "pigskin")
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    where = [
        "player_id_internal = @player_id_internal",
        "projection_horizon = @time_horizon",
        "(as_of_season = @season OR season = @season)",
    ]
    params: list[tuple[str, str, Any]] = [
        ("player_id_internal", "STRING", player_id),
        ("time_horizon", "STRING", claim.get("time_horizon") or "weekly"),
        ("season", "INT64", int(claim.get("season"))),
        ("limit", "INT64", 1),
    ]
    if claim.get("week") is not None:
        where.append("(as_of_week = @week OR week = @week)")
        params.append(("week", "INT64", int(claim["week"])))
    if claim.get("scoring_profile_id"):
        where.append("scoring_profile_id = @scoring_profile_id")
        params.append(("scoring_profile_id", "STRING", claim.get("scoring_profile_id")))
    if claim.get("league_type_id"):
        where.append("league_type_id = @league_type_id")
        params.append(("league_type_id", "STRING", claim.get("league_type_id")))
    if claim.get("roster_format_id"):
        where.append("roster_format_id = @roster_format_id")
        params.append(("roster_format_id", "STRING", claim.get("roster_format_id")))
    if claim.get("model_run_id_at_claim"):
        where.append("model_run_id = @model_run_id_at_claim")
        params.append(("model_run_id_at_claim", "STRING", claim.get("model_run_id_at_claim")))
    sql = f"""
    SELECT
        model_run_id,
        projected_points_or_value AS projected_points,
        rank_overall,
        rank_position,
        tier,
        confidence_score,
        risk_score,
        rank_source,
        created_at
    FROM `{_table_id(client.project, dataset_id, "projection_rankings_current")}`
    WHERE {" AND ".join(where)}
    ORDER BY created_at DESC
    LIMIT @limit
    """
    rows = _query_rows(client, sql, _job_config(params))
    if rows:
        return rows[0]
    return _claim_rank_fallback(claim, "pigskin")


def load_market_snapshot_at_claim(
    *,
    claim: dict[str, Any],
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any] | None:
    """Load market or consensus context from curated current baseline rows."""

    player_id = claim.get("primary_player_id_internal")
    if not player_id:
        return _claim_rank_fallback(claim, "market")
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    where = [
        "player_id_internal = @player_id_internal",
        "season = @season",
    ]
    params: list[tuple[str, str, Any]] = [
        ("player_id_internal", "STRING", player_id),
        ("season", "INT64", int(claim.get("season"))),
        ("limit", "INT64", 1),
    ]
    if claim.get("week") is not None:
        where.append("(week = @week OR week IS NULL)")
        params.append(("week", "INT64", int(claim["week"])))
    if claim.get("scoring_profile_id"):
        where.append("(scoring_profile_id = @scoring_profile_id OR scoring_profile_id IS NULL)")
        params.append(("scoring_profile_id", "STRING", claim.get("scoring_profile_id")))
    if claim.get("league_type_id"):
        where.append("(league_type_id = @league_type_id OR league_type_id IS NULL)")
        params.append(("league_type_id", "STRING", claim.get("league_type_id")))
    if claim.get("roster_format_id"):
        where.append("(roster_format_id = @roster_format_id OR roster_format_id IS NULL)")
        params.append(("roster_format_id", "STRING", claim.get("roster_format_id")))
    sql = f"""
    SELECT
        source_id,
        snapshot_id,
        projected_points,
        rank_overall,
        rank_position,
        market_value,
        adp,
        baseline_type,
        updated_at
    FROM `{_table_id(client.project, dataset_id, "market_consensus_baseline_current")}`
    WHERE {" AND ".join(where)}
    ORDER BY updated_at DESC
    LIMIT @limit
    """
    rows = _query_rows(client, sql, _job_config(params))
    if rows:
        return rows[0]
    return _claim_rank_fallback(claim, "market")


def grade_claim(
    *,
    claim: dict[str, Any],
    actual_outcome: dict[str, Any] | None,
    claim_grading_run_id: str,
    pigskin_snapshot: dict[str, Any] | None = None,
    market_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Grade one claim deterministically."""

    if not claim_grading_run_id:
        raise ValueError("claim_grading_run_id is required")

    flags: list[str] = []
    claim_type = str(claim.get("claim_type") or "").lower()
    time_horizon = str(claim.get("time_horizon") or "").lower()
    primary_player_id = claim.get("primary_player_id_internal")
    if not primary_player_id:
        flags.append("missing_primary_player_id")
    if time_horizon == "dynasty":
        flags.append("insufficient_dynasty_window")

    actual_points = _num(_value(actual_outcome, "actual_points"), None)
    actual_rank_overall = _int_or_none(_value(actual_outcome, "actual_rank_overall"))
    actual_rank_position = _int_or_none(_value(actual_outcome, "actual_rank_position"))
    position = claim.get("primary_position") or _value(actual_outcome, "position")
    if actual_points is None and actual_rank_overall is None:
        flags.append("missing_actual_outcome")

    claim_accuracy = None
    if "insufficient_dynasty_window" not in flags and "missing_actual_outcome" not in flags:
        claim_accuracy = _score_claim_accuracy(claim, actual_points, actual_rank_overall, actual_rank_position, position)
        if claim_accuracy is None:
            flags.append("missing_claim_grading_signal")

    pigskin_projection = _num(_value(pigskin_snapshot, "projected_points"), None)
    pigskin_rank = _int_or_none(_value(pigskin_snapshot, "rank_overall") or claim.get("pigskin_rank_at_claim"))
    market_projection = _num(_value(market_snapshot, "projected_points"), None)
    market_rank = _int_or_none(_value(market_snapshot, "rank_overall") or claim.get("market_rank_at_claim"))

    pigskin_accuracy = _score_baseline_accuracy(actual_points, actual_rank_overall, pigskin_projection, pigskin_rank)
    market_accuracy = _score_baseline_accuracy(actual_points, actual_rank_overall, market_projection, market_rank)
    if pigskin_accuracy is None:
        flags.append("missing_pigskin_snapshot")
    if market_accuracy is None:
        flags.append("missing_market_snapshot")

    confidence = _confidence_score(claim_accuracy, actual_outcome, pigskin_accuracy, market_accuracy, flags)
    verdict = assign_verdict(
        claim_accuracy_score=claim_accuracy,
        pigskin_accuracy_score=pigskin_accuracy,
        market_accuracy_score=market_accuracy,
        confidence_score=confidence,
        missing_data_flags=flags,
    )
    meatbag_delta = _delta(claim_accuracy, pigskin_accuracy)
    model_delta = _delta(pigskin_accuracy, market_accuracy)
    grade_json = {
        "grading_version": DEFAULT_GRADING_VERSION,
        "claim_type": claim_type,
        "claim_direction": claim.get("claim_direction"),
        "scoring_logic": _scoring_logic_label(claim_type),
    }
    evidence_json = {
        "claim_text": claim.get("claim_text"),
        "primary_player": claim.get("primary_display_name"),
        "actual": _compact_actual(actual_outcome),
        "pigskin_snapshot": _compact_snapshot(pigskin_snapshot),
        "market_snapshot": _compact_snapshot(market_snapshot),
    }
    return {
        "claim_grading_run_id": claim_grading_run_id,
        "claim_id": claim["claim_id"],
        "source_id": claim.get("source_id"),
        "source_name": claim.get("source_name"),
        "_source_type": claim.get("claim_source_type"),
        "claim_type": claim.get("claim_type"),
        "claim_direction": claim.get("claim_direction"),
        "time_horizon": claim.get("time_horizon"),
        "primary_player_id_internal": primary_player_id,
        "season": int(claim.get("season")),
        "week": _int_or_none(claim.get("week")),
        "evaluation_window_id": claim.get("evaluation_window_id"),
        "actual_points": _round(actual_points),
        "actual_rank_overall": actual_rank_overall,
        "actual_rank_position": actual_rank_position,
        "pigskin_projection_at_claim": _round(pigskin_projection),
        "pigskin_rank_at_claim": pigskin_rank,
        "market_projection_at_claim": _round(market_projection),
        "market_rank_at_claim": market_rank,
        "claim_accuracy_score": _round(claim_accuracy),
        "pigskin_accuracy_score": _round(pigskin_accuracy),
        "market_accuracy_score": _round(market_accuracy),
        "meatbag_delta": _round(meatbag_delta),
        "model_delta": _round(model_delta),
        "verdict": verdict,
        "confidence_score": _round(confidence),
        "grade_json": _json_dumps(grade_json),
        "evidence_json": _json_dumps(evidence_json),
        "missing_data_flags": _json_dumps(sorted(set(flags))),
        "created_at": _utc_timestamp(),
    }


def assign_verdict(
    *,
    claim_accuracy_score: float | None,
    pigskin_accuracy_score: float | None = None,
    market_accuracy_score: float | None = None,
    confidence_score: float | None = None,
    missing_data_flags: list[str] | None = None,
) -> str:
    """Assign the claim verdict from deterministic scores."""

    flags = set(missing_data_flags or [])
    if claim_accuracy_score is None or "missing_actual_outcome" in flags or "insufficient_dynasty_window" in flags:
        return "inconclusive"

    baselines = [score for score in (pigskin_accuracy_score, market_accuracy_score) if score is not None]
    best_baseline = max(baselines) if baselines else None
    worst_baseline = min(baselines) if baselines else None
    confidence = 0.0 if confidence_score is None else confidence_score
    score = claim_accuracy_score

    if score >= 0.82 and worst_baseline is not None and worst_baseline <= 0.55:
        return "galaxy_brain"
    if score <= 0.25 and best_baseline is not None and best_baseline >= 0.65:
        return "fraud"
    if score >= 0.70 and confidence < 0.55:
        return "lucky"
    if score >= 0.65:
        return "good_take"
    if score <= 0.35:
        return "wrong"
    return "inconclusive"


def build_claim_source_scorecards(
    grades: list[dict[str, Any]],
    *,
    claim_grading_run_id: str,
    season: int | None = None,
    week: int | None = None,
) -> list[dict[str, Any]]:
    """Aggregate claim grades into source-level accountability scorecards."""

    if not claim_grading_run_id:
        raise ValueError("claim_grading_run_id is required")
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in grades:
        grouped.setdefault(str(row.get("source_id")), []).append(row)

    now = _utc_timestamp()
    scorecards = []
    for source_id, rows in sorted(grouped.items()):
        graded_rows = [row for row in rows if row.get("verdict") != "inconclusive"]
        pigskin_comparable = [row for row in rows if row.get("pigskin_accuracy_score") is not None and row.get("claim_accuracy_score") is not None]
        market_comparable = [row for row in rows if row.get("market_accuracy_score") is not None and row.get("claim_accuracy_score") is not None]
        source_name = rows[0].get("source_name") or source_id
        source_type = rows[0].get("_source_type") or rows[0].get("source_type")
        scorecard_json = {
            "verdict_counts": _verdict_counts(rows),
            "graded_claim_ids": [row.get("claim_id") for row in graded_rows],
        }
        scorecards.append({
            "claim_grading_run_id": claim_grading_run_id,
            "source_id": source_id,
            "source_name": source_name,
            "source_type": source_type,
            "season": _int_or_none(season),
            "week": _int_or_none(week),
            "claim_count": len(rows),
            "graded_count": len(graded_rows),
            "average_claim_accuracy": _round(_mean(row.get("claim_accuracy_score") for row in graded_rows)),
            "average_meatbag_delta": _round(_mean(row.get("meatbag_delta") for row in rows if row.get("meatbag_delta") is not None)),
            "pigskin_win_rate": _round(_win_rate(pigskin_comparable, "pigskin_accuracy_score")),
            "market_win_rate": _round(_win_rate(market_comparable, "market_accuracy_score")),
            "good_take_count": sum(1 for row in rows if row.get("verdict") == "good_take"),
            "wrong_count": sum(1 for row in rows if row.get("verdict") == "wrong"),
            "fraud_count": sum(1 for row in rows if row.get("verdict") == "fraud"),
            "galaxy_brain_count": sum(1 for row in rows if row.get("verdict") == "galaxy_brain"),
            "scorecard_json": _json_dumps(scorecard_json),
            "created_at": now,
        })
    return scorecards


def write_claim_grades(
    *,
    grades: list[dict[str, Any]],
    scorecards: list[dict[str, Any]],
    claim_grading_run_id: str,
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Write claim grades and scorecards."""

    if not claim_grading_run_id:
        raise ValueError("claim_grading_run_id is required")
    _ensure_run_id(grades, "grades", claim_grading_run_id)
    _ensure_run_id(scorecards, "scorecards", claim_grading_run_id)
    writable_grades = [_claim_grade_table_row(row) for row in grades]
    if dry_run:
        return {"dry_run": True, "grade_count": len(grades), "scorecard_count": len(scorecards)}

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    _insert_rows(client, dataset_id, GRADES_TABLE, writable_grades)
    _insert_rows(client, dataset_id, SCORECARDS_TABLE, scorecards)
    _mark_grading_run_complete(client, dataset_id, claim_grading_run_id)
    return {"dry_run": False, "grade_count": len(grades), "scorecard_count": len(scorecards)}


def _claim_grade_table_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if not key.startswith("_")}


def run_claim_grading(
    *,
    claim_id: str | None = None,
    season: int | None = None,
    week: int | None = None,
    model_run_id: str | None = None,
    scoring_profile_id: str | None = DEFAULT_SCORING_PROFILE,
    league_type_id: str | None = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str | None = DEFAULT_ROSTER_FORMAT,
    claims: list[dict[str, Any]] | None = None,
    actuals_by_claim_id: dict[str, dict[str, Any] | None] | None = None,
    pigskin_by_claim_id: dict[str, dict[str, Any] | None] | None = None,
    market_by_claim_id: dict[str, dict[str, Any] | None] | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run deterministic claim grading."""

    client = client or (None if dry_run and claims is not None else get_bigquery_client())
    dataset_id = dataset_id or get_bigquery_dataset()
    run = create_claim_grading_run(
        season=season,
        week=week,
        model_run_id=model_run_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        status="running",
        client=client,
        dataset_id=dataset_id,
        dry_run=dry_run,
    )
    run_id = run["claim_grading_run_id"]
    claims = claims if claims is not None else load_claims_ready_to_grade(
        claim_id=claim_id,
        season=season,
        week=week,
        client=client,
        dataset_id=dataset_id,
    )
    actuals_by_claim_id = actuals_by_claim_id or {}
    pigskin_by_claim_id = pigskin_by_claim_id or {}
    market_by_claim_id = market_by_claim_id or {}

    grades = []
    for claim in claims:
        hydrated = _hydrate_claim_defaults(claim, scoring_profile_id, league_type_id, roster_format_id)
        actual = actuals_by_claim_id.get(hydrated["claim_id"])
        if hydrated["claim_id"] not in actuals_by_claim_id:
            actual = _load_primary_actual(hydrated, client=client, dataset_id=dataset_id)
        pigskin = pigskin_by_claim_id.get(hydrated["claim_id"])
        if hydrated["claim_id"] not in pigskin_by_claim_id:
            pigskin = load_pigskin_snapshot_at_claim(claim=hydrated, client=client, dataset_id=dataset_id)
        market = market_by_claim_id.get(hydrated["claim_id"])
        if hydrated["claim_id"] not in market_by_claim_id:
            market = load_market_snapshot_at_claim(claim=hydrated, client=client, dataset_id=dataset_id)
        grades.append(grade_claim(
            claim=hydrated,
            actual_outcome=actual,
            pigskin_snapshot=pigskin,
            market_snapshot=market,
            claim_grading_run_id=run_id,
        ))

    scorecards = build_claim_source_scorecards(
        grades,
        claim_grading_run_id=run_id,
        season=season,
        week=week,
    )
    write_result = write_claim_grades(
        grades=grades,
        scorecards=scorecards,
        claim_grading_run_id=run_id,
        client=client,
        dataset_id=dataset_id,
        dry_run=dry_run,
    )
    if dry_run:
        run["status"] = "completed"
        run["completed_at"] = _utc_timestamp()
    return {
        "dry_run": dry_run,
        "run": run,
        "claim_count": len(claims),
        "grade_count": len(grades),
        "scorecard_count": len(scorecards),
        "grades": grades,
        "scorecards": scorecards,
        "write_result": write_result,
    }


def _load_primary_actual(claim: dict[str, Any], *, client: Any | None, dataset_id: str | None) -> dict[str, Any] | None:
    player_id = claim.get("primary_player_id_internal")
    if not player_id:
        return None
    rows = load_actual_outcomes(
        player_ids=[player_id],
        start_season=int(claim.get("start_season") or claim.get("season")),
        start_week=_int_or_none(claim.get("start_week")),
        end_season=int(claim.get("end_season") or claim.get("season")),
        end_week=_int_or_none(claim.get("end_week")),
        scoring_profile_id=claim.get("scoring_profile_id") or DEFAULT_SCORING_PROFILE,
        league_type_id=claim.get("league_type_id") or DEFAULT_LEAGUE_TYPE,
        roster_format_id=claim.get("roster_format_id") or DEFAULT_ROSTER_FORMAT,
        client=client,
        dataset_id=dataset_id,
    )
    return rows[0] if rows else None


def _hydrate_claim_defaults(
    claim: dict[str, Any],
    scoring_profile_id: str | None,
    league_type_id: str | None,
    roster_format_id: str | None,
) -> dict[str, Any]:
    row = dict(claim)
    row["scoring_profile_id"] = row.get("scoring_profile_id") or scoring_profile_id or DEFAULT_SCORING_PROFILE
    row["league_type_id"] = row.get("league_type_id") or league_type_id or DEFAULT_LEAGUE_TYPE
    row["roster_format_id"] = row.get("roster_format_id") or roster_format_id or DEFAULT_ROSTER_FORMAT
    row["start_season"] = row.get("start_season") or row.get("season")
    row["end_season"] = row.get("end_season") or row.get("season")
    if not row.get("evaluation_window_id"):
        row["evaluation_window_id"] = f"{row.get('claim_id')}:adhoc"
    return row


def _score_claim_accuracy(
    claim: dict[str, Any],
    actual_points: float | None,
    actual_rank_overall: int | None,
    actual_rank_position: int | None,
    position: Any,
) -> float | None:
    claim_type = str(claim.get("claim_type") or "").lower()
    direction = str(claim.get("claim_direction") or "").lower()
    if claim_type == "ranking":
        claimed_rank = _int_or_none(claim.get("player_claimed_rank") or claim.get("claimed_rank"))
        actual_rank = actual_rank_overall or actual_rank_position
        if claimed_rank is None or actual_rank is None:
            return None
        tolerance = max(12.0, claimed_rank * 0.5)
        return _clamp(1.0 - (abs(claimed_rank - actual_rank) / tolerance))
    if claim_type == "dynasty":
        return None

    positive_score = _positive_outcome_score(actual_points, actual_rank_position, position)
    if positive_score is None:
        return None
    negative_types = {"sit", "sell", "bust", "fraud"}
    negative_directions = {"negative", "sit", "sell"}
    if claim_type in negative_types or direction in negative_directions:
        return _clamp(1.0 - positive_score)
    return positive_score


def _positive_outcome_score(
    actual_points: float | None,
    actual_rank_position: int | None,
    position: Any,
) -> float | None:
    if actual_points is None and actual_rank_position is None:
        return None
    boom, bust = _thresholds(position)
    rank_cutoff = _rank_cutoff(position)
    point_score = None
    if actual_points is not None:
        if actual_points >= boom:
            point_score = 1.0
        elif actual_points <= bust:
            point_score = 0.0
        else:
            point_score = (actual_points - bust) / (boom - bust)
    rank_score = None
    if actual_rank_position is not None:
        if actual_rank_position <= rank_cutoff:
            rank_score = 1.0
        elif actual_rank_position <= rank_cutoff * 1.5:
            rank_score = 0.65
        elif actual_rank_position <= rank_cutoff * 2:
            rank_score = 0.40
        else:
            rank_score = 0.10
    values = [value for value in (point_score, rank_score) if value is not None]
    return _clamp(sum(values) / len(values)) if values else None


def _score_baseline_accuracy(
    actual_points: float | None,
    actual_rank_overall: int | None,
    projected_points: float | None,
    projected_rank: int | None,
) -> float | None:
    scores = []
    if actual_points is not None and projected_points is not None:
        denominator = max(10.0, abs(actual_points), abs(projected_points))
        scores.append(_clamp(1.0 - abs(actual_points - projected_points) / denominator))
    if actual_rank_overall is not None and projected_rank is not None:
        scores.append(_clamp(1.0 - abs(actual_rank_overall - projected_rank) / 75.0))
    if not scores:
        return None
    return sum(scores) / len(scores)


def _confidence_score(
    claim_accuracy: float | None,
    actual_outcome: dict[str, Any] | None,
    pigskin_accuracy: float | None,
    market_accuracy: float | None,
    flags: list[str],
) -> float:
    if claim_accuracy is None:
        return 0.0
    confidence = 0.55
    if actual_outcome:
        confidence += 0.20
    if pigskin_accuracy is not None:
        confidence += 0.10
    if market_accuracy is not None:
        confidence += 0.10
    if flags:
        confidence -= min(0.30, len(set(flags)) * 0.08)
    return _clamp(confidence)


def _thresholds(position: Any) -> tuple[float, float]:
    position = str(position or "").upper()
    boom = {"QB": 24.0, "RB": 20.0, "WR": 20.0, "TE": 15.0}.get(position, 18.0)
    bust = {"QB": 12.0, "RB": 8.0, "WR": 8.0, "TE": 6.0}.get(position, 8.0)
    return boom, bust


def _rank_cutoff(position: Any) -> int:
    return {"QB": 12, "RB": 24, "WR": 36, "TE": 12}.get(str(position or "").upper(), 36)


def _scoring_logic_label(claim_type: str) -> str:
    return {
        "start": "positive_outcome_threshold",
        "sit": "negative_outcome_threshold",
        "breakout": "positive_outcome_threshold",
        "buy": "positive_outcome_threshold",
        "sell": "negative_outcome_threshold",
        "bust": "negative_outcome_threshold",
        "fraud": "negative_outcome_threshold",
        "ranking": "claimed_rank_error",
        "dynasty": "placeholder_until_multi_year_window",
    }.get(claim_type, "directional_outcome_threshold")


def _claim_rank_fallback(claim: dict[str, Any], source: str) -> dict[str, Any] | None:
    rank = _int_or_none(claim.get(f"{source}_rank_at_claim"))
    if rank is None:
        return None
    return {"rank_overall": rank, "rank_source": f"{source}_rank_at_claim"}


def _compact_actual(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    return {
        "actual_points": _num(row.get("actual_points"), None),
        "actual_rank_overall": _int_or_none(row.get("actual_rank_overall")),
        "actual_rank_position": _int_or_none(row.get("actual_rank_position")),
        "position": row.get("position"),
    }


def _compact_snapshot(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    return {
        "projected_points": _num(row.get("projected_points"), None),
        "rank_overall": _int_or_none(row.get("rank_overall")),
        "rank_position": _int_or_none(row.get("rank_position")),
        "source_id": row.get("source_id"),
        "model_run_id": row.get("model_run_id"),
    }


def _verdict_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {verdict: sum(1 for row in rows if row.get("verdict") == verdict) for verdict in sorted(ALLOWED_VERDICTS)}


def _win_rate(rows: list[dict[str, Any]], baseline_field: str) -> float | None:
    if not rows:
        return None
    wins = sum(1 for row in rows if _num(row.get(baseline_field), -1.0) > _num(row.get("claim_accuracy_score"), -1.0))
    return wins / len(rows)


def _ensure_run_id(rows: list[dict[str, Any]], label: str, claim_grading_run_id: str) -> None:
    missing = [
        index for index, row in enumerate(rows)
        if row.get("claim_grading_run_id") != claim_grading_run_id
    ]
    if missing:
        raise ValueError(f"{label} missing claim_grading_run_id at row indexes {missing[:5]}")


def _mark_grading_run_complete(client: Any, dataset_id: str, claim_grading_run_id: str) -> None:
    sql = f"""
    UPDATE `{_table_id(client.project, dataset_id, RUNS_TABLE)}`
    SET status = 'completed',
        completed_at = CURRENT_TIMESTAMP()
    WHERE claim_grading_run_id = @claim_grading_run_id
    """
    client.query(sql, job_config=_job_config([
        ("claim_grading_run_id", "STRING", claim_grading_run_id),
    ])).result()


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


def _job_config(
    params: list[tuple[str, str, Any]],
    *,
    arrays: list[tuple[str, str, list[Any]]] | None = None,
) -> bigquery.QueryJobConfig:
    query_parameters = [
        bigquery.ScalarQueryParameter(name, param_type, value)
        for name, param_type, value in params
    ]
    for name, param_type, values in arrays or []:
        query_parameters.append(bigquery.ArrayQueryParameter(name, param_type, values))
    return bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=query_parameters,
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


def _validate_choice(value: str, allowed: set[str], label: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized not in allowed:
        raise ValueError(f"Invalid {label}: {value!r}")
    return normalized


def _value(row: dict[str, Any] | None, key: str) -> Any:
    if not row:
        return None
    return row.get(key)


def _generate_run_id(grading_version: str, season: int | None, week: int | None) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    season_part = str(season) if season is not None else "all"
    week_part = f"w{week}" if week is not None else "all"
    return f"{grading_version}-{season_part}-{week_part}-{stamp}-{uuid.uuid4().hex[:8]}"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _num(value: Any, default: float | None = 0.0) -> float | None:
    if value in (None, ""):
        return default
    try:
        parsed = float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return default
    if math.isnan(parsed) or math.isinf(parsed):
        return default
    return parsed


def _int_or_none(value: Any) -> int | None:
    parsed = _num(value, None)
    if parsed is None:
        return None
    return int(parsed)


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


def _delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return left - right


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic Meatbag Claim Ledger grading.")
    parser.add_argument("--claim-id")
    parser.add_argument("--season", type=int)
    parser.add_argument("--week", type=int)
    parser.add_argument("--model-run-id")
    parser.add_argument("--scoring-profile", default=DEFAULT_SCORING_PROFILE)
    parser.add_argument("--league-type", default=DEFAULT_LEAGUE_TYPE)
    parser.add_argument("--roster-format", default=DEFAULT_ROSTER_FORMAT)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    result = run_claim_grading(
        claim_id=args.claim_id,
        season=args.season,
        week=args.week,
        model_run_id=args.model_run_id,
        scoring_profile_id=args.scoring_profile,
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
