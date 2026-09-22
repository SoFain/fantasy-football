# Phase 16.3 Trade History Staging QA Report

Date: 2026-06-16

Decision: KEEP IN STAGING

## Goal

Enable only `USE_COMPAT_TRADE_PLAYER_HISTORY=true` in staging and validate that Trade Lab can use the compatibility player-history path without changing production.

## Baseline Before Enablement

Staging service:

```text
nfl-studio-dashboard-staging
revision: nfl-studio-dashboard-staging-00001-vhj
url: https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app
```

Baseline health:

```text
GET /_stcore/health
status=200
body=ok
```

Baseline flags:

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
```

Production service before and after this phase:

```text
nfl-studio-dashboard
revision: nfl-studio-dashboard-00074-26x
```

Production was not updated.

## Enablement

Command run:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --update-env-vars=USE_COMPAT_TRADE_PLAYER_HISTORY=true `
  --quiet
```

Result:

```text
nfl-studio-dashboard-staging-00002-k9m
```

Flag diff:

```text
USE_COMPAT_TRADE_PLAYER_HISTORY: false -> true
```

All other compatibility, dashboard, and job-trigger flags remained false.

## Readiness Check

Command run:

```powershell
.\venv\Scripts\python.exe -m src.compat_rollout --check USE_COMPAT_TRADE_PLAYER_HISTORY
```

Result:

- `compat_trade_player_history` exists.
- Object type: `VIEW`.
- Row count: `55,617`.
- Required columns present.
- `source_freshness_json` sampled missing rate: `0.0`.
- `missing_data_flags` sampled missing rate: `0.0`.
- Validation files discovered: `6`.
- Recommendation: enable.

## Validation Results

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_history
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
```

Results:

- `compat_trade_player_history`: 6 passed, 0 failed.
- `market`: 9 passed, 0 failed.
- `content_brief`: 11 passed, 0 failed.

Notable compat validation result:

```text
024_compat_trade_player_history_recent_rows_exist.sql
recent_row_count = 55617
```

Informational review row:

```text
compat_trade_player_history_identity_coverage
row_count = 2249
missing_identity_count = 0
missing_identity_rate = 0.0
```

## Targeted Tests

Command run:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_trade_history tests.test_streamlit_compat_rollout
```

Result:

```text
Ran 14 tests
OK
```

Confirmed by tests and static inspection:

- The compat helper queries `compat_trade_player_history`.
- The compat helper does not query `weekly_metrics`.
- Streamlit contains the marker `Trade player history source: compat_trade_player_history`.
- Legacy fallback still exists and still contains the old `weekly_metrics` query path for use when the flag is false.

## Data Path Smoke

Command run through the helper:

```python
from src.trade_history import get_trade_player_history
get_trade_player_history(player_name="A.J. Brown", limit=5)
get_trade_player_history(player_name="Ja'Marr Chase", limit=5)
```

Result:

- A.J. Brown returned 5 recent rows.
- Ja'Marr Chase returned 5 recent rows.
- Returned rows included `source_freshness_json`.
- Returned rows included `missing_data_flags`.
- Rows were capped by the requested limit.

Sample freshness source:

```text
scoring_source=analytics_player_fantasy_points_by_profile
evidence_source=analytics_player_weekly_truth
identity_source=player_identity_bridge
ranking_source=analytics_pigskin_rankings
environment_source=analytics_game_environment
scoring_refreshed_at=2026-06-16T06:04:25.218868Z
```

## Staging Smoke

After enablement:

```text
GET /_stcore/health
status=200
body=ok
```

Revision health:

```text
nfl-studio-dashboard-staging-00002-k9m
Ready=True
RoutesReady=True
ConfigurationsReady=True
```

Full browser-click Trade Lab QA was not completed in this run. The staging service is private. The local Cloud Run proxy component is not available in the installed SDK, and Chrome profile automation was not used because the user did not explicitly authorize using the logged-in Chrome profile. This leaves the visible UI click path as a manual follow-up, even though the service, flag, tests, and data path validated successfully.

## Rollback Test

Rollback command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --remove-env-vars=USE_COMPAT_TRADE_PLAYER_HISTORY `
  --quiet
```

Rollback revision:

```text
nfl-studio-dashboard-staging-00003-fr6
```

Rollback result:

- `USE_COMPAT_TRADE_PLAYER_HISTORY` was removed.
- The service returned to the default false behavior.
- All other risk flags remained false.
- Health check still returned `status=200`, `body=ok`.
- Legacy fallback remains available by code path and tests.

Re-enable command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --update-env-vars=USE_COMPAT_TRADE_PLAYER_HISTORY=true `
  --quiet
```

Final staging revision:

```text
nfl-studio-dashboard-staging-00004-gz8
```

Final staging flags:

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

Final staging health:

```text
GET /_stcore/health
status=200
body=ok
```

## Issues And Warnings

1. Browser-click QA in the private staging UI remains a manual follow-up.
2. `gcloud` is installed but not on PATH, so commands used the full `gcloud.cmd` path.
3. The staging service is now intentionally left with `USE_COMPAT_TRADE_PLAYER_HISTORY=true` for continued QA.

## Final Decision

KEEP IN STAGING

The compatibility view, helper, validation suite, rollback path, and staging service health all passed. This is not ready for production consideration until a human completes the visible Trade Lab workflow in authenticated staging and confirms the on-screen marker, player selection flow, recent history display, and AI outlook prompt context.
