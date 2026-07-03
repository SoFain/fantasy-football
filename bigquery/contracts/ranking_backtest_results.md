# ranking_backtest_results Contract

Migration SQL: [bigquery/migrations/0028__ranking_formula_backtest_foundation.sql](../migrations/0028__ranking_formula_backtest_foundation.sql)

## Purpose

Stores per-player, per-week ranking formula backtest outcomes.

## Grain

One row per:

- `backtest_run_id`
- `candidate_id`
- `season`
- `week`
- `player_id_internal`

## Required Fields

- `backtest_run_id`
- `candidate_id`
- `formula_version`
- `position`
- `season`
- `week`
- `player_id_internal`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `target_name`
- `feature_values_json`
- `result_json`
- `missing_flags_json`
- `source_freshness_json`
- `created_at`

## Score Rules

- `predicted_score` must be between `0` and `100` when present.
- `win_rate` must be between `0` and `1` when present.
- Missing inputs must be represented in `missing_flags_json`.
- Blocked metrics must not be silently treated as zero.

## Write Rules

Backtest result writes require `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` and use deterministic upsert semantics on the table grain.
