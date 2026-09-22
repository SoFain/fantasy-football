# Phase 24.2 Production Deploy Gate Report

Validation date: 2026-06-19

## Final Decision

`PRODUCTION DEPLOY BLOCKED`

Production deploy may not proceed to Phase 24.3. Phase 24.1 resolved the previous unknown live-proof state, but it resolved it as a failed proof, not a pass or formal waiver.

No production deploy, production flag change, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, ingestion, materialization, or Firebase artifact creation was performed in this phase.

## Gate Summary

| Gate | Status | Evidence |
| --- | --- | --- |
| Live `validate-warehouse` proof passed or waived | failed | Phase 24.1 decision is `LIVE VALIDATE-WAREHOUSE FAIL`. |
| Formal waiver complete | missing | No waiver was supplied. |
| Production deploy authorization | missing | `ALLOW_LIMITED_PRODUCTION_DEPLOY=<unset>`. |
| Production candidate exists | pass | Digest-pinned image exists in Artifact Registry. |
| Production rollback baseline exists | pass | Current production revision and traffic captured. |
| Safety checker | pass | No Firebase artifacts, tracked secrets, secret content, unsafe default flags, or Pigskin SQL regression. |
| Tests and compile | pass | Full tests, app compile, and src/scripts compile passed. |
| Pending migrations | pass | No pending migrations. |
| Validation dry-run | pass | Validation discovery completed. |

## Phase 24.1 Review

Phase 24.1 result:

`LIVE VALIDATE-WAREHOUSE FAIL`

The proof deployed/updated only `validate-warehouse` and triggered one execution, `validate-warehouse-qhwkq`, with the narrow `model_runs` pattern. The execution failed because the digest-pinned image did not contain `/app/scripts/run_bigquery_validations.py`, which is required by `src.job_runner.dispatch_validate_warehouse`.

Production remains blocked until:

1. the image or job runner path is fixed and a new live proof passes, or
2. a formal waiver is supplied with approver, accepted risk, release impact, and follow-up deadline.

## Preflight Results

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 343 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass, validation discovery completed |

## Candidate Image

Requested production candidate:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b
```

Artifact Registry verification:

| Field | Value |
| --- | --- |
| Digest | `sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b` |
| Fully qualified digest | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b` |
| Registry | `us-central1-docker.pkg.dev` |
| Repository | `nfl-studio-repo` |

Warning: Phase 24.1 proved this image is not sufficient for the live `validate-warehouse` job path because it lacks the expected script path.

## Production Baseline

Read-only command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services describe nfl-studio-dashboard --project=fantasy-football-498121 --region=us-central1 --format=json
```

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Current serving revision | `nfl-studio-dashboard-00074-26x` |
| Traffic split | `nfl-studio-dashboard-00074-26x:100%` |
| Current image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Secret references | `GEMINI_API_KEY:GEMINI_API_KEY` |
| Max scale | `20` |
| Ingress | `all` |

Secret values were not printed or committed.

## Production Risk Flag State

All required production risk flags are unset, which is treated as false by the app default-off feature flag path.

| Flag | Production state |
| --- | --- |
| `USE_COMPAT_PLAYER_PROFILES` | `<unset>` |
| `USE_COMPAT_SLEEPER_WATCH` | `<unset>` |
| `USE_COMPAT_TRADE_ASSETS` | `<unset>` |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `<unset>` |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | `<unset>` |
| `USE_BACKTEST_DASHBOARD` | `<unset>` |
| `USE_CLAIM_LEDGER_UI` | `<unset>` |
| `USE_CONTENT_BRIEF_REVIEW_UI` | `<unset>` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `<unset>` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `<unset>` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `<unset>` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `<unset>` |

Other production environment summary:

| Env var | State |
| --- | --- |
| `BQ_PROJECT` | `fantasy-football-498121` |
| `EXTERNAL_SEARCH_DAILY_LIMIT` | `10` |
| `EXTERNAL_SEARCH_MAX_RESULTS` | `3` |
| `EXTERNAL_SEARCH_PROVIDER` | `vertex_ai_search` |
| `GEMINI_API_KEY` | secret reference |
| `GEMINI_MODEL` | `gemini-3.5-flash` |
| `VERTEX_AI_SEARCH_ENGINE_ID` | `fantasy-football-search-engine` |

## Authorization State

```text
ALLOW_LIMITED_PRODUCTION_DEPLOY=[]
```

Production deployment is not authorized in this shell and is blocked by the failed live proof.

## Deploy Command Preview

This command is provided only as a future preview after the live proof blocker is fixed or formally waived. It was not executed.

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --update-env-vars=USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false,USE_TRADE_ANALYZER_SCORE_V0=false,USE_COMPAT_TRADE_PLAYER_SCORE=false `
  --update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest `
  --quiet
```

Preview assessment:

| Requirement | Status |
| --- | --- |
| digest-pinned image | pass |
| production risk flags false | pass |
| Trade History compatibility false | pass |
| Trade Analyzer score flags false | pass |
| Cloud Run Job trigger flags false | pass |
| Secret Manager reference preserved | pass |
| Scheduler jobs | none |

## Rollback Command

If a future deploy is approved and then fails, roll back to the current revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00074-26x=100
```

## Production Decision

`PRODUCTION DEPLOY BLOCKED`

Reasons:

1. Phase 24.1 live `validate-warehouse` proof failed.
2. No formal waiver exists.
3. `ALLOW_LIMITED_PRODUCTION_DEPLOY` is unset.
4. The candidate image exists, but the same image failed the live job proof due missing `/app/scripts/run_bigquery_validations.py`.

## Required Next Step

Fix the Cloud Run job image/path issue, rebuild a new digest-pinned candidate, rerun the live `validate-warehouse` proof with a narrow pattern, and rerun this gate. Do not proceed to production deploy until that proof passes or a formal waiver is accepted.
