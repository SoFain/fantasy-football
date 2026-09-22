# Phase 25.4 Staging Warning Cleanup Deploy Report

Final decision: STAGING WARNING CLEANUP PASS WITH WARNINGS

## Scope

Phase 25.4 built and deployed the Phase 25.3 warning-cleanup changes to staging only.

No production deploy was run. No production flags were changed. No Cloud Run Jobs were triggered. No Scheduler jobs were created. No ingestion, score materialization, LLM-backed action, Pigskin prompt, scraping, Firebase artifact creation, or commit was performed.

## Authorization Gates

Checked before staging work:

| Gate | State |
| --- | --- |
| ALLOW_LIMITED_PRODUCTION_DEPLOY | unset |
| ALLOW_TRADE_SCORE_MATERIALIZATION | unset |
| ALLOW_PROJECTION_CONTEXT_REFRESH | unset |
| ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST | unset |

Temporary browser identity token material was removed after the staging smoke check.

## Git State

Latest committed release:

```text
0001f47 Add Trade Analyzer score v0 and safe production rollout
```

Phase 25.3 cleanup changes were present but not committed:

| File | State |
| --- | --- |
| app.py | modified, Streamlit width cleanup |
| requirements.txt | modified, BigQuery Storage dependency added |
| docs/rebuild/validation/phase-25-3-production-warning-cleanup-report.md | untracked report |

Historical untracked validation reports remain for owner review.

## Pre-build Checks

All required checks passed before the build:

| Check | Result |
| --- | --- |
| scripts/check_deployment_safety.py | pass |
| py_compile app.py | pass |
| compileall src scripts | pass |
| unittest discover tests | pass, 346 tests |
| run_bigquery_migrations.py --list-pending | pass, no pending migrations |
| run_bigquery_validations.py --dry-run | pass |

## Warning Cleanup Verification

| Item | Result |
| --- | --- |
| `rg -n "use_container_width" app.py src tests requirements.txt` | no matches |
| requirements includes `google-cloud-bigquery-storage>=2.24.0` | yes |
| Cloud Build installed BigQuery Storage package | yes, `google-cloud-bigquery-storage-2.39.0` |
| Image still includes validate-warehouse script path | yes, build copied `scripts/run_bigquery_validations.py` and `bigquery/validations/` |

## Build Result

