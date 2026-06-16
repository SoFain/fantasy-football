-- Extend Viewer Team context to the production packet contract.
-- Additive migration only. Existing mart rows and legacy columns are preserved.
-- Data is populated by src/materialize_viewer_team_context.py.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.mart_viewer_team_context` (
    context_id STRING NOT NULL,
    league_id STRING NOT NULL,
    season INT64 NOT NULL,
    week INT64 NOT NULL,
    viewer_roster_id INT64 NOT NULL,
    viewer_team_name STRING,
    roster_rows_json STRING,
    lineup_rows_json STRING,
    waiver_rows_json STRING,
    pigskin_evidence_json STRING,
    rank_tier_json STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2020, 2030, 1))
CLUSTER BY league_id, viewer_roster_id;

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_viewer_team_context`
ADD COLUMN IF NOT EXISTS viewer_team_context_id STRING,
ADD COLUMN IF NOT EXISTS roster_id INT64,
ADD COLUMN IF NOT EXISTS manager_id STRING,
ADD COLUMN IF NOT EXISTS manager_display_name STRING,
ADD COLUMN IF NOT EXISTS scoring_profile_id STRING,
ADD COLUMN IF NOT EXISTS league_type_id STRING,
ADD COLUMN IF NOT EXISTS roster_format_id STRING,
ADD COLUMN IF NOT EXISTS model_run_id STRING,
ADD COLUMN IF NOT EXISTS ranking_version STRING,
ADD COLUMN IF NOT EXISTS snapshot_timestamp TIMESTAMP,
ADD COLUMN IF NOT EXISTS packet_json STRING,
ADD COLUMN IF NOT EXISTS packet_text STRING;

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
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.mart_viewer_team_context`;
