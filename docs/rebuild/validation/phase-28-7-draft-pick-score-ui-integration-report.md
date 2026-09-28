# Phase 28.7 Draft-Pick Score UI Integration Report

Final decision: **DRAFT PICK SCORE UI INTEGRATION READY WITH WARNINGS**

## Scope

Phase 28.7 added code and tests for default-off Trade Lab UI support for draft-pick scores. No deployment, score materialization, ingestion, Cloud Run Job trigger, Scheduler job, LLM action, Pigskin prompt, or Firebase artifact was created.

## Authorization State

Confirmed unset:

- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`
- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `ALLOW_PROJECTION_CONTEXT_REFRESH`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

## Files Changed

Phase 28.7 code/test files:

- `app.py`
- `src/compat_flags.py`
- `src/ui_data_guards.py`
- `src/trade_pick_scores.py` remains untracked from the Phase 28 pick-score lane and now includes the UI read helper.
- `tests/test_trade_pick_scores.py`
- `tests/test_streamlit_compat_rollout.py`
- `tests/test_staging_ui_warning_fixes.py`
- `tests/test_data_ops_local_controls.py`

Pre-existing Phase 28 worktree changes are still present for owner review, including draft-pick score contracts, migration 0026, validation SQL, and rollout docs.

## New Flags

Added default-off flags:

- `USE_TRADE_PICK_SCORE_V0`
- `USE_COMPAT_TRADE_PICK_SCORE`

Pick-score UI requires both flags true. The player-score flags remain separate:

- `USE_TRADE_ANALYZER_SCORE_V0`
- `USE_COMPAT_TRADE_PLAYER_SCORE`

Production remains disabled by default because unset flags evaluate false.

## Pick-Score Read Helper

Added `get_current_trade_pick_scores` and `build_current_trade_pick_scores_query` in `src.trade_pick_scores`.

Behavior:

- reads only `compat_trade_pick_scores_current`;
- filters by `scoring_profile_id`, `league_type_id`, `roster_format_id`, and optional `source_pick_key`;
- uses bounded `LIMIT`;
- returns UI-safe score fields, JSON payloads, model version, score run ID, and created timestamp;
- does not read `draft_picks`, `college_player_stats`, `rookie_scouting_metrics`, raw tables, or source tables.

`app.py` adds cached `load_trade_pick_scores_current()` for Streamlit.

## Trade Lab UI Behavior

Trade Lab now has separate score lanes:

- player assets use `compat_trade_player_scores_current`;
- pick assets use `compat_trade_pick_scores_current` only when both pick-score flags are true;
- selected pick assets are identified by `position == "PICK"` or `:PICK:` source keys;
- compat trade assets now preserve `source_pick_key` and `source_player_key` for stable pick matching.

Pick-score display includes:

- `Pick Score` label;
- source marker `compat_trade_pick_scores_current`;
- model version;
- pick score, confidence, score tier;
- pick year, round, slot, class, bucket;
- market value and risk-adjusted trade value;
- component rows for market, slot capital, time discount, liquidity certainty, college context, and uncertainty risk;
- warning details and source freshness.

## Unavailable-Score Behavior

If pick flags are false, draft picks stay out of the player score lane and retain the existing unavailable reason: `draft pick score lane pending`.

If pick flags are true but no compatible row exists, Trade Lab shows:

- market value and projected value from the existing summary cards;
- `Pick Score: N/A`;
- reason: `No compatible pick score row for this scoring context`.

No player score component breakdown is shown for picks.

## Side Total Behavior

Market totals remain unchanged and combined by side.

Score totals are separate:

- `Player Trade Score` totals are calculated from player score rows only.
- `Pick Score` totals are calculated from pick score rows only.
- mixed sides show a warning that market totals stay combined while score totals stay separate.

The UI does not add `pick_score` and player `trade_score` together.

## Tests Added

Added or updated tests for:

- new pick-score flags default false and env-enabled;
- pick-score UI source marker and flag gate;
- pick-score query reads only `compat_trade_pick_scores_current`;
- source-pick-key filtering;
- pick assets never receiving player score rows;
- pick score attachment by `source_pick_key` or pick label;
- missing pick score row safe handling;
- mixed player/pick side detection;
- Data Ops local controls remain default off.

## Checks Run

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile app.py`
- `.\venv\Scripts\python.exe -m py_compile src\trade_pick_scores.py`
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

Validation notes:

- `trade_pick_scores`: 17 passed, 0 failed.
- `compat_trade_pick_scores`: 2 passed, 0 failed.
- `trade_player_scores`: 12 passed, 0 failed.
- `compat_trade_player_scores`: 2 passed, 0 failed.
- `178_trade_pick_scores_model_version_coverage.sql` returned the expected informational warning for `trade_pick_score_v0_2026_001` with 64 score rows.

## Read-Only Pick Score Data Verification

Verified:

- `trade_pick_scores` rows: 64.
- `trade_pick_scores_current` rows: 64.
- `compat_trade_pick_scores_current` rows: 64.
- PPR rows: 64.
- Exact-slot rows: 48.
- Round-only rows: 16.
- Top pick: `2026 Pick 1.01`.
- Top pick score: `96.7`.
- Top pick model version: `trade_pick_score_v0_2026_001`.
- Duplicate current rows: 0.
- Raw/source dependency check: 0 dependencies using FROM/JOIN-aware view-definition inspection.

## Production Untouched

Read-only production describe confirmed:

- service: `nfl-studio-dashboard`
- revision: `nfl-studio-dashboard-00077-2jp`
- traffic: `nfl-studio-dashboard-00077-2jp=100`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_TRADE_PICK_SCORE_V0` unset
- `USE_COMPAT_TRADE_PICK_SCORE` unset
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

No deployment occurred.

## Remaining Warnings

- This was code/test only. No staging deploy or browser QA was run in this phase.
- `src/trade_pick_scores.py` and Phase 28 warehouse artifacts remain untracked as part of the broader Phase 28 owner-review package.
- The pick-score UI currently loads PPR/redraft/one-QB rows, matching Phase 28.6 materialization. Other scoring contexts should show unavailable until rows exist or the UI context selector is extended.

## Recommended Next Phase

Run a staging-only deploy with:

- `USE_TRADE_ANALYZER_SCORE_V0=true`
- `USE_COMPAT_TRADE_PLAYER_SCORE=true`
- `USE_TRADE_PICK_SCORE_V0=true`
- `USE_COMPAT_TRADE_PICK_SCORE=true`

Then perform authenticated Trade Lab QA with a player and `2026 Pick 1.01`, plus rollback flag testing.
