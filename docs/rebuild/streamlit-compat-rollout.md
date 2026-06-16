# Streamlit Compatibility Rollout

This document covers the first Streamlit compatibility-read rollout. The goal is to move selected UI reads toward compatibility objects without changing default runtime behavior.

## Default-Off Feature Flags

All flags default to `false`.

| Flag | Streamlit area | Compat helper | Compatibility object |
| --- | --- | --- | --- |
| `USE_COMPAT_PLAYER_PROFILES` | Player Profiles and Versus Finder profile directory | `src/player_profiles.py` | `compat_player_profiles_current` |
| `USE_COMPAT_SLEEPER_WATCH` | Sleeper Watch segment | `src/sleeper_watch.py` | `compat_sleeper_watch_candidates` |
| `USE_COMPAT_TRADE_ASSETS` | Trade and Value Analyzer asset list | `src/trade_assets.py` | `compat_trade_assets_current` |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | Trade and Value Analyzer AI outlook history | `src/trade_history.py` | `compat_trade_player_history` |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | Sleeper Viewer Team Review console context | `src/viewer_team_context.py` | `compat_viewer_team_context` |
| `USE_BACKTEST_DASHBOARD` | Backtesting dashboard tab | `src/backtest_readers.py` | `backtest_runs`, `backtest_result_summary`, `backtest_result_player_week`, `backtest_calibration_bins` |
| `USE_CLAIM_LEDGER_UI` | Claim Ledger admin tab | `src/claim_import.py`, `src/claim_ledger.py` | `claim_sources`, `fantasy_claims`, `fantasy_claim_players`, `claim_evaluation_windows` |
| `USE_CONTENT_BRIEF_REVIEW_UI` | Content Brief Review admin tab | `src/content_brief_review.py` | `content_brief_runs`, `content_briefs`, `content_brief_items` |

Accepted enabled values are `1`, `true`, `yes`, `y`, and `on`.

## Phase 13.6 Rollout Status

Current selected flag for staging or local enablement:

- `USE_COMPAT_TRADE_PLAYER_HISTORY=true`

Production defaults remain unchanged. Enable the flag through environment only after reviewing [compat-rollout-status.md](compat-rollout-status.md).

Readiness checker:

```powershell
.\venv\Scripts\python.exe -m src.compat_rollout --check USE_COMPAT_TRADE_PLAYER_HISTORY
.\venv\Scripts\python.exe -m src.compat_rollout --recommend-next
```

Do not enable the other compatibility flags until Trade History manual QA is complete.

## Old Path Versus New Path

| Area | Default legacy path | Flagged compatibility path |
| --- | --- | --- |
| Player Profiles | Existing `fetch_player_profiles_data()` SQL in `app.py` joins roster, contract, depth, college, scouting, and analytics tables. | `fetch_compat_player_profiles_data()` calls `list_player_profiles()` and normalizes the compatibility rows into the current UI shape. |
| Sleeper Watch | Existing direct Streamlit query against the currently materialized Sleeper Watch compatibility view remains unchanged. | `fetch_compat_sleeper_watch_candidates_data()` calls `get_sleeper_watch_candidates()` so the UI goes through the helper layer. |
| Trade Assets | Existing `market_values` query remains unchanged. | `load_compat_trade_assets()` calls `get_trade_assets()` and maps compatibility columns to the current selector shape. |
| Trade Player History | Existing `weekly_metrics` history query remains unchanged. | `query_compat_trade_player_history()` calls `get_trade_player_history()` for capped recent history. |
| Viewer Team Context | Existing raw Sleeper snapshot joins remain unchanged. | `get_compat_sleeper_viewer_team_context()` calls `get_viewer_team_context()` and returns only the materialized packet text and metadata. |
| Backtesting | No dashboard tab is shown by default. | `render_backtest_dashboard()` calls `src.backtest_readers.py` and reads only backtest output tables. |
| Claim Ledger | No claim-admin tab is shown by default. | `render_claim_ledger_ui()` calls manual claim helpers and reads/writes only claim-ledger admin tables. |
| Content Brief Review | No content-brief admin tab is shown by default. | `render_content_brief_review_ui()` calls `src.content_brief_review.py` and reads only content brief output tables. |

## Rollback Process

Rollback is env-only.

