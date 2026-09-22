# Phase 31.9 Scoring Profile Dropdown Groundwork Report

Final decision: **SCORING PROFILE DROPDOWN GROUNDWORK READY**

Date: 2026-07-03

## Scope

Implemented non-mutating groundwork for Standard, PPR, and GNG Keeper ranking-profile support in Player Profiles.

Hard boundaries honored:
- No production deploy.
- No staging deploy.
- No Pigskin chat prompt.
- No LLM-backed ranking generation.
- No materialization.
- No Cloud Run Job or Scheduler trigger.
- No ranking formula or backtest table writes.
- No champion formula selection.
- No production ranking overwrite.

## Git State

Pre-commit changed files for this phase:
- `app.py`
- `src/fantasy_scoring.py`
- `src/generate_pigskin_rankings.py`
- `src/materialize.py`
- `src/player_profile_ranking_profiles.py`
- `bigquery/migrations/0029__gng_keeper_scoring_profile_seed.sql`
- `docs/scoring/gng-keeper-sleeper-scoring-2026.md`
- `tests/test_fantasy_scoring.py`
- `tests/test_pigskin_rankings_materialize_identity.py`
- `tests/test_pigskin_rankings_model_runs.py`
- `tests/test_player_profile_ranking_profiles.py`
- `tests/test_scoring_profile_seeds.py`
- `docs/rebuild/validation/phase-31-9-scoring-profile-dropdown-groundwork-report.md`

Commit hash: recorded in final Phase 31.9 closeout after commit creation.

Known unrelated worktree state:
- Historical validation backlog files remain untracked and were not staged.

## GNG Keeper Profile

The named source file `keeper-sleeper-scoring-report-2026.md` was not present in the repo or attachment folder. No live Sleeper API call was made.

Created repo copy:
- `docs/scoring/gng-keeper-sleeper-scoring-2026.md`

Source used:
- Owner-supplied Phase 31.9 prompt values.
- Sleeper league ID: `1369406895588143104`
- Season: `2026`

Added helper profile:
- `get_gng_keeper_scoring_profile()`
- profile ID: `gng_keeper`
- display name: `GNG Keeper`

Added pending additive migration:
- `0029__gng_keeper_scoring_profile_seed.sql`

The migration uses `MERGE` into `scoring_profiles`. It was not applied.

GNG Keeper JSON summary:
- `pass_yd = 0.02`
- `pass_td = 5.0`
- `rush_yd = 0.04`
- `rush_td = 6.0`
- `rec = 0.1`
- `rec_yd = 0.04`
- `rec_td = 6.0`
- TE premium preserved as `bonus_rec_te = 0.2`
- WR reception bonus preserved as `bonus_rec_wr = 0.1`
- Sleeper-only bonus and long-play keys are preserved in `unmapped_settings`.

Warning:
- Kicker, defense, special teams, fumble, points-allowed, and yards-allowed keys were requested for preservation, but the Phase 31.9 prompt text did not include exact values for them. The repo source file calls this out for later owner completion.

## Profile Inventory

Existing active profiles:
- `standard`
- `half_ppr`
- `ppr`

First Player Profiles dropdown options:
- `PPR`
- `Standard`
- `GNG Keeper`

Half PPR remains in the warehouse but is intentionally excluded from the first Player Profiles dropdown.

Default profile:
- `ppr`

## Candidate Materialization Groundwork

