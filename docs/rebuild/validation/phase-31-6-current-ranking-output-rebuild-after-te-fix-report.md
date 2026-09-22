# Phase 31.6 Current Ranking Output Rebuild After TE Fix

Date: 2026-07-03

Final decision: TREY MCBRIDE CANDIDATE REBUILD FIXED

## Scope

Phase 31.6 rebuilt only `analytics_pigskin_rankings_candidates` after the Phase 31.5 Trey McBride TE omission fix.

This phase did not:

- deploy staging or production
- call Pigskin chat
- call LLM-backed final ranking generation
- call live Sleeper API
- trigger Cloud Run Jobs
- create Scheduler jobs
- select champion ranking formulas
- write ranking backtest tables
- expose ranking formula tables to Pigskin

## Git State

Latest commit before this report:

`f34ce7a Audit TE ranking omission and improve formula dry-runs`

Tracked runtime code changes were already committed in Phase 31.5. Before this report, the working tree contained the known untracked historical validation backlog.

## Pre-Rebuild State

Pre-rebuild table counts:

| Table | Row count |
| --- | ---: |
| `analytics_pigskin_rankings_candidates` | 936 |
| `analytics_pigskin_rankings` | 285 |
| `ranking_formula_candidates` | 12 |
| `ranking_formula_sets` | 1 |
| `ranking_backtest_runs` | 0 |
| `ranking_backtest_results` | 0 |
| `ranking_backtest_candidate_summaries` | 0 |
| `ranking_formula_champions` | 0 |

Pre-rebuild Trey McBride candidate row:

| Field | Value |
| --- | --- |
| `ranking_version` | `pigskin-20260617024106` |
| `generated_at` | `2026-06-17 02:41:06.036397+00:00` |
| `player_id` | `8130` |
| `sleeper_player_id` | `8130` |
| `current_team` | `ARI` |
| `position` | `TE` |
| `rank` | 148 |
| `tier` | `deep or watchlist` |
| `weekly_rows` | 0 |
| `avg_ppr` | null |
| `avg_wopr` | null |
| `avg_target_share` | null |
| `avg_receiving_epa` | null |
| `ranking_score` | 5.0 |
| `confidence_score` | 35.0 |
| `risk_flags` | `missing recent weekly sample` |

Pre-rebuild final ranking table check:

- Trey McBride rows in `analytics_pigskin_rankings`: 0

Pre-rebuild TE candidate summary:

- TE candidate rows: 213
- Top 60 TE candidate rows: 60
- Trey candidate rows: 1
- Trey top 60 rows: 0
- Trey best rank: 148

## Rebuild Command

Candidate materialization only:

```powershell
@'
from google.cloud import bigquery
from src.materialize import materialize_pigskin_rankings
client=bigquery.Client(project='fantasy-football-498121')
jobs = materialize_pigskin_rankings(client, dataset_id='fantasy_football_brain', dry_run=False)
for job in jobs:
    print({'job_id': job.job_id, 'state': job.state, 'error_result': job.error_result, 'total_bytes_processed': job.total_bytes_processed})
'@ | .\venv\Scripts\python.exe -
```

Result:

- BigQuery job ID: `9c78f1dc-1a28-43cb-929d-f80c6c4d5dc4`
- State: `DONE`
- Error: null
- Bytes processed: 5,738,438

The patched SQL dry-run confirmed:

- `player_identity_bridge` path present: true
- `metrics_player_id` path present: true
- dry-run bytes processed: 5,738,438

## Post-Rebuild Verification

Post-rebuild table counts:

| Table | Row count |
| --- | ---: |
| `analytics_pigskin_rankings_candidates` | 936 |
| `analytics_pigskin_rankings` | 285 |
| `ranking_formula_candidates` | 12 |
| `ranking_formula_sets` | 1 |
| `ranking_backtest_runs` | 0 |
| `ranking_backtest_results` | 0 |
| `ranking_backtest_candidate_summaries` | 0 |
| `ranking_formula_champions` | 0 |

Ranking formula and backtest tables were unchanged.

