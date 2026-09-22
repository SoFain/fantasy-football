# Phase 32.37 Dashboard Deploy And TE35 Production Report

Final decision: **FORMULA REVIEW DEPLOYED AND TE35 PRODUCTION DEPTH READY**

## Summary

Phase 32.37 deployed a new production Cloud Run revision containing the Formula Review dashboard code and changed production TE depth from 60 to 35.

The TE depth change was applied in two layers:

- Source/config: future Pigskin ranking generation now uses QB45, RB80, WR100, and TE35.
- Runtime/table state: current active TE rows greater than rank 35 were marked inactive for the four active scoring profiles.

No live ranking regeneration, formula champion activation, BQML training, Gemini call, Pigskin chat call, live Sleeper API call, source ingest, Cloud Run Job trigger, candidate table overwrite, global truncate, or backtest detail write ran.

## Files Changed

Source and tests:

- `src/generate_pigskin_rankings.py`
- `src/player_profile_ranking_profiles.py`
- `tests/test_pigskin_rankings_model_runs.py`
- `tests/test_player_profile_ranking_profiles.py`

Docs:

- `docs/rebuild/formula-ranking-owner-review-index.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/validation/phase-32-37-dashboard-deploy-te35-production-report.md`

Pending prior-phase docs also remain in the worktree:

- `docs/rebuild/validation/phase-32-36-owner-inspection-checklist.md`
- `docs/rebuild/validation/phase-32-36-dashboard-owner-inspection-support-report.md`

## Git State

| Checkpoint | Result |
|---|---|
| Phase 32.35 docs commit | `a6c3ae4 phase 32.35 enable formula review dashboard` |
| TE35 source/config commit | `aac24d5 phase 32.37 te35 ranking depth config` |
| Historical validation backlog | Still untracked and not staged |
| Generated artifacts staged | No |

## Dashboard Source Verification

Confirmed source files:

- `src/formula_review_dashboard.py` exists.
- `src/compat_flags.py` defines `USE_FORMULA_COMPARISON_DASHBOARD`.
- `app.py` adds the Formula Review tab when the flag is true.
- `tests/test_formula_review_dashboard.py` covers default-off behavior and read-only dashboard content.

Dashboard source:

- `docs/rebuild/live-2026-ranking-review-boards.md`

The dashboard is still read-only and Markdown-backed. It does not query BigQuery at runtime and has no write, export, deploy, ranking-generation, champion-selection, Gemini, Pigskin chat, Sleeper API, or Cloud Run Job controls.

## TE Depth Source And Config

Found depth controls:

- `src/generate_pigskin_rankings.py`, `DEFAULT_POSITION_LIMITS`
- `src/player_profile_ranking_profiles.py`, Player Profiles active ranking SELECT

Changed:

- `DEFAULT_POSITION_LIMITS["TE"]`: `60` to `35`
- Player Profiles ranking query now caps active rankings by position:
  - QB 45
  - RB 80
  - WR 100
  - TE 35

Focused tests were added for both contracts.

## BigQuery Pre-Change Shape

Before the bounded TE update:

| Scoring profile | QB | RB | WR | TE |
|---|---:|---:|---:|---:|
| `standard` | 45 | 80 | 100 | 60 |
| `half_ppr` | 45 | 80 | 100 | 60 |
| `ppr` | 45 | 80 | 100 | 60 |
| `gng_keeper` | 45 | 80 | 100 | 60 |

Other pre-change checks:

- TE active rows with rank 36 through 60: 100.
- `ranking_formula_champions` total rows: 0.
- Active champion rows: 0. The table uses `active`, not `is_active`.

## TE35 Data Update

The table stores active production depth directly through `is_active`, so Phase 32.37 applied the approved bounded active-row change.

Dry-run and count controls:

- Exact WHERE clause counted 100 affected rows.
- BigQuery DML dry run completed with `total_bytes_processed=1164168`.
- The command executed only after the affected count matched 100.

Data update:

```sql
UPDATE `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings`
SET is_active = FALSE
WHERE is_active = TRUE
  AND position = 'TE'
  AND rank > 35
  AND rank <= 60
  AND scoring_profile_id IN ('standard','half_ppr','ppr','gng_keeper')
  AND STRUCT(scoring_profile_id, ranking_version) IN (
    SELECT AS STRUCT scoring_profile_id, ranking_version
    FROM `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings`
    WHERE is_active = TRUE
      AND scoring_profile_id IN ('standard','half_ppr','ppr','gng_keeper')
    GROUP BY scoring_profile_id, ranking_version
    HAVING COUNTIF(position = 'TE' AND rank BETWEEN 1 AND 60) = 60
  )
```

Result:

- Job ID: `8647885e-39c5-4b70-b6eb-9d59bbf1145c`
- DML affected rows: 100
- No `DELETE`
- No `TRUNCATE`
- No candidate table write

## BigQuery Post-Change Shape

After the bounded update:

| Scoring profile | QB | RB | WR | TE |
|---|---:|---:|---:|---:|
| `standard` | 45 | 80 | 100 | 35 |
| `half_ppr` | 45 | 80 | 100 | 35 |
| `ppr` | 45 | 80 | 100 | 35 |
| `gng_keeper` | 45 | 80 | 100 | 35 |

Post-change checks:

- Active total rows across the four scoring profiles: 1,040.
- Active TE rows above rank 35: 0.
- `ranking_formula_champions` total rows: 0.
- Active champion rows: 0.

