# Phase 29.18 - Authorized 2015 Pigskin Packet Refresh

Date: 2026-06-29

Final decision: 2015 PIGSKIN PACKETS MATERIALIZED WITH WARNINGS

## Scope

Authorized dry-run and materialization of 2015 Pigskin current context packets from the 2015 nflverse advanced-metrics layer.

Target season range:

- `season_start=2015`
- `season_end=2015`

Packet version:

- `nflverse_pigskin_packet_v0_2015_001`

Source metric version:

- `nflverse_adv_metrics_v0_2015_001`

Write target:

- `pigskin_player_context_packet_current`

No raw backfill, staging materialization, advanced-metrics materialization, ranking build, Pigskin prompt, LLM-backed action, scrape, deployment, feature flag change, Cloud Run Job trigger, Scheduler job, Firebase artifact, or commit occurred.

## Required Code Fix Before Write

Before the live write, `src/nflverse_pigskin_packets.py` had a stale hardcoded packet-text label: `as of 2014 week`.

This was unsafe for a 2015 packet materialization because it would have mislabeled 2015 packet text while the row grain and JSON season were correct.

Changed files:

- `src/nflverse_pigskin_packets.py`
- `tests/test_nflverse_pigskin_packets.py`

Fix:

- Packet SQL now builds text with `as_of_season`.
- Dry-run preview text now uses `row["as_of_season"]`.
- `--write` help text now reflects current gated write behavior.
- Added focused regression coverage for dynamic season text and write SQL.

## Authorization Gate State

All gates were unset before the live write.

| Gate | Before | During live write | After |
| --- | --- | --- | --- |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset | `true` | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset | unset | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset | unset | unset |
| `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY` | unset | unset | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset | unset | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset | unset | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset | unset | unset |

The Pigskin packet gate was set only inside the same PowerShell `try/finally` wrapper around the one live packet command.

## Git State

Latest commit before the phase:

`4805610 Build nflverse Pigskin canary pipeline`

Worktree:

- Existing historical validation backlog remained untracked.
- No files were staged.
- No commit was created.
- This phase introduced tracked source/test changes for the 2015 packet-text label fix.

## Baseline Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `python -m py_compile src\nflverse_pigskin_packets.py` | PASS |
| `python -m py_compile src\nflverse_advanced_metrics.py` | PASS |
| `python -m py_compile src\nflverse_staging.py` | PASS |
| `python -m py_compile src\nflverse_backfill.py` | PASS |
| `python -m py_compile src\nflverse_backfill_plan.py` | PASS |
| `python -m compileall -q src scripts` | PASS |
| `python -m unittest tests.test_nflverse_pigskin_packets` | 11 tests passed |
| `python -m unittest tests.test_nflverse_advanced_metrics` | 12 tests passed |
| `python -m unittest discover tests` | 483 tests passed |
| `scripts/run_bigquery_migrations.py --list-pending` | No pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | 200 validation files discovered |

PowerShell displayed `NativeCommandError` wrappers for stderr logging during some Python test commands, but process exit codes were 0 and test summaries were PASS.

## Packet Source Precheck

2015 source rows were present before packet refresh.

| Object | 2015 Rows |
| --- | ---: |
| `player_week_advanced_metrics` | 17,592 |
| `team_week_context_metrics` | 534 |
| `qb_week_environment_metrics` | 618 |
| `player_recent_advanced_metrics_current` | 2,309 derived rows |
| `player_role_usage_metrics_current` | 2,309 derived rows |

## Packet Pre-Write State

| Object | Total Rows Before | 2014 Rows Before | 2015 Rows Before | Target Version Rows Before |
| --- | ---: | ---: | ---: | ---: |
| `pigskin_player_context_packet_current` | 482 | 482 | 0 | 0 |
| `compat_pigskin_player_context_current` | 482 | 482 | 0 | 0 |

Pre-write packet version distribution:

| Packet Version | Source Metric Version | Season | Rows |
| --- | --- | ---: | ---: |
| `nflverse_pigskin_packet_v0_2014_001` | `nflverse_adv_metrics_v0_2014_001` | 2014 | 482 |

