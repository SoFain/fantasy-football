# Phase 29.50 2025 Expansion Release Package

Final package state: **2025 NFLVERSE PIGSKIN EXPANSION READY FOR COMMIT WITH WARNINGS**

This package locks the completed-season 2025 nflverse Pigskin expansion checkpoint. It does not create or use a current-season lane.

## Owner Correction

The Phase 29.44 current-season lane recommendation is superseded for this package. For this project, 2025 is treated as a completed historical season. The package continues the Phase 29 completed-season historical lane and excludes `phase-29-44-2025-current-season-lane-decision-report.md`.

No BigQuery writes, raw backfill, staging materialization, advanced metrics materialization, Pigskin packet refresh, packet-display repair, ranking build, deploy, feature flag change, Cloud Run Job trigger, Scheduler job, LLM-backed action, Pigskin prompt, scrape, external fetch, Firebase artifact, or unrelated backlog commit belongs to this phase.

## Final 2025 Expansion State

Latest committed checkpoint before this package: `3c83af6 Expand nflverse Pigskin packets through 2024`.

The 2014-2025 historical Pigskin lane is now populated through the 2025 completed season:

- 2025 source metric version: `nflverse_adv_metrics_v0_2025_001`
- 2025 packet version: `nflverse_pigskin_packet_v0_2025_001`
- `pigskin_player_context_packet_current`: 4,084 total rows
- `compat_pigskin_player_context_current`: 4,084 total rows
- 2025 packet rows: 510
- 2026+ nflverse rows: 0

## Raw 2025 Row Counts

| Table | 2025 rows | 2026+ rows |
| --- | ---: | ---: |
| `raw_nflverse_schedules` | 285 | 0 |
| `raw_nflverse_rosters` | 3,134 | 0 |
| `raw_nflverse_rosters_weekly` | 46,831 | 0 |
| `raw_nflverse_weekly` | 19,399 | 0 |
| `raw_nflverse_pbp` | 48,771 | 0 |
| `raw_nflverse_snap_counts` | 26,612 | 0 |

## Staging 2025 Row Counts

| Table | 2025 rows | 2026+ rows |
| --- | ---: | ---: |
| `stg_player_identity` | 46,831 | 0 |
| `stg_game_context` | 285 | 0 |
| `stg_player_week_stats` | 19,399 | 0 |
| `stg_team_week_stats` | 570 | 0 |
| `stg_play_player_events` | 116,369 | 0 |
| `stg_participation_context` | 26,612 | 0 |

Known staging warning: `stg_participation_context` has 80 documented 2025 identity gaps from PFR-based snap-count matching. These are flagged in `missing_data_flags`; they are not hidden or coerced.

## Advanced Metrics 2025 Row Counts

| Table | 2025 rows | 2026+ rows |
| --- | ---: | ---: |
| `player_week_advanced_metrics` | 19,399 | 0 |
| `team_week_context_metrics` | 570 | 0 |
| `qb_week_environment_metrics` | 692 | 0 |

Blocked route, red-zone, high-value-touch, reception-flag, pressure, contact-yards, and alignment metrics remain intentionally unavailable in v0 where nflverse source coverage does not support them safely.

## Packet Row Counts

| Season | Packet rows |
| --- | ---: |
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
| **Total** | **4,084** |

2025 packet integrity checks:

| Check | Result |
| --- | ---: |
| Target packet-version rows | 510 |
| 2026+ packet rows | 0 |
| Duplicate 2025 packet grain count | 0 |
| Missing 2025 packet JSON | 0 |
| Missing 2025 packet text | 0 |
| Missing 2025 source freshness | 0 |
| Missing 2025 blocked metric flags | 0 |

## Week 22 And Postseason-Inclusive Warning

The 2025 packet refresh includes 17 Week 22 rows. These rows are historical/postseason packet rows only. They are not current-season content, and no current-season wording should be applied when exposing them.

## 2026+ Separation

All packaged 2025 evidence confirms 2026+ separation:

- raw 2026+ rows: 0
- staging 2026+ rows: 0
- advanced metrics 2026+ rows: 0
- packet 2026+ rows: 0

## Tyreek Hill Historical-vs-2026 Roster Note

The 2025 lane uses historical nflverse rows and packet candidates from the completed 2025 source slice. Tyreek Hill resolution is historical to the 2025 packet evidence. Do not infer or overwrite any later 2026 roster state from this package.

`Tyreek Hill` remains a known ambiguous compact-display lookup because packet display names include two `T.Hill` candidates. The safe lookup is explicit disambiguation such as `--team MIA --position WR` or a player ID.

## Display-Name Ambiguity Warning

Known abbreviated display-name collisions remain. Ambiguous lookups require explicit `--team`, `--position`, or `--player-id` disambiguation before a single packet is selected.

Examples documented in Phase 29.49 include `T.Hill`, `J.Williams`, `K.Williams`, `T.Johnson`, `B.Allen`, `J.Johnson`, `K.Allen`, `M.Evans`, `R.Wilson`, `B.Robinson`, `D.Moore`, `J.Wright`, and `T.Etienne`.

## Blocked Metrics Summary

Packet JSON carries blocked metric flags for:

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

These blocked metrics should remain visible to Pigskin context consumers so unavailable inputs are not mistaken for zero values.

## Reports Intended For Commit

Commit only these 2025 package files:

- `docs/rebuild/validation/phase-29-45-raw-backfill-2025-report.md`
- `docs/rebuild/validation/phase-29-46-staging-materialization-2025-report.md`
- `docs/rebuild/validation/phase-29-47-advanced-metrics-2025-report.md`
- `docs/rebuild/validation/phase-29-48-pigskin-packet-dry-run-2025-report.md`
- `docs/rebuild/validation/phase-29-49-pigskin-packets-2025-report.md`
- `docs/rebuild/validation/phase-29-50-2025-expansion-release-package.md`

## Files Intentionally Excluded

Do not commit:

- `docs/rebuild/validation/phase-29-44-2025-current-season-lane-decision-report.md`
- unrelated historical Phase 17-28 backlog
- unrelated Phase 29 reports outside the approved 2025 package
- source files
- logs
- caches
- local output folders
- temporary JSON
- deployment artifacts
- browser evidence
- secrets or environment files

## Known Warnings

- 2025 includes Week 22 historical/postseason rows. Treat them as completed-season historical context.
- 22 packet rows carry expected packet warnings, mostly sample-size, null snap-share, or missing QB environment sample notes.
- Known abbreviated display-name collisions remain.
- `stg_participation_context` has 80 documented 2025 identity gaps from PFR-based snap-count matching.
- `raw_nflverse` validation keeps an informational 2014-2025 coverage-review warning.
- `trade_pick_scores` validation keeps the existing informational model-version warning.

## Next Recommended Phase

Recommended next phase after a successful commit:

- Phase 30.1: post-expansion Pigskin integration/readiness review.
- Or an owner-approved release review for how the completed 2014-2025 packet warehouse should be exposed to Pigskin.
