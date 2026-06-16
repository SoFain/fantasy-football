# claim_source_scorecards Contract

Migration: [bigquery/migrations/0023__create_claim_grading.sql](../migrations/0023__create_claim_grading.sql)

Helper: [src/claim_grading.py](../../src/claim_grading.py)

## Purpose

Source-level accountability rollups for a claim-grading run.

## Grain

One row per `claim_grading_run_id`, `source_id`, season, and week scope.

## Metrics

- `claim_count`
- `graded_count`
- `average_claim_accuracy`
- `average_meatbag_delta`
- `pigskin_win_rate`
- `market_win_rate`
- verdict counts for `good_take`, `wrong`, `fraud`, and `galaxy_brain`

## Rules

- Scorecards are derived from `claim_grades`.
- `pigskin_win_rate` is calculated only where both Pigskin and claim scores exist.
- `market_win_rate` is calculated only where both market and claim scores exist.
- `scorecard_json` can hold small explainability fields and verdict counts.

## UI and LLM Safety

Safe for future dashboard scoreboards. Pigskin should consume a curated packet or summary view, not direct table access.
