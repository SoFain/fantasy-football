# Phase 13.1 Warehouse Activation Report

Final decision: GO WITH WARNINGS

## Purpose

Phase 13.1 confirmed Phase 12 warehouse activation remained clean, documented validation runner operations, and prepared the project for Phase 13.2 materialization. This standalone report preserves the Phase 13.1 status that was previously embedded in `docs/rebuild/validation/phase-12-validation-report.md`.

## Migration Activation State

Migrations `0020` through `0024` were already applied during the Phase 12 warehouse activation step:

| Migration | Result |
| --- | --- |
| `0020 create backtest framework` | Applied |
| `0021 create market consensus baselines` | Applied |
| `0022 create meatbag claim ledger` | Applied |
| `0023 create claim grading` | Applied |
| `0024 create content briefs` | Applied |

Post-apply ledger-aware pending check:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
```

Result:

```text
No pending migrations.
```

No migrations were applied during Phase 13.1 follow-up validation.

## Validation Status

Commands used the repo venv explicitly:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern backtest
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern claim
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
```

Validation patterns passed:

| Pattern | Result | Classification |
| --- | --- | --- |
| `backtest` | passed | GO |
| `market` | passed | GO WITH EXPECTED EMPTY-STATE WARNINGS |
| `claim` | passed | GO WITH EXPECTED EMPTY-STATE WARNINGS |
| `content_brief` | passed | GO |
| `cloud_run_job` | passed | GO |

The earlier market freshness warning was reclassified and resolved. `044_compat_trade_assets_current_recent_market_snapshot.sql` is now an informational bounded freshness check aligned to the documented manual and offseason refresh cadence.

## Documentation State

Created:

- [BigQuery Validation Process](../bigquery-validation-process.md)

Updated references in migration, Cloud Run operating model, and Data Ops Cloud Run Jobs rollout documentation so validation runs are clearly separated from migrations.

## Operational Constraints Honored

- No Firebase artifacts were created.
- No production Cloud Run Jobs were triggered.
- No LLM calls were made.
- No scraping or external source calls were made.
- No application runtime behavior was changed.

## Remaining Warnings

- Phase 12 output tables remained mostly empty until Phase 13.2 materialization jobs could seed backtest, market baseline, claim, claim grading, and content brief rows.
- Legacy Streamlit raw/source reads remained until compatibility rollout flags are enabled and old paths are retired.
- Bare `python` still pointed at `C:\Python314\python.exe`; all project commands should keep using `.\venv\Scripts\python.exe`.

## Readiness

Phase 13.1 was ready for Phase 13.2 materialization with warnings.
