# Phase 20.2B Trade Lab Summary Staging QA Report

Date: 2026-06-16

## Decision

TRADE LAB SUMMARY STAGING QA PASS

The Trade Lab summary-card fix was built, deployed to staging, and verified through authenticated browser QA. Production was not touched.

## Image And Deployment

| Field | Value |
| --- | --- |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| Service | `nfl-studio-dashboard-staging` |
| Git short SHA | `ce0eb82eef63` |
| Image tag | `staging-ce0eb82eef63-20260617T021501Z` |
| Build ID | `e97627b2-5a23-4335-9ba1-214bcf9e98ec` |
| Build status | `SUCCESS` |
| Image digest | `sha256:a669cb2d28d65a9aa14a9a008bf4a8c3754e9a2abb2c6e0d4345e79276752ce8` |
| Deployed image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:a669cb2d28d65a9aa14a9a008bf4a8c3754e9a2abb2c6e0d4345e79276752ce8` |
| Deploy revision | `nfl-studio-dashboard-staging-00013-dmb` |
| Rollback test revision | `nfl-studio-dashboard-staging-00014-t2g` |
| Final revision | `nfl-studio-dashboard-staging-00015-dcc` |
| Final traffic | `nfl-studio-dashboard-staging-00015-dcc:100` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |

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

## Pre-Deploy Checks

| Check | Result |
| --- | --- |
| `tests.test_staging_ui_warning_fixes` | PASS, 11 tests |
| `tests.test_streamlit_compat_rollout` | PASS, 8 tests |
| Full unittest discovery | PASS, 309 tests |
| `app.py` compile | PASS |
| `src\ui_data_guards.py` compile | PASS |
| `src` and `scripts` compile | PASS |
| Deployment safety | PASS |
| Pending migrations | PASS, no pending migrations |
| `compat_trade_player_history` validations | PASS, 6 passed, 0 failed |

Non-blocking validation note:

- `026_compat_trade_player_history_identity_coverage.sql` returned an informational warning with `missing_identity_rate = 0.0`.

## Health Check

Authenticated staging health after deploy:

```text
DIRECT_HEALTH=200 BODY=ok
```

## Focused Browser QA

Browser QA used authenticated Cloud Run access and the Streamlit login gate. No LLM calls were made.

Evidence:

| Evidence | Path |
| --- | --- |
| Browser QA summary | `output/phase-20-2b/browser-qa-summary.json` |
| Trade Lab screenshot | `output/phase-20-2b/trade-lab-summary-fixed.png` |
| Rollback browser check | `output/phase-20-2b/rollback-browser-check.json` |
| Final marker check | `output/phase-20-2b/final-marker-check.json` |

Trade Lab result:

| Check | Result |
| --- | --- |
| Trade Lab loads | PASS |
| Compat marker appears | PASS |
| Side A selection | PASS, `A.J. Brown` selected |
| Side B selection | PASS, `Ja'Marr Chase` selected |
| Side A Summary renders selected asset | PASS |
| Side B Summary renders selected asset | PASS |
| Valid selections avoid `No assets selected` | PASS |
| No unresolved-selection warning | PASS |
| No tab error terms | PASS |

Side A Summary evidence:

```text
Side A Summary
Current Total Value: 3821
Projected 3-Year Value: 1721
Selected Assets:
A.J. Brown (WR - PHI)
Age: 28.9 | Val: 3821
```

Side B Summary evidence:

```text
Side B Summary
Current Total Value: 9888
Projected 3-Year Value: 7579
Selected Assets:
Ja'Marr Chase (WR - CIN)
Age: 26.3 | Val: 9888
```

Safety strings absent after valid selections:

- `No assets selected`
- `Selected asset could not be resolved`
- `Traceback`
- `KeyError`
- `NameError`
- `pos_abb`
- `rolling_3_week_ppr`

## Regression Browser QA

| Area | Result |
| --- | --- |
| Pigskin Studio | PASS, loaded |
| Pigskin arbitrary SQL visible | PASS, `execute_bigquery_sql` not visible |
| Pigskin `weekly_metrics` visible | PASS, not visible |
| Show Prep | PASS, loaded |
| Player Profiles | PASS, loaded |
| Versus Finder | PASS, loaded |
| Data Ops | PASS, loaded |
| Data Ops Cloud Run Jobs | PASS, gated |

## Rollback Test

Rollback step:

```powershell
gcloud run services update nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --remove-env-vars USE_COMPAT_TRADE_PLAYER_HISTORY `
  --quiet
```

Rollback result:

- Revision: `nfl-studio-dashboard-staging-00014-t2g`
- Trade Lab loaded.
- Compat marker disappeared.
- Legacy path text appeared:
  - `Data path: Trade Player History is using the legacy warehouse path.`
- No `Traceback`, `KeyError`, `NameError`, `pos_abb`, or `rolling_3_week_ppr` appeared.

Restore step:

```powershell
gcloud run services update nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --update-env-vars USE_COMPAT_TRADE_PLAYER_HISTORY=true,USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false `
  --quiet
```

Final restored result:

- Revision: `nfl-studio-dashboard-staging-00015-dcc`
- Trade Lab loaded.
- Compat marker appeared again.
- All other risk flags remained false.

## Safety Status

| Safety item | Result |
| --- | --- |
| Production touched | No |
| Cloud Run Jobs triggered | No |
| Scheduler jobs created | No |
| LLM calls made | No |
| Scraping introduced | No |
| Firebase artifacts created | No |
| Additional compatibility flags enabled | No |
| Legacy fallback removed | No |
| Pigskin arbitrary SQL reintroduced | No |
| Raw/source tables exposed to Pigskin | No |

## Remaining Warnings

None for the Trade Lab side-summary fix.

The existing `compat_trade_player_history_identity_coverage` validation remains informational and non-blocking because `missing_identity_rate = 0.0`.

## Final Status

TRADE LAB SUMMARY STAGING QA PASS

The Phase 20.2 warning is resolved on staging. Side A and Side B summary cards now render selected assets correctly, valid selections no longer render `No assets selected`, rollback works, Pigskin SQL safety remains intact, and production remains untouched.
