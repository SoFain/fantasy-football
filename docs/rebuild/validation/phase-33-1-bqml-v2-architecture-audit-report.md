# Phase 33.1 BQML V2 Architecture Audit From Theory Notes

Final decision: BQML V2 PLAN READY WITH SOURCE GAPS

## Scope

This phase translated `D:\So Fain\Downloads\BQML-Theory.docx` into a source-backed BQML v2 plan. No model was trained. No live ranking table was changed. No champion was activated.

The theory notes are useful, but several named features are not source-backed in the current warehouse. BQML v2 should use the available xFP, PBP, NGS, WOPR, role, fantasy-point, VOR, and scoring-profile fields now. It should explicitly block route-derived claims until route source coverage exists.

## Current Warehouse Evidence

Target tables and counts from targeted read-only BigQuery checks:

| Object | Current count |
|---|---:|
| `ranking_backtest_feature_mart` | 156,244 |
| `analytics_player_fantasy_points_by_profile` | 297,792 |
| `player_week_opportunity_metrics` | 70,356 |
| `player_week_ideal_opportunity_metrics` | 64,624 |
| `player_week_pbp_opportunity_metrics` | 65,358 |
| `player_week_ngs_metrics` | 24,557 |
| `player_week_role_context_metrics` | 65,864 |

Fantasy-point target coverage:

| scoring_profile_id | rows |
|---|---:|
| `standard` | 74,448 |
| `half_ppr` | 74,448 |
| `ppr` | 74,448 |
| `gng_keeper` | 74,448 |

Feature mart coverage is complete for `target_fantasy_points`, `value_over_replacement`, `elite_week_rate_3yr`, and `bust_week_rate_3yr` across all four scoring profiles and all four positions. Injury and historical depth fields exist in the mart, but current coverage is zero for every profile and position.

Existing BQML summary evidence remains review-only:

- `ranking_backtest_sql_native_bqml_enriched_v1`: 128 summary rows.
- `ranking_backtest_sql_native_bqml_ngs_v1`: 128 summary rows.
- `ranking_formula_champions`: 0 rows.

## Theory Feature Map

| Theory feature | Position | Current status | Source-backed mapping | Decision |
|---|---|---|---|---|
| EPA on non-optimal plays under pressure or to covered receivers | QB | Needs source | Proxy only: `passing_epa_per_play`, `cpoe`, `ngs_qb_passing_efficiency_score_3yr`, `passing_xfp_pbp_3yr` | Do not claim pressure or covered-receiver EPA. Use proxy label only. |
| Rushing baseline | QB | Available now | `rushing_attempts`, `qb_rushing_leverage_index`, `rushing_xfp_pbp_3yr`, `rushing_xfp_share_pbp_3yr` | Include in QB Standard v2. |
| Contract value / AAV | QB | Available as source, not model-ready in feature mart | `player_contracts.apy`, `inflated_apy`, `guaranteed`, `apy_cap_pct` | Add leakage-safe contract feature mart integration before model use. |
| Weighted opportunity | RB | Available now | `rb_high_value_opportunity_score`, `red_zone_opportunities`, `goal_line_opportunities`, `high_value_xfp_score_3yr`, `high_value_rush_xfp_score_3yr`, `high_value_target_xfp_score_3yr` | Include. Use profile-specific weights. |
| PPR, Half PPR, Standard target multipliers | RB | Available now | `scoring_profile_id`, `analytics_player_fantasy_points_by_profile`, `target_fantasy_points`, `xfp_share_3yr` | Train per profile. Do not average profiles. |
| Broken tackle rate | RB | Needs source | Possible weak proxy: `ngs_rush_yards_over_expected_score_3yr`, `ngs_box_resilience_score_3yr` | Do not name broken tackles unless a true source is added. |
| YPRR | WR/TE | Blocked | No approved route source | Exclude from v2 official features. |
| Targets per route run | WR/TE | Blocked | `targets` and target share exist, route denominator does not | Use target share/WOPR, not TPRR. |
| First downs per route run | WR/TE | Available as proxy | `receiving_first_down_exp_pbp_3yr`, `receiving_chain_mover_score_3yr`; route denominator absent | Use as chain-mover proxy, not 1D/RR. |
| Touchdown rate | WR/TE | Available as proxy | `red_zone_targets`, `red_zone_xfp_score_3yr`, `goal_line_xfp_score_3yr`, profile fantasy points | Use as scoring context. Avoid route-rate claim. |
| PRS composite | WR/TE | Needs source | Partial proxies only: WOPR, xFP, first-down proxy, NGS receiving | Build a proxy composite only if named differently, for example `receiving_role_value_proxy_v2`. |
| WOPR | WR/TE | Available now | `wopr_slope_3yr`, `receiving_role_dominance_score`, `target_share`, `air_yards`, `air_yards_share` where available | Include in WR/TE models. |
| Route participation rate | TE | Available as proxy | `offensive_snap_share_3yr`, `snap_role_stability_3yr`; `route_share` remains null/flagged | Use snap-role proxy. Do not call it route participation. |
| VORP / VOR | Overall | Available now | `target_fantasy_points`, `replacement_points`, `value_over_replacement` | Use as core overall-board target and evaluation metric. |
| Fixed QB15/RB36/WR55/TE12 baseline | Overall | Test candidate only | `VOR_BASELINE_POLICIES` includes deep, middle, and current SQL policies | Do not hard-code as default. Run baseline sensitivity by scoring profile. |

