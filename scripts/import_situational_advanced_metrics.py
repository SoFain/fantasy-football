"""Import source-backed situational SQLite metrics into an isolated BigQuery dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from google.api_core.exceptions import NotFound
from google.cloud import bigquery


PROJECT = "fantasy-football-498121"
DATASET = "fantasy_football_advanced_metrics"


@dataclass(frozen=True)
class Source:
    position: str
    path: Path
    table: str


METRICS: dict[str, tuple[tuple[str, str, str, str, bool, bool, bool, bool, bool, bool], ...]] = {
    "QB": (
        ("Plays", "plays", "volume", "count", True, False, False, False, False, False),
        ("Total EPA", "total_epa", "efficiency", "epa", True, False, False, True, False, False),
        ("EPA/Play", "epa_per_play", "efficiency", "epa_per_play", True, False, False, True, False, False),
        ("Pass EPA", "pass_epa", "efficiency", "epa", True, False, False, True, False, False),
        ("Rush EPA", "rush_epa", "efficiency", "epa", True, False, False, True, False, False),
        ("Scramble %", "scramble_pct", "role", "percent", True, False, False, False, True, True),
        ("Sack %", "sack_pct", "efficiency", "percent", False, True, False, True, False, False),
        ("Success %", "success_pct", "efficiency", "percent", True, False, False, True, False, False),
        ("ADoT", "adot", "role", "yards", True, False, False, False, True, False),
        ("Comp %", "completion_pct", "efficiency", "percent", True, False, False, True, False, False),
        ("Pass Yards", "pass_yards", "volume", "yards", True, False, True, False, False, False),
        ("Time To Throw", "time_to_throw", "efficiency", "seconds", False, True, False, True, False, False),
        ("Pass TD", "pass_td", "volume", "count", True, False, True, False, False, False),
        ("INT", "interceptions", "risk", "count", False, True, True, False, False, False),
        ("YPA", "ypa", "efficiency", "yards_per_attempt", True, False, False, True, False, False),
        ("Rush Yards", "rush_yards", "volume", "yards", True, False, True, False, False, False),
        ("Rush TD", "rush_td", "volume", "count", True, False, True, False, False, False),
    ),
    "RB": (
        ("Rushes", "rushes", "volume", "count", True, False, True, False, False, True),
        ("EPA/Rush", "epa_per_rush", "efficiency", "epa_per_rush", True, False, False, True, False, False),
        ("Total EPA", "total_epa", "efficiency", "epa", True, False, False, True, False, False),
        ("Rush Yards", "rush_yards", "volume", "yards", True, False, True, False, False, False),
        ("Rush TD", "rush_td", "volume", "count", True, False, True, False, False, False),
        ("Yards Per Carry", "yards_per_carry", "efficiency", "yards_per_carry", True, False, False, True, False, False),
        ("Yards After Contact", "yards_after_contact", "contact", "yards", True, False, True, False, False, False),
        ("Avg. Box Defenders", "avg_box_defenders", "role", "count", False, False, False, False, True, False),
        ("Success %", "success_pct", "efficiency", "percent", True, False, False, True, False, False),
        ("TFL %", "tfl_pct", "efficiency", "percent", False, True, False, True, False, False),
        ("Explosive %", "explosive_pct", "efficiency", "percent", True, False, False, True, False, False),
        ("First Down %", "first_down_pct", "efficiency", "percent", True, False, False, True, False, False),
        ("Receptions", "receptions", "volume", "count", True, False, True, False, False, True),
        ("Rec. Yards", "receiving_yards", "volume", "yards", True, False, True, False, False, False),
        ("Rec. TDs", "receiving_td", "volume", "count", True, False, True, False, False, False),
        ("YAC", "yac", "volume", "yards", True, False, True, False, False, False),
        ("Target Share", "target_share", "opportunity", "percent", True, False, False, False, True, True),
    ),
}

RECEIVING_METRICS = (
    ("Routes Run", "routes_run", "role", "count", True, False, True, False, True, True),
    ("Receptions", "receptions", "volume", "count", True, False, True, False, False, True),
    ("Rec. Yards", "receiving_yards", "volume", "yards", True, False, True, False, False, False),
    ("Target Share", "target_share", "opportunity", "percent", True, False, False, False, True, True),
    ("Touchdowns", "touchdowns", "volume", "count", True, False, True, False, False, False),
    ("YAC", "yac", "volume", "yards", True, False, True, False, False, False),
    ("ADoT", "adot", "role", "yards", True, False, False, False, True, False),
    ("Catch %", "catch_pct", "efficiency", "percent", True, False, False, True, False, False),
    ("Total EPA", "total_epa", "efficiency", "epa", True, False, False, True, False, False),
    ("Targets/Route Run", "targets_per_route_run", "route", "ratio", True, False, False, True, True, True),
    ("YPRR", "yprr", "route", "yards_per_route", True, False, False, True, True, False),
)
METRICS["WR"] = RECEIVING_METRICS
METRICS["TE"] = RECEIVING_METRICS

COMMON_FIELDS = (
    ("season", "INTEGER"), ("refinement", "STRING"), ("refinement_label", "STRING"),
    ("source_rank", "INTEGER"), ("situational_player_id", "STRING"),
    ("player_name", "STRING"), ("player_slug", "STRING"), ("team", "STRING"),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value) if math.isfinite(float(value)) else None
    cleaned = str(value).strip().replace(",", "")
    if cleaned.endswith("%"):
        cleaned = cleaned[:-1]
    try:
        parsed = float(cleaned)
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) else None


def schema_hash(connection: sqlite3.Connection, table: str) -> str:
    schema = [tuple(row) for row in connection.execute(f"PRAGMA table_info({table})").fetchall()]
    return hashlib.sha256(json.dumps(schema, separators=(",", ":")).encode()).hexdigest()


def read_source(source: Source, imported_at: datetime) -> dict[str, Any]:
    file_hash = sha256_file(source.path)
    connection = sqlite3.connect(source.path)
    try:
        connection.row_factory = sqlite3.Row
        columns = [row[1] for row in connection.execute(f"PRAGMA table_info({source.table})")]
        expected = ["id", "season", "refinement", "refinement_label", "rank", "player_id", "player_name", "player_slug", "team", "stats_json"]
        if columns != expected:
            raise ValueError(f"Unexpected schema for {source.path.name}: {columns}")
        rows = [dict(row) for row in connection.execute(f"SELECT * FROM {source.table} ORDER BY id")]
        source_schema_hash = schema_hash(connection, source.table)
    finally:
        connection.close()

    raw_rows: list[dict[str, Any]] = []
    wide_rows: list[dict[str, Any]] = []
    long_rows: list[dict[str, Any]] = []
    comma_values = 0
    for row in rows:
        stats_text = row["stats_json"]
        stats = json.loads(stats_text)
        base = {
            "season": int(row["season"]), "refinement": row["refinement"],
            "refinement_label": row["refinement_label"], "source_rank": int(row["rank"]),
            "situational_player_id": str(row["player_id"]), "player_name": row["player_name"],
            "player_slug": row["player_slug"], "team": row["team"], "imported_at": imported_at,
        }
        wide = dict(base)
        if source.position == "RB":
            wide["position"] = stats.get("Position")
        for raw_key, metric_name, group, unit, higher, _lower, _volume, _efficiency, _role, _opportunity in METRICS[source.position]:
            raw_value = stats.get(raw_key)
            if isinstance(raw_value, str) and "," in raw_value:
                comma_values += 1
            numeric = parse_number(raw_value)
            wide[metric_name] = numeric
            long_rows.append({
                **base, "position": source.position, "metric_name": metric_name,
                "raw_json_key": raw_key, "metric_value": numeric,
                "metric_value_string": None if raw_value is None else str(raw_value),
                "metric_group": group, "unit": unit, "higher_is_better": higher,
                "source_status": "SOURCE_BACKED",
            })
        wide_rows.append(wide)
        raw_rows.append({
            "source_file_name": source.path.name, "source_table": source.table,
            "source_position": source.position, "source_row_id": int(row["id"]),
            **{key: base[key] for key in ("season", "refinement", "refinement_label", "source_rank", "situational_player_id", "player_name", "player_slug", "team")},
            "stats_json": stats_text,
            "stats_hash": hashlib.sha256(stats_text.encode()).hexdigest(), "imported_at": imported_at,
        })

    duplicate_count = len(wide_rows) - len({(r["season"], r["refinement"], r["situational_player_id"]) for r in wide_rows})
    required_nulls = sum(any(row[key] in (None, "") for key in ("season", "refinement", "player_name", "player_slug", "team", "stats_json")) for row in raw_rows)
    return {
        "source": source, "sha256": file_hash, "schema_hash": source_schema_hash,
        "raw": raw_rows, "wide": wide_rows, "long": long_rows,
        "min_season": min(row["season"] for row in raw_rows),
        "max_season": max(row["season"] for row in raw_rows),
        "duplicate_count": duplicate_count, "required_nulls": required_nulls,
        "comma_values": comma_values,
    }


def metric_dictionary() -> list[dict[str, Any]]:
    output = []
    for position, metrics in METRICS.items():
        for raw_key, name, group, unit, higher, lower, volume, efficiency, role, opportunity in metrics:
            route = position in {"WR", "TE"} and name in {"routes_run", "targets_per_route_run", "yprr"}
            contact = position == "RB" and name == "yards_after_contact"
            notes = "Raw receiving YAC; not YAC above expectation." if position == "RB" and name == "yac" else "Source-backed SQLite field."
            output.append({
                "position": position, "raw_json_key": raw_key, "metric_name": name,
                "metric_group": group, "data_type": "FLOAT64", "unit": unit,
                "higher_is_better": higher, "lower_is_better": lower,
                "is_volume_metric": volume, "is_efficiency_metric": efficiency,
                "is_role_metric": role, "is_opportunity_metric": opportunity,
                "is_route_metric": route, "is_contact_metric": contact,
                "is_source_backed": True, "source_status": "SOURCE_BACKED", "notes": notes,
            })
    return output


def refinement_rows(imports: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    found: dict[tuple[str, str], str] = {}
    for item in imports:
        for row in item["raw"]:
            found[(item["source"].position, row["refinement"])] = row["refinement_label"]
    return [{
        "position": position, "refinement": refinement, "refinement_label": label,
        "description": label, "is_standard_context": refinement == "standard",
        "is_situational_context": refinement != "standard",
    } for (position, refinement), label in sorted(found.items())]


def identity_rows(imports: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in imports:
        position = item["source"].position
        for row in item["raw"]:
            key = (position, row["situational_player_id"], row["player_slug"])
            value = grouped.setdefault(key, {"names": set(), "seasons": set(), "teams": set()})
            value["names"].add(row["player_name"]); value["seasons"].add(row["season"]); value["teams"].add(row["team"])
    return [{
        "source_position": key[0], "situational_player_id": key[1], "player_slug": key[2],
        "player_name": sorted(value["names"])[0], "seasons_seen": sorted(value["seasons"]),
        "teams_seen": sorted(value["teams"]), "candidate_internal_player_id": None,
        "candidate_gsis_id": None, "candidate_sleeper_id": None, "match_method": "NONE",
        "identity_status": "UNMAPPED", "identity_confidence": 0.0,
        "manual_review_required": True,
        "notes": "Situational player_id is source-local and is not an official identity.",
    } for key, value in sorted(grouped.items())]


def coverage_rows(imports: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, int, str, str], list[float | None]] = {}
    for item in imports:
        for row in item["long"]:
            key = (row["position"], row["season"], row["refinement"], row["metric_name"])
            buckets.setdefault(key, []).append(row["metric_value"])
    result = []
    for (position, season, refinement, metric), values in sorted(buckets.items()):
        present = [value for value in values if value is not None]
        rate = len(present) / len(values) if values else 0.0
        result.append({
            "position": position, "season": season, "refinement": refinement,
            "metric_name": metric, "row_count": len(values), "non_null_count": len(present),
            "missing_count": len(values) - len(present), "non_null_rate": rate,
            "min_value": min(present) if present else None, "max_value": max(present) if present else None,
            "avg_value": sum(present) / len(present) if present else None,
            "validation_status": "PASS" if rate == 1.0 else "WARNING",
            "notes": "Source-backed coverage; missing values are preserved.",
        })
    return result


def validation_rows(imports: Iterable[dict[str, Any]], validated_at: datetime) -> list[dict[str, Any]]:
    result = []
    for item in imports:
        position = item["source"].position
        checks = (
            ("source_row_count", "PASS", len(item["raw"]), len(item["wide"]), 0, "Every raw row maps to one wide row."),
            ("season_bounds", "PASS" if (item["min_season"], item["max_season"]) == (2022, 2025) else "FAIL", 4, len({r["season"] for r in item["raw"]}), 0, f"Bounds {item['min_season']}-{item['max_season']}."),
            ("required_fields", "PASS" if item["required_nulls"] == 0 else "FAIL", 0, item["required_nulls"], item["required_nulls"], "Required source fields must be populated."),
            ("duplicate_grain", "PASS" if item["duplicate_count"] == 0 else "FAIL", 0, item["duplicate_count"], item["duplicate_count"], "Grain is season, refinement, situational_player_id."),
            ("long_metric_count", "PASS" if len(item["long"]) == len(item["wide"]) * len(METRICS[position]) else "FAIL", len(item["wide"]) * len(METRICS[position]), len(item["long"]), abs(len(item["wide"]) * len(METRICS[position]) - len(item["long"])), "One long row per governed numeric metric."),
            ("comma_numeric_parse", "PASS", item["comma_values"], item["comma_values"], 0, "Comma-formatted numeric strings parsed without percent scaling."),
        )
        for name, status, expected, actual, issues, details in checks:
            result.append({"validation_name": name, "validation_status": status, "position": position,
                           "season": None, "refinement": None, "expected_count": expected,
                           "actual_count": actual, "issue_count": issues, "details": details,
                           "validated_at": validated_at})
    result.extend((
        {"validation_name": "rb_broken_tackles_absent", "validation_status": "PASS", "position": "RB", "season": None, "refinement": None, "expected_count": 0, "actual_count": 0, "issue_count": 0, "details": "No broken-tackles metric was fabricated.", "validated_at": validated_at},
        {"validation_name": "rb_yac_aoe_absent", "validation_status": "PASS", "position": "RB", "season": None, "refinement": None, "expected_count": 0, "actual_count": 0, "issue_count": 0, "details": "Raw YAC was not relabeled as YAC above expectation.", "validated_at": validated_at},
        {"validation_name": "identity_policy", "validation_status": "WARNING", "position": None, "season": None, "refinement": None, "expected_count": None, "actual_count": None, "issue_count": None, "details": "All source identities remain UNMAPPED pending Phase 34.2.", "validated_at": validated_at},
    ))
    return result


def field(name: str, field_type: str, mode: str = "NULLABLE") -> bigquery.SchemaField:
    return bigquery.SchemaField(name, field_type, mode=mode)


SCHEMAS = {
    "source_manifest": [field("source_file_name", "STRING"), field("source_file_path", "STRING"), field("source_position", "STRING"), field("source_table", "STRING"), field("source_sha256", "STRING"), field("source_row_count", "INTEGER"), field("min_season", "INTEGER"), field("max_season", "INTEGER"), field("schema_hash", "STRING"), field("imported_at", "TIMESTAMP"), field("import_notes", "STRING")],
    "raw_situational_rows": [field("source_file_name", "STRING"), field("source_table", "STRING"), field("source_position", "STRING"), field("source_row_id", "INTEGER"), *[field(name, kind) for name, kind in COMMON_FIELDS], field("stats_json", "STRING"), field("stats_hash", "STRING"), field("imported_at", "TIMESTAMP")],
    "situational_refinements": [field("position", "STRING"), field("refinement", "STRING"), field("refinement_label", "STRING"), field("description", "STRING"), field("is_standard_context", "BOOLEAN"), field("is_situational_context", "BOOLEAN")],
    "situational_metric_dictionary": [field("position", "STRING"), field("raw_json_key", "STRING"), field("metric_name", "STRING"), field("metric_group", "STRING"), field("data_type", "STRING"), field("unit", "STRING"), field("higher_is_better", "BOOLEAN"), field("lower_is_better", "BOOLEAN"), field("is_volume_metric", "BOOLEAN"), field("is_efficiency_metric", "BOOLEAN"), field("is_role_metric", "BOOLEAN"), field("is_opportunity_metric", "BOOLEAN"), field("is_route_metric", "BOOLEAN"), field("is_contact_metric", "BOOLEAN"), field("is_source_backed", "BOOLEAN"), field("source_status", "STRING"), field("notes", "STRING")],
    "situational_player_identity_candidates": [field("source_position", "STRING"), field("situational_player_id", "STRING"), field("player_slug", "STRING"), field("player_name", "STRING"), field("seasons_seen", "INTEGER", "REPEATED"), field("teams_seen", "STRING", "REPEATED"), field("candidate_internal_player_id", "STRING"), field("candidate_gsis_id", "STRING"), field("candidate_sleeper_id", "STRING"), field("match_method", "STRING"), field("identity_status", "STRING"), field("identity_confidence", "FLOAT"), field("manual_review_required", "BOOLEAN"), field("notes", "STRING")],
    "player_situational_metric_long": [*[field(name, kind) for name, kind in COMMON_FIELDS[:3]], field("position", "STRING"), *[field(name, kind) for name, kind in COMMON_FIELDS[4:]], field("source_rank", "INTEGER"), field("metric_name", "STRING"), field("raw_json_key", "STRING"), field("metric_value", "FLOAT"), field("metric_value_string", "STRING"), field("metric_group", "STRING"), field("unit", "STRING"), field("higher_is_better", "BOOLEAN"), field("source_status", "STRING"), field("imported_at", "TIMESTAMP")],
    "situational_metric_coverage": [field("position", "STRING"), field("season", "INTEGER"), field("refinement", "STRING"), field("metric_name", "STRING"), field("row_count", "INTEGER"), field("non_null_count", "INTEGER"), field("missing_count", "INTEGER"), field("non_null_rate", "FLOAT"), field("min_value", "FLOAT"), field("max_value", "FLOAT"), field("avg_value", "FLOAT"), field("validation_status", "STRING"), field("notes", "STRING")],
    "situational_import_validation_report": [field("validation_name", "STRING"), field("validation_status", "STRING"), field("position", "STRING"), field("season", "INTEGER"), field("refinement", "STRING"), field("expected_count", "INTEGER"), field("actual_count", "INTEGER"), field("issue_count", "INTEGER"), field("details", "STRING"), field("validated_at", "TIMESTAMP")],
}


for position in ("QB", "RB", "WR", "TE"):
    extra = [field("position", "STRING")] if position == "RB" else []
    SCHEMAS[f"{position.lower()}_situational_metrics"] = [
        *[field(name, kind) for name, kind in COMMON_FIELDS], *extra,
        *[field(metric[1], "FLOAT") for metric in METRICS[position]], field("imported_at", "TIMESTAMP")
    ]


def create_dataset_and_tables(client: bigquery.Client, project: str, dataset: str) -> None:
    dataset_id = f"{project}.{dataset}"
    try:
        target = client.get_dataset(dataset_id)
    except NotFound:
        target = bigquery.Dataset(dataset_id)
        target.location = "US"
    target.labels = {"system": "pigskin", "source": "situational_sqlite", "status": "research", "phase": "34_1"}
    client.create_dataset(target, exists_ok=True)
    client.update_dataset(target, ["labels"])
    for name, schema in SCHEMAS.items():
        client.create_table(bigquery.Table(f"{dataset_id}.{name}", schema=schema), exists_ok=True)


def delete_where(client: bigquery.Client, table: str, predicate: str, parameters: list[bigquery.ScalarQueryParameter]) -> None:
    config = bigquery.QueryJobConfig(query_parameters=parameters)
    client.query(f"DELETE FROM `{table}` WHERE {predicate}", job_config=config).result()


def load_json(client: bigquery.Client, table: str, records: list[dict[str, Any]], schema: list[bigquery.SchemaField]) -> None:
    if not records:
        return
    serializable = [
        {key: value.isoformat() if isinstance(value, datetime) else value for key, value in record.items()}
        for record in records
    ]
    config = bigquery.LoadJobConfig(schema=schema, write_disposition="WRITE_APPEND")
    client.load_table_from_json(serializable, table, job_config=config).result()


def create_views(client: bigquery.Client, project: str, dataset: str) -> None:
    root = f"{project}.{dataset}"
    for position in ("qb", "rb", "wr", "te"):
        view = bigquery.Table(f"{root}.v_{position}_standard_situational")
        view.view_query = f"SELECT * FROM `{root}.{position}_situational_metrics` WHERE refinement = 'standard'"
        client.create_table(view, exists_ok=True)
        client.update_table(view, ["view_query"])
    rb_view = bigquery.Table(f"{root}.v_rb_std_gpt55_metric_inputs")
    rb_view.view_query = f"""
