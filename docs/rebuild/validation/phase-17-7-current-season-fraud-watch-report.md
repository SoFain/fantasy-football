# Phase 17.7 Current-Season Fraud Watch Report

Date: 2026-06-16

Final status: CURRENT-SEASON FRAUD WATCH BLOCKED

Production-content suitability: historical-only

## Purpose

Materialize current-season `analytics_fraud_watch` rows and current-season `fraud_watch_packets`, or document why current-season Fraud Watch is blocked.

No current-season Fraud Watch rows or packets were materialized in this phase.

## Target Season and Week

Checked modern/current targets:

- `season=2025`, `week=1`, `scoring_profile_id=ppr`
- `season=2026`, `week=1`, `scoring_profile_id=ppr`

These targets were selected because prior phases already proved historical packet generation on `2016 week 17`, while current production content needs a modern 2025 or 2026 slice.

## Source Availability

Read-only BigQuery counts:

```text
analytics_fraud_watch:
  row_count: 3638
  min_season: 2014
  max_season: 2016
  min_week: 1
  max_week: 17

analytics_player_weekly_truth:
  row_count: 50635
  min_season: 2014
  max_season: 2016
  min_week: 1
  max_week: 17

weekly_metrics:
  row_count: 52787
  min_season: 2014
  max_season: 2016
  min_week: 1
  max_week: 21

play_by_play:
  row_count: 143402
  min_season: 2014
  max_season: 2016
  min_week: 1
  max_week: 21

analytics_player_fantasy_points_by_profile:
  row_count: 55617
  min_season: 2025
  max_season: 2025
  min_week: 1
  max_week: 18
```

Target slice counts:

```text
analytics_fraud_watch 2025 week 1: 0
analytics_fraud_watch 2026 week 1: 0
analytics_player_weekly_truth 2025 week 1: 0
analytics_player_weekly_truth 2026 week 1: 0
weekly_metrics 2025 week 1: 0
weekly_metrics 2026 week 1: 0
fraud_watch_packets 2025 week 1: 0
fraud_watch_packets 2026 week 1: 0
```

Existing packets:

```text
fraud_watch_packets:
  2016 week 17 ppr: 3 rows

content_briefs where brief_type = fraud_watch_show:
  2016 week 17: 1 row
```

## Upstream Materialization Support

`src/materialize.py` supports Fraud Watch through `materialize_fraud_watch()`, which builds:

```text
analytics_fraud_watch
```

from:

```text
analytics_player_weekly_truth
```

The Fraud Watch SQL filters:

```text
position IN ('QB', 'RB', 'WR', 'TE')
season_type = 'REG'
fantasy_points_ppr >= 8
fraud_score >= 25
```

The current CLI does not expose a bounded `--only fraud-watch` option. The available choices are:

```text
all
player-weekly-truth
pigskin-rankings
```

Dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.materialize --project fantasy-football-498121 --dataset fantasy_football_brain --dry-run --only all
```

Result:

```text
Dry run passed. Estimated bytes processed: 137851965
```

Interpretation:

- SQL shape is valid.
- The materializer can rebuild Fraud Watch from available upstream tables.
- It cannot create 2025 or 2026 Fraud Watch rows until `analytics_player_weekly_truth` and its raw upstream tables contain 2025 or 2026 rows.
- Running the non-dry materializer now would recreate the current historical-only Fraud Watch mart, not current production content.

## Fraud Watch Packet Dry-Runs

Commands:

```powershell
.\venv\Scripts\python.exe -m src.segment_packets --packet-type fraud-watch --season 2025 --week 1 --scoring-profile ppr --dry-run
.\venv\Scripts\python.exe -m src.segment_packets --packet-type fraud-watch --season 2026 --week 1 --scoring-profile ppr --dry-run
```

Results:

```text
[]
[]
```

Interpretation:

- No packet source rows exist for those target slices.
- No rows were written.

## Materialization Result

No materialization was run.

Rows before and after:

| Object | Before | After |
|---|---:|---:|
| `analytics_fraud_watch` 2025 week 1 | 0 | 0 |
| `analytics_fraud_watch` 2026 week 1 | 0 | 0 |
| `fraud_watch_packets` 2025 week 1 | 0 | 0 |
| `fraud_watch_packets` 2026 week 1 | 0 | 0 |
| `content_briefs` `fraud_watch_show` 2025 week 1 | 0 | 0 |
| `content_briefs` `fraud_watch_show` 2026 week 1 | 0 | 0 |

No packet IDs were created.

No content brief IDs were created.

## Blocker

Current-season Fraud Watch is blocked by source freshness and materialization scope:

1. `analytics_fraud_watch` has no 2025 or 2026 rows.
2. `analytics_player_weekly_truth`, the direct Fraud Watch source, has no 2025 or 2026 rows.
3. `weekly_metrics` and `play_by_play`, the core upstream tables for `analytics_player_weekly_truth`, have no 2025 or 2026 rows in the current warehouse state.
4. `analytics_player_fantasy_points_by_profile` has 2025 rows, but the Fraud Watch builder does not use that table as a source.
5. The materializer can validate SQL, but a live rebuild would remain historical-only until the upstream truth source is refreshed with modern seasons.
6. The materializer does not expose a bounded current-week Fraud Watch-only CLI target.

## Validation

Content brief validation:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
```

Result:

```text
11 passed, 0 failed
```

Market validation:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
```

Result:

```text
9 passed, 0 failed
```

## No LLM and No Scraping Confirmation

- No LLM calls were made.
- No scraping occurred.
- No URLs were fetched.
- No Firebase artifacts were created.
- No current-season Fraud Watch rows were fabricated.
- Historical 2016 Fraud Watch packets remain historical-only and must not be presented as current-week production content.

## Required Next Step

To make current-season Fraud Watch production-suitable:

1. Refresh or restore modern `play_by_play` and `weekly_metrics` source rows for the target season and week.
2. Rebuild `analytics_player_weekly_truth` for that modern slice.
3. Rebuild `analytics_fraud_watch`.
4. Confirm `analytics_fraud_watch` has nonzero rows for the target `season/week`.
5. Dry-run `src.segment_packets --packet-type fraud-watch` for that target.
6. Materialize a bounded `fraud_watch_packets` run.
7. Generate a draft `fraud_watch_show` content brief only after packet rows exist.

## Final Decision

Current-season Fraud Watch is not suitable for production content yet. The infrastructure works for historical slices, but the current warehouse does not contain the modern upstream source rows needed to generate 2025 or 2026 Fraud Watch rows.