## Dry-Run Summary

Command shape:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2015 --season-end 2015 --dry-run --limit 25 --strict --packet-version nflverse_pigskin_packet_v0_2015_001 --source-metric-version nflverse_adv_metrics_v0_2015_001
```

Position dry-runs used the same command with `--position QB`, `--position RB`, `--position WR`, and `--position TE`.

| Dry-Run | Candidate Rows | QB | RB | WR | TE | Missing Freshness | Missing Flags | Examples |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All | 498 | 73 | 132 | 188 | 105 | 0 | 0 | 25 |
| QB | 73 | 73 | 0 | 0 | 0 | 0 | 0 | 25 |
| RB | 132 | 0 | 132 | 0 | 0 | 0 | 0 | 25 |
| WR | 188 | 0 | 0 | 188 | 0 | 0 | 0 | 25 |
| TE | 105 | 0 | 0 | 0 | 105 | 0 | 0 | 25 |

Source tables used:

- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

Blocked metrics preserved:

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

The dry-run SQL read feature marts only. It did not read raw nflverse tables, legacy `play_by_play`, legacy `weekly_metrics`, or Pigskin packet tables.

## Named-Player Dry-Run Summary

| Requested Player | Found | Packet Name | Position | Team | As-Of Week | Notes |
| --- | --- | --- | --- | --- | ---: | --- |
| Aaron Rodgers | Yes | `A.Rodgers` | QB | GB | 19 | Useful QB packet text, no warnings |
| Cam Newton | Yes | `C.Newton` | QB | CAR | 21 | Missing snap-share warning |
| Antonio Brown | Yes | `A.Brown` | WR | PIT | 18 | Useful WR opportunity packet |
| Julio Jones | Yes | `J.Jones` | WR | ATL | 17 | Also matched `J.Jones` GB because the name filter supports compact initial-last variants |
| DeAndre Hopkins | Yes | `D.Hopkins` | WR | HOU | 18 | Missing snap-share warning |
| Todd Gurley | Yes | `T.Gurley` | RB | LA | 16 | Missing snap-share warning |
| Rob Gronkowski | Yes | `R.Gronkowski` | TE | NE | 20 | Useful TE packet |
| Travis Kelce | Yes | `T.Kelce` | TE | KC | 19 | Useful TE packet |

Example packet text after the season-label fix:

`A.Rodgers (QB, GB) as of 2015 week 19: weighted opportunity 2.0 target share 0.0 WOPR 0.0 EPA/opportunity 0.97471643937845 EPA/dropback 0.012721526692662898`

## Live Packet Write

Command:

```powershell
try {
  $env:ALLOW_PIGSKIN_PACKET_REFRESH = "true"

  echo "ALLOW_PIGSKIN_PACKET_REFRESH=$env:ALLOW_PIGSKIN_PACKET_REFRESH"

  .\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2015 --season-end 2015 --write --strict --packet-version nflverse_pigskin_packet_v0_2015_001 --source-metric-version nflverse_adv_metrics_v0_2015_001
} finally {
  Remove-Item Env:\ALLOW_PIGSKIN_PACKET_REFRESH -ErrorAction SilentlyContinue
}
```

Result:

- Exit code: 0
- `dry_run=False`
- `wrote=True`
- `dml_affected_rows=498`
- `write_sql_kind=MERGE`
- Target: `pigskin_player_context_packet_current`

Write result:

| Check | Result |
| --- | ---: |
| `bounded_row_count` | 498 |
| `duplicate_packet_grain_count` | 0 |
| `missing_packet_json_count` | 0 |
| `missing_packet_text_count` | 0 |
| `missing_source_freshness_count` | 0 |
| `missing_blocked_metric_flag_count` | 0 |
| `rows_with_packet_warnings` | 151 |
| `packet_version_count` | 1 |
| `source_metric_version_count` | 1 |
| As-of week range | 1 to 21 |

## Post-Write Packet Verification

| Object | Total Rows After | 2014 Rows | 2015 Rows | Season Range | 2015 Week Range |
| --- | ---: | ---: | ---: | --- | --- |
| `pigskin_player_context_packet_current` | 980 | 482 | 498 | 2014 to 2015 | 1 to 21 |
| `compat_pigskin_player_context_current` | 980 | 482 | 498 | 2014 to 2015 | 1 to 21 |

Version distribution:

| Packet Version | Source Metric Version | Season | Rows |
| --- | --- | ---: | ---: |
| `nflverse_pigskin_packet_v0_2014_001` | `nflverse_adv_metrics_v0_2014_001` | 2014 | 482 |
| `nflverse_pigskin_packet_v0_2015_001` | `nflverse_adv_metrics_v0_2015_001` | 2015 | 498 |

2015 position distribution:

| Position | Rows | Missing Text | Missing JSON | Missing Freshness | Missing Blocked Metrics | Mislabeled `2014 week` Text |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| QB | 73 | 0 | 0 | 0 | 0 | 0 |
| RB | 132 | 0 | 0 | 0 | 0 | 0 |
| TE | 105 | 0 | 0 | 0 | 0 | 0 |
| WR | 188 | 0 | 0 | 0 | 0 | 0 |

Grain and missing-data checks:

| Check | Result |
| --- | ---: |
| 2015 rows | 498 |
| Duplicate packet grains | 0 |
| Missing packet JSON | 0 |
| Missing packet text | 0 |
| Missing source freshness | 0 |
| Missing blocked metric flags | 0 |
| Wrong source metric version | 0 |
| Mislabeled `2014 week` packet text | 0 |
| Rows with warnings | 151 |
| Warning count range | 0 to 2 |

Warning distribution:

| Warning Count | Rows |
| ---: | ---: |
| 0 | 347 |
| 1 | 144 |
| 2 | 7 |

## Packet Usefulness Review

Named-player packets after write:

| Player | Position | Team | As-Of Week | Warning Count | Source Metric Version |
| --- | --- | --- | ---: | ---: | --- |
| `A.Brown` | WR | PIT | 18 | 0 | `nflverse_adv_metrics_v0_2015_001` |
| `A.Rodgers` | QB | GB | 19 | 0 | `nflverse_adv_metrics_v0_2015_001` |
| `C.Newton` | QB | CAR | 21 | 1 | `nflverse_adv_metrics_v0_2015_001` |
| `D.Hopkins` | WR | HOU | 18 | 1 | `nflverse_adv_metrics_v0_2015_001` |
| `J.Jones` | WR | ATL | 17 | 0 | `nflverse_adv_metrics_v0_2015_001` |
| `R.Gronkowski` | TE | NE | 20 | 0 | `nflverse_adv_metrics_v0_2015_001` |
| `T.Gurley` | RB | LA | 16 | 1 | `nflverse_adv_metrics_v0_2015_001` |
| `T.Kelce` | TE | KC | 19 | 0 | `nflverse_adv_metrics_v0_2015_001` |

Sample review:

- Deterministic samples of 10 QB, 10 RB, 10 WR, and 10 TE packets rendered compact packet text.
- 498 of 498 packet texts were between 60 and 500 characters.
- 498 of 498 rows had blocked metrics present.
- 151 rows had warning arrays, mostly sample/snap-share warnings.
- 0 packet text rows referenced `raw_nflverse_`, `stg_`, `play_by_play`, or `weekly_metrics`.
- Source freshness metadata is present for all 498 rows. It includes loader and freshness-source metadata, but packet text and compatibility validation do not expose raw/source table dependencies.

## Non-Target Object Verification

Raw source counts remained at the Phase 29.15/29.17 baseline:

| Raw Table | Total Rows | 2015 Rows |
| --- | ---: | ---: |
| `raw_nflverse_schedules` | 534 | 267 |
| `raw_nflverse_rosters` | 4,341 | 2,189 |
| `raw_nflverse_rosters_weekly` | 60,396 | 30,201 |
| `raw_nflverse_weekly` | 35,193 | 17,592 |
| `raw_nflverse_pbp` | 95,751 | 48,122 |
| `raw_nflverse_snap_counts` | 47,706 | 23,842 |

Staging counts remained at the Phase 29.16/29.17 baseline:

| Staging Table | Total Rows | 2015 Rows |
| --- | ---: | ---: |
| `stg_player_identity` | 60,396 | 30,201 |
| `stg_game_context` | 534 | 267 |
| `stg_player_week_stats` | 35,193 | 17,592 |
| `stg_team_week_stats` | 1,068 | 534 |
| `stg_play_player_events` | 234,469 | 118,069 |
| `stg_participation_context` | 47,706 | 23,842 |

Base advanced metrics remained at the Phase 29.17 baseline:

| Feature Table | Total Rows | 2015 Rows |
| --- | ---: | ---: |
| `player_week_advanced_metrics` | 35,193 | 17,592 |
| `team_week_context_metrics` | 1,068 | 534 |
| `qb_week_environment_metrics` | 1,261 | 618 |

Trade score lanes were unchanged:

| Object | Rows |
| --- | ---: |
| `trade_player_scores` | 154 |
| `trade_player_scores_current` | 77 |
| `compat_trade_player_scores_current` | 77 |
| `trade_pick_scores` | 64 |
| `trade_pick_scores_current` | 64 |
| `compat_trade_pick_scores_current` | 64 |

## Validation Results

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | 3 passed, 0 failed. Informational warning: raw nflverse now spans 2014 and 2015. |
| `stg_` | 7 passed, 0 failed |
| `advanced_metrics` | 4 passed, 0 failed |
| `compat_pigskin` | 2 passed, 0 failed |
| `trade_player_scores` | 12 passed, 0 failed |
| `trade_pick_scores` | 17 passed, 0 failed. Informational warning: `trade_pick_score_v0_2026_001` has 64 prior rows. |

## Final Local Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `python -m py_compile src\nflverse_pigskin_packets.py` | PASS |
| `python -m py_compile src\nflverse_advanced_metrics.py` | PASS |
| `python -m py_compile src\nflverse_staging.py` | PASS |
| `python -m py_compile src\nflverse_backfill.py` | PASS |
| `python -m py_compile src\nflverse_backfill_plan.py` | PASS |
| `python -m compileall -q src scripts` | PASS |
| `python -m unittest tests.test_nflverse_pigskin_packets` | 11 tests passed |
| `python -m unittest tests.test_nflverse_advanced_metrics` | 12 tests passed |
| `python -m unittest discover tests` | 483 tests passed |
| `scripts/run_bigquery_migrations.py --list-pending` | No pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | 200 validation files discovered |

## Deployment and Flag State

Production remained untouched:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Production risk flags: false
- Trade Analyzer score flags: false
- Trade History compatibility: false
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false

Staging remained untouched:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Expected staging-only flags remained true: `USE_COMPAT_TRADE_PLAYER_HISTORY`, `USE_TRADE_ANALYZER_SCORE_V0`, `USE_COMPAT_TRADE_PLAYER_SCORE`
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false

## Remaining Warnings

- Route metrics, pressure/sack/scramble metrics, pass rate over expected, red-zone usage, and high-value-touch metrics remain intentionally blocked in v0.
- 151 of 498 2015 packet rows include warning arrays, mainly missing snap-share or sample-size warnings.
- `--player-name "Julio Jones"` also matched `J.Jones` GB because the lookup supports compact initial-last variants. The expected ATL Julio packet was present.
- This phase required a small source/test fix before materialization so packet text did not mislabel 2015 rows as 2014.

## Recommended Next Phase

Phase 29.19 should package the 2015 raw, staging, advanced-metrics, and Pigskin packet expansion evidence for owner review. Do not rerun raw backfill, staging materialization, advanced metrics, or packet refresh unless a separate phase explicitly authorizes a bounded idempotency test.
