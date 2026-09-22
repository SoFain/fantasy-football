# Phase 23.1B Trade Score Accuracy Fixes Report

Date: 2026-06-17

## Final Decision

`ACCURACY FIXES PASS`

The Phase 23.1A accuracy findings were fixed. `normalized_risk_score` is now consistently documented and validated as `0.00` to `1.00`, validation `152` no longer permits risk values up to `100`, the Trade Analyzer scoring spec now matches the implemented Phase 22 field names, and v0 score tier thresholds are documented.

Migration `0025` was not applied. No score rows were written. No deployment, materialization, ingestion, Cloud Run Job trigger, Scheduler job, LLM call, scrape, Firebase artifact creation, feature flag change, or commit was performed.

## Files Changed

| File | Change |
| --- | --- |
| `bigquery/contracts/trade_player_scores.md` | Corrected `normalized_risk_score` range to `0.00` through `1.00` and documented its formula role. |
| `bigquery/validations/152_trade_player_scores_component_score_range.sql` | Changed `normalized_risk_score` upper bound from `100` to `1`. |
| `tests/test_trade_player_scores.py` | Added regression coverage for validation `152` risk range handling. |
| `docs/rebuild/trade-analyzer-scoring-model-v0.md` | Aligned proposed contract names with the implementation, documented compatibility alias behavior, and added v0 score tier thresholds. |

## Risk Range Fix Summary

The contract now states:

- normal component scores use `0` to `100`;
- `market_score`, `projection_score`, `recent_production_score`, `role_usage_score`, `positional_scarcity_score`, `efficiency_score`, `fraud_score`, `confidence_score`, and `trade_score` use `0` to `100` where applicable;
- `normalized_risk_score` is the exception and uses `0.00` to `1.00`;
- `normalized_risk_score` feeds `risk_adjustment = -10 * normalized_risk_score`.

This matches the formula spec and `src/trade_player_scores.py`.

## Validation 152 Fix Summary

`bigquery/validations/152_trade_player_scores_component_score_range.sql` now checks:

```sql
OR normalized_risk_score IS NULL
OR normalized_risk_score < 0
OR normalized_risk_score > 1
```

Other component score checks remain `0` through `100`, including market, projection, recent production, role usage, positional scarcity, efficiency, and fraud score.

## Spec Field-Name Cleanup Summary

`docs/rebuild/trade-analyzer-scoring-model-v0.md` now uses implemented Phase 22 field names:

| Old wording | Updated wording |
| --- | --- |
| `score_version` | `model_version` |
| canonical `player_id_internal` | canonical `player_id`; `player_id_internal` is compatibility alias only |
| `risk_score` | `normalized_risk_score` and `fraud_score` |
| `component_summary_json` | `component_json` |
| `missing_data_flags` | `missing_flags_json` |
| `market_value` | `current_market_value` |

The spec now states that `bigquery/contracts/*` are the authoritative warehouse contracts.

## Score Tier Documentation Summary

The spec now documents current v0 thresholds:

| Tier | Threshold |
| --- | --- |
| `elite` | `trade_score >= 88` |
| `strong` | `trade_score >= 74` |
| `starter` | `trade_score >= 60` |
| `flex` | `trade_score >= 45` |
| `depth` | `trade_score >= 30` |
| `avoid` | otherwise |

The spec also notes that these are v0 heuristics and may be tuned after backtesting.

## Tests Added Or Updated

Added `TradePlayerScoreTests.test_component_validation_enforces_normalized_risk_zero_to_one`.

The test reads `bigquery/validations/152_trade_player_scores_component_score_range.sql` and verifies:

- `normalized_risk_score IS NULL` is checked;
- `normalized_risk_score < 0` is checked;
- `normalized_risk_score > 1` is checked;
- `normalized_risk_score > 100` is not present;
- other component scores still check upper bound `100`.

## Local Check Results

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | pass, 10 tests |
| `.\venv\Scripts\python.exe -m unittest tests.test_streamlit_compat_rollout` | pass, 10 tests |
| `.\venv\Scripts\python.exe -m unittest tests.test_pipeline_plan` | pass, 13 tests |
| `.\venv\Scripts\python.exe -m unittest tests.test_staging_ui_warning_fixes` | pass, 13 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 328 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run` | pass, local discovery only |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, pending `0025: trade analyzer score v0` |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass, 160 validation files discovered |

PowerShell displayed unittest progress output from stderr as `NativeCommandError` for targeted module runs. Each targeted command exited `0` and ended with `OK`.

## Migration 0025 Authorization Status

From an accuracy standpoint, migration `0025` is now reasonable to review for authorization.

Required before any migration apply:

- explicit operator authorization;
- review of the updated migration, contracts, views, and validation SQL;
- acknowledgement that `trade_score` live validations should not be run until the migration has been applied.

Required before any score write:

- migration `0025` applied successfully;
- explicit score materialization authorization;
- bounded season/week/profile command;
- dry-run first.

## Safety Confirmation

No prohibited action occurred:

- no deploy;
- no migration apply;
- no score write;
- no materialization;
- no ingestion;
- no Cloud Run Job trigger;
- no Scheduler job creation;
- no LLM call;
- no scrape;
- no Firebase artifact;
- no feature flag default change;
- no commit.

Final decision: `ACCURACY FIXES PASS`.
