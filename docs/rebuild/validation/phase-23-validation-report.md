# Phase 23 Validation Report

Validation date: 2026-06-19

## Final Decision

`GO WITH WARNINGS`

Phase 23 is validated for staging, release-package review, and Trade Analyzer score UI staging QA. No hard NO-GO condition was observed in the validation run.

Production deployment is not approved in this phase. The current production state is `PRODUCTION PREVIEW ONLY` because the live `validate-warehouse` proof remains blocked without a formal waiver, and `ALLOW_LIMITED_PRODUCTION_DEPLOY` is unset.

## Classifications

| Area | Classification | Notes |
| --- | --- | --- |
| Production | `PRODUCTION PREVIEW ONLY` | Clean digest-pinned candidate exists, but deploy gate remains blocked. |
| Trade Analyzer | `STAGING UI READY` | Migration applied, bounded score rows materialized, validations passed, staging UI QA passed with warnings. |
| Release package | `READY WITH WARNINGS` | Source, tests, BigQuery assets, and detailed validation docs are classified, but the worktree remains dirty and requires human commit review. |

## Blockers

1. Live `validate-warehouse` proof remains blocked.
   - Phase 23.8 decision: `LIVE VALIDATE-WAREHOUSE STILL BLOCKED`.
   - Required live proof gates were not fully set.
   - No formal waiver was supplied.

2. Production deploy remains blocked.
   - Phase 23.10 decision: `PRODUCTION DEPLOY BLOCKED`.
   - Phase 23.11 decision: `PRODUCTION DEPLOY BLOCKED`.
   - `ALLOW_LIMITED_PRODUCTION_DEPLOY` is unset.
   - No production smoke test ran because no production deploy was approved or attempted.

## Warnings

- The release package remains a reviewed dirty worktree with tracked and untracked files pending human commit review.
- The production candidate image is immutable and digest-pinned, but was built from the reviewed dirty release state rather than a clean Git commit.
- Trade Analyzer v0 score rows are staging-review data only. Phase 23.4 materialized 77 bounded rows for `trade_score_v0_2025_001`, all below confidence 70.
- Trade Analyzer score UI staging QA passed with warnings, not a production approval.
- Claim validation has informational warnings for draft and identity-review state. No failing claim validation was observed.
- Backtest dashboard validations have informational warnings for latest run and summary availability. No failing backtest validation was observed.
- `compat_trade_player_history` identity coverage returned informational review rows with zero missing identity rate.

## Commands Run

