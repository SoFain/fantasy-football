# Phase 32.18 Role Context, First-Down Proxy, and VOR Sensitivity Report

Superseded by `docs/rebuild/validation/phase-32-18-role-context-vor-firstdown-report.md`.

This earlier report records the first five-candidate pass. The revised Phase 32.18 prompt added exact VOR policy names and the PPR-only `gemini31_rb_weighted_opportunity_ppr_v0` diagnostic, so the regenerated report is the controlling evidence.

Final decision: FIRST DOWN PBP PROXIES READY, INJURY DEPTH SOURCES INSUFFICIENT, NO ROLE CONTEXT CANDIDATE BEATS BASELINE

## Scope

Phase 32.18 added the next fast feature-enrichment layer for ranking backtests:

- injury/depth source audit
- first-down PBP opportunity proxies
- Deep VOR baseline sensitivity
- capped SQL-native diagnostic family

No production deploy, staging deploy, Pigskin chat, Gemini/LLM ranking generation, live Sleeper API, live ranking regeneration, champion activation, or detail-row tournament write occurred.

## Git State

Before implementation, the worktree had untracked historical validation backlog reports and the untracked Phase 32.17 report.

The Phase 32.17 report remains uncommitted because this phase package was kept narrow to code, SQL, tests, scorecard, matrix, and the 0034 migration.

Implementation commit:

- `db9023ccce25 Add first down proxy ranking diagnostics`

This Phase 32.18 report was created after the implementation commit and is not part of that commit.

## Files Changed

Committed in `db9023ccce25`:

- `bigquery/migrations/0034__first_down_pbp_proxy_features.sql`
- `bigquery/validations/226_player_week_pbp_opportunity_metrics_ranges.sql`
- `bigquery/validations/227_player_week_pbp_opportunity_metrics_flags.sql`
- `bigquery/validations/228_ranking_feature_mart_pbp_xfp_columns.sql`
- `bigquery/validations/229_ranking_feature_mart_pbp_xfp_ranges.sql`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `src/nflverse_ideal_stats.py`
- `src/ranking_formula_backtests.py`
- `tests/test_nflverse_ideal_stats.py`
- `tests/test_ranking_formula_backtests.py`

## Injury/Depth Source Audit

| Source | Row count | Status |
|---|---:|---|
| `raw_nflverse_injuries` | 0 | Not usable for scoring |
| `raw_nflverse_depth_charts` | 0 | Not usable for scoring |

Schema exists, but there are no rows. Injury burden, missed-time risk, starter proxies, and depth competition were not fabricated. Existing feature mart fields `injury_risk_score_3yr` and `depth_chart_role_score_3yr` remain useful as missing-input flags, not as populated signals.

## First-Down PBP Proxy Implementation

Migration `0034__first_down_pbp_proxy_features.sql` was applied.

New derived PBP fields:

- `receiving_first_down_exp_pbp`
- `rushing_first_down_exp_pbp`
- `passing_first_down_exp_pbp`
- `high_value_first_down_opportunity_score`
- `receiving_chain_mover_score`
- `rushing_chain_mover_score`

New feature mart fields:

- `receiving_first_down_exp_pbp_3yr`
- `rushing_first_down_exp_pbp_3yr`
- `passing_first_down_exp_pbp_3yr`
- `high_value_first_down_opportunity_score_3yr`
- `receiving_chain_mover_score_3yr`
- `rushing_chain_mover_score_3yr`

These are PBP first-down proxies, not route-based first-down rates. No route share, YPRR, first-read share, true pressure, contact yards, or alignment metric was fabricated.

## Refresh Results

PBP derived refresh:

| Item | Result |
|---|---:|
| Dry-run delete bytes | 51,370,801 |
| Dry-run insert bytes | 73,207,440 |
| Derived row count | 65,358 |
| Receiving first-down rows | 53,018 |
| Rushing first-down rows | 27,023 |
| Passing first-down rows | 7,961 |
| Gate after refresh | unset |

Feature mart refresh:

| Target season | Source window | Rows |
|---:|---|---:|
| 2017 | 2014-2016 | 18,164 |
| 2018 | 2015-2017 | 17,108 |
| 2019 | 2016-2018 | 17,572 |
| 2020 | 2017-2019 | 18,540 |
| 2021 | 2018-2020 | 19,796 |
| 2022 | 2019-2021 | 19,432 |
| 2023 | 2020-2022 | 19,196 |
| 2024 | 2021-2023 | 19,672 |
| 2025 | 2022-2024 | 6,764 |

Total refreshed feature mart rows: 156,244.

## Feature Coverage

2024 and 2025 PPR first-down feature coverage:

| Target | Position | Rows | Receiving FD | Rushing FD | High-value FD |
|---:|---|---:|---:|---:|---:|
| 2024 | QB | 573 | 230 | 573 | 573 |
| 2024 | RB | 1,276 | 1,259 | 1,260 | 1,271 |
| 2024 | TE | 1,087 | 1,078 | 327 | 1,078 |
| 2024 | WR | 1,982 | 1,972 | 1,509 | 1,977 |
| 2025 | QB | 295 | 110 | 295 | 295 |
| 2025 | RB | 366 | 366 | 364 | 366 |
| 2025 | TE | 392 | 389 | 152 | 389 |
| 2025 | WR | 638 | 636 | 486 | 636 |

## Diagnostic Family

Backtest version:

- `ranking_backtest_sql_native_role_context_vor_sensitivity_v0`

Candidate family:

- `role_context_and_vor_sensitivity_v0`

Candidates:

| Candidate | Position | Purpose |
|---|---|---|
| `injury_depth_role_diagnostic_v0` | RB | Exposes role-context missing-input rate. |
| `first_down_pbp_proxy_diagnostic_v0` | WR | Isolates first-down PBP receiving proxy signal. |
| `gemini31_vor_baseline_sensitivity_v0` | QB | Marker candidate for policy sensitivity, paired with separate VOR SQL. |
| `rb_role_pbp_context_blend_v0` | RB | Blends RB PBP signal with role context where populated. |
| `wr_chain_mover_context_blend_v0` | WR | Blends WR PBP first-down proxy with Stats02 role fields. |

Dry-run:

| Item | Result |
|---|---:|
| Candidate count | 5 |
| Expected summary rows | 5 |
| Expected detail rows | 0 |
| Summary estimated bytes | 87,818,821 |
| VOR estimated bytes | 3,230,649 |

Controlled summary write:

| Item | Result |
|---|---|
| BigQuery job ID | `77eaa07d-e783-41d0-b09e-c5e686340cbd` |
| Backtest run ID | `ranking_backtest_sql_native_role_context_vor_sensitivity_v0_ppr` |
| Run rows | 1 |
| Candidate summary rows | 5 |
| Detail rows for this run | 0 |
| Write gate after run | unset |

## Results

2024 validation, PPR:

| Candidate | Position | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|
| `gemini31_vor_baseline_sensitivity_v0` | QB | 0.6924 | 0.5278 | 0.7649 | 0.0000 |
| `injury_depth_role_diagnostic_v0` | RB | 0.7680 | 0.6389 | 0.7857 | 0.5000 |
| `rb_role_pbp_context_blend_v0` | RB | 0.7705 | 0.6343 | 0.7819 | 0.1263 |
| `first_down_pbp_proxy_diagnostic_v0` | WR | 0.7400 | 0.4444 | 0.6755 | 0.0020 |
| `wr_chain_mover_context_blend_v0` | WR | 0.7354 | 0.4468 | 0.6802 | 0.0626 |

2025 holdout, PPR:

| Candidate | Position | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|
| `gemini31_vor_baseline_sensitivity_v0` | QB | 0.6951 | 0.8380 | 0.8862 | 0.0000 |
| `injury_depth_role_diagnostic_v0` | RB | 0.7943 | 1.0000 | 1.0000 | 0.5000 |
| `rb_role_pbp_context_blend_v0` | RB | 0.8146 | 1.0000 | 1.0000 | 0.1226 |
| `first_down_pbp_proxy_diagnostic_v0` | WR | 0.7489 | 0.8333 | 0.8891 | 0.0018 |
| `wr_chain_mover_context_blend_v0` | WR | 0.7441 | 0.8403 | 0.8984 | 0.0621 |

2017-2025 aggregate, PPR:

| Candidate | Position | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|
| `gemini31_vor_baseline_sensitivity_v0` | QB | 0.6923 | 0.5781 | 0.7909 | 0.0022 |
| `injury_depth_role_diagnostic_v0` | RB | 0.7333 | 0.6321 | 0.7704 | 0.5000 |
| `rb_role_pbp_context_blend_v0` | RB | 0.7342 | 0.6210 | 0.7598 | 0.1366 |
| `first_down_pbp_proxy_diagnostic_v0` | WR | 0.7456 | 0.5181 | 0.7259 | 0.0098 |
| `wr_chain_mover_context_blend_v0` | WR | 0.7395 | 0.5133 | 0.7212 | 0.0716 |

Baseline comparison, 2024-2025 PPR:

| Position | Current Pigskin pairwise | Best Phase 32.18 pairwise | Current captured | Best Phase 32.18 captured | Read |
|---|---:|---:|---:|---:|---|
| QB | 0.6929 | 0.6923 | 0.8256 | 0.7909 | Does not beat current |
| RB | 0.7859 | 0.7342 aggregate | 0.8820 | 0.7598 aggregate | Holdout looks good, aggregate does not |
| WR | 0.7834 | 0.7456 aggregate | 0.7811 | 0.7259 aggregate | Short-window captured points improve, aggregate and pairwise do not |

## VOR Baseline Sensitivity

2024-2025 PPR:

| Policy | VOR captured | Top-24 hit | Top-50 hit | Top-100 hit | Pick-band regret | Pairwise |
|---|---:|---:|---:|---:|---:|---:|
| `current_sql_vorp_qb12_rb24_wr24_te12` | 0.8403 | 0.3461 | 0.5539 | 0.7937 | 2402.58 | 0.5639 |
| `middle_qb12_rb30_wr42_te12` | 0.7896 | 0.3461 | 0.5539 | 0.7937 | 3516.88 | 0.5639 |
| `deep_vorp_qb15_rb36_wr55_te12` | 0.7805 | 0.3461 | 0.5539 | 0.7937 | 4319.56 | 0.5639 |

The deep QB15/RB36/WR55/TE12 policy did not improve the tested slice. It lowered VOR captured and increased pick-band regret. Stored VOR semantics were not changed.

## Validation

Checks run:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: pass
- `.\venv\Scripts\python.exe -m py_compile app.py src\nflverse_ideal_stats.py src\ranking_formula_backtests.py`: pass
- `.\venv\Scripts\python.exe -m compileall -q src scripts`: pass
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_ideal_stats tests.test_ranking_formula_backtests`: 114 tests, OK
- `.\venv\Scripts\python.exe -m unittest discover tests`: 768 tests, OK
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: no pending migrations
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: discovery succeeded
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern pbp`: 8 passed, 0 failed
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_feature_mart_pbp`: 3 passed, 0 failed
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking`: 22 passed, 1 failed

Known validation warning:

- `093_projection_rankings_rank_order.sql` failed with `bad_rank_rows = 12`.
- The failure is outside the Phase 32.18 formula/feature mart changes. Ranking formula and feature mart validations in that same pattern passed.

## Safety Confirmation

- SQL-native summary evaluator used.
- Old Python full tournament path was not used.
- No Python player/candidate/week result-row builder was used for the official path.
- `ranking_backtest_results` detail rows written: 0.
- `ranking_formula_champions` rows: 0.
- `analytics_pigskin_rankings` active rows remained 1,140.
- No champion formula activated.
- No live ranking regenerated.
- No deployment.
- No Pigskin chat call.
- No Gemini or LLM ranking generation.
- No live Sleeper API call.
- No raw/source table exposure to Pigskin added.

## Recommendation

First-down PBP proxies should stay in the ranking feature mart. They are useful component inputs, especially for WR/RB short-window captured-points reads, but they do not support a challenger promotion yet.

The next highest-ROI phase should be one of:

- Phase 32.19: Direct NGS receiving/rushing ingest if source coverage is real.
- Phase 32.19: Current injury/depth source remediation so role scores can be populated.
- Phase 32.19: Narrow WR first-down proxy refinement that preserves current Pigskin pairwise strength.
