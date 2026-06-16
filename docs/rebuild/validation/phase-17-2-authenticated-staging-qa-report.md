# Phase 17.2 Authenticated Staging QA Report

Date: 2026-06-16

Final decision: STAGING QA PASS WITH WARNINGS

Production readiness: still blocked

This phase completed authenticated browser-click QA against staging. It did not touch production, apply migrations, trigger Cloud Run Jobs, call LLMs, scrape, or create Firebase artifacts.

## Staging Service Details

Service name: `nfl-studio-dashboard-staging`

Project: `fantasy-football-498121`

Region: `us-central1`

Final revision after rollback test and restore: `nfl-studio-dashboard-staging-00009-zkq`

URL: `https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app`

Image tag: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-81ed959`

Runtime service account: `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com`

Auth method used:

- Cloud Run IAM access through active `gcloud` account `sofain@gmail.com`.
- Browser access through a temporary localhost proxy that injected a short-lived identity token.
- Streamlit login through the repo default dashboard credential path.
- Temporary identity token file was deleted after QA.
- Local proxy was stopped after QA.

## Final Feature Flag State

Final staging env state:

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

Other relevant config:

```text
BQ_PROJECT=fantasy-football-498121
BQ_DATASET=fantasy_football_brain
DATASET_NAME=fantasy_football_brain
EXTERNAL_SEARCH_PROVIDER=vertex_ai_search
EXTERNAL_SEARCH_DAILY_LIMIT=0
EXTERNAL_SEARCH_MAX_RESULTS=3
GEMINI_API_KEY=[Secret Manager binding]
```

## Health And Login

Status: pass.

- Direct authenticated `/_stcore/health`: `200 ok`.
- Local authenticated browser proxy `/_stcore/health`: `200 ok`.
- Streamlit rendered the login gate.
- Login succeeded.
- Main dashboard tabs rendered after login.

## Tab QA Results

| Tab | Result | Notes |
|---|---|---|
| Pigskin Studio | Pass | Page loads, prompt box appears, send button disabled with empty input, no raw/source table list visible, no `execute_bigquery_sql` visible, no console errors. No LLM message was sent. |
| Show Prep | Pass with warning | Page loads and Fraud Watch section renders. Sleeper Watch legacy path shows a BigQuery error for missing `rolling_3_week_ppr`. No LLM call was made. |
| Player Profiles | Pass with warning | Page loads, but legacy path query fails with missing `pos_abb`. This confirms the tab renders, but legacy data path is not healthy. |
| Versus Finder | Pass with warning | Page loads, but legacy profile query also fails with missing `pos_abb`. No traceback or console errors. |
| Viewer Team Lab | Pass | Page loads, Sleeper form renders, team console empty-state renders. Legacy path remains available because `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`. |
| Trade Lab | Pass with warnings | Page loads and shows `Trade player history source: compat_trade_player_history`. A.J. Brown and Ja'Marr Chase can be selected. Side A summary updated for A.J. Brown. Side B selectbox showed Ja'Marr Chase, but the Side B summary stayed empty. |
| Data Ops | Pass | Page loads, runtime status renders, Cloud Run path is disabled, trigger allow flag is disabled, and `Trigger Cloud Run Job` is disabled. No job was triggered. |
| Claim Ledger | Pass | Hidden/inactive because `USE_CLAIM_LEDGER_UI=false`. |
| Content Brief Review | Pass | Hidden/inactive because `USE_CONTENT_BRIEF_REVIEW_UI=false`. |

## Trade Lab Compat QA

Status: pass with warnings.

Browser-confirmed:

- Trade Lab loaded.
- `Trade player history source: compat_trade_player_history` was visible.
- `Data path: Trade Player History is using the compatibility contract path` was visible.
- A.J. Brown was selectable.
- Ja'Marr Chase was selectable.
- No `weekly_metrics` text appeared in the browser Trade Lab path.
- No query failure appeared in Trade Lab.
- No traceback appeared in Trade Lab.

UI warnings:

- Side A summary updated for A.J. Brown.
- Side B selectbox showed Ja'Marr Chase, but the Side B summary remained at `Current Total Value: 0` and `No assets selected`.
- Source freshness and missing-data metadata were not visible in the browser until the AI analysis path would run.
- The AI analysis button was not clicked because that would call Gemini, and this phase did not authorize LLM calls.

Safe helper check:

- `get_trade_player_history("A.J. Brown", limit=5)` returned 5 rows.
- `get_trade_player_history("Ja'Marr Chase", limit=5)` returned 5 rows.
- Returned rows include `source_freshness_json`.
- Returned rows include `missing_data_flags`.

Conclusion:

- The compatibility helper and browser source marker are valid.
- The full Trade Lab browser workflow has a UI-state issue on the Side B summary card.
- Browser-visible history metadata should be improved before production promotion.

## Negative Safety QA

Status: pass.

Confirmed in browser and static safety checks:

- Pigskin did not expose `execute_bigquery_sql`.
- Pigskin did not show a raw/source table list.
- Pigskin prompt was not submitted.
- No arbitrary SQL was executed.
- No `SELECT * FROM weekly_metrics` prompt was sent to an LLM.
- Cloud Run Job trigger controls were disabled because `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false` and `DATA_OPS_ALLOW_JOB_TRIGGER=false`.
- No live Cloud Run Job was triggered.
- No scraping was performed.

## Rollback Test

Status: pass with repair note.

Rollback steps:

1. Removed `USE_COMPAT_TRADE_PLAYER_HISTORY`.
2. Staging deployed revision `nfl-studio-dashboard-staging-00007-gjb`.
3. Health stayed `200 ok`.
4. Browser session reset to login, then reauthenticated.
5. Trade Lab loaded and showed `Data path: Trade Player History is using the legacy warehouse path`.
6. The compat marker was absent.

Re-enable steps:

1. Re-enabled `USE_COMPAT_TRADE_PLAYER_HISTORY=true`.
2. Staging deployed revision `nfl-studio-dashboard-staging-00008-7dw`.
3. The first re-enable command left the env listing incomplete.
4. Repaired staging env using `--update-env-vars` to restore the full required safe flag/config set.
5. Final revision `nfl-studio-dashboard-staging-00009-zkq` is healthy and has the required flag state.
6. Browser verified Trade Lab is back on the compatibility path.

Production was not touched.

## Screenshots And Evidence

No screenshots were committed.

Evidence recorded in this report:

- Cloud Run service metadata and final revision.
- Browser-click tab results.
- Browser-visible Trade Lab compat marker.
- Browser-visible rollback to legacy path.
- Safe helper check for bounded compat-history rows.

## Warnings

Production remains blocked by these QA findings:

1. Player Profiles legacy path fails with missing `pos_abb`.
2. Versus Finder legacy path fails with missing `pos_abb`.
3. Show Prep Sleeper Watch legacy path fails with missing `rolling_3_week_ppr`.
4. Trade Lab Side B summary does not reflect selected Ja'Marr Chase even though the selectbox shows the player.
5. Trade History source freshness and missing-data metadata are not browser-visible without running the Gemini analysis path.
6. The first re-enable command showed why staging flag updates must use `--update-env-vars` or a full env manifest, not broad `--set-env-vars`.

## Final Decision

STAGING QA PASS WITH WARNINGS

Authenticated staging browser QA is complete. The safety gates passed, rollback passed, and production was untouched. The QA findings should block production promotion until the Trade Lab Side B summary issue and broken legacy queries are resolved or explicitly accepted as known non-production blockers.

