# Phase 22.9 Trade Score UI Staging Report

Date: 2026-06-17

## Scope

Wired deterministic Trade Analyzer score v0 into Trade Lab behind default-off flags.

No production deploy, staging deploy, migration application, BigQuery score materialization, feature flag enablement, Cloud Run Job trigger, LLM call, scrape, or Firebase artifact was performed.

## Code Changes

Updated `src/compat_flags.py`:

- added `USE_TRADE_ANALYZER_SCORE_V0`
- added `USE_COMPAT_TRADE_PLAYER_SCORE`
- both flags are included in the existing default-off flag registry

Updated `src/trade_player_scores.py`:

- added `get_current_trade_player_scores()`
- added `build_current_trade_player_scores_query()`
- query reads only `compat_trade_player_scores_current`
- query is bounded and parameterized

Updated `src/ui_data_guards.py`:

- added `attach_trade_scores_to_assets()`
- added `summarize_trade_score_side()`
- supports matching by player identity or normalized display name
- missing score rows are reported without breaking side summaries

Updated `app.py`:

- added score UI gate through `use_trade_score_ui()`
- score UI renders only when both new flags are true
- legacy Trade Lab remains available when flags are false
- existing current market value and projected value summaries remain visible
- when enabled, Trade Lab shows:
  - Pigskin Trade Score source marker
  - side score totals
  - score fairness delta
  - per-player score tier
  - confidence
  - risk and Fraud Watch signal
  - component breakdown
  - missing-data warnings
  - source freshness
- missing scores show `Pigskin Trade Score unavailable` warnings instead of breaking the page

Updated tests:

- `tests/test_streamlit_compat_rollout.py`
- `tests/test_staging_ui_warning_fixes.py`

## Flags

Required defaults remain false:

- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`

The UI score panel requires both flags to be true. Production flags were not changed.

## Local Tests

Passed:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_staging_ui_warning_fixes
.\venv\Scripts\python.exe -m unittest tests.test_streamlit_compat_rollout
.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py src\ui_data_guards.py src\compat_flags.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Full unit suite result:

```text
Ran 327 tests
OK
```

Safety checker result:

- no Firebase artifacts
- no tracked secret files
- no secret content
- feature flags default off
- Pigskin `execute_bigquery_sql` absent
- app and src/scripts compile

## Staging

No staging deployment was performed because this prompt did not provide explicit staging deploy authorization.

Staging QA was not run in this phase.

If staging deploy is later authorized, use only:

- `USE_COMPAT_TRADE_PLAYER_HISTORY=true`
- `USE_TRADE_ANALYZER_SCORE_V0=true`
- `USE_COMPAT_TRADE_PLAYER_SCORE=true`

Keep all other risk flags false.

## Rollback

Rollback was not run because no staging flags were changed.

Expected staging rollback if score flags are tested later:

- unset `USE_TRADE_ANALYZER_SCORE_V0`
- unset `USE_COMPAT_TRADE_PLAYER_SCORE`
- keep Trade History compatibility controlled only by `USE_COMPAT_TRADE_PLAYER_HISTORY`

Expected result:

- score UI disappears
- legacy Trade Lab still works
- current value and projected value summaries remain visible

## Production Status

Production was untouched.

Production must keep:

- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`

## Warnings

- Phase 22.8 left migration `0025` pending because migration apply and score materialization were not authorized.
- Until migration `0025` is applied and score rows are materialized, enabled score UI will show unavailable or empty score warnings.
- Browser-level staging QA remains pending.

## Final Decision

TRADE SCORE UI LOCAL ONLY
