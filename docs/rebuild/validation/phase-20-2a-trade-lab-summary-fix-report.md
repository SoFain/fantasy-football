# Phase 20.2A Trade Lab Summary Fix Report

Date: 2026-06-16

## Decision

TRADE LAB SUMMARY FIX PASS WITH WARNINGS

The Trade Lab summary rendering path was fixed and locally validated. Staging deployment and browser re-QA were not run because this prompt allows staging deploy only if authorized, and no explicit staging-deploy authorization was provided.

## Root Cause

Phase 20.2 browser QA showed that Trade Lab selectboxes displayed A.J. Brown and Ja'Marr Chase, but the side-summary cards still rendered `No assets selected`.

The narrow root cause was in the selected-asset collection path:

- The summary cards depended entirely on exact display-label lookup in `player_map`.
- If Streamlit returned a display-label variant, such as a missing leading icon or normalized apostrophe, the selected label did not resolve.
- Unresolved selected labels were silently dropped, which made the summary cards look empty.
- The Trade History compatibility flag was not the source of the value lookup. Trade assets still use the legacy Trade Assets path unless `USE_COMPAT_TRADE_ASSETS=true`.

## Code Changes

Files changed:

- `src/ui_data_guards.py`
- `app.py`
- `tests/test_staging_ui_warning_fixes.py`

Changes:

- Added tolerant Trade Lab asset resolution in `collect_selected_trade_assets`.
- Added label normalization for:
  - leading icon differences
  - straight and curly apostrophes
  - punctuation and whitespace differences
  - exact normalized player name plus position/team matching
- Added `unresolved_trade_asset_labels`.
- Updated Trade Lab summary cards to show a clear unresolved-selection warning instead of silently falling back to `No assets selected`.
- Updated Side A and Side B summary rows to render player name, position, team, age, current value, and projected value.
- Kept `USE_COMPAT_TRADE_PLAYER_HISTORY` scoped only to recent player-history context.
- Did not enable `USE_COMPAT_TRADE_ASSETS`.
- Did not remove legacy fallback.

## Tests Added Or Updated

Updated `tests/test_staging_ui_warning_fixes.py` with coverage for:

- Side A summary asset collection.
- Side B summary asset collection.
- A.J. Brown-style label resolution.
- Ja'Marr Chase-style label resolution.
- Curly apostrophe normalization.
- Unresolved selection reporting.
- Distinct `sel_a_*` and `sel_b_*` Streamlit state keys.
- Default-off compatibility flags.

Existing `tests/test_streamlit_compat_rollout.py` still verifies:

- Feature flags default false.
- Trade History staging marker exists.
- Compatibility helper paths do not reference raw source tables.
- Legacy paths remain available.

## Local Test Results

Commands run:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_staging_ui_warning_fixes
.\venv\Scripts\python.exe -m unittest tests.test_streamlit_compat_rollout
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m py_compile src\ui_data_guards.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_history
```

Results:

| Check | Result |
| --- | --- |
| `tests.test_staging_ui_warning_fixes` | PASS, 11 tests |
| `tests.test_streamlit_compat_rollout` | PASS, 8 tests |
| Full unittest discovery | PASS, 309 tests |
| `app.py` compile | PASS |
| `src/ui_data_guards.py` compile | PASS |
| `src` and `scripts` compile | PASS |
| Deployment safety | PASS |
| BigQuery pending migrations | PASS, no pending migrations |
| `compat_trade_player_history` validations | PASS, 6 passed, 0 failed |

Validation warning retained:

- `026_compat_trade_player_history_identity_coverage.sql` returned an informational warning with `missing_identity_rate = 0.0`. This is review-only and not a blocker.

## Staging Deployment

Not run.

Reason:

- The prompt allows staging deployment only if authorized.
- No explicit staging-deploy authorization was provided in this turn.

Required staging flag state remains:

| Flag | Required state |
| --- | --- |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `true` |
| `USE_COMPAT_PLAYER_PROFILES` | `false` or unset |
| `USE_COMPAT_SLEEPER_WATCH` | `false` or unset |
| `USE_COMPAT_TRADE_ASSETS` | `false` or unset |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | `false` or unset |
| `USE_BACKTEST_DASHBOARD` | `false` or unset |
| `USE_CLAIM_LEDGER_UI` | `false` or unset |
| `USE_CONTENT_BRIEF_REVIEW_UI` | `false` or unset |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` or unset |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` or unset |

## Browser QA

Not rerun against staging because no staging deployment was performed.

Required browser QA after staging deploy:

- Trade Lab loads.
- Compat marker appears:
  - `Trade player history source: compat_trade_player_history`
- A.J. Brown selection renders in Side A Summary.
- Ja'Marr Chase selection renders in Side B Summary.
- Valid selections no longer show `No assets selected`.
- No `Traceback`, `KeyError`, `NameError`, `pos_abb`, or `rolling_3_week_ppr`.
- Removing `USE_COMPAT_TRADE_PLAYER_HISTORY` still restores the legacy history path.

## Safety Status

| Safety check | Status |
| --- | --- |
| Production touched | No |
| Cloud Run Jobs triggered | No |
| Scheduler jobs created | No |
| LLM calls made | No |
| Scraping introduced | No |
| Firebase artifacts created | No |
| Pigskin arbitrary SQL reintroduced | No |
| Raw/source tables exposed to Pigskin | No |
| Legacy fallback removed | No |
| New compatibility flags enabled | No |

## Remaining Warnings

1. Staging image has not been rebuilt or redeployed with this fix.
2. Authenticated staging browser QA for the fixed side summaries is still required after staging deployment.

## Next Step

With staging deploy authorization, build a new immutable staging image, deploy only to `nfl-studio-dashboard-staging`, keep only `USE_COMPAT_TRADE_PLAYER_HISTORY=true`, and rerun the Trade Lab browser QA from Phase 20.2A.
