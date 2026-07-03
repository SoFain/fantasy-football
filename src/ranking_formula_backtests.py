"""Deterministic ranking formula validation and backtest planning."""

from __future__ import annotations

import argparse
import json
import os
import uuid
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any


WRITE_GATE = "ALLOW_RANKING_FORMULA_BACKTEST_WRITE"
DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_PROJECT = "fantasy-football-498121"
DEFAULT_FORMULA_VERSION = "ranking_formula_v0"
CREATED_BY = "ranking_formula_backtests"

POSITIONS = ("QB", "RB", "WR", "TE")
TARGET_DEFINITIONS = {
    "top_12_position": {
        "target_name": "top_12_position",
        "rank_threshold": 12,
        "description": "Player finishes inside same-position weekly top 12.",
    },
    "top_24_position": {
        "target_name": "top_24_position",
        "rank_threshold": 24,
        "description": "Player finishes inside same-position weekly top 24.",
    },
    "beat_position_median": {
        "target_name": "beat_position_median",
        "description": "Player beats same-position median weekly fantasy points.",
    },
}

COMMON_FEATURES = {
    "actual_points",
    "fantasy_points_ppr",
    "recent_points_avg",
    "epa_per_play",
    "success_rate",
    "usage_volume",
    "snap_share_proxy",
    "red_zone_opportunities",
    "team_epa_per_play",
    "opponent_allowed_points",
    "pigskin_context_score",
}
POSITION_FEATURE_ALLOWLISTS: dict[str, set[str]] = {
    "QB": COMMON_FEATURES
    | {
        "passing_epa_per_play",
        "passing_success_rate",
        "cpoe",
        "dropbacks",
        "rushing_attempts",
        "designed_rush_share_proxy",
    },
    "RB": COMMON_FEATURES
    | {
        "carries",
        "targets",
        "rush_success_rate",
        "receiving_usage",
        "goal_line_opportunities",
    },
    "WR": COMMON_FEATURES
    | {
        "targets",
        "air_yards",
        "receiving_yards",
        "receiving_epa",
        "red_zone_targets",
    },
    "TE": COMMON_FEATURES
    | {
        "targets",
        "air_yards",
        "receiving_yards",
        "receiving_epa",
        "red_zone_targets",
        "team_pass_rate",
    },
}
BLOCKED_METRIC_FEATURES = {
    "route_share": "route_share_available",
    "yprr": "yprr_available",
    "first_read_share": "first_read_share_available",
    "true_pressure": "true_pressure_available",
    "contact_yards": "contact_yards_available",
    "alignment": "alignment_available",
}
ALLOWED_INPUT_TABLES = (
    "player_week_advanced_metrics",
    "player_recent_advanced_metrics_current",
    "player_role_usage_metrics_current",
    "pigskin_player_context_packet_current",
    "analytics_player_weekly_truth",
    "analytics_player_fantasy_points_by_profile",
)
FORBIDDEN_TABLE_REFERENCES = {
    "weekly_metrics",
    "play_by_play",
    "draft_picks",
    "player_rosters",
    "raw_",
    "source.",
}
FORMULA_REQUIRED_FIELDS = (
    "version",
    "position",
    "score_expression",
    "features",
    "weights",
    "normalization",
)

