# Phase 15 Validation Report

Final decision: GO WITH WARNINGS

Validation date: 2026-06-16

Project: `fantasy-football-498121`

Dataset: `fantasy_football_brain`

## Scope

This validation covered:

- Phase 15.1: close Phase 14 warnings.
- Phase 15.2: materialize missing segment packets.
- Phase 15.3: promote `USE_COMPAT_TRADE_PLAYER_HISTORY=true` to staging only.
- Phase 15.4: authorized live `validate-warehouse` Cloud Run Job test.
- Phase 15.5: merge and release readiness package.

No migrations were applied. No live Cloud Run Jobs were triggered. No scheduler jobs were created. No LLM calls were made. No scraping was performed. No Firebase artifacts were created.

## Blockers

None.

## Warnings

1. Phase 15.4 live `validate-warehouse` Cloud Run Job testing remains blocked from this local environment because `gcloud`, `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true`, `CLOUD_RUN_JOBS_IMAGE`, and `CLOUD_RUN_JOB_SERVICE_ACCOUNT` are missing.
2. Local dry-run metadata row `validate-warehouse-20260616T133114Z-5e7c51a8` remains a known non-live cleanup warning because BigQuery streaming-buffer limits still block update.
3. Claim validations retain expected informational demo/draft warnings:
   - 3 claim-player rows.
   - 1 intentionally unresolved draft-only demo row.
   - identity missing rate `0.3333333333333333`.
   - 1 draft claim missing review fields, allowed because it is draft-only.
4. Backtest dashboard validations return informational rows confirming the seeded dashboard data:
   - latest backtest runs: `1`.
   - backtest summary rows: `6`.
5. `compat_trade_player_history` identity coverage returns an informational row with `missing_identity_rate = 0.0`.
6. Production feature flags remain default false. Only staging is documented to enable `USE_COMPAT_TRADE_PLAYER_HISTORY=true`.

## Repo And Secret Safety

Commands run:

```powershell
git status --short
git diff --stat
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
```

Result:

- Worktree is dirty with expected Phase 15 docs and previously reviewed rebuild changes.
- 12 tracked files are modified.
- 7 untracked docs are present and classified for commit in the merge readiness report.
- No deleted files were found in the Phase 15.5 inventory.
- Deployment safety checker passed:
  - `no_firebase_artifacts`
  - `no_tracked_secret_files`
  - `no_secret_content`
  - `required_files_exist`
  - `feature_flags_default_off`
  - `pigskin_no_execute_bigquery_sql`
  - `app_py_compiles`
  - `src_scripts_compile`
- Firebase artifact text matches are limited to safety scripts, tests, and historical validation docs, not actual Firebase config artifacts.

Status: pass.

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
- Unit tests passed: 285 tests, 0 failures.

Status: pass.

