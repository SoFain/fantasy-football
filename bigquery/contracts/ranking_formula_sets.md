# ranking_formula_sets Contract

Migration SQL: [bigquery/migrations/0028__ranking_formula_backtest_foundation.sql](../migrations/0028__ranking_formula_backtest_foundation.sql)

## Purpose

Groups position-specific formula candidates into a deployable ranking formula set.

## Grain

One row per `formula_set_id`.

## Required Fields

- `formula_set_id`
- `formula_set_name`
- `formula_set_version`
- `status`
- `created_at`

## Position Candidate Fields

- `qb_candidate_id`
- `rb_candidate_id`
- `wr_candidate_id`
- `te_candidate_id`

Formula sets may be incomplete while in `draft` status. Production use requires a separate future approval phase.
