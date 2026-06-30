# Phase 29.36 - 2021-2023 Pigskin Packets

Final decision: **2021-2023 PIGSKIN PACKETS MATERIALIZED WITH WARNINGS**

Phase 29.36 materialized historical 2021-2023 Pigskin context packets from the already materialized nflverse advanced metrics. The only live write was a gated MERGE into `pigskin_player_context_packet_current` for packet version `nflverse_pigskin_packet_v0_2021_2023_001`.

No raw backfill, staging materialization, advanced metric materialization, 2024+ write, Pigskin prompt, LLM call, ranking build, deployment, feature flag change, Cloud Run Job trigger, Scheduler job, scraping, Firebase artifact, or commit occurred.

## Authorization gate state

Before the write, these gates were empty or unset:

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

During the one live packet command, `ALLOW_PIGSKIN_PACKET_REFRESH=true` was set inside the same PowerShell `try/finally` wrapper.

After the write, these gates were empty or unset:

- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

Manual BigQuery checks used neutral aliases such as `row_count`, `packet_snapshot`, `target_packet`, `duplicate_grains`, and `requested_player`. No check used `rows` as an alias.

## Git state

- Latest commit: `db8f279 Expand nflverse Pigskin packets through 2020`.
- Staged files: 0.
- Existing untracked files remain historical validation backlog reports plus the newly created Phase 29.35 and Phase 29.36 reports.
- No commit was created.

## Baseline checks

Baseline checks passed before the write:

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
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: catalog discovered through `200_no_pressure_metrics_without_source.sql`.

## Packet source precheck

2021-2023 packet source counts matched the expected Phase 29.34 source state:

| Table | 2021 | 2022 | 2023 | Week range |
| --- | ---: | ---: | ---: | --- |
| `player_week_advanced_metrics` | 18,947 | 18,809 | 18,621 | 1-22 |
| `team_week_context_metrics` | 570 | 568 | 570 | 1-22 |
| `qb_week_environment_metrics` | 718 | 694 | 718 | 1-22 |

Current derived views:

- `player_recent_advanced_metrics_current`: 5,497 rows.
- `player_role_usage_metrics_current`: 5,497 rows.

## Packet target pre-write state

Before the write, both packet current surfaces had only 2014-2020 rows:

| Table | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | Target packet version |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `pigskin_player_context_packet_current` | 482 | 498 | 128 | 479 | 111 | 113 | 525 | 0 |
| `compat_pigskin_player_context_current` | 482 | 498 | 128 | 479 | 111 | 113 | 525 | 0 |

The target packet version `nflverse_pigskin_packet_v0_2021_2023_001` did not exist before the authorized write.

