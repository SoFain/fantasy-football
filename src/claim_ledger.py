"""Manual Meatbag Claim Ledger helpers.

This module is intentionally manual-entry first. It does not scrape media,
call LLMs, or fetch external pages.
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
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("CLAIM_LEDGER_MAX_BYTES_BILLED", "1000000000"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")

CLAIM_SOURCES_TABLE = "claim_sources"
FANTASY_CLAIMS_TABLE = "fantasy_claims"
CLAIM_PLAYERS_TABLE = "fantasy_claim_players"
EVALUATION_WINDOWS_TABLE = "claim_evaluation_windows"

ALLOWED_SOURCE_TYPES = {"youtube", "tv", "podcast", "article", "internal_pigskin", "manual"}
ALLOWED_CLAIM_TYPES = {
    "start",
    "sit",
    "buy",
    "sell",
    "trade",
    "breakout",
    "bust",
    "fraud",
    "ranking",
    "dynasty",
    "streamer",
    "waiver",
    "projection",
}
ALLOWED_DIRECTIONS = {"positive", "negative", "neutral", "start", "sit", "buy", "sell"}
ALLOWED_HORIZONS = {"weekly", "ros", "season", "dynasty", "multi_year"}
ALLOWED_REVIEW_STATUSES = {"draft", "reviewed", "ready_to_grade", "graded", "archived", "correction"}
LOCKED_STATUSES = {"graded"}


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def register_claim_source(
    *,
    source_id: str,
    source_name: str,
    source_type: str,
    person_name: str | None = None,
    show_name: str | None = None,
    channel_name: str | None = None,
    source_url: str | None = None,
    notes: str | None = None,
    active: bool = True,
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Register or update a manual claim source."""

    source_id = _safe_id(source_id, "source ID")
    source_type = _validate_choice(source_type, ALLOWED_SOURCE_TYPES, "source_type")
    now = _utc_timestamp()
    row = {
        "source_id": source_id,
        "source_name": source_name,
        "source_type": source_type,
        "person_name": person_name,
        "show_name": show_name,
        "channel_name": channel_name,
        "source_url": source_url,
        "notes": notes,
        "active": bool(active),
        "created_at": now,
        "updated_at": now,
    }
    if dry_run:
        return {"dry_run": True, "source": row}

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql = f"""
    MERGE `{_table_id(client.project, dataset_id, CLAIM_SOURCES_TABLE)}` target
    USING (
        SELECT
            @source_id AS source_id,
            @source_name AS source_name,
            @source_type AS source_type,
            @person_name AS person_name,
            @show_name AS show_name,
            @channel_name AS channel_name,
            @source_url AS source_url,
            @notes AS notes,
            @active AS active
    ) source
    ON target.source_id = source.source_id
    WHEN MATCHED THEN
        UPDATE SET
            source_name = source.source_name,
            source_type = source.source_type,
            person_name = source.person_name,
            show_name = source.show_name,
            channel_name = source.channel_name,
            source_url = source.source_url,
            notes = source.notes,
            active = source.active,
            updated_at = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN
        INSERT (
            source_id,
            source_name,
            source_type,
            person_name,
            show_name,
            channel_name,
            source_url,
            notes,
            active,
            created_at,
            updated_at
        )
        VALUES (
            source.source_id,
            source.source_name,
            source.source_type,
            source.person_name,
            source.show_name,
            source.channel_name,
            source.source_url,
            source.notes,
            source.active,
            CURRENT_TIMESTAMP(),
            CURRENT_TIMESTAMP()
        )
    """
    client.query(sql, job_config=_job_config([
        ("source_id", "STRING", source_id),
        ("source_name", "STRING", source_name),
        ("source_type", "STRING", source_type),
        ("person_name", "STRING", person_name),
        ("show_name", "STRING", show_name),
        ("channel_name", "STRING", channel_name),
        ("source_url", "STRING", source_url),
        ("notes", "STRING", notes),
        ("active", "BOOL", bool(active)),
    ])).result()
    return {"dry_run": False, "source": row}


