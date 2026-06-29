# player_week_advanced_metrics Contract

## Purpose

Derived player-week advanced metrics from canonical staging sources.

## Grain

One player, season, week, team, scoring profile, league type, roster format, and metric version row.

## Allowed Upstream Dependencies

`stg_player_week_stats`, `stg_play_player_events`, `stg_participation_context`, `stg_team_week_stats`, `stg_player_identity`, and curated injury/depth staging.

## Forbidden Dependencies

Direct reads from `raw_nflverse_*`, `play_by_play`, `weekly_metrics`, `ngs_*`, `ftn_charting`, `weekly_snap_counts`, `injury_reports`, `depth_charts`, `source_*`, and `raw_*`.

## Required Metric Fields

`targets`, `carries`, `opportunities`, `target_share`, `air_yards_share`, `wopr`, `adot`, `racr`, `weighted_opportunity`, `carry_share`, `opportunity_share`, `red_zone_targets`, `red_zone_carries`, `red_zone_touches`, `inside_10_carries`, `inside_5_carries`, `high_value_touches`, `epa_total`, `epa_per_opportunity`, `success_rate`, `cpoe`, `explosive_rush_rate`, `explosive_reception_rate`, `snap_share`, `injury_status`, `depth_chart_role`.

## Required Metadata

`metric_version`, `feature_run_id`, `source_freshness_json`, `missing_data_flags`, `created_at`.

## Safety Rules

Derived feature mart. Safe for downstream curated packets after validation, but not a Pigskin prompt surface by itself.
