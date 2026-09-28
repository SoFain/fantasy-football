# Phase 23.10 Production Deploy Gate Report

Date: 2026-06-19

## Final Decision

`PRODUCTION DEPLOY BLOCKED`

Production deploy is not approved. The live `validate-warehouse` proof remains blocked and no formal waiver exists. `ALLOW_LIMITED_PRODUCTION_DEPLOY` is also unset in this process.

No production deploy, staging deploy, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, or Firebase artifact creation was performed.

## Gate Summary

| Gate | Status | Evidence |
| --- | --- | --- |
| Live `validate-warehouse` proof passed or waived | blocked | Phase 23.8 decision is `LIVE VALIDATE-WAREHOUSE STILL BLOCKED` |
| Formal waiver complete | missing | No approver, reason, exact risk, release impact, follow-up deadline, or production permission supplied |
| Production deploy authorization | missing | `ALLOW_LIMITED_PRODUCTION_DEPLOY=<unset>` |
| Production candidate exists | pass with warnings | Phase 23.9 built a digest-pinned candidate from reviewed dirty release state |
| Release package accepted | pass with warnings | Phase 23.1 decision is `RELEASE PACKAGE READY WITH WARNINGS` |
| Safety checker | pass | Current Phase 23.10 preflight |
| Tests | pass | Current Phase 23.10 preflight, 343 tests |
| App compile | pass | Current Phase 23.10 preflight |
| `src` and `scripts` compile | pass | Current Phase 23.10 preflight |
| Pending migrations | pass | No pending migrations |
| Validation dry-run | pass | 160 validation files discovered |

## Live Proof Or Waiver Status

Phase 23.8 result:

```text
LIVE VALIDATE-WAREHOUSE STILL BLOCKED
```

Blocking details:

- `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` was unset.
- `CLOUD_RUN_JOBS_IMAGE` was unset.
- `CLOUD_RUN_JOB_SERVICE_ACCOUNT` was unset.
- `CLOUD_RUN_PROJECT` was unset.
- `CLOUD_RUN_REGION` was unset.
- `BQ_PROJECT` was unset.
- `BQ_DATASET` was unset.
- No waiver was supplied.

Production cannot proceed until the live proof passes or a formal waiver is supplied and accepted.

## Production Candidate

Phase 23.9 candidate:

| Field | Value |
| --- | --- |
| Decision | `CLEAN PRODUCTION CANDIDATE BUILT WITH WARNINGS` |
| Git short SHA | `ce0eb82eef63` |
| Image tag | `prod-candidate-ce0eb82eef63-20260619T041320Z` |
| Build ID | `4158cf71-6fbe-4a19-9252-0b8c0dc59cff` |
| Build status | `SUCCESS` |
| Digest | `sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b` |

Candidate warning:

- Built from a reviewed dirty release package, not from a clean Git commit.

## Release Package

Phase 23.1 result:

```text
RELEASE PACKAGE READY WITH WARNINGS
```

Release package warning:

- Many Phase 17 through Phase 23 docs and release evidence files remain untracked and require human review before commit.
- Generated artifacts under `output/` are excluded by `.gitignore`.
- `pipeline_execution.log` remains tracked but unchanged and should not be included in this release package.

## Current Preflight

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:

| Check | Result |
| --- | --- |
| Deployment safety | pass |
| Unit tests | pass, 343 tests |
| `app.py` compile | pass |
| `src` and `scripts` compile | pass |
| Pending migrations | none |
| Validation dry-run | pass, 160 validation files discovered |

Safety checker details:

| Check | Result |
| --- | --- |
| No Firebase artifacts | pass |
| No tracked secret files | pass |
| No detected secret content | pass |
| Required files exist | pass |
| Feature flags default off | pass |
| Pigskin `execute_bigquery_sql` absent | pass |
| `app.py` compiles | pass |
| `src` and `scripts` compile | pass |

Unit test output included existing mocked job, load, pipeline, and ranking logs. No live ingestion, live Cloud Run Job, production deploy, scrape, or LLM call was run by this phase.

## Authorization State

| Gate | Required | Observed |
| --- | --- | --- |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | `true` | `<unset>` |

Because authorization is unset, this phase is decision and preview only.

## Production Baseline

Read-only production describe:

| Field | Value |
| --- | --- |
| service | `nfl-studio-dashboard` |
| project | `fantasy-football-498121` |
| region | `us-central1` |
| current revision | `nfl-studio-dashboard-00074-26x` |
| current image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2` |
| traffic | 100 percent to `nfl-studio-dashboard-00074-26x` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| secret refs | `GEMINI_API_KEY` |

Current production risk flag state:

| Flag | Observed | Effective state |
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
| `USE_TRADE_ANALYZER_SCORE_V0` | unset | false |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | unset | false |

## Rollback Command

If a future approved deploy occurs, rollback to the current baseline with:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard --project=fantasy-football-498121 --region=us-central1 --to-revisions nfl-studio-dashboard-00074-26x=100
```

## Deploy Preview

This command was not run. It is a preview only and remains blocked until live proof or waiver and production deploy authorization are satisfied.

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --update-env-vars=USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false,USE_TRADE_ANALYZER_SCORE_V0=false,USE_COMPAT_TRADE_PLAYER_SCORE=false `
  --update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest `
  --no-allow-unauthenticated `
  --quiet
```

Deploy preview properties:

| Requirement | Status |
| --- | --- |
| digest-pinned image | pass |
| all compatibility flags false | pass |
| Trade Analyzer score flags false | pass |
| Cloud Run Job trigger flags false | pass |
| Secret Manager binding preserved | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |
| Scheduler jobs created | no |
| Cloud Run Jobs triggered | no |

## Production Decision

`PRODUCTION DEPLOY BLOCKED`

Reason:

1. Live `validate-warehouse` proof is still blocked.
2. No formal waiver exists.
3. `ALLOW_LIMITED_PRODUCTION_DEPLOY` is unset.

The digest-pinned candidate is available for a future approved deploy gate, but this phase does not approve production.

## Acceptance Criteria

| Criterion | Status |
| --- | --- |
| Production decision explicit | pass |
| No deploy unless authorized | pass |
| All flags false if future deploy approved | pass in preview |
| No Firebase artifacts | pass |
