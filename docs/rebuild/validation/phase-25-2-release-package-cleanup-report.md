# Phase 25.2 Release Package Cleanup and Commit Review

Validation date: 2026-06-25 local.

## Final Decision

`RELEASE PACKAGE READY WITH WARNINGS`

The release package has a clear conservative commit plan. Source, BigQuery, tests, and final release evidence are ready to commit after normal owner review. Generated/local evidence is ignored and should stay out of the commit.

Warnings:

- The worktree still has many untracked historical Phase 17 through Phase 24 validation reports. Commit only the final release evidence set unless the owner wants full chronology in-repo.
- `pipeline_execution.log` is already tracked in git. It has no current worktree change, but it remains a local log style artifact and should be removed from the repo only in a separate owner-approved cleanup.
- Git emitted LF-to-CRLF working-copy warnings on several modified files. This is a packaging warning, not a test or safety failure.
- Production runtime warnings from Phase 25.1 remain non-blocking: BigQuery Storage REST fallback and Streamlit `use_container_width` deprecation.

No deployment, rollback, feature flag change, Cloud Run Job trigger, Scheduler change, ingestion, score materialization, LLM-backed action, scraping, or Firebase artifact creation occurred during this phase.

## Authorization Gate State

All checked authorization gates were unset:

| Gate | State |
| --- | --- |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | empty |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | empty |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | empty |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | empty |

No authorization gate was set.

## Git Status Summary

Initial inspection before creating this report:

| Item | Count |
| --- | ---: |
| Modified tracked files | 12 |
| Untracked files | 107 |
| Deleted files | 0 |
| Untracked Phase validation docs | 80 |
| Untracked BigQuery files | 17 |
| Test files in status | 6 |

Modified tracked files:

```text
.dockerignore
.gitignore
Dockerfile
app.py
docs/rebuild/compatibility-contracts.md
docs/rebuild/table-classification.md
docs/rebuild/ui-query-debt-register.md
src/compat_flags.py
src/load.py
src/pipeline.py
tests/test_cloud_run_jobs.py
tests/test_streamlit_compat_rollout.py
```

New ignore file:

```text
.gcloudignore
```

## Ignore and Build Packaging Review

| File | Classification | Notes |
| --- | --- | --- |
| `.gitignore` | keep and commit | Excludes `output/`, `pipeline_execution.log`, `*.log`, `.codex-remote-attachments/`, and `.codex-tools/`. |
| `.dockerignore` | keep and commit | Hardened to exclude `output/`, Codex temp folders, `.env`, `.env.*`, and `.gcloudignore` from Docker build context. |
| `.gcloudignore` | keep and commit | Added to prevent generated evidence, logs, env files, caches, and local tool folders from Cloud Build source uploads. |
| `output/` | generated, do not commit | Local evidence directory exists with 798 files and is ignored. |
| `.codex-remote-attachments/` | generated/local, do not commit | Local attachment cache exists and is ignored. |
| `.codex-tools/` | generated/local, do not commit | Local tooling cache exists and is ignored. |
| `pipeline_execution.log` | owner review | File is already tracked and clean in the current worktree. Do not add new changes. Consider removal in a separate cleanup only if owner approves. |
| `.env`, `.env.*` | risky, do not commit | Ignored and excluded from Docker and Cloud Build submissions. |
| `node_modules/` | generated, do not commit | Not present. |

## File Classification

### Release Code Candidates

| File | Classification | Rationale |
| --- | --- | --- |
| `app.py` | keep and commit | Contains staging-validated UI guard fixes, Trade Lab summary fix, and default-off Trade Analyzer score UI wiring. |
| `src/compat_flags.py` | keep and commit | Adds default-off score flags to the compatibility flag registry. |
| `src/load.py` | keep and commit | Adds schema-aware append coercion for source ingest safety. |
| `src/pipeline.py` | keep and commit | Adds bounded plan-only and ingest-only safety behavior. |
| `src/ui_data_guards.py` | keep and commit | New UI display guard helpers for profile, sleeper, and Trade Lab data. |
| `src/trade_player_scores.py` | keep and commit | New deterministic Trade Analyzer score builder and read helpers. |
| `Dockerfile` | keep and commit | Copies validation runner and validation SQL into the image for `validate-warehouse`. |
| `src/job_runner.py` | no current diff | Keep as existing source. It was part of validation context but has no current worktree change. |
| `scripts/deploy_cloud_run_jobs.ps1` | no current diff | Keep as existing source. It was part of validation context but has no current worktree change. |
| `scripts/deploy_cloud_run_jobs.sh` | no current diff | Keep as existing source. |

### BigQuery Release Candidates

