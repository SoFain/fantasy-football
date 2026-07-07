"""BQML v2 feature and target contract for ranking research.

This module is intentionally non-mutating. It builds Standard-first query text
and validates the source-backed predictor allowlists used by future BQML v2
training phases.
"""

from __future__ import annotations

from dataclasses import dataclass


BQML_V2_DATASET_VERSION = "bqml_v2_standard_training_dataset_v0"
STANDARD_MODEL_SUFFIX = "v0"
STANDARD_MODEL_VERSION = "bqml_v2_standard_v0"
STANDARD_SUMMARY_VERSION = "ranking_backtest_sql_native_bqml_v2_standard_v0"
STANDARD_SCORING_PROFILE = "standard"
SCORING_PROFILE_ORDER = ("standard", "half_ppr", "ppr", "gng_keeper")
POSITIONS = ("QB", "RB", "WR", "TE")
TRAIN_SEASONS = tuple(range(2017, 2024))
VALIDATION_SEASON = 2024
HOLDOUT_SEASON = 2025
TARGET_SEASONS = tuple(range(2017, 2026))
LEAGUE_TYPE_ID = "redraft"
ROSTER_FORMAT_ID = "one_qb"
NO_GLOBAL_ALL_PROFILE_WINNER = True
REVIEW_POSITION_LIMITS = {"QB": 45, "RB": 80, "WR": 100, "TE": 35}
STANDARD_READINESS_THRESHOLDS = {
    "baseline_pigskin_proxies": 0.95,
    "opportunity": 0.95,
    "ideal_xfp": 0.90,
    "pbp_xfp": 0.90,
    "first_down_proxies": 0.90,
    "ngs": 0.70,
    "role_history": 0.90,
}

ALLOWED_MODEL_TYPES = ("LINEAR_REG", "LOGISTIC_REG")
DEFERRED_MODEL_TYPES = ("BOOSTED_TREE_REGRESSOR", "BOOSTED_TREE_CLASSIFIER")
BLOCKED_MODEL_TYPES = ("DNN", "AUTOML", "REMOTE_MODEL", "GEMINI", "HYPERPARAMETER_TUNING")


@dataclass(frozen=True)
class ModelFamily:
    family_id: str
    position: str
    target_group: str
    allowed_model_types: tuple[str, ...]


MODEL_FAMILIES: tuple[ModelFamily, ...] = (
    ModelFamily("bqml_v2_qb_profile_points", "QB", "profile_points", ("LINEAR_REG",)),
    ModelFamily("bqml_v2_qb_elite_bust", "QB", "elite_bust", ("LOGISTIC_REG",)),
    ModelFamily("bqml_v2_rb_profile_points", "RB", "profile_points", ("LINEAR_REG",)),
    ModelFamily("bqml_v2_rb_elite_bust", "RB", "elite_bust", ("LOGISTIC_REG",)),
    ModelFamily("bqml_v2_wr_profile_points", "WR", "profile_points", ("LINEAR_REG",)),
    ModelFamily("bqml_v2_wr_elite_bust", "WR", "elite_bust", ("LOGISTIC_REG",)),
    ModelFamily("bqml_v2_te_profile_points", "TE", "profile_points", ("LINEAR_REG",)),
    ModelFamily("bqml_v2_te_elite_bust", "TE", "elite_bust", ("LOGISTIC_REG",)),
)

IDENTIFIER_FIELDS = (
    "dataset_version",
    "split",
    "source_window_start_season",
    "source_window_end_season",
    "target_season",
    "target_week",
    "scoring_profile_id",
    "league_type_id",
    "roster_format_id",
    "position",
    "player_id_internal",
    "player_name",
    "team",
    "source_team",
)

LABEL_FIELDS = (
    "target_fantasy_points",
    "value_over_replacement",
    "elite_finish_label",
    "starter_finish_label",
    "bust_label",
)

OUTCOME_ONLY_FIELDS = (
    "target_fantasy_points",
    "actual_position_rank",
    "actual_overall_rank",
    "replacement_points",
    "value_over_replacement",
    "top_24_overall",
    "top_50_overall",
    "top_100_overall",
    "actual_pick_band",
)

