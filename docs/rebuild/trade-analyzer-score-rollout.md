# Trade Analyzer Score Rollout

## Purpose

This document tracks the rollout path for the deterministic Trade Analyzer score v0 layer.

The score layer is warehouse-first and default-off. Phase 22.6 adds contracts, additive DDL, view definitions, and validation SQL only. It does not compute scores, wire Streamlit, expose Pigskin tools, deploy, apply migrations, or change production flags.

## Objects

| Object | Type | Purpose |
| --- | --- | --- |
| `trade_player_scores` | output table | Versioned deterministic score rows by player, scoring context, and model version |
| `trade_player_scores_current` | current view | Latest score row per player and scoring context |
| `compat_trade_player_scores_current` | compatibility view | Safe future Streamlit and Pigskin-visible read surface |

Migration:

- `bigquery/migrations/0025__trade_analyzer_score_v0.sql`

Contracts:

- `bigquery/contracts/trade_player_scores.md`
- `bigquery/contracts/trade_player_scores_current.md`
- `bigquery/contracts/compat_trade_player_scores_current.md`

Views:

- `bigquery/views/trade_player_scores_current.sql`
- `bigquery/views/compat_trade_player_scores_current.sql`

## Builder Expectations

A future builder should:

- run outside request-time Streamlit;
- support dry-run and bounded materialization;
- write one row per `model_version`, `season`, `week`, `scoring_profile_id`, `league_type_id`, `roster_format_id`, and `player_id`;
- emit `source_freshness_json`, `missing_flags_json`, and `component_json`;
- keep component scores in the `0` to `100` range;
- leave missing inputs flagged rather than fabricated;
- read curated marts, projection outputs, compatibility views, packet tables, and backtest outputs only.

Allowed source families for a builder include:

- `compat_trade_assets_current`
- `compat_trade_player_history`
- `projection_rankings_current`
- `projections_player_weekly`
- `projections_player_ros`
- `projections_player_dynasty`
- `analytics_player_fantasy_points_by_profile`
- `analytics_player_weekly_truth`
- `analytics_fraud_watch`
- `fraud_watch_packets`
- `backtest_result_summary`
- `backtest_result_player_week`

Forbidden UI and Pigskin-visible source families include:

- `weekly_metrics`
- `play_by_play`
- `market_values`
- raw NGS, FTN, snap, injury, schedule, roster, and Sleeper source tables
- arbitrary SQL tools

## Feature Flags

Future runtime wiring must remain default off:

| Flag | Required default | Purpose |
| --- | --- | --- |
| `USE_TRADE_ANALYZER_SCORE_V0` | `false` | Show deterministic score widgets in Trade Lab |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `false` | Route score reads through `compat_trade_player_scores_current` |

Existing flags remain unchanged:

- `USE_COMPAT_TRADE_ASSETS=false`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false` in production

## Staging Rollout Plan

1. Apply the additive migration only after operator review.
2. Build a dry-run score materializer.
3. Materialize a small bounded score run using real 2025 data.
4. Run the `trade_player_scores` validations.
5. Add a read helper that queries only `compat_trade_player_scores_current`.
6. Wire the Trade Lab score display behind `USE_TRADE_ANALYZER_SCORE_V0=false`.
7. Enable only in staging after validation and browser QA.
8. Confirm the legacy value-only Trade Lab path still works when flags are off.

## Production Rules

- Production remains all-risk-flags-off until separately authorized.
- Do not enable `USE_TRADE_ANALYZER_SCORE_V0` in production during the initial contract rollout.
- Do not enable `USE_COMPAT_TRADE_PLAYER_SCORE` in production during the initial contract rollout.
- Do not trigger materialization from Streamlit.
- Do not expose raw/source table names to Pigskin.
- Do not compute deterministic scores with an LLM.

## Validation Pattern

Validation SQL:

- `150_trade_player_scores_grain.sql`
- `151_trade_player_scores_trade_score_range.sql`
- `152_trade_player_scores_component_score_range.sql`
- `153_trade_player_scores_confidence_range.sql`
- `154_trade_player_scores_required_json_fields.sql`
- `155_trade_player_scores_missing_flags_exist.sql`
- `156_trade_player_scores_source_freshness_exists.sql`
- `157_trade_player_scores_current_grain.sql`
- `158_compat_trade_player_scores_current_exists.sql`
- `159_compat_trade_player_scores_no_raw_source_dependencies.sql`
- `160_trade_player_scores_identity_coverage.sql`

Run examples:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores
```

Do not run the live validation pattern until migration `0025__trade_analyzer_score_v0.sql` has been applied with operator approval.

