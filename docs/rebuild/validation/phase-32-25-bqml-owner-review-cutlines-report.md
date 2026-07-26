# Phase 32.25: BQML Owner Review Cutlines Report

Final decision: BQML OWNER REVIEW READY

## Scope

Phase 32.25 converted the Phase 32.24 enriched BQML retrain into owner-review evidence. This phase used read-only BigQuery SQL against existing summary tables, the existing `ranking_backtest_feature_mart`, and already-trained BQML models.

No deploy occurred. No live rankings were regenerated. No champion formulas were activated. No new BQML models were trained. No hyperparameter tuning, Pigskin chat, Gemini, LLM-backed ranking generation, live Sleeper API, source ingest, detail-row write, global truncate, or old Python full tournament path was used.

## Files Changed

- `docs/rebuild/validation/phase-32-25-bqml-owner-review-cutlines-report.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

Commit hash: recorded after commit if committed.

## Git State

Before this phase:

- Latest commit: `2eb6c10 phase 32.24 retrain enriched bqml challengers`
- Worktree: standing untracked historical validation backlog remained.

After this phase:

- Only Phase 32.25 owner-review docs were changed.
- Historical validation backlog remained untracked and untouched.

## Evidence Rows Verified

| Check | Count |
|---|---:|
| BQML enriched run rows | 8 |
| BQML enriched summary rows | 128 |
| Detail rows for BQML enriched run prefix | 0 |
| `ranking_formula_champions` rows | 0 |
| Active live rankings | 1,140 |

Version prefix verified: `ranking_backtest_sql_native_bqml_enriched_v1`.

## Owner-Review Candidates

| Candidate | Label | Read |
|---|---|---|
| Current Pigskin candidate score v1 | live baseline | Remains live. Strong rank correlation and pairwise protection. |
| Enriched BQML logistic elite v1 | owner-review challenger | Better top-N, captured points, VOR captured, NDCG, tier accuracy, and bust rate than current Pigskin in combined Phase 32.24 evidence. Overall pairwise is weak. |
| Enriched BQML linear points v1 | owner-review challenger | Best enriched BQML board-ordering challenger. Strong overall pairwise and useful early-board cutline gains. |
| Enriched boosted tree VOR v1 | context only | Competitive top-N, but costly and lacks clear owner-review edge. |
| Enriched linear VOR v1 | context only | Weaker than the two primary challengers. |
| Simple projection | strong challenger lane | Clean baseline challenger. Still not a live replacement. |
| Stats02 WR/TE | owner-review concept | Useful source-lane concept, not an activation-ready champion. |
| Selected RB/PBP component lanes | owner-review concept | RB has pockets of signal. WR remains fragile. |
| Injury and availability | risk flag only | Useful as warning context, not as a default ranking formula. |
| Historical depth | blocked | Excluded from BQML v1 predictors. |

## Validation Comparison

2024 validation, from Phase 32.24 summary evidence:

| Candidate | Top-N | Captured | VOR captured | Rank corr | High-conf | Overall pairwise | NDCG | Tier acc | Bust |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Enriched logistic elite v1 | 0.5169 | 0.7039 | 0.5804 | 0.5359 | 0.7430 | 0.5148 | 0.6471 | 0.4071 | 0.1633 |
| Enriched linear points v1 | 0.5122 | 0.7016 | 0.5800 | 0.5452 | 0.9176 | 0.7268 | 0.6479 | 0.4071 | 0.1697 |
| Current Pigskin baseline | 0.4941 | 0.6845 | 0.5566 | 0.5167 | 0.7518 | 0.7581 | 0.6340 | 0.4002 | 0.1771 |

Read: both enriched models helped validation top-N, captured points, VOR captured, NDCG, tier accuracy, and bust rate versus current Pigskin. Linear points had the safer pairwise read. Logistic elite had a poor overall pairwise read.

## Holdout Comparison

2025 holdout, from Phase 32.24 summary evidence:

| Candidate | Top-N | Captured | VOR captured | Rank corr | High-conf | Overall pairwise | NDCG | Tier acc | Bust |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Enriched logistic elite v1 | 0.8562 | 0.9021 | 0.8529 | 0.5543 | 0.7408 | 0.7636 | 0.7779 | 0.7044 | 0.0012 |
| Enriched linear points v1 | 0.8527 | 0.9015 | 0.8514 | 0.5590 | 0.9013 | 0.9454 | 0.7771 | 0.7034 | 0.0012 |
| Current Pigskin baseline | 0.8569 | 0.9013 | 0.8536 | 0.5620 | 0.7741 | 0.7946 | 0.7832 | 0.7054 | 0.0012 |

Read: 2025 alone does not support replacing current Pigskin. Logistic is close on top-N and captured points but trails pairwise. Linear points is excellent on overall pairwise, but slightly weaker on top-N and rank correlation.

## Combined Comparison

2024-2025 combined context:

| Candidate | Top-N | Captured | VOR captured | Rank corr | High-conf | Overall pairwise | NDCG | Tier acc | Bust |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Enriched logistic elite v1 | 0.6866 | 0.8030 | 0.6972 | 0.5451 | 0.7419 | 0.6392 | 0.7125 | 0.5558 | 0.0822 |
| Enriched linear points v1 | 0.6824 | 0.8015 | 0.6963 | 0.5521 | 0.9098 | 0.8361 | 0.7125 | 0.5552 | 0.0854 |
| Current Pigskin baseline | 0.6755 | 0.7929 | 0.6800 | 0.6219 | 0.7540 | 0.7621 | 0.7086 | 0.5528 | 0.0891 |
| Simple projection | 0.6803 | 0.7969 | 0.6932 | 0.6261 | 0.7407 | 0.7441 | 0.7163 | 0.5578 | 0.0887 |
| Phase 32.10 BQML logistic elite | 0.6861 | 0.8051 | 0.7031 | 0.5476 | 0.7468 | 0.6405 | 0.7157 | 0.5529 | 0.0826 |
| Phase 32.10 BQML linear points | 0.6815 | 0.8004 | 0.6963 | 0.5425 | 0.9098 | 0.8178 | 0.7090 | 0.5544 | 0.0841 |

Metric sanity note: top-level pairwise and high-confidence pairwise may be the same stored value for recent SQL-native summaries. This report treats `metric_json.overall_pairwise_draft_win_rate` as the separate cross-position board-ordering read.

## Position-by-Position Read

Read-only `ML.PREDICT` and feature-mart comparison for PPR 2024-2025:

| Position | Logistic elite v1 | Linear points v1 | Label |
|---|---|---|---|
| QB | Mixed. Helps 2024 QB, trails 2025 QB. | Better than logistic on 2024 QB and slightly better on 2025 QB. | linear points owner-review challenger |
| RB | Strongest position for both models. Logistic has the cleaner RB24/RB36 VOR read. | Good early-board and RB12 read. | owner-review challenger |
| WR | Both hurt 2024 WR and are soft around WR12/WR24. Logistic recovers a little in 2025 WR. | Better board-ordering but still not a WR replacement. | component signal only |
| TE | Logistic is safer than linear around TE12/TE18. Both trail 2025 TE baseline. | Linear loses more TE12 and holdout TE ground. | logistic context, not champion |
| Overall board | Logistic improves top-N but weakens overall pairwise. | Linear points improves early-board cutlines and overall pairwise. | linear points owner-review challenger |

## Cutline Results

Cutline deltas versus current Pigskin, averaged across PPR 2024 and 2025. Positive top-N, captured, and VOR deltas are good. Negative bust deltas are good.

### Overall Draft Board

| Cutline | Logistic top-N | Logistic captured | Logistic VOR | Logistic bust | Linear top-N | Linear captured | Linear VOR | Linear bust |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Top 24 | +0.0541 | +0.0228 | +0.0699 | -0.0657 | +0.1412 | +0.1043 | +0.0661 | -0.1128 |
| Top 50 | +0.0385 | +0.0418 | +0.0584 | -0.0147 | +0.0628 | +0.0790 | +0.0504 | -0.0324 |
| Top 100 | +0.0128 | +0.0130 | +0.0156 | -0.0059 | +0.0244 | +0.0234 | +0.0049 | -0.0019 |

Read: linear points is the cleaner owner-review board-ordering challenger. Logistic protects VOR well, but its pairwise weakness means it should not drive the board alone.

### Position Cutlines

| Cutline | Logistic top-N | Logistic captured | Logistic VOR | Linear top-N | Linear captured | Linear VOR | Read |
|---|---:|---:|---:|---:|---:|---:|---|
| QB6 | +0.0023 | -0.0110 | +0.0134 | +0.0220 | +0.0048 | +0.0271 | Linear helps the elite QB cut. |
| QB12 | +0.0041 | -0.0137 | -0.0049 | +0.0150 | +0.0015 | +0.0112 | Linear is stronger. |
| RB12 | +0.0185 | +0.0019 | +0.0362 | +0.0231 | +0.0099 | +0.0378 | Both are worth owner review. |
| RB24 | +0.0119 | +0.0133 | +0.0626 | +0.0098 | +0.0109 | +0.0546 | Logistic has the best RB24 VOR read. |
| WR12 | -0.0220 | -0.0284 | -0.0239 | -0.0093 | -0.0183 | -0.0110 | Neither should own WR early tiers. |
| WR24 | -0.0139 | -0.0181 | -0.0181 | -0.0197 | -0.0222 | -0.0196 | WR is a weakness. |
| TE6 | +0.0104 | -0.0273 | -0.0048 | +0.0069 | -0.0248 | -0.0086 | Hit rate improves, value capture weakens. |
| TE12 | -0.0058 | -0.0060 | +0.0006 | -0.0255 | -0.0187 | -0.0116 | Logistic is safer, but not strong. |
| TE18 | +0.0100 | +0.0073 | +0.0277 | -0.0046 | -0.0015 | +0.0163 | Logistic has a usable TE depth signal. |

## Player Movement Examples

Read-only movement examples use Week 17 validation/holdout rows, current Pigskin rank, BQML rank, actual rank, and available explanation fields. They are examples, not causal claims.

### Useful Risers

| Model | Season | Player | Pos | Current rank | BQML rank | Actual rank | Read |
|---|---:|---|---|---:|---:|---:|---|
| Logistic elite | 2024 | Kyren Williams | RB | 26 | 2 | 8 | Good RB riser. Strong spike-week and role-history context. |
| Linear points | 2024 | Kyren Williams | RB | 26 | 1 | 8 | Same useful RB move, with stronger points-model score. |
| Logistic elite | 2024 | Jerome Ford | RB | 47 | 25 | 52 | Riser did not pay off enough. Useful warning for false optimism. |
| Linear points | 2024 | Jameson Williams | WR | 83 | 60 | 7 | BQML moved him up, but still not enough. WR upside detection exists but is too conservative. |

### Fallers and Busts Avoided

| Model | Season | Player | Pos | Current rank | BQML rank | Actual rank | Read |
|---|---:|---|---|---:|---:|---:|---|
| Logistic elite | 2024 | Tyler Higbee | TE | 8 | 13 | 30 | Avoided a current TE bust. |
| Logistic elite | 2024 | Trey Lance | QB | 11 | 19 | 33 | Avoided a current QB bust. |
| Linear points | 2024 | Ezekiel Elliott | RB | 13 | 27 | 70 | Avoided a current RB bust. |
| Linear points | 2024 | Terry McLaurin | WR | 24 | 26 | 93 | Slight demotion avoided a WR bust at the edge. |

### False Positives

| Model | Season | Player | Pos | BQML rank | Actual rank | Read |
|---|---:|---|---|---:|---:|---|
| Logistic elite | 2024 | C.J. Stroud | QB | 4 | 26 | Major false positive. |
| Linear points | 2024 | C.J. Stroud | QB | 6 | 26 | Same miss, less aggressive. |
| Logistic elite | 2024 | Cooper Kupp | WR | 5 | 70 | Age/injury context did not protect enough. |
| Linear points | 2024 | Cooper Kupp | WR | 9 | 70 | Same WR false positive. |

### False Negatives and Hits Lost

| Model | Season | Player | Pos | BQML rank | Actual rank | Read |
|---|---:|---|---|---:|---:|---|
| Logistic elite | 2024 | Tee Higgins | WR | 29 | 1 | Big WR miss and hit lost. |
| Linear points | 2024 | Marvin Mims | WR | 67 | 2 | Severe WR false negative. |
| Logistic elite | 2024 | Baker Mayfield | QB | 13 | 2 | Just missed QB12. |
| Linear points | 2024 | Zach Ertz | TE | 18 | 2 | TE false negative. |

Movement read: BQML is most useful for RB and early board review. WR movement is the biggest risk. Both models can demote busts, but they also miss spike outcomes that current Pigskin sometimes keeps closer to the cutline.

## Feature Signal Summary

Logistic elite v1:

- Strong positive signals from Phase 32.24: `elite_week_rate_3yr`, `xfp_share_3yr`, `target_share_slope_3yr`, `spike_week_rate_3yr`, `carry_share_slope_3yr`, `wopr_slope_3yr`, `receiving_xfp_share_pbp_3yr`, `team_epa_per_play`, and `rushing_xfp_share_pbp_3yr`.
- Strong negative signal: `bust_week_rate_3yr`.
- xFP and PBP xFP helped enough to keep the model in owner review.
- Injury and availability did not prove a default formula. Keep them as risk flags.
- Role-history metrics helped. This is the cleanest explanation lane for logistic.

Linear points v1:

- Useful as a predictive board-ordering model.
- Feature explanation is noisy because missing indicators dominated top coefficients in Phase 32.24.
- Owner review should treat it as a challenger score, not as a clean explanation artifact.

Boosted tree VOR v1:

- Feature importance included `analytical_grade_proxy`, `total_points_slope_3yr`, `opportunity_score_proxy`, `elite_week_rate_3yr`, `fantasy_points_over_expectation_3yr`, `profile_points_score`, `wopr_slope_3yr`, `carries`, `rb_high_value_opportunity_score`, and `availability_rate_3yr`.
- It was expensive and did not earn primary challenger status.

## Owner Decision Summary

Best top-N/VOR/NDCG/bust control:

- Enriched logistic elite v1 is the stronger top-N utility challenger in the Phase 32.24 combined table and has useful RB/TE depth behavior.

Best board-ordering and overall pairwise:

- Enriched linear points v1 is the better owner-review model for cross-position draft-board ordering.

Should either generate candidate rankings for owner review?

- Yes, but review-only. Generate BQML candidate rankings for owner review only if the owner wants to inspect actual board movement. Do not activate a champion and do not replace current Pigskin.

Should current Pigskin remain live baseline?

- Yes. It still protects rank correlation and pairwise behavior better than the enriched challengers.

Should NGS ingest remain next?

- Yes. If the owner wants better feature signal before more model work, direct NGS receiving/rushing remains the cleanest next source gap.

Should availability stay risk-flag only?

- Yes. Injury burden and missed-time risk are useful warnings, not default ranking formulas.

## Recommended Next Phase

Recommended options:

1. Phase 32.26: generate BQML candidate rankings for owner review only.
2. Phase 32.26: direct NGS receiving/rushing ingest.
3. Phase 32.26: owner selection of challenger lane.

Default recommendation: generate BQML candidate rankings only if the owner wants to inspect player-level board movement. Otherwise move to direct NGS receiving/rushing ingest.

## Checks Run

- BigQuery read-only evidence verification for run rows, summary rows, detail rows, champions, and active live rankings.
- BigQuery read-only `ML.PREDICT` position comparison for current Pigskin, enriched logistic elite v1, and enriched linear points v1.
- BigQuery read-only cutline analysis for QB, RB, WR, TE, overall top-N, and pick-band cutlines.
- BigQuery read-only movement examples with existing trained models.
- `git diff --check`

## No-Live-Change Confirmation

- Live rankings remain unchanged at 1,140 active rows.
- `ranking_formula_champions` remains 0.
- No detail rows were written.
- No champion activation occurred.
- No production or staging deploy occurred.
- No Pigskin model-visible tool exposure changed.

## Remaining Warnings

- WR movement is not trustworthy enough for owner-review challenger status by itself.
- Logistic elite v1 has weak overall pairwise.
- Linear points v1 is hard to explain cleanly because missing-indicator coefficients were prominent.
- 2024 injury and availability coverage is sparse.
- Historical depth context remains blocked.
