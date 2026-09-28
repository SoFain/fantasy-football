# Phase 20.8 Limited Production Deploy Report

## Purpose

Revisit a limited production deploy with all production risk flags off after Phase 20 staging, data, and content-readiness work.

No production deploy was run in this phase.

## Final Status

`PRODUCTION DEPLOY BLOCKED`

Reason:

- `ALLOW_LIMITED_PRODUCTION_DEPLOY` is not set.
- The live `validate-warehouse` Cloud Run Job proof remains `LIVE PROOF BLOCKED`, not passed and not formally waived.

A digest-pinned production deploy preview is documented below, but it must not be executed until the missing authorization and live-proof decision are resolved.

## Authorization State

| Gate | State |
| --- | --- |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| Production deploy authorized | no |
| Production deploy executed | no |
| Cloud Run Jobs triggered | no |
| Scheduler jobs created | no |
| LLM calls made for deploy validation | no |
| Firebase artifacts created | no |

## Readiness Checklist

| Requirement | Status | Evidence |
| --- | --- | --- |
| Current staging image deployed | pass | `phase-20-1-current-staging-image-report.md`, final decision `CURRENT STAGING IMAGE DEPLOYED WITH WARNINGS` |
| Authenticated staging QA pass or accepted warnings | pass with resolved follow-up | `phase-20-2-authenticated-staging-qa-report.md` reported `STAGING QA PASS WITH WARNINGS`; `phase-20-2b-trade-lab-summary-staging-qa-report.md` resolved the Trade Lab side-summary warning |
| Live `validate-warehouse` proof passed or formally waived | blocker | `phase-20-3-validate-warehouse-proof-decision-report.md` reports `LIVE PROOF BLOCKED` |
| Production candidate image immutable | pass | `phase-18-1-production-candidate-image-report.md` |
| Production rollback baseline exists | pass | `phase-18-2-production-baseline-report.md` |
| Tests pass | pass | 309 tests, OK |
| `app.py` compiles | pass | `py_compile app.py` passed |
| `src` and `scripts` compile | pass | `compileall -q src scripts` passed |
| No pending migrations | pass | `run_bigquery_migrations.py --list-pending` returned no pending migrations |
| Validation dry-run passes | pass | `run_bigquery_validations.py --dry-run` exited successfully and discovered 149 validation files |
| Production risk flags false | pass by baseline | production baseline has all risk flags unset, and the app defaults them false |
| Pigskin safety intact | pass | deployment safety checker passed `pigskin_no_execute_bigquery_sql` |

## Phase 20 Evidence Summary

| Phase | Status |
| --- | --- |
| Phase 20.1 staging image | current reviewed staging image deployed |
| Phase 20.2 staging QA | pass with warning, later resolved by Phase 20.2B |
| Phase 20.3 validate-warehouse proof | blocked, not waived |
| Phase 20.4 2025 ingest-only restore | admin/browser ingest produced 2025 rows; later audited before mart rebuild |
| Phase 20.5 current-season marts | `CURRENT MARTS READY` |
| Phase 20.6 Fraud Watch | `CURRENT-SEASON FRAUD WATCH DRAFT READY` |
| Phase 20.7 claims and trades | `BLOCKED BY MISSING OPERATOR INPUTS`, not a production deploy blocker with risk flags off |

## Preflight Commands

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
| Unit tests | pass, 309 tests |
| `app.py` compile | pass |
| `src` and `scripts` compile | pass |
| Migration ledger | pass, no pending migrations |
| Validation dry-run | pass, 149 validation files discovered |

Deployment safety details:

- no Firebase artifacts;
- no tracked secret files;
- no secret content detected;
- required files exist;
- feature flags default off;
- Pigskin `execute_bigquery_sql` remains absent;
- `app.py`, `src`, and `scripts` compile through the safety checker.

## Production Candidate Image

Immutable production candidate from Phase 18.1:

| Field | Value |
| --- | --- |
| Git short SHA | `ce0eb82eef63` |
| Image tag | `prod-candidate-ce0eb82eef63-20260616T181911Z` |
| Image URI | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-ce0eb82eef63-20260616T181911Z` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:6d26118c3fdf3ce10d1983a8cfddb05956f65c34463d4ef02bcce47cb37f25c4` |
| Build ID | `c81856f3-1b16-4585-a92a-4d507d6d5e1a` |
| Build status | success |

## Production Baseline

Current production baseline from Phase 18.2:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| Current ready revision | `nfl-studio-dashboard-00074-26x` |
| Current traffic split | `nfl-studio-dashboard-00074-26x=100` |
| Current image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2` |
| Current digest | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:6447b6f175c1aa2613907b630afeb40d56368ec99210abafacf82d5a94eca57e` |
| Nearest previous ready revision | `nfl-studio-dashboard-00073-9wp` |

Production risk flags are currently unset in production.

## Required Production Flag State

If a future authorized deploy proceeds, production must explicitly keep these flags false:

| Flag | Required production state |
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

## Deploy Command Preview

Do not run this command until:

1. `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` is explicitly set by the operator.
2. The live `validate-warehouse` proof is passed or formally waived.
3. The operator confirms the digest-pinned candidate image.

Preview only:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:6d26118c3fdf3ce10d1983a8cfddb05956f65c34463d4ef02bcce47cb37f25c4 `
  --update-env-vars USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false `
  --quiet
```

Notes:

- This preview uses the digest-pinned image, not `latest`.
- It does not enable Trade History compatibility in production.
- It does not enable Cloud Run Job triggers.
- It does not create Scheduler jobs.
- Existing secret bindings should be preserved by avoiding any secret-clear or secret-reset flag.

## Rollback Command

Rollback to the current production revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions nfl-studio-dashboard-00074-26x=100
```

Fallback rollback to the nearest previous ready revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions nfl-studio-dashboard-00073-9wp=100
```

Risk flag cleanup command if a future deploy accidentally enables any risk flag:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --remove-env-vars USE_COMPAT_PLAYER_PROFILES,USE_COMPAT_SLEEPER_WATCH,USE_COMPAT_TRADE_ASSETS,USE_COMPAT_TRADE_PLAYER_HISTORY,USE_COMPAT_VIEWER_TEAM_CONTEXT,USE_BACKTEST_DASHBOARD,USE_CLAIM_LEDGER_UI,USE_CONTENT_BRIEF_REVIEW_UI,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS,DATA_OPS_ALLOW_JOB_TRIGGER
```

## Smoke Test Status

No production smoke test was run because no production deploy was authorized or executed.

If a future deploy is authorized, the minimum smoke test remains:

- health endpoint;
- Streamlit loads;
- login/session gate works;
- Pigskin safety remains intact;
- Data Ops job triggers disabled;
- all production risk flags false.

## Remaining Blockers

1. `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` is not set.
2. The live `validate-warehouse` proof remains blocked and has not been formally waived.

## Non-Blocking Known Gaps

These are not production deploy blockers when all risk flags are off, but remain product follow-ups:

- real claim and trade inputs are still missing;
- claim grading and Trade Review content remain blocked by missing operator inputs;
- generated Fraud Watch content is draft-only and still requires human review.

## Decision

`PRODUCTION DEPLOY BLOCKED`

The rebuild branch is healthy enough for a previewed all-risk-flags-off production deployment command, but production deployment is not authorized and the live `validate-warehouse` proof is still unresolved. No production changes were made.
