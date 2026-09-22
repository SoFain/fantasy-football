# Phase 29.35 - 2021-2023 Pigskin Packet Dry Run

Final decision: **2021-2023 PIGSKIN PACKET DRY RUN READY WITH WARNINGS**

Phase 29.35 completed the read-only 2021-2023 Pigskin packet selection dry-run against `nflverse_adv_metrics_v0_2021_2023_001`. No Pigskin packets were written. No raw backfill, staging materialization, advanced metric materialization, deployment, Cloud Run Job trigger, Scheduler job, LLM action, Pigskin prompt, ranking build, scraping, Firebase artifact, feature flag change, or commit occurred.

## Authorization gate state

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

Manual BigQuery checks used neutral aliases such as `candidate_packet`, `packet_snapshot`, `metric_snapshot`, and `role_snapshot`. The checks did not use `rows` as a BigQuery alias.

## Git state

- Latest commit at phase start: `db8f279 Expand nflverse Pigskin packets through 2020`.
- No files were staged.
- Existing untracked files were Phase 29 validation backlog reports from earlier phases.
- This phase created only this validation report.

## Baseline checks

All baseline checks passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_pigskin_packets.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_advanced_metrics.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_staging.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill_plan.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_pigskin_packets`: 15 tests passed.
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_advanced_metrics`: 12 tests passed.
- `.\venv\Scripts\python.exe -m unittest discover tests`: 487 tests passed.
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: no pending migrations.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: catalog discovered through validation `200_no_pressure_metrics_without_source.sql`.

## Packet source precheck

The 2021-2023 feature sources were present and matched Phase 29.34 counts:

| Table | 2021 | 2022 | 2023 | Week range |
| --- | ---: | ---: | ---: | --- |
| `player_week_advanced_metrics` | 18,947 | 18,809 | 18,621 | 1-22 |
| `team_week_context_metrics` | 570 | 568 | 570 | 1-22 |
| `qb_week_environment_metrics` | 718 | 694 | 718 | 1-22 |

Current derived views:

- `player_recent_advanced_metrics_current`: 5,497 rows.
- `player_role_usage_metrics_current`: 5,497 rows.

## Packet target pre-write state

Both Pigskin packet current surfaces remained unchanged before and after the dry-runs:

| Table | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | Total | Target 2021-2023 packet version |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `pigskin_player_context_packet_current` | 482 | 498 | 128 | 479 | 111 | 113 | 525 | 2,336 | 0 |
| `compat_pigskin_player_context_current` | 482 | 498 | 128 | 479 | 111 | 113 | 525 | 2,336 | 0 |

No rows exist for packet version `nflverse_pigskin_packet_v0_2021_2023_001`.

