# Phase 31.10 - GNG Profile and Profile-Aware Ranking Writes

## Final Decision

PROFILE AWARE RANKING WRITES READY

## GNG Keeper Profile Completeness

The incomplete GNG Keeper profile was completed from the owner-supplied Sleeper scoring report.

Updated files:

- `src/fantasy_scoring.py`
- `docs/scoring/gng-keeper-sleeper-scoring-2026.md`
- `bigquery/migrations/0029__gng_keeper_scoring_profile_seed.sql`
- `tests/test_fantasy_scoring.py`
- `tests/test_scoring_profile_seeds.py`

Confirmed preserved categories:

- Passing, rushing, receiving, TE premium, and WR reception bonus
- Kicking and missed-kick buckets
- Defense and special teams scoring
- Points-allowed and yards-allowed buckets
- Return scoring and miscellaneous fumbles
- Zero-value variables such as `pass_td_40p`, `rush_td_40p`, `rec_td_40p`, `fum`, and several field-goal buckets
- Source metadata: `source_league_id=1369406895588143104`, `season=2026`, `league_status_at_retrieval=pre_draft`

The internal scoring settings still map only supported player-scoring fields into direct fantasy point calculations. The full Sleeper scoring report is preserved under `sleeper_scoring_settings`, with unsupported or future-use fields retained under `unmapped_settings`.

## Migration 0029 Apply Status

Pre-apply ledger check showed only one pending migration:

- `0029: gng keeper scoring profile seed`

Migration `0029__gng_keeper_scoring_profile_seed.sql` was reviewed as seed-only and additive:

- Uses `MERGE` into `scoring_profiles`
- Inserts or updates only `gng_keeper`
- Does not delete, drop, truncate, or modify the existing `standard`, `half_ppr`, or `ppr` rows

Command run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --apply
```

Result:

- Applied 1 migration: `0029`
- Post-apply `--list-pending`: no pending migrations

## Scoring Profile Row Verification

Read-only BigQuery verification confirmed active scoring profile rows:

- `standard`: active
- `half_ppr`: active
- `ppr`: active
- `gng_keeper`: active

Verified `gng_keeper` JSON values:

- `source_league_id`: `1369406895588143104`
- `league_status_at_retrieval`: `pre_draft`
- `bonus_rec_te`: `0.2`
- `fgm`: `3`
- `sack`: `1`
- `pts_allow_0`: `8`
- `yds_allow_550p`: `-7`
- `fum`: `0`
- `pass_td_40p`: `0`

Queries used neutral aliases and did not use `rows` as a BigQuery alias.

## Profile-Aware Ranking Write Behavior

`src/generate_pigskin_rankings.py` no longer writes active Pigskin rankings with a global final-table truncate.

New active write behavior:

- Loads generated rows into a temporary staging table with `WRITE_EMPTY`
- Deletes only active-board rows matching:
  - `scoring_profile_id`
  - `league_type_id`
  - `roster_format_id`
  - generated `position`
- Inserts the staged rows into `analytics_pigskin_rankings`
- Appends all generated rows to `analytics_pigskin_rankings_history` with `WRITE_APPEND`
- Deletes the temporary staging table in a `finally` block
- Preserves schema selection from existing final/history tables, including TIMESTAMP fields

The delete SQL uses `target_board` and `source_board` aliases. It does not use `rows` as an alias.

Tests now cover:

- Selected-profile delete scope includes scoring profile, league type, roster format, and position
- Standard write scope does not delete PPR
- GNG Keeper write scope does not delete PPR
- Missing profile scope fields fail before loading or querying
- No active-table `WRITE_TRUNCATE` is used
- History append remains `WRITE_APPEND`
- Prompt label uses the selected scoring profile

No ranking generation was run.

## Candidate Board Persistence Recommendation

Keep the candidate board transient and single-profile for now.

Reason: active final ranking writes are now profile-sliced, which removes the immediate cross-profile overwrite risk. Candidate materialization should still be run one profile at a time during controlled generation. If concurrent multi-profile candidate persistence becomes necessary, make `analytics_pigskin_rankings_candidates` explicitly profile-sliced before running parallel profile generation.

## Checks Run

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m py_compile src\generate_pigskin_rankings.py src\fantasy_scoring.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest tests.test_fantasy_scoring tests.test_scoring_profile_seeds tests.test_player_profile_ranking_profiles tests.test_pigskin_rankings_model_runs tests.test_pigskin_rankings_materialize_identity
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:

- Safety checker: pass
- App compile: pass
- `src` and `scripts` compile: pass
- Focused tests: 34 tests passed
- Full test suite: 670 tests passed
- Migration dry-run: discovered migrations through `0029`
- Migration ledger: no pending migrations after apply
- Validation dry-run: discovered 209 validation files

## No Deployment or Runtime Mutation

Confirmed not performed:

- No production deploy
- No staging deploy
- No Pigskin chat call
- No LLM-backed ranking generation
- No ranking generation
- No candidate materialization
- No Cloud Run Job trigger
- No Scheduler job creation
- No ranking formula/backtest table writes
- No live Sleeper API call

The only BigQuery mutation in this phase was the owner-requested application of migration `0029` after it was confirmed to be the sole pending migration.

## Remaining Warnings

- `half_ppr` remains active in `scoring_profiles`, but it is intentionally not part of the first Player Profiles dropdown.
- Future multi-profile candidate-board persistence should be made profile-sliced before any concurrent generation workflow.
- Full test output includes normal logging on stderr from existing tests. The captured test status was successful.

## Recommended Next Phase

Phase 31.11 should run controlled, non-LLM dry-run checks for profile-specific ranking generation inputs, then separately authorize any Standard or GNG Keeper ranking generation after confirming candidate-board scope and rollback expectations.
