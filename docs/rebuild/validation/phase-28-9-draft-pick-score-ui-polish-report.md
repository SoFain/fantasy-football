# Phase 28.9 Draft-Pick Score UI Polish Report

Final decision: **DRAFT PICK SCORE UI POLISH NEEDS STAGING QA**

Generated: 2026-06-28 16:38 ET

## Scope

Phase 28.9 investigated the Phase 28.8 staging QA warnings for draft-pick score UI:

- same-side mixed player/pick selection could not be created in browser QA;
- round-only pick detail displayed `slot N/A`;
- non-PPR unavailable-score behavior was not browser-testable because the Trade Lab has no scoring-context selector;
- component and warning details were mostly inside Streamlit dataframes, which browser text extraction does not read well.

This phase was code, test, and read-only verification only. No deploy, BigQuery write, materialization, ingestion, Cloud Run Job trigger, Scheduler job, LLM action, Pigskin prompt, or Firebase artifact was created.

## Authorization Gates

Checked process environment gates before work:

- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`: unset
- `ALLOW_TRADE_SCORE_MATERIALIZATION`: unset
- `ALLOW_PROJECTION_CONTEXT_REFRESH`: unset
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`: unset
- `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST`: unset
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`: unset

No authorization gate was set in this phase.

## Git State

No files were staged.

Modified tracked files present in the working tree:

- `app.py`
- `docs/rebuild/compatibility-contracts.md`
- `docs/rebuild/table-classification.md`
- `src/compat_flags.py`
- `src/ui_data_guards.py`
- `tests/test_data_ops_local_controls.py`
- `tests/test_staging_ui_warning_fixes.py`
- `tests/test_streamlit_compat_rollout.py`

Relevant untracked Phase 28 files remain present, including draft-pick score contracts, views, validations, source/tests, and Phase 28 validation reports. Historical Phase 17 through Phase 27 validation backlog also remains untracked.

## Files Changed In This Phase

Phase 28.9 code and test changes were made in:

- `app.py`
- `src/ui_data_guards.py`
- `tests/test_staging_ui_warning_fixes.py`
- `tests/test_streamlit_compat_rollout.py`
- `docs/rebuild/validation/phase-28-9-draft-pick-score-ui-polish-report.md`

The existing uncommitted Phase 28 pick-score lane files were not staged or committed.

## Mixed-Side Selector Investigation

Result: **real UI timing bug fixed in code, needs staging browser QA**

The Trade Lab selector code rendered existing selectors first, collected selected assets, then incremented `st.session_state.num_a` or `st.session_state.num_b` after the selector loop:

- Side A rendered `range(st.session_state.num_a)`;
- asset selection was collected;
- if every visible selector was filled, the count was incremented after rendering.

That means `Select Asset A 2` was not available in the same rerun that processed the first selection. Browser QA selected a Side A player, then could not find the second selector without another UI rerun path.

Fix:

- added `trade_asset_selector_count_with_blank` in `src/ui_data_guards.py`;
- Side A and Side B now render the next blank selector in the same run when the visible side is fully filled;
- assets and unresolved labels are recomputed after the extra selector render.

Relevant code:

- `src/ui_data_guards.py:99`
- `app.py:4252`
- `app.py:4278`

Tests added:

- `test_trade_lab_selector_count_keeps_blank_after_filled_side`
- `test_trade_lab_renders_extra_side_a_selector_in_same_rerun`
- `test_trade_lab_renders_extra_side_b_selector_in_same_rerun`

## Mixed-Side Score Separation

Player and pick score lanes remain separate:

- market totals remain combined;
- player score totals use only player assets;
- pick score totals use only draft-pick assets;
- mixed player/pick side warning appears when one side contains both asset types;
- no UI path adds `trade_score` and `pick_score` into one unlabeled number.

Relevant code:

- `app.py:4360`
- `app.py:4362`
- `app.py:4392`
- `app.py:4474`
- `src/ui_data_guards.py:113`
- `src/ui_data_guards.py:124`
- `src/ui_data_guards.py:175`

Tests cover:

- player score rows do not attach to pick assets;
- pick score rows attach only to pick assets;
- mixed side detection remains true when a side contains one player and one pick;
- player and pick score UI source labels remain distinct;
- compatibility queries do not read raw/source draft-pick tables.

## Round-Only Copy Behavior

Result: **fixed in code**

Round-only picks no longer display ambiguous `slot N/A` in the score detail copy. The new display helper returns:

- exact-slot pick with `pick_slot = 1.0`: `1`
- round-only pick with `pick_slot = NULL`: `round-only`

Relevant code:

- `src/ui_data_guards.py:190`
- `app.py:4540`

The UI still shows the underlying class, round, bucket, warning categories, and warning-detail dataframe. The scoring math was not changed.

Tests added:

- `test_trade_pick_slot_display_is_clear_for_exact_and_round_only`

## Non-PPR Unavailable Behavior

The Trade Lab browser flow still has no scoring-context selector, so non-PPR unavailable behavior remains a unit-test proof rather than browser proof in this phase.

Test coverage confirms that when no compatible pick score row exists:

- the pick score remains unavailable;
- the missing count increments;
- the UI copy includes `No compatible pick score row for this scoring context`;
- no additional half-PPR or standard pick rows were materialized.

Tests added:

- `test_non_ppr_missing_pick_score_remains_explicitly_unavailable`

## Warning And Component Summary

Result: **low-risk text summary added**

Pick cards still keep the dataframe detail views, but now include compact browser-readable copy:

- `Components: market, slot capital, time discount, liquidity, college context, uncertainty.`
- `Warnings: <human-readable missing flag labels>`

Relevant code:

- `app.py:4570`
- `app.py:4574`
- `src/ui_data_guards.py:202`

Tests added:

- `test_trade_pick_warning_labels_are_browser_readable`
- `test_pick_score_component_and_warning_text_is_browser_visible`
- `test_pick_score_ui_is_flag_gated_and_uses_compat_view`

## Checks Run

Local checks:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed
- `.\venv\Scripts\python.exe -m py_compile app.py`: passed
- `.\venv\Scripts\python.exe -m py_compile src\trade_pick_scores.py`: passed
- `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py`: passed
- `.\venv\Scripts\python.exe -m compileall -q src scripts`: passed
- `.\venv\Scripts\python.exe -m unittest tests.test_trade_pick_scores`: 21 tests passed
- `.\venv\Scripts\python.exe -m unittest tests.test_trade_pick_score_contracts`: 6 tests passed
- `.\venv\Scripts\python.exe -m unittest tests.test_streamlit_compat_rollout`: 12 tests passed
- `.\venv\Scripts\python.exe -m unittest tests.test_staging_ui_warning_fixes`: 24 tests passed
- `.\venv\Scripts\python.exe -m unittest tests.test_data_ops_local_controls`: 6 tests passed
- `.\venv\Scripts\python.exe -m unittest discover tests`: 407 tests passed

BigQuery validation checks:

- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: discovered 178 validations
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_pick_scores`: 17 passed, 0 failed
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_pick_scores`: 2 passed, 0 failed
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores`: 12 passed, 0 failed
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores`: 2 passed, 0 failed
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: no pending migrations

Expected informational validation warning:

- `178_trade_pick_scores_model_version_coverage.sql` returned `trade_pick_score_v0_2026_001` with 64 rows.

PowerShell printed `NativeCommandError` wrapper text around unittest progress output in one local wrapper, but all command exit codes were `0`.

## Warehouse State Confirmation

Read-only BigQuery checks after the code change:

- `trade_pick_scores`: 64 rows
- `trade_pick_scores` target model rows: 64
- `trade_pick_scores` PPR rows: 64
- `trade_pick_scores` round-only rows: 16
- `trade_pick_scores` null `pick_slot` rows: 16
- `trade_pick_scores_current`: 64 rows
- `compat_trade_pick_scores_current`: 64 rows
- `trade_player_scores`: 154 rows
- `trade_player_scores` rows with `position = PICK`: 0

No BigQuery rows were written in this phase.

## Production Untouched Confirmation

Read-only production describe confirmed:

- service: `nfl-studio-dashboard`
- revision: `nfl-studio-dashboard-00077-2jp`
- traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- service account: `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com`
- `GEMINI_API_KEY`: Secret Manager reference preserved

Production flags:

- `USE_COMPAT_PLAYER_PROFILES=false`
- `USE_COMPAT_SLEEPER_WATCH=false`
- `USE_COMPAT_TRADE_ASSETS=false`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`
- `USE_BACKTEST_DASHBOARD=false`
- `USE_CLAIM_LEDGER_UI=false`
- `USE_CONTENT_BRIEF_REVIEW_UI=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_TRADE_PICK_SCORE_V0`: unset
- `USE_COMPAT_TRADE_PICK_SCORE`: unset
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

No deployment occurred.

## Remaining Warnings

- The selector fix has not been browser-validated in staging yet.
- Non-PPR unavailable behavior remains covered by tests, not browser QA, because the Trade Lab does not expose a scoring-context selector.
- Historical validation reports and owner-review artifacts remain untracked.
- The working tree contains earlier uncommitted Phase 28 pick-score lane changes outside this Phase 28.9 polish pass.

## Recommended Next Phase

Run a staging-only deploy and authenticated browser QA for this Phase 28.9 polish:

- verify `Select Asset A 2` and `Select Asset B 2` appear after the first side selection;
- create same-side mixed player/pick state;
- confirm the mixed-side warning appears;
- confirm player and pick score totals remain separate;
- confirm round-only pick detail displays `slot round-only`;
- confirm compact warning/component text appears outside the dataframes;
- keep production untouched and keep all production score flags false.