## All-position dry-run summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2021 --season-end 2023 --dry-run --limit 25 --strict --packet-version nflverse_pigskin_packet_v0_2021_2023_001 --source-metric-version nflverse_adv_metrics_v0_2021_2023_001 --output-json %TEMP%\phase29_35_packet_dry_run_all.json
```

Result:

- `dry_run=true`
- `wrote=false`
- `errors=[]`
- Candidate rows: 746
- Packet universe: QB/RB/WR/TE only, with offensive opportunity or QB sample.
- Source freshness missing rows: 0
- Missing flags rows: 0
- Missing identity rows: 0
- Missing identity flag rows: 0
- Missing QB identity flag rows: 8
- Null CPOE rows: 78
- Null EPA/opportunity rows: 22
- Null snap share rows: 1
- Sample-size warning rows: 22
- Packet warnings: 4 read-only/scope warnings from the CLI.

Candidate count by season:

| Season | Candidate rows | Week range | Week 22 candidates |
| --- | ---: | --- | ---: |
| 2021 | 107 | 1-21 | 0 |
| 2022 | 131 | 1-22 | 1 |
| 2023 | 508 | 1-22 | 20 |
| Total | 746 | 1-22 | 21 |

Candidate count by position:

| Position | Candidate rows |
| --- | ---: |
| QB | 112 |
| RB | 192 |
| WR | 293 |
| TE | 149 |

Example packet previews:

- `C.Wentz`, QB, LA, week 18
- `E.Stick`, QB, LAC, week 18
- `J.Allen`, QB, BUF, week 20
- `L.Jackson`, QB, BAL, week 21
- `P.Mahomes`, QB, KC, week 22

Week 22 rows are historical/postseason packet context only. They are not current-season content.

## By-position dry-run summary

All by-position dry-runs used the same packet and metric versions, `--dry-run`, `--strict`, and `--limit 25`.

| Position | Candidates | Week range | Week 22 candidates | Missing QB identity flags | Sample-size warnings | Null CPOE | Null snap share | Example players |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| QB | 112 | 1-22 | 2 | 0 | 20 | 14 | 0 | `C.Wentz`, `E.Stick`, `J.Allen`, `L.Jackson`, `P.Mahomes` |
| RB | 192 | 1-22 | 5 | 1 | 0 | 57 | 0 | `Bre.Hall`, `C.McCaffrey`, `T.Pollard`, `J.Conner`, `J.Taylor` |
| WR | 293 | 1-22 | 10 | 6 | 2 | 5 | 1 | `C.Lamb`, `J.Jefferson`, `D.Samuel`, `K.Allen`, `D.Smith` |
| TE | 149 | 1-22 | 4 | 1 | 0 | 2 | 0 | `E.Engram`, `S.LaPorta`, `J.Ferguson`, `D.Njoku`, `R.Gronkowski` |

## Named-player lookup summary

Full names were tested first. Three compact display names were ambiguous and were rerun with team/position filters: A.J. Brown, Justin Jefferson, and Tyreek Hill.

| Requested player | Result | Packet name | Pos | Team | Season | Week | Key metrics | Warnings |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| Patrick Mahomes | found | `P.Mahomes` | QB | KC | 2023 | 22 | dropbacks 49.0, EPA/dropback 0.1237, CPOE 7.7302 | none |
| Josh Allen | found | `J.Allen` | QB | BUF | 2023 | 20 | dropbacks 39.0, EPA/dropback 0.1482, CPOE -0.5439 | none |
| Jalen Hurts | found | `J.Hurts` | QB | PHI | 2023 | 19 | dropbacks 38.0, EPA/dropback -0.0815, CPOE 9.6419 | none |
| Lamar Jackson | found | `L.Jackson` | QB | BAL | 2023 | 21 | dropbacks 41.0, EPA/dropback -0.2928, CPOE -5.5441 | none |
| Joe Burrow | found | `J.Burrow` | QB | CIN | 2023 | 11 | dropbacks 19.0, EPA/dropback 0.1534, CPOE -4.2272 | none |
| Justin Jefferson | found after `--team MIN --position WR` | `J.Jefferson` | WR | MIN | 2023 | 18 | weighted opp 36.0, snap 0.93, WOPR 0.8191, EPA/opportunity 0.5871 | none |
| Ja'Marr Chase | found | `J.Chase` | WR | CIN | 2023 | 18 | weighted opp 15.0, snap 0.48, WOPR 0.3714, EPA/opportunity -0.3464 | none |
| Tyreek Hill | found after `--team MIA --position WR` | `T.Hill` | WR | MIA | 2023 | 19 | weighted opp 20.0, snap 0.66, WOPR 0.5168, EPA/opportunity -0.3055 | none |
| Davante Adams | found | `D.Adams` | WR | LV | 2023 | 18 | weighted opp 20.0, snap 0.94, WOPR 0.5626, EPA/opportunity 0.2893 | none |
| A.J. Brown | found after `--team PHI --position WR` | `A.Brown` | WR | PHI | 2023 | 18 | weighted opp 2.5, snap 0.18, WOPR 0.0611, EPA/opportunity -5.1270 | none |
| CeeDee Lamb | found | `C.Lamb` | WR | DAL | 2023 | 19 | weighted opp 43.5, snap 0.92, WOPR 0.7132, EPA/opportunity -0.3716 | none |
| Christian McCaffrey | found | `C.McCaffrey` | RB | SF | 2023 | 22 | weighted opp 42.0, snap 0.95, WOPR 0.3243, EPA/opportunity -0.1956 | none |
| Derrick Henry | found | `D.Henry` | RB | TEN | 2023 | 18 | weighted opp 19.0, snap 0.65, WOPR 0.0, EPA/opportunity 0.2894 | none |
| Austin Ekeler | found | `A.Ekeler` | RB | LAC | 2023 | 18 | weighted opp 30.0, snap 0.76, WOPR 0.2667, EPA/opportunity -0.4824 | none |
| Travis Kelce | found | `T.Kelce` | TE | KC | 2023 | 22 | weighted opp 25.0, snap 0.85, WOPR 0.4721, EPA/opportunity 0.4463 | none |
| Mark Andrews | found | `M.Andrews` | TE | BAL | 2023 | 21 | weighted opp 5.0, snap 0.31, WOPR 0.1188, EPA/opportunity 0.3799 | none |
| George Kittle | found | `G.Kittle` | TE | SF | 2023 | 22 | weighted opp 7.5, snap 0.84, WOPR 0.1875, EPA/opportunity 0.2467 | none |

Full-name ambiguity examples before disambiguation:

- `A.J. Brown`: 3 compact `A.Brown` candidates: QB BAL, WR TB, WR PHI.
- `Justin Jefferson`: 2 compact `J.Jefferson` candidates: RB DET, WR MIN.
- `Tyreek Hill`: 2 compact `T.Hill` candidates: WR MIA, TE NO.

No requested player remained unresolved after safe disambiguation.

## Display-name ambiguity diagnostics

High-risk abbreviated names exist in the 2021-2023 candidate set. The highest-risk examples:

| Display name | Distinct player IDs | Distinct teams | Distinct positions | Teams | Positions |
| --- | ---: | ---: | ---: | --- | --- |
| `D.Johnson` | 4 | 4 | 2 | BUF, JAX, NO, PIT | RB, WR |
| `J.Williams` | 4 | 4 | 2 | DEN, DET, NO, WAS | RB, WR |
| `A.Brown` | 3 | 3 | 2 | BAL, PHI, TB | QB, WR |
| `T.Johnson` | 3 | 3 | 2 | BUF, HOU, LA | RB, WR |
| `T.Williams` | 3 | 3 | 2 | ARI, CIN, DET | RB, WR |

The lookup behavior is safe for dry-run review: ambiguous compact names produce lookup warnings and can be resolved with `--team`, `--position`, or `--player-id`. No 2021-2023 unresolved example blocked packet planning.

## Packet SQL and source isolation

The generated packet SQL read only approved feature/current objects:

- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

The generated packet SQL did not reference:

- `raw_nflverse_*`
- `stg_*`
- `play_by_play`
- `weekly_metrics`
- `player_rosters`
- `pigskin_player_context_packet_current` as a source
- `compat_pigskin_player_context_current` as a source
- LLM output tables

`compat_pigskin` validation also confirmed no raw source dependency.

## Blocked metric confirmation

Blocked metric flags remain explicit in the packet dry-run:

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

The packet warnings state that diagnostics are read-only unless `--write` is explicitly authorized, the command is scoped by season range and packet version, writes are limited to `pigskin_player_context_packet_current`, and packet SQL reads current/base feature marts only.

## Warehouse unchanged confirmation

Read-only checks after the dry-runs confirmed:

- `pigskin_player_context_packet_current`: 2,336 rows, 0 target-version rows for 2021-2023.
- `compat_pigskin_player_context_current`: 2,336 rows, 0 target-version rows for 2021-2023.
- Raw 2021-2023 counts still match Phase 29.32.
- Staging 2021-2023 counts still match Phase 29.33.
- Feature 2021-2023 counts still match Phase 29.34.
- Score table counts were observed only for unchanged-state confirmation: `trade_player_scores` 154 rows, `trade_pick_scores` 64 rows.
- No write-capable command was run in this phase.

Raw and staging examples still match prior evidence:

| Table | 2021 | 2022 | 2023 | Week range |
| --- | ---: | ---: | ---: | --- |
| `raw_nflverse_pbp` | 49,922 | 49,434 | 49,665 | 1-22 |
| `raw_nflverse_weekly` | 18,947 | 18,809 | 18,621 | 1-22 |
| `raw_nflverse_snap_counts` | 26,468 | 26,381 | 26,540 | 1-22 |
| `stg_player_week_stats` | 18,947 | 18,809 | 18,621 | 1-22 |
| `stg_team_week_stats` | 570 | 568 | 570 | 1-22 |
| `stg_play_player_events` | 121,589 | 119,216 | 120,051 | 1-22 |
| `stg_participation_context` | 26,468 | 26,381 | 26,540 | 1-22 |

## Validation results

Requested validation patterns:

- `raw_nflverse`: 3 passed, 0 failed. Informational coverage warning returned 2014-2023 coverage.
- `stg_`: 7 passed, 0 failed.
- `advanced_metrics`: 4 passed, 0 failed.
- `compat_pigskin`: 2 passed, 0 failed.
- `trade_player_scores`: 12 passed, 0 failed.
- `trade_pick_scores`: 17 passed, 0 failed. Informational model-version coverage warning returned `trade_pick_score_v0_2026_001`.

Final local checks also passed:

- Safety checker passed.
- All requested Python compile checks passed.
- `compileall -q src scripts` passed.
- `tests.test_nflverse_pigskin_packets`: 15 tests passed.
- `tests.test_nflverse_advanced_metrics`: 12 tests passed.
- Full `unittest discover tests`: 487 tests passed.
- No pending migrations.
- Validation dry-run catalog discovered through `200_no_pressure_metrics_without_source.sql`.

## Staging and production untouched

Read-only Cloud Run describe confirmed no deployment occurred in this phase:

| Service | Revision | Traffic | Image | Relevant flags |
| --- | --- | ---: | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100% | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | Trade History false, score flags false, Data Ops job trigger flags false, local subprocess flags false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100% | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | Trade History compat true, score flags true, Data Ops job trigger flags false, local subprocess flags false |

## Remaining warnings

- This remains a dry-run only. The 2021-2023 Pigskin packet tables still have 0 target-version rows.
- 2021-2023 are postseason-inclusive through Week 22. Report and UI copy must not present these packets as current-season content.
- Display-name collisions are real in the candidate set. Any write or QA should continue using full-name lookup plus team/position or player ID disambiguation for compact names.
- Known blocked metrics remain blocked: route metrics, pressure/sack/scramble metrics, red-zone and high-value touch metrics, first-read usage, alignment, and contact-yard metrics.
- Known source gaps remain accepted: `stg_participation_context` identity gaps from PFR snap-count coverage, pass rate over expected null, and historical source limitations.
- PowerShell captured unittest progress emitted on stderr as a `NativeCommandError` wrapper, but the test commands exited 0 and reported `OK`.

## Recommended next phase

Proceed to **Phase 29.36 - authorized 2021-2023 Pigskin packet refresh only**.

Recommended guardrails for Phase 29.36:

- Require `ALLOW_PIGSKIN_PACKET_REFRESH=true` only inside the same command session.
- Use packet version `nflverse_pigskin_packet_v0_2021_2023_001`.
- Use source metric version `nflverse_adv_metrics_v0_2021_2023_001`.
- Write only 2021-2023 Pigskin packets.
- Keep the packet universe QB/RB/WR/TE with the opportunity or QB-sample filter.
- Do not rerun raw, staging, or advanced metrics.
- Recheck display-name ambiguity after write.
- Preserve the blocked metric flags and source isolation checks.
