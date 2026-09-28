# Phase 25.10 Data Ops Hardening Staging QA Report

Date: 2026-06-26

Final decision: DATA OPS HARDENING STAGING QA PASS WITH WARNINGS

## Scope

Phase 25.10 built, deployed, and QAed the Data Ops local subprocess hardening changes in staging only.

No production deploy occurred. No production feature flags changed. No Cloud Run Jobs were triggered. No Scheduler jobs were created. No ingestion, materialization, LLM-backed action, Pigskin prompt, scrape, or Firebase artifact was created.

## Authorization Gates

Checked process environment gates:

| Gate | State |
|---|---|
| ALLOW_LIMITED_PRODUCTION_DEPLOY | unset |
| ALLOW_TRADE_SCORE_MATERIALIZATION | unset |
| ALLOW_PROJECTION_CONTEXT_REFRESH | unset |
| ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST | unset |
| DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER | unset |

`DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=true` was not set.

## Source Review

Confirmed hardening source is present:

| Check | Result |
|---|---|
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` exists and defaults false | PASS |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` exists and defaults false | PASS |
| Data Ops local buttons are gated by both local flags | PASS |
| Cloud Run Job buttons remain gated separately by `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` and `DATA_OPS_ALLOW_JOB_TRIGGER` | PASS |
| Trade Lab AI outlook action is gated by local admin controls | PASS |
| `execute_bigquery_sql` remains absent from Pigskin-visible tools | PASS |

During staging QA, the scouting CSV uploader was visible while local controls were disabled. The UI was hardened to hide the uploader unless local subprocess controls and the local trigger allow flag are both enabled.

During staging QA, Trade Lab rendered blank before its first visible widget. The shared cached BigQuery dataframe helper now uses `to_dataframe(create_bqstorage_client=False)`, which restored Trade Lab rendering without changing feature exposure or write behavior.

## Local Checks

Run after the final code changes:

| Command | Result |
|---|---|
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | PASS |
| `.\venv\Scripts\python.exe -m py_compile app.py` | PASS |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | PASS |
| `.\venv\Scripts\python.exe -m unittest discover tests` | PASS, 352 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | PASS, 160 validation files discovered |

## Build Result

Final staging image:

| Field | Value |
|---|---|
| Build ID | `588a54f7-d798-4919-be5f-f13abad464b0` |
| Build status | SUCCESS |
| Image tag | `staging-63149aa3d816-20260626T081627Z` |
| Image URI | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-63149aa3d816-20260626T081627Z` |
| Digest | `sha256:a1eb5955787ff0801da74daf5653f77f5594456ad9cb35e78204200adfc3efb6` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:a1eb5955787ff0801da74daf5653f77f5594456ad9cb35e78204200adfc3efb6` |

Warnings:

- Two earlier staging-only revisions were superseded during the same phase:
  - `nfl-studio-dashboard-staging-00021-bc5` corrected an initial PowerShell env-var quoting issue from `00020`.
  - `nfl-studio-dashboard-staging-00022-stw` included the hidden uploader fix, but Trade Lab remained blank until the dataframe helper adjustment.

## Staging Deploy Result

| Field | Value |
|---|---|
| Service | `nfl-studio-dashboard-staging` |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| Revision | `nfl-studio-dashboard-staging-00023-ljf` |
| Traffic | `100%` to `nfl-studio-dashboard-staging-00023-ljf` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:a1eb5955787ff0801da74daf5653f77f5594456ad9cb35e78204200adfc3efb6` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Service URL observed in deploy output | `https://nfl-studio-dashboard-staging-583607027760.us-central1.run.app` |
| Service URL observed in service describe | `https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app` |

## Staging Flag State

| Flag | State |
|---|---|
| USE_COMPAT_TRADE_PLAYER_HISTORY | true |
| USE_TRADE_ANALYZER_SCORE_V0 | true |
| USE_COMPAT_TRADE_PLAYER_SCORE | true |
| USE_COMPAT_PLAYER_PROFILES | false |
| USE_COMPAT_SLEEPER_WATCH | false |
| USE_COMPAT_TRADE_ASSETS | false |
| USE_COMPAT_VIEWER_TEAM_CONTEXT | false |
| USE_BACKTEST_DASHBOARD | false |
| USE_CLAIM_LEDGER_UI | false |
| USE_CONTENT_BRIEF_REVIEW_UI | false |
| USE_CLOUD_RUN_JOBS_FOR_DATA_OPS | false |
| DATA_OPS_ALLOW_JOB_TRIGGER | false |
| USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS | false |
| DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER | false |

## HTTP Health Checks

Authenticated checks against staging:

| Check | Result |
|---|---|
| `/_stcore/health` | 200 `ok` |
| `/` | 200 |
| Streamlit shell present | PASS |
| Traceback in root response | ABSENT |

## Browser QA

