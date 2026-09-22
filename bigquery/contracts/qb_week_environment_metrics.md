# qb_week_environment_metrics Contract

## Purpose

Quarterback weekly environment and efficiency feature mart.

## Grain

One quarterback, season, week, team, opponent, and metric version row.

## Allowed Upstream Dependencies

`stg_play_player_events`, `stg_player_week_stats`, `stg_team_week_stats`, and approved NGS-derived staging.

## Forbidden Dependencies

Direct raw/source dependencies in Pigskin or UI compatibility output.

## Required Fields

`metric_version`, `feature_run_id`, `season`, `week`, `qb_player_id_internal`, `player_name`, `team`, `opponent_team`, `dropbacks`, `pass_attempts`, `sacks`, `scrambles`, `designed_rushes`, `epa_per_dropback`, `passing_epa`, `cpoe`, `adot`, `deep_attempt_rate`, `sack_rate`, `scramble_rate`, `pass_rate_over_expected_context`, `source_freshness_json`, `missing_data_flags`, `created_at`.

## Safety Rules

Derived feature mart, safe for downstream packets after validation.
