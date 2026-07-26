# Phase 18.3 Staging UI Warning Fix Report

Date: 2026-06-16

Final decision: STAGING UI CLEAN WITH WARNINGS

## Scope

Fixed the four Phase 17 staging QA warnings in the legacy UI paths without widening the compatibility rollout.

No production flags were changed. No compatibility flag default was changed. No legacy fallback path was removed. No Firebase artifacts were created. No Pigskin arbitrary SQL was reintroduced. No LLM calls were made. No scraping occurred.

Staging deployment and browser QA were not run because this prompt did not explicitly authorize a staging deploy.

## Issue 1: Player Profiles Missing `pos_abb`

Status: fixed locally.

Root cause:

The legacy Player Profiles query referenced `depth_charts.pos_abb`, but the current production warehouse table does not expose that column. The query failed before the UI could render profile rows.

Fix:

- Removed the direct `pos_abb` reference from the legacy Player Profiles SQL.
- Set `latest_depth_charts.depth_position` to `NULL` in the depth CTE.
- Backfilled `depth_position` from the active roster `position` in the final select.
- Added `ensure_player_profile_display_columns()` to fill missing or blank `depth_position` from `position`.

Files changed:

- `app.py`
- `src/ui_data_guards.py`
- `tests/test_staging_ui_warning_fixes.py`

## Issue 2: Versus Finder Missing `pos_abb`

Status: fixed locally.

Root cause:

Versus Finder uses `fetch_player_profiles_data()`, so it inherited the same failing Player Profiles legacy query.

Fix:

The Player Profiles fix also repairs Versus Finder because both tabs share the same data function. Tests cover blank and missing depth-position behavior used by both profile surfaces.

## Issue 3: Show Prep Sleeper Watch Missing `rolling_3_week_ppr`

Status: fixed locally.

Root cause:

The legacy Show Prep Sleeper Watch path queries `compat_sleeper_watch_candidates`, but it selected `rolling_3_week_ppr`, which is not a compatibility-contract column. The contract exposes `fantasy_points_last_3`, so the UI query failed.

Fix:

- Changed the legacy Sleeper Watch query to compute:

```sql
COALESCE(fantasy_points_last_3, 0.0) / 3.0 AS rolling_3_week_ppr
```

- Added `ensure_sleeper_watch_display_columns()` to derive `rolling_3_week_ppr` from `fantasy_points_last_3`, preserve it when already present, and safely default display metrics.

## Issue 4: Trade Lab Side B Summary

Status: fixed locally.

Root cause:

Trade Lab immediately called `st.rerun()` after a side became fully selected. That could preempt the current render cycle before the comparison summary reflected the selected Side B asset.

Fix:

- Added `collect_selected_trade_assets()` to collect selected assets consistently from Side A and Side B labels.
- Removed the immediate `st.rerun()` from both side-selection blocks.
- Kept the existing auto-add blank-slot behavior by incrementing `num_a` and `num_b`; the next Streamlit interaction will render the new blank slot.
- Did not change market-value logic, projection logic, AI outlook logic, or the Trade History compatibility flag path.

## Tests Added

Added `tests/test_staging_ui_warning_fixes.py` covering:

- Player Profiles handles missing `depth_position` by using `position`.
- Versus Finder shared profile rows fill blank `depth_position`.
- Sleeper Watch derives missing `rolling_3_week_ppr` from `fantasy_points_last_3`.
- Sleeper Watch preserves an existing `rolling_3_week_ppr`.
- Trade Lab Side B selection collects Ja'Marr Chase and keeps expected metadata.
- Compatibility feature flags still default false.

## Validation

Commands run:

```text
.\venv\Scripts\python.exe -m unittest tests.test_staging_ui_warning_fixes
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:

```text
targeted tests: 6 passed
full test suite: 296 passed
app.py compile: pass
src and scripts compile: pass
deployment safety: pass
pending migrations: none
validation dry-run: pass
```

Safety checker confirmed:

- no Firebase artifacts
- no tracked secret files
- no secret content
- required files exist
- feature flags default off
- Pigskin arbitrary SQL remains absent
- app, src, and scripts compile

## Staging QA Result

Status: not run in this phase.

Reason:

The prompt allowed staging deploy only if authorized, but did not explicitly authorize deployment. No staging image was built, no staging service was updated, and no browser-click QA was repeated.

Required follow-up QA after staging deploy:

1. Player Profiles legacy path renders without the missing `pos_abb` BigQuery error.
2. Versus Finder renders without the missing `pos_abb` BigQuery error.
3. Show Prep Sleeper Watch renders without the missing `rolling_3_week_ppr` BigQuery error.
4. Trade Lab Side B summary updates after selecting Ja'Marr Chase or another Side B player.
5. `USE_COMPAT_TRADE_PLAYER_HISTORY=true` remains staging-only.
6. All other risk flags remain false.

## Remaining Warnings

1. Browser-level staging QA is still pending because staging deploy was not authorized.
2. `app.py` reports a Git line-ending warning in this Windows checkout: `LF will be replaced by CRLF the next time Git touches it`. The functional diff is narrow and tests pass.
3. Existing raw/source legacy paths remain in place by design. This phase fixed the broken legacy UI paths without migrating them to compatibility views.

## Final Decision

STAGING UI CLEAN WITH WARNINGS

The local code fixes and tests are clean. The prior staging QA warnings should be resolved by these changes, but authenticated staging browser QA must be repeated after an authorized staging deployment before production promotion.
