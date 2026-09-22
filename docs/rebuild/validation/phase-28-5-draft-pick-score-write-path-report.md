# Phase 28.5 Draft-Pick Score Write Path Report

Timestamp: 2026-06-28T17:41Z

## Final Decision

DRAFT PICK SCORE WRITE PATH READY

The draft-pick score write path is implemented behind the pick-specific gate `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION=true`. No gate was set in this phase, no authorized live write was run, and `trade_pick_scores` remains empty.

## Files Changed

| File | Change |
| --- | --- |
| `src/trade_pick_scores.py` | Added pick-specific write authorization, write-row validation, staging-table load, null-safe MERGE SQL, and write summary output. |
| `tests/test_trade_pick_scores.py` | Added tests for fail-closed writes, pick-specific gate behavior, default no-write behavior, contract-shaped rows, null-safe MERGE SQL, staging merge behavior, validation rejection, and round-only null slots. |
| `tests/test_trade_pick_score_contracts.py` | Updated fail-closed write test to expect the new pick-specific authorization gate. |

## Authorization Gate Behavior

Required future write gate:

```text
ALLOW_TRADE_PICK_SCORE_MATERIALIZATION=true
```

Current phase gate state:

| Gate | State |
| --- | --- |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

Behavior:

- `--write` fails before client creation or BigQuery writes unless `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION=true`.
- `ALLOW_TRADE_SCORE_MATERIALIZATION=true` does not authorize pick-score writes.
- Dry-run and default CLI execution remain non-mutating.
- The unauthorized write error explicitly says: `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION must be true to write pick scores`.

## Write Path Design

Future authorized write flow:

1. Query pick assets from `compat_trade_assets_current`.
2. Build deterministic pick-score rows in memory.
3. Validate rows against the `trade_pick_scores` contract.
4. Load valid rows into a staging table named `trade_pick_scores_staging_<timestamp>_<hash>`.
5. MERGE staging rows into `trade_pick_scores`.
6. Delete the staging table.
7. Return a write summary with row counts, target table, staging table, model version, and score summary.

The save helper writes only to `trade_pick_scores`. It does not reference or mutate:

- `trade_player_scores`
- `trade_player_scores_current`
- `compat_trade_player_scores_current`

## Null-Safe Merge Behavior

The MERGE key uses the contract grain:

- `model_version`
- `source_pick_key`
- `pick_year`
- `pick_class`
- `pick_round`
- `pick_slot`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`

Round-only picks have `pick_slot = NULL`, so the MERGE uses:

```sql
IFNULL(target.pick_slot, -1) = IFNULL(source.pick_slot, -1)
```

This prevents repeated authorized writes from duplicating round-only rows where `NULL = NULL` would otherwise fail.

## Schema Alignment

Generated rows now include every `trade_pick_scores` contract field:

- `model_version`
- `score_run_id`
- `source_pick_key`
- `pick_label`
- `pick_year`
- `pick_class`
- `pick_round`
- `pick_slot`
- `estimated_overall_pick`
- `pick_bucket`
- `parse_confidence`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `current_market_value`
- `risk_adjusted_trade_value`
- `market_score`
- `slot_capital_score`
- `time_discount_score`
- `liquidity_certainty_score`
- `college_context_score`
- `uncertainty_risk_score`
- `confidence_score`
- `pick_score`
- `score_tier`
- `component_json`
- `missing_flags_json`
- `source_freshness_json`
- `created_by`
- `created_at`

`created_by` is set to `src.trade_pick_scores`. `created_at` is generated in UTC ISO format.

## Row Rejection Rules

The write-row validator rejects:

- Rows missing required contract fields.
- Rows whose `source_pick_key` is not a `PICK` key.
- Invalid `pick_class` values.
- Exact-slot rows without `pick_slot`.
- Round-only rows with non-null `pick_slot`.
- Missing or invalid `pick_year` and `pick_round`.
- Score fields outside 0 to 100.
- Rows missing `score_tier`.
- Invalid `component_json`, `missing_flags_json`, or `source_freshness_json`.

Unparsed pick labels remain excluded from the built row set.

## Tests Added Or Updated

Added coverage for:

- `--write` without `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` fails closed.
- `ALLOW_TRADE_SCORE_MATERIALIZATION` does not authorize pick writes.
- Dry-run never calls the write or MERGE path.
- Default mode remains no-write safe.
- Generated rows contain every `trade_pick_scores` contract field.
- JSON payload fields parse correctly.
- `college_context_unavailable` remains present in v0.
- MERGE SQL uses all grain fields.
- MERGE SQL handles null `pick_slot`.
- MERGE SQL does not reference `trade_player_scores`.
- Save helper writes only through `trade_pick_scores`.
- Invalid player-like rows and invalid scores are rejected.
- Round-only write rows keep `pick_slot` null.

## Checks Run

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_pick_scores` | Pass, 20 tests. |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_pick_score_contracts` | Pass, 6 tests. |
| `.\venv\Scripts\python.exe -m unittest discover tests` | Pass, 393 tests. |
| `.\venv\Scripts\python.exe -m py_compile app.py` | Pass. |
| `.\venv\Scripts\python.exe -m py_compile src\trade_pick_scores.py` | Pass. |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | Pass. |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Pass. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --project fantasy-football-498121 --dataset fantasy_football_brain --list-pending` | Pass, no pending migrations. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --project fantasy-football-498121 --dataset fantasy_football_brain --dry-run` | Pass, validations discovered through 178. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --project fantasy-football-498121 --dataset fantasy_football_brain --run --pattern trade_pick_scores` | Pass, 17 passed and 0 failed. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --project fantasy-football-498121 --dataset fantasy_football_brain --run --pattern compat_trade_pick_scores` | Pass, 2 passed and 0 failed. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --project fantasy-football-498121 --dataset fantasy_football_brain --run --pattern trade_player_scores` | Pass, 12 passed and 0 failed. |

