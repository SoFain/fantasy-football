"""Deterministic ranking formula validation and backtest planning."""

from __future__ import annotations

import argparse
import json
import math
import os
import uuid
from collections import Counter
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
DEFAULT_SCORING_PROFILES = ("ppr", "half_ppr", "standard", "gng_keeper")
DEFAULT_LEAGUE_TYPE_ID = "redraft"
DEFAULT_ROSTER_FORMAT_ID = "one_qb"
DEFAULT_BACKTEST_VERSION = "v0"
POSITION_TOP_N = {"QB": 12, "RB": 24, "WR": 24, "TE": 12}
OVERALL_DRAFT_TOP_N = (24, 50, 100)
PICK_BANDS = (
    (1, 12, "1-12"),
    (13, 24, "13-24"),
    (25, 36, "25-36"),
    (37, 60, "37-60"),
    (61, 100, "61-100"),
    (101, None, "101+"),
)
DRAFT_UTILITY_K_BY_POSITION = {
    "QB": (6, 12),
    "RB": (12, 24),
    "WR": (12, 24, 36),
    "TE": (3, 6, 12),
}
DRAFT_UTILITY_OVERALL_K = (24, 50, 100)
DRAFT_UTILITY_METRIC_CONTRACT = {
    "ndcg_at_k": "Discounted gain from predicted top K divided by ideal discounted gain for the same weekly slice.",
    "value_captured_at_k": "Actual fantasy points captured by predicted top K divided by actual top K points.",
    "elite_recall_at_k": "Share of actual top K players captured by predicted top K.",
    "tier_accuracy": "Share of rows whose predicted rank tier matches the actual rank tier.",
    "bust_rate": "Share of predicted top K rows that finish outside twice the K threshold.",
    "pick_band_regret": "Positive value lost by predicted pick-band allocation compared with actual pick-band allocation.",
    "overall_pairwise_draft_win_rate": "Pairwise win rate for cross-position draft ordering, bounded to top draft ranks.",
    "high_confidence_pairwise_win_rate": "Pairwise win rate when predicted scores differ by at least ten points.",
    "value_over_replacement_captured_rate": "Positive VOR captured by predicted top K divided by ideal actual top K VOR.",
}
VOR_BASELINE_POLICIES = {
    "current_sql_vorp_qb12_rb24_wr24_te12": {"QB": 12, "RB": 24, "WR": 24, "TE": 12},
    "deep_vorp_qb15_rb36_wr55_te12": {"QB": 15, "RB": 36, "WR": 55, "TE": 12},
    "middle_vorp_qb12_rb30_wr42_te12": {"QB": 12, "RB": 30, "WR": 42, "TE": 12},
}
BQML_TRAIN_SEASONS = (2017, 2023)
BQML_VALIDATION_SEASON = 2024
BQML_HOLDOUT_SEASON = 2025
BQML_COMPONENT_SPECS = ("bqml_logistic_elite", "bqml_linear_points")
BQML_NUMERIC_PREDICTORS = (
    "profile_points_score",
    "opportunity_score_proxy",
    "efficiency_score_proxy",
    "analytical_grade_proxy",
    "role_stability_score",
    "recent_points_avg",
    "targets",
    "carries",
    "receiving_yards",
    "receiving_epa",
    "red_zone_targets",
    "success_rate",
    "passing_success_rate",
    "dropbacks",
    "rushing_attempts",
    "rush_success_rate",
    "receiving_usage",
    "cpoe",
    "usage_volume",
    "epa_per_play",
    "passing_epa_per_play",
    "team_epa_per_play",
    "red_zone_opportunities",
    "goal_line_opportunities",
    "snap_share_proxy",
    "air_yards",
    "team_pass_rate",
    "qb_rushing_leverage_index",
    "rb_high_value_opportunity_score",
    "receiving_role_dominance_score",
    "red_zone_usage_score",
    "goal_line_usage_score",
    "team_environment_score",
    "spike_week_rate_3yr",
    "bust_week_rate_3yr",
    "elite_week_rate_3yr",
    "points_per_game_slope_3yr",
    "total_points_slope_3yr",
    "opportunity_slope_3yr",
    "target_share_slope_3yr",
    "carry_share_slope_3yr",
    "receiving_usage_slope_3yr",
    "wopr_slope_3yr",
    "epa_slope_3yr",
    "efficiency_slope_3yr",
    "availability_rate_3yr",
    "weekly_volatility_3yr",
    "improving_3yr",
    "declining_3yr",
    "breakout_trajectory_3yr",
    "xfp_score_3yr",
    "xfp_share_3yr",
    "fantasy_points_over_expectation_3yr",
    "offensive_snap_share_3yr",
    "snap_role_stability_3yr",
    "receiving_role_dominance_xfp_3yr",
    "high_value_xfp_score_3yr",
    "qb_ngs_efficiency_score_3yr",
    "injury_risk_score_3yr",
    "depth_chart_role_score_3yr",
    "receiving_xfp_pbp_3yr",
    "rushing_xfp_pbp_3yr",
    "passing_xfp_pbp_3yr",
    "red_zone_xfp_score_3yr",
    "goal_line_xfp_score_3yr",
    "high_value_target_xfp_score_3yr",
    "high_value_rush_xfp_score_3yr",
    "receiving_xfp_share_pbp_3yr",
    "rushing_xfp_share_pbp_3yr",
    "opportunity_quality_score_3yr",
    "receiving_first_down_exp_pbp_3yr",
    "rushing_first_down_exp_pbp_3yr",
    "passing_first_down_exp_pbp_3yr",
    "high_value_first_down_opportunity_score_3yr",
    "receiving_chain_mover_score_3yr",
    "rushing_chain_mover_score_3yr",
)
BQML_CATEGORICAL_PREDICTORS = ("scoring_profile_id", "position")
ENSEMBLE_REFERENCE_SEASONS = tuple(range(2017, 2024))
ENSEMBLE_TUNING_SEASON = 2024
ENSEMBLE_HOLDOUT_SEASON = 2025
ENSEMBLE_VERSION = "ranking_backtest_sql_native_ensemble_v0_2024_2025"
ENSEMBLE_FORMULA_COMPONENTS = {
    "current_pigskin": "current_pigskin_candidate_score_v1",
    "simple_projection": "simple_projection_points_baseline_v0",
    "scarcity_adjusted": "scarcity_adjusted_draft_value_v0",
}
ENSEMBLE_BQML_COMPONENTS = {
    "bqml_logistic_elite": "bqml_logistic_elite",
    "bqml_linear_points": "bqml_linear_points",
}

