-- Promote compat_viewer_team_context to precomputed mart.
-- Backed by mart_viewer_team_context table.
-- Data is populated by src/materialize_viewer_team.py.

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

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.compat_viewer_team_context` AS
SELECT *
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.mart_viewer_team_context`;