## Final all-position dry-run

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2021 --season-end 2023 --dry-run --limit 25 --strict --packet-version nflverse_pigskin_packet_v0_2021_2023_001 --source-metric-version nflverse_adv_metrics_v0_2021_2023_001 --output-json %TEMP%\phase29_36_packet_dry_run_all.json
```

Result:

- `dry_run=true`
- `wrote=false`
- `errors=[]`
- Candidate rows: 746
- QB: 112
- RB: 192
- WR: 293
- TE: 149
- Missing source freshness rows: 0
- Missing flags rows: 0
- Missing identity rows: 0
- Missing identity flag rows: 0
- Missing QB identity flag rows: 8
- Null CPOE rows: 78
- Null EPA/opportunity rows: 22
- Null snap-share rows: 1
- Sample-size warning rows: 22
- Packet warning rows from CLI scope/read-only warnings: 4
- Blocked source tokens in generated packet SQL: 0

Candidate count by season:

| Season | Candidate rows | Week range | Week 22 candidates |
| --- | ---: | --- | ---: |
| 2021 | 107 | 1-21 | 0 |
| 2022 | 131 | 1-22 | 1 |
| 2023 | 508 | 1-22 | 20 |
| Total | 746 | 1-22 | 21 |

## Final by-position dry-runs

| Position | Candidates | Week range | Week 22 candidates | Missing QB identity flags | Sample-size warnings | Null CPOE | Null snap share | Example players |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| QB | 112 | 1-22 | 2 | 0 | 20 | 14 | 0 | `C.Wentz`, `E.Stick`, `J.Allen`, `L.Jackson`, `P.Mahomes` |
| RB | 192 | 1-22 | 5 | 1 | 0 | 57 | 0 | `Bre.Hall`, `C.McCaffrey`, `T.Pollard`, `J.Conner`, `J.Taylor` |
| WR | 293 | 1-22 | 10 | 6 | 2 | 5 | 1 | `C.Lamb`, `J.Jefferson`, `D.Samuel`, `K.Allen`, `D.Smith` |
| TE | 149 | 1-22 | 4 | 1 | 0 | 2 | 0 | `E.Engram`, `S.LaPorta`, `J.Ferguson`, `D.Njoku`, `R.Gronkowski` |

## Named-player dry-run summary

Full-name lookups were run before the write. Three names were ambiguous and required team/position disambiguation:

- `A.J. Brown`: 3 candidates, resolved with `--team PHI --position WR`.
- `Justin Jefferson`: 2 candidates, resolved with `--team MIN --position WR`.
- `Tyreek Hill`: 2 candidates, resolved with `--team MIA --position WR`.

All requested examples resolved after safe disambiguation where needed:

| Requested player | Packet name | Pos | Team | Season | Week |
| --- | --- | --- | --- | ---: | ---: |
| Patrick Mahomes | `P.Mahomes` | QB | KC | 2023 | 22 |
| Josh Allen | `J.Allen` | QB | BUF | 2023 | 20 |
| Jalen Hurts | `J.Hurts` | QB | PHI | 2023 | 19 |
| Lamar Jackson | `L.Jackson` | QB | BAL | 2023 | 21 |
| Joe Burrow | `J.Burrow` | QB | CIN | 2023 | 11 |
| Justin Jefferson | `J.Jefferson` | WR | MIN | 2023 | 18 |
| Ja'Marr Chase | `J.Chase` | WR | CIN | 2023 | 18 |
| Tyreek Hill | `T.Hill` | WR | MIA | 2023 | 19 |
| Davante Adams | `D.Adams` | WR | LV | 2023 | 18 |
| A.J. Brown | `A.Brown` | WR | PHI | 2023 | 18 |
| CeeDee Lamb | `C.Lamb` | WR | DAL | 2023 | 19 |
| Christian McCaffrey | `C.McCaffrey` | RB | SF | 2023 | 22 |
| Derrick Henry | `D.Henry` | RB | TEN | 2023 | 18 |
| Austin Ekeler | `A.Ekeler` | RB | LAC | 2023 | 18 |
| Travis Kelce | `T.Kelce` | TE | KC | 2023 | 22 |
| Mark Andrews | `M.Andrews` | TE | BAL | 2023 | 21 |
| George Kittle | `G.Kittle` | TE | SF | 2023 | 22 |

## Live packet write

The write was run once with the required same-session wrapper:

```powershell
try {
  $env:ALLOW_PIGSKIN_PACKET_REFRESH = "true"

  echo "ALLOW_PIGSKIN_PACKET_REFRESH=$env:ALLOW_PIGSKIN_PACKET_REFRESH"

  .\venv\Scripts\python.exe -m src.nflverse_pigskin_packets --season-start 2021 --season-end 2023 --write --strict --packet-version nflverse_pigskin_packet_v0_2021_2023_001 --source-metric-version nflverse_adv_metrics_v0_2021_2023_001 --output-json %TEMP%\phase29_36_packet_write.json
} finally {
  Remove-Item Env:\ALLOW_PIGSKIN_PACKET_REFRESH -ErrorAction SilentlyContinue
}
```

Write result:

- `dry_run=false`
- `wrote=true`
- `write_sql_kind=MERGE`
- Target: `pigskin_player_context_packet_current`
- DML affected rows: 746
- Bounded row count after write: 746
- Duplicate packet grain count: 0
- Missing packet JSON count: 0
- Missing packet text count: 0
- Missing source freshness count: 0
- Missing blocked metric flag count: 0
- Rows with packet warnings: 34
- `packet_version_count=1`
- `source_metric_version_count=1`

## Post-write packet verification

The target table and compat view now include 2014-2023 packets.

| Table | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `pigskin_player_context_packet_current` | 482 | 498 | 128 | 479 | 111 | 113 | 525 | 107 | 131 | 508 | 3,082 |
| `compat_pigskin_player_context_current` | 482 | 498 | 128 | 479 | 111 | 113 | 525 | 107 | 131 | 508 | 3,082 |

Target packet version distribution:

| Packet version | Rows | Season range | Week range |
| --- | ---: | --- | --- |
| `nflverse_pigskin_packet_v0_2021_2023_001` | 746 | 2021-2023 | 1-22 |

Feature run distribution for the target packet version:

| Feature run ID | Rows |
| --- | ---: |
| `nflverse_adv_metrics_v0_2021_2023_001_2021` | 107 |
| `nflverse_adv_metrics_v0_2021_2023_001_2022` | 131 |
| `nflverse_adv_metrics_v0_2021_2023_001_2023` | 508 |

Position distribution:

| Position | Rows | Week range | Week 22 rows |
| --- | ---: | --- | ---: |
| QB | 112 | 1-22 | 2 |
| RB | 192 | 1-22 | 5 |
| TE | 149 | 1-22 | 4 |
| WR | 293 | 1-22 | 10 |

Quality checks for the target packet version:

| Check | Result |
| --- | ---: |
| Duplicate packet grain count | 0 |
| Missing `packet_json` | 0 |
| Missing `packet_text` | 0 |
| Missing source freshness | 0 |
| Missing blocked metric flags | 0 |
| Packet text source leak count | 0 |
| Packet text current-season phrase count | 0 |
| Rows with packet warnings | 34 |

Warning count distribution:

| Warning count in `packet_json` | Rows |
| ---: | ---: |
| 0 | 712 |
| 1 | 34 |

## Packet usefulness review

Named packet rows are present and have compact text with useful usage and efficiency context:

| Player | Packet | Pos | Team | Week | Example metrics |
| --- | --- | --- | --- | ---: | --- |
| Patrick Mahomes | `P.Mahomes` | QB | KC | 22 | dropbacks 49, EPA/dropback 0.1237 |
| Josh Allen | `J.Allen` | QB | BUF | 20 | dropbacks 39, EPA/dropback 0.1482 |
| Lamar Jackson | `L.Jackson` | QB | BAL | 21 | dropbacks 41, EPA/dropback -0.2928 |
| Justin Jefferson | `J.Jefferson` | WR | MIN | 18 | weighted opportunity 36, WOPR 0.8191 |
| CeeDee Lamb | `C.Lamb` | WR | DAL | 19 | weighted opportunity 43.5, WOPR 0.7132 |
| Christian McCaffrey | `C.McCaffrey` | RB | SF | 22 | weighted opportunity 42, WOPR 0.3243 |
| Travis Kelce | `T.Kelce` | TE | KC | 22 | weighted opportunity 25, WOPR 0.4721 |
| George Kittle | `G.Kittle` | TE | SF | 22 | weighted opportunity 7.5, WOPR 0.1875 |

Deterministic position samples were inspected for 10 QB, 10 RB, 10 WR, 10 TE, and 10 Week 22 packets. Packet text is compact and season/week-labeled, for example:

- `P.Mahomes (QB, KC) as of 2023 week 22...`
- `C.McCaffrey (RB, SF) as of 2023 week 22...`
- `T.Kelce (TE, KC) as of 2023 week 22...`
- `B.Aiyuk (WR, SF) as of 2023 week 22...`

Packet text does not expose raw table names or imply current-season content. `packet_json.source_freshness` preserves provenance metadata, including source names, which is expected for traceability.

## Display-name ambiguity behavior

Ambiguous lookup checks after the write returned explicit warnings:

| Lookup | Candidate count | Behavior |
| --- | ---: | --- |
| `A.J. Brown` | 3 | warning, requires `--team`, `--position`, or `--player-id` |
| `Justin Jefferson` | 2 | warning, requires disambiguation |
| `Tyreek Hill` | 2 | warning, requires disambiguation |
| `D.Johnson` | 4 | warning, requires disambiguation |
| `J.Williams` | 4 | warning, requires disambiguation |
| `A.Brown` | 3 | warning, requires disambiguation |

Safe disambiguation returned the intended single candidates:

| Disambiguated lookup | Result |
| --- | --- |
| `A.J. Brown`, PHI, WR | `A.Brown`, WR, PHI, week 18 |
| `Justin Jefferson`, MIN, WR | `J.Jefferson`, WR, MIN, week 18 |
| `Tyreek Hill`, MIA, WR | `T.Hill`, WR, MIA, week 19 |
| `D.Johnson`, PIT, WR | `D.Johnson`, WR, PIT, week 19 |
| `J.Williams`, DEN, RB | `J.Williams`, RB, DEN, week 18 |
| `A.Brown`, PHI, WR | `A.Brown`, WR, PHI, week 18 |

No silent wrong-player selection was observed.

## Packet SQL and source isolation

The generated packet SQL reads only approved feature/current objects:

- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

The generated packet SQL did not read:

- `raw_nflverse_*`
- `stg_*`
- `play_by_play`
- `weekly_metrics`
- `player_rosters`
- `pigskin_player_context_packet_current` as a source
- `compat_pigskin_player_context_current` as a source
- LLM output tables

`compat_pigskin` validations also passed and confirmed no raw source dependency in the compatibility view.

## Blocked metric confirmation

Blocked metric flags remain populated in packet JSON:

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

The write result reported `missing_blocked_metric_flag_count=0`.

## Week 22 and postseason-inclusive behavior

2021-2023 packets are historical and postseason-inclusive through Week 22:

- Total Week 22 target packet rows: 21.
- 2022 Week 22 rows: 1.
- 2023 Week 22 rows: 20.
- Week 22 rows are labeled by season and week in packet text.
- Packet text does not include current-season phrasing.

## Non-target object verification

Read-only checks after the packet write confirmed non-target objects remained unchanged:

| Layer | Evidence |
| --- | --- |
| Raw nflverse | 2021-2023 counts still match Phase 29.32. |
| Staging nflverse | 2021-2023 counts still match Phase 29.33. |
| Base advanced metrics | 2021-2023 counts still match Phase 29.34. |
| Current metric views | `player_recent_advanced_metrics_current=5,497`, `player_role_usage_metrics_current=5,497`. |
| Trade score tables | `trade_player_scores=154`, `trade_pick_scores=64`. |

No deploy command was run.

## Validation results

Post-write validation patterns:

- `raw_nflverse`: 3 passed, 0 failed. Informational coverage warning returned 2014-2023 coverage.
- `stg_`: 7 passed, 0 failed.
- `advanced_metrics`: 4 passed, 0 failed.
- `compat_pigskin`: 2 passed, 0 failed.
- `trade_player_scores`: 12 passed, 0 failed.
- `trade_pick_scores`: 17 passed, 0 failed. Informational model-version coverage warning returned `trade_pick_score_v0_2026_001`.

## Final local checks

Final local checks passed:

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
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: catalog discovered through `200_no_pressure_metrics_without_source.sql`.

PowerShell captured unittest progress output as `NativeCommandError` wrapper text because the unittest runner writes progress to stderr. The process exit codes were 0 and the test summaries reported `OK`.

## Staging and production untouched

Read-only Cloud Run describe confirmed no deployment occurred:

| Service | Revision | Traffic | Image | Relevant flags |
| --- | --- | ---: | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100% | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | Trade History false, score flags false, Data Ops job trigger flags false, local subprocess flags false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100% | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | Trade History compat true, score flags true, Data Ops job trigger flags false, local subprocess flags false |

## Remaining warnings

- 2021-2023 Pigskin packets are historical. They must not be presented as current-season content.
- Week 22 rows are postseason-inclusive historical context.
- Display-name collisions remain real. Use full names plus `--team`, `--position`, or `--player-id` for ambiguous examples.
- Route metrics, pressure/sack/scramble metrics, red-zone usage, high-value touches, true pressure, contact yards, and alignment remain intentionally blocked.
- Pass rate over expected remains unavailable.
- `stg_participation_context` retains known PFR snap-count identity gaps, but packet rows had 0 missing identity rows.
- 34 packet rows carry warning payloads, expected from sample-size or missing-metric context.

## Recommended next phase

Proceed to **Phase 29.37 - package and commit 2021-2023 Pigskin packet refresh evidence**.

Recommended boundaries:

- Commit only reviewed Phase 29.32 through Phase 29.36 evidence if owner approves.
- Do not rerun raw, staging, advanced metrics, or packet writes.
- Keep historical validation backlog decisions separate.
- Continue to keep production and staging deploys out of the nflverse warehouse expansion phases unless explicitly authorized.
