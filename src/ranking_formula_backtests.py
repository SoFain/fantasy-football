"""Deterministic ranking formula validation and backtest planning."""

from __future__ import annotations

import argparse
import json
import math
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
MAX_REAL_DATA_SEASON_SPAN = 1
DEFAULT_REAL_DATA_LIMIT = 100
MAX_REAL_DATA_LIMIT = 500

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
ALLOWED_CANDIDATE_STATUSES = ("draft", "reviewed", "approved")
FEATURE_SOURCE_MAP = {
    "actual_points": "actual_points",
    "fantasy_points_ppr": "actual_points",
    "targets": "targets",
    "carries": "carries",
    "receiving_yards": "receiving_yards",
    "receiving_epa": "receiving_epa",
    "red_zone_targets": "red_zone_targets",
    "success_rate": "success_rate",
    "cpoe": "cpoe",
    "usage_volume": "usage_volume",
    "epa_per_play": "epa_per_play",
    "red_zone_opportunities": "red_zone_opportunities",
    "snap_share_proxy": "snap_share_proxy",
    "air_yards": "air_yards",
}
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


def validate_candidate_status(status: str) -> str:
    normalized = str(status).strip().lower()
    if normalized not in ALLOWED_CANDIDATE_STATUSES:
        raise FormulaValidationError(f"Unsupported candidate status: {status}")
    return normalized


def load_ranking_formula_candidates(
    *,
    client: Any,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    position: str | None = None,
    candidate_ids: list[str] | tuple[str, ...] | None = None,
    formula_version: str | None = None,
    status: str = "draft",
) -> list[dict[str, Any]]:
    normalized_position = _normalize_position(position) if position else None
    normalized_status = validate_candidate_status(status)
    normalized_candidate_ids = [str(candidate_id) for candidate_id in candidate_ids or []]
    for candidate_id in normalized_candidate_ids:
        _reject_executable_text(candidate_id)
    if formula_version is not None:
        _reject_executable_text(formula_version)
    query = f"""
SELECT
    candidate_id,
    formula_set_id,
    formula_name,
    formula_version,
    position,
    formula_json,
    feature_allowlist_json,
    target_definition_json,
    source_requirements_json,
    status,
    notes,
    created_by,
    created_at,
    updated_at
FROM `{table_id(project_id, dataset_id, "ranking_formula_candidates")}`
WHERE status = @status
  AND (@position IS NULL OR position = @position)
  AND (@formula_version IS NULL OR formula_version = @formula_version)
  AND (@candidate_ids_empty OR candidate_id IN UNNEST(@candidate_ids))
ORDER BY position, candidate_id
""".strip()
    rows = _query_records(
        client,
        query,
        [
            _scalar_param("status", "STRING", normalized_status),
            _scalar_param("position", "STRING", normalized_position),
            _scalar_param("formula_version", "STRING", formula_version),
            _scalar_param("candidate_ids_empty", "BOOL", not normalized_candidate_ids),
            _array_param("candidate_ids", "STRING", normalized_candidate_ids),
        ],
    )
    return [_candidate_from_record(row) for row in rows]


def load_ranking_formula_set(
    *,
    client: Any,
    formula_set_id: str,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    status: str = "draft",
) -> dict[str, Any]:
    _reject_executable_text(formula_set_id)
    normalized_status = validate_candidate_status(status)
    query = f"""
SELECT
    formula_set_id,
    formula_set_name,
    formula_set_version,
    qb_candidate_id,
    rb_candidate_id,
    wr_candidate_id,
    te_candidate_id,
    status,
    description,
    created_by,
    created_at,
    updated_at,
    notes
FROM `{table_id(project_id, dataset_id, "ranking_formula_sets")}`
WHERE formula_set_id = @formula_set_id
  AND status = @status
LIMIT 1
""".strip()
    rows = _query_records(
        client,
        query,
        [
            _scalar_param("formula_set_id", "STRING", formula_set_id),
            _scalar_param("status", "STRING", normalized_status),
        ],
    )
    if not rows:
        raise FormulaValidationError(f"Formula set not found for {formula_set_id} with status {normalized_status}")
    return dict(rows[0])