RANKING_TABLES = {
    "ranking_formula_candidates": (
        "candidate_id",
        "formula_set_id",
        "formula_name",
        "formula_version",
        "position",
        "formula_json",
        "feature_allowlist_json",
        "target_definition_json",
        "source_requirements_json",
        "status",
        "notes",
        "created_by",
        "created_at",
        "updated_at",
    ),
    "ranking_backtest_runs": (
        "backtest_run_id",
        "formula_set_id",
        "formula_version",
        "candidate_count",
        "season_start",
        "season_end",
        "week_start",
        "week_end",
        "scoring_profile_id",
        "league_type_id",
        "roster_format_id",
        "target_definition_json",
        "input_tables_json",
        "dry_run",
        "status",
        "created_by",
        "created_at",
        "completed_at",
        "error_message",
        "notes",
    ),
    "ranking_backtest_results": (
        "backtest_run_id",
        "candidate_id",
        "formula_set_id",
        "formula_version",
        "position",
        "season",
        "week",
        "player_id_internal",
        "player_name",
        "team",
        "scoring_profile_id",
        "league_type_id",
        "roster_format_id",
        "predicted_score",
        "predicted_rank_position",
        "actual_points",
        "actual_rank_position",
        "target_name",
        "target_hit",
        "win_rate",
        "feature_values_json",
        "result_json",
        "missing_flags_json",
        "source_freshness_json",
        "created_at",
    ),
    "ranking_backtest_candidate_summaries": (
        "backtest_run_id",
        "candidate_id",
        "formula_version",
        "position",
        "scoring_profile_id",
        "league_type_id",
        "roster_format_id",
        "target_name",
        "sample_size",
        "pairwise_win_rate",
        "top_n_hit_rate",
        "rank_correlation",
        "mean_absolute_error",
        "regret_score",
        "actual_points_captured_rate",
        "missing_input_rate",
        "metric_json",
        "missing_flags_json",
        "source_freshness_json",
        "created_at",
    ),
    "ranking_formula_sets": (
        "formula_set_id",
        "formula_set_name",
        "formula_set_version",
        "qb_candidate_id",
        "rb_candidate_id",
        "wr_candidate_id",
        "te_candidate_id",
        "status",
        "description",
        "created_by",
        "created_at",
        "updated_at",
        "notes",
    ),
}


class FormulaValidationError(ValueError):
    """Raised when a ranking formula violates the contract."""


def is_write_authorized(env: Mapping[str, str] | None = None) -> bool:
    values = env if env is not None else os.environ
    return str(values.get(WRITE_GATE, "")).strip().lower() == "true"


def require_write_authorization(env: Mapping[str, str] | None = None) -> None:
    if not is_write_authorized(env):
        raise PermissionError(f"{WRITE_GATE} must be true to write ranking formula backtests")


def default_formula(position: str) -> dict[str, Any]:
    pos = _normalize_position(position)
    feature_weights = {
        "recent_points_avg": 0.35,
        "usage_volume": 0.25,
        "epa_per_play": 0.2,
        "pigskin_context_score": 0.2,
    }
    if pos == "QB":
        feature_weights = {
            "recent_points_avg": 0.3,
            "passing_epa_per_play": 0.25,
            "passing_success_rate": 0.2,
            "cpoe": 0.1,
            "pigskin_context_score": 0.15,
        }
    return {
        "version": DEFAULT_FORMULA_VERSION,
        "position": pos,
        "score_expression": "weighted_linear",
        "features": list(feature_weights.keys()),
        "weights": feature_weights,
        "normalization": {"method": "position_percentile"},
        "source_flags": {},
    }