POSITIONS = ("QB", "RB", "WR", "TE")
TARGET_DEFINITIONS = {
    "position_default_top_n": {
        "target_name": "position_default_top_n",
        "position_thresholds": POSITION_TOP_N if "POSITION_TOP_N" in globals() else {"QB": 12, "RB": 24, "WR": 24, "TE": 12},
        "description": "Player finishes inside the position-specific default top-N threshold.",
    },
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
    "profile_points_score",
    "analytical_grade_proxy",
    "opportunity_score_proxy",
    "efficiency_score_proxy",
    "role_stability_score",
    "epa_per_play",
    "success_rate",
    "usage_volume",
    "snap_share_proxy",
    "red_zone_opportunities",
    "team_epa_per_play",
    "opponent_allowed_points",
    "pigskin_context_score",
    "team_environment_score",
    "red_zone_usage_score",
    "goal_line_usage_score",
    "spike_week_rate_3yr",
    "bust_week_rate_3yr",
    "elite_week_rate_3yr",
}
TREND_FEATURES = {
    "points_per_game_slope_3yr",
    "total_points_slope_3yr",
    "opportunity_slope_3yr",
    "target_share_slope_3yr",
    "carry_share_slope_3yr",
    "receiving_usage_slope_3yr",
    "wopr_slope_3yr",
    "epa_slope_3yr",
    "efficiency_slope_3yr",
    "availability_rate_3yr",
    "weekly_volatility_3yr",
    "improving_3yr",
    "declining_3yr",
    "breakout_trajectory_3yr",
}
IDEAL_STAT_FEATURES = {
    "xfp_score_3yr",
    "xfp_share_3yr",
    "fantasy_points_over_expectation_3yr",
    "offensive_snap_share_3yr",
    "snap_role_stability_3yr",
    "receiving_role_dominance_xfp_3yr",
    "high_value_xfp_score_3yr",
    "qb_ngs_efficiency_score_3yr",
    "injury_risk_score_3yr",
    "injury_status_score_3yr",
    "injury_burden_score_3yr",
    "missed_time_risk_score_3yr",
    "availability_score_3yr",
    "depth_chart_role_score_3yr",
}
PBP_XFP_FEATURES = {
    "receiving_xfp_pbp_3yr",
    "rushing_xfp_pbp_3yr",
    "passing_xfp_pbp_3yr",
    "red_zone_xfp_score_3yr",
    "goal_line_xfp_score_3yr",
    "high_value_target_xfp_score_3yr",
    "high_value_rush_xfp_score_3yr",
    "receiving_xfp_share_pbp_3yr",
    "rushing_xfp_share_pbp_3yr",
    "opportunity_quality_score_3yr",
}
FIRST_DOWN_PBP_PROXY_FEATURES = {
    "receiving_first_down_exp_pbp_3yr",
    "rushing_first_down_exp_pbp_3yr",
    "passing_first_down_exp_pbp_3yr",
    "high_value_first_down_opportunity_score_3yr",
    "receiving_chain_mover_score_3yr",
    "rushing_chain_mover_score_3yr",
}
RB_WEIGHTED_OPPORTUNITY_FEATURES = {
    "red_zone_carries",
    "outside_red_zone_targets",
    "outside_red_zone_carries",
    "gemini31_rb_weighted_opportunity_ppr",
}
POSITION_FEATURE_ALLOWLISTS: dict[str, set[str]] = {
    "QB": COMMON_FEATURES
    | TREND_FEATURES
    | IDEAL_STAT_FEATURES
    | PBP_XFP_FEATURES
    | FIRST_DOWN_PBP_PROXY_FEATURES
    | {
        "passing_epa_per_play",
        "passing_success_rate",
        "cpoe",
        "dropbacks",
        "rushing_attempts",
        "designed_rush_share_proxy",
        "qb_rushing_leverage_index",
    },
    "RB": COMMON_FEATURES
    | TREND_FEATURES
    | IDEAL_STAT_FEATURES
    | PBP_XFP_FEATURES
    | FIRST_DOWN_PBP_PROXY_FEATURES
    | RB_WEIGHTED_OPPORTUNITY_FEATURES
    | {
        "carries",
        "targets",
        "red_zone_targets",
        "rush_success_rate",
        "receiving_usage",
        "goal_line_opportunities",
        "rb_high_value_opportunity_score",
    },
    "WR": COMMON_FEATURES
    | TREND_FEATURES
    | IDEAL_STAT_FEATURES
    | PBP_XFP_FEATURES
    | FIRST_DOWN_PBP_PROXY_FEATURES
    | {
        "targets",
        "air_yards",
        "receiving_yards",
        "receiving_epa",
        "red_zone_targets",
        "receiving_role_dominance_score",
    },
    "TE": COMMON_FEATURES
    | TREND_FEATURES
    | IDEAL_STAT_FEATURES
    | PBP_XFP_FEATURES
    | FIRST_DOWN_PBP_PROXY_FEATURES
    | {
        "targets",
        "air_yards",
        "receiving_yards",
        "receiving_epa",
        "red_zone_targets",
        "team_pass_rate",
        "receiving_role_dominance_score",
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
    "player_week_opportunity_metrics",
    "player_week_ideal_opportunity_metrics",
    "player_week_pbp_opportunity_metrics",
    "player_week_role_context_metrics",
)
ALLOWED_CANDIDATE_STATUSES = ("draft", "reviewed", "approved")
FEATURE_SOURCE_MAP = {
    "actual_points": "actual_points",
    "fantasy_points_ppr": "actual_points",
    "recent_points_avg": "recent_points_avg",
    "profile_points_score": "profile_points_score",
    "analytical_grade_proxy": "analytical_grade_proxy",
    "opportunity_score_proxy": "opportunity_score_proxy",
    "efficiency_score_proxy": "efficiency_score_proxy",
    "role_stability_score": "role_stability_score",
    "targets": "targets",
    "carries": "carries",
    "receiving_yards": "receiving_yards",
    "receiving_epa": "receiving_epa",
    "red_zone_targets": "red_zone_targets",
    "red_zone_carries": "red_zone_carries",
    "outside_red_zone_targets": "outside_red_zone_targets",
    "outside_red_zone_carries": "outside_red_zone_carries",
    "gemini31_rb_weighted_opportunity_ppr": "gemini31_rb_weighted_opportunity_ppr",
    "success_rate": "success_rate",
    "passing_success_rate": "passing_success_rate",
    "cpoe": "cpoe",
    "dropbacks": "dropbacks",
    "rushing_attempts": "rushing_attempts",
    "rush_success_rate": "rush_success_rate",
    "receiving_usage": "receiving_usage",
    "usage_volume": "usage_volume",
    "epa_per_play": "epa_per_play",
    "passing_epa_per_play": "passing_epa_per_play",
    "team_epa_per_play": "team_epa_per_play",
    "red_zone_opportunities": "red_zone_opportunities",
    "goal_line_opportunities": "goal_line_opportunities",
    "snap_share_proxy": "snap_share_proxy",
    "air_yards": "air_yards",
    "team_pass_rate": "team_pass_rate",
    "qb_rushing_leverage_index": "qb_rushing_leverage_index",
    "rb_high_value_opportunity_score": "rb_high_value_opportunity_score",
    "receiving_role_dominance_score": "receiving_role_dominance_score",
    "red_zone_usage_score": "red_zone_usage_score",
    "goal_line_usage_score": "goal_line_usage_score",
    "team_environment_score": "team_environment_score",
    "spike_week_rate_3yr": "spike_week_rate_3yr",
    "bust_week_rate_3yr": "bust_week_rate_3yr",
    "elite_week_rate_3yr": "elite_week_rate_3yr",
    "points_per_game_slope_3yr": "points_per_game_slope_3yr",
    "total_points_slope_3yr": "total_points_slope_3yr",
    "opportunity_slope_3yr": "opportunity_slope_3yr",
    "target_share_slope_3yr": "target_share_slope_3yr",
    "carry_share_slope_3yr": "carry_share_slope_3yr",
    "receiving_usage_slope_3yr": "receiving_usage_slope_3yr",
    "wopr_slope_3yr": "wopr_slope_3yr",
    "epa_slope_3yr": "epa_slope_3yr",
    "efficiency_slope_3yr": "efficiency_slope_3yr",
    "availability_rate_3yr": "availability_rate_3yr",
    "weekly_volatility_3yr": "weekly_volatility_3yr",
    "improving_3yr": "improving_3yr",
    "declining_3yr": "declining_3yr",
    "breakout_trajectory_3yr": "breakout_trajectory_3yr",
    "xfp_score_3yr": "xfp_score_3yr",
    "xfp_share_3yr": "xfp_share_3yr",
    "fantasy_points_over_expectation_3yr": "fantasy_points_over_expectation_3yr",
    "offensive_snap_share_3yr": "offensive_snap_share_3yr",
    "snap_role_stability_3yr": "snap_role_stability_3yr",
    "receiving_role_dominance_xfp_3yr": "receiving_role_dominance_xfp_3yr",
    "high_value_xfp_score_3yr": "high_value_xfp_score_3yr",
    "qb_ngs_efficiency_score_3yr": "qb_ngs_efficiency_score_3yr",
    "injury_risk_score_3yr": "injury_risk_score_3yr",
    "injury_status_score_3yr": "injury_status_score_3yr",
    "injury_burden_score_3yr": "injury_burden_score_3yr",
    "missed_time_risk_score_3yr": "missed_time_risk_score_3yr",
    "availability_score_3yr": "availability_score_3yr",
    "depth_chart_role_score_3yr": "depth_chart_role_score_3yr",
    "receiving_xfp_pbp_3yr": "receiving_xfp_pbp_3yr",
    "rushing_xfp_pbp_3yr": "rushing_xfp_pbp_3yr",
    "passing_xfp_pbp_3yr": "passing_xfp_pbp_3yr",
    "red_zone_xfp_score_3yr": "red_zone_xfp_score_3yr",
    "goal_line_xfp_score_3yr": "goal_line_xfp_score_3yr",
    "high_value_target_xfp_score_3yr": "high_value_target_xfp_score_3yr",
    "high_value_rush_xfp_score_3yr": "high_value_rush_xfp_score_3yr",
    "receiving_xfp_share_pbp_3yr": "receiving_xfp_share_pbp_3yr",
    "rushing_xfp_share_pbp_3yr": "rushing_xfp_share_pbp_3yr",
    "opportunity_quality_score_3yr": "opportunity_quality_score_3yr",
    "receiving_first_down_exp_pbp_3yr": "receiving_first_down_exp_pbp_3yr",
    "rushing_first_down_exp_pbp_3yr": "rushing_first_down_exp_pbp_3yr",
    "passing_first_down_exp_pbp_3yr": "passing_first_down_exp_pbp_3yr",
    "high_value_first_down_opportunity_score_3yr": "high_value_first_down_opportunity_score_3yr",
    "receiving_chain_mover_score_3yr": "receiving_chain_mover_score_3yr",
    "rushing_chain_mover_score_3yr": "rushing_chain_mover_score_3yr",
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


def trend_formula_candidates(formula_set_id: str = "ranking_formula_set_v2_trend_2026_001") -> list[dict[str, Any]]:
    candidate_specs = [
        (
            "QB",
            "trend_balanced",
            "QB Trend Balanced",
            {
                "opportunity_slope_3yr": 0.25,
                "epa_slope_3yr": 0.25,
                "efficiency_slope_3yr": 0.20,
                "availability_rate_3yr": 0.15,
                "declining_3yr": 0.15,
            },
        ),
        (
            "QB",
            "trend_opportunity",
            "QB Trend Opportunity",
            {
                "opportunity_slope_3yr": 0.35,
                "usage_volume": 0.15,
                "rushing_attempts": 0.20,
                "availability_rate_3yr": 0.20,
                "improving_3yr": 0.15,
            },
        ),
        (
            "QB",
            "trend_efficiency",
            "QB Trend Efficiency",
            {
                "epa_slope_3yr": 0.35,
                "efficiency_slope_3yr": 0.25,
                "success_rate": 0.15,
                "team_epa_per_play": 0.15,
                "weekly_volatility_3yr": 0.10,
            },
        ),
        (
            "RB",
            "trend_balanced",
            "RB Trend Balanced",
            {
                "opportunity_slope_3yr": 0.30,
                "carry_share_slope_3yr": 0.20,
                "epa_slope_3yr": 0.15,
                "availability_rate_3yr": 0.20,
                "declining_3yr": 0.15,
            },
        ),
        (
            "RB",
            "trend_opportunity",
            "RB Trend Opportunity",
            {
                "carry_share_slope_3yr": 0.30,
                "targets": 0.15,
                "usage_volume": 0.20,
                "improving_3yr": 0.20,
                "availability_rate_3yr": 0.15,
            },
        ),
        (
            "RB",
            "trend_risk_adjusted",
            "RB Trend Risk Adjusted",
            {
                "opportunity_slope_3yr": 0.25,
                "efficiency_slope_3yr": 0.20,
                "weekly_volatility_3yr": 0.20,
                "availability_rate_3yr": 0.20,
                "declining_3yr": 0.15,
            },
        ),
        (
            "WR",
            "trend_balanced",
            "WR Trend Balanced",
            {
                "target_share_slope_3yr": 0.25,
                "receiving_usage_slope_3yr": 0.20,
                "wopr_slope_3yr": 0.20,
                "epa_slope_3yr": 0.20,
                "availability_rate_3yr": 0.15,
            },
        ),
        (
            "WR",
            "trend_breakout",
            "WR Trend Breakout",
            {
                "target_share_slope_3yr": 0.30,
                "wopr_slope_3yr": 0.25,
                "breakout_trajectory_3yr": 0.20,
                "improving_3yr": 0.15,
                "air_yards": 0.10,
            },
        ),
        (
            "WR",
            "trend_risk_adjusted",
            "WR Trend Risk Adjusted",
            {
                "target_share_slope_3yr": 0.25,
                "weekly_volatility_3yr": 0.20,
                "availability_rate_3yr": 0.20,
                "declining_3yr": 0.20,
                "efficiency_slope_3yr": 0.15,
            },
        ),
        (
            "TE",
            "trend_balanced",
            "TE Trend Balanced",
            {
                "target_share_slope_3yr": 0.25,
                "receiving_usage_slope_3yr": 0.20,
                "team_pass_rate": 0.20,
                "availability_rate_3yr": 0.20,
                "declining_3yr": 0.15,
            },
        ),
        (
            "TE",
            "trend_breakout",
            "TE Trend Breakout",
            {
                "target_share_slope_3yr": 0.30,
                "breakout_trajectory_3yr": 0.25,
                "wopr_slope_3yr": 0.20,
                "improving_3yr": 0.15,
                "team_pass_rate": 0.10,
            },
        ),
        (
            "TE",
            "trend_efficiency",
            "TE Trend Efficiency",
            {
                "epa_slope_3yr": 0.25,
                "efficiency_slope_3yr": 0.25,
                "receiving_usage_slope_3yr": 0.20,
                "weekly_volatility_3yr": 0.15,
                "availability_rate_3yr": 0.15,
            },
        ),
    ]
    return [
        build_candidate_row(
            {
                "version": "ranking_formula_v2_trend_2026_001",
                "position": position,
                "score_expression": "weighted_linear",
                "features": list(weights),
                "weights": dict(weights),
                "normalization": {"method": "position_percentile"},
                "source_flags": {"trend_features_available": True},
            },
            formula_name=name,
            candidate_id=f"ranking_formula_{position.lower()}_{style}_v2_trend_2026_001",
            formula_set_id=formula_set_id,
            target_name=_target_name_for_position(position),
            status="draft",
        )
        for position, style, name, weights in candidate_specs
    ]


def tournament_formula_candidates(formula_set_id: str = "ranking_formula_set_tournament_v0_2026_001") -> list[dict[str, Any]]:
    """Build the Phase 32.5 in-memory tournament registry.

    The current Pigskin baseline mirrors the deterministic candidate-score weights
    in materialize.py using the historical features available to this runner. The
    live depth-chart penalty is documented as unavailable, not zero-filled.
    """

    specs: list[tuple[str, str, str, str, dict[str, float]]] = []
    for position in POSITIONS:
        specs.extend(
            [
                (
                    position,
                    "current_pigskin_candidate_score_v1",
                    "Current Pigskin Candidate Score v1",
                    "current_pigskin_candidate_score_v1",
                    {
                        "analytical_grade_proxy": 0.55,
                        "opportunity_score_proxy": 0.15,
                        "efficiency_score_proxy": 0.10,
                        "role_stability_score": 0.10,
                        "profile_points_score": 0.10,
                    },
                ),
                (
                    position,
                    "equal_weight_normalized_blend_v0",
                    "Equal Weight Normalized Blend v0",
                    "equal_weight_normalized_blend_v0",
                    {
                        "recent_points_avg": 0.20,
                        "usage_volume": 0.20,
                        "epa_per_play": 0.20,
                        "availability_rate_3yr": 0.20,
                        "profile_points_score": 0.20,
                    },
                ),
                (
                    position,
                    "value_over_replacement_baseline_v0",
                    "Value Over Replacement Baseline v0",
                    "value_over_replacement_baseline_v0",
                    {
                        "profile_points_score": 0.45,
                        "recent_points_avg": 0.35,
                        "availability_rate_3yr": 0.20,
                    },
                ),
                (
                    position,
                    "scarcity_adjusted_draft_value_v0",
                    "Scarcity Adjusted Draft Value v0",
                    "scarcity_adjusted_draft_value_v0",
                    {
                        "usage_volume": 0.25,
                        "profile_points_score": 0.30,
                        "role_stability_score": 0.20,
                        "opportunity_slope_3yr": 0.15,
                        "availability_rate_3yr": 0.10,
                    },
                ),
                (
                    position,
                    "simple_projection_points_baseline_v0",
                    "Simple Projection Points Baseline v0",
                    "simple_projection_points_baseline_v0",
                    {"profile_points_score": 1.0},
                ),
            ]
        )

    specs.extend(_seeded_v0_tournament_specs())
    specs.extend(_v1_improved_tournament_specs())

    candidates = [
        _tournament_candidate(
            position=position,
            family=family,
            name=name,
            version=version,
            weights=weights,
            formula_set_id=formula_set_id,
        )
        for position, family, name, version, weights in specs
    ]
    candidates.extend(
        {
            **row,
            "formula_set_id": formula_set_id,
            "formula_version": "ranking_formula_v2_trend_2026_001",
            "notes": "Phase 32.5 tournament challenger. Trend-aware deterministic formula, not a champion.",
        }
        for row in trend_formula_candidates(formula_set_id=formula_set_id)
    )
    return candidates


def _seeded_v0_tournament_specs() -> list[tuple[str, str, str, str, dict[str, float]]]:
    return [
        ("QB", "seeded_v0_balanced", "QB Seeded v0 Balanced", "ranking_formula_v0_2026_001", {"recent_points_avg": 0.30, "passing_epa_per_play": 0.25, "passing_success_rate": 0.20, "cpoe": 0.10, "pigskin_context_score": 0.15}),
        ("QB", "seeded_v0_volume", "QB Seeded v0 Volume", "ranking_formula_v0_2026_001", {"recent_points_avg": 0.25, "dropbacks": 0.30, "rushing_attempts": 0.15, "usage_volume": 0.15, "pigskin_context_score": 0.15}),
        ("QB", "seeded_v0_efficiency", "QB Seeded v0 Efficiency", "ranking_formula_v0_2026_001", {"passing_epa_per_play": 0.35, "passing_success_rate": 0.25, "cpoe": 0.20, "team_epa_per_play": 0.10, "pigskin_context_score": 0.10}),
        ("RB", "seeded_v0_balanced", "RB Seeded v0 Balanced", "ranking_formula_v0_2026_001", {"recent_points_avg": 0.30, "usage_volume": 0.25, "rush_success_rate": 0.15, "receiving_usage": 0.15, "pigskin_context_score": 0.15}),
        ("RB", "seeded_v0_volume", "RB Seeded v0 Volume", "ranking_formula_v0_2026_001", {"carries": 0.30, "targets": 0.20, "goal_line_opportunities": 0.20, "usage_volume": 0.20, "pigskin_context_score": 0.10}),
        ("RB", "seeded_v0_efficiency", "RB Seeded v0 Efficiency", "ranking_formula_v0_2026_001", {"rush_success_rate": 0.30, "receiving_usage": 0.20, "epa_per_play": 0.20, "success_rate": 0.15, "pigskin_context_score": 0.15}),
        ("WR", "seeded_v0_balanced", "WR Seeded v0 Balanced", "ranking_formula_v0_2026_001", {"recent_points_avg": 0.30, "targets": 0.25, "air_yards": 0.15, "receiving_epa": 0.15, "pigskin_context_score": 0.15}),
        ("WR", "seeded_v0_volume", "WR Seeded v0 Volume", "ranking_formula_v0_2026_001", {"targets": 0.35, "air_yards": 0.25, "red_zone_targets": 0.15, "usage_volume": 0.15, "pigskin_context_score": 0.10}),
        ("WR", "seeded_v0_efficiency", "WR Seeded v0 Efficiency", "ranking_formula_v0_2026_001", {"receiving_epa": 0.30, "receiving_yards": 0.20, "epa_per_play": 0.20, "success_rate": 0.15, "pigskin_context_score": 0.15}),
        ("TE", "seeded_v0_balanced", "TE Seeded v0 Balanced", "ranking_formula_v0_2026_001", {"recent_points_avg": 0.30, "targets": 0.25, "receiving_yards": 0.15, "team_pass_rate": 0.15, "pigskin_context_score": 0.15}),
        ("TE", "seeded_v0_volume", "TE Seeded v0 Volume", "ranking_formula_v0_2026_001", {"targets": 0.35, "red_zone_targets": 0.20, "air_yards": 0.15, "usage_volume": 0.15, "pigskin_context_score": 0.15}),
        ("TE", "seeded_v0_efficiency", "TE Seeded v0 Efficiency", "ranking_formula_v0_2026_001", {"receiving_epa": 0.30, "receiving_yards": 0.20, "team_pass_rate": 0.15, "epa_per_play": 0.15, "pigskin_context_score": 0.20}),
    ]


def _v1_improved_tournament_specs() -> list[tuple[str, str, str, str, dict[str, float]]]:
    return [
        ("QB", "v1_improved_mapping", "QB v1 Improved Mapping", "ranking_formula_v1_improved_2026_001", {"recent_points_avg": 0.25, "passing_epa_per_play": 0.25, "passing_success_rate": 0.20, "usage_volume": 0.15, "availability_rate_3yr": 0.15}),
        ("RB", "v1_improved_mapping", "RB v1 Improved Mapping", "ranking_formula_v1_improved_2026_001", {"recent_points_avg": 0.25, "usage_volume": 0.25, "carry_share_slope_3yr": 0.20, "receiving_usage": 0.15, "availability_rate_3yr": 0.15}),
        ("WR", "v1_improved_mapping", "WR v1 Improved Mapping", "ranking_formula_v1_improved_2026_001", {"recent_points_avg": 0.25, "targets": 0.20, "wopr_slope_3yr": 0.20, "air_yards": 0.15, "availability_rate_3yr": 0.20}),
        ("TE", "v1_improved_mapping", "TE v1 Improved Mapping", "ranking_formula_v1_improved_2026_001", {"recent_points_avg": 0.25, "targets": 0.25, "team_pass_rate": 0.20, "target_share_slope_3yr": 0.15, "availability_rate_3yr": 0.15}),
    ]


def _tournament_candidate(
    *,
    position: str,
    family: str,
    name: str,
    version: str,
    weights: dict[str, float],
    formula_set_id: str,
) -> dict[str, Any]:
    candidate_id = f"ranking_formula_{position.lower()}_{family}_2026_001"
    row = build_candidate_row(
        {
            "version": version,
            "position": position,
            "score_expression": "weighted_linear",
            "features": list(weights),
            "weights": dict(weights),
            "normalization": {"method": "position_percentile"},
            "source_flags": {"historical_tournament": True},
        },
        formula_name=name,
        candidate_id=candidate_id,
        formula_set_id=formula_set_id,
        target_name=_target_name_for_position(position),
        status="draft",
    )
    row["notes"] = f"Phase 32.5 tournament family={family}. Backtest-only, not a champion."
    return row


def build_rolling_season_pairs(
    *,
    source_seasons: list[int] | tuple[int, ...],
    target_seasons: list[int] | tuple[int, ...],
    source_window_years: int = 3,
    min_source_season: int = 2014,
) -> list[dict[str, Any]]:
    normalized_source_window_years = _normalize_source_window_years(source_window_years)
    source_set = {int(season) for season in source_seasons}
    target_set = {int(season) for season in target_seasons}
    pairs: list[dict[str, Any]] = []
    for target_season in sorted(target_set):
        source_season = target_season - 1
        if source_season not in source_set:
            continue
        source_window_start = max(min_source_season, source_season - normalized_source_window_years + 1)
        source_window = [
            season
            for season in range(source_window_start, source_season + 1)
            if season in source_set and season < target_season
        ]
        if not source_window:
            continue
        pairs.append(
            {
                "source_season": source_season,
                "target_season": target_season,
                "source_window_start": min(source_window),
                "source_window_end": max(source_window),
                "source_window_years": len(source_window),
                "source_seasons": source_window,
            }
        )
    return pairs


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
    formula_set_id: str | None = None,
    status: str = "draft",
) -> list[dict[str, Any]]:
    normalized_position = _normalize_position(position) if position else None
    normalized_status = validate_candidate_status(status)
    normalized_candidate_ids = [str(candidate_id) for candidate_id in candidate_ids or []]
    for candidate_id in normalized_candidate_ids:
        _reject_executable_text(candidate_id)
    if formula_version is not None:
        _reject_executable_text(formula_version)
    if formula_set_id is not None:
        _reject_executable_text(formula_set_id)
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
  AND (@formula_set_id IS NULL OR formula_set_id = @formula_set_id)
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
            _scalar_param("formula_set_id", "STRING", formula_set_id),
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


def load_all_position_candidates_for_formula_set(
    *,
    client: Any,
    formula_set_id: str,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    position: str,
    status: str = "draft",
) -> list[dict[str, Any]]:
    load_ranking_formula_set(
        client=client,
        formula_set_id=formula_set_id,
        project_id=project_id,
        dataset_id=dataset_id,
        status=status,
    )
    candidates = load_ranking_formula_candidates(
        client=client,
        project_id=project_id,
        dataset_id=dataset_id,
        position=position,
        formula_set_id=formula_set_id,
        status=status,
    )
    if not candidates:
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
    COALESCE(truth.rolling_3_week_ppr, profile.total_fantasy_points, truth.fantasy_points_ppr, truth.fantasy_points) AS recent_points_avg,
    COALESCE(metrics.targets, truth.targets) AS targets,
    COALESCE(metrics.carries, truth.carries) AS carries,
    truth.receiving_yards AS receiving_yards,
    truth.receiving_epa AS receiving_epa,
    metrics.red_zone_targets AS red_zone_targets,
    metrics.success_rate AS success_rate,
    metrics.success_rate AS passing_success_rate,
    truth.pass_attempts AS dropbacks,
    truth.carries AS rushing_attempts,
    metrics.success_rate AS rush_success_rate,
    COALESCE(metrics.targets, truth.targets) AS receiving_usage,
    metrics.cpoe AS cpoe,
    metrics.opportunities AS usage_volume,
    metrics.epa_per_opportunity AS epa_per_play,
    SAFE_DIVIDE(truth.passing_epa, NULLIF(truth.pass_attempts, 0)) AS passing_epa_per_play,
    metrics.red_zone_touches AS red_zone_opportunities,
    metrics.inside_5_carries AS goal_line_opportunities,
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
    backtest_run_id: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    return {
        "backtest_run_id": backtest_run_id
        or f"ranking-backtest-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}",
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
        "notes": notes,
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
    candidates = load_all_position_candidates_for_formula_set(
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
        "feature_availability": build_feature_availability_report(candidates, feature_rows),
        "target_availability": build_target_availability_report(feature_rows),
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


def run_no_lookahead_backtest(
    *,
    client: Any,
    formula_set_id: str,
    source_season: int,
    target_season: int,
    target_week_start: int,
    target_week_end: int,
    scoring_profile_ids: list[str] | tuple[str, ...],
    positions: list[str] | tuple[str, ...],
    status: str = "draft",
    league_type_id: str = DEFAULT_LEAGUE_TYPE_ID,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT_ID,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    backtest_version: str = DEFAULT_BACKTEST_VERSION,
    source_window_years: int = 1,
    candidate_family: str = "seeded",
    dry_run: bool = True,
    write: bool = False,
    limit: int | None = None,
) -> dict[str, Any]:
    if target_season <= source_season:
        raise FormulaValidationError("target_season must be after source_season to avoid lookahead")
    if target_week_start > target_week_end:
        raise FormulaValidationError("target_week_start must be less than or equal to target_week_end")
    if write:
        require_write_authorization()
    if not dry_run and not write:
        raise ValueError("write=True is required for non-dry-run ranking formula backtests")

    normalized_positions = [_normalize_position(position) for position in positions]
    normalized_profiles = [_normalize_scoring_profile_id(profile) for profile in scoring_profile_ids]
    normalized_backtest_version = _normalize_backtest_version(backtest_version)
    normalized_source_window_years = _normalize_source_window_years(source_window_years)
    normalized_candidate_family = _normalize_candidate_family(candidate_family)
    validate_candidate_status(status)
    load_ranking_formula_set(
        client=client,
        formula_set_id=formula_set_id,
        project_id=project_id,
        dataset_id=dataset_id,
        status=status,
    )
    candidates = load_ranking_formula_candidates(
        client=client,
        project_id=project_id,
        dataset_id=dataset_id,
        formula_set_id=formula_set_id,
        status=status,
    )
    if normalized_candidate_family == "trend_v2":
        candidates = trend_formula_candidates(formula_set_id=formula_set_id)
    elif normalized_candidate_family == "tournament_v0":
        candidates = tournament_formula_candidates(formula_set_id=formula_set_id)
    candidates = [candidate for candidate in candidates if candidate["position"] in normalized_positions]
    if not candidates:
        raise FormulaValidationError("No matching seeded formula candidates found")
    _validate_candidate_coverage(
        candidates,
        normalized_positions,
        expected_count=None if normalized_candidate_family == "tournament_v0" else 3,
    )

    all_result_rows: list[dict[str, Any]] = []
    all_summary_rows: list[dict[str, Any]] = []
    run_rows: list[dict[str, Any]] = []
    feature_reports: dict[str, Any] = {}
    target_reports: dict[str, Any] = {}
    position_input_counts: dict[str, int] = {}

    for profile in normalized_profiles:
        run_row = build_backtest_run_row(
            candidate_count=len(candidates),
            formula_set_id=formula_set_id,
            formula_version=candidates[0]["formula_version"],
            season_start=source_season,
            season_end=target_season,
            week_start=target_week_start,
            week_end=target_week_end,
            scoring_profile_id=profile,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            target_name="position_default_top_n",
            input_tables=ALLOWED_INPUT_TABLES,
            dry_run=not write,
            status="planned" if not write else "complete",
            backtest_run_id=(
                f"ranking_backtest_{normalized_backtest_version}_{source_season}_to_{target_season}_{profile}"
            ),
            notes=(
                f"backtest_version={normalized_backtest_version}; "
                f"source_season={source_season}; source_window_years={normalized_source_window_years}; "
                f"target_season={target_season}; "
                f"target_weeks={target_week_start}-{target_week_end}; no_lookahead=true"
            ),
        )
        if write:
            run_row["completed_at"] = _now()
        run_rows.append(run_row)

        profile_results: list[dict[str, Any]] = []
        for position in normalized_positions:
            position_candidates = [candidate for candidate in candidates if candidate["position"] == position]
            feature_rows = load_no_lookahead_feature_rows(
                client=client,
                position=position,
                source_season=source_season,
                target_season=target_season,
                target_week_start=target_week_start,
                target_week_end=target_week_end,
                scoring_profile_id=profile,
                league_type_id=league_type_id,
                roster_format_id=roster_format_id,
                project_id=project_id,
                dataset_id=dataset_id,
                source_window_years=normalized_source_window_years,
                limit=limit,
            )
            target_name = _target_name_for_position(position)
            result_rows = build_result_rows_for_candidates(
                candidates=position_candidates,
                feature_rows=feature_rows,
                backtest_run_id=run_row["backtest_run_id"],
                formula_set_id=formula_set_id,
                scoring_profile_id=profile,
                league_type_id=league_type_id,
                roster_format_id=roster_format_id,
                target_name=target_name,
            )
            for candidate in position_candidates:
                candidate_results = [
                    row for row in result_rows if row["candidate_id"] == candidate["candidate_id"]
                ]
                all_summary_rows.append(
                    build_summary_from_results(
                        candidate_row=candidate,
                        result_rows=candidate_results,
                        backtest_run_id=run_row["backtest_run_id"],
                        scoring_profile_id=profile,
                        league_type_id=league_type_id,
                        roster_format_id=roster_format_id,
                        target_name=target_name,
                    )
                )
            profile_results.extend(result_rows)
            feature_reports[f"{profile}:{position}"] = build_feature_availability_report(
                position_candidates,
                feature_rows,
            )
            target_reports[f"{profile}:{position}"] = build_target_availability_report(feature_rows)
            position_input_counts[f"{profile}:{position}"] = len(feature_rows)

        all_result_rows.extend(profile_results)

    result = {
        "dry_run": not write,
        "write": write,
        "formula_set_id": formula_set_id,
        "backtest_version": normalized_backtest_version,
        "source_window_years": normalized_source_window_years,
        "candidate_family": normalized_candidate_family,
        "candidate_count": len(candidates),
        "scoring_profile_ids": normalized_profiles,
        "positions": normalized_positions,
        "source_season": source_season,
        "target_season": target_season,
        "target_week_start": target_week_start,
        "target_week_end": target_week_end,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "input_tables": list(ALLOWED_INPUT_TABLES),
        "blocked_metrics": sorted(BLOCKED_METRIC_FEATURES),
        "candidate_rows": candidates,
        "backtest_run_rows": run_rows,
        "result_rows": all_result_rows,
        "candidate_summary_rows": all_summary_rows,
        "result_shape_count": len(all_result_rows),
        "candidate_summary_count": len(all_summary_rows),
        "feature_availability": feature_reports,
        "target_availability": target_reports,
        "position_input_counts": position_input_counts,
        "champion_recommendations": recommend_champions(all_summary_rows, candidates),
    }
    if write:
        result["write_summary"] = save_executed_backtest(
            result,
            project_id=project_id,
            dataset_id=dataset_id,
            client=client,
        )
    return result


def load_no_lookahead_feature_rows(
    *,
    client: Any,
    position: str,
    source_season: int,
    target_season: int,
    target_week_start: int,
    target_week_end: int,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    source_window_years: int = 1,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    normalized_position = _normalize_position(position)
    if target_season <= source_season:
        raise FormulaValidationError("target_season must be after source_season to avoid lookahead")
    if target_week_start > target_week_end:
        raise FormulaValidationError("target_week_start must be less than or equal to target_week_end")
    normalized_source_window_years = _normalize_source_window_years(source_window_years)
    source_window_start = max(int(source_season) - normalized_source_window_years + 1, 2014)
    bounded_limit = None if limit is None or int(limit) <= 0 else min(int(limit), MAX_REAL_DATA_LIMIT)
    limit_sql = "\nLIMIT @limit" if bounded_limit else ""
    query_parameters = [
        _scalar_param("position", "STRING", normalized_position),
        _scalar_param("source_window_start", "INT64", int(source_window_start)),
        _scalar_param("source_season", "INT64", int(source_season)),
        _scalar_param("target_season", "INT64", int(target_season)),
        _scalar_param("target_week_start", "INT64", int(target_week_start)),
        _scalar_param("target_week_end", "INT64", int(target_week_end)),
        _scalar_param("scoring_profile_id", "STRING", scoring_profile_id),
        _scalar_param("league_type_id", "STRING", league_type_id),
        _scalar_param("roster_format_id", "STRING", roster_format_id),
    ]
    if bounded_limit:
        query_parameters.append(_scalar_param("limit", "INT64", bounded_limit))
    query = f"""
CREATE TEMP FUNCTION _slope(points ARRAY<STRUCT<season INT64, value FLOAT64>>)
RETURNS FLOAT64
LANGUAGE js AS '''
  const filtered = points
    .filter((point) => point.value !== null && Number.isFinite(Number(point.value)))
    .sort((left, right) => Number(left.season) - Number(right.season));
  if (filtered.length < 2) return null;
  const first = filtered[0];
  const last = filtered[filtered.length - 1];
  const seasonSpan = Number(last.season) - Number(first.season);
  if (!Number.isFinite(seasonSpan) || seasonSpan === 0) return null;
  return (Number(last.value) - Number(first.value)) / seasonSpan;
''';
WITH season_features AS (
    SELECT
        REGEXP_REPLACE(metrics.player_id_internal, r'^gsis:', '') AS player_key,
        metrics.player_id_internal,
        ANY_VALUE(COALESCE(metrics.player_name, truth.player_display_name, truth.player_name)) AS player_name,
        metrics.position,
        metrics.season,
        ANY_VALUE(COALESCE(metrics.team, truth.team)) AS source_team,
        AVG(source_profile.total_fantasy_points) AS points_per_game,
        SUM(source_profile.total_fantasy_points) AS total_points,
        AVG(COALESCE(source_profile.total_fantasy_points, truth.fantasy_points_ppr, truth.fantasy_points)) AS recent_points_avg,
        LEAST(100.0, GREATEST(0.0, AVG(COALESCE(source_profile.total_fantasy_points, truth.fantasy_points_ppr, truth.fantasy_points)) * 4.0)) AS profile_points_score,
        AVG(metrics.targets) AS targets,
        AVG(metrics.carries) AS carries,
        AVG(truth.receiving_yards) AS receiving_yards,
        AVG(truth.receiving_epa) AS receiving_epa,
        AVG(metrics.red_zone_targets) AS red_zone_targets,
        AVG(metrics.success_rate) AS success_rate,
        AVG(metrics.success_rate) AS passing_success_rate,
        AVG(truth.pass_attempts) AS dropbacks,
        AVG(metrics.carries) AS rushing_attempts,
        AVG(metrics.success_rate) AS rush_success_rate,
        AVG(metrics.targets) AS receiving_usage,
        AVG(metrics.target_share) AS target_share,
        AVG(metrics.carry_share) AS carry_share,
        AVG(metrics.wopr) AS wopr,
        AVG(metrics.cpoe) AS cpoe,
        AVG(metrics.opportunities) AS usage_volume,
        AVG(metrics.epa_per_opportunity) AS epa_per_play,
        LEAST(100.0, GREATEST(0.0, AVG(metrics.opportunities) * 4.0)) AS opportunity_score_proxy,
        LEAST(100.0, GREATEST(0.0, 50.0 + (AVG(metrics.epa_per_opportunity) * 25.0))) AS efficiency_score_proxy,
        AVG(SAFE_DIVIDE(truth.passing_epa, NULLIF(truth.pass_attempts, 0))) AS passing_epa_per_play,
        AVG(metrics.red_zone_touches) AS red_zone_opportunities,
        AVG(metrics.inside_5_carries) AS goal_line_opportunities,
        AVG(metrics.snap_share) AS snap_share_proxy,
        AVG(metrics.air_yards_share) AS air_yards,
        AVG(SAFE_DIVIDE(truth.team_pass_attempts, NULLIF(truth.team_pass_attempts + truth.team_carries, 0))) AS team_pass_rate,
        AVG(opportunity.qb_rushing_leverage_index) AS qb_rushing_leverage_index,
        AVG(CASE WHEN metrics.position = 'RB' THEN opportunity.high_value_opportunity_score ELSE NULL END) AS rb_high_value_opportunity_score,
        AVG(CASE
            WHEN metrics.position = 'WR' THEN opportunity.wr_dominance_score
            WHEN metrics.position = 'TE' THEN opportunity.te_receiving_role_dominance_score
            ELSE NULL
        END) AS receiving_role_dominance_score,
        LEAST(100.0, GREATEST(0.0, AVG(COALESCE(opportunity.red_zone_targets, 0) * 4.0 + COALESCE(opportunity.red_zone_carries, 0) * 4.0 + COALESCE(opportunity.red_zone_touches, 0) * 3.0))) AS red_zone_usage_score,
        LEAST(100.0, GREATEST(0.0, AVG(COALESCE(opportunity.inside_5_carries, 0) * 12.0 + COALESCE(opportunity.inside_10_carries, 0) * 6.0))) AS goal_line_usage_score,
        AVG(opportunity.team_environment_score) AS opportunity_team_environment_score,
        AVG(IF(opportunity.spike_week_flag, 1.0, 0.0)) AS spike_week_rate,
        AVG(IF(opportunity.bust_week_flag, 1.0, 0.0)) AS bust_week_rate,
        AVG(IF(opportunity.elite_week_flag, 1.0, 0.0)) AS elite_week_rate,
        SAFE_DIVIDE(COUNT(DISTINCT metrics.week), 17) AS availability_rate,
        STDDEV(metrics.opportunities) AS weekly_volatility,
        LEAST(100.0, GREATEST(0.0, SAFE_DIVIDE(COUNT(DISTINCT metrics.week), 17) * 100.0 - COALESCE(STDDEV(metrics.opportunities), 0.0) * 2.0)) AS role_stability_score,
        ANY_VALUE(metrics.source_freshness_json) AS metrics_source_freshness_json,
        ANY_VALUE(metrics.missing_data_flags) AS metrics_missing_flags,
        ANY_VALUE(opportunity.source_freshness_json) AS opportunity_source_freshness_json,
        ANY_VALUE(opportunity.missing_flags_json) AS opportunity_missing_flags
    FROM `{table_id(project_id, dataset_id, "player_week_advanced_metrics")}` metrics
    LEFT JOIN `{table_id(project_id, dataset_id, "analytics_player_weekly_truth")}` truth
      ON metrics.season = truth.season
     AND metrics.week = truth.week
     AND REGEXP_REPLACE(metrics.player_id_internal, r'^gsis:', '') = REGEXP_REPLACE(truth.player_id, r'^gsis:', '')
    LEFT JOIN `{table_id(project_id, dataset_id, "analytics_player_fantasy_points_by_profile")}` source_profile
      ON metrics.season = source_profile.season
     AND metrics.week = source_profile.week
     AND REGEXP_REPLACE(metrics.player_id_internal, r'^gsis:', '') = REGEXP_REPLACE(source_profile.player_id_internal, r'^gsis:', '')
     AND source_profile.scoring_profile_id = @scoring_profile_id
     AND COALESCE(source_profile.league_type_id, @league_type_id) = @league_type_id
     AND COALESCE(source_profile.roster_format_id, @roster_format_id) = @roster_format_id
    WHERE metrics.position = @position
      AND metrics.season BETWEEN @source_window_start AND @source_season
      AND metrics.season < @target_season
      AND metrics.scoring_profile_id = 'ppr'
      AND metrics.league_type_id = @league_type_id
      AND metrics.roster_format_id = @roster_format_id
    GROUP BY metrics.player_id_internal, metrics.position, metrics.season
),
source_features AS (
    SELECT
        player_key,
        ANY_VALUE(player_id_internal) AS player_id_internal,
        ANY_VALUE(player_name) AS player_name,
        position,
        ANY_VALUE(source_team HAVING MAX season) AS source_team,
        AVG(recent_points_avg) AS recent_points_avg,
        AVG(profile_points_score) AS profile_points_score,
        AVG(targets) AS targets,
        AVG(carries) AS carries,
        AVG(receiving_yards) AS receiving_yards,
        AVG(receiving_epa) AS receiving_epa,
        AVG(red_zone_targets) AS red_zone_targets,
        AVG(success_rate) AS success_rate,
        AVG(passing_success_rate) AS passing_success_rate,
        AVG(dropbacks) AS dropbacks,
        AVG(rushing_attempts) AS rushing_attempts,
        AVG(rush_success_rate) AS rush_success_rate,
        AVG(receiving_usage) AS receiving_usage,
        AVG(cpoe) AS cpoe,
        AVG(usage_volume) AS usage_volume,
        AVG(epa_per_play) AS epa_per_play,
        AVG(opportunity_score_proxy) AS opportunity_score_proxy,
        AVG(efficiency_score_proxy) AS efficiency_score_proxy,
        AVG((opportunity_score_proxy + efficiency_score_proxy) / 2.0) AS analytical_grade_proxy,
        AVG(passing_epa_per_play) AS passing_epa_per_play,
        AVG(red_zone_opportunities) AS red_zone_opportunities,
        AVG(goal_line_opportunities) AS goal_line_opportunities,
        AVG(snap_share_proxy) AS snap_share_proxy,
        AVG(air_yards) AS air_yards,
        AVG(team_pass_rate) AS team_pass_rate,
        AVG(qb_rushing_leverage_index) AS qb_rushing_leverage_index,
        AVG(rb_high_value_opportunity_score) AS rb_high_value_opportunity_score,
        AVG(receiving_role_dominance_score) AS receiving_role_dominance_score,
        AVG(red_zone_usage_score) AS red_zone_usage_score,
        AVG(goal_line_usage_score) AS goal_line_usage_score,
        AVG(opportunity_team_environment_score) AS opportunity_team_environment_score,
        AVG(spike_week_rate) AS spike_week_rate_3yr,
        AVG(bust_week_rate) AS bust_week_rate_3yr,
        AVG(elite_week_rate) AS elite_week_rate_3yr,
        _slope(ARRAY_AGG(STRUCT(season, points_per_game AS value) ORDER BY season)) AS points_per_game_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, total_points AS value) ORDER BY season)) AS total_points_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, usage_volume AS value) ORDER BY season)) AS opportunity_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, target_share AS value) ORDER BY season)) AS target_share_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, carry_share AS value) ORDER BY season)) AS carry_share_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, receiving_usage AS value) ORDER BY season)) AS receiving_usage_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, wopr AS value) ORDER BY season)) AS wopr_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, epa_per_play AS value) ORDER BY season)) AS epa_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, success_rate AS value) ORDER BY season)) AS efficiency_slope_3yr,
        AVG(availability_rate) AS availability_rate_3yr,
        AVG(weekly_volatility) AS weekly_volatility_3yr,
        AVG(role_stability_score) AS role_stability_score,
        IF(_slope(ARRAY_AGG(STRUCT(season, usage_volume AS value) ORDER BY season)) > 0
           AND _slope(ARRAY_AGG(STRUCT(season, epa_per_play AS value) ORDER BY season)) > 0, 1.0, 0.0) AS improving_3yr,
        IF(_slope(ARRAY_AGG(STRUCT(season, usage_volume AS value) ORDER BY season)) < 0
           AND _slope(ARRAY_AGG(STRUCT(season, epa_per_play AS value) ORDER BY season)) < 0, 1.0, 0.0) AS declining_3yr,
        IF(_slope(ARRAY_AGG(STRUCT(season, target_share AS value) ORDER BY season)) > 0
           OR _slope(ARRAY_AGG(STRUCT(season, carry_share AS value) ORDER BY season)) > 0, 1.0, 0.0) AS breakout_trajectory_3yr,
        ANY_VALUE(metrics_source_freshness_json HAVING MAX season) AS metrics_source_freshness_json,
        ANY_VALUE(metrics_missing_flags HAVING MAX season) AS metrics_missing_flags,
        ANY_VALUE(opportunity_source_freshness_json HAVING MAX season) AS opportunity_source_freshness_json,
        ANY_VALUE(opportunity_missing_flags HAVING MAX season) AS opportunity_missing_flags
    FROM season_features
    GROUP BY player_key, position
),
packet_context AS (
    SELECT
        REGEXP_REPLACE(player_id_internal, r'^gsis:', '') AS player_key,
        position,
        AVG(SAFE_CAST(JSON_VALUE(team_context_json, '$.team_epa_per_play') AS FLOAT64)) AS packet_team_epa_per_play,
        AVG(SAFE_CAST(JSON_VALUE(team_context_json, '$.neutral_pass_rate') AS FLOAT64)) AS packet_team_pass_rate,
        ANY_VALUE(source_freshness_json) AS packet_source_freshness_json
    FROM `{table_id(project_id, dataset_id, "pigskin_player_context_packet_current")}`
    WHERE position = @position
      AND as_of_season = @source_season
      AND scoring_profile_id = 'ppr'
      AND COALESCE(league_type_id, @league_type_id) = @league_type_id
      AND COALESCE(roster_format_id, @roster_format_id) = @roster_format_id
    GROUP BY player_key, position
),
target_points AS (
    SELECT
        target.season,
        target.week,
        REGEXP_REPLACE(target.player_id_internal, r'^gsis:', '') AS player_key,
        REGEXP_REPLACE(target.player_id_internal, r'^gsis:', '') AS player_id_internal,
        target.player_display_name AS player_name,
        target.position,
        target.team,
        target.scoring_profile_id,
        COALESCE(target.league_type_id, @league_type_id) AS league_type_id,
        COALESCE(target.roster_format_id, @roster_format_id) AS roster_format_id,
        target.total_fantasy_points AS actual_points
    FROM `{table_id(project_id, dataset_id, "analytics_player_fantasy_points_by_profile")}` target
    WHERE target.position = @position
      AND target.season = @target_season
      AND target.week BETWEEN @target_week_start AND @target_week_end
      AND target.scoring_profile_id = @scoring_profile_id
      AND COALESCE(target.league_type_id, @league_type_id) = @league_type_id
      AND COALESCE(target.roster_format_id, @roster_format_id) = @roster_format_id
      AND target.player_id_internal IS NOT NULL
)
SELECT
    target.season,
    target.week,
    target.player_id_internal,
    COALESCE(target.player_name, source.player_name) AS player_name,
    target.position,
    COALESCE(target.team, source.source_team) AS team,
    target.scoring_profile_id,
    target.league_type_id,
    target.roster_format_id,
    target.actual_points,
    source.recent_points_avg,
    source.profile_points_score,
    source.targets,
    source.carries,
    source.receiving_yards,
    source.receiving_epa,
    source.red_zone_targets,
    source.success_rate,
    source.passing_success_rate,
    source.dropbacks,
    source.rushing_attempts,
    source.rush_success_rate,
    source.receiving_usage,
    source.cpoe,
    source.usage_volume,
    source.epa_per_play,
    source.opportunity_score_proxy,
    source.efficiency_score_proxy,
    source.analytical_grade_proxy,
    source.passing_epa_per_play,
    packet.packet_team_epa_per_play AS team_epa_per_play,
    source.red_zone_opportunities,
    source.goal_line_opportunities,
    source.snap_share_proxy,
    source.air_yards,
    COALESCE(source.team_pass_rate, packet.packet_team_pass_rate) AS team_pass_rate,
    source.metrics_source_freshness_json,
    source.metrics_missing_flags,
    packet.packet_source_freshness_json,
    source.points_per_game_slope_3yr,
    source.total_points_slope_3yr,
    source.opportunity_slope_3yr,
    source.target_share_slope_3yr,
    source.carry_share_slope_3yr,
    source.receiving_usage_slope_3yr,
    source.wopr_slope_3yr,
    source.epa_slope_3yr,
    source.efficiency_slope_3yr,
    source.availability_rate_3yr,
    source.weekly_volatility_3yr,
    source.role_stability_score,
    source.improving_3yr,
    source.declining_3yr,
    source.breakout_trajectory_3yr
FROM target_points target
JOIN source_features source
  ON target.player_key = source.player_key
LEFT JOIN packet_context packet
  ON target.player_key = packet.player_key
ORDER BY target.week, target.player_id_internal
{limit_sql}
""".strip()
    return _query_records(client, query, query_parameters)


def build_feature_mart_delete_sql(*, project_id: str, dataset_id: str) -> str:
    return f"""
DELETE FROM `{table_id(project_id, dataset_id, "ranking_backtest_feature_mart")}`
WHERE target_season = @target_season
  AND scoring_profile_id IN UNNEST(@scoring_profile_ids)
  AND position IN UNNEST(@positions)
  AND league_type_id = @league_type_id
  AND roster_format_id = @roster_format_id
""".strip()


def build_opportunity_metrics_delete_sql(*, project_id: str, dataset_id: str) -> str:
    return f"""
DELETE FROM `{table_id(project_id, dataset_id, "player_week_opportunity_metrics")}`
WHERE season BETWEEN @season_start AND @season_end
""".strip()


def build_opportunity_metrics_insert_sql(*, project_id: str, dataset_id: str) -> str:
    opportunity_table = table_id(project_id, dataset_id, "player_week_opportunity_metrics")
    metrics_table = table_id(project_id, dataset_id, "player_week_advanced_metrics")
    stats_table = table_id(project_id, dataset_id, "stg_player_week_stats")
    team_table = table_id(project_id, dataset_id, "stg_team_week_stats")
    points_table = table_id(project_id, dataset_id, "analytics_player_fantasy_points_by_profile")
    participation_table = table_id(project_id, dataset_id, "stg_participation_context")
    return f"""
INSERT INTO `{opportunity_table}` (
    opportunity_metric_version,
    opportunity_run_id,
    season,
    week,
    player_id_internal,
    player_name,
    team,
    opponent_team,
    position,
    targets,
    carries,
    receptions,
    air_yards,
    rushing_yards,
    receiving_yards,
    passing_yards,
    pass_attempts,
    rush_attempts,
    team_plays,
    team_pass_attempts,
    team_rush_attempts,
    team_targets,
    team_air_yards,
    team_epa_per_play,
    team_neutral_pass_rate,
    target_share,
    carry_share,
    opportunity_share,
    air_yards_share,
    weighted_opportunity,
    wopr,
    red_zone_targets,
    red_zone_carries,
    red_zone_touches,
    inside_10_carries,
    inside_5_carries,
    goal_line_carry_share,
    red_zone_opportunity_share,
    high_value_touches,
    high_value_opportunity_score,
    receiving_equity_score,
    qb_rushing_leverage_index,
    wr_dominance_score,
    te_receiving_role_dominance_score,
    team_environment_score,
    spike_week_flag,
    bust_week_flag,
    elite_week_flag,
    source_freshness_json,
    missing_flags_json,
    provenance_json,
    created_at
)
WITH participation AS (
    SELECT
        season,
        week,
        REGEXP_REPLACE(player_id_internal, r'^gsis:', '') AS player_key,
        LOGICAL_OR(COALESCE(has_true_route_source, FALSE)) AS has_true_route_source
    FROM `{participation_table}`
    WHERE season BETWEEN @season_start AND @season_end
    GROUP BY 1, 2, 3
),
base AS (
    SELECT
        metrics.*,
        team.plays AS team_plays,
        team.pass_attempts AS team_pass_attempts,
        team.rush_attempts AS team_rush_attempts,
        team.team_targets,
        team.team_air_yards,
        team.epa_per_play AS team_epa_per_play,
        team.neutral_pass_rate AS team_neutral_pass_rate,
        team.red_zone_pass_rate,
        team.red_zone_rush_rate,
        stats.receptions AS source_receptions,
        stats.air_yards AS source_air_yards,
        stats.rushing_yards AS source_rushing_yards,
        stats.receiving_yards AS source_receiving_yards,
        stats.passing_yards AS source_passing_yards,
        profile_points.total_fantasy_points AS ppr_points,
        COALESCE(participation.has_true_route_source, FALSE) AS has_true_route_source
    FROM `{metrics_table}` metrics
    LEFT JOIN `{stats_table}` stats
      ON metrics.season = stats.season
     AND metrics.week = stats.week
     AND REGEXP_REPLACE(metrics.player_id_internal, r'^gsis:', '') = REGEXP_REPLACE(stats.player_id_internal, r'^gsis:', '')
    LEFT JOIN `{team_table}` team
      ON metrics.season = team.season
     AND metrics.week = team.week
     AND metrics.team = team.team
    LEFT JOIN `{points_table}` profile_points
      ON metrics.season = profile_points.season
     AND metrics.week = profile_points.week
     AND REGEXP_REPLACE(metrics.player_id_internal, r'^gsis:', '') = REGEXP_REPLACE(profile_points.player_id_internal, r'^gsis:', '')
     AND profile_points.scoring_profile_id = 'ppr'
     AND COALESCE(profile_points.league_type_id, 'redraft') = 'redraft'
     AND COALESCE(profile_points.roster_format_id, 'one_qb') = 'one_qb'
    LEFT JOIN participation
      ON metrics.season = participation.season
     AND metrics.week = participation.week
     AND REGEXP_REPLACE(metrics.player_id_internal, r'^gsis:', '') = participation.player_key
    WHERE metrics.season BETWEEN @season_start AND @season_end
      AND metrics.scoring_profile_id = 'ppr'
      AND metrics.league_type_id = 'redraft'
      AND metrics.roster_format_id = 'one_qb'
      AND metrics.player_id_internal IS NOT NULL
      AND metrics.position IN ('QB', 'RB', 'WR', 'TE')
),
scored AS (
    SELECT
        *,
        SAFE_DIVIDE(inside_5_carries, NULLIF(red_zone_carries, 0)) AS goal_line_carry_share_calc,
        SAFE_DIVIDE(
            red_zone_touches,
            NULLIF((COALESCE(red_zone_pass_rate, 0) * COALESCE(team_pass_attempts, 0)) + (COALESCE(red_zone_rush_rate, 0) * COALESCE(team_rush_attempts, 0)), 0)
        ) AS red_zone_opportunity_share_calc,
        LEAST(100.0, GREATEST(0.0,
            COALESCE(red_zone_touches, 0) * 6.0
            + COALESCE(high_value_touches, 0) * 8.0
            + COALESCE(target_share, 0) * 35.0
            + COALESCE(opportunity_share, 0) * 35.0
        )) AS high_value_opportunity_score_calc,
        LEAST(100.0, GREATEST(0.0,
            COALESCE(target_share, 0) * 45.0
            + COALESCE(air_yards_share, 0) * 30.0
            + COALESCE(wopr, 0) * 25.0
        )) AS receiving_equity_score_calc,
        CASE
          WHEN position = 'QB' THEN LEAST(100.0, GREATEST(0.0,
              COALESCE(carry_share, 0) * 40.0
              + COALESCE(carries, 0) * 2.0
              + COALESCE(red_zone_carries, 0) * 7.0
              + COALESCE(inside_5_carries, 0) * 12.0
          ))
          ELSE NULL
        END AS qb_rushing_leverage_index_calc,
        CASE
          WHEN position = 'WR' THEN LEAST(100.0, GREATEST(0.0,
              COALESCE(target_share, 0) * 45.0
              + COALESCE(air_yards_share, 0) * 35.0
              + COALESCE(wopr, 0) * 20.0
              + COALESCE(red_zone_targets, 0) * 3.0
          ))
          ELSE NULL
        END AS wr_dominance_score_calc,
        CASE
          WHEN position = 'TE' THEN LEAST(100.0, GREATEST(0.0,
              COALESCE(target_share, 0) * 45.0
              + COALESCE(air_yards_share, 0) * 20.0
              + COALESCE(wopr, 0) * 25.0
              + COALESCE(red_zone_targets, 0) * 4.0
              + COALESCE(snap_share, 0) * 10.0
          ))
          ELSE NULL
        END AS te_receiving_role_dominance_score_calc,
        LEAST(100.0, GREATEST(0.0,
            50.0
            + COALESCE(team_epa_per_play, 0) * 40.0
            + COALESCE(team_neutral_pass_rate, 0) * 25.0
            + LEAST(COALESCE(team_plays, 0), 75) / 75.0 * 25.0
        )) AS team_environment_score_calc
    FROM base
)
SELECT
    @opportunity_metric_version AS opportunity_metric_version,
    @opportunity_run_id AS opportunity_run_id,
    season,
    week,
    REGEXP_REPLACE(player_id_internal, r'^gsis:', '') AS player_id_internal,
    player_name,
    team,
    opponent_team,
    position,
    targets,
    carries,
    source_receptions AS receptions,
    source_air_yards AS air_yards,
    source_rushing_yards AS rushing_yards,
    source_receiving_yards AS receiving_yards,
    source_passing_yards AS passing_yards,
    CAST(NULL AS FLOAT64) AS pass_attempts,
    CAST(NULL AS FLOAT64) AS rush_attempts,
    team_plays,
    team_pass_attempts,
    team_rush_attempts,
    team_targets,
    team_air_yards,
    team_epa_per_play,
    team_neutral_pass_rate,
    target_share,
    carry_share,
    opportunity_share,
    air_yards_share,
    weighted_opportunity,
    wopr,
    red_zone_targets,
    red_zone_carries,
    red_zone_touches,
    inside_10_carries,
    inside_5_carries,
    goal_line_carry_share_calc AS goal_line_carry_share,
    red_zone_opportunity_share_calc AS red_zone_opportunity_share,
    high_value_touches,
    high_value_opportunity_score_calc AS high_value_opportunity_score,
    receiving_equity_score_calc AS receiving_equity_score,
    qb_rushing_leverage_index_calc AS qb_rushing_leverage_index,
    wr_dominance_score_calc AS wr_dominance_score,
    te_receiving_role_dominance_score_calc AS te_receiving_role_dominance_score,
    team_environment_score_calc AS team_environment_score,
    CASE position
      WHEN 'QB' THEN ppr_points >= 25
      WHEN 'RB' THEN ppr_points >= 20
      WHEN 'WR' THEN ppr_points >= 20
      WHEN 'TE' THEN ppr_points >= 16
      ELSE NULL
    END AS spike_week_flag,
    CASE position
      WHEN 'QB' THEN ppr_points <= 10
      WHEN 'RB' THEN ppr_points <= 7
      WHEN 'WR' THEN ppr_points <= 7
      WHEN 'TE' THEN ppr_points <= 5
      ELSE NULL
    END AS bust_week_flag,
    CASE position
      WHEN 'QB' THEN ppr_points >= 30
      WHEN 'RB' THEN ppr_points >= 25
      WHEN 'WR' THEN ppr_points >= 25
      WHEN 'TE' THEN ppr_points >= 20
      ELSE NULL
    END AS elite_week_flag,
    TO_JSON_STRING(STRUCT(
        'player_week_advanced_metrics' AS opportunity_source_table,
        'stg_player_week_stats' AS player_week_source_table,
        'stg_team_week_stats' AS team_source_table,
        'analytics_player_fantasy_points_by_profile' AS spike_bust_source_table,
        CURRENT_TIMESTAMP() AS refreshed_at
    )) AS source_freshness_json,
    TO_JSON_STRING(STRUCT(
        target_share IS NULL AS target_share_missing,
        air_yards_share IS NULL AS air_yards_share_missing,
        carry_share IS NULL AS carry_share_missing,
        red_zone_touches IS NULL AS red_zone_touches_missing,
        inside_5_carries IS NULL AS inside_5_carries_missing,
        team_epa_per_play IS NULL AS team_environment_missing,
        ppr_points IS NULL AS fantasy_points_missing,
        NOT has_true_route_source AS route_share_unavailable,
        TRUE AS first_read_share_unavailable,
        TRUE AS yprr_unavailable,
        TRUE AS end_zone_target_unavailable
    )) AS missing_flags_json,
    TO_JSON_STRING(STRUCT(
        'ranking opportunity metrics v0' AS builder,
        @season_start AS season_start,
        @season_end AS season_end,
        'ppr/redraft/one_qb source profile only' AS scoring_source_policy,
        'blocked metrics remain missing, never fabricated' AS blocked_metric_policy
    )) AS provenance_json,
    CURRENT_TIMESTAMP() AS created_at
FROM scored
""".strip()


def populate_player_week_opportunity_metrics(
    *,
    client: Any,
    season_start: int,
    season_end: int,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    opportunity_metric_version: str = "opportunity_metrics_v0",
) -> dict[str, Any]:
    if int(season_start) > int(season_end):
        raise ValueError("season_start must be less than or equal to season_end")
    opportunity_run_id = f"opportunity_metrics_{int(season_start)}_{int(season_end)}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    params = [
        _scalar_param("season_start", "INT64", int(season_start)),
        _scalar_param("season_end", "INT64", int(season_end)),
        _scalar_param("opportunity_metric_version", "STRING", opportunity_metric_version),
        _scalar_param("opportunity_run_id", "STRING", opportunity_run_id),
    ]
    client.query(
        build_opportunity_metrics_delete_sql(project_id=project_id, dataset_id=dataset_id),
        job_config=_query_job_config(params),
    ).result()
    client.query(
        build_opportunity_metrics_insert_sql(project_id=project_id, dataset_id=dataset_id),
        job_config=_query_job_config(params),
    ).result()
    count_sql = f"""
SELECT
    COUNT(*) AS row_count,
    COUNT(DISTINCT season) AS season_count,
    COUNT(DISTINCT CONCAT(CAST(season AS STRING), '-', CAST(week AS STRING))) AS season_week_count
FROM `{table_id(project_id, dataset_id, "player_week_opportunity_metrics")}`
WHERE season BETWEEN @season_start AND @season_end
""".strip()
    count_row = list(client.query(count_sql, job_config=_query_job_config(params)).result())[0]
    return {
        "target_table": table_id(project_id, dataset_id, "player_week_opportunity_metrics"),
        "season_start": int(season_start),
        "season_end": int(season_end),
        "opportunity_metric_version": opportunity_metric_version,
        "opportunity_run_id": opportunity_run_id,
        "row_count": int(count_row["row_count"]),
        "season_count": int(count_row["season_count"]),
        "season_week_count": int(count_row["season_week_count"]),
    }


def build_feature_mart_insert_sql(*, project_id: str, dataset_id: str) -> str:
    mart_table = table_id(project_id, dataset_id, "ranking_backtest_feature_mart")
    metrics_table = table_id(project_id, dataset_id, "player_week_advanced_metrics")
    truth_table = table_id(project_id, dataset_id, "analytics_player_weekly_truth")
    points_table = table_id(project_id, dataset_id, "analytics_player_fantasy_points_by_profile")
    packet_table = table_id(project_id, dataset_id, "pigskin_player_context_packet_current")
    opportunity_table = table_id(project_id, dataset_id, "player_week_opportunity_metrics")
    ideal_table = table_id(project_id, dataset_id, "player_week_ideal_opportunity_metrics")
    pbp_ideal_table = table_id(project_id, dataset_id, "player_week_pbp_opportunity_metrics")
    role_context_table = table_id(project_id, dataset_id, "player_week_role_context_metrics")
    return f"""
CREATE TEMP FUNCTION _slope(points ARRAY<STRUCT<season INT64, value FLOAT64>>)
RETURNS FLOAT64
LANGUAGE js AS '''
  const filtered = points
    .filter((point) => point.value !== null && Number.isFinite(Number(point.value)))
    .sort((left, right) => Number(left.season) - Number(right.season));
  if (filtered.length < 2) return null;
  const first = filtered[0];
  const last = filtered[filtered.length - 1];
  const seasonSpan = Number(last.season) - Number(first.season);
  if (!Number.isFinite(seasonSpan) || seasonSpan === 0) return null;
  return (Number(last.value) - Number(first.value)) / seasonSpan;
''';

INSERT INTO `{mart_table}` (
    source_window_start_season,
    source_window_end_season,
    target_season,
    target_week,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    position,
    player_id_internal,
    player_name,
    team,
    source_team,
    recent_points_avg,
    profile_points_score,
    opportunity_score_proxy,
    efficiency_score_proxy,
    analytical_grade_proxy,
    role_stability_score,
    targets,
    carries,
    receiving_yards,
    receiving_epa,
    red_zone_targets,
    red_zone_carries,
    outside_red_zone_targets,
    outside_red_zone_carries,
    gemini31_rb_weighted_opportunity_ppr,
    success_rate,
    passing_success_rate,
    dropbacks,
    rushing_attempts,
    rush_success_rate,
    receiving_usage,
    cpoe,
    usage_volume,
    epa_per_play,
    passing_epa_per_play,
    team_epa_per_play,
    red_zone_opportunities,
    goal_line_opportunities,
    snap_share_proxy,
    air_yards,
    team_pass_rate,
    qb_rushing_leverage_index,
    rb_high_value_opportunity_score,
    receiving_role_dominance_score,
    red_zone_usage_score,
    goal_line_usage_score,
    team_environment_score,
    spike_week_rate_3yr,
    bust_week_rate_3yr,
    elite_week_rate_3yr,
    points_per_game_slope_3yr,
    total_points_slope_3yr,
    opportunity_slope_3yr,
    target_share_slope_3yr,
    carry_share_slope_3yr,
    receiving_usage_slope_3yr,
    wopr_slope_3yr,
    epa_slope_3yr,
    efficiency_slope_3yr,
    availability_rate_3yr,
    weekly_volatility_3yr,
    improving_3yr,
    declining_3yr,
    breakout_trajectory_3yr,
    xfp_score_3yr,
    xfp_share_3yr,
    fantasy_points_over_expectation_3yr,
    offensive_snap_share_3yr,
    snap_role_stability_3yr,
    receiving_role_dominance_xfp_3yr,
    high_value_xfp_score_3yr,
    qb_ngs_efficiency_score_3yr,
    injury_risk_score_3yr,
    injury_status_score_3yr,
    injury_burden_score_3yr,
    missed_time_risk_score_3yr,
    availability_score_3yr,
    injury_context_missing_flags_json,
    depth_chart_role_score_3yr,
    receiving_xfp_pbp_3yr,
    rushing_xfp_pbp_3yr,
    passing_xfp_pbp_3yr,
    red_zone_xfp_score_3yr,
    goal_line_xfp_score_3yr,
    high_value_target_xfp_score_3yr,
    high_value_rush_xfp_score_3yr,
    receiving_xfp_share_pbp_3yr,
    rushing_xfp_share_pbp_3yr,
    opportunity_quality_score_3yr,
    receiving_first_down_exp_pbp_3yr,
    rushing_first_down_exp_pbp_3yr,
    passing_first_down_exp_pbp_3yr,
    high_value_first_down_opportunity_score_3yr,
    receiving_chain_mover_score_3yr,
    rushing_chain_mover_score_3yr,
    pbp_xfp_missing_flags_json,
    target_fantasy_points,
    actual_position_rank,
    actual_overall_rank,
    replacement_points,
    value_over_replacement,
    top_24_overall,
    top_50_overall,
    top_100_overall,
    actual_pick_band,
    predictor_missing_flags_json,
    outcome_missing_flags_json,
    source_freshness_json,
    provenance_json,
    created_at
)
WITH profiles AS (
    SELECT scoring_profile_id FROM UNNEST(@scoring_profile_ids) AS scoring_profile_id
),
positions AS (
    SELECT position FROM UNNEST(@positions) AS position
),
season_features AS (
    SELECT
        profiles.scoring_profile_id,
        REGEXP_REPLACE(metrics.player_id_internal, r'^gsis:', '') AS player_key,
        metrics.player_id_internal,
        ANY_VALUE(COALESCE(metrics.player_name, truth.player_display_name, truth.player_name)) AS player_name,
        metrics.position,
        metrics.season,
        ANY_VALUE(COALESCE(metrics.team, truth.team)) AS source_team,
        AVG(source_profile.total_fantasy_points) AS points_per_game,
        SUM(source_profile.total_fantasy_points) AS total_points,
        AVG(COALESCE(source_profile.total_fantasy_points, truth.fantasy_points_ppr, truth.fantasy_points)) AS recent_points_avg,
        LEAST(100.0, GREATEST(0.0, AVG(COALESCE(source_profile.total_fantasy_points, truth.fantasy_points_ppr, truth.fantasy_points)) * 4.0)) AS profile_points_score,
        AVG(metrics.targets) AS targets,
        AVG(metrics.carries) AS carries,
        AVG(truth.receiving_yards) AS receiving_yards,
        AVG(truth.receiving_epa) AS receiving_epa,
        AVG(metrics.red_zone_targets) AS red_zone_targets,
        AVG(opportunity.red_zone_carries) AS red_zone_carries,
        AVG(GREATEST(COALESCE(metrics.targets, 0.0) - COALESCE(metrics.red_zone_targets, 0.0), 0.0)) AS outside_red_zone_targets,
        AVG(GREATEST(COALESCE(metrics.carries, 0.0) - COALESCE(opportunity.red_zone_carries, 0.0), 0.0)) AS outside_red_zone_carries,
        AVG(
            0.47 * GREATEST(COALESCE(metrics.carries, 0.0) - COALESCE(opportunity.red_zone_carries, 0.0), 0.0)
            + 1.28 * COALESCE(opportunity.red_zone_carries, 0.0)
            + 1.54 * GREATEST(COALESCE(metrics.targets, 0.0) - COALESCE(metrics.red_zone_targets, 0.0), 0.0)
            + 2.39 * COALESCE(metrics.red_zone_targets, 0.0)
        ) AS gemini31_rb_weighted_opportunity_ppr,
        AVG(metrics.success_rate) AS success_rate,
        AVG(metrics.success_rate) AS passing_success_rate,
        AVG(truth.pass_attempts) AS dropbacks,
        AVG(metrics.carries) AS rushing_attempts,
        AVG(metrics.success_rate) AS rush_success_rate,
        AVG(metrics.targets) AS receiving_usage,
        AVG(metrics.target_share) AS target_share,
        AVG(metrics.carry_share) AS carry_share,
        AVG(metrics.wopr) AS wopr,
        AVG(metrics.cpoe) AS cpoe,
        AVG(metrics.opportunities) AS usage_volume,
        AVG(metrics.epa_per_opportunity) AS epa_per_play,
        LEAST(100.0, GREATEST(0.0, AVG(metrics.opportunities) * 4.0)) AS opportunity_score_proxy,
        LEAST(100.0, GREATEST(0.0, 50.0 + (AVG(metrics.epa_per_opportunity) * 25.0))) AS efficiency_score_proxy,
        AVG(SAFE_DIVIDE(truth.passing_epa, NULLIF(truth.pass_attempts, 0))) AS passing_epa_per_play,
        AVG(metrics.red_zone_touches) AS red_zone_opportunities,
        AVG(metrics.inside_5_carries) AS goal_line_opportunities,
        AVG(metrics.snap_share) AS snap_share_proxy,
        AVG(metrics.air_yards_share) AS air_yards,
        AVG(SAFE_DIVIDE(truth.team_pass_attempts, NULLIF(truth.team_pass_attempts + truth.team_carries, 0))) AS team_pass_rate,
        AVG(opportunity.qb_rushing_leverage_index) AS qb_rushing_leverage_index,
        AVG(CASE WHEN metrics.position = 'RB' THEN opportunity.high_value_opportunity_score ELSE NULL END) AS rb_high_value_opportunity_score,
        AVG(CASE
            WHEN metrics.position = 'WR' THEN opportunity.wr_dominance_score
            WHEN metrics.position = 'TE' THEN opportunity.te_receiving_role_dominance_score
            ELSE NULL
        END) AS receiving_role_dominance_score,
        LEAST(100.0, GREATEST(0.0, AVG(COALESCE(opportunity.red_zone_targets, 0) * 4.0 + COALESCE(opportunity.red_zone_carries, 0) * 4.0 + COALESCE(opportunity.red_zone_touches, 0) * 3.0))) AS red_zone_usage_score,
        LEAST(100.0, GREATEST(0.0, AVG(COALESCE(opportunity.inside_5_carries, 0) * 12.0 + COALESCE(opportunity.inside_10_carries, 0) * 6.0))) AS goal_line_usage_score,
        AVG(opportunity.team_environment_score) AS opportunity_team_environment_score,
        AVG(ideal.xfp_score) AS xfp_score,
        AVG(ideal.xfp_share) AS xfp_share,
        AVG(ideal.fantasy_points_over_expectation) AS fantasy_points_over_expectation,
        AVG(ideal.offensive_snap_share) AS ideal_offensive_snap_share,
        AVG(ideal.role_stability_from_snaps) AS ideal_role_stability_from_snaps,
        AVG(ideal.receiving_role_dominance_xfp) AS receiving_role_dominance_xfp,
        AVG(ideal.high_value_xfp_score) AS high_value_xfp_score,
        AVG(ideal.qb_ngs_efficiency_score) AS qb_ngs_efficiency_score,
        AVG(ideal.injury_risk_score) AS injury_risk_score,
        AVG(role_context.injury_status_score) AS injury_status_score,
        AVG(role_context.injury_burden_score) AS injury_burden_score,
        AVG(role_context.missed_time_risk_score) AS missed_time_risk_score,
        AVG(role_context.availability_score) AS role_context_availability_score,
        AVG(ideal.depth_chart_role_score) AS depth_chart_role_score,
        AVG(pbp_ideal.receiving_xfp_pbp) AS receiving_xfp_pbp,
        AVG(pbp_ideal.rushing_xfp_pbp) AS rushing_xfp_pbp,
        AVG(pbp_ideal.passing_xfp_pbp) AS passing_xfp_pbp,
        AVG(pbp_ideal.red_zone_xfp_score) AS pbp_red_zone_xfp_score,
        AVG(pbp_ideal.goal_line_xfp_score) AS pbp_goal_line_xfp_score,
        AVG(pbp_ideal.high_value_target_xfp) AS high_value_target_xfp,
        AVG(pbp_ideal.high_value_rush_xfp) AS high_value_rush_xfp,
        AVG(pbp_ideal.receiving_xfp_share) AS receiving_xfp_share_pbp,
        AVG(pbp_ideal.rushing_xfp_share) AS rushing_xfp_share_pbp,
        AVG(pbp_ideal.opportunity_quality_score) AS pbp_opportunity_quality_score,
        AVG(pbp_ideal.receiving_first_down_exp_pbp) AS receiving_first_down_exp_pbp,
        AVG(pbp_ideal.rushing_first_down_exp_pbp) AS rushing_first_down_exp_pbp,
        AVG(pbp_ideal.passing_first_down_exp_pbp) AS passing_first_down_exp_pbp,
        AVG(pbp_ideal.high_value_first_down_opportunity_score) AS high_value_first_down_opportunity_score,
        AVG(pbp_ideal.receiving_chain_mover_score) AS receiving_chain_mover_score,
        AVG(pbp_ideal.rushing_chain_mover_score) AS rushing_chain_mover_score,
        AVG(IF(opportunity.spike_week_flag, 1.0, 0.0)) AS spike_week_rate,
        AVG(IF(opportunity.bust_week_flag, 1.0, 0.0)) AS bust_week_rate,
        AVG(IF(opportunity.elite_week_flag, 1.0, 0.0)) AS elite_week_rate,
        SAFE_DIVIDE(COUNT(DISTINCT metrics.week), 17) AS availability_rate,
        STDDEV(metrics.opportunities) AS weekly_volatility,
        LEAST(100.0, GREATEST(0.0, SAFE_DIVIDE(COUNT(DISTINCT metrics.week), 17) * 100.0 - COALESCE(STDDEV(metrics.opportunities), 0.0) * 2.0)) AS role_stability_score,
        ANY_VALUE(metrics.source_freshness_json) AS metrics_source_freshness_json,
        ANY_VALUE(metrics.missing_data_flags) AS metrics_missing_flags,
        ANY_VALUE(opportunity.source_freshness_json) AS opportunity_source_freshness_json,
        ANY_VALUE(opportunity.missing_flags_json) AS opportunity_missing_flags,
        ANY_VALUE(ideal.source_provenance_json) AS ideal_source_provenance_json,
        ANY_VALUE(ideal.missing_flags_json) AS ideal_missing_flags,
        ANY_VALUE(role_context.source_provenance_json) AS role_context_source_provenance_json,
        ANY_VALUE(role_context.injury_context_missing_flags_json) AS role_context_missing_flags,
        ANY_VALUE(pbp_ideal.source_provenance_json) AS pbp_source_provenance_json,
        ANY_VALUE(pbp_ideal.missing_flags_json) AS pbp_missing_flags
    FROM `{metrics_table}` metrics
    JOIN positions
      ON metrics.position = positions.position
    CROSS JOIN profiles
    LEFT JOIN `{truth_table}` truth
      ON metrics.season = truth.season
     AND metrics.week = truth.week
     AND REGEXP_REPLACE(metrics.player_id_internal, r'^gsis:', '') = REGEXP_REPLACE(truth.player_id, r'^gsis:', '')
    LEFT JOIN `{points_table}` source_profile
      ON metrics.season = source_profile.season
     AND metrics.week = source_profile.week
     AND REGEXP_REPLACE(metrics.player_id_internal, r'^gsis:', '') = REGEXP_REPLACE(source_profile.player_id_internal, r'^gsis:', '')
     AND source_profile.scoring_profile_id = profiles.scoring_profile_id
     AND COALESCE(source_profile.league_type_id, @league_type_id) = @league_type_id
     AND COALESCE(source_profile.roster_format_id, @roster_format_id) = @roster_format_id
    LEFT JOIN `{opportunity_table}` opportunity
      ON metrics.season = opportunity.season
     AND metrics.week = opportunity.week
     AND REGEXP_REPLACE(metrics.player_id_internal, r'^gsis:', '') = REGEXP_REPLACE(opportunity.player_id_internal, r'^gsis:', '')
     AND metrics.position = opportunity.position
    LEFT JOIN `{ideal_table}` ideal
      ON metrics.season = ideal.season
     AND metrics.week = ideal.week
     AND REGEXP_REPLACE(metrics.player_id_internal, r'^gsis:', '') = REGEXP_REPLACE(ideal.player_id_internal, r'^gsis:', '')
     AND metrics.position = ideal.position
     AND ideal.source_version = 'ffopportunity_weekly_latest'
    LEFT JOIN `{pbp_ideal_table}` pbp_ideal
      ON metrics.season = pbp_ideal.season
     AND metrics.week = pbp_ideal.week
     AND REGEXP_REPLACE(metrics.player_id_internal, r'^gsis:', '') = REGEXP_REPLACE(pbp_ideal.player_id_internal, r'^gsis:', '')
     AND metrics.position = pbp_ideal.position
     AND pbp_ideal.source_version = 'ffopportunity_pbp_latest'
    LEFT JOIN `{role_context_table}` role_context
      ON metrics.season = role_context.season
     AND metrics.week = role_context.week
     AND REGEXP_REPLACE(metrics.player_id_internal, r'^gsis:', '') = REGEXP_REPLACE(role_context.player_id_internal, r'^gsis:', '')
     AND metrics.position = role_context.position
    WHERE metrics.season BETWEEN @source_window_start_season AND @source_window_end_season
      AND metrics.season < @target_season
      AND metrics.scoring_profile_id = 'ppr'
      AND metrics.league_type_id = @league_type_id
      AND metrics.roster_format_id = @roster_format_id
    GROUP BY profiles.scoring_profile_id, metrics.player_id_internal, metrics.position, metrics.season
),
source_features AS (
    SELECT
        scoring_profile_id,
        player_key,
        ANY_VALUE(player_id_internal) AS player_id_internal,
        ANY_VALUE(player_name) AS player_name,
        position,
        ANY_VALUE(source_team HAVING MAX season) AS source_team,
        AVG(recent_points_avg) AS recent_points_avg,
        AVG(profile_points_score) AS profile_points_score,
        AVG(targets) AS targets,
        AVG(carries) AS carries,
        AVG(receiving_yards) AS receiving_yards,
        AVG(receiving_epa) AS receiving_epa,
        AVG(red_zone_targets) AS red_zone_targets,
        AVG(red_zone_carries) AS red_zone_carries,
        AVG(outside_red_zone_targets) AS outside_red_zone_targets,
        AVG(outside_red_zone_carries) AS outside_red_zone_carries,
        AVG(gemini31_rb_weighted_opportunity_ppr) AS gemini31_rb_weighted_opportunity_ppr,
        AVG(success_rate) AS success_rate,
        AVG(passing_success_rate) AS passing_success_rate,
        AVG(dropbacks) AS dropbacks,
        AVG(rushing_attempts) AS rushing_attempts,
        AVG(rush_success_rate) AS rush_success_rate,
        AVG(receiving_usage) AS receiving_usage,
        AVG(cpoe) AS cpoe,
        AVG(usage_volume) AS usage_volume,
        AVG(epa_per_play) AS epa_per_play,
        AVG(opportunity_score_proxy) AS opportunity_score_proxy,
        AVG(efficiency_score_proxy) AS efficiency_score_proxy,
        AVG((opportunity_score_proxy + efficiency_score_proxy) / 2.0) AS analytical_grade_proxy,
        AVG(passing_epa_per_play) AS passing_epa_per_play,
        AVG(red_zone_opportunities) AS red_zone_opportunities,
        AVG(goal_line_opportunities) AS goal_line_opportunities,
        AVG(snap_share_proxy) AS snap_share_proxy,
        AVG(air_yards) AS air_yards,
        AVG(team_pass_rate) AS team_pass_rate,
        AVG(qb_rushing_leverage_index) AS qb_rushing_leverage_index,
        AVG(rb_high_value_opportunity_score) AS rb_high_value_opportunity_score,
        AVG(receiving_role_dominance_score) AS receiving_role_dominance_score,
        AVG(red_zone_usage_score) AS red_zone_usage_score,
        AVG(goal_line_usage_score) AS goal_line_usage_score,
        AVG(opportunity_team_environment_score) AS opportunity_team_environment_score,
        AVG(xfp_score) AS xfp_score_3yr,
        AVG(xfp_share) AS xfp_share_3yr,
        AVG(fantasy_points_over_expectation) AS fantasy_points_over_expectation_3yr,
        AVG(ideal_offensive_snap_share) AS offensive_snap_share_3yr,
        AVG(ideal_role_stability_from_snaps) AS snap_role_stability_3yr,
        AVG(receiving_role_dominance_xfp) AS receiving_role_dominance_xfp_3yr,
        AVG(high_value_xfp_score) AS high_value_xfp_score_3yr,
        AVG(qb_ngs_efficiency_score) AS qb_ngs_efficiency_score_3yr,
        AVG(injury_risk_score) AS injury_risk_score_3yr,
        AVG(injury_status_score) AS injury_status_score_3yr,
        AVG(injury_burden_score) AS injury_burden_score_3yr,
        AVG(missed_time_risk_score) AS missed_time_risk_score_3yr,
        AVG(role_context_availability_score) AS availability_score_3yr,
        AVG(depth_chart_role_score) AS depth_chart_role_score_3yr,
        AVG(receiving_xfp_pbp) AS receiving_xfp_pbp_3yr,
        AVG(rushing_xfp_pbp) AS rushing_xfp_pbp_3yr,
        AVG(passing_xfp_pbp) AS passing_xfp_pbp_3yr,
        AVG(pbp_red_zone_xfp_score) AS red_zone_xfp_score_3yr,
        AVG(pbp_goal_line_xfp_score) AS goal_line_xfp_score_3yr,
        AVG(high_value_target_xfp) AS high_value_target_xfp_score_3yr,
        AVG(high_value_rush_xfp) AS high_value_rush_xfp_score_3yr,
        AVG(receiving_xfp_share_pbp) AS receiving_xfp_share_pbp_3yr,
        AVG(rushing_xfp_share_pbp) AS rushing_xfp_share_pbp_3yr,
        AVG(pbp_opportunity_quality_score) AS opportunity_quality_score_3yr,
        AVG(receiving_first_down_exp_pbp) AS receiving_first_down_exp_pbp_3yr,
        AVG(rushing_first_down_exp_pbp) AS rushing_first_down_exp_pbp_3yr,
        AVG(passing_first_down_exp_pbp) AS passing_first_down_exp_pbp_3yr,
        AVG(high_value_first_down_opportunity_score) AS high_value_first_down_opportunity_score_3yr,
        AVG(receiving_chain_mover_score) AS receiving_chain_mover_score_3yr,
        AVG(rushing_chain_mover_score) AS rushing_chain_mover_score_3yr,
        AVG(spike_week_rate) AS spike_week_rate_3yr,
        AVG(bust_week_rate) AS bust_week_rate_3yr,
        AVG(elite_week_rate) AS elite_week_rate_3yr,
        _slope(ARRAY_AGG(STRUCT(season, points_per_game AS value) ORDER BY season)) AS points_per_game_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, total_points AS value) ORDER BY season)) AS total_points_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, usage_volume AS value) ORDER BY season)) AS opportunity_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, target_share AS value) ORDER BY season)) AS target_share_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, carry_share AS value) ORDER BY season)) AS carry_share_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, receiving_usage AS value) ORDER BY season)) AS receiving_usage_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, wopr AS value) ORDER BY season)) AS wopr_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, epa_per_play AS value) ORDER BY season)) AS epa_slope_3yr,
        _slope(ARRAY_AGG(STRUCT(season, success_rate AS value) ORDER BY season)) AS efficiency_slope_3yr,
        AVG(availability_rate) AS availability_rate_3yr,
        AVG(weekly_volatility) AS weekly_volatility_3yr,
        AVG(role_stability_score) AS role_stability_score,
        IF(_slope(ARRAY_AGG(STRUCT(season, usage_volume AS value) ORDER BY season)) > 0
           AND _slope(ARRAY_AGG(STRUCT(season, epa_per_play AS value) ORDER BY season)) > 0, 1.0, 0.0) AS improving_3yr,
        IF(_slope(ARRAY_AGG(STRUCT(season, usage_volume AS value) ORDER BY season)) < 0
           AND _slope(ARRAY_AGG(STRUCT(season, epa_per_play AS value) ORDER BY season)) < 0, 1.0, 0.0) AS declining_3yr,
        IF(_slope(ARRAY_AGG(STRUCT(season, target_share AS value) ORDER BY season)) > 0
           OR _slope(ARRAY_AGG(STRUCT(season, carry_share AS value) ORDER BY season)) > 0, 1.0, 0.0) AS breakout_trajectory_3yr,
        ANY_VALUE(metrics_source_freshness_json HAVING MAX season) AS metrics_source_freshness_json,
        ANY_VALUE(metrics_missing_flags HAVING MAX season) AS metrics_missing_flags,
        ANY_VALUE(opportunity_source_freshness_json HAVING MAX season) AS opportunity_source_freshness_json,
        ANY_VALUE(opportunity_missing_flags HAVING MAX season) AS opportunity_missing_flags,
        ANY_VALUE(ideal_source_provenance_json HAVING MAX season) AS ideal_source_provenance_json,
        ANY_VALUE(ideal_missing_flags HAVING MAX season) AS ideal_missing_flags,
        ANY_VALUE(role_context_source_provenance_json HAVING MAX season) AS role_context_source_provenance_json,
        ANY_VALUE(role_context_missing_flags HAVING MAX season) AS role_context_missing_flags,
        ANY_VALUE(pbp_source_provenance_json HAVING MAX season) AS pbp_source_provenance_json,
        ANY_VALUE(pbp_missing_flags HAVING MAX season) AS pbp_missing_flags
    FROM season_features
    GROUP BY scoring_profile_id, player_key, position
),
packet_context AS (
    SELECT
        REGEXP_REPLACE(player_id_internal, r'^gsis:', '') AS player_key,
        position,
        scoring_profile_id,
        AVG(SAFE_CAST(JSON_VALUE(team_context_json, '$.team_epa_per_play') AS FLOAT64)) AS packet_team_epa_per_play,
        AVG(SAFE_CAST(JSON_VALUE(team_context_json, '$.neutral_pass_rate') AS FLOAT64)) AS packet_team_pass_rate,
        ANY_VALUE(source_freshness_json) AS packet_source_freshness_json
    FROM `{packet_table}`
    WHERE as_of_season = @source_window_end_season
      AND scoring_profile_id IN UNNEST(@scoring_profile_ids)
      AND position IN UNNEST(@positions)
      AND COALESCE(league_type_id, @league_type_id) = @league_type_id
      AND COALESCE(roster_format_id, @roster_format_id) = @roster_format_id
    GROUP BY player_key, position, scoring_profile_id
),
target_points AS (
    SELECT
        target.season AS target_season,
        target.week AS target_week,
        REGEXP_REPLACE(target.player_id_internal, r'^gsis:', '') AS player_key,
        REGEXP_REPLACE(target.player_id_internal, r'^gsis:', '') AS player_id_internal,
        target.player_display_name AS player_name,
        target.position,
        target.team,
        target.scoring_profile_id,
        COALESCE(target.league_type_id, @league_type_id) AS league_type_id,
        COALESCE(target.roster_format_id, @roster_format_id) AS roster_format_id,
        target.total_fantasy_points AS target_fantasy_points
    FROM `{points_table}` target
    WHERE target.season = @target_season
      AND target.scoring_profile_id IN UNNEST(@scoring_profile_ids)
      AND target.position IN UNNEST(@positions)
      AND COALESCE(target.league_type_id, @league_type_id) = @league_type_id
      AND COALESCE(target.roster_format_id, @roster_format_id) = @roster_format_id
      AND target.player_id_internal IS NOT NULL
),
with_source AS (
    SELECT
        @source_window_start_season AS source_window_start_season,
        @source_window_end_season AS source_window_end_season,
        target.target_season,
        target.target_week,
        target.scoring_profile_id,
        target.league_type_id,
        target.roster_format_id,
        target.position,
        target.player_id_internal,
        COALESCE(target.player_name, source.player_name) AS player_name,
        target.team,
        source.source_team,
        source.recent_points_avg,
        source.profile_points_score,
        source.opportunity_score_proxy,
        source.efficiency_score_proxy,
        source.analytical_grade_proxy,
        source.role_stability_score,
        source.targets,
        source.carries,
    source.receiving_yards,
    source.receiving_epa,
    source.red_zone_targets,
    source.red_zone_carries,
    source.outside_red_zone_targets,
    source.outside_red_zone_carries,
    source.gemini31_rb_weighted_opportunity_ppr,
    source.success_rate,
        source.passing_success_rate,
        source.dropbacks,
        source.rushing_attempts,
        source.rush_success_rate,
        source.receiving_usage,
        source.cpoe,
        source.usage_volume,
        source.epa_per_play,
        source.passing_epa_per_play,
        packet.packet_team_epa_per_play AS team_epa_per_play,
        source.red_zone_opportunities,
        source.goal_line_opportunities,
        source.snap_share_proxy,
        source.air_yards,
        COALESCE(source.team_pass_rate, packet.packet_team_pass_rate) AS team_pass_rate,
        source.qb_rushing_leverage_index,
        source.rb_high_value_opportunity_score,
        source.receiving_role_dominance_score,
        source.red_zone_usage_score,
        source.goal_line_usage_score,
        source.opportunity_team_environment_score AS team_environment_score,
        source.spike_week_rate_3yr,
        source.bust_week_rate_3yr,
        source.elite_week_rate_3yr,
        source.points_per_game_slope_3yr,
        source.total_points_slope_3yr,
        source.opportunity_slope_3yr,
        source.target_share_slope_3yr,
        source.carry_share_slope_3yr,
        source.receiving_usage_slope_3yr,
        source.wopr_slope_3yr,
        source.epa_slope_3yr,
        source.efficiency_slope_3yr,
        source.availability_rate_3yr,
        source.weekly_volatility_3yr,
        source.improving_3yr,
        source.declining_3yr,
        source.breakout_trajectory_3yr,
        source.xfp_score_3yr,
        source.xfp_share_3yr,
        source.fantasy_points_over_expectation_3yr,
        source.offensive_snap_share_3yr,
        source.snap_role_stability_3yr,
        source.receiving_role_dominance_xfp_3yr,
        source.high_value_xfp_score_3yr,
        source.qb_ngs_efficiency_score_3yr,
        source.injury_risk_score_3yr,
        source.injury_status_score_3yr,
        source.injury_burden_score_3yr,
        source.missed_time_risk_score_3yr,
        source.availability_score_3yr,
        COALESCE(source.role_context_missing_flags, TO_JSON_STRING(STRUCT(
            source.injury_status_score_3yr IS NULL AS injury_status_score_3yr_missing,
            source.injury_burden_score_3yr IS NULL AS injury_burden_score_3yr_missing,
            source.missed_time_risk_score_3yr IS NULL AS missed_time_risk_score_3yr_missing,
            source.availability_score_3yr IS NULL AS availability_score_3yr_missing,
            TRUE AS aggregated_role_context_flags
        ))) AS injury_context_missing_flags_json,
        source.depth_chart_role_score_3yr,
        source.receiving_xfp_pbp_3yr,
        source.rushing_xfp_pbp_3yr,
        source.passing_xfp_pbp_3yr,
        source.red_zone_xfp_score_3yr,
        source.goal_line_xfp_score_3yr,
        source.high_value_target_xfp_score_3yr,
        source.high_value_rush_xfp_score_3yr,
        source.receiving_xfp_share_pbp_3yr,
        source.rushing_xfp_share_pbp_3yr,
        source.opportunity_quality_score_3yr,
        source.receiving_first_down_exp_pbp_3yr,
        source.rushing_first_down_exp_pbp_3yr,
        source.passing_first_down_exp_pbp_3yr,
        source.high_value_first_down_opportunity_score_3yr,
        source.receiving_chain_mover_score_3yr,
        source.rushing_chain_mover_score_3yr,
        target.target_fantasy_points,
        source.metrics_source_freshness_json,
        source.metrics_missing_flags,
        source.opportunity_source_freshness_json,
        source.opportunity_missing_flags,
        source.ideal_source_provenance_json,
        source.ideal_missing_flags,
        source.role_context_source_provenance_json,
        source.role_context_missing_flags,
        source.pbp_source_provenance_json,
        source.pbp_missing_flags,
        packet.packet_source_freshness_json
    FROM target_points target
    JOIN source_features source
      ON target.player_key = source.player_key
     AND target.position = source.position
     AND target.scoring_profile_id = source.scoring_profile_id
    LEFT JOIN packet_context packet
      ON target.player_key = packet.player_key
     AND target.position = packet.position
     AND target.scoring_profile_id = packet.scoring_profile_id
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY target_season, target_week, scoring_profile_id, league_type_id, roster_format_id, position
            ORDER BY target_fantasy_points DESC, player_id_internal
        ) AS actual_position_rank,
        ROW_NUMBER() OVER (
            PARTITION BY target_season, target_week, scoring_profile_id, league_type_id, roster_format_id
            ORDER BY target_fantasy_points DESC, player_id_internal
        ) AS actual_overall_rank,
        CASE position WHEN 'QB' THEN 12 WHEN 'RB' THEN 24 WHEN 'WR' THEN 24 WHEN 'TE' THEN 12 ELSE 24 END AS replacement_rank
    FROM with_source
),
with_replacement AS (
    SELECT
        *,
        MAX(IF(actual_position_rank = replacement_rank, target_fantasy_points, NULL)) OVER (
            PARTITION BY target_season, target_week, scoring_profile_id, league_type_id, roster_format_id, position
        ) AS replacement_points
    FROM ranked
)
SELECT
    source_window_start_season,
    source_window_end_season,
    target_season,
    target_week,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    position,
    player_id_internal,
    player_name,
    team,
    source_team,
    recent_points_avg,
    profile_points_score,
    opportunity_score_proxy,
    efficiency_score_proxy,
    analytical_grade_proxy,
    role_stability_score,
    targets,
    carries,
    receiving_yards,
    receiving_epa,
    red_zone_targets,
    red_zone_carries,
    outside_red_zone_targets,
    outside_red_zone_carries,
    gemini31_rb_weighted_opportunity_ppr,
    success_rate,
    passing_success_rate,
    dropbacks,
    rushing_attempts,
    rush_success_rate,
    receiving_usage,
    cpoe,
    usage_volume,
    epa_per_play,
    passing_epa_per_play,
    team_epa_per_play,
    red_zone_opportunities,
    goal_line_opportunities,
    snap_share_proxy,
    air_yards,
    team_pass_rate,
    qb_rushing_leverage_index,
    rb_high_value_opportunity_score,
    receiving_role_dominance_score,
    red_zone_usage_score,
    goal_line_usage_score,
    team_environment_score,
    spike_week_rate_3yr,
    bust_week_rate_3yr,
    elite_week_rate_3yr,
    points_per_game_slope_3yr,
    total_points_slope_3yr,
    opportunity_slope_3yr,
    target_share_slope_3yr,
    carry_share_slope_3yr,
    receiving_usage_slope_3yr,
    wopr_slope_3yr,
    epa_slope_3yr,
    efficiency_slope_3yr,
    availability_rate_3yr,
    weekly_volatility_3yr,
    improving_3yr,
    declining_3yr,
    breakout_trajectory_3yr,
    xfp_score_3yr,
    xfp_share_3yr,
    fantasy_points_over_expectation_3yr,
    offensive_snap_share_3yr,
    snap_role_stability_3yr,
    receiving_role_dominance_xfp_3yr,
    high_value_xfp_score_3yr,
    qb_ngs_efficiency_score_3yr,
    injury_risk_score_3yr,
    injury_status_score_3yr,
    injury_burden_score_3yr,
    missed_time_risk_score_3yr,
    availability_score_3yr,
    injury_context_missing_flags_json,
    depth_chart_role_score_3yr,
    receiving_xfp_pbp_3yr,
    rushing_xfp_pbp_3yr,
    passing_xfp_pbp_3yr,
    red_zone_xfp_score_3yr,
    goal_line_xfp_score_3yr,
    high_value_target_xfp_score_3yr,
    high_value_rush_xfp_score_3yr,
    receiving_xfp_share_pbp_3yr,
    rushing_xfp_share_pbp_3yr,
    opportunity_quality_score_3yr,
    receiving_first_down_exp_pbp_3yr,
    rushing_first_down_exp_pbp_3yr,
    passing_first_down_exp_pbp_3yr,
    high_value_first_down_opportunity_score_3yr,
    receiving_chain_mover_score_3yr,
    rushing_chain_mover_score_3yr,
    pbp_missing_flags AS pbp_xfp_missing_flags_json,
    target_fantasy_points,
    actual_position_rank,
    actual_overall_rank,
    replacement_points,
    GREATEST(target_fantasy_points - COALESCE(replacement_points, target_fantasy_points), 0) AS value_over_replacement,
    actual_overall_rank <= 24 AS top_24_overall,
    actual_overall_rank <= 50 AS top_50_overall,
    actual_overall_rank <= 100 AS top_100_overall,
    CASE
      WHEN actual_overall_rank BETWEEN 1 AND 12 THEN '1-12'
      WHEN actual_overall_rank BETWEEN 13 AND 24 THEN '13-24'
      WHEN actual_overall_rank BETWEEN 25 AND 36 THEN '25-36'
      WHEN actual_overall_rank BETWEEN 37 AND 60 THEN '37-60'
      WHEN actual_overall_rank BETWEEN 61 AND 100 THEN '61-100'
      WHEN actual_overall_rank >= 101 THEN '101+'
      ELSE NULL
    END AS actual_pick_band,
    TO_JSON_STRING(STRUCT(
        recent_points_avg IS NULL AS recent_points_avg_missing,
        profile_points_score IS NULL AS profile_points_score_missing,
        opportunity_score_proxy IS NULL AS opportunity_score_proxy_missing,
        efficiency_score_proxy IS NULL AS efficiency_score_proxy_missing,
        analytical_grade_proxy IS NULL AS analytical_grade_proxy_missing,
        role_stability_score IS NULL AS role_stability_score_missing,
        qb_rushing_leverage_index IS NULL AS qb_rushing_leverage_index_missing,
        rb_high_value_opportunity_score IS NULL AS rb_high_value_opportunity_score_missing,
        receiving_role_dominance_score IS NULL AS receiving_role_dominance_score_missing,
        red_zone_usage_score IS NULL AS red_zone_usage_score_missing,
        goal_line_usage_score IS NULL AS goal_line_usage_score_missing,
        team_environment_score IS NULL AS team_environment_score_missing,
        xfp_score_3yr IS NULL AS xfp_score_3yr_missing,
        xfp_share_3yr IS NULL AS xfp_share_3yr_missing,
        offensive_snap_share_3yr IS NULL AS offensive_snap_share_3yr_missing,
        receiving_role_dominance_xfp_3yr IS NULL AS receiving_role_dominance_xfp_3yr_missing,
        qb_ngs_efficiency_score_3yr IS NULL AS qb_ngs_efficiency_score_3yr_missing,
        injury_risk_score_3yr IS NULL AS injury_risk_score_3yr_missing,
        injury_status_score_3yr IS NULL AS injury_status_score_3yr_missing,
        injury_burden_score_3yr IS NULL AS injury_burden_score_3yr_missing,
        missed_time_risk_score_3yr IS NULL AS missed_time_risk_score_3yr_missing,
        availability_score_3yr IS NULL AS availability_score_3yr_missing,
        depth_chart_role_score_3yr IS NULL AS depth_chart_role_score_3yr_missing,
        receiving_xfp_pbp_3yr IS NULL AS receiving_xfp_pbp_3yr_missing,
        rushing_xfp_pbp_3yr IS NULL AS rushing_xfp_pbp_3yr_missing,
        passing_xfp_pbp_3yr IS NULL AS passing_xfp_pbp_3yr_missing,
        red_zone_xfp_score_3yr IS NULL AS red_zone_xfp_score_3yr_missing,
        goal_line_xfp_score_3yr IS NULL AS goal_line_xfp_score_3yr_missing,
        opportunity_quality_score_3yr IS NULL AS opportunity_quality_score_3yr_missing,
        receiving_first_down_exp_pbp_3yr IS NULL AS receiving_first_down_exp_pbp_3yr_missing,
        rushing_first_down_exp_pbp_3yr IS NULL AS rushing_first_down_exp_pbp_3yr_missing,
        passing_first_down_exp_pbp_3yr IS NULL AS passing_first_down_exp_pbp_3yr_missing,
        high_value_first_down_opportunity_score_3yr IS NULL AS high_value_first_down_opportunity_score_3yr_missing,
        receiving_chain_mover_score_3yr IS NULL AS receiving_chain_mover_score_3yr_missing,
        rushing_chain_mover_score_3yr IS NULL AS rushing_chain_mover_score_3yr_missing,
        metrics_missing_flags AS source_missing_flags,
        opportunity_missing_flags AS opportunity_missing_flags,
        ideal_missing_flags AS ideal_missing_flags,
        injury_context_missing_flags_json AS injury_context_missing_flags_json,
        pbp_missing_flags AS pbp_missing_flags
    )) AS predictor_missing_flags_json,
    TO_JSON_STRING(STRUCT(
        target_fantasy_points IS NULL AS target_fantasy_points_missing,
        replacement_points IS NULL AS replacement_points_missing
    )) AS outcome_missing_flags_json,
    TO_JSON_STRING(STRUCT(
        metrics_source_freshness_json AS metrics_source_freshness_json,
        opportunity_source_freshness_json AS opportunity_source_freshness_json,
        ideal_source_provenance_json AS ideal_source_provenance_json,
        role_context_source_provenance_json AS role_context_source_provenance_json,
        pbp_source_provenance_json AS pbp_source_provenance_json,
        packet_source_freshness_json AS packet_source_freshness_json
    )) AS source_freshness_json,
    TO_JSON_STRING(STRUCT(
        'ranking_backtest_feature_mart' AS builder,
        @source_window_start_season AS source_window_start_season,
        @source_window_end_season AS source_window_end_season,
        @target_season AS target_season,
        'target-season predictors excluded' AS leakage_policy
    )) AS provenance_json,
    CURRENT_TIMESTAMP() AS created_at
FROM with_replacement
""".strip()


def populate_ranking_backtest_feature_mart(
    *,
    client: Any,
    target_season: int,
    scoring_profile_ids: list[str] | tuple[str, ...],
    positions: list[str] | tuple[str, ...],
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    league_type_id: str = DEFAULT_LEAGUE_TYPE_ID,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT_ID,
    source_window_years: int = 3,
) -> dict[str, Any]:
    normalized_profiles = [str(profile) for profile in scoring_profile_ids]
    normalized_positions = [_normalize_position(position) for position in positions]
    source_window_end = int(target_season) - 1
    source_window_start = max(source_window_end - _normalize_source_window_years(source_window_years) + 1, 2014)
    params = _feature_mart_query_params(
        target_season=target_season,
        source_window_start=source_window_start,
        source_window_end=source_window_end,
        scoring_profile_ids=normalized_profiles,
        positions=normalized_positions,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    client.query(
        build_feature_mart_delete_sql(project_id=project_id, dataset_id=dataset_id),
        job_config=_query_job_config(params),
    ).result()
    client.query(
        build_feature_mart_insert_sql(project_id=project_id, dataset_id=dataset_id),
        job_config=_query_job_config(params),
    ).result()
    count_sql = f"""
SELECT COUNT(*) AS row_count
FROM `{table_id(project_id, dataset_id, "ranking_backtest_feature_mart")}`
WHERE target_season = @target_season
  AND scoring_profile_id IN UNNEST(@scoring_profile_ids)
  AND position IN UNNEST(@positions)
  AND league_type_id = @league_type_id
  AND roster_format_id = @roster_format_id
""".strip()
    row_count = list(client.query(count_sql, job_config=_query_job_config(params)).result())[0]["row_count"]
    return {
        "target_table": table_id(project_id, dataset_id, "ranking_backtest_feature_mart"),
        "target_season": int(target_season),
        "source_window_start_season": source_window_start,
        "source_window_end_season": source_window_end,
        "scoring_profile_ids": normalized_profiles,
        "positions": normalized_positions,
        "row_count": int(row_count),
    }


def build_sql_native_scoring_prototype_sql(
    *,
    project_id: str,
    dataset_id: str,
    target_season: int = 2025,
    scoring_profile_id: str = "ppr",
    position: str = "TE",
) -> str:
    mart_table = table_id(project_id, dataset_id, "ranking_backtest_feature_mart")
    normalized_position = _normalize_position(position)
    return f"""
WITH formula_weights AS (
  SELECT 'current_pigskin_candidate_score_v1' AS candidate_id, 'analytical_grade_proxy' AS feature_name, 0.55 AS weight UNION ALL
  SELECT 'current_pigskin_candidate_score_v1', 'opportunity_score_proxy', 0.15 UNION ALL
  SELECT 'current_pigskin_candidate_score_v1', 'efficiency_score_proxy', 0.10 UNION ALL
  SELECT 'current_pigskin_candidate_score_v1', 'role_stability_score', 0.10 UNION ALL
  SELECT 'current_pigskin_candidate_score_v1', 'profile_points_score', 0.10 UNION ALL
  SELECT 'simple_projection_points_baseline', 'profile_points_score', 1.00 UNION ALL
  SELECT 'v2_trend_balanced', 'target_share_slope_3yr', 0.25 UNION ALL
  SELECT 'v2_trend_balanced', 'receiving_usage_slope_3yr', 0.20 UNION ALL
  SELECT 'v2_trend_balanced', 'team_pass_rate', 0.20 UNION ALL
  SELECT 'v2_trend_balanced', 'availability_rate_3yr', 0.20
  UNION ALL SELECT 'v2_trend_balanced', 'declining_3yr', 0.15
),
mart AS (
  SELECT *
  FROM `{mart_table}`
  WHERE target_season = {int(target_season)}
    AND scoring_profile_id = '{scoring_profile_id}'
    AND position = '{normalized_position}'
    AND league_type_id = '{DEFAULT_LEAGUE_TYPE_ID}'
    AND roster_format_id = '{DEFAULT_ROSTER_FORMAT_ID}'
),
feature_values AS (
  SELECT
    mart.*,
    feature_name,
    CASE feature_name
      WHEN 'analytical_grade_proxy' THEN analytical_grade_proxy
      WHEN 'opportunity_score_proxy' THEN opportunity_score_proxy
      WHEN 'efficiency_score_proxy' THEN efficiency_score_proxy
      WHEN 'role_stability_score' THEN role_stability_score
      WHEN 'profile_points_score' THEN profile_points_score
      WHEN 'recent_points_avg' THEN recent_points_avg
      WHEN 'targets' THEN targets
      WHEN 'target_share_slope_3yr' THEN target_share_slope_3yr
      WHEN 'receiving_usage_slope_3yr' THEN receiving_usage_slope_3yr
      WHEN 'points_per_game_slope_3yr' THEN points_per_game_slope_3yr
      WHEN 'team_pass_rate' THEN team_pass_rate
      WHEN 'availability_rate_3yr' THEN availability_rate_3yr
      WHEN 'declining_3yr' THEN declining_3yr
      ELSE NULL
    END AS raw_feature_value
  FROM mart
  CROSS JOIN UNNEST([
    'analytical_grade_proxy',
    'opportunity_score_proxy',
    'efficiency_score_proxy',
    'role_stability_score',
    'profile_points_score',
    'recent_points_avg',
    'targets',
    'target_share_slope_3yr',
    'receiving_usage_slope_3yr',
    'points_per_game_slope_3yr',
    'team_pass_rate',
    'availability_rate_3yr',
    'declining_3yr'
  ]) AS feature_name
),
scored_features AS (
  SELECT
    *,
    CASE scoring_profile_id
      WHEN 'ppr' THEN ppr_weight
      WHEN 'half_ppr' THEN half_ppr_weight
      WHEN 'standard' THEN standard_weight
      WHEN 'gng_keeper' THEN gng_keeper_weight
      ELSE weight
    END AS effective_weight,
    CASE
      WHEN raw_feature_value IS NULL THEN NULL
      WHEN feature_name IN ('points_per_game_slope_3yr') THEN LEAST(100.0, GREATEST(0.0, 50.0 + raw_feature_value * 10.0))
      WHEN feature_name IN ('target_share_slope_3yr') THEN LEAST(100.0, GREATEST(0.0, 50.0 + raw_feature_value * 250.0))
      WHEN feature_name IN ('receiving_usage_slope_3yr') THEN LEAST(100.0, GREATEST(0.0, 50.0 + raw_feature_value * 10.0))
      WHEN feature_name = 'availability_rate_3yr' THEN LEAST(100.0, GREATEST(0.0, IF(raw_feature_value <= 1, raw_feature_value * 100.0, raw_feature_value)))
      WHEN feature_name = 'declining_3yr' THEN IF(raw_feature_value > 0, 0.0, 100.0)
      WHEN feature_name = 'team_pass_rate' THEN LEAST(100.0, GREATEST(0.0, raw_feature_value))
      WHEN feature_name = 'recent_points_avg' THEN LEAST(100.0, GREATEST(0.0, raw_feature_value / 35.0 * 100.0))
      WHEN feature_name = 'targets' THEN LEAST(100.0, GREATEST(0.0, raw_feature_value / 25.0 * 100.0))
      ELSE LEAST(100.0, GREATEST(0.0, raw_feature_value))
    END AS feature_score
  FROM feature_values
),
candidate_scores AS (
  SELECT
    weights.candidate_id,
    scored.target_season,
    scored.target_week,
    scored.scoring_profile_id,
    scored.position,
    scored.player_id_internal,
    ANY_VALUE(scored.player_name) AS player_name,
    ANY_VALUE(scored.team) AS team,
    ANY_VALUE(scored.target_fantasy_points) AS actual_points,
    ANY_VALUE(scored.actual_position_rank) AS actual_position_rank,
    ANY_VALUE(scored.value_over_replacement) AS value_over_replacement,
    SAFE_DIVIDE(SUM(scored.feature_score * weights.weight), SUM(IF(scored.feature_score IS NULL, 0, weights.weight))) AS predicted_score,
    1.0 - SAFE_DIVIDE(SUM(IF(scored.feature_score IS NULL, weights.weight, 0)), SUM(weights.weight)) AS available_weight_rate
  FROM formula_weights weights
  JOIN scored_features scored
    ON weights.feature_name = scored.feature_name
  GROUP BY weights.candidate_id, scored.target_season, scored.target_week, scored.scoring_profile_id, scored.position, scored.player_id_internal
),
ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY candidate_id, target_season, target_week, scoring_profile_id, position
      ORDER BY predicted_score DESC, player_id_internal
    ) AS predicted_rank_position
  FROM candidate_scores
),
weekly_summary AS (
  SELECT
    candidate_id,
    target_week,
    COUNT(*) AS source_row_count,
    AVG(1.0 - available_weight_rate) AS missing_input_rate,
    SAFE_DIVIDE(
      COUNTIF(predicted_rank_position <= 12 AND actual_position_rank <= 12),
      NULLIF(COUNTIF(actual_position_rank <= 12), 0)
    ) AS top_n_hit_rate,
    SUM(IF(predicted_rank_position <= 12, actual_points, 0)) AS predicted_top_points,
    SUM(IF(actual_position_rank <= 12, actual_points, 0)) AS actual_top_points,
    SUM(IF(predicted_rank_position <= 12, value_over_replacement, 0)) AS predicted_top_vor,
    SUM(IF(actual_position_rank <= 12, value_over_replacement, 0)) AS actual_top_vor
  FROM ranked
  GROUP BY candidate_id, target_week
),
summary AS (
  SELECT
    candidate_id,
    SUM(source_row_count) AS source_row_count,
    AVG(missing_input_rate) AS missing_input_rate,
    AVG(top_n_hit_rate) AS top_n_hit_rate,
    SAFE_DIVIDE(SUM(predicted_top_points), SUM(actual_top_points)) AS actual_points_captured_rate,
    SAFE_DIVIDE(SUM(predicted_top_vor), SUM(actual_top_vor)) AS value_over_replacement_captured_rate
  FROM weekly_summary
  GROUP BY candidate_id
),
rank_correlation AS (
  SELECT
    candidate_id,
    CORR(CAST(predicted_rank_position AS FLOAT64), CAST(actual_position_rank AS FLOAT64)) AS rank_correlation
  FROM ranked
  GROUP BY candidate_id
),
final_summary AS (
  SELECT
    summary.candidate_id,
    summary.source_row_count,
    summary.missing_input_rate,
    summary.top_n_hit_rate,
    summary.actual_points_captured_rate,
    summary.value_over_replacement_captured_rate,
    rank_correlation.rank_correlation
  FROM summary
  LEFT JOIN rank_correlation USING (candidate_id)
)
SELECT *
FROM final_summary
ORDER BY candidate_id
""".strip()


def run_sql_native_scoring_prototype(
    *,
    client: Any,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    target_season: int = 2025,
    scoring_profile_id: str = "ppr",
    position: str = "TE",
) -> list[dict[str, Any]]:
    sql = build_sql_native_scoring_prototype_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        target_season=target_season,
        scoring_profile_id=scoring_profile_id,
        position=position,
    )
    return [dict(row) for row in client.query(sql).result()]


def draft_utility_metric_contract() -> dict[str, Any]:
    return {
        "metrics": dict(DRAFT_UTILITY_METRIC_CONTRACT),
        "position_k_values": {position: list(values) for position, values in DRAFT_UTILITY_K_BY_POSITION.items()},
        "overall_k_values": list(DRAFT_UTILITY_OVERALL_K),
        "persistence": "ranking_backtest_candidate_summaries.metric_json",
    }


def build_sql_native_tournament_summary_sql(
    *,
    project_id: str,
    dataset_id: str,
    target_seasons: list[int] | tuple[int, ...] = tuple(range(2017, 2026)),
    scoring_profile_ids: list[str] | tuple[str, ...] = DEFAULT_SCORING_PROFILES,
    positions: list[str] | tuple[str, ...] = POSITIONS,
    candidate_rows: list[Mapping[str, Any]] | None = None,
    league_type_id: str = DEFAULT_LEAGUE_TYPE_ID,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT_ID,
) -> str:
    mart_table = table_id(project_id, dataset_id, "ranking_backtest_feature_mart")
    selected_candidates = candidate_rows or sql_native_tournament_candidates()
    formula_weight_sql = _formula_weight_rows_sql(selected_candidates)
    target_season_sql = ", ".join(str(int(season)) for season in sorted({int(season) for season in target_seasons}))
    profile_sql = ", ".join(_sql_string(profile) for profile in scoring_profile_ids)
    position_sql = ", ".join(_sql_string(_normalize_position(position)) for position in positions)
    return f"""
WITH formula_weights AS (
  {formula_weight_sql}
),
mart AS (
  SELECT *
  FROM `{mart_table}`
  WHERE target_season IN ({target_season_sql})
    AND scoring_profile_id IN ({profile_sql})
    AND position IN ({position_sql})
    AND league_type_id = {_sql_string(league_type_id)}
    AND roster_format_id = {_sql_string(roster_format_id)}
    AND source_window_end_season < target_season
),
feature_values AS (
  SELECT
    mart.*,
    weights.candidate_id,
    weights.formula_version,
    weights.feature_name,
    weights.weight,
    weights.ppr_weight,
    weights.half_ppr_weight,
    weights.standard_weight,
    weights.gng_keeper_weight,
    weights.availability_multiplier,
    CASE weights.feature_name
      WHEN 'actual_points' THEN target_fantasy_points
      WHEN 'fantasy_points_ppr' THEN target_fantasy_points
      WHEN 'recent_points_avg' THEN recent_points_avg
      WHEN 'profile_points_score' THEN profile_points_score
      WHEN 'analytical_grade_proxy' THEN analytical_grade_proxy
      WHEN 'opportunity_score_proxy' THEN opportunity_score_proxy
      WHEN 'efficiency_score_proxy' THEN efficiency_score_proxy
      WHEN 'role_stability_score' THEN role_stability_score
      WHEN 'targets' THEN targets
      WHEN 'carries' THEN carries
      WHEN 'receiving_yards' THEN receiving_yards
      WHEN 'receiving_epa' THEN receiving_epa
      WHEN 'red_zone_targets' THEN red_zone_targets
      WHEN 'red_zone_carries' THEN red_zone_carries
      WHEN 'outside_red_zone_targets' THEN outside_red_zone_targets
      WHEN 'outside_red_zone_carries' THEN outside_red_zone_carries
      WHEN 'gemini31_rb_weighted_opportunity_ppr' THEN gemini31_rb_weighted_opportunity_ppr
      WHEN 'success_rate' THEN success_rate
      WHEN 'passing_success_rate' THEN passing_success_rate
      WHEN 'cpoe' THEN cpoe
      WHEN 'dropbacks' THEN dropbacks
      WHEN 'rushing_attempts' THEN rushing_attempts
      WHEN 'rush_success_rate' THEN rush_success_rate
      WHEN 'receiving_usage' THEN receiving_usage
      WHEN 'usage_volume' THEN usage_volume
      WHEN 'epa_per_play' THEN epa_per_play
      WHEN 'passing_epa_per_play' THEN passing_epa_per_play
      WHEN 'team_epa_per_play' THEN team_epa_per_play
      WHEN 'red_zone_opportunities' THEN red_zone_opportunities
      WHEN 'goal_line_opportunities' THEN goal_line_opportunities
      WHEN 'snap_share_proxy' THEN snap_share_proxy
      WHEN 'air_yards' THEN air_yards
      WHEN 'team_pass_rate' THEN team_pass_rate
      WHEN 'qb_rushing_leverage_index' THEN qb_rushing_leverage_index
      WHEN 'rb_high_value_opportunity_score' THEN rb_high_value_opportunity_score
      WHEN 'receiving_role_dominance_score' THEN receiving_role_dominance_score
      WHEN 'red_zone_usage_score' THEN red_zone_usage_score
      WHEN 'goal_line_usage_score' THEN goal_line_usage_score
      WHEN 'team_environment_score' THEN team_environment_score
      WHEN 'spike_week_rate_3yr' THEN spike_week_rate_3yr
      WHEN 'bust_week_rate_3yr' THEN bust_week_rate_3yr
      WHEN 'elite_week_rate_3yr' THEN elite_week_rate_3yr
      WHEN 'points_per_game_slope_3yr' THEN points_per_game_slope_3yr
      WHEN 'total_points_slope_3yr' THEN total_points_slope_3yr
      WHEN 'opportunity_slope_3yr' THEN opportunity_slope_3yr
      WHEN 'target_share_slope_3yr' THEN target_share_slope_3yr
      WHEN 'carry_share_slope_3yr' THEN carry_share_slope_3yr
      WHEN 'receiving_usage_slope_3yr' THEN receiving_usage_slope_3yr
      WHEN 'wopr_slope_3yr' THEN wopr_slope_3yr
      WHEN 'epa_slope_3yr' THEN epa_slope_3yr
      WHEN 'efficiency_slope_3yr' THEN efficiency_slope_3yr
      WHEN 'availability_rate_3yr' THEN availability_rate_3yr
      WHEN 'weekly_volatility_3yr' THEN weekly_volatility_3yr
      WHEN 'improving_3yr' THEN improving_3yr
      WHEN 'declining_3yr' THEN declining_3yr
      WHEN 'breakout_trajectory_3yr' THEN breakout_trajectory_3yr
      WHEN 'xfp_score_3yr' THEN xfp_score_3yr
      WHEN 'xfp_share_3yr' THEN xfp_share_3yr
      WHEN 'fantasy_points_over_expectation_3yr' THEN fantasy_points_over_expectation_3yr
      WHEN 'offensive_snap_share_3yr' THEN offensive_snap_share_3yr
      WHEN 'snap_role_stability_3yr' THEN snap_role_stability_3yr
      WHEN 'receiving_role_dominance_xfp_3yr' THEN receiving_role_dominance_xfp_3yr
      WHEN 'high_value_xfp_score_3yr' THEN high_value_xfp_score_3yr
      WHEN 'qb_ngs_efficiency_score_3yr' THEN qb_ngs_efficiency_score_3yr
      WHEN 'injury_risk_score_3yr' THEN injury_risk_score_3yr
      WHEN 'injury_status_score_3yr' THEN injury_status_score_3yr
      WHEN 'injury_burden_score_3yr' THEN injury_burden_score_3yr
      WHEN 'missed_time_risk_score_3yr' THEN missed_time_risk_score_3yr
      WHEN 'availability_score_3yr' THEN availability_score_3yr
      WHEN 'depth_chart_role_score_3yr' THEN depth_chart_role_score_3yr
      WHEN 'receiving_xfp_pbp_3yr' THEN receiving_xfp_pbp_3yr
      WHEN 'rushing_xfp_pbp_3yr' THEN rushing_xfp_pbp_3yr
      WHEN 'passing_xfp_pbp_3yr' THEN passing_xfp_pbp_3yr
      WHEN 'red_zone_xfp_score_3yr' THEN red_zone_xfp_score_3yr
      WHEN 'goal_line_xfp_score_3yr' THEN goal_line_xfp_score_3yr
      WHEN 'high_value_target_xfp_score_3yr' THEN high_value_target_xfp_score_3yr
      WHEN 'high_value_rush_xfp_score_3yr' THEN high_value_rush_xfp_score_3yr
      WHEN 'receiving_xfp_share_pbp_3yr' THEN receiving_xfp_share_pbp_3yr
      WHEN 'rushing_xfp_share_pbp_3yr' THEN rushing_xfp_share_pbp_3yr
      WHEN 'opportunity_quality_score_3yr' THEN opportunity_quality_score_3yr
      WHEN 'receiving_first_down_exp_pbp_3yr' THEN receiving_first_down_exp_pbp_3yr
      WHEN 'rushing_first_down_exp_pbp_3yr' THEN rushing_first_down_exp_pbp_3yr
      WHEN 'passing_first_down_exp_pbp_3yr' THEN passing_first_down_exp_pbp_3yr
      WHEN 'high_value_first_down_opportunity_score_3yr' THEN high_value_first_down_opportunity_score_3yr
      WHEN 'receiving_chain_mover_score_3yr' THEN receiving_chain_mover_score_3yr
      WHEN 'rushing_chain_mover_score_3yr' THEN rushing_chain_mover_score_3yr
      ELSE NULL
    END AS raw_feature_value
  FROM mart
  JOIN formula_weights weights
    ON mart.position = weights.position
),
scored_features AS (
  SELECT
    *,
    CASE scoring_profile_id
      WHEN 'ppr' THEN ppr_weight
      WHEN 'half_ppr' THEN half_ppr_weight
      WHEN 'standard' THEN standard_weight
      WHEN 'gng_keeper' THEN gng_keeper_weight
      ELSE weight
    END AS effective_weight,
    CASE
      WHEN raw_feature_value IS NULL THEN NULL
      WHEN feature_name IN ('points_per_game_slope_3yr', 'total_points_slope_3yr', 'opportunity_slope_3yr', 'receiving_usage_slope_3yr', 'epa_slope_3yr', 'efficiency_slope_3yr') THEN LEAST(100.0, GREATEST(0.0, 50.0 + raw_feature_value * 10.0))
      WHEN feature_name IN ('target_share_slope_3yr', 'carry_share_slope_3yr', 'wopr_slope_3yr') THEN LEAST(100.0, GREATEST(0.0, 50.0 + raw_feature_value * 250.0))
      WHEN feature_name = 'availability_rate_3yr' THEN LEAST(100.0, GREATEST(0.0, IF(raw_feature_value <= 1, raw_feature_value * 100.0, raw_feature_value)))
      WHEN feature_name = 'weekly_volatility_3yr' THEN LEAST(100.0, GREATEST(0.0, 100.0 - raw_feature_value * 10.0))
      WHEN feature_name IN ('xfp_share_3yr', 'offensive_snap_share_3yr', 'receiving_xfp_share_pbp_3yr', 'rushing_xfp_share_pbp_3yr') THEN LEAST(100.0, GREATEST(0.0, IF(raw_feature_value <= 1, raw_feature_value * 100.0, raw_feature_value)))
      WHEN feature_name = 'fantasy_points_over_expectation_3yr' THEN LEAST(100.0, GREATEST(0.0, 50.0 + raw_feature_value * 5.0))
      WHEN feature_name IN ('injury_risk_score_3yr', 'injury_burden_score_3yr', 'missed_time_risk_score_3yr') THEN LEAST(100.0, GREATEST(0.0, 100.0 - raw_feature_value))
      WHEN feature_name IN ('improving_3yr', 'breakout_trajectory_3yr') THEN IF(raw_feature_value > 0, 100.0, 0.0)
      WHEN feature_name = 'declining_3yr' THEN IF(raw_feature_value > 0, 0.0, 100.0)
      WHEN feature_name IN ('success_rate', 'cpoe', 'snap_share_proxy') THEN LEAST(100.0, GREATEST(0.0, IF(raw_feature_value <= 1, raw_feature_value * 100.0, raw_feature_value)))
      WHEN feature_name IN ('spike_week_rate_3yr', 'bust_week_rate_3yr', 'elite_week_rate_3yr') THEN LEAST(100.0, GREATEST(0.0, IF(raw_feature_value <= 1, raw_feature_value * 100.0, raw_feature_value)))
      WHEN feature_name IN ('actual_points', 'fantasy_points_ppr', 'recent_points_avg') THEN LEAST(100.0, GREATEST(0.0, raw_feature_value / 35.0 * 100.0))
      WHEN feature_name IN ('epa_per_play', 'passing_epa_per_play', 'receiving_epa', 'team_epa_per_play') THEN LEAST(100.0, GREATEST(0.0, 50.0 + raw_feature_value * 25.0))
      WHEN feature_name = 'air_yards' AND raw_feature_value BETWEEN 0 AND 1 THEN LEAST(100.0, GREATEST(0.0, raw_feature_value * 100.0))
      WHEN feature_name IN ('air_yards', 'receiving_yards') THEN LEAST(100.0, GREATEST(0.0, raw_feature_value / 150.0 * 100.0))
      WHEN feature_name IN ('targets', 'carries', 'dropbacks', 'rushing_attempts', 'usage_volume', 'red_zone_targets', 'red_zone_carries', 'outside_red_zone_targets', 'outside_red_zone_carries', 'gemini31_rb_weighted_opportunity_ppr', 'red_zone_opportunities', 'goal_line_opportunities') THEN LEAST(100.0, GREATEST(0.0, raw_feature_value / 25.0 * 100.0))
      WHEN feature_name IN ('receiving_xfp_pbp_3yr', 'rushing_xfp_pbp_3yr', 'passing_xfp_pbp_3yr', 'high_value_target_xfp_score_3yr', 'high_value_rush_xfp_score_3yr') THEN LEAST(100.0, GREATEST(0.0, raw_feature_value / 18.0 * 100.0))
      WHEN feature_name IN ('receiving_first_down_exp_pbp_3yr', 'rushing_first_down_exp_pbp_3yr', 'passing_first_down_exp_pbp_3yr') THEN LEAST(100.0, GREATEST(0.0, raw_feature_value / 8.0 * 100.0))
      ELSE LEAST(100.0, GREATEST(0.0, raw_feature_value))
    END AS feature_score
  FROM feature_values
),
base_candidate_scores AS (
  SELECT
    candidate_id,
    formula_version,
    target_season,
    target_week,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    position,
    player_id_internal,
    ANY_VALUE(player_name) AS player_name,
    ANY_VALUE(team) AS team,
    ANY_VALUE(target_fantasy_points) AS actual_points,
    ANY_VALUE(actual_position_rank) AS actual_rank_position,
    ANY_VALUE(actual_overall_rank) AS actual_overall_rank,
    ANY_VALUE(value_over_replacement) AS value_over_replacement,
    SAFE_DIVIDE(SUM(feature_score * effective_weight), SUM(IF(feature_score IS NULL, 0, effective_weight))) AS base_predicted_score,
    SAFE_DIVIDE(SUM(IF(feature_score IS NULL, effective_weight, 0)), SUM(effective_weight)) AS missing_input_rate,
    MAX(IF(feature_name = 'snap_role_stability_3yr', feature_score, NULL)) AS snap_role_feature_score,
    MAX(IF(feature_name = 'offensive_snap_share_3yr', feature_score, NULL)) AS offensive_snap_feature_score,
    LOGICAL_OR(availability_multiplier) AS availability_multiplier
  FROM scored_features
  GROUP BY candidate_id, formula_version, target_season, target_week, scoring_profile_id, league_type_id, roster_format_id, position, player_id_internal
),
candidate_scores AS (
  SELECT
    candidate_id,
    formula_version,
    target_season,
    target_week,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    position,
    player_id_internal,
    player_name,
    team,
    actual_points,
    actual_rank_position,
    actual_overall_rank,
    value_over_replacement,
    CASE
      WHEN availability_multiplier THEN LEAST(100.0, GREATEST(0.0, base_predicted_score * (
        0.70 + 0.30 * COALESCE(SAFE_DIVIDE(snap_role_feature_score + offensive_snap_feature_score, 200.0), 0.75)
      )))
      ELSE base_predicted_score
    END AS predicted_score,
    missing_input_rate
  FROM base_candidate_scores
),
ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY candidate_id, target_season, target_week, scoring_profile_id, league_type_id, roster_format_id, position
      ORDER BY predicted_score DESC, player_id_internal
    ) AS predicted_rank_position,
    ROW_NUMBER() OVER (
      PARTITION BY candidate_id, target_season, target_week, scoring_profile_id, league_type_id, roster_format_id
      ORDER BY predicted_score DESC, player_id_internal
    ) AS predicted_overall_rank,
    CASE position WHEN 'QB' THEN 12 WHEN 'RB' THEN 24 WHEN 'WR' THEN 24 WHEN 'TE' THEN 12 ELSE 24 END AS default_top_n
  FROM candidate_scores
  WHERE predicted_score IS NOT NULL
),
with_rank_metrics AS (
  SELECT
    *,
    CASE
      WHEN predicted_rank_position BETWEEN 1 AND 12 THEN '1-12'
      WHEN predicted_rank_position BETWEEN 13 AND 24 THEN '13-24'
      WHEN predicted_rank_position BETWEEN 25 AND 36 THEN '25-36'
      WHEN predicted_rank_position BETWEEN 37 AND 60 THEN '37-60'
      WHEN predicted_rank_position BETWEEN 61 AND 100 THEN '61-100'
      ELSE '101+'
    END AS predicted_pick_band,
    CASE
      WHEN actual_rank_position BETWEEN 1 AND 12 THEN '1-12'
      WHEN actual_rank_position BETWEEN 13 AND 24 THEN '13-24'
      WHEN actual_rank_position BETWEEN 25 AND 36 THEN '25-36'
      WHEN actual_rank_position BETWEEN 37 AND 60 THEN '37-60'
      WHEN actual_rank_position BETWEEN 61 AND 100 THEN '61-100'
      ELSE '101+'
    END AS actual_position_pick_band
  FROM ranked
),
weekly_ideal AS (
  SELECT
    candidate_id,
    target_season,
    target_week,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    position,
    player_id_internal,
    ROW_NUMBER() OVER (
      PARTITION BY candidate_id, target_season, target_week, scoring_profile_id, league_type_id, roster_format_id, position
      ORDER BY actual_points DESC, player_id_internal
    ) AS ideal_rank
  FROM with_rank_metrics
),
weekly_metrics AS (
  SELECT
    scored.candidate_id,
    scored.formula_version,
    scored.target_season,
    scored.target_week,
    scored.scoring_profile_id,
    scored.league_type_id,
    scored.roster_format_id,
    scored.position,
    scored.default_top_n,
    COUNT(*) AS source_row_count,
    AVG(scored.missing_input_rate) AS missing_input_rate,
    SAFE_DIVIDE(COUNTIF(scored.predicted_rank_position <= scored.default_top_n AND scored.actual_rank_position <= scored.default_top_n), NULLIF(COUNTIF(scored.actual_rank_position <= scored.default_top_n), 0)) AS top_n_hit_rate,
    SAFE_DIVIDE(SUM(IF(scored.predicted_rank_position <= scored.default_top_n, scored.actual_points, 0)), SUM(IF(scored.actual_rank_position <= scored.default_top_n, scored.actual_points, 0))) AS actual_points_captured_rate,
    SAFE_DIVIDE(SUM(IF(scored.predicted_rank_position <= scored.default_top_n, scored.value_over_replacement, 0)), SUM(IF(scored.actual_rank_position <= scored.default_top_n, scored.value_over_replacement, 0))) AS value_over_replacement_captured_rate,
    SAFE_DIVIDE(SUM(IF(scored.predicted_rank_position <= scored.default_top_n, GREATEST(scored.actual_points, 0) / (LN(scored.predicted_rank_position + 1) / LN(2)), 0)), SUM(IF(ideal.ideal_rank <= scored.default_top_n, GREATEST(scored.actual_points, 0) / (LN(ideal.ideal_rank + 1) / LN(2)), 0))) AS ndcg_at_k,
    SAFE_DIVIDE(COUNTIF(scored.predicted_rank_position <= scored.default_top_n AND scored.actual_rank_position <= scored.default_top_n), NULLIF(COUNTIF(scored.actual_rank_position <= scored.default_top_n), 0)) AS elite_recall_at_k,
    AVG(IF(scored.predicted_pick_band = scored.actual_position_pick_band, 1.0, 0.0)) AS tier_accuracy,
    SAFE_DIVIDE(COUNTIF(scored.predicted_rank_position <= scored.default_top_n AND scored.actual_rank_position > scored.default_top_n * 2), NULLIF(COUNTIF(scored.predicted_rank_position <= scored.default_top_n), 0)) AS bust_rate,
    SUM(IF(scored.actual_rank_position <= scored.default_top_n, scored.value_over_replacement, 0)) - SUM(IF(scored.predicted_rank_position <= scored.default_top_n, scored.value_over_replacement, 0)) AS pick_band_regret
  FROM with_rank_metrics scored
  JOIN weekly_ideal ideal
    ON scored.candidate_id = ideal.candidate_id
   AND scored.target_season = ideal.target_season
   AND scored.target_week = ideal.target_week
   AND scored.scoring_profile_id = ideal.scoring_profile_id
   AND scored.league_type_id = ideal.league_type_id
   AND scored.roster_format_id = ideal.roster_format_id
   AND scored.position = ideal.position
   AND scored.player_id_internal = ideal.player_id_internal
  GROUP BY scored.candidate_id, scored.formula_version, scored.target_season, scored.target_week, scored.scoring_profile_id, scored.league_type_id, scored.roster_format_id, scored.position, scored.default_top_n
),
pairwise AS (
  SELECT
    left_side.candidate_id,
    left_side.scoring_profile_id,
    left_side.league_type_id,
    left_side.roster_format_id,
    left_side.position,
    COUNT(*) AS high_confidence_pairwise_comparison_count,
    SAFE_DIVIDE(COUNTIF(left_side.actual_points > right_side.actual_points), COUNT(*)) AS high_confidence_pairwise_win_rate
  FROM with_rank_metrics left_side
  JOIN with_rank_metrics right_side
    ON left_side.candidate_id = right_side.candidate_id
   AND left_side.target_season = right_side.target_season
   AND left_side.target_week = right_side.target_week
   AND left_side.scoring_profile_id = right_side.scoring_profile_id
   AND left_side.league_type_id = right_side.league_type_id
   AND left_side.roster_format_id = right_side.roster_format_id
   AND left_side.position = right_side.position
   AND left_side.predicted_rank_position < right_side.predicted_rank_position
   AND ABS(left_side.predicted_score - right_side.predicted_score) >= 10
  GROUP BY left_side.candidate_id, left_side.scoring_profile_id, left_side.league_type_id, left_side.roster_format_id, left_side.position
),
overall_pairwise AS (
  SELECT
    left_side.candidate_id,
    left_side.scoring_profile_id,
    left_side.league_type_id,
    left_side.roster_format_id,
    COUNT(*) AS overall_pairwise_comparison_count,
    SAFE_DIVIDE(COUNTIF(left_side.actual_overall_rank < right_side.actual_overall_rank), COUNT(*)) AS overall_pairwise_draft_win_rate
  FROM with_rank_metrics left_side
  JOIN with_rank_metrics right_side
    ON left_side.candidate_id = right_side.candidate_id
   AND left_side.target_season = right_side.target_season
   AND left_side.target_week = right_side.target_week
   AND left_side.scoring_profile_id = right_side.scoring_profile_id
   AND left_side.league_type_id = right_side.league_type_id
   AND left_side.roster_format_id = right_side.roster_format_id
   AND left_side.predicted_overall_rank < right_side.predicted_overall_rank
   AND ABS(left_side.predicted_score - right_side.predicted_score) >= 10
  WHERE (left_side.predicted_overall_rank <= 100 OR left_side.actual_overall_rank <= 100)
    AND (right_side.predicted_overall_rank <= 100 OR right_side.actual_overall_rank <= 100)
  GROUP BY left_side.candidate_id, left_side.scoring_profile_id, left_side.league_type_id, left_side.roster_format_id
),
summary AS (
  SELECT
    candidate_id,
    ANY_VALUE(formula_version) AS formula_version,
    position,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    SUM(source_row_count) AS sample_size,
    AVG(top_n_hit_rate) AS top_n_hit_rate,
    CORR(CAST(default_top_n AS FLOAT64), CAST(default_top_n AS FLOAT64)) AS stable_metric_placeholder,
    AVG(missing_input_rate) AS missing_input_rate,
    AVG(actual_points_captured_rate) AS actual_points_captured_rate,
    AVG(value_over_replacement_captured_rate) AS value_over_replacement_captured_rate,
    AVG(ndcg_at_k) AS ndcg_at_k,
    AVG(actual_points_captured_rate) AS value_captured_at_k,
    AVG(elite_recall_at_k) AS elite_recall_at_k,
    AVG(tier_accuracy) AS tier_accuracy,
    AVG(bust_rate) AS bust_rate,
    SUM(GREATEST(pick_band_regret, 0)) AS pick_band_regret
  FROM weekly_metrics
  GROUP BY candidate_id, position, scoring_profile_id, league_type_id, roster_format_id
),
rank_corr AS (
  SELECT
    candidate_id,
    position,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    CORR(CAST(predicted_rank_position AS FLOAT64), CAST(actual_rank_position AS FLOAT64)) AS rank_correlation_value
  FROM with_rank_metrics
  GROUP BY candidate_id, position, scoring_profile_id, league_type_id, roster_format_id
)
SELECT
  summary.candidate_id,
  summary.formula_version,
  summary.position,
  summary.scoring_profile_id,
  summary.league_type_id,
  summary.roster_format_id,
  'position_default_top_n' AS target_name,
  summary.sample_size,
  pairwise.high_confidence_pairwise_win_rate AS pairwise_win_rate,
  summary.top_n_hit_rate,
  rank_corr.rank_correlation_value AS rank_correlation,
  CAST(NULL AS FLOAT64) AS mean_absolute_error,
  summary.pick_band_regret AS regret_score,
  summary.actual_points_captured_rate,
  summary.missing_input_rate,
    TO_JSON_STRING(STRUCT(
    summary.ndcg_at_k AS ndcg_at_k,
    summary.value_captured_at_k AS value_captured_at_k,
    summary.elite_recall_at_k AS elite_recall_at_k,
    summary.tier_accuracy AS tier_accuracy,
    summary.bust_rate AS bust_rate,
    summary.pick_band_regret AS pick_band_regret,
    overall_pairwise.overall_pairwise_draft_win_rate AS overall_pairwise_draft_win_rate,
    pairwise.high_confidence_pairwise_win_rate AS high_confidence_pairwise_win_rate,
    summary.value_over_replacement_captured_rate AS value_over_replacement_captured_rate,
    overall_pairwise.overall_pairwise_comparison_count AS overall_pairwise_comparison_count,
    pairwise.high_confidence_pairwise_comparison_count AS high_confidence_pairwise_comparison_count,
    'metric_json' AS persistence_target
  )) AS metric_json,
  TO_JSON_STRING(STRUCT(
    summary.missing_input_rate AS missing_input_rate,
    'missing features remain null and reduce available weight' AS missing_policy
  )) AS missing_flags_json,
  TO_JSON_STRING(STRUCT(
    'ranking_backtest_feature_mart' AS source_table,
    MIN(mart.source_window_start_season) AS min_source_window_start_season,
    MAX(mart.source_window_end_season) AS max_source_window_end_season,
    'source_window_end_season < target_season' AS leakage_policy
  )) AS source_freshness_json
FROM summary
LEFT JOIN rank_corr USING (candidate_id, position, scoring_profile_id, league_type_id, roster_format_id)
LEFT JOIN pairwise USING (candidate_id, position, scoring_profile_id, league_type_id, roster_format_id)
LEFT JOIN overall_pairwise USING (candidate_id, scoring_profile_id, league_type_id, roster_format_id)
JOIN mart
  ON summary.scoring_profile_id = mart.scoring_profile_id
 AND summary.position = mart.position
 AND summary.league_type_id = mart.league_type_id
 AND summary.roster_format_id = mart.roster_format_id
GROUP BY
  summary.candidate_id,
  summary.formula_version,
  summary.position,
  summary.scoring_profile_id,
  summary.league_type_id,
  summary.roster_format_id,
  summary.sample_size,
  pairwise.high_confidence_pairwise_win_rate,
  pairwise.high_confidence_pairwise_comparison_count,
  overall_pairwise.overall_pairwise_draft_win_rate,
  overall_pairwise.overall_pairwise_comparison_count,
  summary.top_n_hit_rate,
  rank_corr.rank_correlation_value,
  summary.pick_band_regret,
  summary.actual_points_captured_rate,
  summary.missing_input_rate,
  summary.ndcg_at_k,
  summary.value_captured_at_k,
  summary.elite_recall_at_k,
  summary.tier_accuracy,
  summary.bust_rate,
  summary.value_over_replacement_captured_rate
ORDER BY scoring_profile_id, position, candidate_id
""".strip()


def _vor_policy_rows_sql(policies: Mapping[str, Mapping[str, int]]) -> str:
    rows: list[str] = []
    for policy_name, thresholds in policies.items():
        for position in POSITIONS:
            rows.append(
                "SELECT "
                f"{_sql_string(policy_name)} AS policy_name, "
                f"{_sql_string(position)} AS position, "
                f"{int(thresholds[position])} AS replacement_rank"
            )
    return "\nUNION ALL\n".join(rows)


def build_vor_baseline_sensitivity_sql(
    *,
    project_id: str,
    dataset_id: str,
    target_seasons: list[int] | tuple[int, ...] = (2024, 2025),
    scoring_profile_ids: list[str] | tuple[str, ...] = ("ppr",),
    positions: list[str] | tuple[str, ...] = POSITIONS,
    policies: Mapping[str, Mapping[str, int]] | None = None,
    league_type_id: str = DEFAULT_LEAGUE_TYPE_ID,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT_ID,
) -> str:
    mart_table = table_id(project_id, dataset_id, "ranking_backtest_feature_mart")
    selected_policies = policies or VOR_BASELINE_POLICIES
    target_season_sql = ", ".join(str(int(season)) for season in sorted({int(season) for season in target_seasons}))
    profile_sql = ", ".join(_sql_string(profile) for profile in scoring_profile_ids)
    position_sql = ", ".join(_sql_string(_normalize_position(position)) for position in positions)
    return f"""
WITH policies AS (
  {_vor_policy_rows_sql(selected_policies)}
),
mart AS (
  SELECT *
  FROM `{mart_table}`
  WHERE target_season IN ({target_season_sql})
    AND scoring_profile_id IN ({profile_sql})
    AND position IN ({position_sql})
    AND league_type_id = {_sql_string(league_type_id)}
    AND roster_format_id = {_sql_string(roster_format_id)}
    AND source_window_end_season < target_season
),
scored AS (
  SELECT
    *,
    SAFE_DIVIDE(
      COALESCE(analytical_grade_proxy, 0.0) * 0.55
      + COALESCE(opportunity_score_proxy, 0.0) * 0.15
      + COALESCE(efficiency_score_proxy, 0.0) * 0.10
      + COALESCE(role_stability_score, 0.0) * 0.10
      + COALESCE(profile_points_score, 0.0) * 0.10,
      (IF(analytical_grade_proxy IS NULL, 0.0, 0.55)
       + IF(opportunity_score_proxy IS NULL, 0.0, 0.15)
       + IF(efficiency_score_proxy IS NULL, 0.0, 0.10)
       + IF(role_stability_score IS NULL, 0.0, 0.10)
       + IF(profile_points_score IS NULL, 0.0, 0.10))
    ) AS current_pigskin_proxy_score
  FROM mart
),
ranked AS (
  SELECT
    policies.policy_name,
    policies.replacement_rank,
    scored.*,
    ROW_NUMBER() OVER (
      PARTITION BY policies.policy_name, scored.target_season, scored.target_week, scored.scoring_profile_id, scored.league_type_id, scored.roster_format_id, scored.position
      ORDER BY scored.target_fantasy_points DESC, scored.player_id_internal
    ) AS policy_actual_position_rank,
    ROW_NUMBER() OVER (
      PARTITION BY policies.policy_name, scored.target_season, scored.target_week, scored.scoring_profile_id, scored.league_type_id, scored.roster_format_id
      ORDER BY scored.current_pigskin_proxy_score DESC, scored.player_id_internal
    ) AS predicted_overall_rank
  FROM scored
  JOIN policies
    ON scored.position = policies.position
  WHERE scored.current_pigskin_proxy_score IS NOT NULL
),
with_replacement AS (
  SELECT
    *,
    MAX(IF(policy_actual_position_rank = replacement_rank, target_fantasy_points, NULL)) OVER (
      PARTITION BY policy_name, target_season, target_week, scoring_profile_id, league_type_id, roster_format_id, position
    ) AS policy_replacement_points
  FROM ranked
),
with_vor AS (
  SELECT
    *,
    GREATEST(target_fantasy_points - COALESCE(policy_replacement_points, target_fantasy_points), 0) AS policy_value_over_replacement
  FROM with_replacement
),
overall_pairwise AS (
  SELECT
    left_side.policy_name,
    left_side.scoring_profile_id,
    COUNT(*) AS overall_pairwise_comparison_count,
    SAFE_DIVIDE(COUNTIF(left_side.actual_overall_rank < right_side.actual_overall_rank), COUNT(*)) AS overall_pairwise_draft_win_rate
  FROM with_vor left_side
  JOIN with_vor right_side
    ON left_side.policy_name = right_side.policy_name
   AND left_side.target_season = right_side.target_season
   AND left_side.target_week = right_side.target_week
   AND left_side.scoring_profile_id = right_side.scoring_profile_id
   AND left_side.league_type_id = right_side.league_type_id
   AND left_side.roster_format_id = right_side.roster_format_id
   AND left_side.predicted_overall_rank < right_side.predicted_overall_rank
   AND ABS(left_side.current_pigskin_proxy_score - right_side.current_pigskin_proxy_score) >= 10
  WHERE (left_side.predicted_overall_rank <= 100 OR left_side.actual_overall_rank <= 100)
    AND (right_side.predicted_overall_rank <= 100 OR right_side.actual_overall_rank <= 100)
  GROUP BY left_side.policy_name, left_side.scoring_profile_id
),
summary AS (
  SELECT
    policy_name,
    scoring_profile_id,
    COUNT(*) AS source_row_count,
    SAFE_DIVIDE(
      SUM(IF(predicted_overall_rank <= 100, policy_value_over_replacement, 0)),
      NULLIF(SUM(IF(actual_overall_rank <= 100, policy_value_over_replacement, 0)), 0)
    ) AS value_over_replacement_captured_rate,
    SAFE_DIVIDE(COUNTIF(predicted_overall_rank <= 24 AND actual_overall_rank <= 24), NULLIF(COUNTIF(actual_overall_rank <= 24), 0)) AS top_24_overall_hit_rate,
    SAFE_DIVIDE(COUNTIF(predicted_overall_rank <= 50 AND actual_overall_rank <= 50), NULLIF(COUNTIF(actual_overall_rank <= 50), 0)) AS top_50_overall_hit_rate,
    SAFE_DIVIDE(COUNTIF(predicted_overall_rank <= 100 AND actual_overall_rank <= 100), NULLIF(COUNTIF(actual_overall_rank <= 100), 0)) AS top_100_overall_hit_rate,
    SUM(IF(actual_overall_rank <= 100, policy_value_over_replacement, 0)) - SUM(IF(predicted_overall_rank <= 100, policy_value_over_replacement, 0)) AS pick_band_regret,
    MIN(target_season) AS min_target_season,
    MAX(target_season) AS max_target_season
  FROM with_vor
  GROUP BY policy_name, scoring_profile_id
)
SELECT
  summary.policy_name,
  summary.scoring_profile_id,
  summary.source_row_count,
  summary.value_over_replacement_captured_rate,
  summary.top_24_overall_hit_rate,
  summary.top_50_overall_hit_rate,
  summary.top_100_overall_hit_rate,
  summary.pick_band_regret,
  overall_pairwise.overall_pairwise_draft_win_rate,
  overall_pairwise.overall_pairwise_comparison_count,
  summary.min_target_season,
  summary.max_target_season
FROM summary
LEFT JOIN overall_pairwise USING (policy_name, scoring_profile_id)
ORDER BY scoring_profile_id, policy_name
""".strip()


def sql_native_tournament_candidates() -> list[dict[str, Any]]:
    selected_families = (
        "_current_pigskin_candidate_score_v1_",
        "_equal_weight_normalized_blend_v0_",
        "_simple_projection_points_baseline_v0_",
        "_scarcity_adjusted_draft_value_v0_",
        "_value_over_replacement_baseline_v0_",
        "_v1_improved_mapping_",
        "_trend_balanced_v2_trend_",
    )
    return [
        row
        for row in tournament_formula_candidates()
        if any(family in str(row["candidate_id"]) for family in selected_families)
    ]


def injury_context_diagnostic_tournament_candidates() -> list[dict[str, Any]]:
    specs: list[tuple[str, str, dict[str, Any]]] = []
    for position in POSITIONS:
        position_lower = position.lower()
        specs.extend(
            [
                (
                    f"ranking_formula_{position_lower}_injury_status_only_diagnostic_v0_2026_001",
                    f"{position} Injury Status Only Diagnostic",
                    {
                        "version": "injury_status_only_diagnostic_v0",
                        "position": position,
                        "features": ["injury_status_score_3yr"],
                        "weights": {"injury_status_score_3yr": 1.0},
                        "score_expression": "weighted_linear",
                        "normalization": {"method": "position_percentile"},
                    },
                ),
                (
                    f"ranking_formula_{position_lower}_injury_burden_diagnostic_v0_2026_001",
                    f"{position} Injury Burden Diagnostic",
                    {
                        "version": "injury_burden_diagnostic_v0",
                        "position": position,
                        "features": ["profile_points_score", "injury_burden_score_3yr", "missed_time_risk_score_3yr"],
                        "weights": {
                            "profile_points_score": 0.70,
                            "injury_burden_score_3yr": 0.15,
                            "missed_time_risk_score_3yr": 0.15,
                        },
                        "score_expression": "weighted_linear",
                        "normalization": {"method": "position_percentile"},
                    },
                ),
                (
                    f"ranking_formula_{position_lower}_availability_adjusted_current_pigskin_v0_2026_001",
                    f"{position} Availability Adjusted Current Pigskin",
                    {
                        "version": "availability_adjusted_current_pigskin_v0",
                        "position": position,
                        "features": [
                            "analytical_grade_proxy",
                            "opportunity_score_proxy",
                            "efficiency_score_proxy",
                            "role_stability_score",
                            "profile_points_score",
                            "availability_score_3yr",
                        ],
                        "weights": {
                            "analytical_grade_proxy": 0.50,
                            "opportunity_score_proxy": 0.13,
                            "efficiency_score_proxy": 0.09,
                            "role_stability_score": 0.09,
                            "profile_points_score": 0.09,
                            "availability_score_3yr": 0.10,
                        },
                        "score_expression": "weighted_linear",
                        "normalization": {"method": "position_percentile"},
                    },
                ),
            ]
        )
    return [
        build_candidate_row(formula, formula_name=name, candidate_id=candidate_id, target_name="position_default_top_n")
        for candidate_id, name, formula in specs
    ]


def opportunity_diagnostic_tournament_candidates() -> list[dict[str, Any]]:
    specs = [
        (
            "ranking_formula_qb_opportunity_diagnostic_v0_2026_001",
            "QB Opportunity Diagnostic",
            {
                "version": "qb_opportunity_diagnostic_v0",
                "position": "QB",
                "features": [
                    "profile_points_score",
                    "qb_rushing_leverage_index",
                    "team_environment_score",
                    "spike_week_rate_3yr",
                ],
                "weights": {
                    "profile_points_score": 0.40,
                    "qb_rushing_leverage_index": 0.30,
                    "team_environment_score": 0.20,
                    "spike_week_rate_3yr": 0.10,
                },
                "score_expression": "weighted_linear",
                "normalization": {"method": "position_percentile"},
            },
        ),
        (
            "ranking_formula_rb_opportunity_diagnostic_v0_2026_001",
            "RB Opportunity Diagnostic",
            {
                "version": "rb_opportunity_diagnostic_v0",
                "position": "RB",
                "features": [
                    "profile_points_score",
                    "rb_high_value_opportunity_score",
                    "goal_line_usage_score",
                    "team_environment_score",
                ],
                "weights": {
                    "profile_points_score": 0.35,
                    "rb_high_value_opportunity_score": 0.35,
                    "goal_line_usage_score": 0.20,
                    "team_environment_score": 0.10,
                },
                "score_expression": "weighted_linear",
                "normalization": {"method": "position_percentile"},
            },
        ),
        (
            "ranking_formula_wr_opportunity_diagnostic_v0_2026_001",
            "WR Opportunity Diagnostic",
            {
                "version": "wr_opportunity_diagnostic_v0",
                "position": "WR",
                "features": [
                    "profile_points_score",
                    "receiving_role_dominance_score",
                    "red_zone_usage_score",
                    "team_environment_score",
                ],
                "weights": {
                    "profile_points_score": 0.35,
                    "receiving_role_dominance_score": 0.35,
                    "red_zone_usage_score": 0.15,
                    "team_environment_score": 0.15,
                },
                "score_expression": "weighted_linear",
                "normalization": {"method": "position_percentile"},
            },
        ),
        (
            "ranking_formula_te_opportunity_diagnostic_v0_2026_001",
            "TE Opportunity Diagnostic",
            {
                "version": "te_opportunity_diagnostic_v0",
                "position": "TE",
                "features": [
                    "profile_points_score",
                    "receiving_role_dominance_score",
                    "red_zone_usage_score",
                    "spike_week_rate_3yr",
                ],
                "weights": {
                    "profile_points_score": 0.35,
                    "receiving_role_dominance_score": 0.35,
                    "red_zone_usage_score": 0.20,
                    "spike_week_rate_3yr": 0.10,
                },
                "score_expression": "weighted_linear",
                "normalization": {"method": "position_percentile"},
            },
        ),
    ]
    return [
        build_candidate_row(formula, formula_name=name, candidate_id=candidate_id, target_name="position_default_top_n")
        for candidate_id, name, formula in specs
    ]


def ideal_stats_diagnostic_tournament_candidates() -> list[dict[str, Any]]:
    specs = [
        (
            "ranking_formula_qb_ideal_stats_diagnostic_v0_2026_001",
            "QB Ideal Stats Diagnostic",
            {
                "version": "qb_ideal_stats_diagnostic_v0",
                "position": "QB",
                "features": ["profile_points_score", "xfp_score_3yr", "qb_ngs_efficiency_score_3yr", "snap_role_stability_3yr"],
                "weights": {
                    "profile_points_score": 0.35,
                    "xfp_score_3yr": 0.30,
                    "qb_ngs_efficiency_score_3yr": 0.20,
                    "snap_role_stability_3yr": 0.15,
                },
                "score_expression": "weighted_linear",
                "normalization": {"method": "position_percentile"},
            },
        ),
        (
            "ranking_formula_rb_ideal_stats_diagnostic_v0_2026_001",
            "RB Ideal Stats Diagnostic",
            {
                "version": "rb_ideal_stats_diagnostic_v0",
                "position": "RB",
                "features": ["profile_points_score", "high_value_xfp_score_3yr", "offensive_snap_share_3yr", "snap_role_stability_3yr"],
                "weights": {
                    "profile_points_score": 0.30,
                    "high_value_xfp_score_3yr": 0.35,
                    "offensive_snap_share_3yr": 0.20,
                    "snap_role_stability_3yr": 0.15,
                },
                "score_expression": "weighted_linear",
                "normalization": {"method": "position_percentile"},
            },
        ),
        (
            "ranking_formula_wr_ideal_stats_diagnostic_v0_2026_001",
            "WR Ideal Stats Diagnostic",
            {
                "version": "wr_ideal_stats_diagnostic_v0",
                "position": "WR",
                "features": ["profile_points_score", "xfp_share_3yr", "receiving_role_dominance_xfp_3yr", "fantasy_points_over_expectation_3yr"],
                "weights": {
                    "profile_points_score": 0.30,
                    "xfp_share_3yr": 0.25,
                    "receiving_role_dominance_xfp_3yr": 0.30,
                    "fantasy_points_over_expectation_3yr": 0.15,
                },
                "score_expression": "weighted_linear",
                "normalization": {"method": "position_percentile"},
            },
        ),
        (
            "ranking_formula_te_ideal_stats_diagnostic_v0_2026_001",
            "TE Ideal Stats Diagnostic",
            {
                "version": "te_ideal_stats_diagnostic_v0",
                "position": "TE",
                "features": ["profile_points_score", "xfp_share_3yr", "receiving_role_dominance_xfp_3yr", "offensive_snap_share_3yr"],
                "weights": {
                    "profile_points_score": 0.30,
                    "xfp_share_3yr": 0.25,
                    "receiving_role_dominance_xfp_3yr": 0.30,
                    "offensive_snap_share_3yr": 0.15,
                },
                "score_expression": "weighted_linear",
                "normalization": {"method": "position_percentile"},
            },
        ),
    ]
    return [
        build_candidate_row(formula, formula_name=name, candidate_id=candidate_id, target_name="position_default_top_n")
        for candidate_id, name, formula in specs
    ]


def stats02_ideal_tournament_candidates() -> list[dict[str, Any]]:
    def formula(
        *,
        position: str,
        version: str,
        features: list[str],
        weights: dict[str, float],
        profile_weights: dict[str, dict[str, float]] | None = None,
        availability_multiplier: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "version": version,
            "position": position,
            "features": features,
            "weights": weights,
            "score_expression": "weighted_linear",
            "normalization": {"method": "bounded_0_100_sql"},
            "source_flags": {
                "uses_phase_32_13_ideal_stats": True,
                "availability_multiplier": availability_multiplier,
                "injury_depth_scores_deferred": True,
                "pbp_ffopportunity_deferred": True,
                "no_2025_holdout_weight_tuning": True,
            },
        }
        if profile_weights:
            payload["scoring_profile_weights"] = profile_weights
        return payload

    qb_features = [
        "qb_rushing_leverage_index",
        "xfp_score_3yr",
        "xfp_share_3yr",
        "qb_ngs_efficiency_score_3yr",
        "team_environment_score",
        "snap_role_stability_3yr",
        "offensive_snap_share_3yr",
    ]
    rb_features = [
        "high_value_xfp_score_3yr",
        "xfp_score_3yr",
        "xfp_share_3yr",
        "rb_high_value_opportunity_score",
        "red_zone_usage_score",
        "goal_line_usage_score",
        "offensive_snap_share_3yr",
        "snap_role_stability_3yr",
        "team_environment_score",
    ]
    wr_features = [
        "receiving_role_dominance_xfp_3yr",
        "receiving_role_dominance_score",
        "xfp_score_3yr",
        "xfp_share_3yr",
        "fantasy_points_over_expectation_3yr",
        "red_zone_usage_score",
        "offensive_snap_share_3yr",
        "snap_role_stability_3yr",
        "team_environment_score",
    ]
    te_features = [
        "receiving_role_dominance_xfp_3yr",
        "receiving_role_dominance_score",
        "xfp_score_3yr",
        "xfp_share_3yr",
        "red_zone_usage_score",
        "offensive_snap_share_3yr",
        "snap_role_stability_3yr",
        "team_environment_score",
    ]
    specs = [
        (
            "stats02_qb_ideal_rushing_xfp_v0",
            "Stats02 QB Ideal Rushing XFP",
            formula(
                position="QB",
                version="stats02_ideal_v0",
                features=qb_features,
                weights={
                    "qb_rushing_leverage_index": 0.20,
                    "xfp_score_3yr": 0.22,
                    "xfp_share_3yr": 0.14,
                    "qb_ngs_efficiency_score_3yr": 0.16,
                    "team_environment_score": 0.10,
                    "snap_role_stability_3yr": 0.10,
                    "offensive_snap_share_3yr": 0.08,
                },
            ),
        ),
        (
            "stats02_rb_ideal_high_value_xfp_v0",
            "Stats02 RB Ideal High Value XFP",
            formula(
                position="RB",
                version="stats02_ideal_v0",
                features=rb_features,
                weights={
                    "high_value_xfp_score_3yr": 0.24,
                    "xfp_score_3yr": 0.18,
                    "xfp_share_3yr": 0.14,
                    "rb_high_value_opportunity_score": 0.12,
                    "red_zone_usage_score": 0.08,
                    "goal_line_usage_score": 0.08,
                    "offensive_snap_share_3yr": 0.07,
                    "snap_role_stability_3yr": 0.05,
                    "team_environment_score": 0.04,
                },
                profile_weights={
                    "standard": {"goal_line_usage_score": 0.13, "red_zone_usage_score": 0.12, "team_environment_score": 0.08, "xfp_share_3yr": 0.08},
                    "half_ppr": {"high_value_xfp_score_3yr": 0.25, "xfp_share_3yr": 0.14},
                    "ppr": {"xfp_share_3yr": 0.18, "high_value_xfp_score_3yr": 0.26, "goal_line_usage_score": 0.05},
                    "gng_keeper": {"xfp_share_3yr": 0.18, "high_value_xfp_score_3yr": 0.24, "snap_role_stability_3yr": 0.08},
                },
            ),
        ),
        (
            "stats02_wr_ideal_receiving_dominance_v0",
            "Stats02 WR Ideal Receiving Dominance",
            formula(
                position="WR",
                version="stats02_ideal_v0",
                features=wr_features,
                weights={
                    "receiving_role_dominance_xfp_3yr": 0.22,
                    "receiving_role_dominance_score": 0.14,
                    "xfp_score_3yr": 0.16,
                    "xfp_share_3yr": 0.16,
                    "fantasy_points_over_expectation_3yr": 0.08,
                    "red_zone_usage_score": 0.08,
                    "offensive_snap_share_3yr": 0.06,
                    "snap_role_stability_3yr": 0.05,
                    "team_environment_score": 0.05,
                },
                profile_weights={
                    "standard": {"red_zone_usage_score": 0.12, "team_environment_score": 0.08, "fantasy_points_over_expectation_3yr": 0.10, "xfp_share_3yr": 0.10},
                    "half_ppr": {"receiving_role_dominance_xfp_3yr": 0.23, "xfp_share_3yr": 0.15},
                    "ppr": {"receiving_role_dominance_xfp_3yr": 0.25, "xfp_share_3yr": 0.19, "red_zone_usage_score": 0.05},
                    "gng_keeper": {"receiving_role_dominance_xfp_3yr": 0.24, "xfp_share_3yr": 0.18, "snap_role_stability_3yr": 0.08},
                },
            ),
        ),
        (
            "stats02_te_ideal_receiving_role_v0",
            "Stats02 TE Ideal Receiving Role",
            formula(
                position="TE",
                version="stats02_ideal_v0",
                features=te_features,
                weights={
                    "receiving_role_dominance_xfp_3yr": 0.25,
                    "receiving_role_dominance_score": 0.16,
                    "xfp_score_3yr": 0.15,
                    "xfp_share_3yr": 0.15,
                    "red_zone_usage_score": 0.08,
                    "offensive_snap_share_3yr": 0.08,
                    "snap_role_stability_3yr": 0.08,
                    "team_environment_score": 0.05,
                },
                profile_weights={
                    "standard": {"red_zone_usage_score": 0.13, "team_environment_score": 0.08, "xfp_share_3yr": 0.11},
                    "half_ppr": {"receiving_role_dominance_xfp_3yr": 0.25, "xfp_share_3yr": 0.15},
                    "ppr": {"receiving_role_dominance_xfp_3yr": 0.28, "xfp_share_3yr": 0.18, "red_zone_usage_score": 0.05},
                    "gng_keeper": {"receiving_role_dominance_xfp_3yr": 0.27, "xfp_share_3yr": 0.17, "snap_role_stability_3yr": 0.10},
                },
            ),
        ),
    ]

    position_specific = {
        "QB": specs[0][2],
        "RB": specs[1][2],
        "WR": specs[2][2],
        "TE": specs[3][2],
    }
    rows = [
        build_candidate_row(payload, formula_name=name, candidate_id=candidate_id, target_name="position_default_top_n")
        for candidate_id, name, payload in specs
    ]
    for position, payload in position_specific.items():
        rows.append(
            build_candidate_row(
                payload,
                formula_name=f"Stats02 {position} Position Specific Ideal",
                candidate_id="stats02_position_specific_ideal_v0",
                target_name="position_default_top_n",
            )
        )
        multiplier_payload = dict(payload)
        multiplier_payload["source_flags"] = dict(multiplier_payload.get("source_flags", {}), availability_multiplier=True)
        multiplier_payload["version"] = "stats02_ideal_availability_multiplier_v0"
        rows.append(
            build_candidate_row(
                multiplier_payload,
                formula_name=f"Stats02 {position} Position Specific Ideal Availability Multiplier",
                candidate_id="stats02_position_specific_ideal_availability_multiplier_v0",
                target_name="position_default_top_n",
            )
        )
    return rows


def pbp_xfp_diagnostic_tournament_candidates() -> list[dict[str, Any]]:
    def formula(
        *,
        position: str,
        version: str,
        features: list[str],
        weights: dict[str, float],
        profile_weights: dict[str, dict[str, float]] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "version": version,
            "position": position,
            "features": features,
            "weights": weights,
            "score_expression": "weighted_linear",
            "normalization": {"method": "bounded_0_100_sql"},
            "source_flags": {
                "uses_phase_32_15_pbp_ffopportunity": True,
                "pbp_xfp_is_component_proxy": True,
                "no_2025_holdout_weight_tuning": True,
                "no_champion_activation": True,
            },
        }
        if profile_weights:
            payload["scoring_profile_weights"] = profile_weights
        return payload

    specs = [
        (
            "pbp_xfp_qb_pass_rush_v0",
            "PBP XFP QB Pass Rush Diagnostic",
            formula(
                position="QB",
                version="pbp_xfp_diagnostic_v0",
                features=["profile_points_score", "passing_xfp_pbp_3yr", "rushing_xfp_pbp_3yr", "opportunity_quality_score_3yr"],
                weights={
                    "profile_points_score": 0.35,
                    "passing_xfp_pbp_3yr": 0.30,
                    "rushing_xfp_pbp_3yr": 0.20,
                    "opportunity_quality_score_3yr": 0.15,
                },
            ),
        ),
        (
            "pbp_xfp_rb_high_value_rush_recv_v0",
            "PBP XFP RB High Value Rush Receive Diagnostic",
            formula(
                position="RB",
                version="pbp_xfp_diagnostic_v0",
                features=[
                    "profile_points_score",
                    "rushing_xfp_pbp_3yr",
                    "receiving_xfp_pbp_3yr",
                    "high_value_rush_xfp_score_3yr",
                    "high_value_target_xfp_score_3yr",
                    "goal_line_xfp_score_3yr",
                ],
                weights={
                    "profile_points_score": 0.28,
                    "rushing_xfp_pbp_3yr": 0.22,
                    "receiving_xfp_pbp_3yr": 0.14,
                    "high_value_rush_xfp_score_3yr": 0.16,
                    "high_value_target_xfp_score_3yr": 0.10,
                    "goal_line_xfp_score_3yr": 0.10,
                },
                profile_weights={
                    "standard": {"goal_line_xfp_score_3yr": 0.16, "receiving_xfp_pbp_3yr": 0.08},
                    "ppr": {"receiving_xfp_pbp_3yr": 0.18, "high_value_target_xfp_score_3yr": 0.12},
                    "half_ppr": {"receiving_xfp_pbp_3yr": 0.15},
                    "gng_keeper": {"receiving_xfp_pbp_3yr": 0.16, "opportunity_quality_score_3yr": 0.10},
                },
            ),
        ),
        (
            "pbp_xfp_wr_high_value_receiving_v0",
            "PBP XFP WR High Value Receiving Diagnostic",
            formula(
                position="WR",
                version="pbp_xfp_diagnostic_v0",
                features=[
                    "profile_points_score",
                    "receiving_xfp_pbp_3yr",
                    "receiving_xfp_share_pbp_3yr",
                    "high_value_target_xfp_score_3yr",
                    "red_zone_xfp_score_3yr",
                    "opportunity_quality_score_3yr",
                ],
                weights={
                    "profile_points_score": 0.30,
                    "receiving_xfp_pbp_3yr": 0.22,
                    "receiving_xfp_share_pbp_3yr": 0.18,
                    "high_value_target_xfp_score_3yr": 0.14,
                    "red_zone_xfp_score_3yr": 0.08,
                    "opportunity_quality_score_3yr": 0.08,
                },
                profile_weights={
                    "standard": {"red_zone_xfp_score_3yr": 0.12, "receiving_xfp_share_pbp_3yr": 0.14},
                    "ppr": {"receiving_xfp_share_pbp_3yr": 0.21, "receiving_xfp_pbp_3yr": 0.24},
                    "half_ppr": {"receiving_xfp_pbp_3yr": 0.23},
                    "gng_keeper": {"receiving_xfp_share_pbp_3yr": 0.20},
                },
            ),
        ),
        (
            "pbp_xfp_te_receiving_role_v0",
            "PBP XFP TE Receiving Role Diagnostic",
            formula(
                position="TE",
                version="pbp_xfp_diagnostic_v0",
                features=[
                    "profile_points_score",
                    "receiving_xfp_pbp_3yr",
                    "receiving_xfp_share_pbp_3yr",
                    "high_value_target_xfp_score_3yr",
                    "red_zone_xfp_score_3yr",
                    "goal_line_xfp_score_3yr",
                ],
                weights={
                    "profile_points_score": 0.28,
                    "receiving_xfp_pbp_3yr": 0.24,
                    "receiving_xfp_share_pbp_3yr": 0.18,
                    "high_value_target_xfp_score_3yr": 0.12,
                    "red_zone_xfp_score_3yr": 0.10,
                    "goal_line_xfp_score_3yr": 0.08,
                },
                profile_weights={
                    "standard": {"red_zone_xfp_score_3yr": 0.14, "goal_line_xfp_score_3yr": 0.12},
                    "ppr": {"receiving_xfp_share_pbp_3yr": 0.21, "receiving_xfp_pbp_3yr": 0.26},
                    "half_ppr": {"receiving_xfp_pbp_3yr": 0.25},
                    "gng_keeper": {"receiving_xfp_share_pbp_3yr": 0.20},
                },
            ),
        ),
    ]
    return [
        build_candidate_row(payload, formula_name=name, candidate_id=candidate_id, target_name="position_default_top_n")
        for candidate_id, name, payload in specs
    ]


def role_context_and_vor_sensitivity_tournament_candidates() -> list[dict[str, Any]]:
    def formula(
        *,
        position: str,
        version: str,
        features: list[str],
        weights: dict[str, float],
        source_flags: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "version": version,
            "position": position,
            "features": features,
            "weights": weights,
            "score_expression": "weighted_linear",
            "normalization": {"method": "bounded_0_100_sql"},
            "source_flags": {
                "uses_phase_32_18_role_context_vor_firstdown": True,
                "no_2025_holdout_weight_tuning": True,
                "no_champion_activation": True,
                **source_flags,
            },
        }

    specs = [
        (
            "injury_depth_role_diagnostic_v0",
            "Injury Depth Role Diagnostic",
            formula(
                position="RB",
                version="role_context_vor_firstdown_v0",
                features=["profile_points_score", "injury_risk_score_3yr", "depth_chart_role_score_3yr"],
                weights={"profile_points_score": 0.50, "injury_risk_score_3yr": 0.25, "depth_chart_role_score_3yr": 0.25},
                source_flags={
                    "injury_depth_sources_empty": True,
                    "diagnostic_expected_missing_inputs": True,
                    "missing_role_context_must_reduce_available_weight": True,
                },
            ),
        ),
        (
            "first_down_pbp_proxy_diagnostic_v0",
            "First Down PBP Proxy Diagnostic",
            formula(
                position="WR",
                version="role_context_vor_firstdown_v0",
                features=[
                    "profile_points_score",
                    "receiving_first_down_exp_pbp_3yr",
                    "receiving_chain_mover_score_3yr",
                    "high_value_first_down_opportunity_score_3yr",
                ],
                weights={
                    "profile_points_score": 0.42,
                    "receiving_first_down_exp_pbp_3yr": 0.22,
                    "receiving_chain_mover_score_3yr": 0.20,
                    "high_value_first_down_opportunity_score_3yr": 0.16,
                },
                source_flags={
                    "first_down_fields_are_pbp_proxies": True,
                    "not_route_based": True,
                },
            ),
        ),
        (
            "gemini31_rb_weighted_opportunity_ppr_v0",
            "Gemini 3.1 RB Weighted Opportunity PPR",
            formula(
                position="RB",
                version="role_context_vor_firstdown_v0",
                features=[
                    "profile_points_score",
                    "outside_red_zone_carries",
                    "red_zone_carries",
                    "outside_red_zone_targets",
                    "red_zone_targets",
                    "gemini31_rb_weighted_opportunity_ppr",
                ],
                weights={
                    "profile_points_score": 0.10,
                    "outside_red_zone_carries": 0.047,
                    "red_zone_carries": 0.128,
                    "outside_red_zone_targets": 0.154,
                    "red_zone_targets": 0.239,
                    "gemini31_rb_weighted_opportunity_ppr": 0.322,
                },
                source_flags={
                    "gemini31_report_hypothesis": True,
                    "ppr_only_diagnostic": True,
                    "outside_red_zone_carry_multiplier": 0.47,
                    "red_zone_carry_multiplier": 1.28,
                    "outside_red_zone_target_multiplier": 1.54,
                    "red_zone_target_multiplier": 2.39,
                    "red_zone_definition": "yardline_100 <= 20",
                    "does_not_apply_to_standard_half_ppr_or_gng_keeper": True,
                    "no_2025_holdout_weight_tuning": True,
                },
            ),
        ),
        (
            "rb_role_pbp_context_blend_v0",
            "RB Role PBP Context Blend",
            formula(
                position="RB",
                version="role_context_vor_firstdown_v0",
                features=[
                    "profile_points_score",
                    "rushing_xfp_pbp_3yr",
                    "rushing_first_down_exp_pbp_3yr",
                    "rushing_chain_mover_score_3yr",
                    "high_value_rush_xfp_score_3yr",
                    "injury_risk_score_3yr",
                    "depth_chart_role_score_3yr",
                ],
                weights={
                    "profile_points_score": 0.28,
                    "rushing_xfp_pbp_3yr": 0.20,
                    "rushing_first_down_exp_pbp_3yr": 0.16,
                    "rushing_chain_mover_score_3yr": 0.12,
                    "high_value_rush_xfp_score_3yr": 0.12,
                    "injury_risk_score_3yr": 0.06,
                    "depth_chart_role_score_3yr": 0.06,
                },
                source_flags={
                    "first_down_fields_are_pbp_proxies": True,
                    "role_context_optional_until_sources_populate": True,
                },
            ),
        ),
        (
            "wr_chain_mover_context_blend_v0",
            "WR Chain Mover Context Blend",
            formula(
                position="WR",
                version="role_context_vor_firstdown_v0",
                features=[
                    "profile_points_score",
                    "receiving_role_dominance_xfp_3yr",
                    "receiving_xfp_pbp_3yr",
                    "receiving_first_down_exp_pbp_3yr",
                    "receiving_chain_mover_score_3yr",
                    "high_value_target_xfp_score_3yr",
                    "depth_chart_role_score_3yr",
                ],
                weights={
                    "profile_points_score": 0.26,
                    "receiving_role_dominance_xfp_3yr": 0.18,
                    "receiving_xfp_pbp_3yr": 0.16,
                    "receiving_first_down_exp_pbp_3yr": 0.14,
                    "receiving_chain_mover_score_3yr": 0.12,
                    "high_value_target_xfp_score_3yr": 0.08,
                    "depth_chart_role_score_3yr": 0.06,
                },
                source_flags={
                    "first_down_fields_are_pbp_proxies": True,
                    "role_context_optional_until_sources_populate": True,
                },
            ),
        ),
        (
            "deep_vorp_qb15_rb36_wr55_te12_diagnostic_v0",
            "Deep VOR Baseline Sensitivity",
            formula(
                position="QB",
                version="role_context_vor_firstdown_v0",
                features=[
                    "profile_points_score",
                    "analytical_grade_proxy",
                    "opportunity_score_proxy",
                    "efficiency_score_proxy",
                    "role_stability_score",
                ],
                weights={
                    "profile_points_score": 0.10,
                    "analytical_grade_proxy": 0.55,
                    "opportunity_score_proxy": 0.15,
                    "efficiency_score_proxy": 0.10,
                    "role_stability_score": 0.10,
                },
                source_flags={
                    "evaluated_by_vor_baseline_sensitivity_sql": True,
                    "deep_vorp_policy": "deep_vorp_qb15_rb36_wr55_te12",
                    "does_not_change_stored_vor_semantics": True,
                },
            ),
        ),
    ]
    return [
        build_candidate_row(formula_payload, formula_name=name, candidate_id=candidate_id, target_name="position_default_top_n")
        for candidate_id, name, formula_payload in specs
    ]


def stats02_pbp_refined_tournament_candidates() -> list[dict[str, Any]]:
    def formula(
        *,
        position: str,
        features: list[str],
        weights: dict[str, float],
        profile_weights: dict[str, dict[str, float]] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "version": "stats02_pbp_refined_v0",
            "position": position,
            "features": features,
            "weights": weights,
            "score_expression": "weighted_linear",
            "normalization": {"method": "bounded_0_100_sql"},
            "source_flags": {
                "uses_phase_32_13_ideal_stats": True,
                "uses_phase_32_15_pbp_ffopportunity": True,
                "pbp_xfp_is_component_proxy": True,
                "injury_depth_scores_deferred": True,
                "no_2025_holdout_weight_tuning": True,
                "no_champion_activation": True,
            },
        }
        if profile_weights:
            payload["scoring_profile_weights"] = profile_weights
        return payload

    specs = [
        (
            "stats02_rb_pbp_high_value_blend_v0",
            "Stats02 RB PBP High Value Blend",
            formula(
                position="RB",
                features=[
                    "xfp_score_3yr",
                    "high_value_xfp_score_3yr",
                    "rushing_xfp_pbp_3yr",
                    "receiving_xfp_pbp_3yr",
                    "high_value_rush_xfp_score_3yr",
                    "high_value_target_xfp_score_3yr",
                    "red_zone_xfp_score_3yr",
                    "goal_line_xfp_score_3yr",
                    "offensive_snap_share_3yr",
                    "snap_role_stability_3yr",
                    "team_environment_score",
                    "rb_high_value_opportunity_score",
                ],
                weights={
                    "xfp_score_3yr": 0.13,
                    "high_value_xfp_score_3yr": 0.15,
                    "rushing_xfp_pbp_3yr": 0.13,
                    "receiving_xfp_pbp_3yr": 0.08,
                    "high_value_rush_xfp_score_3yr": 0.11,
                    "high_value_target_xfp_score_3yr": 0.05,
                    "red_zone_xfp_score_3yr": 0.08,
                    "goal_line_xfp_score_3yr": 0.10,
                    "offensive_snap_share_3yr": 0.06,
                    "snap_role_stability_3yr": 0.04,
                    "team_environment_score": 0.03,
                    "rb_high_value_opportunity_score": 0.04,
                },
                profile_weights={
                    "standard": {
                        "rushing_xfp_pbp_3yr": 0.15,
                        "goal_line_xfp_score_3yr": 0.14,
                        "red_zone_xfp_score_3yr": 0.10,
                        "receiving_xfp_pbp_3yr": 0.04,
                    },
                    "half_ppr": {"receiving_xfp_pbp_3yr": 0.09, "high_value_target_xfp_score_3yr": 0.06},
                    "ppr": {"receiving_xfp_pbp_3yr": 0.11, "high_value_target_xfp_score_3yr": 0.08},
                    "gng_keeper": {"receiving_xfp_pbp_3yr": 0.10, "snap_role_stability_3yr": 0.06},
                },
            ),
        ),
        (
            "stats02_rb_pbp_receiving_weighted_v0",
            "Stats02 RB PBP Receiving Weighted",
            formula(
                position="RB",
                features=[
                    "xfp_share_3yr",
                    "high_value_xfp_score_3yr",
                    "receiving_xfp_pbp_3yr",
                    "receiving_xfp_share_pbp_3yr",
                    "high_value_target_xfp_score_3yr",
                    "rushing_xfp_pbp_3yr",
                    "high_value_rush_xfp_score_3yr",
                    "goal_line_xfp_score_3yr",
                    "offensive_snap_share_3yr",
                    "team_environment_score",
                ],
                weights={
                    "xfp_share_3yr": 0.14,
                    "high_value_xfp_score_3yr": 0.14,
                    "receiving_xfp_pbp_3yr": 0.14,
                    "receiving_xfp_share_pbp_3yr": 0.10,
                    "high_value_target_xfp_score_3yr": 0.10,
                    "rushing_xfp_pbp_3yr": 0.12,
                    "high_value_rush_xfp_score_3yr": 0.08,
                    "goal_line_xfp_score_3yr": 0.08,
                    "offensive_snap_share_3yr": 0.06,
                    "team_environment_score": 0.04,
                },
                profile_weights={
                    "standard": {
                        "receiving_xfp_pbp_3yr": 0.08,
                        "receiving_xfp_share_pbp_3yr": 0.06,
                        "rushing_xfp_pbp_3yr": 0.15,
                        "goal_line_xfp_score_3yr": 0.12,
                    },
                    "half_ppr": {"receiving_xfp_pbp_3yr": 0.15, "receiving_xfp_share_pbp_3yr": 0.11},
                    "ppr": {"receiving_xfp_pbp_3yr": 0.18, "receiving_xfp_share_pbp_3yr": 0.14, "high_value_target_xfp_score_3yr": 0.12},
                    "gng_keeper": {"receiving_xfp_pbp_3yr": 0.17, "receiving_xfp_share_pbp_3yr": 0.13, "offensive_snap_share_3yr": 0.08},
                },
            ),
        ),
        (
            "stats02_wr_pbp_receiving_dominance_blend_v0",
            "Stats02 WR PBP Receiving Dominance Blend",
            formula(
                position="WR",
                features=[
                    "receiving_role_dominance_xfp_3yr",
                    "receiving_role_dominance_score",
                    "xfp_score_3yr",
                    "xfp_share_3yr",
                    "receiving_xfp_pbp_3yr",
                    "receiving_xfp_share_pbp_3yr",
                    "high_value_target_xfp_score_3yr",
                    "red_zone_xfp_score_3yr",
                    "offensive_snap_share_3yr",
                    "snap_role_stability_3yr",
                    "team_environment_score",
                ],
                weights={
                    "receiving_role_dominance_xfp_3yr": 0.16,
                    "receiving_role_dominance_score": 0.09,
                    "xfp_score_3yr": 0.10,
                    "xfp_share_3yr": 0.12,
                    "receiving_xfp_pbp_3yr": 0.14,
                    "receiving_xfp_share_pbp_3yr": 0.14,
                    "high_value_target_xfp_score_3yr": 0.10,
                    "red_zone_xfp_score_3yr": 0.05,
                    "offensive_snap_share_3yr": 0.04,
                    "snap_role_stability_3yr": 0.03,
                    "team_environment_score": 0.03,
                },
                profile_weights={
                    "standard": {
                        "red_zone_xfp_score_3yr": 0.08,
                        "team_environment_score": 0.05,
                        "receiving_xfp_share_pbp_3yr": 0.10,
                    },
                    "half_ppr": {"receiving_xfp_pbp_3yr": 0.15, "receiving_xfp_share_pbp_3yr": 0.14},
                    "ppr": {"receiving_xfp_pbp_3yr": 0.16, "receiving_xfp_share_pbp_3yr": 0.16, "high_value_target_xfp_score_3yr": 0.11},
                    "gng_keeper": {"receiving_xfp_share_pbp_3yr": 0.16, "snap_role_stability_3yr": 0.05},
                },
            ),
        ),
        (
            "stats02_wr_pbp_scoring_profile_blend_v0",
            "Stats02 WR PBP Scoring Profile Blend",
            formula(
                position="WR",
                features=[
                    "receiving_role_dominance_xfp_3yr",
                    "receiving_role_dominance_score",
                    "xfp_share_3yr",
                    "fantasy_points_over_expectation_3yr",
                    "receiving_xfp_pbp_3yr",
                    "receiving_xfp_share_pbp_3yr",
                    "high_value_target_xfp_score_3yr",
                    "red_zone_xfp_score_3yr",
                    "goal_line_xfp_score_3yr",
                    "team_environment_score",
                    "snap_role_stability_3yr",
                ],
                weights={
                    "receiving_role_dominance_xfp_3yr": 0.15,
                    "receiving_role_dominance_score": 0.08,
                    "xfp_share_3yr": 0.13,
                    "fantasy_points_over_expectation_3yr": 0.07,
                    "receiving_xfp_pbp_3yr": 0.14,
                    "receiving_xfp_share_pbp_3yr": 0.13,
                    "high_value_target_xfp_score_3yr": 0.11,
                    "red_zone_xfp_score_3yr": 0.07,
                    "goal_line_xfp_score_3yr": 0.04,
                    "team_environment_score": 0.04,
                    "snap_role_stability_3yr": 0.04,
                },
                profile_weights={
                    "standard": {
                        "fantasy_points_over_expectation_3yr": 0.10,
                        "red_zone_xfp_score_3yr": 0.10,
                        "goal_line_xfp_score_3yr": 0.07,
                        "team_environment_score": 0.06,
                        "receiving_xfp_share_pbp_3yr": 0.09,
                    },
                    "half_ppr": {"receiving_xfp_pbp_3yr": 0.15, "receiving_xfp_share_pbp_3yr": 0.13},
                    "ppr": {
                        "receiving_role_dominance_xfp_3yr": 0.17,
                        "xfp_share_3yr": 0.15,
                        "receiving_xfp_share_pbp_3yr": 0.16,
                        "high_value_target_xfp_score_3yr": 0.12,
                    },
                    "gng_keeper": {"receiving_role_dominance_xfp_3yr": 0.16, "xfp_share_3yr": 0.15, "snap_role_stability_3yr": 0.06},
                },
            ),
        ),
    ]
    return [
        build_candidate_row(payload, formula_name=name, candidate_id=candidate_id, target_name="position_default_top_n")
        for candidate_id, name, payload in specs
    ]


def estimate_sql_native_tournament(
    *,
    client: Any,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    target_seasons: list[int] | tuple[int, ...] = tuple(range(2017, 2026)),
    scoring_profile_ids: list[str] | tuple[str, ...] = DEFAULT_SCORING_PROFILES,
    positions: list[str] | tuple[str, ...] = POSITIONS,
) -> dict[str, Any]:
    from google.cloud import bigquery

    sql = build_sql_native_tournament_summary_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        target_seasons=target_seasons,
        scoring_profile_ids=scoring_profile_ids,
        positions=positions,
    )
    job = client.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))
    return {
        "dry_run": True,
        "estimated_bytes_processed": int(job.total_bytes_processed or 0),
        "candidate_count": len(sql_native_tournament_candidates()),
        "expected_summary_rows": len(sql_native_tournament_candidates()) * len(tuple(scoring_profile_ids)),
        "detail_rows_written": 0,
    }


