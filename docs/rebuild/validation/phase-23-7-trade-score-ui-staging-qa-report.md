# Phase 23.7 Trade Score UI Staging QA Report

Date: 2026-06-18

## Final Decision

`TRADE SCORE UI STAGING QA PASS WITH WARNINGS`

Authenticated staging browser QA passed for the Trade Analyzer score UI. The score UI rendered with staging score flags enabled, the legacy Trade Lab path worked after removing score flags, Pigskin SQL safety remained intact, Data Ops job triggers stayed gated, and production was untouched.

Warnings:

- The score data itself remains staging-review data. Phase 23.5 reported all 77 score rows below confidence 70.
- The installed Google Cloud SDK could not use `gcloud run services proxy` because the `cloud-run-proxy` component is not installed and the SDK install directory is not writable. QA used a generated local Node auth proxy under `output/playwright/phase-23-7/`.
- Browser artifacts under `output/playwright/phase-23-7/` are generated QA evidence and should not be committed unless explicitly reviewed.

No production deploy, production flag change, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, or Firebase artifact creation was performed.

## Staging State

| Field | Value |
| --- | --- |
| service | `nfl-studio-dashboard-staging` |
| project | `fantasy-football-498121` |
| region | `us-central1` |
| final revision | `nfl-studio-dashboard-staging-00018-cpz` |
| final traffic | 100 percent to `nfl-studio-dashboard-staging-00018-cpz` |
| URL | `https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app` |
| image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:1fe0253f07332361a5f54e1a654477920de7ad4b0813cef2806acd5be4f4ebc2` |
| auth method | generated local Node proxy using `gcloud auth print-identity-token` |

Health check through authenticated local proxy:

| Check | Result |
| --- | --- |
| `/_stcore/health` | `200 ok` |
| Streamlit login gate | passed |

## Final Feature Flag State

Enabled in staging:

| Flag | Value |
| --- | --- |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `true` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `true` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `true` |

False in staging:

| Flag | Value |
| --- | --- |
| `USE_COMPAT_PLAYER_PROFILES` | `false` |
| `USE_COMPAT_SLEEPER_WATCH` | `false` |
| `USE_COMPAT_TRADE_ASSETS` | `false` |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | `false` |
| `USE_BACKTEST_DASHBOARD` | `false` |
| `USE_CLAIM_LEDGER_UI` | `false` |
| `USE_CONTENT_BRIEF_REVIEW_UI` | `false` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |

## Browser Evidence

Generated local evidence:

| Evidence | Path |
| --- | --- |
| final score-enabled JSON summary | `output/playwright/phase-23-7/qa-evidence.json` |
| final score-enabled run log | `output/playwright/phase-23-7/qa-run-final-score-enabled.log` |
| rollback run log | `output/playwright/phase-23-7/qa-run-score-disabled.log` |
| score UI screenshot | `output/playwright/phase-23-7/trade-score-ui.png` |
| score panel screenshot | `output/playwright/phase-23-7/trade-score-panel.png` |
| missing-score screenshot | `output/playwright/phase-23-7/missing-score-behavior.png` |
| rollback screenshot | `output/playwright/phase-23-7/rollback-trade-lab.png` |

These are generated browser artifacts and are not release commit candidates by default.

## Trade Lab Score UI QA

Selected players:

| Side | Asset | Result |
| --- | --- | --- |
| Side A | `A.J. Brown` | selected and rendered |
| Side B | `Ja'Marr Chase` | selected and rendered |

Observed score evidence:

| Check | Result |
| --- | --- |
| Trade Lab page loads | pass |
| Trade History marker appears | `Trade player history source: compat_trade_player_history` |
| selected asset summaries render | pass |
| market value totals render | pass |
| projected 3-year values render | pass |
| Pigskin Trade Score appears | pass |
| score source marker appears | `Pigskin Trade Score source: compat_trade_player_scores_current` |
| score tier appears | pass |
| score component breakdown appears | pass |
| confidence appears | pass |
| missing-data flags appear | pass |
| source freshness appears | pass |
| side total trade scores appear | pass |
| fairness delta appears | pass |
| market totals remain separate from score totals | pass |
| no `No assets selected` regression | pass |
| no `Traceback`, `KeyError`, `NameError`, `pos_abb`, or `rolling_3_week_ppr` | pass |

