# trade_player_scores_current Contract

Migration SQL: [bigquery/migrations/0025__trade_analyzer_score_v0.sql](../migrations/0025__trade_analyzer_score_v0.sql)

View SQL: [bigquery/views/trade_player_scores_current.sql](../views/trade_player_scores_current.sql)

Backing table: [trade_player_scores](trade_player_scores.md)

## Purpose

Exposes the latest deterministic Trade Analyzer score row for each player and scoring context.

## Grain

One row per:

- `player_id`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`

The view selects the latest row by:

1. `season DESC`
2. `week DESC`
3. `created_at DESC`
4. `model_version DESC`
5. `score_run_id DESC`

## Required Fields

The view preserves the score table fields needed by admin review, future helper modules, and downstream compatibility views:

- identity and context fields
- current market and projected multiyear values
- component scores
- final `trade_score`
- `score_tier`
- `source_freshness_json`
- `missing_flags_json`
- `component_json`
- model and run lineage

## Source Rules

This view reads only `trade_player_scores`. It must not reference raw/source tables.

## Runtime Rules

- This is an internal current view.
- Streamlit and Pigskin-visible helpers should prefer `compat_trade_player_scores_current`.
- The view is read-only.
- The view does not trigger score materialization.

## Validation

Validation SQL:

- `157_trade_player_scores_current_grain.sql`
- `159_compat_trade_player_scores_no_raw_source_dependencies.sql`

