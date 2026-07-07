# Pigskin Advanced Metrics Warehouse

Status: Completed under Phase 33.15. Data is fully populated and validated for seasons 2014-2025 under metric_version 'advanced_player_metrics_v0'.

## Purpose

Pigskin needs read-only, source-labeled advanced metrics with enough history to support player context, trend discussion, and future model calibration.

## Warehouse Layers

### Raw nflverse

`raw_nflverse_*` tables preserve source data from nflreadpy. They are raw/source tables and are not Pigskin or UI safe.

### Canonical Staging

Staging tables normalize player identity, game context, player-week stats, team-week stats, play-player events, and participation context. They are internal only.

### Feature Marts

Feature marts hold derived player-week metrics, team context, QB environment, recent metrics, and current role usage. They must include `metric_version`, `feature_run_id`, source freshness, and missing-data flags.

### Pigskin Packets

`pigskin_player_context_packet_current` stores deterministic current packets. `compat_pigskin_player_context_current` is the future safe read surface for Pigskin and Streamlit.

## Compatibility Boundary

The compatibility view must not directly read:

- `raw_nflverse_*`;
- `play_by_play`;
- `weekly_metrics`;
- `ngs_*`;
- `ftn_charting`;
- `weekly_snap_counts`;
- `injury_reports`;
- `depth_charts`;
- `source_*`;
- `raw_*`.

Pigskin should receive context through named tools and compatibility views, not arbitrary SQL.

## Metric Families

Initial feature marts should support:

- target share, air-yards share, WOPR, aDOT, RACR;
- weighted opportunity, carry share, opportunity share;
- red-zone touches, inside-10 and inside-5 usage;
- EPA per opportunity, success rate, CPOE where valid;
- snap share, injury status, depth role;
- team pace, neutral pass rate, pass rate over expected;
- opponent context and game environment flags.

## Blocked Labels

Do not populate or label route share unless a true route source exists. Do not publish pressure metrics unless a true pressure source exists. Missing or blocked fields must remain null and flagged.

## Feature Versions

Every mart row needs `metric_version` and `feature_run_id`. Packet rows need `packet_version` and `feature_run_id`.

## Rollout Path

1. Add schema and contracts.
2. Apply migration in a separate authorized phase.
3. Backfill raw tables in bounded batches.
4. Validate coverage and metadata.
5. Build staging tables.
6. Build feature marts.
7. Refresh Pigskin packets.
8. Wire Pigskin to compatibility views only after staging validation.

## Production Exposure

No production feature flag changes are part of Phase 29.3. Production Pigskin remains on the existing safe context surface until a later rollout approves the new packet path.
