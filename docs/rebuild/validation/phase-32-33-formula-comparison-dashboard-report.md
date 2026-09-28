# Phase 32.33 Formula Comparison Dashboard Report

Final decision: **FORMULA COMPARISON DASHBOARD READY WITH WARNINGS**

## Summary

Phase 32.33 added a read-only Formula Review dashboard for owner review of the 2026 Current Pigskin versus BQML boards. The dashboard is static Markdown-backed and default-off behind `USE_FORMULA_COMPARISON_DASHBOARD`.

No deployment, ranking generation, Gemini call, Pigskin chat call, Sleeper API call, BigQuery write, BQML training, champion activation, or live ranking table change occurred.

## Git State

Part 0 preserved Phase 32.32 first.

| Item | Result |
|---|---|
| Phase 32.32 commit | `31ec509 phase 32.32 generate scoring profile review boards` |
| Phase 32.33 committed | No. Left uncommitted for owner review. |
| Historical backlog | Still untracked and not staged. |

Phase 32.33 files changed:

| File | Change |
|---|---|
| `app.py` | Added default-off Formula Review tab and read-only dashboard renderer. |
| `src/compat_flags.py` | Added `USE_FORMULA_COMPARISON_DASHBOARD`. |
| `src/formula_review_dashboard.py` | Added Markdown parser, profile order, table mapping, and risk-filter helpers. |
| `tests/test_formula_review_dashboard.py` | Added focused parser, flag, TE35, risk-filter, and read-only source tests. |
| `docs/rebuild/formula-ranking-owner-review-index.md` | Added Phase 32.33 dashboard result and corrected historical Phase 32.30 non-PPR status. |
| `docs/rebuild/ranking-algorithm-scorecard.md` | Added Phase 32.33 scorecard status and updated next experiments. |
| `docs/rebuild/ranking-opportunity-metrics-matrix.md` | Added dashboard source status and marked the old non-PPR blocked note as Phase 32.30 historical state. |
| `docs/rebuild/validation/phase-32-33-formula-comparison-dashboard-report.md` | This report. |

## Data-Source Decision

Decision: static/read-only Markdown-backed dashboard.

Source: `docs/rebuild/live-2026-ranking-review-boards.md`.

Reason: this is the lowest-risk first pass. It avoids BigQuery runtime cost, avoids CTE regeneration, avoids review-table persistence, and prevents accidental writes to production ranking paths.

No `ranking_owner_review_boards` table was created. No `ALLOW_OWNER_REVIEW_BOARD_WRITE` gate was added because persistence was not needed.

## Dashboard Route

Route/location: optional Streamlit tab named `Formula Review`.

Visibility gate:

`USE_FORMULA_COMPARISON_DASHBOARD=true`

Default state: off.

The tab is separate from Data Ops controls. It contains no write buttons, no subprocess launch controls, and no export path.

## Scoring-Profile Policy

Display order:

1. `standard`
2. `half_ppr`
3. `ppr`
4. `gng_keeper`

The dashboard does not choose one global winner. It shows each scoring profile separately.

Profile status:

| Scoring profile | Board status | Best review-only challenger | Current decision |
|---|---|---|---|
| `standard` | ready with warnings | `ranking_bqml_enriched_logistic_elite_v1` | Current Pigskin holds. |
| `half_ppr` | ready with warnings | `ranking_bqml_enriched_logistic_elite_v1` | Current Pigskin holds. |
| `ppr` | ready with warnings | `ranking_bqml_enriched_logistic_elite_v1` | Current Pigskin holds. |
| `gng_keeper` | ready with warnings | `ranking_bqml_enriched_logistic_elite_v1` | Current Pigskin holds. |

## Dashboard Content

Included:

- Review-only warning banner.
- Current Pigskin live-baseline banner.
- No champion active warning.
- Missingness warning.
- Standard-first profile tabs.
- Overall, QB, RB, WR, and TE position views.
- Current Pigskin top 50 overall.
- Enriched Logistic Elite top 50 overall.
- Enriched Linear Points top 50 overall.
- Side-by-side top 100 overall.
- QB45, RB80, WR100, and TE35 boards.
- Logistic risers and fallers.
- Cutline crossings.
- TE35 watch band.
- Risk filters for movement over 20 ranks, high missingness, null current team, questionable/out/injured text, missing Current Pigskin fields, and missing BQML fields.

Labels:

- Current Pigskin: live baseline.
- Enriched Logistic Elite: review-only challenger.
- Enriched Linear Points: context only.
- BQML NGS: context only.
- NGS direct diagnostics: component signal.
- injury/availability: risk flag only.
- Sleeper: display-only live context.
- historical depth: blocked.

## TE35 Confirmation

Owner-review TE output is capped at TE35 through the Markdown source and `POSITION_TABLES["TE"] = "TE Board Top 35"`.

The dashboard also keeps the TE35 watch band and cutline table visible. TE6, TE12, and TE18 cutlines remain present in the source tables.

Live TE60 rows in `analytics_pigskin_rankings` were not changed.

Future owner-approved live-ranking depth change: reduce TE from 60 to 35.

## Read-Only Safety Proof

The new helper reads only the committed Markdown file. It does not import or call:

- `google.cloud`
- `src.generate_pigskin_rankings`
- Gemini credential paths
- Pigskin chat paths
- Sleeper API paths
- production materialization paths

The dashboard does not write:

- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_candidates`
- `ranking_formula_champions`
- `ranking_backtest_results`

The dashboard does not require or fabricate `pigskin_context_score`.

No PPR fallback is used. Standard, Half PPR, PPR, and GNG Keeper profile sections are parsed independently from the Markdown source.

## Missingness Warnings

Warnings remain visible:

- Standard-first smoke average missing feature rate was about `69.0%`.
- Baseline candidate proxies were about `61.2%` missing.
- Ideal xFP was about `61.7%` missing.
- PBP and first-downs were about `69.6%` missing.
- NGS direct was about `89.6%` missing.
- Injury and availability was about `90.2%` missing.

These warnings block automatic promotion. They do not block owner review.

## Checks Run

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_formula_review_dashboard` | Passed, 7 tests. |
| `.\venv\Scripts\python.exe -m py_compile app.py src\compat_flags.py src\formula_review_dashboard.py` | Passed. |
| `.\venv\Scripts\python.exe -m compileall -q src scripts app.py` | Passed. |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Passed. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | Passed, no pending migrations. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | Passed, validation discovery only. |
| `git diff --check` | Passed with line-ending warnings only. |

PowerShell emitted `NativeCommandError` display wrappers for some commands that wrote normal progress to stderr, but the commands returned exit code `0`.

## Warnings

- Dashboard is default-off until `USE_FORMULA_COMPARISON_DASHBOARD=true` is set in the target environment.
- The dashboard is Markdown-backed. It is safe and cheap, but not deeply sortable beyond the Streamlit table controls.
- Missingness remains high. Enriched Logistic Elite is review-only, not a production formula.
- Enriched Linear Points remains context only because its scores are volatile and unbounded.
- BQML NGS context is labeled but not displayed as a board in this first pass.
- Phase 32.33 changes are uncommitted for owner review.

## Recommended Next Phase

Recommended: Phase 32.34, owner selection by scoring profile or hold current Pigskin baseline.

Other valid Phase 32.34 paths:

- Review-only table persistence if Markdown-backed UI is not enough.
- Hold current Pigskin baseline.
- Live ranking generation only after explicit owner approval.
- Production TE depth change only after explicit owner approval.

