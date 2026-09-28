-- Additive injury/depth role context metrics for ranking research.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_role_context_metrics` (
    season INT64 NOT NULL,
    week INT64 NOT NULL,
    player_id_internal STRING,
    gsis_id STRING NOT NULL,
    player_name STRING,
    team STRING,
    position STRING,
    injury_report_count INT64,
    out_status_count INT64,
    doubtful_status_count INT64,
    questionable_status_count INT64,
    limited_practice_count INT64,
    did_not_practice_count INT64,
    injury_risk_score FLOAT64,
    depth_chart_role_score FLOAT64,
    missing_flags_json STRING,
    source_freshness_json STRING,
    source_provenance_json STRING,
    role_context_run_id STRING,
    created_at TIMESTAMP
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, player_id_internal, gsis_id, team;
