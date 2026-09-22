# Phase 32.15 PBP ffopportunity Splits Report

Final decision: **PBP XFP FEATURES IMPLEMENTED WITH WARNINGS**

## Scope

Phase 32.15 ingested PBP-level ffopportunity pass and rush splits, derived weekly player PBP opportunity metrics, refreshed the leakage-safe ranking feature mart, and ran SQL-native diagnostics.

This phase did not deploy, regenerate live rankings, activate champions, call Pigskin chat, call Gemini, run live Sleeper API, write detail rows, or globally truncate any table.

## Git State

Before Phase 32.15 implementation:

- Phase 32.14 files were uncommitted.
- `AGENTS.md` had an unrelated local modification and was not staged.
- Historical validation backlog files remained untracked and were not staged.

Preserve-current-work action:

- Commit created: `8fe2cc2 phase 32.14 test stats02 ideal formulas`

After implementation before final packaging:

- Modified tracked files are Phase 32.15 code, docs, and tests plus unrelated `AGENTS.md`.
- Untracked historical validation backlog files remain untracked.

## Files Changed

- `src/nflverse_ideal_stats.py`
- `src/ranking_formula_backtests.py`
- `tests/test_nflverse_ideal_stats.py`
- `tests/test_ranking_formula_backtests.py`
- `bigquery/migrations/0033__pbp_ffopportunity_splits.sql`
- `bigquery/validations/223_raw_ffopportunity_pbp_tables_exist.sql`
- `bigquery/validations/224_raw_ffopportunity_pbp_grain.sql`
- `bigquery/validations/225_player_week_pbp_opportunity_metrics_grain.sql`
- `bigquery/validations/226_player_week_pbp_opportunity_metrics_ranges.sql`
- `bigquery/validations/227_player_week_pbp_opportunity_metrics_flags.sql`
- `bigquery/validations/228_ranking_feature_mart_pbp_xfp_columns.sql`
- `bigquery/validations/229_ranking_feature_mart_pbp_xfp_ranges.sql`
- `bigquery/validations/230_ranking_feature_mart_pbp_no_target_leakage.sql`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/validation/phase-32-15-pbp-ffopportunity-splits-report.md`

## Source Audit

`nflreadpy.load_ff_opportunity` supports:

- `stat_type="weekly"`
- `stat_type="pbp_pass"`
- `stat_type="pbp_rush"`

PBP pass source fields include passer and receiver IDs, names, positions, `game_id`, `play_id`, `season`, `week`, `air_yards`, `yardline_100`, `goal_to_go`, `pass_completion_exp`, `yards_after_catch_exp`, `pass_touchdown_exp`, `pass_first_down_exp`, `pass_interception_exp`, and `two_point_conv_exp`.

PBP rush source fields include rusher ID, name, position, `game_id`, `play_id`, `season`, `week`, `yardline_100`, `goal_to_go`, `rushing_yards_exp`, `rushing_td_exp`, `rushing_fd_exp`, `rush_yards_exp`, `rush_touchdown_exp`, `rush_first_down_exp`, and `two_point_conv_exp`.

Exact fantasy xFP fields are not exposed by these PBP tables. Phase 32.15 derives xFP-like component proxies from expected component columns and records that policy in `missing_flags_json`.

## Tables Added

Migration applied:

- `0033__pbp_ffopportunity_splits.sql`

Raw tables:

- `raw_ffopportunity_pbp_pass`
- `raw_ffopportunity_pbp_rush`

Derived table:

- `player_week_pbp_opportunity_metrics`

Feature mart columns added:

- `receiving_xfp_pbp_3yr`
- `rushing_xfp_pbp_3yr`
- `passing_xfp_pbp_3yr`
- `red_zone_xfp_score_3yr`
- `goal_line_xfp_score_3yr`
- `high_value_target_xfp_score_3yr`
- `high_value_rush_xfp_score_3yr`
- `receiving_xfp_share_pbp_3yr`
- `rushing_xfp_share_pbp_3yr`
- `opportunity_quality_score_3yr`
- `pbp_xfp_missing_flags_json`

## Backfill Coverage

Dry-run:

- `pbp_pass`: 227,146 source rows, 227,146 normalized rows, 219,842 mapped receiver rows.
- `pbp_rush`: 175,791 source rows, 175,775 normalized rows, 175,775 mapped rusher rows.

Authorized bounded write:

- Gate used: `ALLOW_NFLVERSE_IDEAL_STATS_INGEST=true`
- Gate was set inside the command process and removed afterward.
- Source version: `ffopportunity_pbp_latest`
- Season range: 2014-2025
- Pass raw rows written: 227,146
- Rush raw rows written: 175,775
- Derived weekly PBP rows written: 65,358
- Derived run ID: `pbp-ideal-stats-20260705T154423Z-825eb7fb`

Raw rows by season:

| Season | Pass rows | Pass mapped | Rush rows | Rush mapped |
|---:|---:|---:|---:|---:|
| 2014 | 18,709 | 18,443 | 14,270 | 14,270 |
| 2015 | 19,179 | 18,943 | 14,082 | 14,082 |
| 2016 | 19,193 | 18,885 | 13,889 | 13,889 |
| 2017 | 18,396 | 18,059 | 14,342 | 14,342 |
| 2018 | 18,589 | 18,059 | 13,877 | 13,877 |
| 2019 | 18,642 | 17,889 | 14,029 | 14,029 |
| 2020 | 19,084 | 18,336 | 14,502 | 14,502 |
| 2021 | 19,769 | 19,075 | 15,164 | 15,164 |
| 2022 | 19,100 | 18,282 | 15,463 | 15,463 |
| 2023 | 19,333 | 18,445 | 15,331 | 15,331 |
| 2024 | 18,689 | 17,847 | 15,481 | 15,481 |
| 2025 | 18,463 | 17,579 | 15,345 | 15,345 |

## Feature Mart Refresh

Fast refresh:

- 2024: 19,672 rows, source window 2021-2023.
- 2025: 6,764 rows, source window 2022-2024.

Full bounded refresh:

- Target seasons: 2017-2025.
- Profiles: `ppr`, `half_ppr`, `standard`, `gng_keeper`.
- Positions: QB, RB, WR, TE.
- Total rows refreshed: 156,244.

Rows by target season:

| Target season | Rows |
|---:|---:|
| 2017 | 18,164 |
| 2018 | 17,108 |
| 2019 | 17,572 |
| 2020 | 18,540 |
| 2021 | 19,796 |
| 2022 | 19,432 |
| 2023 | 19,196 |
| 2024 | 19,672 |
| 2025 | 6,764 |

Leakage guard:

- Feature mart still uses `metrics.season BETWEEN @source_window_start_season AND @source_window_end_season`.
- It also requires `metrics.season < @target_season`.
- PBP source years are aggregated only through the source window before each target season.

## SQL-Native Diagnostics

Candidate family:

- `pbp_xfp_diagnostic_v0`

Candidates:

- `pbp_xfp_qb_pass_rush_v0`
- `pbp_xfp_rb_high_value_rush_recv_v0`
- `pbp_xfp_wr_high_value_receiving_v0`
- `pbp_xfp_te_receiving_role_v0`

Dry-run estimates:

| Scope | Candidate count | Summary rows | Detail rows | Estimated bytes |
|---|---:|---:|---:|---:|
| 2024-2025 | 4 | 16 | 0 | 14,060,961 |
| 2017-2025 | 4 | 16 | 0 | 81,842,565 |

2024-2025 PPR PBP diagnostics:

| Candidate | Position | Sample | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|---:|
| `pbp_xfp_qb_pass_rush_v0` | QB | 868 | 0.7032 | 0.6759 | 0.8152 | 0.0000 |
| `pbp_xfp_rb_high_value_rush_recv_v0` | RB | 1,642 | 0.7900 | 0.8171 | 0.8931 | 0.0052 |
| `pbp_xfp_te_receiving_role_v0` | TE | 1,479 | 0.7721 | 0.6088 | 0.7520 | 0.0055 |
| `pbp_xfp_wr_high_value_receiving_v0` | WR | 2,620 | 0.7357 | 0.6458 | 0.7923 | 0.0027 |

2017-2025 PPR aggregate PBP diagnostics:

| Candidate | Position | Sample | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|---:|
| `pbp_xfp_qb_pass_rush_v0` | QB | 4,646 | 0.7068 | 0.5744 | 0.7864 | 0.0018 |
| `pbp_xfp_rb_high_value_rush_recv_v0` | RB | 9,969 | 0.7533 | 0.6253 | 0.7630 | 0.0229 |
| `pbp_xfp_te_receiving_role_v0` | TE | 8,453 | 0.7316 | 0.4800 | 0.6730 | 0.0196 |
| `pbp_xfp_wr_high_value_receiving_v0` | WR | 15,978 | 0.7383 | 0.5144 | 0.7229 | 0.0124 |

Selected 2024-2025 PPR baseline comparison:

| Position | Candidate | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|
| QB | current Pigskin | 0.6929 | 0.6829 | 0.8256 | 0.0000 |
| QB | PBP diagnostic | 0.7032 | 0.6759 | 0.8152 | 0.0000 |
| RB | current Pigskin | 0.7859 | 0.8067 | 0.8820 | 0.0008 |
| RB | PBP diagnostic | 0.7900 | 0.8171 | 0.8931 | 0.0052 |
| RB | scarcity adjusted | 0.7744 | 0.8345 | 0.9108 | 0.0192 |
| TE | current Pigskin | 0.7781 | 0.6181 | 0.7614 | 0.0037 |
| TE | PBP diagnostic | 0.7721 | 0.6088 | 0.7520 | 0.0055 |
| TE | Stats02 ideal | 0.7769 | 0.6343 | 0.7696 | 0.0057 |
| WR | current Pigskin | 0.7834 | 0.6424 | 0.7811 | 0.0018 |
| WR | PBP diagnostic | 0.7357 | 0.6458 | 0.7923 | 0.0027 |
| WR | Stats02 ideal | 0.7658 | 0.6597 | 0.8011 | 0.0022 |

## Controlled Summary Write

Dry-run passed.

Controlled write:

- Gate used: `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`
- Gate removed afterward.
- Version: `ranking_backtest_sql_native_pbp_xfp_v0`
- Job ID: `a657eaa4-77e7-4198-8f30-265dc2a934f3`
- Summary-only: true
- Detail rows written: 0

Post-write verification:

- `ranking_backtest_runs`: 4 rows for `ranking_backtest_sql_native_pbp_xfp_v0`
- `ranking_backtest_candidate_summaries`: 16 rows for `ranking_backtest_sql_native_pbp_xfp_v0`
- `ranking_backtest_results`: 0 rows for `ranking_backtest_sql_native_pbp_xfp_v0`

No rows were written to:

- `ranking_formula_champions`
- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_candidates`

