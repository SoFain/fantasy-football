# Phase 28.12 Draft-Pick Score Package Commit Report

Date: 2026-06-28

Final decision: DRAFT PICK SCORE PACKAGE COMMIT COMPLETE WITH WARNINGS

## Scope

Phase 28.12 staged only the approved Phase 28 draft-pick score lane package and committed it with the approved commit message. No staging deploy, production deploy, BigQuery write, score materialization, Cloud Run Job trigger, Scheduler job, ingestion, LLM-backed action, Pigskin prompt, scrape, external fetch, Firebase artifact, or production flag change occurred.

## Authorization Gate State

All checked authorization gates were unset:

| Gate | State |
| --- | --- |
| ALLOW_TRADE_PICK_SCORE_MATERIALIZATION | unset |
| ALLOW_TRADE_SCORE_MATERIALIZATION | unset |
| ALLOW_PROJECTION_CONTEXT_REFRESH | unset |
| ALLOW_LIMITED_PRODUCTION_DEPLOY | unset |
| ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST | unset |
| DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER | unset |

## Staged Files

The staged file list was verified against the Phase 28.11 approved package. Expected count: 46. Actual count: 46. Missing files: none. Extra files: none.

Staged files:

```text
app.py
src/compat_flags.py
src/ui_data_guards.py
src/trade_pick_scores.py
tests/test_trade_pick_scores.py
tests/test_trade_pick_score_contracts.py
tests/test_streamlit_compat_rollout.py
tests/test_staging_ui_warning_fixes.py
tests/test_data_ops_local_controls.py
bigquery/migrations/0026__trade_pick_score_v0.sql
bigquery/contracts/trade_pick_scores.md
bigquery/contracts/trade_pick_scores_current.md
bigquery/contracts/compat_trade_pick_scores_current.md
bigquery/views/trade_pick_scores_current.sql
bigquery/views/compat_trade_pick_scores_current.sql
bigquery/validations/161_trade_pick_scores_exists.sql
bigquery/validations/162_trade_pick_scores_grain.sql
bigquery/validations/163_trade_pick_scores_pick_score_range.sql
bigquery/validations/164_trade_pick_scores_component_score_range.sql
bigquery/validations/165_trade_pick_scores_confidence_range.sql
bigquery/validations/166_trade_pick_scores_required_identity_fields.sql
bigquery/validations/167_trade_pick_scores_exact_slot_fields.sql
bigquery/validations/168_trade_pick_scores_round_only_fields.sql
bigquery/validations/169_trade_pick_scores_source_freshness_exists.sql
bigquery/validations/170_trade_pick_scores_missing_flags_exist.sql
bigquery/validations/171_trade_pick_scores_component_json_exists.sql
bigquery/validations/172_trade_pick_scores_current_grain.sql
bigquery/validations/173_compat_trade_pick_scores_current_exists.sql
bigquery/validations/174_compat_trade_pick_scores_no_raw_source_dependencies.sql
bigquery/validations/175_trade_player_scores_no_pick_rows.sql
bigquery/validations/176_trade_pick_scores_no_player_columns.sql
bigquery/validations/177_trade_pick_scores_parseability_warning.sql
bigquery/validations/178_trade_pick_scores_model_version_coverage.sql
docs/rebuild/table-classification.md
docs/rebuild/compatibility-contracts.md
docs/rebuild/trade-pick-score-rollout.md
docs/rebuild/validation/phase-28-1-draft-pick-college-source-audit-report.md
docs/rebuild/validation/phase-28-2-draft-pick-parser-and-dry-run-report.md
docs/rebuild/validation/phase-28-3-draft-pick-score-contracts-report.md
docs/rebuild/validation/phase-28-4-trade-pick-score-migration-apply-report.md
docs/rebuild/validation/phase-28-5-draft-pick-score-write-path-report.md
docs/rebuild/validation/phase-28-6-draft-pick-score-ppr-materialization-report.md
docs/rebuild/validation/phase-28-7-draft-pick-score-ui-integration-report.md
docs/rebuild/validation/phase-28-8-draft-pick-score-staging-ui-qa-report.md
docs/rebuild/validation/phase-28-9-draft-pick-score-ui-polish-report.md
docs/rebuild/validation/phase-28-10-draft-pick-score-ui-polish-staging-qa-report.md
```

## Excluded File Confirmation

Confirmed not staged:

```text
docs/rebuild/validation/phase-28-11-draft-pick-score-release-package-review.md
output/
output/playwright/
screenshots
proxy files
.env
.env.*
pipeline_execution.log
*.log
.codex-remote-attachments/
.codex-tools/
node_modules/
historical Phase 17 through Phase 27 validation backlog
generated browser evidence
secret JSON files
```

