# Phase 38.14 Standard WR Cross-Format Candidate Report

Date: 2026-07-13

> Coverage metrics in this report were superseded by Phase 38.15 after the 87 missing historical rows were repaired. The five-candidate decision did not change.

## Final Decision

None of the five new candidates is a better full-board replacement for WR Fable v1. Keep Fable v1 as the deterministic research baseline. Do not promote a new Standard WR formula from this sprint.

`S1 opportunity-efficiency trim` is worth retaining as an elite-selection challenger. It found 20 of 36 top-12 finishers versus 18 for Fable v1. That gain came with worse pairwise ordering, lower NDCG@24, and lower points captured at 24. It is not a full-board winner.

The active Standard WR board is a separate problem. It still uses `pigskin-llm-20260704071412` and `rank_source = llm_pigskin_adjudicated`, not Fable v1. The live formula has no historical point-in-time LLM series, so this report cannot claim an apples-to-apples backtest victory over it. A production swap needs a current-board review after the remaining Fable coverage issue is repaired.

No ranking row, champion, public feed, application, or production object changed.

## Active Standard Diagnosis

The active board's underlying generic score is:

```text
0.55 grade
+ 0.15 opportunity
+ 0.10 efficiency
+ 0.10 inverse role fragility
+ 0.10 Standard profile points
```

`grade` already equals opportunity plus efficiency. The effective weights are therefore 0.70 opportunity and 0.65 efficiency, while actual Standard profile scoring receives 0.10. The path has no minimum sample qualification, age term, or route-volume shrinkage. Jakobie Keeney-James reaching WR54 from one game and two targets is the clearest failure case.

This is why Fable v1 is the deterministic comparison baseline. The active LLM-adjudicated board cannot be reconstructed historically with the same point-in-time inputs.

## What PPR and Half PPR Actually Added

They did not provide two independent WR algorithms. Rows 1 through 90 on both active boards use the same `wr_fable_v1_score`. Rows 91 through 100 are older fallbacks, but those orders are also identical. All 100 shared WRs have matching PPR and Half-PPR ranks. Their historical outcome labels differ only through reception scoring.

The format-specific warehouse metrics were still useful as candidate inputs:

- `weighted_opportunity_standard / games`
- `weighted_opportunity_half_ppr / games`
- `weighted_opportunity_ppr / games`
- `snap_role_stability`
- `receiving_first_down_rate`

Every overlay field was present on all 542 Fable-score rows from 2022 through 2025. Unknown advanced values would have received the input-season mean after z-scoring, or neutral `z = 0`, with a missing count. No such imputation was needed in this run.

One live metadata defect remains. PPR and Half-PPR formula rows 1 through 90 have the correct `scoring_profile_id` but carry `format = 'GNG Keeper'`. Research queries must filter on `scoring_profile_id`. The rank order is unaffected.

## Corrected Evaluation

The old Fable report evaluated 320 player-folds after requiring six target-season games. That removes short-season injuries and every zero-game outcome. It also selected its ideal group by PPG before summing total points.

This sprint used a fixed preseason cohort:

| Fold | Eligible Week 1 WRs |
|---|---:|
| 2022 input to 2023 outcome | 116 |
| 2023 input to 2024 outcome | 119 |
| 2024 input to 2025 outcome | 117 |
| Total | 352 |

Eligibility came from `raw_nflverse_rosters_weekly`, Week 1, position WR, with status in `ACT`, `RES`, `PUP`, `SUS`, `NWT`, or `INA`. `CUT`, `RET`, and `DEV` rows were excluded. Players who made the Week 1 cohort and later recorded no fantasy rows received zero target points.

Primary evaluation used next-season Standard total points. Pairwise success, top-12 hits, NDCG, and points capture all used that same objective. The six-game PPG lane was retained only as continuity evidence.

All candidate weights were frozen before the corrected evaluation query ran. The folds are retrospective screening, not an untouched holdout.

## Five Frozen Algorithms