def load_candidates_for_formula_set(
    *,
    client: Any,
    formula_set_id: str,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    position: str | None = None,
    status: str = "draft",
) -> list[dict[str, Any]]:
    formula_set = load_ranking_formula_set(
        client=client,
        formula_set_id=formula_set_id,
        project_id=project_id,
        dataset_id=dataset_id,
        status=status,
    )
    candidate_ids = [
        formula_set["qb_candidate_id"],
        formula_set["rb_candidate_id"],
        formula_set["wr_candidate_id"],
        formula_set["te_candidate_id"],
    ]
    candidates = load_ranking_formula_candidates(
        client=client,
        project_id=project_id,
        dataset_id=dataset_id,
        position=position,
        candidate_ids=[candidate_id for candidate_id in candidate_ids if candidate_id],
        status=status,
    )
    expected_positions = {_normalize_position(position)} if position else set(POSITIONS)
    found_positions = {row["position"] for row in candidates}
    if not found_positions.issubset(expected_positions):
        raise FormulaValidationError(f"Formula set returned unexpected positions: {sorted(found_positions)}")
    if position and not candidates:
        raise FormulaValidationError(f"No {position} candidates found for formula set {formula_set_id}")
    return candidates


def load_bounded_feature_rows(
    *,
    client: Any,
    position: str,
    season_start: int,
    season_end: int,
    week_start: int | None,
    week_end: int | None,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    limit: int | None = DEFAULT_REAL_DATA_LIMIT,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
) -> list[dict[str, Any]]:
    bounds = _validate_real_data_bounds(
        position=position,
        season_start=season_start,
        season_end=season_end,
        week_start=week_start,
        week_end=week_end,
        limit=limit,
    )
    query = f"""
SELECT
    metrics.season,
    metrics.week,
    metrics.player_id_internal,
    COALESCE(metrics.player_name, truth.player_display_name, truth.player_name) AS player_name,
    metrics.position,
    metrics.team,
    metrics.scoring_profile_id,
    metrics.league_type_id,
    metrics.roster_format_id,
    COALESCE(profile.total_fantasy_points, truth.fantasy_points_ppr, truth.fantasy_points) AS actual_points,
    COALESCE(metrics.targets, truth.targets) AS targets,
    COALESCE(metrics.carries, truth.carries) AS carries,
    truth.receiving_yards AS receiving_yards,
    truth.receiving_epa AS receiving_epa,
    metrics.red_zone_targets AS red_zone_targets,
    metrics.success_rate AS success_rate,
    metrics.cpoe AS cpoe,
    metrics.opportunities AS usage_volume,
    metrics.epa_per_opportunity AS epa_per_play,
    metrics.red_zone_touches AS red_zone_opportunities,
    metrics.snap_share AS snap_share_proxy,
    truth.receiving_air_yards AS air_yards,
    metrics.source_freshness_json AS metrics_source_freshness_json,
    metrics.missing_data_flags AS metrics_missing_flags
FROM `{table_id(project_id, dataset_id, "player_week_advanced_metrics")}` metrics
LEFT JOIN `{table_id(project_id, dataset_id, "analytics_player_weekly_truth")}` truth
  ON metrics.season = truth.season
 AND metrics.week = truth.week
 AND metrics.player_id_internal = truth.player_id
LEFT JOIN `{table_id(project_id, dataset_id, "analytics_player_fantasy_points_by_profile")}` profile
  ON metrics.season = profile.season
 AND metrics.week = profile.week
 AND metrics.player_id_internal = profile.player_id_internal
 AND profile.scoring_profile_id = @scoring_profile_id
 AND profile.league_type_id = @league_type_id
 AND profile.roster_format_id = @roster_format_id
WHERE metrics.position = @position
  AND metrics.season BETWEEN @season_start AND @season_end
  AND (@week_start IS NULL OR metrics.week >= @week_start)
  AND (@week_end IS NULL OR metrics.week <= @week_end)
  AND metrics.scoring_profile_id = @scoring_profile_id
  AND metrics.league_type_id = @league_type_id
  AND metrics.roster_format_id = @roster_format_id
ORDER BY metrics.season, metrics.week, metrics.player_id_internal
LIMIT @limit
""".strip()
    return _query_records(
        client,
        query,
        [
            _scalar_param("position", "STRING", bounds["position"]),
            _scalar_param("season_start", "INT64", bounds["season_start"]),
            _scalar_param("season_end", "INT64", bounds["season_end"]),
            _scalar_param("week_start", "INT64", bounds["week_start"]),
            _scalar_param("week_end", "INT64", bounds["week_end"]),
            _scalar_param("scoring_profile_id", "STRING", scoring_profile_id),
            _scalar_param("league_type_id", "STRING", league_type_id),
            _scalar_param("roster_format_id", "STRING", roster_format_id),
            _scalar_param("limit", "INT64", bounds["limit"]),
        ],
    )


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