1. Set the affected flag back to `false` or remove it from the Cloud Run service.
2. Redeploy or update the Cloud Run environment.
3. Restart the local Streamlit process or clear Streamlit cache after local flag changes.
4. Confirm the affected Streamlit view shows `legacy warehouse path` in the data-path caption.
5. Re-run the local tests:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_streamlit_compat_rollout
```

No migration rollback is required because this phase does not apply migrations or remove legacy code paths.

## Raw Source Tables Replaced By Flagged Paths

The compatibility paths avoid direct request-time reads of these raw/source tables:

- Player Profiles: `player_rosters`, `player_contracts`, `depth_charts`, `college_player_stats`, `rookie_scouting_metrics`.
- Sleeper Watch: `weekly_metrics` and raw Sleeper roster snapshots.
- Trade Assets: `market_values`.
- Trade Player History: `weekly_metrics`.
- Viewer Team Context: `sleeper_viewer_team_snapshots`, `sleeper_roster_players`, `sleeper_lineups`, `sleeper_available_players`.

The legacy paths still exist behind default-off flags for rollback and comparison.

## Known Limitations

- Player Profiles compatibility rows store some profile fields as JSON summaries, so the Streamlit branch normalizes those into the legacy UI shape. Some legacy-only display fields such as headshot, height, weight, jersey number, and draft details may be unavailable until the compat mart includes them explicitly.
- Trade Assets falls back to the legacy path with a visible warning if the flag is enabled but the compatibility object is empty or unavailable.
- Trade Player History falls back to the legacy path with a visible warning if the flagged helper fails during AI outlook generation.
- Viewer Team Context does not fall back when its flag is enabled. It returns a clear unavailable message instead of mixing raw Sleeper joins into the compatibility packet path. The current compat lookup requires `roster_id` or future `manager_id`; it will not guess from league-only, username, team name, or display name.
- Sleeper Watch already had a direct compatibility-view query before this rollout. The new flag moves it through the helper layer for safer gradual migration.
- Backtesting is read-only. It can preview a Cloud Run Job command when Cloud Run Jobs are enabled, but actual backtest execution remains gated by the Data Ops Cloud Run Jobs controls.
- Claim Ledger UI is manual-entry only. CSV import previews validation and player resolution before writing, does not fetch URLs, and does not call LLMs.
- Content Brief Review can update `review_status` explicitly and export Markdown. Reviewer notes are not persisted until the warehouse schema supports them.

## Manual QA Checklist

Run each item with all flags unset first, then enable one flag at a time.

1. Player Profiles
   - Confirm the tab loads with the default legacy path.
   - Enable `USE_COMPAT_PLAYER_PROFILES=true`.
   - Confirm the tab loads or shows a clear compatibility-data warning.
   - Open one player profile and confirm no traceback appears when optional profile fields are missing.

2. Sleeper Watch
   - Confirm the tab loads with the default path.
   - Enable `USE_COMPAT_SLEEPER_WATCH=true`.
   - Confirm candidates render from the helper path or a clear empty-data message appears.
   - Confirm source freshness or missing flags appear when present.

3. Trade and Value Analyzer
   - Confirm the asset selector loads with the default legacy path.
   - Enable `USE_COMPAT_TRADE_PLAYER_HISTORY=true` first.
   - Select two known players and confirm recent history loads through the helper path.
   - Confirm AI trade outlook still receives player history context.
   - Disable `USE_COMPAT_TRADE_PLAYER_HISTORY` and confirm the legacy `weekly_metrics` path still works.
   - Enable `USE_COMPAT_TRADE_ASSETS=true`.
   - Confirm assets render from the compatibility path or the view warns before documented fallback.
   - Run AI outlook for a selected trade and confirm the asset helper path either supplies context or warns before fallback.

4. Sleeper Viewer Team Context
   - Confirm the console works with the default legacy path.
   - Enable `USE_COMPAT_VIEWER_TEAM_CONTEXT=true`.
   - Confirm the console uses packet text when available.
   - Confirm missing packets return a clear unavailable message and do not invent roster context.

5. Safety checks
   - Confirm Pigskin chat still does not expose `execute_bigquery_sql`.
   - Confirm no Firebase artifacts were created.
   - Confirm no migrations were applied during this rollout.

6. Backtesting
   - Confirm the Backtesting tab is absent with `USE_BACKTEST_DASHBOARD` unset.
   - Enable `USE_BACKTEST_DASHBOARD=true`.
   - Confirm latest runs, summary rows, player errors, calibration bins, and markdown export load or show clean empty states.
   - Confirm no request-time Streamlit button runs a large backtest.

7. Claim Ledger
   - Confirm the Claim Ledger tab is absent with `USE_CLAIM_LEDGER_UI` unset.
   - Enable `USE_CLAIM_LEDGER_UI=true`.
   - Confirm source management, manual claim preview, CSV import preview, review board, and claim detail render cleanly.
   - Confirm CSV import writes only after explicit button click.
   - Confirm grading is command-preview only.

8. Content Brief Review
   - Confirm the Content Briefs tab is absent with `USE_CONTENT_BRIEF_REVIEW_UI` unset.
   - Enable `USE_CONTENT_BRIEF_REVIEW_UI=true`.
   - Confirm runs, brief list, detail, item table, Markdown export, and dry-run generation preview render cleanly.
   - Confirm review status changes happen only after explicit button clicks.
   - Confirm no LLM call or long generation job runs from the tab.
