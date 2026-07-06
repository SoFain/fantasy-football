# Phase 32.28: BQML Retrain With Direct NGS Features

Final decision: **BQML NGS MODELS READY WITH WARNINGS**

## Scope

Phase 32.28 retrained bounded BigQuery ML challenger models after Phase 32.27 added direct nflverse NGS fields to `ranking_backtest_feature_mart`.

This was not a live ranking phase. No deployment, live ranking generation, champion activation, detail-row write, Sleeper call, Pigskin chat call, Gemini call, source ingest, or materialization outside the bounded BQML summary path occurred.

## Files Changed

| File | Change |
|---|---|
| `src/ranking_formula_backtests.py` | Added `bqml_ngs_model_specs` for bounded direct-NGS BQML challengers. |
| `tests/test_ranking_formula_backtests.py` | Added focused tests for NGS spec coverage, leakage guard SQL, and summary-only write SQL. |
| `docs/rebuild/ranking-algorithm-scorecard.md` | Added Phase 32.28 BQML NGS scorecard section. |
| `docs/rebuild/ranking-opportunity-metrics-matrix.md` | Added Phase 32.28 direct NGS BQML feature read. |
| `docs/rebuild/validation/phase-32-28-bqml-ngs-retrain-report.md` | This report. |

Commit hash: pending until the Phase 32.28 package commit is created.

## Git State

Before Phase 32.28 packaging:

- Tracked modifications were limited to `src/ranking_formula_backtests.py`, `tests/test_ranking_formula_backtests.py`, and Phase 32.28 docs after this report was created.
- The large historical validation backlog under `docs/rebuild/validation/phase-17-*` through older phase reports remained untracked and was not staged.

## NGS Feature Coverage

Read-only coverage from `ranking_backtest_feature_mart`, filtered to `source_window_end_season < target_season`.

### 2024 and 2025 PPR Detail

| Target season | Position | Records | QB passing NGS | RB rushing NGS | RB RYOE | RB box | Receiving NGS | YAC OE | Separation | Catch OE |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024 | QB | 573 | 570 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2024 | RB | 1,276 | 0 | 1,060 | 1,060 | 1,060 | 0 | 0 | 0 | 0 |
| 2024 | TE | 1,087 | 0 | 0 | 0 | 0 | 816 | 816 | 816 | 0 |
| 2024 | WR | 1,982 | 0 | 0 | 0 | 0 | 1,755 | 1,751 | 1,755 | 0 |
| 2025 | QB | 295 | 292 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2025 | RB | 366 | 0 | 269 | 269 | 269 | 0 | 0 | 0 | 0 |
| 2025 | TE | 392 | 0 | 0 | 0 | 0 | 341 | 341 | 341 | 0 |
| 2025 | WR | 638 | 0 | 0 | 0 | 0 | 594 | 594 | 594 | 0 |

### 2017-2025 PPR Aggregate

| Position | Records | QB passing NGS | RB rushing NGS | RB RYOE | RB box | Receiving NGS | YAC OE | Separation | Catch OE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| QB | 4,646 | 4,474 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RB | 9,969 | 0 | 8,066 | 6,182 | 8,066 | 0 | 0 | 0 | 0 |
| TE | 8,458 | 0 | 0 | 0 | 0 | 6,082 | 6,082 | 6,082 | 0 |
| WR | 15,988 | 0 | 0 | 0 | 0 | 13,814 | 13,810 | 13,814 | 0 |

Unsupported field status:

- `ngs_catch_over_expected_score_3yr` has zero populated records.
- Public nflverse receiving did not provide expected catch or catch-over-expected in the source lane used here.
- The field stays null and missing-flagged. It was not fabricated or zero-filled.

## Leakage Guard

Confirmed:

- `leaked_feature_count`: 0
- `sleeper_source_count`: 0
- BQML training SQL includes `source_window_end_season < target_season`.
- BQML training SQL uses `target_season BETWEEN 2017 AND 2023`.
- 2025 is holdout only. It was not used for training or tuning.
- No target-season outcomes are selected as predictors.
- No Sleeper current context is selected as a historical backtest input.

Excluded target/outcome columns from predictor select:

- `target_fantasy_points`
- `actual_position_rank`
- `actual_overall_rank`
- `value_over_replacement`

Those columns are used only as labels or evaluator targets.

## Split Policy

| Slice | Target seasons | Use |
|---|---:|---|
| Train | 2017-2023 | BQML model training |
| Validation | 2024 | Model comparison |
| Holdout | 2025 | Final evidence only |

No random split was used as primary evidence. BigQuery ML models were created with `data_split_method='NO_SPLIT'`.

## Models Trained