def run_sql_native_tournament_summary(
    *,
    client: Any,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    target_seasons: list[int] | tuple[int, ...] = tuple(range(2017, 2026)),
    scoring_profile_ids: list[str] | tuple[str, ...] = DEFAULT_SCORING_PROFILES,
    positions: list[str] | tuple[str, ...] = POSITIONS,
) -> list[dict[str, Any]]:
    sql = build_sql_native_tournament_summary_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        target_seasons=target_seasons,
        scoring_profile_ids=scoring_profile_ids,
        positions=positions,
    )
    return [dict(row) for row in client.query(sql).result()]


def build_sql_native_tournament_summary_write_sql(
    *,
    project_id: str,
    dataset_id: str,
    target_seasons: list[int] | tuple[int, ...] = tuple(range(2017, 2026)),
    scoring_profile_ids: list[str] | tuple[str, ...] = DEFAULT_SCORING_PROFILES,
    positions: list[str] | tuple[str, ...] = POSITIONS,
    backtest_run_id_prefix: str = "ranking_backtest_sql_native_v0_rolling_2017_2025",
    formula_version: str = "ranking_backtest_sql_native_v0_rolling_2017_2025",
    league_type_id: str = DEFAULT_LEAGUE_TYPE_ID,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT_ID,
    candidate_rows: list[Mapping[str, Any]] | None = None,
) -> str:
    summary_sql = build_sql_native_tournament_summary_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        target_seasons=target_seasons,
        scoring_profile_ids=scoring_profile_ids,
        positions=positions,
        candidate_rows=candidate_rows,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    run_table = table_id(project_id, dataset_id, "ranking_backtest_runs")
    summary_table = table_id(project_id, dataset_id, "ranking_backtest_candidate_summaries")
    season_start = min(int(season) for season in target_seasons)
    season_end = max(int(season) for season in target_seasons)
    return f"""
CREATE TEMP TABLE sql_native_summary AS
{summary_sql};

DELETE FROM `{summary_table}`
WHERE backtest_run_id IN (
  SELECT CONCAT({_sql_string(backtest_run_id_prefix)}, '_', scoring_profile_id)
  FROM (SELECT DISTINCT scoring_profile_id FROM sql_native_summary)
);

DELETE FROM `{run_table}`
WHERE backtest_run_id IN (
  SELECT CONCAT({_sql_string(backtest_run_id_prefix)}, '_', scoring_profile_id)
  FROM (SELECT DISTINCT scoring_profile_id FROM sql_native_summary)
);

INSERT INTO `{run_table}` (
  backtest_run_id,
  formula_set_id,
  formula_version,
  candidate_count,
  season_start,
  season_end,
  week_start,
  week_end,
  scoring_profile_id,
  league_type_id,
  roster_format_id,
  target_definition_json,
  input_tables_json,
  dry_run,
  status,
  created_by,
  created_at,
  completed_at,
  error_message,
  notes
)
SELECT
  CONCAT({_sql_string(backtest_run_id_prefix)}, '_', scoring_profile_id) AS backtest_run_id,
  CAST(NULL AS STRING) AS formula_set_id,
  {_sql_string(formula_version)} AS formula_version,
  COUNT(DISTINCT candidate_id) AS candidate_count,
  {season_start} AS season_start,
  {season_end} AS season_end,
  CAST(NULL AS INT64) AS week_start,
  CAST(NULL AS INT64) AS week_end,
  scoring_profile_id,
  {_sql_string(league_type_id)} AS league_type_id,
  {_sql_string(roster_format_id)} AS roster_format_id,
  TO_JSON_STRING(STRUCT('position_default_top_n' AS target_name, 'draft utility metrics in metric_json' AS metric_contract)) AS target_definition_json,
  TO_JSON_STRING(['ranking_backtest_feature_mart']) AS input_tables_json,
  FALSE AS dry_run,
  'complete' AS status,
  {_sql_string(CREATED_BY)} AS created_by,
  CURRENT_TIMESTAMP() AS created_at,
  CURRENT_TIMESTAMP() AS completed_at,
  CAST(NULL AS STRING) AS error_message,
  'SQL-native summary-only tournament. No detail rows, no champions, no live rankings.' AS notes
FROM sql_native_summary
GROUP BY scoring_profile_id;

INSERT INTO `{summary_table}` (
  backtest_run_id,
  candidate_id,
  formula_version,
  position,
  scoring_profile_id,
  league_type_id,
  roster_format_id,
  target_name,
  sample_size,
  pairwise_win_rate,
  top_n_hit_rate,
  rank_correlation,
  mean_absolute_error,
  regret_score,
  actual_points_captured_rate,
  missing_input_rate,
  metric_json,
  missing_flags_json,
  source_freshness_json,
  created_at
)
SELECT
  CONCAT({_sql_string(backtest_run_id_prefix)}, '_', scoring_profile_id) AS backtest_run_id,
  candidate_id,
  formula_version,
  position,
  scoring_profile_id,
  league_type_id,
  roster_format_id,
  target_name,
  sample_size,
  pairwise_win_rate,
  top_n_hit_rate,
  rank_correlation,
  mean_absolute_error,
  regret_score,
  actual_points_captured_rate,
  missing_input_rate,
  metric_json,
  missing_flags_json,
  source_freshness_json,
  CURRENT_TIMESTAMP() AS created_at
FROM sql_native_summary;
""".strip()


