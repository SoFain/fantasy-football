# Phase 29.6A: nflverse Optional Schema Mapping Report

Date: 2026-06-29

## Final Decision

**NFLVERSE OPTIONAL SOURCE MAPPINGS NEED REPAIR SMOKE**

The optional 2014 nflverse families are no longer blocked at the parser or mapper layer. No live BigQuery writes were run in this phase. The next step should be a separately authorized, narrow repair smoke for the optional raw tables only.

## Boundary Confirmation

No authorization gates were set:

| Gate | State |
| --- | --- |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset |
| `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY` | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

No deployment, ingestion write, materialization, Cloud Run Job trigger, Scheduler creation, LLM action, Pigskin prompt, external scrape, or Firebase artifact creation occurred.

## Files Changed

| File | Change |
| --- | --- |
| `src/nflverse_backfill.py` | Added no-write `--inspect-source-schema` and `--prepare-only` modes, optional-family alias coverage, ff player ID wide-to-long reshape, and clearer skipped-key diagnostics. |
| `tests/test_nflverse_backfill_executor.py` | Added tests for optional-family mapping, schema inspection no-write behavior, and weekly missing-player diagnostics. |
| `docs/rebuild/validation/phase-29-6a-nflverse-optional-schema-mapping-report.md` | This evidence report. |

Existing Phase 29 scaffold files remain untracked. No files were staged or committed.

## Schema Inspection Results

Command shape:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --inspect-source-schema --source-family <family> --season-start 2014 --season-end 2014
```

| Family | Fetched | Normalized | Key Finding |
| --- | ---: | ---: | --- |
| `ff_playerids` | 12,465 | 78,746 | nflverse source is wide by platform. It now reshapes into `platform` plus `platform_player_id` rows. |
| `rosters` | 2,153 | 2,153 | Source has `gsis_id`, `full_name`, `team`, `position`, `week`. `player_id` now maps from `gsis_id`. |
| `rosters_weekly` | 31,964 | 31,964 | Same alias shape as `rosters`. `player_id` now maps from `gsis_id`. |
| `snap_counts` | 23,864 | 23,864 | Source has `pfr_player_id`, not GSIS. `player_id` now maps from `pfr_player_id` for raw capture. |
| `weekly` | 17,622 | 17,622 | 17,601 rows have `player_id`; 21 rows are missing `player_id` and are treated as aggregate or non-player rows. |

Non-null key counts:

| Family | Key Counts |
| --- | --- |
| `ff_playerids` | `gsis_id=69105`, `pfr_id=71649`, `platform=78746`, `platform_player_id=78746`, `position=78746`, `team=78746` |
| `rosters` | `gsis_id=2152`, `full_name=2153`, `position=2153`, `season=2153`, `team=2153`, `week=2153` |
| `rosters_weekly` | `gsis_id=31963`, `full_name=31964`, `position=31964`, `season=31964`, `team=31964`, `week=31964` |
| `snap_counts` | `game_id=23864`, `pfr_player_id=23864`, `position=23864`, `season=23864`, `team=23864`, `week=23864` |
| `weekly` | `player_id=17601`, `player_name=17605`, `player_display_name=17601`, `position=17601`, `season=17622`, `team=17622`, `week=17622` |

## Mapping Fixes

Added aliases:

| Target Field | New or Confirmed Source Aliases |
| --- | --- |
| `player_id` | `player_id`, `gsis_id`, `nflverse_player_id`, `gsis_it_id`, `pfr_player_id`, `pfr_id` |
| `gsis_id` | `gsis_id`, `player_id`, `nflverse_player_id` |
| `nflverse_player_id` | `nflverse_player_id`, `player_id`, `gsis_id`, `nfl_id` |
| `player_name` | `player_name`, `display_name`, `full_name`, `player_display_name`, `player`, `name` |
| `normalized_player_name` | `normalized_player_name`, `merge_name`, `display_name`, `full_name`, `player_name`, `name` |
| `status` | `status`, `status_description`, `status_description_abbr` |
| `game_id` | `game_id`, `old_game_id` |
| snap fields | `offense_snaps`, `offense_pct`, `defense_snaps`, `st_snaps` aliases for nflverse snap-count variants |

Added `ff_playerids` wide-to-long handling for platform columns such as `sleeper_id`, `mfl_id`, `espn_id`, `yahoo_id`, `cbs_id`, `fantasy_data_id`, `rotowire_id`, `pff_id`, and `sportradar_id`.

## No-Write Plan and Prepare Results

Dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2014 --season-end 2014 --dry-run
```

Result:

- `dry_run=True`
- `wrote=False`
- selected families: `schedules`, `teams`, `players`, `ff_playerids`, `rosters`, `rosters_weekly`, `weekly`, `pbp`, `snap_counts`

