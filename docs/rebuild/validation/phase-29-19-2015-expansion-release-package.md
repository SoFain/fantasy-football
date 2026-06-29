# Phase 29.19 - 2015 nflverse Pigskin Expansion Release Package

Date: 2026-06-29

Final package status: READY FOR COMMIT REVIEW

## Expansion State

The 2015 nflverse Pigskin expansion is complete through historical packet materialization.

Checkpoint:

- Base commit before expansion package: `4805610 Build nflverse Pigskin canary pipeline`
- 2014 Pigskin packet rows: 482
- 2015 Pigskin packet rows: 498
- `pigskin_player_context_packet_current`: 980 total rows
- `compat_pigskin_player_context_current`: 980 total rows
- 2015 metric version: `nflverse_adv_metrics_v0_2015_001`
- 2015 packet version: `nflverse_pigskin_packet_v0_2015_001`

No production deploy, staging deploy, feature flag change, Cloud Run Job trigger, Scheduler job, LLM-backed action, Pigskin prompt, scrape, Firebase artifact, ranking build, or new materialization belongs in this package phase.

## Warehouse Evidence

Raw 2015 rows:

| Table | 2015 Rows |
| --- | ---: |
| `raw_nflverse_schedules` | 267 |
| `raw_nflverse_rosters` | 2,189 |
| `raw_nflverse_rosters_weekly` | 30,201 |
| `raw_nflverse_weekly` | 17,592 |
| `raw_nflverse_pbp` | 48,122 |
| `raw_nflverse_snap_counts` | 23,842 |

Staging 2015 rows:

| Table | 2015 Rows |
| --- | ---: |
| `stg_player_identity` | 30,201 |
| `stg_game_context` | 267 |
| `stg_player_week_stats` | 17,592 |
| `stg_team_week_stats` | 534 |
| `stg_play_player_events` | 118,069 |
| `stg_participation_context` | 23,842 |

Advanced metrics 2015 rows:

| Table | 2015 Rows |
| --- | ---: |
| `player_week_advanced_metrics` | 17,592 |
| `team_week_context_metrics` | 534 |
| `qb_week_environment_metrics` | 618 |

Packet rows:

| Object | Total Rows | 2014 Rows | 2015 Rows |
| --- | ---: | ---: | ---: |
| `pigskin_player_context_packet_current` | 980 | 482 | 498 |
| `compat_pigskin_player_context_current` | 980 | 482 | 498 |

2015 duplicate packet grains: 0.

## Source and Test Changes

Phase 29.18 found and fixed a stale packet text label:

- Before: packet text was hardcoded as `as of 2014 week`.
- After: packet text uses the row `as_of_season`.

Files:

- `src/nflverse_pigskin_packets.py`
- `tests/test_nflverse_pigskin_packets.py`

Test coverage added:

- Write SQL does not include hardcoded `as of 2014 week`.
- Write SQL includes dynamic `as_of_season` text construction.
- Dry-run packet preview text uses the row season.

## Reports Included

Commit candidates:

- `docs/rebuild/validation/phase-29-14-historical-expansion-planner-report.md`
- `docs/rebuild/validation/phase-29-15-raw-backfill-2015-report.md`
- `docs/rebuild/validation/phase-29-16-staging-materialization-2015-report.md`
- `docs/rebuild/validation/phase-29-17-advanced-metrics-2015-report.md`
- `docs/rebuild/validation/phase-29-18-pigskin-packets-2015-report.md`
- `docs/rebuild/validation/phase-29-19-2015-expansion-release-package.md`

Source/test commit candidates:

- `src/nflverse_pigskin_packets.py`
- `tests/test_nflverse_pigskin_packets.py`

## Files Intentionally Excluded

Excluded unless the owner explicitly asks for a broader chronology:

- Historical Phase 17 through Phase 28 validation backlog
- Older Phase 29 reports outside the 2015 expansion checkpoint
- Local browser evidence
- `output/`
- logs
- caches
- env files
- secret JSON files
- deployment artifacts

## Known Warnings

- Route metrics remain blocked.
- Pressure, sack, and scramble metrics remain blocked.
- Pass rate over expected remains null.
- Red-zone and high-value-touch metrics remain blocked.
- Some 2015 packet rows carry missing snap-share or sample-size warnings.
- Raw nflverse validation reports a 2014-2015 coverage span as an informational review item.
- Trade pick score validations still report the existing 64-row `trade_pick_score_v0_2026_001` informational review warning.

## Next Recommended Phase

Phase 29.20 should run an authorized 2016-2017 raw backfill planner/write gate, or a 2016-only raw backfill if the owner wants to keep the one-season cadence.

Do not rerun 2015 raw, staging, advanced metrics, or Pigskin packet materialization unless a later phase explicitly asks for a bounded idempotency test.
