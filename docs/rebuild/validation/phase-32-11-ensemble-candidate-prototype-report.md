# Phase 32.11 Ensemble Candidate Prototype Report

Date: 2026-07-05

Final decision: ENSEMBLE PROTOTYPE READY WITH WARNINGS

Owner-review recommendation: no ensemble challenger yet.

## Scope

Phase 32.11 tested constrained SQL-native ensemble candidates built from:

- current Pigskin baseline
- simple projection baseline
- scarcity-adjusted draft value baseline
- BQML logistic elite
- BQML linear points

This phase did not deploy, regenerate live rankings, activate champion formulas, call Pigskin chat, call Gemini ranking generation, call live Sleeper, run the old Python full tournament, write detail rows, or globally truncate any table.

## Git State

Phase 32.10 was uncommitted at the start of this phase, so it was preserved first.

Commit created before ensemble work:

- `7db067f phase 32.10 prototype bqml baselines`

Relevant Phase 32.11 changed files:

- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-research-north-star.md`
- `docs/rebuild/validation/phase-32-11-ensemble-candidate-prototype-report.md`

The historical validation backlog remains untracked and was not staged.

## Leakage And Split Confirmation

Split policy:

- reference seasons: 2017 through 2023
- validation and tuning season: 2024
- holdout season: 2025

The ensemble weights are fixed in code before holdout evaluation. No 2025 result was used to tune weights.

Guardrails added:

- ensemble weights must be non-negative
- ensemble weights must sum to 1.0
- BQML component weight may not exceed 0.50
- holdout season must be 2025
- tuning season must be earlier than 2025
- BQML predictions are treated as candidate scores, not labels

## Ensemble Families Tested

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

All blends normalize component scores per component, target season, week, scoring profile, league, roster format, and position before blending.

## SQL-Native Dry-Run Stats

Dry-run bytes:

- validation 2024: `6,725,304`
- holdout 2025: `2,410,925`
- aggregate 2024-2025: `9,128,003`

The generated SQL uses `ranking_backtest_feature_mart`, BQML `ML.PREDICT`, BigQuery window functions, and summary aggregation. It does not reference `ranking_backtest_results`, `ranking_formula_champions`, or live ranking tables in the ensemble summary query.

## Controlled Summary-Only Write

Write gate:

- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`
- unset immediately after write

Version:

- `ranking_backtest_sql_native_ensemble_v0_2024_2025`

Write result:

- job ID: `a1d726ed-892b-455e-8709-250b528634c0`
- state: `DONE`
- bytes processed: `9,387,829`
- slot millis: `397,153`
- run rows written: 4
- summary rows written: 80
- detail rows written: 0

Written tables:

- `ranking_backtest_runs`
- `ranking_backtest_candidate_summaries`

Not written:

- `ranking_backtest_results`
- `ranking_formula_champions`
- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_candidates`

## Validation Season Results: 2024

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

Validation read: the best ensemble beats current Pigskin on top-N by about 1.43 percentage points, below the 1.5-point threshold. It also trails current Pigskin on high-confidence and overall pairwise metrics. Scarcity-adjusted draft value, BQML logistic, and BQML linear points all beat the ensemble on some validation metrics, so the blend does not add a clear signal.

## Holdout Results: 2025

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

Holdout read: conservative Pigskin-plus leads the ensembles on top-N, but simple projection leads the overall holdout table. Current Pigskin remains stronger than every ensemble on high-confidence and overall pairwise metrics.

## Aggregate 2024-2025 Ensemble Results

| Ensemble | Top-N | Captured points | VOR captured | Rank corr | High-confidence | Overall pairwise | NDCG@K | Tier accuracy | Bust rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| elite-probability blend | 0.6824 | 0.7995 | 0.6939 | 0.6352 | 0.7180 | 0.5593 | 0.7140 | 0.5566 | 0.0831 |
| balanced research blend | 0.6822 | 0.8015 | 0.6978 | 0.6364 | 0.7188 | 0.5611 | 0.7144 | 0.5575 | 0.0836 |
| position-aware first draft | 0.6814 | 0.7978 | 0.6923 | 0.6353 | 0.7176 | 0.5572 | 0.7126 | 0.5562 | 0.0865 |
| pairwise-strength blend | 0.6810 | 0.8002 | 0.6959 | 0.6385 | 0.7188 | 0.5589 | 0.7135 | 0.5574 | 0.0850 |
| conservative Pigskin-plus | 0.6807 | 0.7972 | 0.6895 | 0.6314 | 0.7143 | 0.5456 | 0.7121 | 0.5547 | 0.0877 |

Aggregate read: the ensembles are close, but the high-confidence and overall pairwise metrics are too weak. This is not an activation signal.

## Tests And Checks

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m py_compile src\ranking_formula_backtests.py`
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_backtest`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_formula`

Results:

- focused ranking tests: 82 passed
- full test discovery: 736 passed
- pending migrations: none
- validation dry-run: 209 files discovered
- ranking backtest validations: 3 passed, 0 failed
- ranking formula validations: 6 passed, 0 failed

## Live Ranking And Champion Confirmation

Read-only checks after the controlled write:

- `analytics_pigskin_rankings` active rows:
  - `ppr`: 285
  - `half_ppr`: 285
  - `standard`: 285
  - `gng_keeper`: 285
- active ranking total: 1,140
- `ranking_formula_champions`: 0 rows

No live ranking table changed. No champion formula was activated.

## Remaining Warnings

- The first ensemble set did not outperform the strongest ingredient on validation season 2024.
- High-confidence and overall pairwise metrics weakened for every ensemble relative to current Pigskin.
- The ingredients appear too correlated. Weight tuning alone is unlikely to create a strong ranking improvement.
- Historical validation backlog files remain untracked and out of scope.

## Recommended Next Phase

Recommended: Phase 32.12 - Add missing opportunity metrics to warehouse.

The next useful work is better input data: route-level opportunity, more stable role features, and stronger ceiling or bust signals. A formula comparison dashboard is also useful for owner review, but it should not imply an activation path for these ensemble candidates.