METADATA_FIELDS = (
    "predictor_missing_flags_json",
    "outcome_missing_flags_json",
    "source_freshness_json",
    "provenance_json",
    "bqml_v2_missing_flags_json",
)

QB_ALLOWED_FEATURES = (
    "profile_points_score",
    "recent_points_avg",
    "passing_epa_per_play",
    "cpoe",
    "ngs_qb_passing_efficiency_score_3yr",
    "passing_xfp_pbp_3yr",
    "rushing_attempts",
    "qb_rushing_leverage_index",
    "rushing_xfp_pbp_3yr",
    "rushing_xfp_share_pbp_3yr",
    "team_environment_score",
    "weekly_volatility_3yr",
)

RB_ALLOWED_FEATURES = (
    "profile_points_score",
    "carries",
    "targets",
    "carry_share_slope_3yr",
    "target_share_slope_3yr",
    "rb_high_value_opportunity_score",
    "red_zone_opportunities",
    "goal_line_opportunities",
    "xfp_score_3yr",
    "xfp_share_3yr",
    "high_value_xfp_score_3yr",
    "rushing_xfp_pbp_3yr",
    "receiving_xfp_pbp_3yr",
    "high_value_rush_xfp_score_3yr",
    "high_value_target_xfp_score_3yr",
    "red_zone_xfp_score_3yr",
    "goal_line_xfp_score_3yr",
    "ngs_rushing_efficiency_score_3yr",
    "ngs_rush_yards_over_expected_score_3yr",
    "ngs_box_resilience_score_3yr",
    "team_environment_score",
)

WR_ALLOWED_FEATURES = (
    "profile_points_score",
    "targets",
    "receiving_yards",
    "receiving_epa",
    "red_zone_targets",
    "air_yards",
    "receiving_usage",
    "wopr_slope_3yr",
    "target_share_slope_3yr",
    "receiving_role_dominance_score",
    "xfp_score_3yr",
    "xfp_share_3yr",
    "fantasy_points_over_expectation_3yr",
    "receiving_role_dominance_xfp_3yr",
    "receiving_xfp_pbp_3yr",
    "receiving_xfp_share_pbp_3yr",
    "high_value_target_xfp_score_3yr",
    "receiving_first_down_exp_pbp_3yr",
    "receiving_chain_mover_score_3yr",
    "ngs_receiving_efficiency_score_3yr",
    "ngs_yac_over_expected_score_3yr",
    "ngs_separation_score_3yr",
    "ngs_catch_over_expected_score_3yr",
)

TE_ALLOWED_FEATURES = WR_ALLOWED_FEATURES + (
    "offensive_snap_share_3yr",
    "snap_role_stability_3yr",
    "red_zone_xfp_score_3yr",
    "goal_line_xfp_score_3yr",
)

FEATURE_ALLOWLISTS = {
    "QB": QB_ALLOWED_FEATURES,
    "RB": RB_ALLOWED_FEATURES,
    "WR": WR_ALLOWED_FEATURES,
    "TE": TE_ALLOWED_FEATURES,
}

BLOCKED_FEATURES = frozenset(
    {
        "pigskin_context_score",
        "yprr",
        "yards_per_route_run",
        "tprr",
        "targets_per_route_run",
        "true_route_share",
        "route_share",
        "first_read_share",
        "pressure_epa",
        "covered_receiver_epa",
        "broken_tackle_rate",
        "depth_chart_role_score_3yr",
        "sleeper_current_team",
        "sleeper_current_status",
        "sleeper_status",
        "sleeper_depth_chart_position",
        "sleeper_depth_chart_order",
        "current_team",
        "current_roster_status",
    }
)

STANDARD_ZERO_COVERAGE_DEFERRED_FEATURES = frozenset(
    {
        "ngs_catch_over_expected_score_3yr",
    }
)

PROXY_LABELS = {
    "receiving_first_down_exp_pbp_3yr": "chain-mover proxy",
    "offensive_snap_share_3yr": "snap-role proxy",
}

