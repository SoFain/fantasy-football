# Phase 27.11 Trade Score V1 Track A Closeout Report

Generated: 2026-06-27

## Final Decision

TRACK A COMPLETE — STAGING READY, PRODUCTION DISABLED

## Scope Confirmation

This phase was decision and validation only. No production deploy, staging deploy, production feature flag change, Trade Analyzer score flag enablement, score materialization, Cloud Run Job trigger, Scheduler job, ingestion, LLM-backed action, Pigskin prompt, Data Ops local subprocess click, scrape, Firebase artifact, commit, or authorization-gate change occurred.

## Track A Summary

Track A improved Trade Analyzer score quality before any production score rollout:

- v1 scoring logic, confidence categories, and risk breakdowns are implemented.
- Role/source penalty noise was reduced.
- Team-context mismatch warnings are surfaced.
- Projection freshness metadata warnings were restored.
- v1 score rows were materialized for staging review only.
- Staging confirmed `trade_score_v1_2025_001` through `compat_trade_player_scores_current`.
- Trade Lab now shows active score model context, grouped warnings, source freshness, and draft-pick unavailable behavior.
- Trade Score v1 UI polish was committed in `9ec04f3`.
- Phase 27.9 and Phase 27.10 evidence was committed in `3268a5a`.

Production exposure remains disabled.

## Authorization Gate State

All checked process environment gates were unset:

| Gate | State |
| --- | --- |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

## Git State

Latest commit:

```text
3268a5a Document Trade Score v1 UI polish package
```

Recent expected commits are present:

```text
3268a5a Document Trade Score v1 UI polish package
9ec04f3 Polish Trade Score v1 staging UI
aa543d0 Document Phase 26 evidence commit
251fd18 Document Phase 25 production closeout
```

Worktree state:

| Item | Result |
| --- | --- |
| Modified code files | none |
| Staged files | none |
| Untracked file count | 90 |
| Untracked historical validation reports | 82 |
| Untracked Phase 27 owner-review reports | 8 |

The untracked files are validation backlog and owner-review evidence. Generated Playwright evidence remains ignored under `output/`.

## Checks Run

All requested checks passed:

| Check | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | PASS |
| `.\venv\Scripts\python.exe -m py_compile app.py` | PASS |
| `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py` | PASS |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | PASS |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | PASS, 40 tests |
| `.\venv\Scripts\python.exe -m unittest tests.test_streamlit_compat_rollout` | PASS, 10 tests |
| `.\venv\Scripts\python.exe -m unittest tests.test_staging_ui_warning_fixes` | PASS, 13 tests |
| `.\venv\Scripts\python.exe -m unittest tests.test_data_ops_local_controls` | PASS, 6 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | PASS, 367 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | PASS, 160 validation files discovered |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | PASS, 11 passed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | PASS, 2 passed |

Notes:

- PowerShell surfaced unittest progress written to stderr as native-command output noise. Each targeted unittest process exited `0`.
- The full unittest suite emitted mocked pipeline and load logs from tests. No live ingestion or score materialization command was run.

## V1 Warehouse State

Read-only BigQuery checks against `fantasy-football-498121.fantasy_football_brain.trade_player_scores`:

| Metric | Value |
| --- | ---: |
| total score rows | 154 |
| v0 rows | 77 |
| v1 rows | 77 |
| target v1 rows, 2025 week 18 PPR redraft one-QB | 77 |
| target duplicate grains | 0 |
| target `PICK` rows | 0 |
| target missing `model_run_id` rows | 0 |
| target unresolved identity rows | 0 |
| target invalid score rows | 0 |
| target missing JSON rows | 0 |
| target `projection_freshness_metadata_missing` warning rows | 77 |
| target `team_context_mismatch_warning` rows | 5 |

The target staging score slice is internally consistent and bounded to 2025 week 18 PPR redraft one-QB.

## Compatibility View State

Read-only checks confirmed both current views surface v1:

| View | Model Version | Season | Week | Context | Rows |
| --- | --- | ---: | ---: | --- | ---: |
| `trade_player_scores_current` | `trade_score_v1_2025_001` | 2025 | 18 | `ppr/redraft/one_qb` | 77 |
| `compat_trade_player_scores_current` | `trade_score_v1_2025_001` | 2025 | 18 | `ppr/redraft/one_qb` | 77 |

Dependency review:

