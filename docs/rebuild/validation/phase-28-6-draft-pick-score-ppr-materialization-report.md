# Phase 28.6 Draft-Pick Score PPR Materialization Report

Timestamp: 2026-06-28T18:11Z

## Final Decision

DRAFT PICK SCORE PPR MATERIALIZED WITH WARNINGS

The bounded PPR draft-pick score v0 rows were materialized for staging review. The write used the pick-specific authorization gate inside one PowerShell wrapper, and the gate was removed afterward.

Warning: validation `178_trade_pick_scores_model_version_coverage.sql` returned one informational review row for the newly materialized model version. This is expected after the first score write and is not a hard failure.

## Authorization Gate State

Starting state:

| Gate | State |
| --- | --- |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

Write wrapper:

```powershell
try {
  $env:ALLOW_TRADE_PICK_SCORE_MATERIALIZATION = "true"
  .\venv\Scripts\python.exe -m src.trade_pick_scores --model-version trade_pick_score_v0_2026_001 --scoring-profile-id ppr --write
} finally {
  Remove-Item Env:\ALLOW_TRADE_PICK_SCORE_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

During write:

- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION=true`

After write:

| Gate | State |
| --- | --- |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

## Preflight Results

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | Pass |
| `py_compile app.py` | Pass |
| `py_compile src\trade_pick_scores.py` | Pass |
| `compileall -q src scripts` | Pass |
| `unittest tests.test_trade_pick_scores` | Pass, 20 tests |
| `unittest tests.test_trade_pick_score_contracts` | Pass, 6 tests |
| `unittest discover tests` | Pass, 393 tests |
| `run_bigquery_migrations.py --list-pending` | Pass, no pending migrations |
| `run_bigquery_validations.py --dry-run` | Pass, validations discovered through `178` |
| `run_bigquery_validations.py --run --pattern trade_pick_scores` before write | Pass, 17 passed and 0 failed |
| `run_bigquery_validations.py --run --pattern compat_trade_pick_scores` before write | Pass, 2 passed and 0 failed |
| `run_bigquery_validations.py --run --pattern trade_player_scores` before write | Pass, 12 passed and 0 failed |

## Table State Before Write

Read-only checks before the write:

| Metric | Value |
| --- | ---: |
| `trade_pick_scores` total rows | 0 |
| target PPR rows | 0 |
| exact-slot rows | 0 |
| round-only rows | 0 |
| duplicate grain rows | 0 |
| invalid pick score rows | 0 |
| invalid confidence rows | 0 |
| missing JSON rows | 0 |

## Final PPR Dry-Run

Command:

```powershell
.\venv\Scripts\python.exe -m src.trade_pick_scores --model-version trade_pick_score_v0_2026_001 --scoring-profile-id ppr --dry-run
```

Result:

| Metric | Value |
| --- | ---: |
| `wrote` | false |
| source pick asset rows | 64 |
| parsed pick rows | 64 |
| unparsed pick rows | 0 |
| exact-slot rows | 48 |
| round-only rows | 16 |
| 2026 rows | 52 |
| 2027 rows | 4 |
| 2028 rows | 4 |
| 2029 rows | 4 |
| pick score min | 18.0143 |
| pick score max | 96.7 |
| pick score avg | 43.6848 |
| pick score stddev | 13.8831 |
| confidence min | 62.0 |
| confidence max | 88.0 |
| confidence avg | 83.0 |
| confidence stddev | 8.9443 |

Expected warning flags were present:

- `college_context_unavailable`: 64
- `draft_outcome_prior_insufficient`: 64
- `pick_market_source_only`: 64
- `pick_score_staging_only`: 64
- `pick_round_only_uncertainty`: 16
- `pick_future_year_discount`: 12

## Write Result

Command:

```powershell
.\venv\Scripts\python.exe -m src.trade_pick_scores --model-version trade_pick_score_v0_2026_001 --scoring-profile-id ppr --write
```

Result:

| Field | Value |
| --- | --- |
| `wrote` | true |
| `written_row_count` | 64 |
| target project | `fantasy-football-498121` |
| target dataset | `fantasy_football_brain` |
| target table | `fantasy-football-498121.fantasy_football_brain.trade_pick_scores` |
| model version | `trade_pick_score_v0_2026_001` |
| scoring profile | `ppr` |

Only the PPR pick-score rows were written. No player-score materialization was run.

## Post-Write Verification

Read-only checks after the write:

| Metric | Value |
| --- | ---: |
| `trade_pick_scores` total rows | 64 |
| target PPR rows | 64 |
| exact-slot rows | 48 |
| round-only rows | 16 |
| duplicate grain rows | 0 |
| invalid pick score rows | 0 |
| invalid confidence rows | 0 |
| missing identity rows | 0 |
| exact-slot rows missing `pick_slot` | 0 |
| round-only rows with non-null `pick_slot` | 0 |
| missing `component_json` rows | 0 |
| missing `missing_flags_json` rows | 0 |
| missing `source_freshness_json` rows | 0 |
| `college_context_unavailable` rows | 64 |
| `draft_outcome_prior_insufficient` rows | 64 |
| `pick_round_only_uncertainty` rows | 16 |
| `pick_future_year_discount` rows | 12 |

## Current And Compatibility View Verification

| Object | Row Count | PPR Rows | Exact-Slot Rows | Round-Only Rows |
| --- | ---: | ---: | ---: | ---: |
| `trade_pick_scores_current` | 64 | 64 | 48 | 16 |
| `compat_trade_pick_scores_current` | 64 | 64 | 48 | 16 |

Validation `172_trade_pick_scores_current_grain.sql` passed with duplicate current rows equal to 0. Validation `174_compat_trade_pick_scores_no_raw_source_dependencies.sql` passed with raw/source dependency count equal to 0.

The top pick by `pick_score` is `2026 Pick 1.01` with score `96.7`.

## Post-Write Validation Results

| Validation Pattern | Result |
| --- | --- |
| `trade_pick_scores` | 17 passed, 0 failed. One informational warning from model-version coverage. |
| `compat_trade_pick_scores` | 2 passed, 0 failed. |
| `trade_player_scores` | 12 passed, 0 failed. |
| `compat_trade_player_scores` | 2 passed, 0 failed. |

Player-score separation remains intact. Validation `175_trade_player_scores_no_pick_rows.sql` passed with `pick_player_score_rows=0`.

## Score Distributions

PPR rows:

| Metric | Value |
| --- | ---: |
| row count | 64 |
| pick score min | 18.0143 |
| pick score max | 96.7 |
| pick score avg | 43.6848 |
| pick score stddev | 13.8831 |
| confidence min | 62.0 |
| confidence max | 88.0 |
| confidence avg | 83.0 |
| confidence stddev | 8.9443 |
| exact-slot confidence avg | 88.0 |
| round-only confidence avg | 68.0 |

Tier distribution:

| Tier | Count |
| --- | ---: |
| elite | 1 |
| solid | 7 |
| speculative | 16 |
| deep | 32 |
| avoid | 8 |

Pick year distribution:

| Pick Year | Count |
| --- | ---: |
| 2026 | 52 |
| 2027 | 4 |
| 2028 | 4 |
| 2029 | 4 |

## Top Picks

| Rank | Pick | Class | Value | Score | Confidence | Tier |
| ---: | --- | --- | ---: | ---: | ---: | --- |
| 1 | 2026 Pick 1.01 | exact_slot | 7084.0 | 96.7 | 88.0 | elite |
| 2 | 2026 Pick 1.02 | exact_slot | 4233.0 | 73.7989 | 88.0 | solid |
| 3 | 2026 Pick 1.03 | exact_slot | 3751.0 | 69.6696 | 88.0 | solid |
| 4 | 2026 Pick 1.04 | exact_slot | 3574.0 | 67.957 | 88.0 | solid |
| 5 | 2026 Pick 1.05 | exact_slot | 3376.0 | 66.0781 | 88.0 | solid |
| 6 | 2026 Pick 1.06 | exact_slot | 3183.0 | 64.2388 | 88.0 | solid |
| 7 | 2026 Pick 1.07 | exact_slot | 2963.0 | 62.1855 | 88.0 | solid |
| 8 | 2026 Pick 1.08 | exact_slot | 2772.0 | 60.362 | 88.0 | solid |
| 9 | 2026 Pick 1.09 | exact_slot | 2604.0 | 58.7208 | 88.0 | speculative |
| 10 | 2026 Pick 1.10 | exact_slot | 2455.0 | 57.2302 | 88.0 | speculative |

## Bottom Picks