## Model Families

Standard scoring should run first. Repeat only after Standard passes coverage and sanity checks.

Each family is scoped by:

- `scoring_profile_id`
- `position`
- `league_type_id`
- `roster_format_id`
- source window
- target season/week

Recommended initial grid:

| Family | Position | Scoring profile order | Primary targets | Use |
|---|---|---|---|---|
| `bqml_v2_qb_profile_points` | QB | Standard first, then Half PPR, PPR, GNG Keeper | fantasy points, VOR | QB board ordering. |
| `bqml_v2_qb_elite_bust` | QB | Standard first | elite/starter label, bust label | Risk and ceiling overlay. |
| `bqml_v2_rb_profile_points` | RB | Standard first | fantasy points, VOR | Profile-sensitive RB value. |
| `bqml_v2_rb_elite_bust` | RB | Standard first | elite/starter label, bust label | Bust and high-value opportunity control. |
| `bqml_v2_wr_profile_points` | WR | Standard first | fantasy points, VOR | WR board ordering. |
| `bqml_v2_wr_elite_bust` | WR | Standard first | elite/starter label, bust label | Ceiling and bust control. |
| `bqml_v2_te_profile_points` | TE | Standard first | fantasy points, VOR | TE board ordering with TE35 output policy. |
| `bqml_v2_te_elite_bust` | TE | Standard first | elite/starter label, bust label | Volatility control. |

Start with BigQuery ML linear regression and logistic regression. Consider boosted tree only after the linear/logistic path produces a clean Standard baseline and bytes/runtime are acceptable. Do not use remote, AutoML, DNN, Gemini, or hyperparameter tuning in v2 foundation.

## Position-Specific Feature Allowlists

### QB

Allowed now:

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
- `target_fantasy_points`
- `value_over_replacement`

Add later after source integration:

- contract AAV score from `player_contracts.apy` or `inflated_apy`.

Blocked:

- pressure EPA
- covered-receiver EPA
- first-read share

### RB

Allowed now:

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

Blocked or proxy-only:

- broken tackle rate. Use NGS rushing proxy only with proxy language.
- injury burden as a default model feature. Current feature mart coverage is zero.

### WR

Allowed now:

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

Blocked:

- YPRR
- TPRR
- true route share
- first-read share

### TE

Allowed now:

- WR receiving role fields that are position-valid for TE.
- `offensive_snap_share_3yr`
- `snap_role_stability_3yr`
- `receiving_first_down_exp_pbp_3yr`
- `receiving_chain_mover_score_3yr`
- `ngs_receiving_efficiency_score_3yr`
- `ngs_separation_score_3yr`
- `ngs_catch_over_expected_score_3yr`
- `red_zone_xfp_score_3yr`
- `goal_line_xfp_score_3yr`

Blocked or proxy-only:

- route participation rate. Use snap-role proxy only.
- 1D/RR. Use first-down proxy only.
- historical depth context. Current mart coverage is zero.

## Targets

Use profile-specific targets. Do not train one all-profile model and declare one global winner.

| Target | Source | v2 use |
|---|---|---|
| Fantasy points | `target_fantasy_points` | Regression target by position/profile. |
| VOR | `value_over_replacement` | Regression target and overall-board core. |
| Elite label | position/profile threshold from `actual_position_rank` or existing top-N labels | Logistic ceiling model. Threshold must be config-driven. |
| Starter label | position/profile roster-depth threshold from tested baseline policy | Logistic utility model. |
| Bust label | actual rank or points below replacement after predicted top-K selection | Logistic risk model and board penalty. |

The existing `elite_week_rate_3yr` and `bust_week_rate_3yr` are predictors, not final target labels. BQML v2 should define explicit target labels in SQL, then validate row counts by profile and position.

## Replacement Baseline Policy

Do not hard-code QB15/RB36/WR55/TE12 as the production answer.

Existing code already lists multiple VOR baseline policies:

