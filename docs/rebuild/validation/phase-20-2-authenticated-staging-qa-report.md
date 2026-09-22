# Phase 20.2 Authenticated Staging QA Report

Date: 2026-06-16

## Decision

STAGING QA PASS WITH WARNINGS

The current staging image is reachable, authenticated browser access works, the Phase 18.3 `pos_abb` and `rolling_3_week_ppr` warnings did not reproduce, Pigskin SQL safety remains intact, Data Ops Cloud Run Job triggers remain gated, and the Trade History compatibility flag rollback works.

One Trade Lab display warning remains: after selecting A.J. Brown and Ja'Marr Chase, both selectboxes showed the selected players, but the side summary cards still showed `No assets selected`. This should be fixed before treating Trade Lab browser QA as clean.

## Staging Service

| Field | Value |
| --- | --- |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| Service | `nfl-studio-dashboard-staging` |
| Initial revision | `nfl-studio-dashboard-staging-00010-2gs` |
| Rollback test revision | `nfl-studio-dashboard-staging-00011-jq9` |
| Final revision | `nfl-studio-dashboard-staging-00012-hh4` |
| URL | `https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:fff643754107c848b650d63d60038c6f0e96835c622473cb47866f0f99c43194` |
| Traffic | `nfl-studio-dashboard-staging-00012-hh4:100` |
| Auth method | `gcloud auth print-identity-token` for Cloud Run, then Streamlit login gate |

## Final Feature Flag State

| Flag | Final state |
| --- | --- |
| `USE_COMPAT_PLAYER_PROFILES` | `false` |
| `USE_COMPAT_SLEEPER_WATCH` | `false` |
| `USE_COMPAT_TRADE_ASSETS` | `false` |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `true` |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | `false` |
| `USE_BACKTEST_DASHBOARD` | `false` |
| `USE_CLAIM_LEDGER_UI` | `false` |
| `USE_CONTENT_BRIEF_REVIEW_UI` | `false` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |

## Access And Evidence

The staging service is private. Direct authenticated health returned:

```text
DIRECT_HEALTH=200 BODY=ok
```

The standard `gcloud run services proxy` command could not be used because the `cloud-run-proxy` component is not installed and the local Google Cloud SDK install path is not writable. For browser QA, I used a disposable local authenticated proxy under `output/playwright/` that forwarded HTTP and websocket traffic with the identity token. No app code or deployment configuration was changed for this proxy.

Browser evidence files:

| Evidence | Path |
| --- | --- |
| Main QA summary | `output/playwright/phase-20-2/qa-proxy-authenticated-summary.json` |
| Trade player selection result | `output/playwright/phase-20-2/trade-selected-final.json` |
| Rollback legacy check | `output/playwright/phase-20-2/rollback-legacy-check.json` |
| Final re-enabled compat check | `output/playwright/phase-20-2/final-reenabled-check.json` |
| Trade Lab selected screenshot | `output/playwright/phase-20-2/trade-selected-final.png` |
| Rollback screenshot | `output/playwright/phase-20-2/trade-lab-rollback-legacy.png` |
| Final re-enabled screenshot | `output/playwright/phase-20-2/trade-lab-final-reenabled.png` |

Note: headless screenshots rendered inconsistently in the private Streamlit session, but DOM text, tab state, and control state were captured successfully.

## Tab QA

| Tab | Result | Notes |
| --- | --- | --- |
| Pigskin Studio | Pass | Page loaded after login. `execute_bigquery_sql` was not visible. `weekly_metrics` and raw/source table lists were not visible in the Pigskin tab. LLM prompt execution was not attempted. |
| Show Prep | Pass | Page loaded. No `rolling_3_week_ppr` error appeared. No traceback or unhandled error appeared. |
| Player Profiles | Pass | Page loaded. No `pos_abb` error appeared. Legacy path remains active because `USE_COMPAT_PLAYER_PROFILES=false`. |
| Versus Finder | Pass | Page loaded. No inherited `pos_abb` error appeared. |
| Viewer Team Lab | Pass | Page loaded. Legacy path remains active because `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`. |
| Trade Lab | Pass with warning | Page loaded. `Trade player history source: compat_trade_player_history` appeared. A.J. Brown and Ja'Marr Chase were selectable, but summary cards still displayed `No assets selected`. |
| Data Ops | Pass | Page loaded. Cloud Run Jobs section was visible but live triggering remained gated because `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false` and `DATA_OPS_ALLOW_JOB_TRIGGER=false`. |

## Negative Safety Checks

| Check | Result |
| --- | --- |
| Pigskin `execute_bigquery_sql` visible | Pass, not visible |
| Pigskin `weekly_metrics` visible | Pass, not visible |
| Pigskin raw/source table list visible | Pass, not visible |
| Pigskin `SELECT * FROM weekly_metrics` execution | Not executed, because LLM calls were not authorized. Static/browser checks confirmed no arbitrary SQL tool was visible. |
| Data Ops Cloud Run Job trigger default | Pass, gated by default-off flags |
| LLM calls | None |
| Cloud Run Jobs triggered | None |
| Production touched | No |
| Firebase artifacts created | No |

## Trade Lab Compatibility QA

With `USE_COMPAT_TRADE_PLAYER_HISTORY=true`:

- Trade Lab loaded.
- The compatibility marker appeared:
  - `Trade player history source: compat_trade_player_history`
- A.J. Brown option appeared as:
  - `A.J. Brown (WR - PHI) (Value: 3821)`
- Ja'Marr Chase option appeared as:
  - `Ja'Marr Chase (WR - CIN) (Value: 9888)`
- No `Traceback`, `KeyError`, `NameError`, `pos_abb`, or `rolling_3_week_ppr` errors appeared.

Warning:

- After both players were selected, the Side A and Side B summary cards still showed `No assets selected`.
- The current browser QA therefore confirms the compat history marker and player selection controls, but not clean side-summary behavior.

## Rollback Test

Rollback command executed on staging only:

```powershell
gcloud run services update nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --remove-env-vars USE_COMPAT_TRADE_PLAYER_HISTORY `
  --quiet
```

Rollback result:

- Revision: `nfl-studio-dashboard-staging-00011-jq9`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=<unset>`
- Trade Lab loaded.
- Compat marker was absent.
- Legacy text appeared:
  - `Data path: Trade Player History is using the legacy warehouse path.`
- No tab error terms appeared.

The staging flag was then restored:

```powershell
gcloud run services update nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --update-env-vars USE_COMPAT_TRADE_PLAYER_HISTORY=true `
  --quiet
```

Final result:

- Revision: `nfl-studio-dashboard-staging-00012-hh4`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=true`
- All other risk flags remain false.
- Trade Lab loaded.
- Compat marker appeared again.

## Remaining Warnings

1. Trade Lab side summary cards still show `No assets selected` after player selections in the browser.
2. The local Google Cloud SDK cannot use `gcloud run services proxy` because the `cloud-run-proxy` component is not installed and the SDK install path is not writable. A disposable authenticated QA proxy was used instead.
3. Headless screenshots from the private Streamlit session were inconsistent, so the primary browser evidence is DOM text, tab state, control state, and JSON summaries.

## Final Status

STAGING QA PASS WITH WARNINGS

The stale-image blocker is cleared. The current staging image is deployed and authenticated browser QA verifies the Phase 18.3 missing-column fixes. Trade Lab compatibility remains staging-only and rollback works. Production remains untouched. The remaining Trade Lab summary-card display warning should be fixed before promoting the Trade Lab compatibility path beyond staging.
