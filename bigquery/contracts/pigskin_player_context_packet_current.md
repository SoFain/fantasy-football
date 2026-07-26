# pigskin_player_context_packet_current Contract

## Purpose

Current deterministic player context packets for Pigskin and Streamlit context tools.

## Grain

One player, scoring context, `as_of_season`, `as_of_week`, and `packet_version` row.

## Allowed Upstream Dependencies

Validated current feature marts, projection outputs, ranking outputs, trade compatibility views, and risk/fraud outputs.

## Forbidden Dependencies

Direct dependencies on `raw_nflverse_*`, `play_by_play`, `weekly_metrics`, `ngs_*`, `ftn_charting`, `weekly_snap_counts`, `injury_reports`, `depth_charts`, `source_*`, and `raw_*`.

## Required Fields

`packet_version`, `feature_run_id`, `as_of_season`, `as_of_week`, player identity and scoring context fields, `identity_json`, `advanced_metrics_json`, `recent_form_json`, `team_context_json`, `ranking_context_json`, `projection_context_json`, `trade_context_json`, `risk_context_json`, `source_freshness_json`, `missing_data_flags`, `packet_text`, `packet_json`, `created_at`.

## Safety Rules

Output packet. Safe only after validation. Must be read-only from request-time UI.
