# BQML V2 Ranking Architecture

## Purpose

BQML v2 is a source-backed research lane for future player ranking models. It does not replace the current Pigskin ranking baseline, does not activate champions, and does not change live ranking tables by itself.

The first build target is a Standard scoring training dataset. Other scoring profiles can follow only after Standard passes coverage, leakage, cost, and owner-review checks.

## Core Policy

- Standard is first. Scoring profile display and review order is `standard`, `half_ppr`, `ppr`, then `gng_keeper`.
- Models are position-specific and scoring-profile-specific.
- There is no global all-profile winner. All-profile aggregate results are context only.
- Source-backed fields are required. Theory features are not official predictors until the warehouse proves a real source and coverage.
- Current Sleeper context is live display context only. It is not historical truth and must not be used as a historical predictor.
- `pigskin_context_score` is deprecated for this lane and is blocked.

## Model Families

Initial Standard families:

| Family | Position | Target group | Initial model types |
|---|---|---|---|
| `bqml_v2_qb_profile_points` | QB | fantasy points and VOR | `LINEAR_REG` |
| `bqml_v2_qb_elite_bust` | QB | elite, starter, bust labels | `LOGISTIC_REG` |
| `bqml_v2_rb_profile_points` | RB | fantasy points and VOR | `LINEAR_REG` |
| `bqml_v2_rb_elite_bust` | RB | elite, starter, bust labels | `LOGISTIC_REG` |
| `bqml_v2_wr_profile_points` | WR | fantasy points and VOR | `LINEAR_REG` |
| `bqml_v2_wr_elite_bust` | WR | elite, starter, bust labels | `LOGISTIC_REG` |
| `bqml_v2_te_profile_points` | TE | fantasy points and VOR | `LINEAR_REG` |
| `bqml_v2_te_elite_bust` | TE | elite, starter, bust labels | `LOGISTIC_REG` |

Boosted tree models are deferred until the linear and logistic Standard baseline passes cost and sanity checks. DNN, AutoML, remote models, Gemini-backed models, and broad hyperparameter tuning are blocked.

## Feature Allowlists

The code source of truth is `src/bqml_v2_feature_contract.py`.

QB predictors:

- `profile_points_score`
- `recent_points_avg`
- `passing_epa_per_play`
- `cpoe`
- `ngs_qb_passing_efficiency_score_3yr`
- `passing_xfp_pbp_3yr`
- `rushing_attempts`
- `qb_rushing_leverage_index`
- `rushing_xfp_pbp_3yr`
- `rushing_xfp_share_pbp_3yr`
- `team_environment_score`
- `weekly_volatility_3yr`

RB predictors:

- `profile_points_score`
- `carries`
- `targets`
- `carry_share_slope_3yr`
- `target_share_slope_3yr`
- `rb_high_value_opportunity_score`
- `red_zone_opportunities`
- `goal_line_opportunities`
- `xfp_score_3yr`
- `xfp_share_3yr`
- `high_value_xfp_score_3yr`
- `rushing_xfp_pbp_3yr`
- `receiving_xfp_pbp_3yr`
- `high_value_rush_xfp_score_3yr`
- `high_value_target_xfp_score_3yr`
- `red_zone_xfp_score_3yr`
- `goal_line_xfp_score_3yr`
- `ngs_rushing_efficiency_score_3yr`
- `ngs_rush_yards_over_expected_score_3yr`
- `ngs_box_resilience_score_3yr`
- `team_environment_score`

WR predictors:

- `profile_points_score`
- `targets`
- `receiving_yards`
- `receiving_epa`
- `red_zone_targets`
- `air_yards`
- `receiving_usage`
- `wopr_slope_3yr`
- `target_share_slope_3yr`
- `receiving_role_dominance_score`
- `xfp_score_3yr`
- `xfp_share_3yr`
- `fantasy_points_over_expectation_3yr`
- `receiving_role_dominance_xfp_3yr`
- `receiving_xfp_pbp_3yr`
- `receiving_xfp_share_pbp_3yr`
- `high_value_target_xfp_score_3yr`
- `receiving_first_down_exp_pbp_3yr`
- `receiving_chain_mover_score_3yr`
- `ngs_receiving_efficiency_score_3yr`
- `ngs_yac_over_expected_score_3yr`
- `ngs_separation_score_3yr`
- `ngs_catch_over_expected_score_3yr`

TE predictors use the valid WR receiving fields where present, plus:

- `offensive_snap_share_3yr`
- `snap_role_stability_3yr`
- `red_zone_xfp_score_3yr`
- `goal_line_xfp_score_3yr`

## Blocked Features

These are blocked as official v2 predictors:

- `pigskin_context_score`
- `yprr`
- `yards_per_route_run`
- `tprr`
- `targets_per_route_run`
- `true_route_share`
- `route_share`
- `first_read_share`
- `pressure_epa`
- `covered_receiver_epa`
- `broken_tackle_rate`
- `depth_chart_role_score_3yr` until source coverage exists
- Sleeper current team, status, or depth fields as historical predictors

Proxy naming rules:

- `receiving_first_down_exp_pbp_3yr` is a chain-mover proxy. Do not call it `1D/RR`.
- `offensive_snap_share_3yr` is a snap-role proxy. Do not call it route participation rate.

## Target Contract

Allowed labels:

- `target_fantasy_points`
- `value_over_replacement`
- `elite_finish_label`
- `starter_finish_label`
- `bust_label`

Target and outcome fields are labels only. They must not be predictors. Actual ranks, actual pick bands, replacement points, and target-season fantasy points are excluded from predictor allowlists.

Initial split:

| Split | Target seasons |
|---|---|
| train | 2017-2023 |
| validation | 2024 |
| holdout | 2025 |

The dataset requires `source_window_end_season < target_season`.

## Standard Dry-Run Dataset

Dataset query version: `bqml_v2_standard_training_dataset_v0`.

Scope:

- `scoring_profile_id = 'standard'`
- positions QB, RB, WR, TE
- target seasons 2017 through 2025
- `league_type_id = 'redraft'`
- `roster_format_id = 'one_qb'`

The query outputs identifiers, split, position, scoring profile, predictor fields, label fields, missing flags, source window bounds, and source provenance. It does not train models and does not write rows.

## Expansion Rules

Half PPR, PPR, and GNG Keeper can be added after Standard passes:

- dry-run query validation
- leakage checks
- source coverage review
- owner-review cost check
- model sanity checks

Each profile must be evaluated separately. Do not silently fall back to PPR. Do not average profiles into a single champion.

## Phase 33.3 Standard Dataset Readiness

Phase 33.3 committed the Phase 33.2 contract package as `88963a3 phase 33.2 add bqml v2 feature contract`, then ran the Standard-only dataset readiness pass.

Standard training dataset status:

| Check | Result |
|---|---|
| Standard training predictor columns | 41 |
| Missing predictor columns | 0 |
| Predictor types | 41 `FLOAT` |
| Estimated training-query bytes | 1,201,855,586 |
| Total Standard rows | 39,061 |
| Duplicate grain rows | 0 |
| Missing player IDs | 0 |
| Missing scoring profiles | 0 |
| Missing target labels | 0 |
| Leakage window rows | 0 |

Zero-coverage fields deferred from the initial Standard training dataset:

- `passing_epa_per_play`
- `red_zone_opportunities`
- `goal_line_opportunities`
- `receiving_yards`
- `receiving_epa`
- `red_zone_targets`
- `ngs_catch_over_expected_score_3yr`

These fields remain future-eligible in the broader source-backed allowlist, but the Standard v2 training query and model templates do not use them until coverage exists.

Readiness by position:

| Position | Readiness | Notes |
|---|---|---|
| QB | ready | 11 predictors, no zero-coverage fields, minimum feature coverage 96.3 percent. |
| RB | ready with warnings | 19 predictors, no zero-coverage fields. NGS yards-over-expected coverage is 62.0 percent, so NGS should stay optional/missing-flagged. |
| WR | ready with warnings | 19 predictors, no zero-coverage fields. WOPR and target-share coverage are below 90 percent, NGS receiving fields are about 86.4 percent. |
| TE | ready with warnings | 23 predictors, no zero-coverage fields. NGS receiving coverage is about 71.9 percent and role-history coverage is below 90 percent. |

Prepared but not executed:

- Standard QB/RB/WR/TE linear points templates.
- Standard QB/RB/WR/TE linear VOR templates.
- Standard QB/RB/WR/TE logistic elite templates.
- Standard QB/RB/WR/TE logistic bust templates.

Training policy for the next phase remains `data_split_method = NO_SPLIT`, train rows only for model creation, validation and holdout only for later evaluation, and no 2025 holdout tuning.
