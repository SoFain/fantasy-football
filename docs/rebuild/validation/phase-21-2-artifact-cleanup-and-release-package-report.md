# Phase 21.2 Artifact Cleanup and Release Package Report

## Final Decision

`RELEASE PACKAGE NEEDS REVIEW`

The repo is healthy from a code, test, migration, validation, and safety-check perspective, but the release package should not be merged until the tracked `pipeline_execution.log` diff is explicitly excluded or reviewed. Generated browser QA and runtime artifacts under `output/` are now ignored and should remain local.

## Scope

Phase 21.2 classified Phase 17 through Phase 20 artifacts, source changes, tests, logs, and generated QA output before merge or release packaging.

No deployment, ingestion, materialization, Cloud Run Job trigger, Scheduler creation, scraping, LLM call, Firebase artifact creation, or production flag change was performed.

## Commands Run

| Command | Result |
| --- | --- |
| `git status --short` | Pass, worktree inventory captured |
| `git diff --stat` | Pass, modified tracked files identified |
| `git diff --name-status` | Pass, tracked modifications identified |
| `git ls-files --others --exclude-standard` | Pass, untracked docs/source/tests captured |
| `git ls-files -d` | Pass, no deleted tracked files |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | Pass, 309 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py` | Pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | Pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | Pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | Pass, 149 validation files discovered |

## Worktree Summary

Tracked modified files after cleanup:

| File | Classification | Package action | Notes |
| --- | --- | --- | --- |
| `.gitignore` | keep and commit | commit | Adds generated run artifact exclusions for `output/`, `pipeline_execution.log`, and `*.log`. |
| `app.py` | keep but review carefully | commit after human review | Contains Phase 18.3 and Phase 20.2A UI fixes for Player Profiles, Versus Finder, Sleeper Watch, and Trade Lab summary behavior. Pigskin prompt safety remains covered by tests. |
| `src/pipeline.py` | keep but review carefully | commit after human review | Adds plan-only and ingest-only safety behavior, explicit season guardrails, `WRITE_APPEND` default, and full-refresh protections. |
| `pipeline_execution.log` | generated/local, do not commit | exclude | Tracked file contains 2025 ingest runtime noise and schema mismatch logs. It remains modified because it is already tracked. Restore or untrack before staging release changes unless the owner explicitly wants it committed. |

Deleted tracked files:

| Status | Details |
| --- | --- |
| none | `git ls-files -d` returned no deleted tracked files. |

## Untracked Source and Test Files

| File | Classification | Package action | Notes |
| --- | --- | --- | --- |
| `src/ui_data_guards.py` | keep and commit | commit | Small UI guard helper for legacy display columns and Trade Lab asset label resolution. No secrets or generated content found. |
| `tests/test_pipeline_plan.py` | keep and commit | commit | Covers plan-only, ingest-only, unbounded-run rejection, week-bound rejection, and truncate authorization. |
| `tests/test_staging_ui_warning_fixes.py` | keep and commit | commit | Covers missing `pos_abb` fallback, missing `rolling_3_week_ppr`, Trade Lab Side A and Side B label resolution, and feature flag defaults. |

## Validation Docs

| Artifact group | Files | Classification | Package action |
| --- | --- | --- | --- |
| Phase 17 validation docs | 9 files under `docs/rebuild/validation/phase-17-*.md` | keep but human-review carefully | Commit as release evidence if detailed phase history is desired. |
| Phase 18 validation docs | 9 files under `docs/rebuild/validation/phase-18-*.md` | keep but human-review carefully | Commit as release evidence after checking production metadata summaries and secret redactions. |
| Phase 19 validation docs | 8 files under `docs/rebuild/validation/phase-19-*.md` | keep but human-review carefully | Commit as release evidence after checking operational command previews. |
| Phase 20 validation docs | 13 files under `docs/rebuild/validation/phase-20-*.md` | keep but human-review carefully | Commit as release evidence after checking staging QA screenshots are referenced only through local output paths. |
| Phase 20 follow-up reports | `phase-20-2a-*`, `phase-20-2b-*`, `phase-20-4a-*`, `phase-20-4b-*` | keep but human-review carefully | These are useful for release evidence and explain resolved warnings and ingest audit outcomes. |
| `docs/rebuild/validation/phase-21-1-validate-warehouse-proof-resolution-report.md` | 1 file | keep but human-review carefully | Documents remaining live validate-warehouse proof blocker. |
| `docs/rebuild/modern-source-data-restore.md` | 1 file | keep and commit | Documents safe bounded modern source restore workflow. |
| `docs/rebuild/validation/phase-21-2-artifact-cleanup-and-release-package-report.md` | this report | keep and commit | Current artifact classification and package decision. |

Recommended doc package:

- Keep Phase 17 through Phase 20 validation docs as release evidence if the branch is meant to preserve the full rebuild audit trail.
- If the PR needs a smaller review footprint, summarize them in one release note and exclude detailed phase reports from the PR after owner approval.
- Do not include generated screenshots, JSON, proxy logs, or local browser artifacts unless explicitly requested.

## Generated and Local Artifacts

| Path | Classification | Package action | Notes |
| --- | --- | --- | --- |
| `output/` | generated/local, do not commit | ignored | Contains browser QA screenshots, Playwright dependencies, local proxy logs, PID files, BigQuery audit JSON/logs, and phase command logs. |
| `output/playwright/` | generated/local, do not commit | ignored | Contains local Playwright package files, `node_modules`, auth proxy code, screenshots, and browser QA output. |
| `output/phase-20-*` | generated/local, do not commit | ignored | Contains phase-specific command logs, screenshots, and BigQuery result JSON. |
| `pipeline_execution.log` | generated/local, do not commit | exclude tracked diff | Contains local runtime logs and BigQuery schema mismatch output from ingest attempts. |
| `*.log` | generated/local, do not commit | ignored | Broad log ignore added to avoid accidental local log inclusion. |
| `.codex-remote-attachments/` | generated/local, do not commit | already ignored | Existing ignore rule present. |

Generated artifact inventory before ignore update showed `output/` with 601 files and 93 directories. After ignore update, `output/` no longer appears in `git ls-files --others --exclude-standard`.

## Gitignore Changes

Added:

```gitignore
# Local run artifacts
output/
pipeline_execution.log
*.log
```

Important limitation: `pipeline_execution.log` is already tracked, so `.gitignore` does not hide its current modified tracked diff. Before merge, either restore the log file or explicitly untrack it in a separate owner-approved cleanup.

## Secret and Risky Content Check

Safety checker result:

- no Firebase artifacts: pass
- no tracked secret files: pass
- no secret content: pass
- required files exist: pass
- feature flags default off: pass
- Pigskin `execute_bigquery_sql` absent: pass
- `app.py` compiles: pass
- `src` and `scripts` compile: pass

Targeted source/doc search found only documented secret names or redacted references, such as Secret Manager bindings for `GEMINI_API_KEY`. No secret values, private keys, service account JSON, identity tokens, cookies, or credentials were identified in commit candidates.

Generated `output/` files include auth proxy artifacts and command logs. Those files are classified as local/generated and excluded from the package.

## Source Safety Review

| Area | Status | Evidence |
| --- | --- | --- |
| Pigskin arbitrary SQL | pass | `execute_bigquery_sql` remains absent from Pigskin-visible tools, and tests cover absence. |
| Context Tool Protocol | pass | `### Context Tool Protocol ###` remains in `app.py` and is covered by `tests/test_pigskin_chat_schema.py`. |
| Raw/source tables to Pigskin | pass | Pigskin schema continues to block raw/source tables. Existing legacy Streamlit paths are separate from Pigskin-visible schema. |
| Production feature flags | pass | Feature flag tests confirm defaults remain false. |
| Cloud Run job triggers | pass | Data Ops live triggers remain gated by `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=true` and `DATA_OPS_ALLOW_JOB_TRIGGER=true`. |
| Plan-only pipeline mode | pass | `build_pipeline_plan` is non-mutating and tests cover no write behavior. |
| Ingest-only pipeline mode | pass | `run_pipeline(..., ingest_only=True)` skips materialization and tests cover that behavior. |
| Destructive load protection | pass | `WRITE_TRUNCATE` requires `--allow-full-refresh`; default is `WRITE_APPEND`. |

