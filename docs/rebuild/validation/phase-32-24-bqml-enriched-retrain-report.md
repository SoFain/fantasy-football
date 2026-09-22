# Phase 32.24: BQML Enriched Retrain Report

Final decision: BQML ENRICHED MODEL IMPROVES BUT NOT ENOUGH

## Scope

Phase 32.24 retrained bounded BigQuery ML challenger models using enriched `ranking_backtest_feature_mart` predictors, then evaluated them through the SQL-native summary path.

No production deploy occurred. No live rankings were regenerated. No champion formulas were activated. No Pigskin chat, Gemini, LLM-backed ranking generation, live Sleeper API, source ingest, materialization, old Python full tournament path, persistent detail rows, global truncation, DNN, AutoML, remote model, or broad hyperparameter tuning occurred.

## Files Changed

- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/validation/phase-32-24-bqml-enriched-retrain-report.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

Commit hash: recorded after commit if committed.

## Git State

Before this phase:

- Latest commit: `5886d8f phase 32.23 lock owner formula classifications`
- Worktree: only the standing untracked historical validation backlog was present.

After this phase:

- Source, tests, scorecard, matrix, and this report changed.
- Historical validation backlog remains untracked and untouched.

## Metric Extraction Sanity

Verified before comparison:

| Metric | Extraction path | Read |
|---|---|---|
| Pairwise win rate | top-level `pairwise_win_rate` | Correct for stored summaries. Recent SQL-native summaries populate it from the high-confidence pairwise calculation. |
| High-confidence pairwise | `metric_json.high_confidence_pairwise_win_rate` | Correct. Do not double-count it as independent when it matches top-level pairwise. |
| Overall pairwise draft win rate | `metric_json.overall_pairwise_draft_win_rate` | Correct separate cross-position draft-board metric. |
| Top-N hit rate | top-level `top_n_hit_rate` | Correct. |
| Captured points | top-level `actual_points_captured_rate` | Correct. |
| VOR captured | `metric_json.value_over_replacement_captured_rate` | Correct. |
| NDCG@K | `metric_json.ndcg_at_k` | Correct. |
| Value captured at K | `metric_json.value_captured_at_k` | Correct. |
| Elite recall | `metric_json.elite_recall_at_k` | Correct. |
| Tier accuracy | `metric_json.tier_accuracy` | Correct. |
| Bust rate | `metric_json.bust_rate` | Correct. |
| Pick-band regret | `metric_json.pick_band_regret` | Correct. |
| Missing-input rate | top-level `missing_input_rate` | Correct. |

Decision language below uses overall pairwise as the separate draft-board pairwise read.

## Feature Inventory

Enriched v1 BQML uses the existing feature mart with:

- Baseline predictors: `profile_points_score`, `opportunity_score_proxy`, `efficiency_score_proxy`, `analytical_grade_proxy`, `role_stability_score`.
- Ideal xFP and opportunity: `xfp_score_3yr`, `xfp_share_3yr`, `fantasy_points_over_expectation_3yr`, `high_value_xfp_score_3yr`, `receiving_role_dominance_xfp_3yr`, `receiving_role_dominance_score`, `qb_rushing_leverage_index`, `rb_high_value_opportunity_score`, `red_zone_usage_score`, `goal_line_usage_score`, `team_environment_score`.
- PBP xFP: `receiving_xfp_pbp_3yr`, `rushing_xfp_pbp_3yr`, `passing_xfp_pbp_3yr`, `red_zone_xfp_score_3yr`, `goal_line_xfp_score_3yr`, `high_value_target_xfp_score_3yr`, `high_value_rush_xfp_score_3yr`, `receiving_xfp_share_pbp_3yr`, `rushing_xfp_share_pbp_3yr`, `opportunity_quality_score_3yr`.
- First-down proxies: `receiving_first_down_exp_pbp_3yr`, `rushing_first_down_exp_pbp_3yr`, `passing_first_down_exp_pbp_3yr`, `high_value_first_down_opportunity_score_3yr`, `receiving_chain_mover_score_3yr`, `rushing_chain_mover_score_3yr`.
- Injury and availability: `injury_status_score_3yr`, `injury_burden_score_3yr`, `missed_time_risk_score_3yr`, `availability_score_3yr`.
- Role and outcome-history context: `offensive_snap_share_3yr`, `snap_role_stability_3yr`, `spike_week_rate_3yr`, `bust_week_rate_3yr`, `elite_week_rate_3yr`.

