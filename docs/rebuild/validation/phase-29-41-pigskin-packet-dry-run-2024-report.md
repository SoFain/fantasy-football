# Phase 29.41 - 2024 Pigskin Packet Dry-Run Report

## Final Decision

**2024 PIGSKIN PACKET DRY RUN READY WITH WARNINGS**

The 2024 Pigskin packet selection dry-run is ready for an authorized packet refresh phase. No BigQuery rows were written. No Pigskin packet refresh, raw backfill, staging materialization, advanced metric materialization, 2025/current-season lane, LLM call, Pigskin prompt, deployment, Cloud Run Job trigger, Scheduler job, scrape, or commit occurred.

The main warning is expected: abbreviated display names still collide in the 2024 candidate set. Full-name lookup caught ambiguous cases and team/position disambiguation resolved the two requested examples that collided.

## Authorization Gate State

All checked gates were empty or unset before and after the dry-runs:

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

No write gate was set in this phase.

## Git State

- Latest commit: `e56afa3 Expand nflverse Pigskin packets through 2023`
- No files staged.
- Working tree contains the known historical untracked validation backlog.
- Phase 29 untracked reports now include `phase-29-38`, `phase-29-39`, `phase-29-40`, and this Phase 29.41 report.

## Baseline Checks

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_pigskin_packets.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_advanced_metrics.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_staging.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill_plan.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_pigskin_packets`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_advanced_metrics`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`

Results:

- Safety checker passed.
- `tests.test_nflverse_pigskin_packets`: 15 tests passed.
- `tests.test_nflverse_advanced_metrics`: 12 tests passed.
- Full suite: 487 tests passed.
- No pending migrations.
- Validation catalog discovered through `200`.

## Packet Source Precheck

2024 source feature counts:

| Object | 2024 rows | Week range | Metric version count | 2025+ rows |
|---|---:|---:|---:|---:|
| `player_week_advanced_metrics` | 18,959 | 1-22 | 1 | 0 |
| `team_week_context_metrics` | 570 | 1-22 | 1 | 0 |
| `qb_week_environment_metrics` | 707 | 1-22 | 1 | 0 |

Derived current views:

| Object | Rows |
|---|---:|
| `player_recent_advanced_metrics_current` | 5,883 |
| `player_role_usage_metrics_current` | 5,883 |

Source metric version: `nflverse_adv_metrics_v0_2024_001`.

## Packet Target Pre-Write State

Packet tables before and after dry-run remained unchanged:

| Object | Rows | 2024 rows | 2025+ rows |
|---|---:|---:|---:|
| `pigskin_player_context_packet_current` | 3,082 | 0 | 0 |
| `compat_pigskin_player_context_current` | 3,082 | 0 | 0 |

Existing packet rows by season:

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

Rows for packet version `nflverse_pigskin_packet_v0_2024_001`: 0.

## All-Position Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2024 --season-end 2024 --dry-run --limit 25 --strict --packet-version nflverse_pigskin_packet_v0_2024_001 --source-metric-version nflverse_adv_metrics_v0_2024_001 --output-json %TEMP%\phase29_41_packet_dry_run_all.json
```

Result:

- Exit code: 0.
- `wrote=false`.
- Candidate count: 492.
- Candidate season: 2024 only.
- Candidate week range: 2-22.
- Week 22 candidate count: 19.
- 2025+ candidates: 0.
- Missing source freshness rows: 0.
- Missing flags rows: 0.
- Missing identity rows: 0.
- Missing identity flag rows: 0.
- Missing QB identity flag rows: 5.
- Null CPOE rows: 51.
- Null EPA/opportunity rows: 15.
- Null snap share rows: 0.
- Sample-size warning rows: 15.

Candidate count by position:

