# Phase 29.25 2016-2017 Packet Identity Release Package

Date: 2026-06-29

Final package status: **READY FOR COMMIT WITH WARNINGS**

## Scope

This package locks in the 2016-2017 nflverse Pigskin packet expansion evidence and the Phase 29.24 packet identity/display-name lookup fix.

No new warehouse writes, packet refreshes, packet-display repair, raw backfill, staging materialization, advanced metrics materialization, deploys, Cloud Run Job triggers, LLM actions, Pigskin prompts, scraping, rankings builds, or feature-flag changes were run in this packaging phase.

Latest committed checkpoint before packaging:

```text
67f37e7 Expand nflverse Pigskin pipeline to 2015
```

## Authorization Gate State

All relevant gates were unset:

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

## Final 2016-2017 Expansion State

The warehouse now contains 2014-2017 nflverse raw, staging, base advanced metrics, and Pigskin packet current rows. Phase 29.25 did not change those rows.

Packet table/view totals:

| Object | Total rows |
| --- | ---: |
| `pigskin_player_context_packet_current` | 1,587 |
| `compat_pigskin_player_context_current` | 1,587 |

Packet table by season:

| Season | Packet rows |
| --- | ---: |
| 2014 | 482 |
| 2015 | 498 |
| 2016 | 128 |
| 2017 | 479 |

Duplicate packet grain count for 2016-2017: `0`.

## Raw 2016-2017 Row Counts

| Table | 2016 rows | 2017 rows |
| --- | ---: | ---: |
| `raw_nflverse_schedules` | 267 | 267 |
| `raw_nflverse_rosters` | 3,061 | 3,082 |
| `raw_nflverse_rosters_weekly` | 35,020 | 51,321 |
| `raw_nflverse_weekly` | 17,531 | 17,456 |
| `raw_nflverse_pbp` | 47,651 | 47,245 |
| `raw_nflverse_snap_counts` | 23,890 | 23,862 |

## Staging 2016-2017 Row Counts

| Table | 2016 rows | 2017 rows |
| --- | ---: | ---: |
| `stg_player_identity` | 35,020 | 51,321 |
| `stg_game_context` | 267 | 267 |
| `stg_player_week_stats` | 17,531 | 17,456 |
| `stg_team_week_stats` | 534 | 534 |
| `stg_play_player_events` | 117,281 | 114,910 |
| `stg_participation_context` | 23,890 | 23,862 |

## Advanced Metrics 2016-2017 Row Counts

| Table | 2016 rows | 2017 rows |
| --- | ---: | ---: |
| `player_week_advanced_metrics` | 17,531 | 17,456 |
| `team_week_context_metrics` | 534 | 534 |
| `qb_week_environment_metrics` | 636 | 628 |

## Identity and Display-Name QA Findings

Phase 29.24 confirmed the packet display-name issue was caused by abbreviated nflverse-derived names, not missing player IDs.

### Julio Jones

`Julio Jones` exists in the packet slice as `Ju.Jones`, WR, ATL, `00-0027944`. The prior full-name lookup generated `juliojones` and `jjones`, but not `jujones`.

The lookup now includes first-two-letter abbreviation variants, so `--player-name "Julio Jones"` resolves to the existing `Ju.Jones` packet candidate.

### David Johnson

`David Johnson` exists in the packet slice as `Da.Johnson`, RB, ARI, `00-0032187`.

The abbreviated `D.Johnson` display name is collision-prone. Phase 29.24 found `D.Johnson` rows across multiple player IDs, teams, and positions. The lookup now reports ambiguity for `--player-name "David Johnson"` when multiple candidates are present and supports disambiguation with `--team`, `--position`, or `--player-id`.

## Source and Test Changes from Phase 29.24

| File | Change |
| --- | --- |
| `src/nflverse_pigskin_packets.py` | Added first-two-letter name variants, `--team`, `--player-id`, lookup diagnostics, no-match warnings, ambiguity warnings, and generic warning text without stale Phase 29.11/29.12 labels. |
| `tests/test_nflverse_pigskin_packets.py` | Added tests for first-two-letter abbreviation lookup, team/position/player ID disambiguation, ambiguous lookup warnings, and current warning text. |

## Reports Intended for Commit

| File | Purpose |
| --- | --- |
| `docs/rebuild/validation/phase-29-20-raw-backfill-2016-2017-report.md` | Evidence for authorized 2016-2017 raw nflverse backfill. |
| `docs/rebuild/validation/phase-29-21-staging-materialization-2016-2017-report.md` | Evidence for authorized 2016-2017 staging materialization. |
| `docs/rebuild/validation/phase-29-22-advanced-metrics-2016-2017-report.md` | Evidence for authorized 2016-2017 base advanced metrics materialization. |
| `docs/rebuild/validation/phase-29-23-pigskin-packets-2016-2017-report.md` | Evidence for authorized 2016-2017 Pigskin packet refresh. |
| `docs/rebuild/validation/phase-29-24-pigskin-packet-identity-display-qa-report.md` | Evidence for packet identity/display-name QA and lookup fix. |
| `docs/rebuild/validation/phase-29-25-2016-2017-packet-identity-release-package.md` | This release-package summary. |

Source/test files intended for commit:

| File | Purpose |
| --- | --- |
| `src/nflverse_pigskin_packets.py` | Lookup/display-name safety fix. |
| `tests/test_nflverse_pigskin_packets.py` | Regression coverage for lookup/display-name behavior. |

## Files Intentionally Excluded

The remaining historical validation backlog remains untracked and excluded unless the owner explicitly asks for a broader chronology commit.

Excluded categories:

- Phase 17 through Phase 28 historical validation reports not listed above.
- Superseded Phase 29 reports outside the 2016-2017 packet package.
- `output/`, Playwright/browser evidence, local QA JSON, proxy files, logs, caches, `.env` files, secret JSON files, Codex caches, deployment artifacts.

## Known Warnings

- Existing packet rows still store abbreviated display names such as `Ju.Jones` and `Da.Johnson`. Phase 29.24 fixed lookup and diagnostics, not stored display values.
- `David Johnson` remains ambiguous without `--team`, `--position`, or `--player-id`. This is expected because abbreviated names collide in the source packet data.
- Raw nflverse validation includes an informational coverage warning.
- Trade pick score model-version validation includes an informational model-version coverage warning.

## Next Recommended Phase

Phase 29.26: authorized 2018-2020 raw backfill, or 2018-only if the owner wants a more conservative season-by-season cadence.

