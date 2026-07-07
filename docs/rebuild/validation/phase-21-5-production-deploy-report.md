# Phase 21.5 Production Deploy Report

## Final Decision

`PRODUCTION DEPLOY BLOCKED`

Phase 21.5 did not deploy because Phase 21.4 did not approve production deployment. Phase 21.4 final decision is `PRODUCTION DEPLOY BLOCKED`, not `APPROVED FOR PRODUCTION DEPLOY ALL FLAGS OFF`.

No production deploy, staging deploy, Cloud Run Job trigger, Scheduler creation, LLM call, scrape, Firebase artifact creation, production smoke test, rollback, or production flag change was performed.

## Gate Check

| Required gate | Observed status | Result |
| --- | --- | --- |
| Phase 21.4 approval says `APPROVED FOR PRODUCTION DEPLOY ALL FLAGS OFF` | Phase 21.4 says `PRODUCTION DEPLOY BLOCKED` | blocker |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` | current process value is `<unset>` | blocker |
| Live validate-warehouse proof passed or waived | Phase 21.4 says live proof remains unresolved | blocker |
| Verified digest-pinned candidate image exists | pass | candidate available for future preview |
| All production risk flags false | pass by current baseline and required preview values | not enough to deploy |

## Authorization State

| Env var | Observed value |
| --- | --- |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | `<unset>` |

Because this authorization is unset and Phase 21.4 did not approve deploy, Phase 21.5 stopped before any production mutation.

## Candidate Image

Phase 21.3 verified the current production candidate:

| Field | Value |
| --- | --- |
| Image tag | `prod-candidate-ce0eb82eef63-20260617T033954Z` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31` |
| Build ID | `84ab90b6-97d4-4e8f-8a1a-9b3028380b86` |
| Build status | `SUCCESS` |

This image remains a candidate only. It was not deployed in Phase 21.5.

## Pre-Deploy Production State

Phase 21.5 did not rerun production describe because the first required gate failed and the task requires stopping if Phase 21.4 is not approved.

The latest captured production baseline from Phase 21.4 remains:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| Latest ready revision | `nfl-studio-dashboard-00074-26x` |
| Traffic split | `nfl-studio-dashboard-00074-26x=100` |
| Current image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Production risk flags | unset, app defaults false |

## Required Production Flag State

No flags were changed. If a future deploy is approved, the deploy command must set:

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

## Deploy Command Status

No deploy command was run.

The Phase 21.4 deploy preview remains the correct command shape for a future approved deploy, updated to use this digest:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31
```

Do not run it until:

1. Phase gate says `APPROVED FOR PRODUCTION DEPLOY ALL FLAGS OFF`.
2. `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` is set.
3. Live validate-warehouse proof is passed or formally waived.
4. Release package warnings are accepted or resolved.

## Smoke Test Status

No production smoke test was run because no production deploy occurred.

No rollback was needed because production was not changed.

## Final Status

`PRODUCTION DEPLOY BLOCKED`

Production remains on the previously captured revision. The next step is to resolve the live validate-warehouse proof or record a formal waiver, then rerun the Phase 21.4 deploy gate before attempting Phase 21.5 again.
