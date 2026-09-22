# Phase 19.2 Authenticated Staging QA Rerun Report

Date: 2026-06-16

Final decision: STAGING QA FAIL

Failure reason: staging is still running the pre-fix image, so authenticated browser QA cannot validate the Phase 18.3 UI fixes.

No production deploy was run. No production service was changed. No migrations were applied. No Cloud Run Jobs were triggered. No LLM calls were made. No scraping occurred. No Firebase artifacts were created.

## Purpose

Rerun authenticated staging browser QA after the Phase 18.3 UI fixes for:

- Player Profiles missing `pos_abb`
- Versus Finder inheriting the Player Profiles `pos_abb` issue
- Show Prep Sleeper Watch missing `rolling_3_week_ppr`
- Trade Lab Side B display behavior

## Staging Service Details

Read-only Cloud Run metadata:

```text
service: nfl-studio-dashboard-staging
project: fantasy-football-498121
region: us-central1
url: https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app
revision: nfl-studio-dashboard-staging-00009-zkq
image: us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-81ed959
traffic: 100 percent to nfl-studio-dashboard-staging-00009-zkq
service account: nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
auth method checked: Cloud Run IAM identity token through active gcloud account
```

Current local repo state:

```text
git_short_sha: ce0eb82eef63
worktree: dirty with Phase 18.3 UI fixes and Phase 18/19 reports uncommitted
```

Important finding:

```text
The staging service is still running image tag staging-81ed959 from the Phase 17.2 QA flow.
Phase 18.3 explicitly recorded that no staging deploy was run for the UI fixes.
Therefore the staging browser cannot validate the Phase 18.3 fixes yet.
```

## Required Feature Flag State

Staging currently has the intended feature flag state:

```text
USE_COMPAT_TRADE_PLAYER_HISTORY=true
USE_COMPAT_PLAYER_PROFILES=false
USE_COMPAT_SLEEPER_WATCH=false
USE_COMPAT_TRADE_ASSETS=false
USE_COMPAT_VIEWER_TEAM_CONTEXT=false
USE_BACKTEST_DASHBOARD=false
USE_CLAIM_LEDGER_UI=false
USE_CONTENT_BRIEF_REVIEW_UI=false
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
DATA_OPS_ALLOW_JOB_TRIGGER=false
```

No additional compatibility flags were enabled.

## Health Check

Authenticated health check:

```text
GET /_stcore/health
status: 200
body: ok
```

Interpretation:

- Staging service is reachable and healthy.
- This does not prove the Phase 18.3 UI fixes because the current staging image is stale.

## Browser QA Result

Authenticated browser-click QA was not completed.

Reason:

```text
The staging deployment does not contain the Phase 18.3 UI fixes.
Running browser QA against staging-81ed959 would only repeat the known Phase 17.2 warnings.
```

## Tab-by-Tab Status

| Area | Result | Reason |
|---|---|---|
| Pigskin Studio | Not rerun | Staging image is stale for Phase 18.3 validation. Local safety checks still pass. |
| Show Prep | Blocked | The Sleeper Watch fix is local only and not deployed to staging. |
| Player Profiles | Blocked | The `pos_abb` fix is local only and not deployed to staging. |
| Versus Finder | Blocked | The shared Player Profiles fix is local only and not deployed to staging. |
| Viewer Team Lab | Not rerun | Not one of the Phase 18.3 warning fixes. |
| Trade Lab | Blocked | The Side B display fix is local only and not deployed to staging. |
| Data Ops | Not rerun | Staging flag state says Cloud Run Jobs are disabled, but browser-click QA was not repeated. |
| Claim Ledger / Content Brief Review | Not rerun | Flags remain false. |

## Fixed Warnings Verification

Local code and tests verify the fixes, but staging does not yet:

```text
tests.test_staging_ui_warning_fixes: pass
tests.test_pigskin_chat_schema: pass
tests.test_cloud_run_jobs: pass
```

Targeted test result:

```text
24 tests passed
```

Deployment safety result:

```text
pass
```

`compat_trade_player_history` validation:

```text
6 passed, 0 failed
1 informational warning with missing_identity_rate=0.0
```

## Trade Lab Compatibility Result

Status: not browser-validated in this rerun

Staging remains configured correctly:

```text
USE_COMPAT_TRADE_PLAYER_HISTORY=true
```

Compatibility object validation remains healthy:

```text
compat_trade_player_history recent_row_count: 55617
raw_weekly_metrics_reference_count: 0
invalid_score_count: 0
missing_identity_rate: 0.0
```

However, the browser-visible Trade Lab Side B fix cannot be validated until a staging image containing `src/ui_data_guards.py` and the latest `app.py` is deployed.

## Negative Safety Checks

Status: pass locally, browser rerun blocked

Confirmed by deployment safety and tests:

- Pigskin arbitrary SQL remains absent.
- `execute_bigquery_sql` is not Pigskin-visible.
- Context Tool Protocol remains present.
- Cloud Run Jobs are gated and default off.
- No Firebase artifacts.
- No tracked secrets.

Browser negative checks were not rerun because staging is on the pre-fix image.

## Rollback Check

Rollback was not run.

Reason:

```text
No staging env var or image was changed in this phase.
There was nothing to roll back.
```

The prior Phase 17.2 rollback test remains the latest completed rollback evidence.

## Remaining Warnings

1. Staging browser QA after Phase 18.3 fixes remains incomplete.
2. Staging service must be updated with an image containing the current Phase 18.3 UI fixes before browser QA can be meaningful.
3. The worktree is dirty and includes uncommitted Phase 18.3 code changes, so a staging image should be built from an intentional reviewed commit or clearly documented temporary staging artifact.
4. Trade Lab compatibility remains staging-only.
5. Production remains not approved.

## Required Next Step

Deploy the current reviewed Phase 18.3 fixes to staging only with:

```text
USE_COMPAT_TRADE_PLAYER_HISTORY=true
all other risk flags=false
```

Then rerun authenticated browser-click QA for:

1. Player Profiles
2. Versus Finder
3. Show Prep Sleeper Watch
4. Trade Lab Side A and Side B
5. Data Ops trigger gating
6. Pigskin safety

## Final Decision

```text
STAGING QA FAIL
```

This is a deployment-state failure, not a code-test failure. Staging is healthy, but it does not yet contain the Phase 18.3 fixes that this QA rerun is supposed to validate.
