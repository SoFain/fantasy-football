# player_status_changes Contract

Base SQL: [bigquery/migrations/0044__player_status_watch.sql](../migrations/0044__player_status_watch.sql)

Written by [src/detect_player_changes.py](../../src/detect_player_changes.py).

## Purpose

One row per player attribute that changed between the two most recent Sleeper snapshots. This is the signal that drives injury investigation and team news lookups.

## Required Grain

One row per `(detected_at, sleeper_player_id, field_name)`.

## Watched Fields

`team`, `status`, `injury_status`, `depth_chart_position`, `depth_chart_order`.

## News Triggers

`triggers_news_check` is true only for `injury_status`, `team`, and `depth_chart_order` — the injury / team / depth-chart set. It is deliberately narrower than the watched set:

- `status` alone flips on routine roster paperwork.
- `depth_chart_position` alone flips on positional relabeling, not on a real role change.

`active` is not tracked. The Sleeper players endpoint is called with `?active=true`, so every row is active and the field never varies; a player leaving the active set drops out of the snapshot rather than flipping a value.

## Required Fields

- `detected_at`
- `sleeper_player_id`
- `field_name`
- `triggers_news_check`

## Notes

- A player absent from the previous snapshot produces no rows. A first sighting is not a change, and emitting one would flood the table on the first run and whenever Sleeper adds a batch of players.
- Null and empty string are treated as the same value. Sleeper flips between them constantly, and treating that as a change would produce noise every day.
- `previous_team` is populated on every row so a team change can be traced without a self-join.

## Partitioning

Partitioned by `DATE(detected_at)`, clustered by `field_name`, `team`, `sleeper_player_id`.