def run_seeded_candidate_real_data_dry_run(
    *,
    client: Any,
    formula_set_id: str,
    position: str,
    season_start: int,
    season_end: int,
    week_start: int | None,
    week_end: int | None,
    limit: int,
    status: str = "draft",
    scoring_profile_id: str = "ppr",
    league_type_id: str = "redraft",
    roster_format_id: str = "one_qb",
    target_name: str = "top_12_position",
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
) -> dict[str, Any]:
    if target_name not in TARGET_DEFINITIONS:
        raise FormulaValidationError(f"Unknown target definition: {target_name}")
    normalized_position = _normalize_position(position)
    candidates = load_candidates_for_formula_set(
        client=client,
        formula_set_id=formula_set_id,
        project_id=project_id,
        dataset_id=dataset_id,
        position=normalized_position,
        status=status,
    )
    feature_rows = load_bounded_feature_rows(
        client=client,
        position=normalized_position,
        season_start=season_start,
        season_end=season_end,
        week_start=week_start,
        week_end=week_end,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        limit=limit,
        project_id=project_id,
        dataset_id=dataset_id,
    )
    run_row = build_backtest_run_row(
        candidate_count=len(candidates),
        formula_set_id=formula_set_id,
        formula_version=candidates[0]["formula_version"] if candidates else DEFAULT_FORMULA_VERSION,
        season_start=season_start,
        season_end=season_end,
        week_start=week_start,
        week_end=week_end,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        target_name=target_name,
        input_tables=ALLOWED_INPUT_TABLES,
        dry_run=True,
        status="planned",
    )
    result_rows = build_result_rows_for_candidates(
        candidates=candidates,
        feature_rows=feature_rows,
        backtest_run_id=run_row["backtest_run_id"],
        formula_set_id=formula_set_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        target_name=target_name,
    )
    summary_rows = [
        build_summary_from_results(
            candidate_row=candidate,
            result_rows=[row for row in result_rows if row["candidate_id"] == candidate["candidate_id"]],
            backtest_run_id=run_row["backtest_run_id"],
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            target_name=target_name,
        )
        for candidate in candidates
    ]
    return {
        "dry_run": True,
        "write": False,
        "formula_set_id": formula_set_id,
        "candidate_count": len(candidates),
        "input_row_count": len(feature_rows),
        "result_shape_count": len(result_rows),
        "candidate_summary_count": len(summary_rows),
        "positions": [normalized_position],
        "season_start": season_start,
        "season_end": season_end,
        "week_start": week_start,
        "week_end": week_end,
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "target_definition": TARGET_DEFINITIONS[target_name],
        "input_tables": list(ALLOWED_INPUT_TABLES),
        "blocked_metrics": sorted(BLOCKED_METRIC_FEATURES),
        "candidate_rows": candidates,
        "backtest_run_row": run_row,
        "result_rows": result_rows,
        "candidate_summary_rows": summary_rows,
    }


