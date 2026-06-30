# Phase 29.49 Pigskin Packets 2025 Report

Final decision: **2025 PIGSKIN PACKETS MATERIALIZED WITH WARNINGS**

## Scope

Owner correction accepted: the Phase 29.44 current-season lane recommendation remains superseded for this task. Season 2025 is treated as a completed historical season for the Phase 29 completed-season historical lane.

This phase materialized only 2025 Pigskin evidence packets into:

- `pigskin_player_context_packet_current`

Packet version: `nflverse_pigskin_packet_v0_2025_001`.

Source metric version: `nflverse_adv_metrics_v0_2025_001`.

No raw backfill, staging materialization, advanced metrics materialization, 2026+ write, Pigskin prompt, LLM call, ranking build, deployment, feature flag change, Cloud Run Job, Scheduler job, scrape, Firebase artifact, or commit was run.

All BigQuery checks used neutral aliases. No query in this phase used `rows` as a BigQuery table alias.

## Authorization Gate

Pre-run gates were empty or unset:

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

The packet write gate was set only inside the same PowerShell wrapper around the single live command:

```powershell
try {
  $env:ALLOW_PIGSKIN_PACKET_REFRESH = "true"

  echo "ALLOW_PIGSKIN_PACKET_REFRESH=$env:ALLOW_PIGSKIN_PACKET_REFRESH"

  .\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2025 --season-end 2025 --write --strict --packet-version nflverse_pigskin_packet_v0_2025_001 --source-metric-version nflverse_adv_metrics_v0_2025_001 --output-json %TEMP%\phase29_49_packet_write.json

} finally {
  Remove-Item Env:\ALLOW_PIGSKIN_PACKET_REFRESH -ErrorAction SilentlyContinue
}
```

The command printed `ALLOW_PIGSKIN_PACKET_REFRESH=true` inside the wrapper. Post-wrapper checks confirmed the gate was removed. No other write, materialization, deploy, or local subprocess gate was set.

## Git State

Latest commit at start:

```text
3c83af6 Expand nflverse Pigskin packets through 2024
```

No files were staged. The working tree contained the known untracked validation backlog plus recent Phase 29 reports, including Phase 29.45 through Phase 29.48.

## Baseline Checks

All baseline checks passed before the packet write:

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

Read-only checks confirmed the 2025 source metrics existed before the packet write:

| Table | Total rows | 2025 rows | 2026+ rows | 2025 week range | 2025 metric-version rows |
|---|---:|---:|---:|---|---:|
| `player_week_advanced_metrics` | 217,230 | 19,399 | 0 | 1-22 | 19,399 |
| `team_week_context_metrics` | 6,590 | 570 | 0 | 1-22 | 570 |
| `qb_week_environment_metrics` | 8,042 | 692 | 0 | 1-22 | 692 |

Derived current views were already updated by Phase 29.47:

| Object | Row count |
|---|---:|
| `player_recent_advanced_metrics_current` | 6,269 |
| `player_role_usage_metrics_current` | 6,269 |

## Packet Target Pre-Write State

Pre-write packet counts were unchanged from Phase 29.48:

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

## Final All-Position Dry-Run

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2025 --season-end 2025 --dry-run --limit 25 --strict --packet-version nflverse_pigskin_packet_v0_2025_001 --source-metric-version nflverse_adv_metrics_v0_2025_001 --output-json %TEMP%\phase29_49_packet_dry_run_all.json
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

## Final By-Position Dry-Runs

| Position | Candidates | Week range | Week 22 candidates | Missing identity rows | Missing QB identity flag rows | Sample-size warnings | Null CPOE | Null snap share | Example players |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| QB | 81 | 3-22 | 2 | 0 | 0 | 15 | 8 | 1 | `J.Fields`, `B.Nix`, `J.Allen`, `J.Herbert`, `T.Lance` |
| RB | 126 | 1-22 | 4 | 0 | 2 | 0 | 36 | 1 | `S.Barkley`, `T.Tracy`, `A.Jeanty`, `K.Walker`, `A.Estime` |
| WR | 186 | 4-22 | 8 | 0 | 1 | 0 | 4 | 1 | `A.St. Brown`, `P.Nacua`, `T.Hunter`, `W.Robinson`, `X.Hutchinson` |
| TE | 117 | 3-22 | 3 | 0 | 0 | 0 | 0 | 0 | `C.Loveland`, `C.Otton`, `K.Pitts`, `M.Taylor`, `T.McBride` |

## Named-Player Dry-Run Summary

All requested named-player dry-run lookups found candidates before the write. `Tyreek Hill` was ambiguous because compact packet display names include two `T.Hill` candidates; `--team MIA --position WR` resolved the intended candidate.

All named-player dry-run packets carried the same blocked metric list in packet JSON:

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