| File or group | Classification | Rationale |
| --- | --- | --- |
| `bigquery/migrations/0025__trade_analyzer_score_v0.sql` | keep and commit | Additive Trade Analyzer score schema migration. Already applied and validated. |
| `bigquery/views/trade_player_scores_current.sql` | keep and commit | Current score view. |
| `bigquery/views/compat_trade_player_scores_current.sql` | keep and commit | Compatibility score view with no raw/source dependency. |
| `bigquery/contracts/trade_player_scores.md` | keep and commit | Score table contract. |
| `bigquery/contracts/trade_player_scores_current.md` | keep and commit | Current view contract. |
| `bigquery/contracts/compat_trade_player_scores_current.md` | keep and commit | Compatibility view contract. |
| `bigquery/validations/150_trade_player_scores_grain.sql` through `160_trade_player_scores_identity_coverage.sql` | keep and commit | Trade score validation suite passed. |

### Test Candidates

| File | Classification | Rationale |
| --- | --- | --- |
| `tests/test_trade_player_scores.py` | keep and commit | Covers deterministic score builder behavior. |
| `tests/test_streamlit_compat_rollout.py` | keep and commit | Covers score flags and default-off behavior. |
| `tests/test_staging_ui_warning_fixes.py` | keep and commit | Covers legacy UI warning fixes and Trade Lab side summaries. |
| `tests/test_pipeline_plan.py` | keep and commit | Covers plan-only and ingest-only safety. |
| `tests/test_validate_warehouse_image_packaging.py` | keep and commit | Proves validation runner packaging for the Cloud Run Job image. |
| `tests/test_cloud_run_jobs.py` | keep and commit | Adds narrow validate-warehouse dry-run trigger coverage. |

### Documentation Candidates

| File or group | Classification | Rationale |
| --- | --- | --- |
| `docs/rebuild/trade-analyzer-scoring-model-v0.md` | keep and commit | Trade Analyzer scoring model spec. |
| `docs/rebuild/trade-analyzer-score-rollout.md` | keep and commit | Default-off rollout plan. |
| `docs/rebuild/modern-source-data-restore.md` | keep and commit | Bounded modern source restore docs. |
| `docs/rebuild/compatibility-contracts.md` | keep and commit | Adds Trade Analyzer score compatibility contract references. |
| `docs/rebuild/table-classification.md` | keep and commit | Adds Trade Analyzer score table classification. |
| `docs/rebuild/ui-query-debt-register.md` | keep and commit | Records score compatibility view path. |
| `docs/rebuild/validation/phase-23-validation-report.md` | keep and commit | Final Phase 23 validation summary. |
| `docs/rebuild/validation/phase-24-1a-validate-warehouse-image-path-fix-report.md` | keep and commit | Documents the image path fix for validate-warehouse. |
| `docs/rebuild/validation/phase-24-1b-live-validate-warehouse-proof-report.md` | keep and commit | Documents successful live proof with fixed image. |
| `docs/rebuild/validation/phase-24-2r-production-deploy-gate-report.md` | keep and commit | Documents approved all-flags-off production gate. |
| `docs/rebuild/validation/phase-24-3r-production-deploy-and-smoke-report.md` | keep and commit | Documents production deploy and smoke result. |
| `docs/rebuild/validation/phase-24-4-production-postdeploy-validation-report.md` | keep and commit | Documents postdeploy validation. |
| `docs/rebuild/validation/phase-25-1-production-hold-monitoring-report.md` | keep and commit | Documents production hold pass. |
| `docs/rebuild/validation/phase-25-2-release-package-cleanup-report.md` | keep and commit | This report. |

### Owner Review Before Commit

| File or group | Recommendation | Rationale |
| --- | --- | --- |
| `docs/rebuild/validation/phase-17-*.md` | owner review | Historical evidence. Not needed for a concise release commit unless full chronology is desired. |
| `docs/rebuild/validation/phase-18-*.md` | owner review | Historical evidence. Commit only if the repo should preserve full rollout detail. |
| `docs/rebuild/validation/phase-19-*.md` | owner review | Historical evidence. Can be summarized by final validation docs. |
| `docs/rebuild/validation/phase-20-*.md` | owner review | Historical evidence. Several reports document blocked or superseded steps. |
| `docs/rebuild/validation/phase-21-*.md` | owner review | Historical evidence. Production remained blocked in this phase. |
| `docs/rebuild/validation/phase-22-*.md` | owner review | Historical evidence. Some reports are useful for score contracts, but final Phase 23/24 reports are the cleaner release evidence. |
| `docs/rebuild/validation/phase-23-1a-*.md`, `phase-23-1b-*.md`, `phase-23-3a-*.md`, `phase-23-3b-*.md`, `phase-23-3b-r-*.md`, `phase-23-3e-*.md`, `phase-23-3f-*.md`, `phase-23-3f-r-*.md`, `phase-23-3g-*.md` | owner review | Intermediate investigation and tuning reports. Commit only if detailed audit history is desired. |
| `docs/rebuild/validation/phase-24-1-live-validate-warehouse-proof-report.md`, `phase-24-2-production-deploy-gate-report.md`, `phase-24-3-production-deploy-and-smoke-report.md` | owner review | Superseded by the fixed `24-1a`, `24-1b`, `24-2r`, and `24-3r` reports. |
| `pipeline_execution.log` | owner review | Already tracked local log. No current diff. Do not stage local log changes. |

