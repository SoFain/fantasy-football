# Phase 19.1 Artifact Classification Report

Date: 2026-06-16

Final status: READY FOR HUMAN REVIEW AND COMMIT

No deploy was run. No migrations were applied. No Cloud Run Jobs were triggered. No LLM calls were made. No scraping occurred. No Firebase artifacts were created. Production remains not deployed.

## Purpose

Classify Phase 17 and Phase 18 artifacts, review the modified code paths, and prepare a clean review package for the production-candidate branch.

## Repo Inventory

`git status --short`:

```text
 M app.py
 M src/pipeline.py
?? docs/rebuild/validation/phase-17-validation-report.md
?? docs/rebuild/validation/phase-18-1-production-candidate-image-report.md
?? docs/rebuild/validation/phase-18-2-production-baseline-report.md
?? docs/rebuild/validation/phase-18-3-staging-ui-warning-fix-report.md
?? docs/rebuild/validation/phase-18-4-live-validate-warehouse-job-report.md
?? docs/rebuild/validation/phase-18-5-modern-source-data-report.md
?? docs/rebuild/validation/phase-18-6-current-season-fraud-watch-materialization-report.md
?? docs/rebuild/validation/phase-18-7-real-inputs-report.md
?? docs/rebuild/validation/phase-18-8-limited-production-candidate-report.md
?? docs/rebuild/validation/phase-18-validation-report.md
?? src/ui_data_guards.py
?? tests/test_pipeline_plan.py
?? tests/test_staging_ui_warning_fixes.py
```

`git diff --stat`:

```text
app.py          | 34 changed
src/pipeline.py | 79 changed
```

Git reported Windows line-ending warnings for `app.py` and `src/pipeline.py`:

```text
LF will be replaced by CRLF the next time Git touches it
```

No generated cache files, local logs, secrets, service account JSON, private keys, `.env` files, or Firebase artifacts were found in the changed/untracked set.

## File Classification

| File | Classification | Rationale |
|---|---|---|
| `app.py` | keep but human-review carefully | Contains Phase 18.3 legacy UI fixes for Player Profiles, Versus Finder, Sleeper Watch, and Trade Lab Side B behavior. Tests pass, but `app.py` is broad and user-facing. |
| `src/pipeline.py` | keep but human-review carefully | Adds non-mutating `--plan-only` pipeline planning. Safe by tests, but note the pipeline remains season-bounded only. |
| `src/ui_data_guards.py` | keep and commit | Small helper module for legacy UI display safety. No warehouse writes or external calls. |
| `tests/test_pipeline_plan.py` | keep and commit | Covers non-mutating plan-only behavior and destructive-risk flags. |
| `tests/test_staging_ui_warning_fixes.py` | keep and commit | Covers Phase 18.3 UI guards and confirms compat flags default false. |
| `docs/rebuild/validation/phase-17-validation-report.md` | keep and commit | Required validation evidence carried forward into Phase 18/19. |
| `docs/rebuild/validation/phase-18-1-production-candidate-image-report.md` | keep and commit | Records immutable image build and digest. |
| `docs/rebuild/validation/phase-18-2-production-baseline-report.md` | keep and commit | Records production baseline and rollback commands without secret values. |
| `docs/rebuild/validation/phase-18-3-staging-ui-warning-fix-report.md` | keep and commit | Records UI fix scope and pending staging browser QA warning. |
| `docs/rebuild/validation/phase-18-4-live-validate-warehouse-job-report.md` | keep and commit | Documents live job proof as not authorized. |
| `docs/rebuild/validation/phase-18-5-modern-source-data-report.md` | keep and commit | Documents modern source blocker and plan-only pipeline mode. |
| `docs/rebuild/validation/phase-18-6-current-season-fraud-watch-materialization-report.md` | keep and commit | Documents honest Fraud Watch blocker without historical substitution. |
| `docs/rebuild/validation/phase-18-7-real-inputs-report.md` | keep and commit | Documents missing real claims/trade inputs. |
| `docs/rebuild/validation/phase-18-8-limited-production-candidate-report.md` | keep and commit | Records production deploy preview only and all risk flags off. |
| `docs/rebuild/validation/phase-18-validation-report.md` | keep and commit | Final Phase 18 validation summary and production classification. |

## Files To Commit

Recommended commit set:

```text
app.py
src/pipeline.py
src/ui_data_guards.py
tests/test_pipeline_plan.py
tests/test_staging_ui_warning_fixes.py
docs/rebuild/validation/phase-17-validation-report.md
docs/rebuild/validation/phase-18-1-production-candidate-image-report.md
docs/rebuild/validation/phase-18-2-production-baseline-report.md
docs/rebuild/validation/phase-18-3-staging-ui-warning-fix-report.md
docs/rebuild/validation/phase-18-4-live-validate-warehouse-job-report.md
docs/rebuild/validation/phase-18-5-modern-source-data-report.md
docs/rebuild/validation/phase-18-6-current-season-fraud-watch-materialization-report.md
docs/rebuild/validation/phase-18-7-real-inputs-report.md
docs/rebuild/validation/phase-18-8-limited-production-candidate-report.md
docs/rebuild/validation/phase-18-validation-report.md
docs/rebuild/validation/phase-19-1-artifact-classification-report.md
```

## Files Excluded

No current changed or untracked file is classified as generated, local-only, or do-not-commit.

No secrets, service account files, local caches, or generated binaries are marked for commit.

## Files Needing Human Review

Human review should focus on:

1. `app.py`
2. `src/pipeline.py`
3. `docs/rebuild/validation/phase-18-8-limited-production-candidate-report.md`
4. `docs/rebuild/validation/phase-18-validation-report.md`

## app.py Review

Status: pass with human review recommended

Confirmed:

- Phase 18.3 UI fixes are narrow and focused on legacy display failures.
- Player Profiles no longer directly selects `depth_charts.pos_abb`.
- Versus Finder benefits from the shared Player Profiles guard.
- Sleeper Watch derives `rolling_3_week_ppr` from `fantasy_points_last_3`.
- Trade Lab Side A and Side B collect selected assets through the same helper.
- Immediate `st.rerun()` was removed from side-selection blocks to avoid stale Side B display.
- Production feature flags remain default false.
- Cloud Run Job triggers remain gated by feature flags and explicit allow flags.
- Pigskin arbitrary SQL remains absent by safety checker.
- `execute_bigquery_sql` remains absent from Pigskin-visible tools by safety checker and tests.
- `### Context Tool Protocol ###` remains present in `app.py`.
- Raw/source table names remain blocked in Pigskin schema, not exposed as allowed Pigskin tools.

Known note:

- `app.py` still has legacy UI BigQuery reads by design. This phase did not migrate all legacy Streamlit paths to compatibility objects.

## src/pipeline.py Review

Status: pass with one known limitation

Confirmed:

- `--plan-only` exits before `run_pipeline()`.
- Plan-only mode does not extract data.
- Plan-only mode does not create a BigQuery client.
- Plan-only mode does not write to BigQuery.
- Plan-only mode does not call `materialize_all()`.
- The plan reports raw load truncation risk when `WRITE_TRUNCATE` is selected.
- The plan reports derived table replacement risk because current materializers use `CREATE OR REPLACE TABLE`.
- Tests cover non-mutating plan-only behavior.

Known limitation:

- The current pipeline supports bounded seasons, not bounded weeks. The plan explicitly reports `week_bound_supported: false`. This is existing behavior plus clearer reporting, not a new destructive behavior.

Plan-only command verified:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --write-disposition WRITE_APPEND --dataset fantasy_football_brain --plan-only
```

Result:

```text
will_extract: false
will_write_bigquery: false
will_materialize: false
bounded_by: season
week_bound_supported: false
destructive_risk.raw_load_truncate: false
destructive_risk.derived_create_or_replace: true
```

## Validation Results

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

```text
deployment safety: pass
unit tests: 298 passed
app.py compile: pass
src and scripts compile: pass
pending migrations: none
validation dry-run: pass, 149 validation files discovered
```

Safety checker confirmed:

- no Firebase artifacts
- no tracked secret files
- no secret content
- required files exist
- feature flags default off
- Pigskin arbitrary SQL remains absent
- `app.py`, `src`, and `scripts` compile

## Production Status

Production remains not deployed.

Phase 18 production classification remains:

```text
PRODUCTION CANDIDATE READY, NOT DEPLOYED
```

Production risk flags remain false by default. The production baseline report showed all risk flags unset in production.

## Remaining Warnings

1. `app.py` and `src/pipeline.py` report Windows line-ending warnings.
2. `src/pipeline.py` supports season-bound planning, not week-bound ingestion.
3. Authenticated staging browser QA after Phase 18.3 UI fixes is still pending.
4. Live `validate-warehouse` Cloud Run Job proof is still not authorized.
5. Modern 2025/2026 Fraud Watch source rows remain missing.
6. Real claim and trade inputs remain missing.

## Final Decision

```text
READY FOR HUMAN REVIEW AND COMMIT
```

The full changed/untracked set is classified. No secrets or generated cache files are marked for commit. Tests and safety checks pass. Production remains not deployed.