| Requested name | Found | Ambiguous | Candidates | Packet name | Pos | Team | Week | Key metrics | Warnings |
|---|---|---|---:|---|---|---|---:|---|---|
| Patrick Mahomes | yes | no | 1 | `P.Mahomes` | QB | KC | 15 | wo=2.0, epa/db=-0.108 | none |
| Josh Allen | yes | no | 1 | `J.Allen` | QB | BUF | 20 | wo=12.0, epa/db=0.118 | none |
| Jalen Hurts | yes | no | 1 | `J.Hurts` | QB | PHI | 19 | wo=5.0, epa/db=-0.090 | none |
| Lamar Jackson | yes | no | 1 | `L.Jackson` | QB | BAL | 18 | wo=4.0, epa/db=0.414 | none |
| Joe Burrow | yes | no | 1 | `J.Burrow` | QB | CIN | 18 | wo=2.0, epa/db=-0.297 | none |
| C.J. Stroud | yes | no | 1 | `C.Stroud` | QB | HOU | 20 | wo=2.0, epa/db=-0.470 | none |
| Jayden Daniels | yes | no | 1 | `J.Daniels` | QB | WAS | 14 | wo=4.0, epa/db=-0.536 | none |
| Caleb Williams | yes | no | 1 | `C.Williams` | QB | CHI | 20 | wo=5.0, epa/db=0.039 | none |
| Justin Jefferson | yes | no | 1 | `J.Jefferson` | WR | MIN | 18 | wo=28.5, wopr=0.794 | none |
| Ja'Marr Chase | yes | no | 1 | `J.Chase` | WR | CIN | 18 | wo=25.0, wopr=0.697 | none |
| Tyreek Hill | yes | yes | 2 | `T.Hill` | WR | MIA | 4 | wo=15.0, wopr=0.564 | disambiguate |
| Davante Adams | yes | no | 1 | `D.Adams` | WR | LA | 21 | wo=15.0, wopr=0.426 | none |
| A.J. Brown | yes | no | 1 | `A.Brown` | WR | PHI | 19 | wo=17.5, wopr=0.606 | none |
| CeeDee Lamb | yes | no | 1 | `C.Lamb` | WR | DAL | 18 | wo=2.5, wopr=0.081 | none |
| Jaxon Smith-Njigba | yes | no | 1 | `J.Smith-Njigba` | WR | SEA | 22 | wo=25.0, wopr=0.622 | none |
| Drake London | yes | no | 1 | `D.London` | WR | ATL | 18 | wo=20.0, wopr=0.755 | none |
| Malik Nabers | yes | no | 1 | `M.Nabers` | WR | NYG | 4 | wo=7.5, wopr=0.363 | none |
| Puka Nacua | yes | no | 1 | `P.Nacua` | WR | LA | 21 | wo=36.0, wopr=0.955 | none |
| Christian McCaffrey | yes | no | 1 | `C.McCaffrey` | RB | SF | 20 | wo=26.0, wopr=0.356 | none |
| Derrick Henry | yes | no | 1 | `D.Henry` | RB | BAL | 18 | wo=22.5, wopr=0.088 | none |
| Saquon Barkley | yes | no | 1 | `S.Barkley` | RB | PHI | 19 | wo=41.0, wopr=0.267 | none |
| Jahmyr Gibbs | yes | no | 1 | `J.Gibbs` | RB | DET | 18 | wo=31.5, wopr=0.211 | none |
| Travis Kelce | yes | no | 1 | `T.Kelce` | TE | KC | 18 | wo=15.0, wopr=0.451 | none |
| Mark Andrews | yes | no | 1 | `M.Andrews` | TE | BAL | 18 | wo=7.5, wopr=0.312 | none |
| George Kittle | yes | no | 1 | `G.Kittle` | TE | SF | 19 | wo=5.0, wopr=0.142 | none |
| Sam LaPorta | yes | no | 1 | `S.LaPorta` | TE | DET | 10 | wo=12.5, wopr=0.311 | none |
| Brock Bowers | yes | no | 1 | `B.Bowers` | TE | LV | 16 | wo=12.5, wopr=0.407 | none |