FORBIDDEN_PROXY_LABELS = {
    "receiving_first_down_exp_pbp_3yr": ("1D/RR", "first downs per route run"),
    "offensive_snap_share_3yr": ("route participation rate",),
}

_FAMILY_FEATURES = {
    "baseline_pigskin_proxies": (
        "profile_points_score",
        "recent_points_avg",
        "team_environment_score",
        "weekly_volatility_3yr",
    ),
    "opportunity": (
        "targets",
        "carries",
        "red_zone_opportunities",
        "goal_line_opportunities",
        "rb_high_value_opportunity_score",
    ),
    "ideal_xfp": (
        "xfp_score_3yr",
        "xfp_share_3yr",
        "high_value_xfp_score_3yr",
        "fantasy_points_over_expectation_3yr",
    ),
    "pbp_xfp": (
        "passing_xfp_pbp_3yr",
        "rushing_xfp_pbp_3yr",
        "receiving_xfp_pbp_3yr",
        "rushing_xfp_share_pbp_3yr",
        "receiving_xfp_share_pbp_3yr",
    ),
    "first_down_proxies": (
        "receiving_first_down_exp_pbp_3yr",
        "receiving_chain_mover_score_3yr",
    ),
    "ngs": (
        "ngs_qb_passing_efficiency_score_3yr",
        "ngs_rushing_efficiency_score_3yr",
        "ngs_rush_yards_over_expected_score_3yr",
        "ngs_box_resilience_score_3yr",
        "ngs_receiving_efficiency_score_3yr",
        "ngs_yac_over_expected_score_3yr",
        "ngs_separation_score_3yr",
        "ngs_catch_over_expected_score_3yr",
    ),
    "role_history": (
        "carry_share_slope_3yr",
        "target_share_slope_3yr",
        "wopr_slope_3yr",
        "offensive_snap_share_3yr",
        "snap_role_stability_3yr",
    ),
    "injury_availability": (
        "injury_risk_score_3yr",
        "injury_status_score_3yr",
        "injury_burden_score_3yr",
        "missed_time_risk_score_3yr",
        "availability_score_3yr",
    ),
}


def model_family_ids() -> tuple[str, ...]:
    return tuple(family.family_id for family in MODEL_FAMILIES)


def features_for_position(position: str) -> tuple[str, ...]:
    normalized = position.upper()
    if normalized not in FEATURE_ALLOWLISTS:
        raise ValueError(f"Unknown BQML v2 position: {position}")
    return FEATURE_ALLOWLISTS[normalized]


def all_predictor_fields() -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for position in POSITIONS:
        for feature in features_for_position(position):
            if feature not in seen:
                seen.add(feature)
                ordered.append(feature)
    return tuple(ordered)


def standard_training_predictor_fields() -> tuple[str, ...]:
    return tuple(
        feature
        for feature in all_predictor_fields()
        if feature not in STANDARD_ZERO_COVERAGE_DEFERRED_FEATURES
    )


def is_blocked_feature(feature_name: str, *, depth_coverage_available: bool = False) -> bool:
    normalized = feature_name.strip().lower()
    if normalized == "depth_chart_role_score_3yr" and depth_coverage_available:
        return False
    return normalized in BLOCKED_FEATURES


def validate_features(
    position: str,
    feature_names: tuple[str, ...] | list[str],
    *,
    depth_coverage_available: bool = False,
) -> tuple[str, ...]:
    allowed = set(features_for_position(position))
    validated: list[str] = []
    for feature_name in feature_names:
        if is_blocked_feature(feature_name, depth_coverage_available=depth_coverage_available):
            raise ValueError(f"{feature_name} is blocked for BQML v2")
        if feature_name in OUTCOME_ONLY_FIELDS:
            raise ValueError(f"{feature_name} is a label or outcome field, not a predictor")
        if feature_name not in allowed:
            raise ValueError(f"{feature_name} is not allowed for BQML v2 {position.upper()}")
        validated.append(feature_name)
    return tuple(validated)


