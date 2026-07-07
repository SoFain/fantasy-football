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

## Phase 33.4 Source-Gap Audit

Phase 33.4 audited the seven zero-coverage fields deferred in Phase 33.3. No model was trained and no feature mart refresh ran.

Field decisions:

| Field | Classification | Decision |
|---|---|---|
| `passing_epa_per_play` | recoverable from existing warehouse / nflverse player stats | Defer to additive feature-mart patch. Source exists as `passing_epa` in weekly player stats and as passer EPA events. |
| `receiving_yards` | recoverable from existing warehouse / nflverse player stats | Defer to additive feature-mart patch. Source exists in `stg_player_week_stats` and `player_week_opportunity_metrics`. |
| `receiving_epa` | recoverable from nflverse player stats and staging events | Defer to additive feature-mart patch. Source exists in weekly player stats and receiver EPA events. |
| `red_zone_targets` | recoverable from PBP yardline derivation | Defer to additive feature-mart patch. Existing red-zone flags are not populated, but yardline-derived target events exist. |
| `red_zone_opportunities` | recoverable from PBP yardline derivation | Defer to additive feature-mart patch. Use target plus rusher events with `yardline_100 <= 20`. |
| `goal_line_opportunities` | recoverable from PBP yardline derivation | Defer to additive feature-mart patch. Use rush events with `yardline_100 <= 5` or a clearly named broader goal-line rule if approved. |
| `ngs_catch_over_expected_score_3yr` | unavailable in public loaded NGS lane | Keep deferred. Public receiving NGS loaded here has catch percentage and expected YAC fields, not expected catch or catch-over-expected. |

The Standard training SQL remains unchanged for Phase 33.4: zero-coverage fields stay excluded until an additive, leakage-safe feature-mart patch proves coverage.

## Phase 33.5 Standard Training Result

Phase 33.5 trained the first Standard-only BQML v2 model set. No live ranking table changed and no champion was activated.

Model set:

- `ranking_bqml_v2_standard_qb_linear_points_v0`
- `ranking_bqml_v2_standard_qb_linear_vor_v0`
- `ranking_bqml_v2_standard_qb_logistic_elite_v0`
- `ranking_bqml_v2_standard_qb_logistic_bust_v0`
- Same four families for RB, WR, and TE.

Summary evidence was written only to `ranking_backtest_runs` and `ranking_backtest_candidate_summaries` as `ranking_backtest_sql_native_bqml_v2_standard_v0`. No detail rows were written.

Position labels:

| Position | Best Standard v2 lane | Label | Notes |
|---|---|---|---|
| QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | owner-review challenger | Beats Current Pigskin but trails prior enriched/NGS BQML linear points on combined 2024-2025 VOR. |
| RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | owner-review challenger | Best Standard comparison by combined VOR capture and points capture. |
| WR | `bqml_v2_standard_wr_logistic_elite_v0` | owner-review challenger | Best Standard comparison by combined VOR capture. |
| TE | `bqml_v2_standard_te_linear_points_v0` | owner-review challenger | Best TE comparison and clear lift over Current Pigskin. |

Next recommended step: generate Standard owner-review boards for the four selected challenger lanes, while separately planning the EPA/red-zone/receiving feature-mart patch.

## Phase 33.6 Standard Owner-Review Boards

Phase 33.6 generated Standard-only owner-review boards from the existing Phase 33.5 BQML models. It did not train models, write live rankings, activate champions, call Gemini, call Pigskin chat, call Sleeper, ingest sources, or deploy.

Owner-review board file:

- `docs/rebuild/standard-bqml-v2-owner-review-boards.md`

Generation shape:

- 8,088 weekly BQML prediction rows read from `ML.PREDICT`.
- 783 player-season rows after aggregating weekly predictions to one owner-review row per player, season, candidate, and position.
- 10 selected summary rows read from `ranking_backtest_candidate_summaries`.
- Review limits: QB45, RB80, WR100, TE35.
- Scoring profile: `standard` only.

Phase 33.6 owner-review finalists:

| Position | Finalist | Phase 33.6 status |
|---|---|---|
| QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | owner-review only, with quality warnings. |
| RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | owner-review only, with 2025 VOR denominator and board-shape warnings. |
| WR | `bqml_v2_standard_wr_logistic_elite_v0` | strongest owner-review finalist in this cut. |
| TE | `bqml_v2_standard_te_logistic_bust_inverse_v0` | selected over linear points for owner review because 2025 holdout VOR is stronger and the lane is risk-aware. |

TE decision:

- `bqml_v2_standard_te_linear_points_v0` remains useful component evidence.
- It is not the Phase 33.6 TE finalist because its persisted pairwise fields are null and the bust-inverse lane has stronger 2025 holdout VOR.