## Live Write Result

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2025 --season-end 2025 --write --strict --packet-version nflverse_pigskin_packet_v0_2025_001 --source-metric-version nflverse_adv_metrics_v0_2025_001 --output-json %TEMP%\phase29_49_packet_write.json
```

Result: pass.

| Field | Value |
|---|---|
| `wrote` | `true` |
| Target | `pigskin_player_context_packet_current` |
| Write SQL kind | `MERGE` |
| DML affected rows | 510 |
| Bounded post-write rows | 510 |
| Duplicate packet grain count | 0 |
| Source season range | 2025-2025 |
| 2025 week range | 1-22 |
| Packet version count | 1 |
| Source metric version count | 1 |
| Missing packet JSON | 0 |
| Missing packet text | 0 |
| Missing source freshness | 0 |
| Missing blocked metric flags | 0 |
| Rows with packet warnings | 22 |

## Post-Write Packet Verification

`pigskin_player_context_packet_current` after write:

| Metric | Count |
|---|---:|
| Total rows | 4,084 |
| 2025 rows | 510 |
| 2026+ rows | 0 |
| `nflverse_pigskin_packet_v0_2025_001` rows | 510 |
| Week 22 rows | 17 |
| Duplicate packet grain rows | 0 |
| Missing packet JSON | 0 |
| Missing packet text | 0 |
| Missing source freshness | 0 |
| Missing blocked metric flags | 0 |
| Rows with packet warnings | 22 |

`compat_pigskin_player_context_current` matched the target row counts:

| Metric | Count |
|---|---:|
| Total rows | 4,084 |
| 2025 rows | 510 |
| 2026+ rows | 0 |
| `nflverse_pigskin_packet_v0_2025_001` rows | 510 |
| Week 22 rows | 17 |
| Duplicate packet grain rows | 0 |

Rows by season after write:

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
| 2025 | 510 |

2025 position distribution:

| Position | Rows |
|---|---:|
| QB | 81 |
| RB | 126 |
| TE | 117 |
| WR | 186 |

Packet warning distribution:

| Warning count per row | Rows |
|---:|---:|
| 0 | 488 |
| 1 | 21 |
| 2 | 1 |

Source metric version distribution for 2025:

| Source metric version | Rows |
|---|---:|
| `nflverse_adv_metrics_v0_2025_001` | 510 |

Packet version distribution after write:

| Packet version | Rows |
|---|---:|
| `nflverse_pigskin_packet_v0_2014_001` | 482 |
| `nflverse_pigskin_packet_v0_2015_001` | 498 |
| `nflverse_pigskin_packet_v0_2016_2017_001` | 607 |
| `nflverse_pigskin_packet_v0_2018_2020_001` | 749 |
| `nflverse_pigskin_packet_v0_2021_2023_001` | 746 |
| `nflverse_pigskin_packet_v0_2024_001` | 492 |
| `nflverse_pigskin_packet_v0_2025_001` | 510 |

## Packet Usefulness Review

Packet text is compact and useful. It includes player, position, team, season/week, weighted opportunity, target share, WOPR, EPA per opportunity, and QB EPA per dropback when applicable.

Read-only post-write diagnostics inspected:

- 10 deterministic QB packets from 2025.
- 10 deterministic RB packets from 2025.
- 10 deterministic WR packets from 2025.
- 10 deterministic TE packets from 2025.
- 10 deterministic Week 22 packets from 2025.

The samples had populated packet text, explicit blocked metrics, reasonable packet warnings, no raw/source table text, no 2026+ content, and no current-season wording.

Representative examples:

- QB: `J.Allen (QB, BUF) as of 2025 week 20: weighted opportunity 12, target share 0, WOPR 0, EPA/opportunity 0.9278247102218522, EPA/dropback 0.11803155987891682`
- RB: `S.Barkley (RB, PHI) as of 2025 week 19: weighted opportunity 41, target share 0.17647058823529413, WOPR 0.26694230407818081, EPA/opportunity -0.17395394858795044`
- WR: `A.St. Brown (WR, DET) as of 2025 week 18: weighted opportunity 37.5, target share 0.41666666666666669, WOPR 1.031, EPA/opportunity 0.39666783128365296`
- TE: `C.Loveland (TE, CHI) as of 2025 week 20: weighted opportunity 25, target share 0.23809523809523808, WOPR 0.5485491071428571, EPA/opportunity -0.34078984847871763`

No packet text exposed raw/source table names. No packet text mislabeled 2025 as current-season content.

## Display-Name Ambiguity Behavior

Known ambiguous lookups returned explicit warnings:

| Lookup | Candidate count | Warning behavior |
|---|---:|---|
| `Tyreek Hill` | 2 | explicit ambiguity warning |
| `T.Hill` | 2 | explicit ambiguity warning |
| `J.Williams` | 3 | explicit ambiguity warning |
| `K.Williams` | 3 | explicit ambiguity warning |
| `T.Johnson` | 3 | explicit ambiguity warning |
| `B.Allen` | 2 | explicit ambiguity warning |
| `J.Johnson` | 2 | explicit ambiguity warning |
| `K.Allen` | 2 | explicit ambiguity warning |
| `M.Evans` | 2 | explicit ambiguity warning |
| `R.Wilson` | 2 | explicit ambiguity warning |
| `B.Robinson` | 2 | explicit ambiguity warning |
| `D.Moore` | 2 | explicit ambiguity warning |
| `J.Wright` | 2 | explicit ambiguity warning |
| `T.Etienne` | 2 | explicit ambiguity warning |

The warning text was:

```text
Ambiguous player lookup for <name>: <n> distinct candidates. Use --team, --position, or --player-id to disambiguate.
```

Safe disambiguation worked:

| Lookup | Result |
|---|---|
| `Tyreek Hill --team MIA --position WR` | one candidate: `T.Hill`, WR, MIA, week 4 |

No silent wrong-player selection was observed.

## Packet SQL And Source Isolation

Generated packet SQL reads only approved feature/current objects:

- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

Blocked dependencies were absent from packet SQL:

- `raw_nflverse_*`
- `stg_*`
- `play_by_play`
- `weekly_metrics`
- `player_rosters`
- `pigskin_player_context_packet_current` as a source
- `compat_pigskin_player_context_current` as a source
- LLM output tables
- content brief tables

## Blocked Metric Confirmation

Packet JSON includes blocked metric flags for:

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

Route, pressure, sack, scramble, pass-rate-over-expected, red-zone, and high-value-touch gaps remain explicit and are not silently filled.

## Week 22 Historical Context

The 2025 packet refresh includes 17 Week 22 rows:

| Position | Week 22 rows |
|---|---:|
| QB | 2 |
| RB | 4 |
| WR | 8 |
| TE | 3 |

Representative Week 22 rows include `D.Maye`, `S.Darnold`, `K.Walker`, `R.Stevenson`, `A.Barner`, `H.Henry`, and `C.Kupp`. These are historical/postseason packet rows only. No current-season content label was applied.

## 2026+ Separation

No 2026+ packet rows were written. No 2026+ rows were present in the 2025 dry-run candidate set or the three base advanced metric targets.

## Non-Target Object Verification

Raw counts remained unchanged from Phase 29.45:

| Table | Total rows | 2025 rows | 2026+ rows |
|---|---:|---:|---:|
| `raw_nflverse_schedules` | 3,295 | 285 | 0 |
| `raw_nflverse_rosters` | 35,336 | 3,134 | 0 |
| `raw_nflverse_rosters_weekly` | 526,550 | 46,831 | 0 |
| `raw_nflverse_weekly` | 217,230 | 19,399 | 0 |
| `raw_nflverse_pbp` | 580,005 | 48,771 | 0 |
| `raw_nflverse_snap_counts` | 300,812 | 26,612 | 0 |

Static/global raw counts remained unchanged:

| Table | Rows |
|---|---:|
| `raw_nflverse_teams` | 36 |
| `raw_nflverse_players` | 25,033 |
| `raw_nflverse_ff_playerids` | 69,060 |

Staging counts remained unchanged from Phase 29.46:

| Table | Total rows | 2025 rows | 2026+ rows |
|---|---:|---:|---:|
| `stg_player_identity` | 526,550 | 46,831 | 0 |
| `stg_game_context` | 3,295 | 285 | 0 |
| `stg_player_week_stats` | 217,230 | 19,399 | 0 |
| `stg_team_week_stats` | 6,590 | 570 | 0 |
| `stg_play_player_events` | 1,407,632 | 116,369 | 0 |
| `stg_participation_context` | 300,812 | 26,612 | 0 |

Base metrics and score lanes were unchanged except for the intended packet write:

| Object | Row count |
|---|---:|
| `player_week_advanced_metrics` | 217,230 |
| `team_week_context_metrics` | 6,590 |
| `qb_week_environment_metrics` | 8,042 |
| `player_recent_advanced_metrics_current` | 6,269 |
| `player_role_usage_metrics_current` | 6,269 |
| `trade_player_scores` | 154 |
| `trade_player_scores_current` | 77 |
| `compat_trade_player_scores_current` | 77 |
| `trade_pick_scores` | 64 |
| `trade_pick_scores_current` | 64 |
| `compat_trade_pick_scores_current` | 64 |

## Validation Results

Post-materialization validations:

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

- 22 packet rows have packet warnings. Most are expected sample-size, null snap-share, or missing QB environment sample warnings.
- Known abbreviated display-name collisions remain, and ambiguous lookups require explicit disambiguation.
- Route, pressure, sack, scramble, pass-rate-over-expected, red-zone, and high-value-touch metrics remain blocked or unavailable in v0.
- `raw_nflverse` validation retains an informational 2014-2025 coverage-review warning.
- `trade_pick_scores` validation retains the existing informational model-version warning.

## Recommended Next Phase

Package and commit the 2025 Pigskin packet refresh evidence, or proceed to the next bounded historical expansion/release review phase. Do not rerun the 2025 packet write unless idempotency testing is explicitly requested.
