# ranking_formula_champions Contract

Migration SQL: [bigquery/migrations/0028__ranking_formula_backtest_foundation.sql](../migrations/0028__ranking_formula_backtest_foundation.sql)

## Purpose

Stores owner-selected or automated champion formulas after backtest review.

## Grain

One row per `champion_id`.

Only one active champion per `formula_set_id` and `position` should exist.

## Required Fields

- `champion_id`
- `formula_set_id`
- `position`
- `candidate_id`
- `formula_version`
- `metric_name`
- `active`
- `selected_at`

## Runtime Rules

Champion rows are review artifacts. They do not expose ranking formulas to Pigskin by themselves.