Authenticated browser QA was performed through a temporary local proxy that injected Cloud Run identity-token auth into HTTP and Streamlit websocket traffic.

| Area | Result |
|---|---|
| Login/session gate | PASS |
| Pigskin Studio loads | PASS |
| Show Prep loads | PASS |
| Player Profiles loads | PASS |
| Versus Finder loads | PASS |
| Viewer Team Lab loads | PASS |
| Trade Lab loads | PASS |
| Data Ops loads | PASS |
| `execute_bigquery_sql` absent | PASS |
| raw/source table list absent from Pigskin | PASS |
| No traceback, `KeyError`, `NameError`, `pos_abb`, or `rolling_3_week_ppr` regression | PASS |
| Browser console errors | 0 |
| Browser console warnings | 0 |

Trade Lab staging checks:

| Check | Result |
|---|---|
| Side A and Side B summaries render | PASS |
| Trade Analyzer score UI appears | PASS |
| Score source marker `compat_trade_player_scores_current` appears | PASS |
| Trade History compatibility marker appears | PASS |
| AI 3-year outlook action hidden while local admin controls are disabled | PASS |

Evidence files were written outside the repo under `%TEMP%\phase25_10_evidence\`:

- `trade_lab_score_ui.png`
- `trade_lab_bottom_ai_gate.png`
- `data_ops_gated_controls.png`

These are local browser artifacts and are not commit candidates.

## Data Ops Hardening QA

Data Ops page checks:

| Check | Result |
|---|---|
| Cloud Run path shows disabled | PASS |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false` visible | PASS |
| `DATA_OPS_ALLOW_JOB_TRIGGER=false` visible | PASS |
| Cloud Run Job trigger button disabled | PASS |
| Local controls show disabled | PASS |
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false` visible | PASS |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false` visible | PASS |
| Mutating local subprocess controls disabled | PASS |
| Ingestion controls disabled | PASS |
| External refresh controls disabled | PASS |
| BigQuery-writing controls disabled | PASS |
| LLM-backed local generation controls disabled | PASS |
| Scouting CSV uploader hidden while local gates are false | PASS |
| No local subprocess action triggered | PASS |

Inventoried controls:

| Control | State |
|---|---|
| Run AI 3-Year Outlook Analysis | hidden while local admin controls are disabled |
| Run Validation Sweep | disabled |
| Ingest Realtime Player News | disabled |
| Load Context Event Ledger | disabled |
| Ingest FantasyCalc Market Values | disabled |
| Verify Player Context | disabled |
| Ingest CFBD College Stats | disabled |
| Run Ingestion Pipeline | disabled |
| Generate Pigskin Rankings | disabled |
| Upload and Import Scouting Metrics | unavailable because the uploader is hidden while local gates are false |

## Optional Visibility-Only Check

Skipped. The default-off state was fully verified, and the optional check would have required another staging revision churn. `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=true` was not set.

## Staging Log Review

Reviewed logs for final staging revision `nfl-studio-dashboard-staging-00023-ljf`.

| Metric | Result |
|---|---|
| Log entries reviewed | 16 |
| ERROR-like entries | 0 |
| WARNING-like entries | 0 |
| Traceback-like entries | 0 |
| Startup hard errors | 0 |
| Runtime hard errors | 0 |
| `use_container_width` messages | 0 |
| BigQuery Storage fallback messages | 0 |
| Local subprocess execution evidence | 0 |
| LLM action evidence | 0 |
| Cloud Run Job trigger evidence | 0 |

Recent Cloud Run Job executions remain older than this phase. The latest listed executions were prior validate-warehouse and materialize-ai-vibes jobs from June 19, 2026 and June 3, 2026. No execution was created during Phase 25.10.

Cloud Scheduler list was not enabled for this project: the Cloud Scheduler API is disabled. No Scheduler job was created or enabled in this phase.

## Production Untouched Verification

Read-only production describe confirmed:

| Field | State |
|---|---|
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00076-p6s` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4` |
| Traffic | `100%` to `nfl-studio-dashboard-00076-p6s` |
| Trade History compatibility | false |
| Trade Analyzer score UI | false |
| Trade score compatibility | false |
| Data Ops Cloud Run job trigger flags | false |
| New local Data Ops flags | unset or false |

## Remaining Warnings

- This phase required multiple staging-only revisions because browser QA found two issues after the initial deploy: visible scouting upload control and blank Trade Lab rendering.
- The optional visibility-only local-controls check was skipped to avoid extra staging churn.
- Historical Phase 17 through Phase 24 validation reports remain untracked owner-review artifacts from prior phases.

## Recommendation

Build a production candidate for the Data Ops local-control hardening package only after owner review of the added REST dataframe adjustment and the staging evidence above. Keep all production risk flags false, including both Trade Analyzer score flags and both Data Ops trigger gates.
