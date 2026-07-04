# Phase 31.11 - Profile-Specific Ranking Input Dry-Runs

## Final Decision

GNG PROFILE POINTS NEED MATERIALIZATION

## Git State

Changed files for this phase:

- `src/player_profile_ranking_profiles.py`
- `src/materialize.py`
- `tests/test_player_profile_ranking_profiles.py`
- `tests/test_pigskin_rankings_materialize_identity.py`
- `docs/rebuild/validation/phase-31-11-profile-specific-ranking-input-dry-runs-report.md`

Commit hash:

- Final commit hash is reported in the Phase 31.11 closeout. This report is included in that same commit, so embedding the final self-referential hash would change the commit hash.

Historical validation backlog files remain untracked and were not staged.

## Scoring Profile Verification

Read-only BigQuery checks confirmed all four requested profiles exist and are active:

- `ppr`: active
- `half_ppr`: active
- `standard`: active
- `gng_keeper`: active

Verified `gng_keeper` JSON fields:

- `league_status_at_retrieval`: `pre_draft`
- `bonus_rec_te`: `0.2`
- `fgm`: `3`
- `sack`: `1`
- `pts_allow_0`: `8`
- `yds_allow_550p`: `-7`
- `fum`: `0`
- `pass_td_40p`: `0`

No pending migrations remain.

## Player Profiles Dropdown Readiness

Updated Player Profiles scoring dropdown options to exactly:

- `PPR` -> `ppr`
- `Half PPR` -> `half_ppr`
- `Standard` -> `standard`
- `GNG Keeper` -> `gng_keeper`

Default remains:

- `ppr`

Behavior verified by tests:

- Selected profile maps to its internal ID.
- Half PPR maps to `half_ppr`.
- Ranking query filters by selected `scoring_profile_id`.
- Half PPR does not silently fall back to PPR.
- Missing boards use: `Rankings for this scoring system have not been generated yet.`

`src/materialize.py` was also updated so Half PPR candidate rows use the display label `Half PPR`, not fallback title casing.

## Candidate SQL Dry-Run Results

All dry-runs used:

- `league_type_id=redraft`
- `roster_format_id=one_qb`

| Profile | Dry-run | Estimated bytes | Selected profile filter | Profile points join | Scope columns | Missing sample flag | Uses avg_profile_points |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| `ppr` | pass | 9008224 | yes | yes | yes | yes | yes |
| `half_ppr` | pass | 9008224 | yes | yes | yes | yes | yes |
| `standard` | pass | 9008224 | yes | yes | yes | yes | yes |
| `gng_keeper` | pass | 9008224 | yes | yes | yes | yes | yes |

No candidate table was created or replaced.

## Profile Fantasy Point Availability

Read-only checks against `analytics_player_fantasy_points_by_profile` showed 2025 rows for PPR, Half PPR, and Standard across QB, RB, WR, and TE.

| Profile | QB rows | RB rows | WR rows | TE rows | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| `ppr` | 664 | 1578 | 2500 | 1301 | available |
| `half_ppr` | 664 | 1578 | 2500 | 1301 | available |
| `standard` | 664 | 1578 | 2500 | 1301 | available |
| `gng_keeper` | 0 | 0 | 0 | 0 | seeded, not materialized |

GNG Keeper candidate SQL can dry-run, and it can surface `missing selected scoring profile sample`, but GNG Keeper profile fantasy points need materialization before GNG candidate inputs are complete.

## Final Write Safety Verification

Profile-aware final ranking write behavior remains safe from Phase 31.10:

- No global active-board `WRITE_TRUNCATE` path remains.
- Active writes stage rows with `WRITE_EMPTY`.
- Active deletes are scoped by:
  - `scoring_profile_id`
  - `league_type_id`
  - `roster_format_id`
  - `position`
- History append remains `WRITE_APPEND`.
- Tests cover PPR, Standard, and GNG scoped writes.

Half PPR uses the same scoped write path through `scoring_profile_id=half_ppr`.

## Current Active Board Verification

Read-only checks confirmed current active Pigskin rankings remain PPR only:

- PPR QB: 45 rows, ranks 1 to 45
- PPR RB: 80 rows, ranks 1 to 80
- PPR WR: 100 rows, ranks 1 to 100
- PPR TE: 60 rows, ranks 1 to 60

No active Half PPR, Standard, or GNG Keeper rows were present.

Trey McBride remains visible in active PPR:

- `player_id`: `00-0037744`
- `position`: `TE`
- `rank`: `1`
- `tier`: `elite`
- `ranking_score`: `98.0`

## Tests and Checks Run

```powershell
.\venv\Scripts\python.exe -m py_compile app.py src\materialize.py src\player_profile_ranking_profiles.py
.\venv\Scripts\python.exe -m unittest tests.test_player_profile_ranking_profiles tests.test_pigskin_rankings_materialize_identity tests.test_pigskin_rankings_model_runs tests.test_fantasy_scoring tests.test_scoring_profile_seeds
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:

- Focused tests: 37 passed
- Full suite: 673 passed
- Safety checker: passed
- Compileall: passed
- Migration ledger: no pending migrations
- Validation dry-run: discovered 209 validation files

`py_compile` surfaced existing `src/materialize.py` invalid escape sequence SyntaxWarnings near the history create SQL text, but exited successfully.

## No Runtime Mutation

Confirmed not performed:

- No production deploy
- No staging deploy
- No Pigskin chat call
- No LLM-backed ranking generation
- No final ranking generation
- No live Sleeper API call
- No Cloud Run Job trigger
- No Scheduler job creation
- No active ranking overwrite
- No candidate materialization
- No ranking formula or backtest table writes

## Remaining Warnings

- GNG Keeper is seeded and active, but profile fantasy points have not been materialized into `analytics_player_fantasy_points_by_profile`.
- Current active final rankings are PPR only. Half PPR, Standard, and GNG Keeper should display the explicit missing-board message until their boards are generated.
- Candidate board persistence remains transient and single-profile. Keep generation controlled one profile at a time unless the candidate table is made profile-sliced for concurrent runs.

## Recommended Next Phase

Recommended next phase:

- Phase 31.12 - Materialize GNG Keeper fantasy points by profile, dry-run first, then authorize bounded materialization if safe.

After that, run profile-specific candidate board generation for PPR, Half PPR, Standard, and GNG Keeper as separate controlled steps before any final LLM ranking generation.
