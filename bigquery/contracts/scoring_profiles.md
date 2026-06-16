# scoring_profiles Contract

Migration SQL: [bigquery/migrations/0003__model_run_config_foundation.sql](../migrations/0003__model_run_config_foundation.sql)

## Purpose

Defines scoring profiles used by projection and ranking model runs.

## Required Grain

One row per scoring profile ID.

## Required Fields

- `scoring_profile_id`
- `display_name`
- `scoring_json`
- `created_at`
- `updated_at`
- `active`

## Seed Rows

- `standard`
- `half_ppr`
- `ppr`

## Default Scoring JSON

Default scoring profiles are enriched by `0006__scoring_profile_fantasy_points.sql` when legacy seed rows are missing the full scoring keys.

Supported keys:

- `passing_yards`
- `passing_tds`
- `interceptions`
- `passing_2pt_conversions`
- `rushing_yards`
- `rushing_tds`
- `rushing_2pt_conversions`
- `receptions`
- `receiving_yards`
- `receiving_tds`
- `receiving_2pt_conversions`
- `fumbles_lost`
- `return_tds`
- `bonuses`
- `kicker`
- `dst`

Default values:

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
- bonuses, kicker, and DST: placeholders until source stats exist

## Compatibility Rules

Current UI labels such as `ranking_version` remain backward-compatible while future rankings begin writing `model_run_id` and `scoring_profile_id`.

Profile-aware player-week scoring is materialized into `analytics_player_fantasy_points_by_profile`. UI and LLM paths should use that table or downstream marts instead of raw `weekly_metrics`.
