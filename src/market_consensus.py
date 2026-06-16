"""Market and consensus baseline ingestion helpers.

This module only supports manual and CSV inputs. It does not scrape websites or
call external APIs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from google.cloud import bigquery

from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_SCORING_PROFILE = "ppr"
DEFAULT_LEAGUE_TYPE = "redraft"
DEFAULT_ROSTER_FORMAT = "one_qb"
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("MARKET_CONSENSUS_MAX_BYTES_BILLED", "1000000000"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")

SOURCE_TABLE = "market_consensus_sources"
SNAPSHOT_TABLE = "market_consensus_snapshots"
PLAYER_VALUES_TABLE = "market_consensus_player_values"
CURRENT_BASELINE_TABLE = "market_consensus_baseline_current"

ALLOWED_SOURCE_TYPES = {
    "adp",
    "ecr",
    "projection",
    "prop",
    "market_value",
    "analyst_rank",
    "manual",
}
ALLOWED_ACCESS_METHODS = {"csv", "api", "manual", "internal"}


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def register_market_source(
    *,
    source_id: str,
    source_name: str,
    source_type: str,
    access_method: str,
    license_notes: str | None = None,
    automated_allowed: bool = False,
    active: bool = True,
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Register or update a market source."""

    source_id = _safe_source_id(source_id)
    source_type = _validate_choice(source_type, ALLOWED_SOURCE_TYPES, "source_type")
    access_method = _validate_choice(access_method, ALLOWED_ACCESS_METHODS, "access_method")
    row = {
        "source_id": source_id,
        "source_name": source_name,
        "source_type": source_type,
        "access_method": access_method,
        "license_notes": license_notes,
        "automated_allowed": bool(automated_allowed),
        "active": bool(active),
        "created_at": _utc_timestamp(),
        "updated_at": _utc_timestamp(),
    }
    if dry_run:
        return {"dry_run": True, "source": row}

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql = f"""
    MERGE `{_table_id(client.project, dataset_id, SOURCE_TABLE)}` target
    USING (
        SELECT
            @source_id AS source_id,
            @source_name AS source_name,
            @source_type AS source_type,
            @access_method AS access_method,
            @license_notes AS license_notes,
            @automated_allowed AS automated_allowed,
            @active AS active
    ) source
    ON target.source_id = source.source_id
    WHEN MATCHED THEN
        UPDATE SET
            source_name = source.source_name,
            source_type = source.source_type,
            access_method = source.access_method,
            license_notes = source.license_notes,
            automated_allowed = source.automated_allowed,
            active = source.active,
            updated_at = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN
        INSERT (
            source_id,
            source_name,
            source_type,
            access_method,
            license_notes,
            automated_allowed,
            active,
            created_at,
            updated_at
        )
        VALUES (
            source.source_id,
            source.source_name,
            source.source_type,
            source.access_method,
            source.license_notes,
            source.automated_allowed,
            source.active,
            CURRENT_TIMESTAMP(),
            CURRENT_TIMESTAMP()
        )
    """
    client.query(sql, job_config=_job_config([
        ("source_id", "STRING", source_id),
        ("source_name", "STRING", source_name),
        ("source_type", "STRING", source_type),
        ("access_method", "STRING", access_method),
        ("license_notes", "STRING", license_notes),
        ("automated_allowed", "BOOL", bool(automated_allowed)),
        ("active", "BOOL", bool(active)),
    ])).result()
    return {"dry_run": False, "source": row}


