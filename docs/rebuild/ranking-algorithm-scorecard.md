# Ranking Algorithm Scorecard

Last updated: 2026-07-06

## Purpose

This scorecard records every controlled ranking-algorithm tournament for Pigskin rankings. It is permanent release evidence, not a production activation switch. A formula can win here and still remain inactive until owner review, champion selection, and a separate ranking-generation phase.

## Current Live Ranking Algorithm

Live Player Profiles rankings are still generated outside the formula champion path.

Current deterministic candidate baseline:

- `current_pigskin_candidate_score_v1`
- Contract candidate ID pattern: `ranking_formula_<position>_current_pigskin_candidate_score_v1_2026_001`
- Formula proxy used in tournament:
  - `0.55 * analytical_grade_proxy`
  - `0.15 * opportunity_score_proxy`
  - `0.10 * efficiency_score_proxy`
  - `0.10 * role_stability_score`
  - `0.10 * profile_points_score`

This mirrors the deterministic candidate scoring weights in `src/materialize.py`. The live app also uses current Sleeper eligibility and depth-chart penalties. Those live roster penalties are not historically replayed in this tournament, and they were not filled with zero.

LLM final ranking baseline:

- `current_pigskin_llm_final_v3`
- Status: documented only
- Reason skipped: historical replay would require Gemini calls by season, scoring profile, and position. This phase explicitly forbids LLM calls.

## Accuracy Target

The practical target is a formula that beats the current deterministic baseline across multiple seasons and profiles without relying on high missing-input rates. For this first tournament, a clear win means at least a 1.5 percentage point average pairwise edge with acceptable missing-input rates.

## Scoring Profiles Covered

- `ppr`
- `half_ppr`
- `standard`
- `gng_keeper`

## Historical Seasons Covered

Target seasons: 2017 through 2025.

Rolling source windows:

- 2014-2016 to 2017
- 2015-2017 to 2018
- 2016-2018 to 2019
- 2017-2019 to 2020
- 2018-2020 to 2021
- 2019-2021 to 2022
- 2020-2022 to 2023
- 2021-2023 to 2024
- 2022-2024 to 2025

Target-season features are excluded.

## Algorithm Registry

| Algorithm family | Status | Features used | Notes |
|---|---|---|---|
| `current_pigskin_candidate_score_v1` | baseline | analytical grade proxy, opportunity proxy, efficiency proxy, role stability, profile points | Best numeric stand-in for current deterministic candidate scoring. |
| `current_pigskin_llm_final_v3` | documented baseline | Gemini final adjudication and candidate evidence | Not replayed. LLM calls are intentionally skipped. |
| `seeded_v0` | challenger | seeded weighted formula families | Some rows still rely on unavailable `pigskin_context_score`, so missing rates are high. |
| `v1_improved_mappings` | challenger | safer v1 feature mappings | Lower missing rate than seeded v0, weaker aggregate win rate. |
| `v2_trend_aware` | challenger | rolling three-year trend features | Underperformed in the full tournament. |
| `equal_weight_normalized_blend` | challenger | recent points, usage, EPA, availability, profile points | Simple and low-missing. |
| `value_over_replacement_baseline` | challenger | profile points, recent points, availability | Stable but not the best aggregate family. |
| `scarcity_adjusted_draft_value_baseline` | challenger | profile points, usage, role stability, opportunity trend, availability | Useful in selected RB/QB slices. |
| `simple_projection_points_baseline` | challenger | profile points score only | Best aggregate pairwise score, but not enough to clearly replace the baseline. |
| BigQuery ML baselines | owner-review challenger | feature mart predictors only | Phase 32.10 trained bounded BQML linear, logistic, and boosted-tree prototypes. No champion is active. |
| Python ML baselines | skipped | none | `scikit-learn` was not installed. No packages were installed. |

## Tournament History

### Phase 32.5: Rolling multi-year tournament

Backtest version: `ranking_backtest_tournament_v0_rolling_2017_2025`

Evidence written:

- `ranking_backtest_runs`: 36 rows
- `ranking_backtest_results`: 1,874,928 rows
- `ranking_backtest_candidate_summaries`: 1,728 rows

Not written:

- `ranking_formula_champions`
- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_candidates`

### Phase 32.6: BigQuery-native optimization and overall draft-value prototype

Phase 32.6 did not rerun the tournament. It used existing Phase 32.5 result rows to prototype cross-position draft-value metrics and identify the highest-ROI backtest engine changes.

Key outcomes:

- Current Pigskin remains the live baseline.
- Simple projection remains the strongest challenger, but still only ties the baseline.
- True overall draft-value metrics can be calculated from existing detail rows.
- Future tournaments should move feature scoring, ranking, and summary metrics into BigQuery SQL.
- Exploratory runs should write summaries only unless full detail rows are explicitly needed.

### Phase 32.7: Ranking backtest feature mart and SQL-native scoring prototype

Phase 32.7 added the additive `ranking_backtest_feature_mart` table and populated a bounded 2025 slice for `ppr`, `half_ppr`, `standard`, and `gng_keeper` across QB/RB/WR/TE. The slice contains 6,764 rows and uses the 2022-2024 source window for 2025 targets.

SQL-native scoring prototype:

| Candidate | Rows | Top-N | Captured points | VOR captured | Missing |
|---|---:|---:|---:|---:|---:|
| current Pigskin candidate | 392 | 0.7778 | 0.8676 | 0.8629 | 0.0045 |
| simple projection points | 392 | 0.7778 | 0.8646 | 0.8547 | 0.0000 |
| v2 trend balanced | 392 | 0.5648 | 0.5878 | 0.4824 | 0.0159 |

Scope: PPR, 2025, TE only. No champion was activated. The SQL prototype matched existing Python evidence on row count, top-N, captured points, and rank direction closely enough to proceed toward a SQL-native engine.

Detail-row policy:

- Official tournaments may write full detail rows.
- Exploratory runs should write summaries only.
- Debug runs should write sampled detail rows.
- Pairwise detail rows should be skipped unless explicitly requested.

## Leaderboard By Position

Best average pairwise result by scoring profile and position:

| Profile | Position | Leader | Pairwise | High-confidence | Top-N | VOR captured | Missing |
|---|---|---|---:|---:|---:|---:|---:|
| `gng_keeper` | QB | current Pigskin baseline | 0.6252 | 0.6731 | 0.5708 | 0.6128 | 0.0013 |
| `gng_keeper` | RB | simple projection points | 0.6856 | 0.7617 | 0.6057 | 0.6210 | 0.0008 |
| `gng_keeper` | TE | seeded v0 balanced | 0.6661 | 0.8027 | 0.4402 | 0.4920 | 0.5217 |
| `gng_keeper` | WR | seeded v0 balanced | 0.6866 | 0.7899 | 0.4651 | 0.5437 | 0.4022 |
| `half_ppr` | QB | simple projection points | 0.6438 | 0.6859 | 0.5741 | 0.6174 | 0.0000 |
| `half_ppr` | RB | simple projection points | 0.6969 | 0.7496 | 0.6274 | 0.6536 | 0.0008 |
| `half_ppr` | TE | seeded v0 balanced | 0.6719 | 0.7884 | 0.4689 | 0.5405 | 0.5217 |
| `half_ppr` | WR | seeded v0 balanced | 0.6949 | 0.7842 | 0.4994 | 0.5779 | 0.4022 |
| `ppr` | QB | simple projection points | 0.6436 | 0.6857 | 0.5736 | 0.6173 | 0.0000 |
| `ppr` | RB | simple projection points | 0.6967 | 0.7446 | 0.6307 | 0.6536 | 0.0008 |
| `ppr` | TE | seeded v0 balanced | 0.6757 | 0.7848 | 0.4857 | 0.5556 | 0.5217 |
| `ppr` | WR | simple projection points | 0.6993 | 0.7498 | 0.5156 | 0.6130 | 0.0006 |
| `standard` | QB | simple projection points | 0.6438 | 0.6861 | 0.5746 | 0.6176 | 0.0000 |
| `standard` | RB | simple projection points | 0.6971 | 0.7535 | 0.6245 | 0.6493 | 0.0008 |
| `standard` | TE | seeded v0 balanced | 0.6647 | 0.7912 | 0.4468 | 0.5103 | 0.5217 |
| `standard` | WR | seeded v0 balanced | 0.6869 | 0.7811 | 0.4872 | 0.5562 | 0.4022 |

## Leaderboard By Scoring Profile

The profile-position leader often beats the current deterministic baseline by less than 0.6 percentage points. That is a tie for practical rollout purposes.

| Profile | Clear baseline losses? | Notes |
|---|---|---|
| `ppr` | No | Best challengers are approximately tied with baseline. |
| `half_ppr` | No | Same pattern as PPR. |
| `standard` | No | Simple projection is strong but not a clear replacement. |
| `gng_keeper` | No | Current baseline wins QB; challengers are close elsewhere. |

## Overall Draft-Value Leaderboard

Phase 32.5 position-level results remain below. Phase 32.6 added a read-only prototype for true cross-position draft-value metrics using the existing tournament detail rows. Those prototype results do not activate a champion.

Family-level aggregate:

| Family | Pairwise | High-confidence | Top-N | VOR captured | Captured points | Missing |
|---|---:|---:|---:|---:|---:|---:|
| simple projection points | 0.6728 | 0.7364 | 0.5387 | 0.5956 | 0.7115 | 0.0006 |
| current Pigskin candidate | 0.6697 | 0.7575 | 0.5400 | 0.5981 | 0.7123 | 0.0032 |
| scarcity adjusted draft value | 0.6660 | 0.7394 | 0.5374 | 0.5900 | 0.7094 | 0.0365 |
| value over replacement | 0.6601 | 0.7265 | 0.5223 | 0.5651 | 0.6928 | 0.0004 |
| equal weight blend | 0.6577 | 0.7299 | 0.5185 | 0.5541 | 0.6858 | 0.0018 |
| v1 improved mappings | 0.6496 | 0.7261 | 0.5134 | 0.5488 | 0.6819 | 0.1110 |
| seeded v0 | 0.6353 | 0.6968 | 0.4859 | 0.5228 | 0.6479 | 0.4314 |
| v2 trend aware | 0.5491 | 0.5630 | 0.3919 | 0.3887 | 0.5402 | 0.1157 |

Phase 32.6 overall draft-value prototype:

| Family | Top-100 overall hit | Top-100 pairwise | VOR captured |
|---|---:|---:|---:|
| current Pigskin candidate | 0.5808 | 0.6721 | 0.9922 |
| scarcity adjusted draft value | 0.5807 | 0.6687 | 0.9923 |
| simple projection points | 0.5804 | 0.6730 | 0.9934 |
| value over replacement | 0.5802 | 0.6629 | 0.9917 |
| v1 improved mappings | 0.5802 | 0.6528 | 0.9892 |
| equal weight blend | 0.5802 | 0.6578 | 0.9908 |
| seeded v0 | 0.5802 | 0.6345 | 0.9932 |
| v2 trend aware | 0.5770 | 0.5448 | 0.9767 |

Interpretation: the overall metrics are tightly clustered at top 100 because the available player universe is broad and many candidates select similar top-end players. The top-100 pairwise metric still puts simple projection slightly ahead, but the edge over current Pigskin is about 0.001. That is not a replacement signal.

## Phase 32.8 SQL-Native Tournament Engine

Phase 32.8 expanded `ranking_backtest_feature_mart` from the bounded 2025 slice to rolling target seasons 2017 through 2025. The mart now contains 156,244 rows across PPR, Half PPR, Standard, GNG Keeper, and QB/RB/WR/TE.

The official new path is BigQuery-native:

- `ranking_backtest_feature_mart` is the only tournament feature source.
- Formula weights are converted to SQL rows.
- BigQuery window functions rank players by week, profile, and position.
- Summary metrics are computed in SQL.
- Future controlled writes use `CREATE TEMP TABLE ... AS SELECT` plus `INSERT ... SELECT` into `ranking_backtest_runs` and `ranking_backtest_candidate_summaries`.
- Exploratory runs remain summary-only. Detail rows are reserved for official snapshots.

Draft-utility metrics are persisted in `ranking_backtest_candidate_summaries.metric_json` rather than new columns:

- `ndcg_at_k`
- `value_captured_at_k`
- `elite_recall_at_k`
- `tier_accuracy`
- `bust_rate`
- `pick_band_regret`
- `overall_pairwise_draft_win_rate`
- `high_confidence_pairwise_win_rate`
- `value_over_replacement_captured_rate`

SQL-native read-only tournament runtime:

| Scope | Summary rows | Runtime | Bytes processed |
|---|---:|---:|---:|
| 2017-2025, four profiles, four positions, 16 candidates | 64 | 6.195s | 53,106,789 |

Bounded PPR 2025 TE SQL-native comparison:

| Candidate | Top-N | Captured points | VOR captured | Rank corr | Missing |
|---|---:|---:|---:|---:|---:|
| current Pigskin candidate | 0.7778 | 0.8624 | 0.8570 | 0.5394 | 0.0045 |
| simple projection points | 0.7778 | 0.8605 | 0.8522 | 0.5732 | 0.0000 |
| scarcity adjusted draft value | 0.7037 | 0.7902 | 0.7520 | 0.4659 | 0.0010 |
| v2 trend balanced | 0.5648 | 0.5911 | 0.4850 | 0.0735 | 0.0159 |

The current Pigskin candidate remains the live baseline. Simple projection remains close, but this SQL-native pass does not create a replacement signal. The v2 trend candidate still underperforms on the bounded TE slice.

VOR standardization for SQL-native runs:

- replacement baseline is position-specific weekly replacement rank: QB 12, RB 24, WR 24, TE 12.
- VOR is `GREATEST(actual_points - replacement_points, 0)`.
- replacement points are computed per target season, target week, scoring profile, league type, roster format, and position.
- captured VOR is aggregated across weekly top-K selections before division.

BigQuery ML remains a follow-up. The feature mart is ready to support linear regression, boosted tree regression, random forest regression, and logistic top-N classification using predictor columns only. Target choices should start with `target_fantasy_points`, `value_over_replacement`, and top-K labels.

## Phase 32.9 SQL-Native Source Of Truth

Phase 32.9 accepts the SQL-native tournament summary path as the preferred tournament evidence source. Python tournament evidence remains a historical reference only.

Controlled summary-only write:

- version: `ranking_backtest_sql_native_v0_rolling_2017_2025`
- run rows written: 4
- summary rows written: 112
- detail rows written: 0
- write job ID: `4d58afe0-9450-4fd9-82da-56df6731cb94`
- write duration: 20.593s
- bytes processed: 54,643,889
- slot millis: 579,109

The write used BigQuery scripting with a temporary SQL-native summary table and `INSERT ... SELECT`. It did not use Python player/candidate/week result rows.

SQL-native family leaderboard from persisted summaries:

| Family | Top-N | Captured points | VOR captured | Rank corr | High-confidence | Overall pairwise | NDCG@K | Tier accuracy | Bust rate | Missing |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| current Pigskin baseline | 0.5411 | 0.7132 | 0.6007 | 0.5079 | 0.7385 | 0.7455 | 0.6578 | 0.4307 | 0.1592 | 0.0050 |
| simple projection points | 0.5399 | 0.7121 | 0.5970 | 0.5145 | 0.7238 | 0.7262 | 0.6589 | 0.4353 | 0.1601 | 0.0000 |
| scarcity adjusted draft value | 0.5386 | 0.7098 | 0.5908 | 0.5078 | 0.7202 | 0.7289 | 0.6463 | 0.4278 | 0.1553 | 0.0273 |
| value over replacement | 0.5233 | 0.6935 | 0.5658 | 0.4922 | 0.7126 | 0.7189 | 0.6360 | 0.4221 | 0.1683 | 0.0005 |
| equal weight blend | 0.5194 | 0.6868 | 0.5551 | 0.4853 | 0.7146 | 0.7214 | 0.6305 | 0.4183 | 0.1700 | 0.0018 |
| v1 improved mappings | 0.5151 | 0.6834 | 0.5503 | 0.4714 | 0.7105 | 0.7180 | 0.6259 | 0.4146 | 0.1697 | 0.1357 |
| v2 trend balanced | 0.4059 | 0.5558 | 0.4033 | 0.2070 | 0.5559 | 0.5554 | 0.4840 | 0.3305 | 0.2936 | 0.1684 |

Decision: current Pigskin remains the baseline. Simple projection is close on rank correlation and NDCG, but it does not beat the current baseline on captured points, VOR captured, high-confidence pairwise, or overall pairwise. No champion is active.

Metric gap closure:

- `overall_pairwise_draft_win_rate` is now implemented in SQL.
- It is bounded to rows where either side is top 100 by predicted or actual overall rank.
- It also requires at least a 10-point predicted-score delta to avoid full pairwise explosion.
- All persisted summary rows have populated draft-utility metrics in `metric_json`.

North star: this remains a top-heavy, scarcity-aware draft ranking problem. Raw point projection alone is not enough.

## Phase 32.10 BigQuery ML Baseline Prototype

Phase 32.10 kept the accepted SQL-native tournament path as the evaluation source and trained bounded BigQuery ML prototypes from `ranking_backtest_feature_mart`.

Model policy:

- train seasons: 2017 through 2023
- validation season: 2024
- holdout season: 2025
- primary split: chronological, with `data_split_method='NO_SPLIT'`
- random forest: skipped by default
- DNN, AutoML, remote, Gemini-backed models, and hyperparameter tuning: skipped
- live ranking writes: none
- champion activation: none

Trained BQML models:

| Model | Type | Target |
|---|---|---|
| `ranking_bqml_linear_vor_v0` | linear regression | value over replacement |
| `ranking_bqml_linear_points_v0` | linear regression | target fantasy points |
| `ranking_bqml_logistic_elite_v0` | logistic regression | position-specific elite finish |
| `ranking_bqml_boosted_tree_vor_v0` | boosted tree regression | value over replacement |

2024-2025 SQL-native comparison:

| Family | Top-N | Captured points | VOR captured | Rank corr | High-confidence | Overall pairwise | NDCG@K | Tier accuracy | Bust rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BQML logistic elite | 0.6861 | 0.8051 | 0.7031 | 0.5476 | 0.7468 | 0.6405 | 0.7157 | 0.5529 | 0.0826 |
| BQML linear VOR | 0.6824 | 0.8003 | 0.6941 | 0.5313 | n/a | n/a | 0.7082 | 0.5488 | 0.0849 |
| BQML linear points | 0.6815 | 0.8004 | 0.6963 | 0.5425 | 0.9098 | 0.8178 | 0.7090 | 0.5544 | 0.0841 |
| BQML boosted tree VOR | 0.6762 | 0.7936 | 0.6890 | 0.5340 | n/a | n/a | 0.6996 | 0.5542 | 0.0905 |
| scarcity adjusted draft value | 0.6811 | 0.7967 | 0.6965 | 0.6233 | 0.7373 | 0.7484 | 0.6896 | 0.5385 | 0.0846 |
| simple projection points | 0.6803 | 0.7969 | 0.6932 | 0.6261 | 0.7407 | 0.7441 | 0.7163 | 0.5578 | 0.0887 |
| current Pigskin baseline | 0.6755 | 0.7929 | 0.6800 | 0.6219 | 0.7540 | 0.7621 | 0.7086 | 0.5528 | 0.0891 |

Decision: BQML is now a useful challenger lane, not an active champion. Logistic elite clears the current baseline on top-N, captured points, VOR captured, NDCG, tier accuracy, and bust rate for the 2024-2025 window, but the top-N edge is about 1.06 percentage points, below the 1.5-point owner-review activation threshold. Its overall pairwise result is also weaker than current Pigskin. Linear points is interesting because its high-confidence and overall pairwise rates are strong, but it does not separate enough on top-N.

Next research direction: test a constrained ensemble that blends current Pigskin, simple projection, and BQML signals through the same SQL-native evaluator. Do not activate a champion without owner review.

## Phase 32.11 Constrained Ensemble Prototype

Phase 32.11 tested five constrained convex ensembles with SQL-native evaluation. The ensembles blended current Pigskin, simple projection, scarcity-adjusted draft value, BQML logistic elite, and BQML linear points. No Python player-week result rows were built.

Split policy:

- reference seasons: 2017 through 2023
- validation and tuning season: 2024
- holdout season: 2025
- 2025 was not used to choose weights

Ensemble weights:

| Ensemble | Current | Simple | Scarcity | BQML logistic | BQML linear points |
|---|---:|---:|---:|---:|---:|
| conservative Pigskin-plus | 0.60 | 0.20 | 0.10 | 0.10 | 0.00 |
| elite-probability blend | 0.40 | 0.20 | 0.10 | 0.30 | 0.00 |
| pairwise-strength blend | 0.40 | 0.20 | 0.10 | 0.00 | 0.30 |
| balanced research blend | 0.35 | 0.20 | 0.15 | 0.15 | 0.15 |

Position-aware first draft:

| Position | Current | Simple | Scarcity | BQML logistic | BQML linear points |
|---|---:|---:|---:|---:|---:|
| QB | 0.45 | 0.15 | 0.10 | 0.10 | 0.20 |
| RB | 0.30 | 0.25 | 0.20 | 0.20 | 0.05 |
| WR | 0.35 | 0.25 | 0.10 | 0.20 | 0.10 |
| TE | 0.55 | 0.20 | 0.10 | 0.10 | 0.05 |

Validation season 2024:

| Candidate | Top-N | Captured points | VOR captured | Rank corr | High-confidence | Overall pairwise | NDCG@K | Tier accuracy | Bust rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| scarcity adjusted draft value | 0.5218 | 0.7100 | 0.5951 | 0.5215 | 0.7368 | 0.7467 | 0.6392 | 0.3991 | 0.1681 |
| BQML logistic elite | 0.5165 | 0.7073 | 0.5888 | 0.5332 | 0.7445 | 0.5096 | 0.6501 | 0.3998 | 0.1641 |
| BQML linear points | 0.5120 | 0.7035 | 0.5839 | 0.5399 | 0.9245 | 0.6914 | 0.6471 | 0.4098 | 0.1671 |
| balanced research blend | 0.5084 | 0.7002 | 0.5782 | 0.5359 | 0.7200 | 0.4910 | 0.6454 | 0.4062 | 0.1659 |
| elite-probability blend | 0.5069 | 0.6983 | 0.5740 | 0.5339 | 0.7189 | 0.4906 | 0.6450 | 0.4048 | 0.1651 |
| pairwise-strength blend | 0.5056 | 0.6977 | 0.5751 | 0.5386 | 0.7201 | 0.4878 | 0.6443 | 0.4060 | 0.1688 |
| position-aware first draft | 0.5048 | 0.6942 | 0.5690 | 0.5341 | 0.7186 | 0.4860 | 0.6423 | 0.4017 | 0.1719 |
| conservative Pigskin-plus | 0.5016 | 0.6912 | 0.5638 | 0.5288 | 0.7148 | 0.4748 | 0.6401 | 0.4008 | 0.1743 |
| simple projection points | 0.4996 | 0.6902 | 0.5701 | 0.5230 | 0.7415 | 0.7436 | 0.6411 | 0.4015 | 0.1762 |
| current Pigskin baseline | 0.4941 | 0.6845 | 0.5566 | 0.5167 | 0.7518 | 0.7581 | 0.6340 | 0.4002 | 0.1771 |

Holdout season 2025:

| Candidate | Top-N | Captured points | VOR captured | Rank corr | High-confidence | Overall pairwise | NDCG@K | Tier accuracy | Bust rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| simple projection points | 0.8611 | 0.9036 | 0.8567 | 0.5645 | 0.7451 | 0.7572 | 0.7916 | 0.7141 | 0.0012 |
| conservative Pigskin-plus | 0.8598 | 0.9031 | 0.8548 | 0.5699 | 0.7184 | 0.6814 | 0.7842 | 0.7086 | 0.0012 |
| position-aware first draft | 0.8581 | 0.9013 | 0.8525 | 0.5690 | 0.7182 | 0.6941 | 0.7829 | 0.7108 | 0.0012 |
| elite-probability blend | 0.8578 | 0.9007 | 0.8515 | 0.5712 | 0.7189 | 0.6933 | 0.7830 | 0.7085 | 0.0012 |
| current Pigskin baseline | 0.8569 | 0.9013 | 0.8536 | 0.5620 | 0.7741 | 0.7946 | 0.7832 | 0.7054 | 0.0012 |
| pairwise-strength blend | 0.8563 | 0.9027 | 0.8554 | 0.5677 | 0.7170 | 0.6938 | 0.7828 | 0.7088 | 0.0012 |
| balanced research blend | 0.8560 | 0.9028 | 0.8556 | 0.5667 | 0.7180 | 0.6950 | 0.7834 | 0.7087 | 0.0012 |
| BQML logistic elite | 0.8558 | 0.9030 | 0.8555 | 0.5619 | 0.7492 | 0.7715 | 0.7814 | 0.7060 | 0.0012 |
| BQML linear points | 0.8510 | 0.8973 | 0.8461 | 0.5451 | 0.8927 | 0.9441 | 0.7709 | 0.6990 | 0.0012 |
| scarcity adjusted draft value | 0.8403 | 0.8834 | 0.8171 | 0.5084 | 0.7548 | 0.7742 | 0.7401 | 0.6779 | 0.0012 |

Aggregate 2024-2025 ensemble results:

| Ensemble | Top-N | Captured points | VOR captured | Rank corr | High-confidence | Overall pairwise | NDCG@K | Tier accuracy | Bust rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| elite-probability blend | 0.6824 | 0.7995 | 0.6939 | 0.6352 | 0.7180 | 0.5593 | 0.7140 | 0.5566 | 0.0831 |
| balanced research blend | 0.6822 | 0.8015 | 0.6978 | 0.6364 | 0.7188 | 0.5611 | 0.7144 | 0.5575 | 0.0836 |
| position-aware first draft | 0.6814 | 0.7978 | 0.6923 | 0.6353 | 0.7176 | 0.5572 | 0.7126 | 0.5562 | 0.0865 |
| pairwise-strength blend | 0.6810 | 0.8002 | 0.6959 | 0.6385 | 0.7188 | 0.5589 | 0.7135 | 0.5574 | 0.0850 |
| conservative Pigskin-plus | 0.6807 | 0.7972 | 0.6895 | 0.6314 | 0.7143 | 0.5456 | 0.7121 | 0.5547 | 0.0877 |

Controlled summary-only write:

- version: `ranking_backtest_sql_native_ensemble_v0_2024_2025`
- write job ID: `a1d726ed-892b-455e-8709-250b528634c0`
- run rows written: 4
- summary rows written: 80
- detail rows written: 0
- bytes processed: 9,387,829
- slot millis: 397,153

Decision: no ensemble beats the current baseline strongly enough for owner-review challenger status. The best validation ensemble is only about 1.43 percentage points above current Pigskin on top-N and trails current Pigskin on high-confidence and overall pairwise. The 2025 holdout does not rescue the case because simple projection and current Pigskin remain at least as useful as the ensembles on the most practical metrics.

Next research direction: improve the feature warehouse before another blend pass. Better opportunity and route-level metrics are more likely to help than reweighting the same ingredients.

## Phase 32.12 Opportunity Metrics Warehouse

Phase 32.12 added an additive `player_week_opportunity_metrics` lane and enriched `ranking_backtest_feature_mart` for target seasons 2017 through 2025. No live rankings, champions, Pigskin tools, or ranking formula/backtest tables were changed.

New feature families:

- QB rushing leverage.
- RB high-value opportunity.
- WR and TE receiving role dominance.
- Red-zone and goal-line usage.
- Team environment.
- Spike, bust, and elite week rates.

Backfill and mart refresh:

| Object | Scope | Rows |
|---|---|---:|
| `player_week_opportunity_metrics` | 2014-2025 source weeks | 70,356 |
| `ranking_backtest_feature_mart` | 2017-2025 targets, four profiles, QB/RB/WR/TE | 156,244 |

Bounded 2025 PPR diagnostic smoke:

| Candidate | Position | Sample size | Top-N | NDCG@K | Missing |
|---|---|---:|---:|---:|---:|
| QB opportunity diagnostic | QB | 295 | 0.8333 | 0.8259 | 0.0000 |
| RB opportunity diagnostic | RB | 366 | 1.0000 | 0.9041 | 0.0000 |
| TE opportunity diagnostic | TE | 392 | 0.7778 | 0.7544 | 0.0000 |
| WR opportunity diagnostic | WR | 638 | 0.8356 | 0.7931 | 0.0000 |

Warning: RB VOR captured rate was null in the bounded diagnostic summary, likely because the denominator was zero for that slice. Do not use that single RB VOR result as a champion signal.

Blocked source concepts remain blocked: first-read share, true route share as a reliable feature, YPRR without true routes, and end-zone targets.

## Phase 32.13 ffopportunity Ideal Stats

Phase 32.13 added a bounded ffopportunity weekly xFP lane and refreshed `ranking_backtest_feature_mart` for target seasons 2017 through 2025. No live rankings, champions, Pigskin tools, or detail backtest rows were changed.

Backfill and mart refresh:

| Object | Scope | Rows |
|---|---|---:|
| `raw_ffopportunity_weekly` | 2014-2025 source weeks | 64,624 |
| `player_week_ideal_opportunity_metrics` | 2014-2025 source weeks | 64,624 |
| `ranking_backtest_feature_mart` | 2017-2025 targets, four profiles, QB/RB/WR/TE | 156,244 |

PPR diagnostic summary over 2024 validation and 2025 holdout:

| Candidate | Position | Sample size | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|---:|
| ideal xFP QB diagnostic | QB | 868 | 0.7001 | 0.6921 | 0.8389 | 0.0000 |
| ideal xFP RB diagnostic | RB | 1,642 | 0.7683 | 0.8113 | 0.8892 | 0.0013 |
| ideal xFP TE diagnostic | TE | 1,479 | 0.7725 | 0.6343 | 0.7695 | 0.0054 |
| ideal xFP WR diagnostic | WR | 2,620 | 0.7738 | 0.6447 | 0.7866 | 0.0019 |

Controlled summary-only write:

- version: `ranking_backtest_sql_native_ideal_stats_diagnostics_v0`
- write job ID: `ae1e7417-b036-44dd-a7e3-7cb5ba496b15`
- run rows written: 1
- summary rows written: 4
- detail rows written: 0
- champions written: 0

Warning: direct injury and depth-chart scores remain null with explicit missing flags. The current useful signal is xFP plus snap/role context, not a complete health/depth model.

## Phase 32.14 Stats02 Ideal Formulas

Phase 32.14 tested position-specific Stats02 formulas that use the Phase 32.13 ideal-stat columns through the SQL-native summary evaluator. No live rankings, champions, Pigskin tools, or detail backtest rows were changed.

Stats02 candidates tested:

| Candidate | Position scope | Main idea |
|---|---|---|
| `stats02_qb_ideal_rushing_xfp_v0` | QB | Rushing leverage, xFP, QB efficiency proxy, team environment, snap role |
| `stats02_rb_ideal_high_value_xfp_v0` | RB | High-value xFP plus profile-aware receiving and goal-line weight shifts |
| `stats02_wr_ideal_receiving_dominance_v0` | WR | Receiving-role xFP, xFP share, efficiency over expectation, team context |
| `stats02_te_ideal_receiving_role_v0` | TE | Receiving-role xFP and snap stability for tier separation |
| `stats02_position_specific_ideal_v0` | QB/RB/WR/TE | Position-specific formula dispatch |
| `stats02_position_specific_ideal_availability_multiplier_v0` | QB/RB/WR/TE | Same formulas with snap/role stability as a bounded multiplier |

SQL-native run:

| Version | Candidate rows | Run rows | Summary rows | Detail rows | Estimated bytes |
|---|---:|---:|---:|---:|---:|
| `ranking_backtest_sql_native_stats02_ideal_v0` | 12 | 4 | 48 | 0 | 71,838,149 |

Persisted profile summary:

| Profile | Summary rows | Sample total | Avg top-N | Avg captured points | Avg missing |
|---|---:|---:|---:|---:|---:|
| GNG Keeper | 12 | 117,183 | 0.5192 | 0.6588 | 0.0115 |
| Half PPR | 12 | 117,183 | 0.5402 | 0.7219 | 0.0113 |
| PPR | 12 | 117,183 | 0.5481 | 0.7332 | 0.0118 |
| Standard | 12 | 117,183 | 0.5300 | 0.7006 | 0.0101 |

Key validation and holdout read:

| Slice | Signal |
|---|---|
| 2024 QB validation | Stats02 QB beat current Pigskin on top-N in PPR, Half PPR, and Standard by about 0.46 points, and improved captured points and VOR. |
| 2024 RB validation | Current Pigskin remained better than Stats02 in PPR, Half PPR, and Standard. GNG Keeper was roughly tied on top-N, with Stats02 slightly better on VOR. |
| 2024 WR validation | Stats02 WR beat current Pigskin across all four profiles on top-N, captured points, VOR, NDCG, and bust rate, while rank correlation was slightly weaker. |
| 2024 TE validation | Stats02 TE improved top-N in all four profiles, especially PPR and Half PPR, but rank correlation was weaker than current Pigskin. |
| 2025 holdout | Stats02 WR and TE improved top-N, captured points, VOR, rank correlation, and bust rate in most profiles. QB top-N improved slightly without improving captured points. RB was mostly tied on top-N but weaker on rank correlation. |

Decision: Stats02 ideal stats show signal, especially WR and TE, but `stats02_position_specific_ideal_v0` does not beat the current Pigskin family broadly enough for champion activation. Aggregate context remains below the existing current baseline on top-N and captured points. The availability multiplier variant helped some TE validation and holdout rows, but it did not improve the aggregate enough to justify activation.

Owner-review status: not ready as a champion. Keep Stats02 as a challenger lane and use the gaps to guide the next source sprint.

Next highest-ROI gaps:

- Direct injury and depth scoring.
- PBP-level ffopportunity pass/rush splits.
- Better TE route or participation source.
- Direct receiving and rushing NGS features where source coverage is real.

## Phase 32.15 PBP ffopportunity Split Diagnostics

Phase 32.15 added the PBP split ffopportunity lane and refreshed the SQL-native feature mart. This was not a live ranking phase.

Objects added:

- `raw_ffopportunity_pbp_pass`
- `raw_ffopportunity_pbp_rush`
- `player_week_pbp_opportunity_metrics`
- PBP feature columns on `ranking_backtest_feature_mart`

Backfill and mart refresh:

| Item | Result |
|---|---:|
| Pass PBP rows loaded | 227,146 |
| Rush PBP rows loaded | 175,775 |
| Derived PBP weekly rows | 65,358 |
| Feature mart rows refreshed, 2017-2025 | 156,244 |
| Summary write rows | 4 run rows, 16 candidate summary rows |
| Detail rows written | 0 |

SQL-native dry-run estimates:

| Scope | Candidates | Summary rows | Estimated bytes |
|---|---:|---:|---:|
| 2024-2025 validation plus holdout | 4 | 16 | 14,060,961 |
| 2017-2025 aggregate | 4 | 16 | 81,842,565 |

2024-2025 PPR comparison:

| Position | Candidate | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|
| QB | current Pigskin baseline | 0.6929 | 0.6829 | 0.8256 | 0.0000 |
| QB | `pbp_xfp_qb_pass_rush_v0` | 0.7032 | 0.6759 | 0.8152 | 0.0000 |
| RB | current Pigskin baseline | 0.7859 | 0.8067 | 0.8820 | 0.0008 |
| RB | `pbp_xfp_rb_high_value_rush_recv_v0` | 0.7900 | 0.8171 | 0.8931 | 0.0052 |
| RB | scarcity adjusted baseline | 0.7744 | 0.8345 | 0.9108 | 0.0192 |
| TE | current Pigskin baseline | 0.7781 | 0.6181 | 0.7614 | 0.0037 |
| TE | `pbp_xfp_te_receiving_role_v0` | 0.7721 | 0.6088 | 0.7520 | 0.0055 |
| TE | Stats02 ideal TE | 0.7769 | 0.6343 | 0.7696 | 0.0057 |
| WR | current Pigskin baseline | 0.7834 | 0.6424 | 0.7811 | 0.0018 |
| WR | `pbp_xfp_wr_high_value_receiving_v0` | 0.7357 | 0.6458 | 0.7923 | 0.0027 |
| WR | Stats02 ideal WR | 0.7658 | 0.6597 | 0.8011 | 0.0022 |

2017-2025 PPR aggregate:

| Position | Candidate | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|
| QB | `pbp_xfp_qb_pass_rush_v0` | 0.7068 | 0.5744 | 0.7864 | 0.0018 |
| RB | `pbp_xfp_rb_high_value_rush_recv_v0` | 0.7533 | 0.6253 | 0.7630 | 0.0229 |
| TE | `pbp_xfp_te_receiving_role_v0` | 0.7316 | 0.4800 | 0.6730 | 0.0196 |
| WR | `pbp_xfp_wr_high_value_receiving_v0` | 0.7383 | 0.5144 | 0.7229 | 0.0124 |

Decision:

- PBP split xFP is useful source enrichment and should stay in the feature mart.
- RB showed the best validation and holdout signal from PBP split features.
- WR PBP split features improved captured points versus the current baseline on the 2024-2025 PPR slice, but current Pigskin still had a stronger pairwise read.
- TE needs more than PBP xFP. Stats02 weekly ideal fields remain the better TE signal.
- No champion formula was activated. Current Pigskin remains the live baseline.

Next highest-ROI action: a small RB/WR refinement that blends PBP split xFP with the existing Stats02 ideal fields, plus a separate injury/depth role scoring lane.

## Phase 32.17 RB/WR PBP Refined Formulas

Phase 32.17 tested a small second-pass RB/WR family that blends Phase 32.13 Stats02 ideal fields with Phase 32.15 PBP split xFP proxy fields. This was SQL-native summary-only evidence. No live rankings, champions, detail rows, Pigskin tools, or LLM-backed ranking generation changed.

Candidate family:

- `stats02_pbp_refined_v0`

Candidates:

| Candidate | Position | Main idea |
|---|---|---|
| `stats02_rb_pbp_high_value_blend_v0` | RB | Weekly xFP, PBP rush/receiving xFP, high-value opportunity, red-zone/goal-line xFP, snap role, team environment |
| `stats02_rb_pbp_receiving_weighted_v0` | RB | PPR-sensitive receiving xFP and high-value target xFP, with Standard shifted toward rush and goal-line xFP |
| `stats02_wr_pbp_receiving_dominance_blend_v0` | WR | Stats02 receiving dominance plus PBP receiving xFP, xFP share, high-value targets, snap role, team environment |
| `stats02_wr_pbp_scoring_profile_blend_v0` | WR | Standard favors red-zone, goal-line, team environment, and efficiency. PPR/Half/GNG favor xFP share and high-value target xFP |

SQL-native dry-run:

| Version | Candidate rows | Run rows | Summary rows | Detail rows | Estimated bytes |
|---|---:|---:|---:|---:|---:|
| `ranking_backtest_sql_native_stats02_pbp_refined_v0` | 4 | 4 | 16 | 0 | 81,842,565 |

Controlled summary write:

| Item | Result |
|---|---:|
| BigQuery job ID | `9e3c08e6-c0b9-42df-9977-8ef83b2809ec` |
| `ranking_backtest_runs` rows | 4 |
| `ranking_backtest_candidate_summaries` rows | 16 |
| `ranking_backtest_results` rows | 0 |
| `ranking_formula_champions` rows | 0 |
| live ranking candidate rows | 0 |

2024 validation, best refined candidate versus current:

| Position | Profile | Current overall pairwise | Refined overall pairwise | Current captured | Refined captured | Read |
|---|---|---:|---:|---:|---:|---|
| RB | PPR | 0.7891 | 0.8040 | 0.7641 | 0.7654 | RB pairwise improved, captured roughly flat |
| RB | Half PPR | 0.7862 | 0.7954 | 0.7572 | 0.7571 | RB pairwise improved, captured flat |
| RB | Standard | 0.7820 | 0.7776 | 0.7460 | 0.7503 | Standard captured improved, pairwise slipped |
| RB | GNG Keeper | 0.7714 | 0.7782 | 0.6864 | 0.7008 | RB improved on both pairwise and captured |
| WR | PPR | 0.7791 | 0.7558 | 0.6825 | 0.6880 | WR captured improved, pairwise weaker |
| WR | Half PPR | 0.7746 | 0.7462 | 0.6594 | 0.6672 | WR captured improved, pairwise weaker |
| WR | Standard | 0.7614 | 0.7171 | 0.6206 | 0.6295 | WR captured improved, pairwise much weaker |
| WR | GNG Keeper | 0.7597 | 0.7287 | 0.5870 | 0.5997 | WR captured improved, pairwise weaker |

2025 holdout, best refined candidate versus current:

| Position | Profile | Current overall pairwise | Refined overall pairwise | Current captured | Refined captured | Read |
|---|---|---:|---:|---:|---:|---|
| RB | PPR | 0.8225 | 0.8426 | 1.0000 | 1.0000 | RB pairwise improved |
| RB | Half PPR | 0.8252 | 0.8446 | 1.0000 | 1.0000 | RB pairwise improved |
| RB | Standard | 0.8264 | 0.8374 | 1.0000 | 1.0000 | RB pairwise improved |
| RB | GNG Keeper | 0.8181 | 0.8302 | 1.0000 | 1.0000 | RB pairwise improved |
| WR | PPR | 0.8336 | 0.7889 | 0.8796 | 0.8922 | WR captured improved, pairwise weaker |
| WR | Half PPR | 0.8334 | 0.7861 | 0.8748 | 0.8932 | WR captured improved, pairwise weaker |
| WR | Standard | 0.8284 | 0.7764 | 0.8690 | 0.8876 | WR captured improved, pairwise weaker |
| WR | GNG Keeper | 0.8362 | 0.7818 | 0.8712 | 0.8852 | WR captured improved, pairwise weaker |

2017-2025 aggregate context:

| Position | Profile | Current overall pairwise | Best refined overall pairwise | Current captured | Best refined captured | Read |
|---|---|---:|---:|---:|---:|---|
| RB | PPR | 0.7544 | 0.7369 | 0.7611 | 0.7496 | refined under current |
| RB | Half PPR | 0.7558 | 0.7341 | 0.7573 | 0.7438 | refined under current |
| RB | Standard | 0.7558 | 0.7293 | 0.7483 | 0.7361 | refined under current |
| RB | GNG Keeper | 0.7465 | 0.7224 | 0.7095 | 0.6975 | refined under current |
| WR | PPR | 0.7736 | 0.7419 | 0.7367 | 0.7137 | refined under current |
| WR | Half PPR | 0.7684 | 0.7352 | 0.7165 | 0.6951 | refined under current |
| WR | Standard | 0.7571 | 0.7189 | 0.6835 | 0.6620 | refined under current |
| WR | GNG Keeper | 0.7559 | 0.7226 | 0.6546 | 0.6336 | refined under current |

Decision:

- RB PBP xFP shows a real short-window pairwise signal. It improves 2024 validation in PPR, Half PPR, and GNG Keeper, and it improves all four 2025 holdout profiles.
- WR PBP xFP helps captured points on 2024 and 2025 slices, but it does not beat current Pigskin on pairwise and weakens aggregate performance.
- The refined family does not beat current Pigskin on the 2017-2025 aggregate. It is not ready for champion activation.
- Current Pigskin remains the live baseline. No champion is active.

Owner-review status: RB can be reviewed as a challenger concept, not as a replacement. WR needs either injury/depth role context, direct NGS receiving/rushing ingest, or a narrower blend that preserves current Pigskin pairwise strength.

## Phase 32.18 Role Context, First-Down Proxy, RB Weighted Opportunity, and VOR Sensitivity

Phase 32.18 added first-down PBP proxy fields, added exact PPR RB weighted-opportunity diagnostic fields, and tested a capped six-candidate diagnostic family:

- `injury_depth_role_diagnostic_v0`
- `first_down_pbp_proxy_diagnostic_v0`
- `deep_vorp_qb15_rb36_wr55_te12_diagnostic_v0`
- `gemini31_rb_weighted_opportunity_ppr_v0`
- `rb_role_pbp_context_blend_v0`
- `wr_chain_mover_context_blend_v0`

Injury/depth source audit:

| Source | Rows | Decision |
|---|---:|---|
| `raw_nflverse_injuries` | 0 | Insufficient for role scoring. Do not fabricate injury burden. |
| `raw_nflverse_depth_charts` | 0 | Insufficient for depth role scoring. Do not fabricate starter or depth rank. |

First-down proxy implementation:

| Layer | Result |
|---|---|
| Migration | `0034__first_down_pbp_proxy_features.sql` applied |
| Addendum migration | `0035__ranking_feature_mart_rb_weighted_opportunity.sql` applied |
| Derived PBP rows | 65,358 |
| Receiving first-down rows | 53,018 |
| Rushing first-down rows | 27,023 |
| Passing first-down rows | 7,961 |
| Feature mart refresh | PPR QB/RB/WR/TE rebuilt for target seasons 2017-2025 after migration 0035 |
| Summary write | one PPR run, six candidate summaries, zero detail rows |

2024 validation, PPR:

| Candidate | Position | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|
| `deep_vorp_qb15_rb36_wr55_te12_diagnostic_v0` | QB | 0.6924 | 0.5278 | 0.7649 | 0.0000 |
| `gemini31_rb_weighted_opportunity_ppr_v0` | RB | 0.7829 | 0.6227 | 0.7761 | 0.3707 |
| `injury_depth_role_diagnostic_v0` | RB | 0.7680 | 0.6389 | 0.7857 | 0.5000 |
| `rb_role_pbp_context_blend_v0` | RB | 0.7705 | 0.6343 | 0.7819 | 0.1263 |
| `first_down_pbp_proxy_diagnostic_v0` | WR | 0.7400 | 0.4444 | 0.6755 | 0.0020 |
| `wr_chain_mover_context_blend_v0` | WR | 0.7354 | 0.4468 | 0.6802 | 0.0626 |

2025 holdout, PPR:

| Candidate | Position | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|
| `deep_vorp_qb15_rb36_wr55_te12_diagnostic_v0` | QB | 0.6951 | 0.8380 | 0.8862 | 0.0000 |
| `gemini31_rb_weighted_opportunity_ppr_v0` | RB | 0.8183 | 1.0000 | 1.0000 | 0.3707 |
| `injury_depth_role_diagnostic_v0` | RB | 0.7943 | 1.0000 | 1.0000 | 0.5000 |
| `rb_role_pbp_context_blend_v0` | RB | 0.8146 | 1.0000 | 1.0000 | 0.1226 |
| `first_down_pbp_proxy_diagnostic_v0` | WR | 0.7489 | 0.8333 | 0.8891 | 0.0018 |
| `wr_chain_mover_context_blend_v0` | WR | 0.7441 | 0.8403 | 0.8984 | 0.0621 |

2017-2025 aggregate, PPR:

| Candidate | Position | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|
| `deep_vorp_qb15_rb36_wr55_te12_diagnostic_v0` | QB | 0.6923 | 0.5781 | 0.7909 | 0.0022 |
| `gemini31_rb_weighted_opportunity_ppr_v0` | RB | 0.7477 | 0.6226 | 0.7625 | 0.3708 |
| `injury_depth_role_diagnostic_v0` | RB | 0.7333 | 0.6321 | 0.7704 | 0.5000 |
| `rb_role_pbp_context_blend_v0` | RB | 0.7342 | 0.6210 | 0.7598 | 0.1366 |
| `first_down_pbp_proxy_diagnostic_v0` | WR | 0.7456 | 0.5181 | 0.7259 | 0.0098 |
| `wr_chain_mover_context_blend_v0` | WR | 0.7395 | 0.5133 | 0.7212 | 0.0716 |

Baseline comparison, 2024-2025 PPR:

| Position | Current Pigskin captured | Best Phase 32.18 captured | Current Pigskin pairwise | Best Phase 32.18 pairwise | Read |
|---|---:|---:|---:|---:|---|
| QB | 0.8256 | 0.7909 | 0.6929 | 0.6923 | VOR diagnostic does not beat current |
| RB | 0.8820 | 1.0000 on 2025 only, 0.7625 aggregate | 0.7859 | 0.7477 aggregate | Weighted opportunity helps the 2025 slice, but not aggregate |
| WR | 0.7811 | 0.8984 on 2025 only, 0.7259 aggregate | 0.7834 | 0.7456 aggregate | First-down proxy helps short-window captured points, not pairwise or aggregate |

VOR baseline sensitivity, 2024-2025 PPR:

| Policy | VOR captured | Top-24 hit | Top-50 hit | Top-100 hit | Pick-band regret |
|---|---:|---:|---:|---:|---:|
| `current_sql_vorp_qb12_rb24_wr24_te12` | 0.6911 | 0.2095 | 0.3133 | 0.4371 | 4448.12 |
| `middle_vorp_qb12_rb30_wr42_te12` | 0.6690 | 0.2095 | 0.3133 | 0.4371 | 7116.72 |
| `deep_vorp_qb15_rb36_wr55_te12` | 0.6370 | 0.2095 | 0.3133 | 0.4371 | 10343.76 |

Decision:

- Injury role scoring is no longer blocked after Phase 32.19. Historical injury rows are loaded, and `player_week_role_context_metrics` contains grouped 2014-2025 player-week risk context. It still needs a controlled ideal-stat and feature-mart refresh before another tournament.
- Depth role scoring remains blocked. The available `nflreadpy.load_depth_charts` output is current snapshot-style data without historical `season` and `week`, so no depth score should be fabricated.
- First-down PBP proxies are real enough to keep in the feature mart and use as WR/RB components.
- The first-down proxy family does not beat current Pigskin on aggregate or pairwise.
- The explicit PPR RB weighted-opportunity diagnostic improves 2025 holdout but misses the aggregate threshold.
- The deep VOR baseline `QB15/RB36/WR55/TE12` changed VOR captured and regret materially, but in the wrong direction for this slice.
- No owner-review challenger is strong enough for champion consideration.
- No champion formula was activated. Live rankings remain unchanged.

### Phase 32.19: Source remediation checkpoint

Phase 32.19 added source and context lanes only. It did not run a new tournament, activate a champion, regenerate live rankings, or expose a Pigskin chat tool.

| Object | Result |
|---|---:|
| `raw_nflverse_injuries` | 65,866 rows, seasons 2014-2025 |
| `raw_nflverse_depth_charts` | 0 rows, source blocked for historical season/week use |
| `player_week_role_context_metrics` | 65,864 grouped player-week rows |
| `raw_sleeper_players_snapshot` | 12,200 current Sleeper rows from the 2026 snapshot |
| `sleeper_player_context_current` | 12,200 latest-context rows, one per Sleeper player |

The ranking read stays unchanged until a later phase refreshes `player_week_ideal_stats`, rebuilds `ranking_backtest_feature_mart`, and reruns SQL-native summaries with the injury risk field populated.

### Phase 32.20: Injury context feature-mart refresh

Phase 32.20 added deterministic injury context to the SQL-native ranking research path. It did not regenerate live rankings, activate champions, write detail rows, expose Pigskin chat, or use Sleeper current-team data as historical truth.

| Object | Result |
|---|---:|
| Migration `0038__injury_context_feature_mart_columns.sql` | Applied |
| `player_week_role_context_metrics` | 65,864 refreshed rows, 2014-2025 |
| Missing role-context identity rows | 0 after exact-GSIS fallback |
| `gsis_exact_fallback` identity rows | 32,405, mostly defense and offensive line |
| Feature mart refresh | target seasons 2017-2025, four profiles, QB/RB/WR/TE |
| SQL-native injury diagnostic | 40 PPR candidate summaries, zero detail rows |
| Champion activation | 0 |

2017-2025 aggregate, PPR:

| Position | Current Pigskin pairwise | Best injury-context pairwise | Current Pigskin top-N | Best injury-context top-N | Read |
|---|---:|---:|---:|---:|---|
| QB | 0.6923 | 0.6870 | 0.5781 | 0.5728 | Availability blend is close, but not better. |
| RB | 0.7495 | 0.7436 | 0.6226 | 0.6200 | Useful modifier. Current Pigskin still leads. |
| WR | 0.7754 | 0.7590 | 0.5277 | 0.5058 | Injury context does not close the WR gap. |
| TE | 0.7569 | 0.7364 | 0.4879 | 0.4731 | Useful context, not a champion. |

Decision:

- Keep `availability_score_3yr`, `injury_status_score_3yr`, `injury_burden_score_3yr`, and `missed_time_risk_score_3yr` in the feature mart.
- Treat injury context as a secondary modifier, not a standalone ranking algorithm.
- Do not activate a champion from this run.
- Keep depth role context blocked until a real historical depth source exists.
- Keep Sleeper current context out of historical feature marts. It remains a current-roster display aid only.

### Phase 32.21: Low-weight injury availability modifier sprint

Phase 32.21 tested injury availability only as a low-weight modifier on top of existing stronger formula families. It did not regenerate live rankings, activate champions, write detail rows, expose Pigskin chat, call Gemini, call Sleeper, or tune on 2025 holdout.

Candidate family:

- `current_pigskin_availability_blend_03_v0`: current Pigskin proxy at 97 percent, availability at 3 percent.
- `current_pigskin_availability_blend_05_v0`: current Pigskin proxy at 95 percent, availability at 5 percent.
- `current_pigskin_injury_penalty_cap_v0`: current Pigskin proxy at 95 percent, inverted burden and missed-time risk at 2.5 percent each.
- `rb_current_pigskin_pbp_availability_blend_v0`: RB current Pigskin plus high-value rush xFP and 3 percent availability.
- `wr_current_pigskin_stats02_availability_blend_v0`: WR current Pigskin plus receiving role dominance xFP and 3 percent availability.
- `te_current_pigskin_stats02_availability_blend_v0`: TE current Pigskin plus receiving role dominance xFP and 3 percent availability.

Summary-only write:

| Object | Result |
|---|---:|
| `ranking_backtest_runs` | 4 rows |
| `ranking_backtest_candidate_summaries` | 284 rows |
| New injury-availability summary rows | 60 rows |
| `ranking_backtest_results` | 0 rows |
| `ranking_formula_champions` | 0 rows |

2017-2025 aggregate read:

| Position | Best low-weight read | Result |
|---|---|---|
| QB | `current_pigskin_availability_blend_03_v0` or capped penalty by profile | Mostly tie or tiny decline versus current Pigskin. GNG Keeper had a tiny positive penalty-cap read. |
| RB | `rb_current_pigskin_pbp_availability_blend_v0` | Consistent pairwise improvement across profiles, but captured points usually slipped slightly. |
| WR | `wr_current_pigskin_stats02_availability_blend_v0` | Fragile. Pairwise weakened versus current Pigskin despite occasional captured-points help. |
| TE | `te_current_pigskin_stats02_availability_blend_v0` | Clearest aggregate signal. PPR pairwise improved by about 0.0039 and captured points by about 0.0028 versus current Pigskin. |

2025 holdout read:

| Position | Best low-weight read | Result |
|---|---|---|
| QB | `current_pigskin_injury_penalty_cap_v0` | Pairwise and captured-points improved across PPR, Half PPR, and Standard. |
| RB | `rb_current_pigskin_pbp_availability_blend_v0` | Pairwise improved by about 0.010 to 0.013 across profiles. Captured points stayed maxed at 1.0000. |
| WR | availability blend or WR special by profile | Mixed. Captured points sometimes improved, but pairwise stayed weaker. |
| TE | `te_current_pigskin_stats02_availability_blend_v0` in most profiles | Pairwise improved. Captured points were mixed, especially in Standard. |

2024 validation read:

- QB penalty-cap improved pairwise, but captured points often fell.
- RB special improved pairwise, but captured points fell in validation.
- TE special improved pairwise in most profiles, but 2024 captured points dropped materially.
- WR remained weak on pairwise.

Decision:

- Low-weight availability shows signal as a modifier, especially for RB pairwise and TE aggregate.
- Do not promote any injury-availability candidate to champion.
- Do not use the 5 percent generic blend as the default. It over-penalizes in multiple slices.
- Keep WR injury modifiers out of owner-review challenger status until they preserve current Pigskin pairwise strength.
- BQML comparison was unavailable in the persisted summary table for this run, so it remains a future comparison lane.

### Phase 32.22: RB/TE availability owner-review cutlines

Phase 32.22 turned the Phase 32.21 RB and TE availability-modifier signal into owner-readable cutline evidence. It used read-only SQL CTEs against `ranking_backtest_feature_mart` and the existing Phase 32.21 summary rows. No detail rows, champion rows, live rankings, Pigskin chat, Gemini calls, Sleeper calls, or deploys occurred.

Evidence verified:

| Check | Result |
|---|---:|
| Phase 32.21 run rows | 4 |
| Phase 32.21 summary rows | 284 |
| New injury-availability summary rows | 60 |
| Detail rows for this run prefix | 0 |
| Champion rows | 0 |

Owner-review status:

| Candidate | Position | Status | Reason |
|---|---|---|---|
| `rb_current_pigskin_pbp_availability_blend_v0` | RB | use as risk flag only | Strong overall draft-board deltas, but position cutlines weaken in 2024 validation and 2017-2025 aggregate. |
| `te_current_pigskin_stats02_availability_blend_v0` | TE | use as risk flag only | Useful TE6/TE12 signal, but TE3 and 2024 TE12 remain unstable with hit-lost examples. |
| `current_pigskin_availability_blend_05_v0` | all | reject as default | Phase 32.21 showed over-penalization risk. |
| WR availability modifiers | WR | reject for owner-review | Pairwise remained fragile. |

RB position cutline deltas versus current Pigskin, profile average:

| Slice | RB6 pairwise | RB12 pairwise | RB24 pairwise | Captured read |
|---|---:|---:|---:|---|
| 2017-2025 aggregate | -0.0022 | -0.0029 | -0.0025 | RB12 captured -0.0012, RB24 captured -0.0019. |
| 2024 validation | -0.0082 | -0.0075 | -0.0067 | RB6 captured -0.0168, RB24 captured -0.0122. |
| 2025 holdout | -0.0007 | +0.0003 | -0.0007 | RB18 captured +0.0025. RB24 flat. |

RB overall draft-board deltas versus current Pigskin, profile average:

| Slice | Top 24 overall pairwise | Top 50 overall pairwise | Top 100 overall pairwise | Bust read |
|---|---:|---:|---:|---|
| 2017-2025 aggregate | +0.0115 | +0.0080 | +0.0036 | Bust rate improved at top 24 and top 50. |
| 2024 validation | +0.0078 | +0.0059 | +0.0031 | Top 24 bust rate improved by 0.0347. |
| 2025 holdout | +0.0090 | +0.0047 | +0.0041 | Top 24 bust rate improved by 0.0098. |

TE position cutline deltas versus current Pigskin, profile average:

| Slice | TE3 pairwise | TE6 pairwise | TE12 pairwise | Captured read |
|---|---:|---:|---:|---|
| 2017-2025 aggregate | +0.0015 | +0.0014 | +0.0020 | TE12 captured +0.0041, TE18 captured +0.0029. |
| 2024 validation | +0.0032 | +0.0007 | -0.0137 | TE3 captured +0.0142, TE12 captured -0.0220. |
| 2025 holdout | +0.0145 | +0.0082 | +0.0025 | TE6 captured +0.0108, TE12 captured +0.0021. |

TE overall draft-board deltas versus current Pigskin, profile average:

| Slice | Top 24 overall pairwise | Top 50 overall pairwise | Top 100 overall pairwise | Read |
|---|---:|---:|---:|---|
| 2017-2025 aggregate | +0.0007 | +0.0009 | +0.0006 | Tiny positive, not actionable by itself. |
| 2024 validation | +0.0018 | +0.0015 | +0.0009 | Small overall positive despite TE position instability. |
| 2025 holdout | -0.0002 | -0.0002 | -0.0006 | Slightly weaker overall. |

Player movement read:

- RB moved Kenneth Walker into the 2024 RB12 cutline, which helped in the example row, but also moved Brian Robinson and James Cook down in ways that hurt validation cutlines.
- RB 2025 moved Kareem Hunt into RB12 in several profiles, but also moved Bam Knight out despite top-four actual outcomes in the sampled weeks.
- TE moved Dallas Goedert and David Njoku into 2025 TE6 in PPR examples, but pushed Taysom Hill out in mixed cases and kept false negatives such as Anthony Firkser.
- TE 2024 avoided some Jake Ferguson bust exposure, but also lost Ferguson hit rows and missed Noah Gray spike weeks.

Decision: carry RB and TE low-weight availability forward as a risk flag only. It is not owner-review challenger status for champion selection yet. A future owner-review phase can look at risk badges or formula diagnostics, not production ranking activation.

### Phase 32.23: Formula comparison owner-review report

Phase 32.23 built a lightweight owner-review comparison view from existing SQL-native summary evidence and bounded read-only BigQuery queries. It did not regenerate live rankings, activate champions, call Gemini, call Pigskin chat, use live Sleeper, write detail rows, or run the old Python full tournament.

Status labels:

| Candidate lane | Status | Owner read |
|---|---|---|
| Current Pigskin candidate score v1 | live baseline | Remains the live formula baseline. Latest stored aggregate average: pairwise 0.7385, captured points 0.7132, VOR captured 0.6007, missing 0.0050. |
| Simple projection | strong challenger | Clean low-missing challenger. Latest stored aggregate pairwise 0.7238, below current Pigskin. |
| BQML logistic elite | strong challenger | Best Phase 32.10 BQML top-N/VOR challenger. Not a champion. Needs retrain with newer ideal, PBP, injury, and role fields. |
| BQML linear points | strong challenger | Strong Phase 32.10 high-confidence and overall pairwise BQML lane. Not a champion. |
| Stats02 WR/TE ideal | owner-review concept | Useful position-specific signal. Current Pigskin still protects more aggregate utility. |
| PBP RB/WR refinements | owner-review concept | RB has useful short-window signal. WR helps captured points in places but weakens pairwise. |
| RB availability modifier | risk flag only | Phase 32.22 cutlines rejected formula-default status. |
| TE availability modifier | risk flag only | Better than RB at selected TE cutlines, still unstable. |
| WR availability modifier | deferred | Pairwise fragility keeps it out of challenger status. |
| Generic 5 percent availability blend | rejected | Rejected as default due to over-penalization risk. |
| Historical depth context | blocked | No approved historical depth source exists. |

Position read from latest stored summaries:

| Position | Baseline read | Strongest useful challenger read |
|---|---|---|
| QB | Current Pigskin pairwise 0.6871. | Stats02 position ideal pairwise 0.7172, but needs owner review and model-lane validation. |
| RB | Current Pigskin pairwise 0.7485, captured 0.7440. | Simple projection improves captured/VOR but trails pairwise. Availability and PBP remain risk/component lanes. |
| WR | Current Pigskin pairwise 0.7680. | Stats02/PBP/availability are not activation-ready because they do not protect baseline pairwise. |
| TE | Current Pigskin pairwise 0.7505. | TE availability improves small averages but remains risk flag only after cutline instability. |

Owner-review conclusion:

- Live baseline: current Pigskin candidate score v1.
- Strong challenger lanes: BQML logistic elite, BQML linear points, and simple projection.
- Owner-review concepts: Stats02 WR/TE, QB Stats02, and selected RB/PBP component lanes.
- Risk flags only: RB availability, TE availability, injury burden, and missed-time risk.
- Rejected or not default: generic 5 percent availability blend, v2 trend-aware champion path, broad ensembles, and injury-only candidates.
- Blocked: historical depth context.
- No champion formula is active.
- Recommended next technical lane: BQML retrain with ideal, PBP, injury, and role context, or direct NGS ingest if the owner wants source expansion first.

Metric sanity note:

- Phase 32.23 verified the comparison extraction paths before future BQML comparison work.
- Top-level `pairwise_win_rate` comes from `ranking_backtest_candidate_summaries.pairwise_win_rate`.
- High-confidence pairwise comes from `metric_json.high_confidence_pairwise_win_rate`.
- For the sampled SQL-native summary rows, those two values are identical by construction because the SQL-native summary currently stores the high-confidence pairwise CTE result in both places.
- Treat them as a contract caveat, not as two independent evidence columns, until the summary contract adds a separate all-pairwise metric.

### Phase 32.24: BQML enriched retrain

Phase 32.24 retrained bounded BQML challengers with enriched ideal xFP, PBP split xFP, first-down proxies, injury availability, and role-context predictors from `ranking_backtest_feature_mart`. It did not regenerate live rankings, activate champions, write detail rows, call Gemini, call Pigskin chat, call Sleeper, or ingest new sources.

Trained models:

| Model | Type | Target | Read |
|---|---|---|---|
| `ranking_bqml_enriched_logistic_elite_v1` | logistic regression | position-specific elite finish | Best v1 top-N and holdout utility challenger. |
| `ranking_bqml_enriched_linear_points_v1` | linear regression | target fantasy points | Best v1 overall pairwise challenger. |
| `ranking_bqml_enriched_linear_vor_v1` | linear regression | value over replacement | Weaker and noisy. |
| `ranking_bqml_enriched_boosted_tree_vor_v1` | boosted tree regression | value over replacement | Competitive top-N, but costlier and lacks pairwise reads due sparse high-confidence comparisons. |

2024-2025 comparison:

| Candidate | Top-N | Captured | VOR captured | Rank corr | High-conf | Overall pairwise | NDCG | Tier acc | Bust |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Enriched logistic elite v1 | 0.6866 | 0.8030 | 0.6972 | 0.5451 | 0.7419 | 0.6392 | 0.7125 | 0.5558 | 0.0822 |
| Enriched linear points v1 | 0.6824 | 0.8015 | 0.6963 | 0.5521 | 0.9098 | 0.8361 | 0.7125 | 0.5552 | 0.0854 |
| Enriched boosted tree VOR v1 | 0.6855 | 0.8007 | 0.6960 | 0.5424 | n/a | n/a | 0.7085 | 0.5548 | 0.0825 |
| Enriched linear VOR v1 | 0.6743 | 0.7950 | 0.6865 | 0.5325 | 1.0000 | n/a | 0.7069 | 0.5459 | 0.0886 |
| Phase 32.10 logistic elite | 0.6861 | 0.8051 | 0.7031 | 0.5476 | 0.7468 | 0.6405 | 0.7157 | 0.5529 | 0.0826 |
| Phase 32.10 linear points | 0.6815 | 0.8004 | 0.6963 | 0.5425 | 0.9098 | 0.8178 | 0.7090 | 0.5544 | 0.0841 |
| Current Pigskin baseline | 0.6755 | 0.7929 | 0.6800 | 0.6219 | 0.7540 | 0.7621 | 0.7086 | 0.5528 | 0.0891 |

Decision:

- Enriched BQML improves the challenger lane but does not clear champion-selection criteria.
- Logistic elite v1 is the best top-N and holdout utility challenger.
- Linear points v1 is the strongest overall pairwise challenger and improved over Phase 32.10 linear points.
- Top-N lift versus current Pigskin remains below the 1.5 percentage point activation threshold.
- No champion formula is active.
- Recommended next lane: owner review of enriched BQML challengers or direct NGS receiving/rushing ingest.

### Phase 32.25: BQML owner-review cutlines

Phase 32.25 converted Phase 32.24 enriched BQML results into owner-review evidence using read-only SQL and existing trained models. No live rankings, champion formulas, BQML training, detail rows, Pigskin chat, Gemini calls, Sleeper calls, source ingest, or deploy changed.

Candidate labels:

| Candidate | Label | Owner read |
|---|---|---|
| Current Pigskin candidate score v1 | live baseline | Keep live. Still protects rank correlation and pairwise behavior. |
| Enriched BQML logistic elite v1 | owner-review challenger | Best top-N utility challenger. Useful RB/TE depth reads, but weak overall pairwise. |
| Enriched BQML linear points v1 | owner-review challenger | Best BQML board-ordering challenger. Stronger overall pairwise and early-board cutlines. |
| Enriched boosted tree VOR v1 | context only | Costly, with no clear owner-review edge. |
| Enriched linear VOR v1 | context only | Weaker than the two primary challengers. |
| Injury and availability | risk flag only | Useful warning context, not a default formula. |
| Historical depth | blocked | Still excluded. |

Cutline read:

- Overall top 24: linear points improved top-N by 0.1412 and captured points by 0.1043 versus current Pigskin. Logistic improved top-N by 0.0541 and VOR captured by 0.0699.
- RB24: logistic improved VOR captured by 0.0626, linear points by 0.0546. Both are reviewable.
- WR12 and WR24: both enriched BQML models hurt the early WR tiers. Do not let either model own WR cutlines.
- TE18: logistic had the best depth signal, with +0.0100 top-N and +0.0277 VOR captured. TE6 and TE12 remain mixed.

Movement read:

- Useful moves: Kyren Williams was a good RB riser for both models. Ezekiel Elliott and Tyler Higbee were examples of busts the BQML cuts demoted.
- Risky moves: C.J. Stroud and Cooper Kupp were false positives. Tee Higgins and Marvin Mims were large WR false negatives.

Owner-review recommendation:

- Generate BQML candidate rankings for owner review only if the owner wants player-level board inspection.
- Do not activate a champion.
- Keep current Pigskin as the live baseline.
- Direct NGS receiving/rushing ingest remains the cleanest source-expansion lane if the owner wants better signal before more model work.

### Phase 32.26: BQML owner-review candidate boards

Phase 32.26 generated Markdown-only owner-review candidate boards from the two enriched BQML challenger lanes. It used existing trained models and read-only `ML.PREDICT` against the 2025 Week 18 holdout slice. No persistent review table was created. No live rankings, champions, detail rows, model training, Pigskin chat, Gemini calls, Sleeper calls, source ingest, or deploy changed.

Review board IDs:

| Board ID | Label | Status |
|---|---|---|
| `bqml_enriched_logistic_elite_v1_owner_review` | BQML Logistic Elite v1 | review-only board |
| `bqml_enriched_linear_points_v1_owner_review` | BQML Linear Points v1 | review-only board |

Board read:

- All four scoring profiles were generated: `ppr`, `half_ppr`, `standard`, and `gng_keeper`.
- PPR top-50, position-board, movement, and cutline tables were written into the Phase 32.26 report.
- Logistic elite remains the top-N and bust-control review board, but still carries overall pairwise risk.
- Linear points remains the stronger cross-position board-ordering review board, but its explanation path is noisier.
- WR movement is still the biggest warning. Neither board should own WR cutlines without owner inspection.

Decision: BQML candidate rankings are ready for owner review with warnings. Current Pigskin remains the live baseline. No champion is active.

## Current Baseline Score

Family-level current Pigskin candidate score:

- pairwise win rate: 0.6697
- high-confidence pairwise win rate: 0.7575
- top-N hit rate: 0.5400
- VOR captured rate: 0.5981
- actual points captured rate: 0.7123
- missing-input rate: 0.0032

## Best Challenger Score

Best aggregate family:

- family: simple projection points baseline
- pairwise win rate: 0.6728
- high-confidence pairwise win rate: 0.7364
- top-N hit rate: 0.5387
- VOR captured rate: 0.5956
- actual points captured rate: 0.7115
- missing-input rate: 0.0006

Decision: this is approximately tied with the current baseline, not a clear replacement.

## Known Weaknesses

- The deterministic Pigskin baseline cannot historically replay live Sleeper depth-chart penalties.
- Overall draft-order metrics now have a read-only prototype, but they are not part of the persisted candidate summary contract yet.
- Seeded v0 and some TE/WR winners have high missing-input rates because `pigskin_context_score` is unavailable in the current historical feature path.
- Trend-aware v2 underperformed after the full target backfill.

## Algorithms Rejected

- `v2_trend_aware` as a direct champion path. It needs feature work before another tournament.
- Any historical LLM replay. It violates this phase cost and safety policy.

## Algorithms Pending

- Persisted overall draft-order formula metrics with pick-band regret.
- Better TE-specific features.
- Low-missing WR/TE challenger that does not depend on unavailable `pigskin_context_score`.
- Optional ML baselines only if dependencies already exist in a future environment.

## Next Experiments

1. Build a formula comparison dashboard for owner review.
2. Add a BigQuery-native feature mart and persist cross-position overall draft-order scoring.
3. Improve TE/WR features before another champion-selection attempt.
4. Generate formula-driven candidate rankings only after owner approval.

### Phase 32.27: Direct nflverse NGS metrics

Phase 32.27 ingested public nflverse Next Gen Stats receiving, rushing, and passing data for 2016-2025, derived weekly NGS metrics, refreshed leakage-safe feature-mart predictors for target seasons 2017-2025, and ran a SQL-native summary-only diagnostic. It did not regenerate live rankings, activate champions, train BQML models, call Gemini, call Pigskin chat, call Sleeper, deploy, or write detail rows.

Source coverage:

| Source family | Raw rows | Derived use |
|---|---:|---|
| Receiving NGS | 14,716 | WR/TE receiving efficiency, separation, YAC over expected |
| Rushing NGS | 6,052 | RB rushing efficiency, RYOE, box resilience |
| Passing NGS | 5,925 | QB passing efficiency context |

Derived table:

- `player_week_ngs_metrics` contains 24,557 source-versioned player-week rows for `nflverse_ngs_direct_latest`.
- Public nflverse receiving does not expose expected catch percentage or catch-over-expected. Those fields remain null and explicitly flagged.
- Feature mart NGS predictors use only seasons before the target season.

2017-2025 PPR diagnostic:

| Candidate | Pairwise | Top-N | Captured | VOR captured | NDCG | Missing |
|---|---:|---:|---:|---:|---:|---:|
| `ngs_qb_passing_efficiency_v0` | 0.7299 | 0.5812 | 0.7905 | 0.6214 | 0.7517 | 0.0091 |
| `ngs_rb_rushing_efficiency_v0` | 0.7512 | 0.6247 | 0.7627 | 0.6483 | 0.6989 | 0.1229 |
| `ngs_te_receiving_efficiency_v0` | 0.6916 | 0.4837 | 0.6714 | 0.5557 | 0.6369 | 0.0916 |
| `ngs_wr_receiving_efficiency_v0` | 0.7452 | 0.5159 | 0.7266 | 0.6106 | 0.6719 | 0.0627 |

Decision:

- Direct NGS is real and useful.
- RB rushing NGS and WR/TE receiving NGS are owner-review component lanes, not standalone champions.
- Current Pigskin remains the live baseline.
- No champion formula is active.
- Recommended next lane: BQML retrain with direct NGS features.

### Phase 32.28: BQML NGS retrain

Phase 32.28 retrained bounded BigQuery ML challengers against `ranking_backtest_feature_mart` after the direct NGS fields landed. The run used train seasons 2017-2023, validation season 2024, and holdout season 2025. It wrote summary-only evidence to `ranking_backtest_runs` and `ranking_backtest_candidate_summaries`; it did not write detail rows, live rankings, or champions.

Models trained:

| Model | Type | Target | Training bytes | Runtime |
|---|---|---|---:|---:|
| `ranking_bqml_ngs_logistic_elite_v1` | `LOGISTIC_REG` | elite finish label | 71,101,044 | 110s |
| `ranking_bqml_ngs_linear_points_v1` | `LINEAR_REG` | target fantasy points | 71,101,044 | 128s |
| `ranking_bqml_ngs_linear_vor_v1` | `LINEAR_REG` | value over replacement | 71,101,044 | 144s |
| `ranking_bqml_ngs_boosted_tree_vor_v1` | `BOOSTED_TREE_REGRESSOR` | value over replacement | 14,025,169,231 | 341s |

PPR aggregate comparison:

| Candidate | 2024 top-N | 2024 captured | 2024 VOR | 2024 NDCG | 2025 top-N | 2025 captured | 2025 VOR | 2025 NDCG |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Enriched logistic elite v1 | 0.5376 | 0.7365 | 0.6010 | 0.6828 | 0.8565 | 0.9060 | 0.8578 | 0.7980 |
| NGS logistic elite v1 | 0.5376 | 0.7364 | 0.6008 | 0.6825 | 0.8576 | 0.9071 | 0.8592 | 0.7990 |
| Enriched linear points v1 | 0.5330 | 0.7335 | 0.6013 | 0.6855 | 0.8565 | 0.9095 | 0.8616 | 0.7981 |
| NGS linear points v1 | 0.5324 | 0.7297 | 0.5927 | 0.6785 | 0.8565 | 0.9081 | 0.8607 | 0.7971 |
| Enriched boosted tree VOR v1 | 0.5382 | 0.7374 | 0.6027 | 0.6816 | 0.8565 | 0.9018 | 0.8494 | 0.7933 |
| NGS boosted tree VOR v1 | 0.5295 | 0.7288 | 0.5892 | 0.6751 | 0.8588 | 0.9076 | 0.8618 | 0.8003 |

Feature signal:

- Boosted-tree VOR used `ngs_rushing_efficiency_score_3yr` and `ngs_rush_yards_over_expected_score_3yr` as real split features.
- Linear models leaned heavily on missingness indicators and existing opportunity/profile features. That makes their NGS read less stable.
- Public nflverse receiving still has no expected catch or catch-over-expected field in this lane. `ngs_catch_over_expected_score_3yr` remains null and flagged.

Decision:

- BQML NGS models are valid owner-review evidence, but they do not create a clear champion path.
- The best holdout move was boosted-tree VOR improving 2025 VOR/NDCG over its enriched predecessor, but it regressed on 2024 validation.
- Logistic elite was essentially flat versus enriched v1, with tiny 2025 gains and no material 2024 movement.
- Current Pigskin remains the live baseline. No champion formula is active.
- Recommended next lane: owner-review comparison of NGS challenger movements only if the owner wants player-level inspection; otherwise hold current Pigskin and focus on explainable review tooling.

### Phase 32.29: Baseline hold and live 2026 review path

Phase 32.29 closed the current ranking-research loop. Current Pigskin remains the live baseline, and no formula champion is active.

Final lane classifications:

| Lane | Classification | Decision |
|---|---|---|
| Current Pigskin candidate score v1 plus LLM final rankings | live baseline | Keep live. |
| Simple projection | owner-review signal | Use as a sanity-check challenger. |
| Enriched BQML logistic elite v1 | owner-review signal | Keep for top-N, VOR, NDCG, and bust-control review. |
| Enriched BQML linear points v1 | owner-review signal | Keep for board-ordering review. |
| BQML NGS logistic elite v1 | context only | Flat to enriched logistic. |
| BQML NGS linear points v1 | context only | Did not improve materially over enriched linear points. |
| BQML boosted tree VOR lanes | context only | Interesting nonlinear check, but validation and cost block promotion. |
| Stats02 WR/TE | component signal | Keep as position-specific explanation. |
| PBP RB/WR | component signal | Keep RB high-value opportunity signal. Protect WR movement. |
| NGS direct diagnostics | component signal | RB rushing NGS is the clearest additive component. |
| Injury and availability | risk flag only | Display as risk context, not a formula default. |
| Historical depth | blocked | Source still lacks required historical season/week context. |
| Sleeper current context | live-only display/context | Never use as historical backtest truth. |

Current no-change state:

- `analytics_pigskin_rankings`: 1,140 active rows across PPR, Half PPR, Standard, and GNG Keeper.
- Active profile-position shape: QB 45, RB 80, WR 100, TE 60 per scoring profile.
- Latest active ranking timestamp: `2026-07-04T07:29:22.569631Z`.
- `ranking_formula_champions`: 0 rows, 0 active champions.
- Enriched BQML v1 summaries: 128 rows.
- BQML NGS v1 summaries: 128 rows.

Live 2026 review-board readiness:

- `analytics_pigskin_rankings_candidates` has a 2026 PPR candidate slice with 936 rows.
- `ranking_backtest_feature_mart` has 2025 target slices, not 2026.
- The current BQML prediction builder expects historical outcome labels and is not a live 2026 review input yet.
- Next owner-approved technical step should build an outcome-free, review-only 2026 prediction path. It must not call Gemini, write live rankings, or activate champions.