def predictor_fields_for_position(position: str) -> tuple[str, ...]:
    features = features_for_position(position)
    return tuple(feature for feature in features if feature not in OUTCOME_ONLY_FIELDS)


def standard_training_predictor_fields_for_position(position: str) -> tuple[str, ...]:
    return tuple(
        feature
        for feature in predictor_fields_for_position(position)
        if feature not in STANDARD_ZERO_COVERAGE_DEFERRED_FEATURES
    )


def target_fields_for_family(family_id: str) -> tuple[str, ...]:
    families = {family.family_id: family for family in MODEL_FAMILIES}
    if family_id not in families:
        raise ValueError(f"Unknown BQML v2 model family: {family_id}")
    if families[family_id].target_group == "profile_points":
        return ("target_fantasy_points", "value_over_replacement")
    return ("elite_finish_label", "starter_finish_label", "bust_label")


def _quote_table(project_id: str, dataset_id: str, table_name: str) -> str:
    if not project_id or not dataset_id or not table_name:
        raise ValueError("project_id, dataset_id, and table_name are required")
    return f"`{project_id}.{dataset_id}.{table_name}`"


def _select_predictor_columns() -> str:
    return ",\n    ".join(standard_training_predictor_fields())


def _json_missing_flags_expression() -> str:
    return """TO_JSON_STRING(STRUCT(
      profile_points_score IS NULL AS profile_points_score_missing,
      xfp_score_3yr IS NULL AS xfp_score_3yr_missing,
      receiving_xfp_pbp_3yr IS NULL AS receiving_xfp_pbp_3yr_missing,
      rushing_xfp_pbp_3yr IS NULL AS rushing_xfp_pbp_3yr_missing,
      passing_xfp_pbp_3yr IS NULL AS passing_xfp_pbp_3yr_missing,
      receiving_first_down_exp_pbp_3yr IS NULL AS receiving_first_down_exp_pbp_3yr_missing,
      ngs_receiving_efficiency_score_3yr IS NULL AS ngs_receiving_efficiency_score_3yr_missing,
      ngs_rushing_efficiency_score_3yr IS NULL AS ngs_rushing_efficiency_score_3yr_missing,
      ngs_qb_passing_efficiency_score_3yr IS NULL AS ngs_qb_passing_efficiency_score_3yr_missing
    )) AS bqml_v2_missing_flags_json"""


def build_standard_training_dataset_query(
    project_id: str = "fantasy-football-498121",
    dataset_id: str = "fantasy_football_brain",
    *,
    include_order_by: bool = True,
) -> str:
    """Build the Standard-only BQML v2 training dataset query.

    The query selects labels and predictors into separate fields. It does not
    train a model and does not write data.
    """

    mart_table = _quote_table(project_id, dataset_id, "ranking_backtest_feature_mart")
    predictors = _select_predictor_columns()
    missing_flags = _json_missing_flags_expression()
    order_by = "\nORDER BY target_season, target_week, position, player_id_internal" if include_order_by else ""
    return f"""SELECT
    '{BQML_V2_DATASET_VERSION}' AS dataset_version,
    CASE
      WHEN target_season BETWEEN 2017 AND 2023 THEN 'train'
      WHEN target_season = 2024 THEN 'validation'
      WHEN target_season = 2025 THEN 'holdout'
      ELSE 'excluded'
    END AS split,
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
    {predictors},
    target_fantasy_points,
    value_over_replacement,
    IF(actual_position_rank <= CASE position WHEN 'QB' THEN 6 WHEN 'RB' THEN 12 WHEN 'WR' THEN 12 WHEN 'TE' THEN 6 END, 1, 0) AS elite_finish_label,
    IF(actual_position_rank <= CASE position WHEN 'QB' THEN 12 WHEN 'RB' THEN 24 WHEN 'WR' THEN 36 WHEN 'TE' THEN 12 END, 1, 0) AS starter_finish_label,
    IF(
      target_fantasy_points < COALESCE(replacement_points, target_fantasy_points)
      OR actual_position_rank > CASE position WHEN 'QB' THEN 24 WHEN 'RB' THEN 48 WHEN 'WR' THEN 72 WHEN 'TE' THEN 24 END,
      1,
      0
    ) AS bust_label,
    predictor_missing_flags_json,
    outcome_missing_flags_json,
    source_freshness_json,
    provenance_json,
    {missing_flags}
FROM {mart_table}
WHERE scoring_profile_id = '{STANDARD_SCORING_PROFILE}'
  AND position IN ('QB', 'RB', 'WR', 'TE')
  AND target_season BETWEEN 2017 AND 2025
  AND source_window_end_season < target_season
  AND league_type_id = '{LEAGUE_TYPE_ID}'
  AND roster_format_id = '{ROSTER_FORMAT_ID}'{order_by}"""