| Model | Type | Target | Job ID | Bytes processed | Slot ms | Runtime |
|---|---|---|---|---:|---:|---:|
| `ranking_bqml_ngs_logistic_elite_v1` | `LOGISTIC_REG` | `elite_label` | `901b653b-bc62-4899-9b12-d361bc998bda` | 71,101,044 | 517,887 | 110s |
| `ranking_bqml_ngs_linear_points_v1` | `LINEAR_REG` | `target_fantasy_points` | `5e6d9721-a1a6-485a-8d14-2d6ae65a292a` | 71,101,044 | 10,480,519 | 128s |
| `ranking_bqml_ngs_linear_vor_v1` | `LINEAR_REG` | `value_over_replacement` | `0a0a2a57-6b0e-454d-81c1-0cf4d826ff22` | 71,101,044 | 13,771,942 | 144s |
| `ranking_bqml_ngs_boosted_tree_vor_v1` | `BOOSTED_TREE_REGRESSOR` | `value_over_replacement` | `b6bb36f1-a904-4e31-9ab9-3a29df0fd067` | 14,025,169,231 | 7,613,830 | 341s |

Models skipped:

- `ranking_bqml_ngs_boosted_tree_elite_v1`: optional and skipped to keep cost bounded.
- Random forest, DNN, AutoML, remote models, and hyperparameter tuning: skipped by prompt restriction.

## SQL-Native Dry Run

Dry-run stats:

- Model count: 4
- Candidate count: 4
- Expected run rows: 8
- Expected summary rows: 128
- Expected detail rows: 0
- Summary estimated bytes: 15,864,005

Prediction output was candidate-style and generated through `ML.PREDICT`, with `candidate_id`, `candidate_family`, `model_name`, target slice, player identity, `predicted_score`, and SQL window ranks inside the evaluator.

## Controlled Summary-Only Write

Gate used:

- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`
- Gate was set only for the write command process and was removed immediately afterward.
- Post-write check showed `ALLOW_RANKING_FORMULA_BACKTEST_WRITE` unset.

Write result:

- Job ID: `8be054c6-8880-4d68-a4f7-24e12d5c44bd`
- Summary only: true
- Detail rows written: 0

Persisted row counts:

| Object | Row count |
|---|---:|
| `ranking_backtest_runs` for `ranking_backtest_sql_native_bqml_ngs_v1_%` | 8 |
| `ranking_backtest_candidate_summaries` for `ranking_backtest_sql_native_bqml_ngs_v1_%` | 128 |

No rows were written to:

- `ranking_backtest_results`
- `ranking_formula_champions`
- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_candidates`

## 2024 Validation Results

PPR aggregate, averaged across QB/RB/WR/TE position summaries.

| Candidate | Top-N | Captured points | VOR captured | NDCG@K | Bust rate | High-confidence pairwise | Overall pairwise |
|---|---:|---:|---:|---:|---:|---:|---:|
| `ranking_bqml_ngs_logistic_elite_v1` | 0.5376 | 0.7364 | 0.6008 | 0.6825 | 0.1626 | 0.7521 | 0.5198 |
| `ranking_bqml_ngs_linear_points_v1` | 0.5324 | 0.7297 | 0.5927 | 0.6785 | 0.1742 | 0.9026 | 0.6097 |
| `ranking_bqml_ngs_linear_vor_v1` | 0.5313 | 0.7312 | 0.5921 | 0.6859 | 0.1725 | 0.9853 | n/a |
| `ranking_bqml_ngs_boosted_tree_vor_v1` | 0.5295 | 0.7288 | 0.5892 | 0.6751 | 0.1638 | n/a | n/a |

2024 read:

- NGS logistic was effectively flat versus enriched logistic.
- NGS linear points underperformed enriched linear points on captured points, VOR captured, NDCG, and overall pairwise.
- NGS boosted-tree VOR underperformed enriched boosted-tree VOR on the validation slice.

## 2025 Holdout Results

PPR aggregate, averaged across QB/RB/WR/TE position summaries.

| Candidate | Top-N | Captured points | VOR captured | NDCG@K | Bust rate | High-confidence pairwise | Overall pairwise |
|---|---:|---:|---:|---:|---:|---:|---:|
| `ranking_bqml_ngs_logistic_elite_v1` | 0.8576 | 0.9071 | 0.8592 | 0.7990 | 0.0012 | 0.7430 | 0.7655 |
| `ranking_bqml_ngs_linear_points_v1` | 0.8565 | 0.9081 | 0.8607 | 0.7971 | 0.0012 | 0.8997 | 0.9314 |
| `ranking_bqml_ngs_linear_vor_v1` | 0.8449 | 0.8954 | 0.8386 | 0.7873 | 0.0012 | n/a | n/a |
| `ranking_bqml_ngs_boosted_tree_vor_v1` | 0.8588 | 0.9076 | 0.8618 | 0.8003 | 0.0012 | n/a | n/a |

