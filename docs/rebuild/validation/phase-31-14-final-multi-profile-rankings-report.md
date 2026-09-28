# Phase 31.14 Final Multi Profile Rankings Report

Date: 2026-07-04

Final decision: **FINAL MULTI PROFILE GENERATION BLOCKED**

## Scope

Phase 31.14 was intended to generate final active Pigskin ranking boards for:

- `half_ppr`
- `standard`
- `gng_keeper`

The owner authorized narrow final ranking generation for those missing scoring profiles. PPR was not to be regenerated.

## Blocker

Final ranking generation was blocked before any LLM call or final ranking write because `GEMINI_API_KEY` is unset in the current local command session.

The generator in `src/generate_pigskin_rankings.py` requires `GEMINI_API_KEY` before it can call Gemini and generate final rankings.

Authorization existed, but the required runtime credential was unavailable.

## Git State

Starting git state:

- Latest commit before this report: `2922724 Verify profile-specific candidate boards`
- No staged files at start.
- Historical validation backlog remained untracked.
- No pending migrations.

Files changed in this phase:

- `docs/rebuild/validation/phase-31-14-final-multi-profile-rankings-report.md`

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

- Safety checker passed.
- Compile passed.
- Focused tests passed: 39 tests.
- No pending migrations.
- BigQuery validation dry-run passed.
- Full suite was not run because no source code changed.

## Credential Check

Command run:

```powershell
if ($env:GEMINI_API_KEY) { 'GEMINI_API_KEY=set' } else { 'GEMINI_API_KEY=unset' }
```

Result:

- `GEMINI_API_KEY=unset`

No secret value was printed.

## Pre Generation Final Ranking State

Read-only check against `analytics_pigskin_rankings`:

- Active final ranking row_count: 285
- Active profiles present: `ppr` only

| scoring_profile_id | position | row_count | rank range |
| --- | --- | ---: | --- |
| `ppr` | QB | 45 | 1 to 45 |
| `ppr` | RB | 80 | 1 to 80 |
| `ppr` | WR | 100 | 1 to 100 |
| `ppr` | TE | 60 | 1 to 60 |

Trey McBride PPR row:

- `player_id=00-0037744`
- `position=TE`
- `rank=1`
- `tier=elite`
- `ranking_score=98.0`

Expected missing boards remained missing before generation:

- no active `half_ppr` final rows
- no active `standard` final rows
- no active `gng_keeper` final rows

## Profile Fantasy Point Availability

Read-only check against `analytics_player_fantasy_points_by_profile` confirmed 2025 QB/RB/WR/TE rows exist for all four scoring profiles.

| scoring_profile_id | QB row_count | RB row_count | WR row_count | TE row_count |
| --- | ---: | ---: | ---: | ---: |
| `ppr` | 664 | 1,578 | 2,500 | 1,301 |
| `half_ppr` | 664 | 1,578 | 2,500 | 1,301 |
| `standard` | 664 | 1,578 | 2,500 | 1,301 |
| `gng_keeper` | 664 | 1,578 | 2,500 | 1,301 |

## Generation Details

No final generation commands were run.

No candidate board materialization was run in Phase 31.14.

No calls were made to Gemini.

LLM call count:

- `0`

Final ranking rows written:

- `0`

Profiles generated:

- none

## Final Candidate Board State

The transient candidate table was not changed in this phase.

Per Phase 31.13, `analytics_pigskin_rankings_candidates` had already been restored to `ppr`.

## Ranking Formula And Backtest Isolation

No ranking formula or backtest table writes were run.

No champion formulas were selected.

No ranking formula/backtest tables were exposed to Pigskin chat.

## Pigskin Formula Exposure

No source changes were made.

The prior Phase 31.13 search found no matches in Pigskin-facing files for:

- `ranking_formula`
- `ranking_backtest`
- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE`
- `execute_bigquery_sql`

No arbitrary SQL input was added in this phase.

## Restrictions Confirmation

Confirmed:

- No production deploy.
- No staging deploy.
- No live Sleeper API call.
- No Cloud Run Job trigger.
- No Scheduler job creation.
- No final ranking generation.
- No write to `analytics_pigskin_rankings`.
- No global truncate of `analytics_pigskin_rankings`.
- No PPR final board overwrite.
- No ranking formula/backtest table writes.
- No exploratory prompt tests.

## Remaining Warnings

1. `GEMINI_API_KEY` must be set in the same command/session before Phase 31.14 can proceed.
2. The Half PPR, Standard, and GNG Keeper final ranking boards remain absent.
3. Player Profiles can select all four profiles, but non-PPR final ranking boards will still show the missing-board path until final generation succeeds.

## Recommended Next Phase

Recommended next phase:

- Rerun Phase 31.14 after setting `GEMINI_API_KEY` in the same PowerShell session used for generation.

Recommended command shape after credential setup:

```powershell
.\venv\Scripts\python.exe -m src.generate_pigskin_rankings --scoring-profile-id half_ppr --league-type-id redraft --roster-format-id one_qb --positions QB,RB,WR,TE
```

Then proceed one profile at a time:

- `half_ppr`
- `standard`
- `gng_keeper`

Stop after any profile failure before proceeding to the next profile.
