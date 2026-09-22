# ranking_backtest_candidate_summaries Contract

Migration SQL: [bigquery/migrations/0028__ranking_formula_backtest_foundation.sql](../migrations/0028__ranking_formula_backtest_foundation.sql)

## Purpose

Stores candidate-level aggregate evidence so ranking formulas can be compared by position without manually scanning per-player/week rows.

## Grain

One row per:

- `backtest_run_id`
- `candidate_id`
- `position`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `target_name`

## Required Fields

- `backtest_run_id`
- `candidate_id`
- `formula_version`
- `position`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `target_name`
- `sample_size`
- `metric_json`
- `missing_flags_json`
- `source_freshness_json`
- `created_at`

## Metric Fields

- `pairwise_win_rate`
- `top_n_hit_rate`
- `rank_correlation`
- `mean_absolute_error`
- `regret_score`
- `actual_points_captured_rate`
- `missing_input_rate`

Rate metrics must be between `0` and `1` when present. Error and regret metrics must be non-negative when present.

## Write Rules

Summary writes require `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` and use deterministic upsert semantics on the table grain.
