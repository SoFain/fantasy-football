# team_week_context_metrics Contract

## Purpose

Team-week pace, tendency, opponent, and game-environment feature mart.

## Grain

One team, season, week, opponent, and metric version row.

## Allowed Upstream Dependencies

`stg_team_week_stats`, `stg_game_context`, and approved derived team context sources.

## Forbidden Dependencies

Direct raw/source dependencies in current or compatibility output.

## Required Fields

`metric_version`, `feature_run_id`, `season`, `week`, `team`, `opponent_team`, `plays`, `seconds_per_play`, `neutral_pass_rate`, `pass_rate_over_expected`, `team_epa_per_play`, `pass_epa_per_play`, `rush_epa_per_play`, `team_success_rate`, `red_zone_pass_rate`, `red_zone_rush_rate`, `opponent_epa_allowed`, `opponent_pass_epa_allowed`, `opponent_rush_epa_allowed`, `opponent_funnel_label`, `game_environment_json`, `source_freshness_json`, `missing_data_flags`, `created_at`.

## Safety Rules

Derived feature mart, safe for downstream packets after validation.
