# player_role_usage_metrics_current Contract

## Purpose

Current player role and usage feature mart.

## Grain

One player and current scoring context row for an `as_of_season`, `as_of_week`, and `metric_version`.

## Allowed Upstream Dependencies

`player_week_advanced_metrics`, `stg_participation_context`, and approved recent metrics current views.

## Forbidden Dependencies

Direct raw/source dependencies are forbidden.

## Required Fields

`metric_version`, `feature_run_id`, `as_of_season`, `as_of_week`, player identity fields, `snap_share`, `route_share`, `target_share`, `air_yards_share`, `wopr`, `carry_share`, `opportunity_share`, `red_zone_role`, `high_value_touches`, `trend_direction`, `role_volatility`, `injury_summary`, `depth_summary`, `source_freshness_json`, `missing_data_flags`, `created_at`.

## Route Rule

`route_share` is nullable and must be flagged when no true route source exists.

## Safety Rules

Derived current mart. Safe for compatibility views after validation.
