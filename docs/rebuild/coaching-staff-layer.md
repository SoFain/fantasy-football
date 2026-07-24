# Coaching Staff Layer

The first layer of coaching context: **current staff only.** Coaching styles and historical records are deliberately later layers and are not built yet.

Status 2026-07-24: **live.** `data/coaching_staff.csv` is populated from the Wikipedia source (242 verified coaches, 14 true vacancies), `coaching_staff_current` is loaded and validated (151-155), the immutable dataset object is published to the public bucket, and `v1/manifest.json` lists it under `datasets.coaching_staff` via the ranking publisher's new `--dataset-entry` flag. Refresh path: edit or re-run `scripts/populate_coaching_staff_csv.py --write`, then `ingest-coaching-staff`, `coaching-staff-feed --publish-feed`, then republish the manifest.

Gives agents up-to-date coaching context alongside player data: for each of the 32 teams, eight roles — head coach, senior assistant, offensive coordinator, defensive coordinator, quarterbacks coach, running backs coach, wide receivers coach, offensive line coach.

## Pieces

| Piece | Location |
| --- | --- |
| Table | `coaching_staff_current`, [migration 0045](../../bigquery/migrations/0045__coaching_staff.sql), [contract](../../bigquery/contracts/coaching_staff_current.md) |
| Roles, teams, rendering | [src/coaching_staff.py](../../src/coaching_staff.py) |
| Curated data | [data/coaching_staff.csv](../../data/coaching_staff.csv) |
| Ingest job | `ingest-coaching-staff`, [src/ingest_coaching_staff.py](../../src/ingest_coaching_staff.py) |
| Feed job | `coaching-staff-feed`, [src/coaching_staff_feed.py](../../src/coaching_staff_feed.py) |
| Validations | `bigquery/validations/151`–`155` |

## Data source and why it is curated

Sourced from the Wikipedia [List of current NFL staffs](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Football_League/List_of_current_NFL_staffs). That page transcludes 32 separate per-team templates whose role labels are inconsistent (a "Senior assistant" on one team is an "Assistant head coach" on another, sometimes fused with another title). Scraping it reliably is not worth the risk when the alternative — a small, reviewed CSV — is both more accurate and easy to keep current.

`data/coaching_staff.csv` is the reviewable source of truth. Updating a staff is a CSV edit plus a re-run of `ingest-coaching-staff`. Every row carries `source`, `source_url`, `snapshot_at`, and a `verification_status` (`pending` until confirmed) so unverified seed data is never mistaken for confirmed data.

The shipped CSV is the full 32×8 grid with names **empty** (`verification_status = pending`). It was seeded structure-only on purpose: shipping coach names from memory as "current" context risks feeding agents wrong data. Populate `coach_name` from the source page, set `verification_status = verified`, and re-run.

```bash
python -m src.job_runner --job-name ingest-coaching-staff
```

## Feed integration

The platform's public feed is **JSON, content-addressed**, published to the Cloud Storage bucket the ranking project owns:

`https://storage.googleapis.com/fantasy-football-498121-public-rankings/v1/manifest.json`

Immutable objects live at `v1/.../sha256-<digest>.json`; the single mutable `v1/manifest.json` is rebuilt in full by `scripts/publish_public_rankings.py` in the ranking project (the main `E:\Fantasy Football` checkout, not this branch).

`coaching-staff-feed` therefore does exactly two things and **never touches the manifest** (writing it here would wipe the ranking profiles):

1. Builds the coaching staff dataset object at `v1/datasets/coaching_staff/sha256-<digest>.json` and writes it locally. With `--publish-feed`, it uploads that immutable object to Cloud Storage.
2. Emits a manifest entry — field-compatible with the ranking board entries (`sha256`, `bytes`, `object`, `url`, `source_generated_at`, `warnings`) — as `build/feeds/coaching_staff.manifest-entry.json`.

```bash
python -m src.job_runner --job-name coaching-staff-feed              # local artifacts only
python -m src.job_runner --job-name coaching-staff-feed --publish-feed   # + upload immutable object
```

### Handoff to the ranking publisher

To list coaching staff in the live manifest, the ranking project's `publish_public_rankings.py` must merge this entry into its manifest build under a new `datasets` key (a sibling of `profiles`), so the manifest gains:

```json
{ "profiles": { ... }, "datasets": { "coaching_staff": { ...entry... } } }
```

This is the only cross-repo step. It is deliberately left to the publisher because that script is the single writer of the mutable manifest; two writers would race and clobber each other.

## Repository divergence note

This branch was forked from an old state (24 migrations). The main `E:\Fantasy Football` checkout has diverged well ahead of it: 43 applied migrations, the JSON feed publisher, and the unified ranking tables, none of which are on this branch. The coaching staff **table and data are integrated at the warehouse level** (shared BigQuery), so the ranking publisher can read `coaching_staff_current` today regardless of branch. The **code** in this branch still needs to be reconciled with main. Migration numbers here start at 0044 to sit above the live ledger's max of 0043 and avoid colliding with the main line's migrations.

## Future layers

- Coaching styles: tendencies, scheme, pace, aggressiveness, derived from play-by-play and tracked per coach.
- Historical records: coach win/loss, tenure, prior stops, and coordinator lineage over time. The `snapshot_at` column is already present so a history table can be added without reshaping the current table.
