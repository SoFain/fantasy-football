# Backtesting V1

This document defines the first projection-evaluation framework for AI vs. Meatbags.

## Status

The framework is standalone in [src/backtesting.py](../../src/backtesting.py). It does not change Streamlit runtime behavior and does not call an LLM.

## Phase 14.2 Seed Status

Report: [Phase 14.2 Backtest Seed Report](validation/phase-14-2-backtest-seed-report.md)

A bounded seed backtest now exists for `weekly`, `2025` week `1`, `ppr`, `redraft`, and `one_qb`.

Seeded identifiers:

- `model_run_id = weekly_projection-2025-1-20260616T114422Z-a25a92c1`
- `backtest_run_id = backtest-weekly-2025-2025-20260616T114527Z-2093e839`

Seeded output:

- `backtest_runs = 1`
- `backtest_result_player_week = 25`
- `backtest_result_summary = 6`
- `backtest_calibration_bins = 16`

One failed partial projection attempt remains temporarily visible under `weekly_projection-2025-1-20260616T113848Z-f07a0ccb`. It should be cleaned up with targeted DML after BigQuery releases those rows from the streaming buffer.

## Outputs

- `backtest_runs`
- `backtest_result_player_week`
- `backtest_result_summary`
- `backtest_calibration_bins`

Migration: [bigquery/migrations/0020__create_backtest_framework.sql](../../bigquery/migrations/0020__create_backtest_framework.sql)

## Phase 13.3 Dashboard Read Path

Read helper: [src/backtest_readers.py](../../src/backtest_readers.py)

Dashboard doc: [backtest-dashboard.md](backtest-dashboard.md)

The Streamlit dashboard is behind `USE_BACKTEST_DASHBOARD=false` by default. When enabled, it reads only the four backtest output tables listed above. It does not query `weekly_metrics`, raw play-by-play, NGS, FTN, snap, injury, roster, contract, market, or raw Sleeper tables.

The dashboard can show a dry-run Cloud Run Job command preview when `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=true`, but it does not execute backtests from request-time Streamlit code.

## Inputs

Allowed v1 inputs:

- `projections_player_weekly`
- `analytics_player_fantasy_points_by_profile`
- `model_runs` for optional model-run context

The backtester does not read raw `weekly_metrics`, `play_by_play`, NGS, FTN, snap, injury, or raw Sleeper tables.

## Metrics

- `absolute_error`: absolute value of projected points minus actual points.
- `squared_error`: squared point error.
- `mae`: average absolute error.
- `rmse`: square root of average squared error.
- `mean_bias`: average projected points minus actual points.
- `rank_error_overall`: absolute miss between projected and actual overall rank.
- `rank_error_position`: absolute miss between projected and actual position rank.
- `spearman_proxy`: simple rank-distance proxy. It is a QA signal, not a full statistical report.
- `top_12_hit_rate` and `top_24_hit_rate`: precision among projected top finishers.
- `boom_precision` and `bust_precision`: precision of projected threshold flags.
- `range_calibration_rate`: share of actuals inside projected floor to ceiling.

## No Future Leakage Rule

Backtesting v1 compares target `season` and `week` projection rows to the same target actuals. Projection generation is responsible for using only data available at projection time. The baseline projection engine already filters feature history to the requested target season and week.

Known limitation: if old projection rows were generated after the games were played, the framework can evaluate their target rows, but the run should be labeled as a retrospective backtest. True point-in-time testing needs archived pre-game projection runs.

## Scoring Profile Behavior

Actuals come from `analytics_player_fantasy_points_by_profile`, so `standard`, `half_ppr`, and `ppr` are evaluated independently. Custom Sleeper scoring can be added once that scoring profile has been materialized into the same actuals mart.

## Roster Format Behavior

`league_type_id` and `roster_format_id` are preserved on projection and result rows. Actual fantasy points are usually independent of roster format, but the projected ranks and context are not. Superflex and one-QB projection runs should be backtested separately.

## What Is Not Yet Compared

- ROS and dynasty projection outputs.
- Closing-line odds.
- Injury-adjusted availability.
- True pre-game point-in-time archived projections.

Market, ADP, and consensus baselines now have a first normalized layer in [market-consensus-baselines.md](market-consensus-baselines.md). Backtesting v1 can compare against `market_consensus_baseline_current` when a `market_source_id` is passed.

## CLI

```powershell
.\venv\Scripts\python.exe -m src.backtesting --model-run-id <id> --horizon weekly --season-start 2024 --season-end 2024 --scoring-profile ppr --league-type redraft --roster-format one_qb --dry-run
.\venv\Scripts\python.exe -m src.backtesting --horizon weekly --season-start 2023 --season-end 2024 --scoring-profile half_ppr --league-type redraft --roster-format superflex --dry-run
.\venv\Scripts\python.exe -m src.backtesting --horizon weekly --season-start 2024 --season-end 2024 --scoring-profile ppr --league-type redraft --roster-format one_qb --market-source-id manual_ecr --dry-run
```

Cloud Run Job dispatcher path:

```powershell
.\venv\Scripts\python.exe -m src.job_runner --job-name run-backtests --season-start 2023 --season-end 2024 --horizon weekly --scoring-profile half_ppr --league-type redraft --roster-format superflex --dry-run
```

## Future Baselines

Next evaluation layers should compare Pigskin projections to:

- market and ADP baselines
- consensus rankings
- prior-week rolling averages
- simple Vegas implied totals
- position replacement baselines
