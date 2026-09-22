# Phase 28.10 Draft-Pick Score UI Polish Staging QA Report

Date: 2026-06-28

Final decision: DRAFT PICK SCORE UI POLISH STAGING QA PASS WITH WARNINGS

## Scope

Phase 28.10 deployed the draft-pick score UI polish to staging only and ran authenticated browser QA. No production deployment, BigQuery write, score materialization, ingestion, Cloud Run Job trigger, Scheduler change, LLM action, Pigskin prompt, scrape, or Firebase artifact creation was performed.

## Authorization Gates

Checked before deployment and QA:

| Gate | State |
| --- | --- |
| ALLOW_TRADE_PICK_SCORE_MATERIALIZATION | unset |
| ALLOW_TRADE_SCORE_MATERIALIZATION | unset |
| ALLOW_PROJECTION_CONTEXT_REFRESH | unset |
| ALLOW_LIMITED_PRODUCTION_DEPLOY | unset |
| ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST | unset |
| DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER | unset |

No authorization gate was set in this phase.

## Pre-Build Checks

All required local checks passed before the staging build:

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | pass |
| `py_compile app.py` | pass |
| `py_compile src\trade_pick_scores.py` | pass |
| `py_compile src\trade_player_scores.py` | pass |
| `compileall -q src scripts` | pass |
| `unittest tests.test_trade_pick_scores` | 21 tests OK |
| `unittest tests.test_trade_pick_score_contracts` | 6 tests OK |
| `unittest tests.test_streamlit_compat_rollout` | 12 tests OK |
| `unittest tests.test_staging_ui_warning_fixes` | 24 tests OK |
| `unittest tests.test_data_ops_local_controls` | 6 tests OK |
| `unittest discover tests` | 407 tests OK |
| `run_bigquery_migrations.py --list-pending` | no pending migrations |
| `run_bigquery_validations.py --dry-run` | 178 validations discovered |
| `run_bigquery_validations.py --run --pattern trade_pick_scores` | 17 passed, 0 failed, 1 informational warning |
| `run_bigquery_validations.py --run --pattern compat_trade_pick_scores` | pass |
| `run_bigquery_validations.py --run --pattern trade_player_scores` | pass |
| `run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass |

The informational warning was validation 178, which reported `trade_pick_score_v0_2026_001` with 64 rows. That is expected after the authorized Phase 28.6 staging materialization.

## Data Prerequisite

Read-only warehouse checks confirmed the draft-pick score lane was populated before UI QA:

| Check | Count |
| --- | ---: |
| `trade_pick_scores` total rows | 64 |
| `trade_pick_score_v0_2026_001` rows | 64 |
| PPR rows | 64 |
| exact-slot rows | 48 |
| round-only rows | 16 |
| `trade_pick_scores_current` rows | 64 |
| `compat_trade_pick_scores_current` rows | 64 |
| duplicate current grain rows | 0 |

Player-score separation was checked. A broad text search for "pick" in `trade_player_scores` matched George Pickens in player-score rows, not draft-pick rows. No draft-pick score rows were written to the player-score lane.

## Code Fix During QA

The first staging revision exposed a UI polish gap: compact draft-pick warning labels capped output before the round-only uncertainty flag became visible. The fix increased the default warning-label cap in `src/ui_data_guards.py` and extended the warning-label test in `tests/test_staging_ui_warning_fixes.py`.

After this fix, all local checks above were rerun and passed.

## Staging Build

Superseded first build:

| Field | Value |
| --- | --- |
| Tag | `staging-pick-score-ui-polish-615854978e09-20260628T204959Z` |
| Build ID | `b896bbfc-4281-4c74-bd0e-44a44120a3b8` |
| Digest | `sha256:c9df6fb3b7ab240508001a1e5a27a5ce9c9b0953aa10f1d955b009a01660b90d` |
| Staging revision | `nfl-studio-dashboard-staging-00028-c48` |
| Status | superseded after warning-label fix |

Final build:

| Field | Value |
| --- | --- |
| Tag | `staging-pick-score-ui-polish-615854978e09-20260628T211610Z` |
| Build ID | `9a198676-0e69-4a0d-8553-4338da46b45c` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` |
| Build status | SUCCESS |