Prepare-only command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2014 --season-end 2014 --prepare-only
```

Result:

| Family | Fetched | Prepared | Skipped | Notes |
| --- | ---: | ---: | ---: | --- |
| `schedules` | 267 | 267 | 0 | Existing core source shape remains valid. |
| `teams` | 36 | 36 | 0 | Existing static source shape remains valid. |
| `players` | 25,033 | 25,033 | 0 | Existing static source shape remains valid. |
| `ff_playerids` | 12,465 | 69,060 | 9,686 | Wide source reshaped. 9,641 rows skipped for missing `nflverse_player_id`; 45 duplicate natural-key rows deduped. |
| `rosters` | 2,153 | 2,152 | 1 | One row skipped for missing `player_id`. |
| `rosters_weekly` | 31,964 | 30,195 | 1,769 | One row skipped for missing `player_id`; 1,768 duplicate natural-key rows deduped. |
| `weekly` | 17,622 | 17,601 | 21 | 21 rows skipped for missing `player_id`; diagnosed as non-player or aggregate rows unless a safe source key is proven. |
| `pbp` | 47,629 | 47,629 | 0 | Existing core source shape remains valid. |
| `snap_counts` | 23,864 | 23,864 | 0 | Raw capture can proceed using `pfr_player_id` as the raw player key. |

## Warehouse State After Phase

Read-only row-count checks after the no-write phase:

| Table | Total Rows | 2014 Rows |
| --- | ---: | ---: |
| `raw_nflverse_schedules` | 267 | 267 |
| `raw_nflverse_teams` | 36 | 0, static table |
| `raw_nflverse_players` | 25,033 | 0, static table |
| `raw_nflverse_ff_playerids` | 0 | 0 |
| `raw_nflverse_rosters` | 0 | 0 |
| `raw_nflverse_rosters_weekly` | 0 | 0 |
| `raw_nflverse_weekly` | 17,601 | 17,601 |
| `raw_nflverse_pbp` | 47,629 | 47,629 |
| `raw_nflverse_snap_counts` | 0 | 0 |

Staging and feature marts stayed empty for 2014:

- `stg_player_identity`: 0
- `stg_game_context`: 0
- `stg_player_week_stats`: 0
- `stg_team_week_stats`: 0
- `stg_play_player_events`: 0
- `stg_participation_context`: 0
- `player_week_advanced_metrics`: 0
- `team_week_context_metrics`: 0
- `qb_week_environment_metrics`: 0
- `pigskin_player_context_packet_current`: 0
- `compat_pigskin_player_context_current`: 0

Non-target score lanes were not changed by this phase:

- `trade_player_scores`: 154 total rows, 0 rows for 2014.
- `trade_pick_scores`: 64 total rows from prior authorized work.

## Validation Results

Targeted validation patterns:

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | 3 passed, 0 failed. Coverage warning is expected because only the 2014 core smoke rows exist. |
| `stg_` | 7 passed, 0 failed. |
| `advanced_metrics` | 4 passed, 0 failed. |
| `compat_pigskin` | 2 passed, 0 failed. |
| `trade_player_scores` | 12 passed, 0 failed. |
| `trade_pick_scores` | 17 passed, 0 failed. Informational model-version coverage warning remains expected. |

Final local checks:

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile src\nflverse_backfill.py` | PASS |
| `py_compile src\nflverse_backfill_plan.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_backfill_executor` | PASS, 18 tests |
| `unittest tests.test_nflverse_backfill_plan` | PASS, 15 tests |
| `unittest tests.test_nflverse_historical_contracts` | PASS, 5 tests |
| `unittest tests.test_pigskin_advanced_metrics_contracts` | PASS, 4 tests |
| `unittest discover tests` | PASS, 449 tests |
| `scripts/run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | PASS, 200 validations discovered |

## Production and Staging State

Read-only Cloud Run checks:

| Service | Revision | Traffic | Risk Flag State |
| --- | --- | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100 percent to `00077-2jp` | Trade score false, trade history compat false, Cloud Run Job flags false, local subprocess flags false. |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100 percent to `00029-jtb` | Staging remains on the prior QA state with Trade Score and Trade History flags true; Cloud Run Job and local subprocess trigger flags false. |

No production or staging service was deployed or modified.

## Remaining Warnings

- Optional raw tables remain empty until an explicitly authorized repair smoke is run.
- `snap_counts` raw capture uses `pfr_player_id` because the nflverse snap-count loader does not provide GSIS IDs for this slice. Identity resolution should happen downstream in staging or feature marts.
- `ff_playerids` drops rows that lack a usable `nflverse_player_id`. The prepare-only result makes this visible instead of silently producing zero rows.
- `weekly` has 21 skipped rows with missing `player_id`. These are not safe to force into player-grain raw rows without a proven source key.

## Recommended Next Phase

Run a gated Phase 29.6B repair smoke only if the operator explicitly authorizes live raw writes.

Recommended target:

- `season-start=2014`
- `season-end=2014`
- source families: `ff_playerids`, `rosters`, `rosters_weekly`, `snap_counts`
- no staging or feature mart materialization
- no Pigskin packet refresh
- no broad historical backfill

