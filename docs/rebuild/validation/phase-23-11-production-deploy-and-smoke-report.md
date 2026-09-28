# Phase 23.11 Production Deploy And Smoke Report

Date: 2026-06-19

## Final Decision

`PRODUCTION DEPLOY BLOCKED`

Production deploy was not attempted. Phase 23.10 did not approve production deployment, and `ALLOW_LIMITED_PRODUCTION_DEPLOY` is unset in this process.

No production deploy, staging deploy, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, smoke-test browser flow, rollback, or Firebase artifact creation was performed.

## Approval Gate

Required Phase 23.10 decision:

```text
APPROVED FOR PRODUCTION DEPLOY ALL FLAGS OFF
```

Observed Phase 23.10 decision:

```text
PRODUCTION DEPLOY BLOCKED
```

Blocking reasons from Phase 23.10:

- Phase 23.8 live `validate-warehouse` proof remains blocked.
- No formal waiver exists.
- `ALLOW_LIMITED_PRODUCTION_DEPLOY` is unset.

## Authorization

| Gate | Required | Observed |
| --- | --- | --- |
| Phase 23.10 approval | `APPROVED FOR PRODUCTION DEPLOY ALL FLAGS OFF` | `PRODUCTION DEPLOY BLOCKED` |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | `true` | `<unset>` |

Because both gates are not satisfied, Phase 23.11 stopped before deploy.

## Candidate Image

Available candidate from Phase 23.9:

| Field | Value |
| --- | --- |
| Image tag | `prod-candidate-ce0eb82eef63-20260619T041320Z` |
| Digest | `sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b` |
| Build status | `SUCCESS` |

The candidate was not deployed.

## Production Baseline

No new production describe was run after the blocked gate because Phase 23.11 stops before deploy when Phase 23.10 is not approved.

Latest captured baseline from Phase 23.10:

| Field | Value |
| --- | --- |
| service | `nfl-studio-dashboard` |
| project | `fantasy-football-498121` |
| region | `us-central1` |
| revision | `nfl-studio-dashboard-00074-26x` |
| image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2` |
| traffic | 100 percent to `nfl-studio-dashboard-00074-26x` |
| service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| secret refs | `GEMINI_API_KEY` |

Latest captured production risk flags from Phase 23.10 were unset and effectively false:

```text
USE_COMPAT_PLAYER_PROFILES=false
USE_COMPAT_SLEEPER_WATCH=false
USE_COMPAT_TRADE_ASSETS=false
USE_COMPAT_TRADE_PLAYER_HISTORY=false
USE_COMPAT_VIEWER_TEAM_CONTEXT=false
USE_BACKTEST_DASHBOARD=false
USE_CLAIM_LEDGER_UI=false
USE_CONTENT_BRIEF_REVIEW_UI=false
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
DATA_OPS_ALLOW_JOB_TRIGGER=false
USE_TRADE_ANALYZER_SCORE_V0=false
USE_COMPAT_TRADE_PLAYER_SCORE=false
```

## Deployment Result

No deployment command was run.

The Phase 23.10 deploy preview remains the only deploy command candidate, and it remains blocked until both conditions are true:

1. Live `validate-warehouse` proof passes or a formal waiver is accepted.
2. `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` is set.

## Smoke Tests

Smoke tests were not run because no production deployment occurred.

| Smoke check | Result |
| --- | --- |
| health endpoint | not run |
| Streamlit loads | not run |
| login/session gate | not run |
| Pigskin Studio loads | not run |
| `execute_bigquery_sql` absent | not run |
| raw/source tables not visible to Pigskin | not run |
| Show Prep loads | not run |
| Player Profiles loads | not run |
| Versus Finder loads | not run |
| Viewer Team Lab loads | not run |
| Trade Lab loads | not run |
| Trade History compat marker absent | not run |
| Trade Analyzer score UI absent | not run |
| Data Ops loads | not run |
| Cloud Run Jobs cannot trigger | not run |
| no obvious traceback | not run |

No LLM-backed UI action was invoked.

## Rollback

Rollback was not needed because no deployment occurred.

Rollback command from the Phase 23.10 baseline if a future approved deploy occurs:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard --project=fantasy-football-498121 --region=us-central1 --to-revisions nfl-studio-dashboard-00074-26x=100
```

## Production Impact

Production remains unchanged and blocked for deploy.

Next required action before retrying Phase 23.11:

1. Resolve live `validate-warehouse` proof or provide a formal waiver.
2. Rerun the production deploy gate.
3. Set `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` only after the gate report explicitly approves deployment.

## Acceptance Criteria

| Criterion | Status |
| --- | --- |
| No deploy unless approved and authorized | pass |
| All production risk flags false | unchanged from Phase 23.10 baseline |
| Score flags false | unchanged from Phase 23.10 baseline |
| Pigskin safety intact | no runtime change |
| Data Ops triggers disabled | no runtime change |
| Rollback used if needed | not needed |