Build command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' builds submit --project=fantasy-football-498121 --config=cloudbuild.yaml --substitutions="_IMAGE_TAG=staging-0001f478cce7-20260626T031326Z,_COMMIT_HASH=0001f478cce7,_VERSION_LABEL=staging-0001f478cce7-20260626T031326Z" .
```

| Field | Value |
| --- | --- |
| Build ID | `efa2b746-6616-4ef5-a60d-2303adc80b7d` |
| Build status | `SUCCESS` |
| Image tag | `staging-0001f478cce7-20260626T031326Z` |
| Image URI | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-0001f478cce7-20260626T031326Z` |
| Digest | `sha256:5b668d71b30d84622fb032b0f8ac0c099a353c583228838df24bf6851f477df3` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b668d71b30d84622fb032b0f8ac0c099a353c583228838df24bf6851f477df3` |

## Staging Deploy Result

Deploy command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b668d71b30d84622fb032b0f8ac0c099a353c583228838df24bf6851f477df3 `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --update-env-vars=USE_COMPAT_TRADE_PLAYER_HISTORY=true,USE_TRADE_ANALYZER_SCORE_V0=true,USE_COMPAT_TRADE_PLAYER_SCORE=true,USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false `
  --update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest `
  --no-allow-unauthenticated `
  --quiet
```

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard-staging` |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| Previous revision | `nfl-studio-dashboard-staging-00018-cpz` |
| New revision | `nfl-studio-dashboard-staging-00019-rmj` |
| Traffic | 100 percent to `nfl-studio-dashboard-staging-00019-rmj` |
| URL | `https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b668d71b30d84622fb032b0f8ac0c099a353c583228838df24bf6851f477df3` |
| Secret refs | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |

## Staging Flag State

| Flag | Value |
| --- | --- |
| USE_COMPAT_TRADE_PLAYER_HISTORY | `true` |
| USE_TRADE_ANALYZER_SCORE_V0 | `true` |
| USE_COMPAT_TRADE_PLAYER_SCORE | `true` |
| USE_COMPAT_PLAYER_PROFILES | `false` |
| USE_COMPAT_SLEEPER_WATCH | `false` |
| USE_COMPAT_TRADE_ASSETS | `false` |
| USE_COMPAT_VIEWER_TEAM_CONTEXT | `false` |
| USE_BACKTEST_DASHBOARD | `false` |
| USE_CLAIM_LEDGER_UI | `false` |
| USE_CONTENT_BRIEF_REVIEW_UI | `false` |
| USE_CLOUD_RUN_JOBS_FOR_DATA_OPS | `false` |
| DATA_OPS_ALLOW_JOB_TRIGGER | `false` |

## Health And Browser Smoke

Authenticated HTTP results:

| Check | Result |
| --- | --- |
| `/_stcore/health` | 200, `ok` |
| `/` | 200 |
| Streamlit shell present | yes |
| Traceback in root response | no |

Browser smoke used a temporary local proxy with a Cloud Run identity token because the staging service is private.

| Check | Result |
| --- | --- |
| Login/session gate | pass |
| Main app tabs rendered | pass |
| Pigskin Studio tab text present and clickable | pass |
| Show Prep tab text present and clickable | pass |
| Player Profiles tab text present and clickable | pass |
| Versus Finder tab text present and clickable | pass |
| Viewer Team Lab tab text present and clickable | pass |
| Trade Lab tab text present and clickable | pass |
| Data Ops tab text present and clickable | pass |
| Data Ops job trigger gating text present | pass |
| Browser console errors | 0 |
| Browser console warnings | 0 |
| Traceback, `KeyError`, `NameError`, `pos_abb`, or `rolling_3_week_ppr` | none observed |

Warning: the compact automated browser pass confirmed authenticated app load and clickable tab labels, but it did not reliably surface the Trade Lab score UI marker or score source marker in the final text snapshot. Treat this as a staging smoke coverage warning, not as a functional regression, because the score flags are enabled and no errors or tracebacks appeared.

## Staging Log Review

Log filter:

```text
resource.type="cloud_run_revision" AND resource.labels.service_name="nfl-studio-dashboard-staging" AND resource.labels.revision_name="nfl-studio-dashboard-staging-00019-rmj"
```

| Metric | Count |
| --- | ---: |
| Log entries inspected | 366 |
| ERROR severity | 0 |
| WARNING severity | 18 |
| Traceback-like text | 0 |
| `use_container_width` deprecation messages | 0 |
| BigQuery Storage fallback messages | 0 |
| BigQuery Storage import/install errors | 0 |
| Startup hard errors | 0 |
| Runtime hard errors | 0 |

The warning-severity logs sampled were unauthenticated request warnings from earlier private-service probe attempts with an empty Authorization header. They were not app runtime warnings and did not include Streamlit deprecation noise or BigQuery Storage fallback text.

## Jobs And Scheduler Status

No Cloud Run Job trigger command was run in this phase. A read-only `validate-warehouse` executions list returned existing executions only.

Cloud Scheduler API is disabled for the project, so the read-only scheduler list command could not enumerate jobs without enabling the API. The API was not enabled and no Scheduler job was created.

## Production Untouched Verification

Read-only production describe confirmed the expected production state:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00075-x7p` |
| Traffic | 100 percent to `nfl-studio-dashboard-00075-x7p` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |

Production flag state:

| Flag | Value |
| --- | --- |
| USE_COMPAT_PLAYER_PROFILES | `false` |
| USE_COMPAT_SLEEPER_WATCH | `false` |
| USE_COMPAT_TRADE_ASSETS | `false` |
| USE_COMPAT_TRADE_PLAYER_HISTORY | `false` |
| USE_COMPAT_VIEWER_TEAM_CONTEXT | `false` |
| USE_BACKTEST_DASHBOARD | `false` |
| USE_CLAIM_LEDGER_UI | `false` |
| USE_CONTENT_BRIEF_REVIEW_UI | `false` |
| USE_CLOUD_RUN_JOBS_FOR_DATA_OPS | `false` |
| DATA_OPS_ALLOW_JOB_TRIGGER | `false` |
| USE_TRADE_ANALYZER_SCORE_V0 | `false` |
| USE_COMPAT_TRADE_PLAYER_SCORE | `false` |

## Remaining Warnings

1. Browser smoke did not produce a reliable final text marker for the Trade Lab score UI or score source marker, despite authenticated app load, clickable Trade Lab label, score flags enabled, and no errors.
2. Staging logs include warning-severity entries caused by unauthenticated probe attempts against the private service.
3. Cloud Scheduler API is disabled, so scheduler enumeration was blocked without enabling the API. No scheduler creation command was run.

## Commit And Production Recommendation

The warning cleanup is ready for owner review and commit as a follow-up to the conservative release package.

A future production cleanup deploy is recommended only after:

1. The Phase 25.3 cleanup files and this staging evidence are reviewed.
2. The cleanup changes are committed.
3. A clean digest-pinned production candidate is built from that reviewed source.
4. The normal all-flags-off production gate is rerun.
