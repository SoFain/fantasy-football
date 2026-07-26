# Phase 28.11 Draft-Pick Score Release Package Review

Date: 2026-06-28

Final decision: DRAFT PICK SCORE RELEASE PACKAGE READY WITH WARNINGS

## Scope

Phase 28.11 reviewed the full draft-pick score lane package and identified a narrow commit set. This phase did not stage files, commit, deploy, write BigQuery rows, materialize additional scores, trigger Cloud Run Jobs, create Scheduler jobs, run ingestion, call LLM-backed actions, submit Pigskin prompts, scrape, fetch external data, or create Firebase artifacts.

## Authorization Gates

All checked gates were unset:

| Gate | State |
| --- | --- |
| ALLOW_TRADE_PICK_SCORE_MATERIALIZATION | unset |
| ALLOW_TRADE_SCORE_MATERIALIZATION | unset |
| ALLOW_PROJECTION_CONTEXT_REFRESH | unset |
| ALLOW_LIMITED_PRODUCTION_DEPLOY | unset |
| ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST | unset |
| DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER | unset |

## Git State Summary

Latest commits:

```text
6158549 Document Trade Score v1 Track A closeout
3268a5a Document Trade Score v1 UI polish package
9ec04f3 Polish Trade Score v1 staging UI
aa543d0 Document Phase 26 evidence commit
251fd18 Document Phase 25 production closeout
b3b0ec1 Document Data Ops hardening production rollout
22e3256 Gate Data Ops local subprocess controls
63149aa Clean up production warning noise
0001f47 Add Trade Analyzer score v0 and safe production rollout
ce0eb82 docs: prepare phase 17 production candidate plan
57ab102 docs: record current season fraud watch blocker
66955b2 docs: record phase 17 trade packet input blocker
```

No files are staged.

Modified tracked files:

```text
app.py
docs/rebuild/compatibility-contracts.md
docs/rebuild/table-classification.md
src/compat_flags.py
src/ui_data_guards.py
tests/test_data_ops_local_controls.py
tests/test_staging_ui_warning_fixes.py
tests/test_streamlit_compat_rollout.py
```

Untracked file summary:

| Category | Count | Package Decision |
| --- | ---: | --- |
| Phase 28 validation reports | 10 | include selected Phase 28 release evidence |
| Phase 17 through Phase 27 validation backlog | 90 | exclude |
| Phase 28 warehouse files | 24 | include |
| Phase 28 docs | 1 | include |
| Phase 28 source/tests | 3 | include |
| Other untracked files | 0 | none |

## Commit Candidates

Source:

```text
app.py
src/compat_flags.py
src/ui_data_guards.py
src/trade_pick_scores.py
```

Tests:

```text
tests/test_trade_pick_scores.py
tests/test_trade_pick_score_contracts.py
tests/test_streamlit_compat_rollout.py
tests/test_staging_ui_warning_fixes.py
tests/test_data_ops_local_controls.py
```

Warehouse:

```text
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
```

Docs:

```text
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

## Exclusions

Exclude:

```text
output/
output/playwright/
output/playwright/phase-28-10/
screenshots
local browser evidence JSON
proxy logs
proxy PID files
.codex-remote-attachments/
.codex-tools/
pipeline_execution.log
*.log
.env
.env.*
node_modules/
cache files
secret JSON files
generated QA artifacts
historical Phase 17 through Phase 27 validation backlog
```

## Diff Review Summary

Reviewed candidate changes for secrets, local-only artifacts, production flags, raw/source dependencies, request-time writes, Pigskin SQL safety, and Data Ops local controls.

Findings:

- No staged files.
- No generated browser artifacts are part of the proposed package.
- No secret files were found by `scripts/check_deployment_safety.py`.
- Candidate-file secret scan only found existing UI placeholder strings in `app.py`, such as API key placeholder text. No real credential value was found.
- No production deploy scripts were changed.
- `execute_bigquery_sql` remains absent from Pigskin-visible tools per safety checker.
- Data Ops local subprocess controls remain default-off.
- Production feature flags remain default-off.
- Pick-score flags are default-off.
- Pick-score UI requires both `USE_TRADE_PICK_SCORE_V0` and `USE_COMPAT_TRADE_PICK_SCORE`.
- Player-score and pick-score lanes remain separate in code and tests.

## Migration Safety Review

Reviewed `bigquery/migrations/0026__trade_pick_score_v0.sql`.

Confirmed:

- Creates `trade_pick_scores` with `CREATE TABLE IF NOT EXISTS`.
- Creates or replaces only `trade_pick_scores_current` and `compat_trade_pick_scores_current` views.
- Contains no `DROP`, `DELETE`, `TRUNCATE`, `ALTER TABLE`, `INSERT INTO`, or `MERGE`.
- Does not mutate `trade_player_scores`.
- `trade_pick_scores_current` reads from `trade_pick_scores`.
- `compat_trade_pick_scores_current` reads from `trade_pick_scores_current`.
- Migration 0026 was already applied in Phase 28.4.
- `run_bigquery_migrations.py --list-pending` reports no pending migrations.

## Source Boundary Review

Confirmed:

- `src.trade_pick_scores` reads `compat_trade_assets_current` for deterministic builder input.
- UI helper reads `compat_trade_pick_scores_current`.
- Write mode requires `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION=true`.
- `ALLOW_TRADE_SCORE_MATERIALIZATION` does not authorize pick-score writes.
- Dry-run remains non-mutating.
- Unauthorized write fails closed.
- MERGE SQL matches on the pick-score contract grain and handles nullable `pick_slot` with `IFNULL(target.pick_slot, -1) = IFNULL(source.pick_slot, -1)`.
- Write-row validation rejects non-pick source keys, missing required pick fields, invalid scores, invalid confidence, invalid JSON payloads, exact-slot rows without `pick_slot`, and round-only rows with a non-null `pick_slot`.
- No pick-score code writes to `trade_player_scores`.

## UI Boundary Review

Confirmed:

- Pick-score flags are separate from player-score flags.
- Staging can enable pick-score flags without touching production.
- Player score cards use `compat_trade_player_scores_current`.
- Pick score cards use `compat_trade_pick_scores_current`.
- Pick-score display uses `Pick Score` labels.
- Mixed side warning exists: `Mixed player and draft-pick assets selected. Market totals stay combined, score totals stay separate.`
- Player score totals and pick score totals are displayed separately.
- Round-only copy returns `round-only`.
- Compact component and warning text is browser-visible.
- Missing pick-score copy remains explicit: no compatible pick-score row for the scoring context.
- Tests assert no direct UI helper references to `draft_picks`, `college_player_stats`, `rookie_scouting_metrics`, `source_*`, or `raw_*`.

## Package Check Results

| Check | Result |
| --- | --- |
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
| `unittest discover tests` | 407 tests OK |
| `run_bigquery_migrations.py --list-pending` | no pending migrations |
| `run_bigquery_validations.py --dry-run` | 178 validations discovered |
| `run_bigquery_validations.py --run --pattern trade_pick_scores` | 17 passed, 0 failed, 1 informational warning |
| `run_bigquery_validations.py --run --pattern compat_trade_pick_scores` | 2 passed, 0 failed |
| `run_bigquery_validations.py --run --pattern trade_player_scores` | 12 passed, 0 failed |
| `run_bigquery_validations.py --run --pattern compat_trade_player_scores` | 2 passed, 0 failed |

Validation 178 returned an informational model-version row for `trade_pick_score_v0_2026_001` with 64 rows. That is expected and review-only.

## Warehouse State

Read-only warehouse checks:

| Check | Count |
| --- | ---: |
| `trade_pick_scores` | 64 |
| `trade_pick_scores_current` | 64 |
| `compat_trade_pick_scores_current` | 64 |
| PPR rows | 64 |
| exact-slot rows | 48 |
| round-only rows | 16 |
| duplicate current grain rows | 0 |
| invalid pick score rows | 0 |
| invalid confidence score rows | 0 |
| missing JSON rows | 0 |
| `trade_player_scores` draft-pick rows | 0 |

Note: player names such as George Pickens are not draft-pick rows. The check used `PICK` key and draft-pick label patterns rather than a broad player-name substring.

## Staging State

Read-only staging describe:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard-staging` |
| Revision | `nfl-studio-dashboard-staging-00029-jtb` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` |
| Traffic | `nfl-studio-dashboard-staging-00029-jtb:100` |
| USE_TRADE_PICK_SCORE_V0 | `true` |
| USE_COMPAT_TRADE_PICK_SCORE | `true` |
| USE_TRADE_ANALYZER_SCORE_V0 | `true` |
| USE_COMPAT_TRADE_PLAYER_SCORE | `true` |
| USE_COMPAT_TRADE_PLAYER_HISTORY | `true` |
| USE_CLOUD_RUN_JOBS_FOR_DATA_OPS | `false` |
| DATA_OPS_ALLOW_JOB_TRIGGER | `false` |
| USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS | `false` |
| DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER | `false` |

## Production Untouched

Read-only production describe:

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

No production deployment occurred in this phase.

## Proposed Commit Commands

Do not run these until the owner approves the package.

```powershell
git add app.py
git add src/compat_flags.py src/ui_data_guards.py src/trade_pick_scores.py
git add tests/test_trade_pick_scores.py tests/test_trade_pick_score_contracts.py
git add tests/test_streamlit_compat_rollout.py tests/test_staging_ui_warning_fixes.py tests/test_data_ops_local_controls.py
git add bigquery/migrations/0026__trade_pick_score_v0.sql
git add bigquery/contracts/trade_pick_scores.md bigquery/contracts/trade_pick_scores_current.md bigquery/contracts/compat_trade_pick_scores_current.md
git add bigquery/views/trade_pick_scores_current.sql bigquery/views/compat_trade_pick_scores_current.sql
git add bigquery/validations/161_trade_pick_scores_exists.sql
git add bigquery/validations/162_trade_pick_scores_grain.sql
git add bigquery/validations/163_trade_pick_scores_pick_score_range.sql
git add bigquery/validations/164_trade_pick_scores_component_score_range.sql
git add bigquery/validations/165_trade_pick_scores_confidence_range.sql
git add bigquery/validations/166_trade_pick_scores_required_identity_fields.sql
git add bigquery/validations/167_trade_pick_scores_exact_slot_fields.sql
git add bigquery/validations/168_trade_pick_scores_round_only_fields.sql
git add bigquery/validations/169_trade_pick_scores_source_freshness_exists.sql
git add bigquery/validations/170_trade_pick_scores_missing_flags_exist.sql
git add bigquery/validations/171_trade_pick_scores_component_json_exists.sql
git add bigquery/validations/172_trade_pick_scores_current_grain.sql
git add bigquery/validations/173_compat_trade_pick_scores_current_exists.sql
git add bigquery/validations/174_compat_trade_pick_scores_no_raw_source_dependencies.sql
git add bigquery/validations/175_trade_player_scores_no_pick_rows.sql
git add bigquery/validations/176_trade_pick_scores_no_player_columns.sql
git add bigquery/validations/177_trade_pick_scores_parseability_warning.sql
git add bigquery/validations/178_trade_pick_scores_model_version_coverage.sql
git add docs/rebuild/table-classification.md docs/rebuild/compatibility-contracts.md docs/rebuild/trade-pick-score-rollout.md
git add docs/rebuild/validation/phase-28-1-draft-pick-college-source-audit-report.md
git add docs/rebuild/validation/phase-28-2-draft-pick-parser-and-dry-run-report.md
git add docs/rebuild/validation/phase-28-3-draft-pick-score-contracts-report.md
git add docs/rebuild/validation/phase-28-4-trade-pick-score-migration-apply-report.md
git add docs/rebuild/validation/phase-28-5-draft-pick-score-write-path-report.md
git add docs/rebuild/validation/phase-28-6-draft-pick-score-ppr-materialization-report.md
git add docs/rebuild/validation/phase-28-7-draft-pick-score-ui-integration-report.md
git add docs/rebuild/validation/phase-28-8-draft-pick-score-staging-ui-qa-report.md
git add docs/rebuild/validation/phase-28-9-draft-pick-score-ui-polish-report.md
git add docs/rebuild/validation/phase-28-10-draft-pick-score-ui-polish-staging-qa-report.md
git diff --cached --name-only
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m py_compile src\trade_pick_scores.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest tests.test_trade_pick_scores
.\venv\Scripts\python.exe -m unittest tests.test_trade_pick_score_contracts
git commit -m "Draft pick score lane and staging UI"
```

## Remaining Warnings

- Phase 28.10 staging QA passed with warnings. The optional Side B round-only repeat was flaky in the combined browser script, but the standalone round-only proof passed on the final staging revision.
- Validation 178 is informational and returns one expected model-version row.
- Historical Phase 17 through Phase 27 validation reports remain untracked and intentionally excluded from this package.
- Phase 28.8 and Phase 28.10 reports reference local browser proxy/evidence paths as narrative evidence. The generated artifacts themselves are excluded.

## Recommended Next Phase

Phase 28.12 should stage only the approved package above, verify the staged names, rerun lightweight checks, and commit with:

`Draft pick score lane and staging UI`

## Final Decision

DRAFT PICK SCORE RELEASE PACKAGE READY WITH WARNINGS