def write_sql_native_tournament_summaries(
    *,
    client: Any,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    target_seasons: list[int] | tuple[int, ...] = tuple(range(2017, 2026)),
    scoring_profile_ids: list[str] | tuple[str, ...] = DEFAULT_SCORING_PROFILES,
    positions: list[str] | tuple[str, ...] = POSITIONS,
    backtest_run_id_prefix: str = "ranking_backtest_sql_native_v0_rolling_2017_2025",
    formula_version: str = "ranking_backtest_sql_native_v0_rolling_2017_2025",
    candidate_rows: list[Mapping[str, Any]] | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    require_write_authorization(env)
    sql = build_sql_native_tournament_summary_write_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        target_seasons=target_seasons,
        scoring_profile_ids=scoring_profile_ids,
        positions=positions,
        backtest_run_id_prefix=backtest_run_id_prefix,
        formula_version=formula_version,
        candidate_rows=candidate_rows,
    )
    job = client.query(sql)
    job.result()
    return {
        "write": True,
        "summary_only": True,
        "detail_rows_written": 0,
        "job_id": getattr(job, "job_id", None),
    }


def _bqml_feature_select_sql(*, include_categorical: bool = True) -> str:
    numeric_columns = []
    for column in BQML_NUMERIC_PREDICTORS:
        numeric_columns.append(f"    COALESCE({column}, 0.0) AS {column}")
        numeric_columns.append(f"    IF({column} IS NULL, 1, 0) AS {column}_missing")
    categorical_columns = [f"    {column}" for column in BQML_CATEGORICAL_PREDICTORS] if include_categorical else []
    return ",\n".join(categorical_columns + numeric_columns)


