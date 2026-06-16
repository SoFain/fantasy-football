# Phase 15 Pull Request Summary Draft

## Overview

This PR merges the rebuild branch for the AI vs. Meatbags fantasy football intelligence platform. It keeps the platform on the current Streamlit on Cloud Run architecture with BigQuery as the warehouse source of truth, adds warehouse governance and compatibility contracts, builds the first evaluation and show-prep layers, and keeps all new rollout paths gated behind default-off flags.

This PR does not deploy, apply migrations, trigger Cloud Run Jobs, create Firebase artifacts, scrape, or call LLMs.

## Architecture

The target operating model remains:

- Streamlit as the Cloud Run admin and control surface.
- BigQuery for warehouse tables, compatibility views, marts, projections, packet tables, backtests, claim tracking, and operational metadata.
- Cloud Run Jobs for long-running ingestion, materialization, ranking, validation, packet generation, backtests, content brief generation, and claim grading.
- Cloud Scheduler planned for future recurring triggers.
- Secret Manager for runtime secrets.
- No Firebase dependency.

## Major Changes

Rebuild foundation:

- Documents Cloud Run as the long-term operating model.
- Adds BigQuery migration and validation process documentation.
- Adds compatibility-contract documentation for UI and Pigskin-facing read paths.
- Adds source-of-truth rebuild docs, warehouse inventory, table classification, and UI query debt tracking.

Warehouse and model governance:

- Adds model-run, scoring profile, league type, roster format, projection, ranking, packet, backtest, market, claim, content brief, and Cloud Run Job metadata foundations.
- Keeps migrations additive and idempotent.
- Tracks model outputs through `model_run_id` and context dimensions.
- Keeps large analytical data in BigQuery, not Streamlit state.

Pigskin safety:

- Removes arbitrary Pigskin SQL exposure.
- Keeps Pigskin on parameterized context tools and curated packet/context tables.
- Blocks raw/source table names from Pigskin-visible schemas.
- Preserves the `### Context Tool Protocol ###` prompt guardrail.

Streamlit compatibility rollout:

- Adds default-off compatibility read paths for player profiles, sleeper watch, trade assets, trade player history, and viewer team context.
- Promotes only `USE_COMPAT_TRADE_PLAYER_HISTORY=true` to staging documentation.
- Leaves legacy fallbacks in place.

Evaluation and show prep:

- Adds backtest framework and read dashboard support.
- Adds market and consensus baseline layer.
- Adds claim ledger, import workflow, grading scaffolding, and source scorecards.
- Adds deterministic content brief orchestration and review UI.
- Adds segment packet materialization paths, including sleeper breakout packets.

Cloud Run Jobs:

- Adds feature-flagged Data Ops Cloud Run Job preview and trigger controls.
- Keeps live triggers default off.
- Documents IAM, Secret Manager, scheduler, and rollout assumptions.

Phase 15 documentation and cleanup:

- Added standalone Phase 14.5 claim ledger sample report.
- Added Phase 15.2 segment packet materialization report.
- Added Phase 15.3 Trade Player History staging promotion report.
- Added Phase 15.4 live `validate-warehouse` Cloud Run Job test report.
- Added Phase 15.5 merge readiness report.
- Added rebuild release checklist.

Trade Lab compatibility staging:

- `USE_COMPAT_TRADE_PLAYER_HISTORY` remains default false.
- Trade Lab now displays `Trade player history source: compat_trade_player_history` when the staging flag is true.
- Trade Lab displays source freshness or missing-data metadata from compat history rows when available.
- Legacy `weekly_metrics` fallback remains available.
- Launch script includes only a commented local QA flag.
- Deployment guide documents staging-only enablement and rollback.

Cloud Run Jobs documentation:

- Documents Phase 15.1 cleanup status for the non-live dry-run metadata row.
- Documents Phase 15.4 live-test blocker:
  - missing local `gcloud`
  - missing `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true`
  - missing `CLOUD_RUN_JOBS_IMAGE`
  - missing `CLOUD_RUN_JOB_SERVICE_ACCOUNT`
- Confirms no live job was deployed or triggered.

Claim, projection, and content brief docs:

- Clarifies demo claims are draft-only.
- Documents partial projection cleanup warning and BigQuery streaming-buffer blocker.
- Documents deterministic content brief and segment packet materialization status.

## Safety Controls

- Pigskin arbitrary SQL remains removed.
- Raw/source tables remain blocked from Pigskin-visible tool schemas.
- Feature flags remain default off.
- Cloud Run Job triggers remain default off.
- Live trigger path still requires explicit flags and confirmation.
- No Firebase artifacts were introduced.
- No secrets or service account JSON files were staged for commit.
- No migrations were added in the current worktree.
- No validation SQL was added in the current worktree.

## Feature Flags

Defaults remain false:

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

Only staging may enable:

- `USE_COMPAT_TRADE_PLAYER_HISTORY=true`

Production remains unchanged.

## Validations

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:

- Safety checker: pass.
- Unit tests: 285 passed.
- `app.py` compile: pass.
- `src` and `scripts` compile: pass.
- Pending migrations: none.
- Validation dry-run: pass, 149 validation files discovered.

Live/narrow validations from Phase 15:

- `backtest`: 11 passed, 0 failed.
- `market`: 9 passed, 0 failed.
- `claim`: 17 passed, 0 failed.
- `content_brief`: 11 passed, 0 failed.
- `cloud_run_job`: 8 passed, 0 failed.
- `compat_trade_player_history`: 6 passed, 0 failed.

## Known Warnings

1. Live `validate-warehouse` Cloud Run Job test remains blocked locally until `gcloud`, authorization flag, image, and service account are configured.
2. Dry-run metadata row `validate-warehouse-20260616T133114Z-5e7c51a8` remains a known non-live cleanup warning because BigQuery streaming-buffer limits blocked update.
3. Production compatibility flags remain off until separate approval.
4. Demo/sample claim data must stay draft-only and excluded from public content.
5. Some segment packet families still need real inputs before production show workflows are complete.

## Rollout Plan

Staging:

1. Merge after PR review.
2. Deploy Streamlit to staging.
3. Keep all flags false.
4. Enable only `USE_COMPAT_TRADE_PLAYER_HISTORY=true`.
5. Run Trade Lab manual QA.
6. Run narrow validation patterns.
7. Confirm rollback by removing the flag.

Production:

1. Do not promote production from this PR alone.
2. Require staging signoff first.
3. Keep production flags false unless separately approved.
4. Do not enable Cloud Run Job triggers in production yet.

## Rollback Plan

Trade history staging rollback:

```powershell
gcloud run services update <staging-service-name> --region <region> --remove-env-vars USE_COMPAT_TRADE_PLAYER_HISTORY
```

Application rollback:

- Redeploy the previous known-good Cloud Run image.
- Keep local subprocess Data Ops controls available.
- Do not drop BigQuery tables as rollback.

Cloud Run Jobs:

- Keep `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`.
- Keep `DATA_OPS_ALLOW_JOB_TRIGGER=false`.
- No scheduler rollback is required because no scheduler jobs were created.

## Review Focus

Review these files most carefully:

- `app.py`
- `tests/test_streamlit_compat_rollout.py`
- `deploy_guide.md`
- `docs/rebuild/release-checklist.md`
- `docs/rebuild/validation/phase-15-5-merge-readiness-report.md`

Confirm that no production defaults changed and no live job path was enabled.
