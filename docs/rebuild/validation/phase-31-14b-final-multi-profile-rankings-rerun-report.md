# Phase 31.14B Final Multi Profile Rankings Rerun Report

Date: 2026-07-04

Final decision: **MULTI PROFILE FINAL RANKINGS GENERATED WITH WARNINGS**

## Scope

Phase 31.14B reran final Pigskin ranking generation for the missing scoring profiles after the ranking writer schema-alignment fix.

Generated profiles:

- `half_ppr`
- `standard`
- `gng_keeper`

PPR was not regenerated.

No production deploy, staging deploy, live Sleeper API call, Cloud Run Job trigger, Scheduler job creation, ranking formula/backtest write, or global truncate was run.

## Credential Setup

`GEMINI_API_KEY` was loaded from Secret Manager in the same PowerShell session that ran generation.

Secret handling:

- secret value was not printed
- generation proceeded only after the env var was non-empty
- `GEMINI_API_KEY` was removed in the `finally` block

Post-run check:

- `GEMINI_API_KEY=unset`

## Generation Commands

Commands run inside the credential-loaded session:

```powershell
.\venv\Scripts\python.exe -m src.generate_pigskin_rankings --project fantasy-football-498121 --dataset fantasy_football_brain --scoring-profile-id half_ppr --league-type-id redraft --roster-format-id one_qb --positions QB,RB,WR,TE

.\venv\Scripts\python.exe -m src.generate_pigskin_rankings --project fantasy-football-498121 --dataset fantasy_football_brain --scoring-profile-id standard --league-type-id redraft --roster-format-id one_qb --positions QB,RB,WR,TE

.\venv\Scripts\python.exe -m src.generate_pigskin_rankings --project fantasy-football-498121 --dataset fantasy_football_brain --scoring-profile-id gng_keeper --league-type-id redraft --roster-format-id one_qb --positions QB,RB,WR,TE
```

Candidate restore command used the existing `src.materialize.materialize_pigskin_rankings(...)` path for:

- `scoring_profile_id=ppr`
- `league_type_id=redraft`
- `roster_format_id=one_qb`

## Generation Results

### Half PPR

Result:

- generated row_count: 285
- ranking_version: `pigskin-llm-20260704070315`
- model_run_id: `pigskin_rankings-2026-na-20260704T070322Z-56722e52`
- model: `gemini-3.5-flash`
- model_version: `v1`
- prompt_version: `pigskin-rankings-llm-v3`
- model_run status: `complete`
- completed_at: `2026-07-04 07:14:04.237706+00:00`

### Standard

Result:

- generated row_count: 285
- ranking_version: `pigskin-llm-20260704071412`
- model_run_id: `pigskin_rankings-2026-na-20260704T071419Z-9c498edc`
- model: `gemini-3.5-flash`
- model_version: `v1`
- prompt_version: `pigskin-rankings-llm-v3`
- model_run status: `complete`
- completed_at: `2026-07-04 07:21:13.002782+00:00`

### GNG Keeper

Result:

- generated row_count: 285
- ranking_version: `pigskin-llm-20260704072119`
- model_run_id: `pigskin_rankings-2026-na-20260704T072126Z-52ed1f20`
- model: `gemini-3.5-flash`
- model_version: `v1`
- prompt_version: `pigskin-rankings-llm-v3`
- model_run status: `complete`
- completed_at: `2026-07-04 07:29:35.029361+00:00`

## LLM Call Count

Expected calls:

- 4 calls per profile
- 12 calls total for three profiles

Observed:

- 12 successful final-generation calls
- 1 additional retry call during Half PPR RB generation after `[WinError 10054] An existing connection was forcibly closed by the remote host`

Total observed request attempts:

- 13

The retry succeeded and the Half PPR model run completed.

## Final Active Row Counts

Read-only verification confirmed all four active final boards coexist.

Expected total active rows:

- 1,140

Observed total active rows:

- 1,140

| scoring_profile_id | QB | RB | WR | TE |
| --- | ---: | ---: | ---: | ---: |
| `ppr` | 45 | 80 | 100 | 60 |
| `half_ppr` | 45 | 80 | 100 | 60 |
| `standard` | 45 | 80 | 100 | 60 |
| `gng_keeper` | 45 | 80 | 100 | 60 |

Quality checks by profile and position:

- null rank count: 0 for every profile/position
- duplicate player count within profile/position: 0 for every profile/position
- rank ranges matched expected final pool sizes

PPR remained intact.

## Trey McBride Verification

Trey McBride appears in each TE board:

| scoring_profile_id | rank | tier | ranking_score | ranking_version |
| --- | ---: | --- | ---: | --- |
| `ppr` | 1 | elite | 98.0 | `pigskin-llm-20260703061257` |
| `half_ppr` | 1 | elite | 98.0 | `pigskin-llm-20260704070315` |
| `standard` | 1 | elite | 98.0 | `pigskin-llm-20260704071412` |
| `gng_keeper` | 1 | elite | 98.5 | `pigskin-llm-20260704072119` |

All Trey McBride rows use:

- `player_id=00-0037744`
- `position=TE`

## Player Profiles Query Readiness

Read-only profile-selection checks confirmed each requested profile returns its own active final rows without fallback-like rows.

| scoring_profile_id | row_count | position_count | fallback_like_rows |
| --- | ---: | ---: | ---: |
| `ppr` | 285 | 4 | 0 |
| `half_ppr` | 285 | 4 | 0 |
| `standard` | 285 | 4 | 0 |
| `gng_keeper` | 285 | 4 | 0 |

Player Profiles can now query all four profiles:

- PPR
- Half PPR
- Standard
- GNG Keeper

## Restored PPR Candidate Board

The transient candidate table was restored to PPR after final generation.

Restore job ID:

- `7d226dce-8873-4e5c-8c42-a543909c637f`

Final candidate table state:

- profile purity: `ppr` only

| scoring_profile_id | QB | RB | WR | TE |
| --- | ---: | ---: | ---: | ---: |
| `ppr` | 128 | 202 | 393 | 213 |

## Ranking Formula And Backtest Isolation

Read-only table counts after generation:

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

## Deployment Confirmation

No deployment was run.

No production or staging service was modified.

## Previous Failed Attempt Note

The prior Phase 31.14B attempt created one failed Half PPR model run:

- `model_run_id=pigskin_rankings-2026-na-20260704T065025Z-982d46b9`
- status: `failed`
- error: `Inserted row has wrong column count; Has 82, expected 81`

That failure was addressed by commit `e8270c6 Fix Pigskin ranking write schema alignment`.

The successful Half PPR generation in this report is a new model run:

- `pigskin_rankings-2026-na-20260704T070322Z-56722e52`

## Remaining Warnings

1. The Half PPR RB generation retried once after a transient remote connection reset. The retry succeeded.
2. BigQuery Storage fallback warnings appeared. These are known non-blocking warnings in this local environment.
3. pandas-gbq future dependency warnings appeared during BigQuery DataFrame loads. These are not blockers.
4. Candidate boards remain transient and single-profile. The final state was restored to PPR.

## Recommended Next Phase

Recommended next phase:

- Phase 31.15: Player Profiles multi-profile UI smoke and deploy planning.

Other valid next phases:

- Deploy Player Profiles scoring dropdown.
- Make candidate boards profile-sliced.
- Build a formula comparison dashboard skeleton.
