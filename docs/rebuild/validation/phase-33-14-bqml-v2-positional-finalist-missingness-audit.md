# Phase 33.14 - BQML v2 Positional Finalist Missingness Audit

Final decision: MISSINGNESS REPORTING WAS OVERSTATED

Phase 33.14 audited the Phase 33.13 positional finalists before owner-review board generation. No models were trained. No top-100 builder was built. No live rankings, champions, `ranking_backtest_results`, `analytics_pigskin_rankings`, or `analytics_pigskin_rankings_candidates` were written.

## Scope

Inputs reviewed:

- `docs/rebuild/bqml-v2-positional-formula-finalists.md`
- `src/bqml_v2_feature_contract.py`
- `ranking_backtest_feature_mart`
- `ranking_backtest_candidate_summaries`
- `ML.WEIGHTS` for each finalist model

The exact trained predictor source of truth for this audit is `ML.WEIGHTS`, excluding `__INTERCEPT__`.

## Main Finding

The reported 0.52 to 0.57 missing-input rate was calculated from the broad `predictor_missing_flags_json` payload in `ranking_backtest_feature_mart`, not from the exact trained predictor columns used by each finalist.

For 2024 validation plus 2025 holdout rows, exact trained-predictor missingness is much lower:

| Position | Standard exact missingness | Half PPR exact missingness | PPR exact missingness | GNG Keeper exact missingness |
|---|---:|---:|---:|---:|
| QB | 0.0628% | 0.0576% | 0.0576% | 0.0576% |
| RB | 5.2567% | 4.7735% | 4.7735% | 4.7735% |
| WR | 3.9192% | 3.4178% | 3.4178% | 3.4178% |
| TE | 4.6947% | 4.1946% | 4.1946% | 4.1946% |

Broad missing-flag rates remain near the prior warning range because the JSON contains roughly 82 to 85 `_missing` flags per row, including fields outside a model's exact position-specific predictor set:

| Profile | QB broad flags | RB broad flags | WR broad flags | TE broad flags |
|---|---:|---:|---:|---:|
| standard | 57.5784% | 53.0754% | 52.8976% | 54.2171% |
| half_ppr | 57.3628% | 53.0457% | 52.7914% | 54.1510% |
| ppr | 57.3611% | 53.0436% | 52.8164% | 54.1540% |
| gng_keeper | 57.3837% | 53.0786% | 52.7912% | 54.4663% |

Conclusion: the high missing-input warning is a broad mart-quality warning. It should not block positional owner-review boards by itself.

## Predictor Classification

Required predictors: the exact `ML.WEIGHTS` predictor columns for each model.

Optional predictors: none in the current official finalist path. The current models do not have a separate optional feature channel.

Blocked predictors: not used. Confirmed blocked names absent from exact predictors:

- YPRR
- TPRR
- true route share
- first-read share
- pressure EPA
- covered-receiver EPA
- catch-over-expected
- historical depth
- `pigskin_context_score`

Wrong-position predictors: not used. Finalists are position-locked and trained from position-specific predictor sets.

Unused feature-mart fields: many feature-mart columns are intentionally unused by each position. Examples include cross-position fields such as QB rushing leverage on WR/TE rows, receiver fields on QB/RB rows, and broad flag fields used for evidence rather than training. These unused fields explain the inflated broad missing-flag rate.

## Exact Predictor Lists

Standard finalists are older Phase 33.9 models. They do not include the later patched theory fields. Half PPR, PPR, and GNG Keeper Phase 33.13 models do include the patched fields where expected.

### QB

Standard QB exact predictors:

`cpoe`, `ngs_qb_passing_efficiency_score_3yr`, `passing_xfp_pbp_3yr`, `profile_points_score`, `qb_rushing_leverage_index`, `recent_points_avg`, `rushing_attempts`, `rushing_xfp_pbp_3yr`, `rushing_xfp_share_pbp_3yr`, `team_environment_score`, `weekly_volatility_3yr`

Half PPR, PPR, and GNG Keeper QB exact predictors:

`cpoe`, `ngs_qb_passing_efficiency_score_3yr`, `passing_epa_per_play`, `passing_xfp_pbp_3yr`, `profile_points_score`, `qb_rushing_leverage_index`, `recent_points_avg`, `rushing_attempts`, `rushing_xfp_pbp_3yr`, `rushing_xfp_share_pbp_3yr`, `team_environment_score`, `weekly_volatility_3yr`

