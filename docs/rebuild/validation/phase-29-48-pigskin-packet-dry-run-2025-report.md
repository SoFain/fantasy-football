# Phase 29.48 Pigskin Packet Dry-Run 2025 Report

Final decision: **2025 PIGSKIN PACKET DRY RUN READY WITH WARNINGS**

## Scope

Owner correction accepted: the Phase 29.44 current-season lane recommendation remains superseded for this task. Season 2025 is treated as a completed historical season for the Phase 29 completed-season historical lane.

This phase performed read-only Pigskin packet selection dry-runs from the 2025 advanced metrics materialized in Phase 29.47.

No Pigskin packet rows were written. No raw backfill, staging materialization, advanced metrics materialization, packet refresh, Pigskin prompt, LLM call, ranking build, deployment, feature flag change, Cloud Run Job, Scheduler job, scrape, Firebase artifact, or commit was run.

Packet dry-run version: `nflverse_pigskin_packet_v0_2025_001`.

Source metric version: `nflverse_adv_metrics_v0_2025_001`.

All BigQuery checks used neutral aliases. No query in this phase used `rows` as a BigQuery table alias.

## Authorization Gate State

All gates were empty or unset before and after the phase:

| Gate | State |
|---|---|
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

No authorization gate was set during this dry-run phase.

## Git State

Latest commit at start:

```text
3c83af6 Expand nflverse Pigskin packets through 2024
```

No files were staged. The working tree contained the known untracked validation backlog plus recent Phase 29 reports, including:

- `docs/rebuild/validation/phase-29-45-raw-backfill-2025-report.md`
- `docs/rebuild/validation/phase-29-46-staging-materialization-2025-report.md`
- `docs/rebuild/validation/phase-29-47-advanced-metrics-2025-report.md`

This phase adds only this untracked Phase 29.48 report.

## Baseline Checks

All baseline checks passed before packet dry-runs:

| Check | Result |
|---|---|
| `scripts/check_deployment_safety.py` | pass |
| `py_compile src\nflverse_pigskin_packets.py` | pass |
| `py_compile src\nflverse_advanced_metrics.py` | pass |
| `py_compile src\nflverse_staging.py` | pass |
| `py_compile src\nflverse_backfill.py` | pass |
| `py_compile src\nflverse_backfill_plan.py` | pass |
| `compileall -q src scripts` | pass |
| `unittest tests.test_nflverse_pigskin_packets` | pass, 15 tests |
| `unittest tests.test_nflverse_advanced_metrics` | pass, 12 tests |
| `unittest discover tests` | pass, 487 tests |
| `scripts/run_bigquery_migrations.py --list-pending` | no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | catalog discovered through 200 |

## Packet Source Precheck

Read-only source checks confirmed 2025 base advanced metrics are present and 2026+ rows are absent.

| Table | Total rows | 2025 rows | 2026+ rows | Season range | 2025 week range | 2025 metric-version rows |
|---|---:|---:|---:|---|---|---:|
| `player_week_advanced_metrics` | 217,230 | 19,399 | 0 | 2014-2025 | 1-22 | 19,399 |
| `team_week_context_metrics` | 6,590 | 570 | 0 | 2014-2025 | 1-22 | 570 |
| `qb_week_environment_metrics` | 8,042 | 692 | 0 | 2014-2025 | 1-22 | 692 |

Derived current views after Phase 29.47:

| Object | Row count |
|---|---:|
| `player_recent_advanced_metrics_current` | 6,269 |
| `player_role_usage_metrics_current` | 6,269 |

## Packet Target Pre-Write State

Packet target objects remained at the expected pre-refresh counts.

| Object | Total rows | 2025 rows | 2025 packet-version rows | 2026+ rows |
|---|---:|---:|---:|---:|
| `pigskin_player_context_packet_current` | 3,574 | 0 | 0 | 0 |
| `compat_pigskin_player_context_current` | 3,574 | 0 | 0 | 0 |

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
| 2024 | 492 |

