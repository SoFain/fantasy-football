# Phase 32.12 Opportunity Metrics Warehouse Report

Final decision: OPPORTUNITY METRICS IMPLEMENTED WITH WARNINGS

## Scope

Phase 32.12 added an additive opportunity and role metric layer for ranking research. It did not deploy, regenerate live rankings, activate champions, call Pigskin chat, call Gemini, run live Sleeper, or use the old Python full tournament result-row path.

## Phase 32.11 Checkpoint

Phase 32.11 was uncommitted at the start of this phase. Focused checks passed and the Phase 32.11 package was committed:

- Commit: `d90a766 phase 32.11 test constrained ensemble candidates`
- Checks: deployment safety, `compileall`, `tests.test_ranking_formula_backtests`

## Files Changed

- `bigquery/migrations/0031__ranking_opportunity_metrics.sql`
- `bigquery/validations/210_player_week_opportunity_metrics_exists.sql`
- `bigquery/validations/211_player_week_opportunity_metrics_grain.sql`
- `bigquery/validations/212_player_week_opportunity_metrics_ranges.sql`
- `bigquery/validations/213_ranking_feature_mart_opportunity_columns.sql`
- `bigquery/validations/214_ranking_feature_mart_opportunity_ranges.sql`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/validation/phase-32-12-opportunity-metrics-warehouse-report.md`
- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`

## Source Audit

Available source families:

- QB rushing leverage: carries, carry share, red-zone carries, inside-five carries.
- RB high-value opportunity: high-value touches, red-zone touches, target share, opportunity share.
- WR and TE role dominance: target share, air-yards share, WOPR, red-zone targets.
- Team environment: plays, EPA per play, neutral pass rate.
- Ceiling and bust flags: PPR fantasy point thresholds by position.

Unavailable or blocked:

- First-read share.
- True route share as a reliable derived feature.
- YPRR without true route source.
- End-zone targets.

Unavailable metrics are recorded in missing flags. They were not zero-filled as if they were real inputs.

## Migration

Migration `0031__ranking_opportunity_metrics.sql` was applied.

Initial apply attempt failed because BigQuery rejected multiple sequential table updates to `ranking_backtest_feature_mart`:

`Exceeded rate limits: too many table update operations for this table`

Fix applied:

- Converted the mart column additions to one `ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...` statement with multiple column clauses.
- Retried migration 0031 only.

Result:

- `player_week_opportunity_metrics` exists.
- `ranking_backtest_feature_mart` has the new opportunity columns.
- `scripts/run_bigquery_migrations.py --list-pending`: no pending migrations.

## Backfill

Opportunity metrics backfill:

- Season range: 2014-2025
- Row count: 70,356
- Season count: 12
- Season-week count: 257
- Run ID: `opportunity_metrics_2014_2025_20260705T062507Z`

Feature mart refresh:

| Target season | Row count |
| --- | ---: |
| 2017 | 18,164 |
| 2018 | 17,108 |
| 2019 | 17,572 |
| 2020 | 18,540 |
| 2021 | 19,796 |
| 2022 | 19,432 |
| 2023 | 19,196 |
| 2024 | 19,672 |
| 2025 | 6,764 |

Total refreshed feature-mart rows: 156,244

## Validation Results

Passed:

- `210_player_week_opportunity_metrics_exists.sql`
- `211_player_week_opportunity_metrics_grain.sql`
- `212_player_week_opportunity_metrics_ranges.sql`
- `213_ranking_feature_mart_opportunity_columns.sql`
- `214_ranking_feature_mart_opportunity_ranges.sql`

Feature placement check for 2025 PPR:

| Position | Rows | QB rushing non-null | RB HVO non-null | Receiving role non-null | Team environment non-null |
| --- | ---: | ---: | ---: | ---: | ---: |
| QB | 295 | 295 | 0 | 0 | 295 |
| RB | 366 | 0 | 366 | 0 | 366 |
| TE | 392 | 0 | 0 | 392 | 392 |
| WR | 638 | 0 | 0 | 638 | 638 |

## Diagnostic SQL-Native Smoke

The bounded diagnostic smoke used four draft-only opportunity candidates for 2025 PPR. It was read-only and summary-only.

- Estimated bytes processed: 2,835,595
- Candidate count: 4

| Candidate | Position | Sample size | Top-N hit rate | NDCG at K | Missing input rate | VOR captured rate |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `ranking_formula_qb_opportunity_diagnostic_v0_2026_001` | QB | 295 | 0.8333 | 0.8259 | 0.0 | 0.8346 |
| `ranking_formula_rb_opportunity_diagnostic_v0_2026_001` | RB | 366 | 1.0000 | 0.9041 | 0.0 | null |
| `ranking_formula_te_opportunity_diagnostic_v0_2026_001` | TE | 392 | 0.7778 | 0.7544 | 0.0 | 0.8522 |
| `ranking_formula_wr_opportunity_diagnostic_v0_2026_001` | WR | 638 | 0.8356 | 0.7931 | 0.0 | 0.8864 |

Warning: RB VOR captured rate returned null on the bounded 2025 PPR diagnostic slice, likely because the denominator was zero in the summary window. Hit rate and NDCG still returned usable signal.

## Local Checks

Passed:

- `scripts/check_deployment_safety.py`
- `py_compile app.py src/ranking_formula_backtests.py`
- `compileall -q src scripts`
- `tests.test_ranking_formula_backtests`: 87 tests
- `unittest discover tests`: 741 tests
- `run_bigquery_migrations.py --list-pending`: no pending migrations
- `run_bigquery_validations.py --dry-run`: 214 validation files discovered
- `run_bigquery_validations.py --run --pattern "210|211|212|213|214"`: 5 passed, 0 failed

## Production Impact

No production deployment occurred. No live ranking rows were regenerated. No champion rows were activated. No Pigskin tool exposure changed.

## Remaining Warnings

- True route share, first-read share, YPRR, and end-zone targets remain unavailable under approved sources.
- RB VOR captured rate needs a denominator review before using it as a primary comparison metric.
- Opportunity diagnostic candidates are not champion candidates. They are research probes only.

## Recommended Next Phase

Phase 32.13 should compare the opportunity diagnostics against the current SQL-native scorecard over multiple target seasons, then decide whether to add position-specific opportunity formulas to the official candidate set.
