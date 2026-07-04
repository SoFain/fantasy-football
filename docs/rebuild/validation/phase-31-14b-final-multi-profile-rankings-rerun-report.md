# Phase 31.14B Final Multi Profile Rankings Rerun Report

Date: 2026-07-04

Final decision: **FINAL MULTI PROFILE GENERATION BLOCKED**

## Scope

Phase 31.14B reran final multi-profile Pigskin ranking generation after the prior Phase 31.14 attempt was blocked by a missing `GEMINI_API_KEY`.

Owner authorization remained in scope for:

- `half_ppr`
- `standard`
- `gng_keeper`

PPR was not regenerated.

## Credential Setup

`GEMINI_API_KEY` was loaded from Secret Manager in the same PowerShell session used for the generation attempt.

Secret value handling:

- secret value was not printed
- `GEMINI_API_KEY` was removed in the `finally` block
- post-run check confirmed `GEMINI_API_KEY=unset`

## Pre Generation State

Read-only checks before generation showed:

- Active final ranking row_count: 285
- Active scoring profiles: `ppr` only
- No active `half_ppr`, `standard`, or `gng_keeper` final ranking rows

| scoring_profile_id | position | row_count | rank range |
| --- | --- | ---: | --- |
| `ppr` | QB | 45 | 1 to 45 |
| `ppr` | RB | 80 | 1 to 80 |
| `ppr` | WR | 100 | 1 to 100 |
| `ppr` | TE | 60 | 1 to 60 |

Trey McBride PPR row before generation:

- `player_id=00-0037744`
- `position=TE`
- `rank=1`
- `tier=elite`
- `ranking_score=98.0`

Profile fantasy point slices were present for all four profiles:

| scoring_profile_id | QB row_count | RB row_count | WR row_count | TE row_count |
| --- | ---: | ---: | ---: | ---: |
| `ppr` | 664 | 1,578 | 2,500 | 1,301 |
| `half_ppr` | 664 | 1,578 | 2,500 | 1,301 |
| `standard` | 664 | 1,578 | 2,500 | 1,301 |
| `gng_keeper` | 664 | 1,578 | 2,500 | 1,301 |

## Pre Generation Checks

Commands run:

