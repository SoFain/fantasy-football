# BigQuery Validation Process

This document defines how warehouse validation SQL is written, discovered, run, and reported for the AI vs. Meatbags rebuild.

The validation runner is not a migration runner. It checks warehouse shape, grain, freshness, lineage, and safety expectations after migrations or materialization jobs have run.

## Purpose

Use validations to answer narrow warehouse questions:

- Does a required table or view exist?
- Does a table keep its expected grain?
- Are required lineage fields populated?
- Are model-run joins valid?
- Are compatibility objects hiding raw/source table access from UI and Pigskin paths?
- Are source freshness and missing-data flags present?
- Are empty states expected, documented, and nonfatal?

Validations should be cheap, bounded, and repeatable. They should not mutate warehouse data.

## Migrations Versus Validations

Migrations live in [bigquery/migrations](../../bigquery/migrations) and create or alter warehouse objects. They must be additive and idempotent where possible.

Validations live in [bigquery/validations](../../bigquery/validations) and run read-only SQL checks against existing warehouse objects.

Do not combine schema changes and validation checks in one SQL file. Migrations run through [scripts/run_bigquery_migrations.py](../../scripts/run_bigquery_migrations.py). Validations run through [scripts/run_bigquery_validations.py](../../scripts/run_bigquery_validations.py).

## Required Python Invocation

On this Windows repo, use the project virtual environment:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Do not use bare `python`. On this machine, bare `python` resolves to `C:\Python314\python.exe`, which lacks repo dependencies such as `google-cloud-bigquery` and `pandas`.

## Commands

Discover validations without executing BigQuery queries:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Run all validations:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run
```

Run validations whose file names match a pattern:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern backtest
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern claim
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
```

Override project or dataset when needed:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market --project fantasy-football-498121 --dataset fantasy_football_brain
```

The current validation runner does not persist validation results to a results table. Record results in the relevant phase report. A future `validate-warehouse` Cloud Run Job may also log execution metadata through `cloud_run_job_runs`.

## Expectation Comments

Each validation SQL file should include an `Expected result:` comment near the top. The current runner parses these supported forms:

```sql
-- Expected result: zero rows
-- Expected result: duplicate_grain_count = 0
-- Expected result: row_count > 0
-- Expected result: identity_missing_rate should be reviewed, not always zero.
```

Supported expectation types:

- `zero_rows`: the query must return no rows.
- `equal`: the first returned row must contain a named numeric field equal to the expected value.
- `greater`: the first returned row must contain a named numeric field greater than the expected value.
- `informational`: rows are printed as `WARNING`, but the validation exits successfully.

The current parser does not support literal metadata keys such as:

```sql
-- severity=warning
-- expect_nonzero
-- max_rows=10
-- description=...
```

Those keys are reserved for a future parser upgrade. For now, use `Expected result:` wording the runner already understands.

## Zero-Row Pass Convention

The safest default validation is a query that returns only bad rows:

```sql
-- Expected result: zero rows

SELECT *
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.some_output_table`
WHERE required_field IS NULL;
```

If the query returns zero rows, the validation passes. If it returns one or more rows, the runner prints the first row and exits with failure.

## Informational Warnings

Use informational validations for expected empty states, review thresholds, and nonblocking coverage metrics.

Example:

```sql
-- Expected result: identity_missing_rate should be reviewed, not always zero.

SELECT
    COUNT(*) AS total_rows,
    COUNTIF(player_id_internal IS NULL) AS missing_identity_rows,
    SAFE_DIVIDE(COUNTIF(player_id_internal IS NULL), COUNT(*)) AS identity_missing_rate
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.market_consensus_player_values`;
```

Informational validations can emit warning rows while still exiting successfully. Phase reports must classify these as expected empty-state, warning, or blocker.

## Adding A Validation

1. Add a SQL file under `bigquery/validations/`.
2. Use a numeric prefix that keeps related checks grouped.
3. Include an `Expected result:` comment supported by the current runner.
4. Use `{{PROJECT_ID}}` and `{{DATASET_ID}}` placeholders.
5. Query compatibility objects, marts, output tables, metadata tables, or bounded table metadata.
6. Avoid raw/source table scans unless the validation is explicitly scoped to backend materializer safety.
7. Keep the query cheap. Prefer grouped counts, `INFORMATION_SCHEMA`, partition filters, and capped windows.
8. Run dry-run discovery.
9. Run the narrow pattern that matches the new file.
10. Document any expected warnings in the phase report.

## Cloud Run Jobs

The future `validate-warehouse` Cloud Run Job should call this runner with explicit patterns and environment variables:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
```

Cloud Run validation jobs should:

- Use least-privilege service accounts.
- Read project and dataset from configured environment variables.
- Avoid triggering materialization or ingestion work.
- Log job execution metadata through `cloud_run_job_runs`.
- Fail loudly on schema defects.
- Treat informational warnings as successful runs that require review.

## Deployment Gates

Use validation patterns as warehouse gates:

- After migrations: run validations for newly created objects.
- After materialization jobs: run validations for the affected marts, packets, projections, or scoreboards.
- Before Streamlit feature-flag rollout: run compatibility-object validations for the target path.
- Before enabling LLM-visible context: run packet and raw-source-exposure validations.

Do not treat a broad full-warehouse validation failure as automatically deploy-blocking. Classify the failure:

- `Blocker`: schema defect, raw/source exposure, broken lineage, invalid grain, or failed required field check.
- `Warning`: freshness or coverage condition that needs review but does not make the object unsafe.
- `Expected empty-state`: newly created output tables with no seeded or materialized rows yet.

## Avoiding Unbounded Scans

Validation SQL should avoid expensive reads:

- Prefer `COUNT(*)` with partition filters where possible.
- Use `INFORMATION_SCHEMA` for schema and metadata checks.
- Do not select wide payload columns unless checking size or JSON keys.
- Avoid raw play-by-play and raw source tables in UI/LLM safety checks.
- Cap recent windows by season, week, snapshot date, or model run.
- Keep validation joins on clustered keys where available.

## Phase Reports

When a validation run is part of a rebuild phase, update the phase report with:

- Command used.
- Pattern used.
- Pass and failure counts.
- Warnings and expected empty states.
- Blockers, if any.
- Final decision: `GO`, `GO WITH WARNINGS`, or `NO-GO`.

If a validation failure is reclassified, document why the validation behavior matches the intended refresh cadence, materialization cadence, or rollout state.
