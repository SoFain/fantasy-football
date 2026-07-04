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

Partial only. The current runner ranks and scores within position, so true overall draft-order metrics by pick band are not implemented yet. Available position-level VOR captured rates show simple projection and current Pigskin baseline are the best broad families.

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
- Overall draft-order metrics are not ready because the runner partitions rankings by position.
- Seeded v0 and some TE/WR winners have high missing-input rates because `pigskin_context_score` is unavailable in the current historical feature path.
- Trend-aware v2 underperformed after the full target backfill.

## Algorithms Rejected

- `v2_trend_aware` as a direct champion path. It needs feature work before another tournament.
- Any historical LLM replay. It violates this phase cost and safety policy.

## Algorithms Pending

- Overall draft-order formula with pick-band regret.
- Better TE-specific features.
- Low-missing WR/TE challenger that does not depend on unavailable `pigskin_context_score`.
- Optional ML baselines only if dependencies already exist in a future environment.

## Next Experiments

1. Build a formula comparison dashboard for owner review.
2. Add cross-position overall draft-order scoring.
3. Improve TE/WR features before another champion-selection attempt.
4. Generate formula-driven candidate rankings only after owner approval.
