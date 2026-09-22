# nflverse Historical Backfill Plan

Status: design only. Do not run this plan without a separate authorization phase.

## Goal

Build a 10-plus-year nflverse historical feature warehouse without scraping and without repairing the old 2025-only source shape in place.

## Backfill Order

1. Apply additive schema migration `0027__nflverse_historical_feature_warehouse.sql`.
2. Run object and metadata validations for raw, staging, feature, and compatibility objects.
3. Inspect nflreadpy source schemas locally for the selected source families.
4. Backfill identity and schedule sources first: players, fantasy IDs, teams, schedules, rosters, and weekly rosters.
5. Backfill high-volume play and weekly stat sources in bounded season batches.
6. Backfill support sources: team stats, snap counts, participation, injuries, depth charts, NGS, FTN charting, and draft picks.
7. Build canonical staging tables from raw tables.
8. Build derived feature marts.
9. Build current Pigskin packets only after feature validation passes.

## Source-Family Batching

Recommended backfill batches:

- identity and schedule sources: 1999 through current season, one source family at a time;
- play-by-play and weekly stats: two or three seasons per batch until query cost is understood;
- NGS and FTN: source-supported seasons only;
- participation: schema-inspection phase first, then bounded season batches;
- current-season weekly refresh: explicit `season`, `week-start`, and `week-end` only after the future pipeline supports week bounds.

## Future Authorization Gates

The future write phases should use separate gates:

- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL=true`;
- `ALLOW_NFLVERSE_WEEKLY_REFRESH=true`;
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION=true`;
- `ALLOW_PIGSKIN_PACKET_REFRESH=true`.

These gates must be scoped to the same command process that performs the authorized action and removed afterward.

## Weekly Refresh Flow

1. Plan impacted season/week range.
2. Refresh raw source families for only the impacted weeks.
3. Rebuild affected staging partitions.
4. Rebuild affected feature partitions.
5. Refresh current Pigskin packets only after validation.
6. Run source freshness and missing-flag validations.

## Cloud Run Job Design

Future jobs should be split by action:

- `backfill-nflverse-historical`;
- `refresh-nflverse-weekly`;
- `materialize-advanced-metrics`;
- `refresh-pigskin-context-packets`.

Each job needs a dry-run mode, explicit season bounds, explicit source-family selection, source-refresh metadata, and a refusal path for unbounded writes.

## Scheduler Policy

Scheduler remains disabled until each job has passed a separate live proof. No Scheduler job should be created as part of schema scaffolding.

## Replacement-Over-Repair Policy

Do not mutate the legacy source role in place. Build raw `raw_nflverse_*` tables, canonical staging tables, feature marts, then compatibility views. Only after validation should runtime code move away from legacy tables.

## Blocked Metrics

The following metrics are blocked until true sources are inspected and contracted:

- route share;
- first-read share;
- true pressure rate;
- alignment splits;
- contact yards.

Snap counts, FTN charting, and NGS fields can inform adjacent context, but they must not be relabeled as true route or true pressure data.

## No Rankings Yet

This plan does not build rankings. Rankings require a later model and calibration phase after historical features are backfilled and validated.
