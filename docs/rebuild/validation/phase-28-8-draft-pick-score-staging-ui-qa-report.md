# Phase 28.8 - Draft-Pick Score Staging UI QA

Final decision: **DRAFT PICK SCORE STAGING UI PASS WITH WARNINGS**

## Scope

Deployed the Phase 28 draft-pick score UI integration to staging only and ran authenticated staging QA. Production was not deployed or changed.

No score materialization, ingestion, Cloud Run Job trigger, Scheduler job, LLM-backed action, Pigskin prompt, Firebase artifact, or production authorization gate was used.

## Authorization And Gate State

Process gates were confirmed unset before staging work:

- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`: unset
- `ALLOW_TRADE_SCORE_MATERIALIZATION`: unset
- `ALLOW_PROJECTION_CONTEXT_REFRESH`: unset
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`: unset
- `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST`: unset
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`: unset

Final check also showed these gates remained unset.

## Source And Git State

Latest committed source before deploy:

- `6158549 Document Trade Score v1 Track A closeout`

No files were staged. The worktree still contains the Phase 28 source/test/report changes and historical validation backlog as owner-review artifacts.

Generated browser and build evidence was written under ignored `output/` paths and was not staged.

## Pre-Build Checks

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile app.py`
- `.\venv\Scripts\python.exe -m py_compile src\trade_pick_scores.py`
- `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_trade_pick_scores`
- `.\venv\Scripts\python.exe -m unittest tests.test_trade_pick_score_contracts`
- `.\venv\Scripts\python.exe -m unittest tests.test_streamlit_compat_rollout`
- `.\venv\Scripts\python.exe -m unittest tests.test_staging_ui_warning_fixes`
- `.\venv\Scripts\python.exe -m unittest tests.test_data_ops_local_controls`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_pick_scores`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_pick_scores`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores`

Validation dry-run discovered 178 validation files. `trade_pick_scores`, `compat_trade_pick_scores`, `trade_player_scores`, and `compat_trade_player_scores` validations passed. `178_trade_pick_scores_model_version_coverage.sql` returned the expected informational coverage warning for `trade_pick_score_v0_2026_001` with 64 rows.

## Warehouse Verification

Read-only pick-score checks:

- `trade_pick_scores`: 64 rows
- `trade_pick_scores_current`: 64 rows
- `compat_trade_pick_scores_current`: 64 rows
- PPR rows: 64
- Exact-slot rows: 48
- Round-only rows: 16
- Duplicate current grain rows: 0
- Invalid `pick_score` rows: 0
- Invalid `confidence_score` rows: 0
- Missing JSON rows: 0
- Raw/source dependency count for `compat_trade_pick_scores_current`: 0

Top pick proof:

- `pick_label`: `2026 Pick 1.01`
- `source_pick_key`: `fantasycalc:2026pick101:PICK:UNK`
- `pick_score`: `96.7`
- `confidence_score`: `88.0`
- `score_tier`: `elite`
- `pick_year`: `2026`
- `pick_class`: `exact_slot`
- `pick_round`: `1`
- `pick_slot`: `1`
- `model_version`: `trade_pick_score_v0_2026_001`

Read-only player-score checks:

- `trade_player_scores`: 154 rows
- v1 player score rows: 77
- `compat_trade_player_scores_current`: 77 rows
- Pick rows in `trade_player_scores`: 0

Player score examples:

- Bijan Robinson: `trade_score=88.926`, `confidence_score=79.53`, tier `elite`, model `trade_score_v1_2025_001`
- Ja'Marr Chase: `trade_score=83.3525`, `confidence_score=78.35`, tier `strong`, model `trade_score_v1_2025_001`

## Build Result

Built staging image with Cloud Build.

- Image tag: `staging-pick-score-ui-615854978e09-20260628T192258Z`
- Build ID: `2acfae69-c6e0-47a9-a483-98d6a5c7d579`
- Build status: `SUCCESS`
- Digest: `sha256:2c3a2a2ed19cd81f9f616bf87c613a0145e2686e9987e3550948f1a7efca91d6`
- Digest-pinned image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:2c3a2a2ed19cd81f9f616bf87c613a0145e2686e9987e3550948f1a7efca91d6`

## Staging Deploy Result

Staging service only:

