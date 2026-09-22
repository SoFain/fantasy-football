# team_news_items Contract

Base SQL: [bigquery/migrations/0044__player_status_watch.sql](../migrations/0044__player_status_watch.sql)

Written by [src/detect_player_changes.py](../../src/detect_player_changes.py) via [src/team_news_feeds.py](../../src/team_news_feeds.py).

## Purpose

Beat-writer feed items pulled for teams that had a triggering player change.

These are SB Nation team blogs. They are commentary, not an authoritative injury source. Treat an item as context for investigating a flag, never as the flag itself. The authoritative status is whatever Sleeper reports in `sleeper_players_history`.

## Required Grain

One row per `(fetched_at, team, item_url)`.

## Fetch Policy

Feeds are fetched per affected team, not per affected player. A day where one team places six players on the injury report costs one request; the worst possible day costs 32. A day with no triggering changes costs zero.

A team change fetches both the old and new team feed, since either beat writer may have the transaction story.

## Required Fields

- `fetched_at`
- `team`
- `item_url`
- `title`

## Notes

- A feed that fails to fetch or parse yields no rows for that team and does not fail the run.
- Items older than seven days are dropped. Beat coverage of a status change lands within a day or two.
- Items with no parseable timestamp are kept. A missing date is more likely a feed quirk than an old article.

## Partitioning

Partitioned by `DATE(fetched_at)`, clustered by `team`, `published_at`.
