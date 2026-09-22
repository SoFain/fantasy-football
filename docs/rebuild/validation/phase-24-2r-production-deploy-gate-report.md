# Phase 24.2R Production Deploy Gate Report

Validation date: 2026-06-19

## Final Decision

`APPROVED FOR PRODUCTION DEPLOY ALL FLAGS OFF`

Production deployment may proceed only in a separate Phase 24.3 deploy prompt, and only if explicit deployment authorization is supplied there. No production deploy was run in this phase.

The previous production blocker from Phase 24.2 is resolved. Phase 24.1B reran the live `validate-warehouse` proof with the fixed digest-pinned image and completed successfully with warnings.

## Phase 24.1B Proof Status

Phase 24.1B final decision:

```text
LIVE VALIDATE-WAREHOUSE PASS WITH WARNINGS
```

Accepted warning:

- `scripts/deploy_cloud_run_jobs.ps1` produced a valid dry-run preview, but its live invocation failed in this local PowerShell environment due gcloud argument handling through `gcloud.ps1`;
- the live proof used the equivalent full-path `gcloud.cmd` command for only `validate-warehouse`;
- exactly one narrow live proof was triggered;
- execution `validate-warehouse-gwbpg` completed successfully;
- validation pattern was `model_runs`;
- metadata validation passed, `8 passed, 0 failed`;
- no Scheduler job, broad job deploy, production deploy, staging deploy, LLM call, scrape, or Firebase artifact was created.

The warning does not block this production deploy gate because the live proof itself passed and the production deploy preview does not rely on the affected Cloud Run Job deployment script.

## Preflight Results

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 346 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass |

## Fixed Production Candidate

Use the fixed digest-pinned image from Phase 24.1A:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29
```

Artifact Registry verification:

| Field | Value |
| --- | --- |
| Digest | `sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| Exists in Artifact Registry | yes |
| Old failed digest avoided | `sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b` |

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
| Secret references | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |
| Max scale | `20` |
| Ingress | `all` |

Secret values were not printed.

## Production Risk Flag State

All required production risk flags are unset in the current production baseline, which is treated as false by the app default-off feature flag path.

| Flag | Current production state | Required deploy state |
| --- | --- | --- |
| `USE_COMPAT_PLAYER_PROFILES` | `<unset>` | `false` |
| `USE_COMPAT_SLEEPER_WATCH` | `<unset>` | `false` |
| `USE_COMPAT_TRADE_ASSETS` | `<unset>` | `false` |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `<unset>` | `false` |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | `<unset>` | `false` |
| `USE_BACKTEST_DASHBOARD` | `<unset>` | `false` |
| `USE_CLAIM_LEDGER_UI` | `<unset>` | `false` |
| `USE_CONTENT_BRIEF_REVIEW_UI` | `<unset>` | `false` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `<unset>` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `<unset>` | `false` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `<unset>` | `false` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `<unset>` | `false` |

Other production environment summary:

| Env var | State |
| --- | --- |
| `BQ_PROJECT` | `fantasy-football-498121` |
| `EXTERNAL_SEARCH_DAILY_LIMIT` | `10` |
| `EXTERNAL_SEARCH_MAX_RESULTS` | `3` |
| `EXTERNAL_SEARCH_PROVIDER` | `vertex_ai_search` |
| `GEMINI_API_KEY` | Secret Manager reference |
| `GEMINI_MODEL` | `gemini-3.5-flash` |
| `VERTEX_AI_SEARCH_ENGINE_ID` | `fantasy-football-search-engine` |

## Authorization State

Current shell state:

```text
ALLOW_LIMITED_PRODUCTION_DEPLOY=
```

This is expected for Phase 24.2R. Production deploy was not authorized or executed here. Phase 24.3 must require explicit `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` before executing any deploy.

## Deploy Command Preview

This command was not executed.

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29 `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --update-env-vars=USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false,USE_TRADE_ANALYZER_SCORE_V0=false,USE_COMPAT_TRADE_PLAYER_SCORE=false `
  --update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest `
  --quiet
```

Preview assessment:

| Requirement | Status |
| --- | --- |
| Uses fixed digest-pinned image | pass |
| Avoids old failed digest | pass |
| Production risk flags false | pass |
| Trade History compatibility false | pass |
| Trade Analyzer score flags false | pass |
| Cloud Run Job trigger flags false | pass |
| Secret Manager reference preserved | pass |
| Scheduler jobs | none |

## Rollback Command

If Phase 24.3 is approved and then fails, roll back traffic to the current baseline revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00074-26x=100
```

## Production Decision

`APPROVED FOR PRODUCTION DEPLOY ALL FLAGS OFF`

Reasoning:

1. Phase 24.1B live `validate-warehouse` proof passed with an accepted script warning.
2. The fixed digest-pinned production candidate exists in Artifact Registry.
3. Safety checker passed.
4. Tests passed.
5. App and source/script compilation passed.
6. No migrations are pending.
7. Validation dry-run passed.
8. Current production risk flags are safe.
9. The deploy preview pins all production risk flags and score flags to `false`.
10. Rollback to the current production revision is documented.

## Disallowed In This Phase

The following were not run:

- production deploy;
- staging deploy;
- production feature flag enablement;
- Trade History compatibility in production;
- Trade Analyzer score flags in production;
- Cloud Run Job triggers;
- Scheduler jobs;
- LLM calls;
- scrape;
- Firebase artifact creation.

## Required Phase 24.3 Gate

Phase 24.3 may execute the previewed production deploy only if:

- it explicitly confirms this report decision;
- `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` is set in that deploy phase;
- it uses the fixed digest-pinned image above;
- all production risk flags and score flags remain `false`;
- it performs production smoke tests and rolls back to `nfl-studio-dashboard-00074-26x` if hard checks fail.