## Tests And Checks

Focused checks:

- `python -m py_compile src\nflverse_ideal_stats.py src\ranking_formula_backtests.py`: passed.
- `python -m unittest tests.test_nflverse_ideal_stats tests.test_ranking_formula_backtests`: 106 tests passed. PowerShell wrapped unittest progress stderr as `NativeCommandError`, but unittest reported `OK`.
- `python scripts/run_bigquery_migrations.py --dry-run`: discovered migration 0033.
- `python scripts/run_bigquery_migrations.py --list-pending`: only 0033 pending before apply.
- `python scripts/run_bigquery_migrations.py --apply`: applied 0033.

Validation patterns:

- `python scripts/run_bigquery_validations.py --run --pattern pbp`: 8 passed, 0 failed.
- `python scripts/run_bigquery_validations.py --run --pattern ffopportunity`: 4 passed, 0 failed.
- `python scripts/run_bigquery_validations.py --run --pattern ideal`: 6 passed, 0 failed.
- `python scripts/run_bigquery_validations.py --run --pattern ranking_backtest`: 3 passed, 0 failed.
- `python scripts/run_bigquery_validations.py --run --pattern ranking_formula`: 6 passed, 0 failed.

Final broad checks are run after this report is created.

Final broad checks:

- `python scripts/check_deployment_safety.py`: passed.
- `python -m py_compile app.py`: passed.
- `python -m compileall -q src scripts`: passed.
- `python -m unittest discover tests`: 760 tests passed.
- `python scripts/run_bigquery_migrations.py --list-pending`: no pending migrations.
- `python scripts/run_bigquery_validations.py --dry-run`: discovered validation files through `230_ranking_feature_mart_pbp_no_target_leakage.sql`.

## Warnings

- PBP pass/rush tables do not expose official fantasy-point xFP fields. The derived metrics are component proxies from expected pass, rush, touchdown, first-down, yardline, and two-point fields.
- TE PBP split diagnostics did not beat current Pigskin or Stats02 ideal TE on the 2024-2025 PPR comparison.
- RB and WR signals are useful, but not enough for champion activation.
- Direct injury and depth role scoring remain deferred.
- Unrelated `AGENTS.md` remains locally modified and was not staged.
- Historical validation backlog files remain untracked and were not staged.

## Owner-Review Recommendation

Keep PBP split xFP as a feature-mart enrichment. Do not activate a champion.

Recommended next phase:

- Phase 32.16: fast second-pass RB/WR formula refinement blending PBP split xFP with Stats02 weekly ideal fields.
- Follow-up lane: injury/depth role scoring.

No live ranking change occurred. No champion formula was activated.
