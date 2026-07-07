# Phase 18.6 Current-Season Fraud Watch Materialization Report

Date: 2026-06-16

Final status: BLOCKED

Production suitability: blocked

No Fraud Watch packets were materialized. No content briefs were generated. No scraping, LLM calls, Firebase artifacts, migrations, or Cloud Run Jobs were used.

## Purpose

Materialize current-season Fraud Watch packets and a draft `fraud_watch_show` content brief only if modern source rows exist.

This phase follows:

- `docs/rebuild/validation/phase-18-5-modern-source-data-report.md`
- `docs/rebuild/validation/phase-17-7-current-season-fraud-watch-report.md`

Both reports identified the same blocker: 2025/2026 rows are missing from the direct Fraud Watch source path.

## Target Season and Week

No operator-supplied target season/week was provided in this prompt.

Checked modern target coverage:

- `season=2025`, weeks 1 through 18 where downstream fantasy-point rows exist
- `season=2026`, any available rows
- scoring profile context: `ppr`

No historical season was used as a substitute for current content.

## Source Row Counts

Read-only BigQuery source coverage:

```text
analytics_fraud_watch:
  2025/2026 rows: 0

analytics_player_weekly_truth:
  2025/2026 rows: 0

analytics_player_fantasy_points_by_profile:
  2025 week 1: 3213
  2025 week 2: 3324
  2025 week 3: 3309
  2025 week 4: 3321
  2025 week 5: 2883
  2025 week 6: 3042
  2025 week 7: 3105
  2025 week 8: 2676
  2025 week 9: 2844
  2025 week 10: 2889
  2025 week 11: 3096
  2025 week 12: 2901
  2025 week 13: 3243
  2025 week 14: 2922
  2025 week 15: 3165
  2025 week 16: 3294
  2025 week 17: 3189
  2025 week 18: 3201

projection_rankings_current:
  2025 week 1: 50

fraud_watch_packets:
  2025/2026 rows: 0

content_briefs where brief_type = fraud_watch_show:
  2025/2026 rows: 0
```

Intersection check:

```text
season=2025 week=1 fraud=0 truth=0 fantasy=3213 rankings=50
season=2025 week=2 fraud=0 truth=0 fantasy=3324 rankings=0
season=2025 week=3 fraud=0 truth=0 fantasy=3309 rankings=0
season=2025 week=4 fraud=0 truth=0 fantasy=3321 rankings=0
season=2025 week=5 fraud=0 truth=0 fantasy=2883 rankings=0
season=2025 week=6 fraud=0 truth=0 fantasy=3042 rankings=0
season=2025 week=7 fraud=0 truth=0 fantasy=3105 rankings=0
season=2025 week=8 fraud=0 truth=0 fantasy=2676 rankings=0
season=2025 week=9 fraud=0 truth=0 fantasy=2844 rankings=0
season=2025 week=10 fraud=0 truth=0 fantasy=2889 rankings=0
season=2025 week=11 fraud=0 truth=0 fantasy=3096 rankings=0
season=2025 week=12 fraud=0 truth=0 fantasy=2901 rankings=0
season=2025 week=13 fraud=0 truth=0 fantasy=3243 rankings=0
season=2025 week=14 fraud=0 truth=0 fantasy=2922 rankings=0
season=2025 week=15 fraud=0 truth=0 fantasy=3165 rankings=0
season=2025 week=16 fraud=0 truth=0 fantasy=3294 rankings=0
season=2025 week=17 fraud=0 truth=0 fantasy=3189 rankings=0
season=2025 week=18 fraud=0 truth=0 fantasy=3201 rankings=0
```

Interpretation:

- Downstream 2025 fantasy-point rows exist.
- The direct Fraud Watch source table has no 2025/2026 rows.
- The truth table that feeds Fraud Watch also has no 2025/2026 rows.
- There is no eligible current-season target slice for real Fraud Watch packets.

## Packet Dry-Run

Per the task instructions:

> If no rows: stop and document blocker.

Fraud Watch packet dry-run was not executed because `analytics_fraud_watch` has no 2025/2026 source rows.

The command that would be used after source rows exist is:

```powershell
.\venv\Scripts\python.exe -m src.segment_packets --packet-type fraud-watch --season 2025 --week 1 --scoring-profile ppr --limit 5 --dry-run
```

## Materialization Result

No packet materialization was run.

Materialized packet IDs:

```text
none
```

No current-season rows were written to:

- `fraud_watch_packets`
- `content_briefs`
- `content_brief_items`

## Content Brief Result

No `fraud_watch_show` content brief was generated.

The command that would be used after packets exist is:

```powershell
.\venv\Scripts\python.exe -m src.content_briefs --brief-type fraud_watch_show --season 2025 --week 1 --scoring-profile ppr --dry-run
```

Content brief IDs:

```text
none
```

Draft/review status:

```text
not applicable
```

## Validation

Content brief validation was run because it is read-only and confirms existing content brief tables remain healthy:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
```

Result:

```text
11 passed, 0 failed
```

## Proof Historical Rows Were Not Misrepresented

This phase did not query or use historical Fraud Watch rows for packet generation.

Historical rows remain historical-only. They were not used as current-week content.

No 2025 or 2026 Fraud Watch packets exist after this phase.

## Blocker

Current-season Fraud Watch remains blocked until modern source coverage is restored through the truth-table path:

1. Ingest or restore 2025/2026 `play_by_play` and `weekly_metrics`.
2. Rebuild `analytics_player_weekly_truth` for the target modern season/week.
3. Rebuild `analytics_fraud_watch` for that target.
4. Run Fraud Watch packet dry-run.
5. Materialize bounded draft packets.
6. Generate a draft `fraud_watch_show` content brief from those packets.

## No LLM and No Scraping Confirmation

- No LLM calls were made.
- No scraping occurred.
- No URLs were fetched.
- No Firebase artifacts were created.

## Final Decision

Current-season Fraud Watch is blocked.

Production suitability:

```text
blocked
```