def create_market_snapshot(
    *,
    source_id: str,
    snapshot_type: str,
    season: int,
    week: int | None = None,
    snapshot_id: str | None = None,
    snapshot_date: date | str | None = None,
    snapshot_timestamp: datetime | str | None = None,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    source_file_uri: str | None = None,
    source_url: str | None = None,
    ingested_by: str = "market_consensus",
    row_count: int = 0,
    checksum: str | None = None,
    notes: str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Create a snapshot metadata row."""

    source_id = _safe_source_id(source_id)
    snapshot_type = _safe_source_id(snapshot_type)
    snapshot_id = snapshot_id or _generate_snapshot_id(source_id, snapshot_type, season, week)
    row = {
        "snapshot_id": snapshot_id,
        "source_id": source_id,
        "snapshot_type": snapshot_type,
        "snapshot_date": _date_string(snapshot_date),
        "snapshot_timestamp": _timestamp_string(snapshot_timestamp),
        "season": int(season),
        "week": _int_or_none(week),
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "source_file_uri": source_file_uri,
        "source_url": source_url,
        "ingested_by": ingested_by,
        "ingested_at": _utc_timestamp(),
        "row_count": int(row_count),
        "checksum": checksum,
        "notes": notes,
    }
    if dry_run:
        return {"dry_run": True, "snapshot_id": snapshot_id, "snapshot": row}

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    errors = client.insert_rows_json(_table_id(client.project, dataset_id, SNAPSHOT_TABLE), [row])
    if errors:
        raise RuntimeError(f"Failed to insert market snapshot {snapshot_id}: {errors}")
    return {"dry_run": False, "snapshot_id": snapshot_id, "snapshot": row}


def normalize_market_rows(
    raw_rows: list[dict[str, Any]],
    *,
    snapshot_id: str,
    source_id: str,
    season: int,
    week: int | None = None,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
) -> list[dict[str, Any]]:
    """Normalize CSV or manual source rows into the market player-value shape."""

    _require(snapshot_id, "snapshot_id is required")
    _require(source_id, "source_id is required")
    source_id = _safe_source_id(source_id)
    normalized = []
    seen: dict[tuple[Any, ...], dict[str, Any]] = {}
    for raw in raw_rows:
        row = _normalize_one_market_row(
            raw,
            snapshot_id=snapshot_id,
            source_id=source_id,
            season=season,
            week=week,
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
        )
        key = _source_row_key(row)
        if key in seen:
            _add_missing_flag(seen[key], "duplicate_source_row_dropped")
            continue
        seen[key] = row
        normalized.append(row)
    return normalized


def resolve_market_players(
    rows: list[dict[str, Any]],
    *,
    identity_rows: list[dict[str, Any]] | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Attach canonical player IDs using the identity bridge first."""

    identity_rows = identity_rows if identity_rows is not None else load_identity_rows(client=client, dataset_id=dataset_id)
    identity_maps = _build_identity_maps(identity_rows)
    resolved = []
    for row in rows:
        output = dict(row)
        identity, match_method = _find_identity_match(output, identity_maps)
        if identity:
            output["player_id_internal"] = identity.get("player_id_internal")
            output["display_name"] = output.get("display_name") or identity.get("display_name")
            output["position"] = output.get("position") or identity.get("position")
            output["team"] = output.get("team") or identity.get("current_team")
            output["match_method"] = match_method
            if match_method in {"name_team_position", "name_position"}:
                _add_missing_flag(output, "identity_name_fallback_match")
        else:
            output["match_method"] = "unmatched"
            _add_missing_flag(output, "missing_player_id_internal")
        resolved.append(output)
    return resolved


def ingest_market_consensus_csv(
    csv_path: str | Path,
    *,
    source_id: str,
    season: int,
    week: int | None = None,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    snapshot_type: str | None = None,
    snapshot_id: str | None = None,
    identity_rows: list[dict[str, Any]] | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Ingest a local CSV file into normalized market baseline rows."""

    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(path)
    raw_rows = _read_csv(path)
    checksum = _file_checksum(path)
    snapshot_type = snapshot_type or "csv"
    snapshot_id = snapshot_id or _generate_snapshot_id(source_id, snapshot_type, season, week)
    rows = normalize_market_rows(
        raw_rows,
        snapshot_id=snapshot_id,
        source_id=source_id,
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    rows = resolve_market_players(rows, identity_rows=identity_rows, client=client, dataset_id=dataset_id)
    snapshot = create_market_snapshot(
        source_id=source_id,
        snapshot_type=snapshot_type,
        snapshot_id=snapshot_id,
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        source_file_uri=str(path),
        row_count=len(rows),
        checksum=checksum,
        client=client,
        dataset_id=dataset_id,
        dry_run=dry_run,
    )
    if dry_run:
        return {
            "dry_run": True,
            "snapshot_id": snapshot_id,
            "row_count": len(rows),
            "snapshot": snapshot["snapshot"],
            "rows": rows,
        }

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    _insert_rows(client, dataset_id, PLAYER_VALUES_TABLE, rows)
    _replace_current_baseline(client, dataset_id, rows)
    return {"dry_run": False, "snapshot_id": snapshot_id, "row_count": len(rows)}


def ingest_manual_market_values(
    rows: list[dict[str, Any]],
    *,
    source_id: str,
    season: int,
    week: int | None = None,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    snapshot_id: str | None = None,
    identity_rows: list[dict[str, Any]] | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Ingest already loaded manual market rows."""

    snapshot_id = snapshot_id or _generate_snapshot_id(source_id, "manual", season, week)
    normalized = normalize_market_rows(
        rows,
        snapshot_id=snapshot_id,
        source_id=source_id,
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    normalized = resolve_market_players(normalized, identity_rows=identity_rows, client=client, dataset_id=dataset_id)
    snapshot = create_market_snapshot(
        source_id=source_id,
        snapshot_type="manual",
        snapshot_id=snapshot_id,
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        row_count=len(normalized),
        checksum=_rows_checksum(rows),
        client=client,
        dataset_id=dataset_id,
        dry_run=dry_run,
    )
    if dry_run:
        return {
            "dry_run": True,
            "snapshot_id": snapshot_id,
            "row_count": len(normalized),
            "snapshot": snapshot["snapshot"],
            "rows": normalized,
        }

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    _insert_rows(client, dataset_id, PLAYER_VALUES_TABLE, normalized)
    _replace_current_baseline(client, dataset_id, normalized)
    return {"dry_run": False, "snapshot_id": snapshot_id, "row_count": len(normalized)}


def get_current_market_baseline(
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    source_id: str | None = None,
    season: int | None = None,
    week: int | None = None,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    baseline_type: str | None = None,
    limit: int = 1000,
) -> list[dict[str, Any]]:
    """Read the current normalized market baseline."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    filters = []
    params: list[tuple[str, str, Any]] = [("limit", "INT64", max(1, min(int(limit), 5000)))]
    for name, value, param_type in (
        ("source_id", source_id, "STRING"),
        ("season", season, "INT64"),
        ("week", week, "INT64"),
        ("scoring_profile_id", scoring_profile_id, "STRING"),
        ("league_type_id", league_type_id, "STRING"),
        ("roster_format_id", roster_format_id, "STRING"),
        ("baseline_type", baseline_type, "STRING"),
    ):
        if value is not None:
            if name in {"scoring_profile_id", "league_type_id", "roster_format_id"}:
                filters.append(f"({name} IS NULL OR {name} = @{name})")
            else:
                filters.append(f"{name} = @{name}")
            params.append((name, param_type, value))
    where_clause = "WHERE " + " AND ".join(filters) if filters else ""
    sql = f"""
    SELECT *
    FROM `{_table_id(client.project, dataset_id, CURRENT_BASELINE_TABLE)}`
    {where_clause}
    ORDER BY updated_at DESC
    LIMIT @limit
    """
    return _query_rows(client, sql, _job_config(params))


def compare_projection_to_market(
    projection_rows: list[dict[str, Any]],
    market_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare Pigskin projection result rows with market baseline rows."""

    market_index = _build_market_index(market_rows)
    compared = []
    matched = 0
    for row in projection_rows:
        output = dict(row)
        market = _find_market_row(output, market_index)
        if market:
            matched += 1
            _apply_market_comparison(output, market)
        else:
            _add_missing_flag(output, "missing_market_baseline")
        compared.append(output)
    return {
        "rows": compared,
        "matched_market_rows": matched,
        "missing_market_rows": len(projection_rows) - matched,
        "summary": _market_comparison_summary(compared),
    }


def load_identity_rows(
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    limit: int = 10000,
) -> list[dict[str, Any]]:
    """Load identity bridge rows for controlled backend matching."""

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


def _normalize_one_market_row(
    raw: dict[str, Any],
    *,
    snapshot_id: str,
    source_id: str,
    season: int,
    week: int | None,
    scoring_profile_id: str | None,
    league_type_id: str | None,
    roster_format_id: str | None,
) -> dict[str, Any]:
    now = _utc_timestamp()
    source_player_name = _first_value(raw, "source_player_name", "player", "player_name", "name", "display_name")
    position = _upper_or_none(_first_value(raw, "position", "pos"))
    team = _upper_or_none(_first_value(raw, "team", "current_team", "nfl_team"))
    source_player_key = _first_value(raw, "source_player_key", "player_id", "id", "gsis_id", "sleeper_player_id", "fantasypros_id")
    if not source_player_key:
        source_player_key = _generated_source_key(source_player_name, position, team)
    row = {
        "snapshot_id": snapshot_id,
        "source_id": source_id,
        "player_id_internal": _first_value(raw, "player_id_internal"),
        "source_player_key": str(source_player_key) if source_player_key else None,
        "source_player_name": source_player_name,
        "display_name": _first_value(raw, "display_name", "player_name", "player", "name") or source_player_name,
        "position": position,
        "team": team,
        "season": int(season),
        "week": _int_or_none(week),
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "rank_overall": _int_or_none(_first_value(raw, "rank_overall", "overall_rank", "rank", "ecr", "consensus_rank")),
        "rank_position": _int_or_none(_first_value(raw, "rank_position", "position_rank", "pos_rank")),
        "tier": _first_value(raw, "tier"),
        "projected_points": _num(_first_value(raw, "projected_points", "projection", "points", "fantasy_points"), None),
        "market_value": _num(_first_value(raw, "market_value", "trade_value", "value"), None),
        "adp": _num(_first_value(raw, "adp", "average_draft_position"), None),
        "prop_market": _first_value(raw, "prop_market", "market", "prop"),
        "prop_line": _num(_first_value(raw, "prop_line", "line"), None),
        "prop_over_odds": _num(_first_value(raw, "prop_over_odds", "over_odds"), None),
        "prop_under_odds": _num(_first_value(raw, "prop_under_odds", "under_odds"), None),
        "confidence": _num(_first_value(raw, "confidence", "confidence_score"), None),
        "match_method": None,
        "source_payload_json": _json_dumps(raw),
        "source_freshness_json": _json_dumps({"source_id": source_id, "snapshot_id": snapshot_id, "ingested_at": now}),
        "missing_data_flags": "[]",
        "created_at": now,
    }
    if not source_player_name:
        _add_missing_flag(row, "missing_source_player_name")
    if not position:
        _add_missing_flag(row, "missing_position")
    if row["rank_overall"] is None and row["projected_points"] is None and row["market_value"] is None and row["adp"] is None and row["prop_line"] is None:
        _add_missing_flag(row, "missing_numeric_baseline")
    return row


def _replace_current_baseline(client: Any, dataset_id: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    first = rows[0]
    source_id = first["source_id"]
    season = int(first["season"])
    week = first.get("week")
    scoring_profile_id = first.get("scoring_profile_id")
    league_type_id = first.get("league_type_id")
    roster_format_id = first.get("roster_format_id")
    delete_sql = f"""
    DELETE FROM `{_table_id(client.project, dataset_id, CURRENT_BASELINE_TABLE)}`
    WHERE source_id = @source_id
        AND season = @season
        AND ((@week IS NULL AND week IS NULL) OR week = @week)
        AND ((@scoring_profile_id IS NULL AND scoring_profile_id IS NULL) OR scoring_profile_id = @scoring_profile_id)
        AND ((@league_type_id IS NULL AND league_type_id IS NULL) OR league_type_id = @league_type_id)
        AND ((@roster_format_id IS NULL AND roster_format_id IS NULL) OR roster_format_id = @roster_format_id)
    """
    client.query(delete_sql, job_config=_job_config([
        ("source_id", "STRING", source_id),
        ("season", "INT64", season),
        ("week", "INT64", week),
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
    ])).result()
    current_rows = [_current_baseline_row(row) for row in rows]
    _insert_rows(client, dataset_id, CURRENT_BASELINE_TABLE, current_rows)


def _current_baseline_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": row["source_id"],
        "snapshot_id": row["snapshot_id"],
        "player_id_internal": row.get("player_id_internal"),
        "source_player_key": row.get("source_player_key"),
        "display_name": row.get("display_name"),
        "position": row.get("position"),
        "team": row.get("team"),
        "season": row["season"],
        "week": row.get("week"),
        "scoring_profile_id": row.get("scoring_profile_id"),
        "league_type_id": row.get("league_type_id"),
        "roster_format_id": row.get("roster_format_id"),
        "rank_overall": row.get("rank_overall"),
        "rank_position": row.get("rank_position"),
        "projected_points": row.get("projected_points"),
        "market_value": row.get("market_value"),
        "adp": row.get("adp"),
        "baseline_type": _baseline_type(row),
        "match_method": row.get("match_method"),
        "source_freshness_json": row.get("source_freshness_json"),
        "missing_data_flags": row.get("missing_data_flags"),
        "updated_at": _utc_timestamp(),
    }


def _apply_market_comparison(row: dict[str, Any], market: dict[str, Any]) -> None:
    actual_points = _num(row.get("actual_points"), None)
    market_projected_points = _num(market.get("projected_points"), None)
    market_rank_overall = _int_or_none(market.get("rank_overall"))
    market_rank_position = _int_or_none(market.get("rank_position"))
    actual_rank_overall = _int_or_none(row.get("actual_rank_overall"))
    actual_rank_position = _int_or_none(row.get("actual_rank_position"))
    row.update({
        "market_source_id": market.get("source_id"),
        "market_snapshot_id": market.get("snapshot_id"),
        "market_rank_overall": market_rank_overall,
        "market_rank_position": market_rank_position,
        "market_projected_points": market_projected_points,
        "market_value": _num(market.get("market_value"), None),
        "market_adp": _num(market.get("adp"), None),
        "market_absolute_error": abs(market_projected_points - actual_points)
            if market_projected_points is not None and actual_points is not None
            else None,
        "market_rank_error_overall": abs(market_rank_overall - actual_rank_overall)
            if market_rank_overall is not None and actual_rank_overall is not None
            else None,
        "market_rank_error_position": abs(market_rank_position - actual_rank_position)
            if market_rank_position is not None and actual_rank_position is not None
            else None,
    })
    if row.get("market_absolute_error") is not None and row.get("absolute_error") is not None:
        row["model_better_than_market"] = _num(row["absolute_error"], 0.0) < _num(row["market_absolute_error"], 0.0)
    else:
        row["model_better_than_market"] = None
    result_json = _json_object(row.get("result_json"))
    result_json["market_baseline"] = {
        "source_id": market.get("source_id"),
        "snapshot_id": market.get("snapshot_id"),
        "baseline_type": market.get("baseline_type"),
        "match_method": market.get("match_method"),
    }
    row["result_json"] = _json_dumps(result_json)


def _market_comparison_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    market_errors = [_num(row.get("market_absolute_error"), None) for row in rows]
    model_errors = [_num(row.get("absolute_error"), None) for row in rows if row.get("market_absolute_error") is not None]
    market_rank_errors = [_num(row.get("market_rank_error_overall"), None) for row in rows]
    model_rank_errors = [_num(row.get("rank_error_overall"), None) for row in rows if row.get("market_rank_error_overall") is not None]
    better_rows = [row for row in rows if row.get("model_better_than_market") is not None]
    return {
        "market_mae": _round(_mean(value for value in market_errors if value is not None)),
        "model_mae_on_market_matches": _round(_mean(model_errors)),
        "model_vs_market_mae_delta": _delta(_mean(model_errors), _mean(value for value in market_errors if value is not None)),
        "model_vs_market_rank_delta": _delta(
            _mean(model_rank_errors),
            _mean(value for value in market_rank_errors if value is not None),
        ),
        "model_better_than_market_rate": _round(_precision(better_rows, "model_better_than_market")),
    }


def _build_identity_maps(identity_rows: list[dict[str, Any]]) -> dict[str, Any]:
    maps: dict[str, Any] = {
        "internal": {},
        "source": {},
        "name_team_position": {},
        "name_position": {},
    }
    for row in identity_rows:
        internal = row.get("player_id_internal")
        if not internal:
            continue
        maps["internal"][str(internal)] = row
        for field in ("gsis_id", "sleeper_player_id", "pfr_id", "espn_id", "yahoo_id", "nflverse_id", "fantasypros_id", "source_player_key"):
            value = row.get(field)
            if value:
                maps["source"][str(value)] = row
        name = _normalize_name(row.get("normalized_name") or row.get("display_name") or row.get("full_name"))
        position = _upper_or_none(row.get("position"))
        team = _upper_or_none(row.get("current_team") or row.get("team"))
        if name and position and team:
            maps["name_team_position"][(name, position, team)] = row
        if name and position:
            maps["name_position"].setdefault((name, position), []).append(row)
    return maps


def _find_identity_match(row: dict[str, Any], maps: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    internal = row.get("player_id_internal")
    if internal and str(internal) in maps["internal"]:
        return maps["internal"][str(internal)], "player_id_internal"
    source_key = row.get("source_player_key")
    if source_key and str(source_key) in maps["source"]:
        return maps["source"][str(source_key)], "source_player_key"
    name = _normalize_name(row.get("source_player_name") or row.get("display_name"))
    position = _upper_or_none(row.get("position"))
    team = _upper_or_none(row.get("team"))
    if name and position and team:
        identity = maps["name_team_position"].get((name, position, team))
        if identity:
            return identity, "name_team_position"
    if name and position:
        candidates = maps["name_position"].get((name, position), [])
        if len(candidates) == 1:
            return candidates[0], "name_position"
    return None, "unmatched"


def _build_market_index(rows: list[dict[str, Any]]) -> dict[tuple[Any, ...], dict[str, Any]]:
    index: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        for key in _identity_keys(row):
            index.setdefault(key, row)
    return index


def _find_market_row(row: dict[str, Any], index: dict[tuple[Any, ...], dict[str, Any]]) -> dict[str, Any] | None:
    for key in _identity_keys(row):
        if key in index:
            return index[key]
    return None


def _identity_keys(row: dict[str, Any]) -> list[tuple[Any, ...]]:
    season = _int_or_none(row.get("season"))
    week = _int_or_none(row.get("week"))
    scoring_profile_id = row.get("scoring_profile_id")
    keys = []
    if row.get("player_id_internal"):
        keys.append(("internal", row.get("player_id_internal"), season, week, scoring_profile_id))
    if row.get("source_player_key"):
        keys.append(("source", row.get("source_player_key"), season, week, scoring_profile_id))
    name = _normalize_name(row.get("source_player_name") or row.get("display_name"))
    position = _upper_or_none(row.get("position"))
    if name and position:
        keys.append(("name_position", name, position, season, week, scoring_profile_id))
    return keys


def _baseline_type(row: dict[str, Any]) -> str:
    if row.get("prop_market") or row.get("prop_line") is not None:
        return "prop"
    if row.get("projected_points") is not None:
        return "projection"
    if row.get("adp") is not None:
        return "adp"
    if row.get("market_value") is not None:
        return "market_value"
    if row.get("rank_overall") is not None or row.get("rank_position") is not None:
        return "rank"
    return "manual"


def _source_row_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("source_id"),
        row.get("snapshot_id"),
        row.get("source_player_key"),
        _normalize_name(row.get("source_player_name") or row.get("display_name")),
        row.get("position"),
        row.get("team"),
        row.get("prop_market"),
    )


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


def _read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _file_checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rows_checksum(rows: list[dict[str, Any]]) -> str:
    return hashlib.sha256(_json_dumps(rows).encode("utf-8")).hexdigest()


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


def _safe_source_id(value: str) -> str:
    normalized = str(value or "").strip().lower().replace("-", "_")
    if not IDENTIFIER_RE.fullmatch(normalized):
        raise ValueError(f"Invalid source ID: {value!r}")
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


def _generated_source_key(name: Any, position: Any, team: Any) -> str:
    return f"name:{_normalize_name(name)}|pos:{position or 'UNK'}|team:{team or 'UNK'}"


def _upper_or_none(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value).strip().upper()


def _normalize_name(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def _date_string(value: date | str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


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


def _generate_snapshot_id(source_id: str, snapshot_type: str, season: int, week: int | None) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    week_part = f"w{week}" if week is not None else "season"
    return f"{_safe_source_id(source_id)}-{_safe_source_id(snapshot_type)}-{season}-{week_part}-{stamp}-{uuid.uuid4().hex[:8]}"


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


def _json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


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
    return None if value is None else round(value, 4)


def _delta(model_value: float | None, market_value: float | None) -> float | None:
    if model_value is None or market_value is None:
        return None
    return _round(model_value - market_value)


def _precision(rows: list[dict[str, Any]], flag: str) -> float | None:
    if not rows:
        return None
    return sum(1 for row in rows if row.get(flag)) / len(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage source-agnostic market and consensus baselines.")
    parser.add_argument("--register-source", action="store_true")
    parser.add_argument("--source-id")
    parser.add_argument("--source-name")
    parser.add_argument("--source-type", default="manual")
    parser.add_argument("--access-method", default="csv")
    parser.add_argument("--license-notes")
    parser.add_argument("--automated-allowed", action="store_true")
    parser.add_argument("--inactive", action="store_true")
    parser.add_argument("--ingest-csv")
    parser.add_argument("--season", type=int)
    parser.add_argument("--week", type=int)
    parser.add_argument("--scoring-profile", default=DEFAULT_SCORING_PROFILE)
    parser.add_argument("--league-type", default=DEFAULT_LEAGUE_TYPE)
    parser.add_argument("--roster-format", default=DEFAULT_ROSTER_FORMAT)
    parser.add_argument("--snapshot-id")
    parser.add_argument("--snapshot-type")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.register_source:
        _require(args.source_id, "--source-id is required")
        _require(args.source_name, "--source-name is required")
        result = register_market_source(
            source_id=args.source_id,
            source_name=args.source_name,
            source_type=args.source_type,
            access_method=args.access_method,
            license_notes=args.license_notes,
            automated_allowed=args.automated_allowed,
            active=not args.inactive,
            dry_run=args.dry_run,
        )
    elif args.ingest_csv:
        _require(args.source_id, "--source-id is required")
        _require(args.season, "--season is required")
        result = ingest_market_consensus_csv(
            args.ingest_csv,
            source_id=args.source_id,
            season=args.season,
            week=args.week,
            scoring_profile_id=args.scoring_profile,
            league_type_id=args.league_type,
            roster_format_id=args.roster_format,
            snapshot_id=args.snapshot_id,
            snapshot_type=args.snapshot_type,
            dry_run=args.dry_run,
        )
    else:
        raise SystemExit("Use --register-source or --ingest-csv.")
    print(json.dumps(result, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
