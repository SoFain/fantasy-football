# Phase 25.3 Production Warning Cleanup Report

Validation date: 2026-06-25 local.

## Final Decision

`WARNING CLEANUP READY`

Accepted production warning noise was cleaned up without changing feature exposure. No deployment, staging deploy, production flag change, Cloud Run Job trigger, Scheduler job creation, ingestion, score materialization, LLM-backed action, Pigskin prompt, scraping, Firebase artifact creation, or authorization gate change occurred.

## Starting State

Latest release commit before cleanup:

```text
0001f47 Add Trade Analyzer score v0 and safe production rollout
```

Authorization gates were unset:

| Gate | State |
| --- | --- |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | empty |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | empty |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | empty |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | empty |

## Files Changed

| File | Change |
| --- | --- |
| `app.py` | Replaced Streamlit `use_container_width=True` calls with `width="stretch"` for dataframes, Altair charts, and buttons. |
| `requirements.txt` | Added `google-cloud-bigquery-storage>=2.24.0`. |
| `docs/rebuild/validation/phase-25-3-production-warning-cleanup-report.md` | Added this cleanup report. |

## Streamlit Deprecation Cleanup

Installed Streamlit runtime inspected:

```text
streamlit 1.58.0
```

The local Streamlit signatures support the replacement `width="stretch"` for:

- `st.dataframe`
- `st.altair_chart`
- `st.button`
- `st.sidebar.button`

Cleanup:

- Replaced all runtime `use_container_width=True` calls in `app.py`.
- Confirmed no remaining `use_container_width` references in `app.py`, `src`, `tests`, or `requirements.txt`.
- Kept the intended full-width layout behavior by using `width="stretch"`.

No broad layout or feature behavior was changed.

## BigQuery Storage Dependency Decision

Decision:

```text
Add BigQuery Storage support.
```

Rationale:

- Production logs showed repeated non-blocking fallback warnings from the BigQuery client when fetching data with the REST endpoint.
- The app already depends on `google-cloud-bigquery`, `pyarrow`, and `db-dtypes`.
- Adding `google-cloud-bigquery-storage>=2.24.0` is the standard minimal runtime dependency for BigQuery Storage API dataframe fetch support.

Expected runtime and image impact:

- Future images will install the BigQuery Storage client package.
- BigQuery dataframe fetches can use BigQuery Storage where the client and permissions allow it.
- If BigQuery Storage is unavailable at runtime for permissions or environment reasons, app behavior should still fall back through the Google client path.

No Dockerfile behavior changed in this phase.

## Feature Exposure Verification

No feature flag code or deployment configuration was changed.

Verified exposure remains unchanged:

| Feature | State |
| --- | --- |
| Trade Analyzer score UI | still gated by `USE_TRADE_ANALYZER_SCORE_V0` and `USE_COMPAT_TRADE_PLAYER_SCORE` |
| Trade History compatibility | still gated by `USE_COMPAT_TRADE_PLAYER_HISTORY` |
| Data Ops Cloud Run Job trigger UI | still gated by `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` and `DATA_OPS_ALLOW_JOB_TRIGGER` |
| Claim Ledger UI | still gated by `USE_CLAIM_LEDGER_UI` |
| Content Brief Review UI | still gated by `USE_CONTENT_BRIEF_REVIEW_UI` |
| Backtest Dashboard | still gated by `USE_BACKTEST_DASHBOARD` |
| Sleeper Watch compatibility | still gated by `USE_COMPAT_SLEEPER_WATCH` |
| Trade Assets compatibility | still gated by `USE_COMPAT_TRADE_ASSETS` |
| Viewer Team Context compatibility | still gated by `USE_COMPAT_VIEWER_TEAM_CONTEXT` |

Safety checker also confirmed feature flags remain default off.

## Checks Run

| Command | Result |
| --- | --- |
| `echo $env:ALLOW_LIMITED_PRODUCTION_DEPLOY` | empty |
| `echo $env:ALLOW_TRADE_SCORE_MATERIALIZATION` | empty |
| `echo $env:ALLOW_PROJECTION_CONTEXT_REFRESH` | empty |
| `echo $env:ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | empty |
| `git status --short` | reviewed |
| `git log -1 --oneline` | `0001f47 Add Trade Analyzer score v0 and safe production rollout` |
| `rg -n "use_container_width" app.py src tests requirements.txt` | no matches |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 346 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass |

Safety checker details:

| Check | Result |
| --- | --- |
| `no_firebase_artifacts` | pass |
| `no_tracked_secret_files` | pass |
| `no_secret_content` | pass |
| `required_files_exist` | pass |
| `feature_flags_default_off` | pass |
| `pigskin_no_execute_bigquery_sql` | pass |
| `app_py_compiles` | pass |
| `src_scripts_compile` | pass |

Test note:

- Unit test output includes mocked load and pipeline execution messages from test fixtures.
- No live ingestion command was run in this phase.

## Remaining Warnings

- Historical Phase 17 through Phase 24 validation reports remain untracked for owner review.
- `pipeline_execution.log` remains tracked historical noise with no current diff.
- BigQuery Storage warning cleanup requires a future image build and deployment before production logs can prove the warning is gone.
- Streamlit deprecation warning cleanup requires a future image build and deployment before production logs can prove the warning is gone.

## Future Staging Deploy Recommendation

Recommended before any production image rebuild:

1. Build a new immutable staging image from this cleanup branch.
2. Deploy to staging with the same approved staging flag posture.
3. Confirm no `use_container_width` deprecation warnings appear in staging logs.
4. Confirm BigQuery Storage fallback warning is gone or document any remaining permission/environment reason for REST fallback.
5. Confirm all production risk and score flags remain false in production.

## Commit Status

This phase did not commit automatically. The cleanup is ready for owner review and a later explicit commit instruction.
