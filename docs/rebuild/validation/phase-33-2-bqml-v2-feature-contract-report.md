# Phase 33.2 BQML V2 Feature Contract Report

Final decision: BQML V2 FEATURE CONTRACT READY WITH WARNINGS

## Scope

Phase 33.2 turned the Phase 33.1 BQML v2 architecture audit into an enforceable Standard-first feature and target contract.

No model was trained. No live ranking table changed. No champion was activated. No Gemini, Pigskin chat, Sleeper API, source ingest, materialization, deployment, or BigQuery write path was used.

## Files Changed

| File | Change |
|---|---|
| `src/bqml_v2_feature_contract.py` | Added BQML v2 contract constants, position feature allowlists, blocked feature checks, target labels, Standard dataset SQL builder, coverage SQL builder, and leakage assertion. |
| `tests/test_bqml_v2_feature_contract.py` | Added focused tests for Standard-first policy, model families, allowlists, blocked features, leakage rules, target separation, proxy naming, and TE35 review depth. |
| `docs/rebuild/bqml-v2-ranking-architecture.md` | Added owner-readable architecture contract. |
| `docs/rebuild/ranking-algorithm-scorecard.md` | Added Phase 33.2 scorecard status. |
| `docs/rebuild/ranking-opportunity-metrics-matrix.md` | Added Phase 33.2 feature-family status and Standard coverage summary. |
| `docs/rebuild/validation/phase-33-2-bqml-v2-feature-contract-report.md` | Added this report. |

Commit hash: not committed in this phase.

## Git State

Before this phase, the worktree already contained the historical untracked validation backlog and the untracked Phase 33.1 report.

After this phase:

- Modified tracked docs: `docs/rebuild/ranking-algorithm-scorecard.md`, `docs/rebuild/ranking-opportunity-metrics-matrix.md`.
- New Phase 33.2 files: `src/bqml_v2_feature_contract.py`, `tests/test_bqml_v2_feature_contract.py`, `docs/rebuild/bqml-v2-ranking-architecture.md`, this report.
- The historical validation backlog remains untracked and untouched.
- No files were staged or committed.

## Feature Contract Summary

Standard is the first v2 scoring profile. The scoring-profile review order is:

1. `standard`
2. `half_ppr`
3. `ppr`
4. `gng_keeper`

The contract defines eight model families:

| Family | Position | Target group |
|---|---|---|
| `bqml_v2_qb_profile_points` | QB | fantasy points and VOR |
| `bqml_v2_qb_elite_bust` | QB | elite, starter, bust labels |
| `bqml_v2_rb_profile_points` | RB | fantasy points and VOR |
| `bqml_v2_rb_elite_bust` | RB | elite, starter, bust labels |
| `bqml_v2_wr_profile_points` | WR | fantasy points and VOR |
| `bqml_v2_wr_elite_bust` | WR | elite, starter, bust labels |
| `bqml_v2_te_profile_points` | TE | fantasy points and VOR |
| `bqml_v2_te_elite_bust` | TE | elite, starter, bust labels |

Initial model types: `LINEAR_REG`, `LOGISTIC_REG`.

Deferred: boosted tree models until Standard baseline cost and sanity checks pass.

Blocked: DNN, AutoML, remote models, Gemini-backed models, broad hyperparameter tuning.

The contract has no global all-profile winner. All-profile aggregate is context only.

## Blocked Feature Tests

Focused tests prove these are rejected:

- `pigskin_context_score`
- `yprr`
- `yards_per_route_run`
- `tprr`
- `targets_per_route_run`
- `true_route_share`
- `route_share`
- `first_read_share`
- current Sleeper team/status/depth fields
- `depth_chart_role_score_3yr` while depth coverage is unavailable

Proxy naming is pinned:

- `receiving_first_down_exp_pbp_3yr` is a chain-mover proxy, not `1D/RR`.
- `offensive_snap_share_3yr` is a snap-role proxy, not route participation rate.

## Target Contract Summary

Allowed labels:

- `target_fantasy_points`
- `value_over_replacement`
- `elite_finish_label`
- `starter_finish_label`
- `bust_label`

Target and outcome fields are excluded from predictor allowlists. Actual ranks, replacement points, and pick-band outcomes are not predictors.

Split policy:

| Split | Target seasons |
|---|---|
| train | 2017-2023 |
| validation | 2024 |
| holdout | 2025 |

Leakage rule:

- `source_window_end_season < target_season`

## Standard Dry-Run Query Result

Dataset version:

- `bqml_v2_standard_training_dataset_v0`

Scope:

- `scoring_profile_id = 'standard'`
- QB/RB/WR/TE
- target seasons 2017-2025
- `league_type_id = 'redraft'`
- `roster_format_id = 'one_qb'`

BigQuery dry-run result:

| Query | Estimated bytes |
|---|---:|
| Standard training dataset | 1,201,855,586 |
| Standard coverage aggregation | 25,824,109 |

## Coverage And Missingness

Standard row counts:

| Split | Rows |
|---|---:|
| train | 32,452 |
| validation | 4,918 |
| holdout | 1,691 |

Position row counts:

| Position | Rows |
|---|---:|
| QB | 4,646 |
| RB | 9,969 |
| WR | 15,988 |
| TE | 8,458 |

Feature-family coverage:

| Family | Populated rows | Possible rows |
|---|---:|---:|
| Baseline | 39,033 | 39,061 |
| Opportunity | 39,061 | 39,061 |
| Ideal xFP | 38,321 | 39,061 |
| PBP xFP | 38,321 | 39,061 |
| First-down proxy | 38,321 | 39,061 |
| NGS | 32,436 | 39,061 |
| Role history | 38,650 | 39,061 |

Blocked and source-gap probe:

| Field group | Non-null rows | Decision |
|---|---:|---|
| `depth_chart_role_score_3yr` | 0 | Historical depth remains blocked. |
| `injury_risk_score_3yr` | 0 | Injury is present as a source gap, not required for Standard v2. |

## Checks Run

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract` | Pass, 13 tests |
| `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py` | Pass |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Pass |
| `git diff --check` | Pass with line-ending warnings for two existing Markdown docs |

No SQL validators were added, so `scripts/run_bigquery_validations.py --dry-run` was not run for this phase.

## Warnings

- Standard BQML v2 is contract-ready, not training-ready.
- Injury and historical depth coverage remain empty in the Standard probe.
- The Standard query dry-run estimate is about 1.20 GB. Cost should be accepted before a training phase.
- The worktree still has the long historical untracked validation backlog from earlier phases.
- `git diff --check` reported LF to CRLF warnings on the two modified Markdown files, with exit code 0.

## No-Change Confirmation

- No BQML models trained.
- No live rankings changed.
- No champion activated.
- No writes to `analytics_pigskin_rankings`.
- No writes to `analytics_pigskin_rankings_candidates`.
- No writes to `ranking_formula_champions`.
- No writes to `ranking_backtest_results`.
- No Gemini call.
- No Pigskin chat call.
- No Sleeper API call.
- No source ingest.
- No deployment.

## Next Recommended Phase

Phase 33.3: Standard-only BQML v2 training dataset dry run.

That phase should stay read-only unless the owner explicitly approves model training. It should start by checking whether the 1.20 GB dry-run cost is acceptable and whether injury/depth source gaps should remain excluded.