## Commit Candidates

Recommended for commit after human review:

- `.gitignore`
- `app.py`
- `src/pipeline.py`
- `src/ui_data_guards.py`
- `tests/test_pipeline_plan.py`
- `tests/test_staging_ui_warning_fixes.py`
- `docs/rebuild/modern-source-data-restore.md`
- Phase 17 through Phase 20 validation reports, if full release evidence is desired
- `docs/rebuild/validation/phase-21-1-validate-warehouse-proof-resolution-report.md`
- `docs/rebuild/validation/phase-21-2-artifact-cleanup-and-release-package-report.md`

## Exclude Candidates

Do not commit:

- `pipeline_execution.log` current tracked diff
- `output/`
- `output/playwright/`
- `output/phase-20-*`
- browser QA screenshots unless explicitly approved as release evidence
- proxy logs, PID files, local JSON captures, and command logs
- any local `.log` files

## Human Review Items

| Item | Review needed |
| --- | --- |
| `pipeline_execution.log` | Decide whether to restore tracked file, untrack it, or intentionally commit ingest logs. Recommended action is restore or untrack, not commit. |
| Phase 17 through Phase 20 validation docs | Decide whether the PR should include all detailed phase evidence or a smaller summarized set. |
| `app.py` | Review UI changes around legacy display fallbacks and Trade Lab Side A and Side B summary rendering. |
| `src/pipeline.py` | Review plan-only and ingest-only behavior, especially default `WRITE_APPEND` and refusal rules. |
| Production release package | Keep production blocked until live validate-warehouse proof is passed or formally waived and production deploy authorization is set. |

## Production Status

Production remains untouched.

Current release posture from Phase 20:

- Phase 20 validation decision: `STAGING ONLY`
- Phase 20.8 production report: `PRODUCTION DEPLOY BLOCKED`
- Phase 21.1 validate-warehouse proof: `LIVE VALIDATE-WAREHOUSE STILL BLOCKED`
- No production deployment was authorized or performed in Phase 21.2
- Production risk flags remain expected to be false

## Final Recommendation

Proceed with PR/release packaging only after the tracked `pipeline_execution.log` diff is excluded or explicitly approved. Source and test changes are ready for human review, generated artifacts are now ignored, and all requested safety and validation checks passed.
