# compat_pigskin_player_context_current Contract

## Purpose

Compatibility-safe current Pigskin player context view.

## Grain

One current packet row per player, scoring context, as-of season/week, and packet version.

## Allowed Upstream Dependencies

`pigskin_player_context_packet_current` and approved compatibility-safe current marts only.

## Forbidden Dependencies

The view must not directly depend on `raw_nflverse_*`, `play_by_play`, `weekly_metrics`, `ngs_*`, `ftn_charting`, `weekly_snap_counts`, `injury_reports`, `depth_charts`, `source_*`, or `raw_*`.

## Required Fields

Safe lookup fields, player identity, as-of season/week, scoring context, `packet_version`, `feature_run_id`, `packet_text`, `packet_json`, `source_freshness_json`, `missing_data_flags`, and `created_at`.

## Pigskin and UI Safety

Read-only. No request-time writes. No LLM dependency. No raw/source table exposure.
