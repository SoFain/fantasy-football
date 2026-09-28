# Phase 27.8 Trade Score V1 UI Polish Staging QA Report

Generated: 2026-06-27

## Final Decision

TRADE SCORE V1 UI POLISH STAGING QA PASS WITH WARNINGS

## Scope Confirmation

Staging deploy and read-only QA only. No production deploy, production flag change, score materialization, ingestion, Cloud Run Job trigger, Scheduler job, LLM-backed action, Pigskin prompt, scrape, Firebase artifact, or commit occurred.

Authorization gates were checked before build and were unset:

- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `ALLOW_PROJECTION_CONTEXT_REFRESH`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

## Git State

Current release source was dirty by design for the Phase 27.7 UI polish:

- `app.py` modified
- `src/trade_player_scores.py` modified
- `tests/test_trade_player_scores.py` modified
- `docs/rebuild/validation/phase-27-7-trade-score-v1-ui-explainability-polish-report.md` untracked
- historical Phase 17 through Phase 27 validation backlog remains untracked

No generated browser artifacts were staged or committed.

## Pre-Build Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | pass |
| `py_compile app.py` | pass |
| `compileall -q src scripts` | pass |
| `unittest tests.test_trade_player_scores` | pass, 40 tests |
| `unittest tests.test_streamlit_compat_rollout` | pass, 10 tests |
| `unittest tests.test_staging_ui_warning_fixes` | pass, 13 tests |
| `unittest tests.test_data_ops_local_controls` | pass, 6 tests |
| `unittest discover tests` | pass, 367 tests |
| `run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `run_bigquery_validations.py --dry-run` | pass, 160 validation files discovered |
| `run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 passed |
| `run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 passed |

The full suite emitted existing mocked job, load, and pipeline logs. No live ingestion or score materialization was run.

## V1 BigQuery And View Verification

Read-only checks confirmed the expected score state.

| Metric | Value |
| --- | ---: |
| total `trade_player_scores` rows | 154 |
| v0 rows | 77 |
| v1 rows | 77 |
| target v1 rows, 2025 week 18 PPR redraft one-QB | 77 |
| target duplicate grains | 0 |
| target PICK rows | 0 |
| target missing `model_run_id` rows | 0 |
| target unresolved identity rows | 0 |
| target invalid score rows | 0 |
| target missing JSON rows | 0 |

Both current views surface v1:

| View | Model Version | Season | Week | Context | Rows |
| --- | --- | ---: | ---: | --- | ---: |
| `trade_player_scores_current` | `trade_score_v1_2025_001` | 2025 | 18 | `ppr/redraft/one_qb` | 77 |
| `compat_trade_player_scores_current` | `trade_score_v1_2025_001` | 2025 | 18 | `ppr/redraft/one_qb` | 77 |

Validation `159_compat_trade_player_scores_no_raw_source_dependencies.sql` passed with `raw_source_dependency_count = 0`.

## Build Result

Cloud Build completed successfully.

| Field | Value |
| --- | --- |
| build ID | `b5878748-9266-413f-ac7b-fcb28530d3ce` |
| build status | `SUCCESS` |
| source commit label | `aa543d0042d2` |
| image tag | `staging-aa543d0042d2-20260627T214135Z` |
| image URI | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-aa543d0042d2-20260627T214135Z` |
| digest | `sha256:6efdc0f4895ab4769b3de933f4e12da5dc4a62f12b5fac7e3afe49c89f5358a7` |
| digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:6efdc0f4895ab4769b3de933f4e12da5dc4a62f12b5fac7e3afe49c89f5358a7` |

Warning: PowerShell surfaced the initial `gcloud builds submit` progress output as a native-command error, but `gcloud builds list` confirmed the build succeeded.

## Staging Deploy Result

Staging service only:

| Field | Value |
| --- | --- |
| service | `nfl-studio-dashboard-staging` |
| project | `fantasy-football-498121` |
| region | `us-central1` |
| revision | `nfl-studio-dashboard-staging-00024-2wm` |
| traffic | `nfl-studio-dashboard-staging-00024-2wm:100` |
| image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:6efdc0f4895ab4769b3de933f4e12da5dc4a62f12b5fac7e3afe49c89f5358a7` |
| service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| URL | `https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app` |

Staging flag state:

| Flag | State |
| --- | --- |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `true` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `true` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `true` |
| `USE_COMPAT_PLAYER_PROFILES` | `false` |
| `USE_COMPAT_SLEEPER_WATCH` | `false` |
| `USE_COMPAT_TRADE_ASSETS` | `false` |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | `false` |
| `USE_BACKTEST_DASHBOARD` | `false` |
| `USE_CLAIM_LEDGER_UI` | `false` |
| `USE_CONTENT_BRIEF_REVIEW_UI` | `false` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |

## Authenticated HTTP Checks

Authenticated HTTP used `gcloud auth print-identity-token` through direct requests.

| Path | Result |
| --- | --- |
| `/_stcore/health` | 200, `ok` |
| `/` | 200, Streamlit shell present, no `Traceback` |

The plain identity token worked. An audience-scoped token returned 401 and was not used for QA.

## Browser QA Method

Playwright browser QA used a temporary local Node auth proxy under `output/playwright/phase-27-8/` because private Cloud Run websocket traffic does not complete with browser-level HTTP auth headers alone. The proxy injected the active gcloud identity token into HTTP and Streamlit websocket traffic.

Generated browser evidence was written under `output/playwright/phase-27-8/` and was not staged or committed. The local proxy process was stopped after QA.

## Browser QA Results

Authenticated Streamlit login succeeded through the proxy.