Excluded:

- `depth_chart_role_score_3yr`, because historical depth remains blocked.
- Sleeper current context, because it is live-only and not a historical backtest input.
- Target/outcome predictor columns: `target_fantasy_points`, `actual_position_rank`, `actual_overall_rank`, `value_over_replacement`, top labels, pick-band labels, and target-season outcomes. Outcome fields are used only as labels.

Coverage highlights:

| Slice | Read |
|---|---|
| Ideal xFP | 2024 and 2025 coverage is near complete for RB/WR/TE and complete for QB primary xFP. |
| PBP receiving xFP | RB/WR/TE coverage is high. QB receiver-style PBP fields are sparse and handled with missing indicators. |
| PBP rushing/passing xFP | QB rushing/passing are complete. RB rushing is high. WR/TE rushing and passing are sparse by position. |
| First-down proxies | Follow the same coverage shape as PBP pass/rush fields. |
| Injury/availability | Sparse in 2024, stronger in 2025. Example injury/availability coverage: 2024 RB 0.3378, WR 0.3895, TE 0.3707; 2025 RB 0.8716, WR 0.8652, TE 0.9796. |
| Depth | Excluded. |

## Split Policy

- Train: target seasons 2017-2023.
- Validation: target season 2024.
- Holdout: target season 2025.
- BigQuery ML option: `data_split_method='NO_SPLIT'`.
- 2025 holdout was not used for training or tuning.

## Models Trained

Version suffix: `bqml_enriched_v1`.

| Model | Type | Target | Training job ID | Bytes processed | Runtime |
|---|---|---|---|---:|---:|
| `ranking_bqml_enriched_linear_vor_v1` | linear regression | value over replacement | `820b025f-0350-403a-a836-d22041c82583` | 68,825,556 | 130.86 sec |
| `ranking_bqml_enriched_linear_points_v1` | linear regression | target fantasy points | `a35a2dcc-9c86-4bca-bf35-0c77437a5785` | 68,825,556 | 105.63 sec |
| `ranking_bqml_enriched_logistic_elite_v1` | logistic regression | position-specific elite finish | `2a7bf6f5-900a-48be-ab15-27435e78cdd2` | 68,825,556 | 117.90 sec |
| `ranking_bqml_enriched_boosted_tree_vor_v1` | boosted tree regression | value over replacement | `dbed631a-1abe-4797-93f1-acd2c140753b` | 14,098,005,969 | 325.80 sec |

Skipped:

- Random forest, DNN, AutoML, remote models, Gemini-backed models, and hyperparameter tuning.
- Boosted tree elite classifier, because the four required models were enough for this bounded pass.

Cost guard:

- Training SELECT dry-run estimate was 68,825,556 bytes per model.
- Boosted tree internal training processed materially more bytes than the SELECT estimate. It completed successfully but is a warning for future BQML cost planning.

## Prediction And Summary Output

Read-only prediction summary:

- Validation/holdout summary dry-run bytes: 15,368,621.
- Summary rows produced: 128.
- Persistent detail rows produced: 0.

Controlled summary-only write:

- Gate: `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`.
- Gate removed immediately afterward.
- Write job ID: `d086db06-5861-4ad3-b563-17668c4e7c0e`.
- Expected run rows: 8.
- Expected summary rows: 128.
- Expected detail rows: 0.

Post-write verification:

| Check | Count |
|---|---:|
| BQML enriched run rows | 8 |
| BQML enriched summary rows | 128 |
| Detail rows for BQML enriched run prefix | 0 |
| `ranking_formula_champions` | 0 |
| Active live rankings | 1,140 |

## 2024 Validation Results

| Candidate | Top-N | Captured | VOR captured | Rank corr | High-conf | Overall pairwise | NDCG | Tier acc | Bust |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Enriched logistic elite v1 | 0.5169 | 0.7039 | 0.5804 | 0.5359 | 0.7430 | 0.5148 | 0.6471 | 0.4071 | 0.1633 |
| Enriched linear points v1 | 0.5122 | 0.7016 | 0.5800 | 0.5452 | 0.9176 | 0.7268 | 0.6479 | 0.4071 | 0.1697 |
| Enriched linear VOR v1 | 0.5064 | 0.6960 | 0.5708 | 0.5262 | 1.0000 | n/a | 0.6471 | 0.4058 | 0.1761 |
| Enriched boosted tree VOR v1 | 0.5178 | 0.7026 | 0.5818 | 0.5267 | n/a | n/a | 0.6436 | 0.4108 | 0.1639 |

Validation read:

- Logistic elite v1 slightly improves top-N versus Phase 32.10 logistic elite, but captured points and VOR captured are lower.
- Linear points v1 improves overall pairwise versus Phase 32.10 linear points.
- Boosted tree v1 has the best validation top-N in the v1 group, but lacks pairwise metrics due score-comparison sparsity.

## 2025 Holdout Results

| Candidate | Top-N | Captured | VOR captured | Rank corr | High-conf | Overall pairwise | NDCG | Tier acc | Bust |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Enriched logistic elite v1 | 0.8562 | 0.9021 | 0.8529 | 0.5543 | 0.7408 | 0.7636 | 0.7779 | 0.7044 | 0.0012 |
| Enriched linear points v1 | 0.8527 | 0.9015 | 0.8514 | 0.5590 | 0.9013 | 0.9454 | 0.7771 | 0.7034 | 0.0012 |
| Enriched linear VOR v1 | 0.8423 | 0.8940 | 0.8407 | 0.5389 | n/a | n/a | 0.7667 | 0.6860 | 0.0012 |
| Enriched boosted tree VOR v1 | 0.8532 | 0.8989 | 0.8482 | 0.5580 | n/a | n/a | 0.7734 | 0.6989 | 0.0012 |

Holdout read:

- Logistic elite v1 is the best v1 model on top-N, captured points, VOR captured, NDCG, and tier accuracy.
- Linear points v1 remains the best pairwise-style model because overall pairwise is 0.9454.
- Neither result justifies champion activation in this phase.

## 2024-2025 Combined Context

| Candidate | Top-N | Captured | VOR captured | Rank corr | High-conf | Overall pairwise | NDCG | Tier acc | Bust |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Enriched logistic elite v1 | 0.6866 | 0.8030 | 0.6972 | 0.5451 | 0.7419 | 0.6392 | 0.7125 | 0.5558 | 0.0822 |
| Enriched linear points v1 | 0.6824 | 0.8015 | 0.6963 | 0.5521 | 0.9098 | 0.8361 | 0.7125 | 0.5552 | 0.0854 |
| Enriched linear VOR v1 | 0.6743 | 0.7950 | 0.6865 | 0.5325 | 1.0000 | n/a | 0.7069 | 0.5459 | 0.0886 |
| Enriched boosted tree VOR v1 | 0.6855 | 0.8007 | 0.6960 | 0.5424 | n/a | n/a | 0.7085 | 0.5548 | 0.0825 |

Compared with Phase 32.10:

- Logistic elite: top-N improved from 0.6861 to 0.6866, captured declined from 0.8051 to 0.8030, VOR declined from 0.7031 to 0.6972, NDCG declined from 0.7157 to 0.7125, bust improved from 0.0826 to 0.0822.
- Linear points: top-N improved from 0.6815 to 0.6824, captured improved from 0.8004 to 0.8015, VOR stayed flat at 0.6963, NDCG improved from 0.7090 to 0.7125, overall pairwise improved from 0.8178 to 0.8361.

