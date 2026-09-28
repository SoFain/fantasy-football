# Phase 29.29: 2018-2020 Pigskin Packet Dry Run

Date: 2026-06-30

Final decision: **2018-2020 PIGSKIN PACKET DRY RUN READY WITH WARNINGS**

## Scope

Ran read-only Pigskin packet dry-runs for 2018-2020 from the newly materialized nflverse advanced metrics.

No BigQuery rows were written. No Pigskin packet refresh, raw backfill, staging materialization, advanced metrics materialization, deployment, feature flag change, Cloud Run Job trigger, Scheduler change, Pigskin prompt, LLM action, scraping, or Firebase artifact creation occurred.

Packet version:

```text
nflverse_pigskin_packet_v0_2018_2020_001
```

Source metric version:

```text
nflverse_adv_metrics_v0_2018_2020_001
```

## Authorization Gate State

All checked gates were empty or unset:

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

No authorization gate was set during this phase.

## Git State

Latest commit:

```text
a979a4f Expand nflverse Pigskin packets through 2017
```

No files were staged. The known untracked historical validation backlog remains. This report is the only new Phase 29.29 artifact from this phase.

## Baseline Checks

All baseline checks passed:

- `scripts/check_deployment_safety.py`: PASS
- `py_compile src\nflverse_pigskin_packets.py`: PASS
- `py_compile src\nflverse_advanced_metrics.py`: PASS
- `py_compile src\nflverse_staging.py`: PASS
- `py_compile src\nflverse_backfill.py`: PASS
- `py_compile src\nflverse_backfill_plan.py`: PASS
- `compileall -q src scripts`: PASS
- `unittest tests.test_nflverse_pigskin_packets`: PASS, 15 tests
- `unittest tests.test_nflverse_advanced_metrics`: PASS, 12 tests
- `unittest discover tests`: PASS, 487 tests
- `scripts/run_bigquery_migrations.py --list-pending`: PASS, no pending migrations
- `scripts/run_bigquery_validations.py --dry-run`: PASS, catalog discovered through validation 200

## Packet Source Precheck

2018-2020 feature source rows exist:

| Source | 2018 | 2019 | 2020 |
|---|---:|---:|---:|
| `player_week_advanced_metrics` | 17,393 | 17,341 | 17,581 |
| `team_week_context_metrics` | 534 | 534 | 538 |
| `qb_week_environment_metrics` | 653 | 653 | 682 |

Derived current views:

- `player_recent_advanced_metrics_current`: 4,344 rows
- `player_role_usage_metrics_current`: 4,344 rows

## Packet Target Pre-Write State

Pigskin packet targets remained unchanged before and after the dry-runs:

| Table | Total | 2014 | 2015 | 2016 | 2017 | 2018-2020 New Packet Version |
|---|---:|---:|---:|---:|---:|---:|
| `pigskin_player_context_packet_current` | 1,587 | 482 | 498 | 128 | 479 | 0 |
| `compat_pigskin_player_context_current` | 1,587 | 482 | 498 | 128 | 479 | 0 |