### RB

Standard RB exact predictors:

`carries`, `carry_share_slope_3yr`, `goal_line_xfp_score_3yr`, `high_value_rush_xfp_score_3yr`, `high_value_target_xfp_score_3yr`, `high_value_xfp_score_3yr`, `ngs_box_resilience_score_3yr`, `ngs_rush_yards_over_expected_score_3yr`, `ngs_rushing_efficiency_score_3yr`, `profile_points_score`, `rb_high_value_opportunity_score`, `receiving_xfp_pbp_3yr`, `red_zone_xfp_score_3yr`, `rushing_xfp_pbp_3yr`, `target_share_slope_3yr`, `targets`, `team_environment_score`, `xfp_score_3yr`, `xfp_share_3yr`

Half PPR, PPR, and GNG Keeper RB exact predictors:

`carries`, `carry_share_slope_3yr`, `goal_line_opportunities`, `goal_line_xfp_score_3yr`, `high_value_rush_xfp_score_3yr`, `high_value_target_xfp_score_3yr`, `high_value_xfp_score_3yr`, `ngs_box_resilience_score_3yr`, `ngs_rush_yards_over_expected_score_3yr`, `ngs_rushing_efficiency_score_3yr`, `profile_points_score`, `rb_high_value_opportunity_score`, `receiving_xfp_pbp_3yr`, `red_zone_opportunities`, `red_zone_xfp_score_3yr`, `rushing_xfp_pbp_3yr`, `target_share_slope_3yr`, `targets`, `team_environment_score`, `xfp_score_3yr`, `xfp_share_3yr`

### WR

Standard WR exact predictors:

`air_yards`, `fantasy_points_over_expectation_3yr`, `high_value_target_xfp_score_3yr`, `ngs_receiving_efficiency_score_3yr`, `ngs_separation_score_3yr`, `ngs_yac_over_expected_score_3yr`, `profile_points_score`, `receiving_chain_mover_score_3yr`, `receiving_first_down_exp_pbp_3yr`, `receiving_role_dominance_score`, `receiving_role_dominance_xfp_3yr`, `receiving_usage`, `receiving_xfp_pbp_3yr`, `receiving_xfp_share_pbp_3yr`, `target_share_slope_3yr`, `targets`, `wopr_slope_3yr`, `xfp_score_3yr`, `xfp_share_3yr`

Half PPR, PPR, and GNG Keeper WR exact predictors:

`air_yards`, `fantasy_points_over_expectation_3yr`, `high_value_target_xfp_score_3yr`, `ngs_receiving_efficiency_score_3yr`, `ngs_separation_score_3yr`, `ngs_yac_over_expected_score_3yr`, `profile_points_score`, `receiving_chain_mover_score_3yr`, `receiving_epa`, `receiving_first_down_exp_pbp_3yr`, `receiving_role_dominance_score`, `receiving_role_dominance_xfp_3yr`, `receiving_usage`, `receiving_xfp_pbp_3yr`, `receiving_xfp_share_pbp_3yr`, `receiving_yards`, `red_zone_targets`, `target_share_slope_3yr`, `targets`, `wopr_slope_3yr`, `xfp_score_3yr`, `xfp_share_3yr`

### TE

Standard TE exact predictors:

`air_yards`, `fantasy_points_over_expectation_3yr`, `goal_line_xfp_score_3yr`, `high_value_target_xfp_score_3yr`, `ngs_receiving_efficiency_score_3yr`, `ngs_separation_score_3yr`, `ngs_yac_over_expected_score_3yr`, `offensive_snap_share_3yr`, `profile_points_score`, `receiving_chain_mover_score_3yr`, `receiving_first_down_exp_pbp_3yr`, `receiving_role_dominance_score`, `receiving_role_dominance_xfp_3yr`, `receiving_usage`, `receiving_xfp_pbp_3yr`, `receiving_xfp_share_pbp_3yr`, `red_zone_xfp_score_3yr`, `snap_role_stability_3yr`, `target_share_slope_3yr`, `targets`, `wopr_slope_3yr`, `xfp_score_3yr`, `xfp_share_3yr`

Half PPR, PPR, and GNG Keeper TE exact predictors:

