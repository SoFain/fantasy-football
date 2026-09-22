# Phase 34.8 RB Fable v1.2 Preseason Role-Signal Report

## Final Decision

`REJECT FORMULA CHANGE; KEEP CURRENT-CONTEXT OVERLAY`

Target-season Week 1 roster membership is leakage-safe, but roster membership alone does not establish depth order or expected workload. Two source-backed variants were tested across the unchanged 2022-to-2023, 2023-to-2024, and 2024-to-2025 folds. Neither beat the Phase 34.4 champion.

The active RB Fable formula remains unchanged. Current Sleeper team and depth-chart context remains a display/ranking overlay, not a backtested formula input. Dated Sleeper snapshots must accumulate before that overlay can be evaluated historically.

## Signals Tested

1. Absolute preseason RB-room touch share: each candidate's input-season non-garbage-time touches divided by the combined input-season touches of all experienced backs on his target-season Week 1 roster.
2. Team-change room-share delta: for players whose Week 1 team changed, projected destination-room share minus prior-team share. Same-team players received zero adjustment.

Both signals use target-season Week 1 rosters and input-season workloads only. No target-season outcome enters a score.

## Results

| Variant | Top 6 | Top 12 | Top 24 | Points at 24 | NDCG@24 | Pairwise | Regret | Elite misses | Top-12 busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Phase 34.4 champion | 0.333 | 0.611 | 0.736 | 0.873 | 0.847 | 0.769 | 0.320 | 6 | 1 |
| Absolute share, 0.03 | 0.333 | 0.583 | 0.722 | 0.871 | 0.846 | 0.768 | 0.329 | 6 | 1 |
| Absolute share, 0.05 | 0.333 | 0.556 | 0.722 | 0.862 | 0.841 | 0.767 | 0.334 | 7 | 2 |
| Absolute share, 0.08 | 0.333 | 0.528 | 0.736 | 0.865 | 0.844 | 0.768 | 0.334 | 6 | 2 |
| Team-change delta, 0.10 | 0.333 | 0.611 | 0.736 | 0.872 | 0.846 | 0.769 | 0.320 | 6 | 1 |
| Team-change delta, 0.20 | 0.278 | 0.611 | 0.736 | 0.873 | 0.847 | 0.769 | 0.324 | 6 | 0 |
| Team-change delta, 0.30 | 0.333 | 0.611 | 0.736 | 0.873 | 0.846 | 0.768 | 0.320 | 6 | 0 |

Coverage was 204 complete rows. Week 1 destination teams and room-share values were available for 201 rows; 44 players changed teams.

## Why It Failed

Absolute room share double-counts the champion's strongest existing input, prior-season volume. The team-change delta isolates new information but still treats roster presence as role evidence. It can distinguish a crowded landing spot from a thin one, but cannot tell which back won the job. That is why it removed a bust without reducing elite misses and paid for the change elsewhere.

The missing feature is dated preseason depth order or a comparable role projection. The warehouse has no replayable historical Sleeper snapshots for these folds, and `raw_nflverse_depth_charts` lacks sufficient historical coverage. Fabricating a proxy would violate the research contract.

## Operational Solution

- Keep `rb_fable_v1_standard_rb` version `1.1-phase-34.4` as the formula champion.
- Continue applying current Sleeper depth-chart context outside the validated score for the live board.
- Continue archiving dated Sleeper snapshots through `scripts/build_sleeper_current_player_context.py --archive`.
- Revisit a formula challenger only after enough preseason snapshots exist for forward evaluation. The candidate input should be change in verified depth order or projected role, not roster membership by itself.

## Files

- `bigquery/views/v_rb_fable_v12_backtest_prep.sql`
- `scripts/build_rb_fable_v12_layer.py`
- `scripts/run_rb_fable_v12_backtest.py`
- `tests/test_rb_fable_v12.py`
- `output/phase-34-8-rb-fable-v12-results.json` (local evidence)
- this report

## Checks

- `venv\Scripts\python.exe -m unittest tests.test_rb_fable_v12 tests.test_rb_fable_01_backtest`: 6 tests passed.
- `scripts/build_rb_fable_v12_layer.py --dry-run`: pass.
- Research view applied successfully in `fantasy_football_advanced_metrics`.
- Read-only forward-fold evaluation completed with the same 204-row champion cohort.

## Safety

- No champion record changed.
- No active ranking row changed.
- No production feature mart changed.
- No model was trained or deployed.
- No 2026 outcome was used.
