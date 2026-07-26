# ranking_formula_candidates Contract

Migration SQL: [bigquery/migrations/0028__ranking_formula_backtest_foundation.sql](../migrations/0028__ranking_formula_backtest_foundation.sql)

## Purpose

Stores draft and reviewed deterministic ranking formula candidates by position. These rows define candidate formulas for backtesting. They are not Pigskin-visible and do not grant arbitrary SQL.

## Grain

One row per `candidate_id`.

## Required Fields

- `candidate_id`
- `formula_name`
- `formula_version`
- `position`
- `formula_json`
- `feature_allowlist_json`
- `target_definition_json`
- `source_requirements_json`
- `status`
- `created_at`

## Formula JSON Contract

`formula_json` must be JSON with:

- `version`
- `position`
- `score_expression`
- `features`
- `weights`
- `normalization`

The only supported score expression in the first skeleton is weighted linear scoring. No SQL strings, table names, Python code, or free-form executable expressions are allowed.

## Feature Rules

Allowed features are position-specific and must come from curated historical player/week marts or Pigskin packet outputs. Blocked metrics such as route share, YPRR, first-read share, true pressure, contact yards, and alignment are rejected unless the formula declares matching source availability flags and the runner confirms those flags are true.

## Runtime Rules

- Candidate writes require `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`.
- Streamlit request-time code must not write this table.
- Pigskin chat must not read or write this table directly.
