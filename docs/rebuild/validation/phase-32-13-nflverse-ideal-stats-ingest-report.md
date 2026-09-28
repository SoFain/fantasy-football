# Phase 32.13 nflverse ideal stats ingest report

Final decision: `IDEAL NFLVERSE STATS INGESTED WITH WARNINGS`

## Scope

Phase 32.13 pursued ideal fantasy-ranking stats from public nflverse/ffverse sources. It did not deploy, regenerate live Pigskin rankings, activate champions, call Pigskin chat, call Gemini, call live Sleeper, write detail backtest rows, or run the old Python full tournament path.

Phase 32.12 was preserved first:

- Commit: `c2dcf71 phase 32.12 add opportunity metrics warehouse`

## Source audit

| Source family | Repo status | Source status | Phase 32.13 action |
|---|---|---|---|
| ffopportunity expected fantasy points | Not previously ingested | `nflreadpy.load_ff_opportunity` is installed and supports weekly expected fantasy points. nflreadr documents `weekly`, `pbp_pass`, and `pbp_rush`; ffopportunity publishes automated release data in RDS, parquet, and CSV. | Ingested weekly 2014-2025. |
| Participation | Existing raw/staging lane | Repo already has `raw_nflverse_participation` and `stg_participation_context`. | Used existing `stg_participation_context` snap context where identity maps. |
| Snap counts | Existing raw/staging lane | Repo already has `raw_nflverse_snap_counts` and staging use through participation context. | Used existing offensive snap percentage/count proxies. |
| Next Gen Stats | Existing raw lane | Repo has NGS raw table contracts. Direct NGS derivation remains deferred. | Used existing `player_week_advanced_metrics.cpoe` as a QB efficiency proxy and flagged direct NGS gaps. |
| Injuries | Existing raw lane | Repo has raw injury source contract. | Deferred direct scoring. `injury_risk_score_3yr` remains null with missing flags. |
| Depth charts | Existing raw lane | Repo has raw depth chart source contract. | Deferred direct scoring. `depth_chart_role_score_3yr` remains null with missing flags. |
| PFR advanced stats | Not added in this phase | Python loader coverage was not part of the fast path. | Deferred. |
| FTN charting | Existing historical source lane | Kept out of this phase unless already available/free and clearly documented. | Deferred. |

External source notes:

- nflreadr documents `load_ff_opportunity(seasons, stat_type = c("weekly", "pbp_pass", "pbp_rush"), model_version = c("latest", "v1.0.0"))`: https://nflreadr.nflverse.com/reference/load_ff_opportunity.html
- nflreadpy documents `load_ff_opportunity()` as the Python port path for expected yards, touchdowns, and fantasy points: https://github.com/nflverse/nflreadpy
- ffopportunity documents automated release data and manual release downloads: https://github.com/ffverse/ffopportunity

## Files changed

- `bigquery/migrations/0032__nflverse_ideal_stats.sql`
- `bigquery/validations/215_raw_ffopportunity_weekly_exists.sql`
- `bigquery/validations/216_player_week_ideal_opportunity_metrics_exists.sql`
- `bigquery/validations/217_raw_ffopportunity_weekly_grain.sql`
- `bigquery/validations/218_player_week_ideal_opportunity_metrics_grain.sql`
- `bigquery/validations/219_player_week_ideal_opportunity_metrics_ranges.sql`
- `bigquery/validations/220_player_week_ideal_opportunity_metrics_flags.sql`
- `bigquery/validations/221_ranking_feature_mart_ideal_stats_columns.sql`
- `bigquery/validations/222_ranking_feature_mart_ideal_stats_ranges.sql`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `src/nflverse_ideal_stats.py`
- `src/ranking_formula_backtests.py`
- `tests/test_nflverse_ideal_stats.py`

## Migration and tables

Applied migration:

- `0032__nflverse_ideal_stats.sql`

Created:

- `raw_ffopportunity_weekly`
- `player_week_ideal_opportunity_metrics`

Altered additively:

- `ranking_backtest_feature_mart`

New feature mart columns:

- `xfp_score_3yr`
- `xfp_share_3yr`
- `fantasy_points_over_expectation_3yr`
- `offensive_snap_share_3yr`
- `snap_role_stability_3yr`
- `receiving_role_dominance_xfp_3yr`
- `high_value_xfp_score_3yr`
- `qb_ngs_efficiency_score_3yr`
- `injury_risk_score_3yr`
- `depth_chart_role_score_3yr`

No global truncate was used. Raw and derived writes were bounded by `season BETWEEN 2014 AND 2025` and `source_version = 'ffopportunity_weekly_latest'`.

## Backfill coverage

Ingest command used a temporary gate:

- `ALLOW_NFLVERSE_IDEAL_STATS_INGEST=true`
- `python -m src.nflverse_ideal_stats --season-start 2014 --season-end 2025 --write --derive`
- Gate was removed after the command.

Results:

| Object | Scope | Rows |
|---|---|---:|
| `raw_ffopportunity_weekly` | 2014-2025 | 64,624 |
| `player_week_ideal_opportunity_metrics` | 2014-2025 | 64,624 |