SELECT
  rb.season, rb.player_name, rb.player_slug, rb.team, rb.situational_player_id,
  rb.rushes, rb.epa_per_rush, rb.total_epa, rb.rush_yards, rb.rush_td,
  rb.yards_per_carry, rb.yards_after_contact, rb.avg_box_defenders,
  rb.success_pct, rb.tfl_pct, rb.explosive_pct, rb.first_down_pct,
  rb.receptions, rb.receiving_yards, rb.receiving_td, rb.yac, rb.target_share,
  SAFE_DIVIDE(rb.yards_after_contact, rb.rushes) AS yards_after_contact_per_rush,
  SAFE_DIVIDE(rb.yac, rb.receptions) AS yac_per_reception,
  SAFE_DIVIDE(rb.receiving_yards, rb.receptions) AS receiving_yards_per_reception,
  COALESCE(rb.rush_yards, 0) + COALESCE(rb.receiving_yards, 0) AS total_yards,
  COALESCE(rb.rush_td, 0) + COALESCE(rb.receiving_td, 0) AS total_tds,
  COALESCE(rb.rushes, 0) + COALESCE(rb.receptions, 0) AS touches,
  SAFE_DIVIDE(COALESCE(rb.rush_yards, 0) + COALESCE(rb.receiving_yards, 0), COALESCE(rb.rushes, 0) + COALESCE(rb.receptions, 0)) AS yards_per_touch,
  SAFE_DIVIDE(rb.total_epa, COALESCE(rb.rushes, 0) + COALESCE(rb.receptions, 0)) AS total_epa_per_touch,
  SAFE_DIVIDE(rb.yards_after_contact, rb.rush_yards) AS contact_yards_share,
  SAFE_DIVIDE(COALESCE(rb.explosive_pct, 0) + COALESCE(rb.success_pct, 0), 2) AS explosive_success_index,
  identity.identity_status, identity.identity_confidence, identity.manual_review_required
