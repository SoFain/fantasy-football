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
- Phase 33.31 keeps top-100 cleanup candidates in review-only status. Current Pigskin remains live until QB/WR tripwire caps, Half PPR Breece Hall context, market-only prospect policy, and exact identity/display checks are resolved.
- Phase 33.32 keeps transparent Standard RB formulas in episode-discussion status only. The receiving-back protection formula is useful as a narrow concept, but it is not an active champion, not a top-100 input, and not live-ready.

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

## Phase 33.12 Standard Overlay Calibration

Phase 33.12 calibrated the Standard 2026 overlay without training models or changing live rankings.

Selected owner-review calibration:

- `overlay_80_15_5_anchor_v0`
- 80 percent Current Pigskin normalized score.
- 15 percent BQML VOR normalized score.
- 5 percent finalist safety or elite signal.

Calibration read:

- Phase 33.11 movement was mainly caused by uncalibrated cross-position BQML VOR. QB and RB VOR values sit higher on the global normalized scale than WR and TE.
- The 80/15/5 anchor reduced rank deltas over 20 from 58 to 21 in the rerun comparison.
- QB top-24 count fell from 8 to 6.
- WR/TE current top-24 exits fell from 7 to 4.

Architecture decision: Standard can move to a safer owner-review board, but not champion selection. Historical proxy evaluation still needs a stronger live-like baseline before activation. Current Pigskin remains live.

## Phase 33.13 Profile-Specific Positional Formula Expansion

Phase 33.13 extended the BQML v2 positional architecture to Half PPR, PPR, and GNG Keeper. It trained 48 bounded profile-position models:

- 3 scoring profiles.
- 4 positions.
- 4 model families per profile-position: linear points, linear VOR, logistic elite, logistic bust.

Summary-only evidence was written as `ranking_backtest_sql_native_bqml_v2_profile_positional_v0`.

Write targets:

- `ranking_backtest_runs`: 3 rows.
- `ranking_backtest_candidate_summaries`: 144 rows.
- `ranking_backtest_results`: 0 rows.
- `ranking_formula_champions`: 0 rows.
- `analytics_pigskin_rankings`: 0 rows.

## Advanced Metrics v1 Integration (Phase 33.17)

The feature contract is updated to support training BQML v2 models directly from the `advanced_player_metrics_v1` warehouse, replacing scattered/ad hoc feature-mart fields with audited rolling 3-year averages.
* **Standard-First**: Standard scoring remains the baseline split for training.
* **Route Metrics**: Route-dependent metrics (`routes_run`, `yprr`, `tprr`, `receiving_first_downs_per_route`, `route_participation_rate`) remain strictly **BLOCKED** and mapped to `NULL`.
* **Top-100**: Top-100 interleaving is deferred.

Architecture decision: BQML v2 positional formulas are ready for owner-review boards with warnings. Top-100 work is deferred. The future top-100 builder must use position-locked queues and must not reorder players inside a position.

## Phase 33.18 & 33.18B Advanced BQML v2 Model Expansion

Phase 33.18 and 33.18B completed the training and evaluation of the 64 positional models using the rolling 3-year advanced player metrics.

Summary persistence:
- `ranking_backtest_runs`: 12 rows written (4 validation, 4 holdout, 4 combined)
- `ranking_backtest_candidate_summaries`: 256 rows written

Selected advanced owner-review finalists (Phase 33.18B):
- Standard: QB `adv_standard_qb_logistic_bust`, RB `adv_standard_rb_linear_points`, WR `adv_standard_wr_logistic_elite`, TE `adv_standard_te_linear_points`.
- Half PPR: QB `adv_half_ppr_qb_logistic_bust`, RB `adv_half_ppr_rb_linear_vor`, WR `adv_half_ppr_wr_logistic_elite`, TE `adv_half_ppr_te_logistic_elite`.
- PPR: QB `adv_ppr_qb_logistic_bust`, RB `adv_ppr_rb_logistic_elite`, WR `adv_ppr_wr_logistic_elite`, TE `adv_ppr_te_logistic_bust`.
- GNG Keeper: QB `adv_gng_keeper_qb_linear_points` (with warnings), RB `adv_gng_keeper_rb_linear_points`, WR `adv_gng_keeper_wr_logistic_bust`, TE `adv_gng_keeper_te_logistic_bust`.

