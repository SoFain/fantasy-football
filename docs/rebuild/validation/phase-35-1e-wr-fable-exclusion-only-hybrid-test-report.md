# Phase 35.1E WR Fable Exclusion-Only Hybrid Test

## Final Decision

`WR FABLE V1 STILL BEST`

The exclusion-only hybrid does exactly what was intended technically: every existing v1 score is preserved, and eight previously excluded player-fold rows are added. It still fails the top-12 precision guardrail because Rashee Rice is added at predicted WR24 and finishes WR5 in the target season.

Do not promote the hybrid. The next formula work should focus only on calibrating scores for carry-forward players who were previously unrankable. Existing v1 rows do not need another formula change.

## Test Contract

For I4 rows:

```text
exclusion_only_score = COALESCE(wr_fable_v1_score, injury_candidate_score)
```

- Existing v1 scores changed: 0.
- Existing v1 score ordering changed: 0 on the fixed cohort.
- Environment modifier: not used.
- Current role and depth context: display only.

## Backtest Result

| Formula | Complete | Spearman | Score corr. | Top 6 | Top 12 | Top 24 | Pts@12 | Pts@24 | NDCG@12 | NDCG@24 | Pairwise | Regret | Misses | Busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| WR Fable v1 | 320 | 0.7383 | 0.7460 | 0.2778 | 0.6389 | 0.6250 | 0.9172 | 0.8928 | 0.8437 | 0.8494 | 0.7686 | 0.2659 | 8 | 2 |
| Hybrid, fixed v1 cohort | 320 | 0.7383 | 0.7460 | 0.2778 | 0.6389 | 0.6250 | 0.9172 | 0.8928 | 0.8437 | 0.8494 | 0.7686 | 0.2659 | 8 | 2 |
| Hybrid, expanded cohort | 328 | 0.7398 | 0.7465 | 0.2778 | 0.6111 | 0.6250 | 0.9216 | 0.8929 | 0.8406 | 0.8496 | 0.7695 | 0.2629 | 8 | 2 |

The expanded hybrid passes every acceptance check except top-12 precision. The decline is 0.0278, above the allowed 0.01.

## Added Player-Fold Rows

| Input | Player | Predicted cohort rank | Actual cohort rank | Actual full WR finish | Prior weight | Type |
|---:|---|---:|---:|---:|---:|---|
| 2022 | Brandon Johnson | 98 | 50 | 59 | 0% | Rookie limited sample |
| 2022 | Samori Toure | 100 | 103 | 153 | 0% | Rookie limited sample |
| 2022 | Jalen Tolbert | 111 | 77 | 106 | 0% | Rookie limited sample |
| 2024 | Rashee Rice | 24 | 5 | 5 | 40% | Injury carry-forward |
| 2024 | Malik Heath | 94 | 98 | 146 | 30% | Injury carry-forward |
| 2024 | Tyquan Thornton | 100 | 50 | 57 | 0% | Required prior rate unavailable |
| 2024 | Britain Covey | 105 | 106 | 173 | 0% | Required prior rate unavailable |
| 2024 | Deven Thompkins | 106 | 105 | 171 | 30% | Injury carry-forward |

Rashee Rice is the entire top-12 issue. The baseline 2024-to-2025 predicted top 12 is unchanged by score. Adding Rice to the evaluated cohort makes him actual WR5, shifting CeeDee Lamb from actual cohort rank 12 to 13. Rice is predicted WR24, so hybrid top-12 precision loses one hit.

## Current Board Effect

The current hybrid restores Malik Nabers at WR8 and Tyreek Hill at WR24. All existing v1 scores remain exact. Their ranks below the insertion points shift because the board has more players.