def validate_formula(formula: Mapping[str, Any]) -> dict[str, Any]:
    for field in FORMULA_REQUIRED_FIELDS:
        if field not in formula or formula[field] is None:
            raise FormulaValidationError(f"formula.{field} is required")
    _reject_formula_text_tree(formula)

    position = _normalize_position(str(formula.get("position") or ""))
    if formula.get("score_expression") != "weighted_linear":
        raise FormulaValidationError("Only weighted_linear score_expression is supported")

    features = formula.get("features")
    weights = formula.get("weights")
    if not isinstance(features, list) or not features:
        raise FormulaValidationError("formula.features must be a non-empty list")
    if not isinstance(weights, Mapping):
        raise FormulaValidationError("formula.weights must be an object")

    source_flags = formula.get("source_flags") or {}
    if not isinstance(source_flags, Mapping):
        raise FormulaValidationError("formula.source_flags must be an object when provided")

    allowed = POSITION_FEATURE_ALLOWLISTS[position]
    normalized_features = []
    for raw_feature in features:
        feature = str(raw_feature).strip()
        if not feature:
            raise FormulaValidationError("blank feature name is not allowed")
        _reject_executable_text(feature)
        if feature in BLOCKED_METRIC_FEATURES:
            required_flag = BLOCKED_METRIC_FEATURES[feature]
            if source_flags.get(required_flag) is not True:
                raise FormulaValidationError(f"{feature} requires source flag {required_flag}=true")
        elif feature not in allowed:
            raise FormulaValidationError(f"{feature} is not allowed for position {position}")
        if feature not in weights:
            raise FormulaValidationError(f"{feature} is missing a weight")
        normalized_features.append(feature)

    for feature, raw_weight in weights.items():
        _reject_executable_text(str(feature))
        if feature not in normalized_features:
            raise FormulaValidationError(f"weight provided for unused feature {feature}")
        try:
            weight = float(raw_weight)
        except (TypeError, ValueError) as exc:
            raise FormulaValidationError(f"weight for {feature} must be numeric") from exc
        if weight < 0:
            raise FormulaValidationError(f"weight for {feature} must be non-negative")

    if sum(float(weights[feature]) for feature in normalized_features) <= 0:
        raise FormulaValidationError("formula weights must sum above zero")

    normalized = dict(formula)
    normalized["position"] = position
    normalized["features"] = normalized_features
    normalized["weights"] = {feature: float(weights[feature]) for feature in normalized_features}
    normalized.setdefault("source_flags", dict(source_flags))
    if not isinstance(normalized.get("normalization"), Mapping):
        raise FormulaValidationError("formula.normalization must be an object")
    return normalized


def validate_score(value: float | int | None, *, field_name: str = "score") -> float | None:
    if value is None:
        return None
    score = float(value)
    if score < 0 or score > 100:
        raise FormulaValidationError(f"{field_name} must be between 0 and 100")
    return score


def validate_input_tables(input_tables: list[str] | tuple[str, ...]) -> list[str]:
    normalized = [str(table).strip() for table in input_tables]
    for table in normalized:
        _reject_executable_text(table)
        if table not in ALLOWED_INPUT_TABLES:
            raise FormulaValidationError(f"{table} is not an approved ranking backtest input table")
    return normalized


def build_candidate_row(
    formula: Mapping[str, Any],
    *,
    formula_name: str,
    candidate_id: str | None = None,
    formula_set_id: str | None = None,
    target_name: str = "top_12_position",
    status: str = "draft",
) -> dict[str, Any]:
    normalized = validate_formula(formula)
    if target_name not in TARGET_DEFINITIONS:
        raise FormulaValidationError(f"Unknown target definition: {target_name}")

    position = normalized["position"]
    now = _now()
    return {
        "candidate_id": candidate_id or f"formula-{uuid.uuid4().hex[:12]}",
        "formula_set_id": formula_set_id,
        "formula_name": formula_name,
        "formula_version": str(normalized.get("version") or DEFAULT_FORMULA_VERSION),
        "position": position,
        "formula_json": _json(normalized),
        "feature_allowlist_json": _json(sorted(POSITION_FEATURE_ALLOWLISTS[position])),
        "target_definition_json": _json(TARGET_DEFINITIONS[target_name]),
        "source_requirements_json": _json(_source_requirements(normalized)),
        "status": status,
        "notes": None,
        "created_by": CREATED_BY,
        "created_at": now,
        "updated_at": None,
    }


