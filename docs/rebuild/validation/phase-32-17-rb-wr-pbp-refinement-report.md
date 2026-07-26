# Phase 32.17 - RB/WR PBP Refinement Report

Final decision: RB PBP FORMULA SHOWS SIGNAL

## Files Changed

Committed in `96f7256 phase 32.17 refine rb wr pbp formulas`:

- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

Report created after commit:

- `docs/rebuild/validation/phase-32-17-rb-wr-pbp-refinement-report.md`

## Git State

Before:

- Phase 32.15 package was committed as `facfa18`.
- Phase 32.16 AGENTS/DOX package was committed as `31fc88c`.
- Phase 32.16 report and historical validation backlog files were untracked.

After:

- Phase 32.17 code/docs/tests are committed as `96f7256`.
- Historical validation backlog files remain untracked and out of scope.
- This report remains uncommitted because it was written after the Phase 32.17 commit to include the commit hash.

## Feature Coverage Used

Feature coverage was checked on `ranking_backtest_feature_mart` for 2024 validation and 2025 holdout, PPR, RB/WR, redraft, one-QB.

Key reads:

| Feature | RB 2024 | RB 2025 | WR 2024 | WR 2025 | Use |
|---|---:|---:|---:|---:|---|
| `xfp_score_3yr` | 99.61% | 100.00% | 99.75% | 99.69% | RB, WR |
| `high_value_xfp_score_3yr` | 99.61% | 100.00% | 99.75% | 99.69% | RB |
| `xfp_share_3yr` | 99.61% | 100.00% | 99.75% | 99.69% | RB, WR |
| `receiving_role_dominance_xfp_3yr` | 99.61% | 100.00% | 99.75% | 99.69% | WR |
| `receiving_role_dominance_score` | 0.00% | 0.00% | 100.00% | 100.00% | WR only |
| `receiving_xfp_pbp_3yr` | 98.67% | 100.00% | 99.50% | 99.69% | RB, WR |
| `rushing_xfp_pbp_3yr` | 98.75% | 99.45% | 76.14% | 76.18% | RB only |
| `high_value_target_xfp_score_3yr` | 98.67% | 100.00% | 99.50% | 99.69% | RB, WR |
| `high_value_rush_xfp_score_3yr` | 98.75% | 99.45% | 76.14% | 76.18% | RB only |
| `offensive_snap_share_3yr` | 99.61% | 100.00% | 99.65% | 99.69% | RB, WR |
| `team_environment_score` | 100.00% | 100.00% | 100.00% | 100.00% | RB, WR |

Coverage warning:

- WR rush fields were too sparse for a WR formula in this phase.
- RB receiving-role dominance score coverage is zero, so RB formulas avoided it.

## Formula Definitions

Family:

- `stats02_pbp_refined_v0`

Candidates:

| Candidate | Position | Purpose |
|---|---|---|
| `stats02_rb_pbp_high_value_blend_v0` | RB | Blend weekly xFP, PBP rush/receiving xFP, high-value opportunity, red-zone/goal-line xFP, snap role, and team environment |
| `stats02_rb_pbp_receiving_weighted_v0` | RB | PPR-sensitive RB formula that emphasizes receiving xFP and high-value target xFP, with Standard shifted toward rush and goal-line xFP |
| `stats02_wr_pbp_receiving_dominance_blend_v0` | WR | Blend Stats02 receiving dominance with PBP receiving xFP, high-value target xFP, xFP share, snap role, and team environment |
| `stats02_wr_pbp_scoring_profile_blend_v0` | WR | Standard favors red-zone, goal-line, team environment, and efficiency. PPR/Half/GNG favor receiving dominance, xFP share, and high-value target xFP |

All formulas use:

- non-negative weights
- profile-specific weights where intended
- `no_2025_holdout_weight_tuning=true`
- `no_champion_activation=true`
- PBP xFP fields marked as component proxies

## Dry-Run Stats

Version:

- `ranking_backtest_sql_native_stats02_pbp_refined_v0`

Dry-run:

| Item | Result |
|---|---:|
| candidate count | 4 |
| expected run rows | 4 |
| expected summary rows | 16 |
| expected detail rows | 0 |
| estimated bytes | 81,842,565 |

## Controlled Write Result

Gate:

- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`

Write result:

- BigQuery job ID: `9e3c08e6-c0b9-42df-9977-8ef83b2809ec`
- `ranking_backtest_runs`: 4 rows
- `ranking_backtest_candidate_summaries`: 16 rows
- `ranking_backtest_results`: 0 rows
- `ranking_formula_champions`: 0 rows
- `analytics_pigskin_rankings_candidates`: 0 rows

Gate was removed after the write:

- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=` empty

## Validation Results

2024 validation, best refined candidate versus current:

| Position | Profile | Current pairwise | Refined pairwise | Current captured | Refined captured | Read |
|---|---|---:|---:|---:|---:|---|
| RB | PPR | 0.7891 | 0.8040 | 0.7641 | 0.7654 | improved pairwise, captured flat |
| RB | Half PPR | 0.7862 | 0.7954 | 0.7572 | 0.7571 | improved pairwise, captured flat |
| RB | Standard | 0.7820 | 0.7776 | 0.7460 | 0.7503 | captured improved, pairwise slipped |
| RB | GNG Keeper | 0.7714 | 0.7782 | 0.6864 | 0.7008 | improved pairwise and captured |
| WR | PPR | 0.7791 | 0.7558 | 0.6825 | 0.6880 | captured improved, pairwise weaker |
| WR | Half PPR | 0.7746 | 0.7462 | 0.6594 | 0.6672 | captured improved, pairwise weaker |
| WR | Standard | 0.7614 | 0.7171 | 0.6206 | 0.6295 | captured improved, pairwise weaker |
| WR | GNG Keeper | 0.7597 | 0.7287 | 0.5870 | 0.5997 | captured improved, pairwise weaker |

