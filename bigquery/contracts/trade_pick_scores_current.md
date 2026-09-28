# trade_pick_scores_current Contract

Migration SQL: [bigquery/migrations/0026__trade_pick_score_v0.sql](../migrations/0026__trade_pick_score_v0.sql)

View SQL: [bigquery/views/trade_pick_scores_current.sql](../views/trade_pick_scores_current.sql)

## Purpose

Provides the current deterministic draft-pick score row per pick and scoring context. This view reads only `trade_pick_scores`. It is not a raw/source view and it is not a player-score view.

## Grain

One current row per:

- `source_pick_key`
- `pick_year`
- `pick_class`
- `pick_round`
- `pick_slot`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`

If more than one model version exists, the view selects the latest row by `created_at`, then `model_version`, then `score_run_id`.

## Fields

The view exposes all fields needed by downstream compatibility and QA:

- pick identity and parsed structure;
- scoring, league, and roster context;
- market inputs;
- component scores;
- `pick_score`, `confidence_score`, and `score_tier`;
- `component_json`, `missing_flags_json`, and `source_freshness_json`;
- `model_version`, `score_run_id`, `created_by`, and `created_at`.

## Source Rules

Allowed source:

- `trade_pick_scores`

Forbidden direct dependencies:

- `draft_picks`
- `college_player_stats`
- `rookie_scouting_metrics`
- raw/source tables

## Runtime Rules

This view is internal warehouse current-state plumbing. Streamlit and Pigskin-visible helpers should prefer `compat_trade_pick_scores_current`.

Production exposure remains default-off until a separate rollout approves pick-score UI behavior.

## Validation

Validation SQL:

- `172_trade_pick_scores_current_grain.sql`
- `174_compat_trade_pick_scores_no_raw_source_dependencies.sql`