def create_fantasy_claim(
    *,
    source_id: str,
    claim_text: str,
    claim_type: str,
    season: int,
    week: int | None = None,
    claim_id: str | None = None,
    claim_source_type: str | None = None,
    source_name: str | None = None,
    person_name: str | None = None,
    episode_or_video_title: str | None = None,
    source_url: str | None = None,
    published_at: datetime | str | None = None,
    claimed_at: datetime | str | None = None,
    entered_by: str | None = None,
    claim_direction: str | None = None,
    time_horizon: str = "weekly",
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    players: list[str | dict[str, Any]] | None = None,
    teams: list[str] | None = None,
    claimed_rank: int | None = None,
    claimed_projection: float | None = None,
    claimed_value: float | None = None,
    confidence_claimed: float | None = None,
    model_run_id_at_claim: str | None = None,
    pigskin_rank_at_claim: int | None = None,
    market_rank_at_claim: int | None = None,
    context: dict[str, Any] | None = None,
    review_status: str = "draft",
    identity_rows: list[dict[str, Any]] | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Create a manual fantasy claim and optional player rows."""

    source_id = _safe_id(source_id, "source ID")
    claim_type = _validate_choice(claim_type, ALLOWED_CLAIM_TYPES, "claim_type")
    time_horizon = _validate_choice(time_horizon, ALLOWED_HORIZONS, "time_horizon")
    review_status = _validate_choice(review_status, ALLOWED_REVIEW_STATUSES, "review_status")
    claim_direction = _optional_choice(claim_direction, ALLOWED_DIRECTIONS, "claim_direction")
    claim_id = claim_id or _generate_claim_id(source_id, claim_type, season, week)
    now = _utc_timestamp()

    if not dry_run:
        client = client or get_bigquery_client()
        dataset_id = dataset_id or get_bigquery_dataset()
    if not dry_run and source_name is None:
        source_row = _load_claim_source(client, dataset_id, source_id)
        if source_row:
            source_name = source_row.get("source_name")
            claim_source_type = claim_source_type or source_row.get("source_type")
            person_name = person_name or source_row.get("person_name")
            source_url = source_url or source_row.get("source_url")

    claim_source_type = _validate_choice(claim_source_type or "manual", ALLOWED_SOURCE_TYPES, "claim_source_type")
    source_name = source_name or source_id
    resolved = resolve_claim_players(
        players or [],
        identity_rows=identity_rows,
        client=client if not dry_run else None,
        dataset_id=dataset_id,
    )
    player_rows = _claim_player_rows(
        claim_id=claim_id,
        resolved_players=resolved["resolved_players"],
        claimed_rank=claimed_rank,
        claimed_projection=claimed_projection,
        claimed_value=claimed_value,
    )
    player_ids = [
        row["player_id_internal"]
        for row in player_rows
        if row.get("player_id_internal")
    ]
    team_ids = [str(team).strip().upper() for team in teams or [] if str(team).strip()]
    context_payload = dict(context or {})
    if not dry_run and player_ids:
        rank_snapshot = _snapshot_rank_context(
            client=client,
            dataset_id=dataset_id or get_bigquery_dataset(),
            player_id_internal=player_ids[0],
            season=season,
            week=week,
            time_horizon=time_horizon,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            model_run_id_at_claim=model_run_id_at_claim,
        )
        if rank_snapshot:
            context_payload.setdefault("rank_snapshot", rank_snapshot)
            if pigskin_rank_at_claim is None:
                pigskin_rank_at_claim = rank_snapshot.get("pigskin_rank_at_claim")
            if market_rank_at_claim is None:
                market_rank_at_claim = rank_snapshot.get("market_rank_at_claim")
    row = {
        "claim_id": claim_id,
        "source_id": source_id,
        "claim_source_type": claim_source_type,
        "source_name": source_name,
        "person_name": person_name,
        "episode_or_video_title": episode_or_video_title,
        "source_url": source_url,
        "published_at": _timestamp_string(published_at) if published_at else None,
        "claimed_at": _timestamp_string(claimed_at),
        "entered_by": entered_by,
        "claim_text": claim_text,
        "claim_type": claim_type,
        "claim_direction": claim_direction,
        "time_horizon": time_horizon,
        "season": int(season),
        "week": _int_or_none(week),
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "player_ids_json": _json_dumps(player_ids),
        "team_ids_json": _json_dumps(team_ids),
        "claimed_rank": _int_or_none(claimed_rank),
        "claimed_projection": _num(claimed_projection, None),
        "claimed_value": _num(claimed_value, None),
        "confidence_claimed": _num(confidence_claimed, None),
        "model_run_id_at_claim": model_run_id_at_claim,
        "pigskin_rank_at_claim": _int_or_none(pigskin_rank_at_claim),
        "market_rank_at_claim": _int_or_none(market_rank_at_claim),
        "context_json": _json_dumps(context_payload),
        "review_status": review_status,
        "created_at": now,
        "updated_at": now,
    }
    _validate_claim_for_status(row, player_rows, review_status)
    window = infer_evaluation_window(
        claim_id=claim_id,
        time_horizon=time_horizon,
        season=season,
        week=week,
    )
    result = {
        "dry_run": dry_run,
        "claim": row,
        "players": player_rows,
        "evaluation_window": window,
        "disambiguation": resolved["disambiguation"],
    }
    if dry_run:
        return result

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    _insert_rows(client, dataset_id, FANTASY_CLAIMS_TABLE, [row])
    _insert_rows(client, dataset_id, CLAIM_PLAYERS_TABLE, player_rows)
    _insert_rows(client, dataset_id, EVALUATION_WINDOWS_TABLE, [window])
    return result


def add_claim_players(
    *,
    claim_id: str,
    players: list[str | dict[str, Any]],
    current_claim: dict[str, Any] | None = None,
    identity_rows: list[dict[str, Any]] | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Add player rows to an existing claim."""

    if current_claim is None and not dry_run:
        client = client or get_bigquery_client()
        dataset_id = dataset_id or get_bigquery_dataset()
        current_claim = get_claim(claim_id, client=client, dataset_id=dataset_id)
    if current_claim and str(current_claim.get("review_status") or "") in LOCKED_STATUSES:
        raise ValueError("Graded claims are immutable unless moved to correction status")

    resolved = resolve_claim_players(
        players,
        identity_rows=identity_rows,
        client=client if not dry_run else None,
        dataset_id=dataset_id,
    )
    rows = _claim_player_rows(claim_id=claim_id, resolved_players=resolved["resolved_players"])
    if dry_run:
        return {"dry_run": True, "players": rows, "disambiguation": resolved["disambiguation"]}

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    _insert_rows(client, dataset_id, CLAIM_PLAYERS_TABLE, rows)
    return {"dry_run": False, "players": rows, "disambiguation": resolved["disambiguation"]}


def resolve_claim_players(
    players: list[str | dict[str, Any]],
    *,
    identity_rows: list[dict[str, Any]] | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    """Resolve manually entered claim players against player_identity_bridge."""

    if identity_rows is None:
        identity_rows = _load_identity_rows(client, dataset_id) if client is not None else []
    indexes = _build_identity_indexes(identity_rows)
    resolved_players: list[dict[str, Any]] = []
    disambiguation: list[dict[str, Any]] = []

    for raw_player in players:
        player = _normalize_player_input(raw_player)
        matches, method = _find_identity_matches(player, indexes)
        if len(matches) == 1:
            resolved_players.append(_resolved_player_row(player, matches[0], method))
        elif len(matches) > 1:
            disambiguation.append({
                "input": player,
                "match_method": method,
                "candidates": [_identity_candidate(row) for row in matches],
            })
            unresolved = _resolved_player_row(player, None, "ambiguous")
            _add_missing_flag(unresolved, "ambiguous_player_identity")
            resolved_players.append(unresolved)
        else:
            unresolved = _resolved_player_row(player, None, "unmatched")
            _add_missing_flag(unresolved, "missing_player_id_internal")
            resolved_players.append(unresolved)
    return {"resolved_players": resolved_players, "disambiguation": disambiguation}


def infer_evaluation_window(
    *,
    claim_id: str,
    time_horizon: str,
    season: int,
    week: int | None = None,
) -> dict[str, Any]:
    """Infer the default evaluation window for a claim."""

    time_horizon = _validate_choice(time_horizon, ALLOWED_HORIZONS, "time_horizon")
    start_week = _int_or_none(week)
    if time_horizon == "weekly":
        end_season = int(season)
        end_week = start_week
    elif time_horizon in {"ros", "season"}:
        end_season = int(season)
        end_week = 18
        start_week = start_week or (1 if time_horizon == "season" else None)
    elif time_horizon == "dynasty":
        end_season = int(season) + 2
        end_week = None
        start_week = start_week or None
    else:
        end_season = int(season) + 1
        end_week = None
        start_week = start_week or None

    now = _utc_timestamp()
    return {
        "claim_id": claim_id,
        "evaluation_window_id": _evaluation_window_id(claim_id, time_horizon, season, start_week, end_season, end_week),
        "time_horizon": time_horizon,
        "start_season": int(season),
        "start_week": start_week,
        "end_season": end_season,
        "end_week": end_week,
        "evaluation_status": "pending",
        "created_at": now,
        "updated_at": now,
    }


def get_claim(
    claim_id: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any] | None:
    """Fetch one claim by ID."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql = f"""
    SELECT *
    FROM `{_table_id(client.project, dataset_id, FANTASY_CLAIMS_TABLE)}`
    WHERE claim_id = @claim_id
    LIMIT 1
    """
    rows = _query_rows(client, sql, _job_config([("claim_id", "STRING", claim_id)]))
    return rows[0] if rows else None


def search_claims(
    *,
    source_id: str | None = None,
    player_id_internal: str | None = None,
    review_status: str | None = None,
    claim_type: str | None = None,
    season: int | None = None,
    limit: int = 100,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Search claims using bounded, parameterized filters."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    where = ["1 = 1"]
    params: list[tuple[str, str, Any]] = [("limit", "INT64", max(1, min(int(limit), 500)))]
    if source_id:
        where.append("claims.source_id = @source_id")
        params.append(("source_id", "STRING", _safe_id(source_id, "source ID")))
    if review_status:
        where.append("claims.review_status = @review_status")
        params.append(("review_status", "STRING", _validate_choice(review_status, ALLOWED_REVIEW_STATUSES, "review_status")))
    if claim_type:
        where.append("claims.claim_type = @claim_type")
        params.append(("claim_type", "STRING", _validate_choice(claim_type, ALLOWED_CLAIM_TYPES, "claim_type")))
    if season is not None:
        where.append("claims.season = @season")
        params.append(("season", "INT64", int(season)))
    join_clause = ""
    if player_id_internal:
        join_clause = f"""
        JOIN `{_table_id(client.project, dataset_id, CLAIM_PLAYERS_TABLE)}` players
            ON claims.claim_id = players.claim_id
        """
        where.append("players.player_id_internal = @player_id_internal")
        params.append(("player_id_internal", "STRING", player_id_internal))

    sql = f"""
    SELECT DISTINCT claims.*
    FROM `{_table_id(client.project, dataset_id, FANTASY_CLAIMS_TABLE)}` claims
    {join_clause}
    WHERE {" AND ".join(where)}
    ORDER BY claimed_at DESC
    LIMIT @limit
    """
    return _query_rows(client, sql, _job_config(params))


def update_claim_status(
    claim_id: str,
    new_status: str,
    *,
    current_claim: dict[str, Any] | None = None,
    claim_players: list[dict[str, Any]] | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Update claim review status with graded-claim protection."""

    new_status = _validate_choice(new_status, ALLOWED_REVIEW_STATUSES, "review_status")
    if current_claim is None:
        if dry_run:
            raise ValueError("current_claim is required for dry-run status updates")
        current_claim = get_claim(claim_id, client=client, dataset_id=dataset_id)
    if not current_claim:
        raise ValueError(f"Claim not found: {claim_id}")
    current_status = str(current_claim.get("review_status") or "")
    if current_status in LOCKED_STATUSES and new_status != "correction":
        raise ValueError("Graded claims are immutable unless moved to correction status")

    _validate_claim_for_status(current_claim, claim_players or [], new_status)
    if dry_run:
        return {"dry_run": True, "claim_id": claim_id, "review_status": new_status}

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql = f"""
    UPDATE `{_table_id(client.project, dataset_id, FANTASY_CLAIMS_TABLE)}`
    SET review_status = @review_status,
        updated_at = CURRENT_TIMESTAMP()
    WHERE claim_id = @claim_id
    """
    client.query(sql, job_config=_job_config([
        ("review_status", "STRING", new_status),
        ("claim_id", "STRING", claim_id),
    ])).result()
    return {"dry_run": False, "claim_id": claim_id, "review_status": new_status}


def get_claims_ready_to_grade(
    *,
    season: int | None = None,
    week: int | None = None,
    limit: int = 100,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return claims marked ready to grade, optionally bounded by season/week."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    where = ["claims.review_status = 'ready_to_grade'"]
    params: list[tuple[str, str, Any]] = [("limit", "INT64", max(1, min(int(limit), 500)))]
    if season is not None:
        where.append("windows.end_season <= @season")
        params.append(("season", "INT64", int(season)))
    if week is not None:
        where.append("(windows.end_week IS NULL OR windows.end_week <= @week)")
        params.append(("week", "INT64", int(week)))

    sql = f"""
    SELECT claims.*
    FROM `{_table_id(client.project, dataset_id, FANTASY_CLAIMS_TABLE)}` claims
    JOIN `{_table_id(client.project, dataset_id, EVALUATION_WINDOWS_TABLE)}` windows
        ON claims.claim_id = windows.claim_id
    WHERE {" AND ".join(where)}
    ORDER BY claims.claimed_at ASC
    LIMIT @limit
    """
    return _query_rows(client, sql, _job_config(params))


def _snapshot_rank_context(
    *,
    client: Any,
    dataset_id: str,
    player_id_internal: str,
    season: int,
    week: int | None,
    time_horizon: str,
    scoring_profile_id: str | None,
    league_type_id: str | None,
    roster_format_id: str | None,
    model_run_id_at_claim: str | None,
) -> dict[str, Any]:
    snapshot: dict[str, Any] = {}
    try:
        pigskin = _query_projection_rank(
            client=client,
            dataset_id=dataset_id,
            player_id_internal=player_id_internal,
            season=season,
            week=week,
            time_horizon=time_horizon,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            model_run_id_at_claim=model_run_id_at_claim,
        )
        if pigskin:
            snapshot.update({
                "pigskin_rank_at_claim": pigskin.get("rank_overall"),
                "pigskin_model_run_id": pigskin.get("model_run_id"),
                "pigskin_rank_source": pigskin.get("rank_source"),
            })
    except Exception as exc:
        snapshot["pigskin_rank_snapshot_error"] = str(exc)[:500]

    try:
        market = _query_market_rank(
            client=client,
            dataset_id=dataset_id,
            player_id_internal=player_id_internal,
            season=season,
            week=week,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
        )
        if market:
            snapshot.update({
                "market_rank_at_claim": market.get("rank_overall"),
                "market_source_id": market.get("source_id"),
                "market_snapshot_id": market.get("snapshot_id"),
                "market_baseline_type": market.get("baseline_type"),
            })
    except Exception as exc:
        snapshot["market_rank_snapshot_error"] = str(exc)[:500]
    return snapshot


def _query_projection_rank(
    *,
    client: Any,
    dataset_id: str,
    player_id_internal: str,
    season: int,
    week: int | None,
    time_horizon: str,
    scoring_profile_id: str | None,
    league_type_id: str | None,
    roster_format_id: str | None,
    model_run_id_at_claim: str | None,
) -> dict[str, Any] | None:
    where = [
        "player_id_internal = @player_id_internal",
        "projection_horizon = @time_horizon",
        "(as_of_season = @season OR season = @season)",
    ]
    params: list[tuple[str, str, Any]] = [
        ("player_id_internal", "STRING", player_id_internal),
        ("time_horizon", "STRING", time_horizon),
        ("season", "INT64", int(season)),
        ("limit", "INT64", 1),
    ]
    if week is not None:
        where.append("(as_of_week = @week OR week = @week)")
        params.append(("week", "INT64", int(week)))
    if scoring_profile_id:
        where.append("scoring_profile_id = @scoring_profile_id")
        params.append(("scoring_profile_id", "STRING", scoring_profile_id))
    if league_type_id:
        where.append("league_type_id = @league_type_id")
        params.append(("league_type_id", "STRING", league_type_id))
    if roster_format_id:
        where.append("roster_format_id = @roster_format_id")
        params.append(("roster_format_id", "STRING", roster_format_id))
    if model_run_id_at_claim:
        where.append("model_run_id = @model_run_id_at_claim")
        params.append(("model_run_id_at_claim", "STRING", model_run_id_at_claim))
    sql = f"""
    SELECT
        model_run_id,
        rank_overall,
        rank_position,
        rank_source,
        created_at
    FROM `{_table_id(client.project, dataset_id, "projection_rankings_current")}`
    WHERE {" AND ".join(where)}
    ORDER BY created_at DESC
    LIMIT @limit
    """
    rows = _query_rows(client, sql, _job_config(params))
    return rows[0] if rows else None


def _query_market_rank(
    *,
    client: Any,
    dataset_id: str,
    player_id_internal: str,
    season: int,
    week: int | None,
    scoring_profile_id: str | None,
    league_type_id: str | None,
    roster_format_id: str | None,
) -> dict[str, Any] | None:
    where = [
        "player_id_internal = @player_id_internal",
        "season = @season",
        "rank_overall IS NOT NULL",
    ]
    params: list[tuple[str, str, Any]] = [
        ("player_id_internal", "STRING", player_id_internal),
        ("season", "INT64", int(season)),
        ("limit", "INT64", 1),
    ]
    if week is not None:
        where.append("(week = @week OR week IS NULL)")
        params.append(("week", "INT64", int(week)))
    if scoring_profile_id:
        where.append("(scoring_profile_id = @scoring_profile_id OR scoring_profile_id IS NULL)")
        params.append(("scoring_profile_id", "STRING", scoring_profile_id))
    if league_type_id:
        where.append("(league_type_id = @league_type_id OR league_type_id IS NULL)")
        params.append(("league_type_id", "STRING", league_type_id))
    if roster_format_id:
        where.append("(roster_format_id = @roster_format_id OR roster_format_id IS NULL)")
        params.append(("roster_format_id", "STRING", roster_format_id))
    sql = f"""
    SELECT
        source_id,
        snapshot_id,
        rank_overall,
        rank_position,
        baseline_type,
        updated_at
    FROM `{_table_id(client.project, dataset_id, "market_consensus_baseline_current")}`
    WHERE {" AND ".join(where)}
    ORDER BY updated_at DESC
    LIMIT @limit
    """
    rows = _query_rows(client, sql, _job_config(params))
    return rows[0] if rows else None


def _load_claim_source(client: Any, dataset_id: str, source_id: str) -> dict[str, Any] | None:
    sql = f"""
    SELECT *
    FROM `{_table_id(client.project, dataset_id, CLAIM_SOURCES_TABLE)}`
    WHERE source_id = @source_id
    LIMIT 1
    """
    rows = _query_rows(client, sql, _job_config([("source_id", "STRING", source_id)]))
    return rows[0] if rows else None


def _load_identity_rows(
    client: Any | None = None,
    dataset_id: str | None = None,
    limit: int = 50000,
) -> list[dict[str, Any]]:
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql = f"""
    SELECT
        player_id_internal,
        gsis_id,
        sleeper_player_id,
        pfr_id,
        espn_id,
        yahoo_id,
        nflverse_id,
        fantasypros_id,
        normalized_name,
        display_name,
        full_name,
        position,
        current_team
    FROM `{_table_id(client.project, dataset_id, "player_identity_bridge")}`
    LIMIT @limit
    """
    return _query_rows(client, sql, _job_config([("limit", "INT64", max(1, min(int(limit), 50000)))]))


def _build_identity_indexes(identity_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_internal = {}
    by_external = {}
    by_name = {}
    for row in identity_rows:
        internal = row.get("player_id_internal")
        if internal:
            by_internal[str(internal)] = row
        for key in ("gsis_id", "sleeper_player_id", "pfr_id", "espn_id", "yahoo_id", "nflverse_id", "fantasypros_id"):
            value = row.get(key)
            if value:
                by_external[str(value)] = row
        normalized = row.get("normalized_name") or _normalize_name(row.get("display_name") or row.get("full_name"))
        if normalized:
            by_name.setdefault(str(normalized), []).append(row)
    return {"by_internal": by_internal, "by_external": by_external, "by_name": by_name}


def _find_identity_matches(player: dict[str, Any], indexes: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    internal = player.get("player_id_internal")
    if internal and internal in indexes["by_internal"]:
        return [indexes["by_internal"][internal]], "player_id_internal"
    source_key = player.get("source_player_key")
    if source_key and source_key in indexes["by_external"]:
        return [indexes["by_external"][source_key]], "source_player_key"
    candidates = indexes["by_name"].get(_normalize_name(player.get("display_name")), [])
    position = player.get("position")
    team = player.get("team")
    if candidates and position and team:
        exact = [
            row for row in candidates
            if _upper_or_none(row.get("position")) == position
            and _upper_or_none(row.get("current_team")) == team
        ]
        if exact:
            return exact, "name_team_position"
    if candidates and position:
        exact = [row for row in candidates if _upper_or_none(row.get("position")) == position]
        if exact:
            return exact, "name_position"
    if candidates:
        return candidates, "normalized_name"
    return [], "unmatched"


def _normalize_player_input(raw_player: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(raw_player, str):
        row: dict[str, Any] = {"display_name": raw_player}
    else:
        row = dict(raw_player)
    display_name = _first_value(row, "display_name", "player", "player_name", "name", "source_player_name")
    return {
        "player_id_internal": _string_or_none(_first_value(row, "player_id_internal")),
        "source_player_key": _string_or_none(_first_value(row, "source_player_key", "player_id", "gsis_id", "sleeper_player_id")),
        "display_name": str(display_name or "").strip(),
        "position": _upper_or_none(_first_value(row, "position", "pos")),
        "team": _upper_or_none(_first_value(row, "team", "current_team", "nfl_team")),
        "player_role_in_claim": _string_or_none(_first_value(row, "player_role_in_claim", "role")) or "subject",
        "claimed_rank": _int_or_none(_first_value(row, "claimed_rank")),
        "claimed_projection": _num(_first_value(row, "claimed_projection"), None),
        "claimed_value": _num(_first_value(row, "claimed_value"), None),
        "side": _string_or_none(_first_value(row, "side")),
        "missing_data_flags": "[]",
    }


def _resolved_player_row(player: dict[str, Any], identity: dict[str, Any] | None, match_method: str) -> dict[str, Any]:
    row = dict(player)
    row["match_method"] = match_method
    if identity:
        row["player_id_internal"] = identity.get("player_id_internal")
        row["display_name"] = identity.get("display_name") or identity.get("full_name") or row.get("display_name")
        row["position"] = _upper_or_none(identity.get("position")) or row.get("position")
        row["team"] = _upper_or_none(identity.get("current_team")) or row.get("team")
    if not row.get("display_name"):
        _add_missing_flag(row, "missing_display_name")
    if not row.get("player_id_internal"):
        _add_missing_flag(row, "missing_player_id_internal")
    return row


def _claim_player_rows(
    *,
    claim_id: str,
    resolved_players: list[dict[str, Any]],
    claimed_rank: int | None = None,
    claimed_projection: float | None = None,
    claimed_value: float | None = None,
) -> list[dict[str, Any]]:
    now = _utc_timestamp()
    rows = []
    for player in resolved_players:
        display_name = player.get("display_name")
        if not display_name:
            display_name = player.get("source_player_key") or "Unknown Player"
        rows.append({
            "claim_id": claim_id,
            "player_id_internal": player.get("player_id_internal"),
            "source_player_key": player.get("source_player_key") or _generated_source_key(display_name, player.get("position"), player.get("team")),
            "display_name": display_name,
            "position": player.get("position"),
            "team": player.get("team"),
            "player_role_in_claim": player.get("player_role_in_claim") or "subject",
            "claimed_rank": _int_or_none(player.get("claimed_rank")) if player.get("claimed_rank") is not None else _int_or_none(claimed_rank),
            "claimed_projection": _num(player.get("claimed_projection"), None) if player.get("claimed_projection") is not None else _num(claimed_projection, None),
            "claimed_value": _num(player.get("claimed_value"), None) if player.get("claimed_value") is not None else _num(claimed_value, None),
            "side": player.get("side"),
            "created_at": now,
        })
    return rows


def _validate_claim_for_status(
    claim: dict[str, Any],
    players: list[dict[str, Any]],
    review_status: str,
) -> None:
    if review_status == "draft":
        _require(claim.get("source_id"), "source_id is required")
        _require(claim.get("claim_text"), "claim_text is required")
        _require(claim.get("claim_type"), "claim_type is required")
        _require(claim.get("time_horizon"), "time_horizon is required")
        _require(claim.get("season"), "season is required")
        return
    required_fields = [
        "source_id",
        "source_name",
        "claim_text",
        "claim_type",
        "claim_direction",
        "time_horizon",
        "season",
    ]
    missing = [field for field in required_fields if claim.get(field) in (None, "")]
    player_ids = _json_array(claim.get("player_ids_json"))
    team_ids = _json_array(claim.get("team_ids_json"))
    if not player_ids and not team_ids and not players:
        missing.append("player_ids_json or team_ids_json")
    if missing:
        raise ValueError(f"Claim cannot be {review_status} until required fields are present: {', '.join(missing)}")


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


def _validate_choice(value: str, allowed: set[str], label: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized not in allowed:
        raise ValueError(f"Invalid {label}: {value!r}")
    return normalized


def _optional_choice(value: str | None, allowed: set[str], label: str) -> str | None:
    if value in (None, ""):
        return None
    return _validate_choice(str(value), allowed, label)


def _safe_id(value: str, label: str) -> str:
    normalized = str(value or "").strip().lower().replace("-", "_")
    if not IDENTIFIER_RE.fullmatch(normalized):
        raise ValueError(f"Invalid {label}: {value!r}")
    return normalized


def _require(value: Any, message: str) -> None:
    if value in (None, ""):
        raise ValueError(message)


def _first_value(row: dict[str, Any], *keys: str) -> Any:
    lower_map = {str(key).strip().lower(): value for key, value in row.items()}
    for key in keys:
        value = lower_map.get(key.lower())
        if value not in (None, ""):
            return value
    return None


def _string_or_none(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value).strip()


def _upper_or_none(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value).strip().upper()


def _normalize_name(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def _timestamp_string(value: datetime | str | None) -> str:
    if value is None:
        return _utc_timestamp()
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return str(value)


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _generate_claim_id(source_id: str, claim_type: str, season: int, week: int | None) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    week_part = f"w{week}" if week is not None else "season"
    return f"{_safe_id(source_id, 'source ID')}-{_safe_id(claim_type, 'claim type')}-{season}-{week_part}-{stamp}-{uuid.uuid4().hex[:8]}"


def _evaluation_window_id(
    claim_id: str,
    time_horizon: str,
    season: int,
    start_week: int | None,
    end_season: int,
    end_week: int | None,
) -> str:
    return f"{claim_id}:{time_horizon}:{season}:{start_week or 'na'}:{end_season}:{end_week or 'na'}"


def _generated_source_key(name: Any, position: Any, team: Any) -> str:
    return f"name:{_normalize_name(name)}|pos:{position or 'UNK'}|team:{team or 'UNK'}"


def _identity_candidate(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "player_id_internal": row.get("player_id_internal"),
        "display_name": row.get("display_name") or row.get("full_name"),
        "position": row.get("position"),
        "team": row.get("current_team"),
    }


def _add_missing_flag(row: dict[str, Any], flag: str) -> None:
    flags = set(_json_array(row.get("missing_data_flags")))
    flags.add(flag)
    row["missing_data_flags"] = _json_dumps(sorted(flags))


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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage manual Meatbag Claim Ledger entries.")
    parser.add_argument("--create-source", action="store_true")
    parser.add_argument("--create-claim", action="store_true")
    parser.add_argument("--source-id")
    parser.add_argument("--source-name")
    parser.add_argument("--source-type", default="manual")
    parser.add_argument("--person-name")
    parser.add_argument("--show-name")
    parser.add_argument("--channel-name")
    parser.add_argument("--source-url")
    parser.add_argument("--notes")
    parser.add_argument("--inactive", action="store_true")
    parser.add_argument("--claim-type")
    parser.add_argument("--claim-direction")
    parser.add_argument("--time-horizon", default="weekly")
    parser.add_argument("--player", action="append", default=[])
    parser.add_argument("--season", type=int)
    parser.add_argument("--week", type=int)
    parser.add_argument("--text")
    parser.add_argument("--entered-by")
    parser.add_argument("--review-status", default="draft")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.create_source:
        _require(args.source_id, "--source-id is required")
        _require(args.source_name, "--source-name is required")
        result = register_claim_source(
            source_id=args.source_id,
            source_name=args.source_name,
            source_type=args.source_type,
            person_name=args.person_name,
            show_name=args.show_name,
            channel_name=args.channel_name,
            source_url=args.source_url,
            notes=args.notes,
            active=not args.inactive,
            dry_run=args.dry_run,
        )
    elif args.create_claim:
        _require(args.source_id, "--source-id is required")
        _require(args.claim_type, "--claim-type is required")
        _require(args.season, "--season is required")
        _require(args.text, "--text is required")
        result = create_fantasy_claim(
            source_id=args.source_id,
            source_name=args.source_name,
            claim_source_type=args.source_type,
            claim_text=args.text,
            claim_type=args.claim_type,
            claim_direction=args.claim_direction,
            time_horizon=args.time_horizon,
            season=args.season,
            week=args.week,
            players=args.player,
            entered_by=args.entered_by,
            review_status=args.review_status,
            dry_run=args.dry_run,
        )
    else:
        raise SystemExit("Use --create-source or --create-claim.")
    print(json.dumps(result, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