All `z` terms are standardized within the input season. The Fable efficiency terms keep the existing route or target shrinkage.

### S1: Opportunity-Efficiency Trim

```text
0.34 WOPR
+ 0.16 non-garbage targets/game
+ 0.12 red-zone targets/game
+ 0.14 YPRR
+ 0.03 EPA/target
+ 0.01 YAC/reception
+ 0.02 aDOT-adjusted catch rate
+ 0.10 blended TD rate
+ 0.03 breakout-window bonus
+ 0.025 age decline
+ 0.025 games rate
```

This moves weight out of weak per-target efficiency terms and into earned opportunity.

### S2: Standard TD Balance

```text
0.30 WOPR
+ 0.14 non-garbage targets/game
+ 0.15 red-zone targets/game
+ 0.14 YPRR
+ 0.03 EPA/target
+ 0.01 YAC/reception
+ 0.02 aDOT-adjusted catch rate
+ 0.14 blended TD rate
+ 0.03 breakout-window bonus
+ 0.02 age decline
+ 0.02 games rate
```

This is the strongest Standard-specific touchdown and red-zone tilt.

### S3: PPR Opportunity Transfer

```text
0.75 z(Fable v1) + 0.25 z(PPR weighted opportunity/game)
```

### S4: Half-PPR Role Balance

```text
0.70 z(Fable v1)
+ 0.20 z(Half-PPR weighted opportunity/game)
+ 0.10 z(snap-role stability)
```

### S5: Standard Role Floor

```text
0.65 z(Fable v1)
+ 0.20 z(Standard weighted opportunity/game)
+ 0.10 z(snap-role stability)
+ 0.05 z(receiving first-down rate)
```

## Primary Results: Fixed-Cohort Standard Total Points

Pairwise is the broad success rate. Top-12 is the elite hit rate.

| Formula | Pairwise | Top-12 hits | Top-12 rate | Spearman | Points@24 | NDCG@24 | Elite misses | Top-12 busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| WR Fable v1 baseline | **75.94%** | 18/36 | 50.00% | **0.7118** | 84.84% | 0.8075 | 11 | 3 |
| S1 opportunity-efficiency trim | 75.77% | **20/36** | **55.56%** | 0.7079 | 84.50% | 0.8032 | 11 | 3 |
| S2 Standard TD balance | 75.50% | 19/36 | 52.78% | 0.7028 | 83.88% | 0.8013 | 11 | **2** |
| S3 PPR opportunity transfer | 75.78% | 19/36 | 52.78% | 0.7090 | 84.56% | 0.8011 | 11 | 4 |
| S4 Half-PPR role balance | 75.91% | 19/36 | 52.78% | 0.7116 | **84.85%** | 0.8030 | 11 | 4 |
| S5 Standard role floor | 75.87% | 18/36 | 50.00% | 0.7105 | **84.85%** | **0.8079** | 11 | 4 |

No candidate cleared the replacement gates. A replacement needed at least a 0.010 NDCG@24 gain, two fold wins, no lost top-12 hits, stable points capture, no added busts, full coverage, plus a meaningful pairwise or Spearman gain.

Candidate read:

- S1 is the only useful elite-selection challenger. Its two extra top-12 hits do not outweigh the full-board losses.
- S2 captured the most points at 12 and cut one bust. It was the worst broad ordering model.
- S3 rejected. Direct PPR opportunity hurt NDCG and added a bust.
- S4 came closest to baseline ordering. Its 0.0068 percentage-point Points@24 gain is noise, while NDCG fell 0.0045 and busts rose.
- S5 gained 0.00037 NDCG@24. That is far below the promotion threshold and came with another bust.

## Six-Game PPG Continuity Check

The eligible-roster filter leaves 309 player-folds in this secondary lane.

