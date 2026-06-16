# BigQuery Migration Process

This repo now has a lightweight BigQuery migration framework for the existing `fantasy_football_brain` warehouse.

This process does not change `src/load.py`, `src/materialize.py`, `src/pipeline.py`, or `app.py` startup behavior.

## Files

- Migration runner: [scripts/run_bigquery_migrations.py](../../scripts/run_bigquery_migrations.py)
- Migrations: [bigquery/migrations](../../bigquery/migrations)
- Views and compatibility placeholders: [bigquery/views](../../bigquery/views)
- Validation SQL helpers: [bigquery/validations](../../bigquery/validations)
- Compatibility contracts: [bigquery/contracts](../../bigquery/contracts)

## Configuration

The runner follows the existing repository BigQuery project pattern from `src/load.py`.

Project resolution:

1. `BQ_PROJECT`
2. `GCP_PROJECT`
3. `GOOGLE_CLOUD_PROJECT`
4. default from `src/load.py`, currently `fantasy-football-498121`

Dataset resolution:

1. `BQ_DATASET`
2. `BIGQUERY_DATASET`
3. `DATASET_NAME`
4. default `fantasy_football_brain`

The default keeps migrations pointed at the current dataset unless explicitly overridden.

## Commands

Dry run, local only, no BigQuery connection:

```powershell
python scripts/run_bigquery_migrations.py --dry-run
```

On Windows, prefer the repo venv so dependencies match the application image:

```powershell
.\venv\Scripts\python.exe scripts/run_bigquery_migrations.py --dry-run
```

List pending migrations by checking the ledger table:

```powershell
python scripts/run_bigquery_migrations.py --list-pending
```

Apply pending migrations and record them:

```powershell
python scripts/run_bigquery_migrations.py --apply
```

Record a migration as applied without executing its SQL:

```powershell
python scripts/run_bigquery_migrations.py --record 0001
```

Override project or dataset:

```powershell
python scripts/run_bigquery_migrations.py --dry-run --project fantasy-football-498121 --dataset fantasy_football_brain
```

Live commands such as `--list-pending`, `--apply`, and `--record` require Google credentials with:

- Project-level `roles/bigquery.jobUser` on `fantasy-football-498121`.
- Dataset-level BigQuery permissions on `fantasy_football_brain`, usually `roles/bigquery.dataEditor` for applying migrations or `roles/bigquery.dataViewer` for read-only inspection.

## Migration Ledger

The runner creates `schema_migrations` in the target dataset when a live mode runs.

Ledger columns:

- `migration_id`
- `description`
- `checksum`
- `source_path`
- `applied_at`
- `applied_by`
- `runner_version`

The ledger is partitioned by `DATE(applied_at)` and clustered by `migration_id`.

## Migration File Rules

Migration files live in `bigquery/migrations/`.

Naming convention:

```text
0001__short_description.sql
```

Rules:

1. Prefer `CREATE TABLE IF NOT EXISTS`, `CREATE VIEW OR REPLACE`, `ALTER TABLE ADD COLUMN IF NOT EXISTS`, and `MERGE`.
2. Do not rename existing tables without a separate migration plan.
3. Do not migrate large historical data in this framework until the rebuild plan explicitly calls for it.
4. Do not query raw source tables from new UI or LLM-facing objects.
5. Use placeholders for the current project and dataset:

```sql
`{{PROJECT_ID}}.{{DATASET_ID}}.table_name`
```

## Current Sample Migrations

- `0001__noop.sql`: proves discovery and recording without schema changes.
- `0002__create_model_runs.sql`: creates the harmless `model_runs` metadata table for future ranking and projection run tracking.
- `0003__model_run_config_foundation.sql`: additively extends `model_runs`, creates configuration/freshness tables, and seeds lookup configs idempotently.
- `0019__cloud_run_job_runs.sql`: creates the Cloud Run Job execution metadata table used by `src/job_runner.py`.
- `0020__create_backtest_framework.sql`: creates the backtest run ledger, player-week result, summary, and calibration tables.
- `0021__create_market_consensus_baselines.sql`: creates source-agnostic market and consensus baseline tables and optional backtest market comparison columns.
- `0022__create_meatbag_claim_ledger.sql`: creates manual claim-source, claim, claim-player, and evaluation-window tables for future grading.
- `0023__create_claim_grading.sql`: creates deterministic claim grading run, grade, and source scorecard tables.
- `0024__create_content_briefs.sql`: creates deterministic show content brief run, brief, and item tables.
- `0004__add_model_run_id_to_pigskin_rankings.sql`: conditionally adds model-run lineage columns to active and historical Pigskin ranking tables when they exist.
- `0005__player_identity_bridge.sql`: creates canonical player identity bridge tables without backfilling source data.
- `0006__scoring_profile_fantasy_points.sql`: creates profile-aware fantasy point output and enriches default scoring profile seed JSON.

