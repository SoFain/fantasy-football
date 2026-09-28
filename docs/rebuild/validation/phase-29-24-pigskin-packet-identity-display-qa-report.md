# Phase 29.24 Pigskin Packet Identity and Display-Name QA Report

Date: 2026-06-29

Final decision: **PIGSKIN PACKET IDENTITY DISPLAY QA READY WITH WARNINGS**

## Scope

Phase 29.24 was run as read-only warehouse QA plus code/test repair. No packet refresh, raw backfill, staging materialization, advanced metrics materialization, deploy, Cloud Run Job trigger, LLM action, scraping, or commit occurred.

## Authorization Gates

All write/deploy gates were unset in the process environment:

| Gate | State |
| --- | --- |
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

## Baseline Checks

Passed before the focused QA work:

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile src\nflverse_pigskin_packets.py` | PASS |
| `py_compile src\nflverse_advanced_metrics.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_pigskin_packets` | PASS, 11 tests before changes |
| `unittest tests.test_nflverse_advanced_metrics` | PASS, 12 tests |
| `unittest discover tests` | PASS |
| `run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `run_bigquery_validations.py --dry-run` | PASS, catalog discovered through validation 200 |

## Identity QA Findings

The packet lookup issue was caused by abbreviated names in the nflverse-derived packet source, not by missing player IDs.

### Julio Jones

`Julio Jones` is present in the 2016-2017 packet slice as:

| Packet name | Position | Team | Player ID | Season/week |
| --- | --- | --- | --- | --- |
| `Ju.Jones` | WR | ATL | `00-0027944` | 2017 week 19 |

The old lookup generated compact full-name and one-letter-initial variants only. That allowed `juliojones` and `jjones`, but missed `jujones`.

### David Johnson

`David Johnson` is present in the 2016-2017 packet slice as:

| Packet name | Position | Team | Player ID | Notes |
| --- | --- | --- | --- | --- |
| `Da.Johnson` | RB | ARI | `00-0032187` | Target David Johnson |
| `D.Johnson` | TE | PIT | `00-0026957` | Different player |

The display-name collision is real. `D.Johnson` appears across multiple player IDs, teams, and positions in the packet table.

Collision summary:

| Display name | Packet rows | Player IDs | Teams | Positions |
| --- | ---: | ---: | --- | --- |
| `D.Johnson` | 6 | 3 | ARI, HOU, LAC, NE, PIT | RB, TE, WR |
| `J.Jones` | 4 | 2 | ATL, GB, LV | WR |
| `Ju.Jones` | 1 | 1 | ATL | WR |
| `Da.Johnson` | 1 | 1 | ARI | RB |

## Code Changes

Changed files:

| File | Summary |
| --- | --- |
| `src/nflverse_pigskin_packets.py` | Added `--team` and `--player-id` filters, expanded player-name lookup to include first-two-letter abbreviation variants, added read-only lookup diagnostics, added ambiguity/no-match warnings, removed stale Phase 29.11/29.12 warning text. |
| `tests/test_nflverse_pigskin_packets.py` | Added tests for two-letter abbreviation lookup, team/position/player ID disambiguation, ambiguous lookup warnings, and current warning text. |

The lookup now supports variants such as:

| Full name | Generated variants |
| --- | --- |
| `Julio Jones` | `juliojones`, `jjones`, `jujones` |
| `David Johnson` | `davidjohnson`, `djohnson`, `dajohnson` |

## Post-Fix Lookup Matrix

All commands were dry-runs. Every summary returned `wrote: false`.

| Command shape | Candidate count | Lookup result | Warning |
| --- | ---: | --- | --- |
| `--player-name "Julio Jones"` | 1 | `Ju.Jones`, WR, ATL, `00-0027944` | none |
| `--player-name "J.Jones"` | 0 | none | no packet candidates matched |
| `--player-name "Julio Jones" --team ATL` | 1 | `Ju.Jones`, WR, ATL, `00-0027944` | none |
| `--player-name "Julio Jones" --position WR` | 1 | `Ju.Jones`, WR, ATL, `00-0027944` | none |
| `--player-name "David Johnson"` | 2 | `Da.Johnson` RB ARI and another candidate | ambiguous lookup warning |
| `--player-name "D.Johnson"` | 1 | `D.Johnson`, TE, PIT, `00-0026957` | none |
| `--player-name "David Johnson" --team ARI` | 1 | `Da.Johnson`, RB, ARI, `00-0032187` | none |
| `--player-name "David Johnson" --position RB` | 1 | `Da.Johnson`, RB, ARI, `00-0032187` | none |
| `--player-name "D.Johnson" --team PIT` | 1 | `D.Johnson`, TE, PIT, `00-0026957` | none |
| `--player-name "D.Johnson" --position TE` | 1 | `D.Johnson`, TE, PIT, `00-0026957` | none |

