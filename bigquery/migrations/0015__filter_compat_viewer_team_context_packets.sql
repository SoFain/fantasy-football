-- Keep the compatibility view limited to materialized packet rows.
-- Additive safety migration only. Legacy mart rows remain available in the backing table.

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.compat_viewer_team_context` AS
SELECT
    COALESCE(viewer_team_context_id, context_id) AS viewer_team_context_id,
    league_id,
    COALESCE(roster_id, viewer_roster_id) AS roster_id,
    manager_id,
    COALESCE(manager_display_name, viewer_team_name) AS manager_display_name,
    season,
    week,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    model_run_id,
    ranking_version,
    COALESCE(snapshot_timestamp, updated_at) AS snapshot_timestamp,
    packet_json,
    packet_text,
    source_freshness_json,
    missing_data_flags,
    created_at,
    updated_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.mart_viewer_team_context`
WHERE packet_json IS NOT NULL;
