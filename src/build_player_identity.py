"""Build canonical player identity bridge tables from existing warehouse sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
from google.api_core.exceptions import NotFound
from google.cloud import bigquery

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.bigquery_guardrails import query_to_dataframe
from src.load import get_bigquery_project

logger = logging.getLogger("build_player_identity")

DEFAULT_DATASET = "fantasy_football_brain"
FANTASY_POSITIONS = {"QB", "RB", "WR", "TE", "K", "DEF"}
SOURCE_PRIORITY = {
    "manual_override": 0,
    "sleeper_players_current": 10,
    "player_rosters": 20,
    "sleeper_roster_players": 30,
    "analytics_pigskin_rankings": 40,
    "analytics_player_weekly_truth": 50,
    "depth_charts": 60,
    "market_values": 70,
}
SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}
ID_FIELDS = (
    "gsis_id",
    "sleeper_player_id",
    "pfr_id",
    "espn_id",
    "yahoo_id",
    "nflverse_id",
    "fantasypros_id",
)


@dataclass(frozen=True)
class PlayerIdentityOverride:
    source: str
    source_player_id: str
    player_id_internal: str
    reason: str | None = None
    active: bool = True


@dataclass(frozen=True)
class PlayerSourceRecord:
    source: str
    source_player_id: str | None = None
    gsis_id: str | None = None
    sleeper_player_id: str | None = None
    pfr_id: str | None = None
    espn_id: str | None = None
    yahoo_id: str | None = None
    nflverse_id: str | None = None
    fantasypros_id: str | None = None
    full_name: str | None = None
    display_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    position: str | None = None
    fantasy_positions: str | None = None
    current_team: str | None = None
    previous_team: str | None = None
    active_status: str | None = None
    rookie_year: int | None = None
    birth_date: Any | None = None
    source_updated_at: Any | None = None


def normalize_player_name(name: Any) -> str:
    """Normalize player names for deterministic fallback matching."""

    if name is None or pd.isna(name):
        return ""
    text = str(name).strip().lower()
    text = text.replace("'", "").replace("’", "")
    text = text.replace(".", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    parts = [part for part in text.split() if part]
    while parts and parts[-1] in SUFFIXES:
        parts.pop()
    return "".join(parts)


def split_display_name(name: str | None) -> tuple[str | None, str | None]:
    if not name:
        return None, None
    parts = str(name).strip().split()
    if not parts:
        return None, None
    if len(parts) == 1:
        return parts[0], None
    return parts[0], " ".join(parts[1:])


def _clean_string(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def _clean_int(value: Any) -> int | None:
    if value is None or pd.isna(value):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _clean_date(value: Any) -> date | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text[:10]).date()
    except ValueError:
        return None


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _source_keys(record: PlayerSourceRecord) -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    if record.source and record.source_player_id:
        keys.append((record.source.lower(), str(record.source_player_id)))
    for field_name, source_name in (
        ("sleeper_player_id", "sleeper"),
        ("gsis_id", "gsis"),
        ("pfr_id", "pfr"),
        ("espn_id", "espn"),
        ("yahoo_id", "yahoo"),
        ("nflverse_id", "nflverse"),
        ("fantasypros_id", "fantasypros"),
    ):
        value = getattr(record, field_name)
        if value:
            keys.append((source_name, str(value)))
    return keys


def _stable_internal_id(record: PlayerSourceRecord) -> str:
    for prefix, value in (
        ("gsis", record.gsis_id),
        ("sleeper", record.sleeper_player_id),
        ("pfr", record.pfr_id),
        ("espn", record.espn_id),
        ("yahoo", record.yahoo_id),
        ("nflverse", record.nflverse_id),
    ):
        if value:
            return f"{prefix}:{value}"

    name_key = normalize_player_name(record.display_name or record.full_name)
    position = (record.position or "UNK").upper()
    digest = hashlib.sha1(f"{name_key}|{position}".encode("utf-8")).hexdigest()[:16]
    return f"namepos:{digest}"


def _match_method_from_ids(record: PlayerSourceRecord, id_to_internal: dict[tuple[str, str], str]) -> tuple[str | None, str | None]:
    for source_name, value in _source_keys(record):
        if (source_name, value) in id_to_internal:
            return id_to_internal[(source_name, value)], f"exact_{source_name}_id"
    return None, None


def _candidate_confidence(match_method: str) -> float:
    if match_method == "manual_override":
        return 1.0
    if match_method.startswith("exact_"):
        return 0.95
    if match_method == "normalized_name_team_position":
        return 0.82
    if match_method == "normalized_name_position":
        return 0.65
    return 0.55


def _new_identity_row(record: PlayerSourceRecord, now: datetime, internal_id: str, match_method: str) -> dict[str, Any]:
    display_name = _clean_string(record.display_name or record.full_name)
    full_name = _clean_string(record.full_name or record.display_name)
    first_name = _clean_string(record.first_name)
    last_name = _clean_string(record.last_name)
    if not first_name and not last_name:
        first_name, last_name = split_display_name(full_name or display_name)

    row = {
        "player_id_internal": internal_id,
        "gsis_id": _clean_string(record.gsis_id),
        "sleeper_player_id": _clean_string(record.sleeper_player_id),
        "pfr_id": _clean_string(record.pfr_id),
        "espn_id": _clean_string(record.espn_id),
        "yahoo_id": _clean_string(record.yahoo_id),
        "nflverse_id": _clean_string(record.nflverse_id),
        "fantasypros_id": _clean_string(record.fantasypros_id),
        "full_name": full_name,
        "normalized_name": normalize_player_name(full_name or display_name),
        "display_name": display_name,
        "first_name": first_name,
        "last_name": last_name,
        "position": _clean_string(record.position),
        "fantasy_positions": _clean_string(record.fantasy_positions),
        "current_team": _clean_string(record.current_team),
        "previous_team": _clean_string(record.previous_team),
        "active_status": _clean_string(record.active_status),
        "rookie_year": _clean_int(record.rookie_year),
        "birth_date": _clean_date(record.birth_date),
        "source_confidence": _candidate_confidence(match_method),
        "match_method": match_method,
        "source_priority": record.source,
        "source_freshness_json": _json_dumps({record.source: _stringify_time(record.source_updated_at)}),
        "missing_data_flags": "[]",
        "created_at": now,
        "updated_at": now,
    }
    row["missing_data_flags"] = _json_dumps(_missing_flags(row))
    return row


def _stringify_time(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _missing_flags(row: dict[str, Any]) -> list[str]:
    flags = []
    if not row.get("gsis_id"):
        flags.append("missing_gsis_id")
    if not row.get("sleeper_player_id"):
        flags.append("missing_sleeper_player_id")
    if not row.get("current_team"):
        flags.append("missing_current_team")
    if not row.get("birth_date"):
        flags.append("missing_birth_date")
    if float(row.get("source_confidence") or 0) < 0.8:
        flags.append("low_confidence_match")
    return flags


def _merge_record(row: dict[str, Any], record: PlayerSourceRecord, match_method: str) -> None:
    fill_values = {
        "gsis_id": record.gsis_id,
        "sleeper_player_id": record.sleeper_player_id,
        "pfr_id": record.pfr_id,
        "espn_id": record.espn_id,
        "yahoo_id": record.yahoo_id,
        "nflverse_id": record.nflverse_id,
        "fantasypros_id": record.fantasypros_id,
        "full_name": record.full_name or record.display_name,
        "display_name": record.display_name or record.full_name,
        "first_name": record.first_name,
        "last_name": record.last_name,
        "position": record.position,
        "fantasy_positions": record.fantasy_positions,
        "current_team": record.current_team,
        "previous_team": record.previous_team,
        "active_status": record.active_status,
        "rookie_year": record.rookie_year,
        "birth_date": _clean_date(record.birth_date),
    }
    for field_name, value in fill_values.items():
        value = _clean_int(value) if field_name == "rookie_year" else _clean_string(value) if field_name != "birth_date" else value
        if row.get(field_name) in (None, "") and value not in (None, ""):
            row[field_name] = value

    if not row.get("normalized_name"):
        row["normalized_name"] = normalize_player_name(row.get("full_name") or row.get("display_name"))

    row["source_confidence"] = max(
        float(row.get("source_confidence") or 0),
        _candidate_confidence(match_method),
    )
    if row.get("match_method") not in ("manual_override",) and match_method == "manual_override":
        row["match_method"] = match_method
    elif not row.get("match_method") or row["match_method"] == "new_identity":
        row["match_method"] = match_method

    priorities = [item for item in str(row.get("source_priority") or "").split(",") if item]
    if record.source not in priorities:
        priorities.append(record.source)
    row["source_priority"] = ",".join(priorities)

    freshness = json.loads(row.get("source_freshness_json") or "{}")
    freshness[record.source] = _stringify_time(record.source_updated_at)
    row["source_freshness_json"] = _json_dumps(freshness)
    row["missing_data_flags"] = _json_dumps(_missing_flags(row))


def build_identity_rows(
    source_records: Iterable[PlayerSourceRecord],
    overrides: Iterable[PlayerIdentityOverride] = (),
    *,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    """Build bridge rows from source records with override and exact-ID priority."""

    now = now or datetime.now(timezone.utc)
    active_overrides = [override for override in overrides if override.active]
    override_map = {
        (override.source.lower(), str(override.source_player_id)): override.player_id_internal
        for override in active_overrides
    }
    id_to_internal: dict[tuple[str, str], str] = dict(override_map)
    name_team_position: dict[tuple[str, str, str], str] = {}
    name_position: dict[tuple[str, str], set[str]] = {}
    identities: dict[str, dict[str, Any]] = {}

    records = sorted(
        source_records,
        key=lambda item: SOURCE_PRIORITY.get(item.source, 999),
    )

    for record in records:
        display_name = record.display_name or record.full_name
        normalized = normalize_player_name(display_name)
        position = (record.position or "").upper()
        team = (record.current_team or "").upper()
        if position and position not in FANTASY_POSITIONS:
            continue

        internal_id = None
        match_method = None
        for key in _source_keys(record):
            if key in override_map:
                internal_id = override_map[key]
                match_method = "manual_override"
                break

        if not internal_id:
            internal_id, match_method = _match_method_from_ids(record, id_to_internal)

        if not internal_id and normalized and team and position:
            internal_id = name_team_position.get((normalized, team, position))
            if internal_id:
                match_method = "normalized_name_team_position"

        if not internal_id and normalized and position:
            candidates = name_position.get((normalized, position), set())
            if len(candidates) == 1:
                internal_id = next(iter(candidates))
                match_method = "normalized_name_position"

        if not internal_id:
            internal_id = _stable_internal_id(record)
            match_method = "exact_source_identity" if any(_source_keys(record)) else "new_identity"

        if internal_id not in identities:
            identities[internal_id] = _new_identity_row(record, now, internal_id, match_method or "new_identity")
        else:
            _merge_record(identities[internal_id], record, match_method or "new_identity")

        for key in _source_keys(record):
            id_to_internal[key] = internal_id
        if normalized and team and position:
            name_team_position[(normalized, team, position)] = internal_id
        if normalized and position:
            name_position.setdefault((normalized, position), set()).add(internal_id)

    return sorted(identities.values(), key=lambda row: (row.get("position") or "", row.get("display_name") or ""))


def build_dim_players_current_rows(bridge_rows: Iterable[dict[str, Any]], *, today: date | None = None) -> list[dict[str, Any]]:
    today = today or date.today()
    dim_rows = []
    for row in bridge_rows:
        birth_date = row.get("birth_date")
        age = None
        if isinstance(birth_date, date):
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        dim_rows.append({
            "player_id_internal": row.get("player_id_internal"),
            "display_name": row.get("display_name"),
            "full_name": row.get("full_name"),
            "normalized_name": row.get("normalized_name"),
            "position": row.get("position"),
            "fantasy_positions": row.get("fantasy_positions"),
            "current_team": row.get("current_team"),
            "active_status": row.get("active_status"),
            "sleeper_player_id": row.get("sleeper_player_id"),
            "gsis_id": row.get("gsis_id"),
            "pfr_id": row.get("pfr_id"),
            "espn_id": row.get("espn_id"),
            "yahoo_id": row.get("yahoo_id"),
            "rookie_year": row.get("rookie_year"),
            "birth_date": birth_date,
            "age": float(age) if age is not None else None,
            "source_confidence": row.get("source_confidence"),
            "match_method": row.get("match_method"),
            "source_freshness_json": row.get("source_freshness_json"),
            "missing_data_flags": row.get("missing_data_flags"),
            "updated_at": row.get("updated_at"),
        })
    return dim_rows


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


def _source_query(
    client: bigquery.Client,
    dataset_id: str,
    table_name: str,
    select_exprs: list[str],
    *,
    where_sql: str = "",
    query_name: str,
    allow_large_query: bool,
) -> pd.DataFrame:
    table_id = f"`{client.project}.{dataset_id}.{table_name}`"
    where_clause = f"\nWHERE {where_sql}" if where_sql else ""
    sql = f"""
    SELECT
        {", ".join(select_exprs)}
    FROM {table_id}
    {where_clause}
    """
    return query_to_dataframe(
        client,
        sql,
        component="player_identity",
        query_name=query_name,
        allow_large_query=allow_large_query,
    )


def fetch_source_records(
    client: bigquery.Client,
    dataset_id: str,
    *,
    allow_large_query: bool = False,
) -> list[PlayerSourceRecord]:
    frames: list[pd.DataFrame] = []

    for table_name, builder in (
        ("sleeper_players_current", _fetch_sleeper_players_current),
        ("player_rosters", _fetch_player_rosters),
        ("sleeper_roster_players", _fetch_sleeper_roster_players),
        ("analytics_pigskin_rankings", _fetch_pigskin_rankings),
        ("analytics_player_weekly_truth", _fetch_player_weekly_truth),
        ("depth_charts", _fetch_depth_charts),
        ("market_values", _fetch_market_values),
    ):
        if not table_exists(client, dataset_id, table_name):
            logger.info("Skipping missing optional identity source table: %s", table_name)
            continue
        frame = builder(client, dataset_id, allow_large_query=allow_large_query)
        if not frame.empty:
            frames.append(frame)

    if not frames:
        return []
    return records_from_dataframe(pd.concat(frames, ignore_index=True))


def _fetch_sleeper_players_current(client, dataset_id, *, allow_large_query):
    columns = table_columns(client, dataset_id, "sleeper_players_current")
    where_sql = "snapshot_at = (SELECT MAX(snapshot_at) FROM `{}.{}.sleeper_players_current`)".format(client.project, dataset_id) if "snapshot_at" in columns else ""
    select_exprs = [
        "'sleeper_players_current' AS source",
        _expr(columns, ["sleeper_player_id"], "source_player_id"),
        _expr(columns, ["sleeper_player_id"], "sleeper_player_id"),
        _expr(columns, ["gsis_id"], "gsis_id"),
        _expr(columns, ["player_name", "full_name"], "display_name"),
        _expr(columns, ["player_name", "full_name"], "full_name"),
        _expr(columns, ["position"], "position"),
        _expr(columns, ["fantasy_positions_json"], "fantasy_positions"),
        _expr(columns, ["team"], "current_team"),
        _expr(columns, ["status"], "active_status"),
        _expr(columns, ["snapshot_at"], "source_updated_at", "TIMESTAMP"),
    ]
    return _source_query(client, dataset_id, "sleeper_players_current", select_exprs, where_sql=where_sql, query_name="identity_sleeper_players_current", allow_large_query=allow_large_query)


def _fetch_player_rosters(client, dataset_id, *, allow_large_query):
    columns = table_columns(client, dataset_id, "player_rosters")
    where_sql = "season = (SELECT MAX(season) FROM `{}.{}.player_rosters`)".format(client.project, dataset_id) if "season" in columns else ""
    select_exprs = [
        "'player_rosters' AS source",
        _expr(columns, ["gsis_id"], "source_player_id"),
        _expr(columns, ["gsis_id"], "gsis_id"),
        _expr(columns, ["sleeper_id", "sleeper_player_id"], "sleeper_player_id"),
        _expr(columns, ["pfr_id"], "pfr_id"),
        _expr(columns, ["espn_id"], "espn_id"),
        _expr(columns, ["yahoo_id"], "yahoo_id"),
        _expr(columns, ["display_name", "full_name", "player_name"], "display_name"),
        _expr(columns, ["display_name", "full_name", "player_name"], "full_name"),
        _expr(columns, ["first_name"], "first_name"),
        _expr(columns, ["last_name"], "last_name"),
        _expr(columns, ["position"], "position"),
        _expr(columns, ["latest_team", "team"], "current_team"),
        _expr(columns, ["status"], "active_status"),
        _expr(columns, ["rookie_season", "rookie_year", "draft_year"], "rookie_year", "INT64"),
        _expr(columns, ["birth_date"], "birth_date", "DATE"),
        "CURRENT_TIMESTAMP() AS source_updated_at",
    ]
    return _source_query(client, dataset_id, "player_rosters", select_exprs, where_sql=where_sql, query_name="identity_player_rosters", allow_large_query=allow_large_query)


def _fetch_sleeper_roster_players(client, dataset_id, *, allow_large_query):
    columns = table_columns(client, dataset_id, "sleeper_roster_players")
    where_sql = "snapshot_at = (SELECT MAX(snapshot_at) FROM `{}.{}.sleeper_roster_players`)".format(client.project, dataset_id) if "snapshot_at" in columns else ""
    select_exprs = [
        "'sleeper_roster_players' AS source",
        _expr(columns, ["sleeper_player_id"], "source_player_id"),
        _expr(columns, ["sleeper_player_id"], "sleeper_player_id"),
        _expr(columns, ["gsis_id"], "gsis_id"),
        _expr(columns, ["player_name"], "display_name"),
        _expr(columns, ["player_name"], "full_name"),
        _expr(columns, ["position"], "position"),
        _expr(columns, ["team"], "current_team"),
        _expr(columns, ["status"], "active_status"),
        _expr(columns, ["snapshot_at"], "source_updated_at", "TIMESTAMP"),
    ]
    return _source_query(client, dataset_id, "sleeper_roster_players", select_exprs, where_sql=where_sql, query_name="identity_sleeper_roster_players", allow_large_query=allow_large_query)


def _fetch_pigskin_rankings(client, dataset_id, *, allow_large_query):
    columns = table_columns(client, dataset_id, "analytics_pigskin_rankings")
    where_parts = []
    if "is_active" in columns:
        where_parts.append("is_active IS TRUE")
    if "season" in columns:
        where_parts.append("season = (SELECT MAX(season) FROM `{}.{}.analytics_pigskin_rankings`)".format(client.project, dataset_id))
    select_exprs = [
        "'analytics_pigskin_rankings' AS source",
        _expr(columns, ["player_id", "sleeper_player_id"], "source_player_id"),
        _expr(columns, ["player_id"], "gsis_id"),
        _expr(columns, ["sleeper_player_id"], "sleeper_player_id"),
        _expr(columns, ["player_name"], "display_name"),
        _expr(columns, ["player_name"], "full_name"),
        _expr(columns, ["position"], "position"),
        _expr(columns, ["current_team", "sleeper_team"], "current_team"),
        _expr(columns, ["roster_status", "sleeper_status"], "active_status"),
        _expr(columns, ["generated_at", "adjudicated_at"], "source_updated_at", "TIMESTAMP"),
    ]
    return _source_query(client, dataset_id, "analytics_pigskin_rankings", select_exprs, where_sql=" AND ".join(where_parts), query_name="identity_pigskin_rankings", allow_large_query=allow_large_query)


def _fetch_player_weekly_truth(client, dataset_id, *, allow_large_query):
    columns = table_columns(client, dataset_id, "analytics_player_weekly_truth")
    where_sql = "season = (SELECT MAX(season) FROM `{}.{}.analytics_player_weekly_truth`)".format(client.project, dataset_id) if "season" in columns else ""
    select_exprs = [
        "'analytics_player_weekly_truth' AS source",
        _expr(columns, ["player_id"], "source_player_id"),
        _expr(columns, ["player_id"], "gsis_id"),
        _expr(columns, ["player_full_name", "player_display_name", "player_name"], "display_name"),
        _expr(columns, ["player_full_name", "player_display_name", "player_name"], "full_name"),
        _expr(columns, ["position"], "position"),
        _expr(columns, ["current_team", "team"], "current_team"),
        _expr(columns, ["roster_status"], "active_status"),
        "CURRENT_TIMESTAMP() AS source_updated_at",
    ]
    return _source_query(client, dataset_id, "analytics_player_weekly_truth", select_exprs, where_sql=where_sql, query_name="identity_player_weekly_truth", allow_large_query=allow_large_query)


def _fetch_depth_charts(client, dataset_id, *, allow_large_query):
    columns = table_columns(client, dataset_id, "depth_charts")
    where_parts = []
    if "season" in columns:
        where_parts.append("season = (SELECT MAX(season) FROM `{}.{}.depth_charts`)".format(client.project, dataset_id))
    if "dt" in columns:
        where_parts.append("dt = (SELECT MAX(dt) FROM `{}.{}.depth_charts`)".format(client.project, dataset_id))
    select_exprs = [
        "'depth_charts' AS source",
        _expr(columns, ["gsis_id"], "source_player_id"),
        _expr(columns, ["gsis_id"], "gsis_id"),
        _expr(columns, ["full_name", "player_name", "name"], "display_name"),
        _expr(columns, ["full_name", "player_name", "name"], "full_name"),
        _expr(columns, ["position"], "position"),
        _expr(columns, ["team"], "current_team"),
        _expr(columns, ["dt"], "source_updated_at", "TIMESTAMP"),
    ]
    return _source_query(client, dataset_id, "depth_charts", select_exprs, where_sql=" AND ".join(where_parts), query_name="identity_depth_charts", allow_large_query=allow_large_query)


def _fetch_market_values(client, dataset_id, *, allow_large_query):
    columns = table_columns(client, dataset_id, "market_values")
    select_exprs = [
        "'market_values' AS source",
        _expr(columns, ["player_display_name"], "source_player_id"),
        _expr(columns, ["player_display_name"], "display_name"),
        _expr(columns, ["player_display_name"], "full_name"),
        _expr(columns, ["position"], "position"),
        _expr(columns, ["team"], "current_team"),
        "CURRENT_TIMESTAMP() AS source_updated_at",
    ]
    return _source_query(client, dataset_id, "market_values", select_exprs, query_name="identity_market_values", allow_large_query=allow_large_query)


def records_from_dataframe(frame: pd.DataFrame) -> list[PlayerSourceRecord]:
    records = []
    for row in frame.to_dict("records"):
        records.append(PlayerSourceRecord(
            source=_clean_string(row.get("source")) or "unknown",
            source_player_id=_clean_string(row.get("source_player_id")),
            gsis_id=_clean_string(row.get("gsis_id")),
            sleeper_player_id=_clean_string(row.get("sleeper_player_id")),
            pfr_id=_clean_string(row.get("pfr_id")),
            espn_id=_clean_string(row.get("espn_id")),
            yahoo_id=_clean_string(row.get("yahoo_id")),
            nflverse_id=_clean_string(row.get("nflverse_id")),
            fantasypros_id=_clean_string(row.get("fantasypros_id")),
            full_name=_clean_string(row.get("full_name")),
            display_name=_clean_string(row.get("display_name")),
            first_name=_clean_string(row.get("first_name")),
            last_name=_clean_string(row.get("last_name")),
            position=_clean_string(row.get("position")),
            fantasy_positions=_clean_string(row.get("fantasy_positions")),
            current_team=_clean_string(row.get("current_team")),
            previous_team=_clean_string(row.get("previous_team")),
            active_status=_clean_string(row.get("active_status")),
            rookie_year=_clean_int(row.get("rookie_year")),
            birth_date=row.get("birth_date"),
            source_updated_at=row.get("source_updated_at"),
        ))
    return records


def fetch_overrides(client: bigquery.Client, dataset_id: str) -> list[PlayerIdentityOverride]:
    if not table_exists(client, dataset_id, "player_identity_overrides"):
        return []
    sql = f"""
    SELECT source, source_player_id, player_id_internal, reason, active
    FROM `{client.project}.{dataset_id}.player_identity_overrides`
    WHERE active IS TRUE
    """
    frame = query_to_dataframe(
        client,
        sql,
        component="player_identity",
        query_name="identity_overrides",
    )
    return [
        PlayerIdentityOverride(
            source=_clean_string(row.get("source")) or "",
            source_player_id=_clean_string(row.get("source_player_id")) or "",
            player_id_internal=_clean_string(row.get("player_id_internal")) or "",
            reason=_clean_string(row.get("reason")),
            active=bool(row.get("active")),
        )
        for row in frame.to_dict("records")
        if row.get("source") and row.get("source_player_id") and row.get("player_id_internal")
    ]


def _bridge_schema() -> list[bigquery.SchemaField]:
    return [
        bigquery.SchemaField("player_id_internal", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("gsis_id", "STRING"),
        bigquery.SchemaField("sleeper_player_id", "STRING"),
        bigquery.SchemaField("pfr_id", "STRING"),
        bigquery.SchemaField("espn_id", "STRING"),
        bigquery.SchemaField("yahoo_id", "STRING"),
        bigquery.SchemaField("nflverse_id", "STRING"),
        bigquery.SchemaField("fantasypros_id", "STRING"),
        bigquery.SchemaField("full_name", "STRING"),
        bigquery.SchemaField("normalized_name", "STRING"),
        bigquery.SchemaField("display_name", "STRING"),
        bigquery.SchemaField("first_name", "STRING"),
        bigquery.SchemaField("last_name", "STRING"),
        bigquery.SchemaField("position", "STRING"),
        bigquery.SchemaField("fantasy_positions", "STRING"),
        bigquery.SchemaField("current_team", "STRING"),
        bigquery.SchemaField("previous_team", "STRING"),
        bigquery.SchemaField("active_status", "STRING"),
        bigquery.SchemaField("rookie_year", "INTEGER"),
        bigquery.SchemaField("birth_date", "DATE"),
        bigquery.SchemaField("source_confidence", "FLOAT"),
        bigquery.SchemaField("match_method", "STRING"),
        bigquery.SchemaField("source_priority", "STRING"),
        bigquery.SchemaField("source_freshness_json", "STRING"),
        bigquery.SchemaField("missing_data_flags", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
    ]


def _dim_schema() -> list[bigquery.SchemaField]:
    return [
        bigquery.SchemaField("player_id_internal", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("display_name", "STRING"),
        bigquery.SchemaField("full_name", "STRING"),
        bigquery.SchemaField("normalized_name", "STRING"),
        bigquery.SchemaField("position", "STRING"),
        bigquery.SchemaField("fantasy_positions", "STRING"),
        bigquery.SchemaField("current_team", "STRING"),
        bigquery.SchemaField("active_status", "STRING"),
        bigquery.SchemaField("sleeper_player_id", "STRING"),
        bigquery.SchemaField("gsis_id", "STRING"),
        bigquery.SchemaField("pfr_id", "STRING"),
        bigquery.SchemaField("espn_id", "STRING"),
        bigquery.SchemaField("yahoo_id", "STRING"),
        bigquery.SchemaField("rookie_year", "INTEGER"),
        bigquery.SchemaField("birth_date", "DATE"),
        bigquery.SchemaField("age", "FLOAT"),
        bigquery.SchemaField("source_confidence", "FLOAT"),
        bigquery.SchemaField("match_method", "STRING"),
        bigquery.SchemaField("source_freshness_json", "STRING"),
        bigquery.SchemaField("missing_data_flags", "STRING"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
    ]


def _load_table(client: bigquery.Client, table_id: str, rows: list[dict[str, Any]], schema: list[bigquery.SchemaField]) -> None:
    frame = pd.DataFrame(rows)
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    job = client.load_table_from_dataframe(frame, table_id, job_config=job_config)
    job.result()
    logger.info("Loaded %s rows into %s", len(frame), table_id)


def materialize_player_identity(
    client: bigquery.Client,
    *,
    dataset_id: str = DEFAULT_DATASET,
    dry_run: bool = False,
    allow_large_query: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_records = fetch_source_records(client, dataset_id, allow_large_query=allow_large_query)
    overrides = fetch_overrides(client, dataset_id)
    bridge_rows = build_identity_rows(source_records, overrides)
    dim_rows = build_dim_players_current_rows(bridge_rows)

    logger.info("Built %s identity rows and %s dim rows", len(bridge_rows), len(dim_rows))
    if dry_run:
        return bridge_rows, dim_rows
    if not bridge_rows:
        logger.warning("No identity rows built. Skipping writes to avoid truncating existing identity tables.")
        return bridge_rows, dim_rows

    _load_table(
        client,
        f"{client.project}.{dataset_id}.player_identity_bridge",
        bridge_rows,
        _bridge_schema(),
    )
    _load_table(
        client,
        f"{client.project}.{dataset_id}.dim_players_current",
        dim_rows,
        _dim_schema(),
    )
    return bridge_rows, dim_rows


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical player identity bridge tables.")
    parser.add_argument("--project", default=get_bigquery_project())
    parser.add_argument("--dataset", default=get_bigquery_dataset())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-large-query", action="store_true")
    parser.add_argument("--log-level", default=os.environ.get("LOG_LEVEL", "INFO"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    client = bigquery.Client(project=args.project)
    bridge_rows, dim_rows = materialize_player_identity(
        client,
        dataset_id=args.dataset,
        dry_run=args.dry_run,
        allow_large_query=args.allow_large_query,
    )
    print(f"player_identity_bridge rows: {len(bridge_rows)}")
    print(f"dim_players_current rows: {len(dim_rows)}")


if __name__ == "__main__":
    main()