def build_result_rows_for_candidates(
    *,
    candidates: list[Mapping[str, Any]],
    feature_rows: list[Mapping[str, Any]],
    backtest_run_id: str,
    formula_set_id: str,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    target_name: str,
) -> list[dict[str, Any]]:
    actual_ranks = _actual_ranks(feature_rows)
    result_rows: list[dict[str, Any]] = []
    for candidate in candidates:
        formula = validate_formula(json.loads(candidate["formula_json"]))
        candidate_rows: list[dict[str, Any]] = []
        for feature_row in feature_rows:
            if str(feature_row.get("position", "")).upper() != formula["position"]:
                continue
            evaluated = evaluate_formula_for_feature_row(formula, feature_row)
            actual_rank = actual_ranks.get(_result_grain_key(feature_row))
            target_hit = _target_hit(target_name, actual_rank)
            row = {
                "backtest_run_id": backtest_run_id,
                "candidate_id": candidate["candidate_id"],
                "formula_set_id": formula_set_id,
                "formula_version": candidate["formula_version"],
                "position": candidate["position"],
                "season": int(feature_row["season"]),
                "week": int(feature_row["week"]),
                "player_id_internal": str(feature_row["player_id_internal"]),
                "player_name": feature_row.get("player_name"),
                "team": feature_row.get("team"),
                "scoring_profile_id": scoring_profile_id,
                "league_type_id": league_type_id,
                "roster_format_id": roster_format_id,
                "predicted_score": evaluated["predicted_score"],
                "predicted_rank_position": None,
                "actual_points": _safe_float(feature_row.get("actual_points")),
                "actual_rank_position": actual_rank,
                "target_name": target_name,
                "target_hit": target_hit,
                "win_rate": None if target_hit is None else (1.0 if target_hit else 0.0),
                "feature_values_json": _json(evaluated["feature_values"]),
                "result_json": _json(
                    {
                        "available_feature_weight": evaluated["available_weight"],
                        "missing_feature_count": len(evaluated["missing_features"]),
                    }
                ),
                "missing_flags_json": _json({"missing_features": evaluated["missing_features"]}),
                "source_freshness_json": _json(_source_freshness_for_feature_row(feature_row)),
                "created_at": _now(),
            }
            candidate_rows.append(row)
        _assign_predicted_ranks(candidate_rows)
        result_rows.extend(candidate_rows)
    return result_rows


def evaluate_formula_for_feature_row(formula: Mapping[str, Any], feature_row: Mapping[str, Any]) -> dict[str, Any]:
    values: dict[str, float] = {}
    missing_features: list[str] = []
    weighted_score = 0.0
    available_weight = 0.0
    for feature in formula["features"]:
        source_field = FEATURE_SOURCE_MAP.get(feature)
        raw_value = feature_row.get(source_field) if source_field else None
        numeric_value = _safe_float(raw_value)
        if numeric_value is None:
            missing_features.append(feature)
            continue
        feature_score = _feature_value_to_score(feature, numeric_value)
        values[feature] = numeric_value
        weight = float(formula["weights"][feature])
        weighted_score += feature_score * weight
        available_weight += weight
    predicted_score = None
    if available_weight > 0:
        predicted_score = validate_score(weighted_score / available_weight, field_name="predicted_score")
    return {
        "predicted_score": predicted_score,
        "feature_values": values,
        "missing_features": missing_features,
        "available_weight": available_weight,
    }


