# Phase 29.12 Pigskin Packet Materialization Report

Date: 2026-06-29

Final decision: PIGSKIN CURRENT PACKETS MATERIALIZED WITH WARNINGS

## Scope

Authorized materialization of the 2014 Pigskin current context packet lane from the already materialized nflverse advanced metrics layer.

Only this target was written:

- `pigskin_player_context_packet_current`

No direct write was made to:

- `compat_pigskin_player_context_current`, which remains a view
- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`
- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- raw nflverse tables
- staging nflverse tables
- trade player score tables
- trade pick score tables

No deployment, staging update, Cloud Run Job trigger, Scheduler job, ingestion, rankings run, LLM action, Pigskin prompt, scrape, Firebase artifact, git staging, or commit occurred.

## Authorization

All gates were confirmed unset before the write phase, including:

- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`
- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`
- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

The live write was run inside a PowerShell `try/finally` wrapper with only:

```powershell
$env:ALLOW_PIGSKIN_PACKET_REFRESH = "true"
```

The gate was removed afterward. Final readback:

```text
ALLOW_PIGSKIN_PACKET_REFRESH=
```

## Target Versions

- Packet version: `nflverse_pigskin_packet_v0_2014_001`
- Source metric version: `nflverse_adv_metrics_v0_2014_001`
- Target season: 2014
- Target positions: QB, RB, WR, TE
- Candidate filter: at least one of `targets`, `carries`, `weighted_opportunity`, `dropbacks`, or `pass_attempts` greater than zero

The table stores the season and week as `as_of_season` and `as_of_week`. The source metric version is preserved in `packet_json` and `advanced_metrics_json`.

## Dry-Run Proof

Commands run before the live write:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2014 --season-end 2014 --dry-run --limit 25 --strict --packet-version nflverse_pigskin_packet_v0_2014_001 --source-metric-version nflverse_adv_metrics_v0_2014_001
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2014 --season-end 2014 --dry-run --position QB --limit 25 --strict --packet-version nflverse_pigskin_packet_v0_2014_001 --source-metric-version nflverse_adv_metrics_v0_2014_001
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2014 --season-end 2014 --dry-run --position RB --limit 25 --strict --packet-version nflverse_pigskin_packet_v0_2014_001 --source-metric-version nflverse_adv_metrics_v0_2014_001
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2014 --season-end 2014 --dry-run --position WR --limit 25 --strict --packet-version nflverse_pigskin_packet_v0_2014_001 --source-metric-version nflverse_adv_metrics_v0_2014_001
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2014 --season-end 2014 --dry-run --position TE --limit 25 --strict --packet-version nflverse_pigskin_packet_v0_2014_001 --source-metric-version nflverse_adv_metrics_v0_2014_001
```

Dry-run diagnostics:

| Slice | Candidate rows |
| --- | ---: |
| All QB/RB/WR/TE | 482 |
| QB | 73 |
| RB | 126 |
| WR | 179 |
| TE | 104 |

Dry-run source tables:

- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

Dry-run did not read raw nflverse tables or legacy source tables.

## Live Write

Command shape:

```powershell
try {
  $env:ALLOW_PIGSKIN_PACKET_REFRESH = "true"

  .\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2014 --season-end 2014 --write --strict --packet-version nflverse_pigskin_packet_v0_2014_001 --source-metric-version nflverse_adv_metrics_v0_2014_001
} finally {
  Remove-Item Env:\ALLOW_PIGSKIN_PACKET_REFRESH -ErrorAction SilentlyContinue
}
```

Write result:

- Write SQL kind: `MERGE`
- Target: `pigskin_player_context_packet_current`
- DML affected rows: 482
- Bounded post-write row count: 482
- Duplicate packet grain count: 0
- Packet version count: 1
- Source metric version count: 1
- Missing packet JSON count: 0
- Missing packet text count: 0
- Missing source freshness count: 0
- Missing blocked metric flag count: 0
- Rows with packet warnings: 136

## Post-Write Warehouse Verification

Packet summary:

| Metric | Value |
| --- | ---: |
| `pigskin_player_context_packet_current` rows | 482 |
| `compat_pigskin_player_context_current` rows | 482 |
| Min `as_of_season` | 2014 |
| Max `as_of_season` | 2014 |
| Min `as_of_week` | 1 |
| Max `as_of_week` | 21 |
| Packet versions | 1 |
| Source metric versions | 1 |
| Duplicate packet grains | 0 |

Position distribution:

| Position | Rows |
| --- | ---: |
| QB | 73 |
| RB | 126 |
| TE | 104 |
| WR | 179 |