## Staging Deployment

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard-staging` |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| Revision | `nfl-studio-dashboard-staging-00029-jtb` |
| URL | `https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app` |
| Traffic | `nfl-studio-dashboard-staging-00029-jtb:100` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Secret refs | `GEMINI_API_KEY=secret:GEMINI_API_KEY:latest` |

## Staging Feature Flags

| Flag | State |
| --- | --- |
| USE_COMPAT_TRADE_PLAYER_HISTORY | `true` |
| USE_TRADE_ANALYZER_SCORE_V0 | `true` |
| USE_COMPAT_TRADE_PLAYER_SCORE | `true` |
| USE_TRADE_PICK_SCORE_V0 | `true` |
| USE_COMPAT_TRADE_PICK_SCORE | `true` |
| USE_COMPAT_PLAYER_PROFILES | `false` |
| USE_COMPAT_SLEEPER_WATCH | `false` |
| USE_COMPAT_TRADE_ASSETS | `false` |
| USE_COMPAT_VIEWER_TEAM_CONTEXT | `false` |
| USE_BACKTEST_DASHBOARD | `false` |
| USE_CLAIM_LEDGER_UI | `false` |
| USE_CONTENT_BRIEF_REVIEW_UI | `false` |
| USE_CLOUD_RUN_JOBS_FOR_DATA_OPS | `false` |
| DATA_OPS_ALLOW_JOB_TRIGGER | `false` |
| USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS | `false` |
| DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER | `false` |

## Health Checks

Authenticated HTTP checks passed:

| Check | Result |
| --- | --- |
| `/_stcore/health` | 200 `ok` |
| `/` | 200 |
| Streamlit shell present | yes |
| Traceback in response | no |

An unauthenticated health request returned 403, which is expected for the authenticated staging service.

## Browser QA

Browser evidence was captured under `output/playwright/phase-28-10/`. These generated artifacts are local QA evidence and should not be committed unless the owner explicitly approves.

Main authenticated Trade Lab QA:

| Check | Result |
| --- | --- |
| Login/session gate | pass |
| Trade Lab loads | pass |
| Side A player selection: Bijan Robinson | pass |
| Side A second selector appears | pass |
| Side A mixed player plus exact pick: `2026 Pick 1.01` | pass |
| Side B player selection: Ja'Marr Chase | pass |
| Side B second selector appears | pass |
| Player score lane remains visible | pass |
| Pick score lane remains separate | pass |
| Exact-slot pick score visible | pass, `96.7` |
| Exact-slot class/slot visible | pass, class `exact_slot`, slot `1` |
| Pick component summary visible | pass |
| Pick warning summary visible | pass |
| Mixed player and draft-pick warning visible | pass in later captured states |
| No `No assets selected` regression | pass |
| No `Traceback`, `KeyError`, `NameError`, `pos_abb`, or `rolling_3_week_ppr` | pass |

Standalone round-only QA on final revision:

| Check | Result |
| --- | --- |
| Round-only pick selected: `2026 1st` | pass |
| Round-only pick score visible | pass, `55.71` |
| Confidence visible | pass, `74.0` |
| Model visible | pass, `trade_pick_score_v0_2026_001` |
| Pick class visible | pass, `round_only` |
| Slot copy visible | pass, `round-only` |
| Warning visible | pass, `pick round only uncertainty` |
| Component summary visible | pass |
| Warning summary visible | pass |

Regression QA:

| Area | Result |
| --- | --- |
| Pigskin Studio loads | pass |
| `execute_bigquery_sql` not visible | pass |
| raw/source table list not visible to Pigskin | pass |
| Show Prep loads | pass |
| Player Profiles loads | pass |
| Versus Finder loads | pass |
| Viewer Team Lab loads | pass |
| Data Ops loads | pass |
| Cloud Run Job trigger button | visible but disabled |
| Data Ops local subprocess controls | absent |
| LLM-backed actions | not clicked |

## Logs

Cloud Run logs for `nfl-studio-dashboard-staging-00029-jtb`:

| Check | Count |
| --- | ---: |
| Entries inspected | 150 |
| ERROR severity | 0 |
| WARNING severity | 1 |
| warning-like application text | 0 |
| traceback-like strings | 0 |
| pick-score UI error strings | 0 |
| local subprocess strings | 0 |
| LLM strings | 0 |
| Cloud Run Job trigger strings | 0 |

The single WARNING severity entry was the expected unauthenticated 403 from the first health probe:

`The request was not authenticated. Either allow unauthenticated invocations or set the proper Authorization header.`

## Job And Scheduler Status

No Scheduler jobs were listed in `us-central1`.

Recent `validate-warehouse` executions remained prior proof executions:

| Execution | Created | Completed | Status |
| --- | --- | --- | --- |
| `validate-warehouse-gwbpg` | 2026-06-19T17:26:10Z | 2026-06-19T17:27:44Z | Completed |
| `validate-warehouse-qhwkq` | 2026-06-19T15:52:31Z | 2026-06-19T15:58:38Z | NonZeroExitCode |

No Cloud Run Job was triggered during Phase 28.10.

## Production Untouched

Read-only production describe confirmed production was not changed:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00077-2jp` |
| Traffic | `nfl-studio-dashboard-00077-2jp:100` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| USE_TRADE_PICK_SCORE_V0 | unset |
| USE_COMPAT_TRADE_PICK_SCORE | unset |
| USE_TRADE_ANALYZER_SCORE_V0 | `false` |
| USE_COMPAT_TRADE_PLAYER_SCORE | `false` |
| USE_COMPAT_TRADE_PLAYER_HISTORY | `false` |
| USE_CLOUD_RUN_JOBS_FOR_DATA_OPS | `false` |
| DATA_OPS_ALLOW_JOB_TRIGGER | `false` |
| USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS | `false` |
| DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER | `false` |

## Warnings

- The first staging build was superseded because round-only uncertainty was not visible in compact warning labels. The code and test fix was made, checks were rerun, and final staging revision `nfl-studio-dashboard-staging-00029-jtb` passed the standalone round-only browser QA.
- The main mixed-flow automation recorded failed checks for the optional Side B round-only repeat. A separate authenticated standalone round-only flow passed on the final revision. The required same-side mixed player plus exact-pick flow passed.
- The main automation recorded `side_a_mixed_warning` as failed at an early checkpoint, but later captured states showed `Mixed player and draft-pick assets selected`. This is treated as an automation timing false positive, not a UI blocker.
- One Cloud Logging WARNING entry came from an expected unauthenticated health probe. Authenticated health passed.

## Recommended Next Phase

- Phase 28.11 should review the staged source/test changes and the Phase 28.10 report for a narrow commit package.
- If the owner wants stricter browser evidence, rerun a dedicated Side B mixed round-only flow before commit. The current staging evidence is enough for a pass with warnings because the standalone round-only lane and same-side exact-pick mixed lane both passed.

## Final Decision

DRAFT PICK SCORE UI POLISH STAGING QA PASS WITH WARNINGS
