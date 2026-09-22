# Phase 29.14 - Historical Expansion Planner for 2015-2025 nflverse Pigskin Pipeline

Date: 2026-06-29

Final decision: HISTORICAL EXPANSION PLAN READY WITH WARNINGS

## Scope

Planner and dry-run only for expanding the 2014 nflverse Pigskin canary pipeline across 2015-2025.

No BigQuery rows were written. No materialization commands were run with write gates. No deployment, Cloud Run Job trigger, Scheduler job, ingestion write, LLM-backed action, Pigskin prompt, scrape, Firebase artifact, or commit occurred.

## Authorization Gate State

All write and deploy gates were unset before and after the planner work:

| Gate | State |
| --- | --- |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset |
| `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY` | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

## Repo State

Latest commit:

`4805610 Build nflverse Pigskin canary pipeline`

Worktree status:

- 92 untracked files, consistent with the existing historical validation backlog and owner-review artifacts.
- 0 staged files.
- No generated artifacts were staged or committed.

## 2014 Canary Baseline

The 2014 canary remains the only populated nflverse historical slice.

| Object | Row Count |
| --- | ---: |
| `pigskin_player_context_packet_current` | 482 |
| `compat_pigskin_player_context_current` | 482 |
| `player_week_advanced_metrics` | 17,601 |
| `team_week_context_metrics` | 534 |
| `qb_week_environment_metrics` | 643 |
| `player_recent_advanced_metrics_current` | 1,854 |
| `player_role_usage_metrics_current` | 1,854 |
| `stg_game_context` | 267 |
| `stg_participation_context` | 23,864 |
| `stg_play_player_events` | 116,400 |
| `stg_player_identity` | 30,195 |
| `stg_player_week_stats` | 17,601 |
| `stg_team_week_stats` | 534 |
| `raw_nflverse_pbp` | 47,629 |
| `raw_nflverse_weekly` | 17,601 |
| `raw_nflverse_rosters` | 2,152 |
| `raw_nflverse_rosters_weekly` | 30,195 |
| `raw_nflverse_players` | 25,033 |
| `raw_nflverse_ff_playerids` | 69,060 |
| `raw_nflverse_schedules` | 267 |
| `raw_nflverse_teams` | 36 |
| `raw_nflverse_snap_counts` | 23,864 |

Optional raw families remain empty for 2014:

`raw_nflverse_depth_charts`, `raw_nflverse_draft_picks`, `raw_nflverse_ftn_charting`, `raw_nflverse_injuries`, `raw_nflverse_ngs_passing`, `raw_nflverse_ngs_receiving`, `raw_nflverse_ngs_rushing`, `raw_nflverse_participation`, `raw_nflverse_team_stats`.

## CLI Capability Review

`src.nflverse_backfill` supports:

- `--plan-only`
- `--dry-run`
- `--prepare-only`
- `--inspect-source-schema`
- `--write`

`src.nflverse_backfill_plan` supports `--plan-only` and does not import or call `nflreadpy`.

`src.nflverse_backfill` imports `nflreadpy` inside the loader path, which means `--prepare-only` fetches and prepares source rows but remains non-writing when write gates are unset.

## Proposed Batch Plan

| Batch | Seasons | Recommended Role |
| --- | --- | --- |
| A1 | 2015 only | First authorized raw write candidate because 2015 has the highest skipped-row warning in prepare-only output. |
| A2 | 2016-2017 | Proceed after 2015 raw/staging/metrics validations pass. |
| B | 2018-2020 | Second expansion window after A is clean. |
| C | 2021-2023 | Third window. Watch 17-game schedule transition. |
| D | 2024-2025 | Last historical/current bridge window. Keep current-content labeling strict. |

The original 2015-2017 Batch A is technically planned, but the safer next write phase is a 2015-only raw backfill gate.

## Raw Backfill Plan-Only Results

Commands run:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2015 --season-end 2017
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2018 --season-end 2020
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2021 --season-end 2023
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2024 --season-end 2025
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2015 --season-end 2025
```

All plan-only runs exited 0.

Planned source families:

| Source Family | Target Table |
| --- | --- |
| schedules | `raw_nflverse_schedules` |
| teams | `raw_nflverse_teams` |
| players | `raw_nflverse_players` |
| ff_playerids | `raw_nflverse_ff_playerids` |
| rosters | `raw_nflverse_rosters` |
| rosters_weekly | `raw_nflverse_rosters_weekly` |
| weekly | `raw_nflverse_weekly` |
| pbp | `raw_nflverse_pbp` |
| snap_counts | `raw_nflverse_snap_counts` |

Repeated planner warnings:

- Phase 29.5 planner only. No nflverse loaders called, no BigQuery rows written.
- Raw `raw_nflverse_*` tables are not Pigskin or UI-safe surfaces.
- Schedules include week but loader is season-level.
- Roster-weekly, weekly, and pbp loader week planning is post-load filtering, not week-bounded extraction.
- Snap share is valid from snap counts. Route share still needs a true route source.

## Raw Executor Dry-Run Results

Commands run:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2015 --season-end 2017 --dry-run
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2018 --season-end 2020 --dry-run
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2021 --season-end 2023 --dry-run
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2024 --season-end 2025 --dry-run
```

