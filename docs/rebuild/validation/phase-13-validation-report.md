# Phase 13 Validation Report

Final decision: GO WITH WARNINGS

## Blockers

None.

## Warnings

- Phase 13.1 standalone documentation warning resolved by [Phase 13.1 Warehouse Activation Report](phase-13-1-warehouse-activation-report.md).
- Migration runner wording warning resolved in Phase 14.1. `--dry-run` now labels output as local discovery, while `--list-pending` remains the ledger-aware pending-state command.
- Backtest dashboard empty-state warning resolved in [Phase 14.2 Backtest Seed Report](phase-14-2-backtest-seed-report.md). The dashboard now has one bounded backtest run and six summary rows.
- Market identity warning resolved in [Phase 14.3 Market Identity Coverage Report](phase-14-3-market-identity-coverage-report.md). Player identity missing rate is now `0.0`; the remaining 64 null identities are draft-pick market assets marked not applicable.
- Claim ledger validation reports informational empty-state rows for claim-player coverage and draft review checks.
- The worktree contains many uncommitted and untracked Phase 13 artifacts. This is expected for the current validation branch, but should be reviewed before merge.

## Architecture Status

The documented target architecture remains consistent:

- Streamlit on Cloud Run is the admin and control surface.
- BigQuery is the analytical source of truth.
- Cloud Run Jobs are the target for long-running ingestion, materialization, rankings, evidence, backtests, validations, content briefs, and claim grading.
- Cloud Scheduler is planned for recurring Cloud Run Job triggers.
- Secret Manager is the target for secrets.
- Firebase artifacts are not part of the target architecture.

## Repo And Secrets Status

Commands run:

```powershell
git status --short
git diff --stat
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
```

Result:

- Existing Phase 13 source, docs, tests, validation SQL, scripts, and helper modules are modified or untracked.
- No tracked service account JSON files were found.
- No tracked `.env` files were found.
- No tracked private keys or secret-shaped content were found by the deployment safety checker.
- No Firebase artifacts were found.
- No large generated binary artifacts were visible in `git status`.

Deployment safety checker result: passed.

## Compile And Test Status

Commands run:

```powershell
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest discover tests
```

Results:

- `app.py` compile: passed.
- `src` and `scripts` compile: passed.
- Unit tests: passed, 266 tests.

## Migration Status

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
```

Results:

- Dry-run command completed successfully.
- Dry-run output listed discovered local migration files and explicitly stated it does not read the live ledger.
- Live ledger `--list-pending` reported `No pending migrations.`
- No new migration files are present in the current worktree status.
- Destructive DDL review is not applicable for new migrations in this validation because there are no new migration files.

Classification:

- No migration blocker.
- Warning resolved in Phase 14.1: dry-run output is now labeled local discovery only.

## Validation Status

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern backtest
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern claim
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
```

Results:

| Pattern | Result | Classification |
| --- | --- | --- |
| dry-run | 149 validation files discovered | pass |
| `backtest` | 11 passed, 0 failed | pass with seeded dashboard data |
| `market` | 9 passed, 0 failed | pass with non-player asset classification |
| `claim` | 17 passed, 0 failed | pass with expected empty-state warnings |
| `content_brief` | 11 passed, 0 failed | pass |
| `cloud_run_job` | 8 passed, 0 failed | pass |

Warning details:

- `139_backtest_dashboard_latest_runs.sql`: resolved in Phase 14.2, `latest_backtest_runs = 1`.
- `140_backtest_dashboard_summary_available.sql`: resolved in Phase 14.2, `backtest_summary_rows = 6`, `backtest_run_count = 1`.
- `113_market_identity_coverage.sql`: resolved in Phase 14.3. `total_rows = 461`, `player_rows = 397`, `non_player_asset_rows = 64`, `unresolved_player_rows = 0`, `player_identity_missing_rate = 0.0`.
- `120_claims_player_identity_coverage.sql`: claim-player rows are currently empty.
- `142_claim_ledger_ui_sources_exist.sql`: informational source count returned 3 active sources.
- `143_claim_ledger_ui_draft_claims_allowed_missing_fields.sql`: informational row returned zero draft claims missing review fields.

## UI Feature Flag Status

Runtime check result:

| Flag | Env value | Enabled |
| --- | --- | --- |
| `USE_COMPAT_PLAYER_PROFILES` | unset | false |
| `USE_COMPAT_SLEEPER_WATCH` | unset | false |
| `USE_COMPAT_TRADE_ASSETS` | unset | false |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | unset | false |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | unset | false |
| `USE_BACKTEST_DASHBOARD` | unset | false |
| `USE_CLAIM_LEDGER_UI` | unset | false |
| `USE_CONTENT_BRIEF_REVIEW_UI` | unset | false |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | unset | false |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | unset | false |

Phase 13.6 docs recommend only `USE_COMPAT_TRADE_PLAYER_HISTORY=true` for staged or local QA. Production defaults remain unchanged and all flags are currently false.

