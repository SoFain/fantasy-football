# Phase 25.12 Production Data Ops Hardening Deploy Gate

Final decision: APPROVED FOR PRODUCTION DATA OPS HARDENING DEPLOY ALL FLAGS OFF

Generated: 2026-06-26T11:00:46Z

## Scope

This phase was a production deploy gate only. No production deploy was run. No staging deploy was run. No production feature flags were changed. No Cloud Run Job was triggered. No Scheduler job was created. No ingestion, score materialization, LLM-backed action, Pigskin prompt, scraping, or Firebase action was run.

## Authorization Gate State

All checked gates were unset in the current process.

| Gate | State |
| --- | --- |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

`ALLOW_LIMITED_PRODUCTION_DEPLOY` remains unset. Production deployment must happen in a separate deploy phase with explicit authorization.

## Candidate Image

Phase 25.11 final decision:

`DATA OPS HARDENING PRODUCTION CANDIDATE READY WITH WARNINGS`

Candidate source:

| Field | Value |
| --- | --- |
| Commit | `22e32569c50d7493891c133d561cb4e4f16a569a` |
| Short commit | `22e3256` |
| Commit message | `Gate Data Ops local subprocess controls` |
| Build ID | `6abd92f7-b008-4320-ba55-7a7944a69cd3` |
| Image tag | `prod-candidate-22e32569c50d-20260626T104302Z` |
| Digest | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |

Artifact Registry verification:

| Check | Result |
| --- | --- |
| `gcloud artifacts docker images describe` | passed |
| Digest returned | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| Candidate matches requested Phase 25.12 image | yes |

Remaining candidate warning from Phase 25.11: local Docker is not installed, so direct local `docker run` inspection was not possible. The image was still built from the clean committed release source and verified in Artifact Registry.

## Staging Evidence Review

Phase 25.10 final decision:

`DATA OPS HARDENING STAGING QA PASS WITH WARNINGS`

Staging validated:

| Check | Result |
| --- | --- |
| Data Ops local subprocess controls disabled by default | passed |
| Scouting CSV uploader hidden while local gates are false | passed |
| Trade Lab AI outlook action hidden while local admin controls are disabled | passed |
| Trade Analyzer score UI still works in staging | passed |
| Trade History compatibility marker still works in staging | passed |
| No local subprocess action triggered | passed |
| No LLM action triggered | passed |
| No Cloud Run Job triggered | passed |
| Production untouched | passed |

The Phase 25.10 warnings do not block an all-flags-off production deploy. They were staging-only iteration notes from browser QA and do not require production feature exposure.

## Preflight Results

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | passed |
| `.\venv\Scripts\python.exe -m py_compile app.py` | passed |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | passed |
| `.\venv\Scripts\python.exe -m unittest discover tests` | passed, 352 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | passed, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | passed |

The unit test run emitted expected local test logs for schema coercion and ingest-only planning. The command exited 0.

## Current Production Baseline

Read-only describe command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services describe nfl-studio-dashboard --project=fantasy-football-498121 --region=us-central1 --format=json
```

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Region | `us-central1` |
| Project | `fantasy-football-498121` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Latest ready revision | `nfl-studio-dashboard-00076-p6s` |
| Latest created revision | `nfl-studio-dashboard-00076-p6s` |
| Traffic | `100 percent` to `nfl-studio-dashboard-00076-p6s` |
| Current image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Ingress | `all` |
| Secret references | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |

## Current Production Flag State

| Flag | Current State |
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
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

The Data Ops local subprocess flags are unset on the current production revision. The deploy preview below sets both explicitly to `false`.

## Deploy Command Preview

Do not run this command in this gate phase. It is the preview for a separate authorized production deploy phase.

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --update-env-vars=USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false,USE_TRADE_ANALYZER_SCORE_V0=false,USE_COMPAT_TRADE_PLAYER_SCORE=false,USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false,DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false `
  --update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest `
  --no-allow-unauthenticated `
  --quiet
```

Preview safety checks:

| Requirement | Preview State |
| --- | --- |
| Uses digest-pinned Data Ops hardening image | yes |
| Keeps production compatibility flags false | yes |
| Keeps Trade History compatibility false | yes |
| Keeps Trade Analyzer score flags false | yes |
| Keeps Data Ops Cloud Run trigger flags false | yes |
| Keeps Data Ops local subprocess flags false | yes |
| Preserves `GEMINI_API_KEY` Secret Manager reference | yes |
| Creates no Scheduler jobs | yes |
| Triggers no Cloud Run Jobs | yes |

## Rollback Command

Rollback target is the current production baseline revision captured in this phase:

`nfl-studio-dashboard-00076-p6s`

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00076-p6s=100
```

## Remaining Warnings

- Phase 25.10 staging QA passed with warnings related to staging-only iteration history. No remaining warning requires production feature exposure.
- Phase 25.11 candidate build passed with warnings because local Docker image inspection was unavailable. Artifact Registry verification passed.
- Current production has the Data Ops local subprocess flags unset, not true. The production deploy preview sets both explicitly to `false`.
- `ALLOW_LIMITED_PRODUCTION_DEPLOY` is unset. This is expected for the gate phase. A separate deploy phase must set authorization inside that phase before any deploy.

## Decision

The Data Ops local-control hardening candidate may proceed to a separate production deploy phase, provided that phase sets explicit authorization and uses the digest-pinned image above with all risk, score, Cloud Run trigger, and local subprocess flags false.

Final decision: APPROVED FOR PRODUCTION DATA OPS HARDENING DEPLOY ALL FLAGS OFF