| Position | Candidate count | Null CPOE | Null EPA/opportunity | Sample-size warnings |
|---|---:|---:|---:|---:|
| QB | 79 | 8 | 15 | 15 |
| RB | 123 | 39 | 0 | 0 |
| WR | 185 | 4 | 0 | 0 |
| TE | 105 | 0 | 0 | 0 |

All-position sample packets returned:

- `J.Allen`, QB, BUF, Week 21.
- `J.Hurts`, QB, PHI, Week 22.
- `J.Milton`, QB, NE, Week 18.
- `A.Richardson`, QB, IND, Week 16.
- `B.Mayfield`, QB, TB, Week 19.
- `J.Daniels`, QB, WAS, Week 21.

The packet universe is QB/RB/WR/TE only and requires targets, carries, weighted opportunity, dropbacks, or pass attempts.

## By-Position Dry-Run Summary

Each command exited 0 and wrote no rows.

| Position | JSON output | Candidate count | Example players |
|---|---|---:|---|
| QB | `%TEMP%\phase29_41_packet_dry_run_qb.json` | 79 | `J.Allen`, `J.Hurts`, `J.Milton`, `A.Richardson`, `J.Daniels` |
| RB | `%TEMP%\phase29_41_packet_dry_run_rb.json` | 123 | `S.Barkley`, `J.Gibbs`, `B.Robinson`, `J.Taylor`, `C.Hubbard` |
| WR | `%TEMP%\phase29_41_packet_dry_run_wr.json` | 185 | `D.London`, `J.Chase`, `L.McConkey`, `P.Nacua`, `D.Adams` |
| TE | `%TEMP%\phase29_41_packet_dry_run_te.json` | 105 | `Z.Ertz`, `J.Smith`, `T.McBride`, `B.Bowers`, `T.Kelce` |

By-position diagnostics showed no missing source freshness, no missing flags, no null WOPR rows, and no null snap-share rows.

## Named-Player Lookup Summary

All requested named-player commands exited 0 and wrote no rows. Full-name lookup found all names. Two full-name lookups returned more than one candidate and produced ambiguity warnings.