| Area | Result |
| --- | --- |
| Login/session gate | pass |
| Pigskin Studio | loads, no `execute_bigquery_sql`, no traceback |
| Show Prep | loads, no `rolling_3_week_ppr` regression |
| Player Profiles | loads, no `pos_abb` regression |
| Versus Finder | loads, no `pos_abb` regression |
| Viewer Team Lab | loads |
| Trade Lab | loads |
| Data Ops | loads |
| Hard errors | no `Traceback`, `KeyError`, or `NameError` observed |
| LLM actions | none clicked |
| Pigskin prompts | none submitted |
| Data Ops actions | none clicked |

## Trade Lab Model Version Display

Trade Lab showed:

`Active model: trade_score_v1_2025_001 | Model run: weekly_projection-2025-18-20260618T152142Z-6752df98 | Target: 2025 week 18 | Context: ppr / redraft / one_qb`

The score source marker remained:

`Pigskin Trade Score source: compat_trade_player_scores_current`

## Bijan Robinson vs Ja'Marr Chase

Browser selection:

| Side | Asset | UI Score | Expected V1 Score | Tier | Confidence |
| --- | --- | ---: | ---: | --- | ---: |
| A | Bijan Robinson | 88.93 | 88.926 | elite | 79.53 |
| B | Ja'Marr Chase | 83.35 | 83.3525 | strong | 78.35 |

Verified:

- selected asset summaries render
- side Pigskin Trade Score totals render
- fairness delta renders as `5.58`
- market totals remain separate from score totals
- component breakdown expanders render tiers, confidence, risk, Fraud Watch score, and component scores
- source freshness expanders render score model context, projection model run, target season/week, scoring profile, league type, and roster format

## A.J. Brown vs Malik Nabers

Browser selection:

| Side | Asset | UI Score | Expected V1 Score | Tier | Confidence |
| --- | --- | ---: | ---: | --- | ---: |
| A | A.J. Brown | 57.11 | 57.1075 | flex | 76.78 |
| B | Malik Nabers | 63.92 | 63.9194 | starter | 44.86 |

Verified:

- A.J. Brown shows grouped warning categories including `Team context`
- A.J. Brown warning details include `team_context_mismatch_warning`
- Malik Nabers shows lower confidence `44.86`
- Malik Nabers warning details include `Role/source coverage`
- Malik Nabers grouped warning table includes `efficiency_fallback_used`, `missing_snaps_last_3`, and `role_usage_fallback_used`
- raw warning details remain available in player-specific expanders
- long raw warning lists are not dumped into the main card

## Source Freshness Expander

The expanded source freshness tables showed:

- `score_model` `model_version = trade_score_v1_2025_001`
- `score_model` `model_run_id = weekly_projection-2025-18-20260618T152142Z-6752df98`
- target `season = 2025`
- target `week = 18`
- target `scoring_profile_id = ppr`
- target `league_type_id = redraft`
- target `roster_format_id = one_qb`
- `projection_rankings_current` model run
- `projection_rankings_current` created timestamp
- effective projection as-of season/week

Read-only JSON checks confirmed raw projection as-of fields are currently null for the checked players, and `projection_freshness_metadata_missing` is present in `missing_flags_json`. The UI displays this safely through the warning summary and details table rather than crashing.

## Draft Pick Unavailable Behavior

Selected `2026 Pick 1.01`.

Verified:

- market value displays
- projected value displays
- side Pigskin Trade Score is `N/A`
- unavailable warning says `2026 Pick 1.01 (draft pick score lane pending)`
- component breakdown says `2026 Pick 1.01: Pigskin Trade Score N/A. Reason: draft pick score lane pending.`
- no player-score component breakdown pretends the pick has a player score
- no crash

## Data Ops Gating

Verified in browser:

- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS is false`
- `DATA_OPS_ALLOW_JOB_TRIGGER is false`
- Cloud Run Job execution text says it is not active
- `Trigger Cloud Run Job` button is present but disabled
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS is false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER is false`
- local subprocess controls are described as disabled by default
- local mutating buttons checked were disabled
- scouting CSV upload remains disabled while local gates are false

No Data Ops trigger, local subprocess control, ingestion, or warehouse write button was clicked.

## Staging Log Review

New staging revision `nfl-studio-dashboard-staging-00024-2wm`, last 2 hours:

| Metric | Count |
| --- | ---: |
| log entries inspected | 300 |
| ERROR severity | 0 |
| WARNING severity | 0 |
| traceback-like entries | 0 |
| score UI error-like entries | 0 |
| local subprocess evidence | 0 |
| LLM action evidence | 0 |
| Cloud Run Job trigger evidence | 0 |

## Cloud Run Job Metadata

Read-only `cloud_run_job_runs` check showed the latest job run is still the prior `validate-warehouse` proof from 2026-06-19 17:27:33 UTC. No Cloud Run Job was triggered by this phase.

## Production Untouched Confirmation

Read-only production describe:

| Field | Value |
| --- | --- |
| service | `nfl-studio-dashboard` |
| revision | `nfl-studio-dashboard-00077-2jp` |
| traffic | `nfl-studio-dashboard-00077-2jp:100` |
| image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |

Production flags remain safe:

- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`
- all other listed production risk flags false

## Remaining Warnings

- Staging browser QA required a temporary local auth proxy for private Cloud Run websocket traffic. The proxy was stopped and artifacts remain generated-only under `output/playwright/phase-27-8/`.
- Source freshness data confirms raw projection as-of fields are currently null for checked v1 rows. The UI surfaces `projection_freshness_metadata_missing` safely.
- Data Ops trigger controls are visible but disabled. This matches the current hardening behavior and tests.

## Recommended Next Phase

Run a release-package review for the Phase 27.7 and 27.8 changes before any production score rollout. Keep production score flags false until a separate production gate explicitly approves them.