## Migration Status

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
```

Results:

- Dry-run uses local discovery only and reports 24 migration files.
- Ledger-aware `--list-pending` reported no pending migrations.
- No migrations were applied.

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
| dry-run | 149 validation files discovered | pass |
| `backtest` | 11 passed, 0 failed | pass with informational dashboard rows |
| `market` | 9 passed, 0 failed | pass |
| `claim` | 17 passed, 0 failed | pass with expected demo/draft informational rows |
| `content_brief` | 11 passed, 0 failed | pass |
| `cloud_run_job` | 8 passed, 0 failed | pass |
| `compat_trade_player_history` | 6 passed, 0 failed | pass with informational identity coverage row at 0.0 missing rate |

Status: pass with documented warnings.

## Phase 15.1 Status

Phase 15.1 closed documentation gaps and documented cleanup warnings.

Confirmed:

- `docs/rebuild/validation/phase-14-5-claim-ledger-sample-report.md` exists.
- Partial projection model run `weekly_projection-2025-1-20260616T113848Z-f07a0ccb` is documented as marked `failed`.
- Dry-run `validate-warehouse-20260616T133114Z-5e7c51a8` is documented as a local dry-run metadata artifact, not a live Cloud Run execution.
- BigQuery streaming-buffer limits still block cleanup of that non-live metadata row.

Status: pass with documented cleanup warning.

## Packet Materialization Status

Phase 15.2 materialized at least one non-streamer segment packet family.

Confirmed from `phase-15-2-segment-packet-materialization-report.md`:

- `sleeper_breakout_packets`: `0` before, `2` after.
- `sleeper_breakout_packets` for 2025 week 1 PPR: `0` before, `2` after.
- `sleeper_breakout_show` deterministic content brief was generated.
- `fraud_watch_packets` remains `0`.
- `trade_review_packets` remains `0` because `ENABLE_DEMO_TRADE_REVIEW` was not set.
- Demo claim grading was not run because `ENABLE_DEMO_CLAIM_GRADING` was not set.

Status: pass with expected empty-state blockers documented.

## Compat Staging Status

Phase 15.3 promoted only `USE_COMPAT_TRADE_PLAYER_HISTORY=true` to staging.

Confirmed:

- Production default remains false.
- Other compat flags remain false.
- Trade Lab shows `Trade player history source: compat_trade_player_history` when the flag is true.
- Source freshness and missing-data metadata are displayed when present in compat history rows.
- Legacy fallback remains available.
- Staging enablement and rollback commands are documented.

Feature flag defaults checked in an empty environment:

| Flag | Default |
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

Status: pass.

## Cloud Run Live Job Status

Phase 15.4 did not deploy or trigger a live Cloud Run Job.

Confirmed:

- Dry-run preview for only `validate-warehouse` was produced.
- No live Cloud Run Job was deployed.
- No live Cloud Run Job was triggered.
- No scheduler jobs were created.
- `cloud_run_job` validation passed: 8 passed, 0 failed.

Live test blockers:

- `gcloud` is not installed in the local shell.
- `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true` is not set.
- `CLOUD_RUN_JOBS_IMAGE` is not set.
- `CLOUD_RUN_JOB_SERVICE_ACCOUNT` is not set.

Status: pass for safe gating, NO-GO for live local execution.

## Merge Readiness Status

Phase 15.5 release package exists.

Confirmed:

- `docs/rebuild/validation/phase-15-5-merge-readiness-report.md` exists.
- `docs/rebuild/release-checklist.md` exists.
- `docs/rebuild/validation/phase-15-pr-summary-draft.md` exists.
- Changed files are classified for commit, careful review, or exclusion.
- No generated/cache files were found in current status.
- No secrets or local artifacts are slated for commit.

Status: pass with merge-review warning.

## Pigskin Safety Status

Confirmed:

- `execute_bigquery_sql` remains absent from Pigskin-visible tool declarations.
- `tests/test_pigskin_chat_schema.py` asserts `execute_bigquery_sql` is not present in the visible schema.
- `### Context Tool Protocol ###` remains in the Pigskin prompt content in `app.py`.
- `src/pigskin_chat_schema.py` defines blocked raw/source tables including `weekly_metrics`, `play_by_play`, `player_rosters`, `player_contracts`, `depth_charts`, `ngs_passing`, `ngs_rushing`, `ngs_receiving`, `ftn_charting`, `weekly_snap_counts`, `injury_reports`, and `market_values`.
- The Pigskin schema text instructs Pigskin to use curated mart/output tables and not raw/source tables.
- Tests passed.

Status: pass.

## Hard NO-GO Checks

| Check | Result |
| --- | --- |
| tests fail | no |
| `app.py` compile fails | no |
| Pigskin arbitrary SQL returns | no |
| raw/source tables exposed to Pigskin | no |
| secrets tracked | no |
| Firebase artifacts appear | no |
| production feature flags default unsafe | no |
| Cloud Run Jobs can trigger live by default | no |
| unexpected LLM calls | no |
| scraping introduced | no |
| unsafe fake production claims or packets inserted | no |

No hard NO-GO condition was found.

## Recommended Phase 16 Work

1. Install and authenticate `gcloud`, set `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true`, set `CLOUD_RUN_JOBS_IMAGE`, set or explicitly waive `CLOUD_RUN_JOB_SERVICE_ACCOUNT`, then rerun the narrow `validate-warehouse` live test.
2. Retry cleanup of `validate-warehouse-20260616T133114Z-5e7c51a8` after BigQuery streaming-buffer limits clear, using guarded predicates only.
3. Finish staging QA for `USE_COMPAT_TRADE_PLAYER_HISTORY=true`, then decide whether to promote to production.
4. Materialize a real `fraud_watch_packets` run once source rows support it.
5. Add real reviewed claim data before claim grading or Meatbag Accountability content.
6. Keep all other compatibility flags default false until their staged QA reports are complete.
7. Open the rebuild PR using `phase-15-pr-summary-draft.md` and review the `app.py` Trade Lab compat marker path carefully.

## Final Decision

GO WITH WARNINGS.

Phase 15 is safe to move into PR review. It is not a production deployment approval.