## All-Position Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2025 --season-end 2025 --dry-run --limit 25 --strict --packet-version nflverse_pigskin_packet_v0_2025_001 --source-metric-version nflverse_adv_metrics_v0_2025_001 --output-json %TEMP%\phase29_48_packet_dry_run_all.json
```

Result: pass, read-only, `dry_run=true`, `wrote=false`.

| Metric | Count |
|---|---:|
| Total candidates | 510 |
| QB candidates | 81 |
| RB candidates | 126 |
| WR candidates | 186 |
| TE candidates | 117 |
| Week range | 1-22 |
| Week 22 candidates | 17 |
| 2026+ candidates | 0 |
| Non-QB/RB/WR/TE candidates | 0 |
| No-opportunity candidates | 0 |
| Missing identity rows | 0 |
| Missing source freshness rows | 0 |
| Missing flags rows | 0 |
| Null snap-share rows | 3 |
| Null EPA/opportunity rows | 15 |
| Null CPOE rows | 48 |
| Sample-size warning rows | 15 |
| Missing identity flag rows | 0 |
| Missing QB identity flag rows | 3 |
| Packet warning rows | 22 |
| Blocked metric flags in packet plan | 11 |

Packet examples were generated. The first examples were `J.Fields`, `B.Nix`, `J.Allen`, `J.Herbert`, and `T.Lance`, all from 2025 quarterback contexts.

## By-Position Dry-Run Summary

Commands were run for `QB`, `RB`, `WR`, and `TE` with the same season, version, limit, and strict settings.

| Position | Candidates | Week range | Week 22 candidates | 2026+ candidates | Missing identity flag rows | Missing QB identity flag rows | Sample-size warnings | Null snap share | Null CPOE | Example players |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| QB | 81 | 3-22 | 2 | 0 | 0 | 0 | 15 | 1 | 8 | `J.Fields`, `B.Nix`, `J.Allen`, `J.Herbert`, `T.Lance` |
| RB | 126 | 1-22 | 4 | 0 | 0 | 2 | 0 | 1 | 36 | `S.Barkley`, `T.Tracy`, `A.Jeanty`, `K.Walker`, `A.Estime` |
| WR | 186 | 4-22 | 8 | 0 | 0 | 1 | 0 | 1 | 4 | `A.St. Brown`, `P.Nacua`, `T.Hunter`, `W.Robinson`, `X.Hutchinson` |
| TE | 117 | 3-22 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | `C.Loveland`, `C.Otton`, `K.Pitts`, `M.Taylor`, `T.McBride` |

The packet universe filter worked as intended: QB/RB/WR/TE only, with at least one target, carry, weighted opportunity, dropback, or pass attempt.

## Named-Player Lookup Summary

All requested full-name lookups found at least one candidate. `Tyreek Hill` was ambiguous as a full-name lookup because the normalized abbreviated display name matched two `T.Hill` candidates. A follow-up lookup with `--team MIA --position WR` resolved to a single MIA WR candidate.

| Requested name | Found | Candidates | Packet name | Pos | Team | Week | Key metrics | Warnings |
|---|---|---:|---|---|---|---:|---|---|
| Patrick Mahomes | yes | 1 | `P.Mahomes` | QB | KC | 15 | wo=2.0, wopr=0.000, epa/op=-0.610, epa/db=-0.108 | none |
| Josh Allen | yes | 1 | `J.Allen` | QB | BUF | 20 | wo=12.0, wopr=0.000, epa/op=0.928, epa/db=0.118 | none |
| Jalen Hurts | yes | 1 | `J.Hurts` | QB | PHI | 19 | wo=5.0, wopr=0.000, epa/op=-0.187, epa/db=-0.090 | none |
| Lamar Jackson | yes | 1 | `L.Jackson` | QB | BAL | 18 | wo=4.0, wopr=0.000, epa/op=2.199, epa/db=0.414 | none |
| Joe Burrow | yes | 1 | `J.Burrow` | QB | CIN | 18 | wo=2.0, wopr=0.000, epa/op=-5.390, epa/db=-0.297 | none |
| C.J. Stroud | yes | 1 | `C.Stroud` | QB | HOU | 20 | wo=2.0, wopr=0.000, epa/op=-11.177, epa/db=-0.470 | none |
| Jayden Daniels | yes | 1 | `J.Daniels` | QB | WAS | 14 | wo=4.0, wopr=0.000, epa/op=-2.979, epa/db=-0.536 | none |
| Caleb Williams | yes | 1 | `C.Williams` | QB | CHI | 20 | wo=5.0, wopr=0.000, epa/op=1.586, epa/db=0.039 | none |
| Justin Jefferson | yes | 1 | `J.Jefferson` | WR | MIN | 18 | wo=28.5, wopr=0.794, epa/op=0.364 | none |
| Ja'Marr Chase | yes | 1 | `J.Chase` | WR | CIN | 18 | wo=25.0, wopr=0.697, epa/op=0.787 | none |
| Tyreek Hill | yes | 2 | `T.Hill` | WR | MIA | 4 | wo=15.0, wopr=0.564, epa/op=1.208 | full-name lookup ambiguous, disambiguated with MIA WR |
| Davante Adams | yes | 1 | `D.Adams` | WR | LA | 21 | wo=15.0, wopr=0.426, epa/op=1.129 | none |
| A.J. Brown | yes | 1 | `A.Brown` | WR | PHI | 19 | wo=17.5, wopr=0.606, epa/op=-0.219 | none |
| CeeDee Lamb | yes | 1 | `C.Lamb` | WR | DAL | 18 | wo=2.5, wopr=0.081, epa/op=0.359 | none |
| Jaxon Smith-Njigba | yes | 1 | `J.Smith-Njigba` | WR | SEA | 22 | wo=25.0, wopr=0.622, epa/op=-0.505 | none |
| Drake London | yes | 1 | `D.London` | WR | ATL | 18 | wo=20.0, wopr=0.755, epa/op=0.562 | none |
| Malik Nabers | yes | 1 | `M.Nabers` | WR | NYG | 4 | wo=7.5, wopr=0.363, epa/op=0.215 | none |
| Puka Nacua | yes | 1 | `P.Nacua` | WR | LA | 21 | wo=36.0, wopr=0.955, epa/op=0.555 | none |
| Christian McCaffrey | yes | 1 | `C.McCaffrey` | RB | SF | 20 | wo=26.0, wopr=0.356, epa/op=-0.037 | none |
| Derrick Henry | yes | 1 | `D.Henry` | RB | BAL | 18 | wo=22.5, wopr=0.088, epa/op=0.011 | none |
| Saquon Barkley | yes | 1 | `S.Barkley` | RB | PHI | 19 | wo=41.0, wopr=0.267, epa/op=-0.174 | none |
| Jahmyr Gibbs | yes | 1 | `J.Gibbs` | RB | DET | 18 | wo=31.5, wopr=0.211, epa/op=0.098 | none |
| Travis Kelce | yes | 1 | `T.Kelce` | TE | KC | 18 | wo=15.0, wopr=0.451, epa/op=-0.029 | none |
| Mark Andrews | yes | 1 | `M.Andrews` | TE | BAL | 18 | wo=7.5, wopr=0.312, epa/op=-0.336 | none |
| George Kittle | yes | 1 | `G.Kittle` | TE | SF | 19 | wo=5.0, wopr=0.142, epa/op=-0.236 | none |
| Sam LaPorta | yes | 1 | `S.LaPorta` | TE | DET | 10 | wo=12.5, wopr=0.311, epa/op=1.150 | none |
| Brock Bowers | yes | 1 | `B.Bowers` | TE | LV | 16 | wo=12.5, wopr=0.407, epa/op=0.846 | none |

## Display-Name Ambiguity Diagnostics

The 2025 dry-run candidate set contains 13 abbreviated display names with more than one player ID, team, or position. Full-name lookup avoided wrong-player selection for all requested examples except the expected `Tyreek Hill` collision, which resolved with team and position disambiguation.

Prior 2014-2024 candidate collision count with the same diagnostic query was 0. The following collisions are new to the 2025 candidate set:

| Display name | Player IDs | Teams | Positions | Candidate rows | Player IDs list | Teams list | Positions list |
|---|---:|---:|---:|---:|---|---|---|
| `J.Williams` | 3 | 3 | 2 | 3 | `00-0036997, 00-0037240, 00-0040429` | DAL, DET, TB | RB, WR |
| `K.Williams` | 3 | 3 | 2 | 3 | `00-0037840, 00-0040131, 00-0040534` | CIN, LA, NE | RB, WR |
| `T.Johnson` | 3 | 3 | 2 | 3 | `00-0036427, 00-0039847, 00-0040237` | NYG, NYJ, TB | TE, WR |
| `B.Allen` | 2 | 2 | 2 | 2 | `00-0032434, 00-0039794` | NYJ, TEN | QB, RB |
| `J.Johnson` | 2 | 2 | 2 | 2 | `00-0026300, 00-0036040` | NO, WAS | QB, TE |
| `K.Allen` | 2 | 2 | 2 | 2 | `00-0030279, 00-0034577` | DET, LAC | QB, WR |
| `M.Evans` | 2 | 2 | 2 | 2 | `00-0031408, 00-0040187` | CAR, TB | TE, WR |
| `R.Wilson` | 2 | 2 | 2 | 2 | `00-0029263, 00-0039739` | NYG, PIT | QB, WR |
| `T.Hill` | 2 | 2 | 2 | 2 | `00-0033040, 00-0033357` | MIA, NO | TE, WR |
| `B.Robinson` | 2 | 2 | 1 | 2 | `00-0037746, 00-0038542` | ATL, SF | RB |
| `D.Moore` | 2 | 2 | 1 | 2 | `00-0033589, 00-0034827` | CAR, CHI | WR |
| `J.Wright` | 2 | 2 | 1 | 2 | `00-0039874, 00-0040067` | MIA, SEA | RB |
| `T.Etienne` | 2 | 2 | 1 | 2 | `00-0036973, 00-0040644` | CAR, JAX | RB |

Recommendation for the authorized refresh phase: keep full-name lookup first, and require `--team`, `--position`, or `--player-id` for abbreviated display names that collide.

## Packet SQL And Source Isolation

`src.nflverse_pigskin_packets` built packet SQL using only approved feature/current objects:

- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

Blocked dependencies were absent from the dry-run SQL:

- `raw_nflverse_*`
- `stg_*`
- `play_by_play`
- `weekly_metrics`
- `player_rosters`
- `pigskin_player_context_packet_current`
- `compat_pigskin_player_context_current`
- LLM output tables
- content brief tables

The dry-run source isolation check found no blocked dependency hits.

## Blocked Metric Confirmation

The packet plan carried 11 blocked metric flags:

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

Known v0 gaps remained preserved:

- Route metrics remained blocked.
- Pressure, sack, and scramble metrics remained blocked or unavailable.
- Pass rate over expected remained null.
- Red-zone and high-value-touch metrics remained blocked.

## 2025 Week 22 Behavior

The dry-run included 17 Week 22 candidates from completed-season historical/postseason context:

| Position | Week 22 candidates |
|---|---:|
| QB | 2 |
| RB | 4 |
| WR | 8 |
| TE | 3 |

No current-season scrape, weekly refresh, or 2026+ path was involved.

## 2026+ Separation

The dry-run candidate set had 0 rows for 2026 or later. The three base feature targets also had 0 rows for 2026 or later.

## Warehouse Unchanged Confirmation

Read-only checks after the dry-runs confirmed warehouse counts were unchanged:

| Object | Row count or state |
|---|---:|
| `pigskin_player_context_packet_current` | 3,574 total, 0 rows for 2025 |
| `compat_pigskin_player_context_current` | 3,574 total, 0 rows for 2025 |
| `player_week_advanced_metrics` | 217,230 total, 19,399 rows for 2025 |
| `team_week_context_metrics` | 6,590 total, 570 rows for 2025 |
| `qb_week_environment_metrics` | 8,042 total, 692 rows for 2025 |
| `trade_player_scores` | 154 |
| `trade_player_scores_current` | 77 |
| `compat_trade_player_scores_current` | 77 |
| `trade_pick_scores` | 64 |
| `trade_pick_scores_current` | 64 |
| `compat_trade_pick_scores_current` | 64 |

Raw and staging counts remained consistent with Phase 29.45 and Phase 29.46.

## Validation Results

Post-dry-run validations:

| Pattern | Result |
|---|---|
| `raw_nflverse` | pass, 3 passed, 0 failed, informational coverage warning |
| `stg_` | pass, 7 passed, 0 failed |
| `advanced_metrics` | pass, 4 passed, 0 failed |
| `compat_pigskin` | pass, 2 passed, 0 failed |
| `trade_player_scores` | pass, 12 passed, 0 failed |
| `trade_pick_scores` | pass, 17 passed, 0 failed, existing informational model-version warning |

## Final Local Checks

All final local checks passed:

| Check | Result |
|---|---|
| `scripts/check_deployment_safety.py` | pass |
| `py_compile src\nflverse_pigskin_packets.py` | pass |
| `py_compile src\nflverse_advanced_metrics.py` | pass |
| `py_compile src\nflverse_staging.py` | pass |
| `py_compile src\nflverse_backfill.py` | pass |
| `py_compile src\nflverse_backfill_plan.py` | pass |
| `compileall -q src scripts` | pass |
| `unittest tests.test_nflverse_pigskin_packets` | pass, 15 tests |
| `unittest tests.test_nflverse_advanced_metrics` | pass, 12 tests |
| `unittest discover tests` | pass, 487 tests |
| `scripts/run_bigquery_migrations.py --list-pending` | no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | catalog discovered through 200 |

## Staging And Production Untouched

Production was inspected read-only:

| Field | Value |
|---|---|
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00077-2jp` |
| Traffic | `nfl-studio-dashboard-00077-2jp:100` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |

Production risk, score, Trade History, Data Ops Cloud Run trigger, and Data Ops local subprocess flags remained false.

Staging was inspected read-only:

| Field | Value |
|---|---|
| Service | `nfl-studio-dashboard-staging` |
| Revision | `nfl-studio-dashboard-staging-00029-jtb` |
| Traffic | `nfl-studio-dashboard-staging-00029-jtb:100` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |

No deployment occurred.

## Remaining Warnings

- 22 packet candidates have packet warnings. They are primarily sample-size, null snap-share, or missing QB environment sample warnings.
- 13 abbreviated display names collide across player IDs, teams, or positions in the 2025 candidate set.
- `Tyreek Hill` full-name lookup needs team/position disambiguation because `T.Hill` also matches another 2025 candidate.
- Route, pressure, sack, scramble, pass-rate-over-expected, red-zone, and high-value-touch metrics remain blocked or unavailable in v0.
- `raw_nflverse` validation retains an informational coverage-review warning.
- `trade_pick_scores` validation retains the existing informational model-version warning.

## Recommended Next Phase

Proceed to **Phase 29.49: authorized 2025 Pigskin packet refresh only**.

Use the same packet and source metric versions, keep the refresh bounded to season 2025, preserve the QB/RB/WR/TE opportunity filter, and keep display-name disambiguation warnings visible in the report. Do not combine the refresh with raw, staging, or advanced metrics reruns.