## Dry-Run Results

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
- score range: min=18.0143, max=96.7, avg=43.6848
- confidence range: min=62.0, max=88.0, avg=83.0

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
- score range: min=18.0143, max=96.7, avg=43.6848
- confidence range: min=62.0, max=88.0, avg=83.0

Expected v0 warning flags remain visible:

- `college_context_unavailable`
- `draft_outcome_prior_insufficient`
- `pick_market_source_only`
- `pick_score_staging_only`
- `pick_round_only_uncertainty`
- `pick_future_year_discount`

## Unauthorized Write Smoke

Command:

```powershell
.\venv\Scripts\python.exe -m src.trade_pick_scores --model-version trade_pick_score_v0_2026_001 --scoring-profile-id ppr --write
```

Result:

- Exit code: 1
- Error: `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION must be true to write pick scores`
- No BigQuery write was attempted.

## Table Row Counts After Phase

Read-only row counts:

| Object | Row Count |
| --- | ---: |
| `trade_pick_scores` | 0 |
| `trade_pick_scores_current` | 0 |
| `compat_trade_pick_scores_current` | 0 |

## Production Untouched Confirmation

Read-only Cloud Run describe:

| Field | Value |
| --- | --- |
| service | `nfl-studio-dashboard` |
| serving revision | `nfl-studio-dashboard-00077-2jp` |
| traffic | `nfl-studio-dashboard-00077-2jp=100` |
| image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |

Production flag state remained false for:

- Trade Analyzer score flags.
- Trade History compatibility.
- Data Ops Cloud Run trigger flags.
- Data Ops local subprocess flags.
- All other production risk flags listed in prior rollout reports.

No deployment occurred.

## Safety Confirmation

- No authorized live write.
- No pick score rows written.
- No score materialization.
- No `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` gate set.
- No use of `ALLOW_TRADE_SCORE_MATERIALIZATION`.
- No deployment.
- No production feature flag change.
- No Cloud Run Job trigger.
- No Scheduler job.
- No ingestion.
- No LLM-backed action.
- No Pigskin prompt.
- No scraping or external data fetch.
- No Firebase artifact.
- No commit.

## Remaining Warnings

- The write path is implemented but unproven against live writes by design.
- `trade_pick_scores` remains empty until a future authorized bounded materialization phase.
- College context remains neutral and unavailable in v0.

## Recommended Next Phase

Run a separate bounded materialization phase only with `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION=true` set inside the same command process. Use the PPR-only target first, then verify row counts, rerun validations `161` through `178`, and confirm the compatibility view remains source-safe.