| Player | v1 rank | Hybrid rank | Standard | Score source | GP | Routes | Prior weight |
|---|---:|---:|---:|---|---:|---:|---:|
| Amon-Ra St. Brown | 1 | 1 | 3 | v1 | 17 | 567 | 0% |
| Jaxon Smith-Njigba | 2 | 2 | 1 | v1 | 17 | 497 | 0% |
| Puka Nacua | 3 | 3 | 2 | v1 | 16 | 463 | 0% |
| Rashee Rice | 4 | 4 | 8 | v1 | 8 | 266 | 0% |
| Ja'Marr Chase | 5 | 5 | 4 | v1 | 16 | 634 | 0% |
| Davante Adams | 6 | 6 | 13 | v1 | 14 | 409 | 0% |
| Drake London | 7 | 7 | 5 | v1 | 12 | 396 | 15% unused |
| Malik Nabers | - | 8 | 18 | I4 carry-forward | 4 | 136 | 40% |
| Chris Olave | 8 | 9 | 6 | v1 | 16 | 586 | 0% |
| George Pickens | 9 | 10 | 11 | v1 | 17 | 610 | 0% |
| Nico Collins | 10 | 11 | 15 | v1 | 15 | 483 | 0% |
| CeeDee Lamb | 11 | 12 | 14 | v1 | 13 | 454 | 0% |
| Zay Flowers | 12 | 13 | 12 | v1 | 17 | 480 | 0% |
| Justin Jefferson | 13 | 14 | 9 | v1 | 17 | 558 | 0% |
| Garrett Wilson | 14 | 15 | 10 | v1 | 7 | 228 | 30% unused |
| A.J. Brown | 15 | 16 | 7 | v1 | 15 | 484 | 0% |
| Wan'Dale Robinson | 16 | 17 | 17 | v1 | 16 | 543 | 0% |
| Tetairoa McMillan | 17 | 18 | 16 | v1 | 17 | 553 | 0% |
| Rome Odunze | 18 | 19 | 19 | v1 | 12 | 415 | 15% unused |
| DK Metcalf | 19 | 20 | 34 | v1 | 15 | 429 | 0% |
| Emeka Egbuka | 20 | 21 | 26 | v1 | 17 | 540 | 0% |
| Courtland Sutton | 21 | 22 | 25 | v1 | 17 | 633 | 0% |
| Jaylen Waddle | 22 | 23 | 22 | v1 | 16 | 417 | 0% |
| Tyreek Hill | - | 24 | - | I4 carry-forward | 4 | 105 | 40% |
| Michael Wilson | 23 | 25 | 31 | v1 | 17 | 632 | 0% |
| Quentin Johnston | 24 | 26 | 30 | v1 | 13 | 487 | 0% |
| Terry McLaurin | 25 | 27 | 21 | v1 | 10 | 264 | 15% unused |
| Tee Higgins | 26 | 28 | 24 | v1 | 15 | 527 | 0% |
| DeVonta Smith | 27 | 29 | 20 | v1 | 17 | 524 | 0% |
| Jauan Jennings | 28 | 30 | 37 | v1 | 15 | 466 | 0% |
| Mike Evans | 29 | 31 | 29 | v1 | 8 | 228 | 30% unused |
| Alec Pierce | 30 | 32 | 23 | v1 | 15 | 478 | 0% |
| Romeo Doubs | 31 | 33 | 36 | v1 | 16 | 419 | 0% |
| Parker Washington | 32 | 34 | 39 | v1 | 16 | 412 | 0% |
| Jameson Williams | 33 | 35 | 27 | v1 | 17 | 600 | 0% |
| Troy Franklin | 34 | 36 | 41 | v1 | 17 | 491 | 0% |
| Christian Watson | 35 | 37 | 32 | v1 | 10 | 244 | 15% unused |
| Ladd McConkey | 36 | 38 | 35 | v1 | 16 | 562 | 0% |
| Stefon Diggs | 37 | 39 | - | v1 | 17 | 421 | 0% |
| Jakobi Meyers | 38 | 40 | 28 | v1 | 16 | 529 | 0% |
| Deebo Samuel | 39 | 41 | - | v1 | 16 | 442 | 0% |
| Keenan Allen | 40 | 42 | - | v1 | 17 | 468 | 0% |

`Prior weight unused` means I4 calculated a candidate blend, but the hybrid correctly retained the existing v1 score.

## Files Changed

- `bigquery/views/v_wr_fable_v1d_scored_seasons.sql`
- `bigquery/views/v_wr_fable_v1d_backtest_prep.sql`
- `bigquery/views/v_wr_fable_v1d_current_board.sql`
- `scripts/run_wr_fable_v1e_hybrid_test.py`
- `tests/test_wr_fable_v1d.py`
- this report

## Safety And Checks

- 35 focused tests passed. The three research runners/builders compile.
- Deployment safety checker passed every check.
- Baseline reproduced exactly.
- Existing v1 scores changed: 0.
- Fixed-cohort aggregate differences: 0.
- Active v1d/Phase 35.1E ranking rows: 0.
- No environment score was applied.
- No live ranking write, champion activation, deployment, job trigger, Scheduler creation, Gemini call, or Pigskin chat call occurred.
- No 2026 outcome or market input was used.
- The shared worktree remains dirty from concurrent phase work. Nothing was staged, committed, reverted, or packaged.

Recommended next step: do not change v1. If carry-forward work continues, isolate why Rashee Rice's 40% prior blend lands at WR24 despite a WR5 target finish. Any next test should remain limited to the newly eligible carry-forward cohort.