Compared with current Pigskin baseline from Phase 32.10:

- Current Pigskin 2024-2025: top-N 0.6755, captured 0.7929, VOR 0.6800, high-confidence 0.7540, overall pairwise 0.7621, NDCG 0.7086, tier accuracy 0.5528, bust 0.0891.
- Enriched logistic v1 improves top-N, captured, VOR, NDCG, tier accuracy, and bust, but trails current Pigskin on high-confidence and overall pairwise.
- Enriched linear points v1 improves top-N, captured, VOR, overall pairwise, NDCG, tier accuracy, and bust, but the top-N edge is still under the 1.5 percentage point activation threshold.

## Feature Signal Summary

Model explanation read:

- Logistic elite v1 positive signals: `elite_week_rate_3yr`, `xfp_share_3yr`, `target_share_slope_3yr`, `spike_week_rate_3yr`, `carry_share_slope_3yr`, `wopr_slope_3yr`, `receiving_xfp_share_pbp_3yr`, `team_epa_per_play`, `rushing_xfp_share_pbp_3yr`.
- Logistic elite v1 negative signal: `bust_week_rate_3yr`.
- Boosted tree VOR v1 feature importance: `analytical_grade_proxy`, `total_points_slope_3yr`, `opportunity_score_proxy`, `elite_week_rate_3yr`, `fantasy_points_over_expectation_3yr`, `profile_points_score`, `wopr_slope_3yr`, `carries`, `rb_high_value_opportunity_score`, `availability_rate_3yr`.
- Linear VOR and linear points were noisy because missing-indicator weights dominated the top coefficients. Treat those models as predictive challengers, not clean explanation artifacts.

Read:

- xFP and weekly role-history signals helped enough to keep BQML alive as a challenger lane.
- Injury and availability did not become default-ranking proof. They remain risk flags unless owner approves a separate modifier path.
- Direct NGS remains the next source gap if the owner wants more feature signal before another retrain.

## Owner-Review Recommendation

Classification after Phase 32.24:

| Category | Entries |
|---|---|
| Live baseline | current Pigskin candidate score v1 |
| Strong challenger lanes | enriched BQML logistic elite v1; enriched BQML linear points v1; simple projection |
| Owner-review concepts | Stats02 WR/TE; QB Stats02; selected RB/PBP component lanes |
| Risk flags only | RB availability; TE availability; injury burden; missed-time risk |
| Rejected or not default | generic 5 percent availability blend; v2 trend-aware champion path; broad ensembles; injury-only candidates |
| Blocked | historical depth context |

No champion activation is supported.

Recommended next phase:

1. Phase 32.25: owner review of BQML enriched challenger, especially logistic elite and linear points.
2. Alternative: direct NGS receiving/rushing ingest if the owner wants source expansion first.
3. Alternative: generate formula-driven candidate rankings for owner review only, not live activation.

## Checks Run

- `python -m unittest tests.test_ranking_formula_backtests`
- `python -m py_compile src\ranking_formula_backtests.py`
- `python -m compileall -q src scripts`
- `python scripts/check_deployment_safety.py`
- `python scripts/run_bigquery_migrations.py --list-pending`
- `python scripts/run_bigquery_validations.py --dry-run`
- `python scripts/run_bigquery_validations.py --run --pattern ranking_backtest`
- `python scripts/run_bigquery_validations.py --run --pattern ranking_formula`

## Remaining Warnings

- Boosted tree training processed 14,098,005,969 bytes, materially more than the training SELECT dry-run estimate.
- Linear model feature explanations are noisy because missing-indicator coefficients dominate.
- Pairwise and high-confidence pairwise are not independent for recent SQL-native stored summaries.
- 2024 injury/availability coverage is sparse, so availability remains a risk flag only.
- Historical depth remains blocked.
- Live rankings remain unchanged at 1,140 active rows.
