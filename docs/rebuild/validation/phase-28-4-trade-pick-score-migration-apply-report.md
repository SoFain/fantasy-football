# Phase 28.4 Trade Pick Score Migration Apply Report

Timestamp: 2026-06-28T05:09Z

## Final Decision

TRADE PICK SCORE MIGRATION APPLIED

Migration `0026__trade_pick_score_v0.sql` was applied with the authorized same-session gate. The gate was removed afterward. No pick score rows were written, no score materialization was run, no deployment occurred, and production flags were unchanged.

## Authorization Gate State

Starting state:

| Gate | State |
| --- | --- |
| `ALLOW_TRADE_PICK_SCORE_MIGRATION_APPLY` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

Migration wrapper:

```powershell
try {
  $env:ALLOW_TRADE_PICK_SCORE_MIGRATION_APPLY = "true"
  .\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --project fantasy-football-498121 --dataset fantasy_football_brain --apply
} finally {
  Remove-Item Env:\ALLOW_TRADE_PICK_SCORE_MIGRATION_APPLY -ErrorAction SilentlyContinue
}
```

During apply, `ALLOW_TRADE_PICK_SCORE_MIGRATION_APPLY=true`.

After apply:

| Gate | State |
| --- | --- |
| `ALLOW_TRADE_PICK_SCORE_MIGRATION_APPLY` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

## Preflight Results

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | Pass |
| `py_compile app.py` | Pass |
| `py_compile src\trade_pick_scores.py` | Pass |
| `compileall -q src scripts` | Pass |
| `unittest tests.test_trade_pick_scores` | Pass, 13 tests |
| `unittest tests.test_trade_pick_score_contracts` | Pass, 6 tests |
| `unittest discover tests` | Pass, 386 tests |
| `run_bigquery_migrations.py --dry-run` | Pass, migrations discovered through `0026` |
| `run_bigquery_migrations.py --list-pending` before apply | Pending: `0026` only |
| `run_bigquery_validations.py --dry-run` | Pass, validations discovered through `178` |

## Migration Safety Review

Migration `0026__trade_pick_score_v0.sql` was confirmed safe for this phase:

- Additive only.
- Creates `trade_pick_scores` if not exists.
- Creates or replaces `trade_pick_scores_current`.
- Creates or replaces `compat_trade_pick_scores_current`.
- Does not drop, delete, truncate, or update existing objects.
- Does not alter `trade_player_scores`.
- Does not insert pick score rows.
- Does not materialize score data.
- Compatibility view reads only `trade_pick_scores_current`.
- Compatibility view does not expose raw/source, college, or draft source tables.

## Migration Apply Result

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --project fantasy-football-498121 --dataset fantasy_football_brain --apply
```

Result:

- Pending before apply: `0026: trade pick score v0`
- Applied: `0026`
- Applied migration count: 1
- Pending after apply: none

## Object Verification

Read-only BigQuery verification:

| Object | Type | Field Count | Row Count |
| --- | --- | ---: | ---: |
| `trade_pick_scores` | BASE TABLE | 30 | 0 |
| `trade_pick_scores_current` | VIEW | 30 | 0 |
| `compat_trade_pick_scores_current` | VIEW | 29 | 0 |

The zero row counts are expected. This phase applied schema only and did not materialize pick scores.

## Pick Score Validation Results

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --project fantasy-football-498121 --dataset fantasy_football_brain --run --pattern trade_pick_scores
```

Result: 17 passed, 0 failed.

Covered validations:

- `161_trade_pick_scores_exists.sql`
- `162_trade_pick_scores_grain.sql`
- `163_trade_pick_scores_pick_score_range.sql`
- `164_trade_pick_scores_component_score_range.sql`
- `165_trade_pick_scores_confidence_range.sql`
- `166_trade_pick_scores_required_identity_fields.sql`
- `167_trade_pick_scores_exact_slot_fields.sql`
- `168_trade_pick_scores_round_only_fields.sql`
- `169_trade_pick_scores_source_freshness_exists.sql`
- `170_trade_pick_scores_missing_flags_exist.sql`
- `171_trade_pick_scores_component_json_exists.sql`
- `172_trade_pick_scores_current_grain.sql`
- `173_compat_trade_pick_scores_current_exists.sql`
- `174_compat_trade_pick_scores_no_raw_source_dependencies.sql`
- `176_trade_pick_scores_no_player_columns.sql`
- `177_trade_pick_scores_parseability_warning.sql`
- `178_trade_pick_scores_model_version_coverage.sql`

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --project fantasy-football-498121 --dataset fantasy_football_brain --run --pattern compat_trade_pick_scores
```

Result: 2 passed, 0 failed.

## Player Score Separation Validation

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --project fantasy-football-498121 --dataset fantasy_football_brain --run --pattern trade_player_scores
```

