# sleeper_players_history Contract

Base SQL: [bigquery/migrations/0044__player_status_watch.sql](../migrations/0044__player_status_watch.sql)

Written by [src/ingest_news.py](../../src/ingest_news.py).

## Purpose

Append-only history of the daily Sleeper global player snapshot.

`sleeper_players_current` is written `WRITE_TRUNCATE` and therefore holds only the latest state. That makes day-over-day change detection impossible: yesterday's rows are gone by the time the next run reads them. This table keeps every snapshot so two consecutive runs can be diffed.

Both tables are written in the same run, history first. `sleeper_players_current` is unchanged and all of its existing consumers are unaffected.

## Required Grain

One row per player per snapshot: `(snapshot_at, sleeper_player_id)`.

## Required Fields

- `snapshot_at`
- `sleeper_player_id`
- `player_name`
- `position`
- `team`
- `status`
- `injury_status`
- `depth_chart_position`
- `depth_chart_order`
- `active`
- `birth_date`
- `age`

## Fetch Policy

The source is `GET /v1/players/nfl?active=true`. Sleeper documents this endpoint as "once per day at most" and roughly 5MB, so `src/ingest_news.py` is its single caller and every other job reads the saved snapshot. `active=true` returns only active players and a smaller payload, so every row here has `active = true`.

`src/ingest_news.py` also guards the call: if a snapshot already exists for the current date it skips the fetch, so a manual re-run or retry cannot exceed one call per day. Pass `--force` to override.

## Field Authority

Sleeper wins on conflict with nflreadpy for `team`, `status`, and biographical fields including `birth_date`. nflreadpy fills gaps only.

This is a deliberate choice for freshness over stability. Sleeper updates daily and reflects mid-season moves and rookie signings that the seasonal nflreadpy roster load misses entirely. The tradeoff is that Sleeper data-entry noise can move a player's age or team, which then propagates into the identity bridge and the age-curve formulas. Conflicts are recorded rather than silently absorbed so they can be reviewed.

## Partitioning

Partitioned by `DATE(snapshot_at)`, clustered by `sleeper_player_id`, `team`, `position`.

## Notes

- Age is computed from `birth_date` at snapshot time. A missing or unparseable birth date yields a null age, never a zero: a wrong age is worse than a missing one for the dynasty and value curves.
- Retention is unbounded today. Snapshot rows are small, but a retention policy should be added before this table grows past a season or two.
