-- Additive metadata and configuration foundation for reproducible model runs.
-- This migration does not rename existing tables and does not backfill rankings.

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.model_runs`
ADD COLUMN IF NOT EXISTS model_version STRING,
ADD COLUMN IF NOT EXISTS season INT64,
ADD COLUMN IF NOT EXISTS week INT64,
ADD COLUMN IF NOT EXISTS scoring_profile_id STRING,
ADD COLUMN IF NOT EXISTS league_type_id STRING,
ADD COLUMN IF NOT EXISTS roster_format_id STRING,
ADD COLUMN IF NOT EXISTS feature_config_version_id STRING,
ADD COLUMN IF NOT EXISTS source_freshness_snapshot_id STRING,
ADD COLUMN IF NOT EXISTS created_by STRING,
ADD COLUMN IF NOT EXISTS error_message STRING;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.scoring_profiles` (
    scoring_profile_id STRING NOT NULL,
    display_name STRING NOT NULL,
    scoring_json JSON,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    active BOOL NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY active, scoring_profile_id;

MERGE `{{PROJECT_ID}}.{{DATASET_ID}}.scoring_profiles` target
USING (
    SELECT 'standard' AS scoring_profile_id, 'Standard' AS display_name, '{"reception":0,"passing_td":4,"rushing_td":6,"receiving_td":6}' AS scoring_json_text
    UNION ALL
    SELECT 'half_ppr', 'Half PPR', '{"reception":0.5,"passing_td":4,"rushing_td":6,"receiving_td":6}'
    UNION ALL
    SELECT 'ppr', 'PPR', '{"reception":1,"passing_td":4,"rushing_td":6,"receiving_td":6}'
) source
ON target.scoring_profile_id = source.scoring_profile_id
WHEN NOT MATCHED THEN
    INSERT (
        scoring_profile_id,
        display_name,
        scoring_json,
        created_at,
        updated_at,
        active
    )
    VALUES (
        source.scoring_profile_id,
        source.display_name,
        PARSE_JSON(source.scoring_json_text),
        CURRENT_TIMESTAMP(),
        CURRENT_TIMESTAMP(),
        TRUE
    );

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.league_types` (
    league_type_id STRING NOT NULL,
    display_name STRING NOT NULL,
    description STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    active BOOL NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY active, league_type_id;

MERGE `{{PROJECT_ID}}.{{DATASET_ID}}.league_types` target
USING (
    SELECT 'redraft' AS league_type_id, 'Redraft' AS display_name, 'Single-season managed league.' AS description
    UNION ALL
    SELECT 'keeper', 'Keeper', 'League with a limited number of retained players.'
    UNION ALL
    SELECT 'dynasty', 'Dynasty', 'Long-term league with most or all players retained.'
    UNION ALL
    SELECT 'best_ball', 'Best Ball', 'Draft-focused format with optimized weekly lineups.'
) source
ON target.league_type_id = source.league_type_id
WHEN NOT MATCHED THEN
    INSERT (
        league_type_id,
        display_name,
        description,
        created_at,
        updated_at,
        active
    )
    VALUES (
        source.league_type_id,
        source.display_name,
        source.description,
        CURRENT_TIMESTAMP(),
        CURRENT_TIMESTAMP(),
        TRUE
    );

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.roster_formats` (
    roster_format_id STRING NOT NULL,
    display_name STRING NOT NULL,
    description STRING,
    roster_rules_json JSON,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    active BOOL NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY active, roster_format_id;

MERGE `{{PROJECT_ID}}.{{DATASET_ID}}.roster_formats` target
USING (
    SELECT 'one_qb' AS roster_format_id, 'One QB' AS display_name, 'Traditional one-quarterback lineup format.' AS description, '{"qb":1,"superflex":0}' AS roster_rules_json_text
    UNION ALL
    SELECT 'superflex', 'Superflex', 'Lineup format with one QB slot and one QB-eligible flex slot.', '{"qb":1,"superflex":1}'
    UNION ALL
    SELECT 'two_qb', 'Two QB', 'Lineup format requiring two starting quarterbacks.', '{"qb":2,"superflex":0}'
    UNION ALL
    SELECT 'best_ball', 'Best Ball', 'Best ball roster format with optimized starters.', '{"optimized_lineup":true}'
) source
ON target.roster_format_id = source.roster_format_id
WHEN NOT MATCHED THEN
    INSERT (
        roster_format_id,
        display_name,
        description,
        roster_rules_json,
        created_at,
        updated_at,
        active
    )
    VALUES (
        source.roster_format_id,
        source.display_name,
        source.description,
        PARSE_JSON(source.roster_rules_json_text),
        CURRENT_TIMESTAMP(),
        CURRENT_TIMESTAMP(),
        TRUE
    );

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.feature_config_versions` (
    feature_config_version_id STRING NOT NULL,
    config_name STRING NOT NULL,
    model_name STRING,
    projection_horizon STRING,
    config_json JSON,
    created_by STRING,
    created_at TIMESTAMP NOT NULL,
    published_at TIMESTAMP,
    archived_at TIMESTAMP,
    active BOOL NOT NULL,
    notes STRING
)
PARTITION BY DATE(created_at)
CLUSTER BY active, config_name, projection_horizon;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.source_freshness_snapshots` (
    source_freshness_snapshot_id STRING NOT NULL,
    snapshot_json JSON,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY source_freshness_snapshot_id;
