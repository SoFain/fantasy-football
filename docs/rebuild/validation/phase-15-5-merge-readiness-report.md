# Phase 15.5 Merge Readiness Report

Date: 2026-06-16

Decision: GO WITH WARNINGS

## Scope

This report inventories the current rebuild worktree for merge review. It does not authorize deployment, migration application, Cloud Run Job triggers, scraping, or LLM calls.

Current branch:

```text
codex/phase-14-validation-footer
```

Upstream:

```text
origin/codex/phase-14-validation-footer
```

## Commands Run

```powershell
git status --short
git diff --stat
git diff --name-only
git diff --name-status
git ls-files --others --exclude-standard
git ls-files -d
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

## Tracked Modified Files

Keep and commit after review:

| File | Classification | Summary |
| --- | --- | --- |
| `Launch_Studio.bat` | keep and commit | Adds a commented local QA line for `USE_COMPAT_TRADE_PLAYER_HISTORY=true`; default remains off. |
| `app.py` | keep but review carefully | Adds a Trade Lab compat-source marker and renders compat metadata when `USE_COMPAT_TRADE_PLAYER_HISTORY=true`. Legacy fallback remains. |
| `deploy_guide.md` | keep and commit | Documents staging-only Cloud Run env var enablement and rollback for Trade Lab player history. |
| `docs/rebuild/claim-ledger-ui.md` | keep and commit | Adds Phase 15.1 claim ledger cleanup documentation. |
| `docs/rebuild/cloud-run-jobs.md` | keep and commit | Adds Phase 15.1 cleanup note and Phase 15.4 blocked live-test result. |
| `docs/rebuild/compat-rollout-status.md` | keep and commit | Documents Phase 15.3 staging promotion status and rollback. |
| `docs/rebuild/data-ops-cloud-run-jobs-rollout.md` | keep and commit | Adds Phase 15.1 cleanup note and Phase 15.4 live-test blocker. |
| `docs/rebuild/meatbag-claim-ledger.md` | keep and commit | Adds Phase 15.1 sample claim documentation note. |
| `docs/rebuild/projection-engine-v1.md` | keep and commit | Adds Phase 15.1 partial projection cleanup note. |
| `docs/rebuild/streamlit-compat-rollout.md` | keep and commit | Adds Trade Lab staging marker and metadata QA checks. |
| `docs/rebuild/validation/phase-14-validation-report.md` | keep and commit | Adds Phase 15.1 cleanup addendum. |
| `tests/test_streamlit_compat_rollout.py` | keep and commit | Adds coverage for the Trade Lab staging marker and metadata call. |

## Untracked Files

Keep and commit:

| File | Size | Classification | Summary |
| --- | ---: | --- | --- |
| `docs/rebuild/release-checklist.md` | 6,772 bytes | keep and commit | Release checklist for merge, staging, rollback, IAM, secrets, and feature flags. |
| `docs/rebuild/validation/phase-14-5-claim-ledger-sample-report.md` | 2,579 bytes | keep and commit | Standalone Phase 14.5 sample-claim report. |
| `docs/rebuild/validation/phase-15-2-segment-packet-materialization-report.md` | 7,200 bytes | keep and commit | Segment packet materialization report. |
| `docs/rebuild/validation/phase-15-3-trade-history-staging-promotion-report.md` | 3,883 bytes | keep and commit | Trade player history staging promotion report. |
| `docs/rebuild/validation/phase-15-4-live-validate-warehouse-job-report.md` | 4,685 bytes | keep and commit | Blocked live `validate-warehouse` job test report. |
| `docs/rebuild/validation/phase-15-5-merge-readiness-report.md` | 7,815 bytes | keep and commit | This merge readiness inventory and classification report. |
| `docs/rebuild/validation/phase-15-pr-summary-draft.md` | 6,057 bytes | keep and commit | PR summary draft for review and release planning. |

## Deleted Files

None.

## Generated Or Cache Files To Exclude

No generated/cache files appeared in tracked or untracked status.

Continue excluding:

- `venv/`
- `.venv/`
- `__pycache__/`
- `*.pyc`
- `dist/`
- `build/`
- `*.log`
- local BigQuery or service-account JSON files
- `.env` files
- private keys

## Docs Added Or Updated

Added:

- `docs/rebuild/validation/phase-14-5-claim-ledger-sample-report.md`
- `docs/rebuild/validation/phase-15-2-segment-packet-materialization-report.md`
- `docs/rebuild/validation/phase-15-3-trade-history-staging-promotion-report.md`
- `docs/rebuild/validation/phase-15-4-live-validate-warehouse-job-report.md`
- `docs/rebuild/validation/phase-15-5-merge-readiness-report.md`
- `docs/rebuild/release-checklist.md`
- `docs/rebuild/validation/phase-15-pr-summary-draft.md`

Updated:

- `deploy_guide.md`
- `docs/rebuild/claim-ledger-ui.md`
- `docs/rebuild/cloud-run-jobs.md`
- `docs/rebuild/compat-rollout-status.md`
- `docs/rebuild/data-ops-cloud-run-jobs-rollout.md`
- `docs/rebuild/meatbag-claim-ledger.md`
- `docs/rebuild/projection-engine-v1.md`
- `docs/rebuild/streamlit-compat-rollout.md`
- `docs/rebuild/validation/phase-14-validation-report.md`

## Migrations Added

None in the current worktree.

Migration state:

```text
No pending migrations.
```

## Validation SQL Added

None in the current worktree.

Validation dry-run discovers 149 validation files.

## Tests Added Or Updated

Updated:

- `tests/test_streamlit_compat_rollout.py`

Coverage added:

- Trade Lab staging marker is present.
- Compat metadata rendering call remains wired when the Trade Player History compat path is active.

## Source Modules Added

None in the current worktree.

## app.py Change Summary

`app.py` now stores the Trade Player History compat flag in a local variable inside Trade Lab, displays:

```text
Trade player history source: compat_trade_player_history
```

when the flag is true, and renders source freshness or missing-data metadata from compat history rows when available.

The legacy `weekly_metrics` fallback path remains in place and unchanged for default runtime behavior.

## Launch_Studio.bat Change Summary

`Launch_Studio.bat` now includes a commented local QA line:

```bat
REM set "USE_COMPAT_TRADE_PLAYER_HISTORY=true"
```

It is disabled by default.

## .gitignore Change Summary

No `.gitignore` changes are present in the current worktree.

## Secret And Artifact Check

Safety checker result: pass.

Additional scans found no tracked or untracked matches for:

- service account JSON patterns
- `.env` patterns
- private key patterns
- `.pem`, `.p12`, `.pfx`
- Firebase artifact names
- local generated/cache paths

No secrets or local artifacts are slated for commit.

## Test And Compile Status

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | pass |
| `python -m unittest discover tests` | 285 passed |
| `python -m py_compile app.py` | pass |
| `python -m compileall -q src scripts` | pass |
| `scripts/run_bigquery_migrations.py --list-pending` | no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | pass, 149 validation files discovered |

## Known Warnings

1. Live `validate-warehouse` Cloud Run Job test remains blocked locally because `gcloud`, `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST`, `CLOUD_RUN_JOBS_IMAGE`, and `CLOUD_RUN_JOB_SERVICE_ACCOUNT` are missing.
2. The local dry-run metadata row `validate-warehouse-20260616T133114Z-5e7c51a8` remains a known non-live cleanup warning until BigQuery streaming-buffer limits allow update.
3. Production defaults must remain off for all staged compatibility flags until separate approval.
4. Line-ending warnings appeared in `git diff` on Windows. No functional issue was observed.

## File Classification Summary

Keep and commit:

- All tracked modified files listed above.
- All untracked validation reports listed above.
- This merge readiness report.
- `docs/rebuild/release-checklist.md`.
- `docs/rebuild/validation/phase-15-pr-summary-draft.md`.

Keep but review carefully:

- `app.py`
- `tests/test_streamlit_compat_rollout.py`

Generated or do not commit:

- None found in current status.

Local-only or do not commit:

- None found in current status.

Unknown or manual review required:

- None found in current status.

## Final Recommendation

Proceed to PR review after staging all listed keep-and-commit files. Do not deploy, apply migrations, or enable production feature flags as part of the merge.
