# Phase 14 Validation Report

Final decision: GO WITH WARNINGS

Validation date: 2026-06-16

Project: `fantasy-football-498121`

Dataset: `fantasy_football_brain`

## Scope

This validation covered:

- Phase 14.1 documentation and migration-runner warning cleanup.
- Phase 14.2 bounded backtest seed.
- Phase 14.3 market identity coverage improvement.
- Phase 14.4 `USE_COMPAT_TRADE_PLAYER_HISTORY` staged QA.
- Phase 14.5 claim ledger sample/manual data.
- Phase 14.6 content brief review exercise.
- Phase 14.7 `validate-warehouse` Cloud Run Job test.

No Firebase artifacts were created. No LLM calls were made. No scraping was performed. No migrations were applied. No live Cloud Run Jobs were triggered during this validation pass.

## Blockers

None.

## Warnings

1. `docs/rebuild/validation/phase-14-5-claim-ledger-sample-report.md` is missing. The claim ledger data and validations are present, but the standalone Phase 14.5 report should be added for documentation completeness.
2. Phase 14.2 left a documented partial projection-run cleanup warning. BigQuery rejected cleanup while rows were still in the streaming buffer. The seeded backtest itself is valid and dashboard rows now exist.
3. Claim validation has expected informational warnings:
   - `120_claims_player_identity_coverage.sql`: 3 claim-player rows, 1 intentionally unresolved demo row, identity missing rate `0.3333333333333333`.
   - `142_claim_ledger_ui_sources_exist.sql`: 3 active claim sources.
   - `143_claim_ledger_ui_draft_claims_allowed_missing_fields.sql`: 1 draft claim missing review fields, allowed because it is draft-only.
4. Content brief review is exercised with deterministic `weekly_streamers_show` briefs from projection rankings. Fraud Watch, Sleeper Breakout, Trade Review, and Meatbag Accountability source packet tables remain empty until their packet or grading inputs are populated.
5. Phase 14.7 only reached dry-run preview. Live `validate-warehouse` deployment and trigger were not authorized because `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true` was not set. `gcloud` is also not installed locally.
6. One local dry-run `validate-warehouse` metadata row remains `running`: `validate-warehouse-20260616T133114Z-5e7c51a8`. It does not represent a live Cloud Run execution. It should be marked failed after the streaming buffer clears, or ignored in favor of the fixed load-job metadata writer on the next authorized test.
7. The worktree has a large set of reviewed rebuild changes and untracked Phase 13/14 files. This is expected for the rebuild branch, but it should be reviewed before merge.

## Architecture Status

- Streamlit remains the Cloud Run admin and control surface.
- BigQuery remains the analytical source of truth.
- Cloud Run Jobs remain the target for long-running ingestion, materialization, rankings, evidence, validations, backtests, content briefs, and claim grading.
- Cloud Scheduler remains planned, but no scheduler jobs were created.
- Secret Manager remains the target for runtime secrets.
- Firebase, Firestore, Firebase Functions, and Firebase Hosting are not part of the target architecture.

Status: pass.

## Repo And Secret Safety

Commands run:

```powershell
git status --short
git diff --stat
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
```

Results:

- Deployment safety checker passed:
  - `no_firebase_artifacts`
  - `no_tracked_secret_files`
  - `no_secret_content`
  - `required_files_exist`
  - `feature_flags_default_off`
  - `pigskin_no_execute_bigquery_sql`
  - `app_py_compiles`
  - `src_scripts_compile`
- Tracked Firebase artifact filename scan found no `firebase.json`, `.firebaserc`, `firestore.rules`, `firestore.indexes.json`, or `functions/package.json`.
- Worktree is dirty with expected Phase 13/14 rebuild changes and new validation/docs/helper files.
- No unexpected generated binaries were observed in the reviewed status output.

Status: pass with worktree review warning.

## Compile And Test Status

Commands run:

```powershell
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest discover tests
```

Results:

- `app.py` compiled.
- `src` and `scripts` compiled.
- Unit tests passed: 284 tests, 0 failures.

Status: pass.