## Warehouse State

Read-only row-count checks confirmed the warehouse was not mutated by this phase.

| Table | Total rows | 2014 | 2015 | 2016 | 2017 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `raw_nflverse_pbp` | 190,647 | 47,629 | 48,122 | 47,651 | 47,245 |
| `raw_nflverse_weekly` | 70,180 | 17,601 | 17,592 | 17,531 | 17,456 |
| `raw_nflverse_rosters` | 10,484 | 2,152 | 2,189 | 3,061 | 3,082 |
| `stg_player_identity` | 146,737 | 30,195 | 30,201 | 35,020 | 51,321 |
| `stg_player_week_stats` | 70,180 | 17,601 | 17,592 | 17,531 | 17,456 |
| `player_week_advanced_metrics` | 70,180 | 17,601 | 17,592 | 17,531 | 17,456 |
| `player_recent_advanced_metrics_current` | 3,128 | n/a | n/a | n/a | n/a |
| `pigskin_player_context_packet_current` | 1,587 | n/a | n/a | n/a | n/a |
| `compat_pigskin_player_context_current` | 1,587 | n/a | n/a | n/a | n/a |

No packet rows were written. Existing materialized packet display names remain unchanged until a separately authorized packet refresh or repair phase.

## Validation Results

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | PASS, 3 passed, 0 failed. Informational coverage warning returned 3 rows. |
| `stg_` | PASS, 7 passed, 0 failed |
| `advanced_metrics` | PASS, 4 passed, 0 failed |
| `compat_pigskin` | PASS, 2 passed, 0 failed |
| `trade_player_scores` | PASS, 12 passed, 0 failed |
| `trade_pick_scores` | PASS, 17 passed, 0 failed. Informational model-version warning returned 1 row. |

## Final Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile src\nflverse_pigskin_packets.py` | PASS |
| `py_compile src\nflverse_advanced_metrics.py` | PASS |
| `compileall -q src scripts` | PASS |
| `unittest tests.test_nflverse_pigskin_packets` | PASS, 15 tests |
| `unittest tests.test_nflverse_advanced_metrics` | PASS, 12 tests |
| `unittest discover tests` | PASS, 487 tests |
| `run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `run_bigquery_validations.py --dry-run` | PASS, catalog discovered through validation 200 |

## Deployment State

Production was checked with read-only Cloud Run describe.

| Service | Revision | Traffic | Image | Flag state |
| --- | --- | ---: | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100% | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | all production risk flags false, score flags false, Trade History compatibility false, Data Ops trigger/local flags false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100% | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | staging score and Trade History flags true as previously configured, job/local subprocess flags false |

No deployment occurred.

## Remaining Warnings

- Existing packet rows still use nflverse abbreviated display names such as `Ju.Jones` and `Da.Johnson`. This phase fixed lookup and diagnostics only.
- `David Johnson` remains ambiguous without `--team`, `--position`, or `--player-id`. That is correct behavior because `D.Johnson` collisions exist in the packet data.
- `J.Jones` is not a safe canonical lookup for 2017 Julio Jones because the packet row uses `Ju.Jones`. Full-name lookup now resolves it.
- Raw nflverse coverage and trade pick model-version validations returned informational warnings only.

## Recommended Next Phase

- If the owner wants visible full names in existing packets, run a separate, authorized packet-display repair or packet refresh phase. That phase should be scoped, gated, and should preserve player IDs.
- Add UI-level display-name fallback only if product requirements prefer canonical names over packet-source names.
- Keep using `--team`, `--position`, or `--player-id` when investigating abbreviated or collision-prone player labels.

