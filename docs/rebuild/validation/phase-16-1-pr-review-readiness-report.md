# Phase 16.1 PR Review Readiness Report

Final decision: READY TO OPEN PR

Date: 2026-06-16

Branch: `codex/phase-14-validation-footer`

## Scope

Phase 16.1 reviewed the Phase 15 final state and prepared the rebuild branch for pull request review. No deployment, migration application, live Cloud Run Job trigger, scheduler creation, scraping, Firebase artifact creation, or LLM call was performed.

## Commands Run

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
git diff --check
```

## Test Status

| Check | Result |
| --- | --- |
| Deployment safety checker | pass |
| Unit tests | 285 passed, 0 failed |
| `app.py` compile | pass |
| `src` and `scripts` compile | pass |
| Pending migrations | none |
| Validation dry-run | pass, 149 validation files discovered |
| Diff whitespace check | pass, with Windows line-ending warnings only |

## Safety Status

Confirmed:

- Phase 15 final decision is `GO WITH WARNINGS`.
- Phase 15 reported no blockers.
- No Firebase artifacts were introduced.
- No tracked secrets or service account JSON files were detected by the safety checker.
- Pigskin arbitrary SQL remains removed.
- `execute_bigquery_sql` is not present in Pigskin-visible tool schema tests.
- Pigskin raw/source table blockers remain in `src/pigskin_chat_schema.py`.
- `### Context Tool Protocol ###` remains present in the Pigskin prompt.
- Production feature flags remain default false.
- Cloud Run live job triggers remain gated and default off.

## Changed-File Review Status

### `app.py`

Reviewed Trade Lab compatibility staging diff.

Status: pass.

Findings:

- `USE_COMPAT_TRADE_PLAYER_HISTORY` is evaluated into `trade_history_uses_compat`.
- The staging marker appears only when that flag is true.
- The compat path still calls `query_compat_trade_player_history()`.
- The legacy `weekly_metrics` fallback remains available.
- Source freshness and missing-data metadata render only for compat history rows.
- No new raw/source UI read path was introduced by this diff.

### `tests/test_streamlit_compat_rollout.py`

Status: pass.

Findings:

- Existing default-false flag tests remain.
- Existing compat helper raw-source exclusion tests remain.
- New test verifies the Trade Lab staging marker and metadata rendering call.

### `deploy_guide.md`

Status: pass.

Findings:

- Documents staging-only enablement for `USE_COMPAT_TRADE_PLAYER_HISTORY=true`.
- Documents rollback by removing that env var.
- Does not document production default changes.
- Does not enable other `USE_COMPAT_*` flags.

### `docs/rebuild/release-checklist.md`

Status: pass.

Findings:

- Captures test, migration, validation, Pigskin safety, feature flag, Cloud Run Job trigger, known warning, staging, production, rollback, Secret Manager, and IAM requirements.
- Explicitly says production is not approved by this package.

### `docs/rebuild/validation/phase-15-5-merge-readiness-report.md`

Status: pass.

Findings:

- Classifies tracked and untracked files.
- Marks `app.py` and tests for careful review.
- Confirms no deleted files, no `.gitignore` changes, no generated/cache files, and no secrets or local artifacts slated for commit.

## Phase 15 State Confirmation

Confirmed:

- Phase 14.5 standalone report exists.
- Phase 15.2 packet materialization report exists.
- Phase 15.3 staging promotion report exists.
- Phase 15.4 live job test report exists and classifies the local live path as NO-GO.
- Phase 15.5 merge readiness report exists.
- Release checklist exists.
- PR summary draft exists and was updated for the full rebuild scope.

## Feature Flag Status

Defaults remain false:

- `USE_COMPAT_PLAYER_PROFILES`
- `USE_COMPAT_SLEEPER_WATCH`
- `USE_COMPAT_TRADE_ASSETS`
- `USE_COMPAT_TRADE_PLAYER_HISTORY`
- `USE_COMPAT_VIEWER_TEAM_CONTEXT`
- `USE_BACKTEST_DASHBOARD`
- `USE_CLAIM_LEDGER_UI`
- `USE_CONTENT_BRIEF_REVIEW_UI`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS`
- `DATA_OPS_ALLOW_JOB_TRIGGER`

Only staging documentation enables:

- `USE_COMPAT_TRADE_PLAYER_HISTORY=true`

## PR Title Suggestion

`[codex] Rebuild platform governance and staged Trade Lab compatibility path`

## PR Summary

Use:

- `docs/rebuild/validation/phase-15-pr-summary-draft.md`

The draft includes:

- overview
- architecture
- major changes
- safety controls
- feature flags
- validations
- known warnings
- staging rollout plan
- rollback plan
- review focus

## Known Warnings

1. Live `validate-warehouse` Cloud Run Job testing remains blocked locally because `gcloud`, `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true`, `CLOUD_RUN_JOBS_IMAGE`, and `CLOUD_RUN_JOB_SERVICE_ACCOUNT` are missing.
2. Local dry-run metadata row `validate-warehouse-20260616T133114Z-5e7c51a8` remains a known non-live cleanup warning until BigQuery streaming-buffer limits allow update.
3. Claim ledger demo rows are draft-only and intentionally include one unresolved demo row.
4. `USE_COMPAT_TRADE_PLAYER_HISTORY=true` is approved for staging only, not production.
5. Other compatibility flags remain default false until separate staged QA.

## Files Needing Human Review

Review these carefully in the PR:

- `app.py`
- `tests/test_streamlit_compat_rollout.py`
- `deploy_guide.md`
- `docs/rebuild/release-checklist.md`
- `docs/rebuild/validation/phase-15-5-merge-readiness-report.md`
- `docs/rebuild/validation/phase-15-pr-summary-draft.md`

## Final Decision

READY TO OPEN PR.

No fixes are required before opening the PR.
