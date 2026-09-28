# Phase 27.6 Trade Score V1 Staging UI Validation Report

## Final Decision

TRADE SCORE V1 STAGING UI PASS WITH WARNINGS

Staging Trade Lab reads the intended v1 score rows through `compat_trade_player_scores_current`, displays v1 player scores, preserves draft-pick missing-score behavior, and keeps production disabled.

No deployment, production flag change, score materialization, Cloud Run Job trigger, Scheduler job, ingestion, LLM action, Pigskin prompt, scrape, Firebase artifact, or commit occurred.

## Gate State

All authorization gates were unset before validation and after browser QA:

| Gate | State |
| --- | --- |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

## Local Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | pass |
| `py_compile app.py` | pass |
| `compileall -q src scripts` | pass |
| `unittest discover tests` | pass, 363 tests |
| BigQuery validation dry-run | pass, 160 validation files discovered |
| `--pattern trade_player_scores` | pass, 11 of 11 |
| `--pattern compat_trade_player_scores` | pass, 2 of 2 |

The full test suite emitted existing mocked pipeline/load logs. No live ingestion was run.

## V1 BigQuery Verification

Read-only checks confirmed the bounded v1 materialization state:

| Metric | Value |
| --- | ---: |
| total `trade_player_scores` rows | 154 |
| `trade_score_v0_2025_001` rows | 77 |
| `trade_score_v1_2025_001` rows | 77 |
| target v1 rows, 2025 week 18 PPR redraft one-QB | 77 |
| target v1 duplicate grains | 0 |
| target v1 PICK rows | 0 |
| target v1 missing `model_run_id` rows | 0 |
| target v1 unresolved identity rows | 0 |
| target v1 invalid score rows | 0 |
| target v1 missing JSON rows | 0 |

## Compatibility View Behavior

`trade_player_scores_current` and `compat_trade_player_scores_current` both surfaced only v1 rows for the current score slice:

| View | Model Version | Season | Week | Rows |
| --- | --- | ---: | ---: | ---: |
| `trade_player_scores_current` | `trade_score_v1_2025_001` | 2025 | 18 | 77 |
| `compat_trade_player_scores_current` | `trade_score_v1_2025_001` | 2025 | 18 | 77 |

The current view chooses the latest row per player/profile/context by `season DESC`, `week DESC`, `created_at DESC`, `model_version DESC`, and `score_run_id DESC`. Because v1 rows were created after v0 rows for the same season/week/context, staging currently reads v1.

Warning: the UI does not display `model_version` directly. The staging proof relies on the compatibility view model-version count and exact v1 score matches in the Trade Lab cards. A later UI improvement should expose the active model version in the score source marker.

## Staging Service State

Read-only Cloud Run describe:

| Field | Value |
| --- | --- |
| service | `nfl-studio-dashboard-staging` |
| revision | `nfl-studio-dashboard-staging-00023-ljf` |
| traffic | `nfl-studio-dashboard-staging-00023-ljf:100` |
| image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:a1eb5955787ff0801da74daf5653f77f5594456ad9cb35e78204200adfc3efb6` |
| URL | `https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app` |
| service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |

Staging flag state:

| Flag | State |
| --- | --- |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `true` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `true` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `true` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |
| `USE_COMPAT_PLAYER_PROFILES` | `false` |
| `USE_COMPAT_SLEEPER_WATCH` | `false` |
| `USE_COMPAT_TRADE_ASSETS` | `false` |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | `false` |

## HTTP And Browser Access

Authenticated HTTP checks against staging passed:

| Path | Result |
| --- | --- |
| `/_stcore/health` | 200, `ok` |
| `/` | 200, Streamlit shell present, no `Traceback` |

The in-app browser was not authenticated to Cloud Run and returned 403. The local Cloud SDK could not install `cloud-run-proxy` without administrator rights. For read-only browser QA, a temporary local proxy was started under `%TEMP%` to forward only staging requests with the active gcloud identity token, including Streamlit websocket traffic. The proxy was stopped after QA.

Local Playwright Chromium was installed because the Python Playwright package was present but its browser runtime was missing. Browser evidence was written under `output/playwright/phase-27-6/` and was not staged or committed.

## Browser QA Results

Authenticated Streamlit login succeeded through the temporary proxy.

| Area | Result |
| --- | --- |
| Login/session gate | pass |
| Pigskin Studio | loads, no `execute_bigquery_sql`, no raw/source table list visible in checked text |
| Show Prep | loads, no `rolling_3_week_ppr` regression |
| Player Profiles | loads, no `pos_abb` regression |
| Versus Finder | loads, no inherited `pos_abb` regression |
| Viewer Team Lab | loads |
| Trade Lab | loads after BigQuery-backed panel finishes, roughly 40 seconds in this run |
| Data Ops | loads, Cloud Run path disabled, trigger allow flag disabled, local controls disabled |
| Hard errors | no `Traceback`, `KeyError`, or `NameError` observed |
| LLM actions | no LLM-backed action clicked |
| Pigskin prompts | no Pigskin prompt submitted |
| Data Ops actions | no local subprocess or Cloud Run trigger clicked |

Data Ops displays a `Trigger Cloud Run Job` button, but it is disabled while `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false` and `DATA_OPS_ALLOW_JOB_TRIGGER=false`. The page also states Cloud Run Job execution is not active and local subprocess controls use separate default-off gates.

## Trade Lab V1 Score Examples

### Bijan Robinson vs Ja'Marr Chase

Selected in Trade Lab:

| Side | Asset | UI Score | Expected V1 Score | Tier | Confidence |
| --- | --- | ---: | ---: | --- | ---: |
| A | Bijan Robinson | 88.93 | 88.926 | elite | 79.53 |
| B | Ja'Marr Chase | 83.35 | 83.3525 | strong | 78.35 |

Observed UI behavior:

- `Pigskin Trade Score source: compat_trade_player_scores_current` displayed.
- Side totals displayed separately from market values.
- Fairness delta displayed as 5.58.
- Component expanders rendered score, tier, confidence, risk, Fraud Watch score, missing-data warnings, and source freshness.
- `projection_freshness_metadata_missing` appeared in missing-data warnings.
- No crash.

### A.J. Brown vs Malik Nabers

Selected in Trade Lab:

| Side | Asset | UI Score | Expected V1 Score | Tier | Confidence | Warning Evidence |
| --- | --- | ---: | ---: | --- | ---: | --- |
| A | A.J. Brown | 57.11 | 57.1075 | flex | 76.78 | `team_context_mismatch_warning` |
| B | Malik Nabers | 63.92 | 63.9194 | starter | 44.86 | `role_usage_fallback_used`, `efficiency_fallback_used` |

Observed UI behavior:

- Team-context mismatch was visible in A.J. Brown missing-data warnings.
- Malik Nabers low-confidence row rendered without crashing.
- Projection freshness warnings remained visible.
- Source freshness JSON rendered in truncated caption form.

## Draft Pick Behavior

Selected `2026 Pick 1.01` against Bijan Robinson:

| Check | Result |
| --- | --- |
| pick market value | displayed, 7084 |
| pick projected value | displayed, 7084 |
| pick player score row | absent |
| Side A Pigskin Trade Score | `N/A` |
| unavailable warning | `Pigskin Trade Score unavailable for Side A: 2026 Pick 1.01` |
| component breakdown | `2026 Pick 1.01: score unavailable` |
| misleading player score | not observed |
| crash | not observed |

This confirms draft picks remain market-only for now and are not misrepresented as materialized player-score rows.

## Staging Log Review

Read-only Cloud Logging review for revision `nfl-studio-dashboard-staging-00023-ljf`:

| Metric | Value |
| --- | ---: |
| log entries reviewed | 300 |
| INFO entries | 296 |
| DEFAULT entries | 4 |
| WARNING or higher | 0 |
| ERROR or higher | 0 |
| `Traceback` matches | 0 |
| `KeyError` matches | 0 |
| `NameError` matches | 0 |
| `pos_abb` matches | 0 |
| `rolling_3_week_ppr` matches | 0 |
| local subprocess evidence | 0 |
| Cloud Run Job execution evidence | 0 |
| LLM action evidence | 0 |
| `execute_bigquery_sql` evidence | 0 |

Recent Cloud Run Job executions remain prior jobs from June 19, 2026 or earlier. No Cloud Run Job was triggered during Phase 27.6.

## Production Untouched Confirmation

Read-only production describe:

| Field | Value |
| --- | --- |
| service | `nfl-studio-dashboard` |
| revision | `nfl-studio-dashboard-00077-2jp` |
| traffic | `nfl-studio-dashboard-00077-2jp:100` |
| image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `false` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `false` |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `false` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |

No production deploy or production flag command was run.

## Remaining Warnings

- Trade Lab does not display the active score `model_version` directly. It should.
- Trade Lab took roughly 40 seconds to render the BigQuery-backed score panel in this browser run.
- Source freshness captions are truncated by current UI behavior, which keeps the page readable but hides deeper freshness detail.
- Data Ops keeps the Cloud Run trigger button visible but disabled. That is gated, but the visual affordance may still be confusing.
- The temporary proxy saw transient dynamic DataFrame JS fetch errors during early QA attempts. The asset was later reachable through the proxy, and no staging service log errors appeared.
- Browser evidence under `output/playwright/phase-27-6/` is generated QA output and should not be committed unless explicitly reviewed.

## Recommended Next Phase

Proceed to a focused UI follow-up before production score exposure:

- add model-version visibility to the Trade Lab score source marker;
- optionally summarize warning categories instead of showing long raw warning lists;
- consider making disabled Data Ops trigger controls visually read-only when both job gates are false;
- keep production score flags false until a separate production rollout gate approves them.
