# Phase 22.4 Production Deploy Gate Report

Generated: 2026-06-17T06:19:33Z

## Final Decision

`PRODUCTION DEPLOY BLOCKED`

The limited all-risk-flags-off production deploy is not approved. The local code health checks passed and the current production baseline was captured read-only, but three release gates remain blocked:

- Phase 22.2 did not pass or waive the live `validate-warehouse` Cloud Run Job proof.
- Phase 22.3 did not build a clean-provenance production candidate image.
- `ALLOW_LIMITED_PRODUCTION_DEPLOY` is unset in the current operator environment.

No production deploy was run. No production traffic changed. No Cloud Run Job was triggered. No Scheduler job was created.

## Gate Inputs

| Input | Status | Evidence |
| --- | --- | --- |
| Phase 22.2 live proof or waiver | blocker | `LIVE VALIDATE-WAREHOUSE STILL BLOCKED`; all required live proof env vars are unset and no formal waiver exists |
| Phase 22.1 release package | warning | `RELEASE PACKAGE CLEAN WITH WARNINGS`; generated artifacts are excluded and `pipeline_execution.log` diff was restored, but human review remains |
| Phase 22.3 production candidate | blocker | `PRODUCTION CANDIDATE BLOCKED`; no clean candidate was built from a clean release state |
| Deploy authorization | blocker | `ALLOW_LIMITED_PRODUCTION_DEPLOY=<unset>` |
| Production rollback baseline | pass | Current production revision and rollback command captured read-only in this report |

## Required Preconditions

| Precondition | Status |
| --- | --- |
| Live `validate-warehouse` proof passed or formal waiver accepted | blocker |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` | blocker |
| Release package clean or warnings accepted | warning |
| Immutable digest-pinned production candidate exists with clean provenance | blocker |
| Production rollback baseline exists | pass |
| Safety checker passes | pass |
| Tests pass | pass |
| `app.py` compiles | pass |
| `src` and `scripts` compile | pass |
| No pending migrations | pass |
| Validation dry-run passes | pass |
| No secret or Firebase issues | pass |
| Production flags remain false | pass |
| No Scheduler jobs | pass |
| Cloud Run Jobs do not trigger by default | pass |

## Final Preflight

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
| Unit tests | pass, 314 tests |
| `app.py` compile | pass |
| `src` and `scripts` compile | pass |
| Migration ledger | pass, no pending migrations |
| Validation dry-run | pass |

Safety checker result:

- no Firebase artifacts;
- no tracked secret files;
- no secret content detected;
- required files exist;
- feature flags default off;
- Pigskin `execute_bigquery_sql` remains absent;
- `app.py` compiles;
- `src` and `scripts` compile.

## Authorization State

| Variable | Value |
| --- | --- |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | `<unset>` |

Production deployment remains blocked until an operator explicitly sets:

```powershell
$env:ALLOW_LIMITED_PRODUCTION_DEPLOY = "true"
```

That setting alone is not enough. The live proof or waiver and clean candidate gates must also be resolved.

## Production Baseline

Captured read-only with:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services describe nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --format=json
```

| Field | Value |
| --- | --- |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| Service | `nfl-studio-dashboard` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Current revision | `nfl-studio-dashboard-00074-26x` |
| Latest created revision | `nfl-studio-dashboard-00074-26x` |
| Current image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2` |
| Traffic split | `nfl-studio-dashboard-00074-26x=100` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Ingress | `all` |
| CPU | `2` |
| Memory | `8Gi` |
| Max scale annotation | `20` |

## Production Risk Flag State

Current production risk flags are unset. The application defaults these flags false.

| Flag | Current production value | Required deploy value |
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

## Candidate Image

Phase 22.3 did not produce a clean production candidate. The only digest-pinned candidate referenced there is the Phase 21.3 preview artifact:

| Field | Value |
| --- | --- |
| Image tag | `prod-candidate-ce0eb82eef63-20260617T033954Z` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31` |
| Build ID | `84ab90b6-97d4-4e8f-8a1a-9b3028380b86` |
| Build status | `SUCCESS` |
| Release status | preview artifact only, not clean provenance |

This image is not approved for production by this gate because Phase 22.3 classified the clean production candidate as blocked.

## Deploy Command Preview

No approved deploy command exists for execution in this phase.

If the live proof or waiver is resolved, `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` is set, and a clean digest-pinned candidate is approved, the production deploy command must keep all risk flags false:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=<clean-digest-pinned-production-candidate-image> `
  --update-env-vars USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false `
  --quiet
```

For context only, the Phase 21.3 preview digest was:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31
```

Do not run this preview digest in production unless the operator explicitly accepts the dirty-provenance warning or a clean candidate supersedes it.

## Rollback Command

Rollback to the current production revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions nfl-studio-dashboard-00074-26x=100
```

If a future deploy accidentally enables any risk flag, remove or reset them before holding production:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --update-env-vars USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false
```

## Production Decision

`PRODUCTION DEPLOY BLOCKED`

Allowed actions:

- keep staging validation active;
- complete human release package review;
- resolve or waive the live `validate-warehouse` proof;
- rebuild a clean digest-pinned production candidate from reviewed source;
- rerun this gate after authorization is set.

Disallowed actions:

- production deploy;
- enabling `USE_COMPAT_TRADE_PLAYER_HISTORY` in production;
- enabling any production risk flag;
- enabling Cloud Run Job triggers in production;
- creating Scheduler jobs;
- triggering Cloud Run Jobs from this gate.

## No Runtime Changes

This phase made no production changes:

- no production deploy;
- no production env var update;
- no production traffic update;
- no Cloud Run Job deploy or trigger;
- no Scheduler job creation;
- no LLM calls;
- no scraping;
- no Firebase artifacts.