Architecture decision:
- The advanced BQML v2 positional finalists are verified and ready for promotion to owner-review boards.
- Route metrics remain strictly **BLOCKED** and mapped to `NULL`.
- Current Pigskin remains live, and no champion is currently active.

## Phase 33.18C BQML v2 Advanced Finalist Comparison Correction

Phase 33.18C corrected the baseline prior finalists for non-Standard profiles to match the true Phase 33.13 finalists.

Key findings:
- Phase 33.13 baseline rows for `half_ppr`, `ppr`, and `gng_keeper` are evaluator-incompatible due to buggy baseline calculations and missingness in the prior evaluations. Direct point/VOR capture comparisons are invalid.
- Applied warnings: GNG Keeper QB combined predictive correlation is below 0.45 (`0.4217`); Standard TE validation correlation declined by `-0.0342` (`0.4687` vs `0.5029`) despite holdout improvement.

Advanced owner-review finalists (Phase 33.18C corrected):
- Standard: QB `adv_standard_qb_logistic_bust`, RB `adv_standard_rb_linear_points`, WR `adv_standard_wr_logistic_elite`, TE `adv_standard_te_linear_points`.
- Half PPR: QB `adv_half_ppr_qb_logistic_bust`, RB `adv_half_ppr_rb_linear_vor`, WR `adv_half_ppr_wr_logistic_elite`, TE `adv_half_ppr_te_logistic_elite`.
- PPR: QB `adv_ppr_qb_logistic_bust`, RB `adv_ppr_rb_logistic_elite`, WR `adv_ppr_wr_logistic_elite`, TE `adv_ppr_te_logistic_bust`.
- GNG Keeper: QB `adv_gng_keeper_qb_linear_points` (with warnings), RB `adv_gng_keeper_rb_linear_points`, WR `adv_gng_keeper_wr_logistic_bust`, TE `adv_gng_keeper_te_logistic_bust`.

Architecture decision: The corrected advanced finalists are verified and ready for promotion to owner-review boards. Route metrics remain strictly **BLOCKED** and mapped to `NULL`.

## Phase 33.19 Advanced BQML v2 Owner-Review Boards

Phase 33.19 generated owner-review boards for the 16 positional BQML v2 finalists and alternates using active 2026 player contexts.

Key architecture features:
- Integrated pre-2026 rolling 3-year advanced metrics averages (2023-2025) with 0% missingness via leakage-safe imputation.
- Evaluated models using BQML `ML.PREDICT` on active 2026 player contexts, without live ranking updates.
- Output boards to `docs/rebuild/advanced-bqml-v2-owner-review-boards.md` with riser/faller lists, cutline promote/demote movements, high-risk sparse feature moves, and alternate disagreements.
- Route metrics remain strictly **BLOCKED** and mapped to `NULL`. No route runs or YPRR calculations were fabricated.

## Phase 33.20 Owner Review of Advanced Positional Boards

Phase 33.20 reviewed the candidate review boards.

Key architectural updates:
- Accepted 12 positional boards for review. QB boards require running QB bias capping; Standard TE requires Current Pigskin floor.
- Held 4 positional boards behind Current Pigskin (Half PPR TE, PPR TE, GNG Keeper QB, GNG Keeper TE) due to weak predictive correlation.
- Proposed guardrail integration: rookie draft capital floor (-15 ranks) and sparse feature upward movement cap (+10 ranks).
- Route metrics remain strictly **BLOCKED** and mapped to `NULL`.

## Phase 33.21B Guardrail Identity and History Fix

Phase 33.21B corrected the review board guardrails architecture.

