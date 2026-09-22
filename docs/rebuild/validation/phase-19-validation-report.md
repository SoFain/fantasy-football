# Phase 19 Validation Report

Date: 2026-06-16

Final decision: GO WITH WARNINGS

Production classification: PRODUCTION PREVIEW ONLY

No production deploy was run. No Cloud Run Job was triggered. No Scheduler jobs were created. No LLM calls were made. No scraping occurred. No Firebase artifacts were created.

## Scope

Validated Phase 19 work:

- artifact classification
- authenticated staging QA rerun
- live `validate-warehouse` Cloud Run Job proof
- ingest-only modern source restore mode
- 2025 data restore and current-season marts
- real claims and trade inputs
- limited production deploy decision

## Required Reports

All required Phase 19 reports exist:

- `docs/rebuild/validation/phase-19-1-artifact-classification-report.md`
- `docs/rebuild/validation/phase-19-2-authenticated-staging-qa-rerun-report.md`
- `docs/rebuild/validation/phase-19-3-live-validate-warehouse-job-report.md`
- `docs/rebuild/validation/phase-19-4-ingest-only-mode-report.md`
- `docs/rebuild/validation/phase-19-5-modern-data-restore-report.md`
- `docs/rebuild/validation/phase-19-6-real-inputs-report.md`
- `docs/rebuild/validation/phase-19-7-limited-production-deploy-report.md`

## Repo And Safety Status

Commands run:

```powershell
git status --short
git diff --stat
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
```

Status:

- worktree is dirty with expected Phase 18 and Phase 19 docs and code changes
- modified tracked files: `app.py`, `src/pipeline.py`
- untracked relevant files include Phase 17, Phase 18, and Phase 19 validation docs, `src/ui_data_guards.py`, `tests/test_pipeline_plan.py`, and `tests/test_staging_ui_warning_fixes.py`
- safety checker: pass
- no tracked secret files detected
- no Firebase artifacts detected
- production feature defaults are safe
- Pigskin `execute_bigquery_sql` remains absent

Diff stat:

```text
app.py          |  34 ++++++-----
src/pipeline.py | 187 +++++++++++++++++++++++++++++++++++++++++++++++++++++---
2 files changed, 195 insertions(+), 26 deletions(-)
```

Untracked docs and tests are not included in this diff stat.

## Compile And Test Status

Commands run:

```powershell
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest discover tests
```

Results:

- `app.py` compile: pass
- `src` and `scripts` compile: pass
- unit tests: pass, `304 tests`

## Migration Status

Command run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
```

Result:

```text
No pending migrations.
```

## Validation Status

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_history
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern claim
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern backtest
```

Results:

| Pattern | Result |
|---|---|
| dry-run | pass |
| `compat_trade_player_history` | 6 passed, 0 failed |
| `cloud_run_job` | 8 passed, 0 failed |
| `content_brief` | 11 passed, 0 failed |
| `claim` | 17 passed, 0 failed |
| `market` | 9 passed, 0 failed |
| `backtest` | 11 passed, 0 failed |

Validation warnings:

- `compat_trade_player_history_identity_coverage`: informational row with missing identity rate `0.0`
- `claims_player_identity_coverage`: draft/demo warning, 1 unresolved claim-player row out of 3
- `claim_ledger_ui_sources_exist`: informational source-count row
- `claim_ledger_ui_draft_claims_allowed_missing_fields`: expected draft-claim missing-fields row
- `backtest_dashboard_latest_runs`: informational row, latest backtest run exists
- `backtest_dashboard_summary_available`: informational row, summary rows exist

No validation failures were reported.

## Hard Safety Checks

Status:

- Pigskin arbitrary SQL: absent
- `execute_bigquery_sql` in Pigskin-visible tools: absent
- `### Context Tool Protocol ###`: present in `app.py`
- raw/source tables blocked from Pigskin: pass
- raw/source table names in Pigskin schema are blocked-table entries, not exposed tools
- no tracked secrets: pass
- no Firebase artifacts: pass
- production risk flags safe by default: pass
- no Scheduler jobs created: pass
- Cloud Run Job triggers not default on: pass
- demo claims and packets excluded from public content: pass
- historical Fraud Watch not presented as current: pass
- fabricated claims or trades inserted: no

Static search found raw table names in:

- Pigskin blocked-table schema
- legacy Streamlit UI paths

This does not reintroduce Pigskin arbitrary SQL or raw/source table access to Pigskin-visible tools.

## Phase Results

### Phase 19.1 Artifact Classification

