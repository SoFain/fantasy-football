# Rebuild Release Checklist

Date: 2026-06-16

Use this checklist before merging the rebuild branch and before any staging or production rollout. This checklist does not authorize deployment by itself.

## Current Release Decision

Merge readiness: GO WITH WARNINGS

Deployment readiness: staging only, manual approval required

Production readiness: not approved

## Test Status

Required local checks:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
```

Latest result:

- Deployment safety checker: pass.
- Unit tests: 285 passed.
- `app.py` compile: pass.
- `src` and `scripts` compile: pass.

## Migration Status

Required command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
```

Latest result:

- No pending migrations.

Rules:

- Do not apply migrations as part of merge.
- Review any new pending migrations before apply.
- Migrations must remain additive and idempotent.
- No destructive DDL is approved.

## Validation Status

Required command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Latest result:

- Dry-run passed.
- 149 validation files discovered.

Recommended staging checks after merge:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_history
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern claim
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
```

## Pigskin Safety Status

Current status:

- Pigskin arbitrary SQL remains removed.
- `execute_bigquery_sql` is not exposed to Pigskin.
- Pigskin should use parameterized context tools and curated packet tables.
- Raw/source tables remain blocked from Pigskin-visible paths.

Hard stop if any of these regress.

## Feature Flags

Defaults must remain false:

```text
USE_COMPAT_PLAYER_PROFILES=false
USE_COMPAT_SLEEPER_WATCH=false
USE_COMPAT_TRADE_ASSETS=false
USE_COMPAT_TRADE_PLAYER_HISTORY=false
USE_COMPAT_VIEWER_TEAM_CONTEXT=false
USE_BACKTEST_DASHBOARD=false
USE_CLAIM_LEDGER_UI=false
USE_CONTENT_BRIEF_REVIEW_UI=false
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
DATA_OPS_ALLOW_JOB_TRIGGER=false
```

Approved staging-only flag:

```text
USE_COMPAT_TRADE_PLAYER_HISTORY=true
```

Production default remains false.

## Cloud Run Jobs Trigger Status

Current status:

- Data Ops Cloud Run Jobs remain default off.
- Live triggers require explicit flags and user confirmation.
- Phase 15.4 live `validate-warehouse` test is blocked locally because `gcloud`, `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST`, `CLOUD_RUN_JOBS_IMAGE`, and `CLOUD_RUN_JOB_SERVICE_ACCOUNT` are missing.
- No scheduler jobs are approved.

Do not enable live job triggers during merge.

## Known Warnings

1. Live `validate-warehouse` Cloud Run Job path is not cleared from this local environment.
2. Dry-run metadata row `validate-warehouse-20260616T133114Z-5e7c51a8` remains a known non-live cleanup warning until BigQuery allows update.
3. Compatibility rollout is staged only for Trade Player History.
4. Some segment packet families still need real non-demo inputs before production content workflows are complete.
5. Claim ledger sample/demo data is draft-only and not public content.

## Rollback Plan

Application rollback:

1. Revert the Cloud Run service to the previous image.
2. Remove newly enabled staging feature flags.
3. Keep local subprocess Data Ops controls available.

Feature flag rollback:

```powershell
gcloud run services update <staging-service-name> --region <region> --remove-env-vars USE_COMPAT_TRADE_PLAYER_HISTORY
```

Cloud Run Jobs rollback:

1. Keep `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`.
2. Keep `DATA_OPS_ALLOW_JOB_TRIGGER=false`.
3. Delete or redeploy only the affected Cloud Run Job if a future job deploy fails.
4. Do not drop BigQuery tables as a rollback mechanism without an approved migration plan.

## Staging Plan

1. Merge the rebuild branch after PR review.
2. Deploy the Streamlit service to staging.
3. Keep all compatibility and Cloud Run Job trigger flags false.
4. Enable only `USE_COMPAT_TRADE_PLAYER_HISTORY=true` in staging.
5. Run the Trade Lab manual QA checklist from `docs/rebuild/validation/phase-15-3-trade-history-staging-promotion-report.md`.
6. Run narrow validation patterns.
7. Confirm no raw/source table access appears in compat path logs.
8. Confirm rollback by removing the flag in staging.

## Production Plan

Production is not approved in this package.

Before production:

1. Complete staging QA.
2. Confirm rollback has been tested.
3. Confirm Cloud Run service image and env vars are reviewed.
4. Confirm Secret Manager bindings.
5. Confirm IAM grants.
6. Confirm no pending migrations.
7. Confirm production feature flags remain false unless separately approved.

## Secret Manager Requirements

Required or planned secrets:

- `GEMINI_API_KEY`, only where Gemini calls are allowed.
- External API keys only in jobs or services that need them.

Rules:

- Do not commit service account JSON.
- Do not commit `.env` files.
- Do not pass secrets as plain deploy command env values.
- Bind Secret Manager secrets to specific services or jobs.

## IAM Requirements

Minimum expected grants:

- Runtime service account: project `roles/bigquery.jobUser`.
- Dataset access: scoped to job class.
- Secret access: per secret, not project-wide by default.
- Scheduler identity: invoke only for approved Cloud Run Jobs.
- Deploy identity: separate from runtime identity.

Do not change IAM automatically during this release.

## Do Not Enable Yet

- `USE_COMPAT_PLAYER_PROFILES`
- `USE_COMPAT_SLEEPER_WATCH`
- `USE_COMPAT_TRADE_ASSETS`
- `USE_COMPAT_VIEWER_TEAM_CONTEXT`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS`
- `DATA_OPS_ALLOW_JOB_TRIGGER`
- Cloud Scheduler jobs
- broad warehouse validation runs from Cloud Run Jobs
- external verification jobs without cost review
- production content publishing
- automatic claim grading for demo claims

## Merge Checklist

- [ ] Review `docs/rebuild/validation/phase-15-5-merge-readiness-report.md`.
- [ ] Confirm all keep-and-commit files are staged.
- [ ] Confirm no local-only files are staged.
- [ ] Confirm safety checker passes.
- [ ] Confirm tests pass.
- [ ] Confirm no pending migrations.
- [ ] Confirm validation dry-run passes.
- [ ] Open PR with `docs/rebuild/validation/phase-15-pr-summary-draft.md` as the source summary.