Updated `src/materialize.py` so `build_pigskin_rankings_sql()` and `materialize_pigskin_rankings()` accept:
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`

The candidate SQL now:
- carries `scoring_profile_id`, `league_type_id`, and `roster_format_id`;
- labels the board with the selected scoring profile;
- joins `analytics_player_fantasy_points_by_profile` for selected-profile fantasy points;
- calculates `avg_profile_points`;
- uses `avg_profile_points` in the candidate ranking score;
- adds a `missing selected scoring profile sample` risk flag when profile-specific points are unavailable.

No candidate materialization was run.

Remaining design warning:
- The candidate table still uses `CREATE OR REPLACE TABLE analytics_pigskin_rankings_candidates`. That is acceptable for this non-mutating phase because it was not executed, but Phase 31.10 should decide whether candidate boards need profile-sliced persistence before any Standard or GNG run.

## Final Ranking Write Design

Updated `src/generate_pigskin_rankings.py` so future generation can:
- filter candidates by `scoring_profile_id`;
- derive the prompt label from the selected scoring profile;
- pass profile context into candidate materialization;
- tag output rows with selected profile metadata.

Added future design helper:
- `build_profile_aware_rankings_replace_sql()`

Required future active-board strategy:
- Replace only the selected `scoring_profile_id`, `league_type_id`, `roster_format_id`, and position slice.
- Do not globally truncate `analytics_pigskin_rankings`.
- Preserve PPR while generating Standard or GNG Keeper.
- Keep history append profile-aware.

No final ranking generation was run.

## Player Profiles Dropdown

Added testable helper module:
- `src/player_profile_ranking_profiles.py`

Updated Player Profiles behavior:
- Dropdown options are exactly `PPR`, `Standard`, and `GNG Keeper`.
- Default is `PPR`.
- Selected profile maps to `ppr`, `standard`, or `gng_keeper`.
- Ranking query filters by selected `scoring_profile_id`.
- Ranking badge and canonical ranking heading include the selected scoring label.
- Ranking freshness copy includes the selected scoring label.
- Missing non-PPR profile boards show:
  - `Rankings for this scoring system have not been generated yet.`

No silent fallback to PPR was added for Standard or GNG Keeper.

## Omission Guardrails

Existing Trey McBride regression remains covered by prior ranking tests and Phase 31.7 validation.

Added generic guardrail:
- `normalize_model_rankings()` omission failure is now explicitly tested for any candidate missing from the final pool.

Added diagnostic SQL helper:
- `build_candidate_historical_metrics_gap_query()`

Purpose:
- Identify candidate rows with `weekly_rows = 0` while `player_week_advanced_metrics` has historical metric coverage.

This helper was not run against BigQuery in this phase.

## Tests and Checks

Focused tests:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_fantasy_scoring tests.test_player_profile_ranking_profiles tests.test_pigskin_rankings_materialize_identity tests.test_pigskin_rankings_model_runs tests.test_scoring_profile_seeds tests.test_ranking_formula_backtests
```

Result:
- 59 tests passed.

Full suite:

```powershell
.\venv\Scripts\python.exe -m unittest discover tests
```

Result:
- 667 tests passed.

Other checks:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m py_compile app.py src\fantasy_scoring.py src\materialize.py src\generate_pigskin_rankings.py src\player_profile_ranking_profiles.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:
- Safety checker passed.
- Compile checks passed.
- Migration dry-run discovered 0029.
- Pending migrations: `0029__gng_keeper_scoring_profile_seed.sql`.
- Validation dry-run discovered 209 validation files.

## No-Mutation Confirmation

Confirmed:
- No ranking generation was run.
- No LLM call was made.
- No materialization was run.
- No BigQuery write command was run.
- No migration was applied.
- No deployment was run.
- No production flag was changed.
- No Cloud Run Job or Scheduler was triggered.

## Warnings

- `0029` is pending by design. It must be reviewed and applied in a later authorized phase before live GNG Keeper profile rows exist in BigQuery.
- `keeper-sleeper-scoring-report-2026.md` was not found. The repo copy is based on the Phase 31.9 prompt, not a separate source file.
- Candidate materialization is profile-aware in code, but still uses a replace-table candidate strategy if executed. Do not run Standard or GNG candidate generation until Phase 31.10 resolves candidate-board persistence expectations.
- Final active ranking write is designed but not yet wired as the live write path. Current `write_rankings()` still uses the prior global truncate behavior and must not be used for multi-profile generation until replaced.

## Recommended Next Phase

Recommended next phase: **Phase 31.10 - Implement profile-aware active ranking write**.

Follow-on steps:
- Review and apply migration `0029`.
- Add or confirm exact kicker, defense, special teams, fumble, points-allowed, and yards-allowed GNG settings if the full owner report is supplied.
- Replace `write_rankings()` with profile-sliced active-board writes.
- Decide whether candidate boards need profile-sliced persistence before Standard or GNG generation.
- Only after those are done, run separate authorized candidate/final generation for Standard, PPR, and GNG Keeper.
