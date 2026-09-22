# nflverse Backfill Planner

Phase 29.5 adds a dry-run-only planner for the Phase 29 nflverse historical warehouse. It does not fetch nflverse data, call nflreadpy loaders, write local data files by default, write BigQuery rows, run materialization, refresh Pigskin packets, deploy, trigger jobs, or change feature flags.

The planner exists to make a future authorized backfill explicit before any live write happens.

## CLI

Run with:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2014 --season-end 2025
```

`--plan-only` is required in Phase 29.5. A command without it fails closed with a message that live execution is not implemented.

Supported options:

- `--plan-only`
- `--source-family <name>`, repeatable or comma-separated
- `--all-source-families`
- `--preset core_historical|role_context|tier2_enrichment|all`
- `--season-start YYYY`
- `--season-end YYYY`
- `--week-start N`
- `--week-end N`
- `--mode historical_backfill|weekly_refresh`
- `--project fantasy-football-498121`
- `--dataset fantasy_football_brain`
- `--output-json <path>`, optional explicit plan artifact
- `--strict`
- `--skip-bigquery-inspection`

The default selected source families, when no source family or preset is supplied, are the Tier 1 historical set:

- `schedules`
- `teams`
- `players`
- `ff_playerids`
- `rosters`
- `rosters_weekly`
- `weekly`
- `pbp`
- `snap_counts`

## Source-Family Registry

The registry lives in `src/nflverse_backfill_plan.py`. Each family records:

- source family name
- nflreadpy loader name as metadata only
- target `raw_nflverse_*` table
- source type: `season_range`, `static_snapshot`, or `season_limited`
- default and recommended historical season policy
- limited-range notes for NGS and FTN
- week-filter behavior
- natural keys
- partitioning and clustering expectations
- required load metadata
- downstream staging and feature dependencies
- validation patterns
- future live-write authorization gate
- warnings

Required source families:

| Source family | Target table | Loader metadata |
| --- | --- | --- |
| `pbp` | `raw_nflverse_pbp` | `nflreadpy.load_pbp` |
| `weekly` | `raw_nflverse_weekly` | `nflreadpy.load_player_stats` |
| `rosters` | `raw_nflverse_rosters` | `nflreadpy.load_rosters` |
| `rosters_weekly` | `raw_nflverse_rosters_weekly` | `nflreadpy.load_rosters_weekly` |
| `players` | `raw_nflverse_players` | `nflreadpy.load_players` |
| `ff_playerids` | `raw_nflverse_ff_playerids` | `nflreadpy.load_ff_playerids` |
| `schedules` | `raw_nflverse_schedules` | `nflreadpy.load_schedules` |
| `teams` | `raw_nflverse_teams` | `nflreadpy.load_teams` |
| `team_stats` | `raw_nflverse_team_stats` | `nflreadpy.load_team_stats` |
| `injuries` | `raw_nflverse_injuries` | `nflreadpy.load_injuries` |
| `depth_charts` | `raw_nflverse_depth_charts` | `nflreadpy.load_depth_charts` |
| `snap_counts` | `raw_nflverse_snap_counts` | `nflreadpy.load_snap_counts` |
| `participation` | `raw_nflverse_participation` | `nflreadpy.load_participation` |
| `ngs_passing` | `raw_nflverse_ngs_passing` | `nflreadpy.load_nextgen_stats:passing` |
| `ngs_rushing` | `raw_nflverse_ngs_rushing` | `nflreadpy.load_nextgen_stats:rushing` |
| `ngs_receiving` | `raw_nflverse_ngs_receiving` | `nflreadpy.load_nextgen_stats:receiving` |
| `ftn_charting` | `raw_nflverse_ftn_charting` | `nflreadpy.load_ftn_charting` |
| `draft_picks` | `raw_nflverse_draft_picks` | `nflreadpy.load_draft_picks` |

The loader names are strings. The planner does not import `nflreadpy`.

## Presets

`core_historical`:

- `schedules`
- `teams`
- `players`
- `ff_playerids`
- `rosters`
- `rosters_weekly`
- `weekly`
- `pbp`
- `snap_counts`

`role_context`:

- `injuries`
- `depth_charts`
- `participation`
- `snap_counts`

`tier2_enrichment`:

- `ngs_passing`
- `ngs_rushing`
- `ngs_receiving`
- `ftn_charting`
- `team_stats`
- `draft_picks`

`all` includes every registered source family.

## Week Behavior

Most nflreadpy loaders are season-level. The planner does not pretend true week-bounded extraction exists unless the registry says it is supported.

In `historical_backfill` mode, week bounds are treated as planning notes for season-level loaders. No live write happens.

In `weekly_refresh` mode, explicit `--season-start`, `--season-end`, `--week-start`, and `--week-end` are required. The season start and end must be the same season. Season-level loaders report that a future implementation must pull the season and merge only impacted weeks.

## Read-Only BigQuery Inspection

By default the CLI attempts cheap read-only inspection:

- table existence through BigQuery metadata;
- `num_rows` from table metadata;
- bounded season coverage query, capped to 25 season rows;
- min/max/distinct week coverage when a `week` column exists.

If inspection fails, planning continues with a warning. Use `--skip-bigquery-inspection` for offline tests or local planning.

The planner never previews raw data rows.

## Dry-Run Examples

Historical Tier 1 plan:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2014 --season-end 2025
```

Role-context plan:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset role_context --season-start 2014 --season-end 2025
```

Tier 2 enrichment plan:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset tier2_enrichment --season-start 2014 --season-end 2025
```

Weekly refresh planning:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --mode weekly_refresh --season-start 2026 --season-end 2026 --week-start 1 --week-end 1
```

Fail-closed smoke:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --preset core_historical --season-start 2014 --season-end 2025 --mode historical_backfill
```

Expected result: non-zero exit, no writes, and a message that live execution is not implemented in Phase 29.5.

## Future Authorization Gates

The planner documents future gates only. It does not set them.

Future live historical backfill would require:

```text
ALLOW_NFLVERSE_HISTORICAL_BACKFILL=true
```

Future live weekly refresh would require:

```text
ALLOW_NFLVERSE_WEEKLY_REFRESH=true
```

Future advanced-metric materialization and Pigskin packet refresh remain separate phases with separate gates:

```text
ALLOW_ADVANCED_METRICS_MATERIALIZATION=true
ALLOW_PIGSKIN_PACKET_REFRESH=true
```

## Future Phase Handoff

Planner output should be reviewed before any live backfill phase. A future authorized phase should use the plan to choose:

- source families;
- source season bounds;
- impacted weeks if planning a weekly refresh;
- raw target tables;
- idempotency keys;
- required metadata fields;
- downstream staging and feature build order;
- post-load validation patterns.

The future implementation must use idempotent writes and must keep raw/source tables out of Pigskin and UI read paths.

## Pigskin and UI Boundary

`raw_nflverse_*` tables are source tables. Pigskin and Streamlit must not read them directly.

Safe future read surfaces are derived feature tables, packet tables, and compatibility views after validation:

- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`
- `pigskin_player_context_packet_current`
- `compat_pigskin_player_context_current`