Post-rebuild Trey McBride candidate row:

| Field | Value |
| --- | --- |
| `ranking_version` | `pigskin-20260703060600` |
| `generated_at` | `2026-07-03 06:06:00.862471+00:00` |
| `player_id` | `00-0037744` |
| `sleeper_player_id` | `8130` |
| `current_team` | `ARI` |
| `roster_status` | `ACT` |
| `position` | `TE` |
| `rank` | 1 |
| `tier` | `elite` |
| `stat_season` | 2025 |
| `weekly_rows` | 17 |
| `avg_ppr` | 18.582352941176474 |
| `total_ppr` | 315.90000000000003 |
| `avg_wopr` | 0.59045549633025 |
| `avg_target_share` | 0.2788761551568511 |
| `avg_receiving_epa` | 4.277433346486652 |
| `ranking_score` | 60.04 |
| `confidence_score` | 89.0 |
| `risk_flags` | `no major Pigskin ranking flag` |

Post-rebuild TE candidate summary:

- TE candidate rows: 213
- Top 60 TE candidate rows: 60
- Trey candidate rows: 1
- Trey top 60 rows: 1
- Trey best rank: 1
- Top 60 TE candidates with zero weekly rows: 0

Top TE candidates after rebuild:

| Rank | Player | Player ID | Sleeper ID | Team | Weekly rows | Avg PPR | Score |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: |
| 1 | Trey McBride | `00-0037744` | `8130` | ARI | 17 | 18.58 | 60.04 |
| 2 | Brock Bowers | `00-0039338` | `11604` | LV | 12 | 14.68 | 50.23 |
| 3 | Tucker Kraft | `00-0038996` | `9484` | GB | 8 | 14.65 | 46.93 |
| 4 | George Kittle | `00-0033288` | `4217` | SF | 11 | 14.68 | 46.79 |
| 5 | Kyle Pitts | `00-0036970` | `7553` | ATL | 17 | 12.40 | 44.91 |

## Final Ranking Generation Decision

Final LLM-backed ranking generation was not run.

Reason: Phase 31.6 defaulted to candidate rebuild only unless final ranking generation was explicitly authorized after candidate verification. No such authorization was supplied in this phase.

Current final ranking state:

- Trey McBride rows in `analytics_pigskin_rankings`: 0

Recommended next phase:

- Phase 31.7: owner-authorized final Pigskin ranking generation after candidate rebuild verification.

## Pigskin Exposure and Formula Safety

Focused search of Pigskin-facing files found no exposure of ranking formula or backtest symbols:

```powershell
rg -n "ranking_formula|ranking_backtest|ALLOW_RANKING_FORMULA_BACKTEST_WRITE" app.py src\pigskin_context_tools.py src\pigskin_packet_guardrails.py src\pigskin_context_qa.py
```

Result:

- no matches

## Checks Run

Local and warehouse checks:

- `git status --short --untracked-files=all`
- `git log -8 --oneline`
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile app.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_rankings_materialize_identity`
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`

Results:

- safety checker passed
- app compile passed
- src/scripts compile passed
- `tests.test_pigskin_rankings_materialize_identity`: 2 tests passed
- `tests.test_ranking_formula_backtests`: 28 tests passed
- full test discovery: 652 tests passed
- migrations: no pending migrations
- validation dry-run discovered 209 validation files

## Remaining Warnings

- Final `analytics_pigskin_rankings` still excludes Trey McBride because LLM-backed final ranking generation was intentionally not run.
- Historical validation backlog remains untracked and outside this phase.
- Candidate output now ranks Trey McBride at TE rank 1. That is consistent with the repaired weekly evidence, but final ranking generation should still be reviewed as a separate owner-authorized phase.

## Recommended Next Phase

Phase 31.7 should run only if the owner explicitly authorizes final Pigskin ranking generation.

Suggested objective:

- Generate final Pigskin rankings from the repaired candidate table.
- Verify Trey McBride appears in final TE rankings with the repaired identity and weekly evidence.
- Keep ranking formula and backtest tables out of Pigskin-visible tooling.
