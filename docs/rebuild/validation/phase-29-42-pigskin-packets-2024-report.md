# Phase 29.42 - Authorized 2024 Pigskin Packet Refresh

Date: 2026-06-30

Final decision: 2024 PIGSKIN PACKETS MATERIALIZED WITH WARNINGS

## Scope

Authorized live write was limited to `pigskin_player_context_packet_current` for the 2024 nflverse Pigskin packet lane.

Target versions:
- Packet version: `nflverse_pigskin_packet_v0_2024_001`
- Source metric version: `nflverse_adv_metrics_v0_2024_001`

No raw backfill, staging materialization, advanced metrics materialization, current-season lane work, deployment, Cloud Run Job trigger, Scheduler work, LLM-backed action, Pigskin prompt, scraping, Firebase artifact, commit, or feature flag change was run.

All BigQuery checks used neutral aliases such as `t`. No BigQuery table alias named `rows` was used.

## Authorization

Pre-write gate check:
- `ALLOW_PIGSKIN_PACKET_REFRESH`: unset
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`: unset
- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`: unset
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`: unset
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`: unset
- `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`: unset
- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`: unset
- `ALLOW_TRADE_SCORE_MATERIALIZATION`: unset
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`: unset
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`: unset

The live write was run inside a scoped PowerShell `try/finally` block with only:

```powershell
$env:ALLOW_PIGSKIN_PACKET_REFRESH = "true"
```

The gate was removed immediately after the command. Final gate check showed all authorization gates unset.

## Git State

Latest commit before this report:
- `e56afa3 Expand nflverse Pigskin packets through 2023`

No files were staged. The worktree still contains the existing untracked historical validation backlog and recent Phase 29 report files.

## Baseline Checks

Passed before write:
- `scripts/check_deployment_safety.py`
- `py_compile` for `src/nflverse_pigskin_packets.py`
- `py_compile` for `src/nflverse_advanced_metrics.py`
- `py_compile` for `src/nflverse_staging.py`
- `py_compile` for `src/nflverse_backfill.py`
- `py_compile` for `src/nflverse_backfill_plan.py`
- `compileall -q src scripts`
- `tests.test_nflverse_pigskin_packets`: 15 tests passed
- `tests.test_nflverse_advanced_metrics`: 12 tests passed
- `unittest discover tests`: 487 tests passed
- `scripts/run_bigquery_migrations.py --list-pending`: no pending migrations
- `scripts/run_bigquery_validations.py --dry-run`: validations discovered through `200`

## Source Coverage Before Write

2024 source and feature coverage:

| Object | 2024 rows | Week range | Future rows |
|---|---:|---:|---:|
| `player_week_advanced_metrics` | 18,959 | 1-22 | 0 |
| `team_week_context_metrics` | 570 | 1-22 | 0 |
| `qb_week_environment_metrics` | 707 | 1-22 | 0 |
| `player_recent_advanced_metrics_current` | 2,001 current 2024 rows | 1-22 | 0 |
| `player_role_usage_metrics_current` | 2,001 current 2024 rows | 1-22 | 0 |

Pre-write packet target state:
- `pigskin_player_context_packet_current`: 3,082 total rows
- `compat_pigskin_player_context_current`: 3,082 total rows
- Existing packet seasons: 2014 through 2023
- Target packet version `nflverse_pigskin_packet_v0_2024_001`: 0 rows
- Future packet rows: 0

## Final Dry-Run Results

All-position dry-run:
- Candidate packet rows: 492
- QB: 79
- RB: 123
- WR: 185
- TE: 105
- Missing identity rows: 0
- Missing source freshness rows: 0
- Missing flags rows: 0
- Rows with sample-size warning: 15
- `missing_qb_identity` flag rows: 5
- Blocked metrics count: 11

By-position dry-run:

| Position | Candidates | Notable warnings |
|---|---:|---|
| QB | 79 | 15 `null_epa_per_opportunity`, 15 sample-size warning rows |
| RB | 123 | 1 `missing_qb_identity` flag row |
| WR | 185 | 4 `missing_qb_identity` flag rows |
| TE | 105 | none beyond blocked metric disclosures |

Dry-run source tables:
- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

## Named Player Dry-Runs

All 25 named-player packet lookups found written packet rows after materialization.

Examples:

| Lookup | Packet | Pos | Team | Week | Weighted opportunity | WOPR |
|---|---|---|---|---:|---:|---:|
| Patrick Mahomes | `P.Mahomes` | QB | KC | 22 | 4.0 | 0 |
| Josh Allen | `J.Allen` | QB | BUF | 21 | 11.0 | 0 |
| Jalen Hurts | `J.Hurts` | QB | PHI | 22 | 11.0 | 0 |
| Justin Jefferson | `J.Jefferson` | WR | MIN | 19 | 20.0 | 0.5410 |
| Ja'Marr Chase | `J.Chase` | WR | CIN | 18 | 35.0 | 0.7787 |
| Tyreek Hill | `T.Hill` | WR | MIA | 18 | 7.5 | 0.2166 |
| A.J. Brown | `A.Brown` | WR | PHI | 22 | 12.5 | 0.5997 |
| Saquon Barkley | `S.Barkley` | RB | PHI | 22 | 42.5 | 0.4565 |
| Travis Kelce | `T.Kelce` | TE | KC | 22 | 15.0 | 0.3539 |
| Brock Bowers | `B.Bowers` | TE | LV | 18 | 22.5 | 0.6251 |

Deterministic sample rows included Week 22 postseason rows for `P.Mahomes`, `J.Hurts`, `S.Barkley`, `A.Brown`, and `T.Kelce`.

## Display-Name Ambiguity

Ambiguous names warned instead of silently resolving:
- `Justin Jefferson`: 2 candidates, warning emitted
- `Tyreek Hill`: 2 candidates, warning emitted
- `B.Allen`: 2 candidates, warning emitted
- `D.Johnson`: 2 candidates, warning emitted
- `J.Jefferson`: 2 candidates, warning emitted
- `T.Hill`: 2 candidates, warning emitted
- `K.Allen`: 2 candidates, warning emitted

Disambiguated dry-runs returned one candidate and no ambiguity warning:
- `Justin Jefferson`, `MIN`, `WR` -> `J.Jefferson`, `MIN`, `WR`
- `Tyreek Hill`, `MIA`, `WR` -> `T.Hill`, `MIA`, `WR`
- `B.Allen`, `NYJ`, `RB` -> `B.Allen`, `NYJ`, `RB`
- `D.Johnson`, `HOU`, `WR` -> `D.Johnson`, `HOU`, `WR`
- `J.Jefferson`, `MIN`, `WR` -> `J.Jefferson`, `MIN`, `WR`
- `T.Hill`, `MIA`, `WR` -> `T.Hill`, `MIA`, `WR`
- `K.Allen`, `CHI`, `WR` -> `K.Allen`, `CHI`, `WR`

## Live Write

Command:

```powershell
$tmp = Join-Path $env:TEMP 'phase29_42_packet_write_stdout.txt'
$out = Join-Path $env:TEMP 'phase29_42_packet_write.json'
try {
  $env:ALLOW_PIGSKIN_PACKET_REFRESH = "true"

  .\venv\Scripts\python.exe -m src.nflverse_pigskin_packets `
    --season-start 2024 `
    --season-end 2024 `
    --write `
    --strict `
    --packet-version nflverse_pigskin_packet_v0_2024_001 `
    --source-metric-version nflverse_adv_metrics_v0_2024_001 `
    --output-json $out > $tmp 2>&1
  $exitCode = $LASTEXITCODE
} finally {
  Remove-Item Env:\ALLOW_PIGSKIN_PACKET_REFRESH -ErrorAction SilentlyContinue
}
```

Result:
- Exit code: 0
- `wrote`: true
- Write target: `pigskin_player_context_packet_current`
- Write SQL kind: `MERGE`
- DML affected rows: 492
- Bounded post-write row count for packet version: 492
- Duplicate packet grain count: 0
- Source season range in written rows: 2024 to 2024
- Week range in written rows: 2 to 22
- Packet version count: 1
- Source metric version count: 1
- Rows with packet warnings: 22
- Missing packet JSON: 0
- Missing packet text: 0
- Missing source freshness: 0
- Missing blocked metric flags: 0

## Post-Write Verification

Packet totals after write:

| Object | Total rows | 2024 rows | Future rows |
|---|---:|---:|---:|
| `pigskin_player_context_packet_current` | 3,574 | 492 | 0 |
| `compat_pigskin_player_context_current` | 3,574 | 492 | 0 |

Packet rows by season:

| Season | Rows |
|---:|---:|
| 2014 | 482 |
| 2015 | 498 |
| 2016 | 128 |
| 2017 | 479 |
| 2018 | 111 |
| 2019 | 113 |
| 2020 | 525 |
| 2021 | 107 |
| 2022 | 131 |
| 2023 | 508 |
| 2024 | 492 |

2024 position distribution:
- QB: 79
- RB: 123
- WR: 185
- TE: 105

2024 packet quality:
- Duplicate packet grain count: 0
- Missing packet JSON: 0
- Missing packet text: 0
- Missing source freshness: 0
- Missing blocked metric flags: 0
- Warning count distribution: 470 rows with 0 warnings, 22 rows with 1 warning

## Source Isolation

Packet SQL reads only these derived feature marts:
- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

Confirmed absent from packet SQL and diagnostics SQL:
- `raw_nflverse_`
- `play_by_play`
- `weekly_metrics`
- `player_rosters`
- `pigskin_player_context_packet_current` as a source
- `compat_pigskin_player_context_current` as a source
- `content_briefs`
- `llm_player_context_packet`
- `trade_player_scores`
- `trade_pick_scores`

Blocked metrics are explicitly listed in packet output, not inferred:
- `route_share`
- `yards_per_route_run`
- `targets_per_route_run`
- `first_read_share`
- `red_zone_usage`
- `high_value_touches`
- `touchdown_rates`
- `reception_flag_dependent_metrics`
- `true_pressure`
- `contact_yards`
- `alignment`

## 2024 and Current-Season Separation

2024 packets include playoff/postseason weeks through Week 22. This is expected for the historical 2024 lane and is not current-season content.

No 2025 or future packet rows were created. Current-season and content-brief lanes were not touched.

## Non-Target Object Verification

Read-only checks after the packet write:

| Object | Total rows | 2024 rows | Future rows |
|---|---:|---:|---:|
| `raw_nflverse_pbp` | 531,234 | 49,492 | 0 |
| `raw_nflverse_weekly` | 197,831 | 18,959 | 0 |
| `raw_nflverse_rosters_weekly` | 479,719 | 46,572 | 0 |
| `raw_nflverse_schedules` | 3,010 | 285 | 0 |
| `raw_nflverse_snap_counts` | 274,200 | 26,615 | 0 |
| `stg_player_identity` | 479,719 | 46,572 | 0 |
| `stg_game_context` | 3,010 | 285 | 0 |
| `stg_player_week_stats` | 197,831 | 18,959 | 0 |
| `stg_team_week_stats` | 6,020 | 570 | 0 |
| `stg_play_player_events` | 1,291,263 | 118,037 | 0 |
| `stg_participation_context` | 274,200 | 26,615 | 0 |
| `player_week_advanced_metrics` | 197,831 | 18,959 | 0 |
| `team_week_context_metrics` | 6,020 | 570 | 0 |
| `qb_week_environment_metrics` | 7,350 | 707 | 0 |
| `player_recent_advanced_metrics_current` | 5,883 | 2,001 | 0 |
| `player_role_usage_metrics_current` | 5,883 | 2,001 | 0 |

Score tables were unchanged by this phase:
- `trade_player_scores`: 154 rows
- `trade_player_scores_current`: 77 rows
- `compat_trade_player_scores_current`: 77 rows
- `trade_pick_scores`: 64 rows
- `trade_pick_scores_current`: 64 rows
- `compat_trade_pick_scores_current`: 64 rows

## Validation Results

Post-write validation patterns:
- `raw_nflverse`: 3 passed, 0 failed. One informational coverage warning.
- `stg_`: 7 passed, 0 failed.
- `advanced_metrics`: 4 passed, 0 failed.
- `compat_pigskin`: 2 passed, 0 failed.
- `trade_player_scores`: 12 passed, 0 failed.
- `trade_pick_scores`: 17 passed, 0 failed. One informational model-version coverage warning.

## Final Local Checks

Final checks passed:
- `scripts/check_deployment_safety.py`
- `py_compile` for all nflverse pipeline modules in scope
- `compileall -q src scripts`
- `tests.test_nflverse_pigskin_packets`: 15 tests passed
- `tests.test_nflverse_advanced_metrics`: 12 tests passed
- `unittest discover tests`: 487 tests passed
- `scripts/run_bigquery_migrations.py --list-pending`: no pending migrations
- `scripts/run_bigquery_validations.py --dry-run`: validations discovered through `200`

## Production and Staging Untouched

Production readback:
- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Production risk flags: false
- Trade Analyzer score flags: false
- Trade History compatibility: false
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false

Staging readback:
- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Staging score flags remained in their existing QA state.
- Job trigger and local subprocess flags remained false.

## Warnings

- `raw_nflverse` validation includes an informational coverage review row. No failure.
- `trade_pick_scores` validation includes an informational model-version coverage review row. No failure.
- 22 of 492 2024 packets have one packet warning, mostly expected sample-size or null metric disclosures.
- Display-name collisions remain by design. Ambiguous lookups warn and require `--team`, `--position`, or `--player-id`.
- Historical 2024 packets include playoff weeks through Week 22. Do not present these as current-season rows.
- The worktree still contains historical untracked validation backlog files from earlier phases.

## Recommended Next Phase

Proceed to Phase 29.43 package and commit review for the 2024 Pigskin packet refresh evidence, or continue the nflverse expansion with a separate, explicitly authorized 2025 historical lane if that is still part of the rollout plan.
