# Phase 31.7 Final Ranking Generation After Trey Fix

Date: 2026-07-03

Final decision: TREY MCBRIDE FINAL RANKING FIXED

## Scope

Phase 31.7 ran the owner-authorized final Pigskin ranking generation after the Phase 31.6 candidate rebuild fixed Trey McBride in `analytics_pigskin_rankings_candidates`.

This phase did not:

- deploy staging or production
- call live Sleeper API
- trigger Cloud Run Jobs
- create Scheduler jobs
- select champion formulas
- write ranking formula or backtest tables
- expose ranking formula tables to Pigskin chat
- add arbitrary SQL inputs

## Git State

Latest commit before this phase:

`c4dceca Document Pigskin candidate rebuild after TE fix`

Known untracked historical validation backlog remained present and was not staged.

Files changed in this phase:

- `src/generate_pigskin_rankings.py`
- `tests/test_pigskin_rankings_model_runs.py`
- `docs/rebuild/validation/phase-31-7-final-ranking-generation-after-trey-fix-report.md`

## Pre-Generation State

Pre-generation table counts:

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

Pre-generation Trey McBride candidate state:

| Field | Value |
| --- | --- |
| `ranking_version` | `pigskin-20260703060600` |
| `generated_at` | `2026-07-03 06:06:00.862471+00:00` |
| `player_id` | `00-0037744` |
| `sleeper_player_id` | `8130` |
| `current_team` | `ARI` |
| `position` | `TE` |
| `rank` | 1 |
| `tier` | `elite` |
| `stat_season` | 2025 |
| `weekly_rows` | 17 |
| `avg_ppr` | 18.582352941176474 |
| `total_ppr` | 315.90000000000003 |
| `ranking_score` | 60.04 |
| `confidence_score` | 89.0 |
| `risk_flags` | `no major Pigskin ranking flag` |

Pre-generation final ranking state:

- Trey McBride rows in `analytics_pigskin_rankings`: 0
- TE candidate rows: 213
- Top 60 TE candidate rows: 60
- Trey top 60 candidate rows: 1
- Trey best candidate rank: 1

## Final Generation Command

The existing final generation module is:

`src.generate_pigskin_rankings`

Behavior:

- Reads from `analytics_pigskin_rankings_candidates`
- Materializes candidate evidence as part of the existing generator path
- Calls Gemini once per requested position
- Writes `analytics_pigskin_rankings` with active final rankings
- Appends `analytics_pigskin_rankings_history`
- Creates a `model_runs` row with `run_type='pigskin_rankings'`
- Does not call Sleeper unless `--refresh-sleeper` is supplied

Command used:

```powershell
$ErrorActionPreference = 'Stop'
$gcloud = 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd'
$secret = & $gcloud secrets versions access latest --secret=GEMINI_API_KEY --project=fantasy-football-498121
try {
  $env:GEMINI_API_KEY = ($secret | Out-String).Trim()
  .\venv\Scripts\python.exe -m src.generate_pigskin_rankings --project fantasy-football-498121 --dataset fantasy_football_brain --positions QB,RB,WR,TE
} finally {
  Remove-Item Env:\GEMINI_API_KEY -ErrorAction SilentlyContinue
  Remove-Variable secret -ErrorAction SilentlyContinue
}
```

Result:

- Ranking version: `pigskin-llm-20260703061257`
- Model run ID: `pigskin_rankings-2026-na-20260703T061304Z-f923f2f9`
- Model: `gemini-3.5-flash`
- Prompt version: `pigskin-rankings-llm-v3`
- Rows generated: 285
- LLM calls: 4, one per position: QB, RB, WR, TE
- Sleeper refresh: not run

Generation warnings:

- BigQuery Storage module fallback to REST endpoint
- `pandas_gbq` future dependency warning from BigQuery dataframe load
- BigQuery dataframe type warning for `feature_config_version_id`

## Writer Schema Fix

The first final write succeeded and put 285 rows into `analytics_pigskin_rankings`, but focused validation caught a table schema drift:

