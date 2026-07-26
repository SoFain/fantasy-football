# Phase 32.10 BigQuery ML Baseline Prototype Report

Date: 2026-07-04

Final decision: BQML BASELINES READY WITH WARNINGS

## Scope

Phase 32.10 preserved the accepted SQL-native tournament package, then prototyped bounded BigQuery ML baselines against `ranking_backtest_feature_mart`.

This phase did not deploy, regenerate live rankings, activate champion formulas, call Pigskin chat, call Gemini-backed ranking generation, call live Sleeper, run the old Python full tournament, write detail rows, or globally truncate any table.

## Part 0 Preservation

The accepted Phase 32.8 and Phase 32.9 SQL-native tournament package was committed before BQML work started.

Commit:

- `4fca644 phase 32.9 accept sql native tournament evidence`

Files included in that preservation commit:

- `docs/rebuild/ranking-algorithm-scorecard.md`
- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `bigquery/migrations/0030__ranking_backtest_feature_mart.sql`
- `docs/rebuild/validation/phase-32-7-ranking-backtest-feature-mart-report.md`
- `docs/rebuild/validation/phase-32-8-sql-native-tournament-engine-report.md`
- `docs/rebuild/validation/phase-32-9-sql-native-source-of-truth-report.md`

Pre-commit checks passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`

## Files Changed In Phase 32.10

- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-research-north-star.md`
- `docs/rebuild/validation/phase-32-10-bqml-baseline-prototype-report.md`

## Owner-Review Conclusion

The SQL-native tournament summary path remains the preferred tournament evidence source. Python tournament evidence is historical reference only.

Current Pigskin remains the live baseline. Simple projection remains a strong challenger but does not replace the baseline. No champion formula is active.

The next research direction is constrained ML or ensemble ingredients evaluated through the SQL-native path, not live ranking generation.

## BQML Training Dataset Design

Source:

- `ranking_backtest_feature_mart`

Chronological split:

- train: target seasons 2017 through 2023
- validation: target season 2024
- holdout: target season 2025

Training select dry-run bytes:

- each target training select: `38,145,652` bytes

Leakage guard:

- `source_window_end_season < target_season`
- no random split as primary evidence
- `data_split_method='NO_SPLIT'`
- target/outcome columns excluded from predictor list

Predictors include profile score, opportunity proxy, efficiency proxy, analytical grade proxy, role stability, recent usage and production proxies, trend fields, availability, volatility, and missing indicators. `scoring_profile_id` and `position` are included as categorical model inputs.

Excluded as predictors:

- `target_fantasy_points`
- `actual_position_rank`
- `actual_overall_rank`
- `value_over_replacement`
- top labels
- pick-band labels
- target-season outcome fields

## Models

Trained:

| Model | Type | Target |
|---|---|---|
| `ranking_bqml_linear_vor_v0` | `LINEAR_REGRESSION` | value over replacement |
| `ranking_bqml_linear_points_v0` | `LINEAR_REGRESSION` | target fantasy points |
| `ranking_bqml_logistic_elite_v0` | `LOGISTIC_REGRESSION` | position-specific elite finish |
| `ranking_bqml_boosted_tree_vor_v0` | `BOOSTED_TREE_REGRESSOR` | value over replacement |

Skipped:

- `ranking_bqml_random_forest_vor_v0`

Skip reason: random forest was left disabled by default for cost/runtime control.

Model creation job metadata warning: the local command that submitted model creation exceeded the command timeout. BigQuery model listing confirmed all four bounded models exist. Region-level job history query was blocked by IAM with missing `bigquery.jobs.listAll`, so exact creation job IDs and slot metrics were not available from job history.

## Prediction Output

BQML predictions were generated read-only through `ML.PREDICT`.

Candidate-style output fields:

- `candidate_id`
- `candidate_family`
- `model_name`
- `target_season`
- `target_week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `position`
- `player_id_internal`
- `player_name`
- `team`
- `actual_points`
- `actual_position_rank`
- `actual_overall_rank`
- `value_over_replacement`
- `predicted_score`

Prediction summary job:

- job ID: `e2a9c84a-18bb-4153-92d9-e57e86c93e78`
- dry-run bytes: `9,143,556`
- bytes processed: `9,143,556`
- slot millis: `137,712`
- rows written: `0`

## SQL-Native Evaluation Results

The BQML candidates were evaluated with SQL-native summary logic only. No old Python tournament result-row builder was used.

BQML results by target season:

| Family | Season | Top-N | Captured points | VOR captured | Rank corr | High-confidence | Overall pairwise | NDCG@K | Tier accuracy | Bust rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BQML logistic elite | 2024 | 0.5165 | 0.7073 | 0.5888 | 0.5332 | 0.7445 | 0.5096 | 0.6501 | 0.3998 | 0.1641 |
| BQML linear VOR | 2024 | 0.5145 | 0.7022 | 0.5801 | 0.5248 | n/a | n/a | 0.6461 | 0.4025 | 0.1685 |
| BQML linear points | 2024 | 0.5120 | 0.7035 | 0.5839 | 0.5399 | 0.9245 | 0.6914 | 0.6471 | 0.4098 | 0.1671 |
| BQML boosted tree VOR | 2024 | 0.4993 | 0.6895 | 0.5697 | 0.5149 | n/a | n/a | 0.6267 | 0.4048 | 0.1798 |
| BQML logistic elite | 2025 | 0.8558 | 0.9030 | 0.8555 | 0.5619 | 0.7492 | 0.7715 | 0.7814 | 0.7060 | 0.0012 |
| BQML boosted tree VOR | 2025 | 0.8532 | 0.8976 | 0.8480 | 0.5532 | n/a | n/a | 0.7725 | 0.7036 | 0.0012 |
| BQML linear points | 2025 | 0.8510 | 0.8973 | 0.8461 | 0.5451 | 0.8927 | 0.9441 | 0.7709 | 0.6990 | 0.0012 |
| BQML linear VOR | 2025 | 0.8504 | 0.8985 | 0.8460 | 0.5378 | n/a | n/a | 0.7703 | 0.6951 | 0.0012 |

Aggregate 2024-2025 BQML results:

| Family | Top-N | Captured points | VOR captured | Rank corr | High-confidence | Overall pairwise | NDCG@K | Tier accuracy | Bust rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BQML logistic elite | 0.6861 | 0.8051 | 0.7031 | 0.5476 | 0.7468 | 0.6405 | 0.7157 | 0.5529 | 0.0826 |
| BQML linear VOR | 0.6824 | 0.8003 | 0.6941 | 0.5313 | n/a | n/a | 0.7082 | 0.5488 | 0.0849 |
| BQML linear points | 0.6815 | 0.8004 | 0.6963 | 0.5425 | 0.9098 | 0.8178 | 0.7090 | 0.5544 | 0.0841 |
| BQML boosted tree VOR | 0.6762 | 0.7936 | 0.6890 | 0.5340 | n/a | n/a | 0.6996 | 0.5542 | 0.0905 |

Same-window SQL-native baseline comparison:

| Family | Top-N | Captured points | VOR captured | Rank corr | High-confidence | Overall pairwise | NDCG@K | Tier accuracy | Bust rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| scarcity adjusted draft value | 0.6811 | 0.7967 | 0.6965 | 0.6233 | 0.7373 | 0.7484 | 0.6896 | 0.5385 | 0.0846 |
| simple projection points | 0.6803 | 0.7969 | 0.6932 | 0.6261 | 0.7407 | 0.7441 | 0.7163 | 0.5578 | 0.0887 |
| current Pigskin baseline | 0.6755 | 0.7929 | 0.6800 | 0.6219 | 0.7540 | 0.7621 | 0.7086 | 0.5528 | 0.0891 |

## Decision Rules

No BQML model is activated.

The strongest BQML result is `bqml_logistic_elite`. It beats current Pigskin on top-N, captured points, VOR captured, NDCG, tier accuracy, and bust rate over 2024-2025. The top-N edge is about 1.06 percentage points, which is below the 1.5 percentage point owner-review threshold. It also trails current Pigskin on overall pairwise draft win rate.

`bqml_linear_points` is worth more review because it has strong high-confidence and overall pairwise metrics, but it does not clearly separate on top-N.

Conclusion: BQML baselines are useful owner-review challengers. They are not champion candidates yet.

## Scorecard And Research Note

Updated:

- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-research-north-star.md`

The research note records the accepted direction: draft prediction is a top-heavy, scarcity-aware ranking problem. Raw point projection is not enough. The likely future winner is a constrained ensemble rather than one standalone formula.

## Tests And Checks

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\ranking_formula_backtests.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`
- `git diff --check`

Results:

- focused ranking tests: 77 passed
- full test discovery: 731 passed
- pending migrations: none
- validation dry-run: 209 validation files discovered

Added or covered tests for:

- BQML training SQL excludes outcome predictors
- chronological season split
- no random primary split
- prediction output maps to candidate-style rows
- logistic probability SQL uses BigQuery's `prob` field
- prediction identity columns are not duplicated
- BQML summary SQL is read-only
- no champion activation references
- no live ranking table references in BQML summary SQL
- random forest skipped by default

## Live Ranking And Champion Confirmation

Read-only checks:

- `analytics_pigskin_rankings` active rows by scoring profile:
  - `ppr`: 285
  - `half_ppr`: 285
  - `standard`: 285
  - `gng_keeper`: 285
- active final ranking total: 1,140
- `ranking_formula_champions`: 0 rows

No live rankings were regenerated. No champion was activated.

## Warnings

- Four BQML model objects were created as versioned prototypes. This is expected for the phase, but exact creation job IDs were not available because the local submission command timed out and job-history access is blocked by IAM.
- The boosted-tree model finished after the local command timeout. It was included in evaluation after model listing confirmed it existed.
- `bqml_linear_vor` and `bqml_boosted_tree_vor` produced no high-confidence pairwise metric under the current 10-point predicted-score delta rule. Their score ranges appear too compressed for that metric.
- BQML logistic elite is promising on top-N and VOR, but its overall pairwise rate is weaker than current Pigskin.
- The worktree still contains the existing historical validation backlog as untracked files. Those were not touched or staged.

## Recommended Next Phase

Recommended: Phase 32.11 - Ensemble candidate prototype.

Scope suggestion:

- keep SQL-native evaluation as source of truth
- test constrained blends of current Pigskin, simple projection, scarcity-adjusted draft value, BQML logistic elite, and BQML linear points
- keep writes summary-only unless owner explicitly requests official snapshot detail rows
- do not activate a champion without a separate owner-approved phase
