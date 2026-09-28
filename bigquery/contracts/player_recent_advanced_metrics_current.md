# player_recent_advanced_metrics_current Contract

## Purpose

Current player rolling-window advanced metrics view or table.

## Grain

One player and scoring context row for an `as_of_season`, `as_of_week`, and `metric_version`.

## Allowed Upstream Dependencies

`player_week_advanced_metrics` and approved current feature marts.

## Forbidden Dependencies

Direct raw/source dependencies are forbidden, including `raw_nflverse_*`, `play_by_play`, and `weekly_metrics`.

## Required Fields

`metric_version`, `feature_run_id`, `as_of_season`, `as_of_week`, player identity fields, scoring context fields, season-to-date metrics, last-3 metrics, last-5 metrics, last-8 metrics, trend labels, sample-size flags, `source_freshness_json`, `missing_data_flags`, `created_at`.

## Safety Rules

Derived current mart. Safe for compatibility views after validation.