Status: READY FOR HUMAN REVIEW AND COMMIT

Phase 17 and Phase 18 artifacts were classified. Production remained not deployed.

### Phase 19.2 Authenticated Staging QA Rerun

Status: STAGING QA FAIL

Reason:

- staging is still running pre-fix image `staging-81ed959`
- staging does not include the Phase 18.3 UI fixes
- authenticated browser QA cannot validate the current UI fixes until staging is redeployed with a current reviewed image

This blocks production execution.

### Phase 19.3 Live Validate-Warehouse Job

Status: LIVE VALIDATE-WAREHOUSE NOT AUTHORIZED

The dry-run preview is valid, and Cloud Run job metadata validations pass. Live deploy and trigger were not run because required authorization env vars were not set.

### Phase 19.4 Ingest-Only Restore Mode

Status: BOUNDED INGEST-ONLY MODE READY

`src.pipeline` now has:

- `--ingest-only`
- `--allow-full-refresh`
- `--week-start` and `--week-end` reserved with safe live rejection
- explicit season requirement for live runs
- `WRITE_APPEND` default
- full-refresh guard for `WRITE_TRUNCATE`

Plan-only remains non-mutating.

### Phase 19.5 Modern Source Data Restore

Status: NOT AUTHORIZED, PLAN ONLY

`ALLOW_MODERN_SOURCE_INGEST` was unset. Only the non-mutating plan was run. No 2025 source rows were restored, and current-season marts were not rebuilt.

Modern data status:

- `play_by_play`: still blocked for 2025/2026 restore
- `weekly_metrics`: still blocked for 2025/2026 restore
- `analytics_player_weekly_truth`: not rebuilt
- `analytics_fraud_watch`: not rebuilt

### Fraud Watch Status

Status: BLOCKED FOR CURRENT-SEASON CONTENT

Current-season Fraud Watch cannot be represented as current content until real 2025 source rows are restored and marts are rebuilt. Historical Fraud Watch was not presented as current.

### Phase 19.6 Real Claims And Trade Inputs

Status: BLOCKED BY MISSING OPERATOR INPUTS

Current counts:

- `fantasy_claims`: 3 draft rows
- `claim_grades`: 0
- `trade_review_packets`: 0
- `trade_review_show` briefs: 0

No real operator-supplied claim CSV or trade sides were present. No claims or trade inputs were fabricated.

### Phase 19.7 Limited Production Deploy Decision

Status: PRODUCTION PREVIEW ONLY

No production deploy was run because:

- `ALLOW_LIMITED_PRODUCTION_DEPLOY` was unset
- staging QA is failed
- live `validate-warehouse` proof is not authorized and not waived

The digest-pinned production deploy command and rollback command are documented in `phase-19-7-limited-production-deploy-report.md`.

## Blockers

1. Staging QA rerun is `STAGING QA FAIL` because staging is still on a stale pre-fix image.
2. Live `validate-warehouse` Cloud Run Job proof is not authorized.
3. 2025 source data restore is not authorized.
4. Current-season Fraud Watch remains blocked by missing modern source rows.
5. Real claim and trade workflows remain blocked by missing operator inputs.
6. Limited production deploy is not authorized.

## Warnings

1. Worktree is dirty and needs human review before merge or release.
2. Claim ledger warnings reflect draft/demo state and one unresolved draft claim-player row.
3. Backtest dashboard validations return informational rows, not failures.
4. Trade history compatibility validation returns an informational coverage row with missing identity rate `0.0`.
5. Production candidate image exists, but production remains on the prior image.

## Production Status

`PRODUCTION PREVIEW ONLY`

Production was not deployed. Production risk flags remain safe. No production traffic changed.

## Recommended Phase 20 Work

1. Build and deploy a current reviewed staging image containing the Phase 18.3 UI fixes.
2. Rerun authenticated staging browser QA against that current staging image.
3. Decide whether to authorize or waive the live `validate-warehouse` proof.
4. If desired, set `ALLOW_MODERN_SOURCE_INGEST=true` and run the bounded 2025 ingest-only restore.
5. Rebuild current-season marts after source coverage is verified.
6. Generate current-season Fraud Watch only from real 2025 source rows.
7. Provide real operator claim CSV and real trade sides if claim grading and Trade Review content should advance.
8. Revisit limited production deploy only after staging QA is green and production approval is explicit.

## Final Decision

`GO WITH WARNINGS`

The code and warehouse validation gates passed, and no hard NO-GO condition was hit. Production remains preview-only because staging QA, live job proof, source restore, real inputs, and deploy authorization are still blocked.