def build_backtest_plan(
    formulas: list[Mapping[str, Any]],
    *,
    season_start: int,
    season_end: int,
    week_start: int | None = 1,
    week_end: int | None = 17,
    scoring_profile_id: str = "ppr",
    league_type_id: str = "redraft",
    roster_format_id: str = "one_qb",
    formula_set_id: str | None = None,
    target_name: str = "top_12_position",
    input_tables: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    if not formulas:
        raise FormulaValidationError("At least one formula is required")
    if season_start > season_end:
        raise FormulaValidationError("season_start must be less than or equal to season_end")
    if target_name not in TARGET_DEFINITIONS:
        raise FormulaValidationError(f"Unknown target definition: {target_name}")
    approved_inputs = validate_input_tables(input_tables or ALLOWED_INPUT_TABLES)

    candidates = [
        build_candidate_row(
            formula,
            formula_name=f"{validate_formula(formula)['position']} candidate",
            formula_set_id=formula_set_id,
            target_name=target_name,
        )
        for formula in formulas
    ]
    run_row = build_backtest_run_row(
        candidate_count=len(candidates),
        formula_set_id=formula_set_id,
        formula_version=DEFAULT_FORMULA_VERSION,
        season_start=season_start,
        season_end=season_end,
        week_start=week_start,
        week_end=week_end,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        target_name=target_name,
        input_tables=approved_inputs,
        dry_run=True,
        status="planned",
    )
    summary_rows = [
        build_candidate_summary_row(
            candidate_row=candidate,
            backtest_run_id=run_row["backtest_run_id"],
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            target_name=target_name,
        )
        for candidate in candidates
    ]
    positions = sorted({row["position"] for row in candidates})
    return {
        "dry_run": True,
        "write": False,
        "ready_for_write": False,
        "candidate_count": len(candidates),
        "positions": positions,
        "season_start": season_start,
        "season_end": season_end,
        "week_start": week_start,
        "week_end": week_end,
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "target_definition": TARGET_DEFINITIONS[target_name],
        "input_tables": approved_inputs,
        "blocked_metrics": sorted(BLOCKED_METRIC_FEATURES),
        "candidate_rows": candidates,
        "backtest_run_row": run_row,
        "candidate_summary_rows": summary_rows,
    }


def build_backtest_run_row(
    *,
    candidate_count: int,
    formula_set_id: str | None,
    formula_version: str,
    season_start: int,
    season_end: int,
    week_start: int | None,
    week_end: int | None,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    target_name: str,
    input_tables: list[str] | tuple[str, ...] = ALLOWED_INPUT_TABLES,
    dry_run: bool,
    status: str,
) -> dict[str, Any]:
    return {
        "backtest_run_id": f"ranking-backtest-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}",
        "formula_set_id": formula_set_id,
        "formula_version": formula_version,
        "candidate_count": candidate_count,
        "season_start": season_start,
        "season_end": season_end,
        "week_start": week_start,
        "week_end": week_end,
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "target_definition_json": _json(TARGET_DEFINITIONS[target_name]),
        "input_tables_json": _json(validate_input_tables(input_tables)),
        "dry_run": dry_run,
        "status": status,
        "created_by": CREATED_BY,
        "created_at": _now(),
        "completed_at": None,
        "error_message": None,
        "notes": None,
    }


def build_candidate_summary_row(
    *,
    candidate_row: Mapping[str, Any],
    backtest_run_id: str,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    target_name: str,
) -> dict[str, Any]:
    validate_score(None, field_name="planned_score")
    now = _now()
    metric_payload = {
        "sample_size": 0,
        "pairwise_win_rate": None,
        "top_n_hit_rate": None,
        "rank_correlation": None,
        "mean_absolute_error": None,
        "regret_score": None,
        "actual_points_captured_rate": None,
        "missing_input_rate": None,
    }
    return {
        "backtest_run_id": backtest_run_id,
        "candidate_id": candidate_row["candidate_id"],
        "formula_version": candidate_row["formula_version"],
        "position": candidate_row["position"],
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "target_name": target_name,
        "sample_size": 0,
        "pairwise_win_rate": None,
        "top_n_hit_rate": None,
        "rank_correlation": None,
        "mean_absolute_error": None,
        "regret_score": None,
        "actual_points_captured_rate": None,
        "missing_input_rate": None,
        "metric_json": _json(metric_payload),
        "missing_flags_json": _json({"backtest_not_executed": True}),
        "source_freshness_json": _json({"status": "planned"}),
        "created_at": now,
    }


def run_backtest_skeleton(
    formulas: list[Mapping[str, Any]],
    *,
    dry_run: bool = True,
    write: bool = False,
    client: Any | None = None,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    **plan_kwargs: Any,
) -> dict[str, Any]:
    if write:
        require_write_authorization()
    if not dry_run and not write:
        raise ValueError("write=True is required for non-dry-run ranking formula backtests")

    plan = build_backtest_plan(formulas, **plan_kwargs)
    if not write:
        return plan

    if client is None:
        raise ValueError("client is required for write mode")
    write_summary = save_backtest_plan(plan, project_id=project_id, dataset_id=dataset_id, client=client)
    return {
        **plan,
        "dry_run": False,
        "write": True,
        "ready_for_write": True,
        "write_summary": write_summary,
    }


def save_backtest_plan(
    plan: Mapping[str, Any],
    *,
    project_id: str,
    dataset_id: str,
    client: Any,
) -> dict[str, Any]:
    candidate_rows = [dict(row) for row in plan.get("candidate_rows", [])]
    run_rows = [dict(plan["backtest_run_row"])]
    summary_rows = [dict(row) for row in plan.get("candidate_summary_rows", [])]
    _validate_candidate_rows(candidate_rows)
    _validate_run_rows(run_rows)
    _validate_summary_rows(summary_rows)

    candidate_table = table_id(project_id, dataset_id, "ranking_formula_candidates")
    run_table = table_id(project_id, dataset_id, "ranking_backtest_runs")
    summary_table = table_id(project_id, dataset_id, "ranking_backtest_candidate_summaries")
    candidate_merge_sql = build_merge_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        table_name="ranking_formula_candidates",
        staging_table_name="ranking_formula_candidates_staging",
        key_fields=("candidate_id",),
    )
    run_merge_sql = build_merge_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        table_name="ranking_backtest_runs",
        staging_table_name="ranking_backtest_runs_staging",
        key_fields=("backtest_run_id",),
    )
    summary_merge_sql = build_merge_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        table_name="ranking_backtest_candidate_summaries",
        staging_table_name="ranking_backtest_candidate_summaries_staging",
        key_fields=(
            "backtest_run_id",
            "candidate_id",
            "position",
            "scoring_profile_id",
            "league_type_id",
            "roster_format_id",
            "target_name",
        ),
    )

    client.load_table_from_json(candidate_rows, table_id(project_id, dataset_id, "ranking_formula_candidates_staging")).result()
    client.query(candidate_merge_sql).result()
    client.load_table_from_json(run_rows, table_id(project_id, dataset_id, "ranking_backtest_runs_staging")).result()
    client.query(run_merge_sql).result()
    client.load_table_from_json(summary_rows, table_id(project_id, dataset_id, "ranking_backtest_candidate_summaries_staging")).result()
    client.query(summary_merge_sql).result()
    return {
        "candidate_row_count": len(candidate_rows),
        "backtest_run_row_count": len(run_rows),
        "candidate_summary_row_count": len(summary_rows),
        "candidate_table": candidate_table,
        "run_table": run_table,
        "summary_table": summary_table,
    }


