# Phase 22.8 Trade Score Materialization Report

Date: 2026-06-17

## Scope

Phase 22.8 was intended to apply the additive Trade Analyzer score migration and materialize one bounded 2025 score run only if explicitly authorized.

Target run:

- `season=2025`
- `week=18`
- `scoring_profile_id=ppr`
- `league_type_id=redraft`
- `roster_format_id=one_qb`
- `model_version=trade_score_v0_2025_001`

## Authorization State

Required authorization was not present:

- `ALLOW_TRADE_SCORE_MIGRATION_APPLY`: unset
- `ALLOW_TRADE_SCORE_MATERIALIZATION`: unset

Because `ALLOW_TRADE_SCORE_MIGRATION_APPLY` was not true:

- no migration was applied
- output objects were not created in this phase
- score dry-run and score write were not attempted
- materialization was stopped before any warehouse write path

## Preflight Results

Passed:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Ledger-aware migration check:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
```

Result:

```text
Pending migrations:
- 0025: trade analyzer score v0 (sql)
```

## Migrations

Migration application was not authorized.

Migration `0025__trade_analyzer_score_v0.sql` remains pending and was not applied.

## Object Verification

Object verification was not run because the migration remains pending:

- `trade_player_scores`
- `trade_player_scores_current`
- `compat_trade_player_scores_current`

## Dry-Run Score Builder

The score builder dry-run was not executed because migration authorization was missing and output objects remain pending.

Planned dry-run command once migration apply is authorized:

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v0_2025_001 --dry-run
```

## Materialization

Score materialization was not authorized.

No score rows were written.

Planned write command once both required gates are explicitly authorized:

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v0_2025_001 --write
```

## Validations

Live `trade_score`, `market`, and `content_brief` validation runs were not executed because no migration or score materialization occurred.

Validation dry-run did discover Trade Analyzer score validations:

- `150_trade_player_scores_grain.sql`
- `151_trade_player_scores_trade_score_range.sql`
- `152_trade_player_scores_component_score_range.sql`
- `153_trade_player_scores_confidence_range.sql`
- `154_trade_player_scores_required_json_fields.sql`
- `155_trade_player_scores_missing_flags_exist.sql`
- `156_trade_player_scores_source_freshness_exists.sql`
- `157_trade_player_scores_current_grain.sql`
- `158_compat_trade_player_scores_current_exists.sql`
- `159_compat_trade_player_scores_no_raw_source_dependencies.sql`
- `160_trade_player_scores_identity_coverage.sql`

## Safety Confirmation

- No migration was applied.
- No BigQuery score rows were written.
- No deployment occurred.
- No feature flags were enabled.
- No Cloud Run Jobs were triggered.
- No LLM calls were made.
- No scraping occurred.
- No Firebase artifacts were created.

## Warnings

- Migration `0025` remains pending.
- Score objects are not verified live yet.
- No bounded 2025 week 18 score dry-run or materialization was performed in this phase.

## Final Decision

TRADE SCORE MATERIALIZATION BLOCKED