Key architectural updates:
- **Career Games Integration**: Integrated `hist_games_3yr` (total games in 2023-2025) and `hist_seasons_3yr` from `player_season_advanced_metrics` to prevent false-positive rookie classification on active veterans with partial latest-season records.
- **Rookie & Low-History**: Retained true rookies (Omarion Hampton, Travis Hunter) under `ROOKIE_NO_HISTORY` and low-history career players (Cam Skattebo, Casey Washington) under `LOW_HISTORY`, anchoring them to Current Pigskin.
- **QB Disagreement Lock Fix**: Disabled `MODEL_DISAGREEMENT_LOCK` on QB boards to prevent the rejected points alternate from anchoring all 45 QBs.
- **Diagnostics Validation**: Generated `docs/rebuild/validation/phase-33-21b-guardrail-identity-history-fix-report.md`.
- Route metrics remain strictly **BLOCKED** and mapped to `NULL`.

## Phase 33.22 Owner Approval Packet

Phase 33.22 created the owner approval packet architecture.

Key architectural updates:
- **Approval Packet**: Generated `docs/rebuild/advanced-bqml-v2-owner-approval-packet.md` presenting the guarded boards, top-level recommendation table, and player movement examples.
- **Validation Report**: Generated `docs/rebuild/validation/phase-33-22-owner-approval-packet-report.md` validating git state and safety constraints.
- Route metrics remain strictly **BLOCKED** and mapped to `NULL`.

## Phase 33.23 Owner Decision for Guarded Positional Boards

Phase 33.23 recorded the owner decision and established top-100 planning guidelines.

Key architectural updates:
- **Owner Decision**: Formally logged the owner decision to accept 12 positional boards with guardrails, hold 4 positional boards, and authorize top-100 planner rules in `docs/rebuild/validation/phase-33-23-owner-decision-guarded-positional-boards.md`.
- **Top-100 Planning Architecture**: Defined future position-locked top-100 planner parameters (pulls from locked positional queues, no reordering, preserve held boards, route metrics blocked).
- Route metrics remain strictly **BLOCKED** and mapped to `NULL`.

## Phase 33.24 Position-Locked Top-100 Interleaver Planning

Phase 33.24 established the technical plan architecture for the top-100 interleaver.

Key architectural updates:
- **Interleaver Plan**: Generated `docs/rebuild/position-locked-top-100-interleaver-plan.md` defining position-locked queue rules, identity audits, and VOR selection options.
- **Validation Report**: Generated `docs/rebuild/validation/phase-33-24-position-locked-top-100-planning-report.md`.
- **Identity Hardening Architecture**: Designed the preflight audit schema to catch identity collisions.
- Route metrics remain strictly **BLOCKED** and mapped to `NULL`.

## Phase 33.25 Top-100 Player Identity Preflight

Phase 33.25 audited and hardened player identity mappings before building the interleaver.