### Exclude From Commit

| Path or pattern | Reason |
| --- | --- |
| `output/` | Generated browser and QA evidence. |
| `output/playwright/` | Generated browser artifacts. |
| `.codex-remote-attachments/` | Local attachment cache. |
| `.codex-tools/` | Local tool cache. |
| `*.log` | Runtime and command logs. |
| `.env`, `.env.*` | Local secrets or environment state. |
| `node_modules/` | Dependency cache, not present. |
| `cache/`, `*.parquet` | Local cache data. |
| `*.json` secret or service account files | Must not be committed. No active candidate JSON files were found. |

## Recommended Commit Set

Recommended source and packaging files:

```text
.dockerignore
.gcloudignore
.gitignore
Dockerfile
app.py
src/compat_flags.py
src/load.py
src/pipeline.py
src/trade_player_scores.py
src/ui_data_guards.py
tests/test_cloud_run_jobs.py
tests/test_pipeline_plan.py
tests/test_staging_ui_warning_fixes.py
tests/test_streamlit_compat_rollout.py
tests/test_trade_player_scores.py
tests/test_validate_warehouse_image_packaging.py
```

Recommended BigQuery files:

```text
bigquery/contracts/compat_trade_player_scores_current.md
bigquery/contracts/trade_player_scores.md
bigquery/contracts/trade_player_scores_current.md
bigquery/migrations/0025__trade_analyzer_score_v0.sql
bigquery/views/compat_trade_player_scores_current.sql
bigquery/views/trade_player_scores_current.sql
bigquery/validations/150_trade_player_scores_grain.sql
bigquery/validations/151_trade_player_scores_trade_score_range.sql
bigquery/validations/152_trade_player_scores_component_score_range.sql
bigquery/validations/153_trade_player_scores_confidence_range.sql
bigquery/validations/154_trade_player_scores_required_json_fields.sql
bigquery/validations/155_trade_player_scores_missing_flags_exist.sql
bigquery/validations/156_trade_player_scores_source_freshness_exists.sql
bigquery/validations/157_trade_player_scores_current_grain.sql
bigquery/validations/158_compat_trade_player_scores_current_exists.sql
bigquery/validations/159_compat_trade_player_scores_no_raw_source_dependencies.sql
bigquery/validations/160_trade_player_scores_identity_coverage.sql
```

Recommended documentation files:

```text
docs/rebuild/compatibility-contracts.md
docs/rebuild/modern-source-data-restore.md
docs/rebuild/table-classification.md
docs/rebuild/trade-analyzer-score-rollout.md
docs/rebuild/trade-analyzer-scoring-model-v0.md
docs/rebuild/ui-query-debt-register.md
docs/rebuild/validation/phase-23-validation-report.md
docs/rebuild/validation/phase-24-1a-validate-warehouse-image-path-fix-report.md
docs/rebuild/validation/phase-24-1b-live-validate-warehouse-proof-report.md
docs/rebuild/validation/phase-24-2r-production-deploy-gate-report.md
docs/rebuild/validation/phase-24-3r-production-deploy-and-smoke-report.md
docs/rebuild/validation/phase-24-4-production-postdeploy-validation-report.md
docs/rebuild/validation/phase-25-1-production-hold-monitoring-report.md
docs/rebuild/validation/phase-25-2-release-package-cleanup-report.md
```

## Checks Run

| Command | Result |
| --- | --- |
| `git status --short` | pass, worktree classified |
| `git diff --stat` | pass with LF-to-CRLF warnings |
| `git diff --name-only` | pass with LF-to-CRLF warnings |
| `git ls-files --others --exclude-standard` | pass, untracked files classified |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 346 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass |

Safety checker details:

| Check | Result |
| --- | --- |
| `no_firebase_artifacts` | pass |
| `no_tracked_secret_files` | pass |
| `no_secret_content` | pass |
| `required_files_exist` | pass |
| `feature_flags_default_off` | pass |
| `pigskin_no_execute_bigquery_sql` | pass |
| `app_py_compiles` | pass |
| `src_scripts_compile` | pass |

Secret scan:

