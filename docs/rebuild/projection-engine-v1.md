# Projection Engine V1

This document defines the first deterministic projection layer for AI vs. Meatbags.

## Status

Runtime Streamlit behavior is unchanged. The projection engine is a standalone runner in [src/projection_engine.py](../../src/projection_engine.py). It writes only when called directly or from a future Cloud Run Job.

## Outputs

- `projections_player_weekly`
- `projections_player_ros`
- `projections_player_dynasty`
- `projection_rankings_current`

Every output row must include:

- `model_run_id`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `projection_horizon`
- `rank_source`
- confidence and risk scores
- source freshness
- missing-data flags

## Model Run Governance

Persisted runs must:

1. create a bounded `source_freshness_snapshots` row
2. create a `model_runs` row with status `running`
3. write projection rows
4. write `projection_rankings_current`
5. mark the model run `complete`
6. mark the model run `failed` and re-raise on exception

Dry runs use `model_run_id = "dry-run"` and do not mutate BigQuery.

## Inputs

Allowed curated inputs:

- `compat_trade_player_history`
- `compat_player_profiles_current`
- `compat_trade_assets_current`
- `fraud_watch_packets`
- `sleeper_breakout_packets`
- `analytics_player_weekly_truth` only as source freshness metadata
- `analytics_player_fantasy_points_by_profile` only as source freshness metadata

The engine must not query raw `weekly_metrics`, `play_by_play`, NGS, FTN, snap, injury, or raw Sleeper tables.

## Baseline Formulas

Weekly V1 blends:

- recent profile-aware fantasy points
- current profile fantasy points
- Pigskin projection context
- role score
- trend score
- fraud penalty
- breakout lift
- scoring profile factor
- roster format QB factor

ROS V1 starts from the weekly baseline and applies:

- remaining games placeholder
- role stability
- trend
- position risk
- scoring profile
- roster format
- league type

Dynasty V1 blends:

- year-one projected value
- year-two and year-three decay
- age curve by position
- position lifecycle
- rookie or prospect adjustment
- contract or team stability placeholder
- market value when available

## Config Versions

Migration `0018__create_projection_outputs.sql` seeds:

- `baseline_weekly_v1`
- `baseline_ros_v1`
- `baseline_dynasty_v1`

These are stored in `feature_config_versions` and mirrored as constants in [src/projection_engine.py](../../src/projection_engine.py).

## Limitations

- No ML.
- No LLM projection generation.
- Remaining games are a placeholder.
- Injury availability is used only after curated data exists.
- Dynasty values are placeholders until backtested.
- Public confidence claims require backtesting.

## CLI

```powershell
python -m src.projection_engine --horizon weekly --season 2025 --week 7 --scoring-profile ppr --league-type redraft --roster-format one_qb --dry-run
python -m src.projection_engine --horizon ros --season 2025 --week 7 --scoring-profile ppr --league-type redraft --roster-format one_qb --dry-run
python -m src.projection_engine --horizon dynasty --season 2025 --week 7 --scoring-profile ppr --league-type dynasty --roster-format superflex --dry-run
```

## Phase 15.1 Cleanup Note

Phase 14.2 left a partial projection model run after a BigQuery streaming-buffer update failure:

- `weekly_projection-2025-1-20260616T113848Z-f07a0ccb`

Phase 15.1 marked that model run `failed` without deleting projection rows.

The seeded backtest remains valid and uses the separate complete model run:

- `weekly_projection-2025-1-20260616T114422Z-a25a92c1`

No destructive cleanup was performed.