## Raw And Source Exposure Status

Static checks:

- `execute_bigquery_sql` is not visible in Pigskin prompt or schema files.
- `app.py` still contains the `### Context Tool Protocol ###` marker.
- `src/pigskin_chat_schema.py` lists curated Pigskin allowed tables and explicitly blocks raw/source tables.
- New backtest reader, claim import, content brief review, and compatibility rollout helpers do not reference raw/source tables such as `weekly_metrics`, `play_by_play`, `ngs_*`, `ftn_charting`, `weekly_snap_counts`, `injury_reports`, `player_rosters`, `player_contracts`, `depth_charts`, or `market_values`.
- Legacy raw reads still exist in old Streamlit fallback paths. These are expected during migration and remain behind default-false compatibility rollout paths.

Classification:

- No Pigskin raw/source exposure blocker.
- No new Phase 13 UI helper raw/source blocker.

## Backtest Dashboard Status

Status:

- `src/backtest_readers.py` exists.
- Backtest UI wiring exists behind `USE_BACKTEST_DASHBOARD=false`.
- Reader helpers use `backtest_runs`, `backtest_result_summary`, `backtest_result_player_week`, and `backtest_calibration_bins`.
- Tests confirm query builders avoid raw/source table names and enforce limits and sort enums.
- Validations pass.

Phase 14.2 update:

- The backtest dashboard empty-state is resolved by `backtest-weekly-2025-2025-20260616T114527Z-2093e839`.
- The seeded run covers 2025 week 1, `ppr`, `redraft`, and `one_qb`.
- Backtest reader smoke checks returned one run, six summary rows, and five player-error rows.
- A failed partial projection run remains temporarily visible until BigQuery streaming-buffer cleanup can be retried: `weekly_projection-2025-1-20260616T113848Z-f07a0ccb`.

## Claim Ledger UI Status

Status:

- `src/claim_import.py` exists.
- Claim ledger UI is behind `USE_CLAIM_LEDGER_UI=false`.
- CSV import has preview and validation.
- Import parser reads uploaded CSV content only. It does not scrape URLs.
- Unresolved or ambiguous player identities are flagged and forced to draft-only handling.
- Tests cover feature flag defaults, validation, player resolution, and import behavior.
- Validations pass.

Warning:

- Claim-player coverage is currently an empty-state, so identity coverage is informational only.

## Content Brief Review Status

Status:

- `src/content_brief_review.py` exists.
- Content brief review UI is behind `USE_CONTENT_BRIEF_REVIEW_UI=false`.
- The helper reads only `content_brief_runs`, `content_briefs`, and `content_brief_items`.
- Review status values are validated.
- Markdown export is implemented and tested.
- No LLM calls are made by default.
- Validations pass.

## Compatibility Rollout Status

Status:

- `src/compat_rollout.py` exists.
- `docs/rebuild/compat-rollout-status.md` exists.
- `docs/rebuild/validation/phase-13-6-compat-rollout-report.md` exists.
- All five compatibility candidates are assessed.
- Only `USE_COMPAT_TRADE_PLAYER_HISTORY` is selected for staged or local QA.
- Rollback is documented: unset the flag and restart Streamlit or Cloud Run.
- Legacy paths remain available while flags are false.

Classification:

- No rollout blocker.

## Cloud Run Jobs Hardening Status

Status:

- `src/cloud_run_jobs.py` and `src/job_runner.py` exist and compile.
- Dry-run previews work.
- Live triggers require `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=true`, `DATA_OPS_ALLOW_JOB_TRIGGER=true`, user confirmation, and `gcloud`.
- Live triggers remain default off.
- Missing `gcloud` behavior is explicit.
- `docs/rebuild/iam-hardening-plan.md` exists.
- `docs/rebuild/secret-manager-plan.md` exists.
- `docs/rebuild/cloud-scheduler-plan.md` exists.
- `docs/rebuild/deployment-readiness-checklist.md` exists.
- Deployment safety checker passes.
- Cloud Run job validations pass.

Classification:

- No Cloud Run Jobs blocker.

## Recommended Phase 14 Work

1. Retry targeted cleanup for failed partial projection seed `weekly_projection-2025-1-20260616T113848Z-f07a0ccb` after BigQuery releases streaming-buffer rows.
2. Monitor future market imports for true unresolved players and add audited aliases or `player_identity_overrides` only when deterministic.
3. Run manual QA with only `USE_COMPAT_TRADE_PLAYER_HISTORY=true`, then decide whether to promote that flag in staging.
4. Add a narrowly authorized live Cloud Run Job deployment test for `validate-warehouse` after operator approval.
5. Keep claim import manual-only and add sample claim rows so the claim ledger UI can be exercised beyond empty-state checks.
6. Keep content brief review deterministic until a separate show-writer LLM gate is designed.
