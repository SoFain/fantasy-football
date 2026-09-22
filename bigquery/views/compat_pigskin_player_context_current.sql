-- Compatibility-safe Pigskin player context view.
-- Pigskin and Streamlit should read this surface instead of raw/source tables.

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.compat_pigskin_player_context_current` AS
SELECT
    as_of_season,
    as_of_week,
    player_id_internal,
    player_name,
    position,
    team,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    packet_version,
    feature_run_id,
    packet_text,
    packet_json,
    source_freshness_json,
    missing_data_flags,
    created_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.pigskin_player_context_packet_current`;