## Cloud Run Pre-Deploy State

| Item | Value |
|---|---|
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00083-tlr` |
| Traffic | `nfl-studio-dashboard-00083-tlr=100` |
| Image digest | `sha256:c675aa578b218581c4a9253e6bd5ceefc6da3ee0198dcb7cb9b98e3c541442e6` |
| `USE_FORMULA_COMPARISON_DASHBOARD` | `true` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `false` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `false` |
| `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` | `<unset>` |

## Build

Build command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' builds submit `
  --project=fantasy-football-498121 `
  --config=cloudbuild.yaml `
  --substitutions="_IMAGE_TAG=prod-candidate-aac24d5b2c62-20260706T163543Z,_COMMIT_HASH=aac24d5b2c62,_VERSION_LABEL=prod-candidate-aac24d5b2c62-20260706T163543Z" `
  .
```

Build result:

- Build ID: `a697848d-dd62-4105-8ac0-3210059dead8`
- Build status: `SUCCESS`
- Image tag: `prod-candidate-aac24d5b2c62-20260706T163543Z`
- Digest-pinned image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:d0af08ee49858ab6230fea9b0ab6504a12043cc7066d0f76c79fb84f8b723f7d`

PowerShell stopped the first build wrapper on a native stderr archive message, but Cloud Build itself completed successfully. The build was verified with `gcloud builds list` and Artifact Registry describe.

## Deploy

Deploy command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:d0af08ee49858ab6230fea9b0ab6504a12043cc7066d0f76c79fb84f8b723f7d `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --update-env-vars=USE_FORMULA_COMPARISON_DASHBOARD=true,DATA_OPS_ALLOW_JOB_TRIGGER=false,DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false,USE_TRADE_ANALYZER_SCORE_V0=false,USE_COMPAT_TRADE_PLAYER_SCORE=false `
  --quiet
```

Deploy result:

- New revision: `nfl-studio-dashboard-00084-9z5`
- Traffic: `nfl-studio-dashboard-00084-9z5=100`
- URL: `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app`

## Cloud Run Post-Deploy State

| Item | Value |
|---|---|
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00084-9z5` |
| Traffic | `nfl-studio-dashboard-00084-9z5=100` |
| Image digest | `sha256:d0af08ee49858ab6230fea9b0ab6504a12043cc7066d0f76c79fb84f8b723f7d` |
| `USE_FORMULA_COMPARISON_DASHBOARD` | `true` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `false` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `false` |
| `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` | `<unset>` |
| `USE_PIGSKIN_PACKET_QA_UI` | `true` |

## Health Check

| Check | Result |
|---|---|
| `/_stcore/health` | `200 ok` |
| `/` | `200` |
| Streamlit shell present | Yes |
| Traceback in unauthenticated response | No |

No rollback was needed.

## Manual Owner Verification

Owner should log in and verify:

- `Formula Review` tab appears.
- Standard is first.
- Half PPR, PPR, and GNG Keeper follow.
- Current Pigskin is labeled live baseline.
- Enriched Logistic Elite is review-only challenger.
- Enriched Linear Points is context only.
- No global winner is shown.
- Missingness warnings are visible.
- TE output is capped at TE35.
- TE6, TE12, and TE18 cutlines remain visible.
- No write, export, deploy, ranking-generation, champion-selection, Gemini, Pigskin chat, Sleeper API, or Cloud Run Job controls appear.

Player Profiles manual check:

- TE list should stop at rank 35 for each scoring profile.
- QB, RB, and WR depths should remain 45, 80, and 100.

## Rollback Plan

If app health fails or the owner cannot access the app, route traffic back to the previous healthy revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00083-tlr=100
```

If the TE35 active-row change must be reverted, use a separate owner-approved rollback phase. The rows were not deleted; ranks 36 through 60 were marked inactive.

## Checks Run

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_player_profile_ranking_profiles` | Passed, 8 tests. |
| `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_rankings_model_runs` | Passed, 14 tests. |
| `.\venv\Scripts\python.exe -m unittest tests.test_formula_review_dashboard` | Passed, 7 tests. |
| `.\venv\Scripts\python.exe -m py_compile app.py src\compat_flags.py src\formula_review_dashboard.py src\player_profile_ranking_profiles.py src\generate_pigskin_rankings.py` | Passed. |
| `.\venv\Scripts\python.exe -m compileall -q src scripts app.py` | Passed. |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Passed. |
| `git diff --check` | Passed with line-ending warnings only. |

PowerShell emitted `NativeCommandError` wrappers for normal stderr test progress, build progress, deploy progress, and Git line-ending warnings, but the underlying commands returned successful exit codes or were verified independently.

## Safety Confirmation

Phase 32.37 did not run:

- `src/generate_pigskin_rankings.py`
- ranking generation
- champion activation
- Gemini
- Pigskin chat
- live Sleeper API
- BQML training
- source ingest
- materialization
- Cloud Run Jobs

Phase 32.37 did not write:

- `analytics_pigskin_rankings_candidates`
- `ranking_formula_champions`
- `ranking_backtest_results`

The only BigQuery write was the bounded owner-approved `is_active=false` update for 100 current active TE rows ranked 36 through 60.

## Recommended Next Phase

Recommended: Phase 32.38, owner inspection and hold Current Pigskin.

Other valid next phases:

- Phase 32.38, owner selection by scoring profile.
- Phase 32.38, review-only table persistence.
- Phase 32.38, live ranking generation only after explicit champion selection.