def bqml_model_specs(include_boosted_tree: bool = True, include_random_forest: bool = False) -> list[dict[str, Any]]:
    specs = [
        {
            "model_name": "ranking_bqml_linear_vor_v0",
            "candidate_id": "ranking_bqml_linear_vor_v0",
            "candidate_family": "bqml_linear_vor",
            "model_type": "LINEAR_REG",
            "target": "value_over_replacement",
            "label_column": "label_value",
            "prediction_column": "predicted_label_value",
        },
        {
            "model_name": "ranking_bqml_linear_points_v0",
            "candidate_id": "ranking_bqml_linear_points_v0",
            "candidate_family": "bqml_linear_points",
            "model_type": "LINEAR_REG",
            "target": "target_fantasy_points",
            "label_column": "label_value",
            "prediction_column": "predicted_label_value",
        },
        {
            "model_name": "ranking_bqml_logistic_elite_v0",
            "candidate_id": "ranking_bqml_logistic_elite_v0",
            "candidate_family": "bqml_logistic_elite",
            "model_type": "LOGISTIC_REG",
            "target": "elite_label",
            "label_column": "elite_label",
            "prediction_column": "predicted_elite_probability",
        },
    ]
    if include_boosted_tree:
        specs.append(
            {
                "model_name": "ranking_bqml_boosted_tree_vor_v0",
                "candidate_id": "ranking_bqml_boosted_tree_vor_v0",
                "candidate_family": "bqml_boosted_tree_vor",
                "model_type": "BOOSTED_TREE_REGRESSOR",
                "target": "value_over_replacement",
                "label_column": "label_value",
                "prediction_column": "predicted_label_value",
            }
        )
    if include_random_forest:
        specs.append(
            {
                "model_name": "ranking_bqml_random_forest_vor_v0",
                "candidate_id": "ranking_bqml_random_forest_vor_v0",
                "candidate_family": "bqml_random_forest_vor",
                "model_type": "RANDOM_FOREST_REGRESSOR",
                "target": "value_over_replacement",
                "label_column": "label_value",
                "prediction_column": "predicted_label_value",
            }
        )
    return specs


