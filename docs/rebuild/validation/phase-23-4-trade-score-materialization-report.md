# Phase 23.4 Trade Score Materialization Report

Date: 2026-06-18

## Final Decision

`TRADE SCORE MATERIALIZED WITH WARNINGS`

The bounded Trade Analyzer score v0 materialization was completed for staging review only. The write command materialized only rows that passed the Phase 23.3G materialization policy.

No deployment, feature flag change, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, Firebase artifact creation, or production change was performed. Production score flags remain off.

## Authorization

The operator explicitly authorized Codex to set the materialization gate inside the command process and run Phase 23.4.

The write command process set:

```powershell
$env:ALLOW_TRADE_SCORE_MATERIALIZATION = "true"
```

After the bounded write completed, the same command process set:

```powershell
$env:ALLOW_TRADE_SCORE_MATERIALIZATION = "false"
```

The command output confirmed:

```text
ALLOW_TRADE_SCORE_MATERIALIZATION=false
```

A later Codex shell check observed the variable as unset, which is also safe.

## Target

| Field | Value |
| --- | --- |
| season | `2025` |
| week | `18` |
| scoring profile | `ppr` |
| league type | `redraft` |
| roster format | `one_qb` |
| model version | `trade_score_v0_2025_001` |
| policy version | `trade_score_v0_staging_review_policy` |

## Preflight

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | pass, 25 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 343 tests |
| `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |

Safety checker confirmed no Firebase artifacts, no tracked secret files, no detected secret content, safe default feature flags, Pigskin SQL safety, app compile, and `src` plus `scripts` compile.

## Pre-Existing Table State

Read-only checks before materialization:

| Metric | Value |
| --- | ---: |
| total `trade_player_scores` rows | 0 |
| target rows | 0 |
| duplicate grain rows | 0 |

Because no target rows existed, this was an initial bounded materialization for the target model/version/context.

## Final Dry-Run

Command:

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v0_2025_001 --dry-run
```

Result:

| Metric | Value |
| --- | ---: |
| source rows | 100 |
| score rows | 100 |
| materializable rows | 77 |
| excluded rows | 23 |
| excluded pick rows | 13 |
| excluded missing model-run rows | 23 |
| excluded stale projection rows | 0 |
| written rows | 0 |
| confidence >= 70 | 0 |
| low-confidence materializable rows | 77 |

Dry-run warning:

`all_materializable_rows_below_confidence_70`

## Write Command

The bounded materialization command was run once:

```powershell
$env:ALLOW_TRADE_SCORE_MATERIALIZATION = "true"
try {
  .\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v0_2025_001 --write
} finally {
  $env:ALLOW_TRADE_SCORE_MATERIALIZATION = "false"
}
```

Write result:

| Metric | Value |
| --- | ---: |
| source rows | 100 |
| score rows | 100 |
| materializable rows | 77 |
| excluded rows | 23 |
| excluded pick rows | 13 |
| written rows | 77 |
| wrote | true |

No diagnostic rows were intentionally written.

## Post-Write Verification

Read-only warehouse checks after materialization:

| Metric | Value |
| --- | ---: |
| total `trade_player_scores` rows | 77 |
| target rows | 77 |
| model version rows | 77 |
| duplicate grain rows | 0 |
| `PICK` rows | 0 |
| missing `model_run_id` rows | 0 |
| `stale_projection_context` rows | 0 |
| invalid `trade_score` rows | 0 |
| missing `confidence_score` rows | 0 |
| missing `missing_flags_json` rows | 0 |
| missing `component_json` rows | 0 |
| missing `source_freshness_json` rows | 0 |

## Score Distribution

| Metric | Value |
| --- | ---: |
| trade score min | 7.9352 |
| trade score max | 60.0659 |
| trade score avg | 33.2663 |
| confidence min | 28.66 |
| confidence max | 51.41 |
| confidence avg | 46.3644 |
| confidence >= 70 rows | 0 |

## Position Distribution

| Position | Rows |
| --- | ---: |
| WR | 30 |
| RB | 26 |
| QB | 13 |
| TE | 8 |

## Score Tier Distribution

| Tier | Rows |
| --- | ---: |
| avoid | 34 |
| depth | 30 |
| flex | 12 |
| starter | 1 |

## Top Written Rows

| Rank | Player | Pos | Team | Trade score | Confidence |
| ---: | --- | --- | --- | ---: | ---: |
| 1 | Bijan Robinson | RB | ATL | 60.0659 | 50.53 |
| 2 | Ja'Marr Chase | WR | CIN | 55.7722 | 49.35 |
| 3 | Jahmyr Gibbs | RB | DET | 55.3984 | 50.53 |
| 4 | Puka Nacua | WR | LAR | 54.3830 | 43.72 |
| 5 | Jaxon Smith-Njigba | WR | SEA | 53.3932 | 50.53 |
| 6 | De'Von Achane | RB | MIA | 51.7125 | 49.35 |
| 7 | Amon-Ra St. Brown | WR | DET | 51.6068 | 50.53 |
| 8 | Christian McCaffrey | RB | SF | 51.2452 | 50.53 |
| 9 | Drake Maye | QB | NE | 50.4203 | 43.66 |
| 10 | Ashton Jeanty | RB | LV | 49.2474 | 50.53 |

## Bottom Written Rows

| Rank | Player | Pos | Team | Trade score | Confidence |
| ---: | --- | --- | --- | ---: | ---: |
| 1 | Chuba Hubbard | RB | CAR | 7.9352 | 47.02 |
| 2 | Bhayshul Tuten | RB | JAX | 10.6040 | 45.93 |
| 3 | David Montgomery | RB | HOU | 12.6693 | 49.41 |
| 4 | Marvin Harrison | WR | ARI | 14.5610 | 40.63 |
| 5 | Jaylen Waddle | WR | DEN | 15.2744 | 48.32 |
| 6 | Quentin Johnston | WR | LAC | 16.6338 | 44.96 |
| 7 | Bo Nix | QB | DEN | 17.0614 | 44.12 |
| 8 | Jalen Hurts | QB | PHI | 18.4702 | 42.20 |
| 9 | Christian Watson | WR | GB | 18.6211 | 41.24 |
| 10 | Brian Thomas | WR | JAX | 19.4932 | 45.42 |

## Validation Results

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 of 11 |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 of 2 |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market` | pass, 9 of 9 |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief` | pass, 11 of 11 |

## Warnings

- The 77 written rows are staging-review data only.
- All 77 written rows are below confidence 70.
- These rows are not production-ready trade advice.
- Production score flags remain false.
- `USE_TRADE_ANALYZER_SCORE_V0` and `USE_COMPAT_TRADE_PLAYER_SCORE` must remain off outside explicitly approved staging QA.

## Acceptance Criteria Status

| Criterion | Status |
| --- | --- |
| no score write without authorization | pass |
| only policy-materializable rows written | pass |
| no `PICK` rows written | pass |
| no missing-model rows written | pass |
| no stale-projection rows written | pass |
| no production flags enabled | pass |
| no deployment | pass |
| no LLM calls | pass |
| no scraping | pass |
| no Firebase artifacts | pass |