def build_standard_coverage_query(
    project_id: str = "fantasy-football-498121",
    dataset_id: str = "fantasy_football_brain",
) -> str:
    dataset_query = build_standard_training_dataset_query(project_id, dataset_id, include_order_by=False)
    return f"""WITH standard_dataset AS (
{dataset_query}
)
SELECT
  split,
  position,
  target_season,
  COUNT(*) AS record_count,
  COUNTIF(profile_points_score IS NOT NULL) AS baseline_feature_count,
  COUNTIF(targets IS NOT NULL OR carries IS NOT NULL OR rb_high_value_opportunity_score IS NOT NULL) AS opportunity_feature_count,
  COUNTIF(xfp_score_3yr IS NOT NULL OR high_value_xfp_score_3yr IS NOT NULL) AS ideal_xfp_feature_count,
  COUNTIF(passing_xfp_pbp_3yr IS NOT NULL OR rushing_xfp_pbp_3yr IS NOT NULL OR receiving_xfp_pbp_3yr IS NOT NULL) AS pbp_xfp_feature_count,
  COUNTIF(receiving_first_down_exp_pbp_3yr IS NOT NULL OR receiving_chain_mover_score_3yr IS NOT NULL) AS first_down_proxy_feature_count,
  COUNTIF(ngs_qb_passing_efficiency_score_3yr IS NOT NULL OR ngs_rushing_efficiency_score_3yr IS NOT NULL OR ngs_receiving_efficiency_score_3yr IS NOT NULL) AS ngs_feature_count,
  COUNTIF(carry_share_slope_3yr IS NOT NULL OR target_share_slope_3yr IS NOT NULL OR wopr_slope_3yr IS NOT NULL OR offensive_snap_share_3yr IS NOT NULL) AS role_history_feature_count,
  COUNTIF(target_fantasy_points IS NULL OR value_over_replacement IS NULL) AS missing_label_count
FROM standard_dataset
GROUP BY split, position, target_season
ORDER BY target_season, split, position"""


def build_blocked_field_probe_query(
    project_id: str = "fantasy-football-498121",
    dataset_id: str = "fantasy_football_brain",
) -> str:
    mart_table = _quote_table(project_id, dataset_id, "ranking_backtest_feature_mart")
    return f"""SELECT
  COUNTIF(depth_chart_role_score_3yr IS NOT NULL) AS depth_context_non_null_count,
  COUNTIF(injury_risk_score_3yr IS NOT NULL) AS injury_risk_non_null_count,
  COUNT(*) AS record_count
FROM {mart_table}
WHERE scoring_profile_id = '{STANDARD_SCORING_PROFILE}'
  AND position IN ('QB', 'RB', 'WR', 'TE')
  AND target_season BETWEEN 2017 AND 2025
  AND source_window_end_season < target_season
  AND league_type_id = '{LEAGUE_TYPE_ID}'
  AND roster_format_id = '{ROSTER_FORMAT_ID}'"""