## Holdout Results

2025 holdout, best refined candidate versus current:

| Position | Profile | Current pairwise | Refined pairwise | Current captured | Refined captured | Read |
|---|---|---:|---:|---:|---:|---|
| RB | PPR | 0.8225 | 0.8426 | 1.0000 | 1.0000 | improved pairwise |
| RB | Half PPR | 0.8252 | 0.8446 | 1.0000 | 1.0000 | improved pairwise |
| RB | Standard | 0.8264 | 0.8374 | 1.0000 | 1.0000 | improved pairwise |
| RB | GNG Keeper | 0.8181 | 0.8302 | 1.0000 | 1.0000 | improved pairwise |
| WR | PPR | 0.8336 | 0.7889 | 0.8796 | 0.8922 | captured improved, pairwise weaker |
| WR | Half PPR | 0.8334 | 0.7861 | 0.8748 | 0.8932 | captured improved, pairwise weaker |
| WR | Standard | 0.8284 | 0.7764 | 0.8690 | 0.8876 | captured improved, pairwise weaker |
| WR | GNG Keeper | 0.8362 | 0.7818 | 0.8712 | 0.8852 | captured improved, pairwise weaker |

## Aggregate Context

2017-2025 aggregate:

| Position | Profile | Current pairwise | Refined pairwise | Current captured | Refined captured | Read |
|---|---|---:|---:|---:|---:|---|
| RB | PPR | 0.7544 | 0.7369 | 0.7611 | 0.7496 | refined under current |
| RB | Half PPR | 0.7558 | 0.7341 | 0.7573 | 0.7438 | refined under current |
| RB | Standard | 0.7558 | 0.7293 | 0.7483 | 0.7361 | refined under current |
| RB | GNG Keeper | 0.7465 | 0.7224 | 0.7095 | 0.6975 | refined under current |
| WR | PPR | 0.7736 | 0.7419 | 0.7367 | 0.7137 | refined under current |
| WR | Half PPR | 0.7684 | 0.7352 | 0.7165 | 0.6951 | refined under current |
| WR | Standard | 0.7571 | 0.7189 | 0.6835 | 0.6620 | refined under current |
| WR | GNG Keeper | 0.7559 | 0.7226 | 0.6546 | 0.6336 | refined under current |

## Interpretation

RB:

- PBP split xFP improved RB pairwise in 2024 PPR, Half PPR, and GNG Keeper.
- It improved all four 2025 holdout profiles on pairwise.
- It did not beat the current Pigskin aggregate across 2017-2025.

WR:

- PBP split xFP improved captured points on validation and holdout slices.
- It materially weakened pairwise versus current Pigskin.
- It is not ready for owner-review as a replacement.

BQML:

- The Phase 32.10 scorecard already shows BQML logistic elite and BQML linear points are useful challenger lanes, but they were not re-run in this Phase 32.17 formula-only path.
- No BQML, ensemble, or Python tournament detail processing was run here.

## Owner-Review Recommendation

RB can be reviewed as a challenger concept, not a replacement.

WR should not be elevated from this pass. The next WR pass should preserve current Pigskin pairwise strength and use PBP fields only as captured-points boosters, or wait for injury/depth and direct NGS receiving inputs.

No champion activation is recommended.

## Scorecard Update Summary

`docs/rebuild/ranking-algorithm-scorecard.md` now includes:

- Phase 32.17 candidate family and formula list
- dry-run and write stats
- validation, holdout, and aggregate comparisons
- no champion active confirmation
- owner-review recommendation

## Matrix Update Summary

`docs/rebuild/ranking-opportunity-metrics-matrix.md` now includes:

- PBP and Stats02 fields used by Phase 32.17
- RB/WR coverage reads
- field-level signal interpretation
- next missing source recommendation

## Tests And Checks Run

- `python -m py_compile src\ranking_formula_backtests.py`: passed.
- `python -m unittest tests.test_ranking_formula_backtests`: 94 tests passed.
- `python scripts\run_bigquery_validations.py --run --pattern ranking_backtest`: 3 passed, 0 failed.
- `python scripts\run_bigquery_validations.py --run --pattern ranking_formula`: 6 passed, 0 failed.
- `python scripts\check_deployment_safety.py`: passed.
- `python -m compileall -q src scripts`: passed.
- `python scripts\run_bigquery_migrations.py --list-pending`: no pending migrations.
- `python scripts\run_bigquery_validations.py --dry-run`: discovered validation files through `230_ranking_feature_mart_pbp_no_target_leakage.sql`.

Full test discovery was not run. The source change was limited to formula candidate definitions and SQL-generation tests, and the focused ranking suite covered the edited behavior.

## No-Live-Change Confirmation

- No deployment.
- No live ranking regeneration.
- No champion formula activation.
- No `ranking_backtest_results` writes.
- No `analytics_pigskin_rankings` writes.
- No Pigskin chat call.
- No Gemini or LLM-backed ranking generation.
- No live Sleeper API call.
- No old Python full tournament run.
- No Python player/candidate/week result-row builder was called.

## Remaining Warnings

- Phase 32.17 formulas were not enough to beat current Pigskin aggregate.
- WR pairwise remains the blocker.
- RB signal is short-window promising but not aggregate-safe.
- PBP xFP remains a component proxy, not official xFP.
- Historical validation backlog files remain untracked and out of scope.
- Phase 32.16 and Phase 32.17 reports remain uncommitted after their respective code commits.

## Recommended Next Phase

Phase 32.18 - Injury/depth role scoring.