## Migration Status

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
```

Results:

- Dry-run wording is clear:
  - `Dry run mode: local discovery only. This does not connect to BigQuery or read the schema_migrations ledger.`
  - `Discovered migration files:`
- `--list-pending` reported `No pending migrations.`
- No migrations were applied in this validation pass.

Status: pass.

## Validation Status

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern backtest
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern claim
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_history
```

Results:

| Pattern | Result | Status |
| --- | ---: | --- |
| `backtest` | 11 passed, 0 failed | pass with informational dashboard rows |
| `market` | 9 passed, 0 failed | pass |
| `claim` | 17 passed, 0 failed | pass with expected demo/draft informational rows |
| `content_brief` | 11 passed, 0 failed | pass |
| `cloud_run_job` | 8 passed, 0 failed | pass |
| `compat_trade_player_history` | 6 passed, 0 failed | pass with informational identity coverage row at 0.0 missing rate |

Status: pass with documented warnings.

## Backtest Status

Phase 14.2 resolved the backtest dashboard empty-state.

Current bounded warehouse counts:

| Table | Rows |
| --- | ---: |
| `backtest_runs` | 1 |
| `backtest_result_player_week` | 25 |
| `backtest_result_summary` | 6 |
| `backtest_calibration_bins` | 16 |

Latest dashboard validations:

- `139_backtest_dashboard_latest_runs.sql`: `latest_backtest_runs = 1`.
- `140_backtest_dashboard_summary_available.sql`: `backtest_summary_rows = 6`, `backtest_run_count = 1`.
- `141_backtest_dashboard_no_raw_source_dependencies.sql`: passed.

Status: pass with cleanup warning for the earlier partial projection-run rows.

## Market Identity Status

Phase 14.3 resolved the market identity warning by classifying non-player draft-pick market assets instead of fabricating player IDs.

Current bounded warehouse counts:

- Total market baseline rows: 461.
- Player rows: 397.
- Non-player asset rows: 64.
- Rows missing `player_id_internal`: 64.
- Unresolved player rows: 0.
- Player identity missing rate: `0.0`.
- Rows marked `player_identity_not_applicable`: 64.

`113_market_identity_coverage.sql` passed with `player_identity_warning_rows = 0`.

Status: pass.

## Compatibility Rollout Status

Only `USE_COMPAT_TRADE_PLAYER_HISTORY` was QA'd for staged/local promotion. Other compatibility flags remain default false.

Default flag checks:

| Flag | Effective default |
| --- | --- |
| `USE_COMPAT_PLAYER_PROFILES` | false |
| `USE_COMPAT_SLEEPER_WATCH` | false |
| `USE_COMPAT_TRADE_ASSETS` | false |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | false |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | false |
| `USE_BACKTEST_DASHBOARD` | false |
| `USE_CLAIM_LEDGER_UI` | false |
| `USE_CONTENT_BRIEF_REVIEW_UI` | false |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | false |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | false |

Readiness check:

```powershell
.\venv\Scripts\python.exe -m src.compat_rollout --check USE_COMPAT_TRADE_PLAYER_HISTORY
```

Result:

- `compat_trade_player_history` exists as a view.
- Required columns are present.
- Row count: 55,617.
- `source_freshness_json` and `missing_data_flags` are populated in the sampled rows.
- Rollback is documented: unset `USE_COMPAT_TRADE_PLAYER_HISTORY` and restart Streamlit or Cloud Run.

Status: pass. Recommendation remains staged promotion only.

## Claim Ledger Status

Claim ledger can be exercised with sample/manual data.

Current bounded warehouse counts:

- Demo claims: 3.
- Draft demo claims: 3.
- Non-draft demo claims: 0.
- Claim-player rows: 3.
- Unresolved claim-player rows: 1.

Validation confirms:

- Sample/demo claims are draft-only.
- The unresolved row is draft-only and does not violate ready-review validations.
- No scraping path was exercised.
- CSV import parser is file-content based.

Warning:

- `phase-14-5-claim-ledger-sample-report.md` is missing and should be added.

Status: pass with documentation warning.

## Content Brief Status

Content brief review can be exercised with deterministic data and no LLM calls.

Current bounded warehouse counts:

| Table | Rows |
| --- | ---: |
| `content_brief_runs` | 2 |
| `content_briefs` | 2 |
| `content_brief_items` | 16 |