- `generated_at` was inferred as `INTEGER`
- `adjudicated_at` was inferred as `INTEGER`

That broke `007_pigskin_rankings_model_run_id_present.sql`, which compares `generated_at` to a migration timestamp.

Fix applied:

- `write_rankings` now reuses the existing `analytics_pigskin_rankings_history` schema before loading the active final table.
- The active final table was repaired from the latest valid history snapshot using the same range partitioning and clustering:
  - partition: `RANGE_BUCKET(season, GENERATE_ARRAY(2020, 2050, 1))`
  - cluster: `position`, `rank`, `player_name`

Repair job:

- Job ID: `3bb84906-b495-41b1-bd7d-6b37a8a0471e`
- Result: `DONE`
- Error: null

Post-repair schema:

| Column | Type |
| --- | --- |
| `generated_at` | `TIMESTAMP` |
| `adjudicated_at` | `TIMESTAMP` |
| `ranking_version` | `STRING` |
| `model_run_id` | `STRING` |
| `is_active` | `BOOL` |

## Final Ranking Verification

Post-generation table counts:

| Table | Row count |
| --- | ---: |
| `analytics_pigskin_rankings_candidates` | 936 |
| `analytics_pigskin_rankings` | 285 |
| `analytics_pigskin_rankings_history` rows for `pigskin-llm-20260703061257` | 285 |

Trey McBride final row:

| Field | Value |
| --- | --- |
| `ranking_version` | `pigskin-llm-20260703061257` |
| `generated_at` | `2026-07-03 06:21:06.236476+00:00` |
| `model_run_id` | `pigskin_rankings-2026-na-20260703T061304Z-f923f2f9` |
| `player_id` | `00-0037744` |
| `sleeper_player_id` | `8130` |
| `player_name` | `Trey McBride` |
| `current_team` | `ARI` |
| `roster_status` | `ACT` |
| `position` | `TE` |
| `rank` | 1 |
| `tier` | `elite` |
| `candidate_rank` | 1 |
| `candidate_ranking_score` | 60.04 |
| `ranking_score` | 98.0 |
| `confidence_score` | 89.0 |
| `scoring_profile_id` | `ppr` |
| `league_type_id` | `redraft` |
| `roster_format_id` | `one_qb` |
| `is_active` | true |
| `risk_flags` | `no major Pigskin ranking flag` |

Pigskin verdict:

`McBride is the undisputed king of the tight end landscape heading into 2026.`

Rank rationale:

`His 0.590 WOPR and 27.9% target share are elite wide receiver numbers, translating to a massive 18.58 PPR points per game.`

## Final TE Top 20

| Rank | Player | Player ID | Sleeper ID | Team | Tier | Score |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | Trey McBride | `00-0037744` | `8130` | ARI | elite | 98.0 |
| 2 | Brock Bowers | `00-0039338` | `11604` | LV | elite | 94.0 |
| 3 | George Kittle | `00-0033288` | `4217` | SF | elite | 91.0 |
| 4 | Tucker Kraft | `00-0038996` | `9484` | GB | front-line starter | 88.0 |
| 5 | Sam LaPorta | `00-0039065` | `10859` | DET | front-line starter | 86.0 |
| 6 | Dallas Goedert | `00-0034351` | `5022` | PHI | front-line starter | 85.0 |
| 7 | Kyle Pitts | `00-0036970` | `7553` | ATL | front-line starter | 84.0 |
| 8 | Travis Kelce | `00-0030506` | `1466` | KC | front-line starter | 83.0 |
| 9 | Tyler Warren | `00-0040128` | `12518` | IND | starter | 80.0 |
| 10 | Dalton Kincaid | `00-0038933` | `10236` | BUF | starter | 78.0 |
| 11 | Hunter Henry | `00-0033090` | `3214` | NE | starter | 77.0 |
| 12 | Dalton Schultz | `00-0034383` | `5001` | HOU | starter | 76.0 |
| 13 | Juwan Johnson | `00-0036040` | `7002` | NO | starter | 74.0 |
| 14 | Colston Loveland | `00-0040126` | `12517` | CHI | starter | 73.0 |
| 15 | Jake Ferguson | `00-0038041` | `8110` | DAL | starter | 72.0 |
| 16 | Harold Fannin Jr. | `00-0040663` | `12506` | CLE | starter | 70.0 |
| 17 | Brenton Strange | `00-0038935` | `9480` | JAX | flex or matchup | 68.0 |
| 18 | Mark Andrews | `00-0034753` | `5012` | BAL | flex or matchup | 66.0 |
| 19 | T.J. Hockenson | `00-0035229` | `5844` | MIN | flex or matchup | 65.0 |
| 20 | Cade Otton | `00-0038129` | `8111` | TB | flex or matchup | 64.0 |