- Service: `nfl-studio-dashboard-staging`
- Project: `fantasy-football-498121`
- Region: `us-central1`
- Original staging revision before deploy: `nfl-studio-dashboard-staging-00024-2wm`
- Initial Phase 28.8 deploy revision: `nfl-studio-dashboard-staging-00025-wc6`
- Final staging revision after flag rollback restore: `nfl-studio-dashboard-staging-00027-pq9`
- Final traffic: `nfl-studio-dashboard-staging-00027-pq9=100`
- Final image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:2c3a2a2ed19cd81f9f616bf87c613a0145e2686e9987e3550948f1a7efca91d6`
- Staging URL: `https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app`

Final staging flag state:

- `USE_COMPAT_TRADE_PLAYER_HISTORY=true`
- `USE_TRADE_ANALYZER_SCORE_V0=true`
- `USE_COMPAT_TRADE_PLAYER_SCORE=true`
- `USE_TRADE_PICK_SCORE_V0=true`
- `USE_COMPAT_TRADE_PICK_SCORE=true`
- `USE_COMPAT_PLAYER_PROFILES=false`
- `USE_COMPAT_SLEEPER_WATCH=false`
- `USE_COMPAT_TRADE_ASSETS=false`
- `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`
- `USE_BACKTEST_DASHBOARD=false`
- `USE_CLAIM_LEDGER_UI=false`
- `USE_CONTENT_BRIEF_REVIEW_UI=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

## HTTP Health

Authenticated HTTP checks passed:

- `/_stcore/health`: `200 ok`
- `/`: `200`, Streamlit shell present, no `Traceback` in the root response

## Browser QA

Browser QA used authenticated Playwright through a local bearer-token proxy because the in-app browser could not attach Cloud Run IAM credentials and returned `403 Forbidden`.

Final tab smoke on restored staging revision:

- Login/session gate: passed
- Pigskin Studio: loaded
- Show Prep: loaded
- Player Profiles: loaded
- Versus Finder: loaded
- Viewer Team Lab: loaded
- Trade Lab: loaded
- Data Ops: loaded
- `execute_bigquery_sql`: absent
- Pigskin `weekly_metrics` raw/source exposure: absent
- No `Traceback`, `KeyError`, `NameError`, `pos_abb`, or `rolling_3_week_ppr` regression observed

Data Ops:

- Cloud Run path displayed `Disabled`
- Trigger allow flag displayed `Disabled`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- Local subprocess controls remained hidden or disabled
- No Data Ops control was clicked

## Player Score UI

Trade Lab player-score lane passed:

- Selected `Bijan Robinson` for Side A
- Selected `Ja'Marr Chase` for Side B
- Player score cards rendered from `compat_trade_player_scores_current`
- Model context showed `trade_score_v1_2025_001`
- Bijan score rendered as `88.93`
- Ja'Marr Chase score rendered as `83.35`
- `Pigskin Trade Score source: compat_trade_player_scores_current` was present
- Market totals remained separate from player and pick score totals
- No crash

## Exact-Slot Pick UI

Trade Lab exact-slot pick lane passed:

- Selected `2026 Pick 1.01`
- Pick score source marker showed `compat_trade_pick_scores_current`
- Side A Pick Score rendered as `96.7`
- Scored picks rendered as `1 of 1`
- Pick score remained separate from player Pigskin Trade Score
- Selected asset summary showed `2026 Pick 1.01 (PICK - N/A)`
- Market value total rendered as `7084`
- No crash

Expanded pick detail evidence:

- Model: `trade_pick_score_v0_2026_001`
- Tier: `elite`
- Confidence: `88.0`
- Year: `2026`
- Round: `1`
- Slot: `1.0`
- Class: `exact_slot`
- Bucket: `exact`
- Warning categories rendered
- Pick warning details expander rendered
- Pick source freshness expander rendered

Component scores render as a Streamlit dataframe. The browser text extraction did not expose dataframe cell text, but the component table area rendered and tests cover the expected component keys:

- `market_score`
- `slot_capital_score`
- `time_discount_score`
- `liquidity_certainty_score`
- `college_context_score`
- `uncertainty_risk_score`

## Round-Only Pick UI

Trade Lab round-only pick lane passed with one display warning:

- Selected `2026 1st`
- Side A Pick Score rendered as `55.71`
- Scored picks rendered as `1 of 1`
- Expanded detail showed model `trade_pick_score_v0_2026_001`
- Pick class rendered as `round_only`
- Pick slot rendered as `N/A`
- Tier rendered as `speculative`
- Confidence rendered as `74.0`
- No crash

