# Phase 29.37 - 2021-2023 Expansion Release Package

Final package decision: **2021-2023 NFLVERSE PIGSKIN EXPANSION READY TO COMMIT WITH WARNINGS**

This package locks in the 2021-2023 nflverse Pigskin expansion checkpoint after the bounded raw backfill, staging materialization, advanced metrics materialization, packet dry-run, and authorized packet refresh.

No BigQuery write, raw backfill, staging materialization, advanced metric materialization, Pigskin packet materialization, packet-display repair, ranking build, deployment, feature flag change, Cloud Run Job trigger, Scheduler job, Pigskin prompt, LLM action, scrape, fetch, Firebase artifact, or commit was performed while creating this package report.

## Final 2021-2023 Expansion State

- Latest pre-package checkpoint commit: `db8f279 Expand nflverse Pigskin packets through 2020`.
- 2021-2023 source metric version: `nflverse_adv_metrics_v0_2021_2023_001`.
- 2021-2023 packet version: `nflverse_pigskin_packet_v0_2021_2023_001`.
- `pigskin_player_context_packet_current`: 3,082 rows.
- `compat_pigskin_player_context_current`: 3,082 rows.
- 2021-2023 target packet rows: 746.
- Week 22 packet rows: 21.
- 2021-2023 duplicate packet grain count: 0.
- Production and staging services remained untouched during the expansion phases.

## Raw 2021-2023 Row Counts

| Table | 2021 | 2022 | 2023 | Week range |
| --- | ---: | ---: | ---: | --- |
| `raw_nflverse_schedules` | 285 | 284 | 285 | 1-22 |
| `raw_nflverse_rosters` | 2,960 | 3,133 | 3,089 | season table |
| `raw_nflverse_rosters_weekly` | 46,670 | 46,136 | 45,650 | 1-22 |
| `raw_nflverse_weekly` | 18,947 | 18,809 | 18,621 | 1-22 |
| `raw_nflverse_pbp` | 49,922 | 49,434 | 49,665 | 1-22 |
| `raw_nflverse_snap_counts` | 26,468 | 26,381 | 26,540 | 1-22 |

## Staging 2021-2023 Row Counts

| Table | 2021 | 2022 | 2023 | Week range |
| --- | ---: | ---: | ---: | --- |
| `stg_player_identity` | 46,670 | 46,136 | 45,650 | 1-22 |
| `stg_game_context` | 285 | 284 | 285 | 1-22 |
| `stg_player_week_stats` | 18,947 | 18,809 | 18,621 | 1-22 |
| `stg_team_week_stats` | 570 | 568 | 570 | 1-22 |
| `stg_play_player_events` | 121,589 | 119,216 | 120,051 | 1-22 |
| `stg_participation_context` | 26,468 | 26,381 | 26,540 | 1-22 |

## Advanced Metrics 2021-2023 Row Counts

| Table | 2021 | 2022 | 2023 | Week range |
| --- | ---: | ---: | ---: | --- |
| `player_week_advanced_metrics` | 18,947 | 18,809 | 18,621 | 1-22 |
| `team_week_context_metrics` | 570 | 568 | 570 | 1-22 |
| `qb_week_environment_metrics` | 718 | 694 | 718 | 1-22 |

Derived current views after 2021-2023 expansion:

- `player_recent_advanced_metrics_current`: 5,497 rows.
- `player_role_usage_metrics_current`: 5,497 rows.

## Packet 2021-2023 Row Counts

| Table | 2021 | 2022 | 2023 | Total 2021-2023 |
| --- | ---: | ---: | ---: | ---: |
| `pigskin_player_context_packet_current` | 107 | 131 | 508 | 746 |
| `compat_pigskin_player_context_current` | 107 | 131 | 508 | 746 |

Full packet table and view counts:

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
| Total | 3,082 |

## Warnings To Preserve

- 2021-2023 rows are historical and postseason-inclusive through Week 22. They must not be presented as current-season content.
- Display-name collisions are real. Ambiguous names such as `A.Brown`, `D.Johnson`, and `J.Williams` require team, position, or player ID disambiguation.
- Blocked metrics remain intentionally unavailable: route share, yards per route run, targets per route run, first-read share, red-zone usage, high-value touches, touchdown rates, reception-dependent metrics, true pressure, contact yards, and alignment.
- Pass rate over expected remains unavailable.
- `stg_participation_context` retains known PFR snap-count identity gaps, but the 2021-2023 packet refresh had 0 missing identity rows.
- Packet warning payloads are expected for sample-size or missing-metric context.

## Reports Intended For Commit

The Phase 29.37 checkpoint should commit only these reviewed 2021-2023 expansion files:

- `docs/rebuild/validation/phase-29-32-raw-backfill-2021-2023-report.md`
- `docs/rebuild/validation/phase-29-33-staging-materialization-2021-2023-report.md`
- `docs/rebuild/validation/phase-29-34-advanced-metrics-2021-2023-report.md`
- `docs/rebuild/validation/phase-29-35-pigskin-packet-dry-run-2021-2023-report.md`
- `docs/rebuild/validation/phase-29-36-pigskin-packets-2021-2023-report.md`
- `docs/rebuild/validation/phase-29-37-2021-2023-expansion-release-package.md`

## Files Intentionally Excluded

Excluded from this package:

- Historical Phase 17 through Phase 28 validation backlog.
- Earlier Phase 29 checkpoint reports outside the approved 2021-2023 package.
- `output/`, `output/playwright/`, browser evidence, screenshots, temp JSON, logs, caches, `.env`, `.env.*`, secret JSON, Codex cache folders, and deployment artifacts.
- Source files, since the source modules and tests for this lane were already committed before this evidence checkpoint.

## Known Package Warnings

- The package is evidence-only. It documents warehouse state and does not include source code changes.
- The historical validation backlog remains intentionally untracked unless the owner later chooses to archive or commit a fuller chronology.
- This package does not authorize a 2024 or current-season lane.

## Recommended Next Phase

Proceed to **Phase 29.38 - decide whether to run 2024-only raw backfill**.

Keep 2024 separate from the 2025/current-season lane. It should get its own gate, dry-run, write phase, staging materialization, advanced metrics materialization, packet dry-run, packet refresh, and commit checkpoint.
