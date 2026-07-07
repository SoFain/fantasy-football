# Phase 33.13 BQML V2 Profile Positional Expansion Report

Final decision: BQML V2 PROFILE POSITIONAL MODELS READY WITH WARNINGS

## Scope

Phase 33.13 completed first-pass BQML v2 positional formula research for Half PPR, PPR, and GNG Keeper.

This phase did not build a top-100 interleaver. It did not write live rankings, activate champions, call Gemini, call Pigskin chat, call Sleeper, deploy, run source ingest, run production ranking generation, or write detail rows.

## Git State

Phase 33.12 was already committed before this phase:

- `69126d2 phase 33.12 calibrate standard overlay guardrails`
- `0b95d67 phase 33.12 record calibration package evidence`

Known untracked files remain historical validation backlog and owner-review artifacts. Generated evidence under `output/` was not staged.

Package commit: pending.

## Dataset Readiness

Profiles checked:

- `half_ppr`
- `ppr`
- `gng_keeper`

All three profiles passed the same readiness gates:

- Target seasons: 2017-2025.
- Train: 2017-2023.
- Validation: 2024.
- Holdout: 2025.
- Positions: QB, RB, WR, TE.
- Duplicate grain rows: 0.
- Missing player IDs: 0.
- Missing target labels: 0.
- Leakage windows where `source_window_end_season >= target_season`: 0.
- Patched fields are present where position-appropriate.

Training split row counts are the same by profile because the feature mart has matching profile slices:

| Split | QB | RB | WR | TE |
|---|---:|---:|---:|---:|
| Train | 3,778 | 8,327 | 13,368 | 6,979 |
| Validation | 573 | 1,276 | 1,982 | 1,087 |
| Holdout | 295 | 366 | 638 | 392 |

Dry-run bytes per profile readiness query: 19,255,912.

## Model Training

Models trained: 48.

Profiles trained in order:

1. `half_ppr`
2. `ppr`
3. `gng_keeper`

Families per profile and position:

- linear points
- linear VOR
- logistic elite
- logistic bust

All models used `LINEAR_REG` or `LOGISTIC_REG` with `data_split_method = 'NO_SPLIT'`. No boosted tree, DNN, AutoML, remote model, Gemini model, or hyperparameter tuning was used.

Training bytes by model family were bounded:

| Position | Linear model bytes | Logistic bust bytes |
|---|---:|---:|
| QB | 18,571,140 | 21,058,068 |
| RB | 29,127,964 | 31,614,892 |
| WR | 32,419,756 | 34,906,684 |
| TE | 37,321,708 | 39,808,636 |

No models were skipped.

## Prediction And Summary Evidence

Predictions were generated for:

- 2024 validation.
- 2025 holdout.

Summary query dry-run bytes: 144,939,573.

Summary rows produced: 144.

Controlled summary write:

| Table | Rows |
|---|---:|
| `ranking_backtest_runs` | 3 |
| `ranking_backtest_candidate_summaries` | 144 |
| `ranking_backtest_results` | 0 |
| `ranking_formula_champions` | 0 |

Write job: `51fb541e-579e-4b62-8b8f-12c737c918d5`.

Write gate: `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` was set only inside the command process and was unset afterward.

Formula version:

- `ranking_backtest_sql_native_bqml_v2_profile_positional_v0`

## Positional Finalists

Standard remains documented from Phase 33.9:

| Profile | QB | RB | WR | TE |
|---|---|---|---|---|
| standard | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | `bqml_v2_standard_wr_logistic_elite_v0` | `bqml_v2_standard_te_logistic_bust_inverse_v0` |

First-pass owner-review finalists for newly trained profiles:

