# Phase 33.7 EPA, Receiving, Red-Zone, and Goal-Line Feature-Mart Patch

## Final Decision

EPA REDZONE RECEIVING FEATURE PATCH READY

## Scope

Phase 33.7 patched six recoverable fields into the ranking research feature path:

- `passing_epa_per_play`
- `receiving_yards`
- `receiving_epa`
- `red_zone_targets`
- `red_zone_opportunities`
- `goal_line_opportunities`

No BQML models were trained. No live rankings changed. No champion was activated. No Gemini, Pigskin chat, Sleeper API, deploy, or production action occurred.

## Files Changed

- `src/bqml_v2_feature_contract.py`
- `src/ranking_formula_backtests.py`
- `tests/test_bqml_v2_feature_contract.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/validation/phase-33-7-epa-redzone-receiving-feature-mart-patch-report.md`

## Git State

Phase 33.6 was already committed before this phase as:

- `7fda66d phase 33.6 add standard bqml v2 review boards`

Commit hash for this Phase 33.7 package:

- `23cb77f phase 33.7 patch epa red zone feature mart`

Historical Phase 17-33 validation backlog files remained untracked and were not staged as part of this phase.

## Source Definitions

| Field | Source-backed definition |
|---|---|
| `passing_epa_per_play` | `stg_play_player_events` passer EPA divided by passer event count. |
| `receiving_yards` | `stg_player_week_stats.receiving_yards`, clamped at zero for the feature contract. |
| `receiving_epa` | `stg_play_player_events` receiver EPA, with existing truth fallback. |
| `red_zone_targets` | `stg_play_player_events` target events where `yardline_100 <= 20`. |
| `red_zone_opportunities` | target plus rusher events where `yardline_100 <= 20`. |
| `goal_line_opportunities` | target plus rusher events where `yardline_100 <= 5`. |

`red_zone_flag` and `inside_5_flag` were not used.

## Migrations

No migration was required. `ranking_backtest_feature_mart` already had the six target columns.

## Derived Table Changes

`player_week_opportunity_metrics` was refreshed for 2014-2025 after adding yardline-derived red-zone and inside-five metrics:

- Rows: 70,356
- Seasons: 12
- Season-weeks: 257
- Run ID: `opportunity_metrics_2014_2025_20260707T152240Z`

## Feature-Mart Refresh

Refresh target:

- table: `ranking_backtest_feature_mart`
- target seasons: 2017-2025
- scoring profiles: `standard`, `half_ppr`, `ppr`, `gng_keeper`
- positions: QB, RB, WR, TE
- source-window policy: historical seasons only, `source_window_end_season < target_season`

Refresh results:

| Target season | Rows |
|---|---:|
| 2017 | 18,164 |
| 2018 | 17,108 |
| 2019 | 17,572 |
| 2020 | 18,540 |
| 2021 | 19,796 |
| 2022 | 19,432 |
| 2023 | 19,196 |
| 2024 | 19,672 |
| 2025 | 6,764 |
| Total | 156,244 |

## Coverage After Patch

Coverage is identical across the four refreshed scoring profiles because these source features are scoring-profile independent.

| Position | Rows | Passing EPA rows | Receiving yards rows | Receiving EPA rows | Red-zone target rows | Red-zone opp rows | Goal-line opp rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| QB | 4,646 | 4,630 | 4,646 | 1,950 | 4,646 | 4,646 | 4,646 |
| RB | 9,969 | 1,019 | 9,969 | 9,691 | 9,881 | 9,881 | 9,881 |
| WR | 15,988 | 3,229 | 15,988 | 15,788 | 15,807 | 15,807 | 15,807 |
| TE | 8,458 | 531 | 8,458 | 8,381 | 8,391 | 8,391 | 8,391 |

Position-specific BQML usage remains restricted by the feature contract:

- QB uses `passing_epa_per_play`.
- RB uses `red_zone_opportunities` and `goal_line_opportunities`.
- WR and TE use `receiving_yards`, `receiving_epa`, and `red_zone_targets`.

## Range Checks

Range checks passed after clamping `receiving_yards` to zero:

- `receiving_yards < 0`: 0 rows.
- `red_zone_targets < 0`: 0 rows.
- `red_zone_opportunities < 0`: 0 rows.
- `goal_line_opportunities < 0`: 0 rows.
- extreme red-zone target count: 0 rows.
- extreme red-zone opportunity count: 0 rows.
- extreme goal-line opportunity count: 0 rows.

EPA fields can be negative or positive by design.

## Leakage Checks

Leakage checks passed:

- `source_window_end_season >= target_season`: 0 rows.
- `target_season = 2026`: 0 rows.
- no live ranking writes.
- no champion writes.
- no `ranking_backtest_results` detail writes.
- no `analytics_pigskin_rankings_candidates` overwrite.
- no target-season features added as predictors.

## BQML V2 Contract Updates

Standard BQML v2 training predictors now include the six recovered features where position-appropriate.

Predictor count:

- before Phase 33.7: 41
- after Phase 33.7: 47

Still blocked:

- `ngs_catch_over_expected_score_3yr`
- route-derived metrics without real route denominators
- historical depth
- current Sleeper context as historical truth
- `pigskin_context_score`

## Standard Dataset Dry-Run After Patch

Dry-runs:

| Query | Bytes |
|---|---:|
| feature mart delete, 2025 Standard slice | 63,806,116 |
| feature mart insert, 2025 Standard slice | 193,411,177 |
| Standard training dataset | 1,219,493,385 |
| Standard coverage query | 26,143,117 |
| Standard integrity query | 12,851,069 |

Standard integrity result:

| Check | Result |
|---|---:|
| record_count | 39,061 |
| leakage_window_count | 0 |
| missing_player_id_count | 0 |
| missing_scoring_profile_count | 0 |
| missing_target_label_count | 0 |
| duplicate_grain_count | 0 |

## Tests and Checks

Focused checks run:

- `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract tests.test_ranking_formula_backtests.RankingFormulaBacktestTests.test_opportunity_metrics_insert_sql_uses_safe_sources_and_flags_blocked_metrics tests.test_ranking_formula_backtests.RankingFormulaBacktestTests.test_feature_mart_insert_sql_consumes_opportunity_metrics tests.test_ranking_formula_backtests.RankingFormulaBacktestTests.test_feature_mart_insert_sql_excludes_target_season_predictors tests.test_ranking_formula_backtests.RankingFormulaBacktestTests.test_feature_mart_delete_sql_is_bounded_not_global_truncate`: passed, 23 tests.
- `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py src\ranking_formula_backtests.py`: passed.
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed.
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: passed, no pending migrations.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: passed, validations discovered through 245.
- `git diff --check`: no whitespace errors; Git printed CRLF normalization warnings for touched files.

Known warning:

- Running the full `tests.test_ranking_formula_backtests` module still hits a pre-existing Pigskin declaration scan failure against `app.py` because it finds `ranking_backtest_results`. The focused Phase 33.7 tests passed.

## No-Training Confirmation

No BQML model was trained or created in this phase.

## No-Live-Change Confirmation

No live ranking table changed:

- `analytics_pigskin_rankings`: not written.
- `analytics_pigskin_rankings_candidates`: not overwritten.
- `ranking_formula_champions`: not written.
- `ranking_backtest_results`: not written.

## Recommended Next Phase

Phase 33.8: Standard BQML v2 retrain with patched features.
