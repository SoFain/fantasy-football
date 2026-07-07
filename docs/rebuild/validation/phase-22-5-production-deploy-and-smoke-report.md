# Phase 22.5 Production Deploy And Smoke Report

Generated: 2026-06-17T06:25:00Z

## Final Decision

`PRODUCTION DEPLOY BLOCKED`

Phase 22.5 did not deploy production because the required Phase 22.4 approval gate was not cleared.

No production deploy was run. No smoke test was run against a new revision. No rollback was needed.

## Authorization

| Gate | Status |
| --- | --- |
| Phase 22.4 approval | blocked |
| Required Phase 22.4 decision | `APPROVED FOR PRODUCTION DEPLOY ALL FLAGS OFF` |
| Actual Phase 22.4 decision | `PRODUCTION DEPLOY BLOCKED` |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | `<unset>` |
| Clean digest-pinned production candidate | blocked |

The Phase 22.5 stop condition was met:

- Phase 22.4 did not approve production deployment.
- `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` is not set.
- Phase 22.3 classified the clean production candidate as blocked.

## Pre-Deploy Baseline

No new production describe was required after the stop condition was reached. The latest read-only production baseline from Phase 22.4 remains:

| Field | Value |
| --- | --- |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| Service | `nfl-studio-dashboard` |
| Current revision | `nfl-studio-dashboard-00074-26x` |
| Current image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2` |
| Traffic split | `nfl-studio-dashboard-00074-26x=100` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |

Current production risk flags were reported as unset in Phase 22.4, which means the application defaults keep them false.

## Candidate Image

Phase 22.3 did not approve a clean production candidate. The only digest-pinned image referenced there was retained as a preview artifact:

| Field | Value |
| --- | --- |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31` |
| Build status | `SUCCESS` |
| Release status | preview artifact only, not clean provenance |

This image was not deployed by Phase 22.5.

## Deploy Command

No deploy command was executed.

The production deploy command remains blocked until all of the following are true:

1. Phase 22.4 is rerun and returns `APPROVED FOR PRODUCTION DEPLOY ALL FLAGS OFF`.
2. `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` is set.
3. A clean digest-pinned production candidate is approved.
4. The live `validate-warehouse` proof passes or is formally waived.

## Required Risk Flag State

If a future deployment is approved, every production risk flag must be explicitly false:

| Flag | Required value |
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

## Smoke Test Results

No post-deploy smoke test was run because no deployment occurred.

| Check | Status |
| --- | --- |
| Health endpoint on new revision | not run |
| Streamlit load on new revision | not run |
| Login/session gate on new revision | not run |
| Pigskin Studio on new revision | not run |
| `execute_bigquery_sql` absence on new revision | not run |
| Raw/source table visibility on new revision | not run |
| Show Prep on new revision | not run |
| Player Profiles on new revision | not run |
| Versus Finder on new revision | not run |
| Viewer Team Lab on new revision | not run |
| Trade Lab on new revision | not run |
| Trade History compat marker absent in production | not run |
| Trade Analyzer score v0 absent in production | not run |
| Data Ops job trigger gating on new revision | not run |

## Rollback Status

Rollback was not needed because no production deployment occurred.

The rollback command recorded in Phase 22.4 remains:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions nfl-studio-dashboard-00074-26x=100
```

## Runtime Safety

This phase made no runtime changes:

- no production deploy;
- no production env var update;
- no production traffic update;
- no Cloud Run Job deploy or trigger;
- no Scheduler job creation;
- no LLM calls;
- no Firebase artifacts.