`model_runs` does not migrate existing ranking rows. Existing `ranking_version` remains the backward-compatible display label until the UI is migrated.

During the transition, `ranking_version` and `model_run_id` coexist:

- `ranking_version` remains a human-facing label for existing ranking UI behavior.
- `model_run_id` is the future lineage key for generated rankings, projections, backtests, and evidence packets.
- Future ranking writers should create a `model_runs` row first, then write ranking rows with that `model_run_id`.

Source freshness snapshots should stay cheap:

- Use table metadata for existence, row counts, and modified time.
- Run max season/week checks only for allowlisted mart/output tables.
- Do not scan raw/source tables just to populate freshness metadata.
- Keep live BigQuery smoke tests optional because credentials and IAM vary by environment.

Scoring-profile materialization is a callable job, not a migration backfill:

- Use [src/materialize_fantasy_points.py](../../src/materialize_fantasy_points.py).
- Read `analytics_player_weekly_truth` first.
- Fall back to `weekly_metrics` only inside the controlled backend materializer.
- Do not wire Streamlit or Pigskin chat directly to raw scoring sources.

## Validation SQL

Validation helpers live in `bigquery/validations/`.

The initial helper checks for the migration ledger table:

- `001__schema_migrations_exists.sql`
- `002__scoring_profile_seed_rows_exist.sql`
- `003__league_type_seed_rows_exist.sql`
- `004__roster_format_seed_rows_exist.sql`
- `005__model_runs_required_columns.sql`
- `006__active_config_rows_unique.sql`
- `007_pigskin_rankings_model_run_id_present.sql`
- `008_pigskin_rankings_model_run_join_valid.sql`
- `116_claim_sources_grain.sql`
- `117_fantasy_claims_grain.sql`
- `118_claim_players_grain.sql`
- `119_claims_required_fields_for_review.sql`
- `120_claims_player_identity_coverage.sql`
- `121_claims_model_run_join.sql`
- `122_claim_evaluation_windows_grain.sql`
- `123_claim_grading_runs_grain.sql`
- `124_claim_grades_grain.sql`
- `125_claim_grades_required_scores.sql`
- `126_claim_grades_claim_join.sql`
- `127_claim_source_scorecards_grain.sql`
- `128_claim_grades_missing_flags_exist.sql`
- `129_content_brief_runs_grain.sql`
- `130_content_briefs_grain.sql`
- `131_content_brief_items_grain.sql`
- `132_content_briefs_required_json_keys.sql`
- `133_content_briefs_size_bounds.sql`
- `134_content_briefs_source_freshness_exists.sql`
- `135_content_briefs_missing_flags_exist.sql`

Validation SQL files are not automatically run by the migration runner yet. They are tracked here so future PRs can add explicit checks without mixing validation and migration execution.

## Safety Notes

- Dry run never connects to BigQuery.
- Apply mode ensures the dataset and ledger exist, applies only pending files, and records each applied migration.
- No existing tables are renamed.
- No data is migrated by the sample migrations.
- The Streamlit app and current pipeline continue to use their existing code paths until a later PR wires compatibility objects into runtime.

## Prioritized Migration-Debt List

1. Add a validation runner for `bigquery/validations`.
2. Apply `0004` and keep Pigskin ranking generation writing `model_run_id`.
3. Add `player_identity_bridge` before wiring Player Profiles to compatibility views.
4. Convert compatibility placeholder views into production views or tables in small PRs.
5. Replace arbitrary Pigskin SQL execution with allowlisted context APIs after `llm_player_context_packet` is production-ready.