`air_yards`, `fantasy_points_over_expectation_3yr`, `goal_line_xfp_score_3yr`, `high_value_target_xfp_score_3yr`, `ngs_receiving_efficiency_score_3yr`, `ngs_separation_score_3yr`, `ngs_yac_over_expected_score_3yr`, `offensive_snap_share_3yr`, `profile_points_score`, `receiving_chain_mover_score_3yr`, `receiving_epa`, `receiving_first_down_exp_pbp_3yr`, `receiving_role_dominance_score`, `receiving_role_dominance_xfp_3yr`, `receiving_usage`, `receiving_xfp_pbp_3yr`, `receiving_xfp_share_pbp_3yr`, `receiving_yards`, `red_zone_targets`, `red_zone_xfp_score_3yr`, `snap_role_stability_3yr`, `target_share_slope_3yr`, `targets`, `wopr_slope_3yr`, `xfp_score_3yr`, `xfp_share_3yr`

## Missingness Detail

Exact trained-predictor missingness by split:

| Profile group | Position | Train | Validation | Holdout | Top review-split missing fields |
|---|---|---:|---:|---:|---|
| Standard | QB | 0.7315% | 0.0476% | 0.0924% | `ngs_qb_passing_efficiency_score_3yr` 0.7% |
| Standard | RB | 8.0290% | 5.4735% | 4.5010% | NGS rush fields 19.1%, `carry_share_slope_3yr` 18.5%, `target_share_slope_3yr` 18.5% |
| Standard | WR | 5.7309% | 4.5754% | 1.8809% | `wopr_slope_3yr` 20.5%, `target_share_slope_3yr` 19.4%, NGS receiving fields about 10.3 to 10.5% |
| Standard | TE | 7.5481% | 5.5838% | 2.2294% | NGS receiving fields 21.8%, `target_share_slope_3yr` 15.8%, `wopr_slope_3yr` 15.8% |
| Half PPR/PPR/GNG | QB | 0.7058% | 0.0436% | 0.0847% | `ngs_qb_passing_efficiency_score_3yr` 0.7% |
| Half PPR/PPR/GNG | RB | 7.3616% | 4.9746% | 4.0723% | NGS rush fields 19.1%, `carry_share_slope_3yr` 18.5%, `target_share_slope_3yr` 18.5% |
| Half PPR/PPR/GNG | WR | 5.0725% | 3.9859% | 1.6529% | `wopr_slope_3yr` 20.5%, `target_share_slope_3yr` 19.4%, NGS receiving fields about 10.3 to 10.5% |
| Half PPR/PPR/GNG | TE | 6.7477% | 4.9749% | 2.0310% | NGS receiving fields 21.8%, `target_share_slope_3yr` 15.8%, `wopr_slope_3yr` 15.8% |

Season-level note: older training years carry the largest gaps. The strongest example is `ngs_rush_yards_over_expected_score_3yr`, which is 100% missing for RB training rows in 2017 and 2018. That does not show up as a holdout blocker because 2024 and 2025 coverage is materially better.

## Patched Theory Feature Audit

| Profile | Position | Patched fields expected | ML.WEIGHTS evidence | Status |
|---|---|---|---|---|
| standard | QB | `passing_epa_per_play` | absent | patch not present in older Standard finalist |
| standard | RB | `red_zone_opportunities`, `goal_line_opportunities` | absent | patch not present in older Standard finalist |
| standard | WR | `receiving_yards`, `receiving_epa`, `red_zone_targets` | absent | patch not present in older Standard finalist |
| standard | TE | `receiving_yards`, `receiving_epa`, `red_zone_targets` | absent | patch not present in older Standard finalist |
| half_ppr | QB | `passing_epa_per_play` | -1.75073 | present |
| half_ppr | RB | `red_zone_opportunities`, `goal_line_opportunities` | -1.41395, 1.09601 | present |
| half_ppr | WR | `receiving_yards`, `receiving_epa`, `red_zone_targets` | -0.00382866, -0.0564335, -0.0478855 | present but weak |
| half_ppr | TE | `receiving_yards`, `receiving_epa`, `red_zone_targets` | 0.0990165, -0.0395438, -0.106001 | present |
| ppr | QB | `passing_epa_per_play` | -1.75573 | present |
| ppr | RB | `red_zone_opportunities`, `goal_line_opportunities` | -1.43998, 1.28426 | present |
| ppr | WR | `receiving_yards`, `receiving_epa`, `red_zone_targets` | 0.00409392, 0.0811171, 0.111398 | present |
| ppr | TE | `receiving_yards`, `receiving_epa`, `red_zone_targets` | 0.170696, 0.0318312, -1.695 | present |
| gng_keeper | QB | `passing_epa_per_play` | -1.23411 | present |
| gng_keeper | RB | `red_zone_opportunities`, `goal_line_opportunities` | 0.0241907, -0.000000460141 | present but weak |
| gng_keeper | WR | `receiving_yards`, `receiving_epa`, `red_zone_targets` | 0.0723653, 0.0103847, 0.401853 | present |
| gng_keeper | TE | `receiving_yards`, `receiving_epa`, `red_zone_targets` | 0.107163, -0.01335, -1.16944 | present |