def build_standard_integrity_query(
    project_id: str = "fantasy-football-498121",
    dataset_id: str = "fantasy_football_brain",
) -> str:
    dataset_query = build_standard_training_dataset_query(project_id, dataset_id, include_order_by=False)
    return f"""WITH standard_dataset AS (
{dataset_query}
),
grain AS (
  SELECT
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    position,
    target_season,
    target_week,
    player_id_internal,
    COUNT(*) AS grain_record_count
  FROM standard_dataset
  GROUP BY scoring_profile_id, league_type_id, roster_format_id, position, target_season, target_week, player_id_internal
)
SELECT
  COUNT(*) AS record_count,
  COUNTIF(source_window_end_season >= target_season) AS leakage_window_count,
  COUNTIF(player_id_internal IS NULL OR player_id_internal = '') AS missing_player_id_count,
  COUNTIF(scoring_profile_id IS NULL OR scoring_profile_id = '') AS missing_scoring_profile_count,
  COUNTIF(target_fantasy_points IS NULL OR value_over_replacement IS NULL) AS missing_target_label_count,
  (SELECT COUNT(*) FROM grain WHERE grain_record_count > 1) AS duplicate_grain_count
FROM standard_dataset"""


def build_standard_sample_query(
    project_id: str = "fantasy-football-498121",
    dataset_id: str = "fantasy_football_brain",
    *,
    per_position_limit: int = 5,
) -> str:
    if per_position_limit < 1 or per_position_limit > 25:
        raise ValueError("per_position_limit must be between 1 and 25")
    dataset_query = build_standard_training_dataset_query(project_id, dataset_id, include_order_by=False)
    return f"""WITH standard_dataset AS (
{dataset_query}
),
ranked AS (
  SELECT
    split,
    target_season,
    target_week,
    source_window_start_season,
    source_window_end_season,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    position,
    player_id_internal,
    player_name,
    profile_points_score,
    recent_points_avg,
    team_environment_score,
    xfp_score_3yr,
    receiving_xfp_pbp_3yr,
    rushing_xfp_pbp_3yr,
    passing_xfp_pbp_3yr,
    target_fantasy_points,
    value_over_replacement,
    elite_finish_label,
    starter_finish_label,
    bust_label,
    bqml_v2_missing_flags_json,
    ROW_NUMBER() OVER (
      PARTITION BY position
      ORDER BY target_season DESC, target_week DESC, player_id_internal
    ) AS position_sample_rank
  FROM standard_dataset
)
SELECT * EXCEPT(position_sample_rank)
FROM ranked
WHERE position_sample_rank <= {per_position_limit}
ORDER BY position, target_season DESC, target_week DESC, player_id_internal"""


def build_standard_model_sql_templates(
    project_id: str = "fantasy-football-498121",
    dataset_id: str = "fantasy_football_brain",
    *,
    model_suffix: str = STANDARD_MODEL_SUFFIX,
) -> dict[str, str]:
    dataset_query = build_standard_training_dataset_query(project_id, dataset_id, include_order_by=False)
    templates: dict[str, str] = {}
    for position in POSITIONS:
        predictor_list = ",\n    ".join(standard_training_predictor_fields_for_position(position))
        position_lower = position.lower()
        base_select = f"""WITH standard_dataset AS (
{dataset_query}
)
SELECT
    {predictor_list},
    {{label_field}}
FROM standard_dataset
WHERE split = 'train'
  AND position = '{position}'"""
        templates[f"standard_{position_lower}_linear_points"] = f"""CREATE OR REPLACE MODEL `{project_id}.{dataset_id}.ranking_bqml_v2_standard_{position_lower}_linear_points_{model_suffix}`
OPTIONS(
  model_type = 'LINEAR_REG',
  input_label_cols = ['target_fantasy_points'],
  data_split_method = 'NO_SPLIT'
) AS
{base_select.format(label_field='target_fantasy_points')}"""
        templates[f"standard_{position_lower}_linear_vor"] = f"""CREATE OR REPLACE MODEL `{project_id}.{dataset_id}.ranking_bqml_v2_standard_{position_lower}_linear_vor_{model_suffix}`
OPTIONS(
  model_type = 'LINEAR_REG',
  input_label_cols = ['value_over_replacement'],
  data_split_method = 'NO_SPLIT'
) AS
{base_select.format(label_field='value_over_replacement')}"""
        templates[f"standard_{position_lower}_logistic_elite"] = f"""CREATE OR REPLACE MODEL `{project_id}.{dataset_id}.ranking_bqml_v2_standard_{position_lower}_logistic_elite_{model_suffix}`
OPTIONS(
  model_type = 'LOGISTIC_REG',
  input_label_cols = ['elite_finish_label'],
  data_split_method = 'NO_SPLIT'
) AS
{base_select.format(label_field='elite_finish_label')}"""
        templates[f"standard_{position_lower}_logistic_bust"] = f"""CREATE OR REPLACE MODEL `{project_id}.{dataset_id}.ranking_bqml_v2_standard_{position_lower}_logistic_bust_{model_suffix}`
OPTIONS(
  model_type = 'LOGISTIC_REG',
  input_label_cols = ['bust_label'],
  data_split_method = 'NO_SPLIT'
) AS
{base_select.format(label_field='bust_label')}"""
    return templates


