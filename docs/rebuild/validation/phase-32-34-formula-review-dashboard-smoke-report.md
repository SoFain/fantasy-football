# Phase 32.34 Formula Review Dashboard Smoke Report

Final decision: **FORMULA REVIEW DASHBOARD SMOKE READY**

## Summary

Phase 32.34 preserved the Phase 32.33 Formula Review dashboard package, committed it, and smoke-tested controlled local activation through `USE_FORMULA_COMPARISON_DASHBOARD=true`.

No deployment, live ranking regeneration, champion activation, BQML training, Gemini call, Pigskin chat call, Sleeper API call, BigQuery write, materialization, candidate overwrite, table truncate, or production ranking generator path ran.

## Git State

| Checkpoint | Result |
|---|---|
| Before Phase 32.33 commit | Expected dashboard package files plus historical untracked backlog. |
| Phase 32.33 commit | `e99f3f3 phase 32.33 add formula review dashboard` |
| After Phase 32.33 commit | Only historical validation backlog remained untracked before Phase 32.34 docs edits. |
| Phase 32.34 committed | No. Phase 32.34 smoke docs are left uncommitted for owner review. |

Phase 32.33 committed files:

- `app.py`
- `src/compat_flags.py`
- `src/formula_review_dashboard.py`
- `tests/test_formula_review_dashboard.py`
- `docs/rebuild/formula-ranking-owner-review-index.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/validation/phase-32-33-formula-comparison-dashboard-report.md`

Phase 32.34 documentation updates:

- `docs/rebuild/formula-ranking-owner-review-index.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/validation/phase-32-34-formula-review-dashboard-smoke-report.md`

## Feature Flag Status

| Item | Value |
|---|---|
| Flag name | `USE_FORMULA_COMPARISON_DASHBOARD` |
| Default | off when unset or false |
| Enabled value | `true` |
| Local smoke behavior | Enabled only inside the command process, then removed. |
| Production activation | Requires environment variable update plus app restart or Cloud Run redeploy/update. |
| Code default | Still default-off. |

Activation instruction:

```powershell
$env:USE_FORMULA_COMPARISON_DASHBOARD = "true"
```

Cloud Run activation should use a normal environment-variable update on the target service. This phase did not deploy or change any Cloud Run service.

## Local Smoke Result

Smoke command: one-shot Python process using `src.compat_flags` and `src.formula_review_dashboard`.

Result:

```text
smoke_status=pass
flag_default=false
flag_enabled_value=true
profile_order=standard,half_ppr,ppr,gng_keeper
review_version=phase32_32_live_2026_review_20260706
profile_count=4
te_cutlines=TE6,TE12,TE18
dashboard_write_controls=absent
```

The smoke did not launch a long-running Streamlit process. It verified the same local source used by the dashboard tab and the committed Markdown data source.

## Dashboard Route And Visibility

Route/location: optional Streamlit tab named `Formula Review`.

Visibility:

- Hidden when `USE_FORMULA_COMPARISON_DASHBOARD` is unset or false.
- Visible when `USE_FORMULA_COMPARISON_DASHBOARD=true`.

The tab is separate from Data Ops. It contains no write button, no export/download button, no subprocess launcher, and no Cloud Run Job trigger.

## Dashboard Content Verification

Confirmed:

- Standard profile appears first.
- Half PPR, PPR, and GNG Keeper appear after Standard.
- All four scoring profiles have profile sections.
- Current Pigskin banner states live baseline.
- No champion active warning is present.
- Missingness warning is present.
- Enriched Logistic Elite is labeled review-only challenger.
- Enriched Linear Points is labeled context only.
- No global winner is selected.
- The source says all-profile aggregate is context only.

## TE35 Verification

Confirmed:

- TE owner-review board maps to `TE Board Top 35`.
- TE6, TE12, and TE18 cutlines are present for each scoring profile.
- Live TE60 rows were not changed.

Future owner-approved live-ranking depth change: reduce TE from 60 to 35.

## Read-Only Safety Verification

The dashboard helper does not import or call:

- `google.cloud`
- `src.generate_pigskin_rankings`
- Gemini credential paths
- Pigskin chat paths
- Sleeper API paths
- production materialization paths

The dashboard renderer does not include:

- `st.button`
- `download_button`
- `run_subprocess_live`
- `trigger_cloud_run_job`
- BigQuery imports
- Gemini credential reads
- executable `src.generate_pigskin_rankings` command patterns

The dashboard cannot write:

- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_candidates`
- `ranking_formula_champions`
- `ranking_backtest_results`

The dashboard does not require or fabricate `pigskin_context_score`.

No PPR fallback is used. The profile order and profile-specific sections are parsed from `docs/rebuild/live-2026-ranking-review-boards.md`.

## Checks Run

Pre-commit checks for Phase 32.33:

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_formula_review_dashboard` | Passed, 7 tests. |
| `.\venv\Scripts\python.exe -m py_compile app.py src\compat_flags.py src\formula_review_dashboard.py` | Passed. |
| `.\venv\Scripts\python.exe -m compileall -q src scripts app.py` | Passed. |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Passed. |
| `git diff --check` | Passed with line-ending warnings only. |

Phase 32.34 smoke:

| Check | Result |
|---|---|
| One-shot local dashboard smoke with `USE_FORMULA_COMPARISON_DASHBOARD=true` | Passed. |

Final checks after documentation updates:

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_formula_review_dashboard` | Passed, 7 tests. |
| `.\venv\Scripts\python.exe -m py_compile app.py src\compat_flags.py src\formula_review_dashboard.py` | Passed. |
| `.\venv\Scripts\python.exe -m compileall -q src scripts app.py` | Passed. |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Passed. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | Passed, no pending migrations. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | Passed, validation discovery only. |
| `git diff --check` | Passed with line-ending warnings only. |

PowerShell emitted `NativeCommandError` wrappers for commands that wrote normal progress or warnings to stderr, but the checked commands returned exit code `0`.

## Warnings

- The dashboard is ready and smoke-tested, but not deployed.
- Runtime activation still requires setting `USE_FORMULA_COMPARISON_DASHBOARD=true` in the target environment and restarting/redeploying the app process.
- The dashboard is Markdown-backed. It is safe and cheap, but review-only table persistence may be useful if the owner wants durable sortable data.
- Missingness remains high and blocks automatic promotion.
- Enriched Linear Points remains context only because scores are volatile and unbounded.
- Current Pigskin remains live baseline.

## Recommended Next Phase

Recommended: Phase 32.35, owner selection by scoring profile or hold current Pigskin baseline.

Other valid Phase 32.35 paths:

- Review-only table persistence.
- Live ranking generation only after explicit owner approval.
- Production TE depth change only after explicit owner approval.
