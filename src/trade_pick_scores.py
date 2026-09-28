"""Deterministic scoring for draft-pick trade assets.

Dry-run mode is the default. Live writes require the pick-specific
ALLOW_TRADE_PICK_SCORE_MATERIALIZATION gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_MODEL_VERSION = "trade_pick_score_v0_2026_001"
DEFAULT_LIMIT = 500
MAX_LIMIT = 1000
DEFAULT_SCORE_READ_LIMIT = 500
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("TRADE_PICK_SCORES_MAX_BYTES_BILLED", "1000000000"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")
EXACT_PICK_RE = re.compile(r"^(20[0-9]{2}) Pick ([0-9]+)\.([0-9]+)$", re.IGNORECASE)
ROUND_ONLY_PICK_RE = re.compile(r"^(20[0-9]{2}) ([1-7])(st|nd|rd|th)$", re.IGNORECASE)
SLOTS_PER_ROUND = 12
NEUTRAL_COLLEGE_CONTEXT_SCORE = 50.0
PICK_SCORE_WRITE_GATE = "ALLOW_TRADE_PICK_SCORE_MATERIALIZATION"
TRADE_PICK_SCORE_TABLE = "trade_pick_scores"
TRADE_PICK_SCORE_FIELDS = (
    "model_version",
    "score_run_id",
    "source_pick_key",
    "pick_label",
    "pick_year",
    "pick_class",
    "pick_round",
    "pick_slot",
    "estimated_overall_pick",
    "pick_bucket",
    "parse_confidence",
    "scoring_profile_id",
    "league_type_id",
    "roster_format_id",
    "current_market_value",
    "risk_adjusted_trade_value",
    "market_score",
    "slot_capital_score",
    "time_discount_score",
    "liquidity_certainty_score",
    "college_context_score",
    "uncertainty_risk_score",
    "confidence_score",
    "pick_score",
    "score_tier",
    "component_json",
    "missing_flags_json",
    "source_freshness_json",
    "created_by",
    "created_at",
)
TRADE_PICK_SCORE_MERGE_KEY_FIELDS = (
    "model_version",
    "source_pick_key",
    "pick_year",
    "pick_class",
    "pick_round",
    "pick_slot",
    "scoring_profile_id",
    "league_type_id",
    "roster_format_id",
)
REQUIRED_WRITE_FIELDS = (
    "model_version",
    "score_run_id",
    "source_pick_key",
    "pick_label",
    "pick_year",
    "pick_class",
    "pick_round",
    "pick_bucket",
    "parse_confidence",
    "scoring_profile_id",
    "league_type_id",
    "roster_format_id",
    "component_json",
    "missing_flags_json",
    "source_freshness_json",
    "created_by",
    "created_at",
)
SCORE_FIELDS = (
    "market_score",
    "slot_capital_score",
    "time_discount_score",
    "liquidity_certainty_score",
    "college_context_score",
    "uncertainty_risk_score",
    "confidence_score",
    "pick_score",
)
JSON_FIELDS = ("component_json", "missing_flags_json", "source_freshness_json")
CREATED_BY = "src.trade_pick_scores"


@dataclass(frozen=True)
class PickParseResult:
    pick_label: str
    parsed: bool
    pick_year: int | None = None
    pick_class: str | None = None
    pick_round: int | None = None
    pick_slot: int | None = None
    estimated_overall_pick: int | None = None
    pick_bucket: str | None = None
    parse_confidence: str = "none"
    missing_flags: tuple[str, ...] = ()


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def is_pick_asset(row: dict[str, Any]) -> bool:
    """Classify pick assets without display-name substring matching."""

    position = str(row.get("position") or "").strip().upper()
    source_key = str(row.get("source_player_key") or "").strip().upper()
    return position == "PICK" or ":PICK:" in source_key


def parse_pick_label(label: Any) -> PickParseResult:
    text = str(label or "").strip()
    if not text:
        return PickParseResult(pick_label=text, parsed=False, missing_flags=("pick_label_unparsed",))

    exact = EXACT_PICK_RE.match(text)
    if exact:
        pick_year = int(exact.group(1))
        pick_round = int(exact.group(2))
        pick_slot = int(exact.group(3))
        estimated_overall = (pick_round - 1) * SLOTS_PER_ROUND + pick_slot
        return PickParseResult(
            pick_label=text,
            parsed=True,
            pick_year=pick_year,
            pick_class="exact_slot",
            pick_round=pick_round,
            pick_slot=pick_slot,
            estimated_overall_pick=estimated_overall,
            pick_bucket="exact",
            parse_confidence="high",
        )

    round_only = ROUND_ONLY_PICK_RE.match(text)
    if round_only:
        return PickParseResult(
            pick_label=text,
            parsed=True,
            pick_year=int(round_only.group(1)),
            pick_class="round_only",
            pick_round=int(round_only.group(2)),
            pick_slot=None,
            estimated_overall_pick=None,
            pick_bucket="round_only",
            parse_confidence="medium",
        )

    return PickParseResult(pick_label=text, parsed=False, missing_flags=("pick_label_unparsed",))


def build_trade_pick_asset_query(
    *,
    project_id: str,
    dataset_id: str,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    limit: int | str | None = None,
) -> tuple[str, bigquery.QueryJobConfig]:
    sql = f"""
    SELECT
        source_player_key,
        display_name AS pick_label,
        display_name,
        position,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        CAST(market_value AS FLOAT64) AS current_market_value,
        CAST(risk_adjusted_trade_value AS FLOAT64) AS risk_adjusted_trade_value,
        source_freshness_json,
        missing_data_flags
    FROM `{_table_id(project_id, dataset_id, "compat_trade_assets_current")}`
    WHERE (UPPER(position) = 'PICK' OR UPPER(source_player_key) LIKE '%:PICK:%')
        AND (@scoring_profile_id IS NULL OR scoring_profile_id = @scoring_profile_id)
        AND (@league_type_id IS NULL OR league_type_id = @league_type_id)
        AND (@roster_format_id IS NULL OR roster_format_id = @roster_format_id)
    ORDER BY scoring_profile_id, league_type_id, roster_format_id, current_market_value DESC, display_name
    LIMIT @limit
    """
    return sql, _job_config([
        ("scoring_profile_id", "STRING", _clean_optional(scoring_profile_id)),
        ("league_type_id", "STRING", _clean_optional(league_type_id)),
        ("roster_format_id", "STRING", _clean_optional(roster_format_id)),
        ("limit", "INT64", _clamp_limit(limit)),
    ])


def fetch_trade_pick_assets(
    *,
    client: Any,
    dataset_id: str,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    limit: int | str | None = None,
) -> list[dict[str, Any]]:
    sql, job_config = build_trade_pick_asset_query(
        project_id=client.project,
        dataset_id=dataset_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=limit,
    )
    return _query_rows(client, sql, job_config)


def get_current_trade_pick_scores(
    *,
    scoring_profile_id: str = "ppr",
    league_type_id: str = "redraft",
    roster_format_id: str = "one_qb",
    source_pick_key: str | None = None,
    limit: int | str | None = DEFAULT_SCORE_READ_LIMIT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Read current draft-pick scores from the Streamlit-safe compatibility view."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_current_trade_pick_scores_query(
        project_id=client.project,
        dataset_id=dataset_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        source_pick_key=source_pick_key,
        limit=limit,
    )
    return _query_rows(client, sql, job_config)


def build_current_trade_pick_scores_query(
    *,
    project_id: str,
    dataset_id: str,
    scoring_profile_id: str = "ppr",
    league_type_id: str = "redraft",
    roster_format_id: str = "one_qb",
    source_pick_key: str | None = None,
    limit: int | str | None = DEFAULT_SCORE_READ_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    """Build the bounded pick-score read query for UI use."""

    sql = f"""
    SELECT
        source_pick_key,
        pick_label,
        pick_year,
        pick_class,
        pick_round,
        pick_slot,
        estimated_overall_pick,
        pick_bucket,
        parse_confidence,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        current_market_value,
        risk_adjusted_trade_value,
        market_score,
        slot_capital_score,
        time_discount_score,
        liquidity_certainty_score,
        college_context_score,
        uncertainty_risk_score,
        confidence_score,
        pick_score,
        score_tier,
        source_freshness_json,
        missing_flags_json,
        component_json,
        model_version,
        score_run_id,
        created_at
    FROM `{_table_id(project_id, dataset_id, "compat_trade_pick_scores_current")}`
    WHERE scoring_profile_id = @scoring_profile_id
        AND league_type_id = @league_type_id
        AND roster_format_id = @roster_format_id
        AND (@source_pick_key IS NULL OR source_pick_key = @source_pick_key)
    ORDER BY pick_score DESC, current_market_value DESC, pick_label ASC
    LIMIT @limit
    """
    return sql, _job_config([
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("source_pick_key", "STRING", _clean_optional(source_pick_key)),
        ("limit", "INT64", _clamp_limit(limit)),
    ])


def build_trade_pick_score_dry_run(
    source_rows: list[dict[str, Any]],
    *,
    model_version: str = DEFAULT_MODEL_VERSION,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    pick_assets = [dict(row) for row in source_rows if is_pick_asset(dict(row))]
    parsed_pairs: list[tuple[dict[str, Any], PickParseResult]] = []
    unparsed: list[dict[str, Any]] = []

    for row in pick_assets:
        parsed = parse_pick_label(row.get("pick_label") or row.get("display_name"))
        if parsed.parsed:
            parsed_pairs.append((row, parsed))
        else:
            unparsed.append({
                "pick_label": parsed.pick_label,
                "source_pick_key": _clean_str(row.get("source_player_key")),
                "missing_flags": list(parsed.missing_flags),
            })

    nearest_pick_year = min((parsed.pick_year for _, parsed in parsed_pairs if parsed.pick_year), default=now.year)
    market_context = _market_context(parsed_pairs)
    rows = [
        _build_pick_score_row(
            row,
            parsed,
            market_context=market_context,
            nearest_pick_year=nearest_pick_year,
            model_version=model_version,
            now=now,
        )
        for row, parsed in parsed_pairs
    ]
    rows = sorted(rows, key=lambda row: (row["pick_score"], row["current_market_value"] or 0, row["pick_label"]), reverse=True)
    summary = build_pick_score_summary(
        rows,
        source_pick_asset_rows=len(pick_assets),
        unparsed=unparsed,
        nearest_pick_year=nearest_pick_year,
    )
    return {
        "model_version": model_version,
        "dry_run": True,
        "wrote": False,
        "source_pick_asset_rows": len(pick_assets),
        "parsed_pick_rows": len(rows),
        "unparsed_pick_rows": len(unparsed),
        "nearest_pick_year": nearest_pick_year,
        "rows": rows,
        "unparsed_examples": unparsed[:25],
        "summary": summary,
    }


def build_trade_pick_scores(
    *,
    model_version: str = DEFAULT_MODEL_VERSION,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    limit: int | str | None = None,
    dry_run: bool = True,
    write: bool = False,
    client: Any | None = None,
    dataset_id: str | None = None,
    project_id: str | None = None,
) -> dict[str, Any]:
    if write:
        require_pick_score_write_authorization()
    if not dry_run and not write:
        raise ValueError("write=True is required for non-dry-run pick score materialization")

    client = client or (bigquery.Client(project=project_id) if project_id else get_bigquery_client())
    dataset_id = dataset_id or get_bigquery_dataset()
    source_rows = fetch_trade_pick_assets(
        client=client,
        dataset_id=dataset_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=limit,
    )
    result = build_trade_pick_score_dry_run(source_rows, model_version=model_version)
    if not write:
        return result

    project_id = project_id or client.project
    save_result = save_trade_pick_scores(
        result["rows"],
        project_id=project_id,
        dataset_id=dataset_id,
        client=client,
    )
    output = {
        **result,
        "dry_run": False,
        "wrote": True,
        "written_row_count": save_result["written_row_count"],
        "excluded_rows": result["unparsed_pick_rows"],
        "target_project": project_id,
        "target_dataset": dataset_id,
        "target_table": save_result["target_table"],
        "staging_table": save_result["staging_table"],
    }
    output["summary"] = {
        **result["summary"],
        "dry_run": False,
        "wrote": True,
        "written_row_count": save_result["written_row_count"],
        "excluded_rows": result["unparsed_pick_rows"],
        "target_table": save_result["target_table"],
    }
    return output


def is_pick_score_write_authorized(env: dict[str, str] | None = None) -> bool:
    values = env if env is not None else os.environ
    return str(values.get(PICK_SCORE_WRITE_GATE) or "").strip().lower() == "true"


def require_pick_score_write_authorization(env: dict[str, str] | None = None) -> None:
    if not is_pick_score_write_authorized(env):
        raise PermissionError(f"{PICK_SCORE_WRITE_GATE} must be true to write pick scores")


def save_trade_pick_scores(
    rows: list[dict[str, Any]],
    *,
    project_id: str,
    dataset_id: str,
    client: Any,
) -> dict[str, Any]:
    write_rows = prepare_trade_pick_score_write_rows(rows)
    target_table = _table_id(project_id, dataset_id, TRADE_PICK_SCORE_TABLE)
    if not write_rows:
        return {
            "written_row_count": 0,
            "target_table": target_table,
            "staging_table": None,
        }

    staging_table_name = build_trade_pick_scores_staging_table_name(write_rows)
    staging_table = _table_id(project_id, dataset_id, staging_table_name)
    target = client.get_table(target_table)
    load_config = bigquery.LoadJobConfig(
        schema=target.schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    try:
        client.load_table_from_json(write_rows, staging_table, job_config=load_config).result()
        merge_sql = build_trade_pick_scores_merge_sql(
            project_id=project_id,
            dataset_id=dataset_id,
            staging_table_name=staging_table_name,
        )
        client.query(merge_sql).result()
    finally:
        client.delete_table(staging_table, not_found_ok=True)

    return {
        "written_row_count": len(write_rows),
        "target_table": target_table,
        "staging_table": staging_table,
    }


def prepare_trade_pick_score_write_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prepared: list[dict[str, Any]] = []
    for row in rows:
        write_row = {field: row.get(field) for field in TRADE_PICK_SCORE_FIELDS}
        write_row["created_by"] = write_row.get("created_by") or CREATED_BY
        _validate_trade_pick_score_write_row(write_row)
        prepared.append(write_row)
    return prepared


def build_trade_pick_scores_staging_table_name(rows: list[dict[str, Any]]) -> str:
    model_version = str(rows[0].get("model_version") or DEFAULT_MODEL_VERSION) if rows else DEFAULT_MODEL_VERSION
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    digest = _short_hash(f"{model_version}|{len(rows)}|{stamp}")
    return f"{TRADE_PICK_SCORE_TABLE}_staging_{stamp}_{digest}"


def build_trade_pick_scores_merge_sql(
    *,
    project_id: str,
    dataset_id: str,
    staging_table_name: str,
) -> str:
    target_table = _table_id(project_id, dataset_id, TRADE_PICK_SCORE_TABLE)
    staging_table = _table_id(project_id, dataset_id, staging_table_name)
    conditions = []
    for field in TRADE_PICK_SCORE_MERGE_KEY_FIELDS:
        if field == "pick_slot":
            conditions.append("IFNULL(target.pick_slot, -1) = IFNULL(source.pick_slot, -1)")
        else:
            conditions.append(f"target.{field} = source.{field}")
    update_fields = [field for field in TRADE_PICK_SCORE_FIELDS if field not in TRADE_PICK_SCORE_MERGE_KEY_FIELDS]
    update_sql = ",\n        ".join(f"{field} = source.{field}" for field in update_fields)
    insert_fields = ", ".join(TRADE_PICK_SCORE_FIELDS)
    insert_values = ", ".join(f"source.{field}" for field in TRADE_PICK_SCORE_FIELDS)
    return f"""