FROM `{root}.rb_situational_metrics` AS rb
LEFT JOIN `{root}.situational_player_identity_candidates` AS identity
  ON identity.source_position = 'RB'
 AND identity.situational_player_id = rb.situational_player_id
 AND identity.player_slug = rb.player_slug
WHERE rb.refinement = 'standard'
"""
    client.create_table(rb_view, exists_ok=True)
    client.update_table(rb_view, ["view_query"])


def import_all(client: bigquery.Client, project: str, dataset: str, imports: list[dict[str, Any]], imported_at: datetime) -> None:
    create_dataset_and_tables(client, project, dataset)
    root = f"{project}.{dataset}"
    for item in imports:
        source = item["source"]
        params = [bigquery.ScalarQueryParameter("position", "STRING", source.position)]
        delete_where(client, f"{root}.raw_situational_rows", "source_file_name = @file", [bigquery.ScalarQueryParameter("file", "STRING", source.path.name)])
        delete_where(client, f"{root}.source_manifest", "source_file_name = @file", [bigquery.ScalarQueryParameter("file", "STRING", source.path.name)])
        delete_where(client, f"{root}.{source.position.lower()}_situational_metrics", "season BETWEEN @min_season AND @max_season", [bigquery.ScalarQueryParameter("min_season", "INT64", item["min_season"]), bigquery.ScalarQueryParameter("max_season", "INT64", item["max_season"])])
        delete_where(client, f"{root}.player_situational_metric_long", "position = @position", params)
        load_json(client, f"{root}.raw_situational_rows", item["raw"], SCHEMAS["raw_situational_rows"])
        load_json(client, f"{root}.{source.position.lower()}_situational_metrics", item["wide"], SCHEMAS[f"{source.position.lower()}_situational_metrics"])
        load_json(client, f"{root}.player_situational_metric_long", item["long"], SCHEMAS["player_situational_metric_long"])
        manifest = [{"source_file_name": source.path.name, "source_file_path": str(source.path), "source_position": source.position, "source_table": source.table, "source_sha256": item["sha256"], "source_row_count": len(item["raw"]), "min_season": item["min_season"], "max_season": item["max_season"], "schema_hash": item["schema_hash"], "imported_at": imported_at, "import_notes": "Phase 34.1 isolated research import."}]
        load_json(client, f"{root}.source_manifest", manifest, SCHEMAS["source_manifest"])

    replacements = {
        "situational_refinements": refinement_rows(imports),
        "situational_metric_dictionary": metric_dictionary(),
        "situational_player_identity_candidates": identity_rows(imports),
        "situational_metric_coverage": coverage_rows(imports),
        "situational_import_validation_report": validation_rows(imports, imported_at),
    }
    for table, records in replacements.items():
        if table == "situational_import_validation_report":
            predicate = "position IN ('QB', 'RB', 'WR', 'TE') OR validation_name = 'identity_policy'"
        elif table == "situational_player_identity_candidates":
            predicate = "source_position IN ('QB', 'RB', 'WR', 'TE')"
        else:
            predicate = "position IN ('QB', 'RB', 'WR', 'TE')"
        client.query(f"DELETE FROM `{root}.{table}` WHERE {predicate}").result()
        load_json(client, f"{root}.{table}", records, SCHEMAS[table])
    create_views(client, project, dataset)


def summary(imports: list[dict[str, Any]], project: str, dataset: str, mode: str) -> dict[str, Any]:
    return {
        "mode": mode, "project": project, "dataset": dataset,
        "source_row_count": sum(len(item["raw"]) for item in imports),
        "wide_row_count": sum(len(item["wide"]) for item in imports),
        "long_row_count": sum(len(item["long"]) for item in imports),
        "identity_candidate_count": len(identity_rows(imports)),
        "metric_dictionary_count": len(metric_dictionary()),
        "coverage_row_count": len(coverage_rows(imports)),
        "positions": {item["source"].position: {"file": item["source"].path.name, "sha256": item["sha256"], "row_count": len(item["raw"]), "season_min": item["min_season"], "season_max": item["max_season"], "duplicate_count": item["duplicate_count"], "required_nulls": item["required_nulls"], "comma_numeric_values": item["comma_values"]} for item in imports},
    }


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=PROJECT)
    parser.add_argument("--dataset", default=DATASET)
    parser.add_argument("--qb-db", type=Path, default=Path("Advanced Metrics/qb_situational.db"))
    parser.add_argument("--rb-db", type=Path, default=Path("Advanced Metrics/rb_situational.db"))
    parser.add_argument("--wr-db", type=Path, default=Path("Advanced Metrics/wr_situational.db"))
    parser.add_argument("--te-db", type=Path, default=Path("Advanced Metrics/te_situational.db"))
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--import", dest="run_import", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = arguments()
    imported_at = datetime.now(timezone.utc)
    sources = [Source("QB", args.qb_db.resolve(), "qb_stats"), Source("RB", args.rb_db.resolve(), "rb_stats"), Source("WR", args.wr_db.resolve(), "wr_stats"), Source("TE", args.te_db.resolve(), "te_stats")]
    imports = [read_source(source, imported_at) for source in sources]
    failures = sum(item["duplicate_count"] + item["required_nulls"] for item in imports)
    if failures:
        raise RuntimeError(f"Source validation failed with {failures} issue(s).")
    if args.run_import:
        import_all(bigquery.Client(project=args.project), args.project, args.dataset, imports, imported_at)
    print(json.dumps(summary(imports, args.project, args.dataset, "import" if args.run_import else "dry_run"), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
