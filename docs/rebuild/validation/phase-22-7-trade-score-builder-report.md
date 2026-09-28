# Phase 22.7 Trade Score Builder Report

Date: 2026-06-17

## Scope

Implemented the deterministic Trade Analyzer score v0 builder behind an explicit no-write default.

No deployment, migration application, Cloud Run Job trigger, LLM call, scrape, Firebase artifact, or production feature flag change was performed.

## Files Created

- `src/trade_player_scores.py`
- `tests/test_trade_player_scores.py`

## Builder Summary

The new builder calculates deterministic rows for `trade_player_scores` using curated marts and compatibility views only:

- `compat_trade_assets_current`
- `compat_trade_player_history`
- `analytics_player_weekly_truth`
- `analytics_player_fantasy_points_by_profile`
- `analytics_fraud_watch`
- `projection_rankings_current`

The production builder module does not reference raw/source table names and does not import LLM clients.

## CLI

Supported command shape:

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 6 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --dry-run
```

Write mode requires an explicit non-dry-run flag:

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 6 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --write
```

Default behavior remains non-mutating if `--write` is omitted.

## Formula

Implemented v0 formula:

```text
base_score =
  0.40 * market_score
  + 0.20 * projection_score
  + 0.15 * recent_production_score
  + 0.10 * role_usage_score
  + 0.10 * positional_scarcity_score
  + 0.05 * efficiency_score

risk_adjustment = -10 * normalized_risk_score
confidence_multiplier = clamp(confidence_score / 100, 0.70, 1.00)
trade_score = clamp((base_score + risk_adjustment) * confidence_multiplier, 0, 100)
```

## Write Behavior

The write path stages rows into a unique temporary table with `WRITE_EMPTY`, then merges into `trade_player_scores` on the deterministic grain:

- `model_version`
- `season`
- `week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `player_id`

This supports idempotent updates without destructive changes to the target table.

## Tests Added

`tests/test_trade_player_scores.py` covers:

- documented formula weights
- confidence multiplier clamps
- output score bounds
- required JSON payloads
- missing-data flags and confidence penalty
- roster-format scarcity behavior
- safe source objects only in generated SQL
- parameterized query construction
- dry-run no-write behavior
- explicit write guard
- merge write path
- no LLM client imports

## Validation Results

Passed:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Additional non-mutating migration checks:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
```

Result:

- Dry-run lists discovered migration files through `0025`.
- Ledger-aware `--list-pending` reports `0025: trade analyzer score v0`.
- Migration `0025` was not applied.

## Warnings

- `trade_player_scores`, `trade_player_scores_current`, and `compat_trade_player_scores_current` are still pending live creation until additive migration `0025` is explicitly reviewed and applied.
- No live score materialization was run in this phase.
- The builder is ready for dry-run planning now, but write mode should wait until migration `0025` exists in BigQuery.

## Final Decision

TRADE SCORE BUILDER READY WITH WARNINGS