MERGE `{target_table}` target
USING `{staging_table}` source
ON {' AND '.join(conditions)}
WHEN MATCHED THEN UPDATE SET
        {update_sql}
WHEN NOT MATCHED THEN INSERT ({insert_fields})
VALUES ({insert_values})
""".strip()


def build_pick_score_summary(
    rows: list[dict[str, Any]],
    *,
    source_pick_asset_rows: int,
    unparsed: list[dict[str, Any]],
    nearest_pick_year: int,
    examples: int = 25,
) -> dict[str, Any]:
    flag_counts: Counter[str] = Counter()
    for row in rows:
        flag_counts.update(_json_array(row.get("missing_flags_json")))
    for item in unparsed:
        flag_counts.update(item.get("missing_flags") or [])

    by_profile = Counter(row["scoring_profile_id"] for row in rows)
    by_year = Counter(str(row["pick_year"]) for row in rows)
    by_tier = Counter(row["score_tier"] for row in rows)
    exact_conf = [_num(row.get("confidence_score"), None) for row in rows if row.get("pick_class") == "exact_slot"]
    round_conf = [_num(row.get("confidence_score"), None) for row in rows if row.get("pick_class") == "round_only"]
    top = rows[:examples]
    bottom = list(reversed(rows[-examples:])) if rows else []
    return {
        "source_pick_asset_rows": source_pick_asset_rows,
        "parsed_pick_rows": len(rows),
        "unparsed_pick_rows": len(unparsed),
        "exact_slot_rows": sum(1 for row in rows if row.get("pick_class") == "exact_slot"),
        "round_only_rows": sum(1 for row in rows if row.get("pick_class") == "round_only"),
        "nearest_pick_year": nearest_pick_year,
        "rows_by_scoring_profile": dict(sorted(by_profile.items())),
        "rows_by_pick_year": dict(sorted(by_year.items())),
        "score": _stats([row.get("pick_score") for row in rows]),
        "confidence": _stats([row.get("confidence_score") for row in rows]),
        "exact_slot_confidence": _stats(exact_conf),
        "round_only_confidence": _stats(round_conf),
        "tier_distribution": dict(sorted(by_tier.items())),
        "warning_flag_counts": dict(sorted(flag_counts.items())),
        "top_examples": [_preview_row(row) for row in top],
        "bottom_examples": [_preview_row(row) for row in bottom],
        "example_components": {
            "2026 Pick 1.01": _component_for_label(rows, "2026 Pick 1.01"),
            "2026 1st": _component_for_label(rows, "2026 1st"),
        },
        "unparsed_examples": unparsed[:examples],
    }


def _build_pick_score_row(
    row: dict[str, Any],
    parsed: PickParseResult,
    *,
    market_context: dict[tuple[str | None, str | None, str | None], dict[str, float]],
    nearest_pick_year: int,
    model_version: str,
    now: datetime,
) -> dict[str, Any]:
    flags: list[str] = []
    source_key = _clean_str(row.get("source_player_key"))
    current_market_value = _num(row.get("current_market_value"), None)
    risk_adjusted_trade_value = _num(row.get("risk_adjusted_trade_value"), None)
    source_freshness_json = row.get("source_freshness_json")
    asset_missing_flags = _json_array(row.get("missing_data_flags"))

    flags.extend(asset_missing_flags)
    flags.extend([
        "pick_market_source_only",
        "college_context_unavailable",
        "draft_outcome_prior_insufficient",
        "pick_score_staging_only",
    ])
    if parsed.pick_class == "round_only":
        flags.append("pick_round_only_uncertainty")
    if parsed.pick_year and parsed.pick_year > nearest_pick_year:
        flags.append("pick_future_year_discount")
    if not source_key:
        flags.append("pick_source_key_missing")
    if current_market_value is None:
        flags.append("missing_market_value")
    if source_freshness_json in (None, ""):
        flags.append("pick_market_freshness_missing")

    context_key = _context_key(row)
    market_score = _market_score(current_market_value, market_context.get(context_key, {}))
    slot_capital_score = slot_capital_score_for_pick(parsed)
    time_discount_score = time_discount_score_for_pick(parsed.pick_year, nearest_pick_year)
    liquidity_certainty_score = liquidity_certainty_score_for_pick(
        parsed,
        source_key=source_key,
        market_value=current_market_value,
        source_freshness_json=source_freshness_json,
    )
    college_context_score = NEUTRAL_COLLEGE_CONTEXT_SCORE
    risk_breakdown = risk_breakdown_for_pick(
        parsed,
        source_freshness_json=source_freshness_json,
        nearest_pick_year=nearest_pick_year,
    )
    confidence_breakdown = confidence_breakdown_for_pick(
        parsed,
        source_key=source_key,
        market_value=current_market_value,
        source_freshness_json=source_freshness_json,
        nearest_pick_year=nearest_pick_year,
    )
    formula = calculate_pick_score(
        market_score=market_score,
        slot_capital_score=slot_capital_score,
        time_discount_score=time_discount_score,
        liquidity_certainty_score=liquidity_certainty_score,
        college_context_score=college_context_score,
        risk_adjustment=risk_breakdown["risk_adjustment"],
    )
    confidence_score = confidence_breakdown["confidence_score"]
    component_json = {
        "formula": {
            "model": "trade_pick_score_v0",
            "weights": {
                "market_score": 0.50,
                "slot_capital_score": 0.20,
                "time_discount_score": 0.15,
                "liquidity_certainty_score": 0.10,
                "college_context_score": 0.05,
            },
            "risk_adjustment": risk_breakdown["risk_adjustment"],
            "market_normalization": "min_max_within_scoring_league_roster_context",
            "score_tiers": "elite,premium,solid,speculative,deep,avoid",
        },
        "parse": asdict(parsed),
        "risk_breakdown": risk_breakdown,
        "confidence_breakdown": confidence_breakdown,
        "college_context": {
            "score": college_context_score,
            "status": "neutral_unavailable",
            "source_tables_used": [],
        },
    }
    pick_score = formula["pick_score"]
    return {
        "model_version": model_version,
        "score_run_id": build_score_run_id(
            model_version=model_version,
            source_pick_key=source_key or parsed.pick_label,
            scoring_profile_id=_clean_str(row.get("scoring_profile_id")),
            league_type_id=_clean_str(row.get("league_type_id")),
            roster_format_id=_clean_str(row.get("roster_format_id")),
        ),
        "source_pick_key": source_key,
        "pick_label": parsed.pick_label,
        "pick_year": parsed.pick_year,
        "pick_class": parsed.pick_class,
        "pick_round": parsed.pick_round,
        "pick_slot": parsed.pick_slot,
        "estimated_overall_pick": parsed.estimated_overall_pick,
        "pick_bucket": parsed.pick_bucket,
        "parse_confidence": parsed.parse_confidence,
        "scoring_profile_id": _clean_str(row.get("scoring_profile_id")),
        "league_type_id": _clean_str(row.get("league_type_id")),
        "roster_format_id": _clean_str(row.get("roster_format_id")),
        "current_market_value": current_market_value,
        "risk_adjusted_trade_value": risk_adjusted_trade_value,
        "market_score": market_score,
        "slot_capital_score": slot_capital_score,
        "time_discount_score": time_discount_score,
        "liquidity_certainty_score": liquidity_certainty_score,
        "college_context_score": college_context_score,
        "uncertainty_risk_score": round(abs(risk_breakdown["risk_adjustment"]) * 10.0, 4),
        "confidence_score": confidence_score,
        "pick_score": pick_score,
        "score_tier": pick_score_tier(pick_score),
        "component_json": _json_dumps(component_json),
        "missing_flags_json": _json_dumps(sorted(set(flags))),
        "source_freshness_json": _json_dumps(_parse_json(source_freshness_json, {})),
        "created_by": CREATED_BY,
        "created_at": _timestamp(now),
    }


def calculate_pick_score(
    *,
    market_score: float,
    slot_capital_score: float,
    time_discount_score: float,
    liquidity_certainty_score: float,
    college_context_score: float,
    risk_adjustment: float,
) -> dict[str, float]:
    base_score = (
        0.50 * _clamp(market_score, 0.0, 100.0)
        + 0.20 * _clamp(slot_capital_score, 0.0, 100.0)
        + 0.15 * _clamp(time_discount_score, 0.0, 100.0)
        + 0.10 * _clamp(liquidity_certainty_score, 0.0, 100.0)
        + 0.05 * _clamp(college_context_score, 0.0, 100.0)
    )
    safe_risk_adjustment = _clamp(risk_adjustment, -10.0, 0.0)
    pick_score = _clamp(base_score + safe_risk_adjustment, 0.0, 100.0)
    return {
        "base_score": round(base_score, 4),
        "risk_adjustment": round(safe_risk_adjustment, 4),
        "pick_score": round(pick_score, 4),
    }


def slot_capital_score_for_pick(parsed: PickParseResult) -> float:
    if not parsed.parsed or not parsed.pick_round:
        return 0.0
    if parsed.pick_class == "exact_slot" and parsed.estimated_overall_pick:
        return round(_clamp(100.0 - (parsed.estimated_overall_pick - 1) * 1.55, 25.0, 100.0), 4)
    midpoint = (parsed.pick_round - 1) * SLOTS_PER_ROUND + ((SLOTS_PER_ROUND + 1) / 2)
    return round(_clamp(100.0 - (midpoint - 1) * 1.55 - 4.0, 20.0, 96.0), 4)


def time_discount_score_for_pick(pick_year: int | None, nearest_pick_year: int) -> float:
    if pick_year is None:
        return 50.0
    year_delta = max(0, pick_year - nearest_pick_year)
    return round(_clamp(100.0 - 12.0 * year_delta, 55.0, 100.0), 4)


def liquidity_certainty_score_for_pick(
    parsed: PickParseResult,
    *,
    source_key: str | None,
    market_value: float | None,
    source_freshness_json: Any,
) -> float:
    score = 92.0 if parsed.pick_class == "exact_slot" else 75.0
    if not source_key:
        score -= 10.0
    if market_value is None:
        score -= 20.0
    if source_freshness_json in (None, ""):
        score -= 10.0
    return round(_clamp(score, 0.0, 100.0), 4)


def risk_breakdown_for_pick(
    parsed: PickParseResult,
    *,
    source_freshness_json: Any,
    nearest_pick_year: int,
) -> dict[str, Any]:
    details: list[dict[str, Any]] = []
    risk = 0.0
    if parsed.pick_class == "round_only":
        risk -= 5.0
        details.append({"reason": "round_only_uncertainty", "adjustment": -5.0})
    elif parsed.pick_class == "exact_slot":
        details.append({"reason": "exact_slot_known", "adjustment": 0.0})
    if parsed.pick_year and parsed.pick_year > nearest_pick_year:
        future_adjustment = -min(3.0, float(parsed.pick_year - nearest_pick_year))
        risk += future_adjustment
        details.append({"reason": "future_year_discount", "adjustment": future_adjustment})
    if source_freshness_json in (None, ""):
        risk -= 5.0
        details.append({"reason": "market_freshness_missing", "adjustment": -5.0})
    return {
        "risk_adjustment": round(_clamp(risk, -10.0, 0.0), 4),
        "details": details,
    }


def confidence_breakdown_for_pick(
    parsed: PickParseResult,
    *,
    source_key: str | None,
    market_value: float | None,
    source_freshness_json: Any,
    nearest_pick_year: int,
) -> dict[str, Any]:
    starting = 88.0 if parsed.pick_class == "exact_slot" else 74.0
    deductions: list[dict[str, Any]] = []
    confidence = starting
    if parsed.pick_year and parsed.pick_year > nearest_pick_year:
        deduction = min(12.0, 4.0 * (parsed.pick_year - nearest_pick_year))
        confidence -= deduction
        deductions.append({"reason": "future_year_discount", "deduction": deduction})
    if not source_key:
        confidence -= 8.0
        deductions.append({"reason": "source_pick_key_missing", "deduction": 8.0})
    if market_value is None:
        confidence -= 20.0
        deductions.append({"reason": "market_value_missing", "deduction": 20.0})
    if source_freshness_json in (None, ""):
        confidence -= 10.0
        deductions.append({"reason": "market_freshness_missing", "deduction": 10.0})
    confidence = round(_clamp(confidence, 0.0, 100.0), 4)
    return {
        "starting_confidence": starting,
        "deductions": deductions,
        "confidence_score": confidence,
    }


def pick_score_tier(score: float | int | None) -> str:
    value = _num(score, 0.0) or 0.0
    if value >= 88.0:
        return "elite"
    if value >= 74.0:
        return "premium"
    if value >= 60.0:
        return "solid"
    if value >= 45.0:
        return "speculative"
    if value >= 30.0:
        return "deep"
    return "avoid"


def build_score_run_id(
    *,
    model_version: str,
    source_pick_key: str,
    scoring_profile_id: str | None,
    league_type_id: str | None,
    roster_format_id: str | None,
) -> str:
    key = "|".join([
        model_version,
        source_pick_key,
        scoring_profile_id or "",
        league_type_id or "",
        roster_format_id or "",
    ])
    return f"trade-pick-score-{_slug(model_version)}-{_short_hash(key)}"


def _market_context(parsed_pairs: list[tuple[dict[str, Any], PickParseResult]]) -> dict[tuple[str | None, str | None, str | None], dict[str, float]]:
    grouped: dict[tuple[str | None, str | None, str | None], list[float]] = defaultdict(list)
    for row, _ in parsed_pairs:
        value = _num(row.get("current_market_value"), None)
        if value is not None:
            grouped[_context_key(row)].append(value)
    return {
        key: {"min": min(values), "max": max(values)}
        for key, values in grouped.items()
        if values
    }


def _market_score(value: float | None, context: dict[str, float]) -> float:
    if value is None:
        return 35.0
    minimum = context.get("min")
    maximum = context.get("max")
    if minimum is None or maximum is None:
        return 50.0
    if math.isclose(maximum, minimum):
        return 50.0
    return round(_clamp((value - minimum) / (maximum - minimum) * 100.0, 0.0, 100.0), 4)


def _context_key(row: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    return (
        _clean_str(row.get("scoring_profile_id")),
        _clean_str(row.get("league_type_id")),
        _clean_str(row.get("roster_format_id")),
    )


def _component_for_label(rows: list[dict[str, Any]], label: str) -> dict[str, Any] | None:
    for row in rows:
        if row.get("pick_label") == label:
            return _parse_json(row.get("component_json"), {})
    return None


def _preview_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "pick_label": row.get("pick_label"),
        "source_pick_key": row.get("source_pick_key"),
        "pick_class": row.get("pick_class"),
        "scoring_profile_id": row.get("scoring_profile_id"),
        "league_type_id": row.get("league_type_id"),
        "roster_format_id": row.get("roster_format_id"),
        "current_market_value": row.get("current_market_value"),
        "market_score": row.get("market_score"),
        "confidence_score": row.get("confidence_score"),
        "pick_score": row.get("pick_score"),
        "score_tier": row.get("score_tier"),
    }


def _stats(values: list[Any]) -> dict[str, float | int | None]:
    clean = [_num(value, None) for value in values]
    numbers = [float(value) for value in clean if value is not None]
    if not numbers:
        return {"count": 0, "min": None, "max": None, "avg": None, "stddev": None}
    avg = sum(numbers) / len(numbers)
    variance = sum((value - avg) ** 2 for value in numbers) / len(numbers)
    return {
        "count": len(numbers),
        "min": round(min(numbers), 4),
        "max": round(max(numbers), 4),
        "avg": round(avg, 4),
        "stddev": round(math.sqrt(variance), 4),
    }


def _query_rows(client: Any, sql: str, job_config: bigquery.QueryJobConfig) -> list[dict[str, Any]]:
    try:
        rows = client.query(sql, job_config=job_config).result()
    except NotFound:
        return []
    return [_row_to_dict(row) for row in rows]


def _validate_trade_pick_score_write_row(row: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_WRITE_FIELDS if row.get(field) in (None, "")]
    if missing:
        raise ValueError(f"trade_pick_scores row is missing required fields: {', '.join(missing)}")
    if ":PICK:" not in str(row.get("source_pick_key") or "").upper():
        raise ValueError("trade_pick_scores rows must use PICK source keys")
    if row.get("pick_class") not in {"exact_slot", "round_only"}:
        raise ValueError("trade_pick_scores row has invalid pick_class")
    if row.get("pick_class") == "exact_slot" and row.get("pick_slot") in (None, ""):
        raise ValueError("exact_slot pick rows require pick_slot")
    if row.get("pick_class") == "round_only" and row.get("pick_slot") is not None:
        raise ValueError("round_only pick rows must keep pick_slot null")
    for field in ("pick_year", "pick_round"):
        if _num(row.get(field), None) is None:
            raise ValueError(f"trade_pick_scores row has invalid {field}")
    for field in SCORE_FIELDS:
        value = _num(row.get(field), None)
        if value is None or value < 0.0 or value > 100.0:
            raise ValueError(f"trade_pick_scores row has invalid {field}")
    if not row.get("score_tier"):
        raise ValueError("trade_pick_scores row is missing score_tier")
    for field in JSON_FIELDS:
        parsed = _parse_json(row.get(field), None)
        if parsed is None:
            raise ValueError(f"trade_pick_scores row has invalid {field}")


def _job_config(params: list[tuple[str, str, Any]]) -> bigquery.QueryJobConfig:
    return bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=[
            bigquery.ScalarQueryParameter(name, type_name, value)
            for name, type_name, value in params
        ],
    )


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    if not IDENTIFIER_RE.match(table_name):
        raise ValueError(f"Unsafe BigQuery table name: {table_name}")
    return f"{project_id}.{dataset_id}.{table_name}"


def _row_to_dict(row: Any) -> dict[str, Any]:
    if hasattr(row, "items"):
        return dict(row.items())
    if isinstance(row, dict):
        return dict(row)
    return dict(row)


def _clean_optional(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _clean_str(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _clamp_limit(value: int | str | None) -> int:
    try:
        parsed = int(value) if value is not None else DEFAULT_LIMIT
    except (TypeError, ValueError):
        parsed = DEFAULT_LIMIT
    return max(1, min(MAX_LIMIT, parsed))


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def _num(value: Any, default: float | None = 0.0) -> float | None:
    if value in (None, ""):
        return default
    try:
        if isinstance(value, float) and math.isnan(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _json_array(value: Any) -> list[str]:
    parsed = _parse_json(value, [])
    if isinstance(parsed, list):
        return [str(item) for item in parsed if item not in (None, "")]
    return []


def _parse_json(value: Any, default: Any) -> Any:
    if value in (None, ""):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return default


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _slug(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return text or "unknown"


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build deterministic draft-pick score dry-run rows.")
    parser.add_argument("--model-version", default=DEFAULT_MODEL_VERSION)
    parser.add_argument("--scoring-profile-id")
    parser.add_argument("--league-type-id")
    parser.add_argument("--roster-format-id")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dataset", default=get_bigquery_dataset())
    parser.add_argument("--project")
    args = parser.parse_args()

    dry_run = not args.write
    try:
        result = build_trade_pick_scores(
            model_version=args.model_version,
            scoring_profile_id=args.scoring_profile_id,
            league_type_id=args.league_type_id,
            roster_format_id=args.roster_format_id,
            limit=args.limit,
            dry_run=dry_run,
            write=args.write,
            dataset_id=args.dataset,
            project_id=args.project,
        )
    except PermissionError as exc:
        raise SystemExit(str(exc)) from exc
    output = {key: value for key, value in result.items() if key != "rows"}
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