Score excerpt from evidence:

```text
Side A Pigskin Trade Score: 35.41
Side B Pigskin Trade Score: 55.77
Pigskin Score Fairness Delta: 20.36
A.J. Brown: score 35.4137, tier depth, confidence 47.78, risk 1.0, Fraud Watch 100.0
Ja'Marr Chase: score 55.7722, tier flex, confidence 49.35, risk 0.825, Fraud Watch 60.0
```

## Missing Score Behavior

Known no-score asset tested:

| Asset | Result |
| --- | --- |
| `2026 Pick 1.01` | selected and rendered |

Observed behavior:

| Check | Result |
| --- | --- |
| legacy market summary still works | pass |
| current value appears | `7084` |
| projected 3-year value appears | `7084` |
| score unavailable warning appears | `Pigskin Trade Score unavailable for Side A: 2026 Pick 1.01` |
| Side A score displays safely | `N/A` |
| scored asset count displays safely | `Scored assets: 0 of 1` |
| no crash | pass |

## Regression QA

| Area | Result |
| --- | --- |
| Pigskin Studio loads | pass |
| `execute_bigquery_sql` absent | pass |
| raw/source table list not visible to Pigskin | pass |
| Show Prep loads | pass |
| no `rolling_3_week_ppr` regression | pass |
| Player Profiles loads | pass |
| no `pos_abb` regression | pass |
| Versus Finder loads | pass |
| Viewer Team Lab loads | pass |
| Data Ops loads | pass |
| Data Ops Cloud Run Jobs remain gated | pass |

No Pigskin prompt was submitted and no AI analysis button was clicked.

## Rollback Flag Test

Rollback action:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard-staging --project=fantasy-football-498121 --region=us-central1 --remove-env-vars=USE_TRADE_ANALYZER_SCORE_V0,USE_COMPAT_TRADE_PLAYER_SCORE --update-env-vars=USE_COMPAT_TRADE_PLAYER_HISTORY=true,USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false --quiet
```

Rollback revision:

| Field | Value |
| --- | --- |
| score-disabled revision | `nfl-studio-dashboard-staging-00017-d8w` |
| traffic | 100 percent to score-disabled revision during rollback QA |

Rollback QA result:

| Check | Result |
| --- | --- |
| Trade Lab loads | pass |
| Trade History compat marker remains | pass |
| score UI disappears | pass |
| selected asset summaries render | pass |
| market totals render | pass |
| projected values render | pass |
| no crash | pass |

Restore action:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard-staging --project=fantasy-football-498121 --region=us-central1 --update-env-vars=USE_COMPAT_TRADE_PLAYER_HISTORY=true,USE_TRADE_ANALYZER_SCORE_V0=true,USE_COMPAT_TRADE_PLAYER_SCORE=true,USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false --quiet
```

Restored final revision:

| Field | Value |
| --- | --- |
| final score-enabled revision | `nfl-studio-dashboard-staging-00018-cpz` |
| traffic | 100 percent |
| health | `200 ok` |

## Production Status

Read-only production check:

| Field | Value |
| --- | --- |
| production service | `nfl-studio-dashboard` |
| production revision | `nfl-studio-dashboard-00074-26x` |
| production image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2` |
| `USE_TRADE_ANALYZER_SCORE_V0` | unset |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | unset |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | unset |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | unset |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | unset |

Production was not changed.

## Safety Check

`.\venv\Scripts\python.exe scripts\check_deployment_safety.py` passed:

- no Firebase artifacts
- no tracked secret files
- no detected secret content
- feature flags default off
- Pigskin `execute_bigquery_sql` absent
- app and `src` plus `scripts` compile

## Acceptance Criteria

| Criterion | Status |
| --- | --- |
| score UI renders in staging when flags are true | pass |
| legacy Trade Lab works when score flags are false | pass |
| no production changes | pass |
| Pigskin SQL safety intact | pass |
| Data Ops triggers gated | pass |
| no Firebase artifacts | pass |