def build_merge_sql(
    *,
    project_id: str,
    dataset_id: str,
    table_name: str,
    staging_table_name: str,
    key_fields: tuple[str, ...],
) -> str:
    fields = RANKING_TABLES[table_name]
    target_table = table_id(project_id, dataset_id, table_name)
    staging_table = table_id(project_id, dataset_id, staging_table_name)
    conditions = " AND ".join(f"target.{field} = source.{field}" for field in key_fields)
    update_fields = [field for field in fields if field not in key_fields]
    update_sql = ",\n        ".join(f"{field} = source.{field}" for field in update_fields)
    insert_fields = ", ".join(fields)
    insert_values = ", ".join(f"source.{field}" for field in fields)
    return f"""
MERGE `{target_table}` target
USING `{staging_table}` source
ON {conditions}
WHEN MATCHED THEN UPDATE SET
        {update_sql}
WHEN NOT MATCHED THEN INSERT ({insert_fields})
VALUES ({insert_values})
""".strip()


def table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    return f"{project_id}.{dataset_id}.{table_name}"


def _validate_candidate_rows(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        for field in RANKING_TABLES["ranking_formula_candidates"]:
            if field in {"formula_set_id", "notes", "updated_at"}:
                continue
            if row.get(field) is None:
                raise ValueError(f"candidate row missing {field}")
        validate_formula(json.loads(row["formula_json"]))


def _validate_run_rows(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        for field in RANKING_TABLES["ranking_backtest_runs"]:
            if field in {"formula_set_id", "week_start", "week_end", "completed_at", "error_message", "notes"}:
                continue
            if row.get(field) is None:
                raise ValueError(f"backtest run row missing {field}")


def _validate_summary_rows(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        for field in RANKING_TABLES["ranking_backtest_candidate_summaries"]:
            if field in {
                "pairwise_win_rate",
                "top_n_hit_rate",
                "rank_correlation",
                "mean_absolute_error",
                "regret_score",
                "actual_points_captured_rate",
                "missing_input_rate",
            }:
                continue
            if row.get(field) is None:
                raise ValueError(f"candidate summary row missing {field}")
        for field in ("pairwise_win_rate", "top_n_hit_rate", "actual_points_captured_rate", "missing_input_rate"):
            value = row.get(field)
            if value is not None and (float(value) < 0 or float(value) > 1):
                raise ValueError(f"{field} must be between 0 and 1")
        for field in ("mean_absolute_error", "regret_score"):
            value = row.get(field)
            if value is not None and float(value) < 0:
                raise ValueError(f"{field} must be non-negative")


def _normalize_position(position: str) -> str:
    value = position.strip().upper()
    if value not in POSITIONS:
        raise FormulaValidationError(f"Unsupported position: {position}")
    return value


def _reject_executable_text(value: str) -> None:
    lowered = value.lower()
    forbidden = ("select ", " from ", "join ", ";", "`", "import ", "eval(", "exec(", "__")
    if any(token in lowered for token in forbidden) or any(table in lowered for table in FORBIDDEN_TABLE_REFERENCES):
        raise FormulaValidationError("Formula text cannot contain SQL or executable code")


def _reject_formula_text_tree(value: Any) -> None:
    if isinstance(value, str):
        _reject_executable_text(value)
    elif isinstance(value, Mapping):
        for key, child in value.items():
            _reject_executable_text(str(key))
            _reject_formula_text_tree(child)
    elif isinstance(value, list):
        for child in value:
            _reject_formula_text_tree(child)


def _source_requirements(formula: Mapping[str, Any]) -> dict[str, Any]:
    source_flags = dict(formula.get("source_flags") or {})
    required_blocked = {
        feature: BLOCKED_METRIC_FEATURES[feature]
        for feature in formula.get("features", [])
        if feature in BLOCKED_METRIC_FEATURES
    }
    return {
        "allowed_input_tables": list(ALLOWED_INPUT_TABLES),
        "source_flags": source_flags,
        "blocked_metric_requirements": required_blocked,
    }


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan deterministic ranking formula backtests.")
    parser.add_argument("--position", choices=POSITIONS, default="QB")
    parser.add_argument("--season-start", type=int, default=2014)
    parser.add_argument("--season-end", type=int, default=2014)
    parser.add_argument("--week-start", type=int, default=1)
    parser.add_argument("--week-end", type=int, default=17)
    parser.add_argument("--target", default="top_12_position", choices=sorted(TARGET_DEFINITIONS))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    dry_run = args.dry_run or not args.write
    result = run_backtest_skeleton(
        [default_formula(args.position)],
        dry_run=dry_run,
        write=args.write,
        season_start=args.season_start,
        season_end=args.season_end,
        week_start=args.week_start,
        week_end=args.week_end,
        target_name=args.target,
    )
    print(json.dumps(_cli_summary(result), indent=2, sort_keys=True))
    return 0


def _cli_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "dry_run": result.get("dry_run"),
        "write": result.get("write"),
        "candidate_count": result.get("candidate_count"),
        "positions": result.get("positions"),
        "season_start": result.get("season_start"),
        "season_end": result.get("season_end"),
        "target_definition": result.get("target_definition"),
        "input_tables": result.get("input_tables"),
        "blocked_metrics": result.get("blocked_metrics"),
        "candidate_summary_count": len(result.get("candidate_summary_rows", [])),
    }


if __name__ == "__main__":
    raise SystemExit(main())
