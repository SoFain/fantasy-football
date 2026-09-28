# Phase 25.6 Production Warning Cleanup Deploy Gate Report

Final decision: APPROVED FOR PRODUCTION WARNING CLEANUP DEPLOY ALL FLAGS OFF

## Scope

Phase 25.6 was a gate and decision phase only for the warning-cleanup production candidate.

No production deploy was run. No staging deploy was run. No production feature flags were changed. No Trade Analyzer score flags were enabled in production. No Trade History compatibility was enabled in production. No Cloud Run Jobs were triggered. No Scheduler jobs were created. No ingestion, score materialization, LLM-backed action, Pigskin prompt, scraping, Firebase artifact creation, or authorization gate change occurred.

## Authorization State

Authorization gates checked:

| Gate | State |
| --- | --- |
| ALLOW_LIMITED_PRODUCTION_DEPLOY | unset |
| ALLOW_TRADE_SCORE_MATERIALIZATION | unset |
| ALLOW_PROJECTION_CONTEXT_REFRESH | unset |
| ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST | unset |

Deploy authorization is intentionally unset in this gate phase. A separate deploy phase must set any required deploy gate only inside that deploy command/session.

## Candidate Image

Phase 25.5 final decision:

```text
WARNING CLEANUP PRODUCTION CANDIDATE READY
```

Candidate image verified in Artifact Registry:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4
```

Artifact Registry verification:

| Field | Value |
| --- | --- |
| Registry | `us-central1-docker.pkg.dev` |
| Repository | `nfl-studio-repo` |
| Digest | `sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4` |
| Fully qualified digest | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4` |

Candidate source commit:

```text
63149aa3d8167ed3434a0ea02b8800c475c9dd5a
Clean up production warning noise
```

## Staging Evidence Review

Phase 25.4 final decision:

```text
STAGING WARNING CLEANUP PASS WITH WARNINGS
```

Staging evidence accepted for this gate:

| Check | Result |
| --- | --- |
| Staging deploy succeeded | yes |
| Staging health passed | yes |
| `use_container_width` deprecation messages | 0 |
| BigQuery Storage fallback messages | 0 |
| BigQuery Storage import/install errors | 0 |
| Production remained untouched during staging deploy | yes |

Staging warnings reviewed:

1. Browser smoke did not reliably capture the final Trade Lab score UI marker text, but authenticated app load, clickable tab labels, enabled staging score flags, and no errors were observed.
2. Staging warning-severity logs were unauthenticated probe attempts against the private service, not app runtime warnings.
3. Cloud Scheduler API was disabled, so scheduler enumeration was blocked without enabling the API. No Scheduler job creation command was run.

These warnings do not block an all-flags-off production warning-cleanup deploy because the production deploy preview keeps score flags, Trade History compatibility, and Data Ops job trigger flags false.

## Preflight Results

All required preflight checks passed with process exit code 0:

| Check | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 346 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass |

Note: the test suite printed expected mocked job and pipeline logs. The unittest process exited 0. No live ingestion or materialization command was run.

## Production Baseline

Read-only Cloud Run describe confirmed:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Current revision | `nfl-studio-dashboard-00075-x7p` |
| Traffic | 100 percent to `nfl-studio-dashboard-00075-x7p` |
| Current image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Secret references | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |

## Current Production Flag State

| Flag | Current value |
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

Production is currently in the expected all-risk-flags-off state.

## Deploy Command Preview

Do not run this command in this gate phase. It is the preview for a separate authorized deploy phase.

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4 `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --update-env-vars=USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false,USE_TRADE_ANALYZER_SCORE_V0=false,USE_COMPAT_TRADE_PLAYER_SCORE=false `
  --update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest `
  --no-allow-unauthenticated `
  --quiet
```

The preview:

| Requirement | Result |
| --- | --- |
| Uses warning-cleanup digest-pinned image | yes |
| Keeps all production risk flags false | yes |
| Keeps Trade Analyzer score flags false | yes |
| Keeps Trade History compatibility false | yes |
| Keeps Data Ops job trigger flags false | yes |
| Preserves Secret Manager reference for `GEMINI_API_KEY` | yes |
| Creates Scheduler jobs | no |
| Triggers Cloud Run Jobs | no |

## Rollback Command

If a later deploy phase fails smoke checks, rollback should return traffic to the current baseline revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00075-x7p=100
```

## Remaining Warnings

1. Production deploy authorization is unset by design in this gate phase. The deploy itself must occur only in a separate authorized phase.
2. The working tree still contains untracked historical validation reports retained for owner review.
3. Phase 25.4 staging browser smoke had marker-capture limitations, but no runtime errors or warning-cleanup regressions were found.

## Decision

The warning-cleanup production candidate may proceed to a separate production deploy phase with all production risk flags false.

No deploy was performed in Phase 25.6.
