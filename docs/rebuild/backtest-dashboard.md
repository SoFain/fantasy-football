# Backtest Dashboard

Phase 13.3 adds a default-off Streamlit dashboard for inspecting backtest output tables. It does not run backtests, mutate warehouse data, or read raw source tables.

## Feature Flag

`USE_BACKTEST_DASHBOARD=false` by default.

When the flag is false, the Streamlit tab list is unchanged. When the flag is true, a `Backtesting` tab is appended after Data Ops.

## Reader Module

Helper: [src/backtest_readers.py](../../src/backtest_readers.py)

Read-only tables:

- `backtest_runs`
- `backtest_result_summary`
- `backtest_result_player_week`
- `backtest_calibration_bins`

The helper uses parameterized queries, validates project and dataset identifiers, keeps table names in a closed allowlist, enforces row limits, and returns clean empty lists or `None` when no data is available.

## Streamlit View

The dashboard shows:

- latest backtest runs
- filters for horizon, scoring profile, league type, roster format, position, season, and week
- summary cards for sample size, MAE, RMSE, bias, rank error, top-24 hit rate, and calibration
- detailed summary rows
- player error rows with controlled sort options
- calibration bins
- model and backtest run identifiers
- source freshness snapshot id when present
- missing-data warnings from player error rows
- markdown summary export

## Cloud Run Job Behavior

The dashboard does not execute backtests directly.

If `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=true`, the dashboard can render a dry-run preview for the `run-backtests` Cloud Run Job. Actual triggering remains controlled by the existing Data Ops Cloud Run Jobs panel and still requires explicit trigger flags and confirmation.

## Rollback

Rollback is env-only:

1. Remove `USE_BACKTEST_DASHBOARD` or set it to `false`.
2. Restart or redeploy the Streamlit service.
3. Confirm the Backtesting tab is absent.

No migration rollback is required.

## Manual QA

Run locally with:

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

Then test:

1. With the flag unset, confirm the current tab list is unchanged.
2. Set `USE_BACKTEST_DASHBOARD=true`.
3. Confirm the Backtesting tab appears.
4. Confirm an empty backtest warehouse shows a clear empty state.
5. Confirm populated runs show summary cards, player errors, and calibration rows.
6. Confirm the markdown export contains MAE, RMSE, hit-rate, and calibration fields.
7. Confirm no run button executes a backtest from request-time Streamlit code.

## Validation

Dashboard validation SQL:

- [139_backtest_dashboard_latest_runs.sql](../../bigquery/validations/139_backtest_dashboard_latest_runs.sql)
- [140_backtest_dashboard_summary_available.sql](../../bigquery/validations/140_backtest_dashboard_summary_available.sql)
- [141_backtest_dashboard_no_raw_source_dependencies.sql](../../bigquery/validations/141_backtest_dashboard_no_raw_source_dependencies.sql)

Use:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern backtest_dashboard
```

Empty result tables are expected until backtests are materialized. The no-raw-source-dependency validation should return zero.