```powershell
git status --short --untracked-files=all
git log -10 --oneline
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest tests.test_fantasy_scoring tests.test_materialize_fantasy_points tests.test_player_profile_ranking_profiles tests.test_pigskin_rankings_materialize_identity tests.test_pigskin_rankings_model_runs
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:

- No pending migrations.
- Safety checker passed.
- Compile passed.
- Focused phase tests passed before generation: 39 tests.
- BigQuery validation dry-run passed.

## Half PPR Generation Attempt

Candidate materialization ran for `half_ppr`.

Candidate materialization job IDs:

- `f7cc187d-e2f2-429f-b051-dbce564e1779`
- `23f475b0-dd71-4926-ac24-3017b12bb91a`

Candidate verification before final generation:

- candidate table profile purity: `half_ppr` only
- QB candidates: 128
- RB candidates: 202
- WR candidates: 393
- TE candidates: 213
- Trey McBride TE candidate existed with rank 1

Final generator command:

```powershell
.\venv\Scripts\python.exe -m src.generate_pigskin_rankings --project fantasy-football-498121 --dataset fantasy_football_brain --scoring-profile-id half_ppr --league-type-id redraft --roster-format-id one_qb --positions QB,RB,WR,TE
```

Model:

- `gemini-3.5-flash`

Prompt version:

- `pigskin-rankings-llm-v3`

LLM calls:

- QB: 1 call
- RB: 1 call
- WR: 1 call
- TE: 1 call
- Total: 4 calls

Model run:

- `model_run_id=pigskin_rankings-2026-na-20260704T065025Z-982d46b9`
- `ranking_version=pigskin-llm-20260704065019`
- `status=failed`
- `scoring_profile_id=half_ppr`

Failure:

```text
400 Inserted row has wrong column count; Has 82, expected 81 at [2:5]
```

The failure happened after the four LLM calls, at the BigQuery final write step. No Half PPR active final rows were written.

## Standard Generation Results

Standard generation was not attempted.

Reason:

- The phase requires stopping after any profile failure.
- Half PPR failed before final ranking rows were written.

## GNG Keeper Generation Results

GNG Keeper generation was not attempted.

Reason:

- The phase requires stopping after any profile failure.
- Half PPR failed before final ranking rows were written.

## Root Cause

The final ranking writer loaded a DataFrame containing candidate-only evidence columns into a staging table, then executed:

```sql
INSERT INTO analytics_pigskin_rankings
SELECT *
FROM analytics_pigskin_rankings_staging_...
```

Profile-aware candidate rows include `avg_profile_points`.

The current final ranking table `analytics_pigskin_rankings` does not include `avg_profile_points`.

Result:

- staging table had 82 columns
- final table expected 81 columns
- `INSERT ... SELECT *` failed

## Code Fix Applied

Files changed:

- `src/generate_pigskin_rankings.py`
- `tests/test_pigskin_rankings_model_runs.py`

Fix:

- `write_rankings(...)` now projects generated ranking rows to the BigQuery load schema before loading staging/history tables.
- Candidate-only columns such as `avg_profile_points` are dropped before final ranking writes.

Regression test added:

- `test_write_rankings_drops_candidate_only_columns_before_load`

This test verifies that `avg_profile_points` is not loaded into final/history write DataFrames when it is present in generated rows.

No generation was retried after this fix because the phase requires stopping after a profile failure.

## Candidate Board Restore

The failed Half PPR attempt left `analytics_pigskin_rankings_candidates` on `half_ppr`.

The candidate board was restored to PPR.

Restore job ID:

- `d12bdaa9-96ff-406d-93b8-51ed2b5f0075`

Final candidate table state:

- profile purity: `ppr` only
- QB candidates: 128
- RB candidates: 202
- WR candidates: 393
- TE candidates: 213

## Final Active Ranking State

Read-only checks after the failed Half PPR attempt and PPR candidate restore showed:

- Active final ranking row_count: 285
- Active scoring profiles: `ppr` only

| scoring_profile_id | position | row_count | rank range |
| --- | --- | ---: | --- |
| `ppr` | QB | 45 | 1 to 45 |
| `ppr` | RB | 80 | 1 to 80 |
| `ppr` | WR | 100 | 1 to 100 |
| `ppr` | TE | 60 | 1 to 60 |

No active rows exist for:

- `half_ppr`
- `standard`
- `gng_keeper`

## Player Profiles Query Readiness

All four profile fantasy point slices exist.

Final ranking query readiness:

- `ppr`: ready, active final rows exist
- `half_ppr`: not ready, generation failed before final write
- `standard`: not ready, not attempted
- `gng_keeper`: not ready, not attempted

Player Profiles should still show the missing-board message for Half PPR, Standard, and GNG Keeper until final generation is rerun successfully.

## Ranking Formula And Backtest No-Change Confirmation

Read-only table counts after the failed generation attempt:

| table | row_count |
| --- | ---: |
| `ranking_formula_candidates` | 12 |
| `ranking_formula_sets` | 1 |
| `ranking_backtest_runs` | 0 |
| `ranking_backtest_results` | 0 |
| `ranking_backtest_candidate_summaries` | 0 |
| `ranking_formula_champions` | 0 |

No ranking formula/backtest rows were written.

No champion formulas were selected.

## Pigskin Formula Exposure Check

Searched:

- `app.py`
- `src/pigskin_context_tools.py`
- `src/pigskin_packet_guardrails.py`
- `src/pigskin_context_qa.py`

Search terms:

- `ranking_formula`
- `ranking_backtest`
- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE`
- `execute_bigquery_sql`

Result:

- No matches.
- No arbitrary SQL path added.
- No ranking formula/backtest exposure added.

## Post Fix Checks

Commands run after the writer fix:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_pigskin_rankings_model_runs
.\venv\Scripts\python.exe -m unittest tests.test_fantasy_scoring tests.test_materialize_fantasy_points tests.test_player_profile_ranking_profiles tests.test_pigskin_rankings_materialize_identity tests.test_pigskin_rankings_model_runs
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
.\venv\Scripts\python.exe -m unittest discover tests
```

Results:

- Focused ranking writer tests passed: 13 tests.
- Focused phase tests passed: 40 tests.
- Compile passed.
- Safety checker passed.
- No pending migrations.
- Validation dry-run passed.
- Full suite passed: 677 tests.

## Restrictions Confirmation

Confirmed:

- No production deploy.
- No staging deploy.
- No live Sleeper API call.
- No Cloud Run Job trigger.
- No Scheduler job creation.
- No ranking formula/backtest table writes.
- No champion formula selection.
- No global truncate of `analytics_pigskin_rankings`.
- PPR final board remained intact.
- No exploratory prompt tests.
- `GEMINI_API_KEY` was cleared after the generation attempt.

## Remaining Warnings

1. Half PPR consumed 4 LLM calls and failed at final BigQuery write.
2. No Half PPR, Standard, or GNG Keeper final ranking board exists yet.
3. The writer bug is fixed locally and covered by tests, but final generation must be rerun in a follow-up phase.
4. BigQuery Storage fallback and pandas-gbq warnings appeared during generation and tests. These are not blockers.

## Recommended Next Phase

Recommended next phase:

- Phase 31.14C: Rerun final multi-profile rankings after the schema-alignment fix, starting again with `half_ppr`.

Use the same stop-on-failure policy:

1. `half_ppr`
2. `standard`
3. `gng_keeper`

Expected additional LLM calls:

- 12 calls if all three profiles succeed

Do not regenerate PPR.