Latest brief:

- `content_brief_id`: `brief-weekly_streamers_show-2025-w1-20260616T131307Z-e7fd38e1`
- `brief_type`: `weekly_streamers_show`
- `review_status`: `draft`

Validation confirms:

- Review status values are valid.
- Brief items join to briefs.
- Missing-data flags and source freshness exist.
- No raw source dependency was found.

Status: pass with source-packet empty-state warning.

## Cloud Run Job Status

Phase 14.7 proved the deployment path to dry-run preview only.

Authorization and runtime status:

- `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true` was not set.
- No live Cloud Run Job deployment was run.
- No live Cloud Run Job trigger was run.
- No scheduler jobs were created.
- Live triggers remain gated by `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=true` and `DATA_OPS_ALLOW_JOB_TRIGGER=true`.
- `gcloud` is not installed locally.

Latest local metadata row:

- `job_run_id`: `validate-warehouse-20260616T133114Z-5e7c51a8`
- `job_name`: `validate-warehouse`
- `status`: `running`
- `metadata_json` contains `"dry_run": true` and `"pattern": "^096_"`

The row is a local dry-run metadata artifact, not a live Cloud Run execution.

Status: pass with live-test-not-run warning.

## Pigskin Safety Status

Pigskin arbitrary SQL remains removed.

Checks:

- Safety checker passed `pigskin_no_execute_bigquery_sql`.
- Unit tests covering Pigskin chat schema and context tools passed.
- `src/pigskin_chat_schema.py` lists raw/source tables only in `PIGSKIN_CHAT_BLOCKED_TABLES`.
- Pigskin-visible allowed tables remain curated analytics/output tables.
- `execute_bigquery_sql` is not available as a Pigskin-visible tool.

Status: pass.

## Recommended Phase 15 Work

1. Add the missing `docs/rebuild/validation/phase-14-5-claim-ledger-sample-report.md` from the existing claim sample/import evidence.
2. Retry cleanup or status correction for streaming-buffer leftovers once BigQuery allows mutation:
   - the partial projection run from Phase 14.2
   - the local dry-run `validate-warehouse` metadata row
3. Promote `USE_COMPAT_TRADE_PLAYER_HISTORY=true` to staging only, then run manual Trade Lab QA against real workflows before production default changes.
4. Materialize Fraud Watch, Sleeper Breakout, Trade Review, and claim-grading packets so content briefs can move beyond `weekly_streamers_show`.
5. Install and configure `gcloud`, set `CLOUD_RUN_JOBS_IMAGE`, set `CLOUD_RUN_JOB_SERVICE_ACCOUNT`, then repeat Phase 14.7 with explicit authorization for only `validate-warehouse`.
6. Keep all UI migration flags default false until each compat path has staged QA and rollback evidence.

## Final Decision

GO WITH WARNINGS.

There are no hard blockers. The warnings are operational and documentation cleanup items, not architecture, safety, test, migration, Pigskin, or data-integrity blockers.

## Phase 15.1 Cleanup Addendum

Phase 15.1 closed documentation and cleanup-only warnings.

Results:

- Created `docs/rebuild/validation/phase-14-5-claim-ledger-sample-report.md`.
- Confirmed 3 demo claims, 3 draft demo claims, 0 non-draft demo claims, 3 claim-player rows, and 1 intentionally unresolved draft-only demo row.
- Confirmed no scraping, no LLM calls, and no production claims fabricated.
- Confirmed `validate-warehouse-20260616T133114Z-5e7c51a8` is a local dry-run metadata artifact with `cloud_run_execution_name` null and `metadata_json` containing `"dry_run": true`.
- Attempted guarded Cloud Run metadata cleanup, but BigQuery still rejected the update because the row remains in the streaming buffer.
- Marked partial projection model run `weekly_projection-2025-1-20260616T113848Z-f07a0ccb` as `failed`.
- Confirmed seeded backtest `backtest-weekly-2025-2025-20260616T114527Z-2093e839` remains valid and still points to complete model run `weekly_projection-2025-1-20260616T114422Z-a25a92c1`.

Remaining warning:

- The local dry-run `validate-warehouse` metadata row still needs status cleanup after BigQuery allows mutation.
