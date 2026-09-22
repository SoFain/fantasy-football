# Phase 32.35 Formula Review Dashboard Enable Report

Final decision: **FORMULA REVIEW DASHBOARD ENABLED WITH WARNINGS**

## Summary

Phase 32.35 committed the Phase 32.34 smoke documentation and enabled the read-only Formula Review dashboard in the production Cloud Run service with `USE_FORMULA_COMPARISON_DASHBOARD=true`.

No live ranking generation, champion activation, BQML training, Gemini call, Pigskin chat call, Sleeper API call, source ingest, materialization, BigQuery write, candidate overwrite, table truncate, or production ranking generator path ran.

The only runtime change was a Cloud Run environment-variable update on `nfl-studio-dashboard`.

## Files Changed

Phase 32.34 committed in this phase:

- `docs/rebuild/formula-ranking-owner-review-index.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/validation/phase-32-34-formula-review-dashboard-smoke-report.md`

Phase 32.35 documentation changes:

- `docs/rebuild/formula-ranking-owner-review-index.md`
- `docs/rebuild/validation/phase-32-35-formula-review-dashboard-enable-report.md`

## Phase 32.34 Commit

| Item | Result |
|---|---|
| Commit hash | `72662a3` |
| Commit message | `phase 32.34 smoke formula review dashboard` |
| Staged files | Phase 32.34 docs only |
| Historical backlog staged | No |
| Generated browser artifacts staged | No |

## Git State

Before the Phase 32.34 commit, the worktree had the expected Phase 32.34 documentation changes plus the previously classified historical validation backlog.

After the Phase 32.34 commit and before Phase 32.35 docs edits, the tracked source tree was clean except for untracked historical validation backlog files.

After Phase 32.35 documentation edits:

- `docs/rebuild/formula-ranking-owner-review-index.md` is modified.
- `docs/rebuild/validation/phase-32-35-formula-review-dashboard-enable-report.md` is untracked.
- Historical validation backlog files remain untracked.
- No generated browser evidence, logs, env files, caches, or secret files were staged.

## Feature Flag Status

| Item | Value |
|---|---|
| Flag | `USE_FORMULA_COMPARISON_DASHBOARD` |
| Code default | off when unset or false |
| Enabled value | `true` |
| Target runtime value after enablement | `true` |
| Dashboard source | `docs/rebuild/live-2026-ranking-review-boards.md` |
| Dashboard route/tab | `Formula Review` |
| Runtime query needed | No |

The flag remains default-off in code. No hard-coded enablement was added.

## Target Environment

| Item | Before enablement | After enablement |
|---|---|---|
| Service | `nfl-studio-dashboard` | `nfl-studio-dashboard` |
| Project | `fantasy-football-498121` | `fantasy-football-498121` |
| Region | `us-central1` | `us-central1` |
| Revision | `nfl-studio-dashboard-00082-7bf` | `nfl-studio-dashboard-00083-tlr` |
| Traffic | `nfl-studio-dashboard-00082-7bf=100` | `nfl-studio-dashboard-00083-tlr=100` |
| Image | `sha256:c675aa578b218581c4a9253e6bd5ceefc6da3ee0198dcb7cb9b98e3c541442e6` | unchanged |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` | unchanged |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` | unchanged |

## Enablement Method

The repo docs and Phase 32.34 report both say Cloud Run activation requires setting the environment variable and restarting or updating the app process.

Command run:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --update-env-vars=USE_FORMULA_COMPARISON_DASHBOARD=true `
  --quiet
```

Result:

```text
Service [nfl-studio-dashboard] revision [nfl-studio-dashboard-00083-tlr] has been deployed and is serving 100 percent of traffic.
Service URL: https://nfl-studio-dashboard-583607027760.us-central1.run.app
```

`--update-env-vars` was used. No destructive full environment reset was used.

## Runtime Flag Verification

Read-only Cloud Run describe after enablement:

| Flag | Value |
|---|---|
| `USE_FORMULA_COMPARISON_DASHBOARD` | `true` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |
| `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` | `<unset>` |
| `USE_PIGSKIN_PACKET_QA_UI` | `true` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `false` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `false` |

## Post-Enable Smoke

| Check | Result |
|---|---|
| `/_stcore/health` | `200 ok` |
| `/` | `200` |
| Streamlit shell present | Yes |
| Traceback in unauthenticated response | No |
| Browser probe | Reached app-level login gate |
| Formula Review tab visible in unauthenticated probe | Not visible because login gate stops before dashboard render |

Browser probe sample:

```text
Data Studio Login | Sign in to continue. | Username | Password | Log in
```

The dashboard tab could not be visually confirmed without logging in. No credentials were used. Owner inspection can begin by signing in to the production app and opening the `Formula Review` tab.

## Manual Owner Verification Steps

1. Open `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app`.
2. Sign in through the app-level login gate.
3. Confirm the `Formula Review` tab appears.
4. Confirm Standard appears first, followed by Half PPR, PPR, and GNG Keeper.
5. Confirm Current Pigskin is labeled as the live baseline.
6. Confirm Enriched Logistic Elite is labeled as review-only challenger.
7. Confirm Enriched Linear Points is labeled as context only.
8. Confirm no global winner is shown.
9. Confirm missingness warnings are visible.
10. Confirm TE output is capped at TE35 and TE6, TE12, and TE18 cutlines are visible.
11. Confirm there are no write, export, deploy, ranking generation, or champion activation controls in the tab.

## Read-Only Safety Confirmation

No command was run that calls:

- `src/generate_pigskin_rankings.py`
- Gemini
- Pigskin chat
- Sleeper API
- BQML training
- source ingest
- materialization
- Cloud Run Jobs

No command wrote to:

- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_candidates`
- `ranking_formula_champions`
- `ranking_backtest_results`

The live ranking table was not changed. No formula champion was activated. Current Pigskin remains the live baseline.

## Rollback Option

If owner inspection finds a hard UI issue, route traffic back to the previous revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00082-7bf=100
```

## Checks Run

Pre-commit Phase 32.34 checks:

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_formula_review_dashboard` | Passed, 7 tests. |
| `.\venv\Scripts\python.exe -m py_compile app.py src\compat_flags.py src\formula_review_dashboard.py` | Passed. |
| `.\venv\Scripts\python.exe -m compileall -q src scripts app.py` | Passed. |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Passed. |
| `git diff --check` | Passed with line-ending warnings only. |

Post-enable checks:

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_formula_review_dashboard` | Passed, 7 tests. |
| `.\venv\Scripts\python.exe -m py_compile app.py src\compat_flags.py src\formula_review_dashboard.py` | Passed. |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Passed. |
| `git diff --check` | Passed with line-ending warnings only. |

PowerShell emitted `NativeCommandError` wrappers for normal stderr test progress and Git line-ending warnings, but each command returned exit code `0`.

## Warnings

- Live browser tab visibility is pending owner login. The service is healthy and the flag is enabled, but the unauthenticated probe stops at the login gate.
- The Formula Review dashboard remains Markdown-backed. Review-only table persistence is a separate possible phase if owner wants sortable persistent dashboard data.
- TE live ranking depth is unchanged at TE60. Any live reduction to TE35 needs a separate owner-approved phase.

## Recommended Next Phase

Recommended: Phase 32.36, owner selection by scoring profile or hold current Pigskin baseline.

Other valid next phases:

- Phase 32.36, review-only table persistence.
- Phase 32.36, live ranking generation only after explicit owner approval.
- Phase 32.36, production TE depth change only after explicit owner approval.
