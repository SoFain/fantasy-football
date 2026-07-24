# player_news_matches Contract

Base SQL: [bigquery/migrations/0025__player_status_watch.sql](../migrations/0025__player_status_watch.sql)

Written by [src/detect_player_changes.py](../../src/detect_player_changes.py).

## Purpose

Links a news item to the changed players it mentions, carrying the change that triggered the fetch. This is the join that answers "a flag appeared on this player, what is the team feed saying about them".

## Required Grain

One row per `(fetched_at, item_url, sleeper_player_id)`.

## Matching Rule

Full-name match against the item title and summary, after normalizing case, accents, punctuation, and generational suffixes.

Last-name matching is deliberately not used. Surnames like Smith and Williams appear constantly on a team blog and would produce far more false positives than real matches. Single-word names, such as a team defense entry, are ignored for the same reason.

Apostrophes are removed rather than spaced during normalization, so a feed writing "JaMarr Chase" still matches the roster's "Ja'Marr Chase".

## Required Fields

- `fetched_at`
- `team`
- `sleeper_player_id`
- `item_url`

## Notes

- `trigger_field`, `trigger_old_value`, and `trigger_new_value` record why the fetch happened, so a match can be evaluated against the change it was meant to explain.
- Absence of a match is meaningful: a flag with no matching coverage means the beat has not written about it yet, not that the flag is wrong.

## Partitioning

Partitioned by `DATE(fetched_at)`, clustered by `team`, `sleeper_player_id`.