Warning: the required text expected "pick_slot is null or displayed as unavailable." The UI displays `slot N/A`, which is acceptable but should be normalized to the clearer `round-only` wording in a follow-up polish pass.

The browser text captured warning categories but did not expose the nested warning-detail dataframe rows. Validation and unit coverage confirm round-only missing flags are present in the score payload.

## Mixed Player/Pick Behavior

Browser automation verified the separate score-lane labels and captions, but could not create a same-side mixed asset state.

Observed limitation:

- After selecting `Bijan Robinson` on Side A, the expected `Select Asset A 2` control did not surface during browser automation.
- Player score remained valid for the selected player.
- Pick score lane remained separate and did not add to player score.

Covered by tests:

- `tests.test_staging_ui_warning_fixes` covers mixed player and pick side detection.
- `src.ui_data_guards.trade_side_has_mixed_player_and_pick_assets` keeps player and pick score lanes separate.

Recommended follow-up: investigate why the dynamic extra Side A selector did not surface in headless staging QA after a successful first Side A selection.

## Unavailable-Score Behavior

The UI does not expose a scoring-context selector in this flow. Phase 28.6 materialized only PPR rows, so non-PPR unavailable-score behavior could not be browser-tested in this phase.

The unavailable-score copy is present in code and tests:

- `Pick Score unavailable for <side>: <pick> (No compatible pick score row for this scoring context)`
- `Pick Score N/A. Reason: No compatible pick score row for this scoring context.`

Recommended follow-up: test non-PPR unavailable-score behavior when the Trade Lab exposes scoring context selection.

## Flag Rollback Behavior

Staging-only flag rollback was exercised.

Flag-off update:

- Revision: `nfl-studio-dashboard-staging-00026-lc8`
- `USE_TRADE_PICK_SCORE_V0=false`
- `USE_COMPAT_TRADE_PICK_SCORE=false`
- Player score flags remained true
- Health returned `200 ok`

The flag-off browser probe timed out before tabs rendered, so UI disappearance was not fully browser-confirmed. The service describe confirmed both pick flags were false.

Flag restore:

- Revision: `nfl-studio-dashboard-staging-00027-pq9`
- `USE_TRADE_PICK_SCORE_V0=true`
- `USE_COMPAT_TRADE_PICK_SCORE=true`
- Health returned `200 ok`
- Final staging revision is serving 100 percent traffic

Warning: PowerShell reported `NativeCommandError` for the two `gcloud run services update` calls because progress text was emitted on stderr. Both updates completed successfully and created the expected staging revisions.

## Staging Log Review

Recent staging logs for revisions `00025-wc6`, `00026-lc8`, and `00027-pq9`:

- Entries inspected: 500
- Severity counts: `INFO=470`, `NOTICE=2`, `DEFAULT=28`
- `ERROR`: 0
- `WARNING`: 0
- Traceback-like matches: 0
- Exception-like matches: 0
- Pick-score UI error matches: 0
- JSON parse error matches: 0
- Source-freshness error matches: 0
- Local subprocess evidence: 0
- LLM action evidence: 0
- Cloud Run Job trigger evidence: 0

## Production Untouched

Read-only production describe confirmed production was unchanged:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Traffic: `nfl-studio-dashboard-00077-2jp=100`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- `USE_TRADE_PICK_SCORE_V0`: unset
- `USE_COMPAT_TRADE_PICK_SCORE`: unset
- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

## Remaining Warnings

- In-app browser could not authenticate to IAM-protected staging and returned `403 Forbidden`; Playwright with a local authenticated proxy was used instead.
- Same-side mixed player/pick selection could not be created in headless browser QA because `Select Asset A 2` did not appear after selecting Side A.
- Round-only pick detail displays `slot N/A`; clearer `round-only` copy would reduce ambiguity.
- Component and warning-detail rows render as Streamlit dataframes, which browser body text extraction does not expose. Screenshots and tests provide supporting evidence.
- Flag-off browser probe timed out before tabs rendered, but service describe and health checks confirmed the flag state.

## Recommended Next Phase

- Phase 28.9: fix or explain the dynamic multi-asset selector behavior for same-side mixed player/pick QA.
- Add a small UI polish pass for round-only slot copy: render `round-only` rather than `N/A`.
- Add a context-selector or fixture path to explicitly browser-test non-PPR pick-score unavailable behavior.
- Prepare a release package review for the Phase 28 pick-score lane only after the mixed-side browser limitation is resolved or accepted.