| Profile | Position | Finalist | Top-N | Points captured | VOR captured | NDCG proxy | Bust rate | Missing |
|---|---|---|---:|---:|---:|---:|---:|---:|
| half_ppr | QB | `bqml_v2_half_ppr_qb_linear_points_v0` | 0.026 | 0.061 | 0.071 | 0.054 | 0.004 | 0.569 |
| half_ppr | RB | `bqml_v2_half_ppr_rb_linear_points_v0` | 0.040 | 0.102 | 0.059 | 0.038 | 0.002 | 0.517 |
| half_ppr | WR | `bqml_v2_half_ppr_wr_logistic_bust_inverse_v0` | 0.035 | 0.095 | 0.104 | 0.061 | 0.006 | 0.516 |
| half_ppr | TE | `bqml_v2_half_ppr_te_linear_vor_v0` | 0.017 | 0.064 | 0.069 | 0.049 | 0.004 | 0.528 |
| ppr | QB | `bqml_v2_ppr_qb_linear_points_v0` | 0.026 | 0.060 | 0.067 | 0.055 | 0.005 | 0.570 |
| ppr | RB | `bqml_v2_ppr_rb_linear_points_v0` | 0.040 | 0.118 | 0.061 | 0.038 | 0.002 | 0.517 |
| ppr | WR | `bqml_v2_ppr_wr_logistic_elite_v0` | 0.035 | 0.092 | 0.104 | 0.061 | 0.005 | 0.516 |
| ppr | TE | `bqml_v2_ppr_te_linear_points_v0` | 0.017 | 0.064 | 0.074 | 0.053 | 0.004 | 0.527 |
| gng_keeper | QB | `bqml_v2_gng_keeper_qb_linear_points_v0` | 0.026 | 0.065 | 0.073 | 0.056 | 0.004 | 0.570 |
| gng_keeper | RB | `bqml_v2_gng_keeper_rb_logistic_elite_v0` | 0.041 | 0.108 | 0.073 | 0.042 | 0.001 | 0.517 |
| gng_keeper | WR | `bqml_v2_gng_keeper_wr_linear_points_v0` | 0.035 | 0.101 | 0.109 | 0.067 | 0.007 | 0.516 |
| gng_keeper | TE | `bqml_v2_gng_keeper_te_linear_points_v0` | 0.016 | 0.061 | 0.063 | 0.039 | 0.005 | 0.531 |

## Profile Behavior

Half PPR resembles PPR more than Standard in the RB/WR/TE lane because pass-catching value remains visible in points and VOR targets.

PPR favors linear points for QB/RB/TE and logistic elite for WR in this first pass.

GNG Keeper differs most at RB, where logistic elite is the first-pass owner-review finalist.

Current Pigskin still holds live for every profile. These are positional owner-review formulas only.

## Warnings

- The metric scale is low because the evaluator averages top-N hits across full position universes. Use these values for within-profile, within-position comparison, not public accuracy claims.
- Missing-input rates remain high, roughly 0.52 to 0.57 across many slices.
- Standard finalist status was not retrained in this phase.
- No overall board or top-100 queue rule was tested.

## Files Changed

- `src/bqml_v2_feature_contract.py`
- `tests/test_bqml_v2_feature_contract.py`
- `docs/rebuild/bqml-v2-positional-formula-finalists.md`
- `docs/rebuild/validation/phase-33-13-bqml-v2-profile-positional-expansion-report.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

## Checks

- `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract`: passed, 22 tests.
- `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py`: passed.
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: passed discovery, 245 validation files listed.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_backtest`: passed, 3 validations.
- `git diff --check`: passed. Git reported LF-to-CRLF working-copy warnings only.

Read-only final state:

| Check | Count |
|---|---:|
| Active 2026 live ranking rows | 1,040 |
| Phase 33.13 run rows | 3 |
| Phase 33.13 summary rows | 144 |
| Phase 33.13 detail rows | 0 |
| Phase 33.13 champion rows | 0 |

## No-Top-100 Confirmation

No top-100 interleaver was built. No overall-board merge rule was selected. The future v2.0 top-100 path should use position-locked queues.

## No-Live-Change Confirmation

No live ranking rows changed. No candidate ranking table was overwritten. No champion row was written. No detail rows were written.

## Recommended Next Phase

Phase 33.14: Profile-specific positional owner-review boards.
