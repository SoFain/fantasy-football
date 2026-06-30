# Phase 29.43 - 2024 nflverse Pigskin Expansion Release Package

Date: 2026-06-30

Final decision: 2024 NFLVERSE PIGSKIN EXPANSION PACKAGE READY

## Scope

This package locks in the 2024 historical nflverse Pigskin expansion checkpoint before any decision about a 2025/current-season lane.

No new materialization, raw backfill, staging materialization, advanced metrics materialization, Pigskin packet materialization, deployment, feature flag change, Cloud Run Job trigger, Scheduler job, LLM action, Pigskin prompt, scrape, external fetch, Firebase artifact, ranking build, or current-season work belongs to this package phase.

## Final 2024 Expansion State

Committed checkpoint before packaging:
- `e56afa3 Expand nflverse Pigskin packets through 2023`

2024 versions:
- Packet version: `nflverse_pigskin_packet_v0_2024_001`
- Source metric version: `nflverse_adv_metrics_v0_2024_001`

Packet totals after Phase 29.42:
- `pigskin_player_context_packet_current`: 3,574 rows
- `compat_pigskin_player_context_current`: 3,574 rows
- 2024 packet rows: 492
- 2025/future packet rows: 0

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

## Raw 2024 Row Counts

| Table | 2024 rows |
|---|---:|
| `raw_nflverse_schedules` | 285 |
| `raw_nflverse_rosters` | 3,215 |
| `raw_nflverse_rosters_weekly` | 46,572 |
| `raw_nflverse_weekly` | 18,959 |
| `raw_nflverse_pbp` | 49,492 |
| `raw_nflverse_snap_counts` | 26,615 |

2025/future raw rows: 0.

## Staging 2024 Row Counts

| Table | 2024 rows |
|---|---:|
| `stg_player_identity` | 46,572 |
| `stg_game_context` | 285 |
| `stg_player_week_stats` | 18,959 |
| `stg_team_week_stats` | 570 |
| `stg_play_player_events` | 118,037 |
| `stg_participation_context` | 26,615 |

2025/future staging rows: 0.

## Advanced Metrics 2024 Row Counts

| Table | 2024 rows |
|---|---:|
| `player_week_advanced_metrics` | 18,959 |
| `team_week_context_metrics` | 570 |
| `qb_week_environment_metrics` | 707 |

2025/future feature rows: 0.

## Packet 2024 Quality

2024 packet verification:
- Packet rows: 492
- Duplicate packet grain count: 0
- Missing packet JSON: 0
- Missing packet text: 0
- Missing source freshness: 0
- Missing blocked metric flags: 0
- Rows with packet warnings: 22

2024 position distribution:
- QB: 79
- RB: 123
- WR: 185
- TE: 105

## Week 22 and Current-Season Separation

2024 packets intentionally include postseason-inclusive Week 22 rows. These are historical 2024 packets, not current-season content.

No 2025 or future packet rows exist in the Pigskin packet current table or compatibility view after Phase 29.42.

## Display-Name Ambiguity

Display-name collisions remain an explicit warning state, not an implicit resolution path.

Known ambiguous examples:
- `Justin Jefferson`
- `Tyreek Hill`
- `B.Allen`
- `D.Johnson`
- `J.Jefferson`
- `T.Hill`
- `K.Allen`

Disambiguation through `--team`, `--position`, or `--player-id` is required for exact targeting.

## Blocked Metrics

The 2024 packet lane continues to disclose unavailable metrics instead of inventing them:
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

Packet SQL reads derived feature marts only, not raw/source tables or legacy app tables.

## Reports Intended For Commit

Approved package files:
- `docs/rebuild/validation/phase-29-38-raw-backfill-2024-report.md`
- `docs/rebuild/validation/phase-29-39-staging-materialization-2024-report.md`
- `docs/rebuild/validation/phase-29-40-advanced-metrics-2024-report.md`
- `docs/rebuild/validation/phase-29-41-pigskin-packet-dry-run-2024-report.md`
- `docs/rebuild/validation/phase-29-42-pigskin-packets-2024-report.md`
- `docs/rebuild/validation/phase-29-43-2024-expansion-release-package.md`

## Files Intentionally Excluded

Excluded from this package:
- Historical Phase 17 through Phase 28 validation backlog
- Superseded Phase 29 evidence not part of the 2024 package
- `output/`
- `output/playwright/`
- local browser evidence
- temporary JSON
- logs
- caches
- `.env` or `.env.*`
- secret JSON files
- deployment artifacts
- source files, unless independently reviewed in another phase

## Known Warnings

- `raw_nflverse` coverage validation remains informational.
- `trade_pick_scores` model-version coverage validation remains informational.
- 22 of 492 2024 packets carry one packet warning.
- 2024 Week 22 rows are historical postseason rows.
- Display-name ambiguity requires explicit disambiguation.

## Next Recommended Phase

Phase 29.44: decide whether 2025/current-season work belongs in Phase 29 or should start a separate current-season lane.
