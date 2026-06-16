# backtest_result_summary Contract

Migration: [bigquery/migrations/0020__create_backtest_framework.sql](../migrations/0020__create_backtest_framework.sql)

Helper: [src/backtesting.py](../../src/backtesting.py)

## Purpose

Aggregate backtest quality metrics for dashboard review and future show evidence packets.

## Grain

One row per summary group:

- `backtest_run_id`
- `model_run_id`
- projection context
- optional `position`
- optional `season`
- optional `week`

## Metrics

- `mae`: average absolute error.
- `rmse`: square root of average squared error.
- `mean_bias`: average projected points minus actual points.
- `rank_mae_overall`: average absolute overall-rank miss.
- `rank_mae_position`: average absolute position-rank miss.
- `spearman_proxy`: rank-distance proxy for correlation.
- `top_12_hit_rate`: share of projected top 12 that finished top 12.
- `top_24_hit_rate`: share of projected top 24 that finished top 24.
- `boom_precision`: share of projected boom outcomes that actually boomed.
- `bust_precision`: share of projected bust outcomes that actually busted.
- `range_calibration_rate`: share of actual outcomes inside projected floor to ceiling.

## Consumer Rules

UI views should prefer this table for high-level model quality. Player-level drilldowns should use `backtest_result_player_week`.