- deployed `trade_player_scores_current` reads from `trade_player_scores`;
- deployed `compat_trade_player_scores_current` reads from `trade_player_scores_current`;
- local view SQL matches that pattern;
- validation `159_compat_trade_player_scores_no_raw_source_dependencies.sql` passed with `raw_source_dependency_count = 0`.

The string `source_` appears in deployed view text only because `source_freshness_json` is a selected column, not because the view reads a raw/source table.

Metadata note: a direct dataset `INFORMATION_SCHEMA.VIEW_TABLE_USAGE` query returned a location/path error in this environment. The dependency decision is based on deployed view definitions, local view SQL, and the passing raw-source dependency validation.

## Staging UI Status

Phase 27.8 staging QA decision:

```text
TRADE SCORE V1 UI POLISH STAGING QA PASS WITH WARNINGS
```

Verified staging behavior:

- staging read `trade_score_v1_2025_001`;
- `compat_trade_player_scores_current` surfaced 77 v1 rows;
- active model context displayed in Trade Lab;
- score source marker displayed;
- Bijan Robinson and Ja'Marr Chase v1 scores displayed as expected;
- A.J. Brown displayed grouped `Team context` warning details;
- Malik Nabers displayed lower confidence and role/source warning details;
- source freshness expanders rendered safely;
- draft picks stayed score-unavailable with `draft pick score lane pending`;
- Data Ops remained gated;
- no LLM action, Cloud Run Job trigger, ingestion, materialization, or local subprocess action occurred.

## Production Untouched Confirmation

Read-only Cloud Run describe confirmed production remains unchanged:

| Field | Value |
| --- | --- |
| service | `nfl-studio-dashboard` |
| revision | `nfl-studio-dashboard-00077-2jp` |
| traffic | `nfl-studio-dashboard-00077-2jp:100` |
| image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |

Production flag state:

| Flag | State |
| --- | --- |
| `USE_TRADE_ANALYZER_SCORE_V0` | `false` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `false` |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `false` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |
| `USE_COMPAT_PLAYER_PROFILES` | `false` |
| `USE_COMPAT_SLEEPER_WATCH` | `false` |
| `USE_COMPAT_TRADE_ASSETS` | `false` |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | `false` |
| `USE_BACKTEST_DASHBOARD` | `false` |
| `USE_CLAIM_LEDGER_UI` | `false` |
| `USE_CONTENT_BRIEF_REVIEW_UI` | `false` |

Trade Analyzer score UI remains production-disabled. Trade History compatibility remains production-disabled. Data Ops Cloud Run and local subprocess trigger flags remain production-disabled.

## Production-Readiness Decision

Classification:

```text
TRACK A COMPLETE — STAGING READY, PRODUCTION DISABLED
```

Reason:

Trade Score v1 is a clear staging-quality improvement over v0 and has passed scoring, validation, staging deployment, and browser QA. It is not approved for production score exposure in this phase because production score flags remain false by design and known source-quality warnings remain:

- raw projection `as_of_*` metadata is null, so `projection_freshness_metadata_missing` appears on the target v1 slice;
- 5 team-context mismatch rows need product/data review;
- draft picks still need a separate score lane before pick assets can receive a comparable score.

A separate production rollout planning phase may begin later, but it must explicitly decide product exposure, flag state, rollback plan, smoke checks, and whether the remaining warnings are acceptable.

## Remaining Warnings

- `projection_freshness_metadata_missing` appears on all 77 target v1 rows because raw projection `as_of_*` metadata is null.
- 5 team-context mismatch rows require review.
- Draft picks remain score-unavailable until a pick-score lane exists.
- Historical Phase 17 through Phase 26 validation backlog remains untracked by owner decision.
- Phase 27.1 through Phase 27.6 reports remain untracked owner-review artifacts.
- Phase 27.10A and this Phase 27.11 report remain untracked after creation.
- Generated Playwright evidence remains local and ignored.

## Recommended Next Tracks

- Track B: build a draft-pick score lane so pick assets can be compared without pretending they are player rows.
- Track C: plan read-only production rollout for Trade Analyzer v1 score UI as a separate gated phase.
- Source Contract Work: clean up projection `as_of_*` metadata and normalize team context.
- Score Calibration v1.1: tune high-market edge cases and position-specific thresholds after product review.
- Historical Backlog Cleanup: archive, delete, or commit owner-review validation reports only after explicit owner direction.

