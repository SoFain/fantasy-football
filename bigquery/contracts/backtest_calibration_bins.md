# backtest_calibration_bins Contract

Migration: [bigquery/migrations/0020__create_backtest_framework.sql](../migrations/0020__create_backtest_framework.sql)

Helper: [src/backtesting.py](../../src/backtesting.py)

## Purpose

Calibration view of projected point buckets versus actual outcomes.

## Grain

One row per:

- `backtest_run_id`
- `model_run_id`
- projection context
- optional `position`
- `bin_name`

## Bins

V1 uses projected point buckets:

- `0_to_5`
- `5_to_10`
- `10_to_15`
- `15_to_20`
- `20_plus`

## Consumer Rules

This table supports calibration charts and model QA. It is not a player ranking table.
