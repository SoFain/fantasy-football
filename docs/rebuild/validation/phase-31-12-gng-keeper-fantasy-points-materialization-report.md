# Phase 31.12 - GNG Keeper Fantasy Points Materialization

## Final Decision

GNG KEEPER PROFILE POINTS MATERIALIZED WITH WARNINGS

## Git State

Changed files for this phase:

- `src/fantasy_scoring.py`
- `tests/test_fantasy_scoring.py`
- `tests/test_materialize_fantasy_points.py`
- `docs/rebuild/validation/phase-31-12-gng-keeper-fantasy-points-materialization-report.md`

Commit hash:

- Reported in the Phase 31.12 closeout. This report is included in that commit.

Historical validation backlog files remain untracked and were not staged.

## Pre-Write Profile Row Counts

Before the write, `analytics_player_fantasy_points_by_profile` had 2025 QB/RB/WR/TE rows for PPR, Half PPR, and Standard only.

| Profile | QB | RB | WR | TE |
| --- | ---: | ---: | ---: | ---: |
| `ppr` | 664 | 1578 | 2500 | 1301 |
| `half_ppr` | 664 | 1578 | 2500 | 1301 |
| `standard` | 664 | 1578 | 2500 | 1301 |
| `gng_keeper` | 0 | 0 | 0 | 0 |

`gng_keeper` scoring profile verification:

- Active: yes
- `source_league_id`: `1369406895588143104`
- `season`: `2026`
- `league_status_at_retrieval`: `pre_draft`
- `bonus_rec_te`: `0.2`
- `bonus_rec_wr`: `0.1`
- `fgm`: `3`
- `sack`: `1`
- `pts_allow_0`: `8`
- `yds_allow_550p`: `-7`
- `fum`: `0`
- `pass_td_40p`: `0`

## Scoring Support Summary

Implemented deterministic GNG Keeper reception bonus support:

- TE reception: base `rec=0.1` plus `bonus_rec_te=0.2`, total `0.3` per catch
- WR reception: base `rec=0.1` plus `bonus_rec_wr=0.1`, total `0.2` per catch
- RB reception: base `rec=0.1`, no position bonus

Supported in current player fantasy-point calculation:

- Passing yards, passing touchdowns, interceptions, passing 2-point conversions
- Rushing yards, rushing touchdowns, rushing 2-point conversions
- Receptions, WR reception bonus, TE reception bonus
- Receiving yards, receiving touchdowns, receiving 2-point conversions
- Fumbles lost
- Return touchdowns when source stats contain `return_tds`

Preserved but not fully applied because source stats are unavailable or out of player-skill scope:

- Passing sacks
- Rushing and receiving first downs
- Long-play bonuses
- Yardage milestone bonuses
- Kicker scoring
- Defense/ST scoring
- Points-allowed and yards-allowed buckets

Those keys remain in the seeded profile JSON and are not fabricated as source stats.

## Dry-Run Result

Dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.materialize_fantasy_points --season 2025 --scoring-profile-id gng_keeper --dry-run --allow-large-query
```

Result:

- Source table: `analytics_player_weekly_truth`
- Source rows fetched: `18539`
- Identity rows fetched: `11212`
- GNG Keeper rows built: `18539`
- Rows written: `0`

Warnings during dry-run:

- BigQuery Storage module fallback to REST endpoint

## Write Command and Scope

Write command:

```powershell
.\venv\Scripts\python.exe -m src.materialize_fantasy_points --season 2025 --scoring-profile-id gng_keeper --allow-large-query
```

Write scope:

- Target table: `analytics_player_fantasy_points_by_profile`
- Profile written: `gng_keeper`
- Season: `2025`
- Source table: `analytics_player_weekly_truth`
- Rows merged: `18539`

Write strategy:

- Existing materializer loaded rows to a temporary staging table.
- MERGE matched on `source_player_key`, `season`, `week`, and `scoring_profile_id`.
- No global truncate was used on the target table.
- Existing `ppr`, `half_ppr`, and `standard` rows were preserved.

Warnings during write:

- BigQuery Storage fallback to REST endpoint
- `pandas_gbq` future dependency warning from BigQuery pandas load helper

## Post-Write Profile Row Counts

After the write, 2025 QB/RB/WR/TE rows exist for all four profiles.

| Profile | QB | RB | WR | TE |
| --- | ---: | ---: | ---: | ---: |
| `ppr` | 664 | 1578 | 2500 | 1301 |
| `half_ppr` | 664 | 1578 | 2500 | 1301 |
| `standard` | 664 | 1578 | 2500 | 1301 |
| `gng_keeper` | 664 | 1578 | 2500 | 1301 |

GNG Keeper total 2025 row state:

- Total rows: `18539`
- Null `player_id_internal` rows: `2101`
- Min points: `-1.36`
- Max points: `40.94`
- Average points: `1.3035`
- Duplicate grain count: `0`

## GNG Sample Checks

Week 4 samples:

- Trey McBride: GNG `4.18`, PPR `12.2`, Standard `5.2`
- Ja'Marr Chase: GNG `1.92`, PPR `7.3`, Standard `2.3`
- Bijan Robinson: GNG `13.64`, PPR `28.1`, Standard `24.1`
- Josh Allen: GNG `21.98`, PPR `26.86`, Standard `26.86`
- Lamar Jackson: GNG `9.86`, PPR `14.68`, Standard `14.68`

Trey McBride GNG state:

- `player_id_internal`: `sleeper:8130`
- Position: `TE`
- Row count: `17`
- Average GNG points: `9.0212`
- Average GNG reception points: `2.2235`

Sanity notes:

- GNG differs materially from PPR because base receptions are much lower.
- TE catches score above WR and RB catches under GNG.
- QB GNG differs from PPR/Standard because passing TD and yard settings differ.

## Candidate SQL Dry-Runs After GNG Points

All candidate SQL dry-runs passed after GNG Keeper profile points existed.

| Profile | Dry-run | Estimated bytes | Profile points join | Uses `avg_profile_points` |
| --- | --- | ---: | --- | --- |
| `ppr` | pass | 10166129 | yes | yes |
| `half_ppr` | pass | 10166129 | yes | yes |
| `standard` | pass | 10166129 | yes | yes |
| `gng_keeper` | pass | 10166129 | yes | yes |

Read-only GNG candidate input sample confirmed profile points are visible for all four positions:

| Position | Candidate rows | Rows with profile points | Top examples |
| --- | ---: | ---: | --- |
| QB | 128 | 73 | Josh Allen, Drake Maye, Brock Purdy |
| RB | 202 | 120 | Christian McCaffrey, Bijan Robinson, Jahmyr Gibbs |
| WR | 393 | 200 | Jaxon Smith-Njigba, Amon-Ra St. Brown, Ja'Marr Chase |
| TE | 213 | 122 | Trey McBride, Brock Bowers, Tucker Kraft |

No candidate table was created or replaced.

## Active Final Ranking No-Change Confirmation

Current active Pigskin rankings remain PPR only:

- PPR QB: 45 rows, ranks 1 to 45
- PPR RB: 80 rows, ranks 1 to 80
- PPR WR: 100 rows, ranks 1 to 100
- PPR TE: 60 rows, ranks 1 to 60

Trey McBride remains active PPR TE rank 1:

- `player_id`: `00-0037744`
- `rank`: `1`
- `tier`: `elite`
- `ranking_score`: `98.0`

No active Half PPR, Standard, or GNG Keeper final ranking rows were created.

## Ranking Formula and Backtest No-Change Confirmation

Read-only counts:

- `ranking_formula_candidates`: `12`
- `ranking_formula_sets`: `1`
- `ranking_backtest_runs`: `0`
- `ranking_backtest_results`: `0`
- `ranking_backtest_candidate_summaries`: `0`
- `ranking_formula_champions`: `0`

No champion formulas were selected.

## Pigskin Formula Exposure Confirmation

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

- No ranking formula read/write tool exposure found.
- No arbitrary SQL path added.
- No Streamlit request-time formula/backtest write path added.

## Tests and Checks Run

```powershell
.\venv\Scripts\python.exe -m py_compile app.py src\fantasy_scoring.py src\materialize_fantasy_points.py src\materialize.py
.\venv\Scripts\python.exe -m unittest tests.test_fantasy_scoring tests.test_materialize_fantasy_points tests.test_scoring_profile_seeds tests.test_player_profile_ranking_profiles tests.test_pigskin_rankings_materialize_identity tests.test_pigskin_rankings_model_runs
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:

- Focused tests: 40 passed
- Full suite: 676 passed
- Safety checker: passed
- Compileall: passed
- Migration ledger: no pending migrations
- Validation dry-run: discovered 209 validation files

Known warning:

- `src/materialize.py` still emits existing invalid escape sequence SyntaxWarnings around history SQL text during `py_compile`.

## No Deployment or Ranking Generation

Confirmed not performed:

- No production deploy
- No staging deploy
- No Pigskin chat call
- No LLM-backed ranking generation
- No final ranking generation
- No Pigskin candidate ranking generation
- No active ranking overwrite
- No live Sleeper API call
- No Cloud Run Job trigger
- No Scheduler job creation
- No ranking formula or backtest writes

## Remaining Warnings

- GNG Keeper profile points were materialized for all 2025 source rows, not only QB/RB/WR/TE. QB/RB/WR/TE candidate readiness is confirmed.
- `2101` GNG Keeper 2025 rows have null `player_id_internal`; this appears consistent with source identity coverage and does not block candidate inputs for the ranked examples checked.
- Some GNG Sleeper settings remain preserved but unapplied because the current source rows do not expose those stats.
- Candidate board persistence is still transient and single-profile.

## Recommended Next Phase

Recommended next phase:

- Phase 31.13 - Generate profile-specific candidate boards for PPR, Half PPR, Standard, and GNG Keeper, dry-run or one profile at a time.

Do final LLM ranking generation only after candidate board behavior and rollback expectations are explicit.