Activation policy:

- No Standard BQML v2 candidate is a champion yet.
- The generated boards are owner-review evidence, not a live overall-board builder.
- A production-grade Standard overall board still needs an owner-approved VOR, scarcity, and cutline rule.

## Phase 33.7 EPA, Receiving, Red-Zone Patch

Phase 33.7 patched six recoverable fields into the ranking research feature path without training models, changing live rankings, activating champions, calling Gemini, calling Pigskin chat, calling Sleeper, or deploying.

Patched feature sources:

| Field | Source-backed implementation |
|---|---|
| `passing_epa_per_play` | `stg_play_player_events` passer EPA divided by passer event count, bounded to historical source windows only. |
| `receiving_yards` | `stg_player_week_stats.receiving_yards`, clamped at zero for the feature contract. |
| `receiving_epa` | `stg_play_player_events` receiver EPA, with existing truth fallback. |
| `red_zone_targets` | `stg_play_player_events` target events where `yardline_100 <= 20`. |
| `red_zone_opportunities` | target plus rusher events where `yardline_100 <= 20`. |
| `goal_line_opportunities` | target plus rusher events where `yardline_100 <= 5`. |

The patch refreshed `ranking_backtest_feature_mart` for `standard`, `half_ppr`, `ppr`, and `gng_keeper`, target seasons 2017-2025, positions QB/RB/WR/TE. Total refreshed rows: 156,244.

Standard BQML v2 training predictors increased from 41 to 47. The added predictors are position-specific:

- QB: `passing_epa_per_play`
- RB: `red_zone_opportunities`, `goal_line_opportunities`
- WR: `receiving_yards`, `receiving_epa`, `red_zone_targets`
- TE: `receiving_yards`, `receiving_epa`, `red_zone_targets`

`ngs_catch_over_expected_score_3yr` remains blocked. The loaded public NGS lane still lacks a real catch-over-expected source field.

Standard dataset dry-run after the patch:

| Check | Result |
|---|---:|
| Predictor count before | 41 |
| Predictor count after | 47 |
| Standard training dataset dry-run bytes | 1,219,493,385 |
| Standard coverage dry-run bytes | 26,143,117 |
| Standard integrity dry-run bytes | 12,851,069 |
| Standard integrity rows | 39,061 |
| Leakage rows | 0 |
| Duplicate grain rows | 0 |
| Missing labels | 0 |

These fields are ready for a separate Standard BQML v2 retrain phase. They are not a champion-selection result.

## Phase 33.8 Patched Standard BQML V2 Retrain

Phase 33.8 trained the 47-predictor Standard BQML v2 patched model set after the Phase 33.7 EPA, receiving, red-zone, and goal-line feature-mart patch. It did not deploy, write live rankings, activate champions, call Gemini, call Pigskin chat, call Sleeper, run source ingest, or write backtest detail rows.

Training scope:

| Scope | Result |
|---|---:|
| Scoring profile | `standard` |
| Positions | QB, RB, WR, TE |
| Model families | linear points, linear VOR, logistic elite, logistic bust |
| Models trained | 16 |
| Training seasons | 2017-2023 |
| Evaluation seasons | 2024 validation, 2025 holdout |
| Standard predictor count | 47 |
| Summary runs written | 2 |
| Candidate summary rows written | 32 |
| Detail rows written | 0 |
| Live ranking rows written | 0 |
| Champion rows written | 0 |

Formula version written to summary tables:

- `ranking_backtest_sql_native_bqml_v2_standard_patched_v0`

Controlled write:

- Authorization gate: `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`, set only inside the write command process.
- Write job: `ba463b16-a0aa-46aa-8ebf-94a74df4d212`.
- Gate was removed after the write.
- Write targets were limited to `ranking_backtest_runs` and `ranking_backtest_candidate_summaries`.

Patch outcome versus original Standard v2:

| Season | Position | Best patched signal | Decision read |
|---|---|---|---|
| 2024 | QB | Linear points slightly improved points and VOR capture, but original retained top-N and NDCG edge. | mixed |
| 2024 | RB | Patched logistic elite led top-N and points capture. | useful challenger |
| 2024 | WR | Patched linear points led top-N and points capture, but original logistic elite retained VOR and NDCG edge. | mixed |
| 2024 | TE | Original Standard v2 linear points still led top-N, points, VOR, and NDCG. | patch regressed TE 2024 |
| 2025 | QB | Original Standard v2 logistic bust inverse still led top-N, points, VOR, and NDCG. | original remains stronger |
| 2025 | RB | Both original and patched hit perfect top-N and points in the slice; original retained higher NDCG. | no clear replacement |
| 2025 | WR | Patched bust inverse led points and VOR; original logistic elite retained top-N and NDCG. | mixed |
| 2025 | TE | Patched bust inverse led top-N, points, VOR, and NDCG. | useful challenger |