def build_bqml_training_select_sql(
    *,
    project_id: str,
    dataset_id: str,
    target_name: str,
    season_start: int = BQML_TRAIN_SEASONS[0],
    season_end: int = BQML_TRAIN_SEASONS[1],
    include_identity: bool = False,
) -> str:
    if target_name not in {"value_over_replacement", "target_fantasy_points", "elite_label"}:
        raise FormulaValidationError(f"Unsupported BQML target: {target_name}")
    mart_table = table_id(project_id, dataset_id, "ranking_backtest_feature_mart")
    feature_columns = _bqml_feature_select_sql(include_categorical=not include_identity)
    identity_columns = """
    target_season,
    target_week,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    position,
    player_id_internal,
    player_name,
    team,
    target_fantasy_points,
    actual_position_rank,
    actual_overall_rank,
    value_over_replacement,
""".rstrip() if include_identity else ""
    label_sql = {
        "value_over_replacement": "value_over_replacement AS label_value",
        "target_fantasy_points": "target_fantasy_points AS label_value",
        "elite_label": "IF(actual_position_rank <= CASE position WHEN 'QB' THEN 12 WHEN 'RB' THEN 24 WHEN 'WR' THEN 24 WHEN 'TE' THEN 12 ELSE 24 END, 1, 0) AS elite_label",
    }[target_name]
    prefix = f"{identity_columns}\n" if identity_columns else ""
    return f"""
SELECT
{prefix}{feature_columns},
    {label_sql}
FROM `{mart_table}`
WHERE target_season BETWEEN {int(season_start)} AND {int(season_end)}
  AND source_window_end_season < target_season
  AND target_fantasy_points IS NOT NULL
  AND actual_position_rank IS NOT NULL
  AND value_over_replacement IS NOT NULL
""".strip()


def build_bqml_create_model_sql(
    *,
    project_id: str,
    dataset_id: str,
    spec: Mapping[str, Any],
) -> str:
    model_type = str(spec["model_type"]).upper()
    if model_type not in {"LINEAR_REG", "LOGISTIC_REG", "BOOSTED_TREE_REGRESSOR", "RANDOM_FOREST_REGRESSOR"}:
        raise FormulaValidationError(f"Unsupported BQML model type: {model_type}")
    model_table = table_id(project_id, dataset_id, str(spec["model_name"]))
    target_name = str(spec["target"])
    label_column = str(spec["label_column"])
    options = [
        f"model_type='{model_type}'",
        f"input_label_cols=['{label_column}']",
        "data_split_method='NO_SPLIT'",
    ]
    if model_type in {"LINEAR_REG", "LOGISTIC_REG"}:
        options.append("max_iterations=20")
    elif model_type == "BOOSTED_TREE_REGRESSOR":
        options.extend(("max_iterations=20", "max_tree_depth=4", "learn_rate=0.1"))
    elif model_type == "RANDOM_FOREST_REGRESSOR":
        options.extend(("num_parallel_tree=20", "max_tree_depth=6"))
    training_sql = build_bqml_training_select_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        target_name=target_name,
        season_start=BQML_TRAIN_SEASONS[0],
        season_end=BQML_TRAIN_SEASONS[1],
        include_identity=False,
    )
    return f"""
CREATE OR REPLACE MODEL `{model_table}`
OPTIONS({", ".join(options)}) AS
{training_sql}
""".strip()


def build_bqml_prediction_union_sql(
    *,
    project_id: str,
    dataset_id: str,
    specs: list[Mapping[str, Any]],
    target_seasons: list[int] | tuple[int, ...] = (BQML_VALIDATION_SEASON, BQML_HOLDOUT_SEASON),
) -> str:
    parts = []
    season_start = min(int(season) for season in target_seasons)
    season_end = max(int(season) for season in target_seasons)
    for spec in specs:
        model_id = table_id(project_id, dataset_id, str(spec["model_name"]))
        target_name = str(spec["target"])
        input_sql = build_bqml_training_select_sql(
            project_id=project_id,
            dataset_id=dataset_id,
            target_name=target_name,
            season_start=season_start,
            season_end=season_end,
            include_identity=True,
        )
        if spec["model_type"] == "LOGISTIC_REG":
            predicted_score = "100.0 * COALESCE((SELECT prob FROM UNNEST(predicted_elite_label_probs) WHERE CAST(label AS STRING) = '1' LIMIT 1), 0.0)"
        else:
            predicted_score = "predicted_label_value"
        parts.append(
            f"""
SELECT
  {_sql_string(str(spec["candidate_id"]))} AS candidate_id,
  {_sql_string(str(spec["candidate_family"]))} AS candidate_family,
  {_sql_string(str(spec["model_name"]))} AS model_name,
  target_season,
  target_week,
  scoring_profile_id,
  league_type_id,
  roster_format_id,
  position,
  player_id_internal,
  player_name,
  team,
  target_fantasy_points AS actual_points,
  actual_position_rank,
  actual_overall_rank,
  value_over_replacement,
  {predicted_score} AS predicted_score
FROM ML.PREDICT(MODEL `{model_id}`, ({input_sql}))
""".strip()
        )
    if not parts:
        raise FormulaValidationError("At least one BQML model spec is required")
    return "\nUNION ALL\n".join(parts)


def build_bqml_prediction_summary_sql(
    *,
    project_id: str,
    dataset_id: str,
    specs: list[Mapping[str, Any]] | None = None,
    target_seasons: list[int] | tuple[int, ...] = (BQML_VALIDATION_SEASON, BQML_HOLDOUT_SEASON),
) -> str:
    selected_specs = specs or bqml_model_specs(include_boosted_tree=True, include_random_forest=False)
    prediction_sql = build_bqml_prediction_union_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        specs=selected_specs,
        target_seasons=target_seasons,
    )
    return f"""
WITH predictions AS (
{prediction_sql}
),
ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY candidate_id, target_season, target_week, scoring_profile_id, league_type_id, roster_format_id, position
      ORDER BY predicted_score DESC, player_id_internal
    ) AS predicted_rank_position,
    ROW_NUMBER() OVER (
      PARTITION BY candidate_id, target_season, target_week, scoring_profile_id, league_type_id, roster_format_id
      ORDER BY predicted_score DESC, player_id_internal
    ) AS predicted_overall_rank,
    CASE position WHEN 'QB' THEN 12 WHEN 'RB' THEN 24 WHEN 'WR' THEN 24 WHEN 'TE' THEN 12 ELSE 24 END AS default_top_n
  FROM predictions
  WHERE predicted_score IS NOT NULL
),
with_rank_metrics AS (
  SELECT
    *,
    CASE
      WHEN predicted_rank_position BETWEEN 1 AND 12 THEN '1-12'
      WHEN predicted_rank_position BETWEEN 13 AND 24 THEN '13-24'
      WHEN predicted_rank_position BETWEEN 25 AND 36 THEN '25-36'
      WHEN predicted_rank_position BETWEEN 37 AND 60 THEN '37-60'
      WHEN predicted_rank_position BETWEEN 61 AND 100 THEN '61-100'
      ELSE '101+'
    END AS predicted_pick_band,
    CASE
      WHEN actual_position_rank BETWEEN 1 AND 12 THEN '1-12'
      WHEN actual_position_rank BETWEEN 13 AND 24 THEN '13-24'
      WHEN actual_position_rank BETWEEN 25 AND 36 THEN '25-36'
      WHEN actual_position_rank BETWEEN 37 AND 60 THEN '37-60'
      WHEN actual_position_rank BETWEEN 61 AND 100 THEN '61-100'
      ELSE '101+'
    END AS actual_position_pick_band
  FROM ranked
),
weekly_ideal AS (
  SELECT
    candidate_id,
    target_season,
    target_week,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    position,
    player_id_internal,
    ROW_NUMBER() OVER (
      PARTITION BY candidate_id, target_season, target_week, scoring_profile_id, league_type_id, roster_format_id, position
      ORDER BY actual_points DESC, player_id_internal
    ) AS ideal_rank
  FROM with_rank_metrics
),
weekly_metrics AS (
  SELECT
    scored.candidate_id,
    ANY_VALUE(scored.candidate_family) AS candidate_family,
    ANY_VALUE(scored.model_name) AS model_name,
    scored.target_season,
    scored.target_week,
    scored.scoring_profile_id,
    scored.league_type_id,
    scored.roster_format_id,
    scored.position,
    scored.default_top_n,
    COUNT(*) AS source_row_count,
    SAFE_DIVIDE(COUNTIF(scored.predicted_rank_position <= scored.default_top_n AND scored.actual_position_rank <= scored.default_top_n), NULLIF(COUNTIF(scored.actual_position_rank <= scored.default_top_n), 0)) AS top_n_hit_rate,
    SAFE_DIVIDE(SUM(IF(scored.predicted_rank_position <= scored.default_top_n, scored.actual_points, 0)), SUM(IF(scored.actual_position_rank <= scored.default_top_n, scored.actual_points, 0))) AS actual_points_captured_rate,
    SAFE_DIVIDE(SUM(IF(scored.predicted_rank_position <= scored.default_top_n, scored.value_over_replacement, 0)), SUM(IF(scored.actual_position_rank <= scored.default_top_n, scored.value_over_replacement, 0))) AS value_over_replacement_captured_rate,
    SAFE_DIVIDE(SUM(IF(scored.predicted_rank_position <= scored.default_top_n, GREATEST(scored.actual_points, 0) / (LN(scored.predicted_rank_position + 1) / LN(2)), 0)), SUM(IF(ideal.ideal_rank <= scored.default_top_n, GREATEST(scored.actual_points, 0) / (LN(ideal.ideal_rank + 1) / LN(2)), 0))) AS ndcg_at_k,
    SAFE_DIVIDE(COUNTIF(scored.predicted_rank_position <= scored.default_top_n AND scored.actual_position_rank <= scored.default_top_n), NULLIF(COUNTIF(scored.actual_position_rank <= scored.default_top_n), 0)) AS elite_recall_at_k,
    AVG(IF(scored.predicted_pick_band = scored.actual_position_pick_band, 1.0, 0.0)) AS tier_accuracy,
    SAFE_DIVIDE(COUNTIF(scored.predicted_rank_position <= scored.default_top_n AND scored.actual_position_rank > scored.default_top_n * 2), NULLIF(COUNTIF(scored.predicted_rank_position <= scored.default_top_n), 0)) AS bust_rate,
    SUM(IF(scored.actual_position_rank <= scored.default_top_n, scored.value_over_replacement, 0)) - SUM(IF(scored.predicted_rank_position <= scored.default_top_n, scored.value_over_replacement, 0)) AS pick_band_regret
  FROM with_rank_metrics scored
  JOIN weekly_ideal ideal
    ON scored.candidate_id = ideal.candidate_id
   AND scored.target_season = ideal.target_season
   AND scored.target_week = ideal.target_week
   AND scored.scoring_profile_id = ideal.scoring_profile_id
   AND scored.league_type_id = ideal.league_type_id
   AND scored.roster_format_id = ideal.roster_format_id
   AND scored.position = ideal.position
   AND scored.player_id_internal = ideal.player_id_internal
  GROUP BY scored.candidate_id, scored.target_season, scored.target_week, scored.scoring_profile_id, scored.league_type_id, scored.roster_format_id, scored.position, scored.default_top_n
),
pairwise AS (
  SELECT
    left_side.candidate_id,
    left_side.target_season,
    left_side.scoring_profile_id,
    left_side.league_type_id,
    left_side.roster_format_id,
    left_side.position,
    SAFE_DIVIDE(COUNTIF(left_side.actual_points > right_side.actual_points), COUNT(*)) AS high_confidence_pairwise_win_rate
  FROM with_rank_metrics left_side
  JOIN with_rank_metrics right_side
    ON left_side.candidate_id = right_side.candidate_id
   AND left_side.target_season = right_side.target_season
   AND left_side.target_week = right_side.target_week
   AND left_side.scoring_profile_id = right_side.scoring_profile_id
   AND left_side.league_type_id = right_side.league_type_id
   AND left_side.roster_format_id = right_side.roster_format_id
   AND left_side.position = right_side.position
   AND left_side.predicted_rank_position < right_side.predicted_rank_position
   AND ABS(left_side.predicted_score - right_side.predicted_score) >= 10
  GROUP BY left_side.candidate_id, left_side.target_season, left_side.scoring_profile_id, left_side.league_type_id, left_side.roster_format_id, left_side.position
),
overall_pairwise AS (
  SELECT
    left_side.candidate_id,
    left_side.target_season,
    left_side.scoring_profile_id,
    left_side.league_type_id,
    left_side.roster_format_id,
    SAFE_DIVIDE(COUNTIF(left_side.actual_overall_rank < right_side.actual_overall_rank), COUNT(*)) AS overall_pairwise_draft_win_rate
  FROM with_rank_metrics left_side
  JOIN with_rank_metrics right_side
    ON left_side.candidate_id = right_side.candidate_id
   AND left_side.target_season = right_side.target_season
   AND left_side.target_week = right_side.target_week
   AND left_side.scoring_profile_id = right_side.scoring_profile_id
   AND left_side.league_type_id = right_side.league_type_id
   AND left_side.roster_format_id = right_side.roster_format_id
   AND left_side.predicted_overall_rank < right_side.predicted_overall_rank
   AND ABS(left_side.predicted_score - right_side.predicted_score) >= 10
  WHERE (left_side.predicted_overall_rank <= 100 OR left_side.actual_overall_rank <= 100)
    AND (right_side.predicted_overall_rank <= 100 OR right_side.actual_overall_rank <= 100)
  GROUP BY left_side.candidate_id, left_side.target_season, left_side.scoring_profile_id, left_side.league_type_id, left_side.roster_format_id
),
summary AS (
  SELECT
    candidate_id,
    ANY_VALUE(candidate_family) AS candidate_family,
    ANY_VALUE(model_name) AS model_name,
    target_season,
    position,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    SUM(source_row_count) AS sample_size,
    AVG(top_n_hit_rate) AS top_n_hit_rate,
    AVG(actual_points_captured_rate) AS actual_points_captured_rate,
    AVG(value_over_replacement_captured_rate) AS value_over_replacement_captured_rate,
    AVG(ndcg_at_k) AS ndcg_at_k,
    AVG(elite_recall_at_k) AS elite_recall_at_k,
    AVG(tier_accuracy) AS tier_accuracy,
    AVG(bust_rate) AS bust_rate,
    SUM(GREATEST(pick_band_regret, 0)) AS pick_band_regret
  FROM weekly_metrics
  GROUP BY candidate_id, target_season, position, scoring_profile_id, league_type_id, roster_format_id
),
rank_corr AS (
  SELECT
    candidate_id,
    target_season,
    position,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    CORR(CAST(predicted_rank_position AS FLOAT64), CAST(actual_position_rank AS FLOAT64)) AS rank_correlation
  FROM with_rank_metrics
  GROUP BY candidate_id, target_season, position, scoring_profile_id, league_type_id, roster_format_id
)
SELECT
  summary.*,
  rank_corr.rank_correlation,
  pairwise.high_confidence_pairwise_win_rate,
  overall_pairwise.overall_pairwise_draft_win_rate
FROM summary
LEFT JOIN rank_corr USING (candidate_id, target_season, position, scoring_profile_id, league_type_id, roster_format_id)
LEFT JOIN pairwise USING (candidate_id, target_season, position, scoring_profile_id, league_type_id, roster_format_id)
LEFT JOIN overall_pairwise USING (candidate_id, target_season, scoring_profile_id, league_type_id, roster_format_id)
ORDER BY target_season, scoring_profile_id, position, candidate_id
""".strip()


