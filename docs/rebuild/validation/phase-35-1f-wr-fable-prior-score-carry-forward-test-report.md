# Phase 35.1F WR Fable Prior-Score Carry-Forward Test

## Final Decision

`WR FABLE V1 STILL BEST`

The prior-score carry-forward candidate improves coverage and several secondary metrics, but it still fails the hard top-12 precision requirement. Do not replace the global Standard WR formula.

This should end the current heuristic test sequence. Existing v1 scoring is stable. The remaining failure is confined to previously excluded players, especially Rashee Rice. Another simple availability or environment adjustment is unlikely to solve it.

## Formula Tested

Existing v1 rows remain exact. A previously excluded veteran is eligible only when a prior qualified v1 score exists.

```text
carry_forward_score =
  prior_v1_score
  - prior_v1_age_availability_component
  + current_two_year_age_availability_component
```

Shortened rookies remain in a separate review lane and do not enter the main replacement backtest.

## Backtest Result

| Formula | Complete | Spearman | Score corr. | Top 6 | Top 12 | Top 24 | Pts@12 | Pts@24 | NDCG@12 | NDCG@24 | Pairwise | Regret | Misses | Busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| WR Fable v1 | 320 | 0.7383 | 0.7460 | 0.2778 | 0.6389 | 0.6250 | 0.9172 | 0.8928 | 0.8437 | 0.8494 | 0.7686 | 0.2659 | 8 | 2 |
| Fixed v1 cohort | 320 | 0.7383 | 0.7460 | 0.2778 | 0.6389 | 0.6250 | 0.9172 | 0.8928 | 0.8437 | 0.8494 | 0.7686 | 0.2659 | 8 | 2 |
| Prior-score carry-forward | 335 | 0.7409 | 0.7488 | 0.2778 | 0.6111 | 0.6250 | 0.9216 | 0.8929 | 0.8406 | 0.8497 | 0.7704 | 0.2563 | 8 | 2 |

Existing v1 scores changed: 0. The expanded candidate passes every guardrail except top-12 precision. The decline is 0.0278, above the allowed 0.01.

## Added Carry-Forward Rows

| Input | Player | Prior score | Availability-adjusted score | Predicted | Actual cohort | Actual full WR finish |
|---:|---|---:|---:|---:|---:|---:|
| 2023 | Mike Williams | 0.457 | 0.347 | 49 | 88 | 108 |
| 2023 | Alec Pierce | -0.028 | -0.021 | 68 | 37 | 41 |
| 2023 | Olamide Zaccheaus | 0.022 | -0.089 | 70 | 70 | 85 |
| 2023 | Laviska Shenault | -0.261 | -0.292 | 81 | 103 | 143 |
| 2023 | DeAndre Carter | -0.279 | -0.293 | 82 | 109 | 154 |
| 2023 | Jalen Reagor | -0.712 | -0.743 | 108 | 102 | 140 |
| 2024 | Rashee Rice | 0.906 | 0.832 | 20 | 5 | 5 |
| 2024 | Zay Jones | 0.431 | 0.413 | 44 | 78 | 99 |
| 2024 | Darius Slayton | 0.077 | 0.072 | 60 | 58 | 71 |
| 2024 | Jahan Dotson | 0.059 | 0.042 | 63 | 95 | 125 |
| 2024 | Treylon Burks | -0.400 | -0.424 | 92 | 91 | 121 |
| 2024 | Malik Heath | -0.471 | -0.514 | 98 | 102 | 146 |
| 2024 | Deven Thompkins | -0.624 | -0.698 | 106 | 110 | 171 |
| 2024 | Xavier Hutchinson | -0.808 | -0.788 | 109 | 64 | 79 |
| 2024 | Ben Skowronek | -0.796 | -0.820 | 110 | 107 | 157 |

## Rashee Rice Finding

The prior-score method improves Rice from predicted WR24 under I4 to WR20. He still finishes WR5. Because the newly added elite player remains outside the predicted top 12, the expanded cohort loses one top-12 hit even though every existing v1 score and ordering stays unchanged.

This is not an availability-only problem. Rice's prior qualified v1 score was already too low to place him near the next-season elite tier. Fixing that would require a better performance signal or model, not another carry-forward weight.

## Rookie Review Lane

The main replacement test excludes rookies without prior qualified scores. Three source-backed shortened-rookie rows remain available for review:

| Input | Player | Review score | Actual full WR finish |
|---:|---|---:|---:|
| 2022 | Brandon Johnson | -0.566 | 59 |
| 2022 | Samori Toure | -0.614 | 153 |
| 2022 | Jalen Tolbert | -0.888 | 106 |

None warrants entry into the main ranked board based on this evidence.

## Current Board Effect

- Malik Nabers enters at WR8 using prior v1 performance with current two-year availability.
- Tyreek Hill enters at WR37. The prior-score method is materially more conservative than I4, which placed him WR24.
- All existing v1 scores remain exact. Ranks below Malik shift by one because a new player enters at WR8.
- No environment or depth-chart score is applied.

## Files Changed

- `bigquery/views/v_wr_fable_v1d_scored_seasons.sql`
- `bigquery/views/v_wr_fable_v1d_backtest_prep.sql`
- `bigquery/views/v_wr_fable_v1d_current_board.sql`
- `scripts/run_wr_fable_v1f_carry_forward_test.py`
- `tests/test_wr_fable_v1d.py`
- this report

## Safety And Recommendation

- Baseline reproduced exactly.
- Existing v1 scores changed: 0.
- Fixed-cohort aggregate differences: 0.
- Rookies were excluded from the replacement score.
- No environment score, current depth input, market value, or 2026 outcome entered the backtest.
- No live ranking write, champion activation, deployment, job trigger, Scheduler creation, Gemini call, or Pigskin chat call occurred.

Recommendation: retain WR Fable v1 as the global Standard WR formula. Stop heuristic carry-forward tuning for now. Revisit excluded-player ranking only when a new source-backed performance signal or a properly trained model is available.