Observed feature weights show the patched fields are active in the trained models:

- RB logistic elite emphasized `target_share_slope_3yr`, `xfp_share_3yr`, `carry_share_slope_3yr`, `red_zone_opportunities`, and `receiving_xfp_pbp_3yr`.
- WR logistic bust emphasized `target_share_slope_3yr`, `wopr_slope_3yr`, `xfp_share_3yr`, `receiving_xfp_share_pbp_3yr`, `air_yards`, and `receiving_epa`.
- TE logistic bust emphasized `target_share_slope_3yr`, `xfp_share_3yr`, `wopr_slope_3yr`, `air_yards`, `receiving_xfp_share_pbp_3yr`, and `receiving_epa`.
- QB linear points used `passing_epa_per_play`, but the coefficient direction and QB comparison remain noisy.

Decision: patched Standard BQML v2 is ready for owner review with warnings. It should not replace the original Standard v2 or Current Pigskin automatically. Use it as a position-specific challenger set, especially RB 2024 and TE 2025, then build owner-review boards before any champion decision.

## Phase 33.9 Original vs Patched Standard Review

Phase 33.9 compared original Standard v2 against patched Standard v2 at the owner-review board level. It used existing trained models, read-only `ML.PREDICT`, persisted summary evidence, and generated local board evidence. It did not train models, write live rankings, activate champions, deploy, call Gemini, call Pigskin chat, call Sleeper, or write detail rows.

Selected Standard owner-review finalists:

| Position | Finalist | Decision |
|---|---|---|
| QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | Keep original. Patched QB does not improve enough and remains noisy. |
| RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | Keep original. Patched logistic elite is component evidence, not the finalist. |
| WR | `bqml_v2_standard_wr_logistic_elite_v0` | Keep original. Patched bust inverse helps 2025 points/VOR but loses enough top-N/NDCG context to stay secondary. |
| TE | `bqml_v2_standard_te_logistic_bust_inverse_v0` | Keep original risk-aware finalist. Patched bust inverse and original linear points remain component evidence. |

Architecture decision:

- Standard position finalists are ready for owner review.
- Standard BQML v2 is not ready for activation.
- A Standard overall-board rule is still required before champion-selection review.
- The overall rule should use VOR, scarcity, cutline context, bust-safety context, and deterministic tie-breakers.

## Phase 33.10 Standard Overall-Board Rule Prototype

Phase 33.10 tested transparent Standard-only overall board rules from the Phase 33.9 original Standard v2 finalists. It used existing models, read-only `ML.PREDICT`, and `ranking_backtest_feature_mart`. It did not train models, write live rankings, activate champions, deploy, call Gemini, call Pigskin chat, call Sleeper, ingest source data, or write backtest detail rows.

Selected owner-review rule:

- `standard_bqml_v2_conservative_overlay_v0`

Formula shape:

- 70 percent Current Pigskin normalized score.
- 20 percent BQML VOR score.
- 10 percent BQML finalist safety or elite score.

Combined 2024-2025 comparison:

| Rule | Top-24 | Top-50 | Top-100 | Points cap100 | VOR cap100 | Missing | Extreme top100 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Conservative overlay | 0.479 | 0.560 | 0.810 | 1.022 | 1.081 | 0.003 | 0 |
| Current Pigskin baseline | 0.417 | 0.550 | 0.810 | 1.001 | 1.074 | 0.003 | 0 |

VOR-only and points-to-VOR rules are not ready. VOR-only trailed the baseline on top-100 and VOR capture. Points-to-VOR was sensitive to replacement policy and weaker in early board hit rates.

Draft Priority Index remains display-only. It is not the evaluation source of truth.

Standard can move to owner champion-selection review with warnings. Current Pigskin remains live until a separate owner-approved activation phase.

## Phase 33.11 Standard 2026 Overlay Board

Phase 33.11 generated an outcome-free Standard 2026 owner-review board from active Current Pigskin rows plus the latest pre-2026 feature-mart predictors. It used read-only `ML.PREDICT`; no model was trained and no live ranking table changed.

Board artifact:

- `docs/rebuild/standard-bqml-v2-2026-conservative-overlay-review-board.md`

Result:

- 260 active Standard rows reviewed.
- QB45, RB80, WR100, TE35 baseline shape confirmed.
- 82 rows had no feature-mart match.
- 46 players moved more than 20 overall spots.
- Top 24 shifted to QB9, RB8, WR5, TE2.

Architecture decision: the conservative overlay is useful, but not ready for champion selection without rule refinement. Current Pigskin should hold for Standard.