def ensemble_candidate_specs() -> list[dict[str, Any]]:
    return [
        {
            "ensemble_id": "ensemble_conservative_pigskin_plus_v0",
            "ensemble_family": "ensemble_conservative_pigskin_plus",
            "tuned_on_season": ENSEMBLE_TUNING_SEASON,
            "holdout_season": ENSEMBLE_HOLDOUT_SEASON,
            "weights": {
                "current_pigskin": 0.60,
                "simple_projection": 0.20,
                "scarcity_adjusted": 0.10,
                "bqml_logistic_elite": 0.10,
            },
        },
        {
            "ensemble_id": "ensemble_elite_probability_blend_v0",
            "ensemble_family": "ensemble_elite_probability_blend",
            "tuned_on_season": ENSEMBLE_TUNING_SEASON,
            "holdout_season": ENSEMBLE_HOLDOUT_SEASON,
            "weights": {
                "current_pigskin": 0.40,
                "simple_projection": 0.20,
                "scarcity_adjusted": 0.10,
                "bqml_logistic_elite": 0.30,
            },
        },
        {
            "ensemble_id": "ensemble_pairwise_strength_blend_v0",
            "ensemble_family": "ensemble_pairwise_strength_blend",
            "tuned_on_season": ENSEMBLE_TUNING_SEASON,
            "holdout_season": ENSEMBLE_HOLDOUT_SEASON,
            "weights": {
                "current_pigskin": 0.40,
                "simple_projection": 0.20,
                "scarcity_adjusted": 0.10,
                "bqml_linear_points": 0.30,
            },
        },
        {
            "ensemble_id": "ensemble_balanced_research_blend_v0",
            "ensemble_family": "ensemble_balanced_research_blend",
            "tuned_on_season": ENSEMBLE_TUNING_SEASON,
            "holdout_season": ENSEMBLE_HOLDOUT_SEASON,
            "weights": {
                "current_pigskin": 0.35,
                "simple_projection": 0.20,
                "scarcity_adjusted": 0.15,
                "bqml_logistic_elite": 0.15,
                "bqml_linear_points": 0.15,
            },
        },
        {
            "ensemble_id": "ensemble_position_aware_first_draft_v0",
            "ensemble_family": "ensemble_position_aware_first_draft",
            "tuned_on_season": ENSEMBLE_TUNING_SEASON,
            "holdout_season": ENSEMBLE_HOLDOUT_SEASON,
            "position_weights": {
                "QB": {
                    "current_pigskin": 0.45,
                    "simple_projection": 0.15,
                    "scarcity_adjusted": 0.10,
                    "bqml_logistic_elite": 0.10,
                    "bqml_linear_points": 0.20,
                },
                "RB": {
                    "current_pigskin": 0.30,
                    "simple_projection": 0.25,
                    "scarcity_adjusted": 0.20,
                    "bqml_logistic_elite": 0.20,
                    "bqml_linear_points": 0.05,
                },
                "WR": {
                    "current_pigskin": 0.35,
                    "simple_projection": 0.25,
                    "scarcity_adjusted": 0.10,
                    "bqml_logistic_elite": 0.20,
                    "bqml_linear_points": 0.10,
                },
                "TE": {
                    "current_pigskin": 0.55,
                    "simple_projection": 0.20,
                    "scarcity_adjusted": 0.10,
                    "bqml_logistic_elite": 0.10,
                    "bqml_linear_points": 0.05,
                },
            },
        },
    ]


def validate_ensemble_specs(specs: list[Mapping[str, Any]]) -> None:
    valid_components = set(ENSEMBLE_FORMULA_COMPONENTS) | set(ENSEMBLE_BQML_COMPONENTS)
    for spec in specs:
        if int(spec.get("holdout_season", 0)) != ENSEMBLE_HOLDOUT_SEASON:
            raise FormulaValidationError("Ensemble holdout season must be 2025")
        if int(spec.get("tuned_on_season", 0)) >= ENSEMBLE_HOLDOUT_SEASON:
            raise FormulaValidationError("Ensemble weights must not be tuned on the 2025 holdout")
        weight_groups: list[tuple[str | None, Mapping[str, Any]]] = []
        if "weights" in spec:
            weight_groups.append((None, spec["weights"]))
        for position, weights in dict(spec.get("position_weights", {})).items():
            weight_groups.append((_normalize_position(str(position)), weights))
        if not weight_groups:
            raise FormulaValidationError(f"Ensemble {spec.get('ensemble_id')} has no weights")
        for position, weights in weight_groups:
            total = sum(float(weight) for weight in weights.values())
            if abs(total - 1.0) > 0.000001:
                label = f"{spec.get('ensemble_id')} {position or 'all'}"
                raise FormulaValidationError(f"Ensemble weights must sum to 1.0 for {label}")
            for component_id, weight in weights.items():
                if component_id not in valid_components:
                    raise FormulaValidationError(f"Unknown ensemble component: {component_id}")
                if float(weight) < 0:
                    raise FormulaValidationError(f"Ensemble component weight must be non-negative: {component_id}")
                if component_id in ENSEMBLE_BQML_COMPONENTS and float(weight) > 0.50:
                    raise FormulaValidationError(f"BQML component weight exceeds first-prototype limit: {component_id}")


def _ensemble_weight_rows_sql(specs: list[Mapping[str, Any]]) -> str:
    validate_ensemble_specs(specs)
    rows: list[str] = []
    for spec in specs:
        common = {
            "ensemble_id": str(spec["ensemble_id"]),
            "ensemble_family": str(spec["ensemble_family"]),
        }
        if "weights" in spec:
            for component_id, weight in dict(spec["weights"]).items():
                rows.append(
                    "SELECT "
                    f"{_sql_string(common['ensemble_id'])} AS ensemble_id, "
                    f"{_sql_string(common['ensemble_family'])} AS ensemble_family, "
                    "CAST(NULL AS STRING) AS position, "
                    f"{_sql_string(str(component_id))} AS component_id, "
                    f"{float(weight):.12g} AS weight"
                )
        for position, weights in dict(spec.get("position_weights", {})).items():
            normalized_position = _normalize_position(str(position))
            for component_id, weight in dict(weights).items():
                rows.append(
                    "SELECT "
                    f"{_sql_string(common['ensemble_id'])} AS ensemble_id, "
                    f"{_sql_string(common['ensemble_family'])} AS ensemble_family, "
                    f"{_sql_string(normalized_position)} AS position, "
                    f"{_sql_string(str(component_id))} AS component_id, "
                    f"{float(weight):.12g} AS weight"
                )
    if not rows:
        raise FormulaValidationError("At least one ensemble weight row is required")
    return "\n  UNION ALL\n  ".join(rows)


def _ensemble_formula_candidate_rows() -> list[Mapping[str, Any]]:
    component_versions = set(ENSEMBLE_FORMULA_COMPONENTS.values())
    return [
        candidate
        for candidate in sql_native_tournament_candidates()
        if str(candidate.get("formula_version")) in component_versions
    ]


def build_ensemble_formula_component_prediction_sql(
    *,
    project_id: str,
    dataset_id: str,
    target_seasons: list[int] | tuple[int, ...] = (ENSEMBLE_TUNING_SEASON, ENSEMBLE_HOLDOUT_SEASON),
    scoring_profile_ids: list[str] | tuple[str, ...] = DEFAULT_SCORING_PROFILES,
    positions: list[str] | tuple[str, ...] = POSITIONS,
    league_type_id: str = DEFAULT_LEAGUE_TYPE_ID,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT_ID,
) -> str:
    mart_table = table_id(project_id, dataset_id, "ranking_backtest_feature_mart")
    selected_candidates = _ensemble_formula_candidate_rows()
    formula_weight_sql = _formula_weight_rows_sql(selected_candidates)
    target_season_sql = ", ".join(str(int(season)) for season in sorted({int(season) for season in target_seasons}))
    profile_sql = ", ".join(_sql_string(profile) for profile in scoring_profile_ids)
    position_sql = ", ".join(_sql_string(_normalize_position(position)) for position in positions)
    component_case = " ".join(
        f"WHEN formula_version = {_sql_string(version)} THEN {_sql_string(component_id)}"
        for component_id, version in ENSEMBLE_FORMULA_COMPONENTS.items()
    )
    return f"""
WITH formula_weights AS (
  {formula_weight_sql}
),
mart AS (
  SELECT *
  FROM `{mart_table}`
  WHERE target_season IN ({target_season_sql})
    AND scoring_profile_id IN ({profile_sql})
    AND position IN ({position_sql})
    AND league_type_id = {_sql_string(league_type_id)}
    AND roster_format_id = {_sql_string(roster_format_id)}
    AND source_window_end_season < target_season
),
feature_values AS (
  SELECT
    mart.*,
    weights.candidate_id,
    weights.formula_version,
    weights.feature_name,
    weights.weight,
    CASE weights.feature_name
      WHEN 'actual_points' THEN target_fantasy_points
      WHEN 'fantasy_points_ppr' THEN target_fantasy_points
      WHEN 'recent_points_avg' THEN recent_points_avg
      WHEN 'profile_points_score' THEN profile_points_score
      WHEN 'analytical_grade_proxy' THEN analytical_grade_proxy
      WHEN 'opportunity_score_proxy' THEN opportunity_score_proxy
      WHEN 'efficiency_score_proxy' THEN efficiency_score_proxy
      WHEN 'role_stability_score' THEN role_stability_score
      WHEN 'targets' THEN targets
      WHEN 'carries' THEN carries
      WHEN 'receiving_yards' THEN receiving_yards
      WHEN 'receiving_epa' THEN receiving_epa
      WHEN 'red_zone_targets' THEN red_zone_targets
      WHEN 'red_zone_carries' THEN red_zone_carries
      WHEN 'outside_red_zone_targets' THEN outside_red_zone_targets
      WHEN 'outside_red_zone_carries' THEN outside_red_zone_carries
      WHEN 'gemini31_rb_weighted_opportunity_ppr' THEN gemini31_rb_weighted_opportunity_ppr
      WHEN 'success_rate' THEN success_rate
      WHEN 'passing_success_rate' THEN passing_success_rate
      WHEN 'cpoe' THEN cpoe
      WHEN 'dropbacks' THEN dropbacks
      WHEN 'rushing_attempts' THEN rushing_attempts
      WHEN 'rush_success_rate' THEN rush_success_rate
      WHEN 'receiving_usage' THEN receiving_usage
      WHEN 'usage_volume' THEN usage_volume
      WHEN 'epa_per_play' THEN epa_per_play
      WHEN 'passing_epa_per_play' THEN passing_epa_per_play
      WHEN 'team_epa_per_play' THEN team_epa_per_play
      WHEN 'red_zone_opportunities' THEN red_zone_opportunities
      WHEN 'goal_line_opportunities' THEN goal_line_opportunities
      WHEN 'snap_share_proxy' THEN snap_share_proxy
      WHEN 'air_yards' THEN air_yards
      WHEN 'team_pass_rate' THEN team_pass_rate
      WHEN 'points_per_game_slope_3yr' THEN points_per_game_slope_3yr
      WHEN 'total_points_slope_3yr' THEN total_points_slope_3yr
      WHEN 'opportunity_slope_3yr' THEN opportunity_slope_3yr
      WHEN 'target_share_slope_3yr' THEN target_share_slope_3yr
      WHEN 'carry_share_slope_3yr' THEN carry_share_slope_3yr
      WHEN 'receiving_usage_slope_3yr' THEN receiving_usage_slope_3yr
      WHEN 'wopr_slope_3yr' THEN wopr_slope_3yr
      WHEN 'epa_slope_3yr' THEN epa_slope_3yr
      WHEN 'efficiency_slope_3yr' THEN efficiency_slope_3yr
      WHEN 'availability_rate_3yr' THEN availability_rate_3yr
      WHEN 'weekly_volatility_3yr' THEN weekly_volatility_3yr
      WHEN 'improving_3yr' THEN improving_3yr
      WHEN 'declining_3yr' THEN declining_3yr
      WHEN 'breakout_trajectory_3yr' THEN breakout_trajectory_3yr
      ELSE NULL
    END AS raw_feature_value
  FROM mart
  JOIN formula_weights weights
    ON mart.position = weights.position
),
scored_features AS (
  SELECT
    *,
    CASE
      WHEN raw_feature_value IS NULL THEN NULL
      WHEN feature_name IN ('points_per_game_slope_3yr', 'total_points_slope_3yr', 'opportunity_slope_3yr', 'receiving_usage_slope_3yr', 'epa_slope_3yr', 'efficiency_slope_3yr') THEN LEAST(100.0, GREATEST(0.0, 50.0 + raw_feature_value * 10.0))
      WHEN feature_name IN ('target_share_slope_3yr', 'carry_share_slope_3yr', 'wopr_slope_3yr') THEN LEAST(100.0, GREATEST(0.0, 50.0 + raw_feature_value * 250.0))
      WHEN feature_name = 'availability_rate_3yr' THEN LEAST(100.0, GREATEST(0.0, IF(raw_feature_value <= 1, raw_feature_value * 100.0, raw_feature_value)))
      WHEN feature_name = 'weekly_volatility_3yr' THEN LEAST(100.0, GREATEST(0.0, 100.0 - raw_feature_value * 10.0))
      WHEN feature_name IN ('improving_3yr', 'breakout_trajectory_3yr') THEN IF(raw_feature_value > 0, 100.0, 0.0)
      WHEN feature_name = 'declining_3yr' THEN IF(raw_feature_value > 0, 0.0, 100.0)
      WHEN feature_name IN ('success_rate', 'cpoe', 'snap_share_proxy') THEN LEAST(100.0, GREATEST(0.0, IF(raw_feature_value <= 1, raw_feature_value * 100.0, raw_feature_value)))
      WHEN feature_name IN ('actual_points', 'fantasy_points_ppr', 'recent_points_avg') THEN LEAST(100.0, GREATEST(0.0, raw_feature_value / 35.0 * 100.0))
      WHEN feature_name IN ('epa_per_play', 'passing_epa_per_play', 'receiving_epa', 'team_epa_per_play') THEN LEAST(100.0, GREATEST(0.0, 50.0 + raw_feature_value * 25.0))
      WHEN feature_name = 'air_yards' AND raw_feature_value BETWEEN 0 AND 1 THEN LEAST(100.0, GREATEST(0.0, raw_feature_value * 100.0))
      WHEN feature_name IN ('air_yards', 'receiving_yards') THEN LEAST(100.0, GREATEST(0.0, raw_feature_value / 150.0 * 100.0))
      WHEN feature_name IN ('targets', 'carries', 'dropbacks', 'rushing_attempts', 'usage_volume', 'red_zone_targets', 'red_zone_carries', 'outside_red_zone_targets', 'outside_red_zone_carries', 'gemini31_rb_weighted_opportunity_ppr', 'red_zone_opportunities', 'goal_line_opportunities') THEN LEAST(100.0, GREATEST(0.0, raw_feature_value / 25.0 * 100.0))
      ELSE LEAST(100.0, GREATEST(0.0, raw_feature_value))
    END AS feature_score
  FROM feature_values
),
candidate_scores AS (
  SELECT
    CASE {component_case} ELSE NULL END AS component_id,
    target_season,
    target_week,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    position,
    player_id_internal,
    ANY_VALUE(player_name) AS player_name,
    ANY_VALUE(team) AS team,
    ANY_VALUE(target_fantasy_points) AS actual_points,
    ANY_VALUE(actual_position_rank) AS actual_position_rank,
    ANY_VALUE(actual_overall_rank) AS actual_overall_rank,
    ANY_VALUE(value_over_replacement) AS value_over_replacement,
    SAFE_DIVIDE(SUM(feature_score * weight), SUM(IF(feature_score IS NULL, 0, weight))) AS predicted_score,
    SAFE_DIVIDE(SUM(IF(feature_score IS NULL, weight, 0)), SUM(weight)) AS missing_input_rate
  FROM scored_features
  GROUP BY component_id, target_season, target_week, scoring_profile_id, league_type_id, roster_format_id, position, player_id_internal
)
SELECT *
FROM candidate_scores
WHERE component_id IS NOT NULL
  AND predicted_score IS NOT NULL
""".strip()


def build_ensemble_component_prediction_union_sql(
    *,
    project_id: str,
    dataset_id: str,
    target_seasons: list[int] | tuple[int, ...] = (ENSEMBLE_TUNING_SEASON, ENSEMBLE_HOLDOUT_SEASON),
    scoring_profile_ids: list[str] | tuple[str, ...] = DEFAULT_SCORING_PROFILES,
    positions: list[str] | tuple[str, ...] = POSITIONS,
    league_type_id: str = DEFAULT_LEAGUE_TYPE_ID,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT_ID,
) -> str:
    formula_sql = build_ensemble_formula_component_prediction_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        target_seasons=target_seasons,
        scoring_profile_ids=scoring_profile_ids,
        positions=positions,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    bqml_specs = [
        spec
        for spec in bqml_model_specs(include_boosted_tree=False, include_random_forest=False)
        if str(spec["candidate_family"]) in BQML_COMPONENT_SPECS
    ]
    bqml_sql = build_bqml_prediction_union_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        specs=bqml_specs,
        target_seasons=target_seasons,
    )
    bqml_component_case = " ".join(
        f"WHEN candidate_family = {_sql_string(family)} THEN {_sql_string(component_id)}"
        for component_id, family in ENSEMBLE_BQML_COMPONENTS.items()
    )
    return f"""
SELECT
  component_id,
  target_season,
  target_week,
  scoring_profile_id,
  league_type_id,
  roster_format_id,
  position,
  player_id_internal,
  player_name,
  team,
  actual_points,
  actual_position_rank,
  actual_overall_rank,
  value_over_replacement,
  predicted_score,
  missing_input_rate
FROM ({formula_sql})
UNION ALL
SELECT
  CASE {bqml_component_case} ELSE NULL END AS component_id,
  target_season,
  target_week,
  scoring_profile_id,
  league_type_id,
  roster_format_id,
  position,
  player_id_internal,
  player_name,
  team,
  actual_points,
  actual_position_rank,
  actual_overall_rank,
  value_over_replacement,
  predicted_score,
  0.0 AS missing_input_rate
FROM ({bqml_sql})
WHERE candidate_family IN ({", ".join(_sql_string(family) for family in BQML_COMPONENT_SPECS)})
""".strip()


def build_ensemble_prediction_summary_sql(
    *,
    project_id: str,
    dataset_id: str,
    specs: list[Mapping[str, Any]] | None = None,
    target_seasons: list[int] | tuple[int, ...] = (ENSEMBLE_TUNING_SEASON, ENSEMBLE_HOLDOUT_SEASON),
    scoring_profile_ids: list[str] | tuple[str, ...] = DEFAULT_SCORING_PROFILES,
    positions: list[str] | tuple[str, ...] = POSITIONS,
    league_type_id: str = DEFAULT_LEAGUE_TYPE_ID,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT_ID,
) -> str:
    selected_specs = specs or ensemble_candidate_specs()
    validate_ensemble_specs(selected_specs)
    component_sql = build_ensemble_component_prediction_union_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        target_seasons=target_seasons,
        scoring_profile_ids=scoring_profile_ids,
        positions=positions,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    weight_sql = _ensemble_weight_rows_sql(selected_specs)
    season_start = min(int(season) for season in target_seasons)
    season_end = max(int(season) for season in target_seasons)
    return f"""
WITH component_predictions AS (
{component_sql}
),
ensemble_weights AS (
  {weight_sql}
),
normalized_components AS (
  SELECT
    component_predictions.*,
    CASE
      WHEN MAX(predicted_score) OVER component_window = MIN(predicted_score) OVER component_window THEN 50.0
      ELSE SAFE_DIVIDE(
        predicted_score - MIN(predicted_score) OVER component_window,
        NULLIF(MAX(predicted_score) OVER component_window - MIN(predicted_score) OVER component_window, 0)
      ) * 100.0
    END AS normalized_score
  FROM component_predictions
  WINDOW component_window AS (
    PARTITION BY component_id, target_season, target_week, scoring_profile_id, league_type_id, roster_format_id, position
  )
),
ensemble_scores AS (
  SELECT
    weights.ensemble_id AS candidate_id,
    weights.ensemble_family AS formula_version,
    components.target_season,
    components.target_week,
    components.scoring_profile_id,
    components.league_type_id,
    components.roster_format_id,
    components.position,
    components.player_id_internal,
    ANY_VALUE(components.player_name) AS player_name,
    ANY_VALUE(components.team) AS team,
    ANY_VALUE(components.actual_points) AS actual_points,
    ANY_VALUE(components.actual_position_rank) AS actual_rank_position,
    ANY_VALUE(components.actual_overall_rank) AS actual_overall_rank,
    ANY_VALUE(components.value_over_replacement) AS value_over_replacement,
    SAFE_DIVIDE(SUM(components.normalized_score * weights.weight), SUM(weights.weight)) AS predicted_score,
    SUM(components.missing_input_rate * weights.weight) AS missing_input_rate,
    COUNT(DISTINCT components.component_id) AS available_component_count
  FROM normalized_components components
  JOIN ensemble_weights weights
    ON components.component_id = weights.component_id
   AND (weights.position IS NULL OR components.position = weights.position)
  GROUP BY weights.ensemble_id, weights.ensemble_family, components.target_season, components.target_week, components.scoring_profile_id, components.league_type_id, components.roster_format_id, components.position, components.player_id_internal
),
ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY candidate_id, target_season, target_week, scoring_profile_id, league_type_id, roster_format_id, position
      ORDER BY predicted_score DESC, player_id_internal
    ) AS predicted_rank_position,
    ROW_NUMBER() OVER (
      PARTITION BY candidate_id, target_season, target_week, scoring_profile_id, league_type_id, roster_format_id
      ORDER BY predicted_score DESC, player_id_internal
    ) AS predicted_overall_rank,
    CASE position WHEN 'QB' THEN 12 WHEN 'RB' THEN 24 WHEN 'WR' THEN 24 WHEN 'TE' THEN 12 ELSE 24 END AS default_top_n
  FROM ensemble_scores
  WHERE predicted_score IS NOT NULL
),
with_rank_metrics AS (
  SELECT
    *,
    CASE
      WHEN predicted_rank_position BETWEEN 1 AND 12 THEN '1-12'
      WHEN predicted_rank_position BETWEEN 13 AND 24 THEN '13-24'
      WHEN predicted_rank_position BETWEEN 25 AND 36 THEN '25-36'
      WHEN predicted_rank_position BETWEEN 37 AND 60 THEN '37-60'
      WHEN predicted_rank_position BETWEEN 61 AND 100 THEN '61-100'
      ELSE '101+'
    END AS predicted_pick_band,
    CASE
      WHEN actual_rank_position BETWEEN 1 AND 12 THEN '1-12'
      WHEN actual_rank_position BETWEEN 13 AND 24 THEN '13-24'
      WHEN actual_rank_position BETWEEN 25 AND 36 THEN '25-36'
      WHEN actual_rank_position BETWEEN 37 AND 60 THEN '37-60'
      WHEN actual_rank_position BETWEEN 61 AND 100 THEN '61-100'
      ELSE '101+'
    END AS actual_position_pick_band
  FROM ranked
),
weekly_ideal AS (
  SELECT
    candidate_id,
    target_season,
    target_week,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    position,
    player_id_internal,
    ROW_NUMBER() OVER (
      PARTITION BY candidate_id, target_season, target_week, scoring_profile_id, league_type_id, roster_format_id, position
      ORDER BY actual_points DESC, player_id_internal
    ) AS ideal_rank
  FROM with_rank_metrics
),
weekly_metrics AS (
  SELECT
    scored.candidate_id,
    scored.formula_version,
    scored.target_season,
    scored.target_week,
    scored.scoring_profile_id,
    scored.league_type_id,
    scored.roster_format_id,
    scored.position,
    scored.default_top_n,
    COUNT(*) AS source_row_count,
    AVG(scored.missing_input_rate) AS missing_input_rate,
    SAFE_DIVIDE(COUNTIF(scored.predicted_rank_position <= scored.default_top_n AND scored.actual_rank_position <= scored.default_top_n), NULLIF(COUNTIF(scored.actual_rank_position <= scored.default_top_n), 0)) AS top_n_hit_rate,
    SAFE_DIVIDE(SUM(IF(scored.predicted_rank_position <= scored.default_top_n, scored.actual_points, 0)), SUM(IF(scored.actual_rank_position <= scored.default_top_n, scored.actual_points, 0))) AS actual_points_captured_rate,
    SAFE_DIVIDE(SUM(IF(scored.predicted_rank_position <= scored.default_top_n, scored.value_over_replacement, 0)), SUM(IF(scored.actual_rank_position <= scored.default_top_n, scored.value_over_replacement, 0))) AS value_over_replacement_captured_rate,
    SAFE_DIVIDE(SUM(IF(scored.predicted_rank_position <= scored.default_top_n, GREATEST(scored.actual_points, 0) / (LN(scored.predicted_rank_position + 1) / LN(2)), 0)), SUM(IF(ideal.ideal_rank <= scored.default_top_n, GREATEST(scored.actual_points, 0) / (LN(ideal.ideal_rank + 1) / LN(2)), 0))) AS ndcg_at_k,
    SAFE_DIVIDE(COUNTIF(scored.predicted_rank_position <= scored.default_top_n AND scored.actual_rank_position <= scored.default_top_n), NULLIF(COUNTIF(scored.actual_rank_position <= scored.default_top_n), 0)) AS elite_recall_at_k,
    AVG(IF(scored.predicted_pick_band = scored.actual_position_pick_band, 1.0, 0.0)) AS tier_accuracy,
    SAFE_DIVIDE(COUNTIF(scored.predicted_rank_position <= scored.default_top_n AND scored.actual_rank_position > scored.default_top_n * 2), NULLIF(COUNTIF(scored.predicted_rank_position <= scored.default_top_n), 0)) AS bust_rate,
    SUM(IF(scored.actual_rank_position <= scored.default_top_n, scored.value_over_replacement, 0)) - SUM(IF(scored.predicted_rank_position <= scored.default_top_n, scored.value_over_replacement, 0)) AS pick_band_regret
  FROM with_rank_metrics scored
  JOIN weekly_ideal ideal
    ON scored.candidate_id = ideal.candidate_id
   AND scored.target_season = ideal.target_season
   AND scored.target_week = ideal.target_week
   AND scored.scoring_profile_id = ideal.scoring_profile_id
   AND scored.league_type_id = ideal.league_type_id
   AND scored.roster_format_id = ideal.roster_format_id
   AND scored.position = ideal.position
   AND scored.player_id_internal = ideal.player_id_internal
  GROUP BY scored.candidate_id, scored.formula_version, scored.target_season, scored.target_week, scored.scoring_profile_id, scored.league_type_id, scored.roster_format_id, scored.position, scored.default_top_n
),
pairwise AS (
  SELECT
    left_side.candidate_id,
    left_side.scoring_profile_id,
    left_side.league_type_id,
    left_side.roster_format_id,
    left_side.position,
    SAFE_DIVIDE(COUNTIF(left_side.actual_points > right_side.actual_points), COUNT(*)) AS high_confidence_pairwise_win_rate
  FROM with_rank_metrics left_side
  JOIN with_rank_metrics right_side
    ON left_side.candidate_id = right_side.candidate_id
   AND left_side.target_season = right_side.target_season
   AND left_side.target_week = right_side.target_week
   AND left_side.scoring_profile_id = right_side.scoring_profile_id
   AND left_side.league_type_id = right_side.league_type_id
   AND left_side.roster_format_id = right_side.roster_format_id
   AND left_side.position = right_side.position
   AND left_side.predicted_rank_position < right_side.predicted_rank_position
   AND ABS(left_side.predicted_score - right_side.predicted_score) >= 10
  GROUP BY left_side.candidate_id, left_side.scoring_profile_id, left_side.league_type_id, left_side.roster_format_id, left_side.position
),
overall_pairwise AS (
  SELECT
    left_side.candidate_id,
    left_side.scoring_profile_id,
    left_side.league_type_id,
    left_side.roster_format_id,
    SAFE_DIVIDE(COUNTIF(left_side.actual_overall_rank < right_side.actual_overall_rank), COUNT(*)) AS overall_pairwise_draft_win_rate
  FROM with_rank_metrics left_side
  JOIN with_rank_metrics right_side
    ON left_side.candidate_id = right_side.candidate_id
   AND left_side.target_season = right_side.target_season
   AND left_side.target_week = right_side.target_week
   AND left_side.scoring_profile_id = right_side.scoring_profile_id
   AND left_side.league_type_id = right_side.league_type_id
   AND left_side.roster_format_id = right_side.roster_format_id
   AND left_side.predicted_overall_rank < right_side.predicted_overall_rank
   AND ABS(left_side.predicted_score - right_side.predicted_score) >= 10
  WHERE (left_side.predicted_overall_rank <= 100 OR left_side.actual_overall_rank <= 100)
    AND (right_side.predicted_overall_rank <= 100 OR right_side.actual_overall_rank <= 100)
  GROUP BY left_side.candidate_id, left_side.scoring_profile_id, left_side.league_type_id, left_side.roster_format_id
),
summary AS (
  SELECT
    candidate_id,
    ANY_VALUE(formula_version) AS formula_version,
    position,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    SUM(source_row_count) AS sample_size,
    AVG(top_n_hit_rate) AS top_n_hit_rate,
    AVG(missing_input_rate) AS missing_input_rate,
    AVG(actual_points_captured_rate) AS actual_points_captured_rate,
    AVG(value_over_replacement_captured_rate) AS value_over_replacement_captured_rate,
    AVG(ndcg_at_k) AS ndcg_at_k,
    AVG(actual_points_captured_rate) AS value_captured_at_k,
    AVG(elite_recall_at_k) AS elite_recall_at_k,
    AVG(tier_accuracy) AS tier_accuracy,
    AVG(bust_rate) AS bust_rate,
    SUM(GREATEST(pick_band_regret, 0)) AS pick_band_regret
  FROM weekly_metrics
  GROUP BY candidate_id, position, scoring_profile_id, league_type_id, roster_format_id
),
rank_corr AS (
  SELECT
    candidate_id,
    position,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    CORR(CAST(predicted_rank_position AS FLOAT64), CAST(actual_rank_position AS FLOAT64)) AS rank_correlation
  FROM with_rank_metrics
  GROUP BY candidate_id, position, scoring_profile_id, league_type_id, roster_format_id
)
SELECT
  summary.candidate_id,
  summary.formula_version,
  summary.position,
  summary.scoring_profile_id,
  summary.league_type_id,
  summary.roster_format_id,
  'position_default_top_n' AS target_name,
  summary.sample_size,
  pairwise.high_confidence_pairwise_win_rate AS pairwise_win_rate,
  summary.top_n_hit_rate,
  rank_corr.rank_correlation,
  CAST(NULL AS FLOAT64) AS mean_absolute_error,
  summary.pick_band_regret AS regret_score,
  summary.actual_points_captured_rate,
  summary.missing_input_rate,
  TO_JSON_STRING(STRUCT(
    summary.ndcg_at_k AS ndcg_at_k,
    summary.value_captured_at_k AS value_captured_at_k,
    summary.elite_recall_at_k AS elite_recall_at_k,
    summary.tier_accuracy AS tier_accuracy,
    summary.bust_rate AS bust_rate,
    summary.pick_band_regret AS pick_band_regret,
    overall_pairwise.overall_pairwise_draft_win_rate AS overall_pairwise_draft_win_rate,
    pairwise.high_confidence_pairwise_win_rate AS high_confidence_pairwise_win_rate,
    summary.value_over_replacement_captured_rate AS value_over_replacement_captured_rate,
    {season_start} AS season_start,
    {season_end} AS season_end,
    'ranking_backtest_candidate_summaries.metric_json' AS persistence_target
  )) AS metric_json,
  TO_JSON_STRING(STRUCT(
    summary.missing_input_rate AS missing_input_rate,
    'component scores are min-max normalized per component/week/profile/position before blending' AS missing_policy
  )) AS missing_flags_json,
  TO_JSON_STRING(STRUCT(
    'ranking_backtest_feature_mart' AS feature_source_table,
    'ML.PREDICT BQML prototype models' AS bqml_source,
    'source_window_end_season < target_season' AS leakage_policy,
    '2025 holdout not used for weight tuning' AS holdout_policy
  )) AS source_freshness_json
FROM summary
LEFT JOIN rank_corr USING (candidate_id, position, scoring_profile_id, league_type_id, roster_format_id)
LEFT JOIN pairwise USING (candidate_id, position, scoring_profile_id, league_type_id, roster_format_id)
LEFT JOIN overall_pairwise USING (candidate_id, scoring_profile_id, league_type_id, roster_format_id)
ORDER BY scoring_profile_id, position, candidate_id
""".strip()


def build_ensemble_prediction_summary_write_sql(
    *,
    project_id: str,
    dataset_id: str,
    target_seasons: list[int] | tuple[int, ...] = (ENSEMBLE_TUNING_SEASON, ENSEMBLE_HOLDOUT_SEASON),
    scoring_profile_ids: list[str] | tuple[str, ...] = DEFAULT_SCORING_PROFILES,
    positions: list[str] | tuple[str, ...] = POSITIONS,
    backtest_run_id_prefix: str = ENSEMBLE_VERSION,
    formula_version: str = ENSEMBLE_VERSION,
    league_type_id: str = DEFAULT_LEAGUE_TYPE_ID,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT_ID,
) -> str:
    summary_sql = build_ensemble_prediction_summary_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        target_seasons=target_seasons,
        scoring_profile_ids=scoring_profile_ids,
        positions=positions,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    run_table = table_id(project_id, dataset_id, "ranking_backtest_runs")
    summary_table = table_id(project_id, dataset_id, "ranking_backtest_candidate_summaries")
    season_start = min(int(season) for season in target_seasons)
    season_end = max(int(season) for season in target_seasons)
    return f"""
CREATE TEMP TABLE ensemble_summary AS
{summary_sql};

DELETE FROM `{summary_table}`
WHERE backtest_run_id IN (
  SELECT CONCAT({_sql_string(backtest_run_id_prefix)}, '_', scoring_profile_id)
  FROM (SELECT DISTINCT scoring_profile_id FROM ensemble_summary)
);

DELETE FROM `{run_table}`
WHERE backtest_run_id IN (
  SELECT CONCAT({_sql_string(backtest_run_id_prefix)}, '_', scoring_profile_id)
  FROM (SELECT DISTINCT scoring_profile_id FROM ensemble_summary)
);

INSERT INTO `{run_table}` (
  backtest_run_id,
  formula_set_id,
  formula_version,
  candidate_count,
  season_start,
  season_end,
  week_start,
  week_end,
  scoring_profile_id,
  league_type_id,
  roster_format_id,
  target_definition_json,
  input_tables_json,
  dry_run,
  status,
  created_by,
  created_at,
  completed_at,
  error_message,
  notes
)
SELECT
  CONCAT({_sql_string(backtest_run_id_prefix)}, '_', scoring_profile_id) AS backtest_run_id,
  CAST(NULL AS STRING) AS formula_set_id,
  {_sql_string(formula_version)} AS formula_version,
  COUNT(DISTINCT candidate_id) AS candidate_count,
  {season_start} AS season_start,
  {season_end} AS season_end,
  CAST(NULL AS INT64) AS week_start,
  CAST(NULL AS INT64) AS week_end,
  scoring_profile_id,
  {_sql_string(league_type_id)} AS league_type_id,
  {_sql_string(roster_format_id)} AS roster_format_id,
  TO_JSON_STRING(STRUCT('position_default_top_n' AS target_name, 'ensemble draft utility metrics in metric_json' AS metric_contract)) AS target_definition_json,
  TO_JSON_STRING(['ranking_backtest_feature_mart', 'BQML prototype models']) AS input_tables_json,
  FALSE AS dry_run,
  'complete' AS status,
  {_sql_string(CREATED_BY)} AS created_by,
  CURRENT_TIMESTAMP() AS created_at,
  CURRENT_TIMESTAMP() AS completed_at,
  CAST(NULL AS STRING) AS error_message,
  'SQL-native ensemble summary-only tournament. No detail rows, no champions, no live rankings.' AS notes
FROM ensemble_summary
GROUP BY scoring_profile_id;

INSERT INTO `{summary_table}` (
  backtest_run_id,
  candidate_id,
  formula_version,
  position,
  scoring_profile_id,
  league_type_id,
  roster_format_id,
  target_name,
  sample_size,
  pairwise_win_rate,
  top_n_hit_rate,
  rank_correlation,
  mean_absolute_error,
  regret_score,
  actual_points_captured_rate,
  missing_input_rate,
  metric_json,
  missing_flags_json,
  source_freshness_json,
  created_at
)
SELECT
  CONCAT({_sql_string(backtest_run_id_prefix)}, '_', scoring_profile_id) AS backtest_run_id,
  candidate_id,
  formula_version,
  position,
  scoring_profile_id,
  league_type_id,
  roster_format_id,
  target_name,
  sample_size,
  pairwise_win_rate,
  top_n_hit_rate,
  rank_correlation,
  mean_absolute_error,
  regret_score,
  actual_points_captured_rate,
  missing_input_rate,
  metric_json,
  missing_flags_json,
  source_freshness_json,
  CURRENT_TIMESTAMP() AS created_at
FROM ensemble_summary;
""".strip()


def write_ensemble_prediction_summaries(
    *,
    client: Any,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    target_seasons: list[int] | tuple[int, ...] = (ENSEMBLE_TUNING_SEASON, ENSEMBLE_HOLDOUT_SEASON),
    scoring_profile_ids: list[str] | tuple[str, ...] = DEFAULT_SCORING_PROFILES,
    positions: list[str] | tuple[str, ...] = POSITIONS,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    require_write_authorization(env)
    sql = build_ensemble_prediction_summary_write_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        target_seasons=target_seasons,
        scoring_profile_ids=scoring_profile_ids,
        positions=positions,
    )
    job = client.query(sql)
    job.result()
    return {
        "write": True,
        "summary_only": True,
        "detail_rows_written": 0,
        "job_id": getattr(job, "job_id", None),
    }


