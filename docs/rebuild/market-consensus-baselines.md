# Market And Consensus Baselines

This document defines the first source-agnostic outside-baseline layer for AI vs. Meatbags.

## Status

The layer is implemented in [src/market_consensus.py](../../src/market_consensus.py). It supports manual and CSV ingestion first. It does not scrape websites or call paid APIs.

Migration: [bigquery/migrations/0021__create_market_consensus_baselines.sql](../../bigquery/migrations/0021__create_market_consensus_baselines.sql)

## Tables

- `market_consensus_sources`
- `market_consensus_snapshots`
- `market_consensus_player_values`
- `market_consensus_baseline_current`

The migration also adds optional market comparison columns to:

- `backtest_result_player_week`
- `backtest_result_summary`

## Allowed Sources

Allowed source classes:

- Manual rankings or projections.
- CSV exports the project is allowed to use.
- Internal generated baselines.
- API adapters only after credentials and source terms are explicitly configured.

Not allowed:

- Scraping pages that forbid scraping.
- Assuming paid API access exists.
- Letting UI or Pigskin read raw imported files directly.

## Manual CSV Workflow

Register a source:

```powershell
python -m src.market_consensus --register-source --source-id fantasypros_ecr_manual --source-name "FantasyPros ECR Manual" --source-type ecr --access-method csv --dry-run
```

Ingest a CSV:

```powershell
python -m src.market_consensus --ingest-csv path/to/file.csv --source-id manual_adp --season 2025 --week 1 --scoring-profile ppr --dry-run
```

Common accepted CSV columns include:

- `player`, `player_name`, `name`, `display_name`
- `position`, `pos`
- `team`, `current_team`
- `rank`, `rank_overall`, `overall_rank`, `ecr`
- `rank_position`, `pos_rank`
- `projected_points`, `projection`, `points`
- `adp`, `average_draft_position`
- `market_value`, `trade_value`, `value`

## Identity Matching

The resolver uses `player_identity_bridge` first.

Priority:

1. Existing `player_id_internal`.
2. Exact source IDs such as GSIS, Sleeper, FantasyPros, ESPN, Yahoo, PFR, or nflverse IDs.
3. Normalized name plus team plus position.
4. Normalized name plus position when unique.
5. Retain unknown player with `missing_player_id_internal`.

Fallback name matches add `identity_name_fallback_match` to `missing_data_flags`.

## Backtest Use

Backtests can pass `market_source_id` to compare Pigskin projections against a current market baseline.

The comparison supports:

- Pigskin projected points versus market projected points.
- Pigskin projected rank versus market rank.
- Pigskin error versus market error when actual fantasy points exist.
- `model_vs_market_mae_delta`
- `model_vs_market_rank_delta`
- `model_better_than_market_rate`

A negative `model_vs_market_mae_delta` means the model had lower MAE than the market on matched rows.

## Limitations

- Only weekly projection comparison is wired through backtesting v1.
- ADP and market value are stored but not yet converted into a universal point-value baseline.
- Prop lines are stored but not yet translated into player fantasy projections.
- Consensus source licensing must be reviewed before automation.

## Future API Adapters

Future adapters should be isolated per source and must:

- Check credentials and source terms before calls.
- Respect rate limits.
- Write snapshots and normalized rows through this module.
- Preserve source payloads and missing-data flags.
- Avoid direct UI or Pigskin access to raw source files.