Interpretation: patched theory fields are present in the Phase 33.13 profile expansion models. Their weights are not uniformly strong. WR Half PPR and GNG RB are the weakest patched-field reads. Standard remains a separate older finalist set and should not be described as patched.

## Profile-Position Readiness

| Profile | Position | Finalist | Actual predictor missingness | Theory fields present | Theory fields absent | Confidence | Decision |
|---|---|---|---:|---|---|---|---|
| standard | QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | 0.0628% | none of patched QB field | `passing_epa_per_play` | medium | owner-review ok, but label as pre-patch Standard |
| standard | RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | 5.2567% | none of patched RB fields | `red_zone_opportunities`, `goal_line_opportunities` | medium | owner-review ok, but patch gap should be visible |
| standard | WR | `bqml_v2_standard_wr_logistic_elite_v0` | 3.9192% | none of patched WR fields | `receiving_yards`, `receiving_epa`, `red_zone_targets` | medium | owner-review ok with pre-patch warning |
| standard | TE | `bqml_v2_standard_te_logistic_bust_inverse_v0` | 4.6947% | none of patched TE fields | `receiving_yards`, `receiving_epa`, `red_zone_targets` | medium | owner-review ok with pre-patch warning |
| half_ppr | QB | `bqml_v2_half_ppr_qb_linear_points_v0` | 0.0576% | `passing_epa_per_play` | none | high | ready |
| half_ppr | RB | `bqml_v2_half_ppr_rb_linear_points_v0` | 4.7735% | red-zone and goal-line opportunities | none | medium-high | ready with NGS/role-slope warning |
| half_ppr | WR | `bqml_v2_half_ppr_wr_logistic_bust_inverse_v0` | 3.4178% | receiving yards/EPA/red-zone targets | none | medium | ready, but patched weights are weak |
| half_ppr | TE | `bqml_v2_half_ppr_te_linear_vor_v0` | 4.1946% | receiving yards/EPA/red-zone targets | none | medium-high | ready with NGS/role-slope warning |
| ppr | QB | `bqml_v2_ppr_qb_linear_points_v0` | 0.0576% | `passing_epa_per_play` | none | high | ready |
| ppr | RB | `bqml_v2_ppr_rb_linear_points_v0` | 4.7735% | red-zone and goal-line opportunities | none | medium-high | ready with NGS/role-slope warning |
| ppr | WR | `bqml_v2_ppr_wr_logistic_elite_v0` | 3.4178% | receiving yards/EPA/red-zone targets | none | high | ready |
| ppr | TE | `bqml_v2_ppr_te_linear_points_v0` | 4.1946% | receiving yards/EPA/red-zone targets | none | high | ready |
| gng_keeper | QB | `bqml_v2_gng_keeper_qb_linear_points_v0` | 0.0576% | `passing_epa_per_play` | none | high | ready |
| gng_keeper | RB | `bqml_v2_gng_keeper_rb_logistic_elite_v0` | 4.7735% | red-zone and goal-line opportunities | none | medium | ready, but patched weights are weak |
| gng_keeper | WR | `bqml_v2_gng_keeper_wr_linear_points_v0` | 3.4178% | receiving yards/EPA/red-zone targets | none | high | ready |
| gng_keeper | TE | `bqml_v2_gng_keeper_te_linear_points_v0` | 4.1946% | receiving yards/EPA/red-zone targets | none | high | ready |

## Safety Checks

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
```

Result: passed.

No production deploy occurred. No staging deploy occurred. No BigQuery writes occurred in this phase. No models were trained. No materialization was run. No LLM calls were made.

## Recommendation

Proceed to owner-review board generation for the non-Standard profile-expanded finalists. Keep the Standard finalists available as the current Standard comparison set, but label them as pre-patch Standard models unless a later phase retrains Standard with the patched theory fields.

Recommended next phase: Phase 33.15 generate profile-position owner-review boards from the audited finalists.