Non-target feature row counts after the packet write:

| Object | Rows |
| --- | ---: |
| `player_week_advanced_metrics` | 17,601 |
| `team_week_context_metrics` | 534 |
| `qb_week_environment_metrics` | 643 |
| `player_recent_advanced_metrics_current` | 1,854 |
| `player_role_usage_metrics_current` | 1,854 |
| `trade_player_scores` | 154 |
| `trade_pick_scores` | 64 |

The five feature metrics objects match the pre-write counts captured earlier in the phase. Trade score tables were read for count verification only and were not written.

`compat_pigskin_player_context_current` is a view. Validation `198_compat_pigskin_context_no_raw_dependencies.sql` passed with `raw_source_dependency_count = 0`.

## Named Player Spot Checks

The packet table uses nflverse-style abbreviated names. Spot checks found useful context for the requested players:

| Requested player | Packet name | Position | Team | Week | Notable fields |
| --- | --- | --- | --- | ---: | --- |
| Aaron Rodgers | `A.Rodgers` | QB | GB | 20 | packet present, source metric version preserved |
| DeMarco Murray | `D.Murray` | RB | DAL | 19 | weighted opportunity 30, WOPR 0.1579 |
| Antonio Brown | `A.Brown` | WR | PIT | 18 | weighted opportunity 35, WOPR 0.7174 |
| Rob Gronkowski | `R.Gronkowski` | TE | NE | 21 | weighted opportunity 25, WOPR 0.5207 |
| Odell Beckham Jr. | `O.Beckham` | WR | NYG | 17 | weighted opportunity 52.5, WOPR 0.9177 |
| DeAndre Hopkins | `D.Hopkins` | WR | HOU | 17 | weighted opportunity 15, WOPR 0.4587 |

All spot-checked packets carry the packet version `nflverse_pigskin_packet_v0_2014_001` and source metric version `nflverse_adv_metrics_v0_2014_001`.

## Random Packet Review

Random samples by position returned packet text for 10 QB, 10 RB, 10 WR, and 10 TE rows. Examples included:

- `B.Bortles`, QB, JAX, week 17
- `M.Forte`, RB, CHI, week 17
- `R.Gronkowski`, TE, NE, week 21
- `A.Brown`, WR, PIT, week 18

Packet text includes player, position, team, season/week, weighted opportunity, target share, WOPR, EPA/opportunity, and QB environment fields when available.

Blocked metric caveat is explicit in every checked packet. The blocked metric list includes route share, yards per route run, first-read share, red-zone usage, true pressure, contact yards, and alignment metrics. These are not fabricated.

## Validation Results

Requested validation patterns:

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | 3 passed, 0 failed. One informational coverage warning |
| `stg_` | 7 passed, 0 failed |
| `advanced_metrics` | 4 passed, 0 failed |
| `compat_pigskin` | 2 passed, 0 failed |
| `trade_player_scores` | 12 passed, 0 failed |
| `trade_pick_scores` | 17 passed, 0 failed. One informational model-version coverage warning |

Local checks:

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile` for nflverse packet/backfill/staging/advanced modules | PASS |
| `compileall -q src scripts` | PASS |
| Targeted nflverse/Pigskin tests | 75 tests passed |
| Full test discovery | 482 tests passed |
| `scripts/run_bigquery_migrations.py --list-pending` | No pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | Discovers validation catalog through 200 |

## Deployment State

Read-only Cloud Run describe was run after materialization.

Production:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Image digest: `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- Production risk flags: false
- Trade Analyzer score flags: false
- Trade History compatibility: false
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false

Staging:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- Staging score and Trade History QA flags remain enabled from prior staging work
- Data Ops trigger and local subprocess flags remain false

No service was deployed or modified.

## Warnings

- 136 packet rows have warning arrays, mostly expected missing snap share or sample-size warnings.
- Raw nflverse coverage validation is informational and returned current 2014 coverage for review.
- Trade pick score model-version coverage validation is informational and reflects existing 64 draft-pick score rows.
- The packet table stores season/week as `as_of_season` and `as_of_week`. `packet_json` stores the source metric version but does not currently include a separate `source_season` key.
- Dry-run warning text still identifies the read-only path as Phase 29.11. The write path and report are Phase 29.12.

## Production Suitability

Status: staging/current packet review ready.

These packets are useful for Pigskin context testing against 2014 historical advanced metrics. They should not be presented as 2026 current-season content. The compatibility view is populated only from the packet table and does not expose raw/source dependencies.

## Final Decision

PIGSKIN CURRENT PACKETS MATERIALIZED WITH WARNINGS