| Lookup | Result | Packet | Team | Week | Key metric snapshot |
|---|---|---|---|---:|---|
| Patrick Mahomes | Found | `P.Mahomes` QB | KC | 22 | weighted opportunity 4.0, EPA/dropback -0.3474 |
| Josh Allen | Found | `J.Allen` QB | BUF | 21 | weighted opportunity 11.0, EPA/dropback 0.1968 |
| Jalen Hurts | Found | `J.Hurts` QB | PHI | 22 | weighted opportunity 11.0, EPA/dropback 0.5865 |
| Lamar Jackson | Found | `L.Jackson` QB | BAL | 20 | weighted opportunity 6.0, EPA/dropback -0.0238 |
| Joe Burrow | Found | `J.Burrow` QB | CIN | 18 | weighted opportunity 1.0, EPA/dropback -0.0285 |
| C.J. Stroud | Found | `C.Stroud` QB | HOU | 20 | weighted opportunity 6.0, EPA/dropback 0.0270 |
| Jayden Daniels | Found | `J.Daniels` QB | WAS | 21 | weighted opportunity 6.0, EPA/dropback -0.1859 |
| Caleb Williams | Found | `C.Williams` QB | CHI | 18 | weighted opportunity 3.0, EPA/dropback 0.0340 |
| Justin Jefferson | Ambiguous | first candidate `J.Jefferson` RB | DET | 17 | warning required disambiguation |
| Justin Jefferson, `--team MIN --position WR` | Found | `J.Jefferson` WR | MIN | 19 | weighted opportunity 20.0, WOPR 0.5410 |
| Ja'Marr Chase | Found | `J.Chase` WR | CIN | 18 | weighted opportunity 35.0, WOPR 0.7787 |
| Tyreek Hill | Ambiguous | first candidate `T.Hill` WR | MIA | 18 | warning required disambiguation |
| Tyreek Hill, `--team MIA --position WR` | Found | `T.Hill` WR | MIA | 18 | weighted opportunity 7.5, WOPR 0.2166 |
| Davante Adams | Found | `D.Adams` WR | NYJ | 18 | weighted opportunity 30.0, WOPR 0.8493 |
| A.J. Brown | Found | `A.Brown` WR | PHI | 22 | weighted opportunity 12.5, WOPR 0.5997 |
| CeeDee Lamb | Found | `C.Lamb` WR | DAL | 16 | weighted opportunity 20.0, WOPR 0.6315 |
| Malik Nabers | Found | `M.Nabers` WR | NYG | 18 | weighted opportunity 20.0, WOPR 0.7852 |
| Puka Nacua | Found | `P.Nacua` WR | LA | 20 | weighted opportunity 35.0, WOPR 0.7475 |
| Christian McCaffrey | Found | `C.McCaffrey` RB | SF | 13 | weighted opportunity 14.5, WOPR 0.2647 |
| Derrick Henry | Found | `D.Henry` RB | BAL | 20 | weighted opportunity 21.0, WOPR 0.1542 |
| Saquon Barkley | Found | `S.Barkley` RB | PHI | 22 | weighted opportunity 42.5, WOPR 0.4565 |
| Jahmyr Gibbs | Found | `J.Gibbs` RB | DET | 20 | weighted opportunity 41.5, WOPR 0.5268 |
| Travis Kelce | Found | `T.Kelce` TE | KC | 22 | weighted opportunity 15.0, WOPR 0.3539 |
| Mark Andrews | Found | `M.Andrews` TE | BAL | 20 | weighted opportunity 19.5, WOPR 0.5477 |
| George Kittle | Found | `G.Kittle` TE | SF | 18 | weighted opportunity 7.5, WOPR 0.1824 |
| Sam LaPorta | Found | `S.LaPorta` TE | DET | 20 | weighted opportunity 17.5, WOPR 0.3271 |
| Brock Bowers | Found | `B.Bowers` TE | LV | 18 | weighted opportunity 22.5, WOPR 0.6251 |

Every named-player packet included 11 blocked metric labels in the preview JSON.

## Display-Name Ambiguity Diagnostics

The 2024 candidate set contains 16 abbreviated display names with more than one player ID, team, or position:

| Display name | Player IDs | Teams | Positions |
|---|---:|---|---|
| `B.Allen` | 2 | NYJ, SF | QB, RB |
| `B.Robinson` | 2 | ATL, WAS | RB |
| `D.Johnson` | 2 | HOU, JAX | RB, WR |
| `D.Moore` | 2 | CAR, CHI | WR |
| `J.Brooks` | 2 | CAR, DAL | RB, WR |
| `J.Hill` | 2 | BAL, MIA | RB, TE |
| `J.Jefferson` | 2 | DET, MIN | RB, WR |
| `J.Johnson` | 2 | BAL, NO | QB, TE |
| `J.Ross` | 2 | KC, PHI | WR |
| `J.Taylor` | 2 | HOU, IND | RB |
| `J.Wilson` | 2 | MIA, PHI | RB, WR |
| `Ja.Williams` | 2 | DET, NO | RB, WR |
| `K.Allen` | 2 | CHI, PIT | QB, WR |
| `T.Hill` | 2 | MIA, NO | TE, WR |
| `T.Johnson` | 2 | LA, NYG | TE, WR |
| `T.Taylor` | 2 | NYJ, SF | QB, WR |

Full-name lookup prevented silent wrong-player selection by warning on ambiguous requested names. `--team` and `--position` resolved Justin Jefferson and Tyreek Hill correctly.

Remaining warning: abbreviated packet display names are still collision-prone, so production-facing lookup or review flows should keep requiring full name plus team, position, or player ID for ambiguous cases.

## Packet SQL And Source Isolation

The dry-run SQL reads only:

- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

The dry-run SQL did not reference:

- `raw_nflverse_*`
- `stg_*`
- `play_by_play`
- `weekly_metrics`
- `player_rosters`
- `pigskin_player_context_packet_current`
- `compat_pigskin_player_context_current`
- LLM output tables
- content brief tables

Source isolation result: pass.

## Blocked Metric Confirmation

Dry-run packet JSON preserved these blocked metric labels:

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

The packet previews did not fabricate those metrics.

## 2024 Week 22 And Current-Season Separation

The dry-run candidate set includes postseason Week 22:

- Candidate week range: 2-22.
- Week 22 candidates: 19.
- 2025+ candidates: 0.

Week 22 rows are historical 2024 context only. No current-season lane was run, and no 2025 rows were included.

## Warehouse Unchanged Confirmation

Post dry-run read-only checks:

| Object | Rows | 2024 rows | 2025+ rows |
|---|---:|---:|---:|
| `pigskin_player_context_packet_current` | 3,082 | 0 | 0 |
| `compat_pigskin_player_context_current` | 3,082 | 0 | 0 |
| `player_week_advanced_metrics` | 197,831 | 18,959 | 0 |
| `team_week_context_metrics` | 6,020 | 570 | 0 |
| `qb_week_environment_metrics` | 7,350 | 707 | 0 |

Raw and staging counts remained unchanged from the 2024 Phase 29.38 and Phase 29.39 snapshots. Score tables remained unchanged:

- `trade_player_scores`: 154.
- `trade_player_scores_current`: 77.
- `compat_trade_player_scores_current`: 77.
- `trade_pick_scores`: 64.
- `trade_pick_scores_current`: 64.
- `compat_trade_pick_scores_current`: 64.

## Validation Results

Post dry-run validation commands:

- `raw_nflverse`: 3 passed, 0 failed. Warning: informational season-week coverage review returned 3 rows.
- `stg_`: 7 passed, 0 failed.
- `advanced_metrics`: 4 passed, 0 failed.
- `compat_pigskin`: 2 passed, 0 failed.
- `trade_player_scores`: 12 passed, 0 failed.
- `trade_pick_scores`: 17 passed, 0 failed. Warning: informational model-version coverage returned 1 row.

## Final Local Checks

Passed:

- Safety checker.
- Targeted py_compile checks.
- `compileall -q src scripts`.
- `tests.test_nflverse_pigskin_packets`: 15 tests.
- `tests.test_nflverse_advanced_metrics`: 12 tests.
- Full test suite: 487 tests.
- Migrations list: no pending migrations.
- Validation dry-run: catalog discovered through `200`.

## Staging And Production Untouched

Read-only Cloud Run checks:

| Service | Revision | Traffic | Image digest |
|---|---|---:|---|
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100% | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100% | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` |

Production remains all risk flags off. Staging remains on its existing score-enabled test configuration. Data Ops job trigger flags and local subprocess flags are false on both services.

## Remaining Warnings

- This is a 2024 historical packet dry-run. Do not present it as current-season content.
- 2024 is postseason-inclusive through Week 22.
- Abbreviated display names collide in 16 cases and should stay disambiguated by full name plus team, position, or player ID.
- Five QB rows carry the known missing QB identity flag.
- Fifteen rows carry sample-size warnings.
- `null_cpoe_rows` is 51 across candidates, mostly non-QB context.
- Route, pressure, scramble/sack, pass rate over expected, red-zone, and high-value touch metrics remain blocked or unavailable by design.
- Raw nflverse and trade pick score validation warnings are informational review outputs.

## Recommended Next Phase

Proceed to **Phase 29.42 - authorized 2024 Pigskin packet refresh only**, if the owner accepts the display-name ambiguity warnings and historical Week 22 shape. The next phase should set `ALLOW_PIGSKIN_PACKET_REFRESH=true` only inside the one authorized packet refresh wrapper and should not run raw, staging, or advanced metric materialization again.
