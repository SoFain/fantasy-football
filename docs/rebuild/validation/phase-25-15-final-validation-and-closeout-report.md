# Phase 25.15 Final Validation And Closeout

Final decision: PHASE 25 CLOSEOUT PASS WITH WARNINGS

Generated: 2026-06-26T12:03:30Z

## Classifications

| Area | Classification |
| --- | --- |
| Production | PRODUCTION STABLE ALL FLAGS OFF |
| Trade Analyzer | STAGING VALIDATED, PRODUCTION DISABLED |
| Data Ops | PRODUCTION HARDENED, TRIGGERS DISABLED |

## Scope

This phase performed final Phase 25 validation and closeout after the Data Ops hardening production rollout and evidence commit.

No deployment was run. No rollback was run. No production feature flag was changed. No Trade Analyzer score flag was enabled. No Trade History compatibility flag was enabled. No Data Ops Cloud Run Job trigger or local subprocess gate was enabled. No Cloud Run Job was triggered. No Scheduler job was created. No ingestion, score materialization, LLM-backed action, Pigskin prompt, scraping, or Firebase action was run.

No Data Ops local subprocess control was clicked.

## Authorization Gate State

All checked gates were unset before and after validation.

| Gate | State |
| --- | --- |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

Temporary browser QA variables were also cleared:

| Variable | State |
| --- | --- |
| `STAGING_TARGET_URL` | unset |
| `STAGING_PROXY_PORT` | unset |
| `QA_BASE_URL` | unset |
| `QA_APP_PASSWORD` | unset |

## Git State

Latest commits:

```text
b3b0ec1 Document Data Ops hardening production rollout
22e3256 Gate Data Ops local subprocess controls
63149aa Clean up production warning noise
0001f47 Add Trade Analyzer score v0 and safe production rollout
ce0eb82 docs: prepare phase 17 production candidate plan
57ab102 docs: record current season fraud watch blocker
```

Git state before creating this report:

| Check | Result |
| --- | --- |
| Latest commit | `b3b0ec1 Document Data Ops hardening production rollout` |
| Staged files | none |
| `git status --short` count | `80` |
| Remaining untracked files | historical owner-review validation reports and the Phase 25.14A post-commit report |
| Generated or risky files staged | none |

This Phase 25.15 report was created after the git-state check and remains untracked.

## Local Checks

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | passed |
| `.\venv\Scripts\python.exe -m py_compile app.py` | passed |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | passed |
| `.\venv\Scripts\python.exe -m unittest discover tests` | passed, 352 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | passed, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | passed |

The unit test run emitted expected local test logs for schema coercion and ingest-only planning. The command exited 0.

## BigQuery Validations

| Pattern | Result |
| --- | --- |
| `cloud_run_job` | passed, 8 passed, 0 failed |
| `trade_player_scores` | passed, 11 passed, 0 failed |
| `compat_trade_player_scores` | passed, 2 passed, 0 failed |
| `market` | passed, 9 passed, 0 failed |
| `content_brief` | passed, 11 passed, 0 failed |
| `claim` | passed, 17 passed, 0 failed |
| `backtest` | passed, 11 passed, 0 failed |

Validation warnings were informational:

| Pattern | Warning |
| --- | --- |
| `claim` | identity coverage review row: `total_claim_player_rows=3`, `rows_missing_player_id_internal=1`, `identity_missing_rate=0.3333333333333333` |
| `claim` | claim ledger source count informational row |
| `claim` | draft claims missing review fields: `1` |
| `backtest` | latest backtest run informational row |
| `backtest` | backtest summary availability informational row |

No validation command failed.

## Production Service State