def _formula_weight_rows_sql(candidate_rows: list[Mapping[str, Any]]) -> str:
    selected_rows: list[str] = []
    for candidate in candidate_rows:
        formula = validate_formula(json.loads(str(candidate["formula_json"])))
        profile_weights = formula.get("scoring_profile_weights") or {}
        if profile_weights and not isinstance(profile_weights, Mapping):
            raise FormulaValidationError("formula.scoring_profile_weights must be an object when provided")
        availability_multiplier = bool((formula.get("source_flags") or {}).get("availability_multiplier"))
        for feature_name in formula["features"]:
            base_weight = float(formula["weights"][feature_name])
            def profile_weight(profile_id: str) -> float:
                profile_payload = profile_weights.get(profile_id, {}) if isinstance(profile_weights, Mapping) else {}
                if not isinstance(profile_payload, Mapping):
                    raise FormulaValidationError(f"formula.scoring_profile_weights.{profile_id} must be an object")
                return float(profile_payload.get(feature_name, base_weight))

            selected_rows.append(
                "SELECT "
                f"{_sql_string(str(candidate['candidate_id']))} AS candidate_id, "
                f"{_sql_string(str(candidate['formula_version']))} AS formula_version, "
                f"{_sql_string(str(candidate['position']))} AS position, "
                f"{_sql_string(feature_name)} AS feature_name, "
                f"{base_weight:.12g} AS weight, "
                f"{profile_weight('ppr'):.12g} AS ppr_weight, "
                f"{profile_weight('half_ppr'):.12g} AS half_ppr_weight, "
                f"{profile_weight('standard'):.12g} AS standard_weight, "
                f"{profile_weight('gng_keeper'):.12g} AS gng_keeper_weight, "
                f"{'TRUE' if availability_multiplier else 'FALSE'} AS availability_multiplier, "
                f"{_sql_string(str(candidate['formula_json']))} AS formula_json"
            )
    if not selected_rows:
        raise FormulaValidationError("At least one SQL-native tournament candidate is required")
    return "\n  UNION ALL\n  ".join(selected_rows)


def _sql_string(value: str) -> str:
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"


def _feature_mart_query_params(
    *,
    target_season: int,
    source_window_start: int,
    source_window_end: int,
    scoring_profile_ids: list[str],
    positions: list[str],
    league_type_id: str,
    roster_format_id: str,
) -> list[Any]:
    return [
        _scalar_param("source_window_start_season", "INT64", int(source_window_start)),
        _scalar_param("source_window_end_season", "INT64", int(source_window_end)),
        _scalar_param("target_season", "INT64", int(target_season)),
        _array_param("scoring_profile_ids", "STRING", scoring_profile_ids),
        _array_param("positions", "STRING", positions),
        _scalar_param("league_type_id", "STRING", league_type_id),
        _scalar_param("roster_format_id", "STRING", roster_format_id),
    ]


def build_feature_availability_report(
    candidates: list[Mapping[str, Any]],
    feature_rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    reports: dict[str, Any] = {}
    for candidate in candidates:
        formula = validate_formula(json.loads(candidate["formula_json"]))
        feature_reports = {}
        for feature in formula["features"]:
            source_field = FEATURE_SOURCE_MAP.get(feature)
            available_count = 0
            if source_field:
                available_count = sum(1 for row in feature_rows if _safe_float(row.get(source_field)) is not None)
            feature_reports[feature] = {
                "source_field": source_field,
                "available_count": available_count,
                "missing_count": max(len(feature_rows) - available_count, 0),
            }
        reports[str(candidate["candidate_id"])] = feature_reports
    return reports


def build_target_availability_report(feature_rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    target_count = sum(1 for row in feature_rows if _safe_float(row.get("actual_points")) is not None)
    return {
        "input_row_count": len(feature_rows),
        "target_row_count": target_count,
        "missing_target_count": max(len(feature_rows) - target_count, 0),
        "target_available": target_count > 0,
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
    feature_names = list(formula.get("features", []))
    feature_count = max(len(feature_names), 1)
    missing_counter: Counter[str] = Counter()
    for row in result_rows:
        missing = json.loads(row["missing_flags_json"]).get("missing_features", [])
        missing_counter.update(str(feature) for feature in missing)
        missing_rates.append(len(missing) / feature_count)
    if sample_size:
        fully_missing_features = sorted(
            feature for feature in feature_names if missing_counter.get(str(feature), 0) >= sample_size
        )
        available_features = sorted(feature for feature in feature_names if feature not in fully_missing_features)
    else:
        fully_missing_features = sorted(feature_names)
        available_features = []
    top_missing_features = [
        {"feature": feature, "missing_row_count": count}
        for feature, count in missing_counter.most_common()
    ]
    top_n_hit_rate = None
    if target_rows:
        top_n_hit_rate = sum(1 for row in target_rows if row["target_hit"]) / len(target_rows)
    rank_correlation = _rank_correlation(scored_rows)
    pairwise_win_rate = _pairwise_win_rate(scored_rows)
    high_confidence_pairwise_win_rate = _pairwise_win_rate(scored_rows, min_predicted_score_delta=10.0)
    mean_absolute_error = _mean_absolute_error(scored_rows)
    top_n_capture = _top_n_capture_metrics(scored_rows, candidate_row["position"], target_name)
    metric_payload = {
        "sample_size": sample_size,
        "pairwise_win_rate": pairwise_win_rate,
        "high_confidence_pairwise_win_rate": high_confidence_pairwise_win_rate,
        "top_n_hit_rate": top_n_capture["top_n_hit_rate"] if top_n_capture["top_n_hit_rate"] is not None else top_n_hit_rate,
        "rank_correlation": rank_correlation,
        "mean_absolute_error": mean_absolute_error,
        "regret_score": top_n_capture["regret_score"],
        "actual_points_captured_rate": top_n_capture["actual_points_captured_rate"],
        "value_over_replacement_captured_rate": top_n_capture["value_over_replacement_captured_rate"],
        "missing_input_rate": sum(missing_rates) / len(missing_rates) if missing_rates else None,
        "expected_feature_count": len(feature_names),
        "available_feature_count": len(available_features),
        "missing_feature_count": len(fully_missing_features),
        "missing_feature_names": fully_missing_features,
        "top_missing_features": top_missing_features,
        "null_metric_reasons": {
            "pairwise_win_rate": None if pairwise_win_rate is not None else "fewer than two scored comparison rows",
            "high_confidence_pairwise_win_rate": None if high_confidence_pairwise_win_rate is not None else "fewer than two high-confidence scored comparison rows",
            "mean_absolute_error": None if mean_absolute_error is not None else "fewer than one scored row with ranks",
            "regret_score": None if top_n_capture["regret_score"] is not None else "top-N comparison unavailable",
            "actual_points_captured_rate": None if top_n_capture["actual_points_captured_rate"] is not None else "top-N comparison unavailable",
            "value_over_replacement_captured_rate": None if top_n_capture["value_over_replacement_captured_rate"] is not None else "replacement comparison unavailable",
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
        "pairwise_win_rate": pairwise_win_rate,
        "top_n_hit_rate": metric_payload["top_n_hit_rate"],
        "rank_correlation": rank_correlation,
        "mean_absolute_error": mean_absolute_error,
        "regret_score": top_n_capture["regret_score"],
        "actual_points_captured_rate": top_n_capture["actual_points_captured_rate"],
        "missing_input_rate": metric_payload["missing_input_rate"],
        "metric_json": _json(metric_payload),
        "missing_flags_json": _json(
            {
                "summary_from_results": True,
                "expected_feature_count": len(feature_names),
                "available_feature_count": len(available_features),
                "missing_feature_count": len(fully_missing_features),
                "missing_feature_names": fully_missing_features,
                "top_missing_features": top_missing_features,
            }
        ),
        "source_freshness_json": _json({"status": "computed", "result_row_count": sample_size}),
        "created_at": _now(),
    }


def save_executed_backtest(
    result: Mapping[str, Any],
    *,
    project_id: str,
    dataset_id: str,
    client: Any,
) -> dict[str, Any]:
    run_rows = [dict(row) for row in result.get("backtest_run_rows", [])]
    result_rows = [dict(row) for row in result.get("result_rows", [])]
    summary_rows = [dict(row) for row in result.get("candidate_summary_rows", [])]
    if not run_rows:
        raise ValueError("No backtest run rows to write")
    _validate_run_rows(run_rows)
    _validate_result_rows(result_rows)
    _validate_summary_rows(summary_rows)
    run_ids = [str(row["backtest_run_id"]) for row in run_rows]
    delete_params = [_array_param("backtest_run_ids", "STRING", run_ids)]
    for table_name in (
        "ranking_backtest_results",
        "ranking_backtest_candidate_summaries",
        "ranking_backtest_runs",
    ):
        client.query(
            f"""
DELETE FROM `{table_id(project_id, dataset_id, table_name)}`
WHERE backtest_run_id IN UNNEST(@backtest_run_ids)
""".strip(),
            job_config=_query_job_config(delete_params),
        ).result()
    client.load_table_from_json(
        run_rows,
        table_id(project_id, dataset_id, "ranking_backtest_runs"),
    ).result()
    client.load_table_from_json(
        result_rows,
        table_id(project_id, dataset_id, "ranking_backtest_results"),
    ).result()
    client.load_table_from_json(
        summary_rows,
        table_id(project_id, dataset_id, "ranking_backtest_candidate_summaries"),
    ).result()
    return {
        "backtest_run_row_count": len(run_rows),
        "result_row_count": len(result_rows),
        "candidate_summary_row_count": len(summary_rows),
        "backtest_run_ids": run_ids,
        "target_tables": [
            "ranking_backtest_runs",
            "ranking_backtest_results",
            "ranking_backtest_candidate_summaries",
        ],
    }


def recommend_champions(
    summary_rows: list[Mapping[str, Any]],
    candidates: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    candidate_names = {row["candidate_id"]: row.get("formula_name") for row in candidates}
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for row in summary_rows:
        grouped.setdefault((str(row["scoring_profile_id"]), str(row["position"])), []).append(row)
    recommendations: list[dict[str, Any]] = []
    for (profile, position), summaries in sorted(grouped.items()):
        best = sorted(
            summaries,
            key=lambda row: (
                _metric_sort_value(row.get("pairwise_win_rate")),
                _metric_sort_value(row.get("actual_points_captured_rate")),
                _metric_sort_value(row.get("top_n_hit_rate")),
                -_metric_sort_value(row.get("missing_input_rate"), missing_value=1.0),
            ),
            reverse=True,
        )[0]
        recommendations.append(
            {
                "scoring_profile_id": profile,
                "position": position,
                "candidate_id": best["candidate_id"],
                "formula_name": candidate_names.get(best["candidate_id"]),
                "pairwise_win_rate": best.get("pairwise_win_rate"),
                "actual_points_captured_rate": best.get("actual_points_captured_rate"),
                "top_n_hit_rate": best.get("top_n_hit_rate"),
                "missing_input_rate": best.get("missing_input_rate"),
                "reason": "highest pairwise win rate, with captured-points and top-N hit rate as tie-breakers",
            }
        )
    return recommendations


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


def append_scorecard_tournament_entry(existing_markdown: str, entry_markdown: str) -> str:
    """Append one tournament entry without removing older scorecard history."""
    entry = entry_markdown.strip()
    if not entry:
        return existing_markdown
    if entry in existing_markdown:
        return existing_markdown
    separator = "\n\n" if existing_markdown.strip() else ""
    return f"{existing_markdown.rstrip()}{separator}{entry}\n"


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
    if feature in {
        "points_per_game_slope_3yr",
        "total_points_slope_3yr",
        "opportunity_slope_3yr",
        "targets_slope_3yr",
        "receiving_usage_slope_3yr",
        "epa_slope_3yr",
        "efficiency_slope_3yr",
    }:
        return max(0.0, min(100.0, 50.0 + (value * 10.0)))
    if feature in {"target_share_slope_3yr", "carry_share_slope_3yr", "wopr_slope_3yr"}:
        return max(0.0, min(100.0, 50.0 + (value * 250.0)))
    if feature == "availability_rate_3yr":
        return max(0.0, min(100.0, value * 100.0 if value <= 1 else value))
    if feature in {"xfp_share_3yr", "offensive_snap_share_3yr"}:
        return max(0.0, min(100.0, value * 100.0 if value <= 1 else value))
    if feature == "weekly_volatility_3yr":
        return max(0.0, min(100.0, 100.0 - (value * 10.0)))
    if feature == "injury_risk_score_3yr":
        return max(0.0, min(100.0, 100.0 - value))
    if feature in {"improving_3yr", "breakout_trajectory_3yr"}:
        return 100.0 if value > 0 else 0.0
    if feature == "declining_3yr":
        return 0.0 if value > 0 else 100.0
    if feature in {"success_rate", "cpoe", "snap_share_proxy"}:
        return max(0.0, min(100.0, value * 100 if value <= 1 else value))
    if feature in {"actual_points", "fantasy_points_ppr", "recent_points_avg"}:
        return max(0.0, min(100.0, (value / 35.0) * 100.0))
    if feature in {"epa_per_play", "passing_epa_per_play", "receiving_epa", "team_epa_per_play"}:
        return max(0.0, min(100.0, 50.0 + (value * 25.0)))
    if feature == "air_yards" and 0 <= value <= 1:
        return max(0.0, min(100.0, value * 100.0))
    if feature in {"air_yards", "receiving_yards"}:
        return max(0.0, min(100.0, (value / 150.0) * 100.0))
    if feature == "fantasy_points_over_expectation_3yr":
        return max(0.0, min(100.0, 50.0 + (value * 5.0)))
    if feature in {
        "targets",
        "carries",
        "dropbacks",
        "rushing_attempts",
        "usage_volume",
        "red_zone_targets",
        "red_zone_carries",
        "outside_red_zone_targets",
        "outside_red_zone_carries",
        "gemini31_rb_weighted_opportunity_ppr",
        "red_zone_opportunities",
        "goal_line_opportunities",
    }:
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


def _pairwise_win_rate(rows: list[Mapping[str, Any]], *, min_predicted_score_delta: float = 0.0) -> float | None:
    grouped: dict[tuple[int, int], list[Mapping[str, Any]]] = {}
    for row in rows:
        if (
            row.get("season") is None
            or row.get("week") is None
            or row.get("predicted_rank_position") is None
            or _safe_float(row.get("actual_points")) is None
        ):
            continue
        grouped.setdefault((int(row["season"]), int(row["week"])), []).append(row)
    wins = 0
    comparisons = 0
    for week_rows in grouped.values():
        ordered = sorted(week_rows, key=lambda row: int(row["predicted_rank_position"]))
        for left_index, left in enumerate(ordered):
            left_points = _safe_float(left.get("actual_points"))
            left_score = _safe_float(left.get("predicted_score"))
            if left_points is None:
                continue
            for right in ordered[left_index + 1 :]:
                right_points = _safe_float(right.get("actual_points"))
                right_score = _safe_float(right.get("predicted_score"))
                if right_points is None or left_points == right_points:
                    continue
                if (
                    min_predicted_score_delta > 0
                    and left_score is not None
                    and right_score is not None
                    and abs(left_score - right_score) < min_predicted_score_delta
                ):
                    continue
                comparisons += 1
                if left_points > right_points:
                    wins += 1
    if comparisons == 0:
        return None
    return wins / comparisons


def _mean_absolute_error(rows: list[Mapping[str, Any]]) -> float | None:
    grouped: dict[tuple[int, int], list[Mapping[str, Any]]] = {}
    for row in rows:
        if (
            row.get("season") is None
            or row.get("week") is None
            or row.get("predicted_score") is None
            or row.get("actual_rank_position") is None
        ):
            continue
        grouped.setdefault((int(row["season"]), int(row["week"])), []).append(row)
    errors: list[float] = []
    for week_rows in grouped.values():
        denominator = max(len(week_rows) - 1, 1)
        for row in week_rows:
            predicted_score = _safe_float(row.get("predicted_score"))
            actual_rank = _safe_float(row.get("actual_rank_position"))
            if predicted_score is None or actual_rank is None:
                continue
            actual_rank_score = max(0.0, min(100.0, 100.0 * (1.0 - ((actual_rank - 1.0) / denominator))))
            errors.append(abs(predicted_score - actual_rank_score))
    if not errors:
        return None
    return sum(errors) / len(errors)


def _top_n_capture_metrics(
    rows: list[Mapping[str, Any]],
    position: str,
    target_name: str,
) -> dict[str, float | None]:
    top_n = _top_n_for_target(position, target_name)
    grouped: dict[tuple[int, int], list[Mapping[str, Any]]] = {}
    for row in rows:
        if (
            row.get("season") is None
            or row.get("week") is None
            or row.get("predicted_rank_position") is None
            or _safe_float(row.get("actual_points")) is None
        ):
            continue
        grouped.setdefault((int(row["season"]), int(row["week"])), []).append(row)
    hit_rates: list[float] = []
    predicted_points_total = 0.0
    actual_points_total = 0.0
    for week_rows in grouped.values():
        actual_sorted = sorted(week_rows, key=lambda row: _safe_float(row.get("actual_points")) or -9999.0, reverse=True)
        predicted_sorted = sorted(week_rows, key=lambda row: int(row["predicted_rank_position"]))
        actual_top = actual_sorted[:top_n]
        predicted_top = predicted_sorted[:top_n]
        if not actual_top or not predicted_top:
            continue
        actual_ids = {str(row["player_id_internal"]) for row in actual_top}
        predicted_ids = {str(row["player_id_internal"]) for row in predicted_top}
        hit_rates.append(len(actual_ids & predicted_ids) / max(len(actual_ids), 1))
        predicted_points_total += sum(_safe_float(row.get("actual_points")) or 0.0 for row in predicted_top)
        actual_points_total += sum(_safe_float(row.get("actual_points")) or 0.0 for row in actual_top)
    if actual_points_total <= 0:
        return {
            "top_n_hit_rate": None,
            "regret_score": None,
            "actual_points_captured_rate": None,
            "value_over_replacement_captured_rate": None,
        }
    return {
        "top_n_hit_rate": sum(hit_rates) / len(hit_rates) if hit_rates else None,
        "regret_score": max(actual_points_total - predicted_points_total, 0.0),
        "actual_points_captured_rate": predicted_points_total / actual_points_total,
        "value_over_replacement_captured_rate": _value_over_replacement_captured_rate(grouped, top_n),
    }


def _value_over_replacement_captured_rate(grouped_rows: Mapping[tuple[int, int], list[Mapping[str, Any]]], top_n: int) -> float | None:
    predicted_value_total = 0.0
    actual_value_total = 0.0
    for week_rows in grouped_rows.values():
        actual_sorted = sorted(week_rows, key=lambda row: _safe_float(row.get("actual_points")) or -9999.0, reverse=True)
        predicted_sorted = sorted(week_rows, key=lambda row: int(row["predicted_rank_position"]))
        if len(actual_sorted) <= top_n:
            continue
        replacement_points = _safe_float(actual_sorted[top_n].get("actual_points"))
        if replacement_points is None:
            continue
        actual_top = actual_sorted[:top_n]
        predicted_top = predicted_sorted[:top_n]
        predicted_value_total += sum(
            max((_safe_float(row.get("actual_points")) or 0.0) - replacement_points, 0.0)
            for row in predicted_top
        )
        actual_value_total += sum(
            max((_safe_float(row.get("actual_points")) or 0.0) - replacement_points, 0.0)
            for row in actual_top
        )
    if actual_value_total <= 0:
        return None
    return predicted_value_total / actual_value_total


def replacement_rank_for_position(position: str) -> int:
    return POSITION_TOP_N[_normalize_position(position)]


def assign_pick_band(overall_rank: int | None) -> str | None:
    if overall_rank is None:
        return None
    rank = int(overall_rank)
    if rank <= 0:
        raise ValueError("overall_rank must be positive")
    for band_start, band_end, label in PICK_BANDS:
        if rank >= band_start and (band_end is None or rank <= band_end):
            return label
    return None


def build_overall_draft_value_rows(result_rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Add cross-position draft ranks and position-relative VOR to result rows."""
    grouped: dict[tuple[str, str, int, int], list[Mapping[str, Any]]] = {}
    for row in result_rows:
        if (
            row.get("candidate_id") is None
            or row.get("scoring_profile_id") is None
            or row.get("season") is None
            or row.get("week") is None
            or _safe_float(row.get("predicted_score")) is None
            or _safe_float(row.get("actual_points")) is None
            or not row.get("position")
        ):
            continue
        grouped.setdefault(
            (
                str(row["candidate_id"]),
                str(row["scoring_profile_id"]),
                int(row["season"]),
                int(row["week"]),
            ),
            [],
        ).append(row)

    draft_rows: list[dict[str, Any]] = []
    for group_rows in grouped.values():
        predicted_sorted = sorted(
            group_rows,
            key=lambda item: (-(_safe_float(item.get("predicted_score")) or -9999.0), str(item.get("player_id_internal", ""))),
        )
        actual_sorted = sorted(
            group_rows,
            key=lambda item: (-(_safe_float(item.get("actual_points")) or -9999.0), str(item.get("player_id_internal", ""))),
        )
        predicted_ranks = {str(row["player_id_internal"]): index for index, row in enumerate(predicted_sorted, start=1)}
        actual_ranks = {str(row["player_id_internal"]): index for index, row in enumerate(actual_sorted, start=1)}
        replacement_points = _replacement_points_by_position(group_rows)

        for row in group_rows:
            player_id = str(row["player_id_internal"])
            position = _normalize_position(str(row["position"]))
            actual_points = _safe_float(row.get("actual_points")) or 0.0
            replacement_points_for_position = replacement_points.get(position)
            actual_vor = None
            if replacement_points_for_position is not None:
                actual_vor = max(actual_points - replacement_points_for_position, 0.0)
            predicted_rank = predicted_ranks.get(player_id)
            draft_rows.append(
                {
                    **dict(row),
                    "predicted_overall_rank": predicted_rank,
                    "actual_overall_rank": actual_ranks.get(player_id),
                    "predicted_pick_band": assign_pick_band(predicted_rank),
                    "actual_vor": actual_vor,
                    "replacement_points": replacement_points_for_position,
                }
            )
    return draft_rows


def build_overall_draft_value_summary(
    result_rows: list[Mapping[str, Any]],
    *,
    top_ns: tuple[int, ...] = OVERALL_DRAFT_TOP_N,
    pairwise_rank_limit: int | None = 100,
) -> dict[str, Any]:
    draft_rows = build_overall_draft_value_rows(result_rows)
    grouped: dict[tuple[str, str, int, int], list[Mapping[str, Any]]] = {}
    for row in draft_rows:
        grouped.setdefault(
            (
                str(row["candidate_id"]),
                str(row["scoring_profile_id"]),
                int(row["season"]),
                int(row["week"]),
            ),
            [],
        ).append(row)

    hit_totals: dict[int, list[float]] = {top_n: [] for top_n in top_ns}
    predicted_top_vor_total = 0.0
    actual_top_vor_total = 0.0
    regret_by_pick_band = {label: 0.0 for _, _, label in PICK_BANDS}
    pairwise_wins = 0
    pairwise_comparisons = 0

    for group_rows in grouped.values():
        for top_n in top_ns:
            predicted_ids = {
                str(row["player_id_internal"])
                for row in group_rows
                if row.get("predicted_overall_rank") is not None and int(row["predicted_overall_rank"]) <= top_n
            }
            actual_ids = {
                str(row["player_id_internal"])
                for row in group_rows
                if row.get("actual_overall_rank") is not None and int(row["actual_overall_rank"]) <= top_n
            }
            if actual_ids:
                hit_totals[top_n].append(len(predicted_ids & actual_ids) / min(top_n, len(actual_ids)))

        predicted_top = [
            row for row in group_rows
            if row.get("predicted_overall_rank") is not None and int(row["predicted_overall_rank"]) <= 100
        ]
        actual_top = [
            row for row in group_rows
            if row.get("actual_overall_rank") is not None and int(row["actual_overall_rank"]) <= 100
        ]
        predicted_top_vor_total += sum(_safe_float(row.get("actual_vor")) or 0.0 for row in predicted_top)
        actual_top_vor_total += sum(_safe_float(row.get("actual_vor")) or 0.0 for row in actual_top)

        for band_start, band_end, label in PICK_BANDS:
            predicted_band_value = sum(
                _safe_float(row.get("actual_vor")) or 0.0
                for row in group_rows
                if _rank_in_band(row.get("predicted_overall_rank"), band_start, band_end)
            )
            actual_band_value = sum(
                _safe_float(row.get("actual_vor")) or 0.0
                for row in group_rows
                if _rank_in_band(row.get("actual_overall_rank"), band_start, band_end)
            )
            regret_by_pick_band[label] += max(actual_band_value - predicted_band_value, 0.0)

        ordered = [
            row for row in sorted(group_rows, key=lambda item: int(item["predicted_overall_rank"]))
            if row.get("predicted_overall_rank") is not None
            and (pairwise_rank_limit is None or int(row["predicted_overall_rank"]) <= pairwise_rank_limit)
        ]
        for left_index, left in enumerate(ordered):
            left_points = _safe_float(left.get("actual_points"))
            if left_points is None:
                continue
            for right in ordered[left_index + 1:]:
                right_points = _safe_float(right.get("actual_points"))
                if right_points is None or left_points == right_points:
                    continue
                pairwise_comparisons += 1
                if left_points > right_points:
                    pairwise_wins += 1

    summary = {
        "source_row_count": len(draft_rows),
        "group_count": len(grouped),
        "overall_pairwise_draft_win_rate": None if pairwise_comparisons == 0 else pairwise_wins / pairwise_comparisons,
        "overall_pairwise_comparison_count": pairwise_comparisons,
        "overall_pairwise_rank_limit": pairwise_rank_limit,
        "value_over_replacement_captured_rate": None if actual_top_vor_total <= 0 else predicted_top_vor_total / actual_top_vor_total,
        "regret_by_pick_band": regret_by_pick_band,
    }
    for top_n, rates in hit_totals.items():
        summary[f"top_{top_n}_overall_hit_rate"] = None if not rates else sum(rates) / len(rates)
    return summary


def build_overall_draft_value_metrics_sql(
    *,
    project_id: str,
    dataset_id: str,
    backtest_run_id_like: str = "ranking_backtest_ranking_backtest_tournament_v0_rolling_2017_2025_%",
) -> str:
    """Return read-only SQL for cross-position draft-value metrics from stored detail rows."""
    results_table = table_id(project_id, dataset_id, "ranking_backtest_results")
    return f"""
WITH tournament AS (
  SELECT
    candidate_id,
    scoring_profile_id,
    season,
    week,
    position,
    player_id_internal,
    predicted_score,
    actual_points,
    CASE position WHEN 'QB' THEN 12 WHEN 'RB' THEN 24 WHEN 'WR' THEN 24 WHEN 'TE' THEN 12 ELSE 24 END AS replacement_rank
  FROM `{results_table}`
  WHERE backtest_run_id LIKE '{backtest_run_id_like}'
    AND predicted_score IS NOT NULL
    AND actual_points IS NOT NULL
),
position_ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY candidate_id, scoring_profile_id, season, week, position
      ORDER BY actual_points DESC, player_id_internal
    ) AS actual_position_rank_for_replacement
  FROM tournament
),
with_replacement AS (
  SELECT
    *,
    MAX(IF(actual_position_rank_for_replacement = replacement_rank, actual_points, NULL)) OVER (
      PARTITION BY candidate_id, scoring_profile_id, season, week, position
    ) AS replacement_points
  FROM position_ranked
),
ranked AS (
  SELECT
    *,
    GREATEST(actual_points - COALESCE(replacement_points, actual_points), 0) AS actual_vor,
    ROW_NUMBER() OVER (
      PARTITION BY candidate_id, scoring_profile_id, season, week
      ORDER BY predicted_score DESC, player_id_internal
    ) AS predicted_overall_rank,
    ROW_NUMBER() OVER (
      PARTITION BY candidate_id, scoring_profile_id, season, week
      ORDER BY actual_points DESC, player_id_internal
    ) AS actual_overall_rank
  FROM with_replacement
)
SELECT
  candidate_id,
  scoring_profile_id,
  COUNT(*) AS source_row_count,
  AVG(IF(predicted_overall_rank <= 24 AND actual_overall_rank <= 24, 1.0, 0.0)) AS top_24_overlap_proxy,
  AVG(IF(predicted_overall_rank <= 50 AND actual_overall_rank <= 50, 1.0, 0.0)) AS top_50_overlap_proxy,
  AVG(IF(predicted_overall_rank <= 100 AND actual_overall_rank <= 100, 1.0, 0.0)) AS top_100_overlap_proxy,
  SAFE_DIVIDE(
    SUM(IF(predicted_overall_rank <= 100, actual_vor, 0)),
    SUM(IF(actual_overall_rank <= 100, actual_vor, 0))
  ) AS value_over_replacement_captured_rate
FROM ranked
GROUP BY candidate_id, scoring_profile_id
""".strip()


def _replacement_points_by_position(rows: list[Mapping[str, Any]]) -> dict[str, float]:
    by_position: dict[str, list[float]] = {}
    for row in rows:
        actual_points = _safe_float(row.get("actual_points"))
        if actual_points is None or not row.get("position"):
            continue
        by_position.setdefault(_normalize_position(str(row["position"])), []).append(actual_points)
    replacement_points: dict[str, float] = {}
    for position, point_values in by_position.items():
        sorted_values = sorted(point_values, reverse=True)
        rank = min(replacement_rank_for_position(position), len(sorted_values))
        if rank > 0:
            replacement_points[position] = sorted_values[rank - 1]
    return replacement_points


def _rank_in_band(rank: Any, band_start: int, band_end: int | None) -> bool:
    if rank is None:
        return False
    normalized_rank = int(rank)
    return normalized_rank >= band_start and (band_end is None or normalized_rank <= band_end)


def _top_n_for_target(position: str, target_name: str) -> int:
    if target_name == "position_default_top_n":
        return POSITION_TOP_N[_normalize_position(position)]
    target = TARGET_DEFINITIONS[target_name]
    threshold = target.get("rank_threshold")
    if threshold is None:
        return POSITION_TOP_N[_normalize_position(position)]
    return int(threshold)


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


def _validate_result_rows(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        for field in RANKING_TABLES["ranking_backtest_results"]:
            if field in {
                "formula_set_id",
                "player_name",
                "team",
                "predicted_score",
                "predicted_rank_position",
                "actual_points",
                "actual_rank_position",
                "target_hit",
                "win_rate",
            }:
                continue
            if row.get(field) is None:
                raise ValueError(f"backtest result row missing {field}")
        validate_score(row.get("predicted_score"), field_name="predicted_score")
        win_rate = row.get("win_rate")
        if win_rate is not None and (float(win_rate) < 0 or float(win_rate) > 1):
            raise ValueError("win_rate must be between 0 and 1")
        for rank_field in ("predicted_rank_position", "actual_rank_position"):
            rank_value = row.get(rank_field)
            if rank_value is not None and int(rank_value) < 1:
                raise ValueError(f"{rank_field} must be positive")


def _validate_candidate_coverage(
    candidates: list[Mapping[str, Any]],
    positions: list[str],
    *,
    expected_count: int | None = 3,
) -> None:
    for position in positions:
        count = sum(1 for candidate in candidates if candidate["position"] == position)
        if expected_count is None:
            if count < 1:
                raise FormulaValidationError(f"Expected at least 1 {position} candidate, found {count}")
        elif count != expected_count:
            raise FormulaValidationError(f"Expected 3 {position} candidates, found {count}")


def _normalize_position(position: str) -> str:
    value = position.strip().upper()
    if value not in POSITIONS:
        raise FormulaValidationError(f"Unsupported position: {position}")
    return value


def _normalize_scoring_profile_id(scoring_profile_id: str) -> str:
    value = str(scoring_profile_id or "").strip().lower()
    _reject_executable_text(value)
    if value not in DEFAULT_SCORING_PROFILES:
        raise FormulaValidationError(f"Unsupported scoring_profile_id: {scoring_profile_id}")
    return value


def _normalize_backtest_version(backtest_version: str) -> str:
    value = str(backtest_version or "").strip().lower()
    _reject_executable_text(value)
    if not value or not value.replace("_", "").isalnum():
        raise FormulaValidationError(f"Unsupported backtest_version: {backtest_version}")
    return value


def _normalize_source_window_years(source_window_years: int) -> int:
    value = int(source_window_years)
    if value < 1 or value > 10:
        raise FormulaValidationError("source_window_years must be between 1 and 10")
    return value


def _normalize_candidate_family(candidate_family: str) -> str:
    value = str(candidate_family or "").strip().lower()
    _reject_executable_text(value)
    if value not in {"seeded", "trend_v2", "tournament_v0"}:
        raise FormulaValidationError(f"Unsupported candidate_family: {candidate_family}")
    return value


def _target_name_for_position(position: str) -> str:
    return "top_12_position" if _normalize_position(position) in {"QB", "TE"} else "top_24_position"


def _metric_sort_value(value: Any, *, missing_value: float = -1.0) -> float:
    numeric_value = _safe_float(value)
    return missing_value if numeric_value is None else numeric_value


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
    parser.add_argument("--all-positions", action="store_true")
    parser.add_argument("--season-start", type=int, default=2014)
    parser.add_argument("--season-end", type=int, default=2014)
    parser.add_argument("--source-season", type=int)
    parser.add_argument("--target-season", type=int)
    parser.add_argument("--week-start", type=int, default=1)
    parser.add_argument("--week-end", type=int, default=17)
    parser.add_argument("--target-week-start", type=int)
    parser.add_argument("--target-week-end", type=int)
    parser.add_argument("--target", default="top_12_position", choices=sorted(TARGET_DEFINITIONS))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--from-bigquery-candidates", action="store_true")
    parser.add_argument("--formula-set-id")
    parser.add_argument("--backtest-version", default=DEFAULT_BACKTEST_VERSION)
    parser.add_argument("--source-window-years", type=int, default=1)
    parser.add_argument("--candidate-family", default="seeded", choices=("seeded", "trend_v2", "tournament_v0"))
    parser.add_argument("--status", default="draft")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--scoring-profile-id", default="ppr")
    parser.add_argument("--all-scoring-profiles", action="store_true")
    parser.add_argument("--league-type-id", default="redraft")
    parser.add_argument("--roster-format-id", default="one_qb")
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    args = parser.parse_args(argv)

    if args.from_bigquery_candidates:
        if not args.formula_set_id:
            raise ValueError("--formula-set-id is required with --from-bigquery-candidates")
        from google.cloud import bigquery

        client = bigquery.Client(project=args.project)
        source_season = args.source_season or args.season_start
        target_season = args.target_season or args.season_end
        target_week_start = args.target_week_start if args.target_week_start is not None else args.week_start
        target_week_end = args.target_week_end if args.target_week_end is not None else args.week_end
        if args.all_positions or args.all_scoring_profiles or args.source_season or args.target_season:
            result = run_no_lookahead_backtest(
                client=client,
                formula_set_id=args.formula_set_id,
                source_season=source_season,
                target_season=target_season,
                target_week_start=target_week_start,
                target_week_end=target_week_end,
                scoring_profile_ids=DEFAULT_SCORING_PROFILES
                if args.all_scoring_profiles
                else (args.scoring_profile_id,),
                positions=POSITIONS if args.all_positions else (args.position,),
                status=args.status,
                league_type_id=args.league_type_id,
                roster_format_id=args.roster_format_id,
                project_id=args.project,
                dataset_id=args.dataset,
                backtest_version=args.backtest_version,
                source_window_years=args.source_window_years,
                candidate_family=args.candidate_family,
                dry_run=args.dry_run or not args.write,
                write=args.write,
                limit=args.limit,
            )
            print(json.dumps(_cli_summary(result), indent=2, sort_keys=True))
            return 0

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
        "backtest_version": result.get("backtest_version"),
        "source_window_years": result.get("source_window_years"),
        "candidate_family": result.get("candidate_family"),
        "positions": result.get("positions"),
        "scoring_profile_ids": result.get("scoring_profile_ids"),
        "source_season": result.get("source_season"),
        "target_season": result.get("target_season"),
        "target_week_start": result.get("target_week_start"),
        "target_week_end": result.get("target_week_end"),
        "season_start": result.get("season_start"),
        "season_end": result.get("season_end"),
        "target_definition": result.get("target_definition"),
        "input_tables": result.get("input_tables"),
        "blocked_metrics": result.get("blocked_metrics"),
        "backtest_run_count": len(result.get("backtest_run_rows", [])),
        "candidate_summary_count": len(result.get("candidate_summary_rows", [])),
        "formula_set_id": result.get("formula_set_id"),
        "input_row_count": result.get("input_row_count"),
        "result_shape_count": result.get("result_shape_count"),
        "target_availability": result.get("target_availability"),
        "feature_availability": result.get("feature_availability"),
        "position_input_counts": result.get("position_input_counts"),
        "champion_recommendations": result.get("champion_recommendations"),
        "write_summary": result.get("write_summary"),
        "sample_size": _first_summary_value(result, "sample_size"),
        "pairwise_win_rate": _first_summary_value(result, "pairwise_win_rate"),
        "actual_points_captured_rate": _first_summary_value(result, "actual_points_captured_rate"),
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
