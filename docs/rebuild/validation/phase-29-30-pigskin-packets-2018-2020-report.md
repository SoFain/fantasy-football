# Phase 29.30: 2018-2020 Pigskin Packet Refresh

Date: 2026-06-30

Final decision: **2018-2020 PIGSKIN PACKETS MATERIALIZED WITH WARNINGS**

## Scope

Phase 29.30 materialized only 2018-2020 Pigskin current context packets from the already materialized nflverse advanced metrics.

Target table:

- `fantasy-football-498121.fantasy_football_brain.pigskin_player_context_packet_current`

Packet version:

- `nflverse_pigskin_packet_v0_2018_2020_001`

Source metric version:

- `nflverse_adv_metrics_v0_2018_2020_001`

Bounded write window:

- `season_start=2018`
- `season_end=2020`

No raw backfill, staging materialization, advanced metrics materialization, deployment, feature-flag change, Cloud Run Job trigger, Pigskin prompt, LLM call, external scrape, Firebase artifact, or commit was performed.

## Authorization Gate State

Before the live write, all checked gates were empty or unset:

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

During the live packet command, only this gate was set inside the same PowerShell wrapper:

```powershell
ALLOW_PIGSKIN_PACKET_REFRESH=true
```

After the `finally` block, `ALLOW_PIGSKIN_PACKET_REFRESH` and all other checked gates were empty or unset again.

## Git State

Latest commit at start:

```text
a979a4f Expand nflverse Pigskin packets through 2017
```

No files were staged. The working tree had the known untracked historical validation backlog, including the Phase 29.29 report.

## Baseline Checks

All requested baseline checks passed before the write:

- `scripts/check_deployment_safety.py`: pass
- `py_compile` for `src/nflverse_pigskin_packets.py`: pass
- `py_compile` for `src/nflverse_advanced_metrics.py`: pass
- `py_compile` for `src/nflverse_staging.py`: pass
- `py_compile` for `src/nflverse_backfill.py`: pass
- `py_compile` for `src/nflverse_backfill_plan.py`: pass
- `compileall -q src scripts`: pass
- `tests.test_nflverse_pigskin_packets`: 15 tests passed
- `tests.test_nflverse_advanced_metrics`: 12 tests passed
- `unittest discover tests`: 487 tests passed
- `run_bigquery_migrations.py --list-pending`: no pending migrations
- `run_bigquery_validations.py --dry-run`: validation catalog discovered through 200

## Packet Source Precheck

Read-only source counts matched the expected Phase 29.28 source state.

| Object | 2018 | 2019 | 2020 |
| --- | ---: | ---: | ---: |
| `player_week_advanced_metrics` | 17,393 | 17,341 | 17,581 |
| `team_week_context_metrics` | 534 | 534 | 538 |
| `qb_week_environment_metrics` | 653 | 653 | 682 |

Current derived feature views:

- `player_recent_advanced_metrics_current`: 4,344 rows
- `player_role_usage_metrics_current`: 4,344 rows

## Packet Target Pre-Write State

Before the write:

- `pigskin_player_context_packet_current`: 1,587 rows
- `compat_pigskin_player_context_current`: 1,587 rows

Season distribution before the write:

| Season | Rows |
| --- | ---: |
| 2014 | 482 |
| 2015 | 498 |
| 2016 | 128 |
| 2017 | 479 |

Target packet version pre-write:

- `nflverse_pigskin_packet_v0_2018_2020_001`: 0 rows in target table
- `nflverse_pigskin_packet_v0_2018_2020_001`: 0 rows in compat view