## Staged Diff Summary

`git diff --cached --stat` before commit showed:

```text
46 files changed, 5918 insertions(+), 18 deletions(-)
```

`git diff --cached --check` initially found one trailing blank line at EOF in `docs/rebuild/validation/phase-28-8-draft-pick-score-staging-ui-qa-report.md`. That approved Phase 28 evidence file was fixed by removing only the trailing blank line, restaged, and rechecked.

Final `git diff --cached --check`: pass.

## Checks Run

Pre-commit and post-commit checks:

| Check | Result |
| --- | --- |
| `git diff --cached --check` | pass after Phase 28.8 trailing EOF blank-line cleanup |
| `scripts/check_deployment_safety.py` | pass |
| `py_compile app.py` | pass |
| `py_compile src\trade_pick_scores.py` | pass |
| `py_compile src\trade_player_scores.py` | pass |
| `compileall -q src scripts` | pass |
| `unittest tests.test_trade_pick_scores` | 21 tests OK |
| `unittest tests.test_trade_pick_score_contracts` | 6 tests OK |
| `unittest tests.test_streamlit_compat_rollout` | 12 tests OK |
| `unittest tests.test_staging_ui_warning_fixes` | 24 tests OK |
| `unittest tests.test_data_ops_local_controls` | 6 tests OK |
| `run_bigquery_migrations.py --list-pending` | no pending migrations |
| `run_bigquery_validations.py --dry-run` | 178 validations discovered |

PowerShell surfaced unittest progress output as `NativeCommandError` text in a few runs, but each command returned exit code 0 and the unittest summaries reported `OK`.

## Commit Result

Commit created:

```text
6e4b565 Draft pick score lane and staging UI
```

Commit summary:

```text
46 files changed, 5917 insertions(+), 18 deletions(-)
```

New files in the commit include:

- `src/trade_pick_scores.py`
- `tests/test_trade_pick_scores.py`
- `tests/test_trade_pick_score_contracts.py`
- `bigquery/migrations/0026__trade_pick_score_v0.sql`
- `bigquery/contracts/trade_pick_scores.md`
- `bigquery/contracts/trade_pick_scores_current.md`
- `bigquery/contracts/compat_trade_pick_scores_current.md`
- `bigquery/views/trade_pick_scores_current.sql`
- `bigquery/views/compat_trade_pick_scores_current.sql`
- `bigquery/validations/161_trade_pick_scores_exists.sql` through `bigquery/validations/178_trade_pick_scores_model_version_coverage.sql`
- `docs/rebuild/trade-pick-score-rollout.md`
- Phase 28.1 through Phase 28.10 validation reports

## Post-Commit Git State

Post-commit:

| Check | Result |
| --- | --- |
| HEAD | `6e4b565 Draft pick score lane and staging UI` |
| staged files | none |
| untracked files before this report | 91 |
| generated evidence committed | no |
| historical Phase 17 through Phase 27 backlog committed | no |
| Phase 28.11 report committed | no |

This Phase 28.12 report was created after the commit and remains untracked for a later evidence-only commit decision.

## Production Untouched Confirmation

Read-only production describe confirmed:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00077-2jp` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| Traffic | `nfl-studio-dashboard-00077-2jp:100` |
| USE_TRADE_PICK_SCORE_V0 | unset |
| USE_COMPAT_TRADE_PICK_SCORE | unset |
| USE_TRADE_ANALYZER_SCORE_V0 | `false` |
| USE_COMPAT_TRADE_PLAYER_SCORE | `false` |
| USE_COMPAT_TRADE_PLAYER_HISTORY | `false` |
| USE_CLOUD_RUN_JOBS_FOR_DATA_OPS | `false` |
| DATA_OPS_ALLOW_JOB_TRIGGER | `false` |
| USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS | `false` |
| DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER | `false` |

No production deployment occurred.

## Remaining Warnings

- Phase 28.10 staging QA passed with warnings. The optional Side B round-only repeat was flaky in the combined browser script, while the standalone round-only proof passed.
- Phase 28.11 remains untracked by instruction and should be handled in a later evidence-only commit if desired.
- Historical Phase 17 through Phase 27 validation backlog remains untracked.
- The Phase 28.8 report had a trailing EOF blank line removed before commit. No content meaning changed.

## Recommended Next Phase

Phase 28.13 should decide whether to commit Phase 28.11 and Phase 28.12 evidence reports only, or leave them untracked with the historical backlog.

## Final Decision

DRAFT PICK SCORE PACKAGE COMMIT COMPLETE WITH WARNINGS