| Rank | Pick | Class | Value | Score | Confidence | Tier |
| ---: | --- | --- | ---: | ---: | ---: | --- |
| 1 | 2029 4th | round_only | 784.0 | 18.0143 | 62.0 | avoid |
| 2 | 2028 4th | round_only | 780.0 | 20.7826 | 66.0 | avoid |
| 3 | 2029 3rd | round_only | 954.0 | 23.0813 | 62.0 | avoid |
| 4 | 2027 4th | round_only | 818.0 | 23.8836 | 70.0 | avoid |
| 5 | 2028 3rd | round_only | 957.0 | 25.9051 | 66.0 | avoid |
| 6 | 2026 4th | round_only | 859.0 | 27.0085 | 74.0 | avoid |
| 7 | 2029 2nd | round_only | 1206.0 | 28.7981 | 62.0 | avoid |
| 8 | 2027 3rd | round_only | 1022.0 | 29.2201 | 70.0 | avoid |
| 9 | 2026 Pick 4.12 | exact_slot | 774.0 | 32.13 | 88.0 | deep |
| 10 | 2028 2nd | round_only | 1289.0 | 32.2558 | 66.0 | deep |

## Warning Flags

| Flag | Count |
| --- | ---: |
| `college_context_unavailable` | 64 |
| `draft_outcome_prior_insufficient` | 64 |
| `missing_age` | 64 |
| `missing_fraud_context` | 64 |
| `missing_gsis_id` | 64 |
| `missing_pigskin_ranking_context` | 64 |
| `missing_player_id_internal` | 64 |
| `missing_recent_trade_history` | 64 |
| `missing_sleeper_player_id` | 64 |
| `pick_future_year_discount` | 12 |
| `pick_market_source_only` | 64 |
| `pick_round_only_uncertainty` | 16 |
| `pick_score_staging_only` | 64 |

## Component JSON Examples

`2026 Pick 1.01`:

- parse: exact slot, round 1, slot 1, estimated overall pick 1
- confidence: 88.0
- risk adjustment: 0.0
- college context: neutral unavailable, score 50.0

`2026 1st`:

- parse: round-only, round 1, null slot
- confidence: 74.0
- risk adjustment: -5.0 for round-only uncertainty
- college context: neutral unavailable, score 50.0

`2027 1st`:

- parse: round-only, round 1, null slot
- confidence: 70.0
- risk adjustment: -6.0 for round-only uncertainty plus future-year discount
- college context: neutral unavailable, score 50.0

`2029 4th`:

- parse: round-only, round 4, null slot
- confidence: 62.0
- risk adjustment: -8.0 for round-only uncertainty plus future-year discount
- college context: neutral unavailable, score 50.0

## Production Untouched Confirmation

Read-only Cloud Run describe:

| Field | Value |
| --- | --- |
| service | `nfl-studio-dashboard` |
| serving revision | `nfl-studio-dashboard-00077-2jp` |
| traffic | `nfl-studio-dashboard-00077-2jp=100` |
| image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |

Production flags remain false:

- `USE_COMPAT_PLAYER_PROFILES`
- `USE_COMPAT_SLEEPER_WATCH`
- `USE_COMPAT_TRADE_ASSETS`
- `USE_COMPAT_TRADE_PLAYER_HISTORY`
- `USE_COMPAT_VIEWER_TEAM_CONTEXT`
- `USE_BACKTEST_DASHBOARD`
- `USE_CLAIM_LEDGER_UI`
- `USE_CONTENT_BRIEF_REVIEW_UI`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS`
- `DATA_OPS_ALLOW_JOB_TRIGGER`
- `USE_TRADE_ANALYZER_SCORE_V0`
- `USE_COMPAT_TRADE_PLAYER_SCORE`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

No deployment occurred.

## Safety Confirmation

- Write used same-session `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION=true`.
- Authorization gate was removed afterward.
- Only PPR pick-score rows were written.
- No player rows were written.
- No unparsed pick labels were written.
- No duplicate grain rows.
- No invalid scores.
- No missing JSON fields.
- `trade_player_scores` remains separated from pick scores.
- No production deploy.
- No staging deploy.
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

- The PPR materialization is staging-review data only.
- The all-profile materialization is still intentionally deferred.
- Validation `178` now returns a model-version coverage review row because the first pick-score model rows exist.
- College context remains neutral and unavailable in v0.

## Recommended Next Phase

Run staging UI integration against `compat_trade_pick_scores_current` with score flags limited to staging. Keep production score flags false. Do not materialize other scoring profiles until PPR review accepts the first 64 rows.