| Command | Result |
| --- | --- |
| `git status --short` | Dirty worktree with tracked changes and many untracked release evidence files. |
| `git diff --stat` | 9 tracked files changed, 698 insertions, 44 deletions. |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Pass. |
| `.\venv\Scripts\python.exe -m py_compile app.py` | Pass. |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | Pass. |
| `.\venv\Scripts\python.exe -m unittest discover tests` | Pass, 343 tests. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | Pass, no pending migrations. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | Pass, validation discovery completed. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_history` | Pass, 6 passed, 0 failed. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job` | Pass, 8 passed, 0 failed. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief` | Pass, 11 passed, 0 failed. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern claim` | Pass, 17 passed, 0 failed, informational warnings only. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market` | Pass, 9 passed, 0 failed. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern backtest` | Pass, 11 passed, 0 failed, informational warnings only. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_score` | Pass, 1 passed, 0 failed. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | Pass, 11 passed, 0 failed. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | Pass, 2 passed, 0 failed. |

## Required Reports

| Report | Status |
| --- | --- |
| `phase-23-1-release-package-review-report.md` | present |
| `phase-23-2-trade-score-migration-apply-report.md` | present |
| `phase-23-3-trade-score-dry-run-report.md` | present |
| `phase-23-4-trade-score-materialization-report.md` | present |
| `phase-23-5-trade-score-validation-and-sanity-report.md` | present |
| `phase-23-6-trade-score-ui-staging-deploy-report.md` | present |
| `phase-23-7-trade-score-ui-staging-qa-report.md` | present |
| `phase-23-8-validate-warehouse-proof-or-waiver-report.md` | present |
| `phase-23-9-clean-production-candidate-report.md` | present |
| `phase-23-10-production-deploy-gate-report.md` | present |
| `phase-23-11-production-deploy-and-smoke-report.md` | present, blocked report because production deploy was not approved or attempted |

## Release Package Status

Phase 23.1 classified the release package as `RELEASE PACKAGE READY WITH WARNINGS`.

Commit candidates include:
- UI fixes and Trade Analyzer score wiring in `app.py`.
- Default-off feature flag additions in `src/compat_flags.py`.
- Safe ingest schema hardening in `src/load.py`.
- Bounded pipeline controls in `src/pipeline.py`.
- UI guard helper `src/ui_data_guards.py`.
- Trade Analyzer score builder `src/trade_player_scores.py`.
- Trade score contracts, migration, views, validations, docs, and tests.

Exclude or review carefully:
- Local logs and generated output artifacts.
- Detailed validation reports if the final PR prefers a summarized audit trail.

## Migration Status

Migration 0025 is applied. `run_bigquery_migrations.py --list-pending` returned no pending migrations.

The Trade Analyzer score objects are available:
- `trade_player_scores`
- `trade_player_scores_current`
- `compat_trade_player_scores_current`

## Score Materialization Status

Phase 23.4 materialized bounded staging-review score rows only.

| Field | Value |
| --- | --- |
| Model version | `trade_score_v0_2025_001` |
| Season | `2025` |
| Week | `18` |
| Scoring profile | `ppr` |
| League type | `redraft` |
| Roster format | `one_qb` |
| Source rows | 100 |
| Materializable rows | 77 |
| Written rows | 77 |
| Duplicate grain rows | 0 |
| Pick rows written | 0 |
| Missing model-run rows written | 0 |
| Stale projection rows written | 0 |

The materialization was bounded and authorized in Phase 23.4. It remains staging-review data only and is not production trade advice.

## Score UI Staging Status

Phase 23.6 deployed the Trade Analyzer score UI to staging only. Phase 23.7 authenticated browser QA passed with warnings.

Confirmed in staging:
- Trade Lab page loads.
- Trade History compatibility marker appears.
- Score source marker appears: `Pigskin Trade Score source: compat_trade_player_scores_current`.
- A.J. Brown and Ja'Marr Chase selections render selected asset summaries.
- Side A and Side B Pigskin Trade Scores render.
- Score component breakdown, confidence, source freshness, and missing-data handling render.
- Score flags rollback hides the score UI and legacy Trade Lab continues to work.
- Pigskin SQL safety remains intact.
- Data Ops job triggers remain gated.

Production score flags remain false or unset.

## Live Job Proof Or Waiver Status

Phase 23.8 decision: `LIVE VALIDATE-WAREHOUSE STILL BLOCKED`.

No broad Cloud Run Job deploy occurred. No Scheduler job was created. No Cloud Run Job was triggered during this validation.

Production release remains blocked until one of these happens:
1. Live `validate-warehouse` proof passes with only the approved narrow pattern.
2. A formal waiver is supplied with approver, accepted risk, release impact, and follow-up deadline.

## Production Deploy Status

Phase 23.9 built a clean production candidate with warnings:

`us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b`

Phase 23.10 production deploy gate result: `PRODUCTION DEPLOY BLOCKED`.

Phase 23.11 production deploy and smoke result: `PRODUCTION DEPLOY BLOCKED`.

No production deployment was attempted. No production smoke test was run.

Required production flags remain false or unset, including:
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`

## Hard Safety Checks

| Check | Status |
| --- | --- |
| App compiles | pass |
| Full unittest suite passes | pass |
| Safety checker passes | pass |
| Pigskin arbitrary SQL absent | pass |
| `execute_bigquery_sql` absent from Pigskin-visible tools | pass |
| Raw/source tables blocked from Pigskin | pass |
| No tracked secrets | pass |
| No Firebase artifacts | pass |
| Production risk flags safe | pass |
| Production score flags false or unset | pass |
| Scheduler jobs not created unexpectedly | pass |
| Cloud Run Jobs not triggerable by default | pass |
| Claims and trades not fabricated | pass per Phase 23 reports |
| Source ingest not rerun unsafely | pass, no ingestion run during this validation |
| Score materialization bounded and authorized | pass per Phase 23.4 |
| Score UI staging-only | pass per Phase 23.6 and 23.7 |

## Recommended Phase 24 Work

1. Resolve the live `validate-warehouse` proof or record a formal waiver.
2. Cleanly stage and commit the reviewed release package, excluding generated output and local logs.
3. Rebuild a clean production candidate from the final commit if provenance requires a clean Git SHA.
4. Re-run the production deploy gate only after live proof or waiver is closed and `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` is intentionally set.
5. Keep Trade Analyzer score flags staging-only while improving v0 confidence, fraud context attachment, and projection coverage.
6. Decide whether low-confidence score rows are acceptable as review-only UI evidence or whether additional scoring work is required before broader rollout.
