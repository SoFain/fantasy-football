# Phase 32.36 Dashboard Owner Inspection Support Report

Final decision: **OWNER INSPECTION READY WITH WARNINGS**

## Summary

Phase 32.36 preserved the Phase 32.35 enablement evidence, verified the production Formula Review flag remains enabled, and created the owner inspection checklist and decision form.

No deployment, Cloud Run traffic change, live ranking regeneration, champion activation, BQML training, Gemini call, Pigskin chat call, Sleeper API call, source ingest, materialization, BigQuery write, candidate overwrite, table truncate, or production ranking generator path ran.

## Files Changed

Committed Phase 32.35 docs:

- `docs/rebuild/formula-ranking-owner-review-index.md`
- `docs/rebuild/validation/phase-32-35-formula-review-dashboard-enable-report.md`

Phase 32.36 docs created or updated:

- `docs/rebuild/formula-ranking-owner-review-index.md`
- `docs/rebuild/validation/phase-32-36-owner-inspection-checklist.md`
- `docs/rebuild/validation/phase-32-36-dashboard-owner-inspection-support-report.md`

## Phase 32.35 Commit

| Item | Result |
|---|---|
| Commit hash | `a6c3ae4` |
| Commit message | `phase 32.35 enable formula review dashboard` |
| Staged files | Phase 32.35 docs only |
| Historical backlog staged | No |
| Generated artifacts staged | No |

## Git State

Before the Phase 32.35 commit:

- `docs/rebuild/formula-ranking-owner-review-index.md` was modified.
- `docs/rebuild/validation/phase-32-35-formula-review-dashboard-enable-report.md` was untracked.
- Historical validation backlog files remained untracked.

After the Phase 32.35 commit and before Phase 32.36 docs:

- Latest commit was `a6c3ae4 phase 32.35 enable formula review dashboard`.
- Only the historical validation backlog appeared in the scoped status sample.

After Phase 32.36 docs:

- `docs/rebuild/formula-ranking-owner-review-index.md` is modified.
- `docs/rebuild/validation/phase-32-36-owner-inspection-checklist.md` is untracked.
- `docs/rebuild/validation/phase-32-36-dashboard-owner-inspection-support-report.md` is untracked.
- Historical validation backlog files remain untracked.

## Production Flag Verification

Read-only Cloud Run describe:

| Item | Value |
|---|---|
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00083-tlr` |
| Traffic | `nfl-studio-dashboard-00083-tlr=100` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Image | `sha256:c675aa578b218581c4a9253e6bd5ceefc6da3ee0198dcb7cb9b98e3c541442e6` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| `USE_FORMULA_COMPARISON_DASHBOARD` | `true` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `false` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `false` |
| `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` | `<unset>` |

No service config update, redeploy, rollback, or traffic change was run in Phase 32.36.

## Health Check Result

| Check | Result |
|---|---|
| `/_stcore/health` | `200 ok` |
| `/` | `200` |
| Streamlit shell present | Yes |
| Traceback in unauthenticated response | No |

The unauthenticated route reached the Streamlit shell. Phase 32.36 did not use credentials and did not automate login.

## Owner Inspection Checklist

Checklist created:

- `docs/rebuild/validation/phase-32-36-owner-inspection-checklist.md`

The checklist covers:

- Login and tab visibility.
- Standard-first profile order.
- Current Pigskin live-baseline labeling.
- Enriched Logistic Elite as review-only challenger.
- Enriched Linear Points as context only.
- Missingness and WR movement warnings.
- TE35 owner-review cap with TE6, TE12, and TE18 cutlines.
- Absence of write, export, deploy, ranking-generation, champion-selection, Gemini, Pigskin chat, Sleeper API, and Cloud Run Job controls.
- Profile-specific decision form.

## Read-Only Safety Confirmation

Phase 32.36 did not run commands that call:

- `src/generate_pigskin_rankings.py`
- Gemini
- Pigskin chat
- Sleeper API
- BQML training
- source ingest
- materialization
- Cloud Run Jobs

Phase 32.36 did not write to:

- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_candidates`
- `ranking_formula_champions`
- `ranking_backtest_results`

Current Pigskin remains the live baseline. No formula champion is active. No live ranking table changed.

## Checks Run

Pre-commit Phase 32.35 checks:

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_formula_review_dashboard` | Passed, 7 tests. |
| `.\venv\Scripts\python.exe -m py_compile app.py src\compat_flags.py src\formula_review_dashboard.py` | Passed. |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Passed. |
| `git diff --check` | Passed with line-ending warnings only. |

Final Phase 32.36 checks:

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_formula_review_dashboard` | Passed, 7 tests. |
| `.\venv\Scripts\python.exe -m py_compile app.py src\compat_flags.py src\formula_review_dashboard.py` | Passed. |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Passed. |
| `git diff --check` | Passed with line-ending warnings only. |

PowerShell emitted `NativeCommandError` wrappers for normal stderr test progress and Git line-ending warnings, but the commands returned exit code `0`.

## Warnings

- Live tab visibility still requires owner login.
- Formula Review remains Markdown-backed. Review-only table persistence is a separate possible phase.
- TE live ranking depth remains TE60. Any production depth change to TE35 needs a separate owner-approved phase.
- Historical validation backlog files remain untracked by design.

## Recommended Next Phase

Recommended: Phase 32.37, hold Current Pigskin baseline or owner selection by scoring profile.

Other valid next phases:

- Phase 32.37, review-only table persistence.
- Phase 32.37, production TE depth change only after explicit owner approval.
- Phase 32.37, live ranking generation only after explicit champion selection.