Read-only Cloud Run describe:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services describe nfl-studio-dashboard --project=fantasy-football-498121 --region=us-central1 --format=json
```

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Latest ready revision | `nfl-studio-dashboard-00077-2jp` |
| Latest created revision | `nfl-studio-dashboard-00077-2jp` |
| Traffic | `100 percent` to `nfl-studio-dashboard-00077-2jp` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Secret refs | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |
| Rollback baseline | `nfl-studio-dashboard-00076-p6s` |

`GEMINI_API_KEY` remains a Secret Manager reference. No secret value was printed.

## Production Flag State

| Flag | State |
| --- | --- |
| `USE_COMPAT_PLAYER_PROFILES` | `false` |
| `USE_COMPAT_SLEEPER_WATCH` | `false` |
| `USE_COMPAT_TRADE_ASSETS` | `false` |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `false` |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | `false` |
| `USE_BACKTEST_DASHBOARD` | `false` |
| `USE_CLAIM_LEDGER_UI` | `false` |
| `USE_CONTENT_BRIEF_REVIEW_UI` | `false` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `false` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `false` |
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |

Production risk, score, Trade History, Cloud Run job trigger, and local subprocess flags are safe.

## Health Results

Authenticated HTTP checks used a Cloud Run identity token. The token was not printed.

| Check | Result |
| --- | --- |
| `/_stcore/health` | `200`, body `ok` |
| `/` root | `200` |
| Streamlit shell present | yes |
| Root response contains `Traceback` | no |

## Browser Smoke

Browser smoke used Python Playwright `1.60.0` with local Chrome through a temporary websocket-aware auth proxy for the private Cloud Run service. The proxy process was stopped after the check. No generated browser artifact was committed.

| Check | Result |
| --- | --- |
| Login/session gate | pass, login form submitted |
| Pigskin Studio | pass, clicked and loaded |
| Show Prep | pass, clicked and loaded |
| Player Profiles | pass, clicked and loaded |
| Versus Finder | pass, clicked and loaded |
| Viewer Team Lab | pass, clicked and loaded |
| Trade Lab | pass, clicked and loaded |
| Data Ops | pass, clicked and loaded |
| Browser console errors | `0` |
| Browser console warnings | `0` |
| `Traceback`, `KeyError`, `NameError`, `pos_abb`, `rolling_3_week_ppr` | absent |
| `execute_bigquery_sql` visible in Pigskin | absent |
| Raw/source table list visible in Pigskin | absent |
| Trade History compatibility marker | absent |
| Trade Analyzer score UI | absent |
| Trade Lab AI outlook action | absent |

No LLM-backed action was clicked. No Pigskin prompt was submitted.

## Data Ops Hardening Verification

Focused Data Ops DOM inspection:

| Control | Result |
| --- | --- |
| `Trigger Cloud Run Job` | present but disabled |
| `Run Validation Sweep` | present but disabled |
| `Run Ingestion Pipeline` | present but disabled |
| `Generate Pigskin Rankings` | present but disabled |
| Scouting CSV file input | absent |
| Data Ops local gate copy | confirms `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false` and `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false` |
| Cloud Run job gate copy | confirms `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false` and `DATA_OPS_ALLOW_JOB_TRIGGER=false` |

Data Ops hardening remains effective. Visible mutating controls are disabled with production gates false.

## Log Review

Cloud Run log review for revision `nfl-studio-dashboard-00077-2jp`, freshness window `120m`:

| Metric | Count |
| --- | --- |
| Entries inspected | `362` |
| ERROR or higher severity | `0` |
| WARNING severity | `34` |
| Warning-like app text | `0` |
| Traceback-like text | `0` |
| `use_container_width` messages | `0` |
| BigQuery Storage fallback messages | `0` |
| BigQuery Storage import/install errors | `0` |
| Cloud Run Job trigger evidence | `0` |

The WARNING severity entries are unauthenticated Cloud Run IAM rejects from the Phase 25.13 failed local proxy setup. Authenticated health and browser checks passed after that.

Execution-pattern review:

| Pattern | Result |
| --- | --- |
| Local subprocess-like text | one deploy audit record containing configuration text, not subprocess execution |
| LLM-like text | same deploy audit record containing configuration text, not an LLM call |
| Cloud Run Job trigger text | none |

No hard startup error, runtime error, traceback, local subprocess execution, LLM action, or Cloud Run Job trigger was found.

## Job And Scheduler Status

| Check | Result |
| --- | --- |
| Latest Cloud Run Job execution | `validate-warehouse-gwbpg`, job `validate-warehouse`, created `2026-06-19T17:26:10.331740Z` |
| New Cloud Run Job execution since the prior proof | none found |
| Latest validate-warehouse proof | remains the prior successful proof execution |
| Cloud Scheduler jobs | Cloud Scheduler API is disabled |
| Scheduler API action | not enabled |
| Data Ops Cloud Run trigger flags | both false |
| Data Ops local subprocess flags | both false |

Cloud Scheduler enumeration cannot complete while the API is disabled. This remains a warning, not a rollback trigger.

## Rollback Status

Rollback was not performed. No hard rollback trigger was met.

Rollback target remains:

`nfl-studio-dashboard-00076-p6s`

Rollback command if needed later:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00076-p6s=100
```

## Remaining Warnings

- Historical Phase 17 through Phase 24 validation reports remain untracked for owner review.
- The Phase 25.14A post-commit report remains untracked. This Phase 25.15 report is also untracked after creation.
- Cloud Scheduler API is disabled, so Scheduler jobs cannot be enumerated without enabling that API. It was not enabled.
- The log window still contains unauthenticated IAM warning entries from the Phase 25.13 failed local proxy setup.
- Claim and backtest validation patterns returned informational review rows, but no failures.
- Data Ops shows some mutating controls as visible disabled buttons rather than fully hidden controls. They are not executable with production gates false.

## Recommended Phase 26 Work

1. Decide whether to commit Phase 25.14A and Phase 25.15 closeout reports as release evidence.
2. Clean up or archive historical untracked validation reports after owner review.
3. Keep production score flags and compatibility flags disabled until a separate production rollout is approved.
4. If needed, convert visible disabled Data Ops controls into fully hidden controls for cleaner production UI.
5. Leave Cloud Scheduler API disabled unless Scheduler rollout becomes an explicit requirement.

## Decision

Production is healthy on `nfl-studio-dashboard-00077-2jp` with all production risk, score, Trade History compatibility, Cloud Run trigger, and local subprocess flags false. Data Ops hardening remains effective. No rollback was required.

Final decision: PHASE 25 CLOSEOUT PASS WITH WARNINGS