Final TE integrity:

- TE final rows: 60
- Trey final rows: 1
- Trey best final rank: 1
- Active TE final rows: 60
- Null rank count: 0
- Missing player ID count: 0
- Duplicate TE player ID count: 0

## App-Facing Query Eligibility

The app canonical ranking query reads:

```sql
FROM `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings`
WHERE is_active = TRUE
```

Trey McBride app-facing visibility check:

- Visible rows: 1
- Active visible rows: 1
- Position: `TE`
- Rank: 1
- Ranking version: `pigskin-llm-20260703061257`
- Scoring profile: `ppr`
- League type: `redraft`
- Roster format: `one_qb`

## Ranking Formula and Backtest Isolation

Post-generation formula/backtest counts:

| Table | Row count |
| --- | ---: |
| `ranking_formula_candidates` | 12 |
| `ranking_formula_sets` | 1 |
| `ranking_backtest_runs` | 0 |
| `ranking_backtest_results` | 0 |
| `ranking_backtest_candidate_summaries` | 0 |
| `ranking_formula_champions` | 0 |

No champion formulas were selected.

Focused search of Pigskin-facing files:

```powershell
rg -n "ranking_formula|ranking_backtest|ALLOW_RANKING_FORMULA_BACKTEST_WRITE" app.py src\pigskin_context_tools.py src\pigskin_packet_guardrails.py src\pigskin_context_qa.py
```

Result:

- no matches

## Checks Run

Pre-generation:

- `git status --short --untracked-files=all`
- `git log -10 --oneline`
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_rankings_materialize_identity`
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_rankings_model_runs`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`

Post-generation and post-fix:

- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_rankings_model_runs`
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_rankings_materialize_identity`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern pigskin_rankings`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile app.py`
- `.\venv\Scripts\python.exe -m py_compile src\generate_pigskin_rankings.py`
- `.\venv\Scripts\python.exe -m unittest discover tests`

Results:

- safety checker passed
- app compile passed
- `src.generate_pigskin_rankings` compile passed
- `src/scripts` compile passed
- `tests.test_pigskin_rankings_materialize_identity`: 2 tests passed
- `tests.test_pigskin_rankings_model_runs`: 4 tests passed
- full test discovery: 653 tests passed
- migrations: no pending migrations
- validation dry-run discovered 209 validation files
- focused `pigskin_rankings` validations: 3 passed, 0 failed

## Remaining Warnings

- The final generation path still rematerializes candidates before final rankings because that is how the existing generator is written. It did not call Sleeper because `--refresh-sleeper` was not used.
- BigQuery Storage REST fallback warning appeared during generation.
- BigQuery dataframe load emitted a future `pandas_gbq` warning.
- The active final table schema drift was caught and repaired in this phase. The writer is now patched to preserve schema on future truncating loads.

## Recommended Next Phase

Phase 31.8 should run a production or staging ranking UI smoke depending on owner preference.

If the owner wants to keep ranking formula work moving, the next separate lane should be a controlled bounded formula backtest write or a formula comparison dashboard skeleton. Keep that work isolated from Pigskin chat until explicitly approved.
