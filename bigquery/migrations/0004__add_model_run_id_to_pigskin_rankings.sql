-- Add model-run lineage columns to Pigskin ranking output tables.
-- Existing rows are not backfilled and may keep NULL model_run_id.

DECLARE active_table_exists BOOL DEFAULT (
    SELECT COUNT(1) = 1
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.TABLES`
    WHERE table_name = 'analytics_pigskin_rankings'
);

DECLARE history_table_exists BOOL DEFAULT (
    SELECT COUNT(1) = 1
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.TABLES`
    WHERE table_name = 'analytics_pigskin_rankings_history'
);

IF active_table_exists THEN
    ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_pigskin_rankings`
    ADD COLUMN IF NOT EXISTS model_run_id STRING,
    ADD COLUMN IF NOT EXISTS scoring_profile_id STRING,
    ADD COLUMN IF NOT EXISTS league_type_id STRING,
    ADD COLUMN IF NOT EXISTS roster_format_id STRING,
    ADD COLUMN IF NOT EXISTS feature_config_version_id STRING,
    ADD COLUMN IF NOT EXISTS source_freshness_snapshot_id STRING;
END IF;

IF history_table_exists THEN
    ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_pigskin_rankings_history`
    ADD COLUMN IF NOT EXISTS model_run_id STRING,
    ADD COLUMN IF NOT EXISTS scoring_profile_id STRING,
    ADD COLUMN IF NOT EXISTS league_type_id STRING,
    ADD COLUMN IF NOT EXISTS roster_format_id STRING,
    ADD COLUMN IF NOT EXISTS feature_config_version_id STRING,
    ADD COLUMN IF NOT EXISTS source_freshness_snapshot_id STRING;
END IF;
