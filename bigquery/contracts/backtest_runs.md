# backtest_runs Contract

Migration: [bigquery/migrations/0020__create_backtest_framework.sql](../migrations/0020__create_backtest_framework.sql)

Helper: [src/backtesting.py](../../src/backtesting.py)

## Purpose

Run ledger for deterministic projection backtests.

Each persisted backtest has one `backtest_run_id`. A run may evaluate one `model_run_id` or multiple compatible projection runs when `model_run_id` is null.

## Grain

One row per `backtest_run_id`.

## Required Fields

- `backtest_run_id`
- `projection_horizon`
- `season_start`
- `season_end`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `status`
- `created_at`

## Status Values

- `running`
- `complete`
- `failed`

## Consumer Rules

- Result tables must reference `backtest_run_id`.
- The Streamlit UI should read summaries from result tables, not raw projections or raw actuals.
- Pigskin should consume future evidence packets, not this run ledger directly.