All executor dry-runs exited 0 with `dry_run=True` and no writes.

Warning:

- The executor output still has stale `next_required_phase` wording that references an authorized 2014 core smoke write. The behavior is dry-run safe, but the wording should be cleaned up in a future maintenance phase.

## Prepare-Only Estimates

Prepare-only was run with `--skip-source-family-on-error`, no write flag, and no write authorization.

Full proposed batch prepare-only runs completed for:

- 2015-2017
- 2018-2020
- 2021-2023
- 2024-2025

Because full batch output was large, single-season samples were captured for representative expansion risk.

| Season | schedules | teams | players | ff_playerids prepared/skipped | rosters prepared/skipped | rosters_weekly prepared/skipped | weekly prepared/skipped | pbp | snap_counts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2015 | 267 | 36 | 25,033 | 69,060 / 9,686 | 2,189 / 1 | 30,201 / 1,897 | 17,592 / 21 | 48,122 | 23,842 |
| 2018 | 267 | 36 | 25,033 | 69,060 / 9,686 | 3,141 / 1 | 52,200 / 38 | 17,393 / 21 | 47,109 | 23,877 |
| 2021 | 285 | 36 | 25,033 | 69,060 / 9,686 | 2,960 / 1 | 46,670 / 26 | 18,947 / 22 | 49,922 | 26,468 |
| 2024 | 285 | 36 | 25,033 | 69,060 / 9,686 | 3,215 / 1 | 46,572 / 7 | 18,959 / 22 | 49,492 | 26,615 |
| 2025 | 285 | 36 | 25,033 | 69,060 / 9,686 | 3,134 / 3 | 46,831 / 18 | 19,399 / 22 | 48,771 | 26,612 |

Prepare-only warnings:

- `ff_playerids` appears global/static and expands from 12,465 fetched rows to 69,060 prepared rows with 9,686 skipped rows in every sample. Future writes should be idempotent and should avoid repeatedly treating the table as season-grained.
- 2015 `rosters_weekly` skipped 1,897 rows, much higher than later sample seasons. That is the main reason to start with 2015 only.
- `weekly` consistently skips 21 or 22 rows for missing `player_id`. This is expected but should stay visible in materialization reports.
- Schedule counts move from 267 to 285 at the 2021 schedule era boundary.

## Staging Dry-Run Results

Commands run:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2015 --season-end 2017 --dry-run --all-targets
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2018 --season-end 2020 --dry-run --all-targets
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2021 --season-end 2023 --dry-run --all-targets
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2024 --season-end 2025 --dry-run --all-targets
```

All staging dry-runs exited 0 with `dry_run=True` and `wrote=False`.

The dry-runs returned planned row count 0 and blocked readiness for all 2015+ targets because raw rows for 2015+ have not been written yet.

Targets checked:

- `stg_player_identity`
- `stg_game_context`
- `stg_player_week_stats`
- `stg_team_week_stats`
- `stg_play_player_events`
- `stg_participation_context`

Warnings preserved:

- No name-only identity joins are used.
- Route metrics are not created in play-player events.
- `snap_counts` uses PFR IDs. `route_share` stays null and `has_true_route_source` stays false.

## Advanced Metrics Dry-Run Results

Commands run:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2015 --season-end 2017 --dry-run --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2018 --season-end 2020 --dry-run --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2021 --season-end 2023 --dry-run --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2024 --season-end 2025 --dry-run --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics
```

All advanced-metric dry-runs exited 0 with `dry_run=True` and `wrote=False`.

Each target returned planned row count 0 and blocked readiness because staging rows do not exist yet for 2015+.

Targets checked:

- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

## Pigskin Packet Dry-Run Results