## All-Position Dry Run

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2018 --season-end 2020 --dry-run --limit 25 --strict --packet-version nflverse_pigskin_packet_v0_2018_2020_001 --source-metric-version nflverse_adv_metrics_v0_2018_2020_001 --output-json $env:TEMP\phase29_29_packet_dry_run_all.json
```

Result: read-only, `wrote=false`.

Candidate universe: QB/RB/WR/TE with at least one offensive opportunity or QB environment sample.

Full candidate diagnostics:

| Metric | Count |
|---|---:|
| Candidate rows | 749 |
| Missing source freshness rows | 0 |
| Missing flags rows | 0 |
| Missing identity rows | 0 |
| Missing identity flag rows | 10 |
| Missing QB identity flag rows | 7 |
| Null CPOE rows | 80 |
| Null EPA/opportunity rows | 22 |
| Null snap-share rows | 30 |
| Sample-size warning rows | 47 |
| Non-fantasy position rows | 0 |
| No-opportunity rows | 0 |

Candidate count by season:

| Season | Candidates | Distinct Players |
|---|---:|---:|
| 2018 | 111 | 111 |
| 2019 | 113 | 113 |
| 2020 | 525 | 525 |

Candidate count by position:

| Position | Candidates | Null CPOE | Null EPA/Opp | Null Snap Share | Sample Warnings |
|---|---:|---:|---:|---:|---:|
| QB | 106 | 11 | 22 | 2 | 22 |
| RB | 197 | 60 | 0 | 5 | 0 |
| WR | 278 | 8 | 0 | 19 | 0 |
| TE | 168 | 1 | 0 | 4 | 0 |

Candidate count by position and season:

| Position | 2018 | 2019 | 2020 |
|---|---:|---:|---:|
| QB | 12 | 14 | 80 |
| RB | 33 | 29 | 135 |
| WR | 40 | 44 | 194 |
| TE | 26 | 26 | 116 |

The JSON preview includes packet examples with source freshness, usage summary, efficiency summary, team context, QB context where applicable, blocked metric lists, and warning arrays.

## By-Position Dry Runs

Commands were run for `--position QB`, `--position RB`, `--position WR`, and `--position TE`, each with `--dry-run`, `--limit 25`, `--strict`, the Phase 29.29 packet version, and the Phase 29.28 source metric version.

Results:

- QB: 106 candidates, 22 sample-size warning rows, 11 null CPOE rows, 22 null EPA/opportunity rows, 2 null snap-share rows.
- RB: 197 candidates, 60 null CPOE rows, 5 null snap-share rows.
- WR: 278 candidates, 8 null CPOE rows, 19 null snap-share rows.
- TE: 168 candidates, 1 null CPOE row, 4 null snap-share rows.

Each by-position run wrote nothing and reported the same approved source tables:

- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

## Named-Player Lookup Summary

Full-name lookups were run read-only for the requested examples.

| Query | Result | Packet Name | Position | Team | Season Week | Key Metrics | Warnings |
|---|---|---|---|---|---|---|---|
| Patrick Mahomes | found | `P.Mahomes` | QB | KC | 2020 W21 | dropbacks 52, EPA/dropback -0.271 | missing snap share |
| Lamar Jackson | found | `L.Jackson` | QB | BAL | 2020 W19 | dropbacks 27, EPA/dropback -0.463 | none |
| Josh Allen | ambiguous | `J.Allen` | QB/RB | BUF/NYG | 2020 W20 / 2019 W17 | two candidates | requires team/position/player ID |
| Tom Brady | found | `T.Brady` | QB | TB | 2020 W21 | dropbacks 30, EPA/dropback 0.292 | missing snap share |
| Christian McCaffrey | found | `C.McCaffrey` | RB | CAR | 2020 W9 | weighted opp 43.0, WOPR 0.396 | none |
| Derrick Henry | found | `D.Henry` | RB | TEN | 2020 W18 | weighted opp 25.5, WOPR 0.184 | none |
| Alvin Kamara | found | `A.Kamara` | RB | NO | 2020 W19 | weighted opp 33.0, WOPR 0.305 | none |
| Saquon Barkley | found | `S.Barkley` | RB | NYG | 2020 W2 | weighted opp 4.0, EPA/opp 0.331 | none |
| Davante Adams | found | `D.Adams` | WR | GB | 2020 W20 | targets 15, WOPR 0.640 | none |
| Michael Thomas | found | `M.Thomas` | WR | NO | 2020 W19 | targets 4, WOPR 0.229 | none |
| DeAndre Hopkins | found | `D.Hopkins` | WR | ARI | 2020 W17 | targets 10, WOPR 0.937 | none |
| Tyreek Hill | ambiguous | `T.Hill` | WR/TE | KC/NO | 2020 W21 / 2020 W18 | two candidates | requires team/position/player ID |
| Travis Kelce | found | `T.Kelce` | TE | KC | 2020 W21 | targets 15, WOPR 0.759 | missing snap share |
| George Kittle | found | `G.Kittle` | TE | SF | 2020 W17 | targets 9, WOPR 0.573 | none |

Disambiguation retries:

- `Josh Allen --team BUF --position QB`: one candidate, `J.Allen`, BUF QB, 2020 Week 20.
- `Tyreek Hill --team KC --position WR`: one candidate, `T.Hill`, KC WR, 2020 Week 21.

Full-name lookup prevents silent wrong-player selection by surfacing ambiguous display-name collisions and asking for `--team`, `--position`, or `--player-id`.

## Display-Name Ambiguity Diagnostics

Candidate display-name collisions exist because packet display names are abbreviated.

High-risk examples with multiple player IDs:

| Display Name | Player IDs | Positions | Teams |
|---|---:|---|---|
| `D.Williams` | 3 | RB, WR | BUF, GB, JAX |
| `J.Hill` | 3 | RB, TE | BAL, NE, NO |
| `T.Williams` | 3 | RB, WR | CIN, DAL, LV |
| `A.Brown` | 2 | WR | TB, TEN |
| `A.Jones` | 2 | RB, WR | DET, GB |
| `J.Allen` | 2 | QB, RB | BUF, NYG |
| `K.Allen` | 2 | QB, WR | LAC, WAS |
| `T.Hill` | 2 | TE, WR | KC, NO |

The lookup layer surfaced ambiguity for requested examples `Josh Allen` and `Tyreek Hill`. Disambiguated lookups returned one expected candidate each.

## Packet SQL and Source Isolation

Generated packet SQL reads only approved feature/current objects:

- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

Generated packet SQL did not reference:

- `raw_nflverse_*`
- `stg_*`
- `play_by_play`
- `weekly_metrics`
- `player_rosters`
- `pigskin_player_context_packet_current`
- `compat_pigskin_player_context_current`
- `llm_*`

CLI source dependency warnings also listed raw, legacy, and packet-table dependencies as blocked.

## Blocked Metric Confirmation

Packet JSON examples preserve blocked metrics, including:

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

QB examples also preserve `sack_unavailable` and `scramble_unavailable` flags. Team context examples preserve `pass_rate_over_expected_unavailable`.

## Warehouse Unchanged Confirmation

Read-only counts after all dry-runs:

| Object | Count |
|---|---:|
| `pigskin_player_context_packet_current` | 1,587 |
| `compat_pigskin_player_context_current` | 1,587 |
| `raw_nflverse_schedules` | 1,871 |
| `raw_nflverse_rosters` | 19,805 |
| `raw_nflverse_rosters_weekly` | 294,691 |
| `raw_nflverse_weekly` | 122,495 |
| `raw_nflverse_pbp` | 332,721 |
| `raw_nflverse_snap_counts` | 168,196 |
| `stg_player_identity` | 294,691 |
| `stg_game_context` | 1,871 |
| `stg_player_week_stats` | 122,495 |
| `stg_team_week_stats` | 3,742 |
| `stg_play_player_events` | 812,370 |
| `stg_participation_context` | 168,196 |
| `player_week_advanced_metrics` | 122,495 |
| `team_week_context_metrics` | 3,742 |
| `qb_week_environment_metrics` | 4,513 |
| `player_recent_advanced_metrics_current` | 4,344 |
| `player_role_usage_metrics_current` | 4,344 |
| `trade_player_scores` | 154 |
| `trade_pick_scores` | 64 |

No packet rows were written for `nflverse_pigskin_packet_v0_2018_2020_001`.

## Validation Results

Post-dry-run validation commands:

| Pattern | Result |
|---|---|
| `raw_nflverse` | PASS, 3 passed, 0 failed. Validation 181 returned informational 2014-2020 coverage review rows. |
| `stg_` | PASS, 7 passed, 0 failed. |
| `advanced_metrics` | PASS, 4 passed, 0 failed. |
| `compat_pigskin` | PASS, 2 passed, 0 failed. |
| `trade_player_scores` | PASS, 12 passed, 0 failed. |
| `trade_pick_scores` | PASS, 17 passed, 0 failed. Validation 178 returned the expected informational model-version coverage row. |

## Final Local Checks

Final checks passed:

- `scripts/check_deployment_safety.py`: PASS
- `py_compile src\nflverse_pigskin_packets.py`: PASS
- `py_compile src\nflverse_advanced_metrics.py`: PASS
- `py_compile src\nflverse_staging.py`: PASS
- `py_compile src\nflverse_backfill.py`: PASS
- `py_compile src\nflverse_backfill_plan.py`: PASS
- `compileall -q src scripts`: PASS
- `unittest tests.test_nflverse_pigskin_packets`: PASS, 15 tests
- `unittest tests.test_nflverse_advanced_metrics`: PASS, 12 tests
- `unittest discover tests`: PASS, 487 tests
- `scripts/run_bigquery_migrations.py --list-pending`: PASS, no pending migrations
- `scripts/run_bigquery_validations.py --dry-run`: PASS, catalog discovered through validation 200

## Service State

Read-only Cloud Run describe confirmed no deployment occurred.

Production:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Production risk flags: false
- Trade History compatibility: false
- Trade Analyzer score flags: false
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false

Staging:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Data Ops Cloud Run trigger flags: false
- Data Ops local subprocess flags: false

## Remaining Warnings

- This remains historical 2018-2020 packet dry-run evidence. It is not current-season content.
- Candidate set is heavily weighted toward 2020 because the current derived feature views expose many more 2020 fantasy-position rows than 2018 or 2019.
- Display-name collisions are real. Full-name lookup caught ambiguous cases and disambiguation worked, but packet consumers should keep using player ID, team, or position when selecting by abbreviated display name.
- Missing identity flag rows remain in diagnostics: 10 general identity flag rows and 7 QB identity flag rows.
- Null metric warnings remain expected: CPOE, EPA/opportunity, snap share, and QB sample-size warnings.
- Raw nflverse validation 181 and trade-pick validation 178 remain informational review warnings.

## Recommended Next Phase

Proceed to **Phase 29.30: authorized 2018-2020 Pigskin packet refresh only**, if the operator explicitly authorizes packet writes. Keep the refresh bounded to 2018-2020 and `nflverse_pigskin_packet_v0_2018_2020_001`.
