# Ranking Algorithm Scorecard

Last updated: 2026-07-04

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
| ML baselines | skipped | none | `scikit-learn` was not installed. No packages were installed. |

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
