# BigQuery Validation Process

Validations are the gate between "the migration ran" and "the warehouse object is live". A migration proves the DDL applied. A validation proves the resulting data has the grain, coverage, and lineage the contract promises.

This document was previously referenced by the Phase 12 activation instructions but did not exist. See warning 6 in [validation/phase-12-validation-report.md](validation/phase-12-validation-report.md).

Companion document: [bigquery-migration-process.md](bigquery-migration-process.md).

## Files

- Validation runner: [scripts/run_bigquery_validations.py](../../scripts/run_bigquery_validations.py)
- Validation SQL: [bigquery/validations](../../bigquery/validations), currently 138 files
- Table contracts: [bigquery/contracts](../../bigquery/contracts)

## Configuration

The runner resolves project and dataset the same way the migration runner does, preferring `src/load.py:get_bigquery_project` when importable.

Project resolution: `BQ_PROJECT`, then `GCP_PROJECT`, then `GOOGLE_CLOUD_PROJECT`, then the `fantasy-football-498121` default.

Dataset resolution: `BQ_DATASET`, then `BIGQUERY_DATASET`, then `DATASET_NAME`, then the `fantasy_football_brain` default.

## Commands

List every validation and its parsed expectation without connecting to BigQuery. This is also what happens if you pass no flags at all:

```bash
python scripts/run_bigquery_validations.py --dry-run
```

On Windows, prefer the repo venv so dependencies match the application image:

```bash
.\venv\Scripts\python.exe scripts/run_bigquery_validations.py --dry-run
```

Execute the validations against BigQuery:

```bash
.\venv\Scripts\python.exe scripts/run_bigquery_validations.py --run
```

Run one subject area. `--pattern` is a case-insensitive regex matched against the file name:

```bash
.\venv\Scripts\python.exe scripts/run_bigquery_validations.py --run --pattern claim
```

Override project or dataset:

```bash
.\venv\Scripts\python.exe scripts/run_bigquery_validations.py --run --project fantasy-football-498121 --dataset fantasy_football_brain
```

The runner exits non-zero when any validation fails, so it can gate a deploy step.

Live runs need project-level `roles/bigquery.jobUser` and dataset-level `roles/bigquery.dataViewer` on `fantasy_football_brain`. Validations only read, so `dataEditor` is not required.

## Writing a Validation

Validation files live in `bigquery/validations/` and are named `NNN__short_description.sql`, matching the ordering convention used by migrations.

Use the same placeholders as migrations. The runner substitutes them before execution:

```sql
`{{PROJECT_ID}}.{{DATASET_ID}}.table_name`
```

Declare the expectation in a leading SQL comment. The runner parses the **first** matching `-- Expected result:` line and ignores anything after it, so put exactly one expectation per file:

| Comment form | Passes when |
| --- | --- |
| `-- Expected result: zero rows` | the query returns no rows |
| `-- Expected result: some_column = 0` | first row's `some_column` equals the value |
| `-- Expected result: row_count > 0` | first row's `row_count` exceeds the value |
| `-- Expected result: review_rows should be low` | always passes; returns rows as a WARNING for human review |

A file with no parseable expectation defaults to `zero rows`.

Prefer the `zero rows` form for defect checks: select the offending rows and expect none. The failure output prints the first offending row, which makes the failure self-describing.

Use the informational form only for bounded review checks that are legitimately non-zero in some seasons. Migration `044_compat_trade_assets_current_recent_market_snapshot.sql` is the worked example: it was reclassified from a hard check to a bounded review check so it passes in the offseason inside the 14-day manual-refresh window.

## What to Validate

Every new warehouse object should get at least:

1. **Grain.** Duplicate-key rows return zero. This is the most common validation in the repo.
2. **Required fields.** Rows missing contract-required columns return zero.
3. **Lineage.** Rows whose `model_run_id` does not join to `model_runs` return zero.
4. **Coverage.** Row count exceeds zero after the materialization job runs.
5. **Missing-data flags.** Rows where the contract's missing-data flags are null return zero.

Rule 10 in [CODEX_PROJECT_CONTEXT.md](../CODEX_PROJECT_CONTEXT.md) requires tests or validation queries for every transformation. A table contract without a matching validation is incomplete.

## Activation Sequence

An output table is not live until all four steps pass:

1. Apply the migration: `run_bigquery_migrations.py --apply`.
2. Run the materialization job that populates the table.
3. Run the validations for that subject area: `run_bigquery_validations.py --run --pattern <area>`.
4. Only then promote any `USE_COMPAT_*` flag that reads from it.

Phase 12 created its warehouse objects but most output tables remain empty until step 2 runs for each one. Empty tables will fail coverage validations, which is the intended signal, not a defect in the validation.

## Safety Notes

- Validations only read. They never mutate the warehouse.
- Dry run never connects to BigQuery.
- Validation runs are separate from migration runs on purpose; do not mix validation and DDL execution in one command.
- Do not scan raw or source tables in a validation just to produce a count. Validate the contract object.
