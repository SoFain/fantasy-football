# coaching_staff_current Contract

Base SQL: [bigquery/migrations/0045__coaching_staff.sql](../migrations/0045__coaching_staff.sql)

Written by [src/ingest_coaching_staff.py](../../src/ingest_coaching_staff.py) from [data/coaching_staff.csv](../../data/coaching_staff.csv).

## Purpose

Current NFL coaching staff for all 32 teams, giving agents up-to-date coaching context alongside player data. This is the **first coaching layer: current staff only.** Coaching styles and historical records are deliberately later layers and are not modeled here.

Eight roles per team: head coach, senior assistant, offensive coordinator, defensive coordinator, quarterbacks coach, running backs coach, wide receivers coach, offensive line coach.

## Required Grain

One row per `(team_abbr, role)`. Fully populated the table is 32 teams x 8 roles = 256 rows. The ingest always emits the full grid; a team/role with no coach is emitted as vacant rather than dropped, so a consumer can tell "no coach listed" from "team not covered".

## Source and Curation

Sourced from the Wikipedia [List of current NFL staffs](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Football_League/List_of_current_NFL_staffs) page, which transcludes 32 separate per-team templates.

The data is **curated through a CSV, not scraped live.** The source is 32 templates with inconsistent role labels (a "Senior assistant" on one team is an "Assistant head coach" on another, sometimes combined with another title), and shipping a wrong "current" coach to agents is worse than shipping a known gap. `data/coaching_staff.csv` is the reviewable source of truth; updating a staff is a CSV edit and a re-run of `ingest-coaching-staff`.

## Verification Status

Every row carries `verification_status`, one of:

- `pending` — seeded structure or unconfirmed data. The default.
- `verified` — confirmed against the live source by a human or a checked process.

A populated row that is still `pending` is real data awaiting confirmation, flagged `unverified` in `missing_fields_json`. A row with no `coach_name` is flagged `missing_coach_name` and `is_vacant = true`. This keeps unverified seed data from being mistaken for confirmed data downstream.

## Required Fields

- `snapshot_at`
- `team_abbr`
- `team_name`
- `role`
- `role_title`
- `role_rank`
- `is_vacant`
- `verification_status`

## Consumers

The coaching staff XML feed ([src/coaching_staff_feed.py](../../src/coaching_staff_feed.py)) renders this table for inclusion in the platform's agent-facing feeds, listed under the feed manifest. See [docs/rebuild/coaching-staff-layer.md](../../docs/rebuild/coaching-staff-layer.md).

## Partitioning

Clustered by `team_abbr`, `role_rank`. Not partitioned: the table is a small current-state reference (256 rows), refreshed by full truncate. `snapshot_at` is present so a history table can be added later without reshaping this one.