def build_summary_from_results(
    *,
    candidate_row: Mapping[str, Any],
    result_rows: list[Mapping[str, Any]],
    backtest_run_id: str,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    target_name: str,
) -> dict[str, Any]:
    sample_size = len(result_rows)
    target_rows = [row for row in result_rows if row.get("target_hit") is not None]
    scored_rows = [row for row in result_rows if row.get("predicted_score") is not None]
    missing_rates = []
    formula = json.loads(candidate_row["formula_json"])
    feature_count = max(len(formula.get("features", [])), 1)
    for row in result_rows:
        missing = json.loads(row["missing_flags_json"]).get("missing_features", [])
        missing_rates.append(len(missing) / feature_count)
    top_n_hit_rate = None
    if target_rows:
        top_n_hit_rate = sum(1 for row in target_rows if row["target_hit"]) / len(target_rows)
    rank_correlation = _rank_correlation(scored_rows)
    metric_payload = {
        "sample_size": sample_size,
        "pairwise_win_rate": None,
        "top_n_hit_rate": top_n_hit_rate,
        "rank_correlation": rank_correlation,
        "mean_absolute_error": None,
        "regret_score": None,
        "actual_points_captured_rate": None,
        "missing_input_rate": sum(missing_rates) / len(missing_rates) if missing_rates else None,
        "null_metric_reasons": {
            "pairwise_win_rate": "pairwise comparisons are not implemented in the dry-run skeleton",
            "mean_absolute_error": "predicted scores are normalized 0-100 and not calibrated to fantasy points",
            "regret_score": "requires a champion or baseline comparison",
            "actual_points_captured_rate": "requires a lineup or top-N capture definition",
        },
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
        "sample_size": sample_size,
        "pairwise_win_rate": None,
        "top_n_hit_rate": top_n_hit_rate,
        "rank_correlation": rank_correlation,
        "mean_absolute_error": None,
        "regret_score": None,
        "actual_points_captured_rate": None,
        "missing_input_rate": metric_payload["missing_input_rate"],
        "metric_json": _json(metric_payload),
        "missing_flags_json": _json({"summary_from_dry_run": True}),
        "source_freshness_json": _json({"status": "dry_run", "result_row_count": sample_size}),
        "created_at": _now(),
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


def _validate_real_data_bounds(
    *,
    position: str,
    season_start: int,
    season_end: int,
    week_start: int | None,
    week_end: int | None,
    limit: int | None,
) -> dict[str, Any]:
    normalized_position = _normalize_position(position)
    if season_start is None or season_end is None:
        raise FormulaValidationError("season_start and season_end are required")
    if season_start > season_end:
        raise FormulaValidationError("season_start must be less than or equal to season_end")
    if season_end - season_start + 1 > MAX_REAL_DATA_SEASON_SPAN:
        raise FormulaValidationError(f"season span must be at most {MAX_REAL_DATA_SEASON_SPAN}")
    if week_start is not None and week_end is not None and week_start > week_end:
        raise FormulaValidationError("week_start must be less than or equal to week_end")
    bounded_limit = DEFAULT_REAL_DATA_LIMIT if limit is None else int(limit)
    if bounded_limit <= 0:
        raise FormulaValidationError("limit must be positive")
    if bounded_limit > MAX_REAL_DATA_LIMIT:
        bounded_limit = MAX_REAL_DATA_LIMIT
    return {
        "position": normalized_position,
        "season_start": int(season_start),
        "season_end": int(season_end),
        "week_start": week_start,
        "week_end": week_end,
        "limit": bounded_limit,
    }


def _candidate_from_record(record: Mapping[str, Any]) -> dict[str, Any]:
    row = dict(record)
    row["position"] = _normalize_position(str(row["position"]))
    validate_candidate_status(str(row["status"]))
    validate_formula(json.loads(row["formula_json"]))
    return row


def _query_records(client: Any, query: str, query_parameters: list[Any]) -> list[dict[str, Any]]:
    result = client.query(query, job_config=_query_job_config(query_parameters)).result()
    return [dict(record) for record in result]


def _query_job_config(query_parameters: list[Any]) -> Any:
    from google.cloud import bigquery

    return bigquery.QueryJobConfig(query_parameters=query_parameters)


def _scalar_param(name: str, param_type: str, value: Any) -> Any:
    from google.cloud import bigquery

    return bigquery.ScalarQueryParameter(name, param_type, value)


def _array_param(name: str, param_type: str, values: list[Any]) -> Any:
    from google.cloud import bigquery

    return bigquery.ArrayQueryParameter(name, param_type, values)


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def _feature_value_to_score(feature: str, value: float) -> float:
    if feature in {"success_rate", "cpoe", "snap_share_proxy"}:
        return max(0.0, min(100.0, value * 100 if value <= 1 else value))
    if feature in {"actual_points", "fantasy_points_ppr", "recent_points_avg"}:
        return max(0.0, min(100.0, (value / 35.0) * 100.0))
    if feature in {"epa_per_play", "passing_epa_per_play", "receiving_epa", "team_epa_per_play"}:
        return max(0.0, min(100.0, 50.0 + (value * 25.0)))
    if feature in {"air_yards", "receiving_yards"}:
        return max(0.0, min(100.0, (value / 150.0) * 100.0))
    if feature in {"targets", "carries", "dropbacks", "rushing_attempts", "usage_volume", "red_zone_targets", "red_zone_opportunities", "goal_line_opportunities"}:
        return max(0.0, min(100.0, (value / 25.0) * 100.0))
    return max(0.0, min(100.0, value))


def _source_freshness_for_feature_row(row: Mapping[str, Any]) -> dict[str, Any]:
    raw = row.get("metrics_source_freshness_json")
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    return {"input_table": "player_week_advanced_metrics", "status": "bounded_dry_run"}


def _actual_ranks(feature_rows: list[Mapping[str, Any]]) -> dict[tuple[int, int, str], int]:
    grouped: dict[tuple[int, int], list[Mapping[str, Any]]] = {}
    for row in feature_rows:
        if _safe_float(row.get("actual_points")) is None:
            continue
        grouped.setdefault((int(row["season"]), int(row["week"])), []).append(row)
    ranks: dict[tuple[int, int, str], int] = {}
    for rows_in_week in grouped.values():
        sorted_rows = sorted(rows_in_week, key=lambda item: _safe_float(item.get("actual_points")) or -9999, reverse=True)
        for index, row in enumerate(sorted_rows, start=1):
            ranks[_result_grain_key(row)] = index
    return ranks


def _result_grain_key(row: Mapping[str, Any]) -> tuple[int, int, str]:
    return (int(row["season"]), int(row["week"]), str(row["player_id_internal"]))


def _target_hit(target_name: str, actual_rank: int | None) -> bool | None:
    if actual_rank is None:
        return None
    target = TARGET_DEFINITIONS[target_name]
    threshold = target.get("rank_threshold")
    if threshold is None:
        return None
    return actual_rank <= int(threshold)


def _assign_predicted_ranks(rows: list[dict[str, Any]]) -> None:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for row in rows:
        if row["predicted_score"] is None:
            continue
        grouped.setdefault((row["season"], row["week"]), []).append(row)
    for rows_in_week in grouped.values():
        sorted_rows = sorted(rows_in_week, key=lambda item: item["predicted_score"], reverse=True)
        for index, row in enumerate(sorted_rows, start=1):
            row["predicted_rank_position"] = index


def _rank_correlation(rows: list[Mapping[str, Any]]) -> float | None:
    pairs = [
        (row.get("predicted_rank_position"), row.get("actual_rank_position"))
        for row in rows
        if row.get("predicted_rank_position") is not None and row.get("actual_rank_position") is not None
    ]
    if len(pairs) < 2:
        return None
    predicted = [float(pair[0]) for pair in pairs]
    actual = [float(pair[1]) for pair in pairs]
    return _pearson(predicted, actual)


def _pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_denominator = math.sqrt(sum((a - left_mean) ** 2 for a in left))
    right_denominator = math.sqrt(sum((b - right_mean) ** 2 for b in right))
    if left_denominator == 0 or right_denominator == 0:
        return None
    return numerator / (left_denominator * right_denominator)


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
    parser.add_argument("--from-bigquery-candidates", action="store_true")
    parser.add_argument("--formula-set-id")
    parser.add_argument("--status", default="draft")
    parser.add_argument("--limit", type=int, default=DEFAULT_REAL_DATA_LIMIT)
    parser.add_argument("--scoring-profile-id", default="ppr")
    parser.add_argument("--league-type-id", default="redraft")
    parser.add_argument("--roster-format-id", default="one_qb")
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    args = parser.parse_args(argv)

    if args.from_bigquery_candidates:
        if args.write:
            raise ValueError("--write is not supported for seeded-candidate real-data dry-runs")
        if not args.formula_set_id:
            raise ValueError("--formula-set-id is required with --from-bigquery-candidates")
        from google.cloud import bigquery

        client = bigquery.Client(project=args.project)
        result = run_seeded_candidate_real_data_dry_run(
            client=client,
            formula_set_id=args.formula_set_id,
            position=args.position,
            season_start=args.season_start,
            season_end=args.season_end,
            week_start=args.week_start,
            week_end=args.week_end,
            limit=args.limit,
            status=args.status,
            scoring_profile_id=args.scoring_profile_id,
            league_type_id=args.league_type_id,
            roster_format_id=args.roster_format_id,
            target_name=args.target,
            project_id=args.project,
            dataset_id=args.dataset,
        )
        print(json.dumps(_cli_summary(result), indent=2, sort_keys=True))
        return 0

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
        "formula_set_id": result.get("formula_set_id"),
        "input_row_count": result.get("input_row_count"),
        "result_shape_count": result.get("result_shape_count"),
        "sample_size": _first_summary_value(result, "sample_size"),
        "missing_input_rate": _first_summary_value(result, "missing_input_rate"),
        "top_n_hit_rate": _first_summary_value(result, "top_n_hit_rate"),
        "rank_correlation": _first_summary_value(result, "rank_correlation"),
    }


def _first_summary_value(result: Mapping[str, Any], field: str) -> Any:
    summaries = result.get("candidate_summary_rows") or []
    if not summaries:
        return None
    return summaries[0].get(field)


if __name__ == "__main__":
    raise SystemExit(main())
