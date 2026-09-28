# Phase 27.7 Trade Score v1 UI Explainability Polish Report

Generated: 2026-06-27 15:59:33 -04:00

## Final Decision

TRADE SCORE V1 UI POLISH READY WITH WARNINGS

## Scope

Phase 27.7 was code and tests only. No deployment, ingestion, materialization, Cloud Run Job trigger, Scheduler change, LLM action, Pigskin prompt, Firebase artifact, commit, or production flag change was performed.

## Authorization Gates

All checked gates were unset:

- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `ALLOW_PROJECTION_CONTEXT_REFRESH`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

## Files Changed

- `app.py`
- `src/trade_player_scores.py`
- `tests/test_trade_player_scores.py`

The worktree already had uncommitted Phase 27 score-builder changes in `src/trade_player_scores.py` and `tests/test_trade_player_scores.py` before this phase. This phase added explainability helpers and focused tests on top of that state.

## UI Changes

- Trade Lab now shows the active Pigskin Trade Score model context when score rows are available:
  - `model_version`
  - `model_run_id`
  - season/week
  - scoring profile, league type, and roster format
- Long missing-data warning lists now render as grouped warning categories:
  - Source freshness
  - Team context
  - Role/source coverage
  - Risk/Fraud context
  - Identity/context
  - Scoring data
  - Draft pick/unavailable score
  - Other warnings
- Each scored player now has a source freshness expander with structured rows for:
  - score model context
  - projection model run and created timestamp
  - target season/week
  - raw and effective projection as-of fields
  - market, history, fantasy, and fraud source freshness
- Draft picks remain score-unavailable and now state the reason as `draft pick score lane pending`.
- Missing non-pick scores state `no compatible player score row`.
- Raw warning details remain available as grouped rows in player-specific warning details expanders.
- Market-value totals remain separate from Pigskin Trade Score totals.

## Performance Review

No new BigQuery reads were added. The UI still uses the existing cached `load_trade_player_scores_current()` result and formats the rows already loaded for the Trade Lab score section. The polish adds local JSON parsing and small in-memory row formatting only.

## Data Ops Review

No Data Ops code change was made in this phase. Existing Data Ops Cloud Run and local subprocess controls already show disabled/gated state through explicit feature flags and disabled buttons. No Data Ops control was clicked.

## Tests Added

Added unit coverage for:

- active score model context label includes `trade_score_v1_2025_001`
- v1 warning flags group into readable categories
- projection/source freshness rows expose model run, target context, and missing raw projection metadata warning
- draft picks remain in the unavailable score lane

## Checks Run

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
  - PASS
- `.\venv\Scripts\python.exe -m py_compile app.py`
  - PASS
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
  - PASS
- `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores`
  - PASS, 40 tests
- `.\venv\Scripts\python.exe -m unittest tests.test_streamlit_compat_rollout`
  - PASS, 10 tests
- `.\venv\Scripts\python.exe -m unittest tests.test_staging_ui_warning_fixes tests.test_trade_player_scores`
  - PASS, 53 tests
- `.\venv\Scripts\python.exe -m unittest tests.test_data_ops_local_controls`
  - PASS, 6 tests
- `.\venv\Scripts\python.exe -m unittest discover tests`
  - PASS, 367 tests
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
  - PASS, no pending migrations
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`
  - PASS, 160 validation files discovered
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_score`
  - PASS, 1 passed, 0 failed
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores`
  - PASS, 11 passed, 0 failed
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores`
  - PASS, 2 passed, 0 failed

## Production Exposure Verification

No production flags were changed. This phase did not enable:

- `USE_TRADE_ANALYZER_SCORE_V0`
- `USE_COMPAT_TRADE_PLAYER_SCORE`
- `USE_COMPAT_TRADE_PLAYER_HISTORY`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS`
- `DATA_OPS_ALLOW_JOB_TRIGGER`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

## Remaining Warnings

- This was not a browser QA phase. The next staging QA pass should confirm the model context line, warning expanders, source freshness expander, and draft-pick unavailable reason render correctly in the live Trade Lab.
- No Data Ops disabled-control UI code was changed because the existing gated panels already show explicit disabled status and the requested safety tests pass. If browser QA still finds those controls visually confusing, handle it in a separate low-risk copy-only phase.
- Existing untracked historical validation reports remain outside this phase.

## Recommended Next Step

Build a staging-only image and run authenticated Trade Lab QA for the v1 score UI polish. Keep production score flags false.
