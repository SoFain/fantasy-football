# Phase 32.20 Injury Context Feature Refresh Report

Final decision: INJURY CONTEXT FEATURE MART READY WITH WARNINGS

## Scope

Phase 32.20 improved deterministic historical injury context for ranking research. It did not deploy, regenerate live rankings, activate formula champions, expose Pigskin chat, run Pigskin prompts, call LLM-backed ranking generation, write tournament detail rows, run materializations outside the ranking research lane, or use Sleeper current team as historical truth.

## Files Changed

- `bigquery/migrations/0038__injury_context_feature_mart_columns.sql`
- `bigquery/validations/236_player_week_role_context_identity_coverage.sql`
- `bigquery/validations/237_player_week_role_context_injury_feature_ranges.sql`
- `bigquery/validations/238_ranking_feature_mart_injury_columns.sql`
- `bigquery/validations/239_ranking_feature_mart_injury_no_target_leakage.sql`
- `bigquery/validations/240_ranking_feature_mart_injury_ranges.sql`
- `src/materialize_role_context.py`
- `src/ranking_formula_backtests.py`
- `tests/test_materialize_role_context.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`

## Authorization Gates

Initial gate check showed these unset:

- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE`
- `ALLOW_ROLE_CONTEXT_MATERIALIZATION`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `ALLOW_SLEEPER_2026_SNAPSHOT`

Temporary gates used:

- `ALLOW_ROLE_CONTEXT_MATERIALIZATION=true` only inside the role-context refresh command. It was removed immediately after the command.
- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` only inside the SQL-native summary-only write command. It was removed immediately after the command.

Final gate check showed both transient gates unset.

## Identity Audit

Pre-fix `player_week_role_context_metrics` coverage:

- Total rows: 65,864
- Mapped identity rows: 33,459
- Missing identity rows: 32,405
- Missing rate: 0.4920

The missing rows were mostly defense and offensive line. Fantasy-position coverage was already strong:

- QB: 0 missing identity rows
- RB: 177 missing of 5,100 rows
- WR: 69 missing of 8,688 rows
- TE: 11 missing of 4,269 rows

Exact GSIS source matches existed for the missing rows:

- `raw_nflverse_players`: 2,538 distinct missing GSIS IDs
- `raw_nflverse_rosters`: 2,538
- `raw_nflverse_rosters_weekly`: 2,538
- `sleeper_player_context_current`: 1,319

Fix applied:

- `player_id_internal` now falls back to `gsis:<gsis_id>` when `player_identity_bridge` lacks a mapped ID.
- `identity_mapping_method` records `identity_bridge_gsis_exact` or `gsis_exact_fallback`.
- `identity_mapping_confidence` records `1.0` for bridge hits and `0.75` for exact GSIS fallback.

Post-refresh role-context summary:

- Rows: 65,864
- Seasons: 2014-2025
- Missing identity rows: 0
- `gsis_exact_fallback` rows: 32,405
- Depth score missing rows: 65,864, expected because historical depth remains unavailable

## Injury Features

Added to `player_week_role_context_metrics`:

- `injury_status_score`
- `injury_burden_score`
- `missed_time_risk_score`
- `availability_score`
- `injury_context_missing_flags_json`
- `identity_mapping_method`
- `identity_mapping_confidence`

Added to `ranking_backtest_feature_mart`:

- `injury_status_score_3yr`
- `injury_burden_score_3yr`
- `missed_time_risk_score_3yr`
- `availability_score_3yr`
- `injury_context_missing_flags_json`

Policy:

- Higher `injury_status_score` and `availability_score` are healthier.
- Higher `injury_burden_score` and `missed_time_risk_score` are riskier and are inverted in SQL-native scoring.
- Missing values remain null and are flagged. No zero-fill was introduced.
- Source seasons remain strictly before target season in the feature mart.

## Materialization Results

Migration:

- Applied `0038__injury_context_feature_mart_columns.sql`.
- `run_bigquery_migrations.py --list-pending` later reported no pending migrations.

Role context refresh:

- Command: `python -m src.materialize_role_context --season-start 2014 --season-end 2025 --write`
- Gate: `ALLOW_ROLE_CONTEXT_MATERIALIZATION=true` only inside that command process
- Rows: 65,864
- Run ID: `role_context_2014_2025_20260705T212619Z`

Feature mart dry run:

- 2024 insert dry-run estimated bytes: 154,631,586

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

The refresh covered PPR, Half PPR, Standard, and GNG Keeper for QB/RB/WR/TE.

## SQL-Native Diagnostic

Candidate set:

- Existing SQL-native tournament candidates: 28
- Injury diagnostic candidates: 12
- Total candidates: 40

Read-only 2024-2025 dry run:

- Estimated bytes: 16,174,977
- Summary rows returned: 40

Read-only 2017-2025 dry run:

- Estimated bytes: 94,973,650
- Summary rows returned: 40

Summary-only write:

- Gate: `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` only inside the command process
- Job ID: `9b108261-1e78-4e50-8cde-467f858d6239`
- Candidate summaries written for this run: 40
- Detail rows written: 0
- Matching `ranking_backtest_results` rows: 0
- Matching `ranking_backtest_runs` rows: 1
- `ranking_formula_champions` count for the run: 0

## Diagnostic Results

2017-2025 aggregate, PPR:

| Position | Best injury-context candidate | Pairwise | Top-N | Rank corr. | Missing |
|---|---|---:|---:|---:|---:|
| QB | `availability_adjusted_current_pigskin_v0` | 0.6870 | 0.5728 | 0.4343 | 0.0305 |
| RB | `availability_adjusted_current_pigskin_v0` | 0.7436 | 0.6200 | 0.5476 | 0.0358 |
| WR | `availability_adjusted_current_pigskin_v0` | 0.7590 | 0.5058 | 0.5586 | 0.0351 |
| TE | `availability_adjusted_current_pigskin_v0` | 0.7364 | 0.4731 | 0.4941 | 0.0357 |

Baseline comparison:

- Current Pigskin still leads the injury-context challengers on aggregate pairwise for QB, RB, WR, and TE.
- RB availability-adjusted Pigskin is close enough to keep as a future modifier candidate.
- Injury-only ranking is not a champion path.
- No formula champion was activated.

## Validations

Passed:

- `234_player_week_role_context_metrics_exists.sql`
- `235_player_week_role_context_metrics_ranges.sql`
- `236_player_week_role_context_identity_coverage.sql`
- `237_player_week_role_context_injury_feature_ranges.sql`
- `238_ranking_feature_mart_injury_columns.sql`
- `239_ranking_feature_mart_injury_no_target_leakage.sql`
- `240_ranking_feature_mart_injury_ranges.sql`
- `209_ranking_backtest_candidate_summaries_grain_and_ranges.sql`

Validation discovery:

- `run_bigquery_validations.py --dry-run` listed validations through `240_ranking_feature_mart_injury_ranges.sql`.

## Checks Run

- `python -m py_compile app.py src\ranking_formula_backtests.py src\materialize_role_context.py`
- `python -m compileall -q src scripts`
- `python -m unittest tests.test_materialize_role_context tests.test_ranking_formula_backtests`
- `python -m unittest discover tests`: 781 tests passed
- `scripts/check_deployment_safety.py`: passed
- `scripts/run_bigquery_migrations.py --dry-run`: migration 0038 discovered
- `scripts/run_bigquery_migrations.py --list-pending`: no pending migrations after apply
- `scripts/run_bigquery_validations.py --dry-run`
- Focused live validations listed above

## Sleeper and Production Guardrails

Sleeper 2026 current snapshot was not refreshed in this phase and was not used for historical feature-mart scoring. Current-roster context remains display/context only.

Read-only production state check:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00082-7bf`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:c675aa578b218581c4a9253e6bd5ceefc6da3ee0198dcb7cb9b98e3c541442e6`
- URL: `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app`
- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` absent/unset
- `USE_PIGSKIN_PACKET_QA_UI=true`

No production settings were changed.

## Warnings

- `gsis_exact_fallback` remains explicit for 32,405 role-context rows. This is deterministic and safe for research, but lower confidence than the primary identity bridge.
- Historical depth context is still blocked. `depth_chart_role_score` remains null by design.
- Injury context is useful as a modifier, not a standalone winning formula.
- The SQL-native summary write produced research summaries only. It should not be treated as a champion recommendation.

## Recommended Next Phase

Phase 32.21 should test a tighter RB/WR/TE modifier family that uses `availability_score_3yr` at low weight while preserving current Pigskin pairwise strength. Keep depth context blocked until a real historical depth source exists.
