# analytics_player_fantasy_points_by_profile Contract

Migration: [bigquery/migrations/0006__scoring_profile_fantasy_points.sql](../migrations/0006__scoring_profile_fantasy_points.sql)

Materializer: [src/materialize_fantasy_points.py](../../src/materialize_fantasy_points.py)

Scoring engine: [src/fantasy_scoring.py](../../src/fantasy_scoring.py)

## Purpose

Profile-aware historical fantasy points for player-week evidence.

This table preserves existing PPR fields elsewhere and adds a scoring-profile-aware layer for trade history, player profiles, rankings, projections, backtests, and Pigskin evidence packets.

## Grain

One row per:

- `player_id_internal` when available
- `source_player_key` fallback
- `season`
- `week`
- `scoring_profile_id`

## Required Fields

- player identity: `player_id_internal`, `source_player_key`, `player_display_name`
- context: `team`, `opponent`, `position`, `season`, `week`
- profile context: `scoring_profile_id`, `league_type_id`, `roster_format_id`
- scoring components: `passing_points`, `rushing_points`, `receiving_points`, `reception_points`, `turnover_points`, `bonus_points`, `kicker_points`, `dst_points`
- output: `total_fantasy_points`
- JSON encoded strings: `scoring_breakdown_json`, `source_stat_json`, `source_freshness_json`, `missing_data_flags`
- timestamps: `created_at`, `updated_at`

## Supported Profile IDs

Default profiles:

- `standard`
- `half_ppr`
- `ppr`

The scoring constants come from `scoring_profiles.scoring_json`. The Python module has local seed defaults only for offline tests and custom profile helpers.

## Default Scoring Assumptions

- passing yards: `0.04`
- passing TDs: `4`
- interceptions: `-2`
- rushing yards: `0.1`
- rushing TDs: `6`
- receptions: `0`, `0.5`, or `1`
- receiving yards: `0.1`
- receiving TDs: `6`
- fumbles lost: `-2`
- two-point conversions: `2`
- return TDs: `6`
- bonuses: zero by default
- kicker and DST fields: placeholders until source stats exist

## Missing Data

Missing source fields default to zero and are recorded in `missing_data_flags`.

Known examples:

- `missing_interceptions`
- `missing_fumbles_lost`
- `missing_passing_2pt_conversions`
- `missing_player_id_internal`

## Sleeper Custom Scoring

`build_scoring_profile_from_sleeper_settings()` maps known Sleeper keys to internal scoring fields and preserves unknown keys in `unmapped_settings`.

Sleeper league wiring is intentionally deferred.

## Consumer Rules

UI and LLM paths should consume this table or downstream compatibility marts instead of raw `weekly_metrics`.

Future consumers:

- `compat_trade_player_history`
- `compat_player_profiles_current`
- `compat_trade_assets_current`
- `llm_player_context_packet`
- ranking and projection feature marts
- backtests and claim tracking