Commands run:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2015 --season-end 2017 --dry-run --limit 25
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2018 --season-end 2020 --dry-run --limit 25
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2021 --season-end 2023 --dry-run --limit 25
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2024 --season-end 2025 --dry-run --limit 25
```

All packet dry-runs exited 0.

| Batch | Dry Run | Wrote | Position Diagnostics | Packet Examples |
| --- | --- | --- | --- | ---: |
| 2015-2017 | true | false | none | 0 |
| 2018-2020 | true | false | none | 0 |
| 2021-2023 | true | false | none | 0 |
| 2024-2025 | true | false | none | 0 |

Warnings preserved:

- Phase 29.11 is read-only and dry-run only.
- Pigskin packet writes are limited to `pigskin_player_context_packet_current`.
- Packet SQL reads current/base feature marts only, not raw or legacy source tables.

## Era Risk Review

| Era | Risk |
| --- | --- |
| 2015 | Highest prepare-only warning. `rosters_weekly` skipped 1,897 rows. Start here as a single-season gate. |
| 2016-2017 | Should follow 2015 only after raw and staging validations prove the skipped-row behavior is understood. |
| 2018-2020 | Lower skipped-row rates in sample year 2018. Still pre-17-game schedule. |
| 2021-2023 | 17-game schedule era begins. Schedule count changes from 267 to 285. |
| 2024-2025 | Near-current data. Do not present historical outputs as current content unless the selected source season/week is explicitly current and verified. |

## Recommended Next Write Phase

Recommended Phase 29.15:

Authorized raw backfill for 2015 only.

Proposed shape:

```powershell
$env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL = "true"
.\venv\Scripts\python.exe -m src.nflverse_backfill --preset core_historical --season-start 2015 --season-end 2015 --write
Remove-Item Env:\ALLOW_NFLVERSE_HISTORICAL_BACKFILL -ErrorAction SilentlyContinue
```

Required immediately after:

- Verify raw row counts for 2015.
- Verify duplicate grain checks for raw families.
- Run `raw_nflverse` validations.
- Stop before staging unless a separate staging authorization phase is issued.

If owner accepts the 2015 `rosters_weekly` warning, an alternative Phase 29.15 can run 2015-2017 as Batch A, but this report recommends the smaller first write.

## Future Expansion Sequence

For each batch:

1. Raw backfill write.
2. Raw row count and duplicate checks.
3. Raw validations.
4. Staging dry-run.
5. Authorized staging materialization.
6. Staging validations.
7. Advanced metrics dry-run.
8. Authorized advanced metrics materialization.
9. Advanced metrics validations.
10. Pigskin packet dry-run.
11. Authorized Pigskin packet materialization.
12. Compatibility view validation.
13. Confirm raw/source tables remain blocked from Pigskin.

## Versioning Plan

Recommended metric versions:

- `nflverse_adv_metrics_v0_2015_2017_001`
- `nflverse_adv_metrics_v0_2018_2020_001`
- `nflverse_adv_metrics_v0_2021_2023_001`
- `nflverse_adv_metrics_v0_2024_2025_001`

Recommended packet versions:

- `nflverse_pigskin_packet_v0_2015_2017_001`
- `nflverse_pigskin_packet_v0_2018_2020_001`
- `nflverse_pigskin_packet_v0_2021_2023_001`
- `nflverse_pigskin_packet_v0_2024_2025_001`

If the next write phase uses 2015 only, use:

- `nflverse_adv_metrics_v0_2015_001`
- `nflverse_pigskin_packet_v0_2015_001`

## Validation Results

Pattern validations:

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | 3 passed, 0 failed. Informational warning: `raw_nflverse_pbp` has 47,629 rows, min/max season 2014, 21 season-week combinations. |
| `stg_` | 7 passed, 0 failed. |
| `advanced_metrics` | 4 passed, 0 failed. |
| `compat_pigskin` | 2 passed, 0 failed. |
| `trade_player_scores` | 12 passed, 0 failed. |
| `trade_pick_scores` | 17 passed, 0 failed. Informational warning: model `trade_pick_score_v0_2026_001` has 64 rows. |

Final local checks:

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `python -m unittest discover tests` | 482 tests passed |
| `scripts/run_bigquery_migrations.py --list-pending` | No pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | 200 validation files discovered |

PowerShell surfaced Python stderr logging as `NativeCommandError` text during one combined check wrapper, but manual exit-code handling confirmed the commands exited 0.

## Production and Staging State

Production service:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Traffic: `nfl-studio-dashboard-00077-2jp=100%`
- All production risk flags false.
- Trade Analyzer score flags false.
- Trade History compatibility false.
- Data Ops Cloud Run trigger flags false.
- Data Ops local subprocess flags false.

Staging service:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Traffic: `nfl-studio-dashboard-staging-00029-jtb=100%`
- Existing staging score flags remain true from prior staging work.
- No staging deploy or flag mutation occurred in this phase.

## Warnings

- 2015 `rosters_weekly` skipped-row count is materially higher than later sample years.
- `ff_playerids` behaves like a global/static table and should be handled idempotently across batches.
- Optional nflverse raw families remain empty, so pressure, route, injury, depth-chart, and draft-pick enrichment remain unavailable in this Pigskin lane.
- Staging, advanced metrics, and packet dry-runs for 2015+ are blocked until raw rows are written.
- Executor dry-run output has stale 2014 next-phase wording.

## Blockers

No code or validation blocker for the next planner-approved step.

The next write step still requires explicit authorization and should be scoped to 2015 raw backfill only.

## Production Impact

None. Production and staging were not deployed, mutated, or reconfigured.
