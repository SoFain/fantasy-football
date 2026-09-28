# Phase 22.6 Trade Score Contracts Report

Generated: 2026-06-17T06:30:00Z

## Final Decision

`TRADE SCORE CONTRACTS READY WITH WARNINGS`

The deterministic Trade Analyzer score v0 warehouse contract is ready for review. Phase 22.6 added additive schema DDL, mirrored view definitions, contract docs, rollout docs, and validation SQL. No migration was applied, no BigQuery data was mutated, no production flag was changed, and no runtime path was enabled.

Warning:

- `0025__trade_analyzer_score_v0.sql` is now pending in the live migration ledger, as expected. It must not be applied until the operator explicitly authorizes migration application.

## Files Created

Migration:

- `bigquery/migrations/0025__trade_analyzer_score_v0.sql`

Contracts:

- `bigquery/contracts/trade_player_scores.md`
- `bigquery/contracts/trade_player_scores_current.md`
- `bigquery/contracts/compat_trade_player_scores_current.md`

Views:

- `bigquery/views/trade_player_scores_current.sql`
- `bigquery/views/compat_trade_player_scores_current.sql`

Validations:

- `bigquery/validations/150_trade_player_scores_grain.sql`
- `bigquery/validations/151_trade_player_scores_trade_score_range.sql`
- `bigquery/validations/152_trade_player_scores_component_score_range.sql`
- `bigquery/validations/153_trade_player_scores_confidence_range.sql`
- `bigquery/validations/154_trade_player_scores_required_json_fields.sql`
- `bigquery/validations/155_trade_player_scores_missing_flags_exist.sql`
- `bigquery/validations/156_trade_player_scores_source_freshness_exists.sql`
- `bigquery/validations/157_trade_player_scores_current_grain.sql`
- `bigquery/validations/158_compat_trade_player_scores_current_exists.sql`
- `bigquery/validations/159_compat_trade_player_scores_no_raw_source_dependencies.sql`
- `bigquery/validations/160_trade_player_scores_identity_coverage.sql`

Docs:

- `docs/rebuild/trade-analyzer-score-rollout.md`
- `docs/rebuild/compatibility-contracts.md`
- `docs/rebuild/ui-query-debt-register.md`
- `docs/rebuild/table-classification.md`

## Migration Summary

Migration number:

- `0025`

Migration file:

- `bigquery/migrations/0025__trade_analyzer_score_v0.sql`

Objects:

| Object | Type | Notes |
| --- | --- | --- |
| `trade_player_scores` | table | Output table for deterministic score rows. Partitioned by season and clustered by model and scoring context. |
| `trade_player_scores_current` | view | Latest score row per player and scoring context. Reads only `trade_player_scores`. |
| `compat_trade_player_scores_current` | view | Future safe Streamlit and Pigskin read surface. Reads only `trade_player_scores_current`. |

The migration is additive DDL only. It does not backfill, delete, rename, truncate, or compute score rows.

## Contract Summary

The score table supports:

- multiple `model_version` values;
- run lineage through `score_run_id`, `model_run_id`, `ranking_version`, and `feature_config_version_id`;
- scoring context through `scoring_profile_id`, `league_type_id`, and `roster_format_id`;
- season and week context;
- component score columns;
- `trade_score` and `score_tier`;
- `source_freshness_json`;
- `missing_flags_json`;
- `component_json`;
- `created_at` and `created_by`.

The requested score fields are represented:

- `player_id`
- `player_name`
- `position`
- `team`
- `season`
- `week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `current_market_value`
- `projected_3_year_value`
- `market_score`
- `projection_score`
- `recent_production_score`
- `role_usage_score`
- `positional_scarcity_score`
- `efficiency_score`
- `normalized_risk_score`
- `fraud_score`
- `confidence_score`
- `trade_score`
- `score_tier`
- `source_freshness_json`
- `missing_flags_json`
- `component_json`
- `model_version`
- `created_at`

## View Summary

`trade_player_scores_current`:

- selects one latest row per `player_id`, `scoring_profile_id`, `league_type_id`, and `roster_format_id`;
- orders by season, week, created time, model version, and score run;
- reads only the score output table.

`compat_trade_player_scores_current`:

- exposes the safe future UI and Pigskin score read shape;
- includes `player_id_internal` as an alias of `player_id` for compatibility with existing identity contracts;
- includes score components, source freshness, missing flags, and run lineage;
- reads only `trade_player_scores_current`.

## Raw Source Exposure Check

The new migration and view files were scanned for raw/source table names:

- `weekly_metrics`
- `play_by_play`
- `market_values`
- `sleeper_*`
- `ngs_*`
- `ftn_*`
- `injury_reports`
- `depth_charts`

Result:

- no matches in the new migration or view SQL.

## Validation Summary

New validation coverage:

| Validation | Purpose |
| --- | --- |
| `150_trade_player_scores_grain.sql` | table grain uniqueness |
| `151_trade_player_scores_trade_score_range.sql` | final score range |
| `152_trade_player_scores_component_score_range.sql` | component score ranges |
| `153_trade_player_scores_confidence_range.sql` | confidence score range |
| `154_trade_player_scores_required_json_fields.sql` | component JSON fields |
| `155_trade_player_scores_missing_flags_exist.sql` | missing flags presence |
| `156_trade_player_scores_source_freshness_exists.sql` | source freshness presence |
| `157_trade_player_scores_current_grain.sql` | current view grain |
| `158_compat_trade_player_scores_current_exists.sql` | compatibility view existence |
| `159_compat_trade_player_scores_no_raw_source_dependencies.sql` | raw/source dependency guard |
| `160_trade_player_scores_identity_coverage.sql` | identity coverage |

The validation dry-run discovered files `150` through `160`.

## Commands Run

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
```

Results:

| Command | Result |
| --- | --- |
| Migration dry-run | pass, discovered `0025__trade_analyzer_score_v0.sql` |
| Migration list-pending | pass, reports `0025` pending |
| Validation dry-run | pass, discovered validations through `160` |
| Unit tests | pass, 314 tests |
| `app.py` compile | pass |
| `src` and `scripts` compile | pass |
| Deployment safety | pass |

## Migration Application Status

Migrations applied:

- none

Ledger-aware pending migration status:

- `0025: trade analyzer score v0 (sql)`

This is expected because this phase creates migration scaffolding only.

## Feature Flag Status

No feature flags were changed.

Future score runtime wiring must remain default off:

- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`

Production must not enable Trade Analyzer score widgets or score compatibility reads until a later explicitly approved rollout.

## Runtime Safety

No runtime changes occurred:

- no migration application;
- no BigQuery data mutation;
- no deployment;
- no Streamlit flag change;
- no Cloud Run Job trigger;
- no Scheduler job creation;
- no LLM calls;
- no scraping;
- no Firebase artifacts.

## Next Steps

1. Human-review migration `0025` and contracts.
2. Apply migration `0025` only with explicit operator authorization.
3. Add a bounded score builder with dry-run mode.
4. Materialize a small score run from curated 2025 marts.
5. Run `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` after migration application and score materialization.
6. Add a read helper that queries only `compat_trade_player_scores_current`.
7. Wire Streamlit only behind default-off flags.

