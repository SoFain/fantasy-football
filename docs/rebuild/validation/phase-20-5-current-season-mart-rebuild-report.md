# Phase 20.5 Current-Season Mart Rebuild Report

## Purpose

Phase 20.5 rebuilt the current-season marts needed for 2025 source-backed evidence and Fraud Watch after the admin-run 2025 source ingest was audited.

Source readiness reference:

- `docs/rebuild/validation/phase-20-4-2025-ingest-only-restore-report.md`
- `docs/rebuild/validation/phase-20-4b-admin-ingest-audit-report.md`

No scraping, LLM calls, Firebase artifacts, source ingest, Cloud Run Jobs, deployment, or scheduler work were run in this phase.

## Source Coverage Before

Fresh read-only coverage checks confirmed 2025 source rows exist before mart rebuild.

| Table | 2025 rows | Coverage |
| --- | ---: | --- |
| `play_by_play` | 48,771 | weeks 1 through 22 |
| `weekly_metrics` | 19,421 | weeks 1 through 22 |

Additional source audit from Phase 20.4B confirmed all planned source tables have nonzero 2025 rows and duplicate checks passed for:

- `play_by_play` on `season`, `week`, `game_id`, `play_id`
- `weekly_metrics` on `season`, `week`, `player_id`
- `weekly_metrics` on `season`, `week`, `team`, `player_id`

## Materialization Plan

The existing materializer interfaces are mixed:

| Mart | Interface | Bounded behavior |
| --- | --- | --- |
| `analytics_player_weekly_truth` | `src.materialize.materialize_player_weekly_truth()` | no explicit season arg, table-wide `CREATE OR REPLACE` |
| `analytics_fraud_watch` | `src.materialize.materialize_fraud_watch()` | no explicit season arg, table-wide `CREATE OR REPLACE` from truth table |
| `analytics_player_fantasy_points_by_profile` | `src.materialize_fantasy_points --season 2025 --scoring-profile-id ppr` | explicit season and profile bounds |

Because the current source tables contain 2025 rows and the requested current-season target is 2025, the truth and fraud watch rebuilds were run through targeted functions only. `materialize_all`, Pigskin rankings, source ingest, and projection generation were not run.

## Dry Runs

Commands and results:

```powershell
@'
from google.cloud import bigquery
from src.load import get_bigquery_project
from src.materialize import materialize_player_weekly_truth, materialize_fraud_watch

client = bigquery.Client(project=get_bigquery_project())
dataset = "fantasy_football_brain"
for name, fn in [
    ("analytics_player_weekly_truth", materialize_player_weekly_truth),
    ("analytics_fraud_watch", materialize_fraud_watch),
]:
    job = fn(client, dataset_id=dataset, dry_run=True)
    print(name, job.total_bytes_processed or 0)
'@ | .\venv\Scripts\python.exe -
```

| Mart | Dry-run result |
| --- | ---: |
| `analytics_player_weekly_truth` | passed, estimated 23,433,634 bytes |
| `analytics_fraud_watch` | passed, estimated 5,202,948 bytes |

Fantasy points dry-run:

```powershell
.\venv\Scripts\python.exe -m src.materialize_fantasy_points --season 2025 --scoring-profile-id ppr --dry-run --allow-large-query
```

Result:

| Mart | Dry-run result |
| --- | --- |
| `analytics_player_fantasy_points_by_profile` | passed, built 18,539 PPR rows in dry-run mode |

## Materialization Commands

Targeted truth and Fraud Watch rebuild:

```powershell
@'
from google.cloud import bigquery
from src.load import get_bigquery_project
from src.materialize import materialize_player_weekly_truth, materialize_fraud_watch

client = bigquery.Client(project=get_bigquery_project())
dataset = "fantasy_football_brain"
materialize_player_weekly_truth(client, dataset_id=dataset, dry_run=False)
materialize_fraud_watch(client, dataset_id=dataset, dry_run=False)
'@ | .\venv\Scripts\python.exe -
```

Job results:

| Mart | BigQuery job ID | Result |
| --- | --- | --- |
| `analytics_player_weekly_truth` | `a5bf17d5-9073-4528-8c24-f50599e9f94a` | `DONE` |
| `analytics_fraud_watch` | `7cfa8776-9ebd-4c20-84e1-75ddad4409c6` | `DONE` |

PPR fantasy points rebuild:

```powershell
.\venv\Scripts\python.exe -m src.materialize_fantasy_points --season 2025 --scoring-profile-id ppr --allow-large-query
```

Result:

| Mart | Result |
| --- | --- |
| `analytics_player_fantasy_points_by_profile` | merged 18,539 PPR rows |

## Mart Counts After

Read-only post-rebuild checks:

| Mart | 2025 rows | Coverage |
| --- | ---: | --- |
| `analytics_player_weekly_truth` | 18,539 | weeks 1 through 18 |
| `analytics_fraud_watch` | 1,218 | weeks 1 through 18 |
| `analytics_player_fantasy_points_by_profile` | 55,617 | weeks 1 through 18, profiles `half_ppr`, `ppr`, `standard` |

Notes:

- `weekly_metrics` and `play_by_play` include weeks 1 through 22 because they include postseason rows.
- `analytics_player_weekly_truth` filters `season_type = 'REG'`, so weeks 1 through 18 are expected.
- `analytics_fraud_watch` is built from regular-season truth rows and also covers weeks 1 through 18.
- Only PPR fantasy point rows were rebuilt in this phase. Existing `standard` and `half_ppr` rows remain present.

## Optional Context Tables

| Object | Status |
| --- | --- |
| `projection_rankings_current` | exists with 50 rows for 2025, not rebuilt in this phase |
| `llm_player_context_packet` | exists with 0 rows, not rebuilt in this phase |

Projection generation and LLM player context packet generation were not required for the targeted Fraud Watch mart rebuild and were not run.

## Validations

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern backtest
```

Results:

| Pattern | Result |
| --- | --- |
| `market` | 9 passed, 0 failed |
| `content_brief` | 11 passed, 0 failed |
| `backtest` | 11 passed, 0 failed |

Backtest validations included two informational dashboard warnings:

- `139_backtest_dashboard_latest_runs.sql` returned 1 review row showing one latest backtest run.
- `140_backtest_dashboard_summary_available.sql` returned 1 review row showing six summary rows and one backtest run.

These are informational review rows, not failures.

## Safety Status

`scripts/check_deployment_safety.py` passed.

| Rule | Status |
| --- | --- |
| 2025 source rows verified before rebuild | pass |
| No source ingest | pass |
| No scraping | pass |
| No LLM calls | pass |
| No Firebase artifacts | pass |
| No Cloud Run Jobs | pass |
| No deployment | pass |
| No fake current-season labeling | pass |

## Current-Season Readiness

The core 2025 source-backed evidence marts are ready for current-season planning and Fraud Watch:

- `analytics_player_weekly_truth`
- `analytics_player_fantasy_points_by_profile`
- `analytics_fraud_watch`

Remaining follow-ups:

- add explicit season bounds to `src.materialize.py` before future multi-season warehouse use;
- harden source append schema handling for player ID string fields before rerunning source ingest;
- decide separately whether to generate `llm_player_context_packet`;
- decide separately whether to refresh `projection_rankings_current`.

## Final Decision

`CURRENT MARTS READY`

The requested current-season marts were rebuilt from real 2025 source rows and the requested validation patterns passed.