- `current_sql_vorp_qb12_rb24_wr24_te12`
- `middle_vorp_qb12_rb30_wr42_te12`
- `deep_vorp_qb15_rb36_wr55_te12`

Phase 33 should test these policies by scoring profile and position. The owner should see baseline sensitivity before any candidate board is promoted.

Current median replacement points show real scoring-profile differences. Examples from the live mart:

| scoring_profile_id | QB median | RB median | WR median | TE median |
|---|---:|---:|---:|---:|
| `standard` | 16.6 | 7.2 | 8.5 | 6.1 |
| `half_ppr` | 16.6 | 8.5 | 10.8 | 7.7 |
| `ppr` | 16.6 | 9.7 | 13.0 | 9.5 |
| `gng_keeper` | 10.66 | 3.64 | 6.42 | 4.16 |

That spread is enough to make a single global baseline unsafe.

## Overall Board Builder

Build the overall board per scoring profile.

Recommended score components:

1. `predicted_vor`: primary cross-position value.
2. `position_scarcity_score`: derived from VOR distribution and cutline cliffs by profile.
3. `tier_cutline_value`: extra weight for players near QB/RB/WR/TE starter and elite cutlines.
4. `bust_risk_penalty`: from position/profile logistic bust model.
5. `source_confidence`: missing-input and source freshness penalty.

Do not average Standard, Half PPR, PPR, and GNG Keeper into one champion. Generate one owner-review board per profile, Standard first.

## Implementation Plan

### Phase 33.2: BQML v2 feature contract

- Add a `docs/rebuild/bqml-v2-ranking-architecture.md` plan or contract.
- Define feature allowlists by position.
- Add blocked feature tests for route metrics, YPRR, first-read share, pressure EPA, covered-receiver EPA, and historical depth.
- Define target SQL snippets for fantasy points, VOR, elite/starter, and bust labels.
- No training.

### Phase 33.3: Standard-only training dataset dry run

- Build a query or view for Standard only.
- Validate leakage: `source_window_end_season < target_season`.
- Validate coverage by position and feature group.
- Validate blocked feature columns are absent.
- Produce sample rows and missing-input summary.
- No model training unless owner approves the next phase.

### Phase 33.4: Standard BQML v2 training

- Train QB/RB/WR/TE linear regression for `target_fantasy_points`.
- Train QB/RB/WR/TE linear regression for `value_over_replacement`.
- Train QB/RB/WR/TE logistic models for elite/starter and bust labels.
- Use 2017-2023 train, 2024 validation, 2025 holdout.
- Write summary evidence only.
- Do not write live rankings or champions.

### Phase 33.5: Standard owner-review board

- Use `ML.PREDICT` on the Standard holdout/review input.
- Build Standard-only overall board from predicted VOR, scarcity, cutline value, and bust risk.
- Compare against Current Pigskin, simple projection, enriched BQML v1, and BQML NGS v1.
- Keep Current Pigskin live.

### Phase 33.6: Expand profiles only if Standard passes

- Repeat for `half_ppr`, `ppr`, and `gng_keeper`.
- Keep results profile-specific.
- No all-profile winner.

## Guardrails For BQML V2

- Source-backed features only.
- Missing feature fields stay null and flagged.
- No fabricated route metrics.
- No `pigskin_context_score`.
- No historical depth until source coverage exists.
- No current Sleeper context as historical training truth.
- No live ranking writes.
- No `ranking_formula_champions` writes before a separate owner-approved champion phase.
- No Gemini calls for training or automated validation.

## Checks Run

- Extracted `BQML-Theory.docx` text using the bundled document runtime.
- Read root `AGENTS.md` and `docs/rebuild/AGENTS.md`.
- Read `docs/rebuild/ranking-opportunity-metrics-matrix.md`.
- Read `docs/rebuild/ranking-algorithm-scorecard.md`.
- Ran targeted read-only BigQuery schema and count checks.
- Ran targeted read-only BigQuery coverage checks for `ranking_backtest_feature_mart`.
- No tests were run because this phase changed documentation only.

## No-Live-Change Confirmation

- No BQML models trained.
- No live rankings changed.
- No champion activated.
- No ranking table writes.
- No source ingest.
- No deployment.

## Warnings

- The theory note's cited correlations are not treated as verified project evidence. They are hypotheses until tested in this warehouse.
- Contract value is source-available but not currently in `ranking_backtest_feature_mart`.
- Injury and historical depth fields are present but not currently populated in the feature mart.
- Route-derived metrics are blocked until a true route source is added.

## Recommended Next Phase

Phase 33.2: add the BQML v2 feature/target contract and Standard-only dry-run query tests. Do not train models until that contract passes.