Rows by season were present for every season 2014 through 2025. 2025 row count was 5,631.

Warning: the source returned 69,302 rows before normalization. The written 64,624 rows are the rows with usable player, season, week, and position keys. Non-core special-team/defensive rows can still appear when the source has valid keys, but the ranking feature mart consumes only QB/RB/WR/TE.

## Feature mart refresh

The feature mart was refreshed for target seasons 2017 through 2025, four scoring profiles, and QB/RB/WR/TE only. Predictors use source seasons before the target season.

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

Total refreshed mart rows: 156,244.

2024 and 2025 coverage:

- xFP score/share coverage was effectively full for QB and very high for RB/WR/TE.
- snap share coverage was high where snap count identity mapped.
- QB efficiency proxy covered QB rows through existing CPOE.
- injury and depth chart scores remained intentionally null.

## Diagnostic signal

SQL-native dry-run:

- candidate count: 4
- target seasons: 2024, 2025
- scoring profile: `ppr`
- estimated bytes: 12,314,401
- detail rows written: 0

Controlled summary-only write:

- Gate: `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`
- Version: `ranking_backtest_sql_native_ideal_stats_diagnostics_v0`
- Job ID: `ae1e7417-b036-44dd-a7e3-7cb5ba496b15`
- Run rows written: 1
- Summary rows written: 4
- Detail rows written: 0
- Champions written: 0
- Gate removed afterward.

Diagnostic summaries:

| Candidate | Position | Sample size | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|---:|
| `ranking_formula_qb_ideal_stats_diagnostic_v0_2026_001` | QB | 868 | 0.7001 | 0.6921 | 0.8389 | 0.0000 |
| `ranking_formula_rb_ideal_stats_diagnostic_v0_2026_001` | RB | 1,642 | 0.7683 | 0.8113 | 0.8892 | 0.0013 |
| `ranking_formula_te_ideal_stats_diagnostic_v0_2026_001` | TE | 1,479 | 0.7725 | 0.6343 | 0.7695 | 0.0054 |
| `ranking_formula_wr_ideal_stats_diagnostic_v0_2026_001` | WR | 2,620 | 0.7738 | 0.6447 | 0.7866 | 0.0019 |

Interpretation: the xFP and snap/role features show useful signal, especially RB and WR/TE pairwise behavior. This is evidence for a Phase 32.14 candidate sprint, not a champion activation.

## Missing and proxy policy

The derived table includes:

- `missing_flags_json`
- `source_provenance_json`
- `source_updated_at`

Direct true route share, first-read share, injury scoring, and depth chart scoring are not fabricated. Nulls are preserved with flags. Negative expected fantasy point rows are allowed in raw expected points, but xFP share is computed from nonnegative expected points to avoid impossible negative share values.

## Validations and checks

Passed:

- `python scripts/check_deployment_safety.py`
- `python -m compileall -q src scripts`
- `python -m unittest tests.test_nflverse_ideal_stats`
- `python -m unittest tests.test_ranking_formula_backtests`
- `python -m unittest discover tests` with 750 tests
- `python scripts/run_bigquery_migrations.py --list-pending`: no pending migrations
- `python scripts/run_bigquery_validations.py --dry-run`: 222 validations discovered
- `python scripts/run_bigquery_validations.py --run --pattern "ideal|ffopportunity"`: 8 passed, 0 failed
- `python scripts/run_bigquery_validations.py --run --pattern ranking_backtest`: 3 passed, 0 failed
- `python scripts/run_bigquery_validations.py --run --pattern ranking_formula`: 6 passed, 0 failed

Validation repair:

- Initial xFP-share validation failed because a small number of source rows had negative expected fantasy points.
- Fixed by using nonnegative expected fantasy points for xFP share numerator and team denominator.
- Rebuilt derived metrics and refreshed the feature mart.
- Re-run validations passed.

## No-live-change confirmations

- No production deploy.
- No live Pigskin ranking regeneration.
- No champion formula activation.
- No `analytics_pigskin_rankings` write.
- No `analytics_pigskin_rankings_candidates` write.
- No `ranking_backtest_results` detail rows written.
- No Pigskin chat call.
- No Gemini ranking call.
- No live Sleeper API call.

## Warnings

- `pbp_pass` and `pbp_rush` ffopportunity lanes were not ingested in this phase. Weekly xFP was the fastest high-value source and is enough to start formula iteration.
- Direct injury and depth chart scores are still deferred.
- Direct NGS fields are not fully modeled. `qb_ngs_efficiency_score_3yr` currently uses existing CPOE as a proxy.
- BigQuery emitted a future pandas helper warning: `pandas-gbq` may be required for future `load_table_from_dataframe` behavior.
- The worktree still has historical validation backlog files that were intentionally not staged or committed in prior phases.

## Recommended next phase

`Phase 32.14 — Stats02 formulas using ideal stats`

Recommended work:

- Build position-specific formulas that use the new xFP columns.
- Compare weekly xFP diagnostics against current Pigskin, simple projection, and best opportunity diagnostics.
- Add direct injury/depth scoring only after a separate source-shape audit.
- Consider pbp-level ffopportunity only if weekly xFP diagnostics justify the extra source volume.