- Targeted scan found only expected script variable names and documentation placeholders.
- No private key, service account JSON payload, bearer token, or local credential value was identified in commit candidates.

## Release Note Draft

Production was deployed all flags off and passed postdeploy and hold monitoring on revision `nfl-studio-dashboard-00075-x7p`.

Included changes:

- Added default-off Trade Analyzer score v0 contracts, additive BigQuery migration, current and compatibility views, validations, deterministic builder, and tests.
- Validated Trade Analyzer score UI in staging while keeping score flags disabled in production.
- Fixed the `validate-warehouse` Cloud Run Job image packaging path and proved the live job path with a narrow `model_runs` validation.
- Added schema-aware append hardening and bounded ingest-only planning safeguards for modern source data restore.
- Fixed staging UI warnings for Player Profiles, Versus Finder, Sleeper Watch, and Trade Lab side summaries.
- Hardened git, Docker, and Cloud Build ignore rules so local evidence, logs, env files, and Codex caches stay out of commits and image contexts.

Production remains conservative:

- Trade Analyzer score flags are false in production.
- Trade History compatibility is false in production.
- Data Ops job trigger flags are false in production.
- Score rows remain staging-review only.
- No Cloud Run Jobs are triggerable by default.

Remaining cleanup:

- Decide whether to commit the full historical Phase 17 through Phase 22 validation archive or rely on final Phase 23 through Phase 25 release evidence.
- Consider removing tracked `pipeline_execution.log` in a separate owner-approved cleanup.
- Clean up BigQuery Storage REST fallback and Streamlit deprecation warnings in a later non-release task.

## Remaining Warnings

- Large untracked validation-doc backlog requires owner policy: full chronology versus concise final release evidence.
- `pipeline_execution.log` is tracked historical noise and should not receive new changes.
- CRLF warnings appeared during git diff commands.
- Production warning logs remain non-blocking and known from Phase 25.1.

## Commit Recommendation

Proceed with the recommended commit set above after owner review. Do not use `git add .`.

Suggested staging approach:

```powershell
git add .dockerignore .gcloudignore .gitignore Dockerfile app.py src/compat_flags.py src/load.py src/pipeline.py src/trade_player_scores.py src/ui_data_guards.py
git add tests/test_cloud_run_jobs.py tests/test_pipeline_plan.py tests/test_staging_ui_warning_fixes.py tests/test_streamlit_compat_rollout.py tests/test_trade_player_scores.py tests/test_validate_warehouse_image_packaging.py
git add bigquery/contracts/compat_trade_player_scores_current.md bigquery/contracts/trade_player_scores.md bigquery/contracts/trade_player_scores_current.md bigquery/migrations/0025__trade_analyzer_score_v0.sql bigquery/views/compat_trade_player_scores_current.sql bigquery/views/trade_player_scores_current.sql bigquery/validations/150_trade_player_scores_grain.sql bigquery/validations/151_trade_player_scores_trade_score_range.sql bigquery/validations/152_trade_player_scores_component_score_range.sql bigquery/validations/153_trade_player_scores_confidence_range.sql bigquery/validations/154_trade_player_scores_required_json_fields.sql bigquery/validations/155_trade_player_scores_missing_flags_exist.sql bigquery/validations/156_trade_player_scores_source_freshness_exists.sql bigquery/validations/157_trade_player_scores_current_grain.sql bigquery/validations/158_compat_trade_player_scores_current_exists.sql bigquery/validations/159_compat_trade_player_scores_no_raw_source_dependencies.sql bigquery/validations/160_trade_player_scores_identity_coverage.sql
git add docs/rebuild/compatibility-contracts.md docs/rebuild/modern-source-data-restore.md docs/rebuild/table-classification.md docs/rebuild/trade-analyzer-score-rollout.md docs/rebuild/trade-analyzer-scoring-model-v0.md docs/rebuild/ui-query-debt-register.md docs/rebuild/validation/phase-23-validation-report.md docs/rebuild/validation/phase-24-1a-validate-warehouse-image-path-fix-report.md docs/rebuild/validation/phase-24-1b-live-validate-warehouse-proof-report.md docs/rebuild/validation/phase-24-2r-production-deploy-gate-report.md docs/rebuild/validation/phase-24-3r-production-deploy-and-smoke-report.md docs/rebuild/validation/phase-24-4-production-postdeploy-validation-report.md docs/rebuild/validation/phase-25-1-production-hold-monitoring-report.md docs/rebuild/validation/phase-25-2-release-package-cleanup-report.md
```

Do not stage `output/`, `.codex-remote-attachments/`, `.codex-tools/`, `pipeline_execution.log`, local logs, env files, browser artifacts, cache files, or superseded validation reports unless the owner explicitly asks for them.