| Formula | Pairwise | Top-12 rate | Spearman | Points@24 | NDCG@24 | Misses | Busts |
|---|---:|---:|---:|---:|---:|---:|---:|
| WR Fable v1 baseline | **76.56%** | **63.89%** | **0.7325** | **88.90%** | **0.8494** | 8 | **2** |
| S1 | 76.44% | 61.11% | 0.7282 | 88.67% | 0.8470 | 8 | 2 |
| S2 | 76.07% | 61.11% | 0.7221 | 87.92% | 0.8444 | 8 | 2 |
| S3 | 76.25% | 58.33% | 0.7271 | 88.32% | 0.8458 | 8 | 2 |
| S4 | 76.48% | 58.33% | 0.7305 | 88.31% | 0.8446 | 8 | 2 |
| S5 | 76.50% | 55.56% | 0.7313 | 88.31% | 0.8481 | 8 | 3 |

The old published baseline values, 76.86% pairwise and 0.7383 Spearman, used a different 320-row survivor cohort. They should not be compared as if this were metric drift.

## Current 2026 Board Sanity Check

These ranks use 2025 source-season performance only. Current team and Sleeper context belong in the separate safety layer.

| Player | Fable v1 | S1 | S2 | S3 | S4 | S5 |
|---|---:|---:|---:|---:|---:|---:|
| Justin Jefferson | 13 | 12 | 12 | 12 | 10 | 10 |
| Garrett Wilson | 14 | 13 | 14 | 14 | 14 | 16 |
| A.J. Brown | 15 | 14 | 13 | 15 | 15 | 14 |
| Michael Pittman | 41 | 41 | 39 | 41 | 34 | 34 |
| Khalil Shakir | 43 | 43 | 43 | 43 | 44 | 46 |

Pittman is a real miss in the active Standard board, where he is WR53. Fable v1 puts him at WR41 before current-context handling, and the role candidates lift him to WR34. Shakir is WR46 live and WR43 in Fable v1. His starter status supports eligibility, but the tested role overlays do not support a large formula-driven jump.

The Fable board puts A.J. Brown behind Jefferson and Wilson. That conflicts with the current active positional order and needs owner review before any live swap.

## Resolved Coverage Risk

Phase 38.15 repaired all 87 historical scores. A source audit rejected the proposed blanket zero: 39 rows had between one and seven red-zone targets. Missing split rows now use the exact season red-zone target count from `player_season_advanced_metrics` and play-by-play red-zone touchdowns, with an explicit fallback flag and method. One row also required a play-by-play non-garbage-time target fallback.

One exploratory signal remains worth a clean test. A 90% Fable plus 10% prior receiving-yards/game overlay raised the old-cohort Spearman from 0.7384 to 0.7415 without losing top-12 hits. That weight was inspected on the same folds, so it is hypothesis generation, not replacement evidence.

The Week 1 roster rows were loaded retrospectively on 2026-06-30. They preserve historical week state, but they were not archived before each kickoff. They are suitable for this retrospective roster gate, not for claims about an exact historical preseason date.

## Files Changed

- `scripts/run_standard_wr_candidate_sprint.py`
- `tests/test_standard_wr_candidate_sprint.py`
- `docs/rebuild/validation/phase-38-14-standard-wr-cross-format-candidate-report.md`
- `AGENTS.md`

Generated evidence is stored in ignored output at `output/standard-wr-five-candidate-backtest.json`.

## Checks

- `python -m py_compile scripts/run_standard_wr_candidate_sprint.py tests/test_standard_wr_candidate_sprint.py`
- `python -m unittest tests.test_standard_wr_candidate_sprint`: 4 passed
- Read-only BigQuery candidate run: 352 fixed-cohort player-folds
- Active WR source audit by `scoring_profile_id`
- PPR versus Half-PPR active rank comparison: 100 shared, 0 mismatches
- Structural-null coverage query: 87 null scores, all with missing red-zone inputs

## Next Phase

Test one predeclared yards/game overlay and the existing advanced Standard out-of-fold model under the repaired total-points protocol. Do not tune another set of hand weights on these three folds.