Result: 12 passed, 0 failed.

The separation validation `175_trade_player_scores_no_pick_rows.sql` passed with `pick_player_score_rows=0`.

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --project fantasy-football-498121 --dataset fantasy_football_brain --run --pattern compat_trade_player_scores
```

Result: 2 passed, 0 failed.

## Post-Migration Pick Dry-Runs

All-profile command:

```powershell
.\venv\Scripts\python.exe -m src.trade_pick_scores --model-version trade_pick_score_v0_2026_001 --dry-run
```

Result:

- `wrote`: false
- source pick asset rows: 192
- parsed pick rows: 192
- unparsed pick rows: 0
- exact-slot rows: 144
- round-only rows: 48
- rows by pick year: 2026=156, 2027=12, 2028=12, 2029=12
- rows by scoring profile: half_ppr=64, ppr=64, standard=64
- pick score range: min=18.0143, max=96.7, avg=43.6848
- confidence range: min=62.0, max=88.0, avg=83.0
- tier distribution: elite=3, solid=21, speculative=48, deep=96, avoid=24

PPR-only command:

```powershell
.\venv\Scripts\python.exe -m src.trade_pick_scores --model-version trade_pick_score_v0_2026_001 --scoring-profile-id ppr --dry-run
```

Result:

- `wrote`: false
- source pick asset rows: 64
- parsed pick rows: 64
- unparsed pick rows: 0
- exact-slot rows: 48
- round-only rows: 16
- rows by pick year: 2026=52, 2027=4, 2028=4, 2029=4
- rows by scoring profile: ppr=64
- pick score range: min=18.0143, max=96.7, avg=43.6848
- confidence range: min=62.0, max=88.0, avg=83.0
- tier distribution: elite=1, solid=7, speculative=16, deep=32, avoid=8

Expected warning flags remain visible:

- `college_context_unavailable`
- `draft_outcome_prior_insufficient`
- `pick_market_source_only`
- `pick_score_staging_only`
- `pick_round_only_uncertainty`
- `pick_future_year_discount`

Write mode remains fail-closed through `tests.test_trade_pick_scores` and `tests.test_trade_pick_score_contracts`.

## Production Untouched Confirmation

Read-only Cloud Run describe:

| Field | Value |
| --- | --- |
| service | `nfl-studio-dashboard` |
| serving revision | `nfl-studio-dashboard-00077-2jp` |
| traffic | `nfl-studio-dashboard-00077-2jp=100` |
| image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |

Production flag state:

- `USE_COMPAT_PLAYER_PROFILES=false`
- `USE_COMPAT_SLEEPER_WATCH=false`
- `USE_COMPAT_TRADE_ASSETS=false`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`
- `USE_BACKTEST_DASHBOARD=false`
- `USE_CLAIM_LEDGER_UI=false`
- `USE_CONTENT_BRIEF_REVIEW_UI=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

No production deployment occurred.

## Safety Confirmation

- No pick score rows written.
- No score materialization.
- No `--write` run.
- No production deploy.
- No staging deploy.
- No production feature flag change.
- No Trade Analyzer score production flag enabled.
- No Cloud Run Job trigger.
- No Scheduler job.
- No ingestion.
- No LLM-backed action.
- No Pigskin prompt.
- No scraping or external data fetch.
- No Firebase artifact.
- No commit.

## Remaining Warnings

- `trade_pick_scores` is intentionally empty until a future authorized bounded materialization phase.
- College context remains neutral and unavailable in v0.
- Pick score UI wiring remains out of scope for this phase.

## Recommended Next Phase

Run a bounded draft-pick score materialization phase only if explicitly authorized with a separate write gate. Keep it staging-first, verify `trade_pick_scores` row counts, rerun validations `161` through `178`, then decide whether any default-off UI wiring should read `compat_trade_pick_scores_current`.