def standard_model_specs(*, model_suffix: str = STANDARD_MODEL_SUFFIX) -> tuple[dict[str, str], ...]:
    specs: list[dict[str, str]] = []
    for position in POSITIONS:
        position_lower = position.lower()
        specs.extend(
            [
                {
                    "candidate_id": f"bqml_v2_standard_{position_lower}_linear_points_{model_suffix}",
                    "candidate_family": "bqml_v2_standard_linear_points",
                    "model_name": f"ranking_bqml_v2_standard_{position_lower}_linear_points_{model_suffix}",
                    "position": position,
                    "model_type": "LINEAR_REG",
                    "label_field": "target_fantasy_points",
                    "prediction_column": "predicted_target_fantasy_points",
                    "higher_is_better": "true",
                },
                {
                    "candidate_id": f"bqml_v2_standard_{position_lower}_linear_vor_{model_suffix}",
                    "candidate_family": "bqml_v2_standard_linear_vor",
                    "model_name": f"ranking_bqml_v2_standard_{position_lower}_linear_vor_{model_suffix}",
                    "position": position,
                    "model_type": "LINEAR_REG",
                    "label_field": "value_over_replacement",
                    "prediction_column": "predicted_value_over_replacement",
                    "higher_is_better": "true",
                },
                {
                    "candidate_id": f"bqml_v2_standard_{position_lower}_logistic_elite_{model_suffix}",
                    "candidate_family": "bqml_v2_standard_logistic_elite",
                    "model_name": f"ranking_bqml_v2_standard_{position_lower}_logistic_elite_{model_suffix}",
                    "position": position,
                    "model_type": "LOGISTIC_REG",
                    "label_field": "elite_finish_label",
                    "prediction_column": "predicted_elite_finish_label_probs",
                    "higher_is_better": "true",
                },
                {
                    "candidate_id": f"bqml_v2_standard_{position_lower}_logistic_bust_inverse_{model_suffix}",
                    "candidate_family": "bqml_v2_standard_logistic_bust_inverse",
                    "model_name": f"ranking_bqml_v2_standard_{position_lower}_logistic_bust_{model_suffix}",
                    "position": position,
                    "model_type": "LOGISTIC_REG",
                    "label_field": "bust_label",
                    "prediction_column": "predicted_bust_label_probs",
                    "higher_is_better": "false",
                },
            ]
        )
    return tuple(specs)


def assert_standard_query_leakage_safe(sql: str) -> None:
    lowered = sql.lower()
    for blocked_feature in BLOCKED_FEATURES:
        if blocked_feature in lowered:
            raise ValueError(f"Blocked field appears in Standard BQML v2 query: {blocked_feature}")
    if "scoring_profile_id = 'standard'" not in lowered:
        raise ValueError("Standard BQML v2 query must filter scoring_profile_id = 'standard'")
    if "source_window_end_season < target_season" not in lowered:
        raise ValueError("Standard BQML v2 query must enforce source_window_end_season < target_season")
    if "2026" in lowered:
        raise ValueError("Standard BQML v2 query must not use 2026 outcomes")


def feature_family_map() -> dict[str, tuple[str, ...]]:
    return {family: tuple(features) for family, features in _FAMILY_FEATURES.items()}