Key architectural updates:
- **Identity Gate**: Created [top-100-identity-preflight.md](file:///e:/Fantasy%20Football/docs/rebuild/top-100-identity-preflight.md) establishing preflight universes, allowed statuses, and preflight gate blocking rules.
- **Marvin Harrison Jr. Resolution**: Applied manual override in `player_identity_overrides` mapping Sleeper `11628` to active player `00-0039849` and isolating retired Sr. `00-0007024`. Corrected his WR boards placement to rank 34/35 with verified career history.
- **Validation Report**: Generated [phase-33-25-top-100-identity-preflight-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-25-top-100-identity-preflight-report.md).
- Route metrics remain strictly **BLOCKED** and mapped to `NULL`.

## Phase 33.26 Position-Locked Top-100 Prototype

Phase 33.26 compiled and backtested the first top-100 overall rankings interleaver prototypes.

Key architectural updates:
- **Interleaver Compilation**: Built a python compiler executing three queue-selection strategies under three baseline structures.
- **Top-100 Boards**: Generated [position-locked-top-100-prototype-review.md](file:///e:/Fantasy%20Football/docs/rebuild/position-locked-top-100-prototype-review.md) containing the top-100 overall boards for 2026.
- **Validation & Backtest**: Documented backtest results in [phase-33-26-position-locked-top-100-prototype-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-26-position-locked-top-100-prototype-report.md).
- Route metrics remain strictly **BLOCKED** and mapped to `NULL`.

## Phase 33.26B Position-Locked Top-100 Calibration

Phase 33.26B calibrated the position-locked top-100 interleaver to resolve WR overpull and protect elite RBs.

Key architectural updates:
- **Calibrated Selector**: Implemented Min-Max normalized within-position scaling combined with scarcity, Current Pigskin anchor pressure, and look-ahead anti-monopoly gates.
- **Sanity Guardrails**: Implemented elite RB protection rules (forcing top-6/12 RBs to be selected in top 24/36/40) and anti-monopoly limits (WR max 6 in top 12, max 13 in top 24).
- **Prototype Boards**: Updated [position-locked-top-100-prototype-review.md](file:///e:/Fantasy%20Football/docs/rebuild/position-locked-top-100-prototype-review.md) with the calibrated top-100 overall boards.
- **Validation Report**: Documented the calibration and backtest in [phase-33-26b-top-100-positional-mix-calibration-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-26b-top-100-positional-mix-calibration-report.md).
- Route metrics remain strictly **BLOCKED** and mapped to `NULL`.

## Phase 33.26C Position-Locked Top-100 Weighting Calibration

Phase 33.26C calibrated weightings, softened mix constraints, and added draft-band movement caps to smooth rankings and eliminate position pockets.

Key architectural updates:
- **Soft Target Adjustments**: Replaced hard look-ahead gates with soft scoring adjustments ($+/- 8$ to $+/- 40$ on a 100-point scale).
- **Draft-Band & Position Caps**: Enforced overall caps (top-12 cannot fall outside top 24/36) and position caps (top-6 RB/WR cannot fall outside top 24/20). Capped QBs in top 12 at 1.
- **Calibrated Boards**: Updated [position-locked-top-100-prototype-review.md](file:///e:/Fantasy%20Football/docs/rebuild/position-locked-top-100-prototype-review.md) with calibrated boards.
- **Validation Report**: Documented findings in [phase-33-26c-top-100-weighting-calibration-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-26c-top-100-weighting-calibration-report.md).
- Route metrics remain strictly **BLOCKED** and mapped to `NULL`.

## Phase 33.26D Elite Market-Miss Audit

Phase 33.26D found that top-100 calibration cannot be considered owner-ready until elite miss tripwires are enforced.

Key architectural updates:
- **RB Queue Blocker**: Jahmyr Gibbs is a positional-board miss, not an interleaver-only miss. Guarded RB ranks him RB18/RB19 outside PPR even though Current Pigskin ranks him RB3 in all profiles and market consensus ranks him 2 overall.
- **Anchor Policy Need**: Future review prototypes need Current Pigskin and market tripwire reporting before presentation. These are review guardrails, not training targets.
- **V4 Held**: No `prototype_v4_elite_anchor` was generated because doing so safely requires RB positional-board correction or owner-approved manual anchors.
- **Validation Report**: Documented findings in [phase-33-26d-elite-market-miss-audit-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-26d-elite-market-miss-audit-report.md).
- Route metrics remain strictly **BLOCKED** and mapped to `NULL`.

## Phase 33.27 RB Positional Board Refinement

Phase 33.27 refined the RB positional-board review architecture.

Key architectural updates:
- **Selected Review Candidate**: `anchored_blend_tripwire`, a review-only RB queue using tiered Current Pigskin anchoring and elite RB tripwire locks.
- **Tripwire Rules**: Current or market top-3 RBs must be inside RB8. Current top-6 RBs must be inside RB12. Market top-6 RBs require RB12 placement unless prospect or low-history manual review explains the exception.
- **Model Status**: Existing RB alternates were not sufficient. A future receiving-aware RB model remains recommended, but not required before a review-only top-100 rebuild.
- **Validation Report**: Documented findings in [phase-33-27-rb-positional-board-refinement-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-27-rb-positional-board-refinement-report.md).
- Route metrics remain strictly **BLOCKED** and mapped to `NULL`.

## Phase 33.28 Refined RB Top-100 Rebuild Note

Phase 33.28 keeps the Phase 33.26C calibrated weighted hybrid position-pull sequence and swaps only the RB queue to the Phase 33.27 `anchored_blend_tripwire` review queue. This fixes Jahmyr Gibbs inside RB3 and top 7 overall across all profiles, but the result remains review-only because Current Pigskin and market tripwires still require owner judgment.

Stable constraints:

- Do not write this prototype to `analytics_pigskin_rankings`.
- Do not activate formula champions from this phase.
- Keep Half PPR TE, PPR TE, GNG Keeper QB, and GNG Keeper TE held behind Current Pigskin.
- Treat Jeremiyah Love as a market-only prospect tripwire until the player appears in a source-backed active ranking or approved prospect lane.
- Treat Half PPR Breece Hall as a current-state drift warning because live Current Pigskin now lists him RB6 while the Phase 33.27 evidence used an older RB18 context.
- Route metrics remain blocked/null.

## Phase 33.29 Refined Top-100 Owner Review Decision

Final decision: `REFINED TOP-100 READY FOR OWNER REVIEW WITH TRIPWIRES`.

Phase 33.29 accepts the Phase 33.28 refined top-100 prototype for owner review only. It does not approve live ranking writes, champion activation, production exposure, or deployment.

Owner-review findings:

- Gibbs is fixed at RB3 and inside the top 24 overall in every scoring profile.
- Achane and Chase Brown are not buried outside RB24.
- Omarion Hampton and Cam Skattebo remain manual-review prospect-history cases.
- Jeremiyah Love remains a market-only tripwire and needs a prospect lane or explicit owner rejection before live use.
- Half PPR Breece Hall is stale Current Pigskin context: Phase 33.27 evidence used RB18, while the current active table now lists RB6.
- Patrick Mahomes is an interleaver warning. The prototype pushes elite QBs too low for live use without backtest support.
- Rashee Rice is a WR position-board warning. The guarded WR queue disagrees sharply with Current Pigskin.

Next required gate: bounded historical backtest before any live top-100 decision.

## Phase 33.30 Bounded Backtest And Tripwire Cleanup Decision

Final decision: `REFINED TOP-100 NEEDS TARGETED QB/WR CLEANUP`.

Phase 33.30 ran a bounded proxy backtest against `ranking_backtest_feature_mart` using target seasons 2024 and 2025, target week 18, all four scoring profiles, and no 2026 outcomes. The exact 2026 owner-review queues do not exist historically, so the test used source-window feature proxies and the Phase 33.26C position-pull sequence.

Decision summary:

- The refined RB queue remains useful for owner review and fixes 2026 Gibbs sanity.
- The refined top-100 does not cleanly beat the Current Pigskin proxy on points/VOR capture.
- QB tripwires, especially Patrick Mahomes, point to an interleaver anchor/cap problem.
- WR tripwires, especially Rashee Rice, point to a WR position-board or elite-anchor problem.
- Jeremiyah Love requires a prospect lane or explicit owner rejection of market-only prospect influence.
- Half PPR Breece Hall requires stale-context refresh before live approval.
- Current Pigskin holds for live use.

Next gate: targeted QB/WR tripwire cleanup before another owner-review top-100 pass.

## Phase 33.33 Standard RB Formula Boundary

`RB STD GPT 5.5 v1.0` remains a blocked research specification. Its preferred no-team-multiplier structure is compatible with the architecture because projected team RB xFP pools already encode team environment. The formula cannot enter the backtest lane until RB receiving YAC above expectation is source-backed. Do not replace that component with raw YAC, Current Pigskin, market value, or a subjective rank.

## Phase 33.35 v1.0A Architecture Result

The read-only SQL implementation confirms that a team-pool xFP base can be built without Current Pigskin or subjective inputs. The first formulation is not competitive. A direct multiplicative availability factor is too strong, and 60/30/10 team-pool history retains stale workloads. Keep the SQL research-only. Future work should test tighter recency and a bounded availability penalty before another owner-review board.

## Phase 34.1 Situational Source Boundary

`fantasy_football_advanced_metrics` is a new isolated research dataset for 2022-2025 situational SQLite metrics. QB pressure/play-action splits, RB box/concept contexts, and WR/TE coverage/route contexts are source-backed there. They are not BQML v2 predictors yet. Integration requires an approved identity bridge, leakage-safe windows, and explicit feature-mart mapping. Source-local player IDs must never be used as official IDs.
