# Phase 38.15 WR Fable Structural Fallback Repair

Date: 2026-07-13

## Final Decision

The 87 missing historical WR Fable v1 scores are repaired. Historical score coverage is now 494 of 494 qualified rows across 2022 through 2024.

The repair improved both broad ordering metrics while leaving elite hits, misses, and busts unchanged. It is accepted for the research WR Fable views.

No active ranking, champion, unified board, public JSON object, application, or production job changed. The active Standard WR board remains `pigskin-llm-20260704071412` with 100 rows.

## Why Blanket Zero Was Rejected

All 87 null scores were missing a governed red-zone split row, but that did not mean every player had zero actual red-zone usage.

| Source-backed red-zone target result | Historical rows |
|---|---:|
| Zero targets | 48 |
| One or more targets | 39 |
| Maximum | 7 |

A blanket zero would have understated 39 players. The repair uses a source-backed fallback only when the situational split row is absent.

## Repair Contract

For a missing red-zone split row:

- `sourced_red_zone_targets` comes from regular-season `player_season_advanced_metrics.red_zone_targets`.
- `red_zone_touchdowns` comes from `stg_play_player_events` target events inside the 20-yard line.
- `red_zone_structural_fallback = true`.
- `red_zone_input_method = 'ADVANCED_TARGETS_PBP_TDS'`.

All 87 historical fallback rows had a source-backed target count and touchdown count. The play-by-play touchdown count was zero for all 87.

Danny Gray's 2022 row also lacked a non-garbage-time split. It now uses four target events with win probability between 0.05 and 0.95:

- `non_garbage_structural_fallback = true`
- `non_garbage_input_method = 'PBP_WP_5_95'`

The same bounded fallback restores Ke'Shawn Williams for the descriptive 2025 board. Present situational split rows keep their original route-based metrics. The change does not broadly coalesce unknown values to zero.

## Coverage Result

| Input season | Qualified | Before | After | Restored |
|---|---:|---:|---:|---:|
| 2022 | 161 | 132 | 161 | 29 |
| 2023 | 172 | 140 | 172 | 32 |
| 2024 | 161 | 135 | 161 | 26 |
| Total | 494 | 407 | 494 | 87 |

The descriptive 2025 board now has 168 scores from 169 qualified rows. Travis Hunter remains null because age is unavailable. That is unrelated to the structural split repair.

## Legacy Fable Backtest Impact

This lane retains the prior six-game PPG protocol for comparison with the Phase 35 baseline.

| Metric | Before | After | Change |
|---|---:|---:|---:|
| Complete player-folds | 320 | 363 | +43 |
| Spearman | 0.7383 | **0.7574** | +0.0191 |
| Score correlation | 0.7460 | **0.7623** | +0.0163 |
| Pairwise success | 76.86% | **77.77%** | +0.91 pp |
| Top-12 precision | 63.89% | 63.89% | unchanged |
| Points@12 | 91.72% | 91.72% | unchanged |
| Points@24 | 89.28% | 89.28% | unchanged |
| NDCG@24 | 0.8494 | 0.8501 | +0.0007 |
| Band regret | 0.2659 | **0.2339** | -0.0320 |
| Elite misses | 8 | 8 | unchanged |
| Top-12 busts | 2 | 2 | unchanged |

The restored rows improved full-pool ordering without moving the elite error counts.

## Corrected Fixed-Roster Backtest Impact

This is the primary preseason evaluation from Phase 38.14. It uses eligible Week 1 WRs and next-season Standard total points, including zero-game outcomes.

| Metric | Before | After | Change |
|---|---:|---:|---:|
| Player-folds | 352 | 404 | +52 |
| Pairwise success | 75.94% | **76.57%** | +0.63 pp |
| Spearman | 0.7118 | **0.7260** | +0.0142 |
| Top-12 precision | 50.00% | 50.00% | unchanged |
| Points@24 | 84.84% | 84.84% | unchanged |
| NDCG@24 | 0.8075 | 0.8085 | +0.0010 |
| Elite misses | 11 | 11 | unchanged |
| Top-12 busts | 3 | 3 | unchanged |

## Five-Candidate Rerun

The candidate decision remains unchanged. None beats repaired Fable v1 across the full preseason objective.

| Formula | Pairwise | Top-12 rate | Spearman | Points@24 | NDCG@24 | Busts |
|---|---:|---:|---:|---:|---:|---:|
| Repaired Fable v1 | **76.57%** | 50.00% | **0.7260** | 84.84% | **0.8085** | 3 |
| S1 opportunity-efficiency trim | 76.38% | **55.56%** | 0.7227 | 84.50% | 0.8032 | 3 |
| S2 Standard TD balance | 76.16% | 52.78% | 0.7184 | 83.88% | 0.8017 | **2** |
| S3 PPR opportunity transfer | 76.41% | 52.78% | 0.7236 | 84.59% | 0.7979 | 4 |
| S4 Half-PPR role balance | 76.52% | 52.78% | 0.7253 | **84.85%** | 0.8011 | 4 |
| S5 Standard role floor | 76.49% | 50.00% | 0.7249 | **84.85%** | 0.8046 | 4 |

S1 remains an elite-selection challenger only. S4 remains the closest broad-ordering challenger, but it loses NDCG and adds a bust.

## Current Board Effect

The established review players barely moved:

| Player | Repaired Fable WR rank |
|---|---:|
| Justin Jefferson | 13 |
| Garrett Wilson | 14 |
| A.J. Brown | 15 |
| Michael Pittman | 41 |
| Khalil Shakir | 43 |

Calvin Ridley is the highest restored 2025 player at Fable WR66. This is a research-board result, not a live ranking change.

## Files Changed

- `bigquery/views/v_wr_fable_v1_situational_splits.sql`
- `bigquery/views/v_wr_fable_v1_metric_inputs.sql`
- `tests/test_wr_fable_v1.py`
- `docs/rebuild/validation/phase-38-14-standard-wr-cross-format-candidate-report.md`
- `docs/rebuild/validation/phase-38-15-wr-fable-structural-fallback-repair.md`
- `AGENTS.md`

Generated evidence:

- `output/wr-fable-v1-backtest-red-zone-repair.json`
- `output/standard-wr-five-candidate-backtest-red-zone-repair.json`

The output directory remains ignored.

## Checks

- `python scripts/build_wr_fable_v1_metric_layer.py --dry-run`
- `python -m unittest tests.test_wr_fable_v1 tests.test_standard_wr_candidate_sprint`: 14 passed
- `python scripts/build_wr_fable_v1_metric_layer.py --apply`: five research views replaced successfully
- Coverage query: 494 of 494 historical scores complete
- Fallback-source query: zero missing red-zone and non-garbage fallback values
- Legacy Fable backtest rerun: 363 player-folds
- Fixed-roster candidate rerun: 404 player-folds
- Active Standard WR verification: unchanged at 100 `pigskin-llm-20260704071412` rows

## Next Phase

Use the repaired baseline for one frozen receiving-yards-per-game overlay and an apples-to-apples test of the existing advanced Standard out-of-fold model. Do not publish a Standard WR formula until the A.J. Brown, Pittman, and restored-player board movements receive owner review.