2025 holdout read:

- Boosted-tree VOR improved against enriched boosted-tree VOR on top-N, captured points, VOR captured, and NDCG.
- Logistic elite had tiny gains against enriched logistic.
- Linear points did not materially improve against enriched linear points.
- Linear VOR worsened.

## Comparison Against Phase 32.24 Enriched BQML

| Pair | 2024 read | 2025 read | Decision |
|---|---|---|---|
| NGS logistic vs enriched logistic | Flat | Slightly better | Owner-review only. Not enough lift. |
| NGS linear points vs enriched linear points | Worse | Mostly flat or slightly worse except overall pairwise | Keep enriched linear points as the stronger board-ordering lane. |
| NGS linear VOR vs enriched linear VOR | Mixed but mostly weaker | Weaker | Do not promote. |
| NGS boosted-tree VOR vs enriched boosted-tree VOR | Weaker | Better | Interesting nonlinear NGS interaction check, not stable enough for champion use. |

## Comparison Against Current Pigskin

Current Pigskin remains the live baseline.

Persisted current Pigskin summary rows do not match the exact same historical evaluation shape as the new BQML NGS rows, so this report does not treat that comparison as champion-selection proof. Directionally, the 2025-like current Pigskin and simple projection lanes remain strong on captured points and top-N. No BQML NGS model clears the bar for replacing them.

## NGS Feature Signal Summary

Feature inspection:

- `ML.FEATURE_IMPORTANCE` for `ranking_bqml_ngs_boosted_tree_vor_v1` surfaced `ngs_rushing_efficiency_score_3yr` with positive importance alongside `high_value_rush_xfp_score_3yr`, `availability_rate_3yr`, and `profile_points_score`.
- `ngs_rush_yards_over_expected_score_3yr` also appeared in boosted-tree VOR feature importance.
- Linear models were dominated by missingness indicators and existing opportunity/profile fields. That makes linear NGS reads weaker.
- Missing indicators for receiving NGS fields showed up in linear models, so owner-facing comparisons must show missingness and not overstate direct receiving impact.

Position read:

- RB: strongest direct NGS component signal, especially rushing efficiency.
- WR: direct receiving NGS is real, but the retrain did not remove WR movement risk.
- TE: direct receiving NGS is useful explainability context, not a champion path.
- QB: coverage is strong, but the retrain did not create a clear QB-specific promotion.

## Movement/Risk Summary

Full owner-review movement boards were not generated because the NGS BQML models did not materially improve enough over Phase 32.24 enriched BQML or the current Pigskin baseline.

Risk notes:

- WR movement remains the biggest review risk.
- Boosted-tree VOR had the best 2025 NGS lift but failed the 2024 validation stability check.
- Missing NGS indicators materially affect linear model behavior.

## Tests and Checks

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_backtest
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_formula
```

Results:

- Safety checker: pass.
- `app.py` compile: pass.
- `src` and `scripts` compileall: pass.
- Focused ranking tests: 114 tests passed.
- Pending migrations: none.
- Validation dry-run: pass.
- `ranking_backtest` validations: 3 passed, 0 failed.
- `ranking_formula` validations: 6 passed, 0 failed.

PowerShell displayed `NativeCommandError` around unittest stderr output, but the command exit code was 0 and unittest reported `OK`.

## Scorecard and Matrix Updates

Updated:

- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

Summary:

- Direct NGS is now a real BQML feature lane.
- RB rushing NGS is the clearest additive component signal.
- WR and TE receiving NGS remain useful explainability features but do not solve movement risk alone.
- Expected catch and catch-over-expected remain unsupported and flagged.
- Current Pigskin remains the live baseline.

## Confirmations

- No live ranking change.
- No champion activation.
- No detail rows written.
- No deployment.
- No source ingest.
- No materialization outside summary-only BQML evidence.
- No Sleeper API call.
- No Pigskin chat call.
- No Gemini or LLM call.
- No old Python full tournament path.
- No global truncate.

## Remaining Warnings

- `ngs_catch_over_expected_score_3yr` is present as a nullable contract field but has no public nflverse source values in this lane.
- BQML NGS linear models lean too much on missingness indicators to be treated as clean NGS feature evidence.
- Boosted-tree VOR consumed roughly 14.0 GB for training, much higher than the linear/logistic jobs.
- Persisted current Pigskin comparison rows are not the same exact evaluation shape as the new NGS BQML summary rows.

## Recommended Next Phase

Recommended next phase: **Phase 32.29 - Hold current Pigskin baseline and prepare owner-review-only NGS movement examples if requested.**

Alternate owner path:

- Phase 32.29 - Formula comparison dashboard in app, read-only.
- Phase 32.29 - Generate BQML NGS candidate rankings for owner review only, if the owner wants player-level inspection despite the weak aggregate lift.