## Final All-Position Dry-Run

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2018 --season-end 2020 --dry-run --limit 25 --strict --packet-version nflverse_pigskin_packet_v0_2018_2020_001 --source-metric-version nflverse_adv_metrics_v0_2018_2020_001 --output-json %TEMP%\phase29_30_packet_dry_run_all.json
```

Result:

- No writes
- Candidate rows: 749
- QB candidates: 106
- RB candidates: 197
- WR candidates: 278
- TE candidates: 168
- Missing source freshness rows: 0
- Missing flags rows: 0
- Missing identity rows: 0
- Missing identity flag rows: 10
- Missing QB identity flag rows: 7
- Null CPOE rows: 80
- Null EPA/opportunity rows: 22
- Null snap-share rows: 30
- Sample-size warning rows: 22
- Non-fantasy position rows: 0
- No-opportunity rows: 0

Candidate universe remained QB/RB/WR/TE with at least one of targets, carries, weighted opportunity, dropbacks, or pass attempts greater than 0.

## By-Position Dry-Runs

| Position | Candidates | Null CPOE | Null EPA/opportunity | Null snap share | Sample-size warnings | Missing identity flag rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| QB | 106 | 11 | 22 | 2 | 22 | 0 |
| RB | 197 | 60 | 0 | 5 | 0 | 1 |
| WR | 278 | 8 | 0 | 19 | 0 | 9 |
| TE | 168 | 1 | 0 | 4 | 0 | 0 |

By-position dry-run commands wrote no rows and produced JSON outputs in `%TEMP%`:

- `%TEMP%\phase29_30_packet_dry_run_qb.json`
- `%TEMP%\phase29_30_packet_dry_run_rb.json`
- `%TEMP%\phase29_30_packet_dry_run_wr.json`
- `%TEMP%\phase29_30_packet_dry_run_te.json`

## Named-Player Dry-Run Summary

Read-only lookups were run for the requested names. All requested player examples had matching packet candidates after disambiguation where required.

| Name | Status | Post-write packet check |
| --- | --- | --- |
| Patrick Mahomes | Found | `P.Mahomes`, QB, KC, 2020 week 21 |
| Lamar Jackson | Found | `L.Jackson`, QB, BAL, 2020 week 19 |
| Josh Allen | Ambiguous on full-name lookup | Disambiguated with `--team BUF --position QB`, `J.Allen`, QB, BUF, 2020 week 20 |
| Tom Brady | Found | `T.Brady`, QB, TB, 2020 week 21 |
| Christian McCaffrey | Found | `C.McCaffrey`, RB, CAR, 2020 week 9 |
| Derrick Henry | Found | `D.Henry`, RB, TEN, 2020 week 18 |
| Alvin Kamara | Found | `A.Kamara`, RB, NO, 2020 week 19 |
| Saquon Barkley | Found | `S.Barkley`, RB, NYG, 2020 week 2 |
| Davante Adams | Found | `D.Adams`, WR, GB, 2020 week 20 |
| Michael Thomas | Found | `M.Thomas`, WR, NO, 2020 week 19 |
| DeAndre Hopkins | Found | `D.Hopkins`, WR, ARI, 2020 week 17 |
| Tyreek Hill | Ambiguous on full-name lookup | Disambiguated with `--team KC --position WR`, `T.Hill`, WR, KC, 2020 week 21 |
| Travis Kelce | Found | `T.Kelce`, TE, KC, 2020 week 21 |
| George Kittle | Found | `G.Kittle`, TE, SF, 2020 week 17 |

Ambiguous full-name lookups returned explicit warnings and did not silently choose the wrong candidate.

## Live Packet Write

The live write used the required same-session gate wrapper:

```powershell
try {
  $env:ALLOW_PIGSKIN_PACKET_REFRESH = "true"

  echo "ALLOW_PIGSKIN_PACKET_REFRESH=$env:ALLOW_PIGSKIN_PACKET_REFRESH"

  .\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2018 --season-end 2020 --write --strict --packet-version nflverse_pigskin_packet_v0_2018_2020_001 --source-metric-version nflverse_adv_metrics_v0_2018_2020_001 --output-json %TEMP%\phase29_30_packet_write.json

} finally {
  Remove-Item Env:\ALLOW_PIGSKIN_PACKET_REFRESH -ErrorAction SilentlyContinue
}
```

Write result:

- Exit code: 0
- SQL kind: `MERGE`
- Target: `pigskin_player_context_packet_current`
- `dml_affected_rows`: 749
- `wrote`: true
- Gate removed afterward: confirmed

No second write was run.

## Post-Write Packet Verification

After the write:

- `pigskin_player_context_packet_current`: 2,336 rows
- `compat_pigskin_player_context_current`: 2,336 rows

Season distribution:

| Season | Rows |
| --- | ---: |
| 2014 | 482 |
| 2015 | 498 |
| 2016 | 128 |
| 2017 | 479 |
| 2018 | 111 |
| 2019 | 113 |
| 2020 | 525 |

Packet version distribution:

| Packet version | Rows |
| --- | ---: |
| `nflverse_pigskin_packet_v0_2014_001` | 482 |
| `nflverse_pigskin_packet_v0_2015_001` | 498 |
| `nflverse_pigskin_packet_v0_2016_2017_001` | 607 |
| `nflverse_pigskin_packet_v0_2018_2020_001` | 749 |

Source metric version distribution:

| Source metric version | Rows |
| --- | ---: |
| `nflverse_adv_metrics_v0_2014_001` | 482 |
| `nflverse_adv_metrics_v0_2015_001` | 498 |
| `nflverse_adv_metrics_v0_2016_2017_001` | 607 |
| `nflverse_adv_metrics_v0_2018_2020_001` | 749 |

2018-2020 target packet verification:

- Row count: 749
- Season range: 2018 through 2020
- Week range: 1 through 21
- Position distribution: QB 106, RB 197, WR 278, TE 168
- Duplicate packet grain count: 0
- Missing packet JSON count: 0
- Missing packet text count: 0
- Missing source freshness count: 0
- Missing blocked metric flags count: 0
- Non-fantasy position rows: 0
- No-opportunity rows: 0
- Rows with packet warnings: 61
- Warning-count distribution: 688 rows with 0 warnings, 61 rows with 1 warning

The compat view returned the same 2014-2020 season distribution and the same 2018-2020 target packet verification counts.

## Packet Usefulness Review

Read-only packet lookups after the write confirmed the named players above have compact packet text and populated packet JSON. Example checks included:

- `P.Mahomes` packet text includes 2020 week 21, weighted opportunity, WOPR, EPA/opportunity, and EPA/dropback.
- `C.McCaffrey` packet text includes 2020 week 9, weighted opportunity 43, target share, WOPR, and EPA/opportunity.
- `D.Adams` packet text includes 2020 week 20, weighted opportunity 37.5, target share, WOPR, and EPA/opportunity.
- `T.Kelce` packet text includes 2020 week 21, weighted opportunity 37.5, target share, WOPR, and EPA/opportunity.

Ten deterministic sample packets per position were inspected from the target version. The sampled packet text:

- stayed compact;
- included player, position, team, season, and week;
- included useful opportunity and efficiency fields;
- carried warning text when warnings were present;
- did not mention `raw_nflverse`, `stg_`, `play_by_play`, `weekly_metrics`, or source table names in packet text.

Packet JSON includes source freshness metadata by design. The compatibility view validation still confirmed no raw-source dependency, and packet text did not expose raw/source table names.

## Display-Name Ambiguity Behavior

The full-name lookup remained fail-safe for known ambiguous display names:

- `Josh Allen`: two candidates. The CLI required `--team`, `--position`, or `--player-id`. The intended BUF QB resolved with `--team BUF --position QB`.
- `Tyreek Hill`: two candidates. The CLI required `--team`, `--position`, or `--player-id`. The intended KC WR resolved with `--team KC --position WR`.

No silent wrong-player selection was observed.

## Packet SQL and Source Isolation

Generated packet SQL read only the approved feature marts:

- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

Generated packet SQL did not read:

- `raw_nflverse_*`
- `stg_*`
- `play_by_play`
- `weekly_metrics`
- `player_rosters`
- `pigskin_player_context_packet_current`
- `compat_pigskin_player_context_current`

The write target was limited to `pigskin_player_context_packet_current`.

## Blocked Metric Confirmation

Blocked metrics remained explicit in packet JSON:

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

Additional blocked or unavailable contexts remained explicit where applicable:

- pressure/sack/scramble detail remains unavailable;
- pass rate over expected remains unavailable;
- route, first-read, red-zone, high-value-touch, and reception-flag-dependent metrics remain blocked.

## Non-Target Object Verification

Read-only count checks showed non-target objects remained unchanged from the Phase 29.29 baseline.

Raw tables:

| Table | Rows |
| --- | ---: |
| `raw_nflverse_schedules` | 1,871 |
| `raw_nflverse_rosters` | 19,805 |
| `raw_nflverse_rosters_weekly` | 294,691 |
| `raw_nflverse_weekly` | 122,495 |
| `raw_nflverse_pbp` | 332,721 |
| `raw_nflverse_snap_counts` | 168,196 |

Staging tables:

| Table | Rows |
| --- | ---: |
| `stg_player_identity` | 294,691 |
| `stg_game_context` | 1,871 |
| `stg_player_week_stats` | 122,495 |
| `stg_team_week_stats` | 3,742 |
| `stg_play_player_events` | 812,370 |
| `stg_participation_context` | 168,196 |

Feature marts and views:

| Object | Rows |
| --- | ---: |
| `player_week_advanced_metrics` | 122,495 |
| `team_week_context_metrics` | 3,742 |
| `qb_week_environment_metrics` | 4,513 |
| `player_recent_advanced_metrics_current` | 4,344 |
| `player_role_usage_metrics_current` | 4,344 |

Score lanes:

| Table | Rows |
| --- | ---: |
| `trade_player_scores` | 154 |
| `trade_pick_scores` | 64 |

## Validation Results

Post-write validation patterns:

- `raw_nflverse`: 3 passed, 0 failed. Informational coverage warning remains expected.
- `stg_`: 7 passed, 0 failed.
- `advanced_metrics`: 4 passed, 0 failed.
- `compat_pigskin`: 2 passed, 0 failed.
- `trade_player_scores`: 12 passed, 0 failed.
- `trade_pick_scores`: 17 passed, 0 failed. Informational model-version coverage warning remains expected.

No validation failure was observed.

## Final Local Checks

All requested final checks passed after the write:

- `scripts/check_deployment_safety.py`: pass
- `py_compile` for `src/nflverse_pigskin_packets.py`: pass
- `py_compile` for `src/nflverse_advanced_metrics.py`: pass
- `py_compile` for `src/nflverse_staging.py`: pass
- `py_compile` for `src/nflverse_backfill.py`: pass
- `py_compile` for `src/nflverse_backfill_plan.py`: pass
- `compileall -q src scripts`: pass
- `tests.test_nflverse_pigskin_packets`: 15 tests passed
- `tests.test_nflverse_advanced_metrics`: 12 tests passed
- `unittest discover tests`: 487 tests passed
- `run_bigquery_migrations.py --list-pending`: no pending migrations
- `run_bigquery_validations.py --dry-run`: validation catalog discovered through 200

## Staging and Production Untouched

Read-only Cloud Run describes confirmed no deployment occurred.

Production:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Traffic: `nfl-studio-dashboard-00077-2jp:100`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`
- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`

Staging:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Traffic: `nfl-studio-dashboard-staging-00029-jtb:100`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`
- Staging score and trade-history flags remained as previously configured.

## Remaining Warnings

- This is historical 2018-2020 content, not current-season content.
- The candidate set remains 2020-heavy because the current derived feature views expose more 2020 fantasy-position rows than 2018 or 2019.
- Display-name collisions are real. Ambiguous names must use `--team`, `--position`, or `--player-id`.
- Null CPOE, EPA/opportunity, snap share, and sample-size warning rows remain expected packet warnings.
- Route metrics, pressure/sack/scramble detail, red-zone usage, high-value touches, first-read share, and pass rate over expected remain blocked or unavailable.
- `raw_nflverse` validation 181 is informational and returned the expected coverage review.
- `trade_pick_scores` validation 178 is informational and returned the existing `trade_pick_score_v0_2026_001` model-version coverage row.

## Recommended Next Phase

Proceed to Phase 29.31 package and commit review for the 2018-2020 Pigskin packet refresh evidence and any approved package files. Do not start a 2021-plus expansion until a separate bounded phase explicitly authorizes the next source and packet window.
